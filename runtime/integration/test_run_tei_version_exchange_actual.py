import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import run_tei_version_exchange_actual as subject


class TEIVersionExchangeActualRunnerTest(unittest.TestCase):
    def make_paths(self, root: Path):
        return {
            "source_repo": root / "tei-b",
            "reference_source_repo": root / "tei-a",
            "output_archive": root / "evidence" / "bundle.tar.gz",
            "soza_repo_root": root / "soza",
            "expected_soza_head": "a" * 40,
            "result_file": root / "evidence" / "result.json",
        }

    @mock.patch.object(subject.adapter_runner, "run_compatibility")
    @mock.patch.object(subject.bundle_runner, "produce_bundle")
    def test_success_records_e2_and_e3(self, produce, compatibility):
        produce.return_value = {"result": "bundle_produced", "bundle": {}}
        compatibility.return_value = {"result": "adapter_compatible"}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            args = self.make_paths(root)
            code, payload = subject.run_actual(**args)
            saved = json.loads(args["result_file"].read_text(encoding="utf-8"))
        self.assertEqual(0, code)
        self.assertEqual("ready_to_review", payload["result"])
        self.assertEqual("bundle_produced", saved["e2"]["result"])
        self.assertEqual("adapter_compatible", saved["e3"]["result"])
        compatibility.assert_called_once_with(
            args["output_archive"].resolve(),
            soza_repo_root=args["soza_repo_root"],
            expected_source_commit=subject.bundle_runner.source_identity.REVISION_B,
            expected_soza_head=args["expected_soza_head"],
        )

    @mock.patch.object(subject.adapter_runner, "run_compatibility")
    @mock.patch.object(subject.bundle_runner, "produce_bundle")
    def test_e2_stage_failure_is_persisted_and_e3_is_not_started(
        self, produce, compatibility
    ):
        produce.side_effect = subject.bundle_runner.TEIEvidenceStageError(
            "tei_cli_build",
            "build failed",
            command=["go", "build"],
            returncode=2,
            stderr="compile failed",
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            args = self.make_paths(root)
            code, payload = subject.run_actual(**args)
            saved = json.loads(args["result_file"].read_text(encoding="utf-8"))
        self.assertEqual(1, code)
        self.assertEqual("E2", payload["phase"])
        self.assertEqual("tei_cli_build", saved["failure"]["stage"])
        self.assertEqual(2, saved["failure"]["returnCode"])
        self.assertIn("compile failed", saved["failure"]["stderrTail"])
        compatibility.assert_not_called()

    @mock.patch.object(subject.adapter_runner, "run_compatibility")
    @mock.patch.object(subject.bundle_runner, "produce_bundle")
    def test_e3_stage_failure_keeps_e2_result(self, produce, compatibility):
        produce.return_value = {
            "result": "bundle_produced",
            "bundle": {"observation": {"source_commit": "b" * 40}},
        }
        compatibility.side_effect = subject.adapter_runner.TEIAdapterStageError(
            "soza_teiintegration_live_test",
            "live test failed",
            command=["go", "test"],
            returncode=1,
            stderr="strict decode failed",
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            args = self.make_paths(root)
            code, payload = subject.run_actual(**args)
            saved = json.loads(args["result_file"].read_text(encoding="utf-8"))
        self.assertEqual(1, code)
        self.assertEqual("E3", payload["phase"])
        self.assertEqual("bundle_produced", saved["e2"]["result"])
        self.assertEqual(
            "soza_teiintegration_live_test", saved["failure"]["stage"]
        )

    @mock.patch.object(subject.adapter_runner, "run_compatibility")
    @mock.patch.object(subject.bundle_runner, "produce_bundle")
    def test_existing_result_file_is_never_overwritten(self, produce, compatibility):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            args = self.make_paths(root)
            args["result_file"].parent.mkdir(parents=True)
            args["result_file"].write_text("historical\n", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                subject.run_actual(**args)
            self.assertEqual(
                "historical\n",
                args["result_file"].read_text(encoding="utf-8"),
            )
        produce.assert_not_called()
        compatibility.assert_not_called()

    @mock.patch.object(subject.adapter_runner, "run_compatibility")
    @mock.patch.object(subject.bundle_runner, "produce_bundle")
    def test_existing_evidence_bundle_is_never_overwritten(
        self, produce, compatibility
    ):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            args = self.make_paths(root)
            args["output_archive"].parent.mkdir(parents=True)
            args["output_archive"].write_bytes(b"historical")
            with self.assertRaises(FileExistsError):
                subject.run_actual(**args)
            self.assertEqual(b"historical", args["output_archive"].read_bytes())
        produce.assert_not_called()
        compatibility.assert_not_called()

    def test_result_json_and_bundle_cannot_share_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            args = self.make_paths(root)
            args["result_file"] = args["output_archive"]
            with self.assertRaisesRegex(ValueError, "同じpath"):
                subject.run_actual(**args)


if __name__ == "__main__":
    unittest.main()
