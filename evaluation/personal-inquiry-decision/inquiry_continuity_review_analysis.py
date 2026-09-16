#!/usr/bin/env python3
"""Validate and compare ISSUE-000078 Inquiry Continuity human reviews.

Evaluation-only: this module never mutates canonical meaning, computes an
overall score/winner, or upgrades synthetic review to Product Value evidence.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from inquiry_continuity_packet import (
    INQUIRY_MANIFEST_SCHEMA,
    load_manifest_fixtures,
    validate_matched_set,
)
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
READER_CONTEXT_VALUES = {"original", "handoff", "not-observed"}
FINDING_FIELDS = (
    "original_concern_retention",
    "observation_hypothesis_unknown_separation",
    "unresolved_preservation",
    "temporal_integrity",
    "false_continuity_avoided",
    "first_useful_action",
)


class InquiryReviewError(ValueError):
    pass


def _answers(response: dict[str, Any], questions: Any, label: str) -> None:
    values = response.get("answers")
    if not isinstance(questions, list) or not questions:
        raise InquiryReviewError(f"{label} questions must be a non-empty list")
    if not isinstance(values, list) or len(values) != len(questions):
        raise InquiryReviewError(
            f"{label} requires exactly one answer per question "
            f"({len(questions)} expected)"
        )
    if not all(isinstance(value, str) and value.strip() for value in values):
        raise InquiryReviewError(f"{label} answers must be non-empty strings")


def _count(value: Any, field: str) -> None:
    if value == "not-observed":
        return
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise InquiryReviewError(
            f"{field} must be a non-negative integer or 'not-observed'"
        )


def _number(value: Any, field: str) -> None:
    if value == "not-observed":
        return
    if (
        not isinstance(value, (int, float))
        or isinstance(value, bool)
        or value < 0
    ):
        raise InquiryReviewError(
            f"{field} must be a non-negative number or 'not-observed'"
        )


def _phase1(response: dict[str, Any], fixture: dict[str, Any]) -> None:
    _answers(
        response,
        fixture["human_review_template"]["before_post_interruption_evidence"],
        "phase1",
    )
    obs = response.get("operator_observation")
    required = {
        "time_to_orientation_seconds",
        "source_reopen_count",
        "attention_load",
        "first_useful_action_reached",
        "reader_context",
    }
    if not isinstance(obs, dict) or not required <= set(obs):
        raise InquiryReviewError("phase1 operator_observation is incomplete")
    _number(obs["time_to_orientation_seconds"], "time_to_orientation_seconds")
    _count(obs["source_reopen_count"], "source_reopen_count")
    if obs["attention_load"] not in BURDEN_VALUES:
        raise InquiryReviewError("attention_load has invalid value")
    if obs["first_useful_action_reached"] not in {True, False, "not-observed"}:
        raise InquiryReviewError(
            "first_useful_action_reached must be boolean or 'not-observed'"
        )
    if obs["reader_context"] not in READER_CONTEXT_VALUES:
        raise InquiryReviewError("reader_context has invalid value")


def _post(response: dict[str, Any], fixture: dict[str, Any]) -> None:
    _answers(
        response,
        fixture["human_review_template"]["after_post_interruption_evidence"],
        "post",
    )


def _audit(response: dict[str, Any]) -> None:
    findings = response.get("findings")
    if not isinstance(findings, dict) or set(findings) != set(FINDING_FIELDS):
        raise InquiryReviewError(
            "audit findings must contain the Inquiry finding fields exactly"
        )
    if any(value not in FINDING_VALUES for value in findings.values()):
        raise InquiryReviewError("audit findings must be pass/fail/not-observed")
    obs = response.get("operator_observation")
    required = {
        "historical_misattribution_count",
        "role_confusion_count",
        "unresolved_omission_count",
        "correction_burden",
    }
    if not isinstance(obs, dict) or not required <= set(obs):
        raise InquiryReviewError("audit operator_observation is incomplete")
    for field in (
        "historical_misattribution_count",
        "role_confusion_count",
        "unresolved_omission_count",
    ):
        _count(obs[field], field)
    if obs["correction_burden"] not in BURDEN_VALUES:
        raise InquiryReviewError("correction_burden has invalid value")
    if not isinstance(response.get("notes", ""), str):
        raise InquiryReviewError("audit notes must be a string")


def validate_inquiry_response(
    stage: str,
    response: Any,
    fixture: dict[str, Any],
) -> None:
    if stage not in REVIEW_STAGES:
        raise InquiryReviewError(f"invalid stage: {stage}")
    if not isinstance(response, dict):
        raise InquiryReviewError(f"{stage} response must be an object")
    {"phase1": _phase1, "post": _post}.get(stage, lambda r, f: _audit(r))(
        response, fixture
    )


def validate_inquiry_session(
    session: dict[str, Any],
    manifest: dict[str, Any],
    fixtures_by_id: dict[str, dict[str, Any]],
    *,
    require_complete: bool = False,
) -> None:
    if manifest.get("schema") != INQUIRY_MANIFEST_SCHEMA:
        raise InquiryReviewError("manifest is not an Inquiry Continuity matched set")
    try:
        validate_matched_set(manifest, fixtures_by_id)
        validate_session(session, manifest, fixtures_by_id)
    except (ReviewSessionError, ValueError) as exc:
        raise InquiryReviewError(str(exc)) from exc
    for assignment in session["assignments"]:
        fid = assignment["fixture_id"]
        if fid not in fixtures_by_id:
            raise InquiryReviewError(f"unknown Inquiry fixture: {fid}")
        for stage in REVIEW_STAGES:
            record = assignment["records"][stage]
            if record is None:
                continue
            try:
                validate_inquiry_response(
                    stage, record["response"], fixtures_by_id[fid]
                )
            except InquiryReviewError as exc:
                raise InquiryReviewError(f"{fid}/{stage}: {exc}") from exc
    if require_complete and current_stage(session) != COMPLETE:
        raise InquiryReviewError("Inquiry Continuity review session is not complete")


def response_template(stage: str, fixture: dict[str, Any]) -> dict[str, Any]:
    """Return an incomplete template; empty answers prevent fabricated evidence."""
    if stage == "phase1":
        questions = fixture["human_review_template"][
            "before_post_interruption_evidence"
        ]
        return {
            "answers": ["" for _ in questions],
            "operator_observation": {
                "time_to_orientation_seconds": "not-observed",
                "source_reopen_count": "not-observed",
                "attention_load": "not-observed",
                "first_useful_action_reached": "not-observed",
                "reader_context": "not-observed",
            },
        }
    if stage == "post":
        questions = fixture["human_review_template"][
            "after_post_interruption_evidence"
        ]
        return {"answers": ["" for _ in questions]}
    if stage == "audit":
        return {
            "findings": {field: "not-observed" for field in FINDING_FIELDS},
            "operator_observation": {
                "historical_misattribution_count": "not-observed",
                "role_confusion_count": "not-observed",
                "unresolved_omission_count": "not-observed",
                "correction_burden": "not-observed",
            },
            "notes": "",
        }
    raise InquiryReviewError(f"invalid stage: {stage}")


def _summary() -> dict[str, Any]:
    return {
        "audited_attempts": 0,
        "fixture_ids": [],
        "reader_context_counts": {
            value: 0 for value in sorted(READER_CONTEXT_VALUES)
        },
        "finding_counts": {
            field: {value: 0 for value in sorted(FINDING_VALUES)}
            for field in FINDING_FIELDS
        },
        "time_to_orientation_seconds": [],
        "source_reopen_count": 0,
        "source_reopen_observed_attempts": 0,
        "attention_load_counts": {
            value: 0 for value in sorted(BURDEN_VALUES)
        },
        "first_useful_action_reached_counts": {
            "yes": 0, "no": 0, "not-observed": 0
        },
        "historical_misattribution_count": 0,
        "historical_misattribution_observed_attempts": 0,
        "role_confusion_count": 0,
        "role_confusion_observed_attempts": 0,
        "unresolved_omission_count": 0,
        "unresolved_omission_observed_attempts": 0,
        "correction_burden_counts": {
            value: 0 for value in sorted(BURDEN_VALUES)
        },
    }


def _add(group: dict[str, Any], field: str, observed: str, value: Any) -> None:
    if value != "not-observed":
        group[field] += value
        group[observed] += 1


def comparison_projection(
    sessions: list[dict[str, Any]],
    manifest: dict[str, Any],
    fixtures_by_id: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    if not sessions:
        raise InquiryReviewError("at least one completed session is required")
    session_ids = [session.get("session_id") for session in sessions]
    if any(not isinstance(value, str) or not value for value in session_ids):
        raise InquiryReviewError("every session requires a non-empty session_id")
    if len(session_ids) != len(set(session_ids)):
        raise InquiryReviewError("duplicate session_id would double-count observations")

    expected = {
        (fid, condition)
        for fid in fixtures_by_id
        for condition in manifest["condition_codes"]
    }
    observed: set[tuple[str, str]] = set()
    by_condition: dict[str, dict[str, Any]] = {}
    rotations = []

    for session in sessions:
        validate_inquiry_session(
            session, manifest, fixtures_by_id, require_complete=True
        )
        rotations.append(session["rotation"])
        for assignment in session["assignments"]:
            fid, condition = assignment["fixture_id"], assignment["condition"]
            observed.add((fid, condition))
            group = by_condition.setdefault(condition, _summary())
            group["audited_attempts"] += 1
            group["fixture_ids"].append(fid)

            phase = assignment["records"]["phase1"]["response"][
                "operator_observation"
            ]
            group["reader_context_counts"][phase["reader_context"]] += 1
            if phase["time_to_orientation_seconds"] != "not-observed":
                group["time_to_orientation_seconds"].append(
                    phase["time_to_orientation_seconds"]
                )
            _add(
                group, "source_reopen_count",
                "source_reopen_observed_attempts", phase["source_reopen_count"],
            )
            group["attention_load_counts"][phase["attention_load"]] += 1
            useful = phase["first_useful_action_reached"]
            useful = (
                "not-observed" if useful == "not-observed"
                else ("yes" if useful else "no")
            )
            group["first_useful_action_reached_counts"][useful] += 1

            audit = assignment["records"]["audit"]["response"]
            for field in FINDING_FIELDS:
                group["finding_counts"][field][audit["findings"][field]] += 1
            audit_obs = audit["operator_observation"]
            observed_fields = {
                "historical_misattribution_count":
                    "historical_misattribution_observed_attempts",
                "role_confusion_count":
                    "role_confusion_observed_attempts",
                "unresolved_omission_count":
                    "unresolved_omission_observed_attempts",
            }
            for field, observed_field in observed_fields.items():
                _add(group, field, observed_field, audit_obs[field])
            group["correction_burden_counts"][
                audit_obs["correction_burden"]
            ] += 1

    missing = sorted(expected - observed)
    handoff = sum(
        value["reader_context_counts"]["handoff"]
        for value in by_condition.values()
    )
    return {
        "projection": "sei.inquiry-continuity-human-review-comparison/v0",
        "status": "evaluation-only",
        "set_id": manifest["set_id"],
        "session_ids": session_ids,
        "rotations": rotations,
        "completed_sessions": len(sessions),
        "counterbalance_coverage": {
            "observed_pairs": len(observed),
            "expected_pairs": len(expected),
            "complete": not missing,
            "missing_pairs": [
                {"fixture_id": fid, "condition": condition}
                for fid, condition in missing
            ],
        },
        "handoff_observation": {
            "synthetic_handoff_attempts": handoff,
            "observed": handoff > 0,
        },
        "by_condition": by_condition,
        "evidence_boundaries": {
            "synthetic_human_review": "operator-provenance-required",
            "actual_long_gap_resumption": "not-established-by-this-artifact",
            "actual_team_handoff": "not-established-by-synthetic-handoff",
            "capture_burden": "not-measured-by-prepared-synthetic-fixtures",
            "product_value": "not-established-by-this-artifact",
            "stable_requirement_change": "not-authorized-by-this-artifact",
        },
        "interpretation_stoplines": [
            "no overall score, ranking, or winner is computed",
            "historical correctness and role separation are not traded away for speed",
            "a single rotation remains scenario-confounded",
            "full R1/R2/R3 coverage is not generalizable user evidence",
            "B0/B1 matching or outperforming SEI supports reducing SEI-specific structure",
            "synthetic handoff does not substitute for actual team handoff",
            "synthetic review does not substitute for actual long-gap resumption",
            "prepared fixtures do not establish capture/review overhead in real work",
        ],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Analyze ISSUE-000078 Inquiry Continuity matched reviews"
    )
    parser.add_argument(
        "--manifest",
        default=(
            "evaluation/personal-inquiry-decision/"
            "inquiry_continuity_counterfactual_matched_set_v1.json"
        ),
    )
    parser.add_argument("--repo-root", default=".")
    sub = parser.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("validate-session")
    validate.add_argument("session")
    validate.add_argument("--require-complete", action="store_true")
    compare = sub.add_parser("compare")
    compare.add_argument("sessions", nargs="+")
    template = sub.add_parser("response-template")
    template.add_argument("--fixture-id", required=True)
    template.add_argument("--stage", choices=REVIEW_STAGES, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    manifest, fixtures = load_manifest_fixtures(
        Path(args.manifest), Path(args.repo_root)
    )
    if args.command == "response-template":
        if args.fixture_id not in fixtures:
            raise InquiryReviewError(
                f"unknown Inquiry fixture: {args.fixture_id}"
            )
        result = response_template(args.stage, fixtures[args.fixture_id])
    elif args.command == "validate-session":
        session = load_session(args.session)
        validate_inquiry_session(
            session, manifest, fixtures,
            require_complete=args.require_complete,
        )
        result = {
            "valid": True,
            "session_id": session["session_id"],
            "stage": current_stage(session),
            "evidence": (
                "evaluation observation only; actual long-gap/Product Value "
                "not established"
            ),
        }
    else:
        result = comparison_projection(
            [load_session(path) for path in args.sessions],
            manifest,
            fixtures,
        )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
