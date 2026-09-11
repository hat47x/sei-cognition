import json
import os
import subprocess
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import run_tei_revision_b_prepositioned as subject
import verify_tei_execution_source_identity as source_identity


class TEIRevisionBPrepositionedRunnerTest(unittest.TestCase):
    def make_source(self, root: Path, name: str, fixture: str) -> Path:
        repo = root / name
        (repo / "reference/workspace/.tei").mkdir(parents=True)
        (repo / "reference/order_rollout.durable-run.m0.21.start.json").write_text(
            "{}\n", encoding="utf-8"
        )
        (repo / "reference/workspace/.tei/plugin-lock.json").write_text(
            "{}\n", encoding="utf-8"
        )
        (repo / "reference/workspace/input.txt").write_text(
            fixture + "\n", encoding="utf-8"
        )
        return repo

    def fake_run(self, argv, *, cwd, env):
        if argv[:2] == ["go", "build"]:
            output = Path(argv[argv.index("-o") + 1])
            output.write_bytes(b"fake-tei-binary")
            output.chmod(0o755)
            return subprocess.CompletedProcess(argv, 0, "", "")
        if argv == ["go", "version"]:
            return subprocess.CompletedProcess(
                argv, 0, "go version go1.23.2 linux/amd64\n", ""
            )
        if argv == ["go", "env", "GOOS", "GOARCH"]:
            return subprocess.CompletedProcess(argv, 0, "linux\namd64\n", "")
        if len(argv) > 1 and argv[1] == "deployment-provider-plan":
            self.provider_argv = argv
            return subprocess.CompletedProcess(
                argv,
                0,
                json.dumps({"executors": [{"executorId": "reference"}]}) + "\n",
                "",
            )
        raise AssertionError(argv)

    def verified_observations(self):
        source_observation = {
            "result": "verified",
            "head": source_identity.REVISION_B,
        }
        reference_observation = {
            "result": "verified",
            "head": source_identity.REVISION_A,
            "executionSourceObjects": source_identity.REVISION_A_REFERENCE_OBJECTS,
        }
        return [
            source_observation,
            reference_observation,
            source_observation,
            reference_observation,
        ]

    def make_pair(self, root: Path):
        return (
            self.make_source(root, "tei-b", "revision-b-input"),
            self.make_source(root, "tei-a", "revision-a-input"),
        )

    @mock.patch.object(subject.source_identity, "verify_repository")
    @mock.patch.object(subject, "_run")
    def test_output_inside_input_checkout_is_rejected_before_side_effect(
        self, run, verify_source
    ):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source_repo, reference_repo = self.make_pair(root)
            for input_repo in (source_repo, reference_repo):
                with self.subTest(input_repo=input_repo.name):
                    output = input_repo / "generated-evidence/out.tar.gz"
                    with self.assertRaisesRegex(ValueError, "配下には置けません"):
                        subject.produce_bundle(source_repo, reference_repo, output)
                    self.assertFalse(output.parent.exists())
                    verify_source.assert_not_called()
                    run.assert_not_called()

    @mock.patch.object(subject.source_identity, "verify_repository")
    @mock.patch.object(subject, "_run")
    def test_existing_output_archive_is_not_overwritten(self, run, verify_source):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source_repo, reference_repo = self.make_pair(root)
            output = root / "existing.tar.gz"
            output.write_bytes(b"keep")
            with self.assertRaisesRegex(ValueError, "無言で上書き"):
                subject.produce_bundle(source_repo, reference_repo, output)
            self.assertEqual(b"keep", output.read_bytes())
            verify_source.assert_not_called()
            run.assert_not_called()

    @mock.patch.object(subject.source_identity, "verify_repository")
    @mock.patch.object(subject, "_run")
    def test_symlink_output_archive_is_rejected(self, run, verify_source):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source_repo, reference_repo = self.make_pair(root)
            target = root / "target.tar.gz"
            output = root / "out.tar.gz"
            output.symlink_to(target)
            with self.assertRaisesRegex(ValueError, "symlink"):
                subject.produce_bundle(source_repo, reference_repo, output)
            self.assertFalse(target.exists())
            verify_source.assert_not_called()
            run.assert_not_called()

    @mock.patch.object(subject.source_identity, "verify_repository")
    @mock.patch.object(subject, "_run")
    def test_output_inside_sei_repository_is_rejected(self, run, verify_source):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source_repo, reference_repo = self.make_pair(root)
            sei_root = root / "sei"
            sei_root.mkdir()
            output = sei_root / "evidence/out.tar.gz"
            with mock.patch.object(subject, "SEI_ROOT", sei_root.resolve()):
                with self.assertRaisesRegex(ValueError, "SEI repository"):
                    subject.produce_bundle(source_repo, reference_repo, output)
            self.assertFalse(output.parent.exists())
            verify_source.assert_not_called()
            run.assert_not_called()

    @mock.patch.object(subject.bundle_verifier, "verify_bundle")
    @mock.patch.object(subject, "_ensure_linux_amd64")
    @mock.patch.object(subject.source_identity, "verify_repository")
    @mock.patch.object(subject, "_run")
    def test_exact_b_checkout_uses_exact_a_reference_input(
        self, run, verify_source, ensure_platform, verify_bundle
    ):
        run.side_effect = self.fake_run
        verify_source.side_effect = self.verified_observations()
        verify_bundle.return_value = {
            "result": "verified",
            "observation": {"source_commit": source_identity.REVISION_B},
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source_repo, reference_repo = self.make_pair(root)
            output = root / "out.tar.gz"
            result = subject.produce_bundle(source_repo, reference_repo, output)
            self.assertTrue(output.is_file())

            with tarfile.open(output, "r:gz") as tar:
                fixed_input = tar.extractfile("reference/workspace/input.txt")
                self.assertIsNotNone(fixed_input)
                self.assertEqual(b"revision-a-input\n", fixed_input.read())
                metadata_file = tar.extractfile("metadata.json")
                self.assertIsNotNone(metadata_file)
                metadata = json.load(metadata_file)

        self.assertEqual("bundle_produced", result["result"])
        self.assertEqual(
            source_identity.REVISION_B,
            result["bundle"]["observation"]["source_commit"],
        )
        self.assertEqual(source_identity.REVISION_A, result["referenceInput"]["head"])
        self.assertEqual(
            source_identity.REVISION_B,
            result["postExecutionIdentity"]["source"]["head"],
        )
        self.assertEqual(
            source_identity.REVISION_A,
            result["postExecutionIdentity"]["referenceInput"]["head"],
        )
        self.assertEqual(
            source_identity.REVISION_A,
            metadata["reference_input_source_commit"],
        )
        self.assertEqual(
            source_identity.REVISION_A_REFERENCE_OBJECTS[subject.FIXED_WORKSPACE],
            metadata["reference_workspace_tree"],
        )
        self.assertIn(str(reference_repo / subject.FIXED_WORKSPACE), self.provider_argv)
        self.assertNotIn(str(source_repo / subject.FIXED_WORKSPACE), self.provider_argv)
        self.assertIn("evidence_bundle_publish", result["completedStages"])
        self.assertEqual(
            [
                mock.call(source_repo.resolve(), expected_head=source_identity.REVISION_B),
                mock.call(
                    reference_repo.resolve(),
                    expected_objects=source_identity.REVISION_A_REFERENCE_OBJECTS,
                    expected_head=source_identity.REVISION_A,
                ),
                mock.call(source_repo.resolve(), expected_head=source_identity.REVISION_B),
                mock.call(
                    reference_repo.resolve(),
                    expected_objects=source_identity.REVISION_A_REFERENCE_OBJECTS,
                    expected_head=source_identity.REVISION_A,
                ),
            ],
            verify_source.call_args_list,
        )
        verify_bundle.assert_called_once()
        self.assertEqual(
            source_identity.REVISION_B,
            verify_bundle.call_args.kwargs["expected_source_commit"],
        )

    @mock.patch.object(subject, "_ensure_linux_amd64")
    @mock.patch.object(subject.source_identity, "verify_repository")
    @mock.patch.object(subject, "_run")
    def test_b_source_identity_failure_has_stage(
        self, run, verify_source, ensure_platform
    ):
        verify_source.side_effect = ValueError("HEADが期待値と一致しません")
        with tempfile.TemporaryDirectory() as tmp:
            source_repo, reference_repo = self.make_pair(Path(tmp))
            with self.assertRaises(subject.TEIEvidenceStageError) as raised:
                subject.produce_bundle(source_repo, reference_repo, Path(tmp) / "out.tar.gz")
        self.assertEqual("revision_b_source_identity", raised.exception.stage)
        self.assertIn("HEADが期待値", raised.exception.message)
        run.assert_not_called()

    @mock.patch.object(subject, "_ensure_linux_amd64")
    @mock.patch.object(subject.source_identity, "verify_repository")
    @mock.patch.object(subject, "_run")
    def test_reference_input_identity_failure_has_stage(
        self, run, verify_source, ensure_platform
    ):
        verify_source.side_effect = [
            {"result": "verified", "head": source_identity.REVISION_B},
            ValueError("Git object identityが期待値と一致しません"),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            source_repo, reference_repo = self.make_pair(Path(tmp))
            with self.assertRaises(subject.TEIEvidenceStageError) as raised:
                subject.produce_bundle(source_repo, reference_repo, Path(tmp) / "out.tar.gz")
        self.assertEqual("revision_a_fixed_reference_identity", raised.exception.stage)
        run.assert_not_called()

    @mock.patch.object(subject, "_ensure_linux_amd64")
    @mock.patch.object(subject.source_identity, "verify_repository")
    @mock.patch.object(subject, "_run")
    def test_go_version_mismatch_has_stage(
        self, run, verify_source, ensure_platform
    ):
        verify_source.side_effect = self.verified_observations()
        run.return_value = subprocess.CompletedProcess(
            ["go", "version"], 0, "go version go1.24.0 linux/amd64\n", ""
        )
        with tempfile.TemporaryDirectory() as tmp:
            source_repo, reference_repo = self.make_pair(Path(tmp))
            with self.assertRaises(subject.TEIEvidenceStageError) as raised:
                subject.produce_bundle(source_repo, reference_repo, Path(tmp) / "out.tar.gz")
        self.assertEqual("tei_go_toolchain", raised.exception.stage)
        self.assertIn("go1.24.0", raised.exception.message)

    @mock.patch.object(subject, "_ensure_linux_amd64")
    @mock.patch.object(subject.source_identity, "verify_repository")
    @mock.patch.object(subject, "_run")
    def test_go_controlled_target_mismatch_has_stage(
        self, run, verify_source, ensure_platform
    ):
        verify_source.side_effect = self.verified_observations()

        def wrong_target(argv, *, cwd, env):
            if argv == ["go", "version"]:
                return subprocess.CompletedProcess(
                    argv, 0, "go version go1.23.2 linux/amd64\n", ""
                )
            if argv == ["go", "env", "GOOS", "GOARCH"]:
                return subprocess.CompletedProcess(argv, 0, "linux\narm64\n", "")
            raise AssertionError(argv)

        run.side_effect = wrong_target
        with tempfile.TemporaryDirectory() as tmp:
            source_repo, reference_repo = self.make_pair(Path(tmp))
            with self.assertRaises(subject.TEIEvidenceStageError) as raised:
                subject.produce_bundle(source_repo, reference_repo, Path(tmp) / "out.tar.gz")
        self.assertEqual("tei_go_toolchain", raised.exception.stage)
        self.assertIn("linux/arm64", raised.exception.message)
        self.assertEqual(
            ["go", "env", "GOOS", "GOARCH"],
            raised.exception.command,
        )

    @mock.patch.object(subject, "_ensure_linux_amd64")
    @mock.patch.object(subject.source_identity, "verify_repository")
    @mock.patch.object(subject, "_run")
    def test_build_failure_has_stage_and_process_detail(
        self, run, verify_source, ensure_platform
    ):
        verify_source.side_effect = self.verified_observations()

        def build_fails(argv, *, cwd, env):
            if argv == ["go", "version"]:
                return subprocess.CompletedProcess(
                    argv, 0, "go version go1.23.2 linux/amd64\n", ""
                )
            if argv == ["go", "env", "GOOS", "GOARCH"]:
                return subprocess.CompletedProcess(argv, 0, "linux\namd64\n", "")
            if argv[:2] == ["go", "build"]:
                return subprocess.CompletedProcess(argv, 2, "", "compile failed")
            raise AssertionError(argv)

        run.side_effect = build_fails
        with tempfile.TemporaryDirectory() as tmp:
            source_repo, reference_repo = self.make_pair(Path(tmp))
            with self.assertRaises(subject.TEIEvidenceStageError) as raised:
                subject.produce_bundle(source_repo, reference_repo, Path(tmp) / "out.tar.gz")
        exc = raised.exception
        self.assertEqual("tei_cli_build", exc.stage)
        self.assertEqual(2, exc.returncode)
        self.assertEqual("compile failed", exc.stderr)
        self.assertEqual("go", exc.command[0])

    @mock.patch.object(subject, "_ensure_linux_amd64")
    @mock.patch.object(subject.source_identity, "verify_repository")
    @mock.patch.object(subject, "_run")
    def test_provider_plan_process_failure_has_process_stage_only(
        self, run, verify_source, ensure_platform
    ):
        verify_source.side_effect = self.verified_observations()

        def provider_fails(argv, *, cwd, env):
            result = self.fake_run(argv, cwd=cwd, env=env)
            if len(argv) > 1 and argv[1] == "deployment-provider-plan":
                return subprocess.CompletedProcess(
                    argv,
                    3,
                    "",
                    "workspace validation failed internally",
                )
            return result

        run.side_effect = provider_fails
        with tempfile.TemporaryDirectory() as tmp:
            source_repo, reference_repo = self.make_pair(Path(tmp))
            with self.assertRaises(subject.TEIEvidenceStageError) as raised:
                subject.produce_bundle(source_repo, reference_repo, Path(tmp) / "out.tar.gz")
        exc = raised.exception
        self.assertEqual("deployment_provider_plan_execution", exc.stage)
        self.assertEqual(3, exc.returncode)
        self.assertIn("workspace validation", exc.stderr)
        # stderr文言からworkspace/validation等のTEI内部substageへは昇格させない。
        self.assertNotEqual("validation", exc.stage)

    @mock.patch.object(subject, "_ensure_linux_amd64")
    @mock.patch.object(subject.source_identity, "verify_repository")
    @mock.patch.object(subject, "_run")
    def test_invalid_provider_plan_has_validation_stage_and_no_final_archive(
        self, run, verify_source, ensure_platform
    ):
        verify_source.side_effect = self.verified_observations()

        def invalid_provider(argv, *, cwd, env):
            result = self.fake_run(argv, cwd=cwd, env=env)
            if len(argv) > 1 and argv[1] == "deployment-provider-plan":
                return subprocess.CompletedProcess(argv, 0, '{"unknown":true}\n', "")
            return result

        run.side_effect = invalid_provider
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source_repo, reference_repo = self.make_pair(root)
            output = root / "out.tar.gz"
            with self.assertRaises(subject.TEIEvidenceStageError) as raised:
                subject.produce_bundle(source_repo, reference_repo, output)
            self.assertFalse(output.exists())
        self.assertEqual("provider_plan_validation", raised.exception.stage)
        self.assertIn("unknown top-level field", raised.exception.message)

    def test_stage_error_detail_is_bounded(self):
        exc = subject.TEIEvidenceStageError(
            "tei_cli_build",
            "failed",
            command=["go", "build"],
            returncode=1,
            stdout="a" * (subject.MAX_STAGE_OUTPUT + 10),
            stderr="b" * (subject.MAX_STAGE_OUTPUT + 20),
        )
        detail = exc.as_dict()
        self.assertEqual(subject.MAX_STAGE_OUTPUT, len(detail["stdoutTail"]))
        self.assertEqual(subject.MAX_STAGE_OUTPUT, len(detail["stderrTail"]))

    def test_controlled_go_env_disables_workspace_and_user_goflags(self):
        with mock.patch.dict(os.environ, {"GOFLAGS": "-mod=vendor"}, clear=False):
            env = subject._controlled_go_env()
        self.assertEqual("off", env["GOWORK"])
        self.assertEqual("off", env["GOENV"])
        self.assertNotIn("GOFLAGS", env)
        self.assertNotIn("GOOS", env)
        self.assertNotIn("GOARCH", env)

    @mock.patch.object(subject.platform, "system", return_value="Darwin")
    @mock.patch.object(subject.platform, "machine", return_value="arm64")
    def test_non_linux_amd64_environment_is_rejected(self, machine, system):
        with self.assertRaisesRegex(ValueError, "Linux/amd64"):
            subject._ensure_linux_amd64()


if __name__ == "__main__":
    unittest.main()
