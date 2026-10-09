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

FIXTURE_RAW = (HERE / "fixture.v1.json").read_bytes()
FIXTURE = json.loads(FIXTURE_RAW)
DIAGNOSTIC_RAW = (HERE / "papaya_choice11_diagnostic.v1.json").read_bytes()
DIAGNOSTIC = json.loads(DIAGNOSTIC_RAW)
CHOICE11 = json.loads(
    (HERE / "choice11_sequence_attestation.v1.json").read_text(encoding="utf-8")
)
SOURCE_SHA = "1" * 40


def compact(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def answer_for(question):
    kind = question["type"]
    if kind == "choice":
        keys = list(question["criteria"])
        p = 1.0 / len(keys)
        return {
            "type": kind,
            "choice": keys[0],
            "probabilities": {key: p for key in keys},
            "confidence": 0.25,
        }
    if kind == "score":
        n = len(question["criteria"])
        p = 1.0 / n
        return {
            "type": kind,
            "score": sum(i * p for i in range(n)),
            "legend": {str(i): value for i, value in enumerate(question["criteria"])},
            "probabilities": {str(i): p for i in range(n)},
            "confidence": 0.25,
        }
    return {"type": "noul", "noul": 0.4}


def record(case, model, *, reference, diagnostic=False, input_tokens=10):
    request = copy.deepcopy(case["request"])
    request["model"] = model
    qid, question = next(iter(case["request"]["questions"].items()))
    response = {
        "model": model,
        "answers": {qid: answer_for(question)},
        "usage": {"input_tokens": input_tokens, "output_tokens": 1},
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
        if not diagnostic:
            row["input_tokens"] = input_tokens
            row["expected_reference_input_tokens"] = input_tokens
            row["live_token_count_matches_reference"] = True
    else:
        row["diagnostic"] = diagnostic
        row["input_tokens"] = input_tokens
        if not diagnostic:
            row["retained_replay_input_tokens"] = input_tokens
            row["live_token_count_matches_replay"] = True
    return row


def reference_verification():
    return {
        "valid": True,
        "source_repository": mod.REFERENCE_REPOSITORY,
        "source_revision": mod.REFERENCE_REVISION,
        "runtime_consumed_files": {
            "model.safetensors": {
                "sha256": mod.REFERENCE_MODEL_SHA256,
                "bytes": mod.REFERENCE_MODEL_BYTES,
            }
        },
        "tokenizer_config_rewrite_required": False,
        "raw_choice_11_plus_temperature": 0.10058280825614929,
        "laya_0_3_20_applied_choice_11_plus_temperature": 0.5,
        "endpoint_loaded_exact_directory_attested": False,
        "live_reference_inference": False,
    }


def reference_run():
    fixture_sha = hashlib.sha256(FIXTURE_RAW).hexdigest()
    diagnostic_sha = hashlib.sha256(DIAGNOSTIC_RAW).hexdigest()
    verification = reference_verification()
    diag = record(
        DIAGNOSTIC["cases"][0],
        mod.REFERENCE_RESPONSE_MODEL,
        reference=True,
        diagnostic=True,
        input_tokens=mod.CHOICE11_TOKEN_COUNT,
    )
    diag["diagnostic_contract"] = {
        "option_count": 12,
        "temperature_bucket": "choice:11+",
        "reference_applied_temperature": 0.5,
        "expected_answer": None,
        "quality_claim": False,
    }
    return {
        "schema": mod.REFERENCE_RUN_SCHEMA,
        "status": "complete",
        "run_id": "ref",
        "source": {"git_sha": SOURCE_SHA},
        "provider": {
            "name": "laya",
            "managed_endpoint": True,
            "runtime_source_revision": mod.REFERENCE_LAYA_SOURCE_REVISION,
            "runtime_wheel": {
                "sha256": mod.REFERENCE_LAYA_WHEEL_SHA256,
                "bytes": mod.REFERENCE_LAYA_WHEEL_BYTES,
            },
            "runtime_dependencies": {},
        },
        "runtime_identity": {
            "laya_version": mod.REFERENCE_LAYA_VERSION,
            "imported_from_extracted_wheel": True,
            "loaded": [mod.REFERENCE_LOGICAL_MODEL],
            "model_binding_local_directory": True,
            "device": "cpu",
            "offline": {
                "HF_HUB_OFFLINE": "1",
                "TRANSFORMERS_OFFLINE": "1",
            },
        },
        "checkpoint": {
            "repository": mod.REFERENCE_REPOSITORY,
            "revision": mod.REFERENCE_REVISION,
            "attestation_schema": mod.REFERENCE_MODEL_ATTESTATION_SCHEMA,
            "verification_immediately_before_launch": copy.deepcopy(verification),
            "verification_after_health_before_inference": copy.deepcopy(verification),
            "verification_after_inference": copy.deepcopy(verification),
        },
        "fixture": {"sha256": fixture_sha, "case_count": 4},
        "choice11_diagnostic": {
            "sha256": diagnostic_sha,
            "case_count": 1,
            "option_count": 12,
        },
        "frozen_cases": [
            record(c, mod.REFERENCE_RESPONSE_MODEL, reference=True)
            for c in FIXTURE["cases"]
        ],
        "diagnostic_cases": [diag],
        "scope": {
            "reference_runtime_wheel_bytes_verified": True,
            "reference_runtime_imported_from_verified_wheel": True,
            "reference_model_directory_verified": True,
            "endpoint_loaded_exact_directory_attested": True,
            "endpoint_exact_runtime_wheel_attested": True,
            "reference_live_inference": True,
            "frozen_protocol_contract": True,
            "frozen_live_token_count_matches_reference": True,
            "choice11_reference_path_exercised": True,
            "numeric_parity_with_papaya": False,
            "task_quality": False,
            "calibration_validity": False,
            "jev_provider_identity": False,
        },
    }


def papaya_run():
    fixture_sha = hashlib.sha256(FIXTURE_RAW).hexdigest()
    diagnostic_sha = hashlib.sha256(DIAGNOSTIC_RAW).hexdigest()
    diag = record(
        DIAGNOSTIC["cases"][0],
        mod.PAPAYA_RESPONSE_MODEL,
        reference=False,
        diagnostic=True,
        input_tokens=mod.CHOICE11_TOKEN_COUNT,
    )
    diag["diagnostic_contract"] = {
        "question_id": mod.CHOICE11_QUESTION_ID,
        "question_type": "choice",
        "option_count": 12,
        "temperature_bucket": "choice:11+",
        "compat_temperature": 0.5,
        "expected_answer": None,
        "quality_claim": False,
    }
    return {
        "schema": mod.PAPAYA_RUN_SCHEMA,
        "status": "complete",
        "run_id": "pap",
        "source": {"git_sha": SOURCE_SHA},
        "provider": {
            "name": "papaya",
            "identity": mod.PAPAYA_RESPONSE_MODEL,
            "jev_provider_identity": False,
            "python_laya_reference_identity": False,
        },
        "papaya_runtime": {
            "repository": mod.PAPAYA_SOURCE_REPOSITORY,
            "revision": mod.PAPAYA_SOURCE_REVISION,
            "import_binding": {"source_checkout_imported": True},
        },
        "llama_runtime": {
            "sha256": mod.PAPAYA_LLAMA_SERVER_SHA256,
            "version_verified": True,
        },
        "fixture": {"sha256": fixture_sha, "case_count": 4},
        "choice11_diagnostic": {
            "sha256": diagnostic_sha,
            "case_count": 1,
            "option_count": 12,
        },
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
        "overlay": {
            "verification_before_launch": {"valid": True},
            "verification_after_health_before_inference": {"valid": True},
            "receipt": {
                "temperature_policy": {
                    "changes": [copy.deepcopy(mod.EXPECTED_CLAMP_CHANGE)],
                    "compat_config_sha256": mod.PAPAYA_COMPAT_CONFIG_SHA256,
                }
            },
        },
        "frozen_cases": [
            record(c, mod.PAPAYA_RESPONSE_MODEL, reference=False)
            for c in FIXTURE["cases"]
        ],
        "diagnostic_cases": [diag],
    }


def compare(reference=None, papaya=None):
    return mod.compare_runs(
        copy.deepcopy(FIXTURE),
        FIXTURE_RAW,
        reference or reference_run(),
        papaya or papaya_run(),
        copy.deepcopy(DIAGNOSTIC),
        DIAGNOSTIC_RAW,
        copy.deepcopy(CHOICE11),
    )


class NumericComparatorTest(unittest.TestCase):
    def test_identical_managed_outputs_measure_zero_without_parity_decision(self):
        report = compare()
        self.assertEqual(report["aggregate"]["max_probability_abs_delta"], 0.0)
        self.assertEqual(report["aggregate"]["max_score_or_noul_abs_delta"], 0.0)
        self.assertTrue(report["aggregate"]["includes_choice11_diagnostic"])
        self.assertEqual(report["aggregate"]["choice_selected_equal_count"], 3)
        self.assertEqual(report["aggregate"]["choice_selected_compared_count"], 3)
        self.assertEqual(report["aggregate"]["noul_threshold_0_5_equal_count"], 1)
        self.assertEqual(report["aggregate"]["noul_threshold_0_5_compared_count"], 1)
        self.assertEqual(
            report["aggregate"]["score_probability_argmax_equal_count"], 1
        )
        self.assertEqual(
            report["aggregate"]["score_probability_argmax_compared_count"], 1
        )
        self.assertNotIn("selected_output_equal_count", report["aggregate"])
        self.assertNotIn("selected_output_compared_count", report["aggregate"])
        self.assertFalse(report["scope"]["numeric_parity_threshold_defined"])
        self.assertFalse(report["scope"]["numeric_parity_decision"])
        self.assertFalse(report["inputs"]["provider_provenance_merged"])
        self.assertEqual(
            report["choice11_sequence_precondition"]["token_count"],
            mod.CHOICE11_TOKEN_COUNT,
        )

    def test_old_attach_reference_schema_is_rejected(self):
        ref = reference_run()
        ref["schema"] = "sei.local-typed-comparator-run/v1alpha1"
        with self.assertRaises(mod.NumericComparisonError):
            compare(reference=ref)

    def test_managed_reference_scope_missing_is_rejected(self):
        ref = reference_run()
        ref["scope"]["endpoint_exact_runtime_wheel_attested"] = False
        with self.assertRaises(mod.NumericComparisonError):
            compare(reference=ref)

    def test_managed_reference_cpu_offline_binding_is_required(self):
        ref = reference_run()
        ref["runtime_identity"]["device"] = "cuda"
        with self.assertRaises(mod.NumericComparisonError):
            compare(reference=ref)

        ref = reference_run()
        ref["runtime_identity"]["offline"]["HF_HUB_OFFLINE"] = "0"
        with self.assertRaises(mod.NumericComparisonError):
            compare(reference=ref)

    def test_reference_attestation_schema_drift_is_rejected(self):
        ref = reference_run()
        ref["checkpoint"]["attestation_schema"] = "wrong"
        with self.assertRaises(mod.NumericComparisonError):
            compare(reference=ref)

    def test_source_git_sha_must_match(self):
        pap = papaya_run()
        pap["source"]["git_sha"] = "2" * 40
        with self.assertRaises(mod.NumericComparisonError):
            compare(papaya=pap)

    def test_choice_option_order_drift_is_rejected(self):
        pap = papaya_run()
        row = pap["frozen_cases"][0]
        request = json.loads(row["request_utf8"])
        criteria = request["questions"]["route"]["criteria"]
        request["questions"]["route"]["criteria"] = {
            key: criteria[key] for key in reversed(list(criteria))
        }
        raw = compact(request)
        row["request_utf8"] = raw
        row["request_sha256"] = hashlib.sha256(raw.encode()).hexdigest()
        with self.assertRaises(mod.NumericComparisonError):
            compare(papaya=pap)

    def test_papaya_runtime_provenance_drift_is_rejected(self):
        pap = papaya_run()
        pap["llama_runtime"]["sha256"] = "0" * 64
        with self.assertRaises(mod.NumericComparisonError):
            compare(papaya=pap)

    def test_choice11_live_token_count_must_match_attestation(self):
        pap = papaya_run()
        row = pap["diagnostic_cases"][0]
        response = json.loads(row["response_utf8"])
        response["usage"]["input_tokens"] = 154
        raw = compact(response)
        row["response_utf8"] = raw
        row["response_sha256"] = hashlib.sha256(raw.encode()).hexdigest()
        with self.assertRaises(mod.NumericComparisonError):
            compare(papaya=pap)

    def test_choice11_probability_delta_is_measured(self):
        pap = papaya_run()
        row = pap["diagnostic_cases"][0]
        response = json.loads(row["response_utf8"])
        probs = response["answers"][mod.CHOICE11_QUESTION_ID]["probabilities"]
        keys = list(probs)
        probs[keys[0]] += 0.05
        probs[keys[1]] -= 0.05
        raw = compact(response)
        row["response_utf8"] = raw
        row["response_sha256"] = hashlib.sha256(raw.encode()).hexdigest()
        report = compare(papaya=pap)
        self.assertAlmostEqual(
            report["choice11_diagnostic"]["questions"][0]["probabilities"][
                "total_variation_distance"
            ],
            0.05,
        )
        self.assertFalse(report["scope"]["numeric_parity_decision"])

    def test_noul_threshold_agreement_is_separate_from_scalar_delta(self):
        pap = papaya_run()
        row = next(
            item
            for item in pap["frozen_cases"]
            if item["case_id"] == "noul-review"
        )
        response = json.loads(row["response_utf8"])
        response["answers"]["needs_review"]["noul"] = 0.6
        raw = compact(response)
        row["response_utf8"] = raw
        row["response_sha256"] = hashlib.sha256(raw.encode()).hexdigest()
        report = compare(papaya=pap)
        self.assertEqual(
            report["aggregate"]["noul_threshold_0_5_equal_count"], 0
        )
        self.assertEqual(
            report["aggregate"]["noul_threshold_0_5_compared_count"], 1
        )
        self.assertTrue(report["scope"]["numeric_difference_observed"])

    def test_choice11_attestation_overclaim_is_rejected(self):
        packet = copy.deepcopy(CHOICE11)
        packet["scope"]["numeric_model_parity"] = True
        with self.assertRaises(mod.NumericComparisonError):
            mod.compare_runs(
                copy.deepcopy(FIXTURE),
                FIXTURE_RAW,
                reference_run(),
                papaya_run(),
                copy.deepcopy(DIAGNOSTIC),
                DIAGNOSTIC_RAW,
                packet,
            )

    def test_response_probability_order_drift_is_rejected(self):
        pap = papaya_run()
        row = pap["frozen_cases"][0]
        response = json.loads(row["response_utf8"])
        probs = response["answers"]["route"]["probabilities"]
        response["answers"]["route"]["probabilities"] = {
            key: probs[key] for key in reversed(list(probs))
        }
        raw = compact(response)
        row["response_utf8"] = raw
        row["response_sha256"] = hashlib.sha256(raw.encode()).hexdigest()
        with self.assertRaises(mod.NumericComparisonError):
            compare(papaya=pap)


if __name__ == "__main__":
    unittest.main()
