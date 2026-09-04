import importlib.util
import re
import subprocess
import unittest
from pathlib import Path


INTEGRATION_DIR = Path(__file__).resolve().parent
RUNTIME_DIR = INTEGRATION_DIR.parent
SCRIPT = INTEGRATION_DIR / "run_runtime_version_exchange.sh"
SOURCE_VERIFIER = INTEGRATION_DIR / "verify_kj_atlas_runtime_source.py"
GO_EXCHANGE_TEST = RUNTIME_DIR / "go" / "livemethodintegration" / "runtime_version_exchange_test.go"
GO_GUARD = RUNTIME_DIR / "go" / "livemethodintegration" / "runtime_version_artifact_guard_test.go"

SOURCE_VERIFIER_SPEC = importlib.util.spec_from_file_location(
    "verify_kj_atlas_runtime_source",
    SOURCE_VERIFIER,
)
if SOURCE_VERIFIER_SPEC is None or SOURCE_VERIFIER_SPEC.loader is None:
    raise RuntimeError(f"cannot load source verifier: {SOURCE_VERIFIER}")
SOURCE_VERIFIER_MODULE = importlib.util.module_from_spec(SOURCE_VERIFIER_SPEC)
SOURCE_VERIFIER_SPEC.loader.exec_module(SOURCE_VERIFIER_MODULE)


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
        self.assertIn("--kj-atlas-backend-bundle", completed.stdout)
        self.assertNotIn("--kj-atlas-dir", completed.stdout)
        self.assertIn("--evidence-dir", completed.stdout)
        self.assertIn("--runtime-a-archive", completed.stdout)
        self.assertIn("--runtime-b-archive", completed.stdout)
        self.assertIn("--model-dir", completed.stdout)
        self.assertIn("既存pathは拒否する", completed.stdout)
        self.assertIn("run_runtime_version_exchange_strict.py", completed.stdout)

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

    def test_source_identity_is_shared_across_harness_verifier_and_go_guard(self):
        self.assertEqual(
            shell_value(self.script_text, "KJ_ATLAS_COMMIT"),
            SOURCE_VERIFIER_MODULE.PINNED_IDENTITY.source_commit,
        )
        self.assertEqual(
            go_value(self.go_guard_text, "pinnedKJAtlasBackendTree"),
            SOURCE_VERIFIER_MODULE.PINNED_IDENTITY.backend_tree,
        )
        self.assertEqual(
            go_value(self.go_guard_text, "pinnedKJAtlasRuntimeSurfaceTree"),
            SOURCE_VERIFIER_MODULE.PINNED_IDENTITY.runtime_surface_tree,
        )

    def test_runtime_surface_tree_is_not_confused_with_parent_backend_tree(self):
        self.assertNotEqual(
            SOURCE_VERIFIER_MODULE.PINNED_IDENTITY.runtime_surface_tree,
            SOURCE_VERIFIER_MODULE.PINNED_IDENTITY.backend_tree,
        )
        verifier_text = SOURCE_VERIFIER.read_text(encoding="utf-8")
        self.assertIn('"pinnedBackendTree": identity.backend_tree', verifier_text)
        self.assertIn('"runtimeSurfaceTree": actual["runtimeSurfaceTree"]', verifier_text)

    def test_harness_passes_every_live_guard_path_explicitly(self):
        required_names = {
            "SOZA_E3B_RUNTIME_EXCHANGE_KJ_ATLAS_SOURCE_MODE",
            "SOZA_E3B_RUNTIME_EXCHANGE_KJ_ATLAS_BACKEND_DIR",
            "SOZA_E3B_RUNTIME_EXCHANGE_KJ_ATLAS_SOURCE_VERIFIER",
            "SOZA_E3B_RUNTIME_EXCHANGE_ARCHIVE_A",
            "SOZA_E3B_RUNTIME_EXCHANGE_ARCHIVE_B",
            "SOZA_E3B_RUNTIME_EXCHANGE_VERSION_LOG_A",
            "SOZA_E3B_RUNTIME_EXCHANGE_VERSION_LOG_B",
        }
        for name in required_names:
            with self.subTest(environment=name):
                self.assertIn(f'export {name}=', self.script_text)
        self.assertNotIn("SOZA_E3B_RUNTIME_EXCHANGE_KJ_ATLAS_DIR", self.script_text)

    def test_go_live_guard_has_no_github_workspace_or_tmp_fallback(self):
        self.assertNotIn("GITHUB_WORKSPACE", self.go_guard_text)
        self.assertNotIn('"/tmp/runtime-exchange-', self.go_guard_text)
        self.assertNotIn('"/tmp/ollama-', self.go_guard_text)

    def test_evidence_directory_must_be_new_for_each_run(self):
        self.assertIn('if [[ -e "${EVIDENCE_DIR}" ]]', self.script_text)
        self.assertIn("Evidence directory already exists; specify a new path", self.script_text)

    def test_verified_source_bundle_is_copied_before_execution_and_install(self):
        self.assertIn('KJ_ATLAS_BACKEND_DIR="${WORK_DIR}/kj-atlas-backend-execution"', self.script_text)
        self.assertIn('KJ_ATLAS_INSTALL_DIR="${WORK_DIR}/kj-atlas-backend-install"', self.script_text)
        self.assertIn('cp -a "${KJ_ATLAS_SOURCE_ROOT}/." "${KJ_ATLAS_BACKEND_DIR}/"', self.script_text)
        self.assertIn('cp -a "${KJ_ATLAS_SOURCE_ROOT}/." "${KJ_ATLAS_INSTALL_DIR}/"', self.script_text)
        self.assertIn('--backend-dir "${KJ_ATLAS_BACKEND_DIR}"', self.script_text)
        self.assertIn('--backend-dir "${KJ_ATLAS_INSTALL_DIR}"', self.script_text)
        self.assertIn('PYTHONPATH="${KJ_ATLAS_BACKEND_DIR}/src"', self.script_text)

    def test_package_install_never_builds_from_actual_execution_source(self):
        self.assertIn('KJ_ATLAS_INSTALL_DIR="${WORK_DIR}/kj-atlas-backend-install"', self.script_text)
        self.assertIn('cp -a "${KJ_ATLAS_SOURCE_ROOT}/." "${KJ_ATLAS_INSTALL_DIR}/"', self.script_text)
        self.assertIn(
            'pip install --disable-pip-version-check "${KJ_ATLAS_INSTALL_DIR}"',
            self.script_text,
        )
        self.assertNotIn('pip install --disable-pip-version-check -e', self.script_text)

    def test_low_level_harness_requires_verified_bundle_and_has_no_checkout_fallback(self):
        self.assertIn('if [[ -z "${KJ_ATLAS_BACKEND_BUNDLE}" ]]', self.script_text)
        self.assertIn("verified KJ Atlas backend bundle is required", self.script_text)
        self.assertNotIn("--kj-atlas-dir", self.script_text)
        self.assertNotIn("_external/kj-atlas", self.script_text)
        self.assertNotIn('"sourceMode": "git-checkout"', self.script_text)
        self.assertIn('KJ_ATLAS_SOURCE_MODE="verified-runtime-bundle"', self.script_text)

    def test_go_live_guard_keeps_git_checkout_rejected(self):
        self.assertIn(
            "runtime exchange live testではGit working treeを実行sourceにできません",
            self.go_guard_text,
        )

    def test_source_identity_is_preserved_as_run_evidence(self):
        self.assertIn('KJ_ATLAS_SOURCE_IDENTITY_FILE="${WORK_DIR}/kj-atlas-source-identity.json"', self.script_text)
        self.assertIn('"methodSource": method_source', self.script_text)
        self.assertIn('"${KJ_ATLAS_SOURCE_IDENTITY_FILE}" \\', self.script_text)

    def test_prepositioned_runtime_archives_are_still_digest_verified(self):
        self.assertIn('RUNTIME_ACQUISITION_A="prepositioned"', self.script_text)
        self.assertIn('RUNTIME_ACQUISITION_B="prepositioned"', self.script_text)
        self.assertIn('read -r actual_sha remainder < <(sha256sum "${archive}")', self.script_text)
        self.assertIn('if [[ "${actual_sha}" != "${expected_sha}" ]]', self.script_text)

    def test_downloaded_runtime_archives_use_the_canonical_preparation_helper(self):
        self.assertIn(
            'RUNTIME_ARCHIVE_PREPARER="${SOZA_ROOT}/runtime/integration/prepare_runtime_version_exchange_archives.py"',
            self.script_text,
        )
        self.assertIn('prepare_downloaded_runtime_archive()', self.script_text)
        self.assertIn('python3 "${RUNTIME_ARCHIVE_PREPARER}" \\', self.script_text)
        self.assertIn('--output-dir "${RUNTIME_ARCHIVE_PREPARATION_DIR}"', self.script_text)
        self.assertIn('--runtime "${label}"', self.script_text)
        self.assertIn('--json >"${result_file}"', self.script_text)
        self.assertIn('RUNTIME_ARCHIVE_A="$(prepare_downloaded_runtime_archive a)"', self.script_text)
        self.assertIn('RUNTIME_ARCHIVE_B="$(prepare_downloaded_runtime_archive b)"', self.script_text)
        self.assertNotIn(
            'https://github.com/ollama/ollama/releases/download/v${version}/ollama-linux-amd64.tar.zst',
            self.script_text,
        )

    def test_runtime_archive_preparation_observation_is_preserved_when_available(self):
        self.assertIn(
            '"${WORK_DIR}/runtime-exchange-a-archive-preparation.json" \\',
            self.script_text,
        )
        self.assertIn(
            '"${WORK_DIR}/runtime-exchange-b-archive-preparation.json" \\',
            self.script_text,
        )
        self.assertIn('payload.get("result") != "ok"', self.script_text)
        self.assertIn('archive.get("status") != "ok"', self.script_text)

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
