import json
import tempfile
import unittest
from pathlib import Path

import run_tei_version_exchange_evidence as subject


class TEICanonicalReportPublishTest(unittest.TestCase):
    def test_legacy_fixed_tmp_symlink_is_not_followed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = root / subject.REPORT_NAME
            target = root / "sentinel.txt"
            target.write_text("unchanged\n", encoding="utf-8")
            legacy_candidate = report.with_name(report.name + ".tmp")
            legacy_candidate.symlink_to(target)

            subject._write_report(report, {"result": "verified"})

            self.assertEqual("unchanged\n", target.read_text(encoding="utf-8"))
            self.assertTrue(legacy_candidate.is_symlink())
            self.assertEqual(
                {"result": "verified"},
                json.loads(report.read_text(encoding="utf-8")),
            )

    def test_final_report_symlink_is_rejected_without_touching_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = root / subject.REPORT_NAME
            target = root / "sentinel.txt"
            target.write_text("unchanged\n", encoding="utf-8")
            report.symlink_to(target)

            with self.assertRaises(ValueError):
                subject._write_report(report, {"result": "verified"})

            self.assertEqual("unchanged\n", target.read_text(encoding="utf-8"))
            self.assertTrue(report.is_symlink())

    def test_success_leaves_no_owned_temporary_candidate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = root / subject.REPORT_NAME

            subject._write_report(report, {"result": "verified"})

            self.assertTrue(report.is_file())
            candidates = [
                path
                for path in root.iterdir()
                if path.name.startswith(f".{report.name}.")
                and path.name.endswith(".tmp")
            ]
            self.assertEqual([], candidates)


if __name__ == "__main__":
    unittest.main()
