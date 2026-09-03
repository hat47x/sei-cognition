import json
import sys
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from check_grouping_structure import inspect_grouping_structure


class HistoricalActualSamplesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog_path = BASE_DIR / "historical_actual_samples.json"
        cls.catalog_bytes = cls.catalog_path.read_bytes()
        cls.catalog = json.loads(cls.catalog_bytes.decode("utf-8"))
        cls.samples = cls.catalog["samples"]

    def test_historical_samples_remain_non_golden(self):
        rules = self.catalog["rules"]
        self.assertFalse(rules["goldenGrouping"])
        self.assertFalse(rules["machineScoring"])
        self.assertFalse(rules["preferredOutput"])
        self.assertEqual(rules["qualityJudgement"], "not_evaluated")

        forbidden = {
            "expectedGroups",
            "expectedLabel",
            "qualityScore",
            "preferred",
            "winner",
        }

        def walk(value):
            if isinstance(value, dict):
                self.assertTrue(forbidden.isdisjoint(value.keys()), value)
                for child in value.values():
                    walk(child)
            elif isinstance(value, list):
                for child in value:
                    walk(child)

        walk(self.catalog)

    def test_each_historical_result_passes_only_structural_checks(self):
        self.assertGreaterEqual(len(self.samples), 2)
        for sample in self.samples:
            request_bytes = json.dumps(
                sample["request"], ensure_ascii=False, sort_keys=True
            ).encode("utf-8")
            result_bytes = json.dumps(
                sample["result"], ensure_ascii=False, sort_keys=True
            ).encode("utf-8")
            report = inspect_grouping_structure(
                sample["request"],
                sample["result"],
                request_bytes=request_bytes,
                result_bytes=result_bytes,
            )
            self.assertEqual(report["status"], "passed", sample["id"])
            self.assertEqual(report["qualityJudgement"], "not_evaluated")
            self.assertEqual(report["violations"], [])

    def test_same_execution_identity_can_preserve_different_generated_wording(self):
        first, second = self.samples[0], self.samples[1]
        self.assertEqual(first["request"], second["request"])

        identity_fields = (
            "methodSourceCommit",
            "runtime",
            "runtimeVersion",
            "model",
            "observedModelIdPrefix",
            "promptSha256",
        )
        for field in identity_fields:
            self.assertEqual(first["source"][field], second["source"][field], field)

        self.assertNotEqual(first["result"], second["result"])
        self.assertNotEqual(
            first["result"]["groups"][0]["label"],
            second["result"]["groups"][0]["label"],
        )

    def test_source_runs_are_distinct_and_traceable(self):
        run_ids = [sample["source"]["workflowRunId"] for sample in self.samples]
        job_ids = [sample["source"]["jobId"] for sample in self.samples]
        repository_commits = [
            sample["source"]["repositoryCommit"] for sample in self.samples
        ]

        self.assertEqual(len(run_ids), len(set(run_ids)))
        self.assertEqual(len(job_ids), len(set(job_ids)))
        self.assertEqual(len(repository_commits), len(set(repository_commits)))
        for sample in self.samples:
            self.assertTrue(sample["source"]["workflowRunId"].isdigit())
            self.assertTrue(sample["source"]["jobId"].isdigit())
            self.assertEqual(len(sample["source"]["repositoryCommit"]), 40)
            self.assertEqual(len(sample["source"]["methodSourceCommit"]), 40)
            self.assertEqual(len(sample["source"]["promptSha256"]), 64)


if __name__ == "__main__":
    unittest.main()
