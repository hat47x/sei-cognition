import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import run_tei_bundle_adapter_compatibility as subject


class TEIE3PostLiveSourceRevalidationTest(unittest.TestCase):
    def make_layout(self, root: Path) -> tuple[Path, Path]:
        archive = root / "bundle.tar.gz"
        archive.write_bytes(b"fixture")
        sei = root / "sei"
        go_root = sei / "runtime/go"
        (go_root / "teiintegration").mkdir(parents=True)
        (go_root / "go.mod").write_text(
            "module test\n\ngo 1.25\n", encoding="utf-8"
        )
        (go_root / "teiintegration/tei_live_test.go").write_text(
            "package teiintegration\n", encoding="utf-8"
        )
        return archive, sei

    def verified_bundle(self):
        return {
            "observation": {
                "source_commit": subject.REVISION_B,
                "binary_sha256": "b" * 64,
                "provider_plan_sha256": "c" * 64,
                "archive_sha256": "d" * 64,
            },
            "metadata": {},
        }

    def staged_paths(self, root: Path):
        return {
            "executable": root / "bin/tei",
            "workspace": root / subject.FIXED_WORKSPACE,
            "run": root / subject.FIXED_RUN,
            "plugin_lock": root / subject.FIXED_PLUGIN_LOCK,
        }

    @mock.patch.object(subject, "_run_stage")
    @mock.patch.object(subject, "_verify_sei_go_requirement")
    @mock.patch.object(subject, "_verify_reference_input_identity")
    @mock.patch.object(subject, "_stage_bundle")
    @mock.patch.object(subject, "_ensure_linux_amd64")
    @mock.patch.object(subject.bundle_verifier, "verify_bundle")
    @mock.patch.object(subject, "_verify_sei_source_identity")
    def test_success_records_pre_and_post_live_sei_source(
        self,
        verify_sei,
        verify_bundle,
        ensure_platform,
        stage_bundle,
        verify_reference,
        verify_go,
        run_stage,
    ):
        pre = {"head": "e" * 40, "objects": {"runtime/go": "1" * 40}}
        post = {"head": "e" * 40, "objects": {"runtime/go": "1" * 40}}
        verify_sei.side_effect = [pre, post]
        verify_bundle.return_value = self.verified_bundle()
        verify_reference.return_value = {
            "sourceCommit": subject.REVISION_A,
            "objects": {},
        }
        verify_go.return_value = {
            "required": "1.25",
            "observed": "go version go1.25.0 linux/amd64",
        }
        run_stage.return_value = subprocess.CompletedProcess([], 0, "PASS\n", "")

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive, sei = self.make_layout(root)
            stage_bundle.return_value = self.staged_paths(root / "stage")
            result = subject.run_compatibility(
                archive,
                sei_repo_root=sei,
                expected_sei_head="e" * 40,
            )

        self.assertEqual(pre, result["seiSource"])
        self.assertEqual(post, result["postLiveTestSeiSource"])
        self.assertEqual(
            [
                mock.call(sei.resolve(), expected_head="e" * 40),
                mock.call(sei.resolve(), expected_head="e" * 40),
            ],
            verify_sei.call_args_list,
        )

    @mock.patch.object(subject, "_run_stage")
    @mock.patch.object(subject, "_verify_sei_go_requirement")
    @mock.patch.object(subject, "_verify_reference_input_identity")
    @mock.patch.object(subject, "_stage_bundle")
    @mock.patch.object(subject, "_ensure_linux_amd64")
    @mock.patch.object(subject.bundle_verifier, "verify_bundle")
    @mock.patch.object(subject, "_verify_sei_source_identity")
    def test_post_live_source_drift_reuses_existing_identity_stage(
        self,
        verify_sei,
        verify_bundle,
        ensure_platform,
        stage_bundle,
        verify_reference,
        verify_go,
        run_stage,
    ):
        verify_sei.side_effect = [
            {"head": "e" * 40, "objects": {}},
            ValueError("runtime/go changed during live test"),
        ]
        verify_bundle.return_value = self.verified_bundle()
        verify_reference.return_value = {
            "sourceCommit": subject.REVISION_A,
            "objects": {},
        }
        verify_go.return_value = {
            "required": "1.25",
            "observed": "go version go1.25.0 linux/amd64",
        }
        run_stage.return_value = subprocess.CompletedProcess([], 0, "PASS\n", "")

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive, sei = self.make_layout(root)
            stage_bundle.return_value = self.staged_paths(root / "stage")
            with self.assertRaises(subject.TEIAdapterStageError) as raised:
                subject.run_compatibility(
                    archive,
                    sei_repo_root=sei,
                    expected_sei_head="e" * 40,
                )

        self.assertEqual("sei_source_identity", raised.exception.stage)
        self.assertIn("live test実行後", raised.exception.message)
        self.assertIn("runtime/go changed", raised.exception.message)
        self.assertEqual(2, verify_sei.call_count)


if __name__ == "__main__":
    unittest.main()
