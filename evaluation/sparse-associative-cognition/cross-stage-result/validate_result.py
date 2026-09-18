#!/usr/bin/env python3
"""Validate immutable cross-stage benchmark result artifacts.

This module validates result provenance and metric completeness. It does not
execute a benchmark, interpret results, choose a winning variant, open B5, or
change production defaults.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
SACS_DIR = HERE.parent
RUN_DIR = SACS_DIR / "cross-stage-run"
FREEZE_DIR = SACS_DIR / "cross-stage-freeze"

RESULT_PATH = HERE / "result.json"
RUN_PATH = RUN_DIR / "evaluation_run.json"
PREREG_PATH = SACS_DIR / "cross_stage_benchmark_preregistration.json"

for path in (SACS_DIR, RUN_DIR, FREEZE_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from freeze_manifests import load_directory  # noqa: E402
from validate_cross_stage_preregistration import (  # noqa: E402
    validate_preregistration,
    validate_unlock,
)
from validate_evaluation_run import validate_authorized_run  # noqa: E402

EXPECTED_SCHEMA = "sei.sacs-cross-stage-result/v1alpha1"
UTC_SECOND = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
COMMIT_SHA = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")

TOP_LEVEL_KEYS = {
    "schema",
    "issue",
    "state",
    "result_id",
    "generated_at",
    "run_binding",
    "execution",
    "track",
    "variant",
    "capacity_profile",
    "stress_policy",
    "observed_environment",
    "metrics",
    "raw_evidence",
    "results_generated",
    "result_digest",
}
RUN_BINDING_KEYS = {"ref", "digest"}
EXECUTION_KEYS = {
    "executor_ref",
    "executor_commit",
    "started_at",
    "completed_at",
    "exit_code",
}
ENVIRONMENT_KEYS = {"os", "arch", "runtime"}
METRIC_KEYS = {
    "name",
    "role",
    "status",
    "value",
    "unit",
    "sample_count",
    "unavailable_reason",
}
RAW_EVIDENCE_KEYS = {"kind", "ref", "digest"}
RAW_EVIDENCE_KINDS = {"raw-output", "environment-capture", "runner-log"}


def _canonical_string(value: object) -> bool:
    return isinstance(value, str) and value != "" and value == value.strip()


def canonical_result_digest(result: dict[str, Any]) -> str:
    payload = copy.deepcopy(result)
    payload.pop("result_digest", None)
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _metric_role_map(prereg: dict[str, Any], track: str) -> dict[str, str]:
    tracks = prereg.get("tracks", {})
    section = tracks.get(track, {})
    metrics = section.get("metrics", {})
    if isinstance(metrics, list):
        return {
            name: "track-metric"
            for name in metrics
            if isinstance(name, str)
        }
    if not isinstance(metrics, dict):
        return {}

    category_roles = {
        "quality": "quality",
        "robustness": "robustness",
        "resource": "resource",
        "diagnostics": "diagnostic",
    }
    out: dict[str, str] = {}
    for category, values in metrics.items():
        role = category_roles.get(category)
        if role is None or not isinstance(values, list):
            continue
        for name in values:
            if isinstance(name, str):
                out[name] = role
    return out


def validate_result_structure(result: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if set(result) != TOP_LEVEL_KEYS:
        missing = sorted(TOP_LEVEL_KEYS - set(result))
        extra = sorted(set(result) - TOP_LEVEL_KEYS)
        errors.append(
            f"result top-level keys mismatch: missing={missing}, extra={extra}"
        )

    if result.get("schema") != EXPECTED_SCHEMA:
        errors.append(f"result.schema must be {EXPECTED_SCHEMA}")
    if result.get("state") not in {"draft", "completed"}:
        errors.append("result.state must be draft or completed")
    if not _canonical_string(result.get("result_id")):
        errors.append("result.result_id must be canonical and non-empty")

    run_binding = result.get("run_binding")
    if not isinstance(run_binding, dict) or set(run_binding) != RUN_BINDING_KEYS:
        errors.append("result.run_binding must contain exactly ref and digest")
    elif run_binding.get("ref") != "../cross-stage-run/evaluation_run.json":
        errors.append(
            "result.run_binding.ref must remain ../cross-stage-run/evaluation_run.json"
        )

    execution = result.get("execution")
    if not isinstance(execution, dict) or set(execution) != EXECUTION_KEYS:
        errors.append("result.execution keys do not match the registered contract")

    environment = result.get("observed_environment")
    if not isinstance(environment, dict) or set(environment) != ENVIRONMENT_KEYS:
        errors.append(
            "result.observed_environment must contain exactly os, arch, runtime"
        )

    metrics = result.get("metrics")
    if not isinstance(metrics, list):
        errors.append("result.metrics must be a list")
    else:
        for index, metric in enumerate(metrics):
            if not isinstance(metric, dict) or set(metric) != METRIC_KEYS:
                errors.append(
                    f"result.metrics[{index}] keys do not match the registered metric contract"
                )

    raw_evidence = result.get("raw_evidence")
    if not isinstance(raw_evidence, list):
        errors.append("result.raw_evidence must be a list")
    else:
        for index, item in enumerate(raw_evidence):
            if not isinstance(item, dict) or set(item) != RAW_EVIDENCE_KEYS:
                errors.append(
                    f"result.raw_evidence[{index}] keys do not match the registered evidence contract"
                )

    if result.get("state") == "draft":
        if result.get("generated_at") is not None:
            errors.append("draft result generated_at must be null")
        if result.get("results_generated") is not False:
            errors.append("draft result must keep results_generated=false")
        if result.get("result_digest") != "":
            errors.append("draft result result_digest must be empty")

    return errors


def validate_completed_result(
    result: dict[str, Any],
    run: dict[str, Any],
    prereg: dict[str, Any],
    freeze_documents: dict[str, dict[str, Any]],
) -> list[str]:
    errors = validate_result_structure(result)
    errors.extend(
        f"preregistration: {error}"
        for error in validate_preregistration(prereg)
    )
    errors.extend(
        f"authorized run: {error}"
        for error in validate_authorized_run(run, prereg, freeze_documents)
    )
    errors.extend(
        f"full unlock: {error}"
        for error in validate_unlock(prereg)
    )

    if result.get("state") != "completed":
        errors.append("completed result validation requires result.state=completed")
        return errors

    if result.get("result_id") == "cross-stage-result-template":
        errors.append("completed result must replace the template result_id")

    generated_at = result.get("generated_at")
    if not isinstance(generated_at, str) or UTC_SECOND.fullmatch(generated_at) is None:
        errors.append(
            "completed result generated_at must use UTC second format YYYY-MM-DDTHH:MM:SSZ"
        )

    if result.get("results_generated") is not True:
        errors.append("completed result requires results_generated=true")

    digest = result.get("result_digest")
    if not isinstance(digest, str) or HEX64.fullmatch(digest) is None:
        errors.append("completed result requires result_digest as lowercase SHA-256 hex")
    elif digest != canonical_result_digest(result):
        errors.append("completed result result_digest does not match canonical content")

    run_digest = run.get("run_digest")
    run_binding = result.get("run_binding", {})
    if not isinstance(run_digest, str) or HEX64.fullmatch(run_digest) is None:
        errors.append("completed result requires authorized run with valid run_digest")
    elif run_binding.get("digest") != run_digest:
        errors.append("result run_binding.digest does not match authorized run digest")

    for key in ("track", "variant", "capacity_profile", "stress_policy"):
        if result.get(key) != run.get(key):
            errors.append(f"result.{key} must match authorized run")

    observed_environment = result.get("observed_environment", {})
    run_environment = run.get("environment", {})
    if observed_environment != run_environment:
        errors.append("result observed_environment must exactly match authorized run environment")

    execution = result.get("execution", {})
    if not _canonical_string(execution.get("executor_ref")):
        errors.append("completed result requires canonical execution.executor_ref")
    executor_commit = execution.get("executor_commit")
    if (
        not isinstance(executor_commit, str)
        or COMMIT_SHA.fullmatch(executor_commit) is None
    ):
        errors.append(
            "completed result execution.executor_commit must be a 40-char lowercase git SHA"
        )

    started_at = execution.get("started_at")
    completed_at = execution.get("completed_at")
    for key, value in (("started_at", started_at), ("completed_at", completed_at)):
        if not isinstance(value, str) or UTC_SECOND.fullmatch(value) is None:
            errors.append(
                f"completed result execution.{key} must use UTC second format YYYY-MM-DDTHH:MM:SSZ"
            )
    if (
        isinstance(started_at, str)
        and isinstance(completed_at, str)
        and UTC_SECOND.fullmatch(started_at)
        and UTC_SECOND.fullmatch(completed_at)
        and started_at > completed_at
    ):
        errors.append("execution.started_at must not be after execution.completed_at")
    if (
        isinstance(completed_at, str)
        and isinstance(generated_at, str)
        and UTC_SECOND.fullmatch(completed_at)
        and UTC_SECOND.fullmatch(generated_at)
        and completed_at > generated_at
    ):
        errors.append("execution.completed_at must not be after result.generated_at")

    exit_code = execution.get("exit_code")
    if not isinstance(exit_code, int) or isinstance(exit_code, bool) or exit_code != 0:
        errors.append("completed result requires execution.exit_code=0")

    role_map = _metric_role_map(prereg, run.get("track", ""))
    requested = run.get("requested_metrics", [])
    metrics = result.get("metrics", [])
    metric_names = [
        metric.get("name")
        for metric in metrics
        if isinstance(metric, dict)
    ]

    if len(metric_names) != len(set(metric_names)):
        errors.append("result metric names must be unique")
    if sorted(metric_names) != sorted(requested):
        errors.append(
            "completed result metrics must match authorized run requested_metrics exactly"
        )

    for index, metric in enumerate(metrics):
        if not isinstance(metric, dict):
            continue
        name = metric.get("name")
        if not _canonical_string(name):
            errors.append(f"result.metrics[{index}].name must be canonical and non-empty")
            continue

        expected_role = role_map.get(name)
        if expected_role is None:
            errors.append(f"result metric is not preregistered for track: {name}")
        elif metric.get("role") != expected_role:
            errors.append(
                f"result metric role mismatch for {name}: expected {expected_role}"
            )

        status = metric.get("status")
        if status not in {"measured", "unavailable"}:
            errors.append(
                f"result.metrics[{index}].status must be measured or unavailable"
            )
            continue

        value = metric.get("value")
        unit = metric.get("unit")
        sample_count = metric.get("sample_count")
        unavailable_reason = metric.get("unavailable_reason")

        if status == "measured":
            if (
                not isinstance(value, (int, float))
                or isinstance(value, bool)
                or not math.isfinite(value)
            ):
                errors.append(
                    f"measured metric {name} requires a finite numeric value"
                )
            if not _canonical_string(unit):
                errors.append(f"measured metric {name} requires canonical unit")
            if (
                not isinstance(sample_count, int)
                or isinstance(sample_count, bool)
                or sample_count < 1
            ):
                errors.append(
                    f"measured metric {name} requires sample_count >= 1"
                )
            if unavailable_reason != "":
                errors.append(
                    f"measured metric {name} must keep unavailable_reason empty"
                )
        else:
            if value is not None:
                errors.append(f"unavailable metric {name} must keep value=null")
            if unit != "":
                errors.append(f"unavailable metric {name} must keep unit empty")
            if sample_count != 0:
                errors.append(f"unavailable metric {name} must keep sample_count=0")
            if not _canonical_string(unavailable_reason):
                errors.append(
                    f"unavailable metric {name} requires a non-empty reason"
                )

    raw_evidence = result.get("raw_evidence", [])
    seen_refs: set[str] = set()
    kinds: set[str] = set()
    for index, item in enumerate(raw_evidence):
        if not isinstance(item, dict):
            continue
        kind = item.get("kind")
        if kind not in RAW_EVIDENCE_KINDS:
            errors.append(
                f"result.raw_evidence[{index}].kind is not registered: {kind}"
            )
        else:
            kinds.add(kind)
        ref = item.get("ref")
        if not _canonical_string(ref):
            errors.append(
                f"result.raw_evidence[{index}].ref must be canonical and non-empty"
            )
        elif ref in seen_refs:
            errors.append(f"raw evidence ref must be unique: {ref}")
        else:
            seen_refs.add(ref)
        evidence_digest = item.get("digest")
        if (
            not isinstance(evidence_digest, str)
            or HEX64.fullmatch(evidence_digest) is None
        ):
            errors.append(
                f"result.raw_evidence[{index}].digest must be lowercase SHA-256 hex"
            )

    for required_kind in ("raw-output", "environment-capture"):
        if required_kind not in kinds:
            errors.append(
                f"completed result requires raw_evidence kind={required_kind}"
            )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result", type=Path, default=RESULT_PATH)
    parser.add_argument("--run", type=Path, default=RUN_PATH)
    parser.add_argument("--prereg", type=Path, default=PREREG_PATH)
    parser.add_argument("--freeze-dir", type=Path, default=FREEZE_DIR)
    args = parser.parse_args()

    try:
        result = json.loads(args.result.read_text(encoding="utf-8"))
        run = json.loads(args.run.read_text(encoding="utf-8"))
        prereg = json.loads(args.prereg.read_text(encoding="utf-8"))
        freeze_documents = load_directory(args.freeze_dir)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"cross-stage result load failed: {exc}", file=sys.stderr)
        return 1

    structural = validate_result_structure(result)
    if structural:
        for error in structural:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    if result.get("state") == "draft":
        print("Cross-stage result validated; current result remains draft/empty")
        return 0

    errors = validate_completed_result(
        result,
        run,
        prereg,
        freeze_documents,
    )
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("Cross-stage result validated; completed artifact is provenance-bound")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
