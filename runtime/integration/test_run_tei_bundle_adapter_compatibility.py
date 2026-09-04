import io
import os
import subprocess
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import run_tei_bundle_adapter_compatibility as subject


def add_file(tar, name, data=b"x", mode=0o644):
    info = tarfile.TarInfo(name)
    info.size = len(data)
    info.mode = mode
    tar.addfile(info, io.BytesIO(data))


class TEIBundleAdapterCompatibilityRunnerTest(unittest.TestCase):
    def make_bundle(self, root: Path, extra=None):
        archive = root / "bundle.tar.gz"
        with tarfile.open(archive, "w:gz") as tar:
            add_file(tar, "bin/tei", b"fake", 0o755)
            info = tarfile.TarInfo("reference/workspace")
            info.type = tarfile.DIRTYPE
            info.mode = 0o755
            tar.addfile(info)
            add_file(tar, "reference/workspace/input.txt", b"fixture")
            add_file(tar, subject.FIXED_PLUGIN_LOCK, b"{}")
            add_file(tar, subject.FIXED_RUN, b"{}")
            if extra:
                extra(tar)
        return archive

    def make_soza(self, root: Path):
        go_root = root / "runtime/go"
        (go_root / "teiintegration").mkdir(parents=True)
        (go_root / "go.mod").write_text("module test\n", encoding="utf-8")
        (go_root / "teiintegration/tei_live_test.go").write_text(
            "package teiintegration\n", encoding="utf-8"
        )
        return root

    def test_stage_bundle_extracts_only_live_inputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive = self.make_bundle(
                root,
                lambda tar: add_file(tar, "metadata.json", b"ignored"),
            )
            staged = root / "stage"
            paths = subject._stage_bundle(archive, staged)
            self.assertTrue(paths["executable"].is_file())
            self.assertTrue(os.access(paths["executable"], os.X_OK))
            self.assertFalse((staged / "metadata.json").exists())

    def test_path_traversal_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive = self.make_bundle(
                root,
                lambda tar: add_file(tar, "../escape", b"x"),
            )
            with self.assertRaisesRegex(ValueError, "pathが不正"):
                subject._stage_bundle(archive, root / "stage")

    def test_symlink_is_rejected(self):
        def extra(tar):
            info = tarfile.TarInfo("reference/workspace/link")
            info.type = tarfile.SYMTYPE
            info.linkname = "input.txt"
            tar.addfile(info)

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive = self.make_bundle(root, extra)
            with self.assertRaisesRegex(ValueError, "link/device"):
                subject._stage_bundle(archive, root / "stage")

    @mock.patch.object(subject, "_ensure_linux_amd64")
    @mock.patch.object(subject.subprocess, "run")
    @mock.patch.object(subject.bundle_verifier, "verify_bundle")
    def test_verified_bundle_runs_existing_live_test_with_provenance(
        self, verify, run, ensure
    ):
        verify.return_value = {
            "observation": {
                "source_commit": subject.REVISION_B,
                "binary_sha256": "b" * 64,
                "provider_plan_sha256": "c" * 64,
                "archive_sha256": "d" * 64,
            }
        }
        run.return_value = subprocess.CompletedProcess([], 0, "PASS\n", "")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive = self.make_bundle(root)
            soza = self.make_soza(root / "soza")
            result = subject.run_compatibility(archive, soza_repo_root=soza)
        self.assertEqual("adapter_compatible", result["result"])
        argv = run.call_args.args[0]
        self.assertEqual(
            [
                "go",
                "test",
                "./teiintegration",
                "-run",
                subject.LIVE_TEST,
                "-count=1",
                "-v",
            ],
            argv,
        )
        env = run.call_args.kwargs["env"]
        self.assertEqual("1", env["SOZA_E3B_TEI_LIVE"])
        self.assertEqual(
            f"tei-cli:{subject.REVISION_B}:bundle-sha256:{'d' * 64}",
            env["SOZA_TEI_SOURCE_STATE_REF"],
        )

    @mock.patch.object(subject, "_ensure_linux_amd64")
    @mock.patch.object(subject.subprocess, "run")
    @mock.patch.object(subject.bundle_verifier, "verify_bundle")
    def test_live_test_failure_is_not_promoted_to_compatibility(
        self, verify, run, ensure
    ):
        verify.return_value = {
            "observation": {
                "source_commit": subject.REVISION_B,
                "binary_sha256": "b" * 64,
                "provider_plan_sha256": "c" * 64,
                "archive_sha256": "d" * 64,
            }
        }
        run.return_value = subprocess.CompletedProcess(
            [], 1, "FAIL\n", "adapter failure"
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive = self.make_bundle(root)
            soza = self.make_soza(root / "soza")
            with self.assertRaisesRegex(RuntimeError, "adapter failure"):
                subject.run_compatibility(archive, soza_repo_root=soza)


if __name__ == "__main__":
    unittest.main()
