#!/usr/bin/env python3
"""Validate the evaluation-only sparse associative cognition research boundary."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PLAN_PATH = ROOT / "evaluation" / "sparse-associative-cognition" / "research_plan.json"
EXPECTED_SCHEMA = "soza.sparse-associative-cognition-research/v1alpha1"
REQUIRED_CASES = {
    "SAC-01-soza-artifact-method-recall",
    "SAC-02-grammar-constrained-code-completion",
    "SAC-03-spreadsheet-format-recognition",
    "SAC-04-functional-dependency-testdata",
}
FORBIDDEN_SEMANTIC_PROMOTIONS = {
    "truth",
    "confidence",
    "SOZA Unknown",
    "SOZA Conflict",
    "Recommendation",
    "Decision",
    "Authority",
    "Assurance",
}
REQUIRED_DIMENSIONS = {
    "recall_at_k",
    "false_activation_rate",
    "novelty_abstention_behavior",
    "perturbation_stability",
    "p50_latency",
    "p95_latency",
    "memory_footprint",
    "deterministic_reproducibility",
}


def validate_research_plan(plan: dict) -> list[str]:
    errors: list[str] = []

    if plan.get("schema") != EXPECTED_SCHEMA:
        errors.append(f"schema must be {EXPECTED_SCHEMA}")
    if plan.get("status") != "evaluation-only":
        errors.append("status must remain evaluation-only")

    position = plan.get("architectural_position")
    if not isinstance(position, dict):
        errors.append("architectural_position must be an object")
    else:
        required_false = (
            "is_cognitive_method_definition",
            "is_universal_semantic_contract",
            "requires_universal_contract_change",
            "is_production_runtime",
            "is_mandatory_pipeline",
        )
        for key in required_false:
            if position.get(key) is not False:
                errors.append(f"architectural_position.{key} must remain false")
        if position.get("classification") != "cognitive-realization-support-substrate":
            errors.append(
                "architectural_position.classification must remain cognitive-realization-support-substrate"
            )

    placement = plan.get("placement_policy")
    if not isinstance(placement, dict):
        errors.append("placement_policy must be an object")
    else:
        if placement.get("ownership_is_deployment") is not False:
            errors.append("placement_policy.ownership_is_deployment must remain false")
        if placement.get("network_service_required") is not False:
            errors.append("placement_policy.network_service_required must remain false")

    llm_boundary = plan.get("llm_boundary")
    if not isinstance(llm_boundary, dict):
        errors.append("llm_boundary must be an object")
    else:
        if llm_boundary.get("llm_required") is not False:
            errors.append("llm_boundary.llm_required must remain false")
        if llm_boundary.get("llm_is_fallback_by_default") is not False:
            errors.append("llm_boundary.llm_is_fallback_by_default must remain false")

    deterministic = plan.get("deterministic_boundary")
    if not isinstance(deterministic, dict) or not deterministic.get("rule"):
        errors.append("deterministic_boundary.rule must be declared")

    stop_lines = plan.get("semantic_stop_lines")
    if not isinstance(stop_lines, list) or not all(isinstance(item, str) for item in stop_lines):
        errors.append("semantic_stop_lines must be a string list")
    else:
        for semantic in sorted(FORBIDDEN_SEMANTIC_PROMOTIONS):
            if not any(semantic in line for line in stop_lines):
                errors.append(f"semantic stop line missing for {semantic}")

    cases = plan.get("initial_evaluation_cases")
    if not isinstance(cases, list):
        errors.append("initial_evaluation_cases must be a list")
    else:
        ids = [case.get("id") for case in cases if isinstance(case, dict)]
        if len(ids) != len(cases) or set(ids) != REQUIRED_CASES:
            errors.append("initial_evaluation_cases must contain exactly SAC-01 through SAC-04")
        if not any(
            isinstance(case, dict) and case.get("domain") == "soza-native" for case in cases
        ):
            errors.append("initial_evaluation_cases must retain a SOZA-native case")

    baselines = plan.get("comparison_baselines")
    if not isinstance(baselines, list):
        errors.append("comparison_baselines must be a list")
    else:
        baseline_ids = {
            item.get("id") for item in baselines if isinstance(item, dict) and item.get("id")
        }
        if "exact-deterministic" not in baseline_ids:
            errors.append("comparison_baselines must retain exact-deterministic")
        if "sparse-random-expansion-kwta" not in baseline_ids:
            errors.append("comparison_baselines must retain sparse-random-expansion-kwta")

    dimensions = plan.get("evaluation_dimensions")
    if not isinstance(dimensions, list) or not all(isinstance(item, str) for item in dimensions):
        errors.append("evaluation_dimensions must be a string list")
    elif not REQUIRED_DIMENSIONS.issubset(set(dimensions)):
        errors.append("evaluation_dimensions are missing required independent dimensions")

    evaluation_policy = plan.get("evaluation_policy")
    if not isinstance(evaluation_policy, dict):
        errors.append("evaluation_policy must be an object")
    else:
        if evaluation_policy.get("single_composite_score") is not False:
            errors.append("evaluation_policy.single_composite_score must remain false")
        if evaluation_policy.get("llm_judge_required") is not False:
            errors.append("evaluation_policy.llm_judge_required must remain false")
        if evaluation_policy.get("human_quality_judgement_automated") is not False:
            errors.append(
                "evaluation_policy.human_quality_judgement_automated must remain false"
            )

    implementation = plan.get("implementation_policy")
    if not isinstance(implementation, dict):
        errors.append("implementation_policy must be an object")
    else:
        if implementation.get("gpu_required") is not False:
            errors.append("implementation_policy.gpu_required must remain false in first research slice")
        if implementation.get("offline_capable_target") is not True:
            errors.append("implementation_policy.offline_capable_target must remain true")

    evidence = plan.get("current_evidence")
    if not isinstance(evidence, dict) or evidence.get("level") != "executable-evaluation":
        errors.append("current_evidence.level must remain executable-evaluation")
    elif not evidence.get("evidence_file"):
        errors.append("current_evidence.evidence_file must be declared")

    return errors


def main() -> int:
    try:
        plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"sparse associative cognition research plan validation failed: {exc}", file=sys.stderr)
        return 1

    errors = validate_research_plan(plan)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("Sparse associative cognition research plan validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
