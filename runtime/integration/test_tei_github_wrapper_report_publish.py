import json
import tempfile
import unittest
from pathlib import Path

import run_tei_version_exchange_from_github as subject


class TEIGitHubWrapperReportPublishTest(unittest.TestCase):
    def test_report_created_during_run_is_not_overwritten_without_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = root / subject.REPORT_NAME
            report.write_text("intruder\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "暗黙上書き"):
                subject._write_report(
                    report,
                    {"result": "new"},
                    overwrite=False,
                )

            self.assertEqual("intruder\n", report.read_text(encoding="utf-8"))

    def test_overwrite_replaces_regular_report_atomically(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = root / subject.REPORT_NAME
            report.write_text("old\n", encoding="utf-8")

            subject._write_report(
                report,
                {"result": "new"},
                overwrite=True,
            )

            self.assertEqual(
                {"result": "new"},
                json.loads(report.read_text(encoding="utf-8")),
            )
            self.assertEqual([], list(root.glob(f".{report.name}.*.tmp")))

    def test_symlink_report_is_rejected_without_writing_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "target.txt"
            target.write_text("protected\n", encoding="utf-8")
            report = root / subject.REPORT_NAME
            report.symlink_to(target)

            with self.assertRaises(ValueError):
                subject._write_report(
                    report,
                    {"result": "new"},
                    overwrite=True,
                )

            self.assertEqual("protected\n", target.read_text(encoding="utf-8"))

    def test_success_uses_unique_temp_and_leaves_no_candidate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = root / subject.REPORT_NAME

            subject._write_report(
                report,
                {"schema": "test", "result": "verified"},
                overwrite=False,
            )

            self.assertTrue(report.is_file())
            self.assertFalse(report.is_symlink())
            self.assertEqual([], list(root.glob(f".{report.name}.*.tmp")))


if __name__ == "__main__":
    unittest.main()
