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
        version = "go1.23.2" if name == "go123" else "go1.25.0"
        path.write_text(
            "#!/bin/sh\n"
            "if [ \"${1:-}\" = version ]; then\n"
            f"  echo 'go version {version} linux/amd64'\n"
            "fi\n"
            "exit 0\n",
            encoding="utf-8",
        )
        path.chmod(0o755)
        return path

    def make_inputs(self, root: Path):
        source = root / "tei-b"
        reference = root / "tei-a"
        soza = root / "soza"
        for path in (source, reference, soza):
            path.mkdir()
        go_root = soza / "runtime/go"
        go_root.mkdir(parents=True)
        (go_root / "go.mod").write_text(
            "module example.invalid/soza-test\n\ngo 1.25\n",
            encoding="utf-8",
        )
        return source, reference, soza

    def build_success(self, archive: Path):
        archive.write_bytes(b"bundle")
        return {"result": "bundle_produced"}

    @mock.patch.object(subject.adapter_runner, "run_compatibility")
    @mock.patch.object(subject.build_runner, "produce_bundle")
    def test_output_dir_inside_input_checkout_is_rejected_before_creation(
        self, build, adapter
    ):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, reference, soza = self.make_inputs(root)
            tei_go = self.make_go(root, "go123")
            soza_go = self.make_go(root, "go125")
            for input_repo in (source, reference, soza):
                with self.subTest(input_repo=input_repo.name):
                    output = input_repo / "nested/evidence"
                    with self.assertRaisesRegex(ValueError, "配下には置けません"):
                        subject.run_version_exchange(
                            source,
                            reference,
                            soza,
                            output,
                            tei_go_executable=tei_go,
                            soza_go_executable=soza_go,
                        )
                    self.assertFalse(output.exists())
            build.assert_not_called()
            adapter.assert_not_called()

    @mock.patch.object(subject.adapter_runner, "run_compatibility")
    @mock.patch.object(subject.build_runner, "produce_bundle")
    def test_output_dir_cannot_contain_input_checkouts(self, build, adapter):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace = root / "workspace"
            workspace.mkdir()
            source, reference, soza = self.make_inputs(workspace)
            tei_go = self.make_go(root, "go123")
            soza_go = self.make_go(root, "go125")
            with self.assertRaisesRegex(ValueError, "包含できません"):
                subject.run_version_exchange(
                    source,
                    reference,
                    soza,
                    workspace,
                    tei_go_executable=tei_go,
                    soza_go_executable=soza_go,
                )
            build.assert_not_called()
            adapter.assert_not_called()

    @mock.patch.object(subject.adapter_runner, "run_compatibility")
    @mock.patch.object(subject.build_runner, "produce_bundle")
    def test_symlink_output_dir_is_rejected_before_runner_start(self, build, adapter):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, reference, soza = self.make_inputs(root)
            tei_go = self.make_go(root, "go123")
            soza_go = self.make_go(root, "go125")
            actual = root / "actual-evidence"
            actual.mkdir()
            output = root / "evidence-link"
            output.symlink_to(actual, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "symlink"):
                subject.run_version_exchange(
                    source,
                    reference,
                    soza,
                    output,
                    tei_go_executable=tei_go,
                    soza_go_executable=soza_go,
                )
            self.assertEqual([], list(actual.iterdir()))
            build.assert_not_called()
            adapter.assert_not_called()

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
                return self.build_success(archive)

            def adapter_side_effect(archive, **kwargs):
                observed["e3_go"] = Path(shutil.which("go")).resolve()
                return {
                    "result": "adapter_compatible",
                    "sozaGoRequirement": "1.25",
                    "sozaGoVersion": "go version go1.25.0 linux/amd64",
                }

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
            self.assertEqual("1.25", report["comparisonAxis"]["sozaGoRequirement"])
            self.assertEqual(
                "go version go1.25.0 linux/amd64",
                report["comparisonAxis"]["sozaGoObserved"],
            )

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
            self.assertNotIn("substage", report["failure"])

    @mock.patch.object(subject.adapter_runner, "run_compatibility")
    @mock.patch.object(subject.build_runner, "produce_bundle")
    def test_missing_e2_go_is_recorded_as_tei_go_toolchain(self, build, adapter):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, reference, soza = self.make_inputs(root)
            missing_tei_go = root / "missing-e2/bin/go"
            soza_go = self.make_go(root, "go125")
            output = root / "evidence"
            with self.assertRaises(subject.VersionExchangeRunFailed) as raised:
                subject.run_version_exchange(
                    source,
                    reference,
                    soza,
                    output,
                    tei_go_executable=missing_tei_go,
                    soza_go_executable=soza_go,
                )
            self.assertEqual("E2", raised.exception.stage)
            build.assert_not_called()
            adapter.assert_not_called()
            report = json.loads((output / subject.REPORT_NAME).read_text(encoding="utf-8"))
            failure = report["failure"]
            self.assertEqual("E2", failure["stage"])
            self.assertEqual("tei_go_toolchain", failure["substage"])
            self.assertEqual("tei_go_toolchain", failure["detail"]["stage"])

    @mock.patch.object(subject.adapter_runner, "run_compatibility")
    @mock.patch.object(subject.build_runner, "produce_bundle")
    def test_staged_e2_failure_propagates_substage_detail(self, build, adapter):
        build.side_effect = subject.build_runner.TEIEvidenceStageError(
            "tei_cli_build",
            "external process returned non-zero status",
            command=["go", "build", "./cmd/tei"],
            returncode=2,
            stderr="compile failed",
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, reference, soza = self.make_inputs(root)
            tei_go = self.make_go(root, "go123")
            soza_go = self.make_go(root, "go125")
            output = root / "evidence"
            with self.assertRaises(subject.VersionExchangeRunFailed):
                subject.run_version_exchange(
                    source,
                    reference,
                    soza,
                    output,
                    tei_go_executable=tei_go,
                    soza_go_executable=soza_go,
                )
            report = json.loads((output / subject.REPORT_NAME).read_text(encoding="utf-8"))
            failure = report["failure"]
            self.assertEqual("E2", failure["stage"])
            self.assertEqual("tei_cli_build", failure["substage"])
            self.assertEqual("tei_cli_build", failure["detail"]["stage"])
            self.assertEqual(2, failure["detail"]["returnCode"])
            self.assertEqual("compile failed", failure["detail"]["stderrTail"])
            adapter.assert_not_called()

    @mock.patch.object(subject.adapter_runner, "run_compatibility")
    @mock.patch.object(subject.build_runner, "produce_bundle")
    def test_e3_failure_preserves_e2_bundle_and_report(self, build, adapter):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, reference, soza = self.make_inputs(root)
            tei_go = self.make_go(root, "go123")
            soza_go = self.make_go(root, "go125")
            output = root / "evidence"

            build.side_effect = lambda source_repo, reference_repo, archive: self.build_success(archive)
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
            self.assertNotIn("substage", report["failure"])
            self.assertEqual("bundle_produced", report["e2"]["result"])

    @mock.patch.object(subject.adapter_runner, "run_compatibility")
    @mock.patch.object(subject.build_runner, "produce_bundle")
    def test_missing_e3_go_is_recorded_as_soza_go_toolchain(self, build, adapter):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, reference, soza = self.make_inputs(root)
            tei_go = self.make_go(root, "go123")
            missing_soza_go = root / "missing-e3/bin/go"
            output = root / "evidence"
            build.side_effect = lambda source_repo, reference_repo, archive: self.build_success(archive)
            with self.assertRaises(subject.VersionExchangeRunFailed) as raised:
                subject.run_version_exchange(
                    source,
                    reference,
                    soza,
                    output,
                    tei_go_executable=tei_go,
                    soza_go_executable=missing_soza_go,
                )
            self.assertEqual("E3", raised.exception.stage)
            adapter.assert_not_called()
            self.assertTrue((output / subject.BUNDLE_NAME).is_file())
            report = json.loads((output / subject.REPORT_NAME).read_text(encoding="utf-8"))
            failure = report["failure"]
            self.assertEqual("e2_verified_e3_failed", report["result"])
            self.assertEqual("E3", failure["stage"])
            self.assertEqual("soza_go_toolchain", failure["substage"])
            self.assertEqual("soza_go_toolchain", failure["detail"]["stage"])

    @mock.patch.object(subject.adapter_runner, "run_compatibility")
    @mock.patch.object(subject.build_runner, "produce_bundle")
    def test_staged_e3_failure_propagates_substage_detail(self, build, adapter):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, reference, soza = self.make_inputs(root)
            tei_go = self.make_go(root, "go123")
            soza_go = self.make_go(root, "go125")
            output = root / "evidence"
            build.side_effect = lambda source_repo, reference_repo, archive: self.build_success(archive)
            adapter.side_effect = subject.adapter_runner.TEIAdapterStageError(
                "soza_teiintegration_live_test",
                "external process returned non-zero status",
                command=["go", "test", "./teiintegration"],
                returncode=1,
                stderr="strict decode / validator failure",
            )
            with self.assertRaises(subject.VersionExchangeRunFailed):
                subject.run_version_exchange(
                    source,
                    reference,
                    soza,
                    output,
                    tei_go_executable=tei_go,
                    soza_go_executable=soza_go,
                )
            report = json.loads((output / subject.REPORT_NAME).read_text(encoding="utf-8"))
            failure = report["failure"]
            self.assertEqual("E3", failure["stage"])
            self.assertEqual("soza_teiintegration_live_test", failure["substage"])
            self.assertEqual(
                "soza_teiintegration_live_test", failure["detail"]["stage"]
            )
            self.assertEqual(1, failure["detail"]["returnCode"])
            self.assertIn("validator", failure["detail"]["stderrTail"])

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

    @mock.patch.object(subject.adapter_runner, "run_compatibility")
    @mock.patch.object(subject.build_runner, "produce_bundle")
    def test_overwrite_removes_stale_bundle_before_e2_failure(self, build, adapter):
        build.side_effect = ValueError("build failed")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, reference, soza = self.make_inputs(root)
            tei_go = self.make_go(root, "go123")
            soza_go = self.make_go(root, "go125")
            output = root / "evidence"
            output.mkdir()
            stale_bundle = output / subject.BUNDLE_NAME
            stale_bundle.write_bytes(b"stale")
            (output / subject.REPORT_NAME).write_text("old\n", encoding="utf-8")
            with self.assertRaises(subject.VersionExchangeRunFailed):
                subject.run_version_exchange(
                    source,
                    reference,
                    soza,
                    output,
                    tei_go_executable=tei_go,
                    soza_go_executable=soza_go,
                    overwrite=True,
                )
            self.assertFalse(stale_bundle.exists())
            report = json.loads((output / subject.REPORT_NAME).read_text(encoding="utf-8"))
            self.assertEqual("e2_failed", report["result"])
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

    def test_go_symlink_named_go_is_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "toolchains/go-real"
            target.parent.mkdir(parents=True)
            target.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            target.chmod(0o755)
            link = root / "bin/go"
            link.parent.mkdir()
            link.symlink_to(target)
            with subject._go_on_path(link) as resolved:
                self.assertEqual(target.resolve(), resolved)
                self.assertEqual(target.resolve(), Path(shutil.which("go")).resolve())


if __name__ == "__main__":
    unittest.main()
