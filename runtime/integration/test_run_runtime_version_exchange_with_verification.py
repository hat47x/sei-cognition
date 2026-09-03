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

READY_PREFLIGHT = {
    "schema": "soza.runtime-version-exchange-preflight/v1",
    "result": "ready",
    "blockers": [],
    "checks": [],
}


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
            prepare_model_dir=None,
            work_dir=Path("/tmp/work"),
            evidence_dir=Path("/tmp/evidence"),
            forwarded=["--keep-work"],
        )
        self.assertEqual("checkout-to-verified-runtime-bundle", mode)
        self.assertEqual(sys.executable, command[0])
        self.assertEqual(str(MODULE.STRICT_ENTRYPOINT), command[1])
        self.assertIn("--kj-atlas-dir", command)
        self.assertIn("--model-dir", command)
        self.assertIn("--work-dir", command)
        self.assertIn("--evidence-dir", command)

    def test_bundle_command_uses_same_strict_entrypoint(self):
        command, mode = MODULE._build_command(
            kj_atlas_dir=None,
            kj_atlas_backend_bundle=Path("/tmp/bundle"),
            model_dir=None,
            prepare_model_dir=None,
            work_dir=None,
            evidence_dir=Path("/tmp/evidence"),
            forwarded=[],
        )
        self.assertEqual("verified-runtime-bundle", mode)
        self.assertEqual(sys.executable, command[0])
        self.assertEqual(str(MODULE.STRICT_ENTRYPOINT), command[1])
        self.assertIn("--kj-atlas-backend-bundle", command)

    def test_prepare_model_dir_is_forwarded_before_separator(self):
        command, _ = MODULE._build_command(
            kj_atlas_dir=None,
            kj_atlas_backend_bundle=Path("/tmp/bundle"),
            model_dir=None,
            prepare_model_dir=Path("/tmp/new-models"),
            work_dir=Path("/tmp/work"),
            evidence_dir=Path("/tmp/evidence"),
            forwarded=["--keep-work"],
        )
        separator = command.index("--")
        self.assertLess(command.index("--prepare-model-dir"), separator)
        self.assertLess(command.index("--work-dir"), separator)
        self.assertGreater(command.index("--keep-work"), separator)

    def test_forwarded_identity_and_evidence_options_are_rejected(self):
        for option in (
            "--kj-atlas-dir",
            "--kj-atlas-backend-bundle=/tmp/x",
            "--model-dir",
            "--prepare-model-dir",
            "--evidence-dir",
            "--work-dir",
        ):
            with self.subTest(option=option):
                with self.assertRaises(ValueError):
                    MODULE._reject_forwarded_options([option])

    def test_preflight_command_checks_existing_inputs_before_strict_execution(self):
        command = MODULE._build_preflight_command(
            kj_atlas_dir=None,
            kj_atlas_backend_bundle=Path("/tmp/bundle"),
            model_dir=Path("/tmp/models"),
            work_dir=Path("/tmp/work"),
            evidence_dir=Path("/tmp/evidence"),
            forwarded=[
                "--runtime-a-archive",
                "/tmp/a.tar.zst",
                "--keep-work",
                "--runtime-b-archive=/tmp/b.tar.zst",
            ],
        )
        self.assertEqual(sys.executable, command[0])
        self.assertEqual(str(MODULE.PREFLIGHT), command[1])
        self.assertIn("--kj-atlas-backend-bundle", command)
        self.assertIn("--model-dir", command)
        self.assertIn("--work-dir", command)
        self.assertIn("--evidence-dir", command)
        self.assertIn("--runtime-a-archive", command)
        self.assertIn("/tmp/a.tar.zst", command)
        self.assertIn("--runtime-b-archive=/tmp/b.tar.zst", command)
        self.assertNotIn("--keep-work", command)
        self.assertNotIn("--prepare-model-dir", command)
        self.assertEqual("--json", command[-1])

    def test_prepare_model_path_is_not_required_by_side_effect_free_preflight(self):
        command = MODULE._build_preflight_command(
            kj_atlas_dir=Path("/tmp/kj"),
            kj_atlas_backend_bundle=None,
            model_dir=None,
            work_dir=None,
            evidence_dir=Path("/tmp/evidence"),
            forwarded=[],
        )
        self.assertNotIn("--model-dir", command)
        self.assertNotIn("--prepare-model-dir", command)

    def test_missing_runtime_archive_value_is_rejected_before_process_start(self):
        with self.assertRaisesRegex(ValueError, "requires PATH"):
            MODULE._runtime_archive_preflight_arguments(["--runtime-a-archive"])

    def test_blocked_preflight_stops_before_strict_execution(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            with patch.object(
                MODULE,
                "_run_preflight",
                side_effect=ValueError("runtime exchange preflight blocked: blockers=['port.ollama']"),
            ), patch.object(MODULE, "_run_and_capture") as runner:
                with self.assertRaisesRegex(ValueError, "preflight blocked"):
                    MODULE.run(
                        kj_atlas_dir=None,
                        kj_atlas_backend_bundle=root / "bundle",
                        model_dir=None,
                        prepare_model_dir=root / "new-models",
                        work_dir=root / "work",
                        evidence_dir=root / "evidence",
                        verification_output=root / "verification.json",
                        forwarded=[],
                    )
            runner.assert_not_called()
            self.assertFalse((root / "new-models").exists())
            self.assertFalse((root / "evidence").exists())

    def test_success_preserves_preflight_runner_observation_and_runs_verifier(self):
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
            with patch.object(MODULE, "_run_preflight", return_value=dict(READY_PREFLIGHT)), patch.object(
                MODULE, "STRICT_ENTRYPOINT", strict
            ), patch.object(MODULE, "EVIDENCE_VERIFIER", verifier):
                status = MODULE.run(
                    kj_atlas_dir=None,
                    kj_atlas_backend_bundle=root / "bundle",
                    model_dir=None,
                    prepare_model_dir=None,
                    work_dir=None,
                    evidence_dir=evidence,
                    verification_output=output,
                    forwarded=[],
                )
            self.assertEqual(0, status)
            preflight = json.loads((evidence / "runtime-exchange-preflight.json").read_text())
            observation = json.loads(
                (evidence / "runtime-exchange-runner-observation.json").read_text()
            )
            log = (evidence / "runtime-exchange-runner.log").read_bytes()
            self.assertEqual("ready", preflight["result"])
            self.assertTrue(observation["completed"])
            self.assertEqual(0, observation["exitCode"])
            self.assertEqual("ready", observation["preflightResult"])
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
            with patch.object(MODULE, "_run_preflight", return_value=dict(READY_PREFLIGHT)), patch.object(
                MODULE, "STRICT_ENTRYPOINT", strict
            ), patch.object(MODULE, "EVIDENCE_VERIFIER", verifier):
                status = MODULE.run(
                    kj_atlas_dir=None,
                    kj_atlas_backend_bundle=root / "bundle",
                    model_dir=None,
                    prepare_model_dir=None,
                    work_dir=None,
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
            self.assertEqual("ready", observation["preflightResult"])
            self.assertTrue(output.is_file())

    def test_verification_output_inside_evidence_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            with self.assertRaises(ValueError):
                MODULE.run(
                    kj_atlas_dir=None,
                    kj_atlas_backend_bundle=root / "bundle",
                    model_dir=None,
                    prepare_model_dir=None,
                    work_dir=None,
                    evidence_dir=root / "evidence",
                    verification_output=root / "evidence" / "verification.json",
                    forwarded=[],
                )

    def test_verification_output_cannot_overlap_source_model_or_work(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            evidence = root / "evidence"
            cases = (
                (
                    "checkout",
                    root / "checkout" / "verification.json",
                    {"kj_atlas_dir": root / "checkout"},
                ),
                (
                    "bundle-parent",
                    root / "bundle-parent",
                    {"kj_atlas_backend_bundle": root / "bundle-parent" / "bundle"},
                ),
                (
                    "model",
                    root / "model" / "verification.json",
                    {"model_dir": root / "model"},
                ),
                (
                    "prepared-model",
                    root / "prepared" / "verification.json",
                    {"prepare_model_dir": root / "prepared"},
                ),
                (
                    "work",
                    root / "work" / "verification.json",
                    {"work_dir": root / "work"},
                ),
            )
            for label, output, overrides in cases:
                with self.subTest(label=label):
                    arguments = {
                        "evidence_dir": evidence,
                        "kj_atlas_dir": None,
                        "kj_atlas_backend_bundle": None,
                        "model_dir": None,
                        "prepare_model_dir": None,
                        "work_dir": None,
                    }
                    arguments.update(overrides)
                    with self.assertRaisesRegex(ValueError, "verification output"):
                        MODULE._protect_verification_output(output, **arguments)

    def test_verification_output_cannot_contain_evidence_directory(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            output = root / "container"
            evidence = output / "evidence"
            with self.assertRaisesRegex(ValueError, "verification output"):
                MODULE._protect_verification_output(
                    output,
                    evidence_dir=evidence,
                    kj_atlas_dir=None,
                    kj_atlas_backend_bundle=None,
                    model_dir=None,
                    prepare_model_dir=None,
                    work_dir=None,
                )

    def test_verification_output_inside_soza_repository_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "SOZA repository"):
            MODULE._protect_verification_output(
                MODULE.SOZA_ROOT / ".tmp-runtime-exchange-verification.json",
                evidence_dir=Path("/tmp/soza-evidence-outside-repository"),
                kj_atlas_dir=None,
                kj_atlas_backend_bundle=None,
                model_dir=None,
                prepare_model_dir=None,
                work_dir=None,
            )

    def test_safe_sibling_verification_output_is_accepted(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            MODULE._protect_verification_output(
                root / "verification.json",
                evidence_dir=root / "evidence",
                kj_atlas_dir=root / "checkout",
                kj_atlas_backend_bundle=None,
                model_dir=root / "model",
                prepare_model_dir=None,
                work_dir=root / "work",
            )


if __name__ == "__main__":
    unittest.main()
