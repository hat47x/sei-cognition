import copy
import json
import tempfile
import unittest
from contextlib import nullcontext
from pathlib import Path
from unittest import mock

import run_tei_version_exchange_resume_from_e2_partial as subject


class TEIVersionExchangeResumeFromE2PartialTest(unittest.TestCase):
    def _observation(self):
        return {
            "source_commit": subject.source_identity.REVISION_B,
            "binary_sha256": "b" * 64,
            "provider_plan_sha256": "p" * 64,
            "archive_sha256": "a" * 64,
        }

    def _source_provenance(self):
        return {
            "mode": subject.SOURCE_ACQUISITION_MODE,
            "repository": subject.source_acquisition.GITHUB_REPOSITORY,
            "sourceCommit": subject.source_identity.REVISION_B,
            "rootTree": subject.source_acquisition.REVISION_B_ROOT_TREE,
            "credentialSource": "environment",
            "objectAcquisition": {
                "apiRequests": 10,
                "treesMaterialized": 3,
                "uniqueBlobsMaterialized": 7,
                "blobBytesMaterialized": 1024,
            },
            "canonicalSourceVerification": {
                "head": subject.source_identity.REVISION_B,
                "expectedHead": subject.source_identity.REVISION_B,
                "expectedHeadMatched": True,
                "revisionBExactHead": True,
                "executionSourceObjects": dict(subject.source_identity.EXPECTED_OBJECTS),
                "worktreeCleanWithinBoundary": True,
            },
        }

    def _partial_report(self):
        observation = self._observation()
        return {
            "schema": subject.partial_runner.SCHEMA,
            "result": "e2_bundle_verified_e3_not_run",
            "sourceAcquisition": self._source_provenance(),
            "comparisonAxis": {
                "buildSourceCommit": subject.source_identity.REVISION_B,
                "referenceInputSourceCommit": subject.source_identity.REVISION_A,
                "referenceInputAcquisition": "historical_evidence_bundle",
                "referenceInputBundle": "/historical/a.tar.gz",
                "teiGoRequirement": subject.partial_runner.e2_runner.EXPECTED_GO_VERSION,
                "teiGoExecutable": "/toolchains/go1.23.2/bin/go",
                "e3IntentionallyNotRun": True,
            },
            "bundleArchive": "/old/location/revision-b-e2-partial.tar.gz",
            "e2": {
                "result": "bundle_produced",
                "bundle": {
                    "result": "verified",
                    "observation": observation,
                },
                "completedStages": [
                    "revision_b_source_identity",
                    "revision_a_fixed_reference_identity",
                    "execution_platform",
                    "tei_go_toolchain",
                    "tei_cli_build",
                    "deployment_provider_plan_execution",
                    "provider_plan_validation",
                    "evidence_bundle_verification",
                    "evidence_bundle_publish",
                ],
                "qualityJudgement": "not_evaluated",
            },
            "e3": None,
            "qualityJudgement": "not_evaluated",
        }

    def _verification(self):
        return {
            "result": "verified",
            "observation": self._observation(),
            "referenceInput": dict(subject.fixed_reference.EXPECTED_REFERENCE),
        }

    def _loaded_partial(self, partial_report: Path, bundle: Path):
        validated = subject._validate_partial_report(
            self._partial_report(),
            self._verification(),
        )
        return {
            **validated,
            "partialReport": str(partial_report.resolve()),
            "bundleArchive": str(bundle.resolve()),
            "bundleVerification": self._verification(),
        }

    def test_validate_partial_rejects_bundle_identity_mismatch(self):
        report = self._partial_report()
        verification = self._verification()
        verification["observation"]["archive_sha256"] = "c" * 64

        with self.assertRaisesRegex(ValueError, "identityが一致しません"):
            subject._validate_partial_report(report, verification)

    def test_load_partial_reverifies_bundle_against_fixed_revision_a(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            partial = root / "partial.json"
            bundle = root / "bundle.tar.gz"
            partial.write_text(
                json.dumps(self._partial_report(), ensure_ascii=False),
                encoding="utf-8",
            )
            bundle.write_bytes(b"placeholder")

            with mock.patch.object(
                subject.bundle_verifier,
                "verify_bundle",
                return_value=self._verification(),
            ) as verifier:
                loaded = subject._load_partial_evidence(partial, bundle)

            verifier.assert_called_once_with(
                bundle.resolve(),
                expected_source_commit=subject.source_identity.REVISION_B,
                expected_reference_input=subject.fixed_reference.EXPECTED_REFERENCE,
            )
            self.assertEqual(str(partial.resolve()), loaded["partialReport"])
            self.assertEqual(str(bundle.resolve()), loaded["bundleArchive"])

    def test_resume_success_reuses_e2_and_writes_canonical_and_wrapper_reports(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            partial_report = root / "partial.json"
            bundle = root / "bundle.tar.gz"
            sei = root / "sei"
            output = root / "evidence"
            go = root / "go125" / "go"
            partial_report.write_text("{}", encoding="utf-8")
            bundle.write_bytes(b"placeholder")
            sei.mkdir()
            loaded = self._loaded_partial(partial_report, bundle)
            e3 = {
                "result": "adapter_compatible",
                "seiGoRequirement": "go1.25.0",
                "seiGoVersion": "go version go1.25.1 linux/amd64",
                "seiSource": {"head": "sei-head"},
                "postLiveTestSeiSource": {"head": "sei-head"},
            }

            with mock.patch.object(
                subject,
                "_load_partial_evidence",
                return_value=loaded,
            ), mock.patch.object(
                subject.version_exchange,
                "_go_on_path",
                return_value=nullcontext(go),
            ), mock.patch.object(
                subject.adapter_runner,
                "run_compatibility",
                return_value=e3,
            ) as adapter, mock.patch.object(
                subject.github_runner,
                "_write_report",
            ) as writer, mock.patch.object(
                subject.partial_runner.e2_runner,
                "produce_bundle",
                side_effect=AssertionError("E2 must not be rerun"),
            ), mock.patch.object(
                subject.source_acquisition,
                "materialize_revision_b_source",
                side_effect=AssertionError("revision B source must not be reacquired"),
            ):
                result = subject.resume_e3(
                    partial_report,
                    bundle,
                    sei,
                    output,
                    sei_go_executable=go,
                    expected_sei_head="sei-head",
                )

            adapter.assert_called_once_with(
                bundle.resolve(),
                sei_repo_root=sei.resolve(),
                expected_source_commit=subject.source_identity.REVISION_B,
                expected_sei_head="sei-head",
            )
            self.assertEqual("fixed_scope_e2_e3_verified", result["result"])
            self.assertEqual(2, writer.call_count)
            canonical = writer.call_args_list[0].args[1]
            wrapper = writer.call_args_list[1].args[1]
            self.assertEqual(subject.version_exchange.SCHEMA, canonical["schema"])
            self.assertEqual("fixed_scope_e2_e3_verified", canonical["result"])
            self.assertEqual(loaded["e2"], canonical["e2"])
            self.assertEqual(e3, canonical["e3"])
            self.assertEqual(subject.EXECUTION_MODE, canonical["executionProvenance"]["mode"])
            self.assertEqual(
                "go version go1.25.1 linux/amd64",
                canonical["comparisonAxis"]["seiGoObserved"],
            )
            self.assertEqual(subject.github_runner.SCHEMA, wrapper["schema"])
            self.assertEqual("fixed_scope_e2_e3_verified", wrapper["result"])
            self.assertEqual(subject.EXECUTION_MODE, wrapper["executionMode"])
            self.assertEqual(loaded["sourceAcquisition"], wrapper["sourceAcquisition"])

    def test_resume_e3_failure_preserves_canonical_e2_and_stage(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            partial_report = root / "partial.json"
            bundle = root / "bundle.tar.gz"
            sei = root / "sei"
            output = root / "evidence"
            go = root / "go125" / "go"
            partial_report.write_text("{}", encoding="utf-8")
            bundle.write_bytes(b"placeholder")
            sei.mkdir()
            loaded = self._loaded_partial(partial_report, bundle)
            failure = subject.adapter_runner.TEIAdapterStageError(
                "sei_teiintegration_live_test",
                "live test failed",
            )

            with mock.patch.object(
                subject,
                "_load_partial_evidence",
                return_value=loaded,
            ), mock.patch.object(
                subject.version_exchange,
                "_go_on_path",
                return_value=nullcontext(go),
            ), mock.patch.object(
                subject.adapter_runner,
                "run_compatibility",
                side_effect=failure,
            ), mock.patch.object(
                subject.github_runner,
                "_write_report",
            ) as writer:
                with self.assertRaises(subject.ResumeE3Failed):
                    subject.resume_e3(
                        partial_report,
                        bundle,
                        sei,
                        output,
                        sei_go_executable=go,
                    )

            self.assertEqual(2, writer.call_count)
            canonical = writer.call_args_list[0].args[1]
            wrapper = writer.call_args_list[1].args[1]
            self.assertEqual("e2_verified_e3_failed", canonical["result"])
            self.assertEqual(loaded["e2"], canonical["e2"])
            self.assertIsNone(canonical["e3"])
            self.assertEqual("E3", canonical["failure"]["stage"])
            self.assertEqual(
                "sei_teiintegration_live_test",
                canonical["failure"]["substage"],
            )
            self.assertEqual("version_exchange_failed", wrapper["result"])
            self.assertEqual("E3", wrapper["failure"]["stage"])

    def test_source_provenance_mismatch_is_rejected(self):
        report = self._partial_report()
        report["sourceAcquisition"]["sourceCommit"] = "0" * 40

        with self.assertRaisesRegex(ValueError, "sourceCommit"):
            subject._validate_partial_report(report, self._verification())

    def test_output_collision_is_rejected_without_mutation(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            partial_report = root / "partial.json"
            bundle = root / "bundle.tar.gz"
            sei = root / "sei"
            output = root / "evidence"
            partial_report.write_text("{}", encoding="utf-8")
            bundle.write_bytes(b"placeholder")
            sei.mkdir()
            output.mkdir()
            existing = output / subject.version_exchange.REPORT_NAME
            existing.write_text("existing", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "--overwrite"):
                subject._prepare_output_reports(
                    output,
                    sei_repo_root=sei,
                    partial_report=partial_report,
                    bundle=bundle,
                    overwrite=False,
                )

            self.assertEqual("existing", existing.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
