#!/usr/bin/env python3
"""Verify the exact standalone Laya typed-decisions reference model directory.

The directory contract is bound to
convaiinnovations/laya-typed-decisions@f9ab0b228f0fc0f14d873dbc99038f135c2da1b2.
It covers every file the pinned Laya 0.3.20 Agent consumes for this standalone
checkpoint. It does not claim that any HTTP endpoint has loaded the directory.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SCHEMA = "sei.local-typed-comparator-reference-model-directory-attestation/v1"
SOURCE_REPOSITORY = "convaiinnovations/laya-typed-decisions"
SOURCE_REVISION = "f9ab0b228f0fc0f14d873dbc99038f135c2da1b2"
INDEPENDENT_REPOSITORY = "mizorewww/laya-coreml"
INDEPENDENT_REVISION = "4619e0483f07adf39068532e85b42ec2347edb83"
INDEPENDENT_PATH = "benchmarks/results/validation-typed-enumerated-cpu_gpu.json"
INDEPENDENT_BLOB = "3c8aa8975d70fa30117b72bdab11450bb46b85b0"
LAYA_REPOSITORY = "NandhaKishorM/laya"
LAYA_REVISION = "23a17522aa4942da6cce53a995a275760320b691"
LAYA_AGENT_BLOB = "b0fb78a75a7dc51e971b15409840c44871455f31"
LAYA_COMMON_BLOB = "6c4c426e64eb9660c97d40bc64c227e8c7e71361"
RAW_CHOICE_11_PLUS = 0.10058280825614929
APPLIED_CHOICE_11_PLUS = 0.5


class ReferenceModelDirectoryError(ValueError):
    pass


@dataclass(frozen=True)
class FileSpec:
    relative_path: str
    bytes: int
    sha256: str


DEFAULT_FILE_SPECS = (
    FileSpec(
        "model.safetensors",
        842_609_220,
        "4fa56de72383a9d3efa9cfa78955733c81b9fc8067a587ca4beb82c78107a24e",
    ),
    FileSpec(
        "encoder/config.json",
        2_084,
        "5268d24ad3b77c8151de5dcb0762ba4391619aad9ab0bda33e36fb083cfeae6d",
    ),
    FileSpec(
        "rl_agent_config.json",
        847,
        "ebf0cd524d92342a6be5e48e9fca3d7c2babfb5a56ccd79d2171ef5d8c7f7be8",
    ),
    FileSpec(
        "tokenizer/tokenizer.json",
        3_583_228,
        "6c8aaa9a542084f2457eab775d4eeb51f92a70c0fd9de28d5edb0ddec3c08d30",
    ),
    FileSpec(
        "tokenizer/tokenizer_config.json",
        337,
        "08d4cf3ac4dca381759441b85b91a6d40e688471dcd33d15d6649eb0a9a854d1",
    ),
)


def sha256_file(path: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(block)
            size += len(block)
    return digest.hexdigest(), size


def _object(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ReferenceModelDirectoryError(f"{field} must be an object")
    return value


def validate_attestation(packet: dict[str, Any]) -> None:
    if packet.get("schema") != SCHEMA:
        raise ReferenceModelDirectoryError(f"schema must be {SCHEMA}")

    source = _object(packet.get("source_checkpoint"), "source_checkpoint")
    if source.get("repository") != SOURCE_REPOSITORY:
        raise ReferenceModelDirectoryError("source repository drift")
    if source.get("revision") != SOURCE_REVISION:
        raise ReferenceModelDirectoryError("source revision drift")

    files = _object(packet.get("runtime_consumed_files"), "runtime_consumed_files")
    if set(files) != {spec.relative_path for spec in DEFAULT_FILE_SPECS}:
        raise ReferenceModelDirectoryError("runtime-consumed file set drift")
    for spec in DEFAULT_FILE_SPECS:
        value = _object(files.get(spec.relative_path), spec.relative_path)
        if value.get("bytes") != spec.bytes:
            raise ReferenceModelDirectoryError(
                f"{spec.relative_path}: byte-size drift"
            )
        if value.get("sha256") != spec.sha256:
            raise ReferenceModelDirectoryError(
                f"{spec.relative_path}: SHA-256 drift"
            )

    independent = _object(
        packet.get("independent_manifest"), "independent_manifest"
    )
    expected_independent = {
        "repository": INDEPENDENT_REPOSITORY,
        "revision": INDEPENDENT_REVISION,
        "path": INDEPENDENT_PATH,
        "git_blob": INDEPENDENT_BLOB,
        "binds_source_revision": True,
        "binds_source_weights_sha256": True,
        "binds_ancillary_file_bytes_and_sha256": True,
    }
    for field, expected in expected_independent.items():
        if independent.get(field) != expected:
            raise ReferenceModelDirectoryError(
                f"independent_manifest.{field} drift"
            )

    runtime = _object(packet.get("laya_runtime_semantics"), "laya_runtime_semantics")
    expected_runtime = {
        "repository": LAYA_REPOSITORY,
        "revision": LAYA_REVISION,
        "agent_git_blob": LAYA_AGENT_BLOB,
        "common_git_blob": LAYA_COMMON_BLOB,
        "tokenizer_config_expected_to_be_rewritten": False,
        "tokenizer_class": "PreTrainedTokenizerFast",
        "raw_choice_11_plus_temperature": RAW_CHOICE_11_PLUS,
        "applied_choice_11_plus_temperature": APPLIED_CHOICE_11_PLUS,
    }
    for field, expected in expected_runtime.items():
        if runtime.get(field) != expected:
            raise ReferenceModelDirectoryError(
                f"laya_runtime_semantics.{field} drift"
            )

    scope = _object(packet.get("scope"), "scope")
    if scope.get("reference_model_directory_byte_contract_attested") is not True:
        raise ReferenceModelDirectoryError(
            "reference model directory byte contract must be attested"
        )
    for field in (
        "endpoint_loaded_exact_directory_attested",
        "endpoint_exact_runtime_wheel_attested",
        "live_reference_inference",
        "numeric_parity_with_papaya",
    ):
        if scope.get(field) is not False:
            raise ReferenceModelDirectoryError(f"scope.{field} must remain false")


def verify_model_directory(
    root: Path,
    *,
    specs: tuple[FileSpec, ...] = DEFAULT_FILE_SPECS,
) -> dict[str, Any]:
    root = root.resolve()
    if not root.is_dir():
        raise ReferenceModelDirectoryError(
            f"reference model directory not found: {root}"
        )

    observed: dict[str, dict[str, Any]] = {}
    for spec in specs:
        path = root / spec.relative_path
        if not path.is_file():
            raise ReferenceModelDirectoryError(
                f"missing reference model file: {spec.relative_path}"
            )
        digest, size = sha256_file(path)
        if size != spec.bytes:
            raise ReferenceModelDirectoryError(
                f"{spec.relative_path}: expected {spec.bytes} bytes, got {size}"
            )
        if digest != spec.sha256:
            raise ReferenceModelDirectoryError(
                f"{spec.relative_path}: SHA-256 mismatch"
            )
        observed[spec.relative_path] = {
            "bytes": size,
            "sha256": digest,
        }

    tokenizer_config_path = root / "tokenizer/tokenizer_config.json"
    rl_config_path = root / "rl_agent_config.json"
    try:
        tokenizer_config = json.loads(
            tokenizer_config_path.read_text(encoding="utf-8")
        )
        rl_config = json.loads(rl_config_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ReferenceModelDirectoryError(
            "reference model JSON config cannot be parsed"
        ) from exc

    if tokenizer_config.get("tokenizer_class") != "PreTrainedTokenizerFast":
        raise ReferenceModelDirectoryError(
            "tokenizer config would require a Laya compatibility rewrite"
        )
    if "extra_special_tokens" in tokenizer_config and isinstance(
        tokenizer_config["extra_special_tokens"], list
    ):
        raise ReferenceModelDirectoryError(
            "tokenizer extra_special_tokens would require a Laya compatibility rewrite"
        )

    temperatures = rl_config.get("temperature_by_options")
    if not isinstance(temperatures, dict):
        raise ReferenceModelDirectoryError(
            "rl_agent_config.temperature_by_options must be an object"
        )
    if temperatures.get("choice:11+") != RAW_CHOICE_11_PLUS:
        raise ReferenceModelDirectoryError(
            "reference raw choice:11+ temperature drift"
        )

    return {
        "valid": True,
        "source_repository": SOURCE_REPOSITORY,
        "source_revision": SOURCE_REVISION,
        "runtime_consumed_files": observed,
        "tokenizer_config_rewrite_required": False,
        "raw_choice_11_plus_temperature": RAW_CHOICE_11_PLUS,
        "laya_0_3_20_applied_choice_11_plus_temperature": APPLIED_CHOICE_11_PLUS,
        "endpoint_loaded_exact_directory_attested": False,
        "live_reference_inference": False,
    }


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ReferenceModelDirectoryError(f"cannot read JSON: {path}") from exc
    if not isinstance(value, dict):
        raise ReferenceModelDirectoryError("JSON root must be an object")
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("attestation", type=Path)
    parser.add_argument("model_dir", type=Path)
    args = parser.parse_args(argv)
    try:
        packet = load_json(args.attestation)
        validate_attestation(packet)
        result = verify_model_directory(args.model_dir)
    except ReferenceModelDirectoryError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
