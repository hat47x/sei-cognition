import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import run_tei_revision_b_prepositioned as subject
import verify_tei_execution_source_identity as source_identity


class TEIRevisionBPrepositionedRunnerTest(unittest.TestCase):
    def make_source(self, root: Path) -> Path:
        repo = root / "tei"
        (repo / "reference/workspace/.tei").mkdir(parents=True)
        (repo / "reference/order_rollout.durable-run.m0.21.start.json").write_text("{}\n", encoding="utf-8")
        (repo / "reference/workspace/.tei/plugin-lock.json").write_text("{}\n", encoding="utf-8")
        (repo / "reference/workspace/input.txt").write_text("fixture\n", encoding="utf-8")
        return repo

    def fake_run(self, argv, *, cwd, env):
        if argv[:2] == ["go", "build"]:
            output = Path(argv[argv.index("-o") + 1])
            output.write_bytes(b"fake-tei-binary")
            output.chmod(0o755)
            return subprocess.CompletedProcess(argv, 0, "", "")
        if argv == ["go", "version"]:
            return subprocess.CompletedProcess(argv, 0, "go version go1.23.2 linux/amd64\n", "")
        if len(argv) > 1 and argv[1] == "deployment-provider-plan":
            return subprocess.CompletedProcess(
                argv,
                0,
                json.dumps({"executors": [{"executorId": "reference"}]}) + "\n",
                "",
            )
        raise AssertionError(argv)

    @mock.patch.object(subject, "_ensure_linux_amd64")
    @mock.patch.object(subject.source_identity, "verify_repository")
    @mock.patch.object(subject, "_run")
    def test_exact_b_checkout_produces_verified_bundle(self, run, verify_source, ensure_platform):
        run.side_effect = self.fake_run
        verify_source.return_value = {
            "result": "verified",
            "head": source_identity.REVISION_B,
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = self.make_source(root)
            output = root / "out.tar.gz"
            result = subject.produce_bundle(repo, output)
            self.assertTrue(output.is_file())
        self.assertEqual("bundle_produced", result["result"])
        self.assertEqual(source_identity.REVISION_B, result["bundle"]["observation"]["source_commit"])
        verify_source.assert_called_once_with(repo.resolve(), expected_head=source_identity.REVISION_B)

    @mock.patch.object(subject, "_ensure_linux_amd64")
    @mock.patch.object(subject.source_identity, "verify_repository")
    @mock.patch.object(subject, "_run")
    def test_source_identity_failure_stops_before_build(self, run, verify_source, ensure_platform):
        verify_source.side_effect = ValueError("HEADが期待値と一致しません")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = self.make_source(root)
            with self.assertRaisesRegex(ValueError, "HEADが期待値"):
                subject.produce_bundle(repo, root / "out.tar.gz")
        run.assert_not_called()

    @mock.patch.object(subject, "_ensure_linux_amd64")
    @mock.patch.object(subject.source_identity, "verify_repository")
    @mock.patch.object(subject, "_run")
    def test_invalid_provider_plan_leaves_no_final_archive(self, run, verify_source, ensure_platform):
        verify_source.return_value = {"result": "verified", "head": source_identity.REVISION_B}

        def invalid_provider(argv, *, cwd, env):
            result = self.fake_run(argv, cwd=cwd, env=env)
            if len(argv) > 1 and argv[1] == "deployment-provider-plan":
                return subprocess.CompletedProcess(argv, 0, '{"unknown":true}\n', "")
            return result

        run.side_effect = invalid_provider
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = self.make_source(root)
            output = root / "out.tar.gz"
            with self.assertRaisesRegex(ValueError, "unknown top-level field"):
                subject.produce_bundle(repo, output)
            self.assertFalse(output.exists())

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
