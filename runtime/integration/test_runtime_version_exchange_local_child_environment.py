import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import run_runtime_version_exchange_local_checks as local_checks
import run_runtime_version_exchange_with_verification as verified_runner


class RuntimeVersionExchangeLocalChildEnvironmentTest(unittest.TestCase):
    def test_parent_python_git_and_temp_environment_is_not_inherited(self):
        parent = {
            "PATH": "/usr/bin",
            "HOME": "/home/example",
            "UNRELATED": "keep",
            "SEI_RUNTIME_EXCHANGE_MODEL_DIR": "/tmp/model",
            "SEI_E3B_RUNTIME_EXCHANGE_LIVE": "1",
            "OLLAMA_HOST": "127.0.0.1:11434",
            "OLLAMA_MODELS": "/tmp/ollama-models",
            "PYTHONPATH": "/tmp/injected-pythonpath",
            "PYTHONHOME": "/tmp/injected-pythonhome",
            "PYTHONSTARTUP": "/tmp/startup.py",
            "PYTHONUSERBASE": "/tmp/python-user-base",
            "TMPDIR": "/tmp/injected-tmpdir",
            "TMP": "/tmp/injected-tmp",
            "TEMP": "/tmp/injected-temp",
            "GIT_DIR": "/tmp/injected-git-dir",
            "GIT_WORK_TREE": "/tmp/injected-work-tree",
            "GIT_COMMON_DIR": "/tmp/injected-common-dir",
            "GIT_INDEX_FILE": "/tmp/injected-index",
            "GIT_OBJECT_DIRECTORY": "/tmp/injected-objects",
            "PYTHONDONTWRITEBYTECODE": "0",
            "PYTHONNOUSERSITE": "0",
        }
        with patch.dict(os.environ, parent, clear=True):
            actual = local_checks.sanitized_environment()

        self.assertEqual("/usr/bin", actual["PATH"])
        self.assertEqual("/home/example", actual["HOME"])
        self.assertEqual("keep", actual["UNRELATED"])

        for key in (
            "SEI_RUNTIME_EXCHANGE_MODEL_DIR",
            "SEI_E3B_RUNTIME_EXCHANGE_LIVE",
            "OLLAMA_HOST",
            "OLLAMA_MODELS",
            "PYTHONPATH",
            "PYTHONHOME",
            "PYTHONSTARTUP",
            "PYTHONUSERBASE",
            "TMPDIR",
            "TMP",
            "TEMP",
        ):
            with self.subTest(key=key):
                self.assertNotIn(key, actual)

        self.assertFalse(any(key.startswith("GIT_") for key in actual))
        self.assertEqual("1", actual["PYTHONDONTWRITEBYTECODE"])
        self.assertEqual("1", actual["PYTHONNOUSERSITE"])

    def test_repository_observation_does_not_inherit_parent_git_internal_environment(self):
        parent = {
            "PATH": "/usr/bin",
            "UNRELATED": "keep",
            "GIT_DIR": "/tmp/other.git",
            "GIT_WORK_TREE": "/tmp/other-work-tree",
            "GIT_COMMON_DIR": "/tmp/other-common-dir",
            "GIT_INDEX_FILE": "/tmp/other-index",
            "GIT_OBJECT_DIRECTORY": "/tmp/other-objects",
        }
        completed = subprocess.CompletedProcess(
            args=["git"],
            returncode=0,
            stdout="a" * 40 + "\n",
            stderr="",
        )
        with patch.dict(os.environ, parent, clear=True), patch.object(
            local_checks.subprocess,
            "run",
            return_value=completed,
        ) as runner:
            observed, error = local_checks._run_git_observation("rev-parse", "HEAD")

        self.assertIsNone(error)
        self.assertIs(observed, completed)
        command = runner.call_args.args[0]
        self.assertEqual(["git", "-C", str(local_checks.SEI_ROOT)], command[:3])
        environment = runner.call_args.kwargs["env"]
        self.assertEqual("/usr/bin", environment["PATH"])
        self.assertEqual("keep", environment["UNRELATED"])
        self.assertFalse(any(key.startswith("GIT_") for key in environment))

    def test_verified_runner_child_environment_isolated_from_parent_python_git_and_temp(self):
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
            environment = verified_runner._verified_child_environment()

        self.assertEqual("/usr/bin", environment["PATH"])
        self.assertEqual("/home/example", environment["HOME"])
        self.assertEqual("/tmp/venv", environment["VIRTUAL_ENV"])
        self.assertEqual("keep", environment["UNRELATED"])
        for key in verified_runner.VERIFIED_CHILD_PYTHON_ENVIRONMENT_KEYS:
            self.assertNotIn(key, environment)
        for key in verified_runner.VERIFIED_CHILD_TEMP_ENVIRONMENT_KEYS:
            self.assertNotIn(key, environment)
        self.assertFalse(any(key.startswith("GIT_") for key in environment))
        self.assertEqual("1", environment["PYTHONDONTWRITEBYTECODE"])
        self.assertEqual("1", environment["PYTHONNOUSERSITE"])

    def test_verified_runner_default_work_is_evidence_sibling_and_ignores_parent_tmpdir(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            evidence = root / "evidence"
            with patch.dict(os.environ, {"TMPDIR": "/tmp/injected-parent"}, clear=False):
                default_work = verified_runner._effective_work_dir(evidence, None)
            explicit = verified_runner._effective_work_dir(evidence, root / "custom-work")

        self.assertEqual(root / "evidence-work", default_work)
        self.assertEqual(root / "custom-work", explicit)

    def test_verified_runner_output_paths_cannot_modify_model_input(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            model = root / "model"
            model.mkdir()
            with self.assertRaisesRegex(ValueError, "Evidence directory.*model directory"):
                verified_runner._protect_runner_output_paths(
                    evidence_dir=model / "evidence",
                    work_dir=root / "work",
                    verification_output=root / "verification.json",
                    kj_atlas_dir=None,
                    kj_atlas_backend_bundle=root / "bundle",
                    model_dir=model,
                    prepare_model_dir=None,
                )

    def test_verified_runner_output_paths_cannot_overlap_each_other(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            evidence = root / "evidence"
            with self.assertRaisesRegex(ValueError, "runner出力pathを相互に重ねられません"):
                verified_runner._protect_runner_output_paths(
                    evidence_dir=evidence,
                    work_dir=evidence / "work",
                    verification_output=root / "verification.json",
                    kj_atlas_dir=None,
                    kj_atlas_backend_bundle=root / "bundle",
                    model_dir=None,
                    prepare_model_dir=None,
                )

    def test_verified_runner_safe_sibling_outputs_are_accepted(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            verified_runner._protect_runner_output_paths(
                evidence_dir=root / "evidence",
                work_dir=root / "work",
                verification_output=root / "verification.json",
                kj_atlas_dir=None,
                kj_atlas_backend_bundle=root / "bundle",
                model_dir=root / "model",
                prepare_model_dir=root / "prepared-model",
            )

    def test_verified_preflight_receives_sanitized_environment(self):
        completed = subprocess.CompletedProcess(
            args=["preflight"],
            returncode=0,
            stdout='{"result":"ready","blockers":[]}',
            stderr="",
        )
        parent = {
            "PATH": "/usr/bin",
            "PYTHONPATH": "/tmp/injected",
            "GIT_DIR": "/tmp/other.git",
            "TMPDIR": "/tmp/injected-tmpdir",
        }
        with patch.dict(os.environ, parent, clear=True), patch.object(
            verified_runner.subprocess,
            "run",
            return_value=completed,
        ) as runner:
            result = verified_runner._run_preflight(["preflight"])

        self.assertEqual("ready", result["result"])
        environment = runner.call_args.kwargs["env"]
        self.assertNotIn("PYTHONPATH", environment)
        self.assertNotIn("TMPDIR", environment)
        self.assertFalse(any(key.startswith("GIT_") for key in environment))
        self.assertEqual("1", environment["PYTHONDONTWRITEBYTECODE"])
        self.assertEqual("1", environment["PYTHONNOUSERSITE"])

    def test_verified_runner_combined_log_uses_explicit_safe_parent(self):
        with tempfile.TemporaryDirectory() as temporary:
            log_dir = Path(temporary)
            parent = {
                "PATH": os.environ.get("PATH", ""),
                "PYTHONPATH": "/tmp/injected-pythonpath",
                "PYTHONHOME": "/tmp/injected-pythonhome",
                "TMPDIR": "/tmp/injected-tmpdir",
                "GIT_DIR": "/tmp/other.git",
            }
            command = [
                sys.executable,
                "-c",
                (
                    "import os; "
                    "print(os.environ.get('PYTHONPATH')); "
                    "print(os.environ.get('GIT_DIR')); "
                    "print(os.environ.get('TMPDIR'))"
                ),
            ]
            with patch.dict(os.environ, parent, clear=True):
                status, log_path, _digest, size = verified_runner._run_and_capture(
                    command,
                    log_dir=log_dir,
                )
            try:
                content = log_path.read_text(encoding="utf-8")
                self.assertEqual(0, status)
                self.assertEqual(log_dir, log_path.parent)
                self.assertGreater(size, 0)
                self.assertEqual(["None", "None", "None"], content.strip().splitlines())
            finally:
                log_path.unlink(missing_ok=True)

    def test_new_environment_test_is_registered_as_focused_check(self):
        self.assertIn(
            "test_runtime_version_exchange_local_child_environment.py",
            local_checks.CHECK_FILES,
        )
        self.assertIn(
            "test_runtime_version_exchange_local_child_environment.py",
            local_checks.discover_focused_candidate_names(),
        )

    def test_environment_sanitization_does_not_promote_focused_result(self):
        self.assertIn("!= actual Ollama A/B inference PASS", local_checks.STOP_LINE)
        self.assertIn(
            "!= runtime-version-exchange Scoped Executable Evidence",
            local_checks.STOP_LINE,
        )


if __name__ == "__main__":
    unittest.main()
