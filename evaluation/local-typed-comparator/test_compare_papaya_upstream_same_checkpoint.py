import copy
import importlib.util
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "cmp", Path(__file__).with_name("compare_papaya_upstream_same_checkpoint.py")
)
cmp = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(cmp)


def payload(label):
    answers = {
        "c": {
            "type": "choice",
            "choice": "a",
            "probabilities": {"a": 0.6, "b": 0.4},
            "confidence": 0.1,
        },
        "n": {"type": "noul", "noul": 0.7},
        "s1": {
            "type": "score",
            "score": 1.2,
            "probabilities": {"0": 0.2, "1": 0.5, "2": 0.3},
            "confidence": 0.2,
        },
        "s2": {
            "type": "score",
            "score": 2.1,
            "probabilities": {"0": 0.1, "1": 0.3, "2": 0.6},
            "confidence": 0.3,
        },
        "x": {
            "type": "choice",
            "choice": "b",
            "probabilities": {"a": 0.4, "b": 0.6},
            "confidence": 0.1,
        },
    }
    rows = []
    # 48 cases * 5 questions; scale types to 72 choice / 72 noul / 96 score.
    # Cases 0-23: 2 choice,1 noul,2 score. Cases 24-47: 1 choice,2 noul,2 score.
    for i in range(48):
        answer_set = copy.deepcopy(answers)
        if i < 24:
            answer_set.pop("n")
            answer_set["n0"] = {"type": "noul", "noul": 0.7}
        else:
            answer_set.pop("x")
            answer_set["n2"] = {"type": "noul", "noul": 0.8}
        rows.append(
            {
                "id": f"case_{i:06d}",
                "answers": answer_set,
                "usage": {"input_tokens": 10},
            }
        )
    return {
        "label": label,
        "n": 48,
        "mean_s": 1.0 if label == "laya-cpp" else 2.0,
        "total_s": 48.0 if label == "laya-cpp" else 96.0,
        "results": rows,
    }


class TestComparison(unittest.TestCase):
    def test_metrics_and_scope(self):
        a = payload("laya-cpp")
        b = payload("navopw-typed")
        out = cmp.compare_payloads(a, b)
        self.assertEqual(
            out["population"]["by_type"],
            {"choice": 72, "noul": 72, "score": 96},
        )
        self.assertEqual(
            out["agreement"]["published_discrete_scope"],
            {
                "agree": 144,
                "n": 144,
                "meaning": (
                    "choice selected label plus noul thresholded at 0.5; "
                    "score is excluded"
                ),
            },
        )
        self.assertEqual(out["source"]["papaya_results"]["label"], "laya-cpp")
        self.assertEqual(out["source"]["onnx_results"]["label"], "navopw-typed")
        self.assertEqual(
            out["agreement"]["score_probability_argmax"]["agree"],
            96,
        )
        self.assertFalse(out["scope"]["python_laya_reference_comparison"])
        self.assertTrue(out["scope"]["tolerance_context_only"])

    def test_score_argmax_mismatch_is_not_counted_as_published_discrete(self):
        a = payload("laya-cpp")
        b = payload("navopw-typed")
        b["results"][0]["answers"]["s1"]["probabilities"] = {
            "0": 0.2,
            "1": 0.3,
            "2": 0.5,
        }
        out = cmp.compare_payloads(a, b)
        self.assertEqual(
            out["agreement"]["published_discrete_scope"]["agree"],
            144,
        )
        self.assertEqual(
            out["agreement"]["score_probability_argmax"]["agree"],
            95,
        )
        self.assertEqual(
            len(out["agreement"]["score_probability_argmax"]["mismatches"]),
            1,
        )

    def test_case_order_drift_rejected(self):
        a = payload("laya-cpp")
        b = payload("navopw-typed")
        b["results"][0], b["results"][1] = (
            b["results"][1],
            b["results"][0],
        )
        with self.assertRaises(cmp.ComparisonError):
            cmp.compare_payloads(a, b)

    def test_question_order_drift_rejected(self):
        a = payload("laya-cpp")
        b = payload("navopw-typed")
        answers = b["results"][0]["answers"]
        b["results"][0]["answers"] = {
            key: answers[key] for key in reversed(list(answers))
        }
        with self.assertRaises(cmp.ComparisonError):
            cmp.compare_payloads(a, b)

    def test_git_blob_oid(self):
        self.assertEqual(
            cmp.git_blob_oid(b"hello\n"),
            "ce013625030ba8dba906f756967f9e9ca394464a",
        )


if __name__ == "__main__":
    unittest.main()
