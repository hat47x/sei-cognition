import copy
import importlib.util
import io
import json
import tempfile
import urllib.error
from unittest import mock
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("teacher_dataset", HERE / "teacher_dataset.py")
td = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(td)


class TeacherDatasetTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = td.load_manifest(HERE / "tasks.v1.json")

    @staticmethod
    def valid_response(case, model="jev-test-1.0"):
        qid, question = next(iter(case["questions"].items()))
        qtype = question["type"]
        if qtype == "noul":
            answer = {"type": "noul", "noul": 0.7}
        elif qtype == "choice":
            options = list(question["criteria"])
            probabilities = {key: 0.0 for key in options}
            probabilities[options[0]] = 1.0
            answer = {"type": "choice", "choice": options[0], "confidence": 1.0, "probabilities": probabilities}
        else:
            probabilities = {str(i): 0.0 for i in range(len(question["criteria"]))}
            probabilities["0"] = 1.0
            answer = {
                "type": "score",
                "score": 0.0,
                "confidence": 1.0,
                "probabilities": probabilities,
                "legend": {str(i): v for i, v in enumerate(question["criteria"])},
            }
        return {"model": model, "answers": {qid: answer}, "usage": {"input_tokens": 1, "output_tokens": 1}}

    def test_manifest_covers_three_typed_primitives(self):
        types = {next(iter(c["questions"].values()))["type"] for c in self.manifest["cases"]}
        self.assertEqual(types, {"choice", "score", "noul"})

    def test_all_states_are_structured(self):
        self.assertTrue(all(isinstance(c["state"], (dict, list)) for c in self.manifest["cases"]))

    def test_split_groups_do_not_cross_splits(self):
        group_splits = {}
        for case in self.manifest["cases"]:
            group_splits.setdefault(case["split_group_identity"], set()).add(case["split"])
        self.assertTrue(all(len(splits) == 1 for splits in group_splits.values()))
        counts = {split_name: sum(c["split"] == split_name for c in self.manifest["cases"]) for split_name in ("train", "valid", "test")}
        self.assertEqual(counts, {"train": 6, "valid": 3, "test": 3})

    def test_manifest_rejects_cross_split_group(self):
        bad = copy.deepcopy(self.manifest)
        first = bad["cases"][0]
        second = bad["cases"][1]
        second["split_group_identity"] = first["split_group_identity"]
        second["split"] = "valid" if first["split"] != "valid" else "train"
        with self.assertRaises(td.ContractError):
            td.validate_manifest(bad)

    def test_request_hash_is_canonical(self):
        case = self.manifest["cases"][0]
        req = td.request_for(case)
        reordered = {"questions": req["questions"], "model": req["model"], "state": req["state"]}
        self.assertEqual(td.sha256_json(req), td.sha256_json(reordered))

    def test_plan_has_one_descriptor_per_case(self):
        desc = td.plan(self.manifest)
        self.assertEqual(len(desc), len(self.manifest["cases"]))
        self.assertTrue(all(len(x["request_sha256"]) == 64 for x in desc))

    def test_choice_response_builds_versioned_row(self):
        case = next(c for c in self.manifest["cases"] if next(iter(c["questions"].values()))["type"] == "choice")
        opts = list(next(iter(case["questions"].values()))["criteria"])
        probs = {k: 0.0 for k in opts}; probs[opts[0]] = 1.0
        resp = {"model":"jev-1.13.0","answers":{"route":{"type":"choice","choice":opts[0],"confidence":1.0,"probabilities":probs}},"usage":{"input_tokens":1,"output_tokens":1}}
        row = td.dataset_row(case, resp, generated_at="2026-09-21T00:00:00Z", latency_ms=12.5)
        self.assertEqual(row["teacher_model_version"], "jev-1.13.0")
        self.assertEqual(row["typed_output"], opts[0])
        self.assertIn("probabilities", row["teacher_probability_or_score"])

    def test_score_response_rejects_incomplete_distribution(self):
        case = next(c for c in self.manifest["cases"] if next(iter(c["questions"].values()))["type"] == "score")
        resp = {"model":"jev-1.13.0","answers":{"urgency":{"type":"score","score":1.0,"confidence":0.8,"probabilities":{"0":0.2,"1":0.8}}}}
        with self.assertRaises(td.ContractError): td.validate_response(case, resp)

    def test_noul_response_rejects_out_of_range(self):
        case = next(c for c in self.manifest["cases"] if next(iter(c["questions"].values()))["type"] == "noul")
        resp = {"model":"jev-1.13.0","answers":{"needs_human_review":{"type":"noul","noul":1.1}}}
        with self.assertRaises(td.ContractError): td.validate_response(case, resp)

    def test_alias_only_response_model_is_rejected(self):
        case = self.manifest["cases"][0]
        opts = list(next(iter(case["questions"].values()))["criteria"])
        probs = {k: 0.0 for k in opts}; probs[opts[0]] = 1.0
        resp = {"model":"jev-latest","answers":{"route":{"type":"choice","choice":opts[0],"confidence":1.0,"probabilities":probs}}}
        with self.assertRaises(td.ContractError): td.validate_response(case, resp)

    def test_missing_api_key_blocks_before_network(self):
        with self.assertRaises(td.CollectionBlocked): td.collect_case(self.manifest["cases"][0], "")

    def test_run_refuses_without_api_key(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(td.CollectionBlocked):
                td.run_collection(self.manifest, Path(d), api_key="")

    def test_manifest_rejects_raw_text_state(self):
        bad = copy.deepcopy(self.manifest)
        bad["cases"][0]["state"] = "raw text"
        with self.assertRaises(td.ContractError): td.validate_manifest(bad)

    def test_manifest_rejects_missing_split_group(self):
        bad = copy.deepcopy(self.manifest)
        bad["cases"][0]["split_group_identity"] = ""
        with self.assertRaises(td.ContractError): td.validate_manifest(bad)

    def test_import_raw_directory_normalizes_all_cases(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            raw = root / "raw"
            raw.mkdir()
            for case in self.manifest["cases"]:
                (raw / f"{case['case_id']}.json").write_text(json.dumps(self.valid_response(case)), encoding="utf-8")
            rows_path = root / "out" / "teacher_rows.jsonl"
            count = td.normalize_raw_directory(
                self.manifest,
                raw,
                rows_path,
                generated_at="2026-09-21T00:00:00Z",
            )
            self.assertEqual(count, len(self.manifest["cases"]))
            rows = [json.loads(line) for line in rows_path.read_text().splitlines()]
            self.assertEqual(len(rows), len(self.manifest["cases"]))
            self.assertTrue(all(row["teacher_model_version"] == "jev-test-1.0" for row in rows))
            self.assertTrue(all(row["teacher_latency_ms"] is None for row in rows))

    def test_import_raw_directory_rejects_missing_case(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            raw = root / "raw"
            raw.mkdir()
            with self.assertRaises(td.CollectionBlocked):
                td.normalize_raw_directory(self.manifest, raw, root / "rows.jsonl")

    def test_collect_case_retries_529_then_succeeds(self):
        case = self.manifest["cases"][0]
        payload = json.dumps(self.valid_response(case)).encode()

        class FakeResponse:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                return False
            def read(self):
                return payload

        err = urllib.error.HTTPError(
            td.API_URL,
            529,
            "overloaded",
            hdrs=None,
            fp=io.BytesIO(b'{"error":"overloaded"}'),
        )
        with mock.patch.object(td.urllib.request, "urlopen", side_effect=[err, FakeResponse()]) as call, mock.patch.object(td.time, "sleep") as sleep:
            response, latency = td.collect_case(case, "secret", backoff_base_seconds=0.0)
        self.assertEqual(response["model"], "jev-test-1.0")
        self.assertGreaterEqual(latency, 0.0)
        self.assertEqual(call.call_count, 2)
        sleep.assert_called_once()


if __name__ == "__main__": unittest.main()
