import tempfile
import unittest
from pathlib import Path

import run_tei_revision_b_prepositioned as subject


class TEIE2BundleNoOverwritePublishTest(unittest.TestCase):
    def test_publish_creates_exact_bytes_without_leaving_temporary_file(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            candidate = root / "candidate.tar.gz"
            candidate.write_bytes(b"verified-bundle-bytes")
            output = root / "evidence.tar.gz"

            subject._publish_bundle_no_overwrite(candidate, output)

            self.assertEqual(b"verified-bundle-bytes", output.read_bytes())
            leftovers = list(root.glob(f".{output.name}.*.tmp"))
            self.assertEqual([], leftovers)

    def test_existing_regular_output_is_rejected_without_overwrite(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            candidate = root / "candidate.tar.gz"
            candidate.write_bytes(b"new")
            output = root / "evidence.tar.gz"
            output.write_bytes(b"sentinel")

            with self.assertRaises(ValueError):
                subject._publish_bundle_no_overwrite(candidate, output)

            self.assertEqual(b"sentinel", output.read_bytes())

    def test_dangling_symlink_output_is_rejected_without_creating_target(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            candidate = root / "candidate.tar.gz"
            candidate.write_bytes(b"new")
            target = root / "missing-target.tar.gz"
            output = root / "evidence.tar.gz"
            output.symlink_to(target)
            self.assertTrue(output.is_symlink())
            self.assertFalse(target.exists())

            with self.assertRaises(ValueError):
                subject._publish_bundle_no_overwrite(candidate, output)

            self.assertTrue(output.is_symlink())
            self.assertFalse(target.exists())


if __name__ == "__main__":
    unittest.main()
