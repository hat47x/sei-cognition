from __future__ import annotations

import copy
import hashlib
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
from validate_execution_attempt import (  # noqa: E402
    canonical_attempt_digest,
    validate_completed_attempt,
)

ATTEMPT_PATH = HERE / "execution_attempt.json"
RUN_PATH = RUN_DIR / "evaluation_run.json"
PREREG_PATH = SACS_DIR / "cross_stage_benchmark_preregistration.json"


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def completed_attempt(run: dict, *, exit_code: int = 0) -> dict:
    attempt = json.loads(ATTEMPT_PATH.read_text(encoding="utf-8"))
    attempt.update({
        "state": "completed",
        "attempt_id": "attempt:integration:001",
        "started_at": "2026-09-18T19:30:00Z",
        "completed_at": "2026-09-18T19:31:00Z",
        "exit_code": exit_code,
        "outcome": "succeeded" if exit_code == 0 else "failed",
        "observed_environment": copy.deepcopy(run["environment"]),
        "raw_evidence": [
            {
                "kind": "runner-log",
                "ref": "evidence:integration:runner-log",
                "digest": sha("runner-log"),
            },
            {
                "kind": "environment-capture",
                "ref": "evidence:integration:environment",
                "digest": sha("environment"),
            },
        ],
    })
    if exit_code == 0:
        attempt["raw_evidence"].append({
            "kind": "raw-output",
            "ref": "evidence:integration:raw-output",
            "digest": sha("raw-output"),
        })
    attempt["run_binding"]["digest"] = run["run_digest"]
    attempt["executor"] = {
        "ref": "executor:integration:v1",
        "commit": "c" * 40,
    }
    attempt["attempt_digest"] = canonical_attempt_digest(attempt)
    return attempt


class ExecutionAttemptIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.current_run = json.loads(RUN_PATH.read_text(encoding="utf-8"))
        self.current_prereg = json.loads(PREREG_PATH.read_text(encoding="utf-8"))
        self.current_freeze = load_directory(FREEZE_DIR)

        self.frozen = freeze_documents(
            synthetic_freeze_draft(),
            "2026-09-18T19:20:00Z",
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

    def test_successful_attempt_passes_real_upstream_chain(self) -> None:
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

    def test_failed_attempt_passes_real_upstream_chain_without_result(self) -> None:
        attempt = completed_attempt(self.run, exit_code=17)
        self.assertEqual(
            validate_completed_attempt(
                attempt,
                self.run,
                self.prereg,
                self.frozen,
            ),
            [],
        )
        self.assertFalse(attempt["results_generated"])
        self.assertFalse(
            any(item["kind"] == "raw-output" for item in attempt["raw_evidence"])
        )

    def test_current_draft_chain_cannot_complete_attempt(self) -> None:
        attempt = completed_attempt(self.run)
        errors = validate_completed_attempt(
            attempt,
            self.current_run,
            self.current_prereg,
            self.current_freeze,
        )
        self.assert_error(errors, "authorized run")
        self.assert_error(errors, "full unlock")

    def test_attempt_run_digest_mismatch_is_rejected_after_upstream_passes(self) -> None:
        attempt = completed_attempt(self.run)
        attempt["run_binding"]["digest"] = "0" * 64
        attempt["attempt_digest"] = canonical_attempt_digest(attempt)
        errors = validate_completed_attempt(
            attempt,
            self.run,
            self.prereg,
            self.frozen,
        )
        self.assert_error(errors, "does not match authorized run digest")

    def test_full_unlock_error_is_preserved(self) -> None:
        prereg = frozen_prereg(self.frozen)
        attempt = completed_attempt(self.run)
        errors = validate_completed_attempt(
            attempt,
            self.run,
            prereg,
            self.frozen,
        )
        self.assert_error(
            errors,
            "unlock requires authorized explicit evaluation-run artifact",
        )


if __name__ == "__main__":
    unittest.main()
