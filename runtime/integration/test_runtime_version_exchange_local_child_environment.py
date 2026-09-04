import os
import subprocess
import unittest
from unittest.mock import patch

import run_runtime_version_exchange_local_checks as local_checks


class RuntimeVersionExchangeLocalChildEnvironmentTest(unittest.TestCase):
    def test_parent_python_git_and_temp_environment_is_not_inherited(self):
        parent = {
            "PATH": "/usr/bin",
            "HOME": "/home/example",
            "UNRELATED": "keep",
            "SOZA_RUNTIME_EXCHANGE_MODEL_DIR": "/tmp/model",
            "SOZA_E3B_RUNTIME_EXCHANGE_LIVE": "1",
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
            "PYTHONDONTWRITEBYTECODE": "0",
            "PYTHONNOUSERSITE": "0",
        }
        with patch.dict(os.environ, parent, clear=True):
            actual = local_checks.sanitized_environment()

        self.assertEqual("/usr/bin", actual["PATH"])
        self.assertEqual("/home/example", actual["HOME"])
        self.assertEqual("keep", actual["UNRELATED"])

        for key in (
            "SOZA_RUNTIME_EXCHANGE_MODEL_DIR",
            "SOZA_E3B_RUNTIME_EXCHANGE_LIVE",
            "OLLAMA_HOST",
            "OLLAMA_MODELS",
            "PYTHONPATH",
            "PYTHONHOME",
            "PYTHONSTARTUP",
            "PYTHONUSERBASE",
            "TMPDIR",
            "TMP",
            "TEMP",
            "GIT_DIR",
            "GIT_WORK_TREE",
        ):
            with self.subTest(key=key):
                self.assertNotIn(key, actual)

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
        self.assertEqual(["git", "-C", str(local_checks.SOZA_ROOT)], command[:3])
        environment = runner.call_args.kwargs["env"]
        self.assertEqual("/usr/bin", environment["PATH"])
        self.assertEqual("keep", environment["UNRELATED"])
        self.assertFalse(any(key.startswith("GIT_") for key in environment))

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
