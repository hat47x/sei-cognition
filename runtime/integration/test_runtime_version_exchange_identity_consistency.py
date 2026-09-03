import re
import unittest
from pathlib import Path

import check_runtime_version_exchange_preflight as preflight
import prepare_runtime_version_exchange_archives as prepare
import verify_kj_atlas_runtime_source as source_verifier


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


if __name__ == "__main__":
    unittest.main()
