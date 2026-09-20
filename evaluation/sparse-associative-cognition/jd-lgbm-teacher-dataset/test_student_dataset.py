import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("student_dataset", HERE / "student_dataset.py")
sd = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(sd)
td = sd.td


class StudentDatasetTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = td.load_manifest(HERE / "tasks.v1.json")

    @staticmethod
    def response(case, model="jev-test-1.0"):
        qid, q = next(iter(case["questions"].items()))
        if q["type"] == "noul":
            answer = {"type": "noul", "noul": 0.7}
        elif q["type"] == "choice":
            opts = list(q["criteria"])
            probs = {key: 0.0 for key in opts}; probs[opts[0]] = 1.0
            answer = {"type": "choice", "choice": opts[0], "confidence": 1.0, "probabilities": probs}
        else:
            probs = {str(i): 0.0 for i in range(len(q["criteria"]))}; probs["0"] = 1.0
            answer = {"type": "score", "score": 0.0, "confidence": 1.0, "probabilities": probs, "legend": {str(i): v for i, v in enumerate(q["criteria"])}}
        return {"model": model, "answers": {qid: answer}, "usage": {"input_tokens": 1, "output_tokens": 1}}

    def rows(self, model="jev-test-1.0"):
        return [td.dataset_row(c, self.response(c, model), generated_at="2026-09-21T00:00:00Z", latency_ms=None) for c in self.manifest["cases"]]

    def test_prepared_records_join_manifest_state_without_mutation(self):
        records, version = sd.prepare_student_records(self.manifest, self.rows())
        self.assertEqual(len(records), 12)
        self.assertEqual(version, "jev-test-1.0")
        for record, case in zip(records, self.manifest["cases"]):
            self.assertEqual(record["features"], case["state"])
            self.assertIsNot(record["features"], case["state"])
        self.assertEqual({r["split"] for r in records}, {"train", "valid", "test"})

    def test_missing_teacher_case_is_rejected(self):
        with self.assertRaises(sd.StudentDatasetError):
            sd.prepare_student_records(self.manifest, self.rows()[:-1])

    def test_duplicate_teacher_case_is_rejected(self):
        rows = self.rows(); rows.append(copy.deepcopy(rows[0]))
        with self.assertRaises(sd.StudentDatasetError):
            sd.prepare_student_records(self.manifest, rows)

    def test_unknown_teacher_case_is_rejected(self):
        rows = self.rows(); rows[0]["case_id"] = "unknown-case"
        with self.assertRaises(sd.StudentDatasetError):
            sd.prepare_student_records(self.manifest, rows)

    def test_request_hash_mismatch_is_rejected(self):
        rows = self.rows(); rows[0]["teacher_request_hash"] = "0" * 64
        with self.assertRaises(sd.StudentDatasetError):
            sd.prepare_student_records(self.manifest, rows)

    def test_split_mismatch_is_rejected(self):
        rows = self.rows(); rows[0]["split"] = "test" if rows[0]["split"] != "test" else "train"
        with self.assertRaises(sd.StudentDatasetError):
            sd.prepare_student_records(self.manifest, rows)

    def test_mixed_teacher_versions_are_rejected(self):
        rows = self.rows(); rows[-1]["teacher_model_version"] = "jev-test-2.0"
        with self.assertRaises(sd.StudentDatasetError):
            sd.prepare_student_records(self.manifest, rows)

    def test_choice_distribution_tamper_is_rejected(self):
        rows = self.rows()
        row = next(r for r in rows if r["question_type"] == "choice")
        keys = list(row["teacher_probability_or_score"]["probabilities"])
        row["teacher_probability_or_score"]["probabilities"] = {keys[0]: 1.0}
        with self.assertRaises(sd.StudentDatasetError):
            sd.prepare_student_records(self.manifest, rows)

    def test_empty_teacher_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "rows.jsonl"; p.write_text("")
            with self.assertRaises(sd.StudentDatasetError):
                sd.load_teacher_rows(p)

    def test_write_dataset_records_source_hashes_and_no_training_claim(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            rows_path = root / "teacher_rows.jsonl"
            rows_path.write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in self.rows()))
            summary = sd.write_student_dataset(HERE / "tasks.v1.json", rows_path, root / "out")
            self.assertEqual(summary["record_count"], 12)
            self.assertEqual(summary["split_counts"], {"train": 6, "valid": 3, "test": 3})
            self.assertFalse(summary["lightgbm_training_performed"])
            self.assertEqual(len(summary["source_manifest_sha256"]), 64)
            self.assertEqual(len(summary["source_teacher_rows_sha256"]), 64)
            self.assertEqual(len(summary["student_records_sha256"]), 64)


if __name__ == "__main__":
    unittest.main()
