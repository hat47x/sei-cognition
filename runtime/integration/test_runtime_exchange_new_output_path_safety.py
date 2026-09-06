import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import run_runtime_version_exchange_with_verification as subject


class RuntimeExchangeNewOutputPathSafetyTest(unittest.TestCase):
    def test_normal_nonexistent_path_is_canonicalized(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            requested = root / "new-output"

            resolved = subject._prepare_new_path(requested, "test output")

            self.assertEqual(requested.resolve(strict=False), resolved)
            self.assertFalse(requested.exists())

    def test_direct_dangling_symlink_is_rejected_without_creating_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "missing-target"
            requested = root / "new-output"
            requested.symlink_to(target)
            self.assertTrue(requested.is_symlink())
            self.assertFalse(requested.exists())
            self.assertFalse(target.exists())

            with self.assertRaises(ValueError):
                subject._prepare_new_path(requested, "test output")

            self.assertTrue(requested.is_symlink())
            self.assertFalse(target.exists())

    def test_symlink_parent_is_rejected_before_resolution(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            real_parent = root / "real-parent"
            real_parent.mkdir()
            linked_parent = root / "linked-parent"
            linked_parent.symlink_to(real_parent, target_is_directory=True)
            requested = linked_parent / "new-output"

            with self.assertRaises(ValueError):
                subject._prepare_new_path(requested, "test output")

            self.assertFalse((real_parent / "new-output").exists())

    def test_main_preserves_lexical_output_paths_until_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            evidence_target = root / "evidence-target"
            evidence = root / "evidence-link"
            evidence.symlink_to(evidence_target)
            verification_target = root / "verification-target.json"
            verification = root / "verification-link.json"
            verification.symlink_to(verification_target)

            argv = [
                "run_runtime_version_exchange_with_verification.py",
                "--kj-atlas-dir",
                str(root / "kj-atlas"),
                "--evidence-dir",
                str(evidence),
                "--verification-output",
                str(verification),
            ]
            with mock.patch.object(sys, "argv", argv), mock.patch.object(
                subject, "run", return_value=0
            ) as run_mock:
                self.assertEqual(0, subject.main())

            call = run_mock.call_args.kwargs
            self.assertEqual(evidence, call["evidence_dir"])
            self.assertEqual(verification, call["verification_output"])
            self.assertTrue(call["evidence_dir"].is_symlink())
            self.assertTrue(call["verification_output"].is_symlink())


if __name__ == "__main__":
    unittest.main()
