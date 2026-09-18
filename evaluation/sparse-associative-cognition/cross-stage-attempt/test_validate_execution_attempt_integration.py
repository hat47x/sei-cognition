from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SACS_DIR = HERE.parent
RUN_DIR = SACS_DIR / "cross-stage-run"
FREEZE_DIR = SACS_DIR / "cross-stage-freeze"

for path in (HERE, SACS_DIR, RUN_DIR, FREEZE_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from freeze_manifests import freeze_documents, load_directory  # noqa: E402
from test_validate_evaluation_run import (  # noqa: E402
    authorized_run,
    frozen_prereg,
    synthetic_freeze_draft,
)
from test_validate_execution_attempt import completed_attempt  # noqa: E402
from validate_execution_attempt import (  # noqa: E402
    canonical_attempt_digest,
    validate_completed_attempt,
)

PREREG_PATH = SACS_DIR / "cross_stage_benchmark_preregistration.json"
RUN_PATH = RUN_DIR / "evaluation_run.json"


class ExecutionAttemptIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.current_prereg = json.loads(PREREG_PATH.read_text(encoding="utf-8"))
        self.current_run = json.loads(RUN_PATH.read_text(encoding="utf-8"))
        self.current_freeze = load_directory(FREEZE_DIR)

        self.frozen = freeze_documents(
            synthetic_freeze_draft(),
            "2026-09-18T16:10:00Z",
        )
        self.prereg = frozen_prereg(self.frozen)
        self.prereg["evaluation_run"].update({
            "state": "authorized",
            "current_run_authorized": True,
        })
        self.run = authorized_run(self.frozen)

    def assert_error(self, errors: list[str], fragment: str) -> None:
        self.assertTrue(
            any(fragment in error for error in errors),
            f"expected {fragment!r}; got {errors!r}",
        )

    def test_current_draft_upstream_rejects_completed_attempt(self) -> None:
        attempt = completed_attempt(self.run)
        errors = validate_completed_attempt(
            attempt,
            self.run,
            self.current_prereg,
            self.current_freeze,
        )
        self.assert_error(errors, "authorized run:")
        self.assert_error(errors, "full unlock:")

    def test_synthetic_successful_attempt_passes_actual_upstream_validation(self) -> None:
        attempt = completed_attempt(self.run)
        self.assertEqual(
            validate_completed_attempt(
                attempt,
                self.run,
                self.prereg,
                self.frozen,
            ),
            [],
        )

    def test_synthetic_failed_attempt_passes_actual_upstream_validation(self) -> None:
        attempt = completed_attempt(self.run, exit_code=17)
        self.assertEqual(attempt["outcome"], "failed")
        self.assertFalse(
            any(item["kind"] == "raw-output" for item in attempt["raw_evidence"])
        )
        self.assertEqual(
            validate_completed_attempt(
                attempt,
                self.run,
                self.prereg,
                self.frozen,
            ),
            [],
        )

    def test_attempt_run_digest_mismatch_rejects_with_actual_upstream(self) -> None:
        attempt = completed_attempt(self.run)
        attempt["run_binding"]["digest"] = "0" * 64
        attempt["attempt_digest"] = canonical_attempt_digest(attempt)
        self.assert_error(
            validate_completed_attempt(
                attempt,
                self.run,
                self.prereg,
                self.frozen,
            ),
            "does not match authorized run digest",
        )

    def test_full_unlock_error_is_preserved_by_actual_upstream(self) -> None:
        attempt = completed_attempt(self.run)
        prereg = copy.deepcopy(self.prereg)
        prereg["evaluation_run"].update({
            "state": "draft",
            "current_run_authorized": False,
        })
        errors = validate_completed_attempt(
            attempt,
            self.run,
            prereg,
            self.frozen,
        )
        self.assert_error(
            errors,
            "full unlock: unlock requires authorized explicit evaluation-run artifact",
        )

    def test_post_completion_mutation_rejects_with_actual_upstream(self) -> None:
        attempt = completed_attempt(self.run)
        attempt["executor"]["ref"] = "executor:mutated-after-completion"
        self.assert_error(
            validate_completed_attempt(
                attempt,
                self.run,
                self.prereg,
                self.frozen,
            ),
            "attempt_digest does not match canonical content",
        )


if __name__ == "__main__":
    unittest.main()
