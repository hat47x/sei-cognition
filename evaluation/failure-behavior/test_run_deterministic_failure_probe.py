#!/usr/bin/env python3

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from run_deterministic_failure_probe import REPORT_SCHEMA, TEST_SECRET, main, run_probe


class DeterministicFailureProbeTest(unittest.TestCase):
    def test_probe_covers_all_catalog_cases(self) -> None:
        report = run_probe()
        self.assertEqual(report["schema"], REPORT_SCHEMA)
        self.assertEqual(report["scope"], "evaluation-only")
        self.assertEqual(report["authority"], "non-universal")
        self.assertEqual({case["caseId"] for case in report["cases"]}, {f"FB-C{i:02d}" for i in range(1, 10)})

    def test_probe_report_is_deterministic(self) -> None:
        self.assertEqual(run_probe(), run_probe())

    def test_report_does_not_persist_secret_or_provider_policy_fields(self) -> None:
        report = run_probe()
        serialized = json.dumps(report, sort_keys=True)
        self.assertNotIn(TEST_SECRET, serialized)
        for forbidden in (
            "httpStatus",
            "providerErrorCode",
            "retryDelaySeconds",
            "retrySchedule",
            "accessToken",
            "apiKey",
            "password",
            "secret",
        ):
            self.assertNotIn(forbidden, serialized)

    def test_semantic_state_remains_unchanged_for_every_case(self) -> None:
        report = run_probe()
        self.assertTrue(all(case["semanticStateChanged"] is False for case in report["cases"]))

    def test_identity_integrity_failure_is_fail_closed(self) -> None:
        report = run_probe()
        case = next(case for case in report["cases"] if case["caseId"] == "FB-C05")
        self.assertTrue(case["failClosed"])
        self.assertEqual(case["attempts"][0]["outcome"], "failure")
        self.assertFalse(case["attempts"][0]["executionStarted"])

    def test_retry_preserves_initial_failure_as_separate_attempt(self) -> None:
        report = run_probe()
        case = next(case for case in report["cases"] if case["caseId"] == "FB-C09")
        self.assertTrue(case["initialFailurePreserved"])
        self.assertTrue(case["retryOutcomeSeparate"])
        self.assertEqual([attempt["outcome"] for attempt in case["attempts"]], ["failure", "success"])
        self.assertEqual([attempt["attempt"] for attempt in case["attempts"]], [1, 2])

    def test_cli_writes_same_report_as_library_call(self) -> None:
        expected = run_probe()
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "report.json"
            self.assertEqual(main([str(path)]), 0)
            actual = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
