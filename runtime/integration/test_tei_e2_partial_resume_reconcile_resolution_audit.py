import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import audit_tei_version_exchange_resolution as audit
import reconcile_tei_e2_partial_resume_reports as reconcile
import run_tei_version_exchange_resume_from_e2_partial as resume


class TEIE2PartialResumeReconcileResolutionAuditTest(unittest.TestCase):
    def _source(self):
        return {
            "mode": resume.SOURCE_ACQUISITION_MODE,
            "repository": resume.source_acquisition.GITHUB_REPOSITORY,
            "sourceCommit": resume.source_identity.REVISION_B,
            "rootTree": resume.source_acquisition.REVISION_B_ROOT_TREE,
            "credentialSource": "environment",
            "objectAcquisition": {"apiRequests": 1},
            "canonicalSourceVerification": {
                "head": resume.source_identity.REVISION_B,
                "expectedHead": resume.source_identity.REVISION_B,
                "expectedHeadMatched": True,
                "revisionBExactHead": True,
                "executionSourceObjects": dict(resume.source_identity.EXPECTED_OBJECTS),
                "worktreeCleanWithinBoundary": True,
            },
        }

    def test_reconstructed_wrapper_is_accepted_by_existing_resolution_audit_boundary(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            partial_report = root / "tei-revision-b-e2-github.json"
            bundle = root / "tei-e3b-p2-revision-b-e2-partial.tar.gz"
            evidence = root / "resume"
            evidence.mkdir()
            canonical_path = evidence / reconcile.version_exchange.REPORT_NAME
            wrapper_path = evidence / reconcile.github_runner.REPORT_NAME

            partial_report.write_text("{}", encoding="utf-8")
            bundle.write_bytes(b"placeholder")

            partial_axis = {
                "buildSourceCommit": resume.source_identity.REVISION_B,
                "referenceInputSourceCommit": resume.source_identity.REVISION_A,
                "referenceInputAcquisition": "historical_evidence_bundle",
                "referenceInputBundle": str(root / "historical-a.tar.gz"),
                "teiGoRequirement": resume.partial_runner.e2_runner.EXPECTED_GO_VERSION,
                "teiGoExecutable": "/toolchains/go1.23.2/bin/go",
            }
            e2 = {
                "result": "bundle_produced",
                "completedStages": ["tei_cli_build", "evidence_bundle_verification"],
            }
            partial = {
                "axis": partial_axis,
                "sourceAcquisition": self._source(),
                "e2": e2,
                "partialReport": str(partial_report.resolve()),
                "bundleArchive": str(bundle.resolve()),
            }
            canonical_axis = {
                **partial_axis,
                "seiGoRequirement": "go1.25.0",
                "seiGoExecutable": "/toolchains/go1.25/bin/go",
                "expectedSeiHead": "sei-head",
                "seiGoObserved": "go version go1.25.1 linux/amd64",
            }
            canonical = {
                "schema": reconcile.version_exchange.SCHEMA,
                "result": "fixed_scope_e2_e3_verified",
                "comparisonAxis": canonical_axis,
                "bundleArchive": str(bundle.resolve()),
                "e2": e2,
                "e3": {
                    "result": "adapter_compatible",
                    "seiSource": {"head": "sei-head"},
                    "postLiveTestSeiSource": {"head": "sei-head"},
                },
                "executionProvenance": {
                    "mode": resume.EXECUTION_MODE,
                    "partialEvidenceReport": str(partial_report.resolve()),
                    "bundleArchive": str(bundle.resolve()),
                },
                "qualityJudgement": "not_evaluated",
                "stopLine": reconcile.version_exchange.STOP_LINE,
            }
            canonical_path.write_text(
                json.dumps(canonical, ensure_ascii=False),
                encoding="utf-8",
            )

            with mock.patch.object(
                reconcile.resume_runner,
                "_load_partial_evidence",
                return_value=partial,
            ), mock.patch.object(
                reconcile.resume_runner,
                "resume_e3",
                side_effect=AssertionError("E3 must not rerun during reconcile"),
            ):
                reconciled = reconcile.reconcile(
                    partial_report,
                    bundle,
                    canonical_path,
                )

            self.assertEqual(
                "wrapper_reconstructed_without_e3_rerun",
                reconciled["result"],
            )
            self.assertTrue(wrapper_path.is_file())

            validated_axis = audit._validate_canonical(canonical)
            criterion, observed = audit._boundary_criterion(
                validated_axis,
                canonical,
                wrapper_path,
            )

            self.assertEqual("satisfied", criterion["status"])
            self.assertEqual(resume.EXECUTION_MODE, observed["executionMode"])
            self.assertEqual(
                resume.SOURCE_ACQUISITION_MODE,
                criterion["detail"]["sourceAcquisition"]["mode"],
            )
            self.assertEqual(
                "fixed_scope_e2_e3_verified",
                observed["result"],
            )


if __name__ == "__main__":
    unittest.main()
