#!/usr/bin/env python3
"""Atomically materialize the exact Papaya evaluation candidate bytes.

The only admitted transport is the immutable Hugging Face repository revision
already used by the retained Papaya artifact/tokenizer attestations. Downloaded
content is staged beside the destination, verified while streaming, checked by
prepare_papaya_compat_overlay.inspect_overlay_inputs(), and only then atomically
published.

This materializes candidate inputs only. It does not prepare the compatibility
overlay, load weights, run inference, establish numeric parity, or make a
shipping decision.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
import urllib.request
from contextlib import closing
from pathlib import Path, PurePosixPath
from typing import Any, BinaryIO, Callable, ContextManager

import prepare_papaya_compat_overlay as overlay

SCHEMA = "sei.local-typed-comparator-papaya-candidate-transport/v1"
STATUS = "transport-candidate"
TRANSPORT_ID = "huggingface-immutable"
TRANSPORT_KIND = "huggingface-resolve"
HF_REPOSITORY = overlay.CANDIDATE_REPOSITORY
CANDIDATE_REVISION = overlay.CANDIDATE_REVISION
TOKENIZER_REVISION = overlay.CANDIDATE_TOKENIZER_REVISION
HF_BASE = f"https://huggingface.co/{HF_REPOSITORY}/resolve"

ROLE_ORDER = (
    "q8_backbone",
    "decision_head",
    "raw_config",
    "tokenizer_config",
    "attested_tokenizer",
)


class PapayaCandidateTransportError(ValueError):
    pass


def _lower_hex(value: Any, length: int, field: str) -> str:
    if not isinstance(value, str) or len(value) != length:
        raise PapayaCandidateTransportError(
            f"{field} must be {length}-character lowercase hex"
        )
    if value != value.lower() or any(
        c not in "0123456789abcdef" for c in value
    ):
        raise PapayaCandidateTransportError(
            f"{field} must be {length}-character lowercase hex"
        )
    return value


def _positive_int(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise PapayaCandidateTransportError(
            f"{field} must be a positive integer"
        )
    return value


def _safe_relative_path(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise PapayaCandidateTransportError(
            f"{field} must be a non-empty string"
        )
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or "." in path.parts:
        raise PapayaCandidateTransportError(
            f"{field} must be a safe relative path"
        )
    return path.as_posix()


def load_manifest(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PapayaCandidateTransportError(
            f"cannot read manifest: {path}"
        ) from exc
    if not isinstance(value, dict):
        raise PapayaCandidateTransportError(
            "manifest root must be an object"
        )
    return value


def _expected_specs() -> dict[str, overlay.ArtifactSpec]:
    specs = {spec.role: spec for spec in overlay.DEFAULT_ARTIFACTS}
    specs[overlay.ATTESTED_TOKENIZER_SPEC.role] = (
        overlay.ATTESTED_TOKENIZER_SPEC
    )
    if set(specs) != set(ROLE_ORDER):
        raise PapayaCandidateTransportError(
            "Papaya candidate artifact role set drift"
        )
    return specs


def _expected_revision(role: str) -> str:
    return (
        TOKENIZER_REVISION
        if role == "attested_tokenizer"
        else CANDIDATE_REVISION
    )


def validate_manifest(
    manifest: dict[str, Any],
) -> list[dict[str, Any]]:
    if manifest.get("schema") != SCHEMA:
        raise PapayaCandidateTransportError(f"schema must be {SCHEMA}")
    if manifest.get("status") != STATUS:
        raise PapayaCandidateTransportError(
            f"status must remain {STATUS}"
        )
    _lower_hex(
        manifest.get("observed_from_sei_source_sha"),
        40,
        "observed_from_sei_source_sha",
    )

    contract = manifest.get("candidate_contract")
    if not isinstance(contract, dict):
        raise PapayaCandidateTransportError(
            "candidate_contract must be an object"
        )
    expected_contract = {
        "repository": HF_REPOSITORY,
        "candidate_revision": CANDIDATE_REVISION,
        "tokenizer_revision": TOKENIZER_REVISION,
        "overlay_schema": overlay.SCHEMA,
    }
    if contract != expected_contract:
        raise PapayaCandidateTransportError(
            "candidate contract drift"
        )

    transport = manifest.get("transport")
    if not isinstance(transport, dict):
        raise PapayaCandidateTransportError(
            "transport must be an object"
        )
    if transport.get("id") != TRANSPORT_ID:
        raise PapayaCandidateTransportError("transport id drift")
    if transport.get("kind") != TRANSPORT_KIND:
        raise PapayaCandidateTransportError("transport kind drift")
    if transport.get("content_addressed_url") is not True:
        raise PapayaCandidateTransportError(
            "immutable revision URL must remain content-addressed"
        )
    if (
        transport.get("requires_post_download_verification")
        is not True
    ):
        raise PapayaCandidateTransportError(
            "post-download verification gate must remain true"
        )

    files = transport.get("files")
    if not isinstance(files, list) or len(files) != len(ROLE_ORDER):
        raise PapayaCandidateTransportError(
            "transport file count drift"
        )

    specs = _expected_specs()
    seen_roles: set[str] = set()
    seen_paths: set[str] = set()
    normalized: list[dict[str, Any]] = []
    for index, entry in enumerate(files):
        if not isinstance(entry, dict):
            raise PapayaCandidateTransportError(
                f"transport.files[{index}] must be an object"
            )
        role = entry.get("role")
        if (
            not isinstance(role, str)
            or role not in specs
            or role in seen_roles
        ):
            raise PapayaCandidateTransportError(
                "transport role drift or duplicate"
            )
        seen_roles.add(role)
        spec = specs[role]
        relative = _safe_relative_path(
            entry.get("path"),
            f"transport.files[{index}].path",
        )
        if relative != spec.relative_path or relative in seen_paths:
            raise PapayaCandidateTransportError(
                f"{role}: path drift or duplicate"
            )
        seen_paths.add(relative)

        revision = _lower_hex(
            entry.get("revision"),
            40,
            f"{role}.revision",
        )
        expected_revision = _expected_revision(role)
        if revision != expected_revision:
            raise PapayaCandidateTransportError(
                f"{role}: revision drift"
            )
        expected_url = (
            f"{HF_BASE}/{expected_revision}/{relative}"
        )
        if entry.get("url") != expected_url:
            raise PapayaCandidateTransportError(
                f"{role}: URL drift"
            )
        if _positive_int(entry.get("bytes"), f"{role}.bytes") != spec.bytes:
            raise PapayaCandidateTransportError(
                f"{role}: byte-size drift"
            )
        if (
            _lower_hex(entry.get("sha256"), 64, f"{role}.sha256")
            != spec.sha256
        ):
            raise PapayaCandidateTransportError(
                f"{role}: SHA-256 drift"
            )
        normalized.append(
            {
                "path": relative,
                "role": role,
                "revision": expected_revision,
                "url": expected_url,
                "bytes": spec.bytes,
                "sha256": spec.sha256,
            }
        )

    if tuple(item["role"] for item in normalized) != ROLE_ORDER:
        raise PapayaCandidateTransportError(
            "transport file order drift"
        )

    scope = manifest.get("scope")
    if not isinstance(scope, dict):
        raise PapayaCandidateTransportError(
            "scope must be an object"
        )
    if scope.get("candidate_contract_matches_transport") is not True:
        raise PapayaCandidateTransportError(
            "candidate/transport binding must remain true"
        )
    if scope.get("transport_candidate_only") is not True:
        raise PapayaCandidateTransportError(
            "transport candidate scope must remain true"
        )
    if scope.get("independent_exact_byte_mirror_available") is not False:
        raise PapayaCandidateTransportError(
            "independent exact-byte mirror must not be claimed"
        )
    for field in (
        "current_chat_transport_succeeded",
        "candidate_bytes_materialized",
        "compatibility_overlay_prepared",
        "model_weights_loaded",
        "live_inference",
        "numeric_parity",
        "shipping_decision",
    ):
        if scope.get(field) is not False:
            raise PapayaCandidateTransportError(
                f"scope.{field} must remain false"
            )

    return normalized


def _url_stream(
    url: str, timeout: float
) -> ContextManager[BinaryIO]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "sei-cognition-papaya-candidate-materializer/1"
        },
    )
    return closing(urllib.request.urlopen(request, timeout=timeout))


def _download_verified(
    entry: dict[str, Any],
    destination: Path,
    *,
    timeout: float,
    stream_factory: Callable[
        [str, float], ContextManager[BinaryIO]
    ],
) -> dict[str, Any]:
    destination.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    size = 0
    try:
        with stream_factory(
            entry["url"], timeout
        ) as source, destination.open("xb") as target:
            while True:
                block = source.read(8 * 1024 * 1024)
                if not block:
                    break
                if not isinstance(block, (bytes, bytearray)):
                    raise PapayaCandidateTransportError(
                        "download stream returned non-bytes"
                    )
                target.write(block)
                digest.update(block)
                size += len(block)
    except FileExistsError as exc:
        raise PapayaCandidateTransportError(
            f"staged file already exists: {destination}"
        ) from exc
    except OSError as exc:
        raise PapayaCandidateTransportError(
            f"download failed for {entry['path']}: {exc}"
        ) from exc

    observed_sha = digest.hexdigest()
    if size != entry["bytes"]:
        raise PapayaCandidateTransportError(
            f"{entry['path']}: expected {entry['bytes']} bytes, got {size}"
        )
    if observed_sha != entry["sha256"]:
        raise PapayaCandidateTransportError(
            f"{entry['path']}: SHA-256 mismatch"
        )
    return {
        "path": entry["path"],
        "role": entry["role"],
        "revision": entry["revision"],
        "bytes": size,
        "sha256": observed_sha,
    }


def _verify_candidate_inputs(root: Path) -> dict[str, Any]:
    try:
        receipt, _compat_bytes = overlay.inspect_overlay_inputs(
            root,
            root / overlay.ATTESTED_TOKENIZER_SPEC.relative_path,
        )
    except overlay.OverlayError as exc:
        raise PapayaCandidateTransportError(
            f"Papaya candidate input verification failed: {exc}"
        ) from exc

    candidate_bundle = receipt.get("candidate_bundle")
    tokenizer = receipt.get("tokenizer_identity")
    policy = receipt.get("temperature_policy")
    if (
        not isinstance(candidate_bundle, dict)
        or candidate_bundle.get("repository") != HF_REPOSITORY
        or candidate_bundle.get("revision") != CANDIDATE_REVISION
    ):
        raise PapayaCandidateTransportError(
            "candidate verifier repository/revision drift"
        )
    if (
        not isinstance(tokenizer, dict)
        or tokenizer.get("candidate_revision") != TOKENIZER_REVISION
        or tokenizer.get("candidate_byte_identity_attested") is not True
        or tokenizer.get("staged_bytes_verified") is not True
    ):
        raise PapayaCandidateTransportError(
            "candidate tokenizer verification drift"
        )
    if (
        not isinstance(policy, dict)
        or policy.get("current_candidate_delta_exactly_expected")
        is not True
        or policy.get("compat_config_sha256")
        != overlay.EXPECTED_COMPAT_CONFIG_SHA256
    ):
        raise PapayaCandidateTransportError(
            "candidate compatibility-policy verification drift"
        )
    return receipt


def materialize_entries(
    entries: list[dict[str, Any]],
    output_dir: Path,
    *,
    timeout: float = 300.0,
    stream_factory: Callable[
        [str, float], ContextManager[BinaryIO]
    ] = _url_stream,
    input_verifier: Callable[
        [Path], dict[str, Any]
    ] = _verify_candidate_inputs,
) -> dict[str, Any]:
    if timeout <= 0:
        raise PapayaCandidateTransportError(
            "timeout must be positive"
        )
    output = output_dir.expanduser().resolve()
    if output.exists():
        raise PapayaCandidateTransportError(
            f"output already exists: {output}"
        )
    output.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(
        tempfile.mkdtemp(
            prefix=f".{output.name}.staging-",
            dir=output.parent,
        )
    )
    files: list[dict[str, Any]] = []
    try:
        for entry in entries:
            relative = _safe_relative_path(
                entry.get("path"),
                "download path",
            )
            files.append(
                _download_verified(
                    entry,
                    staging / relative,
                    timeout=timeout,
                    stream_factory=stream_factory,
                )
            )
        verification = input_verifier(staging)
        if not isinstance(verification, dict):
            raise PapayaCandidateTransportError(
                "candidate input verifier must return an object"
            )
        os.replace(staging, output)
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise

    return {
        "schema": SCHEMA,
        "status": "materialized-and-verified",
        "transport_id": TRANSPORT_ID,
        "output_dir": str(output),
        "files": files,
        "candidate_input_verification": verification,
        "scope": {
            "candidate_bytes_materialized": True,
            "candidate_inputs_verified": True,
            "compatibility_overlay_prepared": False,
            "model_weights_loaded": False,
            "live_inference": False,
            "numeric_parity": False,
            "shipping_decision": False,
        },
    }


def materialize_papaya_candidate(
    manifest: dict[str, Any],
    output_dir: Path,
    *,
    timeout: float = 300.0,
) -> dict[str, Any]:
    entries = validate_manifest(manifest)
    return materialize_entries(
        entries,
        output_dir,
        timeout=timeout,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--timeout", type=float, default=300.0)
    args = parser.parse_args(argv)

    try:
        receipt = materialize_papaya_candidate(
            load_manifest(args.manifest),
            args.output_dir,
            timeout=args.timeout,
        )
    except (
        PapayaCandidateTransportError,
        overlay.OverlayError,
    ) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
