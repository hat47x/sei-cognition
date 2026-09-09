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

    def test_soza_native_case_is_required(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["initial_evaluation_cases"][0]["domain"] = "generic-retrieval"
        self.assert_has_error(plan, "must retain a SOZA-native case")

    def test_exact_deterministic_baseline_is_required(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["comparison_baselines"] = [
            item
            for item in plan["comparison_baselines"]
            if item["id"] != "exact-deterministic"
        ]
        self.assert_has_error(plan, "must retain exact-deterministic")

    def test_flyhash_style_candidate_is_not_the_only_allowed_baseline(self) -> None:
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

    def test_design_evidence_is_not_executable_evidence(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["current_evidence"]["level"] = "executable"
        self.assert_has_error(plan, "current_evidence.level must remain design-only")


if __name__ == "__main__":
    unittest.main()
