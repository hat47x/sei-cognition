import importlib.util
import json
import os
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "capture_papaya_l0", HERE / "capture_papaya_l0.py"
)
capture = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = capture
SPEC.loader.exec_module(capture)

PROTOCOL_SPEC = importlib.util.spec_from_file_location(
    "protocol_contract_for_papaya_test", HERE / "protocol_contract.py"
)
protocol = importlib.util.module_from_spec(PROTOCOL_SPEC)
PROTOCOL_SPEC.loader.exec_module(protocol)


class PapayaCaptureTest(unittest.TestCase):
    def test_git_blob_sha1_matches_known_git_identity(self):
        self.assertEqual(
            capture.git_blob_sha1_bytes(b"hello\n"),
            "ce013625030ba8dba906f756967f9e9ca394464a",
        )

    def test_loopback_endpoint_is_fail_closed(self):
        self.assertEqual(
            capture.require_loopback_endpoint(
                "http://127.0.0.1:8080/v1/systemone"
            ),
            "http://127.0.0.1:8080/v1/systemone",
        )
        for bad in (
            "https://127.0.0.1:8080/v1/systemone",
            "http://example.com:8080/v1/systemone",
            "http://127.0.0.1:8080/other",
            "http://user:pass@127.0.0.1:8080/v1/systemone",
            "http://127.0.0.1:8080/v1/systemone?x=1",
        ):
            with self.subTest(endpoint=bad), self.assertRaises(
                capture.PapayaCaptureError
            ):
                capture.require_loopback_endpoint(bad)

    def test_child_environment_forces_offline_source_import(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "src").mkdir()
            previous_key = os.environ.get("PAPAYA_API_KEY")
            os.environ["PAPAYA_API_KEY"] = "must-not-propagate"
            try:
                env = capture.child_environment(root)
            finally:
                if previous_key is None:
                    os.environ.pop("PAPAYA_API_KEY", None)
                else:
                    os.environ["PAPAYA_API_KEY"] = previous_key
            self.assertEqual(env["HF_HUB_OFFLINE"], "1")
            self.assertEqual(env["TRANSFORMERS_OFFLINE"], "1")
            self.assertNotIn("PAPAYA_API_KEY", env)
            self.assertEqual(
                env["PYTHONPATH"].split(os.pathsep)[0],
                str((root / "src").resolve()),
            )

    def test_runtime_dependency_versions_are_retained_and_required(self):
        versions = {
            "numpy": "2.1.0",
            "torch": "2.5.0",
            "transformers": "4.50.0",
            "safetensors": "0.5.0",
            "huggingface-hub": "0.30.0",
        }
        with mock.patch.object(
            capture,
            "package_version",
            side_effect=lambda name: versions.get(name),
        ):
            observed = capture.require_runtime_dependencies()
        self.assertEqual(observed["numpy"], "2.1.0")
        self.assertEqual(observed["huggingface_hub"], "0.30.0")

        with mock.patch.object(
            capture,
            "package_version",
            side_effect=lambda name: None if name == "torch" else "1.0",
        ):
            with self.assertRaises(capture.PapayaCaptureError):
                capture.require_runtime_dependencies()

    def test_log_capture_sanitizes_known_local_paths_but_hashes_raw_log(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "runtime.log"
            path.write_text(
                "loading /private/work/papaya/model from /private/work/papaya\n",
                encoding="utf-8",
            )
            raw_digest, raw_size = capture.sha256_file(path)
            retained = capture.capture_log(
                path, {"/private/work/papaya": "<papaya-source>"}
            )
            self.assertEqual(retained["sha256"], raw_digest)
            self.assertEqual(retained["size_bytes"], raw_size)
            self.assertNotIn(
                "/private/work/papaya", retained["utf8_prefix_sanitized"]
            )
            self.assertIn(
                "<papaya-source>/model", retained["utf8_prefix_sanitized"]
            )

    def test_retained_choice11_diagnostic_is_exact_12_option_probe(self):
        diagnostic = json.loads(
            (HERE / "papaya_choice11_diagnostic.v1.json").read_text(
                encoding="utf-8"
            )
        )
        capture.validate_choice11_diagnostic(diagnostic, protocol)
        question = diagnostic["cases"][0]["request"]["questions"]["choice12"]
        self.assertEqual(len(question["criteria"]), 12)

    def _fixture(self):
        return {
            "schema": "sei.local-typed-comparator-fixture/v1alpha1",
            "cases": [
                {
                    "case_id": "simple-choice",
                    "request": {
                        "state": {"x": 1},
                        "questions": {
                            "route": {
                                "type": "choice",
                                "instructions": "Choose one route.",
                                "criteria": {
                                    "a": "Route A",
                                    "b": "Route B",
                                },
                            }
                        },
                    },
                }
            ],
        }

    def _transport(self, *, input_tokens=9, model=None):
        response_model = model or capture.PAPAYA_RESPONSE_MODEL

        def transport(_url, method, body=None, timeout=180.0):
            self.assertEqual(method, "POST")
            self.assertIsNotNone(body)
            response = {
                "model": response_model,
                "answers": {
                    "route": {
                        "type": "choice",
                        "choice": "a",
                        "probabilities": {"a": 0.6, "b": 0.4},
                        "confidence": 0.1,
                    }
                },
                "usage": {
                    "input_tokens": input_tokens,
                    "output_tokens": 0,
                },
            }
            raw = json.dumps(response, separators=(",", ":")).encode()
            return 200, {}, raw, 12.5

        return transport

    def test_frozen_capture_binds_live_token_count_to_replay(self):
        fixture = self._fixture()
        protocol.validate_fixture(fixture)
        records = capture.capture_fixture_cases(
            fixture,
            "http://127.0.0.1:8080/v1/systemone",
            protocol,
            expected_token_counts={"simple-choice": 9},
            transport=self._transport(input_tokens=9),
        )
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["input_tokens"], 9)
        self.assertTrue(records[0]["live_token_count_matches_replay"])
        self.assertEqual(
            records[0]["response_model"], capture.PAPAYA_RESPONSE_MODEL
        )

    def test_live_token_count_drift_is_rejected(self):
        fixture = self._fixture()
        with self.assertRaises(capture.PapayaCaptureError):
            capture.capture_fixture_cases(
                fixture,
                "http://127.0.0.1:8080/v1/systemone",
                protocol,
                expected_token_counts={"simple-choice": 9},
                transport=self._transport(input_tokens=10),
            )

    def test_response_model_alias_drift_is_rejected(self):
        fixture = self._fixture()
        with self.assertRaises(capture.PapayaCaptureError):
            capture.capture_fixture_cases(
                fixture,
                "http://127.0.0.1:8080/v1/systemone",
                protocol,
                expected_token_counts={"simple-choice": 9},
                transport=self._transport(
                    input_tokens=9, model="laya-rl-agent"
                ),
            )

    def test_diagnostic_capture_retains_no_quality_claim(self):
        diagnostic = json.loads(
            (HERE / "papaya_choice11_diagnostic.v1.json").read_text(
                encoding="utf-8"
            )
        )
        probabilities = {
            f"option_{i:02d}": round(1.0 / 12.0, 4) for i in range(12)
        }
        # Correct rounding residue so the provider-neutral validator sees 1.0.
        probabilities["option_11"] = round(
            1.0 - sum(probabilities[f"option_{i:02d}"] for i in range(11)),
            4,
        )

        def transport(_url, _method, _body=None, timeout=180.0):
            response = {
                "model": capture.PAPAYA_RESPONSE_MODEL,
                "answers": {
                    "choice12": {
                        "type": "choice",
                        "choice": "option_00",
                        "probabilities": probabilities,
                        "confidence": 0.0,
                    }
                },
                "usage": {"input_tokens": 100, "output_tokens": 0},
            }
            return (
                200,
                {},
                json.dumps(response, separators=(",", ":")).encode(),
                5.0,
            )

        records = capture.capture_fixture_cases(
            diagnostic,
            "http://127.0.0.1:8080/v1/systemone",
            protocol,
            diagnostic=True,
            transport=transport,
        )
        contract = records[0]["diagnostic_contract"]
        self.assertEqual(contract["option_count"], 12)
        self.assertEqual(contract["temperature_bucket"], "choice:11+")
        self.assertEqual(contract["compat_temperature"], 0.5)
        self.assertIsNone(contract["expected_answer"])
        self.assertFalse(contract["quality_claim"])


if __name__ == "__main__":
    unittest.main()
