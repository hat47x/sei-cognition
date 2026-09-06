import tempfile
import unittest
from pathlib import Path

import preflight_tei_version_exchange_from_github as github_preflight
import run_tei_version_exchange_evidence as canonical


class TEICanonicalOutputSymlinkPreflightTest(unittest.TestCase):
    def test_canonical_runner_rejects_dangling_output_symlinks_even_with_overwrite(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name in (canonical.BUNDLE_NAME, canonical.REPORT_NAME):
                for overwrite in (False, True):
                    with self.subTest(name=name, overwrite=overwrite):
                        case = root / f"case-{name}-{overwrite}"
                        case.mkdir()
                        target = case / "missing-target"
                        output = case / name
                        output.symlink_to(target)

                        bundle = case / canonical.BUNDLE_NAME
                        report = case / canonical.REPORT_NAME
                        with self.assertRaisesRegex(ValueError, "symlink"):
                            canonical._prepare_output_paths(
                                bundle,
                                report,
                                overwrite=overwrite,
                            )

                        self.assertTrue(output.is_symlink())
                        self.assertFalse(target.exists())

    def test_github_preflight_rejects_dangling_canonical_output_symlinks(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            soza = root / "soza"
            soza.mkdir()

            for name in (canonical.BUNDLE_NAME, canonical.REPORT_NAME):
                for overwrite in (False, True):
                    with self.subTest(name=name, overwrite=overwrite):
                        output_dir = root / f"evidence-{name}-{overwrite}"
                        output_dir.mkdir()
                        target = output_dir / "missing-target"
                        output = output_dir / name
                        output.symlink_to(target)

                        with self.assertRaisesRegex(ValueError, "symlink"):
                            github_preflight._check_output_path(
                                output_dir,
                                soza_repo_root=soza,
                                reference_source_repo=None,
                                reference_evidence_bundle=None,
                                overwrite=overwrite,
                            )

                        self.assertTrue(output.is_symlink())
                        self.assertFalse(target.exists())


if __name__ == "__main__":
    unittest.main()
