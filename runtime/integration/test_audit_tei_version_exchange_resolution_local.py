import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import audit_tei_version_exchange_resolution_local as subject


class LocalResolutionAuditTest(unittest.TestCase):
    def base_result(self):
        criteria = {
            str(number): {
                "criterion": number,
                "status": (
                    subject.base_audit.SATISFIED
                    if number <= 5
                    else subject.base_audit.MANUAL
                ),
                "summary": "fixture",
            }
            for number in range(1, 9)
        }
        criteria["7"]["status"] = subject.base_audit.MANUAL
        criteria["8"]["status"] = subject.base_audit.MANUAL
        return {
            "schema": subject.base_audit.SCHEMA,
            "result": "blocked",
            "resolutionCandidate": False,
            "autoResolvePermitted": False,
            "canonicalReport": {
                "comparisonAxis": {
                    "buildSourceCommit": subject.source_identity.REVISION_B,
                    "referenceInputSourceCommit": subject.source_identity.REVISION_A,
                    "referenceInputAcquisition": "historical_evidence_bundle",
                }
            },
            "criteria": criteria,
            "automatedCriteria": {
                "scope": [1, 2, 3, 4, 5, 6],
                "satisfied": [1, 2, 3, 4, 5],
                "blockedOrManual": [6],
            },
            "manualReviewRequired": [7, 8],
            "qualityJudgement": "not_evaluated",
        }

    def source_verification(self, repo: Path):
        return {
            "schema": "sei.tei-execution-source-identity/v1",
            "result": "verified",
            "repositoryRoot": str(repo),
            "head": subject.source_identity.REVISION_B,
            "revisionBExactHead": True,
            "executionSourceObjects": {"cmd": "a" * 40},
            "worktreeCleanWithinBoundary": True,
        }

    @mock.patch.object(subject.source_identity, "verify_repository")
    @mock.patch.object(subject.base_audit, "audit_resolution")
    def test_local_boundary_replaces_manual_criterion6(
        self, base_audit, verify_repository
    ):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source_repo = root / "tei-b"
            source_repo.mkdir()
            base_audit.return_value = self.base_result()
            verify_repository.return_value = self.source_verification(source_repo)

            result = subject.audit_local_resolution(
                root / "canonical.json",
                revision_b_source_repo=source_repo,
                sei_repo_root=root / "sei",
            )

        self.assertEqual(subject.SCHEMA, result["schema"])
        self.assertTrue(result["resolutionCandidate"])
        self.assertFalse(result["autoResolvePermitted"])
        self.assertEqual(
            subject.base_audit.SATISFIED,
            result["criteria"]["6"]["status"],
        )
        self.assertEqual(
            "not_applicable",
            result["criteria"]["6"]["detail"]["sourceAcquisition"][
                "credentialRequirement"
            ],
        )
        self.assertEqual([1, 2, 3, 4, 5, 6], result["automatedCriteria"]["satisfied"])
        self.assertEqual([], result["automatedCriteria"]["blockedOrManual"])

    @mock.patch.object(subject.source_identity, "verify_repository")
    @mock.patch.object(subject.base_audit, "audit_resolution")
    def test_source_identity_failure_keeps_resolution_blocked(
        self, base_audit, verify_repository
    ):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source_repo = root / "tei-b"
            source_repo.mkdir()
            base_audit.return_value = self.base_result()
            verify_repository.side_effect = ValueError("HEAD drift")

            result = subject.audit_local_resolution(
                root / "canonical.json",
                revision_b_source_repo=source_repo,
                sei_repo_root=root / "sei",
            )

        self.assertFalse(result["resolutionCandidate"])
        self.assertEqual(
            subject.base_audit.BLOCKED,
            result["criteria"]["6"]["status"],
        )
        self.assertEqual([6], result["automatedCriteria"]["blockedOrManual"])

    @mock.patch.object(subject.source_identity, "verify_repository")
    @mock.patch.object(subject.base_audit, "audit_resolution")
    def test_valid_checkout_preparation_provenance_is_recorded(
        self, base_audit, verify_repository
    ):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source_repo = root / "tei-b"
            source_repo.mkdir()
            report = root / "checkout.json"
            report.write_text(
                json.dumps(
                    {
                        "schema": subject.CHECKOUT_PREPARATION_SCHEMA,
                        "result": "prepared_verified",
                        "sourceRepository": str(root / "source-clone"),
                        "sourceStateBefore": {"head": "abc", "status": []},
                        "sourceStateAfter": {"head": "abc", "status": []},
                        "sourceHeadAndStatusUnchanged": True,
                        "sourceObjectDatabaseSelfContained": True,
                        "outputRepository": str(source_repo),
                        "revision": subject.source_identity.REVISION_B,
                        "detachedHead": True,
                        "cloneMode": "local_no_hardlinks_no_checkout",
                        "outputObjectDatabaseSelfContained": True,
                        "prePublishIdentityVerified": True,
                        "verification": {
                            "head": subject.source_identity.REVISION_B,
                            "revisionBExactHead": True,
                            "worktreeCleanWithinBoundary": True,
                        },
                    }
                ),
                encoding="utf-8",
            )
            base_audit.return_value = self.base_result()
            verify_repository.return_value = self.source_verification(source_repo)

            result = subject.audit_local_resolution(
                root / "canonical.json",
                revision_b_source_repo=source_repo,
                sei_repo_root=root / "sei",
                checkout_preparation_report=report,
            )

        detail = result["criteria"]["6"]["detail"]["sourceAcquisition"]
        self.assertTrue(detail["checkoutPreparationProvenance"]["observed"])
        self.assertTrue(result["checkoutPreparationReportObserved"])
        self.assertTrue(result["resolutionCandidate"])

    @mock.patch.object(subject.source_identity, "verify_repository")
    @mock.patch.object(subject.base_audit, "audit_resolution")
    def test_preparation_report_output_mismatch_blocks(
        self, base_audit, verify_repository
    ):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source_repo = root / "tei-b"
            source_repo.mkdir()
            other_repo = root / "other"
            other_repo.mkdir()
            report = root / "checkout.json"
            report.write_text(
                json.dumps(
                    {
                        "schema": subject.CHECKOUT_PREPARATION_SCHEMA,
                        "result": "prepared_verified",
                        "sourceHeadAndStatusUnchanged": True,
                        "sourceObjectDatabaseSelfContained": True,
                        "outputRepository": str(other_repo),
                        "revision": subject.source_identity.REVISION_B,
                        "detachedHead": True,
                        "cloneMode": "local_no_hardlinks_no_checkout",
                        "outputObjectDatabaseSelfContained": True,
                        "prePublishIdentityVerified": True,
                        "verification": {
                            "head": subject.source_identity.REVISION_B,
                            "revisionBExactHead": True,
                            "worktreeCleanWithinBoundary": True,
                        },
                    }
                ),
                encoding="utf-8",
            )
            base_audit.return_value = self.base_result()
            verify_repository.return_value = self.source_verification(source_repo)

            result = subject.audit_local_resolution(
                root / "canonical.json",
                revision_b_source_repo=source_repo,
                sei_repo_root=root / "sei",
                checkout_preparation_report=report,
            )

        self.assertFalse(result["resolutionCandidate"])
        self.assertEqual(
            subject.base_audit.BLOCKED,
            result["criteria"]["6"]["status"],
        )

    @mock.patch.object(subject.source_identity, "verify_repository")
    @mock.patch.object(subject.base_audit, "audit_resolution")
    def test_existing_other_blocker_is_preserved(
        self, base_audit, verify_repository
    ):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source_repo = root / "tei-b"
            source_repo.mkdir()
            base = self.base_result()
            base["criteria"]["2"]["status"] = subject.base_audit.BLOCKED
            base_audit.return_value = base
            verify_repository.return_value = self.source_verification(source_repo)

            result = subject.audit_local_resolution(
                root / "canonical.json",
                revision_b_source_repo=source_repo,
                sei_repo_root=root / "sei",
            )

        self.assertFalse(result["resolutionCandidate"])
        self.assertEqual([2], result["automatedCriteria"]["blockedOrManual"])
        self.assertEqual(
            subject.base_audit.SATISFIED,
            result["criteria"]["6"]["status"],
        )


if __name__ == "__main__":
    unittest.main()
