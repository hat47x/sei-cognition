import tempfile
import unittest
from pathlib import Path
from unittest import mock

import preflight_tei_version_exchange_local as subject


class LocalPreflightTest(unittest.TestCase):
    def patch_common_ready(self):
        patches = [
            mock.patch.object(subject.common, "_check_platform", return_value={"linuxAmd64": True}),
            mock.patch.object(subject.common, "_check_reference_input", return_value={"mode": "historical_evidence_bundle"}),
            mock.patch.object(subject.common, "_check_soza_source", return_value={"head": "s" * 40}),
            mock.patch.object(subject.common, "_check_tei_go", return_value={"exactMatch": True}),
            mock.patch.object(subject.common, "_check_soza_go", return_value={"requirementSatisfied": True}),
        ]
        return patches

    @mock.patch.object(subject, "_check_evidence_output_path")
    @mock.patch.object(subject, "_check_checkout_output_path")
    @mock.patch.object(subject, "_check_source_clone")
    def test_ready_without_credential_or_network(
        self, check_source, check_checkout, check_output
    ):
        patches = self.patch_common_ready()
        for patcher in patches:
            patcher.start()
            self.addCleanup(patcher.stop)
        check_source.return_value = {"sourceObjectDatabaseSelfContained": True}
        check_checkout.return_value = {"newPathRequired": True}
        check_output.return_value = {"staticPathSafetyVerified": True}

        result = subject.run_preflight(
            Path("/src"),
            Path("/checkout"),
            None,
            Path("/soza"),
            Path("/evidence"),
            reference_evidence_bundle=Path("/a.tar.gz"),
            tei_go_executable=Path("/go123/bin/go"),
            soza_go_executable=Path("/go125/bin/go"),
        )

        self.assertTrue(result["ready"])
        self.assertFalse(result["credentialRequired"])
        self.assertFalse(result["networkAccessPerformed"])
        self.assertNotIn("github_credential", [c["name"] for c in result["checks"]])

    @mock.patch.object(subject, "_check_evidence_output_path")
    @mock.patch.object(subject, "_check_checkout_output_path")
    @mock.patch.object(subject, "_check_source_clone")
    def test_multiple_blockers_are_aggregated(
        self, check_source, check_checkout, check_output
    ):
        patches = self.patch_common_ready()
        for patcher in patches:
            patcher.start()
            self.addCleanup(patcher.stop)
        check_source.side_effect = ValueError("missing B")
        check_checkout.side_effect = ValueError("checkout exists")
        check_output.return_value = {"staticPathSafetyVerified": True}

        result = subject.run_preflight(
            Path("/src"),
            Path("/checkout"),
            None,
            Path("/soza"),
            Path("/evidence"),
            reference_evidence_bundle=Path("/a.tar.gz"),
            tei_go_executable=Path("/go123/bin/go"),
            soza_go_executable=Path("/go125/bin/go"),
        )

        self.assertFalse(result["ready"])
        self.assertEqual(
            ["revision_b_source_clone", "revision_b_checkout_output_path"],
            result["blockedChecks"],
        )

    @mock.patch.object(subject.checkout_prepare, "_source_state")
    @mock.patch.object(subject.checkout_prepare, "_ensure_revision_available")
    @mock.patch.object(subject.checkout_prepare, "_ensure_self_contained_object_database")
    @mock.patch.object(subject.checkout_prepare, "_ensure_git_worktree")
    @mock.patch.object(subject, "_git")
    def test_source_clone_checks_fixed_revision_b_objects(
        self, run_git, ensure_worktree, ensure_self_contained, ensure_revision, source_state
    ):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            values = iter(subject.source_identity.EXPECTED_OBJECTS.values())
            run_git.side_effect = [
                mock.Mock(stdout=value + "\n", returncode=0, stderr="")
                for value in values
            ]
            source_state.return_value = {"head": "branch-head", "status": []}

            observation = subject._check_source_clone(repo)

        ensure_worktree.assert_called_once()
        ensure_self_contained.assert_called_once()
        ensure_revision.assert_called_once()
        self.assertEqual(
            subject.source_identity.EXPECTED_OBJECTS,
            observation["revisionBExecutionSourceObjects"],
        )
        self.assertFalse(observation["networkAccessPerformed"])
        self.assertFalse(observation["filesystemMutationPerformed"])

    @mock.patch.object(subject.checkout_prepare, "_source_state")
    @mock.patch.object(subject.checkout_prepare, "_ensure_revision_available")
    @mock.patch.object(subject.checkout_prepare, "_ensure_self_contained_object_database")
    @mock.patch.object(subject.checkout_prepare, "_ensure_git_worktree")
    @mock.patch.object(subject, "_git")
    def test_source_object_drift_blocks(
        self, run_git, ensure_worktree, ensure_self_contained, ensure_revision, source_state
    ):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            expected = list(subject.source_identity.EXPECTED_OBJECTS.values())
            expected[0] = "f" * 40
            run_git.side_effect = [
                mock.Mock(stdout=value + "\n", returncode=0, stderr="")
                for value in expected
            ]
            source_state.return_value = {"head": "branch-head", "status": []}
            with self.assertRaisesRegex(ValueError, "object identity"):
                subject._check_source_clone(repo)

    def test_checkout_and_evidence_overlap_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source"
            soza = root / "soza"
            source.mkdir()
            soza.mkdir()
            evidence = root / "workspace"
            checkout = evidence / "tei-b"
            evidence.mkdir()
            with self.assertRaisesRegex(ValueError, "Evidence directory"):
                subject._check_checkout_output_path(
                    checkout,
                    source_repo=source,
                    soza_repo_root=soza,
                    reference_source_repo=None,
                    reference_evidence_bundle=None,
                    evidence_output_dir=evidence,
                )

    def test_existing_checkout_output_is_rejected_without_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            checkout = root / "tei-b"
            checkout.mkdir()
            with self.assertRaisesRegex(ValueError, "新規path"):
                subject._normalized_new_path(checkout, "revision B checkout output")
            self.assertTrue(checkout.is_dir())


if __name__ == "__main__":
    unittest.main()
