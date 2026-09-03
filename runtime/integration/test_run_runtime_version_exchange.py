import re
import subprocess
import unittest
from pathlib import Path


INTEGRATION_DIR = Path(__file__).resolve().parent
RUNTIME_DIR = INTEGRATION_DIR.parent
SCRIPT = INTEGRATION_DIR / "run_runtime_version_exchange.sh"
GO_EXCHANGE_TEST = RUNTIME_DIR / "go" / "livemethodintegration" / "runtime_version_exchange_test.go"
GO_GUARD = RUNTIME_DIR / "go" / "livemethodintegration" / "runtime_version_artifact_guard_test.go"


def shell_value(text: str, name: str) -> str:
    match = re.search(rf'^{re.escape(name)}="([^"]+)"$', text, re.MULTILINE)
    if match is None:
        raise AssertionError(f"shell constant not found: {name}")
    return match.group(1)


def go_value(text: str, name: str) -> str:
    match = re.search(rf'^\s*{re.escape(name)}\s*=\s*"([^"]+)"$', text, re.MULTILINE)
    if match is None:
        raise AssertionError(f"Go constant not found: {name}")
    return match.group(1)


class RuntimeVersionExchangeHarnessTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.script_text = SCRIPT.read_text(encoding="utf-8")
        cls.go_exchange_text = GO_EXCHANGE_TEST.read_text(encoding="utf-8")
        cls.go_guard_text = GO_GUARD.read_text(encoding="utf-8")

    def test_shell_syntax_is_valid(self):
        subprocess.run(["bash", "-n", str(SCRIPT)], check=True)

    def test_help_is_available_without_starting_the_probe(self):
        completed = subprocess.run(
            ["bash", str(SCRIPT), "--help"],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("runtime/integration/run_runtime_version_exchange.sh", completed.stdout)
        self.assertIn("GitHub Actions", completed.stdout)
        self.assertIn("--evidence-dir", completed.stdout)

    def test_shell_and_go_use_the_same_runtime_versions_and_artifact_digests(self):
        pairs = [
            ("RUNTIME_VERSION_A", "runtimeExchangeVersionA"),
            ("RUNTIME_VERSION_B", "runtimeExchangeVersionB"),
            ("RUNTIME_SHA256_A", "runtimeExchangeArtifactA"),
            ("RUNTIME_SHA256_B", "runtimeExchangeArtifactB"),
        ]
        for shell_name, go_name in pairs:
            with self.subTest(shell=shell_name, go=go_name):
                self.assertEqual(
                    shell_value(self.script_text, shell_name),
                    go_value(self.go_exchange_text, go_name),
                )

    def test_harness_passes_every_live_guard_path_explicitly(self):
        required_names = {
            "SOZA_E3B_RUNTIME_EXCHANGE_KJ_ATLAS_DIR",
            "SOZA_E3B_RUNTIME_EXCHANGE_ARCHIVE_A",
            "SOZA_E3B_RUNTIME_EXCHANGE_ARCHIVE_B",
            "SOZA_E3B_RUNTIME_EXCHANGE_VERSION_LOG_A",
            "SOZA_E3B_RUNTIME_EXCHANGE_VERSION_LOG_B",
        }
        for name in required_names:
            with self.subTest(environment=name):
                self.assertIn(f'export {name}=', self.script_text)

    def test_go_live_guard_has_no_github_workspace_or_tmp_fallback(self):
        self.assertNotIn("GITHUB_WORKSPACE", self.go_guard_text)
        self.assertNotIn('"/tmp/runtime-exchange-', self.go_guard_text)
        self.assertNotIn('"/tmp/ollama-', self.go_guard_text)


if __name__ == "__main__":
    unittest.main()
