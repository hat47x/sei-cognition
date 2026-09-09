#!/usr/bin/env python3

from __future__ import annotations

import subprocess
import unittest

from run_local_checks import (
    STOP_LINE,
    build_result,
    configured_checks,
    run_checks,
    sanitized_environment,
)


class FailureBehaviorLocalCheckRunnerTest(unittest.TestCase):
    def test_configured_checks_cover_python_and_go_failure_boundaries(self) -> None:
        checks = configured_checks()
        self.assertEqual(
            [check.name for check in checks],
            [
                "case-catalog-validator-tests",
                "deterministic-probe-tests",
                "local-runner-tests",
                "live-provider-runner-tests",
                "requirement-audit-tests",
                "scoped-go-evidence-tests",
                "actual-provider-service-observation-tests",
                "provider-adapter-go-tests",
                "live-provider-integration-go-tests",
            ],
        )
        self.assertEqual(checks[3].command[-1], "test_run_live_provider_failure_probe.py")
        self.assertEqual(checks[4].command[-1], "test_requirement_audit.py")
        self.assertEqual(
            checks[5].command[-1], "test_scoped_go_failure_execution_evidence.py"
        )
        self.assertEqual(
            checks[6].command[-1], "test_actual_provider_missing_revision_observation.py"
        )
        self.assertEqual(checks[-2].command, ("go", "test", "./provideradapter"))
        self.assertEqual(checks[-1].command, ("go", "test", "./liveintegration"))

    def test_sanitized_environment_removes_live_probe_and_secret_inputs(self) -> None:
        environment = sanitized_environment(
            {
                "PATH": "/bin",
                "SOZA_E3B_LIVE": "1",
                "SOZA_E3B_FAILURE_LIVE": "1",
                "SOZA_LIVE_PROVIDER_TOKEN": "secret-token",
                "KJ_ATLAS_DATABASE_URL": "secret-db",
                "OLLAMA_HOST": "127.0.0.1:11434",
                "OPENAI_API_KEY": "secret",
                "PYTHONPATH": "/tmp/injected",
            }
        )
        self.assertEqual(environment["PATH"], "/bin")
        for removed in (
            "SOZA_E3B_LIVE",
            "SOZA_E3B_FAILURE_LIVE",
            "SOZA_LIVE_PROVIDER_TOKEN",
            "KJ_ATLAS_DATABASE_URL",
            "OLLAMA_HOST",
            "OPENAI_API_KEY",
            "PYTHONPATH",
        ):
            self.assertNotIn(removed, environment)
        self.assertEqual(environment["PYTHONDONTWRITEBYTECODE"], "1")
        self.assertEqual(environment["PYTHONNOUSERSITE"], "1")

    def test_all_pass_returns_fixture_scoped_success(self) -> None:
        def runner(command, *, cwd, env, timeout):
            return subprocess.CompletedProcess(command, 0)

        exit_code, result = run_checks(configured_checks(), runner=runner)
        self.assertEqual(exit_code, 0)
        self.assertEqual(result["result"], "ok")
        self.assertEqual(result["failedCount"], 0)
        self.assertFalse(result["actualProviderFailureEvidence"])
        self.assertFalse(result["actualDeploymentFailureEvidence"])
        self.assertFalse(result["operationalEvidence"])
        self.assertEqual(result["stopLine"], STOP_LINE)

    def test_failure_is_preserved_and_overall_result_fails(self) -> None:
        calls = 0

        def runner(command, *, cwd, env, timeout):
            nonlocal calls
            calls += 1
            return subprocess.CompletedProcess(command, 7 if calls == 2 else 0)

        exit_code, result = run_checks(configured_checks(), runner=runner)
        self.assertEqual(exit_code, 1)
        self.assertEqual(result["result"], "failed")
        self.assertEqual(result["failedCount"], 1)
        self.assertEqual(result["executed"][1]["exitCode"], 7)
        self.assertEqual(result["executedCount"], result["selectedCount"])

    def test_stop_on_failure_does_not_claim_unexecuted_checks(self) -> None:
        def runner(command, *, cwd, env, timeout):
            return subprocess.CompletedProcess(command, 1)

        exit_code, result = run_checks(
            configured_checks(), stop_on_failure=True, runner=runner
        )
        self.assertEqual(exit_code, 1)
        self.assertTrue(result["stoppedEarly"])
        self.assertEqual(result["executedCount"], 1)
        self.assertGreater(result["selectedCount"], result["executedCount"])

    def test_build_result_requires_all_selected_checks_to_execute(self) -> None:
        checks = configured_checks()
        result = build_result(
            checks,
            [{"name": checks[0].name, "exitCode": 0}],
            stopped_early=True,
        )
        self.assertEqual(result["result"], "failed")


if __name__ == "__main__":
    unittest.main()
