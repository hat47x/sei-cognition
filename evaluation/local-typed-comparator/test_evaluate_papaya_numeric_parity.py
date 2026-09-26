import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "evaluate_papaya_numeric_parity_tested",
    HERE / "evaluate_papaya_numeric_parity.py",
)
mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = mod
SPEC.loader.exec_module(mod)
POLICY = json.loads((HERE / "papaya_numeric_parity_policy.v1.json").read_text())


def choice(qid="route", p=0.01, c=0.005, equal=True):
    return {
        "question_id": qid,
        "type": "choice",
        "probabilities": {"max_abs_delta": p},
        "confidence_abs_delta": c,
        "choice_selected_equal": equal,
    }


def score(qid="urgency", p=0.01, c=0.005, s=0.02, argmax=True):
    return {
        "question_id": qid,
        "type": "score",
        "probabilities": {"max_abs_delta": p},
        "confidence_abs_delta": c,
        "score_abs_delta": s,
        "score_probability_argmax_equal": argmax,
    }


def noul(qid="review", d=0.01, threshold=True):
    return {
        "question_id": qid,
        "type": "noul",
        "noul_abs_delta": d,
        "noul_threshold_0_5_equal": threshold,
    }


def report():
    return {
        "schema": mod.REPORT_SCHEMA,
        "fixture": {
            "schema": mod.FIXTURE_SCHEMA,
            "sha256": mod.FIXTURE_SHA256,
            "case_ids": list(mod.EXPECTED_CASE_IDS),
        },
        "choice11_sequence_precondition": {
            "schema": mod.CHOICE11_ATTESTATION_SCHEMA,
            "diagnostic_sha256": mod.CHOICE11_DIAGNOSTIC_SHA256,
            "token_count": 155,
            "source_equivalent_exact_sequence_attested": True,
            "live_input_token_count_matched": True,
            "live_input_ids_observed": False,
            "live_marker_positions_observed": False,
        },
        "inputs": {
            "reference": {
                "schema": mod.REFERENCE_RUN_SCHEMA,
                "run_id": "ref",
                "provider": "laya",
                "artifact_sha256": "c" * 64,
            },
            "papaya": {
                "schema": mod.PAPAYA_RUN_SCHEMA,
                "run_id": "pap",
                "provider": "papaya",
                "artifact_sha256": "d" * 64,
            },
            "same_sei_source_git_sha": "1" * 40,
            "provider_provenance_merged": False,
        },
        "cases": [
            {"case_id": "choice-route-a", "questions": [choice("route")]},
            {"case_id": "choice-route-b", "questions": [choice("route")]},
            {"case_id": "score-urgency", "questions": [score()]},
            {
                "case_id": "noul-review",
                "questions": [noul("needs_human_review")],
            },
        ],
        "choice11_diagnostic": {
            "case_id": mod.CHOICE11_CASE_ID,
            "questions": [choice("choice12", p=0.02, c=0.01)],
            "expected_answer": None,
            "quality_claim": False,
        },
        "scope": {
            "complete_managed_capture_inputs_required": True,
            "numeric_parity_threshold_defined": False,
            "numeric_parity_decision": False,
            "task_quality": False,
            "calibration_validity": False,
            "cross_runtime_performance_comparison": False,
            "jev_provider_identity_equivalence": False,
            "reference_provider_promotion": False,
        },
    }


