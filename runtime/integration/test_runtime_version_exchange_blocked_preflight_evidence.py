import importlib.util
import json
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "run_runtime_version_exchange_with_verification_blocked_preflight",
    HERE / "run_runtime_version_exchange_with_verification.py",
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)

BLOCKED_PREFLIGHT = {
    "schema": "sei.runtime-version-exchange-preflight/v1",
    "result": "blocked",
    "blockers": ["port.ollama"],
    "checks": [
        {
            "id": "port.ollama",
            "status": "blocked",
            "detail": "127.0.0.1:11434 は使用できません",
        }
    ],
}


def executable(path: Path, text: str) -> Path:
    path.write_text(text, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)
    return path


class BlockedPreflightEvidenceTest(unittest.TestCase):
    def test_run_preflight_raises_structured_blocked_exception(self):
        completed = subprocess.CompletedProcess(
            args=["preflight"],
            returncode=1,
            stdout=json.dumps(BLOCKED_PREFLIGHT),
            stderr="",
        )
        with patch.object(MODULE.subprocess, "run", return_value=completed):
            with self.assertRaises(MODULE.PreflightBlocked) as raised:
                MODULE._run_preflight(["preflight"])

        self.assertEqual(BLOCKED_PREFLIGHT, raised.exception.report)
        self.assertEqual(1, raised.exception.returncode)
        self.assertIn("port.ollama", str(raised.exception))

    def test_blocked_preflight_is_preserved_without_starting_strict_execution(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            evidence = root / "evidence"
            verification = root / "verification.json"
            prepare_model = root / "prepared-model"
            verifier = executable(
                root / "verifier.py",
                """#!/usr/bin/env python3
import pathlib, sys
args=sys.argv[1:]
out=pathlib.Path(args[args.index('--output')+1])
out.write_text('{\"result\":\"not-sufficient\"}\\n', encoding='utf-8')
raise SystemExit(1)
""",
            )

            blocked = MODULE.PreflightBlocked(dict(BLOCKED_PREFLIGHT), 1)
            with patch.object(MODULE, "_run_preflight", side_effect=blocked), patch.object(
                MODULE,
                "_run_and_capture",
            ) as strict_runner, patch.object(MODULE, "EVIDENCE_VERIFIER", verifier):
                status = MODULE.run(
                    kj_atlas_dir=None,
                    kj_atlas_backend_bundle=root / "bundle",
                    model_dir=None,
                    prepare_model_dir=prepare_model,
                    work_dir=root / "work",
                    evidence_dir=evidence,
                    verification_output=verification,
                    forwarded=[],
                )

            self.assertEqual(2, status)
            strict_runner.assert_not_called()
            self.assertFalse(prepare_model.exists())
            self.assertTrue(evidence.is_dir())
            self.assertEqual(
                BLOCKED_PREFLIGHT,
                json.loads((evidence / "runtime-exchange-preflight.json").read_text()),
            )
            observation = json.loads(
                (evidence / "runtime-exchange-preflight-observation.json").read_text()
            )
            self.assertTrue(observation["completed"])
            self.assertEqual(1, observation["exitCode"])
            self.assertEqual("blocked", observation["preflightResult"])
            self.assertEqual(["port.ollama"], observation["blockers"])
            self.assertFalse(observation["strictStarted"])
            self.assertEqual("not_evaluated", observation["qualityJudgement"])
            self.assertTrue(verification.is_file())

    def test_malformed_preflight_error_still_does_not_create_evidence(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            evidence = root / "evidence"
            with patch.object(
                MODULE,
                "_run_preflight",
                side_effect=ValueError("runtime exchange preflightのJSONを読めません"),
            ), patch.object(MODULE, "_run_and_capture") as strict_runner:
                with self.assertRaisesRegex(ValueError, "JSONを読めません"):
                    MODULE.run(
                        kj_atlas_dir=None,
                        kj_atlas_backend_bundle=root / "bundle",
                        model_dir=None,
                        prepare_model_dir=None,
                        work_dir=None,
                        evidence_dir=evidence,
                        verification_output=root / "verification.json",
                        forwarded=[],
                    )

            strict_runner.assert_not_called()
            self.assertFalse(evidence.exists())


if __name__ == "__main__":
    unittest.main()
