import json
import os
import tempfile
import unittest
from pathlib import Path
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

    def test_runner_self_test_is_registered(self):
        self.assertIn(
            "test_run_runtime_version_exchange_local_checks.py",
            local_checks.CHECK_FILES,
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

    def test_result_output_must_be_new_and_outside_soza_repository(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            soza = root / "soza"
            soza.mkdir()
            outside = root / "focused-result.json"
            with patch.object(local_checks, "SOZA_ROOT", soza):
                self.assertEqual(outside, local_checks.prepare_result_output(outside))
                with self.assertRaisesRegex(ValueError, "SOZA repository外"):
                    local_checks.prepare_result_output(soza / "focused-result.json")

                outside.write_text("existing\n", encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "新規path"):
                    local_checks.prepare_result_output(outside)

    def test_result_output_rejects_symlink_path(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            soza = root / "soza"
            soza.mkdir()
            actual = root / "actual.json"
            actual.write_text("existing\n", encoding="utf-8")
            linked = root / "linked.json"
            linked.symlink_to(actual)
            with patch.object(local_checks, "SOZA_ROOT", soza):
                with self.assertRaisesRegex(ValueError, "symlink"):
                    local_checks.prepare_result_output(linked)

    def test_build_result_never_promotes_focused_success_to_actual_evidence(self):
        selected = [Path("test_a.py"), Path("test_b.py")]
        executions = [
            {"name": "test_a.py", "exitCode": 0},
            {"name": "test_b.py", "exitCode": 0},
        ]
        with patch.object(
            local_checks,
            "repository_observation",
            return_value={
                "commit": "a" * 40,
                "clean": True,
                "commitObserved": True,
                "cleanlinessObserved": True,
            },
        ):
            result = local_checks.build_result(
                selected=selected,
                executions=executions,
                stopped_early=False,
            )

        self.assertEqual("ok", result["result"])
        self.assertFalse(result["actualRuntimeExchangeEvidence"])
        self.assertEqual("not_evaluated", result["qualityJudgement"])
        self.assertEqual(2, result["selectedCount"])
        self.assertEqual(2, result["executedCount"])
        self.assertEqual(0, result["failedCount"])
        self.assertIn("!= actual Ollama A/B inference PASS", result["stopLine"])

    def test_build_result_marks_failure_and_early_stop(self):
        selected = [Path("test_a.py"), Path("test_b.py")]
        executions = [{"name": "test_a.py", "exitCode": 3}]
        with patch.object(local_checks, "repository_observation", return_value={}):
            result = local_checks.build_result(
                selected=selected,
                executions=executions,
                stopped_early=True,
            )

        self.assertEqual("failed", result["result"])
        self.assertEqual(1, result["executedCount"])
        self.assertEqual(1, result["failedCount"])
        self.assertTrue(result["stoppedEarly"])
        self.assertFalse(result["actualRuntimeExchangeEvidence"])

    def test_write_result_creates_machine_readable_json(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "result.json"
            payload = {
                "schema": local_checks.RESULT_SCHEMA,
                "result": "ok",
                "actualRuntimeExchangeEvidence": False,
            }
            local_checks.write_result(path, payload)
            actual = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(payload, actual)

    def test_parser_rejects_list_with_result_output(self):
        parser = local_checks.build_parser()
        args = parser.parse_args(["--list", "--result-output", "/tmp/result.json"])
        self.assertTrue(args.list)
        self.assertIsNotNone(args.result_output)

    def test_stop_line_does_not_promote_helper_success_to_actual_evidence(self):
        self.assertIn("!= actual Ollama A/B inference PASS", local_checks.STOP_LINE)
        self.assertIn(
            "!= runtime-version-exchange Scoped Executable Evidence",
            local_checks.STOP_LINE,
        )


if __name__ == "__main__":
    unittest.main()
