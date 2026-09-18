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
