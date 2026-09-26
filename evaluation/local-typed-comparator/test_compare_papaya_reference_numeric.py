import copy
import hashlib
import importlib.util
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "compare_papaya_reference_numeric",
    HERE / "compare_papaya_reference_numeric.py",
)
mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = mod
SPEC.loader.exec_module(mod)

FIXTURE = json.loads((HERE / "fixture.v1.json").read_text(encoding="utf-8"))
FIXTURE_RAW = (HERE / "fixture.v1.json").read_bytes()


def compact(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def response_for(case):
    request = case["request"]
    qid, q = next(iter(request["questions"].items()))
    if q["type"] == "choice":
        keys = list(q["criteria"])
        probs = {key: 1.0 / len(keys) for key in keys}
        answer = {
            "type": "choice",
            "choice": keys[0],
            "probabilities": probs,
            "confidence": 0.25,
        }
    elif q["type"] == "score":
        probs = {str(i): 0.25 for i in range(len(q["criteria"]))}
        answer = {
            "type": "score",
            "score": 1.5,
            "legend": {str(i): v for i, v in enumerate(q["criteria"])},
            "probabilities": probs,
            "confidence": 0.25,
        }
    else:
        answer = {"type": "noul", "noul": 0.4}
    return qid, answer


def record(case, model, *, reference):
    request = copy.deepcopy(case["request"])
    request["model"] = model
    qid, answer = response_for(case)
    response = {
        "model": model,
        "answers": {qid: answer},
        "usage": {"input_tokens": 10, "output_tokens": 1},
    }
    if reference:
        response["routing"] = {"model": mod.REFERENCE_LOGICAL_MODEL}
    req = compact(request)
    resp = compact(response)
    row = {
        "case_id": case["case_id"],
        "http_status": 200,
        "request_utf8": req,
        "response_utf8": resp,
        "request_sha256": hashlib.sha256(req.encode()).hexdigest(),
        "response_sha256": hashlib.sha256(resp.encode()).hexdigest(),
        "round_trip_latency_ms": 5.0,
        "response_model": model,
        "contract": "pass",
    }
    if reference:
        row["routing_model"] = mod.REFERENCE_LOGICAL_MODEL
    else:
        row["diagnostic"] = False
        row["input_tokens"] = 10
        row["retained_replay_input_tokens"] = 10
        row["live_token_count_matches_replay"] = True
    return row


def reference_run():
    fixture_sha = hashlib.sha256(FIXTURE_RAW).hexdigest()
    return {
        "schema": mod.REFERENCE_RUN_SCHEMA,
        "status": "complete",
        "run_id": "ref",
        "provider": {"name": "laya"},
        "checkpoint": {
            "repository": mod.REFERENCE_REPOSITORY,
            "hub_revision": mod.REFERENCE_REVISION,
            "logical_model": mod.REFERENCE_LOGICAL_MODEL,
            "model_artifact": {
                "sha256": mod.REFERENCE_MODEL_SHA256,
                "size_bytes": mod.REFERENCE_MODEL_BYTES,
            },
            "runtime_binding": {"logical_checkpoint_observed": True},
        },
        "fixture": {"sha256": fixture_sha, "case_count": 4},
        "cases": [
            record(c, mod.REFERENCE_RESPONSE_MODEL, reference=True)
            for c in FIXTURE["cases"]
        ],
    }


def papaya_run():
    fixture_sha = hashlib.sha256(FIXTURE_RAW).hexdigest()
    diag = {
        "case_id": "choice-12-clamp-path",
        "diagnostic": True,
    }
    return {
        "schema": mod.PAPAYA_RUN_SCHEMA,
        "status": "complete",
        "run_id": "pap",
        "provider": {
            "name": "papaya",
            "identity": mod.PAPAYA_RESPONSE_MODEL,
            "jev_provider_identity": False,
            "python_laya_reference_identity": False,
        },
        "fixture": {"sha256": fixture_sha, "case_count": 4},
        "scope": {
            "papaya_runtime_source_verified": True,
            "papaya_live_inference": True,
            "frozen_protocol_contract": True,
            "frozen_live_token_count_matches_replay": True,
            "choice11_overlay_path_exercised": True,
            "numeric_parity_with_python_laya": False,
            "task_quality": False,
            "calibration_validity": False,
            "jev_provider_identity": False,
            "reference_provider_promotion": False,
        },
        "overlay": {"verification_after_health_before_inference": {"valid": True}},
        "frozen_cases": [
            record(c, mod.PAPAYA_RESPONSE_MODEL, reference=False)
            for c in FIXTURE["cases"]
        ],
        "diagnostic_cases": [diag],
    }


class NumericComparatorTest(unittest.TestCase):
    def test_identical_synthetic_outputs_measure_zero_without_parity_decision(self):
        report = mod.compare_runs(
            copy.deepcopy(FIXTURE),
            FIXTURE_RAW,
            reference_run(),
            papaya_run(),
        )
        self.assertEqual(report["aggregate"]["max_probability_abs_delta"], 0.0)
        self.assertEqual(report["aggregate"]["max_score_or_noul_abs_delta"], 0.0)
        self.assertFalse(report["scope"]["numeric_parity_threshold_defined"])
        self.assertFalse(report["scope"]["numeric_parity_decision"])
        self.assertFalse(report["inputs"]["provider_provenance_merged"])

    def test_probability_delta_is_measured(self):
        pap = papaya_run()
        row = pap["frozen_cases"][0]
        response = json.loads(row["response_utf8"])
        probs = response["answers"]["route"]["probabilities"]
        keys = list(probs)
        probs[keys[0]] += 0.1
        probs[keys[1]] -= 0.1
        raw = compact(response)
        row["response_utf8"] = raw
        row["response_sha256"] = hashlib.sha256(raw.encode()).hexdigest()
        report = mod.compare_runs(FIXTURE, FIXTURE_RAW, reference_run(), pap)
        self.assertAlmostEqual(
            report["cases"][0]["questions"][0]["probabilities"]["total_variation_distance"],
            0.1,
        )

    def test_incomplete_run_is_rejected(self):
        pap = papaya_run()
        pap["status"] = "incomplete"
        with self.assertRaises(mod.NumericComparisonError):
            mod.compare_runs(FIXTURE, FIXTURE_RAW, reference_run(), pap)

    def test_fixture_binding_drift_is_rejected(self):
        pap = papaya_run()
        pap["fixture"]["sha256"] = "0" * 64
        with self.assertRaises(mod.NumericComparisonError):
            mod.compare_runs(FIXTURE, FIXTURE_RAW, reference_run(), pap)

    def test_provider_identity_collapse_is_rejected(self):
        pap = papaya_run()
        pap["provider"]["jev_provider_identity"] = True
        with self.assertRaises(mod.NumericComparisonError):
            mod.compare_runs(FIXTURE, FIXTURE_RAW, reference_run(), pap)

    def test_papaya_numeric_parity_preclaim_is_rejected(self):
        pap = papaya_run()
        pap["scope"]["numeric_parity_with_python_laya"] = True
        with self.assertRaises(mod.NumericComparisonError):
            mod.compare_runs(FIXTURE, FIXTURE_RAW, reference_run(), pap)

    def test_request_semantics_drift_is_rejected(self):
        pap = papaya_run()
        row = pap["frozen_cases"][0]
        request = json.loads(row["request_utf8"])
        request["state"]["retry_count"] = 99
        raw = compact(request)
        row["request_utf8"] = raw
        row["request_sha256"] = hashlib.sha256(raw.encode()).hexdigest()
        with self.assertRaises(mod.NumericComparisonError):
            mod.compare_runs(FIXTURE, FIXTURE_RAW, reference_run(), pap)


if __name__ == "__main__":
    unittest.main()
