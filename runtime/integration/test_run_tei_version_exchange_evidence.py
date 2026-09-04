import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import run_tei_version_exchange_evidence as subject


class TEIVersionExchangeEvidenceRunnerTest(unittest.TestCase):
    def make_go(self, root: Path, name: str) -> Path:
        path = root / name / "bin/go"
        path.parent.mkdir(parents=True)
        path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        path.chmod(0o755)
        return path

    def make_inputs(self, root: Path):
        source = root / "tei-b"
        reference = root / "tei-a"
        soza = root / "soza"
        for path in (source, reference, soza):
            path.mkdir()
        return source, reference, soza

    @mock.patch.object(subject.adapter_runner, "run_compatibility")
    @mock.patch.object(subject.build_runner, "produce_bundle")
    def test_distinct_go_toolchains_are_used_for_e2_and_e3(self, build, adapter):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, reference, soza = self.make_inputs(root)
            tei_go = self.make_go(root, "go123")
            soza_go = self.make_go(root, "go125")
            output = root / "evidence"
            observed = {}

            def build_side_effect(source_repo, reference_repo, archive):
                observed["e2_go"] = Path(shutil.which("go")).resolve()
                archive.write_bytes(b"bundle")
                return {"result": "bundle_produced"}

            def adapter_side_effect(archive, **kwargs):
                observed["e3_go"] = Path(shutil.which("go")).resolve()
                return {"result": "adapter_compatible"}

            build.side_effect = build_side_effect
            adapter.side_effect = adapter_side_effect
            original_path = os.environ.get("PATH")
            result = subject.run_version_exchange(
                source,
                reference,
                soza,
                output,
                tei_go_executable=tei_go,
                soza_go_executable=soza_go,
                expected_soza_head="f" * 40,
            )

            self.assertEqual(tei_go.resolve(), observed["e2_go"])
            self.assertEqual(soza_go.resolve(), observed["e3_go"])
            self.assertEqual(original_path, os.environ.get("PATH"))
            self.assertEqual("fixed_scope_e2_e3_verified", result["result"])
            report = json.loads((output / subject.REPORT_NAME).read_text(encoding="utf-8"))
            self.assertEqual("fixed_scope_e2_e3_verified", report["result"])
            self.assertEqual(str(tei_go.resolve()), report["comparisonAxis"]["teiGoExecutable"])
            self.assertEqual(str(soza_go.resolve()), report["comparisonAxis"]["sozaGoExecutable"])

    @mock.patch.object(subject.adapter_runner, "run_compatibility")
    @mock.patch.object(subject.build_runner, "produce_bundle")
    def test_e2_failure_writes_report_and_does_not_run_e3(self, build, adapter):
        build.side_effect = ValueError("TEI Go version mismatch")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, reference, soza = self.make_inputs(root)
            tei_go = self.make_go(root, "go123")
            soza_go = self.make_go(root, "go125")
            output = root / "evidence"
            with self.assertRaises(subject.VersionExchangeRunFailed) as raised:
                subject.run_version_exchange(
                    source,
                    reference,
                    soza,
                    output,
                    tei_go_executable=tei_go,
                    soza_go_executable=soza_go,
                )
            self.assertEqual("E2", raised.exception.stage)
            adapter.assert_not_called()
            report = json.loads((output / subject.REPORT_NAME).read_text(encoding="utf-8"))
            self.assertEqual("e2_failed", report["result"])
            self.assertEqual("E2", report["failure"]["stage"])

    @mock.patch.object(subject.adapter_runner, "run_compatibility")
    @mock.patch.object(subject.build_runner, "produce_bundle")
    def test_e3_failure_preserves_e2_bundle_and_report(self, build, adapter):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, reference, soza = self.make_inputs(root)
            tei_go = self.make_go(root, "go123")
            soza_go = self.make_go(root, "go125")
            output = root / "evidence"

            def build_side_effect(source_repo, reference_repo, archive):
                archive.write_bytes(b"bundle")
                return {"result": "bundle_produced"}

            build.side_effect = build_side_effect
            adapter.side_effect = RuntimeError("adapter live test failed")
            with self.assertRaises(subject.VersionExchangeRunFailed) as raised:
                subject.run_version_exchange(
                    source,
                    reference,
                    soza,
                    output,
                    tei_go_executable=tei_go,
                    soza_go_executable=soza_go,
                )
            self.assertEqual("E3", raised.exception.stage)
            self.assertTrue((output / subject.BUNDLE_NAME).is_file())
            report = json.loads((output / subject.REPORT_NAME).read_text(encoding="utf-8"))
            self.assertEqual("e2_verified_e3_failed", report["result"])
            self.assertEqual("E3", report["failure"]["stage"])
            self.assertEqual("bundle_produced", report["e2"]["result"])

    @mock.patch.object(subject.adapter_runner, "run_compatibility")
    @mock.patch.object(subject.build_runner, "produce_bundle")
    def test_existing_evidence_is_not_overwritten_without_opt_in(self, build, adapter):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, reference, soza = self.make_inputs(root)
            tei_go = self.make_go(root, "go123")
            soza_go = self.make_go(root, "go125")
            output = root / "evidence"
            output.mkdir()
            (output / subject.REPORT_NAME).write_text("old\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "無言で上書き"):
                subject.run_version_exchange(
                    source,
                    reference,
                    soza,
                    output,
                    tei_go_executable=tei_go,
                    soza_go_executable=soza_go,
                )
            build.assert_not_called()
            adapter.assert_not_called()

    def test_go_executable_basename_is_fixed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            invalid = root / "go1.23.2"
            invalid.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            invalid.chmod(0o755)
            with self.assertRaisesRegex(ValueError, "basename"):
                with subject._go_on_path(invalid):
                    pass


if __name__ == "__main__":
    unittest.main()
