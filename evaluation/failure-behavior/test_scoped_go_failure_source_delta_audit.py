#!/usr/bin/env python3

from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


EVIDENCE_PATH = Path(__file__).with_name(
    "scoped_go_failure_source_delta_audit_20260918.json"
)
REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def git_blob_sha1(path: Path) -> str:
    payload = path.read_bytes()
    header = f"blob {len(payload)}\0".encode("ascii")
    return hashlib.sha1(header + payload).hexdigest()



def normalized_executable_text(path: str, text: str) -> str:
    normalized = (
        text.replace("github.com/hat47x/soza", "github.com/hat47x/sei-cognition")
        .replace("SOZA", "SEI")
        .replace("Soza", "Sei")
        .replace("soza.", "sei.")
        .replace("soza-", "sei-")
    )
    if path == "runtime/go/semanticruntime/loader.go":
        normalized = normalized.replace(
            "\t\t\t\t// The reference may point outside this bundle. Payload acquisition and\n",
            "",
        ).replace(
            "\t\t\t\t// digest verification are handled by Payload Source / Verifier layers.\n",
            "",
        )
    return normalized


def normalized_executable_sha1(path: str, file_path: Path) -> str:
    normalized = normalized_executable_text(path, file_path.read_text(encoding="utf-8"))
    return hashlib.sha1(normalized.encode("utf-8")).hexdigest()


def load_audit() -> dict:
    return json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))


class ScopedGoFailureSourceDeltaAuditTest(unittest.TestCase):
    def test_current_source_blobs_still_match_audit(self) -> None:
        audit = load_audit()
        for item in audit["files"]:
            path = REPOSITORY_ROOT / item["path"]
            self.assertTrue(path.is_file(), item["path"])
            self.assertEqual(
                git_blob_sha1(path),
                item["currentBlobSha"],
                item["path"],
            )

    def test_audit_keeps_historical_execution_separate_from_current_pass(self) -> None:
        audit = load_audit()
        self.assertEqual(audit["scope"], "source-delta-audit-only")
        self.assertEqual(audit["authority"], "evaluation-only")
        self.assertEqual(
            audit["historicalExecutionEvidence"]["path"],
            "evaluation/failure-behavior/scoped_go_failure_execution_20260910.json",
        )
        self.assertEqual(audit["historicalExecutionEvidence"]["goVersion"], "go1.23.2")
        self.assertEqual(audit["historicalExecutionEvidence"]["repositoryBaselineGo"], "1.25")

    def test_all_audited_files_match_fixed_normalized_content_digest(self) -> None:
        audit = load_audit()
        self.assertEqual(
            audit["comparisonMethod"]["normalizedContentDigestAlgorithm"],
            "sha1-over-utf8-normalized-content",
        )
        self.assertGreater(len(audit["files"]), 0)
        for item in audit["files"]:
            path = REPOSITORY_ROOT / item["path"]
            self.assertTrue(path.is_file(), item["path"])
            self.assertTrue(item["normalizedExecutableContentEquivalent"], item["path"])
            self.assertTrue(
                item["historicalAndCurrentNormalizedContentMatchedAtAudit"],
                item["path"],
            )
            self.assertEqual(
                normalized_executable_sha1(item["path"], path),
                item["normalizedExecutableContentSha1"],
                item["path"],
            )

    def test_digest_correction_provenance_is_preserved(self) -> None:
        correction = load_audit()["digestCorrection"]
        self.assertEqual(correction["recordedAt"], "2026-09-18")
        self.assertIn("64-bit message-length trailer", correction["reason"])
        self.assertIn("Only the derived normalizedExecutableContentSha1", correction["impact"])
        self.assertIn("matched for all 7 audited files", correction["verification"])

    def test_claims_fail_closed_at_current_execution_boundary(self) -> None:
        claims = load_audit()["claims"]
        self.assertTrue(claims["scopedHistoricalExecutionRemainsRelevantRegressionContext"])
        self.assertFalse(claims["additionalExecutableBehaviorDeltaDetectedInAuditedFiles"])
        for key in (
            "currentExactBlobExecutionVerified",
            "fullRepositoryRegressionVerified",
            "go125BaselineVerified",
            "actualProviderFailureEvidenceEstablishedByThisAudit",
            "operationalEvidence",
        ):
            self.assertFalse(claims[key], key)

    def test_stop_line_does_not_promote_source_equivalence_to_execution(self) -> None:
        stop_line = load_audit()["stopLine"]
        self.assertIn("source-delta audit equivalence", stop_line)
        self.assertIn("current exact-blob Go execution PASS", stop_line)
        self.assertIn("Go 1.25 baseline verification", stop_line)
        self.assertIn("Operational Evidence", stop_line)


if __name__ == "__main__":
    unittest.main()
