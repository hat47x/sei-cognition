#!/usr/bin/env python3
"""Build the canonical stage-gated ISSUE-000078 E78.3 distortion packets.

The provisional AI summary and next-question suggestion are deliberately fallible
evaluation material. Source fixtures remain authoritative for historical
comparison; neither the stimulus nor a human correction mutates canonical Inquiry
meaning. This module is the single maintained E78.3 probe path.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

SCHEMA = "sei.inquiry-continuity-summary-distortion-probe/v0"
FIXTURE_SCHEMA = "sei.inquiry-continuity-comparison-fixture/v0"
PACKET_SCHEMA = "sei.inquiry-continuity-summary-distortion-packet/v0"
RESPONSE_SCHEMA = "sei.inquiry-continuity-summary-distortion-response/v0"
REQUIRED_KINDS = {
    "hypothesis_to_certainty",
    "alternate_hypothesis_omission",
    "temporal_backfill",
}
PRIOR_EXPOSURE_VALUES = {
    "none-declared",
    "known-material-exposure",
    "unknown",
}
RESPONSE_AUTHORSHIP_VALUES = {
    "human-direct",
    "human-transcribed",
}
BURDEN_VALUES = {"low", "medium", "high", "not-observed"}


class SummaryDistortionProbeError(ValueError):
    pass


def load_json(path: str | Path) -> dict[str, Any]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SummaryDistortionProbeError(f"cannot load JSON: {path}") from exc
    if not isinstance(value, dict):
        raise SummaryDistortionProbeError("JSON root must be an object")
    return value


def git_blob_sha1(raw: bytes) -> str:
    return hashlib.sha1(f"blob {len(raw)}\0".encode("ascii") + raw).hexdigest()


def _validate_string_list(value: Any, label: str) -> None:
    if (
        not isinstance(value, list)
        or not value
        or any(not isinstance(item, str) or not item.strip() for item in value)
    ):
        raise SummaryDistortionProbeError(
            f"{label} must be a non-empty list of non-empty strings"
        )


def _validate_questions(value: Any) -> None:
    if not isinstance(value, list) or len(value) < 5:
        raise SummaryDistortionProbeError("review questions are incomplete")
    ids: list[str] = []
    for question in value:
        if not isinstance(question, dict):
            raise SummaryDistortionProbeError("review question must be an object")
        qid = question.get("id")
        prompt = question.get("prompt")
        if not isinstance(qid, str) or not qid.strip():
            raise SummaryDistortionProbeError("review question id must be non-empty")
        if not isinstance(prompt, str) or not prompt.strip():
            raise SummaryDistortionProbeError("review question prompt must be non-empty")
        ids.append(qid)
    if len(ids) != len(set(ids)):
        raise SummaryDistortionProbeError("review question ids must be unique")


def validate_probe(probe: dict[str, Any]) -> None:
    if probe.get("schema") != SCHEMA:
        raise SummaryDistortionProbeError(f"schema must be {SCHEMA}")
    if (
        probe.get("status") != "evaluation-only"
        or probe.get("issue") != "ISSUE-000078"
    ):
        raise SummaryDistortionProbeError(
            "probe must remain evaluation-only for ISSUE-000078"
        )

    _validate_string_list(probe.get("presentation_rules"), "presentation_rules")
    _validate_string_list(
        probe.get("interpretation_stoplines"),
        "interpretation_stoplines",
    )

    stop = probe.get("semantic_stopline")
    expected_false = (
        "distorted_summary_is_canonical",
        "ai_summary_may_overwrite_source",
        "correction_may_mutate_historical_state",
        "overall_score_or_winner_allowed",
        "stable_requirement_change_authorized",
    )
    if not isinstance(stop, dict) or any(
        stop.get(key) is not False for key in expected_false
    ):
        raise SummaryDistortionProbeError("semantic stopline is incomplete")

    cases = probe.get("cases")
    if not isinstance(cases, list) or len(cases) != 3:
        raise SummaryDistortionProbeError(
            "exactly three distortion cases are required"
        )
    ids: list[str] = []
    for case in cases:
        if not isinstance(case, dict):
            raise SummaryDistortionProbeError("case must be an object")
        for key in (
            "fixture_id",
            "path",
            "blob_sha1",
            "distorted_summary",
            "distorted_next_question",
            "distortion_key",
        ):
            if not case.get(key):
                raise SummaryDistortionProbeError(f"case missing {key}")
        kinds = {
            item.get("kind")
            for item in case["distortion_key"]
            if isinstance(item, dict)
        }
        if not REQUIRED_KINDS.issubset(kinds):
            raise SummaryDistortionProbeError(
                f"{case['fixture_id']} must cover certainty, omission, and temporal backfill"
            )
        ids.append(case["fixture_id"])
    if len(ids) != len(set(ids)):
        raise SummaryDistortionProbeError("fixture ids must be unique")

    _validate_questions(probe.get("review_questions"))
    if not probe.get("audit_dimensions"):
        raise SummaryDistortionProbeError("audit dimensions are required")


def load_sources(
    probe: dict[str, Any],
    repo_root: str | Path,
) -> dict[str, dict[str, Any]]:
    validate_probe(probe)
    root = Path(repo_root)
    result: dict[str, dict[str, Any]] = {}
    for case in probe["cases"]:
        path = root / case["path"]
        try:
            raw = path.read_bytes()
        except OSError as exc:
            raise SummaryDistortionProbeError(
                f"cannot load source fixture: {path}"
            ) from exc
        if git_blob_sha1(raw) != case["blob_sha1"]:
            raise SummaryDistortionProbeError(
                f"source fixture changed after probe design: {case['fixture_id']}"
            )
        fixture = load_json(path)
        if (
            fixture.get("schema") != FIXTURE_SCHEMA
            or fixture.get("status") != "evaluation-only"
        ):
            raise SummaryDistortionProbeError(
                f"invalid source fixture: {case['fixture_id']}"
            )
        if fixture.get("fixture_id") != case["fixture_id"]:
            raise SummaryDistortionProbeError(
                f"fixture id mismatch: {case['fixture_id']}"
            )
        if fixture.get("scenario", {}).get("decision_present") is not False:
            raise SummaryDistortionProbeError(
                "E78.3 source fixture must remain Decisionless"
            )
        result[case["fixture_id"]] = fixture
    return result


def _case(probe: dict[str, Any], fixture_id: str) -> dict[str, Any]:
    for case in probe["cases"]:
        if case["fixture_id"] == fixture_id:
            return case
    raise SummaryDistortionProbeError(f"unknown fixture: {fixture_id}")


def response_template(probe: dict[str, Any]) -> dict[str, Any]:
    """Return an intentionally incomplete human-response template."""
    _validate_questions(probe.get("review_questions"))
    return {
        "schema": RESPONSE_SCHEMA,
        "answers": ["" for _ in probe["review_questions"]],
        "review_provenance": {
            "reviewer_id": "",
            "prior_exposure": "",
            "response_authorship": "",
            "note": "",
        },
        "operator_observation": {
            "review_completion_seconds": "not-observed",
            "source_reopen_count": "not-observed",
            "correction_burden": "not-observed",
        },
        "notes": "",
    }


def _non_negative_number_or_not_observed(value: Any, field: str) -> None:
    if value == "not-observed":
        return
    if (
        not isinstance(value, (int, float))
        or isinstance(value, bool)
        or value < 0
    ):
        raise SummaryDistortionProbeError(
            f"{field} must be a non-negative number or 'not-observed'"
        )


def _non_negative_int_or_not_observed(value: Any, field: str) -> None:
    if value == "not-observed":
        return
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise SummaryDistortionProbeError(
            f"{field} must be a non-negative integer or 'not-observed'"
        )


def validate_human_response(response: Any, probe: dict[str, Any]) -> None:
    """Fail closed unless a response is structurally usable as human-review input."""
    required = {
        "schema",
        "answers",
        "review_provenance",
        "operator_observation",
        "notes",
    }
    if not isinstance(response, dict) or set(response) != required:
        raise SummaryDistortionProbeError(
            "human response must contain schema/answers/review_provenance/"
            "operator_observation/notes exactly"
        )
    if response["schema"] != RESPONSE_SCHEMA:
        raise SummaryDistortionProbeError(
            f"human response schema must be {RESPONSE_SCHEMA}"
        )

    questions = probe.get("review_questions")
    _validate_questions(questions)
    answers = response["answers"]
    if not isinstance(answers, list) or len(answers) != len(questions):
        raise SummaryDistortionProbeError(
            f"human response requires exactly one answer per question "
            f"({len(questions)} expected)"
        )
    if any(not isinstance(value, str) or not value.strip() for value in answers):
        raise SummaryDistortionProbeError(
            "human response answers must be non-empty strings"
        )

    provenance = response["review_provenance"]
    provenance_keys = {
        "reviewer_id",
        "prior_exposure",
        "response_authorship",
        "note",
    }
    if not isinstance(provenance, dict) or set(provenance) != provenance_keys:
        raise SummaryDistortionProbeError("review_provenance has invalid shape")
    if (
        not isinstance(provenance["reviewer_id"], str)
        or not provenance["reviewer_id"].strip()
    ):
        raise SummaryDistortionProbeError(
            "reviewer_id must be a non-empty opaque id"
        )
    if provenance["prior_exposure"] not in PRIOR_EXPOSURE_VALUES:
        raise SummaryDistortionProbeError("prior_exposure has invalid value")
    if provenance["response_authorship"] not in RESPONSE_AUTHORSHIP_VALUES:
        raise SummaryDistortionProbeError(
            "response_authorship must declare human-direct or human-transcribed"
        )
    if not isinstance(provenance["note"], str):
        raise SummaryDistortionProbeError("review_provenance note must be a string")

    observation = response["operator_observation"]
    observation_keys = {
        "review_completion_seconds",
        "source_reopen_count",
        "correction_burden",
    }
    if not isinstance(observation, dict) or set(observation) != observation_keys:
        raise SummaryDistortionProbeError("operator_observation has invalid shape")
    _non_negative_number_or_not_observed(
        observation["review_completion_seconds"],
        "review_completion_seconds",
    )
    _non_negative_int_or_not_observed(
        observation["source_reopen_count"],
        "source_reopen_count",
    )
    if observation["correction_burden"] not in BURDEN_VALUES:
        raise SummaryDistortionProbeError("correction_burden has invalid value")
    if not isinstance(response["notes"], str):
        raise SummaryDistortionProbeError("human response notes must be a string")


def load_human_response(
    path: str | Path,
    probe: dict[str, Any],
) -> tuple[dict[str, Any], bytes]:
    try:
        raw = Path(path).read_bytes()
    except OSError as exc:
        raise SummaryDistortionProbeError(f"cannot load response: {path}") from exc
    if not raw.strip():
        raise SummaryDistortionProbeError("human response must not be empty")
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SummaryDistortionProbeError(
            "human response must be valid UTF-8 JSON"
        ) from exc
    validate_human_response(value, probe)
    return value, raw


def response_sha256(path: str | Path, probe: dict[str, Any]) -> str:
    _, raw = load_human_response(path, probe)
    return hashlib.sha256(raw).hexdigest()


def build_review_packet(
    probe: dict[str, Any],
    fixtures: dict[str, dict[str, Any]],
    fixture_id: str,
) -> dict[str, Any]:
    case, fixture = _case(probe, fixture_id), fixtures[fixture_id]
    orientation = fixture["conditions"]["C_sei_resume"]["surface_text"][
        "orientation"
    ]
    return {
        "schema": PACKET_SCHEMA,
        "status": "evaluation-only",
        "probe_id": probe["probe_id"],
        "fixture_id": fixture_id,
        "stage": "review",
        "canonical_orientation": orientation,
        "provisional_ai_summary": case["distorted_summary"],
        "provisional_ai_next_question": case["distorted_next_question"],
        "ai_stimulus_provenance": (
            "deliberately fallible evaluation-only AI summary / next-question "
            "suggestion; not canonical meaning"
        ),
        "questions": probe["review_questions"],
        "response_template": response_template(probe),
        "presentation_rules": probe["presentation_rules"],
        "interpretation_stoplines": probe["interpretation_stoplines"],
        "semantic_stopline": probe["semantic_stopline"],
    }


def build_audit_packet(
    probe: dict[str, Any],
    fixtures: dict[str, dict[str, Any]],
    fixture_id: str,
    response: str | Path,
) -> dict[str, Any]:
    response_value, raw = load_human_response(response, probe)
    fixed = hashlib.sha256(raw).hexdigest()
    case, fixture = _case(probe, fixture_id), fixtures[fixture_id]
    return {
        "schema": PACKET_SCHEMA,
        "status": "evaluation-only",
        "probe_id": probe["probe_id"],
        "fixture_id": fixture_id,
        "stage": "audit",
        "fixed_human_response_sha256": fixed,
        "review_provenance": dict(response_value["review_provenance"]),
        "operator_observation": dict(response_value["operator_observation"]),
        "provenance_stopline": (
            "reviewer id, prior exposure, and response authorship are declared "
            "evaluation metadata; they are not independent proof of blinding "
            "or human authorship"
        ),
        "distortion_key": case["distortion_key"],
        "reference_state": fixture["reference_state"],
        "post_interruption_evidence": fixture["scenario"][
            "post_interruption_evidence"
        ],
        "audit_dimensions": probe["audit_dimensions"],
        "evidence_boundary": probe["evidence_boundary"],
        "interpretation_stoplines": probe["interpretation_stoplines"],
        "semantic_stopline": probe["semantic_stopline"],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build canonical ISSUE-000078 E78.3 summary-distortion packets"
    )
    parser.add_argument("--probe", required=True)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--fixture-id")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate")
    sub.add_parser("review")
    audit = sub.add_parser("audit")
    audit.add_argument("--response", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    probe = load_json(args.probe)
    fixtures = load_sources(probe, args.repo_root)
    if args.command == "validate":
        result = {
            "valid": True,
            "probe_id": probe["probe_id"],
            "cases": len(fixtures),
            "human_response_schema": RESPONSE_SCHEMA,
        }
    else:
        if not args.fixture_id:
            raise SummaryDistortionProbeError(
                "--fixture-id is required for review/audit"
            )
        if args.fixture_id not in fixtures:
            raise SummaryDistortionProbeError(
                f"unknown fixture: {args.fixture_id}"
            )
        if args.command == "review":
            result = build_review_packet(probe, fixtures, args.fixture_id)
        elif args.command == "audit":
            result = build_audit_packet(
                probe,
                fixtures,
                args.fixture_id,
                args.response,
            )
        else:
            raise AssertionError(f"unhandled command: {args.command}")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
