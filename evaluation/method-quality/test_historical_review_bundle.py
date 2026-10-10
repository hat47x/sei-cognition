import json
import sys
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from build_review_bundle_manifest import build_manifest
from check_grouping_structure import inspect_grouping_structure

BUNDLE_DIR = BASE_DIR / "historical" / "M1B-RUN-33596839607"

# emit側が書く現行identity。ADR-0031の3に従い、凍結recordの旧identityだけを読み替える。
CURRENT_REPORT_SCHEMA = "sei.method-quality-structure-report/v1"
CURRENT_MANIFEST_SCHEMA = "sei.method-quality-review-bundle/v1"


def legacy_schema(schema: str) -> str:
    """ADR-0031の3。改名前に記録されたEvidenceが持つ旧identityを返す。

    emit側は常に`sei.*`だけを書く。読み取り側だけが双方を受け付ける。
    記録済みEvidenceが存在する限り必要な恒久措置であり、期限は切らない。
    """
    return "soza." + schema[len("sei."):] if schema.startswith("sei.") else schema


def read_recorded_record(record: dict, current_schema: str) -> dict:
    """凍結recordのschema identityを読み取り側だけで受理し、比較用の写しを返す。

    凍結recordのfileは書き換えない。emit側の出力は current_schema と完全一致しなければならない。
    """
    recorded = record.get("schema")
    if recorded not in (current_schema, legacy_schema(current_schema)):
        raise AssertionError(
            f"凍結recordのschemaが現行identityにも旧identityにも一致しません: {recorded!r}"
        )
    return {**record, "schema": current_schema}


class HistoricalReviewBundleTest(unittest.TestCase):
    def test_structure_report_is_reproducible(self):
        request_path = BUNDLE_DIR / "request.json"
        result_path = BUNDLE_DIR / "result.json"
        request_bytes = request_path.read_bytes()
        result_bytes = result_path.read_bytes()

        actual = inspect_grouping_structure(
            json.loads(request_bytes.decode("utf-8")),
            json.loads(result_bytes.decode("utf-8")),
            request_bytes=request_bytes,
            result_bytes=result_bytes,
        )
        expected = json.loads(
            (BUNDLE_DIR / "structure-report.json").read_text(encoding="utf-8")
        )

        expected = read_recorded_record(expected, CURRENT_REPORT_SCHEMA)

        self.assertEqual(actual, expected)
        self.assertEqual(actual["status"], "passed")
        self.assertEqual(actual["qualityJudgement"], "not_evaluated")

    def test_review_manifest_is_reproducible(self):
        provenance = json.loads(
            (BUNDLE_DIR / "reconstruction-provenance.json").read_text(
                encoding="utf-8"
            )
        )
        actual = build_manifest(
            workflow_run_id=provenance["sourceWorkflowRunId"],
            workflow_run_attempt=provenance["sourceWorkflowRunAttempt"],
            repository_commit=provenance["checkedOutRepositoryCommit"],
            method_source_commit=provenance["methodSourceCommit"],
            request_path=BUNDLE_DIR / "request.json",
            result_path=BUNDLE_DIR / "result.json",
            model_evidence_path=BUNDLE_DIR / "model-evidence.json",
            structure_report_path=BUNDLE_DIR / "structure-report.json",
            runtime_version_path=BUNDLE_DIR / "runtime-version.txt",
            model_list_path=BUNDLE_DIR / "model-list.txt",
        )
        expected = json.loads(
            (BUNDLE_DIR / "review-manifest.json").read_text(encoding="utf-8")
        )

        expected = read_recorded_record(expected, CURRENT_MANIFEST_SCHEMA)

        self.assertEqual(actual, expected)
        self.assertEqual(actual["structureStatus"], "passed")
        self.assertEqual(actual["qualityJudgement"], "not_evaluated")

    def test_provenance_marks_bundle_as_reconstructed(self):
        provenance = json.loads(
            (BUNDLE_DIR / "reconstruction-provenance.json").read_text(
                encoding="utf-8"
            )
        )

        self.assertFalse(provenance["originalWorkflowArtifactAvailable"])
        self.assertEqual(provenance["sourceWorkflowRunId"], "33596839607")
        self.assertEqual(provenance["sourceJobId"], "100141890796")
        self.assertEqual(provenance["qualityJudgement"], "not_evaluated")


if __name__ == "__main__":
    unittest.main()
