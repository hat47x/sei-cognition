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
from validate_result import (  # noqa: E402
    canonical_result_digest,
    validate_completed_result,
    validate_result_structure,
)

RESULT_PATH = HERE / "result.json"
RUN_PATH = RUN_DIR / "evaluation_run.json"
PREREG_PATH = SACS_DIR / "cross_stage_benchmark_preregistration.json"


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def metric_role(name: str) -> str:
    roles = {
        "recall_at_k": "quality",
        "pairwise_ordering_accuracy": "quality",
        "false_activation_rate": "quality",
        "perturbation_stability": "robustness",
        "cross_profile_ordering_stability": "robustness",
        "oversized_residual_policy_stress": "robustness",
        "p50_latency": "resource",
        "p95_latency": "resource",
        "memory_footprint": "resource",
        "allocation_count": "resource",
        "observed_touched_dimensions": "diagnostic",
        "observed_winner_share": "diagnostic",
        "local_incremental_dimensions": "diagnostic",
        "residual_containment_behavior": "diagnostic",
    }
    return roles.get(name, "track-metric")


def completed_result(run: dict) -> dict:
    result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    result.update({
        "state": "completed",
        "result_id": "result:fixture:001",
        "generated_at": "2026-09-18T11:40:00Z",
        "track": run["track"],
        "variant": run["variant"],
        "capacity_profile": run["capacity_profile"],
        "stress_policy": run["stress_policy"],
        "observed_environment": copy.deepcopy(run["environment"]),
        "metrics": [
            {
                "name": name,
                "role": metric_role(name),
                "status": "measured",
                "value": 0.75,
                "unit": "ratio",
                "sample_count": 8,
                "unavailable_reason": "",
            }
            for name in run["requested_metrics"]
        ],
        "raw_evidence": [
            {
                "kind": "raw-output",
                "ref": "evidence:fixture:raw",
                "digest": sha("raw-output"),
            },
            {
                "kind": "environment-capture",
                "ref": "evidence:fixture:environment",
                "digest": sha("environment-capture"),
            },
        ],
        "results_generated": True,
    })
    result["run_binding"]["digest"] = run["run_digest"]
    result["execution"] = {
        "executor_ref": "executor:fixture:v1",
        "executor_commit": "b" * 40,
        "started_at": "2026-09-18T11:35:00Z",
        "completed_at": "2026-09-18T11:39:00Z",
        "exit_code": 0,
    }
    result["result_digest"] = canonical_result_digest(result)
    return result


def refresh_digest(result: dict) -> None:
    result["result_digest"] = canonical_result_digest(result)


