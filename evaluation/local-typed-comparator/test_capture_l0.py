import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("capture_l0", HERE / "capture_l0.py")
cap = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(cap)


def fixture():
    return {
        "schema": "test",
        "cases": [
            {
                "case_id": "choice-order",
                "request": {
                    "state": {"x": 1},
                    "questions": {
                        "route": {
                            "type": "choice",
                            "instructions": "pick",
                            "criteria": {"b": "B", "a": "A"},
                        }
                    },
                },
            }
        ],
    }


def valid_response():
    return {
        "model": "laya-rl-agent",
        "answers": {
            "route": {
                "type": "choice",
                "choice": "b",
                "probabilities": {"b": 0.75, "a": 0.25},
                "confidence": 0.5,
            }
        },
        "usage": {"input_tokens": 3, "output_tokens": 0},
        "routing": {"model": "typed-decisions", "reason": "explicit model"},
    }


class CaptureTest(unittest.TestCase):
    def test_pinned_checkpoint_identity_is_single_lineage(self):
        self.assertEqual(
            cap.PINNED_MODEL_REPOSITORY,
            "convaiinnovations/laya-typed-decisions",
        )
        self.assertEqual(
            cap.PINNED_REQUEST_MODEL,
            "convaiinnovations/laya-typed-decisions",
        )
        self.assertEqual(cap.PINNED_LOGICAL_MODEL, "typed-decisions")
        self.assertEqual(cap.PINNED_RESPONSE_MODEL, "laya-rl-agent")
        self.assertEqual(
            cap.PINNED_HUB_REVISION,
            "f9ab0b228f0fc0f14d873dbc99038f135c2da1b2",
        )
        self.assertEqual(
            cap.PINNED_MODEL_SHA256,
            "4fa56de72383a9d3efa9cfa78955733c81b9fc8067a587ca4beb82c78107a24e",
        )

    def test_endpoint_is_loopback_only(self):
        self.assertEqual(
            cap.require_local_endpoint(cap.DEFAULT_ENDPOINT),
            cap.DEFAULT_ENDPOINT,
        )
        with self.assertRaises(cap.CaptureError):
            cap.require_local_endpoint("https://127.0.0.1:8000/v1/systemone")
        with self.assertRaises(cap.CaptureError):
            cap.require_local_endpoint("http://example.com:8000/v1/systemone")
        with self.assertRaises(cap.CaptureError):
            cap.require_local_endpoint("http://127.0.0.1:8000/predict")

    def test_request_serialization_preserves_choice_order(self):
        req = fixture()["cases"][0]["request"]
        raw = cap.serialize_request(req).decode("utf-8")
        self.assertLess(raw.index('"b":"B"'), raw.index('"a":"A"'))

    def test_capture_records_exact_request_response_and_latency(self):
        response_raw = json.dumps(
            valid_response(), separators=(",", ":")
        ).encode()
        seen = []

        def transport(url, method, body=None, api_key=None, timeout=120.0):
            seen.append((url, method, body, api_key))
            return (
                200,
                {"X-Inference-Time-Ms": "7.25"},
                response_raw,
                9.5,
            )

        def validator(request, response):
            self.assertEqual(
                list(request["questions"]["route"]["criteria"]),
                ["b", "a"],
            )
            self.assertEqual(
                response["answers"]["route"]["choice"],
                "b",
            )

        rows = cap.capture_cases(
            fixture(),
            cap.DEFAULT_ENDPOINT,
            cap.PINNED_REQUEST_MODEL,
            validator,
            transport,
        )
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["contract"], "pass")
        self.assertEqual(rows[0]["provider_inference_time_ms"], 7.25)
        self.assertEqual(
            rows[0]["response_sha256"],
            hashlib.sha256(response_raw).hexdigest(),
        )
        sent = json.loads(seen[0][2].decode())
        self.assertEqual(sent["model"], cap.PINNED_REQUEST_MODEL)

    def test_non_200_is_fail_closed_and_retains_partial_record(self):
        def transport(url, method, body=None, api_key=None, timeout=120.0):
            return 422, {}, b'{"detail":"bad"}', 1.0

        records = []
        with self.assertRaisesRegex(cap.CaptureError, "HTTP 422"):
            cap.capture_cases(
                fixture(),
                cap.DEFAULT_ENDPOINT,
                cap.PINNED_REQUEST_MODEL,
                lambda r, s: None,
                transport,
                records=records,
            )
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["http_status"], 422)
        self.assertEqual(records[0]["response_utf8"], '{"detail":"bad"}')

    def test_health_capture(self):
        raw = (
            b'{"status":"ok","loaded":["typed-decisions"],"device":"cpu"}'
        )

        def transport(url, method, body=None, api_key=None, timeout=120.0):
            return 200, {}, raw, 2.0

        result = cap.capture_health(cap.DEFAULT_ENDPOINT, transport)
        self.assertEqual(result["loaded"], ["typed-decisions"])
        self.assertEqual(result["device"], "cpu")

    def test_health_requires_pinned_logical_checkpoint(self):
        raw = b'{"status":"ok","loaded":["english"],"device":"cpu"}'

        def transport(url, method, body=None, api_key=None, timeout=120.0):
            return 200, {}, raw, 2.0

        with self.assertRaisesRegex(cap.CaptureError, "logical checkpoint"):
            cap.capture_health(cap.DEFAULT_ENDPOINT, transport)

    def test_capture_rejects_wrong_logical_route(self):
        response = valid_response()
        response["routing"]["model"] = "english"
        response_raw = json.dumps(response, separators=(",", ":")).encode()

        def transport(url, method, body=None, api_key=None, timeout=120.0):
            return 200, {}, response_raw, 1.0

        with self.assertRaisesRegex(cap.CaptureError, "routing through"):
            cap.capture_cases(
                fixture(),
                cap.DEFAULT_ENDPOINT,
                cap.PINNED_REQUEST_MODEL,
                lambda r, s: None,
                transport,
            )

    def test_capture_rejects_unexpected_response_model(self):
        response = valid_response()
        response["model"] = "other-runtime"
        response_raw = json.dumps(response, separators=(",", ":")).encode()

        def transport(url, method, body=None, api_key=None, timeout=120.0):
            return 200, {}, response_raw, 1.0

        with self.assertRaisesRegex(cap.CaptureError, "unexpected response model"):
            cap.capture_cases(
                fixture(),
                cap.DEFAULT_ENDPOINT,
                cap.PINNED_REQUEST_MODEL,
                lambda r, s: None,
                transport,
            )

    def test_pinned_artifact_rejects_wrong_hash(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "artifact"
            path.write_bytes(b"abc")
            with self.assertRaisesRegex(cap.CaptureError, "sha256 mismatch"):
                cap.require_pinned_artifact(
                    path,
                    "0" * 64,
                    3,
                    "artifact",
                )


if __name__ == "__main__":
    unittest.main()
