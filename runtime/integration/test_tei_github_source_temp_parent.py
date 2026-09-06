import tempfile
import unittest
from pathlib import Path
from unittest import mock

import preflight_tei_version_exchange_from_github as preflight
import run_tei_version_exchange_from_github as subject


class TEIGitHubSourceTempParentTest(unittest.TestCase):
    def test_common_parent_is_allowed_but_input_or_output_descendant_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            soza = root / "soza"
            reference = root / "reference-a"
            evidence = root / "evidence"
            for path in (soza, reference, evidence):
                path.mkdir()

            with mock.patch.object(subject.tempfile, "gettempdir", return_value=str(root)):
                self.assertEqual(
                    root.resolve(),
                    subject._prepare_source_temp_parent(evidence, soza, reference),
                )

            for label, unsafe in (
                ("SOZA repository", soza / "tmp"),
                ("revision A reference checkout", reference / "tmp"),
                ("Evidence directory", evidence / "tmp"),
            ):
                with self.subTest(label=label):
                    unsafe.mkdir()
                    with mock.patch.object(
                        subject.tempfile,
                        "gettempdir",
                        return_value=str(unsafe),
                    ):
                        with self.assertRaisesRegex(ValueError, label):
                            subject._prepare_source_temp_parent(
                                evidence,
                                soza,
                                reference,
                            )

    def test_preflight_reports_source_temp_parent_blocker_without_mutation(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            soza = root / "soza"
            unsafe = soza / "tmp"
            unsafe.mkdir(parents=True)
            output = root / "evidence"

            ready = {"ready": True}
            with mock.patch.object(preflight, "_check_platform", return_value=ready), mock.patch.object(
                preflight,
                "_check_reference_input",
                return_value=ready,
            ), mock.patch.object(
                preflight,
                "_check_soza_source",
                return_value=ready,
            ), mock.patch.object(
                preflight,
                "_check_tei_go",
                return_value=ready,
            ), mock.patch.object(
                preflight,
                "_check_soza_go",
                return_value=ready,
            ), mock.patch.object(
                preflight,
                "_check_output_path",
                return_value=ready,
            ), mock.patch.object(
                subject.tempfile,
                "gettempdir",
                return_value=str(unsafe),
            ):
                result = preflight.run_preflight(
                    None,
                    soza,
                    output,
                    reference_evidence_bundle=root / "a.tar.gz",
                    tei_go_executable=root / "go123/go",
                    soza_go_executable=root / "go125/go",
                    env={"GITHUB_TOKEN": "placeholder"},
                )

            self.assertFalse(result["ready"])
            self.assertIn("source_temp_parent", result["blockedChecks"])
            self.assertFalse(output.exists())
            self.assertFalse(result["revisionBSourceMaterialized"])
            self.assertFalse(result["evidenceOutputCreated"])

    def test_one_shot_rechecks_temp_parent_before_source_acquisition(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            soza = root / "soza"
            unsafe = soza / "tmp"
            unsafe.mkdir(parents=True)
            output = root / "evidence"

            with mock.patch.object(
                subject,
                "_run_preflight",
                return_value={"ready": True, "blockedChecks": []},
            ), mock.patch.object(
                subject.tempfile,
                "gettempdir",
                return_value=str(unsafe),
            ), mock.patch.object(
                subject.source_acquisition,
                "materialize_revision_b_source",
            ) as acquisition:
                with self.assertRaisesRegex(ValueError, "SOZA repository"):
                    subject.run_from_github(
                        None,
                        soza,
                        output,
                        reference_evidence_bundle=root / "a.tar.gz",
                        tei_go_executable=root / "go123/go",
                        soza_go_executable=root / "go125/go",
                        token="placeholder",
                    )

            acquisition.assert_not_called()
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
