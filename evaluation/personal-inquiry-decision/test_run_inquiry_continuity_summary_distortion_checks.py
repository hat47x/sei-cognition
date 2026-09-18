#!/usr/bin/env python3

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from run_inquiry_continuity_summary_distortion_checks import (
    FIXTURE_IDS,
    STOP_LINE,
    build_result,
    configured_checks,
    run_checks,
    sanitized_environment,
    save_result,
)


class SummaryDistortionLocalChecksTest(unittest.TestCase):
    def test_configured_checks_cover_units_validate_and_three_preflights(self):
        checks = configured_checks()
        self.assertEqual(
            [check.name for check in checks[:4]],
            [
                "summary-distortion-probe-tests",
                "summary-distortion-evidence-tests",
                "summary-distortion-local-runner-tests",
                "summary-distortion-probe-validate",
            ],
        )
        self.assertEqual(len(checks), 4 + len(FIXTURE_IDS))
        for fixture_id, check in zip(FIXTURE_IDS, checks[4:]):
            self.assertEqual(
                check.name,
                f"summary-distortion-preflight-{fixture_id}",
            )
            self.assertEqual(check.command[-1], "preflight")
            self.assertIn(fixture_id, check.command)

    def test_sanitized_environment_removes_secret_and_injection_inputs(self):
        environment = sanitized_environment(
            {
                "PATH": "/bin",
                "SEI_LIVE_PROVIDER_TOKEN": "secret",
                "SOZA_LEGACY_SECRET": "legacy",
                "KJ_ATLAS_DATABASE_URL": "db",
                "OLLAMA_HOST": "127.0.0.1:11434",
                "OPENAI_API_KEY": "secret",
                "PYTHONPATH": "/tmp/injected",
                "PYTHONHOME": "/tmp/python",
            }
        )
        self.assertEqual(environment["PATH"], "/bin")
        for removed in (
            "SEI_LIVE_PROVIDER_TOKEN",
            "SOZA_LEGACY_SECRET",
            "KJ_ATLAS_DATABASE_URL",
            "OLLAMA_HOST",
            "OPENAI_API_KEY",
            "PYTHONPATH",
            "PYTHONHOME",
        ):
            self.assertNotIn(removed, environment)
        self.assertEqual(environment["PYTHONDONTWRITEBYTECODE"], "1")
        self.assertEqual(environment["PYTHONNOUSERSITE"], "1")

    def test_all_pass_is_mechanics_only(self):
        def runner(command, *, cwd, env, timeout):
            return subprocess.CompletedProcess(command, 0)

        exit_code, result = run_checks(
            configured_checks(),
            runner=runner,
        )
        self.assertEqual(exit_code, 0)
        self.assertEqual(result["result"], "ok")
        self.assertEqual(result["failedCount"], 0)
        self.assertFalse(result["humanReviewObserved"])
        self.assertFalse(result["actualLongGapResumptionEstablished"])
        self.assertFalse(result["productValueEstablished"])
        self.assertFalse(result["stableRequirementAuthorized"])
        self.assertEqual(result["stopLine"], STOP_LINE)

    def test_failure_is_preserved_without_claiming_unexecuted_pass(self):
        calls = 0

        def runner(command, *, cwd, env, timeout):
            nonlocal calls
            calls += 1
            return subprocess.CompletedProcess(
                command,
                7 if calls == 2 else 0,
            )

        exit_code, result = run_checks(
            configured_checks(),
            runner=runner,
        )
        self.assertEqual(exit_code, 1)
        self.assertEqual(result["failedCount"], 1)
        self.assertEqual(
            result["executedCount"],
            result["selectedCount"],
        )

    def test_stop_on_failure_marks_incomplete_run(self):
        def runner(command, *, cwd, env, timeout):
            return subprocess.CompletedProcess(command, 1)

        exit_code, result = run_checks(
            configured_checks(),
            stop_on_failure=True,
            runner=runner,
        )
        self.assertEqual(exit_code, 1)
        self.assertTrue(result["stoppedEarly"])
        self.assertEqual(result["executedCount"], 1)
        self.assertGreater(
            result["selectedCount"],
            result["executedCount"],
        )

    def test_empty_check_set_is_rejected(self):
        from run_inquiry_continuity_summary_distortion_checks import (
            validate_checks,
        )

        with self.assertRaises(ValueError):
            validate_checks(())

    def test_build_result_requires_all_selected_checks(self):
        checks = configured_checks()
        result = build_result(
            checks,
            [{"name": checks[0].name, "exitCode": 0}],
            stopped_early=True,
        )
        self.assertEqual(result["result"], "failed")

    def test_save_result_is_exclusive_create(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "result.json"
            result = build_result(
                (),
                (),
                stopped_early=False,
            )
            save_result(path, result)
            written = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(written["schema"], result["schema"])
            with self.assertRaises(ValueError):
                save_result(path, result)


if __name__ == "__main__":
    unittest.main()