class TestPapayaNumericParityPolicy(unittest.TestCase):
    def test_passing_surface(self):
        out = mod.evaluate(
            copy.deepcopy(POLICY),
            report(),
            policy_sha256="1" * 64,
            report_sha256="2" * 64,
        )
        self.assertEqual(out["decision"], "pass")
        self.assertEqual(out["failures"], [])
        self.assertTrue(
            out["scope"]["bounded_numeric_parity_on_preregistered_surface"]
        )
        self.assertFalse(out["scope"]["shipping_decision"])

    def test_probability_limit_is_fail_closed(self):
        value = report()
        value["cases"][0]["questions"][0]["probabilities"]["max_abs_delta"] = 0.025001
        out = mod.evaluate(copy.deepcopy(POLICY), value)
        self.assertEqual(out["decision"], "fail")
        self.assertEqual(out["failures"][0]["metric"], "probability_max_abs_delta")

    def test_discrete_mismatch_fails_even_with_small_numeric_delta(self):
        value = report()
        value["cases"][2]["questions"][0]["score_probability_argmax_equal"] = False
        out = mod.evaluate(copy.deepcopy(POLICY), value)
        self.assertEqual(out["decision"], "fail")
        self.assertEqual(
            out["failures"][0]["metric"], "score_probability_argmax_equal"
        )

    def test_choice11_uses_separate_preregistered_limit(self):
        value = report()
        value["choice11_diagnostic"]["questions"][0]["probabilities"][
            "max_abs_delta"
        ] = 0.027
        out = mod.evaluate(copy.deepcopy(POLICY), value)
        self.assertEqual(out["decision"], "pass")

        value["choice11_diagnostic"]["questions"][0]["probabilities"][
            "max_abs_delta"
        ] = 0.030001
        out = mod.evaluate(copy.deepcopy(POLICY), value)
        self.assertEqual(out["decision"], "fail")

    def test_missing_or_extra_question_rows_are_rejected(self):
        value = report()
        value["cases"][0]["questions"] = []
        with self.assertRaises(mod.ParityDecisionError):
            mod.evaluate(copy.deepcopy(POLICY), value)

        value = report()
        value["cases"][0]["questions"].append(choice("route"))
        with self.assertRaises(mod.ParityDecisionError):
            mod.evaluate(copy.deepcopy(POLICY), value)

    def test_question_identity_and_type_drift_are_rejected(self):
        value = report()
        value["cases"][3]["questions"][0]["question_id"] = "review"
        with self.assertRaises(mod.ParityDecisionError):
            mod.evaluate(copy.deepcopy(POLICY), value)

        value = report()
        value["cases"][2]["questions"][0]["type"] = "choice"
        with self.assertRaises(mod.ParityDecisionError):
            mod.evaluate(copy.deepcopy(POLICY), value)

    def test_choice11_question_identity_or_type_drift_is_rejected(self):
        value = report()
        value["choice11_diagnostic"]["questions"][0]["question_id"] = "choice13"
        with self.assertRaises(mod.ParityDecisionError):
            mod.evaluate(copy.deepcopy(POLICY), value)

        value = report()
        value["choice11_diagnostic"]["questions"][0]["type"] = "score"
        with self.assertRaises(mod.ParityDecisionError):
            mod.evaluate(copy.deepcopy(POLICY), value)

    def test_negative_delta_is_rejected(self):
        value = report()
        value["cases"][0]["questions"][0]["probabilities"]["max_abs_delta"] = -0.001
        with self.assertRaises(mod.ParityDecisionError):
            mod.evaluate(copy.deepcopy(POLICY), value)

    def test_decision_rule_drift_is_rejected(self):
        policy = copy.deepcopy(POLICY)
        policy["decision_rule"]["all_observed_questions_must_pass"] = False
        with self.assertRaises(mod.ParityDecisionError):
            mod.evaluate(policy, report())

    def test_exact_fixture_and_diagnostic_bytes_are_required(self):
        value = report()
        value["fixture"]["sha256"] = "a" * 64
        with self.assertRaises(mod.ParityDecisionError):
            mod.evaluate(copy.deepcopy(POLICY), value)

        value = report()
        value["choice11_sequence_precondition"]["diagnostic_sha256"] = "b" * 64
        with self.assertRaises(mod.ParityDecisionError):
            mod.evaluate(copy.deepcopy(POLICY), value)

        policy = copy.deepcopy(POLICY)
        policy["surface"]["fixture_sha256"] = "a" * 64
        with self.assertRaises(mod.ParityDecisionError):
            mod.evaluate(policy, report())

        policy = copy.deepcopy(POLICY)
        policy["surface"]["choice11_diagnostic_sha256"] = "b" * 64
        with self.assertRaises(mod.ParityDecisionError):
            mod.evaluate(policy, report())

    def test_managed_input_artifact_sha_is_required(self):
        value = report()
        value["inputs"]["reference"]["artifact_sha256"] = None
        with self.assertRaises(mod.ParityDecisionError):
            mod.evaluate(copy.deepcopy(POLICY), value)

    def test_question_identity_drift_is_rejected(self):
        value = report()
        value["cases"][3]["questions"][0]["question_id"] = "review"
        with self.assertRaises(mod.ParityDecisionError):
            mod.evaluate(copy.deepcopy(POLICY), value)

    def test_choice11_sequence_precondition_drift_is_rejected(self):
        value = report()
        value["choice11_sequence_precondition"]["token_count"] = 154
        with self.assertRaises(mod.ParityDecisionError):
            mod.evaluate(copy.deepcopy(POLICY), value)

    def test_provider_provenance_cannot_be_merged(self):
        value = report()
        value["inputs"]["provider_provenance_merged"] = True
        with self.assertRaises(mod.ParityDecisionError):
            mod.evaluate(copy.deepcopy(POLICY), value)

    def test_policy_managed_schema_drift_is_rejected(self):
        policy = copy.deepcopy(POLICY)
        policy["surface"]["managed_reference_schema"] = "wrong"
        with self.assertRaises(mod.ParityDecisionError):
            mod.evaluate(policy, report())

    def test_raw_report_cannot_arrive_with_decision_already_set(self):
        value = report()
        value["scope"]["numeric_parity_decision"] = True
        with self.assertRaises(mod.ParityDecisionError):
            mod.evaluate(copy.deepcopy(POLICY), value)

    def test_policy_threshold_drift_is_rejected(self):
        policy = copy.deepcopy(POLICY)
        policy["thresholds"]["frozen_cases"]["probability_max_abs_delta_max"] = 0.03
        with self.assertRaises(mod.ParityDecisionError):
            mod.evaluate(policy, report())


if __name__ == "__main__":
    unittest.main()
