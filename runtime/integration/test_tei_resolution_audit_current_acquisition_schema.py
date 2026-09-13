import json
import tempfile
import unittest
from pathlib import Path

import audit_tei_version_exchange_resolution as subject


class TEIResolutionAuditCurrentAcquisitionSchemaTest(unittest.TestCase):
    def test_current_wrapper_acquisition_provenance_is_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            wrapper = root / "wrapper.json"
            wrapper.write_text(
                json.dumps(
                    {
                        "schema": subject.WRAPPER_SCHEMA,
                        "result": "fixed_scope_e2_e3_verified",
                        "sourceAcquisition": {
                            "mode": subject.CURRENT_GITHUB_ACQUISITION_MODE,
                            "repository": subject.github_source.GITHUB_REPOSITORY,
                            "sourceCommit": subject.source_identity.REVISION_B,
                            "rootTree": subject.github_source.REVISION_B_ROOT_TREE,
                            "credentialSource": "environment",
                            "canonicalSourceVerification": {
                                "revisionBExactHead": True,
                                "worktreeCleanWithinBoundary": True,
                            },
                        },
                    }
                ),
                encoding="utf-8",
            )
            axis = {
                "referenceInputAcquisition": "historical_evidence_bundle",
            }
            canonical = {"result": "fixed_scope_e2_e3_verified"}

            criterion, observed = subject._boundary_criterion(
                axis,
                canonical,
                wrapper,
            )

        self.assertEqual(subject.SATISFIED, criterion["status"])
        self.assertIsNotNone(observed)
        provenance = criterion["detail"]["sourceAcquisition"]
        self.assertEqual(
            subject.CURRENT_GITHUB_ACQUISITION_MODE,
            provenance["mode"],
        )
        self.assertEqual("environment", provenance["credentialSource"])


if __name__ == "__main__":
    unittest.main()
