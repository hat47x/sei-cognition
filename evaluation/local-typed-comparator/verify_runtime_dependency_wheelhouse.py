#!/usr/bin/env python3
from __future__ import annotations

import argparse
import email
import hashlib
import json
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = "sei.local-typed-comparator-runtime-wheelhouse/v1"
OBSERVED_PLATFORM = {
    "os": "linux",
    "arch": "x86_64",
    "python": "3.13.5",
}
MANAGED_REFERENCE_REQUIRED = (
    "torch",
    "transformers",
    "tokenizers",
    "safetensors",
    "huggingface-hub",
    "numpy",
    "fastapi",
    "uvicorn",
)
WHEELHOUSE_SUPPLIED_RUNTIME = (
    "transformers",
    "tokenizers",
    "safetensors",
)
HOST_REQUIRED_NOT_SUPPLIED = (
    "torch",
    "huggingface-hub",
    "numpy",
    "fastapi",
    "uvicorn",
)
EXPECTED_VALIDATION_OBSERVATION = {
    "offline_install": "pass",
    "laya_import": "pass",
    "transformers_import": "pass",
    "modernbert_import": "pass",
}


class WheelhouseError(ValueError):
    pass


def sha256_file(path: Path) -> tuple[str, int]:
    h = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            h.update(block)
            size += len(block)
    return h.hexdigest(), size


