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
        (go_root / "go.mod").write_text(
            "module test\n\ngo 1.25\n", encoding="utf-8"
        )
        (go_root / "teiintegration/tei_live_test.go").write_text(
            "package teiintegration\n", encoding="utf-8"
        )
        return root

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

    def test_reference_identity_accepts_matching_metadata_and_staged_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive = self.make_bundle(root)
            paths = subject._stage_bundle(archive, root / "stage")
            expected = {
                subject.FIXED_WORKSPACE: subject._git_tree_sha1(paths["workspace"]),
                subject.FIXED_RUN: subject._git_blob_sha1(paths["run"]),
                subject.FIXED_PLUGIN_LOCK: subject._git_blob_sha1(
                    paths["plugin_lock"]
                ),
            }
            metadata = {
                "reference_input_source_commit": subject.REVISION_A,
                "reference_workspace_tree": expected[subject.FIXED_WORKSPACE],
                "reference_run_blob": expected[subject.FIXED_RUN],
                "reference_plugin_lock_blob": expected[subject.FIXED_PLUGIN_LOCK],
            }
            result = subject._verify_reference_input_identity(
                paths, metadata, expected_objects=expected
            )
        self.assertEqual(subject.REVISION_A, result["sourceCommit"])
        self.assertEqual(expected, result["objects"])

    def test_reference_identity_rejects_metadata_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive = self.make_bundle(root)
            paths = subject._stage_bundle(archive, root / "stage")
            expected = {
                subject.FIXED_WORKSPACE: subject._git_tree_sha1(paths["workspace"]),
                subject.FIXED_RUN: subject._git_blob_sha1(paths["run"]),
                subject.FIXED_PLUGIN_LOCK: subject._git_blob_sha1(
                    paths["plugin_lock"]
                ),
            }
            metadata = {
                "reference_input_source_commit": "0" * 40,
                "reference_workspace_tree": expected[subject.FIXED_WORKSPACE],
                "reference_run_blob": expected[subject.FIXED_RUN],
                "reference_plugin_lock_blob": expected[subject.FIXED_PLUGIN_LOCK],
            }
            with self.assertRaisesRegex(ValueError, "bundle metadata"):
                subject._verify_reference_input_identity(
                    paths, metadata, expected_objects=expected
                )

    def test_soza_source_identity_rejects_dirty_runtime_boundary(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "soza"
            (root / "runtime/go").mkdir(parents=True)
            (root / "runtime/go/file.go").write_text(
                "package x\n", encoding="utf-8"
            )
            subprocess.run(["git", "-C", str(root), "init", "-q"], check=True)
            subprocess.run(
                [
                    "git",
                    "-C",
                    str(root),
                    "config",
                    "user.email",
                    "test@example.invalid",
                ],
                check=True,
            )
            subprocess.run(
                ["git", "-C", str(root), "config", "user.name", "test"],
                check=True,
            )
            subprocess.run(["git", "-C", str(root), "add", "."], check=True)
            subprocess.run(
                ["git", "-C", str(root), "commit", "-qm", "fixture"],
                check=True,
            )
            (root / "runtime/go/file.go").write_text(
                "package changed\n", encoding="utf-8"
            )
            with self.assertRaisesRegex(ValueError, "未commit変更"):
                subject._verify_soza_source_identity(root, paths=["runtime/go"])

    @mock.patch.object(subject, "_verify_soza_source_identity")
    @mock.patch.object(subject.bundle_verifier, "verify_bundle")
    def test_bundle_verifier_failure_has_identity_stage(self, verify, verify_soza):
        verify_soza.return_value = {"head": "e" * 40, "objects": {}}
        verify.side_effect = ValueError("binary SHA mismatch")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive = self.make_bundle(root)
            soza = self.make_soza(root / "soza")
            with self.assertRaises(subject.TEIAdapterStageError) as raised:
                subject.run_compatibility(archive, soza_repo_root=soza)
        self.assertEqual("bundle_identity_verification", raised.exception.stage)

    @mock.patch.object(subject, "_verify_soza_source_identity")
    @mock.patch.object(subject, "_verify_reference_input_identity")
    @mock.patch.object(subject, "_ensure_linux_amd64")
    @mock.patch.object(subject.bundle_verifier, "verify_bundle")
    def test_reference_failure_has_reference_stage(
        self, verify, ensure, verify_reference, verify_soza
    ):
        verify.return_value = self.verified_bundle()
        verify_soza.return_value = {"head": "e" * 40, "objects": {}}
        verify_reference.side_effect = ValueError("reference input mismatch")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive = self.make_bundle(root)
            soza = self.make_soza(root / "soza")
            with self.assertRaises(subject.TEIAdapterStageError) as raised:
                subject.run_compatibility(archive, soza_repo_root=soza)
        self.assertEqual("reference_input_identity", raised.exception.stage)

    @mock.patch.object(subject, "_verify_soza_source_identity")
    @mock.patch.object(subject, "_verify_reference_input_identity")
    @mock.patch.object(subject, "_ensure_linux_amd64")
    @mock.patch.object(subject.subprocess, "run")
    @mock.patch.object(subject.bundle_verifier, "verify_bundle")
    def test_verified_bundle_runs_existing_live_test_with_provenance(
        self, verify, run, ensure, verify_reference, verify_soza
    ):
        verify.return_value = self.verified_bundle()
        verify_reference.return_value = {
            "sourceCommit": subject.REVISION_A,
            "objects": {},
        }
        verify_soza.return_value = {"head": "e" * 40, "objects": {}}
        run.side_effect = [
            subprocess.CompletedProcess(
                [], 0, "go version go1.25.0 linux/amd64\n", ""
            ),
            subprocess.CompletedProcess([], 0, "PASS\n", ""),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive = self.make_bundle(root)
            soza = self.make_soza(root / "soza")
            result = subject.run_compatibility(archive, soza_repo_root=soza)
        self.assertEqual("adapter_compatible", result["result"])
        self.assertEqual("1.25", result["sozaGoRequirement"])
        self.assertEqual(
            "go version go1.25.0 linux/amd64", result["sozaGoVersion"]
        )
        self.assertIn("soza_teiintegration_live_test", result["completedStages"])
        argv = run.call_args_list[1].args[0]
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
        env = run.call_args_list[1].kwargs["env"]
        self.assertEqual("1", env["SOZA_E3B_TEI_LIVE"])
        self.assertEqual("local", env["GOTOOLCHAIN"])
        self.assertEqual(
            f"tei-cli:{subject.REVISION_B}:reference:{subject.REVISION_A}:"
            f"bundle-sha256:{'d' * 64}",
            env["SOZA_TEI_SOURCE_STATE_REF"],
        )

    @mock.patch.object(subject, "_verify_soza_source_identity")
    @mock.patch.object(subject, "_verify_reference_input_identity")
    @mock.patch.object(subject, "_ensure_linux_amd64")
    @mock.patch.object(subject.subprocess, "run")
    @mock.patch.object(subject.bundle_verifier, "verify_bundle")
    def test_go_toolchain_failure_has_stage(
        self, verify, run, ensure, verify_reference, verify_soza
    ):
        verify.return_value = self.verified_bundle()
        verify_reference.return_value = {
            "sourceCommit": subject.REVISION_A,
            "objects": {},
        }
        verify_soza.return_value = {"head": "e" * 40, "objects": {}}
        run.return_value = subprocess.CompletedProcess(
            ["go", "version"], 1, "", "go unavailable"
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive = self.make_bundle(root)
            soza = self.make_soza(root / "soza")
            with self.assertRaises(subject.TEIAdapterStageError) as raised:
                subject.run_compatibility(archive, soza_repo_root=soza)
        exc = raised.exception
        self.assertEqual("soza_go_toolchain", exc.stage)
        self.assertEqual(1, exc.returncode)
        self.assertEqual("go unavailable", exc.stderr)

    @mock.patch.object(subject, "_verify_soza_source_identity")
    @mock.patch.object(subject, "_verify_reference_input_identity")
    @mock.patch.object(subject, "_ensure_linux_amd64")
    @mock.patch.object(subject.subprocess, "run")
    @mock.patch.object(subject.bundle_verifier, "verify_bundle")
    def test_old_go_is_rejected_before_live_test(
        self, verify, run, ensure, verify_reference, verify_soza
    ):
        verify.return_value = self.verified_bundle()
        verify_reference.return_value = {
            "sourceCommit": subject.REVISION_A,
            "objects": {},
        }
        verify_soza.return_value = {"head": "e" * 40, "objects": {}}
        run.return_value = subprocess.CompletedProcess(
            [], 0, "go version go1.24.9 linux/amd64\n", ""
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive = self.make_bundle(root)
            soza = self.make_soza(root / "soza")
            with self.assertRaises(subject.TEIAdapterStageError) as raised:
                subject.run_compatibility(archive, soza_repo_root=soza)
        exc = raised.exception
        self.assertEqual("soza_go_toolchain", exc.stage)
        self.assertIn("required>=1.25", exc.message)
        self.assertEqual(1, run.call_count)

    @mock.patch.object(subject, "_verify_soza_source_identity")
    @mock.patch.object(subject, "_verify_reference_input_identity")
    @mock.patch.object(subject, "_ensure_linux_amd64")
    @mock.patch.object(subject.subprocess, "run")
    @mock.patch.object(subject.bundle_verifier, "verify_bundle")
    def test_live_test_failure_keeps_process_stage_without_text_inference(
        self, verify, run, ensure, verify_reference, verify_soza
    ):
        verify.return_value = self.verified_bundle()
        verify_reference.return_value = {
            "sourceCommit": subject.REVISION_A,
            "objects": {},
        }
        verify_soza.return_value = {"head": "e" * 40, "objects": {}}
        run.side_effect = [
            subprocess.CompletedProcess(
                [], 0, "go version go1.25.0 linux/amd64\n", ""
            ),
            subprocess.CompletedProcess(
                [], 1, "FAIL\n", "strict decode / validator failure"
            ),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive = self.make_bundle(root)
            soza = self.make_soza(root / "soza")
            with self.assertRaises(subject.TEIAdapterStageError) as raised:
                subject.run_compatibility(archive, soza_repo_root=soza)
        exc = raised.exception
        self.assertEqual("soza_teiintegration_live_test", exc.stage)
        self.assertIn("validator", exc.stderr)
        self.assertNotEqual("validator", exc.stage)
        self.assertNotEqual("strict_decode", exc.stage)

    def test_stage_error_detail_is_bounded(self):
        exc = subject.TEIAdapterStageError(
            "soza_teiintegration_live_test",
            "failed",
            command=["go", "test"],
            returncode=1,
            stdout="a" * (subject.MAX_STAGE_OUTPUT + 10),
            stderr="b" * (subject.MAX_STAGE_OUTPUT + 20),
        )
        detail = exc.as_dict()
        self.assertEqual(subject.MAX_STAGE_OUTPUT, len(detail["stdoutTail"]))
        self.assertEqual(subject.MAX_STAGE_OUTPUT, len(detail["stderrTail"]))


if __name__ == "__main__":
    unittest.main()
