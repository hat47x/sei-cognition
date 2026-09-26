#!/usr/bin/env python3
"""Prepare a fail-closed Papaya compatibility overlay for SEI parity evaluation.

The overlay is intentionally not "Papaya as-is". It keeps the pinned Papaya
runtime plus the attested Q8 backbone/head and tokenizer byte identity, but
replaces the raw config with a derived config whose temperatures are clamped
with the pinned Python Laya 0.3.20 policy. No inference or numeric-parity claim
is made by preparing the directory.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import shutil
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SCHEMA = "sei.local-typed-comparator-papaya-compat-overlay/v1"

PAPAYA_REPOSITORY = "m0rphtail/papaya"
PAPAYA_REVISION = "a76bc99bddafdac32863b2edc5319773e0cd3532"
PAPAYA_RUNTIME_BLOBS = {
    "runtime.py": "b3999b7f1e02d4761ffba63b7f846b210f3e27dd",
    "head.py": "a38529ca7a07c130460754200e834bfd3f1c3d5b",
    "sequences.py": "f21139970d6d288114213db8f917f0cead9c082f",
}

CANDIDATE_REPOSITORY = "fr0stbit3/laya-typed-decisions-gguf"
CANDIDATE_REVISION = "54ec2dbb58aad9e3c74782cb2feb5801f72b13d0"
CANDIDATE_TOKENIZER_REVISION = "75300646cddbac2b47409fc1ca839c95bec004c8"
CANDIDATE_TOKENIZER_GIT_BLOB = "2f4d8583e507b7466d2490e2d6c045647a822698"
REFERENCE_REPOSITORY = "convaiinnovations/laya-typed-decisions"
REFERENCE_REVISION = "f9ab0b228f0fc0f14d873dbc99038f135c2da1b2"
REFERENCE_TOKENIZER_SHA256 = (
    "6c8aaa9a542084f2457eab775d4eeb51f92a70c0fd9de28d5edb0ddec3c08d30"
)
REFERENCE_TOKENIZER_BYTES = 3_583_228
REFERENCE_LAYA_REPOSITORY = "NandhaKishorM/laya"
REFERENCE_LAYA_REVISION = "23a17522aa4942da6cce53a995a275760320b691"
REFERENCE_COMMON_BLOB = "6c4c426e64eb9660c97d40bc64c227e8c7e71361"
TEMP_MIN = 0.5
TEMP_MAX = 5.0
EXPECTED_COMPAT_CONFIG_BYTES = 832
EXPECTED_COMPAT_CONFIG_SHA256 = (
    "279207d55fefd56b2c6738dd141a3e10ab1d3f46b755c43faee42364ce1cc892"
)
SEQUENCE_REPLAY_SCHEMA = "sei.local-typed-comparator-papaya-sequence-replay/v1"
SEQUENCE_REPLAY_MERGE = "1debf7180fd00a49bc90c1a26bb78422a55d3cb2"

EXPECTED_CURRENT_CHANGE = {
    "path": "temperature_by_options.choice:11+",
    "raw": 0.10058280825614929,
    "applied": 0.5,
}


class OverlayError(ValueError):
    pass


@dataclass(frozen=True)
class ArtifactSpec:
    relative_path: str
    bytes: int
    sha256: str
    role: str


DEFAULT_ARTIFACTS = (
    ArtifactSpec(
        "laya-typed-decisions-Q8_0.gguf",
        421_407_968,
        "84f16d7b0b0a07343e7a6f8d8bd7ae9633aa0372d55621e2242d0ed9a0aca28c",
        "q8_backbone",
    ),
    ArtifactSpec(
        "laya-typed-decisions-head.safetensors",
        106_052_952,
        "f115a16370df62e24a88aded4ef10d6542d2cdec9439df86d3aea3689f13ca44",
        "decision_head",
    ),
    ArtifactSpec(
        "rl_agent_config.json",
        847,
        "ebf0cd524d92342a6be5e48e9fca3d7c2babfb5a56ccd79d2171ef5d8c7f7be8",
        "raw_config",
    ),
    ArtifactSpec(
        "tokenizer_config.json",
        337,
        "08d4cf3ac4dca381759441b85b91a6d40e688471dcd33d15d6649eb0a9a854d1",
        "tokenizer_config",
    ),
)
ATTESTED_TOKENIZER_SPEC = ArtifactSpec(
    "tokenizer.json",
    REFERENCE_TOKENIZER_BYTES,
    REFERENCE_TOKENIZER_SHA256,
    "attested_tokenizer",
)


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _validate_sha256(value: str, field: str) -> None:
    if len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
        raise OverlayError(f"{field} must be lowercase SHA-256 hex")


def verify_artifact(path: Path, spec: ArtifactSpec) -> dict[str, Any]:
    if not path.is_file():
        raise OverlayError(f"missing {spec.role}: {path}")
    actual_size = path.stat().st_size
    if actual_size != spec.bytes:
        raise OverlayError(
            f"{spec.role} byte-size mismatch: expected {spec.bytes}, got {actual_size}"
        )
    _validate_sha256(spec.sha256, f"{spec.role}.sha256")
    actual_sha = _sha256_file(path)
    if actual_sha != spec.sha256:
        raise OverlayError(
            f"{spec.role} SHA-256 mismatch: expected {spec.sha256}, got {actual_sha}"
        )
    return {
        "role": spec.role,
        "bytes": actual_size,
        "sha256": actual_sha,
    }


def clamp_temperature(value: Any, lo: float = TEMP_MIN, hi: float = TEMP_MAX) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 1.0
    if not math.isfinite(number):
        return 1.0
    return min(hi, max(lo, number))


def derive_compat_config(config: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Return a deep JSON copy with only Laya temperature application semantics changed."""
    derived = json.loads(json.dumps(config, ensure_ascii=False))
    changes: list[dict[str, Any]] = []

    raw_temperature = derived.get("temperature", [1.0, 1.0, 1.0])
    if not isinstance(raw_temperature, list):
        raise OverlayError("temperature must be an array")
    applied_temperature = []
    for index, raw in enumerate(raw_temperature):
        applied = clamp_temperature(raw)
        applied_temperature.append(applied)
        try:
            same = float(raw) == applied
        except (TypeError, ValueError):
            same = False
        if not same:
            changes.append(
                {"path": f"temperature[{index}]", "raw": raw, "applied": applied}
            )
    derived["temperature"] = applied_temperature

    raw_buckets = derived.get("temperature_by_options", {})
    if not isinstance(raw_buckets, dict):
        raise OverlayError("temperature_by_options must be an object")
    applied_buckets = {}
    for key, raw in raw_buckets.items():
        applied = clamp_temperature(raw)
        applied_buckets[key] = applied
        try:
            same = float(raw) == applied
        except (TypeError, ValueError):
            same = False
        if not same:
            changes.append(
                {
                    "path": f"temperature_by_options.{key}",
                    "raw": raw,
                    "applied": applied,
                }
            )
    derived["temperature_by_options"] = applied_buckets
    return derived, changes


