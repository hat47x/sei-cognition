import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load_module(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


fc = load_module("finalize_capture", "finalize_capture.py")
td = fc.td


class FinalizeCaptureTest(unittest.TestCase):
    @staticmethod
    def valid_response(case):
        qid, question = next(iter(case["questions"].items()))
        qtype = question["type"]
        if qtype == "noul":
            answer = {"type": "noul", "noul": 0.6}
        elif qtype == "choice":
            options = list(question["criteria"])
            probabilities = {key: 0.0 for key in options}
            probabilities[options[0]] = 1.0
            answer = {
                "type": "choice",
                "choice": options[0],
                "confidence": 1.0,
                "probabilities": probabilities,
            }
        else:
            probabilities = {str(i): 0.0 for i in range(len(question["criteria"]))}
            probabilities["0"] = 1.0
            answer = {
                "type": "score",
                "score": 0.0,
                "confidence": 1.0,
                "probabilities": probabilities,
                "legend": {str(i): value for i, value in enumerate(question["criteria"])},
            }
        return {
            "model": "jev-test-1.0",
            "answers": {qid: answer},
            "usage": {"input_tokens": 4, "output_tokens": 2},
        }

    def build_inputs(self, root):
        manifest_path = HERE / "tasks.v1.json"
        manifest = td.load_manifest(manifest_path)
        bundle_dir = root / "bundle"
        td.write_capture_bundle(
            manifest_path,
            manifest,
            bundle_dir,
            source_git_sha="a" * 40,
        )

        raw_dir = root / "raw"
        raw_dir.mkdir()
        for case in manifest["cases"]:
            (raw_dir / f"{case['case_id']}.json").write_text(
                json.dumps(self.valid_response(case), ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

        normalized = root / "normalized"
        teacher_rows = normalized / "teacher_rows.jsonl"
        raw_manifest = normalized / "raw_response_manifest.json"
        td.normalize_raw_directory(
            manifest,
            raw_dir,
            teacher_rows,
            generated_at="2026-09-22T00:00:00Z",
            manifest_path=manifest_path,
            capture_manifest_path=bundle_dir / "capture_manifest.json",
            raw_manifest_path=raw_manifest,
        )
        return {
            "manifest": manifest_path,
            "capture": bundle_dir / "capture_manifest.json",
            "raw_dir": raw_dir,
            "raw_manifest": raw_manifest,
            "teacher_rows": teacher_rows,
        }

    def finalize(self, paths, output):
        return fc.finalize_capture(
            paths["manifest"],
            paths["capture"],
            paths["raw_dir"],
            paths["raw_manifest"],
            paths["teacher_rows"],
            output,
            expected_source_git_sha="a" * 40,
        )

    def test_success_publishes_atomic_receipt_and_student_ready_dataset(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            paths = self.build_inputs(root)
            output = root / "finalized"
            receipt = self.finalize(paths, output)

            self.assertEqual(receipt["status"], "PASS")
            self.assertEqual(receipt["case_count"], 12)
            self.assertEqual(receipt["capture_mode"], "external-import")
            self.assertEqual(receipt["teacher_model_version"], "jev-test-1.0")
            self.assertEqual(receipt["network_requests_sent"], 0)
            self.assertIs(receipt["lightgbm_training_performed"], False)
            self.assertIs(receipt["student_dataset"]["lightgbm_training_performed"], False)

            self.assertTrue((output / "student-ready" / "student_records.jsonl").is_file())
            self.assertTrue((output / "student-ready" / "dataset_manifest.json").is_file())
            self.assertTrue((output / "evidence_chain_verification.json").is_file())
            saved = json.loads((output / "capture_verification_receipt.json").read_text(encoding="utf-8"))
            self.assertEqual(saved, receipt)

    def test_wrong_expected_source_sha_fails_without_output(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            paths = self.build_inputs(root)
            output = root / "finalized"
            with self.assertRaises(fc.FinalizeError):
                fc.finalize_capture(
                    paths["manifest"],
                    paths["capture"],
                    paths["raw_dir"],
                    paths["raw_manifest"],
                    paths["teacher_rows"],
                    output,
                    expected_source_git_sha="b" * 40,
                )
            self.assertFalse(output.exists())

    def test_tampered_raw_bytes_fail_without_partial_student_artifacts(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            paths = self.build_inputs(root)
            first_raw = next(paths["raw_dir"].glob("*.json"))
            first_raw.write_bytes(first_raw.read_bytes() + b" ")
            output = root / "finalized"
            with self.assertRaises(fc.eg.GateError):
                self.finalize(paths, output)
            self.assertFalse(output.exists())

    def test_existing_output_is_rejected_before_work(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            paths = self.build_inputs(root)
            output = root / "finalized"
            output.mkdir()
            marker = output / "keep.txt"
            marker.write_text("keep", encoding="utf-8")
            with self.assertRaises(fc.FinalizeError):
                self.finalize(paths, output)
            self.assertEqual(marker.read_text(encoding="utf-8"), "keep")

    def test_invalid_expected_source_sha_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            paths = self.build_inputs(root)
            output = root / "finalized"
            with self.assertRaises(fc.FinalizeError):
                fc.finalize_capture(
                    paths["manifest"],
                    paths["capture"],
                    paths["raw_dir"],
                    paths["raw_manifest"],
                    paths["teacher_rows"],
                    output,
                    expected_source_git_sha="not-a-sha",
                )
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
