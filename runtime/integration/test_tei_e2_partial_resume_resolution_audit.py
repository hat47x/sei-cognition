import json
import tempfile
import unittest
from pathlib import Path

import audit_tei_version_exchange_resolution as audit
import run_tei_version_exchange_resume_from_e2_partial as subject


class TEIE2PartialResumeResolutionAuditTest(unittest.TestCase):
    def _source(self):
        return {
            "mode": subject.SOURCE_ACQUISITION_MODE,
            "repository": subject.source_acquisition.GITHUB_REPOSITORY,
            "sourceCommit": subject.source_identity.REVISION_B,
            "rootTree": subject.source_acquisition.REVISION_B_ROOT_TREE,
            "credentialSource": "environment",
            "objectAcquisition": {"apiRequests": 1},
            "canonicalSourceVerification": {
                "head": subject.source_identity.REVISION_B,
                "expectedHead": subject.source_identity.REVISION_B,
                "expectedHeadMatched": True,
                "revisionBExactHead": True,
                "executionSourceObjects": dict(subject.source_identity.EXPECTED_OBJECTS),
                "worktreeCleanWithinBoundary": True,
            },
        }

    def _axis(self):
        return {
            "buildSourceCommit": subject.source_identity.REVISION_B,
            "referenceInputSourceCommit": subject.source_identity.REVISION_A,
            "referenceInputAcquisition": "historical_evidence_bundle",
            "referenceInputBundle": "/historical/a.tar.gz",
            "teiGoRequirement": subject.partial_runner.e2_runner.EXPECTED_GO_VERSION,
            "seiGoRequirement": "go1.25.0",
            "teiGoExecutable": "/toolchains/go1.23.2/bin/go",
            "seiGoExecutable": "/toolchains/go1.25/bin/go",
            "expectedSeiHead": "sei-head",
            "seiGoObserved": "go version go1.25.1 linux/amd64",
        }

    def test_resumed_success_is_accepted_by_existing_resolution_audit_boundaries(self):
        axis = self._axis()
        e2 = {
            "result": "bundle_produced",
            "completedStages": ["tei_cli_build", "evidence_bundle_verification"],
        }
        e3 = {
            "result": "adapter_compatible",
            "seiSource": {"head": "sei-head"},
            "postLiveTestSeiSource": {"head": "sei-head"},
        }
        canonical = {
            "schema": subject.version_exchange.SCHEMA,
            "result": "fixed_scope_e2_e3_verified",
            "comparisonAxis": axis,
            "bundleArchive": "/evidence/revision-b.tar.gz",
            "e2": e2,
            "e3": e3,
            "executionProvenance": {
                "mode": subject.EXECUTION_MODE,
                "partialEvidenceReport": "/evidence/partial.json",
                "bundleArchive": "/evidence/revision-b.tar.gz",
            },
            "qualityJudgement": "not_evaluated",
            "stopLine": subject.version_exchange.STOP_LINE,
        }
        wrapper = subject._wrapper_report(
            result="fixed_scope_e2_e3_verified",
            source=self._source(),
            canonical_path=Path("/evidence/tei-version-exchange-evidence.json"),
            partial_report="/evidence/partial.json",
            bundle_archive="/evidence/revision-b.tar.gz",
            comparison_axis=axis,
        )

        validated_axis = audit._validate_canonical(canonical)
        self.assertEqual("fixed_scope_e2_e3_verified", validated_axis["result"])
        self.assertEqual("satisfied", audit._e2_criterion(canonical)["status"])
        self.assertEqual("satisfied", audit._e3_criterion(canonical)["status"])

        with tempfile.TemporaryDirectory() as temporary:
            wrapper_path = Path(temporary) / "wrapper.json"
            wrapper_path.write_text(
                json.dumps(wrapper, ensure_ascii=False),
                encoding="utf-8",
            )
            criterion, observed = audit._boundary_criterion(
                validated_axis,
                canonical,
                wrapper_path,
            )

        self.assertEqual("satisfied", criterion["status"])
        self.assertEqual(subject.EXECUTION_MODE, observed["executionMode"])
        self.assertEqual(
            subject.SOURCE_ACQUISITION_MODE,
            criterion["detail"]["sourceAcquisition"]["mode"],
        )

    def test_resumed_e3_failure_keeps_audit_stage_semantics(self):
        axis = self._axis()
        canonical = {
            "schema": subject.version_exchange.SCHEMA,
            "result": "e2_verified_e3_failed",
            "comparisonAxis": axis,
            "bundleArchive": "/evidence/revision-b.tar.gz",
            "e2": {"result": "bundle_produced"},
            "e3": None,
            "failure": {
                "stage": "E3",
                "substage": "sei_teiintegration_live_test",
                "type": "TEIAdapterStageError",
                "message": "failure",
            },
            "qualityJudgement": "not_evaluated",
        }

        validated_axis = audit._validate_canonical(canonical)
        e3_criterion = audit._e3_criterion(canonical)

        self.assertEqual("e2_verified_e3_failed", validated_axis["result"])
        self.assertEqual("satisfied", e3_criterion["status"])
        self.assertEqual("failed", e3_criterion["detail"]["outcome"])
        self.assertEqual(
            "sei_teiintegration_live_test",
            e3_criterion["detail"]["substage"],
        )


if __name__ == "__main__":
    unittest.main()
