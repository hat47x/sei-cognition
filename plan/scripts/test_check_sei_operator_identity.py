#!/usr/bin/env python3
"""Self-tests for check_sei_operator_identity.py using only the Python stdlib."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("check_sei_operator_identity.py")
SPEC = importlib.util.spec_from_file_location("check_sei_operator_identity", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class SeiOperatorIdentityCheckerTest(unittest.TestCase):
    def make_repo(self, files: dict[str, str] | None = None) -> Path:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        root = Path(temp_dir.name)
        if files:
            for relative, content in files.items():
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")
        return root

    def test_current_sei_operator_tokens_pass(self) -> None:
        root = self.make_repo(
            {
                "runtime/TEI_VERSION_EXCHANGE_CURRENT_READINESS_2026-09-06.md":
                    "SEI_REPO=/path/to/sei-cognition\n--sei-repo-root \"$SEI_REPO\"\n",
                "runtime/integration/run_tei_version_exchange_evidence.py":
                    'stage = "sei_go_toolchain"\nkey = "seiGoVersion"\n',
            }
        )
        self.assertEqual([], MODULE.check_repo(root))

    def test_old_cli_and_variable_are_rejected(self) -> None:
        root = self.make_repo(
            {
                "runtime/TEI_VERSION_EXCHANGE_CURRENT_READINESS_2026-09-06.md":
                    'SOZA_REPO=/path/to/soza\n--soza-repo-root "$SOZA_REPO"\n'
            }
        )
        errors = MODULE.check_repo(root)
        self.assertEqual(3, len(errors))
        self.assertTrue(any("SOZA_REPO" in error for error in errors))
        self.assertTrue(any("--soza-repo-root" in error for error in errors))

    def test_old_stage_and_result_key_are_rejected(self) -> None:
        root = self.make_repo(
            {
                "runtime/integration/run_tei_version_exchange_evidence.py":
                    'stage = "soza_teiintegration_live_test"\nkey = "sozaGoRequirement"\n'
            }
        )
        errors = MODULE.check_repo(root)
        self.assertEqual(2, len(errors))
        self.assertTrue(any("soza_teiintegration_live_test" in error for error in errors))
        self.assertTrue(any("sozaGoRequirement" in error for error in errors))

    def test_non_tei_production_integration_script_is_scanned(self) -> None:
        root = self.make_repo(
            {
                "runtime/integration/e3b_m1b_ollama_adapter.py":
                    'legacy_env = "SOZA_GO"\n'
            }
        )
        errors = MODULE.check_repo(root)
        self.assertEqual(1, len(errors))
        self.assertIn("SOZA_GO", errors[0])

    def test_historical_names_and_legacy_schema_are_not_banned(self) -> None:
        root = self.make_repo(
            {
                "runtime/TEI_GITHUB_HOSTED_JOB_START_DELTA_2026-09-06.md":
                    "workflow = SOZA E3b-P2 TEI Evidence\n"
                    "artifact = tei-soza-e3b-p2-linux-amd64\n"
                    "historical schema = soza.tei-version-exchange-evidence-run/v1\n"
            }
        )
        self.assertEqual([], MODULE.check_repo(root))

    def test_runtime_evidence_is_outside_current_operator_surface(self) -> None:
        root = self.make_repo(
            {
                "runtime/evidence/fixed/observation.json":
                    '{"stage":"soza_go_toolchain","schema":"soza.historical/v1"}\n'
            }
        )
        self.assertEqual([], MODULE.check_repo(root))

    def test_test_sources_are_not_scanned_as_operator_surface(self) -> None:
        root = self.make_repo(
            {
                "runtime/integration/test_run_tei_version_exchange_evidence.py":
                    'legacy = "--soza-repo-root"\n'
            }
        )
        self.assertEqual([], MODULE.check_repo(root))


if __name__ == "__main__":
    unittest.main()