def load_manifest(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise WheelhouseError(f"cannot read manifest: {path}") from exc
    if not isinstance(value, dict):
        raise WheelhouseError("manifest root must be an object")
    return value


def _lower_hex(value: Any, length: int, field: str) -> str:
    if not isinstance(value, str) or len(value) != length:
        raise WheelhouseError(f"{field} must be {length}-character hex")
    lowered = value.lower()
    if value != lowered or any(c not in "0123456789abcdef" for c in lowered):
        raise WheelhouseError(f"{field} must be lowercase hex")
    return lowered


def _positive_int(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise WheelhouseError(f"{field} must be a positive integer")
    return value


def _wheel_metadata(path: Path) -> tuple[str, str, list[str]]:
    try:
        with zipfile.ZipFile(path) as archive:
            metadata = [
                name
                for name in archive.namelist()
                if name.endswith(".dist-info/METADATA")
            ]
            wheel = [
                name
                for name in archive.namelist()
                if name.endswith(".dist-info/WHEEL")
            ]
            if len(metadata) != 1 or len(wheel) != 1:
                raise WheelhouseError(
                    f"{path.name}: wheel must contain one METADATA and one WHEEL"
                )
            message = email.message_from_bytes(archive.read(metadata[0]))
            name = message.get("Name")
            version = message.get("Version")
            if not name or not version:
                raise WheelhouseError(
                    f"{path.name}: missing Name/Version metadata"
                )
            tags = []
            for line in archive.read(wheel[0]).decode("utf-8").splitlines():
                if line.startswith("Tag: "):
                    tags.append(line[5:])
            if not tags:
                raise WheelhouseError(f"{path.name}: WHEEL contains no Tag")
            return name.lower().replace("_", "-"), version, tags
    except (OSError, zipfile.BadZipFile, UnicodeDecodeError) as exc:
        raise WheelhouseError(f"cannot inspect wheel: {path}") from exc


def validate_manifest(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    if manifest.get("schema") != SCHEMA:
        raise WheelhouseError(f"schema must be {SCHEMA}")
    if manifest.get("status") != "transport-candidate":
        raise WheelhouseError("status must remain transport-candidate")

    _lower_hex(
        manifest.get("observed_from_sei_source_sha"),
        40,
        "observed_from_sei_source_sha",
    )
    platform = manifest.get("platform")
    if platform != OBSERVED_PLATFORM:
        raise WheelhouseError("observed platform drift")

    boundary = manifest.get("transport_boundary")
    if not isinstance(boundary, dict):
        raise WheelhouseError("transport_boundary must be an object")
    if boundary.get("host_assisted_transport") is not True:
        raise WheelhouseError(
            "transport_boundary.host_assisted_transport must be true"
        )
    if boundary.get("wheelhouse_is_self_contained") is not False:
        raise WheelhouseError(
            "transport_boundary.wheelhouse_is_self_contained must be false"
        )
    expected_boundary_lists = {
        "managed_reference_required_distributions": list(
            MANAGED_REFERENCE_REQUIRED
        ),
        "wheelhouse_supplied_managed_reference_distributions": list(
            WHEELHOUSE_SUPPLIED_RUNTIME
        ),
        "required_host_distributions_not_supplied": list(
            HOST_REQUIRED_NOT_SUPPLIED
        ),
    }
    for field, expected in expected_boundary_lists.items():
        if boundary.get(field) != expected:
            raise WheelhouseError(f"transport_boundary.{field} drift")

    host_dependencies = manifest.get("observed_host_dependencies")
    if not isinstance(host_dependencies, dict) or not host_dependencies:
        raise WheelhouseError(
            "observed_host_dependencies must be a non-empty object"
        )
    for distribution in HOST_REQUIRED_NOT_SUPPLIED:
        version = host_dependencies.get(distribution)
        if not isinstance(version, str) or not version:
            raise WheelhouseError(
                f"observed_host_dependencies.{distribution} missing"
            )
    observation = manifest.get("validation_observation")
    if observation != EXPECTED_VALIDATION_OBSERVATION:
        raise WheelhouseError("validation_observation drift")

    entries = manifest.get("entries")
    if not isinstance(entries, list) or not entries:
        raise WheelhouseError("entries must be a non-empty array")

    seen = set()
    normalized = []
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise WheelhouseError(f"entries[{index}] must be an object")

        distribution = entry.get("distribution")
        version = entry.get("version")
        filename = entry.get("wheel_filename")
        tags = entry.get("wheel_tags")
        if not all(
            isinstance(value, str) and value
            for value in (distribution, version, filename)
        ):
            raise WheelhouseError(
                f"entries[{index}] identity fields must be strings"
            )

        canonical = distribution.lower().replace("_", "-")
        if canonical in seen:
            raise WheelhouseError(f"duplicate distribution: {canonical}")
        seen.add(canonical)

        if (
            not isinstance(tags, list)
            or not tags
            or not all(isinstance(tag, str) and tag for tag in tags)
        ):
            raise WheelhouseError(
                f"{canonical}.wheel_tags must be non-empty strings"
            )

        source = entry.get("source")
        if not isinstance(source, dict):
            raise WheelhouseError(f"{canonical}.source must be an object")
        for field in ("repository", "artifact_name"):
            if not isinstance(source.get(field), str) or not source[field]:
                raise WheelhouseError(
                    f"{canonical}.source.{field} must be a string"
                )
        _lower_hex(
            source.get("revision"),
            40,
            f"{canonical}.source.revision",
        )
        if source.get("workflow_conclusion") != "success":
            raise WheelhouseError(
                f"{canonical}.source.workflow_conclusion must be success"
            )
        expires_at = source.get("artifact_expires_at")
        if not isinstance(expires_at, str) or not expires_at.endswith("Z"):
            raise WheelhouseError(
                f"{canonical}.source.artifact_expires_at must be UTC ISO-8601"
            )
        try:
            expiry = datetime.fromisoformat(
                expires_at[:-1] + "+00:00"
            )
        except ValueError as exc:
            raise WheelhouseError(
                f"{canonical}.source.artifact_expires_at must be UTC ISO-8601"
            ) from exc
        if expiry.tzinfo != timezone.utc:
            raise WheelhouseError(
                f"{canonical}.source.artifact_expires_at must be UTC"
            )
        _positive_int(
            source.get("workflow_run_id"),
            f"{canonical}.source.workflow_run_id",
        )
        _positive_int(
            source.get("artifact_id"),
            f"{canonical}.source.artifact_id",
        )
        _lower_hex(
            source.get("artifact_zip_sha256"),
            64,
            f"{canonical}.source.artifact_zip_sha256",
        )

        normalized.append(
            {
                "distribution": canonical,
                "version": version,
                "wheel_filename": filename,
                "wheel_bytes": _positive_int(
                    entry.get("wheel_bytes"), f"{canonical}.wheel_bytes"
                ),
                "wheel_sha256": _lower_hex(
                    entry.get("wheel_sha256"),
                    64,
                    f"{canonical}.wheel_sha256",
                ),
                "wheel_tags": tags,
            }
        )

    scope = manifest.get("scope")
    if not isinstance(scope, dict):
        raise WheelhouseError("scope must be an object")

    if scope.get("transport_candidate_only") is not True:
        raise WheelhouseError(
            "scope.transport_candidate_only must remain true"
        )
    if scope.get("host_assisted_transport") is not True:
        raise WheelhouseError("scope.host_assisted_transport must remain true")
    if scope.get("self_contained_wheelhouse") is not False:
        raise WheelhouseError(
            "scope.self_contained_wheelhouse must remain false"
        )

    for field in (
        "product_runtime_pin",
        "model_bytes_materialized",
        "model_weights_loaded",
        "live_inference",
        "numeric_parity",
        "shipping_decision",
    ):
        if scope.get(field) is not False:
            raise WheelhouseError(f"scope.{field} must remain false")

    return normalized


def verify_wheelhouse(
    manifest: dict[str, Any], wheelhouse: Path
) -> dict[str, Any]:
    entries = validate_manifest(manifest)
    root = wheelhouse.expanduser().resolve()
    if not root.is_dir():
        raise WheelhouseError(f"wheelhouse not found: {root}")

    expected_names = {entry["wheel_filename"] for entry in entries}
    actual_names = {
        path.name for path in root.glob("*.whl") if path.is_file()
    }
    if actual_names != expected_names:
        missing = sorted(expected_names - actual_names)
        extra = sorted(actual_names - expected_names)
        raise WheelhouseError(
            f"wheel set mismatch: missing={missing}, extra={extra}"
        )

    receipts = []
    for entry in entries:
        path = root / entry["wheel_filename"]
        digest, size = sha256_file(path)
        if size != entry["wheel_bytes"]:
            raise WheelhouseError(f"{path.name}: byte-size mismatch")
        if digest != entry["wheel_sha256"]:
            raise WheelhouseError(f"{path.name}: SHA-256 mismatch")

        name, version, tags = _wheel_metadata(path)
        if name != entry["distribution"]:
            raise WheelhouseError(
                f"{path.name}: distribution metadata drift"
            )
        if version != entry["version"]:
            raise WheelhouseError(f"{path.name}: version metadata drift")
        if set(tags) != set(entry["wheel_tags"]):
            raise WheelhouseError(f"{path.name}: wheel tag drift")

        receipts.append(
            {
                "distribution": name,
                "version": version,
                "filename": path.name,
                "bytes": size,
                "sha256": digest,
                "tags": tags,
            }
        )

    return {
        "schema": SCHEMA,
        "valid": True,
        "wheel_count": len(receipts),
        "wheels": receipts,
        "scope": manifest["scope"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("wheelhouse", type=Path)
    args = parser.parse_args(argv)

    try:
        result = verify_wheelhouse(
            load_manifest(args.manifest), args.wheelhouse
        )
    except WheelhouseError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
