import unittest
from pathlib import Path
from unittest import mock

import verify_tei_version_exchange_e2_bundle as subject


class TEIVersionExchangeE2BundleVerifierTest(unittest.TestCase):
    def test_strict_verifier_binds_exact_b_and_exact_a_without_predeclared_output_hashes(self):
        verification = {
            "archive": "/evidence/revision-b.tar.gz",
            "observation": {
                "source_commit": subject.source_identity.REVISION_B,
                "binary_sha256": "1" * 64,
                "provider_plan_sha256": "2" * 64,
                "archive_sha256": "3" * 64,
            },
            "referenceInput": dict(subject.fixed_reference.EXPECTED_REFERENCE),
        }

        with mock.patch.object(
            subject.bundle_verifier,
            "verify_bundle",
            return_value=verification,
        ) as verifier:
            result = subject.verify_version_exchange_e2_bundle(
                Path("/evidence/revision-b.tar.gz")
            )

        verifier.assert_called_once_with(
            Path("/evidence/revision-b.tar.gz"),
            expected_source_commit=subject.source_identity.REVISION_B,
            expected_reference_input=subject.fixed_reference.EXPECTED_REFERENCE,
        )
        kwargs = verifier.call_args.kwargs
        self.assertNotIn("expected_binary_sha256", kwargs)
        self.assertNotIn("expected_provider_plan_sha256", kwargs)
        self.assertEqual("verified", result["result"])
        self.assertEqual(subject.source_identity.REVISION_B, result["observation"]["source_commit"])
        self.assertEqual(
            subject.source_identity.REVISION_A,
            result["referenceInput"]["source_commit"],
        )
        self.assertEqual("not_evaluated", result["qualityJudgement"])

    def test_underlying_identity_failure_is_not_reinterpreted(self):
        failure = ValueError("actual fixed reference input Git object identity mismatch")
        with mock.patch.object(
            subject.bundle_verifier,
            "verify_bundle",
            side_effect=failure,
        ):
            with self.assertRaisesRegex(ValueError, "fixed reference input"):
                subject.verify_version_exchange_e2_bundle(Path("/evidence/bad.tar.gz"))


if __name__ == "__main__":
    unittest.main()
