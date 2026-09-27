#!/usr/bin/env python3
"""Verify a returned managed-pair evidence directory without re-running models.

The verifier checks the pair receipt, every completed stage artifact, and any
retained failed-stage output against the exact digest/semantic bindings produced
by run_managed_pair.py. It verifies internal evidence integrity; it does not
re-run inference, recompute numeric parity, or make a shipping decision.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

VERIFICATION_SCHEMA = (
    "sei.local-typed-comparator-managed-pair-bundle-verification/v1"
)
STAGES = ("preflight", "reference", "papaya", "comparison", "decision")
STAGE_FILES = {
    "preflight": "pair-preflight.json",
    "reference": "reference-run.json",
    "papaya": "papaya-run.json",
    "comparison": "numeric-difference-report.json",
    "decision": "numeric-parity-decision.json",
}
RECEIPT_FILE = "pair-run-receipt.json"


class ManagedPairBundleError(ValueError):
    pass


def _load_pair_module():
    here = Path(__file__).resolve().parent
    path = here / "run_managed_pair.py"
    spec = importlib.util.spec_from_file_location(
        "run_managed_pair_bundle_verifier", path
    )
    if spec is None or spec.loader is None:
        raise ManagedPairBundleError(f"cannot import paired-run module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _object(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ManagedPairBundleError(f"{field} must be an object")
    return value


def _completed_summary(
    pair: Any,
    *,
    stage: str,
    path: Path,
    source_sha: str,
    completed: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    try:
        if stage == "preflight":
            return pair._preflight_summary(path, source_sha)
        if stage == "reference":
            return pair._artifact_summary(
                path,
                expected_schema=pair.REFERENCE_SCHEMA,
                source_sha=source_sha,
                label="reference run",
            )
        if stage == "papaya":
            return pair._artifact_summary(
                path,
                expected_schema=pair.PAPAYA_SCHEMA,
                source_sha=source_sha,
                label="Papaya run",
            )
        if stage == "comparison":
            return pair._report_summary(path, source_sha)
        if stage == "decision":
            return pair._decision_summary(
                path,
                source_sha=source_sha,
                report_sha=completed["comparison"]["sha256"],
                reference_sha=completed["reference"]["sha256"],
                papaya_sha=completed["papaya"]["sha256"],
            )
    except Exception as exc:
        raise ManagedPairBundleError(
            f"{stage} artifact verification failed: {exc}"
        ) from exc
    raise ManagedPairBundleError(f"unknown stage: {stage}")


def _expected_failure_stage(stage: str, kind: str) -> str:
    if kind == "process_exit":
        return f"{stage}_failed"
    if kind == "runner_exception":
        return f"{stage}_launch_failed"
    if kind == "artifact_validation":
        return f"{stage}_validation_failed"
    raise ManagedPairBundleError(f"unknown failure kind: {kind!r}")


def _validate_scope(
    scope: dict[str, Any], *, completed_stages: tuple[str, ...]
) -> None:
    if scope.get("single_sei_source_git_sha") is not True:
        raise ManagedPairBundleError("single source SHA scope must be true")
    if scope.get("preflight_all_required_inputs_verified") is not (
        "preflight" in completed_stages
    ):
        raise ManagedPairBundleError("preflight scope/completed-stage drift")
    if scope.get("provider_provenance_merged") is not False:
        raise ManagedPairBundleError("provider provenance must remain separate")
    if scope.get("raw_comparator_threshold_defined") is not False:
        raise ManagedPairBundleError("raw comparator threshold scope drift")
    if scope.get("preregistered_numeric_policy_applied") is not (
        "decision" in completed_stages
    ):
        raise ManagedPairBundleError("numeric policy scope/completed-stage drift")
    for field in (
        "task_quality",
        "calibration_validity",
        "cross_runtime_performance_comparison",
        "jev_provider_identity_equivalence",
        "reference_provider_promotion",
        "shipping_decision",
    ):
        if scope.get(field) is not False:
            raise ManagedPairBundleError(f"scope.{field} must remain false")


def verify_bundle(
    bundle_dir: Path,
    *,
    expected_source_sha: str,
    pair_module: Any | None = None,
) -> dict[str, Any]:
    pair = pair_module or _load_pair_module()
    source_sha = pair._require_full_sha(expected_source_sha)
    root = bundle_dir.expanduser().resolve()
    if not root.is_dir():
        raise ManagedPairBundleError(f"bundle directory not found: {root}")

    receipt_path = root / RECEIPT_FILE
    try:
        receipt = pair._load_json(receipt_path, "pair-run receipt")
    except Exception as exc:
        raise ManagedPairBundleError(f"cannot load pair receipt: {exc}") from exc

    if receipt.get("schema") != pair.PAIR_SCHEMA:
        raise ManagedPairBundleError("pair receipt schema drift")
    if receipt.get("source_git_sha") != source_sha:
        raise ManagedPairBundleError("pair receipt source Git SHA drift")

    run_id = receipt.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        raise ManagedPairBundleError("pair receipt run_id missing")
    run_ids = _object(receipt.get("run_ids"), "pair receipt run_ids")
    if run_ids != {
        "reference": f"{run_id}-reference",
        "papaya": f"{run_id}-papaya",
    }:
        raise ManagedPairBundleError("pair receipt provider run IDs drift")

    status = receipt.get("status")
    if status not in ("complete", "failed"):
        raise ManagedPairBundleError(
            "pair receipt must be complete or failed for returned-bundle verification"
        )

    failure: dict[str, Any] | None = None
    if status == "complete":
        if receipt.get("stage") != "complete":
            raise ManagedPairBundleError("complete receipt stage drift")
        if "failure" in receipt:
            raise ManagedPairBundleError("complete receipt must not retain failure")
        completed_stages = STAGES
    else:
        failure = _object(receipt.get("failure"), "pair receipt failure")
        failed_stage = failure.get("stage")
        if failed_stage not in STAGES:
            raise ManagedPairBundleError("failed stage identity drift")
        kind = failure.get("kind")
        if not isinstance(kind, str):
            raise ManagedPairBundleError("failure kind missing")
        if receipt.get("stage") != _expected_failure_stage(failed_stage, kind):
            raise ManagedPairBundleError("failure stage/kind receipt drift")
        failed_index = STAGES.index(failed_stage)
        completed_stages = STAGES[:failed_index]

        if kind == "process_exit":
            returncode = failure.get("returncode")
            if (
                isinstance(returncode, bool)
                or not isinstance(returncode, int)
                or returncode == 0
            ):
                raise ManagedPairBundleError(
                    "process-exit failure must retain non-zero returncode"
                )
        else:
            error_type = failure.get("error_type")
            if not isinstance(error_type, str) or not error_type:
                raise ManagedPairBundleError(
                    f"{kind} failure must retain error_type"
                )

    recorded_artifacts = _object(
        receipt.get("artifacts"), "pair receipt artifacts"
    )
    if set(recorded_artifacts) != set(completed_stages):
        raise ManagedPairBundleError(
            "completed artifact set does not match receipt stage"
        )

    regenerated: dict[str, dict[str, Any]] = {}
    for stage in completed_stages:
        path = root / STAGE_FILES[stage]
        summary = _completed_summary(
            pair,
            stage=stage,
            path=path,
            source_sha=source_sha,
            completed=regenerated,
        )
        if recorded_artifacts.get(stage) != summary:
            raise ManagedPairBundleError(
                f"{stage} receipt summary/disk artifact drift"
            )
        regenerated[stage] = summary

    scope = _object(receipt.get("scope"), "pair receipt scope")
    _validate_scope(scope, completed_stages=completed_stages)

    failure_summary: dict[str, Any] | None = None
    if failure is not None:
        failed_stage = failure["stage"]
        failed_path = root / STAGE_FILES[failed_stage]
        actual_partial = pair._partial_artifact_summary(failed_path)
        recorded_partial = _object(
            failure.get("stage_output"), "pair receipt failure.stage_output"
        )
        if recorded_partial != actual_partial:
            raise ManagedPairBundleError(
                "failed-stage output summary/disk artifact drift"
            )
        failure_summary = {
            "stage": failed_stage,
            "kind": failure["kind"],
            "stage_output_present": bool(actual_partial.get("present")),
        }

    return {
        "schema": VERIFICATION_SCHEMA,
        "status": "verified",
        "pair_status": status,
        "source_git_sha": source_sha,
        "run_id": run_id,
        "receipt": {
            "file": RECEIPT_FILE,
            "sha256": pair._sha256_file(receipt_path),
        },
        "completed_artifacts": {
            stage: {
                "file": regenerated[stage]["file"],
                "sha256": regenerated[stage]["sha256"],
            }
            for stage in completed_stages
        },
        "failure": failure_summary,
        "scope": {
            "internal_bundle_integrity_verified": True,
            "live_inference_reexecuted": False,
            "numeric_parity_recomputed": False,
            "task_quality": False,
            "calibration_validity": False,
            "shipping_decision": False,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle_dir", type=Path)
    parser.add_argument("--source-git-sha", required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    try:
        verification = verify_bundle(
            args.bundle_dir,
            expected_source_sha=args.source_git_sha,
        )
        rendered = json.dumps(verification, ensure_ascii=False, indent=2) + "\n"
        if args.output is not None:
            if args.output.exists():
                raise ManagedPairBundleError(
                    f"output already exists: {args.output}"
                )
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered, encoding="utf-8")
        print(rendered, end="")
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
