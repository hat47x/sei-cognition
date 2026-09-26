#!/usr/bin/env python3
"""Apply the preregistered Papaya numeric-parity policy to a managed report."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

POLICY_SCHEMA = "sei.local-typed-comparator-numeric-parity-policy/v1"
REPORT_SCHEMA = "sei.local-typed-comparator-cross-provider-numeric-report/v1"
DECISION_SCHEMA = "sei.local-typed-comparator-numeric-parity-decision/v1"
EXPECTED_CASE_IDS = (
    "choice-route-a",
    "choice-route-b",
    "score-urgency",
    "noul-review",
)
CHOICE11_CASE_ID = "choice-12-clamp-path"


class ParityDecisionError(ValueError):
    pass


def _object(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ParityDecisionError(f"{field} must be an object")
    return value


def _array(value: Any, field: str) -> list[Any]:
    if not isinstance(value, list):
        raise ParityDecisionError(f"{field} must be an array")
    return value


def _finite(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ParityDecisionError(f"{field} must be numeric")
    result = float(value)
    if not math.isfinite(result):
        raise ParityDecisionError(f"{field} must be finite")
    return result


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _load(path: Path, label: str) -> tuple[dict[str, Any], bytes]:
    try:
        raw = path.read_bytes()
        value = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ParityDecisionError(f"cannot read {label}: {path}") from exc
    if not isinstance(value, dict):
        raise ParityDecisionError(f"{label} root must be an object")
    return value, raw


def _validate_policy(policy: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    if policy.get("schema") != POLICY_SCHEMA:
        raise ParityDecisionError("policy schema drift")
    if policy.get("preregistered_date") != "2026-09-26":
        raise ParityDecisionError("policy preregistration date drift")
    if policy.get("comparator_report_schema") != REPORT_SCHEMA:
        raise ParityDecisionError("policy comparator schema drift")

    surface = _object(policy.get("surface"), "policy.surface")
    if tuple(surface.get("frozen_case_ids", ())) != EXPECTED_CASE_IDS:
        raise ParityDecisionError("policy frozen-case identity/order drift")
    if surface.get("choice11_diagnostic_case_id") != CHOICE11_CASE_ID:
        raise ParityDecisionError("policy choice11 case drift")

    thresholds = _object(policy.get("thresholds"), "policy.thresholds")
    frozen = _object(thresholds.get("frozen_cases"), "policy.thresholds.frozen_cases")
    diag = _object(
        thresholds.get("choice11_diagnostic"),
        "policy.thresholds.choice11_diagnostic",
    )
    expected_frozen = {
        "probability_max_abs_delta_max": 0.025,
        "confidence_abs_delta_max": 0.015,
        "score_abs_delta_max": 0.04,
        "noul_abs_delta_max": 0.025,
        "require_choice_selected_equal": True,
        "require_noul_threshold_0_5_equal": True,
        "require_score_probability_argmax_equal": True,
    }
    expected_diag = {
        "probability_max_abs_delta_max": 0.03,
        "confidence_abs_delta_max": 0.02,
        "require_choice_selected_equal": True,
    }
    if frozen != expected_frozen:
        raise ParityDecisionError("frozen threshold policy drift")
    if diag != expected_diag:
        raise ParityDecisionError("choice11 threshold policy drift")

    scope = _object(policy.get("scope"), "policy.scope")
    if scope.get("threshold_preregistered_before_managed_live_results") is not True:
        raise ParityDecisionError("policy preregistration scope drift")
    for field in (
        "task_quality",
        "calibration_validity",
        "cross_runtime_performance_comparison",
        "jev_provider_identity_equivalence",
        "reference_provider_promotion",
        "shipping_decision",
    ):
        if scope.get(field) is not False:
            raise ParityDecisionError(f"policy must keep {field}=false")
    return frozen, diag


def _validate_report(report: dict[str, Any]) -> None:
    if report.get("schema") != REPORT_SCHEMA:
        raise ParityDecisionError("numeric report schema drift")
    scope = _object(report.get("scope"), "report.scope")
    if scope.get("complete_managed_capture_inputs_required") is not True:
        raise ParityDecisionError("report managed-capture scope drift")
    if scope.get("numeric_parity_threshold_defined") is not False:
        raise ParityDecisionError("raw comparator report must not contain a threshold")
    if scope.get("numeric_parity_decision") is not False:
        raise ParityDecisionError("raw comparator report must not contain a parity decision")
    for field in (
        "task_quality",
        "calibration_validity",
        "cross_runtime_performance_comparison",
        "jev_provider_identity_equivalence",
        "reference_provider_promotion",
    ):
        if scope.get(field) is not False:
            raise ParityDecisionError(f"report overclaims {field}")


def _check_question(
    case_id: str,
    row: dict[str, Any],
    thresholds: dict[str, Any],
    failures: list[dict[str, Any]],
) -> None:
    qid = row.get("question_id")
    qtype = row.get("type")
    if not isinstance(qid, str) or qtype not in ("choice", "score", "noul"):
        raise ParityDecisionError(f"{case_id}: invalid question row")

    def fail(metric: str, observed: Any, limit: Any) -> None:
        failures.append(
            {
                "case_id": case_id,
                "question_id": qid,
                "type": qtype,
                "metric": metric,
                "observed": observed,
                "limit": limit,
            }
        )

    if qtype in ("choice", "score"):
        probs = _object(row.get("probabilities"), f"{case_id}.{qid}.probabilities")
        pmax = _finite(probs.get("max_abs_delta"), f"{case_id}.{qid}.max_abs_delta")
        limit = float(thresholds["probability_max_abs_delta_max"])
        if pmax > limit:
            fail("probability_max_abs_delta", pmax, limit)
        conf = _finite(
            row.get("confidence_abs_delta"),
            f"{case_id}.{qid}.confidence_abs_delta",
        )
        conf_limit = float(thresholds["confidence_abs_delta_max"])
        if conf > conf_limit:
            fail("confidence_abs_delta", conf, conf_limit)

    if qtype == "choice":
        if thresholds.get("require_choice_selected_equal") is True and row.get(
            "choice_selected_equal"
        ) is not True:
            fail("choice_selected_equal", row.get("choice_selected_equal"), True)
    elif qtype == "score":
        if thresholds.get("require_score_probability_argmax_equal") is True and row.get(
            "score_probability_argmax_equal"
        ) is not True:
            fail(
                "score_probability_argmax_equal",
                row.get("score_probability_argmax_equal"),
                True,
            )
        score_delta = _finite(
            row.get("score_abs_delta"), f"{case_id}.{qid}.score_abs_delta"
        )
        score_limit = float(thresholds["score_abs_delta_max"])
        if score_delta > score_limit:
            fail("score_abs_delta", score_delta, score_limit)
    else:
        if thresholds.get("require_noul_threshold_0_5_equal") is True and row.get(
            "noul_threshold_0_5_equal"
        ) is not True:
            fail(
                "noul_threshold_0_5_equal",
                row.get("noul_threshold_0_5_equal"),
                True,
            )
        noul_delta = _finite(
            row.get("noul_abs_delta"), f"{case_id}.{qid}.noul_abs_delta"
        )
        noul_limit = float(thresholds["noul_abs_delta_max"])
        if noul_delta > noul_limit:
            fail("noul_abs_delta", noul_delta, noul_limit)


def evaluate(
    policy: dict[str, Any],
    report: dict[str, Any],
    *,
    policy_sha256: str | None = None,
    report_sha256: str | None = None,
) -> dict[str, Any]:
    frozen_thresholds, diag_thresholds = _validate_policy(policy)
    _validate_report(report)

    cases = _array(report.get("cases"), "report.cases")
    if tuple(
        case.get("case_id") for case in cases if isinstance(case, dict)
    ) != EXPECTED_CASE_IDS:
        raise ParityDecisionError("report frozen-case identity/order drift")

    failures: list[dict[str, Any]] = []
    for case in cases:
        case = _object(case, "report.case")
        cid = case["case_id"]
        for row in _array(case.get("questions"), f"{cid}.questions"):
            _check_question(
                cid,
                _object(row, f"{cid}.question"),
                frozen_thresholds,
                failures,
            )

    diagnostic = _object(report.get("choice11_diagnostic"), "report.choice11_diagnostic")
    if diagnostic.get("case_id") != CHOICE11_CASE_ID:
        raise ParityDecisionError("report choice11 case drift")
    diag_questions = _array(
        diagnostic.get("questions"), "report.choice11_diagnostic.questions"
    )
    if len(diag_questions) != 1:
        raise ParityDecisionError("choice11 diagnostic must contain exactly one question")
    _check_question(
        CHOICE11_CASE_ID,
        _object(diag_questions[0], "report.choice11_diagnostic.question"),
        diag_thresholds,
        failures,
    )

    passed = not failures
    return {
        "schema": DECISION_SCHEMA,
        "policy": {
            "schema": POLICY_SCHEMA,
            "sha256": policy_sha256,
            "preregistered_date": policy["preregistered_date"],
        },
        "numeric_report": {
            "schema": REPORT_SCHEMA,
            "sha256": report_sha256,
        },
        "decision": "pass" if passed else "fail",
        "failures": failures,
        "scope": {
            "bounded_numeric_parity_on_preregistered_surface": passed,
            "task_quality": False,
            "calibration_validity": False,
            "cross_runtime_performance_comparison": False,
            "jev_provider_identity_equivalence": False,
            "reference_provider_promotion": False,
            "shipping_decision": False,
        },
    }


def main(argv: list[str] | None = None) -> int:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser()
    parser.add_argument("numeric_report", type=Path)
    parser.add_argument(
        "--policy",
        type=Path,
        default=here / "papaya_numeric_parity_policy.v1.json",
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)

    try:
        if args.output.exists():
            raise ParityDecisionError(f"output already exists: {args.output}")
        policy, policy_raw = _load(args.policy, "policy")
        report, report_raw = _load(args.numeric_report, "numeric report")
        decision = evaluate(
            policy,
            report,
            policy_sha256=_sha256(policy_raw),
            report_sha256=_sha256(report_raw),
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(decision, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(
        json.dumps(
            {
                "status": "complete",
                "decision": decision["decision"],
                "failure_count": len(decision["failures"]),
                "output": str(args.output),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
