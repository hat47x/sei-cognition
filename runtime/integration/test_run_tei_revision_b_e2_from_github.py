import tempfile
import unittest
from contextlib import nullcontext
from pathlib import Path
from unittest import mock

import run_tei_revision_b_e2_from_github as subject


class TEIRevisionBE2FromGitHubTest(unittest.TestCase):
    def _common_patches(self, root: Path):
        evidence = root / "evidence"
        go = root / "go123" / "go"
        provenance = {
            "mode": "github-git-data-api-content-addressed",
            "sourceCommit": subject.e2_runner.source_identity.REVISION_B,
        }
        return evidence, go, provenance

    def test_success_collects_e2_without_e3_preflight_or_soza_go(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            evidence, go, provenance = self._common_patches(root)

            with mock.patch.object(
                subject,
                "_prepare_output_dir_before_source",
                return_value=evidence,
            ), mock.patch.object(
                subject,
                "_verify_e2_prerequisites_before_source",
                return_value={
                    "requiredVersion": "go1.23.2",
                    "observedVersion": "go version go1.23.2 linux/amd64",
                    "requiredTarget": "linux/amd64",
                    "observedTarget": "linux/amd64",
                    "executable": str(go),
                },
            ), mock.patch.object(
                subject.github_runner,
                "_prepare_source_temp_parent",
                return_value=root,
            ), mock.patch.object(
                subject.source_acquisition,
                "materialize_revision_b_source",
                return_value={"result": "verified"},
            ) as acquisition, mock.patch.object(
                subject.github_runner,
                "_source_provenance",
                return_value=provenance,
            ), mock.patch.object(
                subject.version_exchange,
                "_prepare_output_dir",
                return_value=evidence,
            ), mock.patch.object(
                subject.version_exchange,
                "_prepare_output_paths",
            ), mock.patch.object(
                subject.version_exchange,
                "_go_on_path",
                return_value=nullcontext(go),
            ), mock.patch.object(
                subject.e2_runner,
                "produce_bundle",
                return_value={"result": "bundle_produced"},
            ) as e2, mock.patch.object(
                subject.github_runner,
                "_write_report",
            ) as write_report, mock.patch.object(
                subject.github_runner,
                "_run_preflight",
                side_effect=AssertionError("E3-aware preflight must not run"),
            ):
                result = subject.run_e2_from_github(
                    None,
                    evidence,
                    reference_evidence_bundle=root / "a.tar.gz",
                    tei_go_executable=go,
                    token="placeholder",
                )

            acquisition.assert_called_once()
            e2.assert_called_once()
            self.assertEqual("e2_bundle_verified_e3_not_run", result["result"])
            self.assertIsNone(result["e3"])
            self.assertTrue(result["comparisonAxis"]["e3IntentionallyNotRun"])
            written = write_report.call_args.args[1]
            self.assertEqual("e2_bundle_verified_e3_not_run", written["result"])

    def test_invalid_e2_toolchain_stops_before_source_acquisition(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            evidence, go, _ = self._common_patches(root)

            with mock.patch.object(
                subject,
                "_prepare_output_dir_before_source",
                return_value=evidence,
            ), mock.patch.object(
                subject,
                "_verify_e2_prerequisites_before_source",
                side_effect=ValueError("wrong Go"),
            ), mock.patch.object(
                subject.source_acquisition,
                "materialize_revision_b_source",
            ) as acquisition:
                with self.assertRaisesRegex(ValueError, "wrong Go"):
                    subject.run_e2_from_github(
                        None,
                        evidence,
                        reference_evidence_bundle=root / "a.tar.gz",
                        tei_go_executable=go,
                        token="placeholder",
                    )

            acquisition.assert_not_called()
            self.assertFalse(evidence.exists())

    def test_e2_failure_preserves_acquisition_provenance_and_substage(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            evidence, go, provenance = self._common_patches(root)
            failure = subject.e2_runner.TEIEvidenceStageError(
                "deployment_provider_plan_execution",
                "provider failed",
                command=["tei", "deployment-provider-plan"],
                returncode=2,
                stderr="failure",
            )

            with mock.patch.object(
                subject,
                "_prepare_output_dir_before_source",
                return_value=evidence,
            ), mock.patch.object(
                subject,
                "_verify_e2_prerequisites_before_source",
                return_value={"executable": str(go)},
            ), mock.patch.object(
                subject.github_runner,
                "_prepare_source_temp_parent",
                return_value=root,
            ), mock.patch.object(
                subject.source_acquisition,
                "materialize_revision_b_source",
                return_value={"result": "verified"},
            ), mock.patch.object(
                subject.github_runner,
                "_source_provenance",
                return_value=provenance,
            ), mock.patch.object(
                subject.version_exchange,
                "_prepare_output_dir",
                return_value=evidence,
            ), mock.patch.object(
                subject.version_exchange,
                "_prepare_output_paths",
            ), mock.patch.object(
                subject.version_exchange,
                "_go_on_path",
                return_value=nullcontext(go),
            ), mock.patch.object(
                subject.e2_runner,
                "produce_bundle",
                side_effect=failure,
            ), mock.patch.object(
                subject.github_runner,
                "_write_report",
            ) as write_report:
                with self.assertRaises(subject.GitHubE2RunFailed):
                    subject.run_e2_from_github(
                        None,
                        evidence,
                        reference_evidence_bundle=root / "a.tar.gz",
                        tei_go_executable=go,
                        token="placeholder",
                    )

            report = write_report.call_args.args[1]
            self.assertEqual("e2_failed", report["result"])
            self.assertEqual(provenance, report["sourceAcquisition"])
            self.assertEqual("E2", report["failure"]["stage"])
            self.assertEqual(
                "deployment_provider_plan_execution",
                report["failure"]["substage"],
            )
            self.assertIsNone(report["e3"])

    def test_e2_go_check_happens_before_source_acquisition(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            evidence, go, provenance = self._common_patches(root)
            order: list[str] = []

            def verify_go(_path):
                order.append("go")
                return {"executable": str(go)}

            def acquire(*_args, **_kwargs):
                order.append("acquire")
                return {"result": "verified"}

            with mock.patch.object(
                subject,
                "_prepare_output_dir_before_source",
                return_value=evidence,
            ), mock.patch.object(
                subject,
                "_verify_e2_prerequisites_before_source",
                side_effect=verify_go,
            ), mock.patch.object(
                subject.github_runner,
                "_prepare_source_temp_parent",
                return_value=root,
            ), mock.patch.object(
                subject.source_acquisition,
                "materialize_revision_b_source",
                side_effect=acquire,
            ), mock.patch.object(
                subject.github_runner,
                "_source_provenance",
                return_value=provenance,
            ), mock.patch.object(
                subject.version_exchange,
                "_prepare_output_dir",
                return_value=evidence,
            ), mock.patch.object(
                subject.version_exchange,
                "_prepare_output_paths",
            ), mock.patch.object(
                subject.version_exchange,
                "_go_on_path",
                return_value=nullcontext(go),
            ), mock.patch.object(
                subject.e2_runner,
                "produce_bundle",
                return_value={"result": "bundle_produced"},
            ), mock.patch.object(
                subject.github_runner,
                "_write_report",
            ):
                subject.run_e2_from_github(
                    None,
                    evidence,
                    reference_evidence_bundle=root / "a.tar.gz",
                    tei_go_executable=go,
                    token="placeholder",
                )

            self.assertEqual(["go", "acquire"], order)


if __name__ == "__main__":
    unittest.main()
