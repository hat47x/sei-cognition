import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent

PAIR_SPEC = importlib.util.spec_from_file_location(
    "run_managed_pair_for_bundle_test", HERE / "run_managed_pair.py"
)
pair = importlib.util.module_from_spec(PAIR_SPEC)
sys.modules[PAIR_SPEC.name] = pair
PAIR_SPEC.loader.exec_module(pair)

VERIFY_SPEC = importlib.util.spec_from_file_location(
    "verify_managed_pair_bundle_tested",
    HERE / "verify_managed_pair_bundle.py",
)
verify = importlib.util.module_from_spec(VERIFY_SPEC)
sys.modules[VERIFY_SPEC.name] = verify
VERIFY_SPEC.loader.exec_module(verify)

SHA = "1" * 40


def write_json(path: Path, value):
    path.write_text(
        json.dumps(value, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )


class BundleRunner:
    def __init__(self, fail_stage=None, partial_failure=False, decision="pass"):
        self.fail_stage = fail_stage
        self.partial_failure = partial_failure
        self.decision = decision

    def __call__(self, command, *, cwd, check):
        script = Path(command[1]).name
        stage = {
            "preflight_managed_pair.py": "preflight",
            "capture_reference_l0.py": "reference",
            "capture_papaya_l0.py": "papaya",
            "compare_papaya_reference_numeric.py": "comparison",
            "evaluate_papaya_numeric_parity.py": "decision",
        }[script]
        output = Path(command[command.index("--output") + 1])
        root = output.parent

        if stage == self.fail_stage:
            if self.partial_failure:
                schema = {
                    "preflight": pair.PREFLIGHT_SCHEMA,
                    "reference": pair.REFERENCE_SCHEMA,
                    "papaya": pair.PAPAYA_SCHEMA,
                    "comparison": pair.REPORT_SCHEMA,
                    "decision": pair.DECISION_SCHEMA,
                }[stage]
                value = {"schema": schema, "status": "incomplete"}
                if stage in ("reference", "papaya"):
                    value["source"] = {"git_sha": SHA}
                    value["run_id"] = f"r1-{stage}"
                write_json(output, value)
            return subprocess.CompletedProcess(command, 2)

        if stage == "preflight":
            write_json(
                output,
                {
                    "schema": pair.PREFLIGHT_SCHEMA,
                    "status": "ready",
                    "source": {"git_sha": SHA},
                    "runtime_wheelhouse": {"provided": False},
                    "scope": {
                        "all_required_inputs_verified": True,
                        "model_weights_loaded": False,
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
                    "schema": pair.REFERENCE_SCHEMA,
                    "status": "complete",
                    "source": {"git_sha": SHA},
                },
            )
        elif stage == "papaya":
            write_json(
                output,
                {
                    "schema": pair.PAPAYA_SCHEMA,
                    "status": "complete",
                    "source": {"git_sha": SHA},
                },
            )
        elif stage == "comparison":
            write_json(
                output,
                {
                    "schema": pair.REPORT_SCHEMA,
                    "inputs": {"same_sei_source_git_sha": SHA},
                    "scope": {
                        "numeric_parity_threshold_defined": False,
                        "numeric_parity_decision": False,
                    },
                },
            )
        else:
            passed = self.decision == "pass"
            write_json(
                output,
                {
                    "schema": pair.DECISION_SCHEMA,
                    "decision": self.decision,
                    "failures": [] if passed else [{"metric": "synthetic"}],
                    "numeric_report": {
                        "sha256": pair._sha256_file(root / pair.REPORT_FILE),
                        "same_sei_source_git_sha": SHA,
                        "reference_artifact_sha256": pair._sha256_file(
                            root / pair.REFERENCE_FILE
                        ),
                        "papaya_artifact_sha256": pair._sha256_file(
                            root / pair.PAPAYA_FILE
                        ),
                    },
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


class ManagedPairBundleVerifierTest(unittest.TestCase):
    def _commands(self, root: Path, output: Path):
        commands = pair.build_commands(
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

    def _make_bundle(
        self,
        root: Path,
        *,
        fail_stage=None,
        partial_failure=False,
        decision="pass",
    ) -> Path:
        out = root / "evidence"
        out.mkdir()
        runner = BundleRunner(
            fail_stage=fail_stage,
            partial_failure=partial_failure,
            decision=decision,
        )
        if fail_stage is None:
            pair.execute_pair(
                source_sha=SHA,
                output_dir=out,
                commands=self._commands(root, out),
                run_id="r1",
                cwd=root,
                runner=runner,
            )
        else:
            with self.assertRaises(pair.ManagedPairError):
                pair.execute_pair(
                    source_sha=SHA,
                    output_dir=out,
                    commands=self._commands(root, out),
                    run_id="r1",
                    cwd=root,
                    runner=runner,
                )
        return out

    def test_complete_bundle_verifies(self):
        with tempfile.TemporaryDirectory() as td:
            out = self._make_bundle(Path(td))
            result = verify.verify_bundle(
                out, expected_source_sha=SHA, pair_module=pair
            )
        self.assertEqual(result["status"], "verified")
        self.assertEqual(result["pair_status"], "complete")
        self.assertEqual(
            set(result["completed_artifacts"]), set(verify.STAGES)
        )
        self.assertIsNone(result["failure"])
        self.assertTrue(
            result["scope"]["internal_bundle_integrity_verified"]
        )
        self.assertFalse(result["scope"]["live_inference_reexecuted"])
        self.assertFalse(result["scope"]["numeric_parity_recomputed"])

    def test_complete_fail_decision_is_valid_bundle(self):
        with tempfile.TemporaryDirectory() as td:
            out = self._make_bundle(Path(td), decision="fail")
            result = verify.verify_bundle(
                out, expected_source_sha=SHA, pair_module=pair
            )
        self.assertEqual(result["pair_status"], "complete")

    def test_wrong_expected_source_sha_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            out = self._make_bundle(Path(td))
            with self.assertRaises(verify.ManagedPairBundleError):
                verify.verify_bundle(
                    out, expected_source_sha="2" * 40, pair_module=pair
                )

    def test_completed_artifact_tamper_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            out = self._make_bundle(Path(td))
            path = out / pair.REFERENCE_FILE
            value = json.loads(path.read_text())
            value["tampered"] = True
            write_json(path, value)
            with self.assertRaises(verify.ManagedPairBundleError):
                verify.verify_bundle(
                    out, expected_source_sha=SHA, pair_module=pair
                )

    def test_failed_bundle_with_partial_output_verifies(self):
        with tempfile.TemporaryDirectory() as td:
            out = self._make_bundle(
                Path(td), fail_stage="papaya", partial_failure=True
            )
            result = verify.verify_bundle(
                out, expected_source_sha=SHA, pair_module=pair
            )
        self.assertEqual(result["pair_status"], "failed")
        self.assertEqual(
            set(result["completed_artifacts"]), {"preflight", "reference"}
        )
        self.assertEqual(result["failure"]["stage"], "papaya")
        self.assertEqual(result["failure"]["kind"], "process_exit")
        self.assertTrue(result["failure"]["stage_output_present"])

    def test_failed_partial_output_tamper_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            out = self._make_bundle(
                Path(td), fail_stage="papaya", partial_failure=True
            )
            path = out / pair.PAPAYA_FILE
            value = json.loads(path.read_text())
            value["tampered"] = True
            write_json(path, value)
            with self.assertRaises(verify.ManagedPairBundleError):
                verify.verify_bundle(
                    out, expected_source_sha=SHA, pair_module=pair
                )

    def test_failed_receipt_cannot_claim_failed_stage_as_completed(self):
        with tempfile.TemporaryDirectory() as td:
            out = self._make_bundle(Path(td), fail_stage="reference")
            receipt_path = out / pair.RECEIPT_FILE
            receipt = json.loads(receipt_path.read_text())
            receipt["artifacts"]["reference"] = {
                "file": pair.REFERENCE_FILE,
                "sha256": "0" * 64,
                "schema": pair.REFERENCE_SCHEMA,
                "status": "complete",
            }
            write_json(receipt_path, receipt)
            with self.assertRaises(verify.ManagedPairBundleError):
                verify.verify_bundle(
                    out, expected_source_sha=SHA, pair_module=pair
                )

    def test_receipt_cannot_promote_transported_wheel_origin(self):
        with tempfile.TemporaryDirectory() as td:
            out = self._make_bundle(Path(td))
            receipt_path = out / pair.RECEIPT_FILE
            receipt = json.loads(receipt_path.read_text())
            receipt["scope"][
                "transported_wheel_installation_origin_attested"
            ] = True
            write_json(receipt_path, receipt)
            with self.assertRaises(verify.ManagedPairBundleError):
                verify.verify_bundle(
                    out, expected_source_sha=SHA, pair_module=pair
                )

    def test_complete_receipt_cannot_retain_failure_block(self):
        with tempfile.TemporaryDirectory() as td:
            out = self._make_bundle(Path(td))
            receipt_path = out / pair.RECEIPT_FILE
            receipt = json.loads(receipt_path.read_text())
            receipt["failure"] = {
                "stage": "papaya",
                "kind": "process_exit",
                "returncode": 2,
                "stage_output": {"file": pair.PAPAYA_FILE, "present": False},
            }
            write_json(receipt_path, receipt)
            with self.assertRaises(verify.ManagedPairBundleError):
                verify.verify_bundle(
                    out, expected_source_sha=SHA, pair_module=pair
                )


if __name__ == "__main__":
    unittest.main()
