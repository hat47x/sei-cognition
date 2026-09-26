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
        "cases": [
            {"case_id": "choice-route-a", "questions": [choice("route")]},
            {"case_id": "choice-route-b", "questions": [choice("route")]},
            {"case_id": "score-urgency", "questions": [score()]},
            {"case_id": "noul-review", "questions": [noul()]},
        ],
        "choice11_diagnostic": {
            "case_id": mod.CHOICE11_CASE_ID,
            "questions": [choice("choice12", p=0.02, c=0.01)],
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
