#!/usr/bin/env python3
"""Validate a provider-neutral burst-compute run manifest.

The manifest records an already completed external GPU/accelerator work unit. It is
provenance and reproducibility evidence only; it grants no model/runtime authority.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

SCHEMA = "sei.cognition-burst-run-manifest/v1alpha1"
ALLOWED_PURPOSES = {
    "teacher-batch",
    "fine-tune",
    "distillation",
    "export-validation",
    "connectome-sweep",
    "embodied-offline-learning",
}
ALLOWED_ENVIRONMENTS = {"kaggle", "colab", "local", "other"}
ALLOWED_PROMOTION = {"local-validation", "research-only", "reject", "undecided"}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
GIT_SHA_RE = re.compile(r"^[0-9a-f]{40}$")


class BurstRunManifestError(ValueError):
    pass


def _obj(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise BurstRunManifestError(f"{field} must be an object")
    return value


def _nonempty_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise BurstRunManifestError(f"{field} must be a non-empty string")
    return value


def _sha256(value: Any, field: str) -> str:
    value = _nonempty_string(value, field)
    if not SHA256_RE.fullmatch(value):
        raise BurstRunManifestError(f"{field} must be a lowercase SHA-256 hex digest")
    return value


def _finite_nonnegative(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise BurstRunManifestError(f"{field} must be a finite non-negative number")
    number = float(value)
    if not math.isfinite(number) or number < 0:
        raise BurstRunManifestError(f"{field} must be a finite non-negative number")
    return number


def validate_manifest(manifest: dict[str, Any]) -> None:
    if manifest.get("schema") != SCHEMA:
        raise BurstRunManifestError(f"schema must be {SCHEMA}")

    purpose = manifest.get("purpose")
    if purpose not in ALLOWED_PURPOSES:
        raise BurstRunManifestError(f"purpose must be one of {sorted(ALLOWED_PURPOSES)}")

    source_git_sha = _nonempty_string(manifest.get("source_git_sha"), "source_git_sha")
    if not GIT_SHA_RE.fullmatch(source_git_sha):
        raise BurstRunManifestError("source_git_sha must be a lowercase 40-character Git SHA")

    inputs = _obj(manifest.get("inputs"), "inputs")
    for field in ("dataset_sha256", "split_manifest_sha256", "preregistered_metrics_sha256"):
        _sha256(inputs.get(field), f"inputs.{field}")

    model = _obj(manifest.get("model"), "model")
    _nonempty_string(model.get("provider"), "model.provider")
    _nonempty_string(model.get("name"), "model.name")
    _nonempty_string(model.get("revision"), "model.revision")
    if model.get("provider") == "typesafe" and not str(model.get("name", "")).startswith("jev-"):
        raise BurstRunManifestError("typesafe provider identity must not be used for a non-Jev model")

    runtime = _obj(manifest.get("runtime"), "runtime")
    if runtime.get("environment") not in ALLOWED_ENVIRONMENTS:
        raise BurstRunManifestError(f"runtime.environment must be one of {sorted(ALLOWED_ENVIRONMENTS)}")
    _nonempty_string(runtime.get("accelerator_observed"), "runtime.accelerator_observed")
    _sha256(runtime.get("dependency_lock_sha256"), "runtime.dependency_lock_sha256")
    _nonempty_string(runtime.get("python_version"), "runtime.python_version")
    seed = runtime.get("seed")
    if isinstance(seed, bool) or not isinstance(seed, int) or seed < 0:
        raise BurstRunManifestError("runtime.seed must be a non-negative integer")

    execution = _obj(manifest.get("execution"), "execution")
    _nonempty_string(execution.get("started_at"), "execution.started_at")
    _nonempty_string(execution.get("ended_at"), "execution.ended_at")
    elapsed = _finite_nonnegative(execution.get("elapsed_seconds"), "execution.elapsed_seconds")
    if elapsed == 0:
        raise BurstRunManifestError("execution.elapsed_seconds must be greater than zero")
    observed_cost = execution.get("cost_observed")
    if not isinstance(observed_cost, bool):
        raise BurstRunManifestError("execution.cost_observed must be boolean")
    if observed_cost:
        cost = _obj(execution.get("cost"), "execution.cost")
        _nonempty_string(cost.get("unit"), "execution.cost.unit")
        _finite_nonnegative(cost.get("amount"), "execution.cost.amount")
    elif execution.get("cost") is not None:
        raise BurstRunManifestError("execution.cost must be null/absent when cost_observed is false")

    outputs = manifest.get("outputs")
    if not isinstance(outputs, list) or not outputs:
        raise BurstRunManifestError("outputs must be a non-empty array")
    seen_names: set[str] = set()
    for index, raw in enumerate(outputs):
        artifact = _obj(raw, f"outputs[{index}]")
        name = _nonempty_string(artifact.get("name"), f"outputs[{index}].name")
        if name in seen_names:
            raise BurstRunManifestError(f"duplicate output artifact name: {name}")
        seen_names.add(name)
        _nonempty_string(artifact.get("kind"), f"outputs[{index}].kind")
        _sha256(artifact.get("sha256"), f"outputs[{index}].sha256")

    evaluation = _obj(manifest.get("evaluation"), "evaluation")
    held_out = evaluation.get("held_out_metrics")
    if not isinstance(held_out, dict) or not held_out:
        raise BurstRunManifestError("evaluation.held_out_metrics must be a non-empty object")
    for key, value in held_out.items():
        _nonempty_string(key, "evaluation.held_out_metrics key")
        _finite_nonnegative(value, f"evaluation.held_out_metrics.{key}")
    local_export = evaluation.get("local_export_compatible")
    if not isinstance(local_export, bool):
        raise BurstRunManifestError("evaluation.local_export_compatible must be boolean")
    if evaluation.get("promotion_decision") not in ALLOWED_PROMOTION:
        raise BurstRunManifestError(f"evaluation.promotion_decision must be one of {sorted(ALLOWED_PROMOTION)}")

    claims = _obj(manifest.get("claims"), "claims")
    if claims.get("semantic_truth") is not False:
        raise BurstRunManifestError("claims.semantic_truth must be false")
    if claims.get("production_authority") is not False:
        raise BurstRunManifestError("claims.production_authority must be false")


def load_manifest(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise BurstRunManifestError(f"manifest does not exist: {path}") from exc
    except json.JSONDecodeError as exc:
        raise BurstRunManifestError(f"manifest is not valid JSON: {path}") from exc
    if not isinstance(data, dict):
        raise BurstRunManifestError("manifest root must be an object")
    validate_manifest(data)
    return data


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args(argv)
    try:
        data = load_manifest(args.manifest)
    except BurstRunManifestError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"valid": True, "schema": data["schema"], "purpose": data["purpose"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
