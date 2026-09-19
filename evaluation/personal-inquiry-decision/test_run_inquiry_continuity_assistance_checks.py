#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from run_inquiry_continuity_assistance_checks import (
    FIXTURE_IDS,
    STOP_LINE,
    build_contract_snapshot,
    build_result,
    configured_checks,
    run_checks,
    sanitized_environment,
    save_result,
    validate_checks,
    validate_result,
)


class AssistanceLocalChecksTest(unittest.TestCase):
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

    def test_configured_checks_cover_units_and_validate(self):
        checks = configured_checks()
        self.assertEqual(
            [check.name for check in checks],
            [
                "assistance-probe-tests",
                "assistance-evidence-tests",
                "assistance-local-runner-tests",
                "assistance-probe-validate",
            ],
        )
        self.assertEqual(
            checks[3].command[-1],
            "validate",
        )

    def test_contract_snapshot_binds_probe_manifest_and_sources(self):
        snapshot = build_contract_snapshot()
        self.assertEqual(
            snapshot["probeSchema"],
            "sei.inquiry-continuity-assistance-probe/v2",
        )
        self.assertEqual(
            len(snapshot["probeContentSha256"]),
            64,
        )
        self.assertEqual(
            snapshot["sourceSet"]["expectedBlobSha1"],
            snapshot["sourceSet"]["actualBlobSha1"],
        )
        self.assertEqual(
            tuple(
                item["fixtureId"]
                for item in snapshot["sourceFixtures"]
            ),
            FIXTURE_IDS,
        )
        for source in snapshot["sourceFixtures"]:
            self.assertEqual(
                source["expectedBlobSha1"],
                source["actualBlobSha1"],
            )

    def test_contract_snapshot_rejects_changed_frozen_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target_dir = (
                root
                / "evaluation/personal-inquiry-decision"
            )
            target_dir.mkdir(parents=True)
            repo_root = Path(__file__).resolve().parents[2]
            relative_names = (
                "inquiry_continuity_assistance_probe_v1.json",
                "inquiry_continuity_assistance_probe.py",
                "inquiry_continuity_assistance_evidence.py",
                "test_inquiry_continuity_assistance_probe.py",
                "test_inquiry_continuity_assistance_evidence.py",
                "run_inquiry_continuity_assistance_checks.py",
                "test_run_inquiry_continuity_assistance_checks.py",
                "inquiry_continuity_counterfactual_matched_set_v1.json",
                "inquiry_continuity_counterfactual_001.json",
                "inquiry_continuity_counterfactual_002.json",
                "inquiry_continuity_counterfactual_003.json",
            )
            for name in relative_names:
                source = (
                    repo_root
                    / "evaluation/personal-inquiry-decision"
                    / name
                )
                (target_dir / name).write_bytes(
                    source.read_bytes()
                )
            changed = (
                target_dir
                / "inquiry_continuity_counterfactual_001.json"
            )
            changed.write_text("{}\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                build_contract_snapshot(root)

    def test_contract_snapshot_rejects_source_path_escape(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target_dir = (
                root
                / "evaluation/personal-inquiry-decision"
            )
            target_dir.mkdir(parents=True)
            repo_root = Path(__file__).resolve().parents[2]
            probe_source = (
                repo_root
                / "evaluation/personal-inquiry-decision/"
                "inquiry_continuity_assistance_probe_v1.json"
            )
            probe = json.loads(
                probe_source.read_text(encoding="utf-8")
            )
            probe["source_set"]["path"] = "../../outside.json"
            (target_dir / "inquiry_continuity_assistance_probe_v1.json").write_text(
                json.dumps(probe),
                encoding="utf-8",
            )
            for name in (
                "inquiry_continuity_assistance_probe.py",
                "inquiry_continuity_assistance_evidence.py",
                "test_inquiry_continuity_assistance_probe.py",
                "test_inquiry_continuity_assistance_evidence.py",
                "run_inquiry_continuity_assistance_checks.py",
                "test_run_inquiry_continuity_assistance_checks.py",
            ):
                source = (
                    repo_root
                    / "evaluation/personal-inquiry-decision"
                    / name
                )
                (target_dir / name).write_bytes(
                    source.read_bytes()
                )
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
                "OPENROUTER_API_KEY": "secret",
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
            "OPENROUTER_API_KEY",
            "PYTHONPATH",
            "PYTHONHOME",
        ):
            self.assertNotIn(removed, environment)
        self.assertEqual(
            environment["PYTHONDONTWRITEBYTECODE"],
            "1",
        )
        self.assertEqual(
            environment["PYTHONNOUSERSITE"],
            "1",
        )

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
            snapshot_builder=lambda: {
                "probeContentSha256": "a" * 64
            },
        )
        self.assertEqual(exit_code, 0)
        self.assertEqual(result["result"], "ok")
        self.assertFalse(result["humanReviewObserved"])
        self.assertFalse(
            result["actualLongGapComparisonEstablished"]
        )
        self.assertFalse(
            result["productValueEstablished"]
        )
        self.assertFalse(
            result["stableRequirementAuthorized"]
        )
        self.assertEqual(result["stopLine"], STOP_LINE)
        self.assertEqual(
            result["executed"][0]["command"][0],
            "<python>",
        )

    def test_failure_and_stop_on_failure_are_preserved(self):
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
            stop_on_failure=True,
            runner=runner,
            snapshot_builder=lambda: {
                "probeContentSha256": "a" * 64
            },
        )
        self.assertEqual(exit_code, 1)
        self.assertEqual(result["failedCount"], 1)
        self.assertTrue(result["stoppedEarly"])
        self.assertEqual(result["executedCount"], 2)
        self.assertLess(
            result["executedCount"],
            result["selectedCount"],
        )

    def test_launch_error_is_sanitized(self):
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
            snapshot_builder=lambda: {
                "probeContentSha256": "a" * 64
            },
        )
        self.assertEqual(exit_code, 1)
        execution = result["executed"][0]
        self.assertEqual(
            execution["launchError"],
            {
                "type": "FileNotFoundError",
                "errno": 2,
            },
        )
        serialized = json.dumps(execution)
        self.assertNotIn("/host/private", serialized)
        self.assertNotIn(
            "No such file or directory",
            serialized,
        )

    def test_empty_check_set_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_checks(())
        with self.assertRaises(ValueError):
            build_result(
                (),
                (),
                stopped_early=False,
                contract_snapshot={
                    "probeContentSha256": "a" * 64
                },
            )

    def test_validate_result_rejects_tampering(self):
        result = self.mechanics_result()

        tampered = copy.deepcopy(result)
        tampered["stopLine"] = "PASS"
        with self.assertRaises(ValueError):
            validate_result(tampered)

        tampered = copy.deepcopy(result)
        tampered["executed"][0]["stdout"][
            "sha256"
        ] = "not-a-digest"
        with self.assertRaises(ValueError):
            validate_result(tampered)

        tampered = copy.deepcopy(result)
        tampered["contractSnapshot"]["sourceSet"][
            "actualBlobSha1"
        ] = "0" * 40
        with self.assertRaises(ValueError):
            validate_result(tampered)

        tampered = copy.deepcopy(result)
        tampered["executed"][0]["command"][0] = (
            "/host/private/python"
        )
        with self.assertRaises(ValueError):
            validate_result(tampered)

    def test_save_result_is_exclusive_create(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "result.json"
            result = self.mechanics_result()
            save_result(path, result)
            written = json.loads(
                path.read_text(encoding="utf-8")
            )
            self.assertEqual(
                written["schema"],
                result["schema"],
            )
            with self.assertRaises(ValueError):
                save_result(path, result)


if __name__ == "__main__":
    unittest.main()
