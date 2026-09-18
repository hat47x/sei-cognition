#!/usr/bin/env python3

from __future__ import annotations

import copy
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from run_inquiry_continuity_summary_distortion_checks import (
    FIXTURE_IDS,
    STOP_LINE,
    build_contract_snapshot,
    build_result,
    configured_checks,
    run_checks,
    sanitized_environment,
    save_result,
    validate_result,
)


class SummaryDistortionLocalChecksTest(unittest.TestCase):
    def mechanics_result(self):
        def runner(command, *, cwd, env, timeout):
            return subprocess.CompletedProcess(
                command,
                0,
                stdout="ok\n",
                stderr="",
            )

        exit_code, result = run_checks(
            configured_checks(),
            runner=runner,
        )
        self.assertEqual(exit_code, 0)
        return result

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

    def test_contract_snapshot_binds_probe_mechanics_and_frozen_sources(self):
        snapshot = build_contract_snapshot()
        self.assertEqual(
            snapshot["probeSchema"],
            "sei.inquiry-continuity-summary-distortion-probe/v1",
        )
        self.assertEqual(len(snapshot["probeContentSha256"]), 64)
        self.assertEqual(
            tuple(item["fixtureId"] for item in snapshot["sourceFixtures"]),
            FIXTURE_IDS,
        )
        for source in snapshot["sourceFixtures"]:
            self.assertEqual(
                source["actualBlobSha1"],
                source["expectedBlobSha1"],
            )
        mechanics = {
            item["path"]: item["sha256"]
            for item in snapshot["mechanicsFiles"]
        }
        self.assertIn(
            "evaluation/personal-inquiry-decision/"
            "inquiry_continuity_summary_distortion_probe_v1.json",
            mechanics,
        )
        self.assertTrue(all(len(value) == 64 for value in mechanics.values()))

    def test_contract_snapshot_rejects_changed_frozen_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source_root = root / "evaluation/personal-inquiry-decision"
            source_root.mkdir(parents=True)
            repo_root = Path(__file__).resolve().parents[2]
            for relative in (
                "inquiry_continuity_summary_distortion_probe_v1.json",
                "inquiry_continuity_summary_distortion_probe.py",
                "inquiry_continuity_summary_distortion_evidence.py",
                "test_inquiry_continuity_summary_distortion_probe.py",
                "test_inquiry_continuity_summary_distortion_evidence.py",
                "run_inquiry_continuity_summary_distortion_checks.py",
                "test_run_inquiry_continuity_summary_distortion_checks.py",
                "inquiry_continuity_counterfactual_001.json",
                "inquiry_continuity_counterfactual_002.json",
                "inquiry_continuity_counterfactual_003.json",
            ):
                source = repo_root / "evaluation/personal-inquiry-decision" / relative
                target = source_root / relative
                target.write_bytes(source.read_bytes())
            changed = source_root / "inquiry_continuity_counterfactual_001.json"
            changed.write_text("{}\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                build_contract_snapshot(root)

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
            return subprocess.CompletedProcess(
                command,
                0,
                stdout="ok\n",
                stderr="",
            )

        exit_code, result = run_checks(
            configured_checks(),
            runner=runner,
            snapshot_builder=lambda: {"probeContentSha256": "a" * 64},
        )
        self.assertEqual(exit_code, 0)
        self.assertEqual(result["result"], "ok")
        self.assertEqual(result["failedCount"], 0)
        self.assertFalse(result["humanReviewObserved"])
        self.assertFalse(result["actualLongGapResumptionEstablished"])
        self.assertFalse(result["productValueEstablished"])
        self.assertFalse(result["stableRequirementAuthorized"])
        self.assertEqual(result["stopLine"], STOP_LINE)
        self.assertEqual(
            result["contractSnapshot"]["probeContentSha256"],
            "a" * 64,
        )
        first = result["executed"][0]
        expected_command = list(configured_checks()[0].command)
        expected_command[0] = "<python>"
        self.assertEqual(first["command"], expected_command)
        self.assertEqual(first["cwdRelativeToRepo"], ".")
        self.assertEqual(first["stdout"]["bytes"], 3)
        self.assertEqual(len(first["stdout"]["sha256"]), 64)
        self.assertEqual(first["stderr"]["bytes"], 0)

    def test_failure_is_preserved_without_claiming_unexecuted_pass(self):
        calls = 0

        def runner(command, *, cwd, env, timeout):
            nonlocal calls
            calls += 1
            return subprocess.CompletedProcess(
                command,
                7 if calls == 2 else 0,
                stdout=f"call-{calls}\n",
                stderr="failed\n" if calls == 2 else "",
            )

        exit_code, result = run_checks(
            configured_checks(),
            runner=runner,
            snapshot_builder=lambda: {"probeContentSha256": "a" * 64},
        )
        self.assertEqual(exit_code, 1)
        self.assertEqual(result["failedCount"], 1)
        self.assertEqual(
            result["executedCount"],
            result["selectedCount"],
        )
        failed = result["executed"][1]
        self.assertEqual(failed["exitCode"], 7)
        self.assertEqual(failed["stderr"]["bytes"], len("failed\n".encode("utf-8")))
        self.assertEqual(len(failed["stderr"]["sha256"]), 64)

    def test_launch_error_does_not_store_os_message_or_path(self):
        def runner(command, *, cwd, env, timeout):
            raise FileNotFoundError(
                2,
                "No such file or directory",
                "/host/private/bin/python",
            )

        exit_code, result = run_checks(
            configured_checks(),
            stop_on_failure=True,
            runner=runner,
            snapshot_builder=lambda: {"probeContentSha256": "a" * 64},
        )
        self.assertEqual(exit_code, 1)
        execution = result["executed"][0]
        self.assertEqual(execution["exitCode"], 127)
        self.assertEqual(
            execution["launchError"],
            {"type": "FileNotFoundError", "errno": 2},
        )
        serialized = json.dumps(execution)
        self.assertNotIn("/host/private", serialized)
        self.assertNotIn("No such file or directory", serialized)

    def test_stop_on_failure_marks_incomplete_run(self):
        def runner(command, *, cwd, env, timeout):
            return subprocess.CompletedProcess(
                command,
                1,
                stdout="",
                stderr="failed\n",
            )

        exit_code, result = run_checks(
            configured_checks(),
            stop_on_failure=True,
            runner=runner,
            snapshot_builder=lambda: {"probeContentSha256": "a" * 64},
        )
        self.assertEqual(exit_code, 1)
        self.assertTrue(result["stoppedEarly"])
        self.assertEqual(result["executedCount"], 1)
        self.assertGreater(
            result["selectedCount"],
            result["executedCount"],
        )

    def test_timeout_preserves_partial_output_digests(self):
        def runner(command, *, cwd, env, timeout):
            raise subprocess.TimeoutExpired(
                command,
                timeout,
                output=b"partial-out",
                stderr=b"partial-err",
            )

        exit_code, result = run_checks(
            configured_checks(),
            stop_on_failure=True,
            runner=runner,
            snapshot_builder=lambda: {"probeContentSha256": "a" * 64},
        )
        self.assertEqual(exit_code, 1)
        execution = result["executed"][0]
        self.assertTrue(execution["timedOut"])
        self.assertEqual(execution["exitCode"], 124)
        self.assertEqual(execution["stdout"]["bytes"], len(b"partial-out"))
        self.assertEqual(execution["stderr"]["bytes"], len(b"partial-err"))
        self.assertEqual(len(execution["stdout"]["sha256"]), 64)
        self.assertEqual(len(execution["stderr"]["sha256"]), 64)

    def test_empty_check_set_is_rejected(self):
        from run_inquiry_continuity_summary_distortion_checks import (
            validate_checks,
        )

        with self.assertRaises(ValueError):
            validate_checks(())

    def test_build_result_rejects_empty_check_set(self):
        with self.assertRaises(ValueError):
            build_result(
                (),
                (),
                stopped_early=False,
                contract_snapshot={"probeContentSha256": "a" * 64},
            )

    def test_check_cwd_must_stay_within_repository_root(self):
        from run_inquiry_continuity_summary_distortion_checks import (
            Check,
            validate_checks,
        )

        with tempfile.TemporaryDirectory() as tmp:
            outside = Path(tmp)
            with self.assertRaises(ValueError):
                validate_checks(
                    (
                        Check(
                            name="outside",
                            command=("python", "-V"),
                            cwd=outside,
                        ),
                    )
                )

    def test_absolute_command_outside_repo_is_rejected_before_execution(self):
        from run_inquiry_continuity_summary_distortion_checks import (
            Check,
            run_checks,
        )

        runner_called = False

        def runner(command, *, cwd, env, timeout):
            nonlocal runner_called
            runner_called = True
            raise AssertionError("runner must not be called")

        check = Check(
            name="outside-command",
            command=("/definitely/outside/repository/tool",),
            cwd=configured_checks()[0].cwd,
        )
        with self.assertRaises(ValueError):
            run_checks(
                (check,),
                runner=runner,
                snapshot_builder=lambda: {"probeContentSha256": "a" * 64},
            )
        self.assertFalse(runner_called)

    def test_build_result_requires_all_selected_checks(self):
        checks = configured_checks()
        result = build_result(
            checks,
            [{"name": checks[0].name, "exitCode": 0}],
            stopped_early=True,
            contract_snapshot={"probeContentSha256": "a" * 64},
        )
        self.assertEqual(result["result"], "failed")

    def test_validate_result_rejects_tampered_stopline_and_digest(self):
        result = self.mechanics_result()

        tampered = copy.deepcopy(result)
        tampered["stopLine"] = "PASS"
        with self.assertRaises(ValueError):
            validate_result(tampered)

        tampered = copy.deepcopy(result)
        tampered["executed"][0]["stdout"]["sha256"] = "not-a-digest"
        with self.assertRaises(ValueError):
            validate_result(tampered)

    def test_validate_result_rejects_absolute_command_and_count_mismatch(self):
        result = self.mechanics_result()

        tampered = copy.deepcopy(result)
        tampered["executed"][0]["command"][0] = "/host/private/python"
        with self.assertRaises(ValueError):
            validate_result(tampered)

        tampered = copy.deepcopy(result)
        tampered["executedCount"] += 1
        with self.assertRaises(ValueError):
            validate_result(tampered)

    def test_validate_result_rejects_shape_and_contract_identity_tampering(self):
        result = self.mechanics_result()

        tampered = copy.deepcopy(result)
        tampered["executed"][0]["unexpected"] = True
        with self.assertRaises(ValueError):
            validate_result(tampered)

        tampered = copy.deepcopy(result)
        tampered["contractSnapshot"]["mechanicsFiles"][0]["path"] = "other.py"
        with self.assertRaises(ValueError):
            validate_result(tampered)

        tampered = copy.deepcopy(result)
        tampered["contractSnapshot"]["sourceFixtures"][0]["fixtureId"] = "other"
        with self.assertRaises(ValueError):
            validate_result(tampered)

        tampered = copy.deepcopy(result)
        tampered["executed"][0]["command"][1] = "../../outside.py"
        with self.assertRaises(ValueError):
            validate_result(tampered)

    def test_save_result_is_exclusive_create(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "result.json"
            result = self.mechanics_result()
            save_result(path, result)
            written = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(written["schema"], result["schema"])
            with self.assertRaises(ValueError):
                save_result(path, result)


if __name__ == "__main__":
    unittest.main()
