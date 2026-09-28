#!/usr/bin/env python3
"""Prepare the materialized model-input workspace for one managed pair run.

This composes the already-retained reference/Papaya materializers and Papaya
compatibility-overlay verifier. It adds no new download identity or model
semantics.

Each large sub-materializer remains atomic on its own. The workspace root is
created before those operations because the Papaya overlay contains symlinks to
the final candidate directory; moving a fully prepared parent staging tree
would invalidate the current absolute symlink targets. On any failure this
wrapper removes the whole new workspace, so the requested destination is absent
after failure.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path
from typing import Any

import capture_papaya_l0 as papaya_capture
import materialize_papaya_candidate as papaya_materializer
import materialize_reference_model as reference_materializer
import prepare_papaya_compat_overlay as overlay
import verify_runtime_dependency_wheelhouse as wheelhouse_verifier
import materialize_managed_runtime_env as runtime_materializer

SCHEMA = "sei.local-typed-comparator-managed-pair-input-materialization/v1"
RECEIPT_FILE = "managed-pair-input-materialization.json"
REFERENCE_DIR = "reference-model"
PAPAYA_CANDIDATE_DIR = "papaya-candidate"
PAPAYA_OVERLAY_DIR = "papaya-overlay"
RUNTIME_ENV_DIR = "runtime-env"
DEFAULT_DOWNLOAD_ATTEMPTS = reference_materializer.DEFAULT_ATTEMPTS


class ManagedPairMaterializationError(ValueError):
    pass


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _full_sha(value: str) -> str:
    sha = value.lower()
    if len(sha) != 40 or any(c not in "0123456789abcdef" for c in sha):
        raise ManagedPairMaterializationError(
            "source-git-sha must be a full 40-character hexadecimal SHA"
        )
    return sha


def _require_script_source_binding(here: Path, sei_source_dir: Path) -> Path:
    script_root = here.parents[1].resolve()
    supplied_root = sei_source_dir.expanduser().resolve()
    if script_root != supplied_root:
        raise ManagedPairMaterializationError(
            "materializer script checkout must equal --sei-source-dir"
        )
    return script_root


def _new_external_workspace(path: Path, sei_source_dir: Path) -> Path:
    resolved = path.expanduser().resolve()
    if resolved.exists():
        raise ManagedPairMaterializationError(
            f"output workspace already exists: {resolved}"
        )
    source_root = sei_source_dir.expanduser().resolve()
    try:
        resolved.relative_to(source_root)
    except ValueError:
        return resolved
    raise ManagedPairMaterializationError(
        "output workspace must be outside the SEI source checkout"
    )


def _load_json_bytes(path: Path, label: str) -> tuple[dict[str, Any], bytes]:
    try:
        raw = path.read_bytes()
        value = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ManagedPairMaterializationError(
            f"cannot read {label}: {path}"
        ) from exc
    if not isinstance(value, dict):
        raise ManagedPairMaterializationError(
            f"{label} root must be an object"
        )
    return value, raw


def _require_raw_binding(
    value: dict[str, Any], raw: bytes, label: str
) -> None:
    try:
        decoded = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ManagedPairMaterializationError(
            f"{label} raw bytes must be UTF-8 JSON"
        ) from exc
    if decoded != value:
        raise ManagedPairMaterializationError(
            f"{label} object/raw-byte binding drift"
        )


def _verify_overlay_workspace_binding(
    candidate_dir: Path, overlay_dir: Path
) -> dict[str, Any]:
    by_role = {spec.role: spec for spec in overlay.DEFAULT_ARTIFACTS}
    observed: dict[str, str] = {}
    for role in ("q8_backbone", "decision_head"):
        spec = by_role.get(role)
        if spec is None:
            raise ManagedPairMaterializationError(
                f"overlay artifact role missing: {role}"
            )
        staged = overlay_dir / spec.relative_path
        expected = (candidate_dir / spec.relative_path).resolve()
        if not staged.is_symlink():
            raise ManagedPairMaterializationError(
                f"overlay {role} must remain a symlink"
            )
        if staged.resolve() != expected:
            raise ManagedPairMaterializationError(
                f"overlay {role} symlink target drift"
            )
        observed[role] = spec.relative_path
    return {
        "valid": True,
        "absolute_symlink_targets": True,
        "workspace_relocatable": False,
        "candidate_relative_paths": observed,
    }


def _portable_materialization_summary(
    receipt: dict[str, Any],
    *,
    expected_schema: str,
    label: str,
) -> dict[str, Any]:
    if receipt.get("schema") != expected_schema:
        raise ManagedPairMaterializationError(f"{label} schema drift")
    if receipt.get("status") != "materialized-and-verified":
        raise ManagedPairMaterializationError(
            f"{label} must be materialized-and-verified"
        )
    result = {
        key: value
        for key, value in receipt.items()
        if key != "output_dir"
    }
    if "output_dir" in result:
        raise ManagedPairMaterializationError(
            f"{label} portable summary retained output_dir"
        )
    return result


def _write_receipt(path: Path, value: dict[str, Any]) -> None:
    temp = path.with_name(path.name + ".tmp")
    temp.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temp.replace(path)


def _attested_tokenizer_relative_path(
    normalized_entries: list[dict[str, Any]],
) -> str:
    matches = [
        item.get("path")
        for item in normalized_entries
        if item.get("role") == "attested_tokenizer"
    ]
    if len(matches) != 1 or not isinstance(matches[0], str):
        raise ManagedPairMaterializationError(
            "Papaya transport must retain exactly one attested tokenizer"
        )
    return matches[0]


def prepare_workspace(
    *,
    source_sha: str,
    sei_source_dir: Path,
    reference_manifest: dict[str, Any],
    reference_manifest_raw: bytes,
    reference_transport: str,
    papaya_manifest: dict[str, Any],
    papaya_manifest_raw: bytes,
    output_dir: Path,
    timeout: float,
    attempts: int = DEFAULT_DOWNLOAD_ATTEMPTS,
    runtime_wheelhouse_dir: Path | None = None,
    runtime_wheelhouse_manifest: dict[str, Any] | None = None,
    runtime_wheelhouse_manifest_raw: bytes | None = None,
    materialize_runtime_environment: bool = False,
) -> dict[str, Any]:
    source_sha = _full_sha(source_sha)
    if timeout <= 0:
        raise ManagedPairMaterializationError("timeout must be positive")
    if (
        reference_materializer.DEFAULT_ATTEMPTS
        != papaya_materializer.DEFAULT_ATTEMPTS
    ):
        raise ManagedPairMaterializationError(
            "reference/Papaya default download-attempt policy drift"
        )
    if isinstance(attempts, bool) or not isinstance(attempts, int) or attempts < 1:
        raise ManagedPairMaterializationError(
            "attempts must be an integer >= 1"
        )

    output = _new_external_workspace(output_dir, sei_source_dir)

    source_receipt = papaya_capture.require_git_checkout(
        sei_source_dir,
        source_sha,
        label="SEI source",
    )
    if (
        source_receipt.get("git_sha") != source_sha
        or source_receipt.get("clean") is not True
    ):
        raise ManagedPairMaterializationError(
            "SEI source checkout receipt drift"
        )

    # Bind the manifest bytes whose digests will be retained to the exact
    # objects used for validation/materialization.
    _require_raw_binding(
        reference_manifest,
        reference_manifest_raw,
        "reference transport manifest",
    )
    _require_raw_binding(
        papaya_manifest,
        papaya_manifest_raw,
        "Papaya transport manifest",
    )

    # Validate all transport contracts before creating the workspace or
    # performing any network transfer.
    reference_materializer.validate_manifest(reference_manifest)
    papaya_entries = papaya_materializer.validate_manifest(papaya_manifest)
    tokenizer_relative = _attested_tokenizer_relative_path(papaya_entries)

    if (
        materialize_runtime_environment
        and runtime_wheelhouse_dir is None
    ):
        raise ManagedPairMaterializationError(
            "runtime environment materialization requires runtime wheelhouse"
        )

    wheelhouse = {"provided": False}
    if runtime_wheelhouse_dir is not None:
        if (
            runtime_wheelhouse_manifest is None
            or runtime_wheelhouse_manifest_raw is None
        ):
            raise ManagedPairMaterializationError(
                "runtime wheelhouse manifest is required with wheelhouse dir"
            )
        _require_raw_binding(
            runtime_wheelhouse_manifest,
            runtime_wheelhouse_manifest_raw,
            "runtime dependency wheelhouse manifest",
        )
        try:
            wheelhouse_verification = wheelhouse_verifier.verify_wheelhouse(
                runtime_wheelhouse_manifest,
                runtime_wheelhouse_dir,
            )
        except Exception as exc:
            raise ManagedPairMaterializationError(
                f"runtime wheelhouse verification failed: {exc}"
            ) from exc
        if wheelhouse_verification.get("valid") is not True:
            raise ManagedPairMaterializationError(
                "runtime wheelhouse verification did not return valid=true"
            )
        wheelhouse = {
            "provided": True,
            "manifest_sha256": _sha256_bytes(
                runtime_wheelhouse_manifest_raw
            ),
            "verification": wheelhouse_verification,
            "external_path_retained": False,
        }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.mkdir()
    reference_dir = output / REFERENCE_DIR
    candidate_dir = output / PAPAYA_CANDIDATE_DIR
    overlay_dir = output / PAPAYA_OVERLAY_DIR
    runtime_env_dir = output / RUNTIME_ENV_DIR

    try:
        runtime_environment = {"provided": False}
        if materialize_runtime_environment:
            if (
                runtime_wheelhouse_manifest is None
                or runtime_wheelhouse_manifest_raw is None
                or runtime_wheelhouse_dir is None
            ):
                raise ManagedPairMaterializationError(
                    "runtime environment materialization inputs missing"
                )
            runtime_receipt = runtime_materializer.materialize_environment(
                runtime_wheelhouse_manifest,
                runtime_wheelhouse_manifest_raw,
                runtime_wheelhouse_dir,
                runtime_env_dir,
            )
            if (
                runtime_receipt.get("schema")
                != runtime_materializer.SCHEMA
                or runtime_receipt.get("status")
                != "materialized-and-verified"
            ):
                raise ManagedPairMaterializationError(
                    "managed runtime environment receipt drift"
                )
            expected_wheelhouse_manifest_sha = _sha256_bytes(
                runtime_wheelhouse_manifest_raw
            )
            if (
                runtime_receipt.get("wheelhouse_manifest_sha256")
                != expected_wheelhouse_manifest_sha
            ):
                raise ManagedPairMaterializationError(
                    "managed runtime wheelhouse-manifest binding drift"
                )
            runtime_wheelhouse = runtime_receipt.get("wheelhouse")
            if (
                not isinstance(runtime_wheelhouse, dict)
                or runtime_wheelhouse.get("valid") is not True
            ):
                raise ManagedPairMaterializationError(
                    "managed runtime wheelhouse verification missing"
                )
            runtime_install = runtime_receipt.get("install")
            if (
                not isinstance(runtime_install, dict)
                or runtime_install.get("returncode") != 0
            ):
                raise ManagedPairMaterializationError(
                    "managed runtime install receipt drift"
                )
            runtime_verification = runtime_receipt.get(
                "environment_verification"
            )
            if (
                not isinstance(runtime_verification, dict)
                or runtime_verification.get("valid") is not True
            ):
                raise ManagedPairMaterializationError(
                    "managed runtime environment verification missing"
                )
            runtime_scope = runtime_receipt.get("scope")
            if not isinstance(runtime_scope, dict):
                raise ManagedPairMaterializationError(
                    "managed runtime environment scope missing"
                )
            if (
                runtime_scope.get(
                    "transported_wheel_installation_origin_attested"
                )
                is not True
            ):
                raise ManagedPairMaterializationError(
                    "managed runtime transported-wheel origin missing"
                )
            if (
                runtime_scope.get("runtime_installation_origin_attested")
                is not False
            ):
                raise ManagedPairMaterializationError(
                    "managed runtime overclaims full installation origin"
                )
            runtime_environment = {
                "provided": True,
                "receipt": runtime_receipt,
            }

        reference_receipt = (
            reference_materializer.materialize_reference_model(
                reference_manifest,
                reference_transport,
                reference_dir,
                timeout=timeout,
                attempts=attempts,
            )
        )
        reference_summary = _portable_materialization_summary(
            reference_receipt,
            expected_schema=reference_materializer.SCHEMA,
            label="reference materialization",
        )

        papaya_receipt = papaya_materializer.materialize_papaya_candidate(
            papaya_manifest,
            candidate_dir,
            timeout=timeout,
            attempts=attempts,
        )
        papaya_summary = _portable_materialization_summary(
            papaya_receipt,
            expected_schema=papaya_materializer.SCHEMA,
            label="Papaya candidate materialization",
        )

        tokenizer_path = candidate_dir / tokenizer_relative
        overlay_receipt = overlay.prepare_overlay(
            candidate_dir,
            tokenizer_path,
            overlay_dir,
        )
        overlay_verification = overlay.verify_prepared_overlay(overlay_dir)
        if overlay_verification.get("valid") is not True:
            raise ManagedPairMaterializationError(
                "Papaya overlay verification did not return valid=true"
            )
        if overlay_receipt.get("schema") != overlay.SCHEMA:
            raise ManagedPairMaterializationError(
                "Papaya overlay receipt schema drift"
            )
        workspace_binding = _verify_overlay_workspace_binding(
            candidate_dir,
            overlay_dir,
        )

        receipt = {
            "schema": SCHEMA,
            "status": "ready-for-managed-pair-preflight",
            "source": {
                "git_sha": source_sha,
                "clean": True,
            },
            "layout": {
                "reference_model_dir": REFERENCE_DIR,
                "papaya_candidate_dir": PAPAYA_CANDIDATE_DIR,
                "papaya_overlay_dir": PAPAYA_OVERLAY_DIR,
                "runtime_environment_dir": (
                    RUNTIME_ENV_DIR
                    if materialize_runtime_environment
                    else None
                ),
            },
            "contracts": {
                "reference_transport_manifest_sha256": _sha256_bytes(
                    reference_manifest_raw
                ),
                "reference_transport": reference_transport,
                "papaya_transport_manifest_sha256": _sha256_bytes(
                    papaya_manifest_raw
                ),
                "papaya_transport": papaya_materializer.TRANSPORT_ID,
            },
            "download_policy": {
                "attempts_per_file": attempts,
                "restart_from_zero": True,
                "retryable_failures": "transport/read only",
                "integrity_failures_retried": False,
            },
            "reference": reference_summary,
            "papaya_candidate": papaya_summary,
            "papaya_overlay": {
                "schema": overlay.SCHEMA,
                "receipt": overlay_receipt,
                "verification": overlay_verification,
                "workspace_binding": workspace_binding,
            },
            "runtime_wheelhouse": wheelhouse,
            "runtime_environment": runtime_environment,
            "scope": {
                "reference_model_bytes_materialized": True,
                "reference_model_directory_verified": True,
                "papaya_candidate_bytes_materialized": True,
                "papaya_candidate_inputs_verified": True,
                "papaya_compatibility_overlay_prepared": True,
                "papaya_compatibility_overlay_verified": True,
                "workspace_relocatable": False,
                "runtime_wheelhouse_verified": (
                    runtime_wheelhouse_dir is not None
                ),
                "runtime_environment_materialized": (
                    materialize_runtime_environment
                ),
                "transported_wheel_installation_origin_attested": (
                    materialize_runtime_environment
                ),
                "runtime_installation_origin_attested": False,
                "model_weights_loaded": False,
                "live_reference_inference": False,
                "live_papaya_inference": False,
                "numeric_difference_observed": False,
                "numeric_parity_decision_observed": False,
                "task_quality": False,
                "calibration_validity": False,
                "shipping_decision": False,
            },
        }
        _write_receipt(output / RECEIPT_FILE, receipt)
        return receipt
    except BaseException:
        shutil.rmtree(output, ignore_errors=True)
        raise


def main(argv: list[str] | None = None) -> int:
    here = Path(__file__).resolve().parent
    default_sei_root = here.parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-git-sha", required=True)
    parser.add_argument("--sei-source-dir", type=Path, default=default_sei_root)
    parser.add_argument(
        "--reference-transport-manifest",
        type=Path,
        default=here / "reference_model_transport.v1.json",
    )
    parser.add_argument(
        "--reference-transport",
        choices=(
            reference_materializer.HF_ID,
            reference_materializer.MIRROR_ID,
        ),
        default=reference_materializer.HF_ID,
    )
    parser.add_argument(
        "--papaya-transport-manifest",
        type=Path,
        default=here / "papaya_candidate_transport.v1.json",
    )
    parser.add_argument("--runtime-wheelhouse-dir", type=Path)
    parser.add_argument(
        "--materialize-runtime-environment",
        action="store_true",
    )
    parser.add_argument(
        "--runtime-wheelhouse-manifest",
        type=Path,
        default=here / "runtime_dependency_wheelhouse.v1.json",
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--timeout", type=float, default=300.0)
    parser.add_argument(
        "--attempts",
        type=int,
        default=DEFAULT_DOWNLOAD_ATTEMPTS,
    )
    args = parser.parse_args(argv)

    try:
        _require_script_source_binding(here, args.sei_source_dir)
        reference_manifest, reference_raw = _load_json_bytes(
            args.reference_transport_manifest,
            "reference transport manifest",
        )
        papaya_manifest, papaya_raw = _load_json_bytes(
            args.papaya_transport_manifest,
            "Papaya transport manifest",
        )
        wheelhouse_manifest = None
        wheelhouse_raw = None
        if args.runtime_wheelhouse_dir is not None:
            wheelhouse_manifest, wheelhouse_raw = _load_json_bytes(
                args.runtime_wheelhouse_manifest,
                "runtime dependency wheelhouse manifest",
            )
        receipt = prepare_workspace(
            source_sha=args.source_git_sha,
            sei_source_dir=args.sei_source_dir.resolve(),
            reference_manifest=reference_manifest,
            reference_manifest_raw=reference_raw,
            reference_transport=args.reference_transport,
            papaya_manifest=papaya_manifest,
            papaya_manifest_raw=papaya_raw,
            output_dir=args.output_dir,
            timeout=args.timeout,
            attempts=args.attempts,
            runtime_wheelhouse_dir=(
                args.runtime_wheelhouse_dir.resolve()
                if args.runtime_wheelhouse_dir is not None
                else None
            ),
            runtime_wheelhouse_manifest=wheelhouse_manifest,
            runtime_wheelhouse_manifest_raw=wheelhouse_raw,
            materialize_runtime_environment=(
                args.materialize_runtime_environment
            ),
        )
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(
        json.dumps(
            {
                "status": receipt["status"],
                "output_dir": str(args.output_dir.expanduser().resolve()),
                "receipt": RECEIPT_FILE,
                "model_weights_loaded": False,
                "live_inference": False,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
