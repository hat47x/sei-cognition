import argparse
import hashlib
import re
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import check_runtime_version_exchange_preflight as preflight


INTEGRATION_DIR = Path(__file__).resolve().parent
HARNESS = INTEGRATION_DIR / "run_runtime_version_exchange.sh"


def shell_value(text: str, name: str) -> str:
    match = re.search(rf'^{re.escape(name)}="([^"]+)"$', text, re.MULTILINE)
    if match is None:
        raise AssertionError(f"shell constant not found: {name}")
    return match.group(1)


class RuntimeVersionExchangePreflightTest(unittest.TestCase):
    def test_is_within_distinguishes_source_tree_and_sibling(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "repo"
            child = root / "runtime" / "evidence"
            sibling = Path(temp) / "repo-output"
            self.assertTrue(preflight.is_within(child, root))
            self.assertFalse(preflight.is_within(sibling, root))

    def test_archive_check_accepts_exact_digest(self):
        with tempfile.TemporaryDirectory() as temp:
            archive = Path(temp) / "runtime.tar.zst"
            archive.write_bytes(b"fixed-runtime-artifact")
            expected = hashlib.sha256(archive.read_bytes()).hexdigest()
            checks = preflight.archive_check("runtime-a", archive, expected, True)
            self.assertEqual("ok", checks[0].status)

    def test_archive_check_rejects_digest_mismatch(self):
        with tempfile.TemporaryDirectory() as temp:
            archive = Path(temp) / "runtime.tar.zst"
            archive.write_bytes(b"different-runtime-artifact")
            checks = preflight.archive_check("runtime-a", archive, "0" * 64, True)
            self.assertEqual("blocked", checks[0].status)
            self.assertIn("digest", checks[0].detail)

    def test_missing_archive_is_deferred_when_download_is_allowed(self):
        checks = preflight.archive_check("runtime-a", None, "0" * 64, False)
        self.assertEqual("deferred", checks[0].status)

    def test_missing_archive_blocks_prepositioned_only_preflight(self):
        checks = preflight.archive_check("runtime-a", None, "0" * 64, True)
        self.assertEqual("blocked", checks[0].status)

    def test_model_store_does_not_claim_digest_verification(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "source"
            model = Path(temp) / "model"
            source.mkdir()
            model.mkdir()
            checks = preflight.model_store_check(model, (source,), True)
            self.assertEqual("ok", checks[0].status)
            self.assertIn("Ollama起動後", checks[0].detail)

    def test_parser_rejects_checkout_and_bundle_together(self):
        parser = preflight.build_parser()
        with self.assertRaises(SystemExit):
            parser.parse_args(
                [
                    "--kj-atlas-dir",
                    "/tmp/kj-atlas",
                    "--kj-atlas-backend-bundle",
                    "/tmp/kj-atlas-bundle",
                ]
            )

    def test_runtime_bundle_check_accepts_verified_identity(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            soza = root / "soza"
            bundle = root / "bundle"
            soza.mkdir()
            bundle.mkdir()
            payload = {
                "sourceCommit": preflight.PINNED_IDENTITY.source_commit,
                "pinnedBackendTree": preflight.PINNED_IDENTITY.backend_tree,
                "runtimeSurfaceTree": preflight.PINNED_IDENTITY.runtime_surface_tree,
            }
            with patch.object(preflight, "verify_runtime_bundle", return_value=payload):
                checks = preflight.runtime_bundle_check(bundle, soza)
            self.assertEqual(["ok", "ok"], [check.status for check in checks])
            self.assertIn(preflight.PINNED_IDENTITY.runtime_surface_tree, checks[1].detail)

    def test_runtime_bundle_check_rejects_identity_mismatch(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            soza = root / "soza"
            bundle = root / "bundle"
            soza.mkdir()
            bundle.mkdir()
            with patch.object(
                preflight,
                "verify_runtime_bundle",
                side_effect=ValueError("runtime source bundle identity mismatch"),
            ):
                checks = preflight.runtime_bundle_check(bundle, soza)
            self.assertEqual("blocked", checks[0].status)
            self.assertIn("identity", checks[0].detail)

    def test_runtime_bundle_check_rejects_bundle_inside_soza(self):
        with tempfile.TemporaryDirectory() as temp:
            soza = Path(temp) / "soza"
            bundle = soza / "bundle"
            bundle.mkdir(parents=True)
            checks = preflight.runtime_bundle_check(bundle, soza)
            self.assertEqual("blocked", checks[0].status)
            self.assertIn("SOZA repository配下", checks[0].detail)

    def test_preflight_and_harness_use_the_same_fixed_identity(self):
        text = HARNESS.read_text(encoding="utf-8")
        pairs = [
            ("KJ_ATLAS_COMMIT", preflight.KJ_ATLAS_COMMIT),
            ("MODEL_NAME", preflight.MODEL_NAME),
            ("MODEL_SHA256", preflight.MODEL_SHA256),
            ("RUNTIME_VERSION_A", preflight.RUNTIME_VERSION_A),
            ("RUNTIME_VERSION_B", preflight.RUNTIME_VERSION_B),
            ("RUNTIME_SHA256_A", preflight.RUNTIME_SHA256_A),
            ("RUNTIME_SHA256_B", preflight.RUNTIME_SHA256_B),
        ]
        for shell_name, expected in pairs:
            with self.subTest(shell=shell_name):
                self.assertEqual(expected, shell_value(text, shell_name))
        self.assertEqual(preflight.KJ_ATLAS_COMMIT, preflight.PINNED_IDENTITY.source_commit)

    def test_report_contains_source_identity_without_promoting_it(self):
        result = preflight.report([preflight.Check("sample", "ok", "ok")])
        self.assertEqual(preflight.PINNED_IDENTITY.source_commit, result["sourceIdentity"]["sourceCommit"])
        self.assertEqual(
            preflight.PINNED_IDENTITY.runtime_surface_tree,
            result["sourceIdentity"]["runtimeSurfaceTree"],
        )
        self.assertIn("!= actual runtime A/B inference PASS", result["stopLine"])

    def test_report_never_promotes_preflight_to_executable_evidence(self):
        result = preflight.report([preflight.Check("sample", "ok", "ok")])
        self.assertEqual("ready", result["result"])
        self.assertIn("!= actual runtime A/B inference PASS", result["stopLine"])

    def test_report_is_blocked_when_any_check_is_blocked(self):
        result = preflight.report(
            [
                preflight.Check("ok", "ok", "ok"),
                preflight.Check("blocked", "blocked", "blocked"),
            ]
        )
        self.assertEqual("blocked", result["result"])
        self.assertEqual(["blocked"], result["blockers"])


if __name__ == "__main__":
    unittest.main()
