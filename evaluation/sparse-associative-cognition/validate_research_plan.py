#!/usr/bin/env python3
"""Validate the evaluation-only sparse associative cognition research boundary."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PLAN_PATH = ROOT / "evaluation" / "sparse-associative-cognition" / "research_plan.json"
EXPECTED_SCHEMA = "sei.sparse-associative-cognition-research/v1alpha1"
REQUIRED_CASES = {
    "SAC-01-sei-artifact-method-recall",
    "SAC-02-grammar-constrained-code-completion",
    "SAC-03-spreadsheet-format-recognition",
    "SAC-04-functional-dependency-testdata",
}
FORBIDDEN_SEMANTIC_PROMOTIONS = {
    "truth",
    "confidence",
    "SEI Unknown",
    "SEI Conflict",
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
REQUIRED_BIO_ABSTRACTIONS = {
    "input-normalization",
    "sparse-expansion-wta",
    "localized-inhibition",
    "biased-sparse-projection",
    "temporal-familiarity",
    "homeostatic-sparsity",
    "compartmental-outcome-learning",
}
REQUIRED_FOLLOW_ON_STAGES = {
    "SAC-B0",
    "SAC-B1",
    "SAC-B2",
    "SAC-B3",
    "SAC-B4",
    "SAC-B5",
    "SAC-B6",
    "SEI-B7",
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

    bio_policy = plan.get("bio_inspired_design_policy")
    if not isinstance(bio_policy, dict):
        errors.append("bio_inspired_design_policy must be an object")
    else:
        for key in (
            "biological_fidelity_required",
            "whole_connectome_simulation_required",
            "biology_is_authority",
        ):
            if bio_policy.get(key) is not False:
                errors.append(f"bio_inspired_design_policy.{key} must remain false")
        if not bio_policy.get("translation_rule"):
            errors.append("bio_inspired_design_policy.translation_rule must be declared")
        if not bio_policy.get("adoption_rule"):
            errors.append("bio_inspired_design_policy.adoption_rule must be declared")

    abstractions = plan.get("biological_abstraction_map")
    if not isinstance(abstractions, list):
        errors.append("biological_abstraction_map must be a list")
    else:
        ids = [item.get("id") for item in abstractions if isinstance(item, dict)]
        if len(ids) != len(abstractions) or len(ids) != len(set(ids)):
            errors.append("biological_abstraction_map ids must be present and unique")
        missing = REQUIRED_BIO_ABSTRACTIONS.difference(ids)
        if missing:
            errors.append(
                "biological_abstraction_map is missing required abstractions: "
                + ", ".join(sorted(missing))
            )
        for item in abstractions:
            if not isinstance(item, dict):
                continue
            for key in (
                "biological_observation",
                "engineering_abstraction",
                "sei_role",
                "adoption_state",
                "risk",
            ):
                if not item.get(key):
                    errors.append(
                        f"biological_abstraction_map.{item.get('id', '<unknown>')}.{key} must be declared"
                    )

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
            isinstance(case, dict) and case.get("domain") == "sei-native" for case in cases
        ):
            errors.append("initial_evaluation_cases must retain a SEI-native case")

    follow_on = plan.get("follow_on_experiments")
    if not isinstance(follow_on, list):
        errors.append("follow_on_experiments must be a list")
    else:
        stages = [item.get("stage") for item in follow_on if isinstance(item, dict)]
        if len(stages) != len(follow_on) or len(stages) != len(set(stages)):
            errors.append("follow_on_experiments stages must be present and unique")
        missing = REQUIRED_FOLLOW_ON_STAGES.difference(stages)
        if missing:
            errors.append(
                "follow_on_experiments is missing required stages: "
                + ", ".join(sorted(missing))
            )

    stage_gate = plan.get("stage_gate_policy")
    if not isinstance(stage_gate, dict):
        errors.append("stage_gate_policy must be an object")
    else:
        if stage_gate.get("no_single_score") is not True:
            errors.append("stage_gate_policy.no_single_score must remain true")
        if stage_gate.get("rejection_is_valid_completion") is not True:
            errors.append("stage_gate_policy.rejection_is_valid_completion must remain true")

    cross_stage = plan.get("cross_stage_evaluation_gate")
    if not isinstance(cross_stage, dict):
        errors.append("cross_stage_evaluation_gate must be an object")
    else:
        if cross_stage.get("state") != "locked-preregistration":
            errors.append("cross_stage_evaluation_gate.state must remain locked-preregistration")
        if cross_stage.get("preregistration_file") != "cross_stage_benchmark_preregistration.json":
            errors.append("cross_stage_evaluation_gate.preregistration_file must remain declared")
        if cross_stage.get("results_generation_enabled") is not False:
            errors.append("cross_stage_evaluation_gate.results_generation_enabled must remain false")
        if cross_stage.get("human_adjudication_required") is not True:
            errors.append("cross_stage_evaluation_gate.human_adjudication_required must remain true")
        if cross_stage.get("human_adjudication_state") not in {"pending", "frozen"}:
            errors.append("cross_stage_evaluation_gate.human_adjudication_state must be pending or frozen")
        if cross_stage.get("variant_set_frozen") is not True:
            errors.append("cross_stage_evaluation_gate.variant_set_frozen must remain true")
        tracks = cross_stage.get("tracks")
        if not isinstance(tracks, list) or set(tracks) != {"retrieval", "familiarity", "routing"}:
            errors.append("cross_stage_evaluation_gate.tracks must remain retrieval/familiarity/routing")
        if cross_stage.get("no_single_composite_score") is not True:
            errors.append("cross_stage_evaluation_gate.no_single_composite_score must remain true")
        if cross_stage.get("b5_entry_gate_changed") is not False:
            errors.append("cross_stage_evaluation_gate.b5_entry_gate_changed must remain false")
        if not cross_stage.get("unlock_rule"):
            errors.append("cross_stage_evaluation_gate.unlock_rule must be declared")

        freeze_kit = cross_stage.get("freeze_kit")
        if not isinstance(freeze_kit, dict):
            errors.append("cross_stage_evaluation_gate.freeze_kit must be an object")
        else:
            if freeze_kit.get("state") not in {"draft", "frozen"}:
                errors.append("cross_stage_evaluation_gate.freeze_kit.state must be draft or frozen")
            if freeze_kit.get("directory") != "cross-stage-freeze":
                errors.append("cross_stage_evaluation_gate.freeze_kit.directory must remain cross-stage-freeze")
            if freeze_kit.get("bundle_ref") != "cross-stage-freeze/freeze_bundle.json":
                errors.append("cross_stage_evaluation_gate.freeze_kit.bundle_ref must remain declared")
            if freeze_kit.get("validator_ref") != "cross-stage-freeze/freeze_manifests.py":
                errors.append("cross_stage_evaluation_gate.freeze_kit.validator_ref must remain declared")
            if freeze_kit.get("evidence_ref") != "cross-stage-freeze/freeze_kit_evidence_2026-09-18.json":
                errors.append("cross_stage_evaluation_gate.freeze_kit.evidence_ref must remain declared")
            frozen = freeze_kit.get("state") == "frozen"
            if freeze_kit.get("current_bundle_is_frozen") is not frozen:
                errors.append(
                    "cross_stage_evaluation_gate.freeze_kit.current_bundle_is_frozen must match state"
                )
            if freeze_kit.get("result_generation_enabled_after_freeze") is not False:
                errors.append(
                    "cross_stage_evaluation_gate.freeze_kit.result_generation_enabled_after_freeze must remain false"
                )
            if freeze_kit.get("b5_entry_gate_changed") is not False:
                errors.append(
                    "cross_stage_evaluation_gate.freeze_kit.b5_entry_gate_changed must remain false"
                )

    deferred = plan.get("deferred_directions")
    if not isinstance(deferred, list):
        errors.append("deferred_directions must be a list")
    else:
        deferred_ids = {
            item.get("id") for item in deferred if isinstance(item, dict) and item.get("id")
        }
        if "whole-connectome-simulation" not in deferred_ids:
            errors.append("deferred_directions must retain whole-connectome-simulation")
        if "autonomous-semantic-salience-learning" not in deferred_ids:
            errors.append(
                "deferred_directions must retain autonomous-semantic-salience-learning"
            )

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
