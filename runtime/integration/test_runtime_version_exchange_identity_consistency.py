import re
import unittest
from pathlib import Path

import check_runtime_version_exchange_preflight as preflight
import prepare_runtime_version_exchange_archives as prepare
import verify_kj_atlas_runtime_source as source_verifier
import verify_runtime_version_exchange_evidence as core_evidence
import verify_runtime_version_exchange_provenance as provenance


INTEGRATION_DIR = Path(__file__).resolve().parent
HARNESS = INTEGRATION_DIR / "run_runtime_version_exchange.sh"
GO_ARTIFACT_GUARD = (
    INTEGRATION_DIR.parent
    / "go"
    / "livemethodintegration"
    / "runtime_version_artifact_guard_test.go"
)

HEX40 = re.compile(r"^[0-9a-f]{40}$")


def shell_value(text: str, name: str) -> str:
    match = re.search(rf'^{re.escape(name)}="([^"]+)"$', text, re.MULTILINE)
    if match is None:
        raise AssertionError(f"shell constant not found: {name}")
    return match.group(1)


def go_value(text: str, name: str) -> str:
    match = re.search(
        rf'^\s*{re.escape(name)}\s*=\s*"([^"]+)"$',
        text,
        re.MULTILINE,
    )
    if match is None:
        raise AssertionError(f"Go constant not found: {name}")
    return match.group(1)


