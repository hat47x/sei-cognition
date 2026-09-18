#!/usr/bin/env python3

from __future__ import annotations

import json
import subprocess
import unittest
from contextlib import redirect_stderr
from io import StringIO

from run_live_provider_failure_probe import (
    EXPECTED_TESTS,
    LIVE_FLAG,
    STOP_LINE,
    build_parser,
    evaluate_execution,
    live_command,
    main,
    run_live_probe,
    sanitized_live_environment,
)


def go_event(action: str, test: str) -> str:
    return json.dumps(
        {
            "Time": "2026-09-10T00:00:00Z",
            "Action": action,
            "Package": "github.com/hat47x/sei-cognition/runtime/go/liveintegration",
            "Test": test,
        }
    )


def passing_output() -> str:
    return "\n".join(go_event("pass", test) for test in EXPECTED_TESTS) + "\n"


class LiveProviderFailureRunnerTest(unittest.TestCase):
    def test_parser_labels_current_issue(self) -> None:\n        parser = build_parser()\n        self.assertIn("ISSUE-000076", parser.description or "")\n        self.assertNotIn("ISSUE-000072", parser.description or "")\n\n    def test_live_command_targets_only_expected_negative_probes(self) -> None:
        command = live_command()
        self.assertEqual(command[:3], ("go", "test", "./liveintegration"))
        pattern = command[command.index("-run") + 1]
        for test in EXPECTED_TESTS:
            self.assertIn(test, pattern)
        self.assertIn("-count=1", command)
        self.assertIn("-json", command)

    def test_environment_is_live_opt_in_but_does_not_inherit_credentials(self) -> None:
        environment = sanitized_live_environment(
            {
                "PATH": "/bin",
                "SEI_E3B_FAILURE_LIVE": "old",
                "SEI_LIVE_PROVIDER_TOKEN": "real-secret-token",
                "SOZA_LIVE_PROVIDER_TOKEN": "legacy-secret-token",
                "GITHUB_TOKEN": "github-secret",
                "GH_TOKEN": "gh-secret",
                "KJ_ATLAS_DATABASE_URL": "secret-db",
                "OPENAI_API_KEY": "openai-secret",
                "GOTOOLCHAIN": "auto",
                "GOWORK": "/tmp/injected.work",
                "GOENV": "/tmp/injected-goenv",
                "GOFLAGS": "-mod=mod",
                "GOOS": "windows",
                "GOARCH": "arm64",
                "CGO_ENABLED": "1",
            }
        )
        self.assertEqual(environment["PATH"], "/bin")
        self.assertEqual(environment[LIVE_FLAG], "1")
        for removed in (
            "SEI_LIVE_PROVIDER_TOKEN",
            "SOZA_LIVE_PROVIDER_TOKEN",
            "GITHUB_TOKEN",
            "GH_TOKEN",
            "KJ_ATLAS_DATABASE_URL",
            "OPENAI_API_KEY",
            "GOFLAGS",
            "GOOS",
            "GOARCH",
            "CGO_ENABLED",
        ):
            self.assertNotIn(removed, environment)
        self.assertEqual(environment["GOTOOLCHAIN"], "local")
        self.assertEqual(environment["GOWORK"], "off")
        self.assertEqual(environment["GOENV"], "off")
        serialized = json.dumps(environment, sort_keys=True)
        self.assertNotIn("real-secret-token", serialized)
        self.assertNotIn("legacy-secret-token", serialized)

    def test_two_exact_pass_events_establish_actual_provider_failure_evidence(self) -> None:
        result = evaluate_execution(0, passing_output())
        self.assertEqual(result["result"], "ok")
        self.assertTrue(result["actualProviderFailureEvidence"])
        self.assertFalse(result["operationalEvidence"])
        self.assertEqual(result["missingTests"], [])
        self.assertEqual(result["nonPassTests"], {})
        self.assertEqual(result["stopLine"], STOP_LINE)

    def test_zero_exit_without_both_expected_tests_is_failure(self) -> None:
        output = go_event("pass", EXPECTED_TESTS[0]) + "\n"
        result = evaluate_execution(0, output)
        self.assertEqual(result["result"], "failed")
        self.assertFalse(result["actualProviderFailureEvidence"])
        self.assertEqual(result["missingTests"], [EXPECTED_TESTS[1]])

    def test_skip_or_fail_is_not_actual_provider_failure_evidence(self) -> None:
        output = "\n".join(
            (
                go_event("pass", EXPECTED_TESTS[0]),
                go_event("skip", EXPECTED_TESTS[1]),
            )
        )
        result = evaluate_execution(0, output)
        self.assertEqual(result["result"], "failed")
        self.assertEqual(result["nonPassTests"], {EXPECTED_TESTS[1]: "skip"})
        self.assertFalse(result["actualProviderFailureEvidence"])

    def test_nonzero_command_exit_is_failure_even_when_tests_report_pass(self) -> None:
        result = evaluate_execution(1, passing_output())
        self.assertEqual(result["result"], "failed")
        self.assertFalse(result["actualProviderFailureEvidence"])

    def test_malformed_go_json_is_failure(self) -> None:
        result = evaluate_execution(0, passing_output() + "not-json\n")
        self.assertEqual(result["result"], "failed")
        self.assertTrue(result["parseErrors"])

    def test_run_live_probe_marks_timeout_as_failure(self) -> None:
        def runner(command, *, cwd, env, timeout):
            raise subprocess.TimeoutExpired(command, timeout)

        exit_code, result = run_live_probe(timeout_seconds=3, runner=runner)
        self.assertEqual(exit_code, 1)
        self.assertEqual(result["commandExitCode"], 124)
        self.assertTrue(result["timedOut"])
        self.assertFalse(result["actualProviderFailureEvidence"])

    def test_run_live_probe_accepts_only_complete_go_test_evidence(self) -> None:
        def runner(command, *, cwd, env, timeout):
            self.assertEqual(env[LIVE_FLAG], "1")
            self.assertNotIn("SEI_LIVE_PROVIDER_TOKEN", env)
            self.assertNotIn("SOZA_LIVE_PROVIDER_TOKEN", env)
            return subprocess.CompletedProcess(
                command,
                0,
                stdout=passing_output(),
                stderr="",
            )

        exit_code, result = run_live_probe(runner=runner)
        self.assertEqual(exit_code, 0)
        self.assertTrue(result["actualProviderFailureEvidence"])

    def test_main_requires_explicit_allow_live_before_execution(self) -> None:
        stderr = StringIO()
        with redirect_stderr(stderr), self.assertRaises(SystemExit) as caught:
            main([])
        self.assertEqual(caught.exception.code, 2)
        self.assertIn("--allow-live", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
