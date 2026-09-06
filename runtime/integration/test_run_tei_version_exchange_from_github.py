import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import run_tei_version_exchange_from_github as subject


TEST_CREDENTIAL = "placeholder"


class GitHubAcquiredVersionExchangeRunnerTest(unittest.TestCase):
    def acquisition_result(self) -> dict[str, object]:
        return {
            "result": "verified",
            "sourceAcquisition": "github-git-data-api-content-addressed",
            "repository": "example/repository",
            "sourceCommit": "b" * 40,
            "rootTree": "c" * 40,
            "credentialSource": "environment",
            "objectAcquisition": {
                "apiRequests": 10,
                "treesMaterialized": 3,
                "uniqueBlobsMaterialized": 7,
                "blobBytesMaterialized": 1234,
            },
            "canonicalSourceVerification": {
                "repositoryRoot": "/temporary/source",
                "head": "b" * 40,
                "expectedHead": "b" * 40,
                "expectedHeadMatched": True,
                "revisionBExactHead": True,
                "executionSourceObjects": {"cmd": "d" * 40},
                "worktreeCleanWithinBoundary": True,
            },
        }

    def materialize(self, result: dict[str, object]):
        def run(path: Path, *, token: str):
            self.assertEqual(TEST_CREDENTIAL, token)
            self.assertFalse(path.exists())
            path.mkdir(parents=True)
            return result

        return run

    def test_success_delegates_to_canonical_runner_and_persists_provenance(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = root / "evidence"
            observed_source: list[Path] = []

            def run_exchange(source_repo: Path, *args, **kwargs):
                self.assertTrue(source_repo.is_dir())
                observed_source.append(source_repo)
                output.mkdir(parents=True, exist_ok=True)
                return {
                    "result": "fixed_scope_e2_e3_verified",
                    "comparisonAxis": {"buildSourceCommit": "b" * 40},
                    "bundleArchive": str(output / "bundle.tar.gz"),
                }

            with mock.patch.object(
                subject.source_acquisition,
                "materialize_revision_b_source",
                side_effect=self.materialize(self.acquisition_result()),
            ), mock.patch.object(
                subject.version_exchange,
                "run_version_exchange",
                side_effect=run_exchange,
            ):
                result = subject.run_from_github(
                    None,
                    root / "soza",
                    output,
                    reference_evidence_bundle=root / "a.tar.gz",
                    tei_go_executable=root / "go123" / "go",
                    soza_go_executable=root / "go125" / "go",
                    token=TEST_CREDENTIAL,
                )

            self.assertEqual("fixed_scope_e2_e3_verified", result["result"])
            self.assertEqual(
                "github-git-data-api-content-addressed",
                result["sourceAcquisition"]["mode"],
            )
            self.assertNotIn(
                "repositoryRoot",
                result["sourceAcquisition"]["canonicalSourceVerification"],
            )
            self.assertEqual(1, len(observed_source))
            self.assertFalse(observed_source[0].exists())
            persisted = json.loads(
                (output / subject.REPORT_NAME).read_text(encoding="utf-8")
            )
            self.assertEqual(result, persisted)

    def test_acquisition_failure_does_not_start_canonical_runner(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(
            subject.source_acquisition,
            "materialize_revision_b_source",
            side_effect=ValueError("acquisition failed"),
        ), mock.patch.object(
            subject.version_exchange,
            "run_version_exchange",
        ) as exchange_mock:
            with self.assertRaisesRegex(ValueError, "acquisition failed"):
                subject.run_from_github(
                    None,
                    Path(tmp) / "soza",
                    Path(tmp) / "evidence",
                    reference_evidence_bundle=Path(tmp) / "a.tar.gz",
                    tei_go_executable=Path(tmp) / "go123" / "go",
                    soza_go_executable=Path(tmp) / "go125" / "go",
                    token=TEST_CREDENTIAL,
                )
        exchange_mock.assert_not_called()

    def test_canonical_failure_persists_acquisition_provenance(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = root / "evidence"
            canonical_report = output / subject.version_exchange.REPORT_NAME

            def fail_exchange(*args, **kwargs):
                output.mkdir(parents=True, exist_ok=True)
                canonical_report.write_text("{}\n", encoding="utf-8")
                raise subject.version_exchange.VersionExchangeRunFailed(
                    "E2",
                    canonical_report,
                    ValueError("provider failed"),
                )

            with mock.patch.object(
                subject.source_acquisition,
                "materialize_revision_b_source",
                side_effect=self.materialize(self.acquisition_result()),
            ), mock.patch.object(
                subject.version_exchange,
                "run_version_exchange",
                side_effect=fail_exchange,
            ):
                with self.assertRaises(subject.GitHubAcquiredVersionExchangeFailed):
                    subject.run_from_github(
                        None,
                        root / "soza",
                        output,
                        reference_evidence_bundle=root / "a.tar.gz",
                        tei_go_executable=root / "go123" / "go",
                        soza_go_executable=root / "go125" / "go",
                        token=TEST_CREDENTIAL,
                    )

            persisted = json.loads(
                (output / subject.REPORT_NAME).read_text(encoding="utf-8")
            )
            self.assertEqual("version_exchange_failed", persisted["result"])
            self.assertEqual("E2", persisted["failure"]["stage"])
            self.assertEqual(
                "github-git-data-api-content-addressed",
                persisted["sourceAcquisition"]["mode"],
            )

    def test_existing_wrapper_report_requires_overwrite_before_acquisition(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = root / "evidence"
            output.mkdir()
            (output / subject.REPORT_NAME).write_text("old\n", encoding="utf-8")
            with mock.patch.object(
                subject.source_acquisition,
                "materialize_revision_b_source",
            ) as acquire_mock:
                with self.assertRaisesRegex(ValueError, "--overwrite"):
                    subject.run_from_github(
                        None,
                        root / "soza",
                        output,
                        reference_evidence_bundle=root / "a.tar.gz",
                        tei_go_executable=root / "go123" / "go",
                        soza_go_executable=root / "go125" / "go",
                        token=TEST_CREDENTIAL,
                    )
            acquire_mock.assert_not_called()


if __name__ == "__main__":
    unittest.main()
