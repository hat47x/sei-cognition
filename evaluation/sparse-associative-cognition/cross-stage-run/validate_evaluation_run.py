#!/usr/bin/env python3
"""Validate an explicit cross-stage evaluation-run authorization artifact.

This module does not execute a benchmark and does not generate result artifacts.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
SACS_DIR = HERE.parent
FREEZE_DIR = SACS_DIR / "cross-stage-freeze"
PREREG_PATH = SACS_DIR / "cross_stage_benchmark_preregistration.json"
RUN_PATH = HERE / "evaluation_run.json"

if str(SACS_DIR) not in sys.path:
    sys.path.insert(0, str(SACS_DIR))
if str(FREEZE_DIR) not in sys.path:
    sys.path.insert(0, str(FREEZE_DIR))

from validate_cross_stage_preregistration import (  # noqa: E402
    validate_pre_run_prerequisites,
    validate_preregistration,
)
from freeze_manifests import load_directory, validate_all  # noqa: E402

EXPECTED_SCHEMA = "sei.sacs-cross-stage-evaluation-run/v1alpha1"
UTC_SECOND = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
COMMIT_SHA = re.compile(r"^[0-9a-f]{40}$")

TOP_LEVEL_KEYS = {
    "schema",
    "issue",
    "state",
    "run_id",
    "authorized_at",
    "freeze_bundle",
    "implementation",
    "track",
    "variant",
    "capacity_profile",
    "stress_policy",
    "requested_metrics",
    "output_ref",
    "environment",
    "authorization",
    "results_generated",
    "result_artifact_ref",
}
AUTH_KEYS = {
    "execution_authorized",
    "freeze_bundle_verified",
    "preregistration_verified",
    "split_boundary_verified",
    "prior_boundary_verified",
    "no_evaluation_tuning",
    "no_composite_score",
    "b5_gate_unchanged",
    "production_default_unchanged",
}
SAFETY_TRUE_FLAGS = {
    "no_evaluation_tuning",
    "no_composite_score",
    "b5_gate_unchanged",
    "production_default_unchanged",
}
VERIFICATION_FLAGS = {
    "freeze_bundle_verified",
    "preregistration_verified",
    "split_boundary_verified",
    "prior_boundary_verified",
}


def _canonical_string(value: object) -> bool:
    return isinstance(value, str) and value != "" and value == value.strip()


def _metric_set(prereg: dict[str, Any], track: str) -> set[str]:
    tracks = prereg.get("tracks", {})
    section = tracks.get(track, {})
    metrics = section.get("metrics", {})
    if isinstance(metrics, list):
        return {m for m in metrics if isinstance(m, str)}
    if isinstance(metrics, dict):
        out: set[str] = set()
        for values in metrics.values():
            if isinstance(values, list):
                out.update(v for v in values if isinstance(v, str))
        return out
    return set()


def _variant_set(prereg: dict[str, Any]) -> set[str]:
    return {
        item.get("id")
        for item in prereg.get("variants", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }


def _primary_profiles(prereg: dict[str, Any]) -> set[str]:
    return {
        item.get("id")
        for item in prereg.get("capacity_profiles", {}).get("profiles", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }


def _stress_policy_set(prereg: dict[str, Any]) -> set[str]:
    return {
        item.get("id")
        for item in prereg.get("capacity_profiles", {})
        .get("stress_track", {})
        .get("residual_policies", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }


def validate_run_structure(run: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if set(run) != TOP_LEVEL_KEYS:
        missing = sorted(TOP_LEVEL_KEYS - set(run))
        extra = sorted(set(run) - TOP_LEVEL_KEYS)
        errors.append(f"run top-level keys mismatch: missing={missing}, extra={extra}")

    if run.get("schema") != EXPECTED_SCHEMA:
        errors.append(f"run.schema must be {EXPECTED_SCHEMA}")
    if run.get("state") not in {"draft", "authorized"}:
        errors.append("run.state must be draft or authorized")
    if not _canonical_string(run.get("run_id")):
        errors.append("run.run_id must be canonical and non-empty")

    bundle = run.get("freeze_bundle")
    if not isinstance(bundle, dict) or set(bundle) != {"ref", "digest"}:
        errors.append("run.freeze_bundle must contain exactly ref and digest")
    elif bundle.get("ref") != "../cross-stage-freeze/freeze_bundle.json":
        errors.append("run.freeze_bundle.ref must remain ../cross-stage-freeze/freeze_bundle.json")

    implementation = run.get("implementation")
    if not isinstance(implementation, dict) or set(implementation) != {"ref", "commit"}:
        errors.append("run.implementation must contain exactly ref and commit")

    environment = run.get("environment")
    if not isinstance(environment, dict) or set(environment) != {"os", "arch", "runtime"}:
        errors.append("run.environment must contain exactly os, arch, runtime")

    auth = run.get("authorization")
    if not isinstance(auth, dict) or set(auth) != AUTH_KEYS:
        errors.append("run.authorization keys do not match the registered authorization contract")
    else:
        for key in AUTH_KEYS:
            if not isinstance(auth.get(key), bool):
                errors.append(f"run.authorization.{key} must be boolean")
        for key in SAFETY_TRUE_FLAGS:
            if auth.get(key) is not True:
                errors.append(f"run.authorization.{key} must remain true")

    metrics = run.get("requested_metrics")
    if not isinstance(metrics, list) or not all(isinstance(v, str) for v in metrics):
        errors.append("run.requested_metrics must be a string list")
    elif len(metrics) != len(set(metrics)):
        errors.append("run.requested_metrics must be unique")

    if run.get("results_generated") is not False:
        errors.append("evaluation-run artifact must keep results_generated=false")
    if run.get("result_artifact_ref") != "":
        errors.append("evaluation-run artifact must not embed a result artifact ref")

    if run.get("state") == "draft":
        if run.get("authorized_at") is not None:
            errors.append("draft run authorized_at must be null")
        if isinstance(auth, dict):
            if auth.get("execution_authorized") is not False:
                errors.append("draft run cannot be execution-authorized")
            for key in VERIFICATION_FLAGS:
                if auth.get(key) is not False:
                    errors.append(f"draft run authorization.{key} must be false")
    return errors


def validate_authorized_run(
    run: dict[str, Any],
    prereg: dict[str, Any],
    freeze_documents: dict[str, dict[str, Any]],
) -> list[str]:
    errors = validate_run_structure(run)
    errors.extend(f"preregistration: {e}" for e in validate_preregistration(prereg))
    freeze_errors = validate_all(freeze_documents)
    errors.extend(f"freeze bundle: {e}" for e in freeze_errors)

    if run.get("state") != "authorized":
        errors.append("authorization requires run.state=authorized")
        return errors

    if not isinstance(run.get("authorized_at"), str) or UTC_SECOND.fullmatch(run["authorized_at"]) is None:
        errors.append("authorized run authorized_at must use UTC second format YYYY-MM-DDTHH:MM:SSZ")

    if run.get("run_id") == "cross-stage-run-template":
        errors.append("authorized run must replace the template run_id")

    auth = run.get("authorization", {})
    if auth.get("execution_authorized") is not True:
        errors.append("authorized run requires authorization.execution_authorized=true")
    for key in VERIFICATION_FLAGS:
        if auth.get(key) is not True:
            errors.append(f"authorized run requires authorization.{key}=true")

    pre_run_errors = validate_pre_run_prerequisites(prereg)
    errors.extend(f"preregistration pre-run: {e}" for e in pre_run_errors)

    bundle_doc = freeze_documents.get("bundle", {})
    if bundle_doc.get("state") != "frozen":
        errors.append("authorized run requires frozen freeze bundle")
    bundle_digest = bundle_doc.get("bundle_digest")
    binding = run.get("freeze_bundle", {})
    if not isinstance(bundle_digest, str) or not bundle_digest:
        errors.append("authorized run requires non-empty frozen bundle digest")
    elif binding.get("digest") != bundle_digest:
        errors.append("run freeze-bundle digest does not match frozen bundle")

    implementation = run.get("implementation", {})
    if not _canonical_string(implementation.get("ref")):
        errors.append("authorized run requires canonical implementation.ref")
    commit = implementation.get("commit")
    if not isinstance(commit, str) or COMMIT_SHA.fullmatch(commit) is None:
        errors.append("authorized run implementation.commit must be a 40-char lowercase git SHA")

    track = run.get("track")
    if track not in {"retrieval", "familiarity", "routing"}:
        errors.append("authorized run track must be retrieval, familiarity, or routing")
        return errors

    variant = run.get("variant")
    capacity = run.get("capacity_profile")
    stress_policy = run.get("stress_policy")

    if track == "retrieval":
        if variant not in _variant_set(prereg):
            errors.append("retrieval run variant is not preregistered")
        primary = _primary_profiles(prereg)
        if capacity in primary:
            if stress_policy is not None:
                errors.append("primary capacity profile cannot set stress_policy")
        elif capacity == "oversized-stress":
            if stress_policy not in _stress_policy_set(prereg):
                errors.append("oversized-stress run requires a preregistered stress_policy")
        else:
            errors.append("retrieval run capacity_profile is not preregistered")
    elif track == "familiarity":
        if variant != "SAC-B4":
            errors.append("familiarity run variant must be SAC-B4")
        if capacity is not None or stress_policy is not None:
            errors.append("familiarity run must not set capacity_profile or stress_policy")
    elif track == "routing":
        if variant != "SEI-B7":
            errors.append("routing run variant must be SEI-B7")
        if capacity is not None or stress_policy is not None:
            errors.append("routing run must not set capacity_profile or stress_policy")

    metrics = run.get("requested_metrics", [])
    allowed_metrics = _metric_set(prereg, track)
    if not metrics:
        errors.append("authorized run requires at least one requested metric")
    unknown_metrics = sorted(set(metrics) - allowed_metrics)
    if unknown_metrics:
        errors.append(f"run requested metrics are not preregistered: {unknown_metrics}")
    stress_metric = "oversized_residual_policy_stress"
    if track == "retrieval":
        if capacity == "oversized-stress" and stress_metric not in metrics:
            errors.append("oversized-stress run must request oversized_residual_policy_stress")
        if capacity != "oversized-stress" and stress_metric in metrics:
            errors.append("primary retrieval profile must not request oversized stress metric")

    if not _canonical_string(run.get("output_ref")):
        errors.append("authorized run requires canonical output_ref")
    environment = run.get("environment", {})
    for key in ("os", "arch", "runtime"):
        if not _canonical_string(environment.get(key)):
            errors.append(f"authorized run requires canonical environment.{key}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", type=Path, default=RUN_PATH)
    parser.add_argument("--prereg", type=Path, default=PREREG_PATH)
    parser.add_argument("--freeze-dir", type=Path, default=FREEZE_DIR)
    args = parser.parse_args()

    try:
        run = json.loads(args.run.read_text(encoding="utf-8"))
        prereg = json.loads(args.prereg.read_text(encoding="utf-8"))
        frozen = load_directory(args.freeze_dir)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"evaluation-run load failed: {exc}", file=sys.stderr)
        return 1

    structural = validate_run_structure(run)
    if structural:
        for error in structural:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    if run.get("state") == "draft":
        print("Cross-stage evaluation-run validated; current run remains draft/locked")
        return 0

    errors = validate_authorized_run(run, prereg, frozen)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("Cross-stage evaluation-run authorized; no benchmark results were generated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