class CrossStageResultTests(unittest.TestCase):
    def setUp(self) -> None:
        self.current_result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
        self.current_run = json.loads(RUN_PATH.read_text(encoding="utf-8"))
        self.current_prereg = json.loads(PREREG_PATH.read_text(encoding="utf-8"))
        self.current_freeze = load_directory(FREEZE_DIR)

        self.frozen = freeze_documents(
            synthetic_freeze_draft(),
            "2026-09-18T11:20:00Z",
        )
        self.prereg = frozen_prereg(self.frozen)
        self.prereg["evaluation_run"].update({
            "state": "authorized",
            "current_run_authorized": True,
        })
        self.run = authorized_run(
            self.frozen,
            metrics=["recall_at_k", "observed_winner_share"],
        )

    def assert_error(self, errors: list[str], fragment: str) -> None:
        self.assertTrue(
            any(fragment in error for error in errors),
            f"expected {fragment!r}; got {errors!r}",
        )

    def validate(self, result: dict, run: dict | None = None) -> list[str]:
        return validate_completed_result(
            result,
            run or self.run,
            self.prereg,
            self.frozen,
        )

    def test_current_draft_result_is_structurally_valid(self) -> None:
        self.assertEqual(validate_result_structure(self.current_result), [])

    def test_current_draft_run_and_freeze_cannot_support_completed_result(self) -> None:
        result = completed_result(self.run)
        errors = validate_completed_result(
            result,
            self.current_run,
            self.current_prereg,
            self.current_freeze,
        )
        self.assert_error(errors, "authorized run")
        self.assert_error(errors, "full unlock")

    def test_synthetic_completed_retrieval_result_is_valid(self) -> None:
        result = completed_result(self.run)
        self.assertEqual(self.validate(result), [])

    def test_retrieval_diagnostic_role_is_preserved(self) -> None:
        result = completed_result(self.run)
        roles = {item["name"]: item["role"] for item in result["metrics"]}
        self.assertEqual(roles["observed_winner_share"], "diagnostic")
        self.assertEqual(self.validate(result), [])

    def test_missing_requested_metric_is_rejected(self) -> None:
        result = completed_result(self.run)
        result["metrics"] = result["metrics"][:-1]
        refresh_digest(result)
        self.assert_error(self.validate(result), "requested_metrics exactly")

    def test_duplicate_metric_is_rejected(self) -> None:
        result = completed_result(self.run)
        result["metrics"].append(copy.deepcopy(result["metrics"][0]))
        refresh_digest(result)
        self.assert_error(self.validate(result), "metric names must be unique")

    def test_unknown_metric_is_rejected(self) -> None:
        result = completed_result(self.run)
        result["metrics"][0]["name"] = "magic_score"
        refresh_digest(result)
        errors = self.validate(result)
        self.assert_error(errors, "requested_metrics exactly")
        self.assert_error(errors, "not preregistered")

    def test_nonfinite_metric_is_rejected(self) -> None:
        for value in (float("nan"), float("inf"), float("-inf")):
            with self.subTest(value=value):
                result = completed_result(self.run)
                result["metrics"][0]["value"] = value
                refresh_digest(result)
                self.assert_error(self.validate(result), "finite numeric value")

    def test_unavailable_metric_requires_reason(self) -> None:
        result = completed_result(self.run)
        metric = result["metrics"][0]
        metric.update({
            "status": "unavailable",
            "value": None,
            "unit": "",
            "sample_count": 0,
            "unavailable_reason": "",
        })
        refresh_digest(result)
        self.assert_error(self.validate(result), "requires a non-empty reason")

    def test_unavailable_metric_is_explicit_not_zero(self) -> None:
        result = completed_result(self.run)
        metric = result["metrics"][0]
        metric.update({
            "status": "unavailable",
            "value": None,
            "unit": "",
            "sample_count": 0,
            "unavailable_reason": "runner-did-not-produce-metric",
        })
        refresh_digest(result)
        self.assertEqual(self.validate(result), [])

    def test_metric_role_spoofing_is_rejected(self) -> None:
        result = completed_result(self.run)
        result["metrics"][1]["role"] = "quality"
        refresh_digest(result)
        self.assert_error(self.validate(result), "metric role mismatch")

    def test_raw_evidence_digest_is_required(self) -> None:
        result = completed_result(self.run)
        result["raw_evidence"][0]["digest"] = ""
        refresh_digest(result)
        self.assert_error(self.validate(result), "must be lowercase SHA-256 hex")

    def test_raw_output_and_environment_capture_are_both_required(self) -> None:
        for missing_kind in ("raw-output", "environment-capture"):
            with self.subTest(missing_kind=missing_kind):
                result = completed_result(self.run)
                result["raw_evidence"] = [
                    item
                    for item in result["raw_evidence"]
                    if item["kind"] != missing_kind
                ]
                refresh_digest(result)
                self.assert_error(
                    self.validate(result),
                    f"requires raw_evidence kind={missing_kind}",
                )

    def test_run_digest_binding_is_exact(self) -> None:
        result = completed_result(self.run)
        result["run_binding"]["digest"] = "0" * 64
        refresh_digest(result)
        self.assert_error(self.validate(result), "does not match authorized run digest")

    def test_post_completion_mutation_is_detected(self) -> None:
        result = completed_result(self.run)
        result["metrics"][0]["value"] = 0.5
        self.assert_error(
            self.validate(result),
            "result_digest does not match canonical content",
        )

    def test_result_cannot_add_winner_or_decision_field(self) -> None:
        result = copy.deepcopy(self.current_result)
        result["winner"] = "B1-B2"
        self.assert_error(
            validate_result_structure(result),
            "top-level keys mismatch",
        )

    def test_observed_environment_must_match_authorized_run(self) -> None:
        result = completed_result(self.run)
        result["observed_environment"]["runtime"] = "go9.99"
        refresh_digest(result)
        self.assert_error(
            self.validate(result),
            "observed_environment must exactly match",
        )

    def test_nonzero_executor_exit_is_rejected(self) -> None:
        result = completed_result(self.run)
        result["execution"]["exit_code"] = 1
        refresh_digest(result)
        self.assert_error(self.validate(result), "execution.exit_code=0")

    def test_execution_time_order_is_checked(self) -> None:
        result = completed_result(self.run)
        result["execution"]["started_at"] = "2026-09-18T11:41:00Z"
        refresh_digest(result)
        self.assert_error(self.validate(result), "must not be after execution.completed_at")

    def test_generated_at_must_follow_completion(self) -> None:
        result = completed_result(self.run)
        result["generated_at"] = "2026-09-18T11:38:00Z"
        refresh_digest(result)
        self.assert_error(self.validate(result), "must not be after result.generated_at")

    def test_completed_result_requires_utc_second_timestamp(self) -> None:
        result = completed_result(self.run)
        result["generated_at"] = "2026-09-18T20:40:00+09:00"
        refresh_digest(result)
        self.assert_error(self.validate(result), "UTC second format")

    def test_familiarity_result_is_track_bound(self) -> None:
        run = authorized_run(
            self.frozen,
            track="familiarity",
            variant="SAC-B4",
            capacity_profile=None,
            metrics=["missed_change_rate"],
        )
        result = completed_result(run)
        self.assertEqual(
            validate_completed_result(result, run, self.prereg, self.frozen),
            [],
        )
        self.assertEqual(result["metrics"][0]["role"], "track-metric")

    def test_routing_result_is_track_bound(self) -> None:
        run = authorized_run(
            self.frozen,
            track="routing",
            variant="SEI-B7",
            capacity_profile=None,
            metrics=["regret_against_static_policy"],
        )
        result = completed_result(run)
        self.assertEqual(
            validate_completed_result(result, run, self.prereg, self.frozen),
            [],
        )

    def test_oversized_stress_result_preserves_stress_identity(self) -> None:
        run = authorized_run(
            self.frozen,
            capacity_profile="oversized-stress",
            stress_policy="cap128",
            metrics=["oversized_residual_policy_stress"],
        )
        result = completed_result(run)
        self.assertEqual(
            validate_completed_result(result, run, self.prereg, self.frozen),
            [],
        )
        self.assertEqual(result["stress_policy"], "cap128")


if __name__ == "__main__":
    unittest.main()
