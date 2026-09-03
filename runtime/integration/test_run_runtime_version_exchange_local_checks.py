import os
import unittest
from unittest.mock import patch

import run_runtime_version_exchange_local_checks as local_checks


class RuntimeVersionExchangeLocalChecksTest(unittest.TestCase):
    def test_registered_checks_are_unique_existing_regular_files(self):
        paths = local_checks.validate_check_files()
        self.assertEqual(len(local_checks.CHECK_FILES), len(paths))
        self.assertEqual(len(local_checks.CHECK_FILES), len(set(local_checks.CHECK_FILES)))
        for path in paths:
            with self.subTest(path=path.name):
                self.assertTrue(path.is_file())
                self.assertFalse(path.is_symlink())

    def test_allowlist_covers_all_focused_candidates(self):
        self.assertEqual(
            set(local_checks.CHECK_FILES),
            local_checks.discover_focused_candidate_names(),
        )

    def test_validate_rejects_unregistered_runtime_exchange_test(self):
        discovered = set(local_checks.CHECK_FILES) | {"test_runtime_version_exchange_new_boundary.py"}
        with patch.object(
            local_checks,
            "discover_focused_candidate_names",
            return_value=discovered,
        ):
            with self.assertRaisesRegex(ValueError, "allowlistへ未登録"):
                local_checks.validate_check_files()

    def test_validate_rejects_stale_allowlist_entry(self):
        discovered = set(local_checks.CHECK_FILES)
        discovered.remove("test_verify_runtime_version_exchange_provenance.py")
        with patch.object(
            local_checks,
            "discover_focused_candidate_names",
            return_value=discovered,
        ):
            with self.assertRaisesRegex(ValueError, "候補外"):
                local_checks.validate_check_files()

    def test_source_identity_and_evidence_checks_are_included(self):
        expected = {
            "test_verify_kj_atlas_runtime_source.py",
            "test_export_kj_atlas_runtime_source.py",
            "test_runtime_version_exchange_identity_consistency.py",
            "test_verify_runtime_version_exchange_evidence.py",
            "test_verify_runtime_version_exchange_provenance.py",
        }
        self.assertTrue(expected.issubset(set(local_checks.CHECK_FILES)))

    def test_actual_low_level_harness_is_not_registered_as_focused_test(self):
        self.assertNotIn("run_runtime_version_exchange.sh", local_checks.CHECK_FILES)
        self.assertNotIn("run_runtime_version_exchange_strict.py", local_checks.CHECK_FILES)
        self.assertNotIn(
            "run_runtime_version_exchange_with_verification.py",
            local_checks.CHECK_FILES,
        )

    def test_select_checks_preserves_allowlist_order(self):
        selected = local_checks.select_checks(
            [
                "test_verify_runtime_version_exchange_provenance.py",
                "test_prepare_runtime_version_exchange_archives.py",
            ]
        )
        self.assertEqual(
            [
                "test_prepare_runtime_version_exchange_archives.py",
                "test_verify_runtime_version_exchange_provenance.py",
            ],
            [path.name for path in selected],
        )

    def test_select_checks_rejects_unknown_file(self):
        with self.assertRaisesRegex(ValueError, "未登録"):
            local_checks.select_checks(["test_unknown.py"])

    def test_parent_live_probe_environment_is_removed(self):
        environment = {
            "PATH": "/usr/bin",
            "SOZA_E3B_RUNTIME_EXCHANGE_LIVE": "1",
            "SOZA_E3B_RUNTIME_EXCHANGE_ARCHIVE_A": "/tmp/a",
            "SOZA_RUNTIME_EXCHANGE_MODEL_DIR": "/tmp/models",
            "OLLAMA_HOST": "127.0.0.1:11434",
            "OLLAMA_MODELS": "/tmp/models",
            "UNRELATED": "keep",
        }
        with patch.dict(os.environ, environment, clear=True):
            actual = local_checks.sanitized_environment()

        self.assertEqual("/usr/bin", actual["PATH"])
        self.assertEqual("keep", actual["UNRELATED"])
        self.assertNotIn("SOZA_E3B_RUNTIME_EXCHANGE_LIVE", actual)
        self.assertNotIn("SOZA_E3B_RUNTIME_EXCHANGE_ARCHIVE_A", actual)
        self.assertNotIn("SOZA_RUNTIME_EXCHANGE_MODEL_DIR", actual)
        self.assertNotIn("OLLAMA_HOST", actual)
        self.assertNotIn("OLLAMA_MODELS", actual)

    def test_stop_line_does_not_promote_helper_success_to_actual_evidence(self):
        self.assertIn("!= actual Ollama A/B inference PASS", local_checks.STOP_LINE)
        self.assertIn(
            "!= runtime-version-exchange Scoped Executable Evidence",
            local_checks.STOP_LINE,
        )


if __name__ == "__main__":
    unittest.main()
