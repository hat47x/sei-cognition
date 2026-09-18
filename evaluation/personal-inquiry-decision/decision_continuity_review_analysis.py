#!/usr/bin/env python3
"""Decision-specific validation and comparison for ISSUE-000073 matched reviews.

The generic matched_review_session.py owns source freezing and stage gating.
This module adds only Decision Continuity response semantics and non-scored
comparison. It never mutates canonical SEI meaning and does not certify Product
Value or H1 actual-resume evidence.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from decision_continuity_preflight import (
    load_decision_set,
    validate_decision_matched_set,
)
from inquiry_continuity_packet import DECISION_MANIFEST_SCHEMA
from matched_review_session import (
    COMPLETE,
    REVIEW_STAGES,
    ReviewSessionError,
    current_stage,
    load_session,
    validate_session,
)

FINDING_VALUES = {"pass", "fail", "not-observed"}
BURDEN_VALUES = {"low", "medium", "high", "not-observed"}
CONTINUED_USE_VALUES = {"yes", "no", "not-observed"}

FINDING_FIELDS = (
    "current_question_correct",
    "decision_correct",
    "recommendation_decision_integrity",
    "historical_basis_integrity",
    "unresolved_preservation",
    "post_decision_temporal_integrity",
)


class DecisionReviewError(ValueError):
    pass


def _require_keys(value: dict[str, Any], *keys: str) -> None:
    missing = [key for key in keys if key not in value]
    if missing:
        raise DecisionReviewError(f"missing required keys: {', '.join(missing)}")


def _validate_answers(
    response: dict[str, Any],
    questions: Any,
    label: str,
) -> None:
    if not isinstance(questions, list) or not questions:
        raise DecisionReviewError(f"{label} questions must be a non-empty list")
    answers = response.get("answers")
    if not isinstance(answers, list):
        raise DecisionReviewError(f"{label} answers must be a list")
    if len(answers) != len(questions):
        raise DecisionReviewError(
            f"{label} requires exactly one answer per question "
            f"({len(questions)} expected, {len(answers)} received)"
        )
    if not all(isinstance(answer, str) and answer.strip() for answer in answers):
        raise DecisionReviewError(f"{label} answers must be non-empty strings")


def _validate_nonnegative_int_or_unobserved(value: Any, field: str) -> None:
    if value == "not-observed":
        return
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise DecisionReviewError(
            f"{field} must be a non-negative integer or 'not-observed'"
        )


def _validate_nonnegative_number_or_unobserved(value: Any, field: str) -> None:
    if value == "not-observed":
        return
    if (
        not isinstance(value, (int, float))
        or isinstance(value, bool)
        or value < 0
    ):
        raise DecisionReviewError(
            f"{field} must be a non-negative number or 'not-observed'"
        )


def _validate_phase1_response(
    response: dict[str, Any],
    fixture: dict[str, Any],
) -> None:
    _validate_answers(
        response,
        fixture["human_review_template"]["before_post_decision_evidence"],
        "phase1",
    )
    observation = response.get("operator_observation")
    if not isinstance(observation, dict):
        raise DecisionReviewError("phase1 operator_observation must be an object")
    _require_keys(
        observation,
        "time_to_orientation_seconds",
        "source_reopen_count",
        "mental_effort_1_to_5",
    )
    _validate_nonnegative_number_or_unobserved(
        observation["time_to_orientation_seconds"],
        "time_to_orientation_seconds",
    )
    _validate_nonnegative_int_or_unobserved(
        observation["source_reopen_count"],
        "source_reopen_count",
    )
    effort = observation["mental_effort_1_to_5"]
    if effort != "not-observed" and (
        not isinstance(effort, int)
        or isinstance(effort, bool)
        or not 1 <= effort <= 5
    ):
        raise DecisionReviewError(
            "mental_effort_1_to_5 must be 1..5 or 'not-observed'"
        )


def _validate_post_response(
    response: dict[str, Any],
    fixture: dict[str, Any],
) -> None:
    _validate_answers(
        response,
        fixture["human_review_template"]["after_post_decision_evidence"],
        "post",
    )


def _validate_audit_response(response: dict[str, Any]) -> None:
    findings = response.get("findings")
    if not isinstance(findings, dict):
        raise DecisionReviewError("audit findings must be an object")
    for field in FINDING_FIELDS:
        if findings.get(field) not in FINDING_VALUES:
            raise DecisionReviewError(
                f"audit finding {field} must be pass/fail/not-observed"
            )

    observation = response.get("operator_observation")
    if not isinstance(observation, dict):
        raise DecisionReviewError("audit operator_observation must be an object")
    _require_keys(
        observation,
        "historical_misattribution_count",
        "recommendation_decision_confusion",
        "correction_burden",
    )
    _validate_nonnegative_int_or_unobserved(
        observation["historical_misattribution_count"],
        "historical_misattribution_count",
    )
    confusion = observation["recommendation_decision_confusion"]
    if confusion != "not-observed" and not isinstance(confusion, bool):
        raise DecisionReviewError(
            "recommendation_decision_confusion must be boolean or 'not-observed'"
        )
    if observation["correction_burden"] not in BURDEN_VALUES:
        raise DecisionReviewError("correction_burden has invalid value")

    continued = response.get("continued_use", "not-observed")
    if continued not in CONTINUED_USE_VALUES:
        raise DecisionReviewError("continued_use has invalid value")
    reason = response.get("continued_use_reason", "")
    notes = response.get("notes", "")
    if not isinstance(reason, str) or not isinstance(notes, str):
        raise DecisionReviewError(
            "continued_use_reason and notes must be strings"
        )


def validate_decision_response(
    stage: str,
    response: Any,
    fixture: dict[str, Any],
) -> None:
    if stage not in REVIEW_STAGES:
        raise DecisionReviewError(f"invalid stage: {stage}")
    if not isinstance(response, dict):
        raise DecisionReviewError(f"{stage} response must be an object")
    if stage == "phase1":
        _validate_phase1_response(response, fixture)
    elif stage == "post":
        _validate_post_response(response, fixture)
    else:
        _validate_audit_response(response)


def validate_decision_session(
    session: dict[str, Any],
    manifest: dict[str, Any],
    fixtures_by_id: dict[str, dict[str, Any]],
    *,
    require_complete: bool = False,
) -> None:
    if manifest.get("schema") != DECISION_MANIFEST_SCHEMA:
        raise DecisionReviewError("manifest is not a Decision Continuity matched set")
    try:
        validate_decision_matched_set(manifest, fixtures_by_id)
        validate_session(session, manifest, fixtures_by_id)
    except (ReviewSessionError, ValueError) as exc:
        raise DecisionReviewError(str(exc)) from exc

    for assignment in session["assignments"]:
        fixture_id = assignment["fixture_id"]
        fixture = fixtures_by_id.get(fixture_id)
        if fixture is None:
            raise DecisionReviewError(f"unknown Decision fixture: {fixture_id}")
        for stage in REVIEW_STAGES:
            record = assignment["records"][stage]
            if record is None:
                continue
            try:
                validate_decision_response(stage, record["response"], fixture)
            except DecisionReviewError as exc:
                raise DecisionReviewError(
                    f"{fixture_id}/{stage}: {exc}"
                ) from exc

    if require_complete and current_stage(session) != COMPLETE:
        raise DecisionReviewError("Decision Continuity review session is not complete")



def response_template(stage: str, fixture: dict[str, Any]) -> dict[str, Any]:
    """Return an incomplete Decision review template; empty answers are not Evidence."""
    if stage == "phase1":
        questions = fixture["human_review_template"]["before_post_decision_evidence"]
        return {
            "answers": ["" for _ in questions],
            "operator_observation": {
                "time_to_orientation_seconds": "not-observed",
                "source_reopen_count": "not-observed",
                "mental_effort_1_to_5": "not-observed",
            },
        }
    if stage == "post":
        questions = fixture["human_review_template"]["after_post_decision_evidence"]
        return {"answers": ["" for _ in questions]}
    if stage == "audit":
        return {
            "findings": {field: "not-observed" for field in FINDING_FIELDS},
            "operator_observation": {
                "historical_misattribution_count": "not-observed",
                "recommendation_decision_confusion": "not-observed",
                "correction_burden": "not-observed",
            },
            "continued_use": "not-observed",
            "continued_use_reason": "",
            "notes": "",
        }
    raise DecisionReviewError(f"invalid stage: {stage}")


def _condition_summary() -> dict[str, Any]:
    return {
        "audited_attempts": 0,
        "fixture_ids": [],
        "finding_counts": {
            field: {value: 0 for value in sorted(FINDING_VALUES)}
            for field in FINDING_FIELDS
        },
        "time_to_orientation_seconds": [],
        "source_reopen_count": 0,
        "source_reopen_observed_attempts": 0,
        "mental_effort_1_to_5": [],
        "historical_misattribution_count": 0,
        "historical_misattribution_observed_attempts": 0,
        "recommendation_decision_confusion_count": 0,
        "recommendation_decision_confusion_observed_attempts": 0,
        "correction_burden_counts": {
            value: 0 for value in sorted(BURDEN_VALUES)
        },
        "continued_use_counts": {
            value: 0 for value in sorted(CONTINUED_USE_VALUES)
        },
    }


def comparison_projection(
    sessions: list[dict[str, Any]],
    manifest: dict[str, Any],
    fixtures_by_id: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    if not sessions:
        raise DecisionReviewError("at least one completed session is required")

    expected_pairs = {
        (fixture_id, condition)
        for fixture_id in fixtures_by_id
        for condition in manifest["condition_codes"]
    }
    observed_pairs: set[tuple[str, str]] = set()
    by_condition: dict[str, dict[str, Any]] = {}

    session_ids: list[str] = []
    rotations: list[str] = []
    for session in sessions:
        validate_decision_session(
            session,
            manifest,
            fixtures_by_id,
            require_complete=True,
        )
        session_ids.append(session["session_id"])
        rotations.append(session["rotation"])

        for assignment in session["assignments"]:
            fixture_id = assignment["fixture_id"]
            condition = assignment["condition"]
            observed_pairs.add((fixture_id, condition))
            group = by_condition.setdefault(condition, _condition_summary())
            group["audited_attempts"] += 1
            group["fixture_ids"].append(fixture_id)

            phase1 = assignment["records"]["phase1"]["response"]
            phase_obs = phase1["operator_observation"]
            time_value = phase_obs["time_to_orientation_seconds"]
            if time_value != "not-observed":
                group["time_to_orientation_seconds"].append(time_value)
            reopen = phase_obs["source_reopen_count"]
            if reopen != "not-observed":
                group["source_reopen_count"] += reopen
                group["source_reopen_observed_attempts"] += 1
            effort = phase_obs["mental_effort_1_to_5"]
            if effort != "not-observed":
                group["mental_effort_1_to_5"].append(effort)

            audit = assignment["records"]["audit"]["response"]
            for field in FINDING_FIELDS:
                group["finding_counts"][field][audit["findings"][field]] += 1

            audit_obs = audit["operator_observation"]
            misattribution = audit_obs["historical_misattribution_count"]
            if misattribution != "not-observed":
                group["historical_misattribution_count"] += misattribution
                group["historical_misattribution_observed_attempts"] += 1
            confusion = audit_obs["recommendation_decision_confusion"]
            if confusion != "not-observed":
                group["recommendation_decision_confusion_observed_attempts"] += 1
                group["recommendation_decision_confusion_count"] += int(confusion)
            burden = audit_obs["correction_burden"]
            group["correction_burden_counts"][burden] += 1
            continued = audit.get("continued_use", "not-observed")
            group["continued_use_counts"][continued] += 1

    missing_pairs = sorted(expected_pairs - observed_pairs)
    return {
        "projection": "sei.decision-continuity-human-review-comparison/v0",
        "status": "evaluation-only",
        "set_id": manifest["set_id"],
        "session_ids": session_ids,
        "rotations": rotations,
        "completed_sessions": len(sessions),
        "counterbalance_coverage": {
            "observed_pairs": len(observed_pairs),
            "expected_pairs": len(expected_pairs),
            "complete": not missing_pairs,
            "missing_pairs": [
                {"fixture_id": fixture_id, "condition": condition}
                for fixture_id, condition in missing_pairs
            ],
        },
        "by_condition": by_condition,
        "evidence_boundaries": {
            "h1_actual_resume_usability": "not-established-by-this-artifact",
            "capture_burden": "not-measured-by-prepared-synthetic-fixtures",
            "product_value": "not-established-by-this-artifact",
            "human_authorship": "operator-provenance-required",
        },
        "interpretation_stoplines": [
            "no overall score or winner is computed",
            "faster orientation with worse historical accuracy is not Product Value improvement",
            "a single rotation is pilot observation and remains scenario-confounded",
            "full R1/R2/R3 coverage improves counterbalancing but is not generalizable user evidence",
            "synthetic matched review does not substitute for H1 actual-resume review",
            "prepared synthetic fixtures do not establish capture or review overhead in real work",
        ],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate/analyze ISSUE-000073 Decision Continuity matched reviews"
    )
    parser.add_argument(
        "--manifest",
        default=(
            "evaluation/personal-inquiry-decision/"
            "decision_continuity_counterfactual_matched_set_v1.json"
        ),
    )
    parser.add_argument("--repo-root", default=".")
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser("validate-session")
    validate.add_argument("session")
    validate.add_argument("--require-complete", action="store_true")

    compare = sub.add_parser("compare")
    compare.add_argument("sessions", nargs="+")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    manifest, fixtures = load_decision_set(
        Path(args.manifest),
        Path(args.repo_root),
    )

    if args.command == "validate-session":
        session = load_session(args.session)
        validate_decision_session(
            session,
            manifest,
            fixtures,
            require_complete=args.require_complete,
        )
        print(
            json.dumps(
                {
                    "valid": True,
                    "session_id": session["session_id"],
                    "stage": current_stage(session),
                    "evidence": (
                        "evaluation observation record only; "
                        "H1/Product Value not established"
                    ),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    sessions = [load_session(path) for path in args.sessions]
    print(
        json.dumps(
            comparison_projection(sessions, manifest, fixtures),
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())