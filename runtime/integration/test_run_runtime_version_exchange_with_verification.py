import importlib.util
import json
import stat
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "run_runtime_version_exchange_with_verification",
    HERE / "run_runtime_version_exchange_with_verification.py",
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def executable(path: Path, text: str) -> Path:
    path.write_text(text, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)
    return path


class VerifiedRunnerTest(unittest.TestCase):
    def test_checkout_command_uses_strict_entrypoint(self):
        command, mode = MODULE._build_command(
            kj_atlas_dir=Path("/tmp/kj"),
            kj_atlas_backend_bundle=None,
            model_dir=Path("/tmp/models"),
            evidence_dir=Path("/tmp/evidence"),
            forwarded=["--keep-work"],
        )
        self.assertEqual("checkout-to-verified-runtime-bundle", mode)
        self.assertEqual(sys.executable, command[0])
        self.assertEqual(str(MODULE.STRICT_ENTRYPOINT), command[1])
        self.assertIn("--kj-atlas-dir", command)
        self.assertIn("--model-dir", command)
        self.assertIn("--evidence-dir", command)

    def test_bundle_command_uses_same_strict_entrypoint(self):
        command, mode = MODULE._build_command(
            kj_atlas_dir=None,
            kj_atlas_backend_bundle=Path("/tmp/bundle"),
            model_dir=None,
            evidence_dir=Path("/tmp/evidence"),
            forwarded=[],
        )
        self.assertEqual("verified-runtime-bundle", mode)
        self.assertEqual(sys.executable, command[0])
        self.assertEqual(str(MODULE.STRICT_ENTRYPOINT), command[1])
        self.assertIn("--kj-atlas-backend-bundle", command)

    def test_forwarded_identity_and_evidence_options_are_rejected(self):
        for option in (
            "--kj-atlas-dir",
            "--kj-atlas-backend-bundle=/tmp/x",
            "--model-dir",
            "--evidence-dir",
        ):
            with self.subTest(option=option):
                with self.assertRaises(ValueError):
                    MODULE._reject_forwarded_options([option])

    def test_success_preserves_runner_observation_and_runs_verifier(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            strict = executable(
                root / "strict.py",
                """#!/usr/bin/env python3
import pathlib, sys
args=sys.argv[1:]
p=pathlib.Path(args[args.index('--evidence-dir')+1])
p.mkdir()
print('fixture strict output')
""",
            )
            verifier = executable(
                root / "verifier.py",
                """#!/usr/bin/env python3
import pathlib, sys
args=sys.argv[1:]
out=pathlib.Path(args[args.index('--output')+1])
out.write_text('{\"result\":\"ready-to-review\"}\\n')
""",
            )
            evidence = root / "evidence"
            output = root / "verification.json"
            with patch.object(MODULE, "STRICT_ENTRYPOINT", strict), patch.object(
                MODULE, "EVIDENCE_VERIFIER", verifier
            ):
                status = MODULE.run(
                    kj_atlas_dir=None,
                    kj_atlas_backend_bundle=root / "bundle",
                    model_dir=None,
                    evidence_dir=evidence,
                    verification_output=output,
                    forwarded=[],
                )
            self.assertEqual(0, status)
            observation = json.loads(
                (evidence / "runtime-exchange-runner-observation.json").read_text()
            )
            log = (evidence / "runtime-exchange-runner.log").read_bytes()
            self.assertTrue(observation["completed"])
            self.assertEqual(0, observation["exitCode"])
            self.assertEqual("verified-runtime-bundle", observation["sourcePreparation"])
            self.assertEqual(len(log), observation["combinedOutputBytes"])
            self.assertIn(b"fixture strict output", log)
            self.assertTrue(output.is_file())

    def test_failure_preserves_observation_but_returns_strict_status(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            strict = executable(
                root / "strict.py",
                """#!/usr/bin/env python3
import pathlib, sys
args=sys.argv[1:]
p=pathlib.Path(args[args.index('--evidence-dir')+1])
p.mkdir()
print('fixture failure')
raise SystemExit(7)
""",
            )
            verifier = executable(
                root / "verifier.py",
                """#!/usr/bin/env python3
import pathlib, sys
args=sys.argv[1:]
out=pathlib.Path(args[args.index('--output')+1])
out.write_text('{\"result\":\"not-sufficient\"}\\n')
raise SystemExit(1)
""",
            )
            evidence = root / "evidence"
            output = root / "verification.json"
            with patch.object(MODULE, "STRICT_ENTRYPOINT", strict), patch.object(
                MODULE, "EVIDENCE_VERIFIER", verifier
            ):
                status = MODULE.run(
                    kj_atlas_dir=None,
                    kj_atlas_backend_bundle=root / "bundle",
                    model_dir=None,
                    evidence_dir=evidence,
                    verification_output=output,
                    forwarded=[],
                )
            self.assertEqual(7, status)
            observation = json.loads(
                (evidence / "runtime-exchange-runner-observation.json").read_text()
            )
            self.assertFalse(observation["completed"])
            self.assertEqual(7, observation["exitCode"])
            self.assertTrue(output.is_file())

    def test_verification_output_inside_evidence_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            with self.assertRaises(ValueError):
                MODULE.run(
                    kj_atlas_dir=None,
                    kj_atlas_backend_bundle=root / "bundle",
                    model_dir=None,
                    evidence_dir=root / "evidence",
                    verification_output=root / "evidence" / "verification.json",
                    forwarded=[],
                )


if __name__ == "__main__":
    unittest.main()
