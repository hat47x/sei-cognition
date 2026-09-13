import tempfile
import unittest
from pathlib import Path
from unittest import mock

import run_tei_revision_b_e2_from_github as subject


class TEIE2PartialOutputPrecheckTest(unittest.TestCase):
    def test_existing_partial_bundle_blocks_before_source_acquisition(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            output = root / "evidence"
            output.mkdir()
            bundle = output / subject.BUNDLE_NAME
            bundle.write_bytes(b"existing")
            reference = root / "a.tar.gz"
            reference.write_bytes(b"placeholder")

            with mock.patch.object(
                subject.source_acquisition,
                "materialize_revision_b_source",
            ) as acquisition:
                with self.assertRaisesRegex(ValueError, "既存E2 partial Evidence"):
                    subject.run_e2_from_github(
                        None,
                        output,
                        reference_evidence_bundle=reference,
                        tei_go_executable=root / "go123" / "go",
                        token="placeholder",
                    )

            acquisition.assert_not_called()
            self.assertEqual(b"existing", bundle.read_bytes())

    def test_overwrite_precheck_is_read_only_for_existing_regular_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            bundle = output / subject.BUNDLE_NAME
            report = output / subject.REPORT_NAME
            bundle.write_bytes(b"bundle")
            report.write_bytes(b"report")

            observed = subject._precheck_partial_output_paths(output, overwrite=True)

            self.assertEqual((bundle, report), observed)
            self.assertEqual(b"bundle", bundle.read_bytes())
            self.assertEqual(b"report", report.read_bytes())

    def test_dangling_symlink_is_rejected_even_with_overwrite(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            bundle = output / subject.BUNDLE_NAME
            missing = output / "missing-target"
            bundle.symlink_to(missing)

            with self.assertRaises(ValueError):
                subject._precheck_partial_output_paths(output, overwrite=True)

            self.assertTrue(bundle.is_symlink())
            self.assertFalse(missing.exists())


if __name__ == "__main__":
    unittest.main()
