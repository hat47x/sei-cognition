import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import prepare_tei_revision_b_checkout as subject


class CheckoutPreparationReportTest(unittest.TestCase):
    def test_report_path_inside_source_or_output_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source"
            source.mkdir()
            output = root / "tei-b"

            with self.assertRaisesRegex(ValueError, "source clone配下"):
                subject._prepare_report_output(
                    source / "report.json",
                    source_repo=source,
                    output_repo=output,
                )

            output.mkdir()
            with self.assertRaisesRegex(ValueError, "revision B checkout output配下"):
                subject._prepare_report_output(
                    output / "report.json",
                    source_repo=source,
                    output_repo=output,
                )

    def test_existing_and_dangling_symlink_report_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source"
            source.mkdir()
            output = root / "tei-b"

            existing = root / "existing.json"
            existing.write_text("old\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "新規path"):
                subject._prepare_report_output(
                    existing,
                    source_repo=source,
                    output_repo=output,
                )
            self.assertEqual("old\n", existing.read_text(encoding="utf-8"))

            dangling = root / "dangling.json"
            dangling.symlink_to(root / "missing-target.json")
            with self.assertRaises((ValueError, OSError)):
                subject._prepare_report_output(
                    dangling,
                    source_repo=source,
                    output_repo=output,
                )
            self.assertTrue(dangling.is_symlink())
            self.assertFalse((root / "missing-target.json").exists())

    def test_write_json_no_overwrite_publishes_complete_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = root / "report.json"
            value = {
                "schema": "sei.tei-revision-b-checkout-preparation/v1",
                "result": "prepared_verified",
                "qualityJudgement": "not_evaluated",
            }

            subject._write_json_no_overwrite(report, value)

            self.assertEqual(value, json.loads(report.read_text(encoding="utf-8")))
            self.assertEqual([], list(root.glob(".report.json.*.tmp")))

    def test_write_json_no_overwrite_preserves_existing_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = root / "report.json"
            report.write_text("old\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "暗黙上書き"):
                subject._write_json_no_overwrite(report, {"result": "new"})

            self.assertEqual("old\n", report.read_text(encoding="utf-8"))
            self.assertEqual([], list(root.glob(".report.json.*.tmp")))

    @mock.patch.object(subject, "_write_json_no_overwrite")
    @mock.patch.object(subject, "prepare_checkout")
    def test_report_publish_failure_removes_checkout_created_by_call(
        self, prepare_checkout, write_report
    ):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source"
            source.mkdir()
            output = root / "tei-b"
            report = root / "report.json"

            def prepare_side_effect(source_repo, output_repo):
                output_repo.mkdir()
                (output_repo / "marker").write_text("owned\n", encoding="utf-8")
                return {
                    "schema": "sei.tei-revision-b-checkout-preparation/v1",
                    "result": "prepared_verified",
                    "sourceRepository": str(source_repo),
                    "outputRepository": str(output_repo),
                }

            prepare_checkout.side_effect = prepare_side_effect
            write_report.side_effect = ValueError("publish race")

            with self.assertRaisesRegex(ValueError, "publish race"):
                subject.prepare_checkout_with_report(source, output, report)

            self.assertFalse(output.exists())
            self.assertFalse(report.exists())

    @mock.patch.object(subject, "_write_json_no_overwrite")
    @mock.patch.object(subject, "prepare_checkout")
    def test_report_path_is_validated_before_checkout_creation(
        self, prepare_checkout, write_report
    ):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source"
            source.mkdir()
            output = root / "tei-b"
            report = source / "report.json"

            with self.assertRaisesRegex(ValueError, "source clone配下"):
                subject.prepare_checkout_with_report(source, output, report)

            prepare_checkout.assert_not_called()
            write_report.assert_not_called()
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
