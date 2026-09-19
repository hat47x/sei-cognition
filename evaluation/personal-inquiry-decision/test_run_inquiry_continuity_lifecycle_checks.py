#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from run_inquiry_continuity_lifecycle_checks import (
    STOP_LINE,
    build_contract_snapshot,
    configured_checks,
    run_checks,
    sanitized_environment,
    save_result,
    validate_checks,
    validate_result,
)


class LifecycleLocalChecksTest(unittest.TestCase):
    def mechanics_result(self):
        def fake(command, *, cwd, env, timeout):
            return subprocess.CompletedProcess(
                command,
                0,
                stdout="ok\n",
                stderr="",
            )
        code, result = run_checks(
            configured_checks(),
            runner=fake,
        )
        self.assertEqual(code, 0)
        return result

    def test_configured_checks_cover_units_and_validate(self):
        self.assertEqual(
            [check.name for check in configured_checks()],
            [
                "lifecycle-probe-tests",
                "lifecycle-evidence-tests",
                "lifecycle-local-runner-tests",
                "lifecycle-probe-validate",
            ],
        )

    def test_contract_snapshot_binds_probe_and_mechanics(self):
        snapshot = build_contract_snapshot()
        self.assertEqual(
            snapshot["probeSchema"],
            "sei.inquiry-continuity-lifecycle-probe/v2",
        )
        self.assertEqual(
            len(snapshot["probeContentSha256"]),
            64,
        )
        self.assertEqual(
            [item["path"] for item in snapshot["mechanicsFiles"]],
            list(
                __import__(
                    "run_inquiry_continuity_lifecycle_checks"
                ).MECHANICS_PATHS
            ),
        )

    def test_environment_is_sanitized(self):
        env = sanitized_environment(
            {
                "PATH": "/bin",
                "SEI_TOKEN": "secret",
                "SOZA_SECRET": "secret",
                "KJ_ATLAS_DB": "secret",
                "OPENAI_API_KEY": "secret",
                "OPENROUTER_API_KEY": "secret",
                "PYTHONPATH": "/tmp/injected",
            }
        )
        self.assertEqual(env["PATH"], "/bin")
        for key in (
            "SEI_TOKEN",
            "SOZA_SECRET",
            "KJ_ATLAS_DB",
            "OPENAI_API_KEY",
            "OPENROUTER_API_KEY",
            "PYTHONPATH",
        ):
            self.assertNotIn(key, env)
        self.assertEqual(
            env["PYTHONDONTWRITEBYTECODE"],
            "1",
        )

    def test_pass_is_mechanics_only(self):
        result = self.mechanics_result()
        self.assertEqual(result["result"], "ok")
        self.assertFalse(result["humanReviewObserved"])
        self.assertFalse(result["productValueEstablished"])
        self.assertFalse(result["universalStatusAuthorized"])
        self.assertFalse(result["stableRequirementAuthorized"])
        self.assertEqual(result["stopLine"], STOP_LINE)

    def test_failure_stop_and_launch_error_are_preserved(self):
        calls = 0
        def failing(command, *, cwd, env, timeout):
            nonlocal calls
            calls += 1
            if calls == 2:
                return subprocess.CompletedProcess(
                    command,
                    7,
                    stdout="",
                    stderr="failed\n",
                )
            return subprocess.CompletedProcess(
                command,
                0,
                stdout="ok\n",
                stderr="",
            )
        code, result = run_checks(
            configured_checks(),
            runner=failing,
            stop_on_failure=True,
            snapshot_builder=lambda: {
                "probeContentSha256": "a" * 64
            },
        )
        self.assertEqual(code, 1)
        self.assertTrue(result["stoppedEarly"])
        self.assertEqual(result["failedCount"], 1)

        def missing(command, *, cwd, env, timeout):
            raise FileNotFoundError(
                2,
                "No such file",
                "/host/private/python",
            )
        code, result = run_checks(
            configured_checks(),
            runner=missing,
            stop_on_failure=True,
            snapshot_builder=lambda: {
                "probeContentSha256": "a" * 64
            },
        )
        self.assertEqual(code, 1)
        serialized = json.dumps(result["executed"][0])
        self.assertNotIn("/host/private", serialized)
        self.assertNotIn("No such file", serialized)

    def test_empty_checks_and_result_tampering_are_rejected(self):
        with self.assertRaises(ValueError):
            validate_checks(())

        result = self.mechanics_result()
        changed = copy.deepcopy(result)
        changed["stopLine"] = "PASS"
        with self.assertRaises(ValueError):
            validate_result(changed)

        changed = copy.deepcopy(result)
        changed["executed"][0]["stdout"]["sha256"] = "bad"
        with self.assertRaises(ValueError):
            validate_result(changed)

        changed = copy.deepcopy(result)
        changed["contractSnapshot"]["mechanicsFiles"][0][
            "path"
        ] = "../../outside"
        with self.assertRaises(ValueError):
            validate_result(changed)

        changed = copy.deepcopy(result)
        changed["executed"][0]["cwdRelativeToRepo"] = 7
        with self.assertRaises(ValueError):
            validate_result(changed)

        changed = copy.deepcopy(result)
        changed["contractSnapshot"]["mechanicsFiles"][0][
            "path"
        ] = 7
        with self.assertRaises(ValueError):
            validate_result(changed)

    def test_validate_result_rejects_noncanonical_execution_contract(self):
        result = self.mechanics_result()

        changed = copy.deepcopy(result)
        changed["selected"][0] = "other-check"
        changed["executed"][0]["name"] = "other-check"
        with self.assertRaises(ValueError):
            validate_result(changed)

        changed = copy.deepcopy(result)
        changed["executed"][0]["command"][1] = (
            "evaluation/personal-inquiry-decision/"
            "inquiry_continuity_lifecycle_evidence.py"
        )
        with self.assertRaises(ValueError):
            validate_result(changed)

        changed = copy.deepcopy(result)
        changed["executed"][0]["cwdRelativeToRepo"] = "evaluation"
        with self.assertRaises(ValueError):
            validate_result(changed)

    def test_validate_result_rejects_execution_state_tampering(self):
        result = self.mechanics_result()

        changed = copy.deepcopy(result)
        changed["executed"] = []
        changed["executedCount"] = 0
        changed["failedCount"] = 0
        changed["result"] = "failed"
        changed["stoppedEarly"] = True
        with self.assertRaises(ValueError):
            validate_result(changed)

        changed = copy.deepcopy(result)
        changed["executed"][1]["timeoutSeconds"] += 1
        with self.assertRaises(ValueError):
            validate_result(changed)

        changed = copy.deepcopy(result)
        changed["executed"] = changed["executed"][:2]
        changed["executedCount"] = 2
        changed["failedCount"] = 0
        changed["result"] = "failed"
        changed["stoppedEarly"] = True
        with self.assertRaises(ValueError):
            validate_result(changed)

    def test_validate_result_rejects_failure_metadata_and_snapshot_tampering(self):
        result = self.mechanics_result()

        changed = copy.deepcopy(result)
        changed["executed"][0]["timedOut"] = True
        with self.assertRaises(ValueError):
            validate_result(changed)

        def missing(command, *, cwd, env, timeout):
            raise FileNotFoundError(2, "No such file", "/private/tool")

        code, failed = run_checks(
            configured_checks(),
            runner=missing,
            stop_on_failure=True,
        )
        self.assertEqual(code, 1)
        changed = copy.deepcopy(failed)
        changed["executed"][0]["stdout"] = {
            "sha256": "0" * 64,
            "bytes": 1,
        }
        with self.assertRaises(ValueError):
            validate_result(changed)

        changed = copy.deepcopy(result)
        changed["contractSnapshot"]["probeContentSha256"] = "0" * 64
        with self.assertRaises(ValueError):
            validate_result(changed)

    def test_save_result_is_exclusive(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "result.json"
            result = self.mechanics_result()
            save_result(path, result)
            original = path.read_bytes()
            with self.assertRaises(ValueError):
                save_result(path, result)
            self.assertEqual(
                path.read_bytes(),
                original,
            )


if __name__ == "__main__":
    unittest.main()
