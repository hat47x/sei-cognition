import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


INTEGRATION_DIR = Path(__file__).resolve().parent
ENTRYPOINT_PATH = INTEGRATION_DIR / "run_runtime_version_exchange_strict.py"
SPEC = importlib.util.spec_from_file_location("run_runtime_version_exchange_strict", ENTRYPOINT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load strict entrypoint: {ENTRYPOINT_PATH}")
ENTRYPOINT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ENTRYPOINT)


class StrictRuntimeVersionExchangeTest(unittest.TestCase):
    def test_rejects_forwarded_identity_options(self):
        for option in (
            "--kj-atlas-dir",
            "--kj-atlas-backend-bundle=/tmp/source",
            "--model-dir",
            "--evidence-dir=/tmp/evidence",
        ):
            with self.subTest(option=option):
                with self.assertRaisesRegex(ValueError, "identity option"):
                    ENTRYPOINT._reject_forwarded_identity_options([option])

    def test_prepositioned_model_store_is_verified_before_harness(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bundle = root / "bundle"
            model = root / "model"
            evidence = root / "evidence"
            bundle.mkdir()
            model.mkdir()
            calls = []

            def fake_model_store(path):
                calls.append(("model", path))
                return {"verified": True, "manifestSha256": "a" * 64}

            def fake_source(path):
                calls.append(("source", path))
                return {"verified": True}

            class Completed:
                returncode = 0

            def fake_run(command, check):
                calls.append(("run", command, check))
                evidence.mkdir()
                return Completed()

            with patch.object(ENTRYPOINT, "verify_model_store", side_effect=fake_model_store), patch.object(
                ENTRYPOINT,
                "verify_runtime_bundle",
                side_effect=fake_source,
            ), patch.object(ENTRYPOINT.subprocess, "run", side_effect=fake_run):
                result = ENTRYPOINT.run_strict_probe(
                    checkout_dir=None,
                    backend_bundle=bundle,
                    model_dir=model,
                    evidence_dir=evidence,
                    harness_arguments=["--keep-work"],
                )

            self.assertEqual(0, result)
            self.assertEqual("model", calls[0][0])
            self.assertEqual("source", calls[1][0])
            self.assertEqual("run", calls[2][0])
            command = calls[2][1]
            self.assertEqual("bash", command[0])
            self.assertEqual(str(ENTRYPOINT.HARNESS), command[1])
            self.assertIn("--kj-atlas-backend-bundle", command)
            self.assertIn("--model-dir", command)
            self.assertIn("--evidence-dir", command)
            self.assertIn("--keep-work", command)

            payload = json.loads(
                (evidence / "runtime-exchange-model-store-static-verification.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertTrue(payload["verified"])

    def test_invalid_model_store_stops_before_harness(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bundle = root / "bundle"
            model = root / "model"
            evidence = root / "evidence"
            bundle.mkdir()
            model.mkdir()

            with patch.object(
                ENTRYPOINT,
                "verify_model_store",
                side_effect=ValueError("model manifest mismatch"),
            ), patch.object(ENTRYPOINT, "verify_runtime_bundle") as source_verifier, patch.object(
                ENTRYPOINT.subprocess,
                "run",
            ) as runner:
                with self.assertRaisesRegex(ValueError, "model manifest mismatch"):
                    ENTRYPOINT.run_strict_probe(
                        checkout_dir=None,
                        backend_bundle=bundle,
                        model_dir=model,
                        evidence_dir=evidence,
                        harness_arguments=[],
                    )

                source_verifier.assert_not_called()
                runner.assert_not_called()
                self.assertFalse(evidence.exists())

    def test_checkout_is_exported_from_fixed_commit_before_harness(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            checkout = root / "checkout"
            checkout.mkdir()
            evidence = root / "evidence"
            calls = []

            def fake_export(checkout_dir, output_dir):
                calls.append(("export", checkout_dir, output_dir))
                output_dir.mkdir(parents=True)
                return {
                    "schema": "soza.kj-atlas-runtime-source-export/v1",
                    "sourceAcquisition": "git-archive-from-pinned-commit",
                }

            class Completed:
                returncode = 1

            def fake_run(command, check):
                calls.append(("run", command, check))
                evidence.mkdir()
                return Completed()

            with patch.object(ENTRYPOINT, "export_runtime_bundle", side_effect=fake_export), patch.object(
                ENTRYPOINT.subprocess,
                "run",
                side_effect=fake_run,
            ):
                result = ENTRYPOINT.run_strict_probe(
                    checkout_dir=checkout,
                    backend_bundle=None,
                    model_dir=None,
                    evidence_dir=evidence,
                    harness_arguments=[],
                )

            self.assertEqual(1, result)
            self.assertEqual("export", calls[0][0])
            self.assertEqual("run", calls[1][0])
            source_payload = json.loads(
                (evidence / "runtime-exchange-source-export.json").read_text(encoding="utf-8")
            )
            self.assertEqual("git-archive-from-pinned-commit", source_payload["sourceAcquisition"])

    def test_existing_evidence_directory_is_rejected_before_verification(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bundle = root / "bundle"
            evidence = root / "evidence"
            bundle.mkdir()
            evidence.mkdir()

            with patch.object(ENTRYPOINT, "verify_runtime_bundle") as source_verifier, patch.object(
                ENTRYPOINT.subprocess,
                "run",
            ) as runner:
                with self.assertRaisesRegex(ValueError, "新しいpath"):
                    ENTRYPOINT.run_strict_probe(
                        checkout_dir=None,
                        backend_bundle=bundle,
                        model_dir=None,
                        evidence_dir=evidence,
                        harness_arguments=[],
                    )
                source_verifier.assert_not_called()
                runner.assert_not_called()


if __name__ == "__main__":
    unittest.main()