def _compat_config_bytes(config: dict[str, Any]) -> bytes:
    return (json.dumps(config, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def inspect_overlay_inputs(
    candidate_dir: Path,
    attested_tokenizer: Path,
    *,
    artifact_specs: tuple[ArtifactSpec, ...] = DEFAULT_ARTIFACTS,
    attested_tokenizer_spec: ArtifactSpec = ATTESTED_TOKENIZER_SPEC,
    enforce_current_change: bool = True,
) -> tuple[dict[str, Any], bytes]:
    candidate_dir = candidate_dir.resolve()
    attested_tokenizer = attested_tokenizer.resolve()

    candidate_artifacts: dict[str, dict[str, Any]] = {}
    for spec in artifact_specs:
        candidate_artifacts[spec.role] = verify_artifact(
            candidate_dir / spec.relative_path, spec
        )
    tokenizer_observation = verify_artifact(
        attested_tokenizer, attested_tokenizer_spec
    )

    raw_config_path = candidate_dir / next(
        spec.relative_path for spec in artifact_specs if spec.role == "raw_config"
    )
    try:
        raw_config = json.loads(raw_config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise OverlayError(f"cannot parse raw config: {raw_config_path}") from exc
    if not isinstance(raw_config, dict):
        raise OverlayError("raw config root must be an object")

    compat_config, changes = derive_compat_config(raw_config)
    if enforce_current_change and changes != [EXPECTED_CURRENT_CHANGE]:
        raise OverlayError(
            "current candidate temperature delta changed; expected only "
            f"{EXPECTED_CURRENT_CHANGE!r}, got {changes!r}"
        )
    compat_bytes = _compat_config_bytes(compat_config)
    compat_sha = hashlib.sha256(compat_bytes).hexdigest()
    if len(compat_bytes) != EXPECTED_COMPAT_CONFIG_BYTES:
        raise OverlayError(
            f"compat config byte-size drift: expected {EXPECTED_COMPAT_CONFIG_BYTES}, "
            f"got {len(compat_bytes)}"
        )
    if compat_sha != EXPECTED_COMPAT_CONFIG_SHA256:
        raise OverlayError(
            f"compat config SHA-256 drift: expected {EXPECTED_COMPAT_CONFIG_SHA256}, "
            f"got {compat_sha}"
        )

    receipt = {
        "schema": SCHEMA,
        "papaya_runtime": {
            "repository": PAPAYA_REPOSITORY,
            "revision": PAPAYA_REVISION,
            "source_blobs": PAPAYA_RUNTIME_BLOBS,
            "source_verified_by_overlay": False,
        },
        "candidate_bundle": {
            "repository": CANDIDATE_REPOSITORY,
            "revision": CANDIDATE_REVISION,
            "artifacts": candidate_artifacts,
        },
        "tokenizer_identity": {
            "candidate_revision": CANDIDATE_TOKENIZER_REVISION,
            "candidate_git_blob": CANDIDATE_TOKENIZER_GIT_BLOB,
            "reference_repository": REFERENCE_REPOSITORY,
            "reference_revision": REFERENCE_REVISION,
            "bytes": tokenizer_observation["bytes"],
            "sha256": tokenizer_observation["sha256"],
            "candidate_byte_identity_attested": True,
            "staged_bytes_verified": True,
        },
        "sequence_replay_evidence": {
            "schema": SEQUENCE_REPLAY_SCHEMA,
            "merge_commit": SEQUENCE_REPLAY_MERGE,
            "frozen_four_case_token_marker_parity": True,
        },
        "temperature_policy": {
            "source_repository": REFERENCE_LAYA_REPOSITORY,
            "source_revision": REFERENCE_LAYA_REVISION,
            "source_common_blob": REFERENCE_COMMON_BLOB,
            "min": TEMP_MIN,
            "max": TEMP_MAX,
            "changes": changes,
            "compat_config_sha256": compat_sha,
            "compat_config_bytes": len(compat_bytes),
            "current_candidate_delta_exactly_expected": True,
        },
        "scope": {
            "upstream_papaya_unmodified": False,
            "runtime_source_verified": False,
            "tokenizer_byte_identity_preserved": True,
            "frozen_token_marker_parity_precondition": True,
            "temperature_semantics_aligned_by_construction": True,
            "encoder_numeric_parity": False,
            "head_numeric_parity": False,
            "full_numeric_parity": False,
            "live_inference": False,
            "reference_provider_promotion": False,
        },
    }
    return receipt, compat_bytes


def _symlink_file(source: Path, destination: Path) -> None:
    destination.symlink_to(source.resolve())


def verify_prepared_overlay(
    output_dir: Path,
    *,
    artifact_specs: tuple[ArtifactSpec, ...] = DEFAULT_ARTIFACTS,
    attested_tokenizer_spec: ArtifactSpec = ATTESTED_TOKENIZER_SPEC,
) -> dict[str, Any]:
    """Re-hash the staged overlay so symlink targets cannot drift silently."""
    output_dir = output_dir.resolve()
    if not output_dir.is_dir():
        raise OverlayError(f"overlay directory does not exist: {output_dir}")

    receipt_path = output_dir / "sei_compat_overlay_receipt.json"
    try:
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise OverlayError(f"cannot parse overlay receipt: {receipt_path}") from exc
    if not isinstance(receipt, dict) or receipt.get("schema") != SCHEMA:
        raise OverlayError("overlay receipt schema drift")

    runtime = receipt.get("papaya_runtime")
    if not isinstance(runtime, dict):
        raise OverlayError("papaya_runtime receipt must be an object")
    if runtime.get("repository") != PAPAYA_REPOSITORY:
        raise OverlayError("Papaya runtime repository drift")
    if runtime.get("revision") != PAPAYA_REVISION:
        raise OverlayError("Papaya runtime revision drift")
    if runtime.get("source_blobs") != PAPAYA_RUNTIME_BLOBS:
        raise OverlayError("Papaya runtime source-blob drift")
    if runtime.get("source_verified_by_overlay") is not False:
        raise OverlayError("overlay must not claim local Papaya runtime source verification")

    by_role = {spec.role: spec for spec in artifact_specs}
    required_roles = {"q8_backbone", "decision_head", "raw_config", "tokenizer_config"}
    if set(by_role) != required_roles:
        raise OverlayError(
            f"artifact role set drift: expected {sorted(required_roles)}, "
            f"got {sorted(by_role)}"
        )

    observations: dict[str, dict[str, Any]] = {}
    for role in ("q8_backbone", "decision_head"):
        spec = by_role[role]
        observations[role] = verify_artifact(
            output_dir / spec.relative_path, spec
        )

    tokcfg = by_role["tokenizer_config"]
    observations["tokenizer_config"] = verify_artifact(
        output_dir / "tokenizer" / "tokenizer_config.json",
        ArtifactSpec(
            "tokenizer/tokenizer_config.json",
            tokcfg.bytes,
            tokcfg.sha256,
            "tokenizer_config",
        ),
    )
    observations["attested_tokenizer"] = verify_artifact(
        output_dir / "tokenizer" / "tokenizer.json",
        ArtifactSpec(
            "tokenizer/tokenizer.json",
            attested_tokenizer_spec.bytes,
            attested_tokenizer_spec.sha256,
            "attested_tokenizer",
        ),
    )
    observations["compat_config"] = verify_artifact(
        output_dir / "rl_agent_config.json",
        ArtifactSpec(
            "rl_agent_config.json",
            EXPECTED_COMPAT_CONFIG_BYTES,
            EXPECTED_COMPAT_CONFIG_SHA256,
            "compat_config",
        ),
    )

    candidate_bundle = receipt.get("candidate_bundle")
    if not isinstance(candidate_bundle, dict):
        raise OverlayError("candidate_bundle receipt must be an object")
    if candidate_bundle.get("repository") != CANDIDATE_REPOSITORY:
        raise OverlayError("candidate repository drift")
    if candidate_bundle.get("revision") != CANDIDATE_REVISION:
        raise OverlayError("candidate revision drift")
    recorded = candidate_bundle.get("artifacts")
    if not isinstance(recorded, dict):
        raise OverlayError("candidate artifact receipt must be an object")
    for role in ("q8_backbone", "decision_head", "tokenizer_config"):
        observed = observations[role]
        source_record = recorded.get(role)
        if not isinstance(source_record, dict):
            raise OverlayError(f"missing candidate artifact receipt: {role}")
        if source_record.get("bytes") != observed["bytes"]:
            raise OverlayError(f"{role} staged/source byte-size mismatch")
        if source_record.get("sha256") != observed["sha256"]:
            raise OverlayError(f"{role} staged/source SHA-256 mismatch")

    tokenizer_identity = receipt.get("tokenizer_identity")
    if not isinstance(tokenizer_identity, dict):
        raise OverlayError("tokenizer_identity receipt must be an object")
    if tokenizer_identity.get("candidate_revision") != CANDIDATE_TOKENIZER_REVISION:
        raise OverlayError("candidate tokenizer revision drift")
    if tokenizer_identity.get("candidate_git_blob") != CANDIDATE_TOKENIZER_GIT_BLOB:
        raise OverlayError("candidate tokenizer Git blob drift")
    if tokenizer_identity.get("bytes") != observations["attested_tokenizer"]["bytes"]:
        raise OverlayError("staged tokenizer byte-size mismatch")
    if tokenizer_identity.get("sha256") != observations["attested_tokenizer"]["sha256"]:
        raise OverlayError("staged tokenizer SHA-256 mismatch")

    policy = receipt.get("temperature_policy")
    if not isinstance(policy, dict):
        raise OverlayError("temperature_policy receipt must be an object")
    if policy.get("compat_config_bytes") != EXPECTED_COMPAT_CONFIG_BYTES:
        raise OverlayError("receipt compat config byte-size drift")
    if policy.get("compat_config_sha256") != EXPECTED_COMPAT_CONFIG_SHA256:
        raise OverlayError("receipt compat config SHA-256 drift")
    if policy.get("changes") != [EXPECTED_CURRENT_CHANGE]:
        raise OverlayError("receipt temperature delta drift")

    scope = receipt.get("scope")
    if not isinstance(scope, dict):
        raise OverlayError("scope receipt must be an object")
    if scope.get("runtime_source_verified") is not False:
        raise OverlayError("overlay scope must keep runtime_source_verified=false")
    for field in (
        "encoder_numeric_parity",
        "head_numeric_parity",
        "full_numeric_parity",
        "live_inference",
        "reference_provider_promotion",
    ):
        if scope.get(field) is not False:
            raise OverlayError(f"overlay scope overclaims {field}")

    return {
        "valid": True,
        "schema": SCHEMA,
        "runtime_source_verified": False,
        "staged_artifacts": observations,
    }


def prepare_overlay(
    candidate_dir: Path,
    attested_tokenizer: Path,
    output_dir: Path,
    *,
    artifact_specs: tuple[ArtifactSpec, ...] = DEFAULT_ARTIFACTS,
    attested_tokenizer_spec: ArtifactSpec = ATTESTED_TOKENIZER_SPEC,
    enforce_current_change: bool = True,
) -> dict[str, Any]:
    candidate_dir = candidate_dir.resolve()
    attested_tokenizer = attested_tokenizer.resolve()
    output_dir = output_dir.resolve()

    if output_dir.exists():
        raise OverlayError(f"output directory already exists: {output_dir}")

    receipt, compat_bytes = inspect_overlay_inputs(
        candidate_dir,
        attested_tokenizer,
        artifact_specs=artifact_specs,
        attested_tokenizer_spec=attested_tokenizer_spec,
        enforce_current_change=enforce_current_change,
    )

    output_dir.parent.mkdir(parents=True, exist_ok=True)
    temp_path = Path(
        tempfile.mkdtemp(prefix=".papaya-compat-overlay-", dir=output_dir.parent)
    )
    try:
        tokenizer_dir = temp_path / "tokenizer"
        tokenizer_dir.mkdir()

        by_role = {spec.role: spec for spec in artifact_specs}
        for role in ("q8_backbone", "decision_head"):
            spec = by_role[role]
            _symlink_file(candidate_dir / spec.relative_path, temp_path / spec.relative_path)

        tokenizer_config = by_role["tokenizer_config"]
        shutil.copyfile(
            candidate_dir / tokenizer_config.relative_path,
            tokenizer_dir / "tokenizer_config.json",
        )
        shutil.copyfile(attested_tokenizer, tokenizer_dir / "tokenizer.json")
        (temp_path / "rl_agent_config.json").write_bytes(compat_bytes)

        receipt_path = temp_path / "sei_compat_overlay_receipt.json"
        receipt_path.write_text(
            json.dumps(receipt, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        verify_prepared_overlay(
            temp_path,
            artifact_specs=artifact_specs,
            attested_tokenizer_spec=attested_tokenizer_spec,
        )
        os.replace(temp_path, output_dir)
    except BaseException:
        shutil.rmtree(temp_path, ignore_errors=True)
        raise

    return receipt


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("candidate_dir", type=Path, nargs="?")
    parser.add_argument("attested_tokenizer", type=Path, nargs="?")
    parser.add_argument("output_dir", type=Path, nargs="?")
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="verify inputs and print the overlay receipt without creating a directory",
    )
    parser.add_argument(
        "--verify-staged",
        type=Path,
        help="re-hash an already prepared overlay directory before execution",
    )
    args = parser.parse_args(argv)

    try:
        if args.verify_staged is not None:
            if any(
                value is not None
                for value in (
                    args.candidate_dir,
                    args.attested_tokenizer,
                    args.output_dir,
                )
            ) or args.verify_only:
                parser.error("--verify-staged cannot be combined with other modes")
            receipt = verify_prepared_overlay(args.verify_staged)
        else:
            if args.candidate_dir is None or args.attested_tokenizer is None:
                parser.error("candidate_dir and attested_tokenizer are required")
            if args.verify_only:
                receipt, _ = inspect_overlay_inputs(
                    args.candidate_dir, args.attested_tokenizer
                )
            else:
                if args.output_dir is None:
                    parser.error("output_dir is required unless --verify-only is used")
                receipt = prepare_overlay(
                    args.candidate_dir, args.attested_tokenizer, args.output_dir
                )
    except OverlayError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
