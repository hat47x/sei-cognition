import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("evidence_gate", HERE / "evidence_gate.py")
eg = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(eg)


class EvidenceGateTest(unittest.TestCase):
    def write_json(self, path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def write_jsonl(self, path, rows):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
            encoding="utf-8",
        )

    def build_chain(self, root):
        manifest_path = root / "tasks.v1.json"
        cases = []
        for i in range(12):
            split = "train" if i < 6 else "valid" if i < 9 else "test"
            cases.append({
                "case_id": f"case-{i:02d}",
                "task_id": "synthetic_gate_test",
                "feature_schema_version": "feature/v1",
                "task_schema_version": "task/v1",
                "source_provenance_class": "synthetic-test",
                "split": split,
                "split_group_identity": f"group-{i:02d}",
                "state": {"x": i},
                "questions": {
                    "q": {
                        "type": "noul",
                        "instructions": "synthetic mechanical test",
                        "criteria": {"true": "yes", "false": "no"},
                    }
                },
            })
        manifest = {
            "schema": eg.TEACHER_MANIFEST_SCHEMA,
            "model": eg.DEFAULT_MODEL,
            "cases": cases,
        }
        self.write_json(manifest_path, manifest)
        manifest_sha = eg.sha256_file(manifest_path)

        bundle_dir = root / "bundle"
        requests_dir = bundle_dir / "requests"
        requests_dir.mkdir(parents=True)
        request_entries = []
        for case in cases:
            request = {
                "state": case["state"],
                "model": eg.DEFAULT_MODEL,
                "questions": case["questions"],
            }
            request_bytes = eg.canonical_json(request) + b"\n"
            request_path = requests_dir / f"{case['case_id']}.json"
            request_path.write_bytes(request_bytes)
            request_entries.append({
                "case_id": case["case_id"],
                "task_id": case["task_id"],
                "request_sha256": eg.sha256_json(request),
                "question_type": "noul",
                "split": case["split"],
                "split_group_identity": case["split_group_identity"],
                "source_provenance_class": case["source_provenance_class"],
                "request_path": f"requests/{case['case_id']}.json",
                "request_file_sha256": hashlib.sha256(request_bytes).hexdigest(),
            })
        capture_manifest_path = bundle_dir / "capture_manifest.json"
        capture = {
            "schema": eg.CAPTURE_BUNDLE_SCHEMA,
            "api_url": "https://api.typesafe.ai/v1/systemone",
            "method": "POST",
            "content_type": "application/json",
            "model_alias": eg.DEFAULT_MODEL,
            "source_git_sha": "a" * 40,
            "source_manifest_name": manifest_path.name,
            "source_manifest_sha256": manifest_sha,
            "request_count": 12,
            "requests": request_entries,
            "boundaries": [],
        }
        self.write_json(capture_manifest_path, capture)

        raw_dir = root / "raw"
        raw_dir.mkdir()
        response_entries = []
        teacher_rows = []
        student_rows = []
        for case, request_entry in zip(cases, request_entries):
            response = {
                "model": "jev-test-1.0",
                "answers": {"q": {"type": "noul", "noul": 0.5}},
            }
            raw_path = raw_dir / f"{case['case_id']}.json"
            raw_bytes = (json.dumps(response, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
            raw_path.write_bytes(raw_bytes)
            canonical_response_sha = eg.sha256_json(response)
            response_entries.append({
                "case_id": case["case_id"],
                "request_sha256": request_entry["request_sha256"],
                "raw_response_path": f"raw/{case['case_id']}.json",
                "raw_response_file_sha256": hashlib.sha256(raw_bytes).hexdigest(),
                "canonical_response_sha256": canonical_response_sha,
                "teacher_model_version": "jev-test-1.0",
                "teacher_latency_ms": None,
            })
            teacher_rows.append({
                "schema": eg.TEACHER_ROW_SCHEMA,
                "case_id": case["case_id"],
                "task_id": case["task_id"],
                "question_id": "q",
                "question_type": "noul",
                "feature_schema_version": case["feature_schema_version"],
                "task_schema_version": case["task_schema_version"],
                "teacher_provider": "typesafe",
                "teacher_model_alias": eg.DEFAULT_MODEL,
                "teacher_model_version": "jev-test-1.0",
                "teacher_request_hash": request_entry["request_sha256"],
                "teacher_response_hash": canonical_response_sha,
                "typed_output": 0.5,
                "teacher_probability_or_score": {"p_yes": 0.5},
                "source_provenance_class": case["source_provenance_class"],
                "generation_time": "2026-09-21T00:00:00Z",
                "split": case["split"],
                "split_group_identity": case["split_group_identity"],
                "teacher_latency_ms": None,
                "usage": None,
            })
            student_rows.append({
                "schema": eg.STUDENT_ROW_SCHEMA,
                "case_id": case["case_id"],
                "task_id": case["task_id"],
                "question_type": "noul",
                "feature_schema_version": case["feature_schema_version"],
                "task_schema_version": case["task_schema_version"],
                "split": case["split"],
                "split_group_identity": case["split_group_identity"],
                "source_provenance_class": case["source_provenance_class"],
                "features": case["state"],
                "target": 0.5,
                "teacher_distribution": {"p_yes": 0.5},
                "teacher_model_version": "jev-test-1.0",
                "teacher_request_hash": request_entry["request_sha256"],
                "teacher_response_hash": canonical_response_sha,
            })

        raw_response_manifest_path = root / "raw_response_manifest.json"
        raw_manifest = {
            "schema": eg.RAW_RESPONSE_MANIFEST_SCHEMA,
            "source_git_sha": capture["source_git_sha"],
            "source_manifest_sha256": manifest_sha,
            "capture_manifest_sha256": eg.sha256_file(capture_manifest_path),
            "capture_mode": "external-import",
            "capture_latency_observed": False,
            "response_count": 12,
            "responses": response_entries,
            "raw_response_set_sha256": eg.sha256_json(response_entries),
            "teacher_model_versions": ["jev-test-1.0"],
            "external_capture_latency_observed": False,
            "boundaries": [],
        }
        self.write_json(raw_response_manifest_path, raw_manifest)

        teacher_rows_path = root / "teacher_rows.jsonl"
        student_records_path = root / "student_records.jsonl"
        self.write_jsonl(teacher_rows_path, teacher_rows)
        self.write_jsonl(student_records_path, student_rows)

        dataset_manifest_path = root / "dataset_manifest.json"
        dataset = {
            "schema": eg.DATASET_MANIFEST_SCHEMA,
            "record_count": 12,
            "split_counts": {"train": 6, "valid": 3, "test": 3},
            "teacher_model_version": "jev-test-1.0",
            "source_manifest_sha256": manifest_sha,
            "source_teacher_rows_sha256": eg.sha256_file(teacher_rows_path),
            "student_records_sha256": eg.sha256_file(student_records_path),
            "lightgbm_training_performed": False,
        }
        self.write_json(dataset_manifest_path, dataset)

        return {
            "manifest": manifest_path,
            "capture": capture_manifest_path,
            "raw_dir": raw_dir,
            "raw_manifest": raw_response_manifest_path,
            "teacher_rows": teacher_rows_path,
            "student_records": student_records_path,
            "dataset": dataset_manifest_path,
        }

    def verify(self, paths):
        return eg.verify_evidence_chain(
            paths["manifest"],
            paths["capture"],
            paths["raw_dir"],
            paths["raw_manifest"],
            paths["teacher_rows"],
            paths["student_records"],
            paths["dataset"],
        )

    def test_complete_chain_passes(self):
        with tempfile.TemporaryDirectory() as d:
            result = self.verify(self.build_chain(Path(d)))
            self.assertEqual(result["status"], "PASS")
            self.assertEqual(result["case_count"], 12)
            self.assertEqual(result["capture_mode"], "external-import")
            self.assertEqual(result["teacher_model_version"], "jev-test-1.0")
            self.assertFalse(result["lightgbm_training_performed"])

    def test_tampered_raw_bytes_are_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            paths = self.build_chain(Path(d))
            path = paths["raw_dir"] / "case-00.json"
            path.write_bytes(path.read_bytes() + b" ")
            with self.assertRaises(eg.GateError):
                self.verify(paths)

    def test_teacher_response_hash_break_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            paths = self.build_chain(Path(d))
            rows = eg.load_jsonl(paths["teacher_rows"])
            rows[0]["teacher_response_hash"] = "0" * 64
            self.write_jsonl(paths["teacher_rows"], rows)
            dataset = eg.load_json(paths["dataset"])
            dataset["source_teacher_rows_sha256"] = eg.sha256_file(paths["teacher_rows"])
            self.write_json(paths["dataset"], dataset)
            with self.assertRaises(eg.GateError):
                self.verify(paths)

    def test_student_target_break_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            paths = self.build_chain(Path(d))
            rows = eg.load_jsonl(paths["student_records"])
            rows[0]["target"] = 0.9
            self.write_jsonl(paths["student_records"], rows)
            dataset = eg.load_json(paths["dataset"])
            dataset["student_records_sha256"] = eg.sha256_file(paths["student_records"])
            self.write_json(paths["dataset"], dataset)
            with self.assertRaises(eg.GateError):
                self.verify(paths)

    def test_training_performed_flag_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            paths = self.build_chain(Path(d))
            dataset = eg.load_json(paths["dataset"])
            dataset["lightgbm_training_performed"] = True
            self.write_json(paths["dataset"], dataset)
            with self.assertRaises(eg.GateError):
                self.verify(paths)

    def test_external_capture_latency_claim_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            paths = self.build_chain(Path(d))
            raw_manifest = eg.load_json(paths["raw_manifest"])
            raw_manifest["capture_latency_observed"] = True
            self.write_json(paths["raw_manifest"], raw_manifest)
            with self.assertRaises(eg.GateError):
                self.verify(paths)

    def test_tampered_frozen_request_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            paths = self.build_chain(Path(d))
            request_path = paths["capture"].parent / "requests" / "case-00.json"
            request_path.write_bytes(request_path.read_bytes() + b" ")
            with self.assertRaises(eg.GateError):
                self.verify(paths)


if __name__ == "__main__":
    unittest.main()
