import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import reconcile_tei_e2_partial_resume_reports as subject


class TEIE2PartialResumeReportReconcileTest(unittest.TestCase):
    def _fixture(self, root: Path):
        partial_report = root / "partial.json"
        bundle = root / "bundle.tar.gz"
        evidence = root / "evidence"
        evidence.mkdir()
        canonical = evidence / subject.version_exchange.REPORT_NAME
        partial_report.write_text("{}", encoding="utf-8")
        bundle.write_bytes(b"bundle")
        axis = {
            "buildSourceCommit": "b" * 40,
            "referenceInputSourceCommit": "a" * 40,
            "referenceInputAcquisition": "historical_evidence_bundle",
            "referenceInputBundle": str(root / "a.tar.gz"),
            "teiGoRequirement": "go1.23.2",
            "teiGoExecutable": "/opt/go1.23.2/bin/go",
        }
        e2 = {
            "result": "bundle_produced",
            "completedStages": ["build", "deployment_provider_plan_execution"],
            "bundle": {
                "observation": {
                    "source_commit": "b" * 40,
                    "binary_sha256": "1" * 64,
                    "provider_plan_sha256": "2" * 64,
                    "archive_sha256": "3" * 64,
                }
            },
        }
        partial = {
            "axis": axis,
            "sourceAcquisition": {
                "mode": "github-git-data-api-content-addressed",
                "repository": "hat47x/tei-platform",
                "sourceCommit": "b" * 40,
            },
            "e2": e2,
            "partialReport": str(partial_report.resolve()),
            "bundleArchive": str(bundle.resolve()),
        }
        return partial_report, bundle, canonical, partial

    def _canonical(self, partial, *, result="fixed_scope_e2_e3_verified"):
        value = {
            "schema": subject.version_exchange.SCHEMA,
            "result": result,
            "comparisonAxis": {
                **partial["axis"],
                "sozaGoRequirement": "1.25",
                "sozaGoExecutable": "/opt/go1.25/bin/go",
                "sozaGoObserved": "go version go1.25.0 linux/amd64",
                "expectedSozaHead": "c" * 40,
            },
            "bundleArchive": partial["bundleArchive"],
            "e2": partial["e2"],
            "executionProvenance": {
                "mode": subject.resume_runner.EXECUTION_MODE,
                "partialEvidenceReport": partial["partialReport"],
                "bundleArchive": partial["bundleArchive"],
            },
            "qualityJudgement": "not_evaluated",
            "stopLine": subject.version_exchange.STOP_LINE,
        }
        if result == "fixed_scope_e2_e3_verified":
            value["e3"] = {"result": "adapter_compatible"}
        else:
            value["e3"] = None
            value["failure"] = {
                "stage": "E3",
                "type": "TEIAdapterStageError",
                "message": "live test failed",
                "substage": "soza_teiintegration_live_test",
            }
        return value

    def test_missing_wrapper_is_reconstructed_without_e3_rerun(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            partial_report, bundle, canonical_path, partial = self._fixture(root)
            canonical = self._canonical(partial)
            canonical_path.write_text(json.dumps(canonical), encoding="utf-8")

            with mock.patch.object(
                subject.resume_runner,
                "_load_partial_evidence",
                return_value=partial,
            ), mock.patch.object(
                subject.github_runner,
                "_write_report",
            ) as writer, mock.patch.object(
                subject.resume_runner,
                "resume_e3",
                side_effect=AssertionError("E3 must not rerun"),
            ):
                result = subject.reconcile(partial_report, bundle, canonical_path)

            self.assertEqual(
                "wrapper_reconstructed_without_e3_rerun",
                result["result"],
            )
            writer.assert_called_once()
            wrapper_path, wrapper = writer.call_args.args[:2]
            self.assertEqual(
                canonical_path.parent / subject.github_runner.REPORT_NAME,
                wrapper_path,
            )
            self.assertEqual("fixed_scope_e2_e3_verified", wrapper["result"])
            self.assertEqual(str(canonical_path.resolve()), wrapper["canonicalVersionExchangeReport"])

    def test_e3_failure_wrapper_is_reconstructed_with_e3_stage(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            partial_report, bundle, canonical_path, partial = self._fixture(root)
            canonical = self._canonical(partial, result="e2_verified_e3_failed")
            canonical_path.write_text(json.dumps(canonical), encoding="utf-8")

            with mock.patch.object(
                subject.resume_runner,
                "_load_partial_evidence",
                return_value=partial,
            ), mock.patch.object(
                subject.github_runner,
                "_write_report",
            ) as writer:
                result = subject.reconcile(partial_report, bundle, canonical_path)

            self.assertEqual("e2_verified_e3_failed", result["canonicalResult"])
            wrapper = writer.call_args.args[1]
            self.assertEqual("version_exchange_failed", wrapper["result"])
            self.assertEqual("E3", wrapper["failure"]["stage"])
            self.assertEqual("TEIAdapterStageError", wrapper["failure"]["type"])

    def test_existing_consistent_wrapper_is_noop(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            partial_report, bundle, canonical_path, partial = self._fixture(root)
            canonical = self._canonical(partial)
            canonical_path.write_text(json.dumps(canonical), encoding="utf-8")
            wrapper_path = canonical_path.parent / subject.github_runner.REPORT_NAME
            expected = subject.resume_runner._wrapper_report(
                result="fixed_scope_e2_e3_verified",
                source=partial["sourceAcquisition"],
                canonical_path=canonical_path.resolve(),
                partial_report=partial["partialReport"],
                bundle_archive=partial["bundleArchive"],
                comparison_axis=canonical["comparisonAxis"],
            )
            wrapper_path.write_text(json.dumps(expected), encoding="utf-8")

            with mock.patch.object(
                subject.resume_runner,
                "_load_partial_evidence",
                return_value=partial,
            ), mock.patch.object(
                subject.github_runner,
                "_write_report",
            ) as writer:
                result = subject.reconcile(partial_report, bundle, canonical_path)

            self.assertEqual("already_consistent", result["result"])
            writer.assert_not_called()

    def test_existing_mismatched_wrapper_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            partial_report, bundle, canonical_path, partial = self._fixture(root)
            canonical_path.write_text(
                json.dumps(self._canonical(partial)),
                encoding="utf-8",
            )
            wrapper_path = canonical_path.parent / subject.github_runner.REPORT_NAME
            wrapper_path.write_text(json.dumps({"schema": "wrong"}), encoding="utf-8")

            with mock.patch.object(
                subject.resume_runner,
                "_load_partial_evidence",
                return_value=partial,
            ), mock.patch.object(
                subject.github_runner,
                "_write_report",
            ) as writer:
                with self.assertRaisesRegex(ValueError, "上書きしません"):
                    subject.reconcile(partial_report, bundle, canonical_path)

            writer.assert_not_called()
            self.assertEqual({"schema": "wrong"}, json.loads(wrapper_path.read_text()))

    def test_canonical_e2_drift_is_rejected_before_wrapper_write(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            partial_report, bundle, canonical_path, partial = self._fixture(root)
            canonical = self._canonical(partial)
            canonical["e2"] = {"result": "forged"}
            canonical_path.write_text(json.dumps(canonical), encoding="utf-8")

            with mock.patch.object(
                subject.resume_runner,
                "_load_partial_evidence",
                return_value=partial,
            ), mock.patch.object(
                subject.github_runner,
                "_write_report",
            ) as writer:
                with self.assertRaisesRegex(ValueError, "E2がpartial Evidenceと一致しません"):
                    subject.reconcile(partial_report, bundle, canonical_path)

            writer.assert_not_called()


if __name__ == "__main__":
    unittest.main()
