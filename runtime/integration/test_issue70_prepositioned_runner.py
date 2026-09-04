import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch

import run_runtime_version_exchange_prepositioned as subject


PREPARED = {
    "verifiedRunnerInputs": {
        "modelDir": "/artifacts/ollama-models",
        "runtimeAArchive": "/artifacts/runtime-archives/ollama-0.32.13-linux-amd64.tar.zst",
        "runtimeBArchive": "/artifacts/runtime-archives/ollama-0.32.14-linux-amd64.tar.zst",
        "requirePrepositionedArtifacts": True,
    }
}


class PrepositionedRuntimeExchangeRunnerTest(unittest.TestCase):
    def test_checkout_source_builds_verified_runner_command_without_manual_artifact_paths(self):
        with patch.object(subject, "prepare_prepositioned_inputs", return_value=PREPARED) as prepare:
            command, prepared = subject.build_verified_runner_command(
                artifact_root=Path("/artifacts"),
                kj_atlas_dir=Path("/kj-atlas"),
                kj_atlas_backend_bundle=None,
                evidence_dir=Path("/evidence/run-1"),
                verification_output=Path("/evidence/run-1-verification.json"),
                work_dir=Path("/work/run-1"),
            )

        prepare.assert_called_once_with(Path("/artifacts"), verify_only=True)
        self.assertIs(PREPARED, prepared)
        self.assertIn("--kj-atlas-dir", command)
        self.assertIn("/kj-atlas", command)
        self.assertIn("--require-prepositioned-artifacts", command)
        self.assertIn("/artifacts/ollama-models", command)
        separator = command.index("--")
        self.assertEqual(
            [
                "--runtime-a-archive",
                PREPARED["verifiedRunnerInputs"]["runtimeAArchive"],
                "--runtime-b-archive",
                PREPARED["verifiedRunnerInputs"]["runtimeBArchive"],
            ],
            command[separator + 1 :],
        )

    def test_verified_bundle_source_is_supported(self):
        with patch.object(subject, "prepare_prepositioned_inputs", return_value=PREPARED):
            command, _ = subject.build_verified_runner_command(
                artifact_root=Path("/artifacts"),
                kj_atlas_dir=None,
                kj_atlas_backend_bundle=Path("/kj-bundle"),
                evidence_dir=Path("/evidence/run-2"),
                verification_output=None,
                work_dir=None,
            )

        self.assertIn("--kj-atlas-backend-bundle", command)
        self.assertIn("/kj-bundle", command)
        self.assertNotIn("--verification-output", command)
        self.assertNotIn("--work-dir", command)

    def test_invalid_preparation_result_never_starts_verified_runner(self):
        invalid = {
            "verifiedRunnerInputs": {
                "modelDir": "/artifacts/ollama-models",
                "runtimeAArchive": "/artifacts/a",
                "runtimeBArchive": "/artifacts/b",
                "requirePrepositionedArtifacts": False,
            }
        }
        with (
            patch.object(subject, "prepare_prepositioned_inputs", return_value=invalid),
            patch.object(subject.subprocess, "run") as run_process,
        ):
            with self.assertRaisesRegex(ValueError, "requirePrepositionedArtifacts=true"):
                subject.run(
                    artifact_root=Path("/artifacts"),
                    kj_atlas_dir=Path("/kj-atlas"),
                    kj_atlas_backend_bundle=None,
                    evidence_dir=Path("/evidence/run-3"),
                )
        run_process.assert_not_called()

    def test_runner_exit_code_is_preserved(self):
        completed = subprocess.CompletedProcess(args=["python"], returncode=7)
        with (
            patch.object(subject, "prepare_prepositioned_inputs", return_value=PREPARED),
            patch.object(subject.subprocess, "run", return_value=completed) as run_process,
        ):
            exit_code = subject.run(
                artifact_root=Path("/artifacts"),
                kj_atlas_dir=Path("/kj-atlas"),
                kj_atlas_backend_bundle=None,
                evidence_dir=Path("/evidence/run-4"),
            )

        self.assertEqual(7, exit_code)
        run_process.assert_called_once()
        self.assertFalse(run_process.call_args.kwargs["check"])


if __name__ == "__main__":
    unittest.main()
