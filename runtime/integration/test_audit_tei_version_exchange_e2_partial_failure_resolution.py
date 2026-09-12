import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import audit_tei_version_exchange_e2_partial_failure_resolution as subject


class TEIE2PartialFailureResolutionAuditTest(unittest.TestCase):
    def _report(self) -> dict[str, object]:
        return {
            "schema": subject.e2_partial.SCHEMA,
            "result": "e2_failed",
            "sourceAcquisition": {
                "mode": subject.base_audit.CURRENT_GITHUB_ACQUISITION_MODE,
                "repository": subject.github_source.GITHUB_REPOSITORY,
                "sourceCommit": subject.source_identity.REVISION_B,
                "rootTree": subject.github_source.REVISION_B_ROOT_TREE,
                "credentialSource": "environment",
                "canonicalSourceVerification": {
                    "revisionBExactHead": True,
                    "worktreeCleanWithinBoundary": True,
                },
            },
            "comparisonAxis": {
                "buildSourceCommit": subject.source_identity.REVISION_B,
                "referenceInputSourceCommit": subject.source_identity.REVISION_A,
                "referenceInputAcquisition": "historical_evidence_bundle",
                "e3IntentionallyNotRun": True,
            },
            "bundleArchive": "/tmp/tei-e3b-p2-revision-b-e2-partial.tar.gz",
            "e2": None,
            "e3": None,
            "failure": {
                "stage": "E2",
                "substage": "tei_cli_build",
                "type": "TEIEvidenceStageError",
            },
            "qualityJudgement": "not_evaluated",
        }

    def _audit(self, report: dict[str, object]) -> dict[str, object]:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            report_path = root / "partial.json"
            report_path.write_text(
                json.dumps(report, ensure_ascii=False),
                encoding="utf-8",
            )
            c1 = subject.base_audit._criterion(
                1,
                subject.base_audit.SATISFIED,
                "historical A verified",
            )
            historical = {
                "sourceCommit": subject.source_identity.REVISION_A,
                "archive": "/tmp/a.tar.gz",
                "archiveSha256": "a" * 64,
                "referenceInput": {"verified": True},
            }
            with mock.patch.object(
                subject.base_audit,
                "_verify_sei_baseline",
                return_value={"head": "sei-head", "worktreeCleanWithinBoundary": True},
            ), mock.patch.object(
                subject.base_audit,
                "_historical_a",
                return_value=(c1, historical),
            ):
                return subject.audit_partial_failure(
                    report_path,
                    sei_repo_root=root,
                    historical_a_bundle=root / "a.tar.gz",
                )

    def test_valid_failure_maps_stage_without_becoming_resolution_candidate(self):
        result = self._audit(self._report())

        self.assertEqual("blocked", result["result"])
        self.assertFalse(result["resolutionCandidate"])
        self.assertFalse(result["autoResolvePermitted"])
        self.assertEqual("not_evaluated", result["qualityJudgement"])
        self.assertEqual(
            [1, 3, 5],
            result["automatedCriteria"]["satisfied"],
        )
        self.assertEqual(
            [2, 4, 6],
            result["automatedCriteria"]["blockedOrManual"],
        )
        self.assertEqual(
            subject.base_audit.SATISFIED,
            result["criteria"]["3"]["status"],
        )
        self.assertEqual(
            "tei_cli_build",
            result["criteria"]["3"]["detail"]["substage"],
        )
        self.assertEqual(
            subject.base_audit.BLOCKED,
            result["criteria"]["2"]["status"],
        )
        self.assertEqual(
            subject.base_audit.BLOCKED,
            result["criteria"]["4"]["status"],
        )
        self.assertEqual(
            "actual_artifact_identity",
            result["criteria"]["6"]["detail"]["missingBoundary"],
        )

    def test_missing_substage_keeps_criterion3_blocked(self):
        report = self._report()
        report["failure"] = {"stage": "E2", "type": "RuntimeError"}
        result = self._audit(report)
        self.assertEqual(
            subject.base_audit.BLOCKED,
            result["criteria"]["3"]["status"],
        )
        self.assertEqual([1, 5], result["automatedCriteria"]["satisfied"])

    def test_wrong_schema_is_rejected(self):
        report = self._report()
        report["schema"] = "wrong"
        with self.assertRaisesRegex(ValueError, "schema"):
            subject._validate_partial_failure(report)

    def test_success_report_is_rejected_by_failure_only_audit(self):
        report = self._report()
        report["result"] = "e2_bundle_verified_e3_not_run"
        with self.assertRaisesRegex(ValueError, "failure report専用"):
            subject._validate_partial_failure(report)

    def test_snapshot_transport_is_observed_but_artifact_boundary_stays_blocked(self):
        report = self._report()
        source = report["sourceAcquisition"]
        assert isinstance(source, dict)
        source["sourceTransport"] = {
            "mode": subject.snapshot_source.SNAPSHOT_TRANSPORT_MODE,
            "schema": subject.snapshot_source.SNAPSHOT_SCHEMA,
            "sha256": "b" * 64,
            "runtimeCredentialUsed": False,
        }
        result = self._audit(report)
        criterion = result["criteria"]["6"]
        self.assertEqual(subject.base_audit.BLOCKED, criterion["status"])
        self.assertEqual(
            subject.snapshot_source.SNAPSHOT_TRANSPORT_MODE,
            criterion["detail"]["observedSourceBoundaries"]["sourceTransport"]["mode"],
        )
        self.assertEqual(
            "actual_artifact_identity",
            criterion["detail"]["missingBoundary"],
        )

    def test_snapshot_runtime_credential_use_is_provenance_mismatch(self):
        report = self._report()
        source = report["sourceAcquisition"]
        assert isinstance(source, dict)
        source["sourceTransport"] = {
            "mode": subject.snapshot_source.SNAPSHOT_TRANSPORT_MODE,
            "schema": subject.snapshot_source.SNAPSHOT_SCHEMA,
            "sha256": "b" * 64,
            "runtimeCredentialUsed": True,
        }
        result = self._audit(report)
        mismatches = result["criteria"]["6"]["detail"]["mismatches"]
        self.assertIn("sourceTransport.runtimeCredentialUsed", mismatches)

    def test_revision_axis_drift_is_rejected(self):
        report = self._report()
        axis = report["comparisonAxis"]
        assert isinstance(axis, dict)
        axis["buildSourceCommit"] = "0" * 40
        with self.assertRaisesRegex(ValueError, "comparison axis"):
            subject._validate_partial_failure(report)


if __name__ == "__main__":
    unittest.main()
