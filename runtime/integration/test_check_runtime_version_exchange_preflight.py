import hashlib
import re
import tempfile
import unittest
from pathlib import Path

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

    def test_archive_check_accepts_exact_size_and_digest(self):
        with tempfile.TemporaryDirectory() as temp:
            archive = Path(temp) / "runtime.tar.zst"
            data = b"fixed-runtime-artifact"
            archive.write_bytes(data)
            expected = hashlib.sha256(data).hexdigest()
            checks = preflight.archive_check("runtime-a", archive, expected, len(data), True)
            self.assertEqual("ok", checks[0].status)
            self.assertIn("size=", checks[0].detail)
            self.assertIn("sha256=", checks[0].detail)

    def test_archive_check_rejects_size_mismatch_before_digest(self):
        with tempfile.TemporaryDirectory() as temp:
            archive = Path(temp) / "runtime.tar.zst"
            data = b"fixed-runtime-artifact"
            archive.write_bytes(data)
            expected = hashlib.sha256(data).hexdigest()
            checks = preflight.archive_check("runtime-a", archive, expected, len(data) + 1, True)
            self.assertEqual("blocked", checks[0].status)
            self.assertIn("size", checks[0].detail)

    def test_archive_check_rejects_digest_mismatch_after_size_match(self):
        with tempfile.TemporaryDirectory() as temp:
            archive = Path(temp) / "runtime.tar.zst"
            data = b"different-runtime-artifact"
            archive.write_bytes(data)
            checks = preflight.archive_check("runtime-a", archive, "0" * 64, len(data), True)
            self.assertEqual("blocked", checks[0].status)
            self.assertIn("digest", checks[0].detail)

    def test_missing_archive_is_deferred_when_download_is_allowed(self):
        checks = preflight.archive_check("runtime-a", None, "0" * 64, 123, False)
        self.assertEqual("deferred", checks[0].status)
        self.assertIn("123", checks[0].detail)

    def test_missing_archive_blocks_prepositioned_only_preflight(self):
        checks = preflight.archive_check("runtime-a", None, "0" * 64, 123, True)
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

    def test_disk_capacity_check_is_observational_only(self):
        with tempfile.TemporaryDirectory() as temp:
            check = preflight.disk_capacity_check(Path(temp) / "future-work")
            self.assertEqual("ok", check.status)
            self.assertIn(str(preflight.TOTAL_COMPRESSED_RUNTIME_BYTES), check.detail)
            self.assertIn("十分とは判定しません", check.detail)

    def test_fixed_runtime_sizes_match_official_metadata_values(self):
        self.assertEqual(1421793186, preflight.RUNTIME_SIZE_A)
        self.assertEqual(1421191399, preflight.RUNTIME_SIZE_B)
        self.assertEqual(2842984585, preflight.TOTAL_COMPRESSED_RUNTIME_BYTES)

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

    def test_report_exposes_fixed_artifact_sizes_without_promoting_evidence(self):
        result = preflight.report([preflight.Check("sample", "ok", "ok")])
        self.assertEqual("ready", result["result"])
        self.assertEqual(1421793186, result["fixedArtifacts"]["runtimeA"]["sizeBytes"])
        self.assertEqual(1421191399, result["fixedArtifacts"]["runtimeB"]["sizeBytes"])
        self.assertEqual(2842984585, result["fixedArtifacts"]["totalCompressedRuntimeBytes"])
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
