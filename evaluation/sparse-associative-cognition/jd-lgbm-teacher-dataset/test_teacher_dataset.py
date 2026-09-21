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

    def test_capture_bundle_freezes_all_requests(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            output = root / "bundle"
            source_sha = "a" * 40
            bundle = td.write_capture_bundle(
                HERE / "tasks.v1.json",
                self.manifest,
                output,
                source_git_sha=source_sha,
            )
            self.assertEqual(bundle["schema"], td.CAPTURE_BUNDLE_SCHEMA)
            self.assertEqual(bundle["request_count"], len(self.manifest["cases"]))
            self.assertEqual(bundle["source_git_sha"], source_sha)
            self.assertEqual(bundle["source_manifest_sha256"], td.sha256_file(HERE / "tasks.v1.json"))

            by_case = {entry["case_id"]: entry for entry in bundle["requests"]}
            self.assertEqual(set(by_case), {case["case_id"] for case in self.manifest["cases"]})
            for case in self.manifest["cases"]:
                request_path = output / by_case[case["case_id"]]["request_path"]
                request = json.loads(request_path.read_text(encoding="utf-8"))
                self.assertEqual(request, td.request_for(case))
                self.assertEqual(by_case[case["case_id"]]["request_sha256"], td.sha256_json(request))
                self.assertEqual(by_case[case["case_id"]]["request_file_sha256"], td.sha256_file(request_path))
                self.assertNotIn("Authorization", request_path.read_text(encoding="utf-8"))

            saved = json.loads((output / "capture_manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(saved, bundle)

    def test_capture_bundle_is_deterministic(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            source_sha = "b" * 40
            first = root / "first"
            second = root / "second"
            td.write_capture_bundle(HERE / "tasks.v1.json", self.manifest, first, source_git_sha=source_sha)
            td.write_capture_bundle(HERE / "tasks.v1.json", self.manifest, second, source_git_sha=source_sha)
            self.assertEqual(
                (first / "capture_manifest.json").read_bytes(),
                (second / "capture_manifest.json").read_bytes(),
            )
            for case in self.manifest["cases"]:
                name = f"{case['case_id']}.json"
                self.assertEqual((first / "requests" / name).read_bytes(), (second / "requests" / name).read_bytes())

    def test_capture_bundle_rejects_nonempty_output(self):
        with tempfile.TemporaryDirectory() as d:
            output = Path(d) / "bundle"
            output.mkdir()
            (output / "unrelated.txt").write_text("keep", encoding="utf-8")
            with self.assertRaises(td.CollectionBlocked):
                td.write_capture_bundle(
                    HERE / "tasks.v1.json",
                    self.manifest,
                    output,
                    source_git_sha="c" * 40,
                )

    def test_capture_bundle_rejects_file_output_path(self):
        with tempfile.TemporaryDirectory() as d:
            output = Path(d) / "bundle"
            output.write_text("not-a-directory", encoding="utf-8")
            with self.assertRaises(td.CollectionBlocked):
                td.write_capture_bundle(
                    HERE / "tasks.v1.json",
                    self.manifest,
                    output,
                    source_git_sha="d" * 40,
                )

    def test_capture_bundle_requires_exact_source_sha(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(td.ContractError):
                td.write_capture_bundle(
                    HERE / "tasks.v1.json",
                    self.manifest,
                    Path(d) / "bundle",
                    source_git_sha="not-a-git-sha",
                )

    def test_capture_bundle_loader_rejects_tampered_request_bytes(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            bundle_dir = root / "bundle"
            td.write_capture_bundle(
                HERE / "tasks.v1.json",
                self.manifest,
                bundle_dir,
                source_git_sha="e" * 40,
            )
            request_path = bundle_dir / "requests" / f"{self.manifest['cases'][0]['case_id']}.json"
            request_path.write_bytes(request_path.read_bytes() + b" ")
            with self.assertRaises(td.ContractError):
                td.load_capture_bundle(
                    HERE / "tasks.v1.json",
                    self.manifest,
                    bundle_dir / "capture_manifest.json",
                )

    def test_import_with_capture_bundle_writes_raw_response_manifest(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            bundle_dir = root / "bundle"
            raw_dir = root / "raw"
            raw_dir.mkdir()
            td.write_capture_bundle(
                HERE / "tasks.v1.json",
                self.manifest,
                bundle_dir,
                source_git_sha="f" * 40,
            )
            for case in self.manifest["cases"]:
                response = self.valid_response(case)
                (raw_dir / f"{case['case_id']}.json").write_text(
                    json.dumps(response, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )

            rows_path = root / "normalized" / "teacher_rows.jsonl"
            raw_manifest_path = root / "normalized" / "raw_response_manifest.json"
            count = td.normalize_raw_directory(
                self.manifest,
                raw_dir,
                rows_path,
                generated_at="2026-09-21T00:00:00Z",
                manifest_path=HERE / "tasks.v1.json",
                capture_manifest_path=bundle_dir / "capture_manifest.json",
                raw_manifest_path=raw_manifest_path,
            )
            self.assertEqual(count, len(self.manifest["cases"]))
            raw_manifest = json.loads(raw_manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(raw_manifest["schema"], td.RAW_RESPONSE_MANIFEST_SCHEMA)
            self.assertEqual(raw_manifest["source_git_sha"], "f" * 40)
            self.assertEqual(raw_manifest["response_count"], len(self.manifest["cases"]))
            self.assertEqual(raw_manifest["teacher_model_versions"], ["jev-test-1.0"])
            self.assertEqual(raw_manifest["capture_mode"], "external-import")
            self.assertFalse(raw_manifest["capture_latency_observed"])
            self.assertFalse(raw_manifest["external_capture_latency_observed"])
            self.assertEqual(
                raw_manifest["capture_manifest_sha256"],
                td.sha256_file(bundle_dir / "capture_manifest.json"),
            )
            self.assertEqual(len(raw_manifest["raw_response_set_sha256"]), 64)

            by_case = {entry["case_id"]: entry for entry in raw_manifest["responses"]}
            self.assertEqual(set(by_case), {case["case_id"] for case in self.manifest["cases"]})
            for case in self.manifest["cases"]:
                raw_path = raw_dir / f"{case['case_id']}.json"
                response = json.loads(raw_path.read_bytes())
                entry = by_case[case["case_id"]]
                self.assertEqual(entry["raw_response_file_sha256"], td.sha256_file(raw_path))
                self.assertEqual(entry["canonical_response_sha256"], td.sha256_json(response))
                self.assertEqual(entry["teacher_model_version"], "jev-test-1.0")
                self.assertIsNone(entry["teacher_latency_ms"])

    def test_import_with_capture_bundle_rejects_unexpected_raw_json(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            bundle_dir = root / "bundle"
            raw_dir = root / "raw"
            raw_dir.mkdir()
            td.write_capture_bundle(
                HERE / "tasks.v1.json",
                self.manifest,
                bundle_dir,
                source_git_sha="1" * 40,
            )
            for case in self.manifest["cases"]:
                (raw_dir / f"{case['case_id']}.json").write_text(
                    json.dumps(self.valid_response(case)),
                    encoding="utf-8",
                )
            (raw_dir / "extra.json").write_text("{}", encoding="utf-8")
            with self.assertRaises(td.CollectionBlocked):
                td.normalize_raw_directory(
                    self.manifest,
                    raw_dir,
                    root / "teacher_rows.jsonl",
                    manifest_path=HERE / "tasks.v1.json",
                    capture_manifest_path=bundle_dir / "capture_manifest.json",
                    raw_manifest_path=root / "raw_response_manifest.json",
                )

    def test_import_cli_requires_capture_manifest(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            raw_dir = root / "raw"
            raw_dir.mkdir()
            result = td.main([
                str(HERE / "tasks.v1.json"),
                "--mode", "import",
                "--raw-dir", str(raw_dir),
                "--output-dir", str(root / "out"),
            ])
            self.assertEqual(result, 2)
            self.assertFalse((root / "out" / "teacher_rows.jsonl").exists())

    def test_collect_case_raw_preserves_exact_http_bytes(self):
        case = self.manifest["cases"][0]
        payload = (
            b'{\n  "model": "jev-test-1.0",\n  "answers": {"route": '
            + json.dumps(self.valid_response(case)["answers"]["route"], separators=(",", ":")).encode()
            + b'},\n  "usage": {"input_tokens": 1, "output_tokens": 1}\n}'
        )

        class FakeResponse:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                return False
            def read(self):
                return payload

        with mock.patch.object(td.urllib.request, "urlopen", return_value=FakeResponse()):
            response, latency, raw = td.collect_case_raw(case, "secret")
        self.assertEqual(response["model"], "jev-test-1.0")
        self.assertGreaterEqual(latency, 0.0)
        self.assertEqual(raw, payload)

    def test_direct_run_binds_capture_bundle_and_preserves_raw_bytes(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            bundle_dir = root / "bundle"
            output_dir = root / "run"
            td.write_capture_bundle(
                HERE / "tasks.v1.json",
                self.manifest,
                bundle_dir,
                source_git_sha="2" * 40,
            )

            raw_by_case = {}
            def fake_collect(case, api_key):
                response = self.valid_response(case)
                raw = (
                    json.dumps(response, ensure_ascii=False, separators=(", ", ": "))
                    + "\n"
                ).encode("utf-8")
                raw_by_case[case["case_id"]] = raw
                return response, 12.5, raw

            with mock.patch.object(td, "collect_case_raw", side_effect=fake_collect) as collect:
                count = td.run_collection(
                    self.manifest,
                    output_dir,
                    api_key="secret",
                    manifest_path=HERE / "tasks.v1.json",
                    capture_manifest_path=bundle_dir / "capture_manifest.json",
                )
            self.assertEqual(count, len(self.manifest["cases"]))
            self.assertEqual(collect.call_count, len(self.manifest["cases"]))

            raw_manifest = json.loads((output_dir / "raw_response_manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(raw_manifest["capture_mode"], "direct-run")
            self.assertTrue(raw_manifest["capture_latency_observed"])
            self.assertFalse(raw_manifest["external_capture_latency_observed"])
            self.assertEqual(raw_manifest["response_count"], len(self.manifest["cases"]))
            self.assertEqual(raw_manifest["teacher_model_versions"], ["jev-test-1.0"])

            by_case = {entry["case_id"]: entry for entry in raw_manifest["responses"]}
            for case in self.manifest["cases"]:
                raw_path = output_dir / "raw" / f"{case['case_id']}.json"
                self.assertEqual(raw_path.read_bytes(), raw_by_case[case["case_id"]])
                entry = by_case[case["case_id"]]
                self.assertEqual(entry["raw_response_file_sha256"], td.sha256_file(raw_path))
                self.assertEqual(entry["teacher_latency_ms"], 12.5)

    def test_direct_run_validates_capture_bundle_before_network(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            bundle_dir = root / "bundle"
            td.write_capture_bundle(
                HERE / "tasks.v1.json",
                self.manifest,
                bundle_dir,
                source_git_sha="3" * 40,
            )
            request_path = bundle_dir / "requests" / f"{self.manifest['cases'][0]['case_id']}.json"
            request_path.write_bytes(request_path.read_bytes() + b" ")
            with mock.patch.object(td, "collect_case_raw") as collect:
                with self.assertRaises(td.ContractError):
                    td.run_collection(
                        self.manifest,
                        root / "run",
                        api_key="secret",
                        manifest_path=HERE / "tasks.v1.json",
                        capture_manifest_path=bundle_dir / "capture_manifest.json",
                    )
            collect.assert_not_called()

    def test_direct_capture_preflight_is_network_free_and_binds_source(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            bundle_dir = root / "bundle"
            output_dir = root / "run"
            source_sha = "4" * 40
            td.write_capture_bundle(
                HERE / "tasks.v1.json",
                self.manifest,
                bundle_dir,
                source_git_sha=source_sha,
            )
            with mock.patch.object(td.urllib.request, "urlopen") as urlopen:
                report = td.direct_capture_preflight(
                    self.manifest,
                    output_dir,
                    api_key="secret",
                    manifest_path=HERE / "tasks.v1.json",
                    capture_manifest_path=bundle_dir / "capture_manifest.json",
                    expected_source_git_sha=source_sha,
                )
            urlopen.assert_not_called()
            self.assertEqual(report["status"], "ready")
            self.assertEqual(report["network_requests_sent"], 0)
            self.assertTrue(report["api_key_present"])
            self.assertEqual(report["source_git_sha"], source_sha)
            self.assertEqual(report["request_count"], len(self.manifest["cases"]))
            self.assertNotIn("secret", json.dumps(report))

    def test_direct_capture_preflight_rejects_source_mismatch(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            bundle_dir = root / "bundle"
            td.write_capture_bundle(
                HERE / "tasks.v1.json",
                self.manifest,
                bundle_dir,
                source_git_sha="5" * 40,
            )
            with self.assertRaises(td.ContractError):
                td.direct_capture_preflight(
                    self.manifest,
                    root / "run",
                    api_key="secret",
                    manifest_path=HERE / "tasks.v1.json",
                    capture_manifest_path=bundle_dir / "capture_manifest.json",
                    expected_source_git_sha="6" * 40,
                )

    def test_direct_capture_preflight_rejects_existing_artifact(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            bundle_dir = root / "bundle"
            output_dir = root / "run"
            td.write_capture_bundle(
                HERE / "tasks.v1.json",
                self.manifest,
                bundle_dir,
                source_git_sha="7" * 40,
            )
            output_dir.mkdir()
            (output_dir / "teacher_rows.jsonl").write_text("existing\n", encoding="utf-8")
            with self.assertRaises(td.CollectionBlocked):
                td.direct_capture_preflight(
                    self.manifest,
                    output_dir,
                    api_key="secret",
                    manifest_path=HERE / "tasks.v1.json",
                    capture_manifest_path=bundle_dir / "capture_manifest.json",
                    expected_source_git_sha="7" * 40,
                )

    def test_run_cli_requires_capture_manifest(self):
        with tempfile.TemporaryDirectory() as d:
            result = td.main([
                str(HERE / "tasks.v1.json"),
                "--mode", "run",
                "--output-dir", str(Path(d) / "run"),
            ])
            self.assertEqual(result, 2)

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

    def test_response_rejects_unrequested_answer(self):
        case = self.manifest["cases"][0]
        response = self.valid_response(case)
        response["answers"]["unexpected"] = {"type": "noul", "noul": 0.5}
        with self.assertRaises(td.ContractError):
            td.validate_response(case, response)

    def test_score_response_requires_exact_legend(self):
        case = next(c for c in self.manifest["cases"] if next(iter(c["questions"].values()))["type"] == "score")
        qid, question = next(iter(case["questions"].items()))
        response = self.valid_response(case)
        response["answers"][qid].pop("legend")
        with self.assertRaises(td.ContractError):
            td.validate_response(case, response)

        response = self.valid_response(case)
        response["answers"][qid]["legend"]["0"] = "wrong"
        with self.assertRaises(td.ContractError):
            td.validate_response(case, response)

    def test_response_requires_usage_token_counts(self):
        case = self.manifest["cases"][0]
        response = self.valid_response(case)
        response.pop("usage")
        with self.assertRaises(td.ContractError):
            td.validate_response(case, response)

        response = self.valid_response(case)
        response["usage"]["input_tokens"] = True
        with self.assertRaises(td.ContractError):
            td.validate_response(case, response)

        response = self.valid_response(case)
        response["usage"]["output_tokens"] = -1
        with self.assertRaises(td.ContractError):
            td.validate_response(case, response)

    def test_noul_response_rejects_out_of_range(self):
        case = next(c for c in self.manifest["cases"] if next(iter(c["questions"].values()))["type"] == "noul")
        resp = {"model":"jev-1.13.0","answers":{"needs_human_review":{"type":"noul","noul":1.1}}}
        with self.assertRaises(td.ContractError): td.validate_response(case, resp)

    def test_noul_response_rejects_boolean(self):
        case = next(c for c in self.manifest["cases"] if next(iter(c["questions"].values()))["type"] == "noul")
        qid = next(iter(case["questions"]))
        resp = {"model":"jev-1.13.0","answers":{qid:{"type":"noul","noul":True}}}
        with self.assertRaises(td.ContractError): td.validate_response(case, resp)

    def test_choice_response_rejects_boolean_probability_and_confidence(self):
        case = next(c for c in self.manifest["cases"] if next(iter(c["questions"].values()))["type"] == "choice")
        qid, question = next(iter(case["questions"].items()))
        opts = list(question["criteria"])
        probs = {k: 0.0 for k in opts}; probs[opts[0]] = True
        resp = {"model":"jev-1.13.0","answers":{qid:{"type":"choice","choice":opts[0],"confidence":1.0,"probabilities":probs}}}
        with self.assertRaises(td.ContractError): td.validate_response(case, resp)

        probs = {k: 0.0 for k in opts}; probs[opts[0]] = 1.0
        resp = {"model":"jev-1.13.0","answers":{qid:{"type":"choice","choice":opts[0],"confidence":True,"probabilities":probs}}}
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
