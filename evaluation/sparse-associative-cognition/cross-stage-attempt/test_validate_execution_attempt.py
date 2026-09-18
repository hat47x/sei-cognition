from __future__ import annotations

import copy
import hashlib
import json
import unittest
from pathlib import Path

from validate_execution_attempt import (
    canonical_attempt_digest,
    validate_attempt_structure,
    validate_completed_attempt,
)

HERE = Path(__file__).resolve().parent
ATTEMPT_PATH = HERE / "execution_attempt.json"


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def synthetic_run() -> dict:
    return {
        "state": "authorized",
        "run_digest": "a" * 64,
        "environment": {
            "os": "linux",
            "arch": "amd64",
            "runtime": "go1.25",
        },
    }


def upstream_ok(run: dict, prereg: dict, freeze: dict) -> list[str]:
    return []


def completed_attempt(run: dict, *, exit_code: int = 0) -> dict:
    attempt = json.loads(ATTEMPT_PATH.read_text(encoding="utf-8"))
    attempt.update({
        "state": "completed",
        "attempt_id": "attempt:fixture:001",
        "started_at": "2026-09-18T16:20:00Z",
        "completed_at": "2026-09-18T16:21:00Z",
        "exit_code": exit_code,
        "outcome": "succeeded" if exit_code == 0 else "failed",
        "observed_environment": copy.deepcopy(run["environment"]),
        "raw_evidence": [
            {
                "kind": "runner-log",
                "ref": "evidence:fixture:runner-log",
                "digest": sha("runner-log"),
            },
            {
                "kind": "environment-capture",
                "ref": "evidence:fixture:environment",
                "digest": sha("environment"),
            },
        ],
    })
    if exit_code == 0:
        attempt["raw_evidence"].append({
            "kind": "raw-output",
            "ref": "evidence:fixture:raw-output",
            "digest": sha("raw-output"),
        })
    attempt["run_binding"]["digest"] = run["run_digest"]
    attempt["executor"] = {
        "ref": "executor:fixture:v1",
        "commit": "b" * 40,
    }
    attempt["attempt_digest"] = canonical_attempt_digest(attempt)
    return attempt


def validate(attempt: dict, run: dict | None = None, upstream=upstream_ok) -> list[str]:
    return validate_completed_attempt(
        attempt,
        run or synthetic_run(),
        {},
        {},
        upstream_validator=upstream,
    )


