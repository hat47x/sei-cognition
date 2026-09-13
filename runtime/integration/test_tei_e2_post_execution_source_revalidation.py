import subprocess
import unittest
from pathlib import Path
from unittest import mock

import run_tei_revision_b_prepositioned as subject
import verify_tei_execution_source_identity as source_identity


class TEIE2PostExecutionSourceRevalidationTest(unittest.TestCase):
    @mock.patch.object(subject.source_identity, "verify_repository")
    def test_git_source_and_reference_are_reverified(self, verify_repository):
        source_repo = Path("/tmp/tei-b")
        reference_repo = Path("/tmp/tei-a")
        source_observation = {
            "result": "verified",
            "head": source_identity.REVISION_B,
        }
        reference_observation = {
            "result": "verified",
            "head": source_identity.REVISION_A,
        }
        verify_repository.side_effect = [source_observation, reference_observation]

        result = subject._reverify_execution_inputs_after_provider(
            source_repo,
            reference_repo,
        )

        self.assertEqual(source_observation, result["source"])
        self.assertEqual(reference_observation, result["referenceInput"])
        self.assertEqual(
            [
                mock.call(source_repo, expected_head=source_identity.REVISION_B),
                mock.call(
                    reference_repo,
                    expected_objects=source_identity.REVISION_A_REFERENCE_OBJECTS,
                    expected_head=source_identity.REVISION_A,
                ),
            ],
            verify_repository.call_args_list,
        )

    @mock.patch.object(subject.source_identity, "verify_repository")
    def test_revision_b_drift_is_rejected_with_existing_stage(self, verify_repository):
        verify_repository.side_effect = ValueError("working tree changed")

        with self.assertRaises(subject.TEIEvidenceStageError) as raised:
            subject._reverify_execution_inputs_after_provider(
                Path("/tmp/tei-b"),
                Path("/tmp/tei-a"),
            )

        self.assertEqual("revision_b_source_identity", raised.exception.stage)
        self.assertIn("Provider Plan実行後", raised.exception.message)
        self.assertIn("working tree changed", raised.exception.message)
        self.assertEqual(1, verify_repository.call_count)

    @mock.patch.object(subject.source_identity, "verify_repository")
    def test_revision_a_drift_is_rejected_with_existing_stage(self, verify_repository):
        verify_repository.side_effect = [
            {"result": "verified", "head": source_identity.REVISION_B},
            ValueError("fixed input changed"),
        ]

        with self.assertRaises(subject.TEIEvidenceStageError) as raised:
            subject._reverify_execution_inputs_after_provider(
                Path("/tmp/tei-b"),
                Path("/tmp/tei-a"),
            )

        self.assertEqual(
            "revision_a_fixed_reference_identity",
            raised.exception.stage,
        )
        self.assertIn("Provider Plan実行後", raised.exception.message)
        self.assertIn("fixed input changed", raised.exception.message)
        self.assertEqual(2, verify_repository.call_count)

    @mock.patch.object(subject.source_identity, "verify_repository")
    def test_historical_bundle_mode_reverifies_only_revision_b(self, verify_repository):
        source_observation = {
            "result": "verified",
            "head": source_identity.REVISION_B,
        }
        verify_repository.return_value = source_observation

        result = subject._reverify_execution_inputs_after_provider(
            Path("/tmp/tei-b"),
            None,
        )

        self.assertEqual(source_observation, result["source"])
        self.assertIsNone(result["referenceInput"])
        verify_repository.assert_called_once_with(
            Path("/tmp/tei-b"),
            expected_head=source_identity.REVISION_B,
        )

    @mock.patch.object(subject.source_identity, "verify_repository")
    def test_subprocess_identity_failure_is_wrapped(self, verify_repository):
        verify_repository.side_effect = subprocess.SubprocessError("git failed")

        with self.assertRaises(subject.TEIEvidenceStageError) as raised:
            subject._reverify_execution_inputs_after_provider(
                Path("/tmp/tei-b"),
                None,
            )

        self.assertEqual("revision_b_source_identity", raised.exception.stage)
        self.assertIn("git failed", raised.exception.message)


if __name__ == "__main__":
    unittest.main()
