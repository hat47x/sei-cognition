import importlib.util
import json
import os
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
            "--work-dir=/tmp/work",
        ):
            with self.subTest(option=option):
                with self.assertRaisesRegex(ValueError, "identity / safety option"):
                    ENTRYPOINT._reject_forwarded_identity_options([option])

    def test_forwarded_runtime_archive_options_support_split_and_equals_forms(self):
        selected = ENTRYPOINT._forwarded_runtime_archives(
            [
                "--runtime-a-archive",
                "/tmp/a.tar.zst",
                "--keep-work",
                "--runtime-b-archive=/tmp/b.tar.zst",
            ]
        )
        self.assertEqual(Path("/tmp/a.tar.zst"), selected["--runtime-a-archive"])
        self.assertEqual(Path("/tmp/b.tar.zst"), selected["--runtime-b-archive"])

    def test_duplicate_runtime_archive_option_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "重複指定"):
            ENTRYPOINT._forwarded_runtime_archives(
                [
                    "--runtime-a-archive=/tmp/a.tar.zst",
                    "--runtime-a-archive",
                    "/tmp/b.tar.zst",
                ]
            )

    def test_strict_child_environment_removes_identity_and_safety_overrides(self):
        injected = {
            key: f"unexpected-{index}"
            for index, key in enumerate(ENTRYPOINT.STRICT_CHILD_ENVIRONMENT_KEYS)
        }
        with patch.dict(os.environ, injected, clear=False):
            environment = ENTRYPOINT._strict_child_environment()
        for key in ENTRYPOINT.STRICT_CHILD_ENVIRONMENT_KEYS:
            self.assertNotIn(key, environment)

    def test_strict_child_environment_isolates_python_git_and_temp_from_parent(self):
        with tempfile.TemporaryDirectory() as temporary:
            work = Path(temporary) / "work"
            parent = {
                "PATH": "/usr/bin",
                "HOME": "/home/example",
                "VIRTUAL_ENV": "/tmp/venv",
                "UNRELATED": "keep",
                "PYTHONPATH": "/tmp/injected-pythonpath",
                "PYTHONHOME": "/tmp/injected-pythonhome",
                "PYTHONSTARTUP": "/tmp/startup.py",
                "PYTHONUSERBASE": "/tmp/userbase",
                "TMPDIR": "/tmp/injected-tmpdir",
                "TMP": "/tmp/injected-tmp",
                "TEMP": "/tmp/injected-temp",
                "GIT_DIR": "/tmp/other.git",
                "GIT_WORK_TREE": "/tmp/other-work-tree",
                "GIT_COMMON_DIR": "/tmp/other-common",
                "GIT_INDEX_FILE": "/tmp/other-index",
                "PYTHONDONTWRITEBYTECODE": "0",
                "PYTHONNOUSERSITE": "0",
            }
            with patch.dict(os.environ, parent, clear=True):
                environment = ENTRYPOINT._strict_child_environment(work)

        self.assertEqual("/usr/bin", environment["PATH"])
        self.assertEqual("/home/example", environment["HOME"])
        self.assertEqual("/tmp/venv", environment["VIRTUAL_ENV"])
        self.assertEqual("keep", environment["UNRELATED"])
        for key in ENTRYPOINT.STRICT_CHILD_PYTHON_ENVIRONMENT_KEYS:
            self.assertNotIn(key, environment)
        self.assertFalse(any(key.startswith("GIT_") for key in environment))
        for key in ENTRYPOINT.STRICT_CHILD_TEMP_ENVIRONMENT_KEYS:
            self.assertEqual(str(work), environment[key])
        self.assertEqual("1", environment["PYTHONDONTWRITEBYTECODE"])
        self.assertEqual("1", environment["PYTHONNOUSERSITE"])

    def test_runtime_archive_inside_source_is_rejected_before_verification(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bundle = root / "bundle"
            bundle.mkdir()
            archive = bundle / "runtime-a.tar.zst"
            archive.write_bytes(b"runtime")
            evidence = root / "evidence"

            with patch.object(ENTRYPOINT, "verify_runtime_bundle") as source_verifier, patch.object(
                ENTRYPOINT.subprocess, "run"
            ) as runner:
                with self.assertRaisesRegex(ValueError, "runtime archive.*KJ Atlas verified runtime bundle"):
                    ENTRYPOINT.run_strict_probe(
                        checkout_dir=None,
                        backend_bundle=bundle,
                        model_dir=None,
                        evidence_dir=evidence,
                        harness_arguments=["--runtime-a-archive", str(archive)],
                    )
            source_verifier.assert_not_called()
            runner.assert_not_called()

    def test_runtime_archive_symlink_is_rejected_before_verification(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bundle = root / "bundle"
            bundle.mkdir()
            actual = root / "actual.tar.zst"
            actual.write_bytes(b"runtime")
            archive = root / "runtime-a.tar.zst"
            archive.symlink_to(actual)
            evidence = root / "evidence"

            with patch.object(ENTRYPOINT, "verify_runtime_bundle") as source_verifier, patch.object(
                ENTRYPOINT.subprocess, "run"
            ) as runner:
                with self.assertRaisesRegex(ValueError, "symlink"):
                    ENTRYPOINT.run_strict_probe(
                        checkout_dir=None,
                        backend_bundle=bundle,
                        model_dir=None,
                        evidence_dir=evidence,
                        harness_arguments=["--runtime-a-archive", str(archive)],
                    )
            source_verifier.assert_not_called()
            runner.assert_not_called()

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

            def fake_run(command, check, env=None):
                calls.append(("run", command, check, env))
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
            child_env = calls[2][3]
            self.assertEqual("bash", command[0])
            self.assertEqual(str(ENTRYPOINT.HARNESS), command[1])
            self.assertIn("--kj-atlas-backend-bundle", command)
            self.assertIn("--model-dir", command)
            self.assertIn("--evidence-dir", command)
            self.assertIn("--keep-work", command)
            for key in ENTRYPOINT.STRICT_CHILD_ENVIRONMENT_KEYS:
                self.assertNotIn(key, child_env)
            for key in ENTRYPOINT.STRICT_CHILD_PYTHON_ENVIRONMENT_KEYS:
                self.assertNotIn(key, child_env)
            self.assertFalse(any(key.startswith("GIT_") for key in child_env))
            self.assertEqual("1", child_env["PYTHONDONTWRITEBYTECODE"])
            self.assertEqual("1", child_env["PYTHONNOUSERSITE"])

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
                    "schema": "sei.kj-atlas-runtime-source-export/v1",
                    "sourceAcquisition": "git-archive-from-pinned-commit",
                }

            class Completed:
                returncode = 1

            def fake_run(command, check, env=None):
                calls.append(("run", command, check, env))
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

    def test_model_store_inside_checkout_is_rejected_before_verification(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            checkout = root / "checkout"
            model = checkout / "models"
            evidence = root / "evidence"
            model.mkdir(parents=True)

            with patch.object(ENTRYPOINT, "verify_model_store") as model_verifier, patch.object(
                ENTRYPOINT,
                "export_runtime_bundle",
            ) as exporter, patch.object(ENTRYPOINT.subprocess, "run") as runner:
                with self.assertRaisesRegex(ValueError, "model directory.*KJ Atlas checkout"):
                    ENTRYPOINT.run_strict_probe(
                        checkout_dir=checkout,
                        backend_bundle=None,
                        model_dir=model,
                        evidence_dir=evidence,
                        harness_arguments=[],
                    )

            model_verifier.assert_not_called()
            exporter.assert_not_called()
            runner.assert_not_called()

    def test_evidence_inside_checkout_is_rejected_before_export(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            checkout = root / "checkout"
            checkout.mkdir()
            evidence = checkout / "evidence"

            with patch.object(ENTRYPOINT, "export_runtime_bundle") as exporter, patch.object(
                ENTRYPOINT.subprocess,
                "run",
            ) as runner:
                with self.assertRaisesRegex(ValueError, "Evidence directory.*KJ Atlas checkout"):
                    ENTRYPOINT.run_strict_probe(
                        checkout_dir=checkout,
                        backend_bundle=None,
                        model_dir=None,
                        evidence_dir=evidence,
                        harness_arguments=[],
                    )

            exporter.assert_not_called()
            runner.assert_not_called()

    def test_evidence_inside_model_store_is_rejected_without_mutating_store(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bundle = root / "bundle"
            model = root / "model"
            evidence = model / "evidence"
            bundle.mkdir()
            model.mkdir()

            with patch.object(ENTRYPOINT, "verify_model_store") as model_verifier, patch.object(
                ENTRYPOINT,
                "verify_runtime_bundle",
            ) as source_verifier, patch.object(ENTRYPOINT.subprocess, "run") as runner:
                with self.assertRaisesRegex(ValueError, "Evidence directory.*model directory"):
                    ENTRYPOINT.run_strict_probe(
                        checkout_dir=None,
                        backend_bundle=bundle,
                        model_dir=model,
                        evidence_dir=evidence,
                        harness_arguments=[],
                    )

            model_verifier.assert_not_called()
            source_verifier.assert_not_called()
            runner.assert_not_called()
            self.assertFalse(evidence.exists())

    def test_safe_custom_work_directory_is_forwarded_by_strict_entrypoint(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bundle = root / "bundle"
            evidence = root / "evidence"
            work = root / "work"
            bundle.mkdir()

            class Completed:
                returncode = 0

            def fake_run(command, check, env=None):
                evidence.mkdir()
                return Completed()

            with patch.object(ENTRYPOINT, "verify_runtime_bundle"), patch.object(
                ENTRYPOINT.subprocess,
                "run",
                side_effect=fake_run,
            ) as runner:
                result = ENTRYPOINT.run_strict_probe(
                    checkout_dir=None,
                    backend_bundle=bundle,
                    model_dir=None,
                    evidence_dir=evidence,
                    harness_arguments=[],
                    work_dir=work,
                )

            self.assertEqual(0, result)
            command = runner.call_args.args[0]
            self.assertIn("--work-dir", command)
            self.assertEqual(str(work.resolve()), command[command.index("--work-dir") + 1])
            child_env = runner.call_args.kwargs["env"]
            for key in ENTRYPOINT.STRICT_CHILD_ENVIRONMENT_KEYS:
                self.assertNotIn(key, child_env)
            for key in ENTRYPOINT.STRICT_CHILD_TEMP_ENVIRONMENT_KEYS:
                self.assertEqual(str(work.resolve()), child_env[key])

    def test_work_directory_inside_checkout_is_rejected_before_export(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            checkout = root / "checkout"
            checkout.mkdir()
            evidence = root / "evidence"
            work = checkout / "work"

            with patch.object(ENTRYPOINT, "export_runtime_bundle") as exporter, patch.object(
                ENTRYPOINT.subprocess,
                "run",
            ) as runner:
                with self.assertRaisesRegex(ValueError, "Work directory.*KJ Atlas checkout"):
                    ENTRYPOINT.run_strict_probe(
                        checkout_dir=checkout,
                        backend_bundle=None,
                        model_dir=None,
                        evidence_dir=evidence,
                        harness_arguments=[],
                        work_dir=work,
                    )

            exporter.assert_not_called()
            runner.assert_not_called()


if __name__ == "__main__":
    unittest.main()
