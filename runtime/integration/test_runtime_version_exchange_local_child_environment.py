import os
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
