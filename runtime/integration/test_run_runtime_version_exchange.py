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
        self.assertIn("--runtime-a-archive", completed.stdout)
        self.assertIn("--runtime-b-archive", completed.stdout)
        self.assertIn("--model-dir", completed.stdout)
        self.assertIn("既存pathは拒否する", completed.stdout)

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

    def test_evidence_directory_must_be_new_for_each_run(self):
        self.assertIn('if [[ -e "${EVIDENCE_DIR}" ]]', self.script_text)
        self.assertIn("Evidence directory already exists; specify a new path", self.script_text)

    def test_prepositioned_runtime_archives_are_still_digest_verified(self):
        self.assertIn('RUNTIME_ACQUISITION_A="prepositioned"', self.script_text)
        self.assertIn('RUNTIME_ACQUISITION_B="prepositioned"', self.script_text)
        self.assertIn('read -r actual_sha remainder < <(sha256sum "${archive}")', self.script_text)
        self.assertIn('if [[ "${actual_sha}" != "${expected_sha}" ]]', self.script_text)

    def test_prepositioned_model_store_is_not_auto_pulled_when_pinned_model_is_missing(self):
        marker = 'if [[ "${MODEL_STORE_MODE}" == "prepositioned" ]]'
        start = self.script_text.index(marker)
        end = self.script_text.index('"${ollama}" pull "${MODEL_NAME}"', start)
        prepositioned_branch = self.script_text[start:end]
        self.assertIn("prepositioned model directory does not contain the pinned artifact", prepositioned_branch)
        self.assertIn("return 1", prepositioned_branch)

    def test_acquisition_path_is_recorded_without_replacing_artifact_identity(self):
        self.assertIn('"archiveAcquisition": os.environ["RUNTIME_ACQUISITION_A"]', self.script_text)
        self.assertIn('"archiveAcquisition": os.environ["RUNTIME_ACQUISITION_B"]', self.script_text)
        self.assertIn('"archiveSha256": os.environ["RUNTIME_SHA256_A"]', self.script_text)
        self.assertIn('"archiveSha256": os.environ["RUNTIME_SHA256_B"]', self.script_text)
        self.assertIn('"storageMode": os.environ["MODEL_STORE_MODE"]', self.script_text)


if __name__ == "__main__":
    unittest.main()
