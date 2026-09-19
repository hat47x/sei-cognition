from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVALUATION_DIR = ROOT / "evaluation" / "sparse-associative-cognition"
if str(EVALUATION_DIR) not in sys.path:
    sys.path.insert(0, str(EVALUATION_DIR))

from validate_research_plan import validate_research_plan  # noqa: E402

PLAN_PATH = EVALUATION_DIR / "research_plan.json"


class SparseAssociativeCognitionResearchPlanTests(unittest.TestCase):
    def setUp(self) -> None:
        self.plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))

    def assert_has_error(self, plan: dict, fragment: str) -> None:
        errors = validate_research_plan(plan)
        self.assertTrue(
            any(fragment in error for error in errors),
            f"expected error containing {fragment!r}; got {errors!r}",
        )

    def test_current_plan_is_valid(self) -> None:
        self.assertEqual(validate_research_plan(self.plan), [])

    def test_plan_cannot_be_promoted_to_universal_contract_by_flag(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["architectural_position"]["requires_universal_contract_change"] = True
        self.assert_has_error(plan, "requires_universal_contract_change must remain false")

    def test_plan_cannot_become_mandatory_pipeline(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["architectural_position"]["is_mandatory_pipeline"] = True
        self.assert_has_error(plan, "is_mandatory_pipeline must remain false")

    def test_ownership_does_not_force_deployment(self) -> None:
        for key in ("ownership_is_deployment", "network_service_required"):
            with self.subTest(key=key):
                plan = copy.deepcopy(self.plan)
                plan["placement_policy"][key] = True
                self.assert_has_error(plan, f"placement_policy.{key} must remain false")

    def test_biology_cannot_become_architectural_authority(self) -> None:
        for key in (
            "biological_fidelity_required",
            "whole_connectome_simulation_required",
            "biology_is_authority",
        ):
            with self.subTest(key=key):
                plan = copy.deepcopy(self.plan)
                plan["bio_inspired_design_policy"][key] = True
                self.assert_has_error(plan, f"bio_inspired_design_policy.{key} must remain false")

    def test_required_bio_abstractions_cannot_disappear_silently(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["biological_abstraction_map"] = [
            item
            for item in plan["biological_abstraction_map"]
            if item["id"] != "localized-inhibition"
        ]
        self.assert_has_error(plan, "missing required abstractions")

    def test_whole_connectome_simulation_remains_deferred(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["deferred_directions"] = [
            item
            for item in plan["deferred_directions"]
            if item["id"] != "whole-connectome-simulation"
        ]
        self.assert_has_error(plan, "must retain whole-connectome-simulation")

    def test_autonomous_semantic_salience_learning_remains_deferred(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["deferred_directions"] = [
            item
            for item in plan["deferred_directions"]
            if item["id"] != "autonomous-semantic-salience-learning"
        ]
        self.assert_has_error(plan, "must retain autonomous-semantic-salience-learning")

    def test_follow_on_experiment_stages_cannot_disappear_silently(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["follow_on_experiments"] = [
            item for item in plan["follow_on_experiments"] if item["stage"] != "SAC-B4"
        ]
        self.assert_has_error(plan, "missing required stages")

    def test_b6i_follow_on_stage_cannot_disappear_silently(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["follow_on_experiments"] = [
            item for item in plan["follow_on_experiments"] if item["stage"] != "SAC-B6i"
        ]
        self.assert_has_error(plan, "missing required stages")

    def test_rejection_remains_valid_research_completion(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["stage_gate_policy"]["rejection_is_valid_completion"] = False
        self.assert_has_error(plan, "rejection_is_valid_completion must remain true")

    def test_cross_stage_preregistration_remains_locked(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["cross_stage_evaluation_gate"]["results_generation_enabled"] = True
        self.assert_has_error(plan, "results_generation_enabled must remain false")

    def test_cross_stage_gate_cannot_open_b5(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["cross_stage_evaluation_gate"]["b5_entry_gate_changed"] = True
        self.assert_has_error(plan, "b5_entry_gate_changed must remain false")

    def test_cross_stage_freeze_kit_state_flag_must_match(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["cross_stage_evaluation_gate"]["freeze_kit"]["state"] = "frozen"
        self.assert_has_error(plan, "current_bundle_is_frozen must match state")

    def test_cross_stage_freeze_kit_cannot_enable_results(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["cross_stage_evaluation_gate"]["freeze_kit"][
            "result_generation_enabled_after_freeze"
        ] = True
        self.assert_has_error(
            plan,
            "result_generation_enabled_after_freeze must remain false",
        )

    def test_cross_stage_freeze_kit_cannot_open_b5(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["cross_stage_evaluation_gate"]["freeze_kit"]["b5_entry_gate_changed"] = True
        self.assert_has_error(plan, "freeze_kit.b5_entry_gate_changed must remain false")

    def test_cross_stage_evaluation_run_state_flag_must_match(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["cross_stage_evaluation_gate"]["evaluation_run"]["state"] = "authorized"
        self.assert_has_error(plan, "current_run_authorized must match state")

    def test_cross_stage_evaluation_run_stop_lines_remain_closed(self) -> None:
        for key in (
            "executor_implemented",
            "result_artifact_generated",
            "b5_entry_gate_changed",
            "production_default_changed",
        ):
            with self.subTest(key=key):
                plan = copy.deepcopy(self.plan)
                plan["cross_stage_evaluation_gate"]["evaluation_run"][key] = True
                self.assert_has_error(plan, f"evaluation_run.{key} must remain false")

    def test_cross_stage_evaluation_run_runtime_evidence_floor_is_retained(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["cross_stage_evaluation_gate"]["evaluation_run"]["runtime_tests_passed"] = 19
        self.assert_has_error(plan, "runtime_tests_passed must be >= 20")
        plan = copy.deepcopy(self.plan)
        plan["cross_stage_evaluation_gate"]["evaluation_run"]["integration_tests_passed"] = 40
        self.assert_has_error(plan, "integration_tests_passed must be >= 41")

    def test_cross_stage_result_artifact_state_flag_must_match(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["cross_stage_evaluation_gate"]["result_artifact"]["state"] = "completed"
        self.assert_has_error(plan, "current_result_completed must match state")

    def test_cross_stage_result_artifact_cannot_become_interpretation_or_decision(self) -> None:
        for key in (
            "semantic_interpretation_generated",
            "b5_entry_gate_changed",
            "production_default_changed",
        ):
            with self.subTest(key=key):
                plan = copy.deepcopy(self.plan)
                plan["cross_stage_evaluation_gate"]["result_artifact"][key] = True
                self.assert_has_error(plan, f"result_artifact.{key} must remain false")

    def test_cross_stage_interpretation_artifact_state_flag_must_match(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["cross_stage_evaluation_gate"]["interpretation_artifact"]["state"] = "interpreted"
        self.assert_has_error(
            plan,
            "current_interpretation_generated must match state",
        )

    def test_cross_stage_interpretation_requires_completed_result(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["cross_stage_evaluation_gate"]["interpretation_artifact"][
            "requires_completed_result"
        ] = False
        self.assert_has_error(
            plan,
            "requires_completed_result must remain true",
        )

    def test_cross_stage_interpreted_state_requires_completed_result_state(self) -> None:
        plan = copy.deepcopy(self.plan)
        artifact = plan["cross_stage_evaluation_gate"]["interpretation_artifact"]
        artifact.update({
            "state": "interpreted",
            "current_interpretation_generated": True,
        })
        self.assert_has_error(
            plan,
            "interpreted state requires completed result",
        )

    def test_cross_stage_interpretation_cannot_become_decision(self) -> None:
        for key in (
            "semantic_truth_claimed",
            "variant_winner_declared",
            "recommendation_generated",
            "b5_decision_generated",
            "production_default_changed",
        ):
            with self.subTest(key=key):
                plan = copy.deepcopy(self.plan)
                plan["cross_stage_evaluation_gate"]["interpretation_artifact"][key] = True
                self.assert_has_error(
                    plan,
                    f"interpretation_artifact.{key} must remain false",
                )

    def test_cross_stage_result_runtime_metadata_is_pinned(self) -> None:
        for key, value in (
            (
                "runtime_evidence_ref",
                "cross-stage-result/result_runtime_evidence_2026-09-18.json",
            ),
            (
                "runtime_validation_state",
                "passed-current-draft-and-synthetic-regression",
            ),
        ):
            with self.subTest(key=key):
                plan = copy.deepcopy(self.plan)
                plan["cross_stage_evaluation_gate"]["result_artifact"][key] = "stale"
                self.assert_has_error(plan, f"result_artifact.{key} must remain")

    def test_cross_stage_result_runtime_test_floors_are_retained(self) -> None:
        floors = {
            "runtime_tests_passed": 24,
            "integration_tests_passed": 65,
            "total_tests_passed": 89,
        }
        for key, minimum in floors.items():
            with self.subTest(key=key):
                plan = copy.deepcopy(self.plan)
                plan["cross_stage_evaluation_gate"]["result_artifact"][key] = minimum - 1
                self.assert_has_error(
                    plan,
                    f"result_artifact.{key} must be >= {minimum}",
                )
        plan = copy.deepcopy(self.plan)
        plan["cross_stage_evaluation_gate"]["result_artifact"]["total_tests_passed"] = True
        self.assert_has_error(plan, "result_artifact.total_tests_passed must be >= 89")

    def test_cross_stage_interpretation_runtime_metadata_is_pinned(self) -> None:
        mutations = (
            ("runtime_evidence_ref", "stale"),
            ("upstream_integration_runtime_evidence", False),
            ("runtime_validation_state", "stale"),
        )
        for key, value in mutations:
            with self.subTest(key=key):
                plan = copy.deepcopy(self.plan)
                plan["cross_stage_evaluation_gate"]["interpretation_artifact"][key] = value
                self.assert_has_error(plan, f"interpretation_artifact.{key} must remain")

    def test_cross_stage_interpretation_runtime_test_floors_are_retained(self) -> None:
        floors = {
            "runtime_tests_passed": 27,
            "upstream_regression_tests_passed": 94,
            "total_tests_passed": 121,
        }
        for key, minimum in floors.items():
            with self.subTest(key=key):
                plan = copy.deepcopy(self.plan)
                plan["cross_stage_evaluation_gate"]["interpretation_artifact"][key] = minimum - 1
                self.assert_has_error(
                    plan,
                    f"interpretation_artifact.{key} must be >= {minimum}",
                )
        plan = copy.deepcopy(self.plan)
        plan["cross_stage_evaluation_gate"]["interpretation_artifact"][
            "total_tests_passed"
        ] = True
        self.assert_has_error(
            plan,
            "interpretation_artifact.total_tests_passed must be >= 121",
        )

    def test_cross_stage_execution_attempt_draft_is_registered(self) -> None:
        artifact = self.plan["cross_stage_evaluation_gate"]["execution_attempt"]
        self.assertEqual(artifact["state"], "draft")
        self.assertFalse(artifact["current_attempt_completed"])
        self.assertFalse(artifact["benchmark_result_generated"])
        self.assertTrue(artifact["upstream_integration_runtime_evidence"])

    def test_cross_stage_execution_attempt_state_flag_must_match(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["cross_stage_evaluation_gate"]["execution_attempt"]["state"] = "completed"
        self.assert_has_error(
            plan,
            "execution_attempt.current_attempt_completed must match state",
        )

    def test_cross_stage_execution_attempt_stop_lines_remain_closed(self) -> None:
        for key in (
            "benchmark_result_generated",
            "b5_entry_gate_changed",
            "production_default_changed",
        ):
            with self.subTest(key=key):
                plan = copy.deepcopy(self.plan)
                plan["cross_stage_evaluation_gate"]["execution_attempt"][key] = True
                self.assert_has_error(plan, f"execution_attempt.{key} must remain false")

    def test_cross_stage_execution_attempt_runtime_metadata_is_pinned(self) -> None:
        mutations = (
            ("runtime_evidence_ref", "stale"),
            ("upstream_integration_runtime_evidence", False),
            ("runtime_validation_state", "stale"),
        )
        for key, value in mutations:
            with self.subTest(key=key):
                plan = copy.deepcopy(self.plan)
                plan["cross_stage_evaluation_gate"]["execution_attempt"][key] = value
                self.assert_has_error(plan, f"execution_attempt.{key} must remain")

    def test_cross_stage_execution_attempt_runtime_test_floors_are_retained(self) -> None:
        floors = {
            "focused_tests_passed": 20,
            "integration_tests_passed": 6,
            "upstream_regression_tests_passed": 70,
            "total_tests_passed": 96,
        }
        for key, minimum in floors.items():
            with self.subTest(key=key):
                plan = copy.deepcopy(self.plan)
                plan["cross_stage_evaluation_gate"]["execution_attempt"][key] = minimum - 1
                self.assert_has_error(
                    plan,
                    f"execution_attempt.{key} must be >= {minimum}",
                )
        plan = copy.deepcopy(self.plan)
        plan["cross_stage_evaluation_gate"]["execution_attempt"][
            "total_tests_passed"
        ] = True
        self.assert_has_error(
            plan,
            "execution_attempt.total_tests_passed must be >= 96",
        )

    def test_remaining_cross_stage_runtime_evidence_refs_must_remain_supported(self) -> None:
        refs = (
            "cross-stage-result/result_runtime_evidence_2026-09-18.json",
            "cross-stage-interpretation/interpretation_runtime_evidence_2026-09-19.json",
            "cross-stage-attempt/execution_attempt_runtime_evidence_2026-09-19.json",
        )
        for ref in refs:
            with self.subTest(ref=ref):
                plan = copy.deepcopy(self.plan)
                plan["current_evidence"]["supporting_evidence_files"] = [
                    item
                    for item in plan["current_evidence"]["supporting_evidence_files"]
                    if item != ref
                ]
                self.assert_has_error(plan, f"must retain {ref}")

    def test_cross_stage_decision_artifact_draft_is_registered(self) -> None:
        artifact = self.plan["cross_stage_evaluation_gate"]["decision_artifact"]
        self.assertEqual(artifact["state"], "draft")
        self.assertFalse(artifact["current_decision_generated"])
        self.assertEqual(artifact["current_disposition"], "not-assessed")
        self.assertTrue(artifact["requires_interpreted_artifact"])
        self.assertFalse(artifact["b5_review_requested"])

    def test_cross_stage_decision_state_flag_must_match(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["cross_stage_evaluation_gate"]["decision_artifact"]["state"] = "decided"
        self.assert_has_error(
            plan,
            "decision_artifact.current_decision_generated must match state",
        )

    def test_cross_stage_decision_requires_interpreted_artifact(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["cross_stage_evaluation_gate"]["decision_artifact"][
            "requires_interpreted_artifact"
        ] = False
        self.assert_has_error(
            plan,
            "decision_artifact.requires_interpreted_artifact must remain true",
        )

    def test_cross_stage_decided_state_requires_interpreted_state(self) -> None:
        plan = copy.deepcopy(self.plan)
        artifact = plan["cross_stage_evaluation_gate"]["decision_artifact"]
        artifact.update({
            "state": "decided",
            "current_decision_generated": True,
            "current_disposition": "retain-current-stage",
        })
        self.assert_has_error(
            plan,
            "decided state requires interpreted interpretation",
        )

    def test_cross_stage_request_b5_review_does_not_open_gate(self) -> None:
        plan = copy.deepcopy(self.plan)
        result = plan["cross_stage_evaluation_gate"]["result_artifact"]
        result.update({
            "state": "completed",
            "current_result_completed": True,
        })
        interpretation = plan["cross_stage_evaluation_gate"]["interpretation_artifact"]
        interpretation.update({
            "state": "interpreted",
            "current_interpretation_generated": True,
        })
        decision = plan["cross_stage_evaluation_gate"]["decision_artifact"]
        decision.update({
            "state": "decided",
            "current_decision_generated": True,
            "current_disposition": "request-b5-review",
            "b5_review_requested": True,
        })
        self.assertEqual(validate_research_plan(plan), [])
        self.assertFalse(decision["b5_gate_opened"])

    def test_cross_stage_decision_cannot_become_truth_winner_gate_or_production(self) -> None:
        for key in (
            "semantic_truth_claimed",
            "variant_winner_selected",
            "b5_gate_opened",
            "production_default_changed",
        ):
            with self.subTest(key=key):
                plan = copy.deepcopy(self.plan)
                plan["cross_stage_evaluation_gate"]["decision_artifact"][key] = True
                self.assert_has_error(
                    plan,
                    f"decision_artifact.{key} must remain false",
                )

    def test_cross_stage_decision_runtime_metadata_is_pinned(self) -> None:
        for key, value in (
            (
                "contract_validation_state",
                "runtime-validated-contract-and-synthetic-upstream-regression",
            ),
            ("runtime_execution_observed", True),
            (
                "runtime_evidence_ref",
                "cross-stage-decision/decision_runtime_evidence_2026-09-19.json",
            ),
            (
                "runtime_validation_state",
                "passed-current-draft-and-synthetic-upstream-regression",
            ),
        ):
            with self.subTest(key=key):
                plan = copy.deepcopy(self.plan)
                plan["cross_stage_evaluation_gate"]["decision_artifact"][key] = (
                    False if isinstance(value, bool) else "stale"
                )
                self.assert_has_error(plan, f"decision_artifact.{key} must remain")

    def test_cross_stage_decision_runtime_test_floors_are_retained(self) -> None:
        floors = {
            "decision_tests_defined": 27,
            "preregistration_tests_defined": 38,
            "research_plan_tests_defined": 39,
            "total_tests_defined": 104,
            "decision_tests_passed": 27,
            "upstream_regression_tests_passed": 127,
            "total_tests_passed": 154,
        }
        for key, minimum in floors.items():
            with self.subTest(key=key):
                plan = copy.deepcopy(self.plan)
                plan["cross_stage_evaluation_gate"]["decision_artifact"][key] = (
                    minimum - 1
                )
                self.assert_has_error(
                    plan,
                    f"decision_artifact.{key} must be >= {minimum}",
                )

    def test_cross_stage_decision_runtime_test_floors_reject_bool(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["cross_stage_evaluation_gate"]["decision_artifact"][
            "total_tests_passed"
        ] = True
        self.assert_has_error(
            plan,
            "decision_artifact.total_tests_passed must be >= 154",
        )

    def test_decision_runtime_evidence_must_remain_in_supporting_files(self) -> None:
        plan = copy.deepcopy(self.plan)
        ref = "cross-stage-decision/decision_runtime_evidence_2026-09-19.json"
        plan["current_evidence"]["supporting_evidence_files"] = [
            item
            for item in plan["current_evidence"]["supporting_evidence_files"]
            if item != ref
        ]
        self.assert_has_error(
            plan,
            "supporting_evidence_files must retain decision runtime Evidence",
        )

    def test_hybrid_call_avoidance_evidence_must_remain_in_supporting_files(self) -> None:
        plan = copy.deepcopy(self.plan)
        ref = "hybrid_model_call_avoidance_evidence_2026-09-19.json"
        plan["current_evidence"]["supporting_evidence_files"] = [
            item
            for item in plan["current_evidence"]["supporting_evidence_files"]
            if item != ref
        ]
        self.assert_has_error(
            plan,
            "supporting_evidence_files must retain hybrid call-avoidance Evidence",
        )

    def test_b6i_governance_runtime_evidence_must_remain_supported(self) -> None:
        plan = copy.deepcopy(self.plan)
        ref = "workload_class_governance_runtime_evidence_2026-09-19.json"
        plan["current_evidence"]["supporting_evidence_files"] = [
            item
            for item in plan["current_evidence"]["supporting_evidence_files"]
            if item != ref
        ]
        self.assert_has_error(
            plan,
            "supporting_evidence_files must retain SAC-B6i governance runtime Evidence",
        )

    def test_hybrid_call_avoidance_real_workload_boundary_is_required(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["current_evidence"]["not_yet_verified"] = [
            item
            for item in plan["current_evidence"]["not_yet_verified"]
            if "実SEI workloadでのLLM呼び出し削減量" not in item
        ]
        self.assert_has_error(
            plan,
            "not_yet_verified must retain real-workload LLM-call-reduction boundary",
        )

    def test_hybrid_call_avoidance_boundary_retains_non_promotion_fragments(self) -> None:
        required_fragments = (
            "3/7",
            "actual model telemetry",
            "task success",
            "total system cost",
            "未検証",
        )
        for fragment in required_fragments:
            with self.subTest(fragment=fragment):
                plan = copy.deepcopy(self.plan)
                items = plan["current_evidence"]["not_yet_verified"]
                plan["current_evidence"]["not_yet_verified"] = [
                    (
                        item.replace(fragment, "removed")
                        if "実SEI workloadでのLLM呼び出し削減量" in item
                        else item
                    )
                    for item in items
                ]
                self.assert_has_error(
                    plan,
                    f"hybrid call-avoidance boundary must retain {fragment}",
                )

    def test_b6i_real_governance_boundary_is_required(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["current_evidence"]["not_yet_verified"] = [
            item
            for item in plan["current_evidence"]["not_yet_verified"]
            if "SAC-B6i governance contract" not in item
        ]
        self.assert_has_error(
            plan,
            "not_yet_verified must retain SAC-B6i real-governance boundary",
        )

    def test_b6i_real_governance_boundary_retains_non_promotion_fragments(self) -> None:
        required_fragments = (
            "実workload class taxonomy",
            "宣言error rate",
            "human reviewer governance process",
            "production activation",
            "未検証",
        )
        for fragment in required_fragments:
            with self.subTest(fragment=fragment):
                plan = copy.deepcopy(self.plan)
                items = plan["current_evidence"]["not_yet_verified"]
                plan["current_evidence"]["not_yet_verified"] = [
                    (
                        item.replace(fragment, "removed")
                        if "SAC-B6i governance contract" in item
                        else item
                    )
                    for item in items
                ]
                self.assert_has_error(
                    plan,
                    f"SAC-B6i boundary must retain {fragment}",
                )

    def test_llm_is_not_required_or_default_fallback(self) -> None:
        for key in ("llm_required", "llm_is_fallback_by_default"):
            with self.subTest(key=key):
                plan = copy.deepcopy(self.plan)
                plan["llm_boundary"][key] = True
                self.assert_has_error(plan, f"llm_boundary.{key} must remain false")

    def test_candidate_recall_cannot_silently_become_decision_semantics(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["semantic_stop_lines"] = [
            line for line in plan["semantic_stop_lines"] if "Decision" not in line
        ]
        self.assert_has_error(plan, "semantic stop line missing for Decision")

    def test_sei_native_case_is_required(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["initial_evaluation_cases"][0]["domain"] = "generic-retrieval"
        self.assert_has_error(plan, "must retain a SEI-native case")

    def test_exact_deterministic_baseline_is_required(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["comparison_baselines"] = [
            item
            for item in plan["comparison_baselines"]
            if item["id"] != "exact-deterministic"
        ]
        self.assert_has_error(plan, "must retain exact-deterministic")

    def test_sparse_expansion_candidate_is_required(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["comparison_baselines"] = [
            item
            for item in plan["comparison_baselines"]
            if item["id"] != "sparse-random-expansion-kwta"
        ]
        self.assert_has_error(plan, "must retain sparse-random-expansion-kwta")

    def test_single_composite_score_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["evaluation_policy"]["single_composite_score"] = True
        self.assert_has_error(plan, "single_composite_score must remain false")

    def test_first_slice_remains_cpu_offline_capable(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["implementation_policy"]["gpu_required"] = True
        plan["implementation_policy"]["offline_capable_target"] = False
        errors = validate_research_plan(plan)
        self.assertTrue(any("gpu_required" in error for error in errors), errors)
        self.assertTrue(any("offline_capable_target" in error for error in errors), errors)

    def test_executable_evaluation_is_not_promoted_to_production_evidence(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["current_evidence"]["level"] = "production"
        self.assert_has_error(plan, "current_evidence.level must remain executable-evaluation")

    def test_execution_evidence_file_is_required(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["current_evidence"].pop("evidence_file", None)
        self.assert_has_error(plan, "current_evidence.evidence_file must be declared")


if __name__ == "__main__":
    unittest.main()