class ExecutionAttemptTests(unittest.TestCase):
    def setUp(self) -> None:
        self.current = json.loads(ATTEMPT_PATH.read_text(encoding="utf-8"))
        self.run = synthetic_run()

    def assert_error(self, errors: list[str], fragment: str) -> None:
        self.assertTrue(
            any(fragment in error for error in errors),
            f"expected {fragment!r}; got {errors!r}",
        )

    def test_current_draft_attempt_is_structurally_valid(self) -> None:
        self.assertEqual(validate_attempt_structure(self.current), [])

    def test_draft_attempt_cannot_claim_results(self) -> None:
        attempt = copy.deepcopy(self.current)
        attempt["results_generated"] = True
        self.assert_error(validate_attempt_structure(attempt), "results_generated=false")

    def test_synthetic_successful_attempt_is_valid(self) -> None:
        self.assertEqual(validate(completed_attempt(self.run)), [])

    def test_synthetic_failed_attempt_is_valid_without_raw_output(self) -> None:
        self.assertEqual(validate(completed_attempt(self.run, exit_code=17)), [])

    def test_upstream_validation_error_is_preserved(self) -> None:
        attempt = completed_attempt(self.run)
        self.assert_error(
            validate(attempt, upstream=lambda *_: ["authorized run: fixture rejected"]),
            "fixture rejected",
        )

    def test_completed_attempt_must_replace_template_id(self) -> None:
        attempt = completed_attempt(self.run)
        attempt["attempt_id"] = "cross-stage-attempt-template"
        attempt["attempt_digest"] = canonical_attempt_digest(attempt)
        self.assert_error(validate(attempt), "replace the template attempt_id")

    def test_run_digest_binding_is_exact(self) -> None:
        attempt = completed_attempt(self.run)
        attempt["run_binding"]["digest"] = "0" * 64
        attempt["attempt_digest"] = canonical_attempt_digest(attempt)
        self.assert_error(validate(attempt), "does not match authorized run digest")

    def test_observed_environment_must_match_authorized_run(self) -> None:
        attempt = completed_attempt(self.run)
        attempt["observed_environment"]["runtime"] = "go9.99"
        attempt["attempt_digest"] = canonical_attempt_digest(attempt)
        self.assert_error(validate(attempt), "must exactly match authorized run environment")

    def test_executor_commit_requires_git_sha(self) -> None:
        attempt = completed_attempt(self.run)
        attempt["executor"]["commit"] = "main"
        attempt["attempt_digest"] = canonical_attempt_digest(attempt)
        self.assert_error(validate(attempt), "40-char lowercase git SHA")

    def test_timestamps_require_utc_second_format(self) -> None:
        attempt = completed_attempt(self.run)
        attempt["started_at"] = "2026-09-19T01:20:00+09:00"
        attempt["attempt_digest"] = canonical_attempt_digest(attempt)
        self.assert_error(validate(attempt), "UTC second format")

    def test_started_at_cannot_follow_completed_at(self) -> None:
        attempt = completed_attempt(self.run)
        attempt["started_at"] = "2026-09-18T16:22:00Z"
        attempt["attempt_digest"] = canonical_attempt_digest(attempt)
        self.assert_error(validate(attempt), "must not be after")

    def test_exit_code_bool_is_rejected(self) -> None:
        attempt = completed_attempt(self.run)
        attempt["exit_code"] = False
        attempt["attempt_digest"] = canonical_attempt_digest(attempt)
        self.assert_error(validate(attempt), "exit_code must be an integer")

    def test_outcome_must_match_exit_code(self) -> None:
        attempt = completed_attempt(self.run, exit_code=3)
        attempt["outcome"] = "succeeded"
        attempt["attempt_digest"] = canonical_attempt_digest(attempt)
        self.assert_error(validate(attempt), "outcome must be failed")

    def test_success_requires_raw_output(self) -> None:
        attempt = completed_attempt(self.run)
        attempt["raw_evidence"] = [
            item for item in attempt["raw_evidence"] if item["kind"] != "raw-output"
        ]
        attempt["attempt_digest"] = canonical_attempt_digest(attempt)
        self.assert_error(validate(attempt), "requires raw_evidence kind=raw-output")

    def test_failure_does_not_require_raw_output(self) -> None:
        attempt = completed_attempt(self.run, exit_code=9)
        self.assertFalse(any(item["kind"] == "raw-output" for item in attempt["raw_evidence"]))
        self.assertEqual(validate(attempt), [])

    def test_runner_and_environment_evidence_are_always_required(self) -> None:
        for missing_kind in ("runner-log", "environment-capture"):
            with self.subTest(missing_kind=missing_kind):
                attempt = completed_attempt(self.run)
                attempt["raw_evidence"] = [
                    item for item in attempt["raw_evidence"] if item["kind"] != missing_kind
                ]
                attempt["attempt_digest"] = canonical_attempt_digest(attempt)
                self.assert_error(validate(attempt), "missing required raw evidence kinds")

    def test_raw_evidence_digest_is_required(self) -> None:
        attempt = completed_attempt(self.run)
        attempt["raw_evidence"][0]["digest"] = ""
        attempt["attempt_digest"] = canonical_attempt_digest(attempt)
        self.assert_error(validate(attempt), "must be lowercase SHA-256 hex")

    def test_raw_evidence_kind_must_be_unique(self) -> None:
        attempt = completed_attempt(self.run)
        duplicate = copy.deepcopy(attempt["raw_evidence"][0])
        duplicate["ref"] = "evidence:fixture:runner-log-2"
        attempt["raw_evidence"].append(duplicate)
        attempt["attempt_digest"] = canonical_attempt_digest(attempt)
        self.assert_error(validate(attempt), "kind must be unique")

    def test_post_completion_mutation_is_detected(self) -> None:
        attempt = completed_attempt(self.run)
        attempt["executor"]["ref"] = "executor:mutated"
        self.assert_error(validate(attempt), "attempt_digest does not match canonical content")

    def test_attempt_cannot_add_metric_winner_or_decision_fields(self) -> None:
        for key in ("metrics", "winner", "b5_decision", "production_default"):
            with self.subTest(key=key):
                attempt = copy.deepcopy(self.current)
                attempt[key] = [] if key == "metrics" else "forbidden"
                self.assert_error(validate_attempt_structure(attempt), "top-level keys mismatch")


if __name__ == "__main__":
    unittest.main()
