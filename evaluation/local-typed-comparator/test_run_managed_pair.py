import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "run_managed_pair_tested", HERE / "run_managed_pair.py"
)
mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = mod
SPEC.loader.exec_module(mod)

SHA = "1" * 40


def write_json(path: Path, value):
    path.write_text(
        json.dumps(value, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )


class FakeRunner:
    def __init__(
        self,
        fail_stage=None,
        report_sha=SHA,
        decision="pass",
        bad_decision_binding=None,
        preflight_live=False,
    ):
        self.calls = []
        self.fail_stage = fail_stage
        self.report_sha = report_sha
        self.decision = decision
        self.bad_decision_binding = bad_decision_binding
        self.preflight_live = preflight_live

    def __call__(self, command, *, cwd, check):
        self.calls.append((command, cwd, check))
        script = Path(command[1]).name
        stage = {
            "preflight_managed_pair.py": "preflight",
            "capture_reference_l0.py": "reference",
            "capture_papaya_l0.py": "papaya",
            "compare_papaya_reference_numeric.py": "comparison",
            "evaluate_papaya_numeric_parity.py": "decision",
        }[script]
        if stage == self.fail_stage:
            return subprocess.CompletedProcess(command, 2)

        output = Path(command[command.index("--output") + 1])
        root = output.parent
        if stage == "preflight":
            write_json(
                output,
                {
                    "schema": mod.PREFLIGHT_SCHEMA,
                    "status": "ready",
                    "source": {"git_sha": SHA},
                    "scope": {
                        "all_required_inputs_verified": True,
                        "model_weights_loaded": self.preflight_live,
                        "live_reference_inference": False,
                        "live_papaya_inference": False,
                        "numeric_difference_observed": False,
                        "numeric_parity_decision_observed": False,
                        "task_quality": False,
                        "calibration_validity": False,
                        "shipping_decision": False,
                    },
                },
            )
        elif stage == "reference":
            write_json(
                output,
                {
                    "schema": mod.REFERENCE_SCHEMA,
                    "status": "complete",
                    "source": {"git_sha": SHA},
                },
            )
        elif stage == "papaya":
            write_json(
                output,
                {
                    "schema": mod.PAPAYA_SCHEMA,
                    "status": "complete",
                    "source": {"git_sha": SHA},
                },
            )
        elif stage == "comparison":
            write_json(
                output,
                {
                    "schema": mod.REPORT_SCHEMA,
                    "inputs": {"same_sei_source_git_sha": self.report_sha},
                    "scope": {
                        "numeric_parity_threshold_defined": False,
                        "numeric_parity_decision": False,
                    },
                },
            )
        else:
            report_sha = mod._sha256_file(root / mod.REPORT_FILE)
            reference_sha = mod._sha256_file(root / mod.REFERENCE_FILE)
            papaya_sha = mod._sha256_file(root / mod.PAPAYA_FILE)
            bindings = {
                "sha256": report_sha,
                "same_sei_source_git_sha": SHA,
                "reference_artifact_sha256": reference_sha,
                "papaya_artifact_sha256": papaya_sha,
            }
            if self.bad_decision_binding is not None:
                bindings[self.bad_decision_binding] = "0" * (
                    40
                    if self.bad_decision_binding == "same_sei_source_git_sha"
                    else 64
                )
            passed = self.decision == "pass"
            write_json(
                output,
                {
                    "schema": mod.DECISION_SCHEMA,
                    "decision": self.decision,
                    "failures": (
                        []
                        if passed
                        else [{"metric": "probability_max_abs_delta"}]
                    ),
                    "numeric_report": bindings,
                    "scope": {
                        "bounded_numeric_parity_on_preregistered_surface": passed,
                        "task_quality": False,
                        "calibration_validity": False,
                        "cross_runtime_performance_comparison": False,
                        "jev_provider_identity_equivalence": False,
                        "reference_provider_promotion": False,
                        "shipping_decision": False,
                    },
                },
            )
        return subprocess.CompletedProcess(command, 0)


class ManagedPairTest(unittest.TestCase):
    def _commands(self, root, output):
        commands = mod.build_commands(
            python_executable="python3",
            here=root / "scripts",
            source_sha=SHA,
            sei_source_dir=root / "sei",
            reference_model_dir=root / "reference-model",
            laya_runtime_wheel=root / "laya.whl",
            papaya_source_dir=root / "papaya-source",
            papaya_overlay_dir=root / "papaya-overlay",
            llama_binary=root / "llama-server",
            output_dir=output,
            run_id="r1",
            threads=4,
            reference_startup_timeout=300.0,
            papaya_startup_timeout=240.0,
        )
        return tuple(
            zip(
                ("preflight", "reference", "papaya", "comparison", "decision"),
                commands,
            )
        )

    def test_commands_bind_same_source_and_report_chain(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            out = root / "evidence"
            commands = self._commands(root, out)
            pre = commands[0][1]
            ref = commands[1][1]
            pap = commands[2][1]
            cmp = commands[3][1]
            dec = commands[4][1]
            self.assertEqual(pre[pre.index("--source-git-sha") + 1], SHA)
            self.assertEqual(ref[ref.index("--source-git-sha") + 1], SHA)
            self.assertEqual(pap[pap.index("--source-git-sha") + 1], SHA)
            self.assertIn(str(out / mod.PREFLIGHT_FILE), pre)
            self.assertIn(str(out / mod.REFERENCE_FILE), cmp)
            self.assertIn(str(out / mod.PAPAYA_FILE), cmp)
            self.assertIn(str(out / mod.REPORT_FILE), dec)

    def test_preflight_failure_stops_before_model_load(self):
        self._assert_stage_failure("preflight", 1)

    def test_reference_failure_is_fail_fast(self):
        self._assert_stage_failure("reference", 2)

    def test_papaya_failure_stops_before_comparison(self):
        self._assert_stage_failure("papaya", 3)

    def test_comparison_failure_stops_before_decision(self):
        self._assert_stage_failure("comparison", 4)

    def _assert_stage_failure(self, stage, expected_calls):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            out = root / "evidence"
            out.mkdir()
            runner = FakeRunner(fail_stage=stage)
            with self.assertRaises(mod.ManagedPairError):
                mod.execute_pair(
                    source_sha=SHA,
                    output_dir=out,
                    commands=self._commands(root, out),
                    run_id="r1",
                    cwd=root,
                    runner=runner,
                )
            self.assertEqual(len(runner.calls), expected_calls)
            receipt = json.loads((out / mod.RECEIPT_FILE).read_text())
            self.assertEqual(receipt["status"], "failed")
            self.assertEqual(receipt["stage"], f"{stage}_failed")

    def test_runner_exception_updates_receipt(self):
        class LaunchFailureRunner(FakeRunner):
            def __call__(self, command, *, cwd, check):
                script = Path(command[1]).name
                if script == "capture_reference_l0.py":
                    self.calls.append((command, cwd, check))
                    raise OSError("synthetic launch failure")
                return super().__call__(command, cwd=cwd, check=check)

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            out = root / "evidence"
            out.mkdir()
            runner = LaunchFailureRunner()
            with self.assertRaises(OSError):
                mod.execute_pair(
                    source_sha=SHA,
                    output_dir=out,
                    commands=self._commands(root, out),
                    run_id="r1",
                    cwd=root,
                    runner=runner,
                )
            receipt = json.loads((out / mod.RECEIPT_FILE).read_text())
            self.assertEqual(receipt["status"], "failed")
            self.assertEqual(receipt["stage"], "reference_launch_failed")
            self.assertEqual(
                receipt["failure"]["kind"], "runner_exception"
            )
            self.assertEqual(receipt["failure"]["error_type"], "OSError")
            self.assertFalse(receipt["failure"]["stage_output"]["present"])
            self.assertIn("preflight", receipt["artifacts"])
            self.assertNotIn("reference", receipt["artifacts"])

    def test_process_failure_retains_partial_stage_artifact_digest(self):
        class PartialPapayaFailureRunner(FakeRunner):
            def __call__(self, command, *, cwd, check):
                script = Path(command[1]).name
                if script == "capture_papaya_l0.py":
                    self.calls.append((command, cwd, check))
                    output = Path(command[command.index("--output") + 1])
                    write_json(
                        output,
                        {
                            "schema": mod.PAPAYA_SCHEMA,
                            "status": "incomplete",
                            "run_id": "r1-papaya",
                            "source": {"git_sha": SHA},
                        },
                    )
                    return subprocess.CompletedProcess(command, 2)
                return super().__call__(command, cwd=cwd, check=check)

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            out = root / "evidence"
            out.mkdir()
            runner = PartialPapayaFailureRunner()
            with self.assertRaises(mod.ManagedPairError):
                mod.execute_pair(
                    source_sha=SHA,
                    output_dir=out,
                    commands=self._commands(root, out),
                    run_id="r1",
                    cwd=root,
                    runner=runner,
                )
            receipt = json.loads((out / mod.RECEIPT_FILE).read_text())
            self.assertEqual(receipt["status"], "failed")
            self.assertEqual(receipt["stage"], "papaya_failed")
            self.assertEqual(receipt["failure"]["kind"], "process_exit")
            self.assertEqual(receipt["failure"]["returncode"], 2)
            partial = receipt["failure"]["stage_output"]
            self.assertTrue(partial["present"])
            self.assertTrue(partial["readable_utf8"])
            self.assertTrue(partial["json_object"])
            self.assertEqual(partial["schema"], mod.PAPAYA_SCHEMA)
            self.assertEqual(partial["status"], "incomplete")
            self.assertEqual(partial["source_git_sha"], SHA)
            self.assertEqual(
                partial["sha256"],
                mod._sha256_file(out / mod.PAPAYA_FILE),
            )
            self.assertIn("reference", receipt["artifacts"])
            self.assertNotIn("papaya", receipt["artifacts"])

    def test_artifact_validation_failure_updates_receipt(self):
        class InvalidReferenceRunner(FakeRunner):
            def __call__(self, command, *, cwd, check):
                completed = super().__call__(command, cwd=cwd, check=check)
                if Path(command[1]).name == "capture_reference_l0.py":
                    output = Path(command[command.index("--output") + 1])
                    value = json.loads(output.read_text())
                    value["status"] = "incomplete"
                    write_json(output, value)
                return completed

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            out = root / "evidence"
            out.mkdir()
            runner = InvalidReferenceRunner()
            with self.assertRaises(mod.ManagedPairError):
                mod.execute_pair(
                    source_sha=SHA,
                    output_dir=out,
                    commands=self._commands(root, out),
                    run_id="r1",
                    cwd=root,
                    runner=runner,
                )
            receipt = json.loads((out / mod.RECEIPT_FILE).read_text())
            self.assertEqual(receipt["status"], "failed")
            self.assertEqual(receipt["stage"], "reference_validation_failed")
            self.assertEqual(
                receipt["failure"]["kind"], "artifact_validation"
            )
            self.assertEqual(
                receipt["failure"]["error_type"], "ManagedPairError"
            )
            partial = receipt["failure"]["stage_output"]
            self.assertTrue(partial["present"])
            self.assertEqual(partial["schema"], mod.REFERENCE_SCHEMA)
            self.assertEqual(partial["status"], "incomplete")
            self.assertIn("preflight", receipt["artifacts"])
            self.assertNotIn("reference", receipt["artifacts"])

    def test_pass_decision_completes_pipeline(self):
        receipt = self._complete("pass")
        self.assertEqual(receipt["status"], "complete")
        self.assertEqual(receipt["artifacts"]["decision"]["decision"], "pass")
        self.assertTrue(
            receipt["scope"]["preflight_all_required_inputs_verified"]
        )
        self.assertTrue(
            receipt["scope"]["preregistered_numeric_policy_applied"]
        )
        self.assertFalse(receipt["scope"]["shipping_decision"])

    def test_fail_decision_is_evidence_not_pipeline_failure(self):
        receipt = self._complete("fail")
        self.assertEqual(receipt["status"], "complete")
        self.assertEqual(receipt["artifacts"]["decision"]["decision"], "fail")
        self.assertEqual(receipt["artifacts"]["decision"]["failure_count"], 1)

    def _complete(self, decision):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            out = root / "evidence"
            out.mkdir()
            runner = FakeRunner(decision=decision)
            receipt = mod.execute_pair(
                source_sha=SHA,
                output_dir=out,
                commands=self._commands(root, out),
                run_id="r1",
                cwd=root,
                runner=runner,
            )
            self.assertEqual(len(runner.calls), 5)
            self.assertEqual(
                set(receipt["artifacts"]),
                {"preflight", "reference", "papaya", "comparison", "decision"},
            )
            return receipt

    def test_report_source_sha_drift_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            out = root / "evidence"
            out.mkdir()
            runner = FakeRunner(report_sha="2" * 40)
            with self.assertRaises(mod.ManagedPairError):
                mod.execute_pair(
                    source_sha=SHA,
                    output_dir=out,
                    commands=self._commands(root, out),
                    run_id="r1",
                    cwd=root,
                    runner=runner,
                )
            self.assertEqual(len(runner.calls), 4)

    def test_decision_artifact_digest_binding_drift_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            out = root / "evidence"
            out.mkdir()
            runner = FakeRunner(
                bad_decision_binding="reference_artifact_sha256"
            )
            with self.assertRaises(mod.ManagedPairError):
                mod.execute_pair(
                    source_sha=SHA,
                    output_dir=out,
                    commands=self._commands(root, out),
                    run_id="r1",
                    cwd=root,
                    runner=runner,
                )
            self.assertEqual(len(runner.calls), 5)

    def test_preflight_overclaim_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            out = root / "evidence"
            out.mkdir()
            runner = FakeRunner(preflight_live=True)
            with self.assertRaises(mod.ManagedPairError):
                mod.execute_pair(
                    source_sha=SHA,
                    output_dir=out,
                    commands=self._commands(root, out),
                    run_id="r1",
                    cwd=root,
                    runner=runner,
                )
            self.assertEqual(len(runner.calls), 1)

    def test_script_checkout_must_equal_sei_source_dir(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            here = root / "sei" / "evaluation" / "local-typed-comparator"
            here.mkdir(parents=True)
            self.assertEqual(
                mod._require_script_source_binding(here, root / "sei"),
                (root / "sei").resolve(),
            )
            with self.assertRaises(mod.ManagedPairError):
                mod._require_script_source_binding(here, root / "other-sei")

    def test_partial_artifact_summary_handles_non_json(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "partial.json"
            path.write_text("{not-json", encoding="utf-8")
            summary = mod._partial_artifact_summary(path)
            self.assertTrue(summary["present"])
            self.assertTrue(summary["readable_utf8"])
            self.assertFalse(summary["json_object"])
            self.assertEqual(summary["bytes"], len(b"{not-json"))
            self.assertEqual(summary["sha256"], mod._sha256_file(path))

    def test_output_dir_must_be_new_and_external(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            sei = root / "sei"
            papaya = root / "papaya"
            sei.mkdir()
            papaya.mkdir()
            with self.assertRaises(mod.ManagedPairError):
                mod._require_external_new_output_dir(
                    sei / "evidence",
                    sei_source_dir=sei,
                    papaya_source_dir=papaya,
                )
            existing = root / "existing"
            existing.mkdir()
            with self.assertRaises(mod.ManagedPairError):
                mod._require_external_new_output_dir(
                    existing,
                    sei_source_dir=sei,
                    papaya_source_dir=papaya,
                )
            external = root / "evidence"
            self.assertEqual(
                mod._require_external_new_output_dir(
                    external,
                    sei_source_dir=sei,
                    papaya_source_dir=papaya,
                ),
                external.resolve(),
            )


if __name__ == "__main__":
    unittest.main()
