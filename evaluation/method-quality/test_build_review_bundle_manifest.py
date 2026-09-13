from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("build_review_bundle_manifest.py")
SPEC = importlib.util.spec_from_file_location("review_bundle_manifest", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MANIFEST = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MANIFEST)


class ReviewBundleManifestTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.request = self.write("request.json", b'{"cards":[]}\n')
        self.result = self.write("result.json", b'{"groups":[]}\n')
        self.model_evidence = self.write("model.json", b'{"model":"example"}\n')
        self.runtime_version = self.write("runtime.txt", b"ollama version 0.32.14\n")
        self.model_list = self.write("models.txt", b"example model-id\n")
        structure = {
            "status": "passed",
            "requestSha256": self.digest(self.request),
            "resultSha256": self.digest(self.result),
            "qualityJudgement": "not_evaluated",
        }
        self.structure = self.write(
            "structure.json",
            (json.dumps(structure, sort_keys=True) + "\n").encode("utf-8"),
        )

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def write(self, name: str, data: bytes) -> Path:
        path = self.root / name
        path.write_bytes(data)
        return path

    def digest(self, path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def build(self) -> dict:
        return MANIFEST.build_manifest(
            workflow_run_id="123",
            workflow_run_attempt="2",
            repository_commit="repo-sha",
            method_source_commit="method-sha",
            request_path=self.request,
            result_path=self.result,
            model_evidence_path=self.model_evidence,
            structure_report_path=self.structure,
            runtime_version_path=self.runtime_version,
            model_list_path=self.model_list,
        )

    def test_manifest_records_run_identity_and_exact_file_digests(self) -> None:
        manifest = self.build()
        self.assertEqual("sei.method-quality-review-bundle/v1", manifest["schema"])
        self.assertEqual("123", manifest["workflowRunId"])
        self.assertEqual("2", manifest["workflowRunAttempt"])
        self.assertEqual("repo-sha", manifest["repositoryCommit"])
        self.assertEqual("method-sha", manifest["methodSourceCommit"])
        self.assertEqual(self.digest(self.request), manifest["files"]["request"]["sha256"])
        self.assertEqual(self.digest(self.result), manifest["files"]["result"]["sha256"])
        self.assertEqual("passed", manifest["structureStatus"])
        self.assertEqual("not_evaluated", manifest["qualityJudgement"])

    def test_manifest_rejects_request_digest_mismatch(self) -> None:
        structure = json.loads(self.structure.read_text(encoding="utf-8"))
        structure["requestSha256"] = "0" * 64
        self.structure.write_text(json.dumps(structure), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "requestSha256"):
            self.build()

    def test_manifest_rejects_result_digest_mismatch(self) -> None:
        structure = json.loads(self.structure.read_text(encoding="utf-8"))
        structure["resultSha256"] = "f" * 64
        self.structure.write_text(json.dumps(structure), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "resultSha256"):
            self.build()

    def test_manifest_does_not_promote_structure_result_to_quality_judgement(self) -> None:
        manifest = self.build()
        self.assertEqual("not_evaluated", manifest["qualityJudgement"])
        self.assertNotIn("qualityScore", manifest)
        self.assertNotIn("qualityStatus", manifest)


if __name__ == "__main__":
    unittest.main()
