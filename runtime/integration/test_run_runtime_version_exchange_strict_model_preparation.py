import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


INTEGRATION_DIR = Path(__file__).resolve().parent
ENTRYPOINT_PATH = INTEGRATION_DIR / "run_runtime_version_exchange_strict.py"
SPEC = importlib.util.spec_from_file_location(
    "run_runtime_version_exchange_strict_model_preparation",
    ENTRYPOINT_PATH,
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load strict entrypoint: {ENTRYPOINT_PATH}")
ENTRYPOINT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ENTRYPOINT)


class StrictRuntimeVersionExchangeModelPreparationTest(unittest.TestCase):
    def test_prepare_model_option_cannot_be_forwarded_to_low_level_harness(self):
        for option in (
            "--prepare-model-dir",
            "--prepare-model-dir=/tmp/model",
        ):
            with self.subTest(option=option):
                with self.assertRaisesRegex(ValueError, "identity / safety option"):
                    ENTRYPOINT._reject_forwarded_identity_options([option])

    def test_model_is_prepared_after_source_verification_and_reverified_before_harness(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bundle = root / "bundle"
            model = root / "prepared-model"
            evidence = root / "evidence"
            bundle.mkdir()
            calls: list[tuple[str, object]] = []

            def fake_source(path):
                calls.append(("source", path))
                return {"verified": True}

            def fake_prepare(path):
                calls.append(("prepare", path))
                path.mkdir()
                return {
                    "prepared": True,
                    "target": str(path),
                    "manifestSha256": "a" * 64,
                }

            def fake_model(path):
                calls.append(("model", path))
                return {
                    "verified": True,
                    "modelStore": str(path),
                    "manifestSha256": "a" * 64,
                }

            class Completed:
                returncode = 0

            def fake_run(command, check, env=None):
                calls.append(("run", command, env))
                evidence.mkdir()
                return Completed()

            with patch.object(
                ENTRYPOINT,
                "verify_runtime_bundle",
                side_effect=fake_source,
            ), patch.object(
                ENTRYPOINT,
                "prepare_model_store",
                side_effect=fake_prepare,
            ), patch.object(
                ENTRYPOINT,
                "verify_model_store",
                side_effect=fake_model,
            ), patch.object(
                ENTRYPOINT.subprocess,
                "run",
                side_effect=fake_run,
            ):
                result = ENTRYPOINT.run_strict_probe(
                    checkout_dir=None,
                    backend_bundle=bundle,
                    model_dir=None,
                    prepare_model_dir=model,
                    evidence_dir=evidence,
                    harness_arguments=[],
                )

            self.assertEqual(0, result)
            self.assertEqual(
                ["source", "prepare", "model", "run"],
                [call[0] for call in calls],
            )
            command = calls[-1][1]
            self.assertIn("--model-dir", command)
            self.assertEqual(str(model.resolve()), command[command.index("--model-dir") + 1])
            child_env = calls[-1][2]
            self.assertIsNotNone(child_env)
            self.assertEqual("1", child_env["PYTHONNOUSERSITE"])

            preparation = json.loads(
                (evidence / "runtime-exchange-model-store-preparation.json").read_text(
                    encoding="utf-8"
                )
            )
            verification = json.loads(
                (evidence / "runtime-exchange-model-store-static-verification.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertTrue(preparation["prepared"])
            self.assertTrue(verification["verified"])

    def test_existing_prepare_target_is_rejected_before_source_or_network_work(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bundle = root / "bundle"
            model = root / "prepared-model"
            evidence = root / "evidence"
            bundle.mkdir()
            model.mkdir()

            with patch.object(ENTRYPOINT, "verify_runtime_bundle") as source_verifier, patch.object(
                ENTRYPOINT,
                "prepare_model_store",
            ) as preparer, patch.object(ENTRYPOINT.subprocess, "run") as runner:
                with self.assertRaisesRegex(ValueError, "Prepared model directory.*新しいpath"):
                    ENTRYPOINT.run_strict_probe(
                        checkout_dir=None,
                        backend_bundle=bundle,
                        model_dir=None,
                        prepare_model_dir=model,
                        evidence_dir=evidence,
                        harness_arguments=[],
                    )

            source_verifier.assert_not_called()
            preparer.assert_not_called()
            runner.assert_not_called()

    def test_prepare_target_overlapping_source_is_rejected_before_network_work(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bundle = root / "bundle"
            bundle.mkdir()
            model = bundle / "prepared-model"
            evidence = root / "evidence"

            with patch.object(ENTRYPOINT, "verify_runtime_bundle") as source_verifier, patch.object(
                ENTRYPOINT,
                "prepare_model_store",
            ) as preparer, patch.object(ENTRYPOINT.subprocess, "run") as runner:
                with self.assertRaisesRegex(ValueError, "model directory.*verified runtime bundle"):
                    ENTRYPOINT.run_strict_probe(
                        checkout_dir=None,
                        backend_bundle=bundle,
                        model_dir=None,
                        prepare_model_dir=model,
                        evidence_dir=evidence,
                        harness_arguments=[],
                    )

            source_verifier.assert_not_called()
            preparer.assert_not_called()
            runner.assert_not_called()

    def test_existing_and_prepared_model_inputs_are_mutually_exclusive(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bundle = root / "bundle"
            model = root / "model"
            bundle.mkdir()
            model.mkdir()

            with patch.object(ENTRYPOINT, "verify_model_store") as model_verifier, patch.object(
                ENTRYPOINT,
                "prepare_model_store",
            ) as preparer, patch.object(ENTRYPOINT.subprocess, "run") as runner:
                with self.assertRaisesRegex(ValueError, "同時に指定できません"):
                    ENTRYPOINT.run_strict_probe(
                        checkout_dir=None,
                        backend_bundle=bundle,
                        model_dir=model,
                        prepare_model_dir=root / "prepared-model",
                        evidence_dir=root / "evidence",
                        harness_arguments=[],
                    )

            model_verifier.assert_not_called()
            preparer.assert_not_called()
            runner.assert_not_called()

    def test_preparation_failure_stops_before_model_reverification_and_harness(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bundle = root / "bundle"
            model = root / "prepared-model"
            evidence = root / "evidence"
            bundle.mkdir()

            with patch.object(ENTRYPOINT, "verify_runtime_bundle"), patch.object(
                ENTRYPOINT,
                "prepare_model_store",
                side_effect=ValueError("fixed manifest mismatch"),
            ), patch.object(ENTRYPOINT, "verify_model_store") as model_verifier, patch.object(
                ENTRYPOINT.subprocess,
                "run",
            ) as runner:
                with self.assertRaisesRegex(ValueError, "fixed manifest mismatch"):
                    ENTRYPOINT.run_strict_probe(
                        checkout_dir=None,
                        backend_bundle=bundle,
                        model_dir=None,
                        prepare_model_dir=model,
                        evidence_dir=evidence,
                        harness_arguments=[],
                    )

            model_verifier.assert_not_called()
            runner.assert_not_called()
            self.assertFalse(evidence.exists())


if __name__ == "__main__":
    unittest.main()