class RuntimeVersionExchangeIdentityConsistencyTest(unittest.TestCase):
    def test_manifest_method_source_matches_pinned_source_verifier_identity(self):
        method_source = prepare.load_manifest()["methodSource"]
        identity = source_verifier.PINNED_IDENTITY

        self.assertEqual(identity.repository, method_source["repository"])
        self.assertEqual(identity.source_commit, method_source["commit"])
        self.assertEqual(identity.backend_tree, method_source["backendTree"])
        self.assertEqual(
            identity.runtime_surface_tree,
            method_source["runtimeSurfaceTree"],
        )
        self.assertEqual(identity.pyproject_blob, method_source["pyprojectBlob"])
        self.assertEqual(identity.alembic_ini_blob, method_source["alembicIniBlob"])
        self.assertEqual(identity.alembic_tree, method_source["alembicTree"])
        self.assertEqual(identity.src_tree, method_source["srcTree"])

    def test_manifest_source_commit_matches_preflight_and_low_level_harness(self):
        method_source = prepare.load_manifest()["methodSource"]
        harness = HARNESS.read_text(encoding="utf-8")

        self.assertEqual(method_source["commit"], preflight.KJ_ATLAS_COMMIT)
        self.assertEqual(
            method_source["commit"],
            shell_value(harness, "KJ_ATLAS_COMMIT"),
        )

    def test_manifest_source_trees_match_go_live_guard(self):
        method_source = prepare.load_manifest()["methodSource"]
        guard = GO_ARTIFACT_GUARD.read_text(encoding="utf-8")

        self.assertEqual(
            method_source["backendTree"],
            go_value(guard, "pinnedKJAtlasBackendTree"),
        )
        self.assertEqual(
            method_source["runtimeSurfaceTree"],
            go_value(guard, "pinnedKJAtlasRuntimeSurfaceTree"),
        )

    def test_manifest_source_identity_matches_core_evidence_verifier(self):
        method_source = prepare.load_manifest()["methodSource"]

        self.assertEqual(method_source["commit"], core_evidence.EXPECTED_SOURCE_COMMIT)
        self.assertEqual(
            method_source["backendTree"],
            core_evidence.EXPECTED_PARENT_BACKEND_TREE,
        )
        self.assertEqual(
            method_source["runtimeSurfaceTree"],
            core_evidence.EXPECTED_RUNTIME_SURFACE_TREE,
        )

    def test_manifest_source_identity_matches_provenance_expectation(self):
        method_source = prepare.load_manifest()["methodSource"]

        self.assertEqual(
            {
                "repository": method_source["repository"],
                "sourceCommit": method_source["commit"],
                "pinnedBackendTree": method_source["backendTree"],
                "runtimeSurfaceTree": method_source["runtimeSurfaceTree"],
            },
            provenance._expected_source_identity(),
        )

    def test_manifest_source_git_object_ids_are_lowercase_sha1(self):
        method_source = prepare.load_manifest()["methodSource"]
        for field in (
            "commit",
            "backendTree",
            "runtimeSurfaceTree",
            "pyprojectBlob",
            "alembicIniBlob",
            "alembicTree",
            "srcTree",
        ):
            with self.subTest(field=field):
                self.assertRegex(method_source[field], HEX40)

    def test_runtime_and_model_identity_remain_manifest_aligned(self):
        manifest = prepare.load_manifest()
        harness = HARNESS.read_text(encoding="utf-8")

        self.assertEqual(manifest["runtimeArchives"]["a"]["version"], preflight.RUNTIME_VERSION_A)
        self.assertEqual(manifest["runtimeArchives"]["b"]["version"], preflight.RUNTIME_VERSION_B)
        self.assertEqual(manifest["runtimeArchives"]["a"]["sha256"], preflight.RUNTIME_SHA256_A)
        self.assertEqual(manifest["runtimeArchives"]["b"]["sha256"], preflight.RUNTIME_SHA256_B)
        self.assertEqual(manifest["model"]["name"], preflight.MODEL_NAME)
        self.assertEqual(manifest["model"]["sha256"], preflight.MODEL_SHA256)
        self.assertEqual(manifest["model"]["name"], shell_value(harness, "MODEL_NAME"))
        self.assertEqual(manifest["model"]["sha256"], shell_value(harness, "MODEL_SHA256"))

    def test_runtime_archive_size_and_platform_remain_manifest_aligned(self):
        manifest = prepare.load_manifest()
        runtime_a = manifest["runtimeArchives"]["a"]
        runtime_b = manifest["runtimeArchives"]["b"]
        expected_platform = {"os": "linux", "arch": "amd64"}

        self.assertEqual(runtime_a["sizeBytes"], preflight.RUNTIME_SIZE_A)
        self.assertEqual(runtime_b["sizeBytes"], preflight.RUNTIME_SIZE_B)
        self.assertEqual(
            runtime_a["sizeBytes"] + runtime_b["sizeBytes"],
            preflight.TOTAL_COMPRESSED_RUNTIME_BYTES,
        )
        self.assertEqual(expected_platform, runtime_a["platform"])
        self.assertEqual(expected_platform, runtime_b["platform"])

        harness = HARNESS.read_text(encoding="utf-8")
        self.assertIn('if [[ "${HOST_OS}" != "Linux" ]]', harness)
        self.assertIn("x86_64|amd64)", harness)

    def test_runtime_archive_download_origin_remains_manifest_aligned(self):
        manifest = prepare.load_manifest()
        harness = HARNESS.read_text(encoding="utf-8")

        for label in ("a", "b"):
            archive = manifest["runtimeArchives"][label]
            expected_url = (
                "https://github.com/ollama/ollama/releases/download/"
                f"v{archive['version']}/{archive['assetName']}"
            )
            with self.subTest(runtime=label):
                self.assertEqual(expected_url, archive["downloadUrl"])
                self.assertEqual("ollama-linux-amd64.tar.zst", archive["assetName"])

        # The harness no longer builds the download URL itself; it delegates the
        # runtime archive acquisition to the preparation helper (6a7ac02), which
        # validates each downloadUrl against the official release template.
        preparer = (INTEGRATION_DIR / "prepare_runtime_version_exchange_archives.py").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            'RUNTIME_ARCHIVE_PREPARER="${SEI_ROOT}/runtime/integration/prepare_runtime_version_exchange_archives.py"',
            harness,
        )
        self.assertNotIn("releases/download/v${version}", harness)
        self.assertIn('"https://github.com/ollama/ollama/releases/download/"', preparer)
        self.assertIn('f"v{version}/{asset_name}"', preparer)


if __name__ == "__main__":
    unittest.main()
