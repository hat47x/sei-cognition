#!/usr/bin/env python3
"""Build the canonical stage-gated ISSUE-000078 E78.3 distortion packets.

The provisional AI summary and next-question suggestion are deliberately fallible
evaluation material. Source fixtures remain authoritative for historical
comparison; neither the stimulus nor a human correction mutates canonical Inquiry
meaning. This module is the single maintained E78.3 probe path.
"""
from __future__ import annotations

import argparse
import copy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
from typing import Any

SCHEMA = "sei.inquiry-continuity-summary-distortion-probe/v1"
FIXTURE_SCHEMA = "sei.inquiry-continuity-comparison-fixture/v0"
PACKET_SCHEMA = "sei.inquiry-continuity-summary-distortion-packet/v0"
RESPONSE_SCHEMA = "sei.inquiry-continuity-summary-distortion-response/v1"
REVIEW_START_RECEIPT_SCHEMA = (
    "sei.inquiry-continuity-summary-distortion-review-start-receipt/v0"
)
AUDIT_REVEAL_RECEIPT_SCHEMA = (
    "sei.inquiry-continuity-summary-distortion-audit-reveal-receipt/v1"
)
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


def probe_content_sha256(probe: dict[str, Any]) -> str:
    """Return a stable semantic digest for the evaluation probe content."""
    payload = json.dumps(
        probe,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


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
    dimensions = probe.get("audit_dimensions")
    if not isinstance(dimensions, list) or not dimensions:
        raise SummaryDistortionProbeError("audit dimensions are required")
    dimension_ids: list[str] = []
    for dimension in dimensions:
        if not isinstance(dimension, dict) or set(dimension) != {
            "id",
            "value_kind",
            "allowed_values",
        }:
            raise SummaryDistortionProbeError(
                "audit dimension must contain id/value_kind/allowed_values exactly"
            )
        dimension_id = dimension["id"]
        value_kind = dimension["value_kind"]
        allowed_values = dimension["allowed_values"]
        if not isinstance(dimension_id, str) or not dimension_id.strip():
            raise SummaryDistortionProbeError(
                "audit dimension id must be non-empty"
            )
        if not isinstance(value_kind, str) or not value_kind.strip():
            raise SummaryDistortionProbeError(
                "audit dimension value_kind must be non-empty"
            )
        if (
            not isinstance(allowed_values, list)
            or not allowed_values
            or any(
                not isinstance(value, str) or not value.strip()
                for value in allowed_values
            )
            or len(allowed_values) != len(set(allowed_values))
        ):
            raise SummaryDistortionProbeError(
                "audit dimension allowed_values must be unique non-empty strings"
            )
        if "not-observed" not in allowed_values:
            raise SummaryDistortionProbeError(
                "audit dimension must allow not-observed"
            )
        dimension_ids.append(dimension_id)
    if len(dimension_ids) != len(set(dimension_ids)):
        raise SummaryDistortionProbeError("audit dimension ids must be unique")


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


def response_template(
    probe: dict[str, Any],
    review_receipt_value: dict[str, Any],
    review_receipt_raw: bytes,
) -> dict[str, Any]:
    """Return an intentionally incomplete response bound to pre-stimulus provenance."""
    _validate_questions(probe.get("review_questions"))
    validate_review_start_receipt(
        review_receipt_value,
        probe,
        review_receipt_value.get("fixture_id"),
    )
    return {
        "schema": RESPONSE_SCHEMA,
        "probe_sha256": probe_content_sha256(probe),
        "review_start_receipt_sha256": review_receipt_sha,
        "answers": ["" for _ in probe["review_questions"]],
        "review_provenance": {
            "reviewer_id": review_receipt_value["reviewer_id"],
            "prior_exposure": review_receipt_value["prior_exposure"],
            "response_authorship": review_receipt_value["response_authorship"],
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
        "probe_sha256",
        "review_start_receipt_sha256",
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
    if response["probe_sha256"] != probe_content_sha256(probe):
        raise SummaryDistortionProbeError(
            "human response is bound to a different probe content"
        )
    review_receipt_sha = response["review_start_receipt_sha256"]
    if (
        not isinstance(review_receipt_sha, str)
        or len(review_receipt_sha) != 64
        or any(c not in "0123456789abcdef" for c in review_receipt_sha)
    ):
        raise SummaryDistortionProbeError(
            "review_start_receipt_sha256 must be a lowercase SHA-256 hex digest"
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


def _parse_timestamp(value: Any, field: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise SummaryDistortionProbeError(f"{field} must be a non-empty timestamp")
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise SummaryDistortionProbeError(
            f"{field} must be ISO-8601"
        ) from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise SummaryDistortionProbeError(
            f"{field} must include a timezone offset"
        )
    return parsed.astimezone(timezone.utc)


def review_start_receipt_bytes(receipt: dict[str, Any]) -> bytes:
    return (
        json.dumps(receipt, ensure_ascii=False, indent=2) + "\n"
    ).encode("utf-8")


def build_review_start_receipt(
    probe: dict[str, Any],
    fixture_id: str,
    reviewer_id: str,
    prior_exposure: str,
    response_authorship: str,
    started_at: str,
) -> dict[str, Any]:
    validate_probe(probe)
    _case(probe, fixture_id)
    if not isinstance(reviewer_id, str) or not reviewer_id.strip():
        raise SummaryDistortionProbeError(
            "reviewer_id must be a non-empty opaque id"
        )
    if prior_exposure not in PRIOR_EXPOSURE_VALUES:
        raise SummaryDistortionProbeError("prior_exposure has invalid value")
    if response_authorship not in RESPONSE_AUTHORSHIP_VALUES:
        raise SummaryDistortionProbeError(
            "response_authorship must declare human-direct or human-transcribed"
        )
    _parse_timestamp(started_at, "started_at")
    return {
        "schema": REVIEW_START_RECEIPT_SCHEMA,
        "status": "evaluation-only",
        "probe_id": probe["probe_id"],
        "fixture_id": fixture_id,
        "probe_sha256": probe_content_sha256(probe),
        "reviewer_id": reviewer_id,
        "prior_exposure": prior_exposure,
        "response_authorship": response_authorship,
        "started_at": started_at,
    }


def save_review_start_receipt(
    path: str | Path,
    receipt: dict[str, Any],
) -> None:
    target = Path(path)
    payload = review_start_receipt_bytes(receipt)
    try:
        with target.open("xb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError as exc:
        raise SummaryDistortionProbeError(
            f"refusing to overwrite existing review-start receipt: {target}"
        ) from exc


def validate_review_start_receipt(
    value: Any,
    probe: dict[str, Any],
    fixture_id: str,
) -> None:
    required = {
        "schema",
        "status",
        "probe_id",
        "fixture_id",
        "probe_sha256",
        "reviewer_id",
        "prior_exposure",
        "response_authorship",
        "started_at",
    }
    if not isinstance(value, dict) or set(value) != required:
        raise SummaryDistortionProbeError("review-start receipt has invalid shape")
    if value["schema"] != REVIEW_START_RECEIPT_SCHEMA:
        raise SummaryDistortionProbeError(
            f"review-start receipt schema must be {REVIEW_START_RECEIPT_SCHEMA}"
        )
    if value["status"] != "evaluation-only":
        raise SummaryDistortionProbeError(
            "review-start receipt must remain evaluation-only"
        )
    if value["probe_id"] != probe["probe_id"]:
        raise SummaryDistortionProbeError("review-start receipt probe_id mismatch")
    if value["fixture_id"] != fixture_id:
        raise SummaryDistortionProbeError("review-start receipt fixture_id mismatch")
    if value["probe_sha256"] != probe_content_sha256(probe):
        raise SummaryDistortionProbeError(
            "review-start receipt is bound to different probe content"
        )
    if (
        not isinstance(value["reviewer_id"], str)
        or not value["reviewer_id"].strip()
    ):
        raise SummaryDistortionProbeError(
            "review-start reviewer_id must be a non-empty opaque id"
        )
    if value["prior_exposure"] not in PRIOR_EXPOSURE_VALUES:
        raise SummaryDistortionProbeError(
            "review-start prior_exposure has invalid value"
        )
    if value["response_authorship"] not in RESPONSE_AUTHORSHIP_VALUES:
        raise SummaryDistortionProbeError(
            "review-start response_authorship has invalid value"
        )
    _parse_timestamp(value["started_at"], "started_at")


def load_review_start_receipt(
    path: str | Path,
    probe: dict[str, Any],
    fixture_id: str,
) -> tuple[dict[str, Any], bytes]:
    try:
        raw = Path(path).read_bytes()
    except OSError as exc:
        raise SummaryDistortionProbeError(
            f"cannot load review-start receipt: {path}"
        ) from exc
    if not raw.strip():
        raise SummaryDistortionProbeError("review-start receipt must not be empty")
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SummaryDistortionProbeError(
            "review-start receipt must be valid UTF-8 JSON"
        ) from exc
    validate_review_start_receipt(value, probe, fixture_id)
    return value, raw


def validate_human_response_against_review_start(
    response: dict[str, Any],
    probe: dict[str, Any],
    fixture_id: str,
    review_receipt_value: dict[str, Any],
    review_receipt_raw: bytes,
) -> None:
    validate_human_response(response, probe)
    validate_review_start_receipt(
        review_receipt_value,
        probe,
        fixture_id,
    )
    receipt_sha = hashlib.sha256(review_receipt_raw).hexdigest()
    if response["review_start_receipt_sha256"] != receipt_sha:
        raise SummaryDistortionProbeError(
            "human response is bound to a different review-start receipt"
        )
    provenance = response["review_provenance"]
    for field in ("reviewer_id", "prior_exposure", "response_authorship"):
        if provenance[field] != review_receipt_value[field]:
            raise SummaryDistortionProbeError(
                f"human response {field} differs from pre-stimulus declaration"
            )


def build_audit_material(
    probe: dict[str, Any],
    fixtures: dict[str, dict[str, Any]],
    fixture_id: str,
) -> dict[str, Any]:
    """Build the exact reference material that will be revealed at audit stage."""
    case, fixture = _case(probe, fixture_id), fixtures[fixture_id]
    return {
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


def audit_material_sha256(material: dict[str, Any]) -> str:
    payload = json.dumps(
        material,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def audit_reveal_receipt_bytes(receipt: dict[str, Any]) -> bytes:
    return (
        json.dumps(receipt, ensure_ascii=False, indent=2) + "\n"
    ).encode("utf-8")


def build_audit_reveal_receipt(
    probe: dict[str, Any],
    fixture_id: str,
    response: str | Path,
    review_receipt_value: dict[str, Any],
    review_receipt_raw: bytes,
    audit_material_digest: str,
    revealed_at: str,
) -> dict[str, Any]:
    """Bind the fixed response and review start before audit material is emitted."""
    validate_probe(probe)
    _case(probe, fixture_id)
    response_value, raw = load_human_response(response, probe)
    validate_human_response_against_review_start(
        response_value,
        probe,
        fixture_id,
        review_receipt_value,
        review_receipt_raw,
    )
    if (
        not isinstance(audit_material_digest, str)
        or len(audit_material_digest) != 64
        or any(c not in "0123456789abcdef" for c in audit_material_digest)
    ):
        raise SummaryDistortionProbeError(
            "audit_material_digest must be a lowercase SHA-256 hex digest"
        )
    started = _parse_timestamp(
        review_receipt_value["started_at"],
        "review_started_at",
    )
    revealed = _parse_timestamp(revealed_at, "revealed_at")
    if revealed < started:
        raise SummaryDistortionProbeError(
            "revealed_at must not precede review started_at"
        )
    review_receipt_sha = hashlib.sha256(review_receipt_raw).hexdigest()
    return {
        "schema": AUDIT_REVEAL_RECEIPT_SCHEMA,
        "status": "evaluation-only",
        "probe_id": probe["probe_id"],
        "fixture_id": fixture_id,
        "probe_sha256": probe_content_sha256(probe),
        "review_start_receipt_sha256": review_receipt_sha,
        "review_started_at": review_receipt_value["started_at"],
        "fixed_human_response_sha256": hashlib.sha256(raw).hexdigest(),
        "audit_material_sha256": audit_material_digest,
        "revealed_at": revealed_at,
    }


def save_audit_reveal_receipt(
    path: str | Path,
    receipt: dict[str, Any],
) -> None:
    """Persist the reveal boundary before returning audit material."""
    target = Path(path)
    payload = audit_reveal_receipt_bytes(receipt)
    try:
        with target.open("xb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError as exc:
        raise SummaryDistortionProbeError(
            f"refusing to overwrite existing audit-reveal receipt: {target}"
        ) from exc


def validate_audit_reveal_receipt(
    value: Any,
    probe: dict[str, Any],
    fixture_id: str,
    fixed_human_response_sha256: str,
    expected_review_start_receipt_sha256: str,
    expected_review_started_at: str,
    expected_audit_material_sha256: str,
) -> None:
    required = {
        "schema",
        "status",
        "probe_id",
        "fixture_id",
        "probe_sha256",
        "review_start_receipt_sha256",
        "review_started_at",
        "fixed_human_response_sha256",
        "audit_material_sha256",
        "revealed_at",
    }
    if not isinstance(value, dict) or set(value) != required:
        raise SummaryDistortionProbeError(
            "audit-reveal receipt has invalid shape"
        )
    if value["schema"] != AUDIT_REVEAL_RECEIPT_SCHEMA:
        raise SummaryDistortionProbeError(
            f"audit-reveal receipt schema must be {AUDIT_REVEAL_RECEIPT_SCHEMA}"
        )
    if value["status"] != "evaluation-only":
        raise SummaryDistortionProbeError(
            "audit-reveal receipt must remain evaluation-only"
        )
    if value["probe_id"] != probe["probe_id"]:
        raise SummaryDistortionProbeError("audit-reveal receipt probe_id mismatch")
    if value["fixture_id"] != fixture_id:
        raise SummaryDistortionProbeError("audit-reveal receipt fixture_id mismatch")
    if value["probe_sha256"] != probe_content_sha256(probe):
        raise SummaryDistortionProbeError(
            "audit-reveal receipt is bound to different probe content"
        )
    if (
        value["review_start_receipt_sha256"]
        != expected_review_start_receipt_sha256
    ):
        raise SummaryDistortionProbeError(
            "audit-reveal receipt is bound to a different review-start receipt"
        )
    if value["review_started_at"] != expected_review_started_at:
        raise SummaryDistortionProbeError(
            "audit-reveal receipt review_started_at mismatch"
        )
    if value["fixed_human_response_sha256"] != fixed_human_response_sha256:
        raise SummaryDistortionProbeError(
            "audit-reveal receipt is bound to a different human response"
        )
    if value["audit_material_sha256"] != expected_audit_material_sha256:
        raise SummaryDistortionProbeError(
            "audit-reveal receipt is bound to different audit material"
        )
    started = _parse_timestamp(
        value["review_started_at"],
        "review_started_at",
    )
    revealed = _parse_timestamp(value["revealed_at"], "revealed_at")
    if revealed < started:
        raise SummaryDistortionProbeError(
            "audit-reveal receipt revealed_at precedes review started_at"
        )


def load_audit_reveal_receipt(
    path: str | Path,
    probe: dict[str, Any],
    fixture_id: str,
    fixed_human_response_sha256: str,
    expected_review_start_receipt_sha256: str,
    expected_review_started_at: str,
    expected_audit_material_sha256: str,
) -> tuple[dict[str, Any], bytes]:
    try:
        raw = Path(path).read_bytes()
    except OSError as exc:
        raise SummaryDistortionProbeError(
            f"cannot load audit-reveal receipt: {path}"
        ) from exc
    if not raw.strip():
        raise SummaryDistortionProbeError("audit-reveal receipt must not be empty")
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SummaryDistortionProbeError(
            "audit-reveal receipt must be valid UTF-8 JSON"
        ) from exc
    validate_audit_reveal_receipt(
        value,
        probe,
        fixture_id,
        fixed_human_response_sha256,
        expected_review_start_receipt_sha256,
        expected_review_started_at,
        expected_audit_material_sha256,
    )
    return value, raw


def build_review_packet_from_receipt(
    probe: dict[str, Any],
    fixtures: dict[str, dict[str, Any]],
    fixture_id: str,
    review_receipt_value: dict[str, Any],
    review_receipt_raw: bytes,
) -> dict[str, Any]:
    validate_review_start_receipt(
        review_receipt_value,
        probe,
        fixture_id,
    )
    case, fixture = _case(probe, fixture_id), fixtures[fixture_id]
    orientation = fixture["conditions"]["C_sei_resume"]["surface_text"][
        "orientation"
    ]
    receipt_sha = hashlib.sha256(review_receipt_raw).hexdigest()
    return {
        "schema": PACKET_SCHEMA,
        "status": "evaluation-only",
        "probe_id": probe["probe_id"],
        "fixture_id": fixture_id,
        "probe_sha256": probe_content_sha256(probe),
        "stage": "review",
        "review_start_receipt_sha256": receipt_sha,
        "review_started_at": review_receipt_value["started_at"],
        "review_provenance_declaration": {
            "reviewer_id": review_receipt_value["reviewer_id"],
            "prior_exposure": review_receipt_value["prior_exposure"],
            "response_authorship": review_receipt_value["response_authorship"],
        },
        "canonical_orientation": orientation,
        "provisional_ai_summary": case["distorted_summary"],
        "provisional_ai_next_question": case["distorted_next_question"],
        "ai_stimulus_provenance": (
            "deliberately fallible evaluation-only AI summary / next-question "
            "suggestion; not canonical meaning"
        ),
        "questions": probe["review_questions"],
        "response_template": response_template(
            probe,
            review_receipt_value,
            review_receipt_raw,
        ),
        "presentation_rules": probe["presentation_rules"],
        "interpretation_stoplines": probe["interpretation_stoplines"],
        "semantic_stopline": probe["semantic_stopline"],
    }


def build_review_packet(
    probe: dict[str, Any],
    fixtures: dict[str, dict[str, Any]],
    fixture_id: str,
    review_receipt: str | Path,
) -> dict[str, Any]:
    review_receipt_value, review_receipt_raw = load_review_start_receipt(
        review_receipt,
        probe,
        fixture_id,
    )
    return build_review_packet_from_receipt(
        probe,
        fixtures,
        fixture_id,
        review_receipt_value,
        review_receipt_raw,
    )


def build_audit_packet_from_receipt(
    probe: dict[str, Any],
    fixtures: dict[str, dict[str, Any]],
    fixture_id: str,
    response: str | Path,
    review_receipt_value: dict[str, Any],
    review_receipt_raw: bytes,
    receipt_value: dict[str, Any],
    receipt_raw: bytes,
) -> dict[str, Any]:
    response_value, raw = load_human_response(response, probe)
    validate_human_response_against_review_start(
        response_value,
        probe,
        fixture_id,
        review_receipt_value,
        review_receipt_raw,
    )
    fixed = hashlib.sha256(raw).hexdigest()
    material = build_audit_material(probe, fixtures, fixture_id)
    material_digest = audit_material_sha256(material)
    review_receipt_sha = hashlib.sha256(review_receipt_raw).hexdigest()
    validate_audit_reveal_receipt(
        receipt_value,
        probe,
        fixture_id,
        fixed,
        review_receipt_sha,
        review_receipt_value["started_at"],
        material_digest,
    )
    return {
        "schema": PACKET_SCHEMA,
        "status": "evaluation-only",
        "probe_id": probe["probe_id"],
        "fixture_id": fixture_id,
        "probe_sha256": probe_content_sha256(probe),
        "stage": "audit",
        "review_start_receipt_sha256": hashlib.sha256(
            review_receipt_raw
        ).hexdigest(),
        "review_started_at": review_receipt_value["started_at"],
        "fixed_human_response_sha256": fixed,
        "audit_material_sha256": material_digest,
        "audit_reveal_receipt_sha256": hashlib.sha256(receipt_raw).hexdigest(),
        "audit_revealed_at": receipt_value["revealed_at"],
        "review_provenance": dict(response_value["review_provenance"]),
        "operator_observation": dict(response_value["operator_observation"]),
        "provenance_stopline": (
            "reviewer id, prior exposure, and response authorship are declared "
            "evaluation metadata; they are not independent proof of blinding "
            "or human authorship"
        ),
        **material,
    }


def build_audit_packet(
    probe: dict[str, Any],
    fixtures: dict[str, dict[str, Any]],
    fixture_id: str,
    response: str | Path,
    review_receipt: str | Path,
    receipt: str | Path,
) -> dict[str, Any]:
    response_value, raw = load_human_response(response, probe)
    review_receipt_value, review_receipt_raw = load_review_start_receipt(
        review_receipt,
        probe,
        fixture_id,
    )
    validate_human_response_against_review_start(
        response_value,
        probe,
        fixture_id,
        review_receipt_value,
        review_receipt_raw,
    )
    fixed = hashlib.sha256(raw).hexdigest()
    material = build_audit_material(probe, fixtures, fixture_id)
    material_digest = audit_material_sha256(material)
    review_receipt_sha = hashlib.sha256(review_receipt_raw).hexdigest()
    receipt_value, receipt_raw = load_audit_reveal_receipt(
        receipt,
        probe,
        fixture_id,
        fixed,
        review_receipt_sha,
        review_receipt_value["started_at"],
        material_digest,
    )
    return build_audit_packet_from_receipt(
        probe,
        fixtures,
        fixture_id,
        response,
        review_receipt_value,
        review_receipt_raw,
        receipt_value,
        receipt_raw,
    )


def probe_contract_summary(
    probe: dict[str, Any],
    fixtures: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Return the operator-visible E78.3 contract after full source validation."""
    validate_probe(probe)
    expected_fixture_ids = {
        case["fixture_id"] for case in probe["cases"]
    }
    if set(fixtures) != expected_fixture_ids:
        raise SummaryDistortionProbeError(
            "validated fixture set must match all probe cases exactly"
        )
    return {
        "valid": True,
        "probe_id": probe["probe_id"],
        "probe_schema": probe["schema"],
        "probe_sha256": probe_content_sha256(probe),
        "cases": len(fixtures),
        "source_fixtures": [
            {
                "fixture_id": case["fixture_id"],
                "path": case["path"],
                "blob_sha1": case["blob_sha1"],
            }
            for case in probe["cases"]
        ],
        "packet_schema": PACKET_SCHEMA,
        "human_response_schema": RESPONSE_SCHEMA,
        "review_start_receipt_schema": REVIEW_START_RECEIPT_SCHEMA,
        "audit_reveal_receipt_schema": AUDIT_REVEAL_RECEIPT_SCHEMA,
        "audit_dimensions": copy.deepcopy(probe["audit_dimensions"]),
        "evidence_boundary": copy.deepcopy(probe["evidence_boundary"]),
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
    review = sub.add_parser("review")
    review.add_argument("--review-receipt", required=True)
    review.add_argument("--reviewer-id", required=True)
    review.add_argument(
        "--prior-exposure",
        required=True,
        choices=sorted(PRIOR_EXPOSURE_VALUES),
    )
    review.add_argument(
        "--response-authorship",
        required=True,
        choices=sorted(RESPONSE_AUTHORSHIP_VALUES),
    )
    audit = sub.add_parser("audit")
    audit.add_argument("--response", required=True)
    audit.add_argument("--review-receipt", required=True)
    audit.add_argument("--receipt", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    probe = load_json(args.probe)
    fixtures = load_sources(probe, args.repo_root)
    if args.command == "validate":
        result = probe_contract_summary(probe, fixtures)
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
            started_at = datetime.now(timezone.utc).isoformat().replace(
                "+00:00", "Z"
            )
            review_receipt = build_review_start_receipt(
                probe,
                args.fixture_id,
                args.reviewer_id,
                args.prior_exposure,
                args.response_authorship,
                started_at,
            )
            review_receipt_raw = review_start_receipt_bytes(review_receipt)
            result = build_review_packet_from_receipt(
                probe,
                fixtures,
                args.fixture_id,
                review_receipt,
                review_receipt_raw,
            )
            save_review_start_receipt(
                args.review_receipt,
                review_receipt,
            )
        elif args.command == "audit":
            response_value, _ = load_human_response(args.response, probe)
            review_receipt_value, review_receipt_raw = load_review_start_receipt(
                args.review_receipt,
                probe,
                args.fixture_id,
            )
            validate_human_response_against_review_start(
                response_value,
                probe,
                args.fixture_id,
                review_receipt_value,
                review_receipt_raw,
            )
            material = build_audit_material(
                probe,
                fixtures,
                args.fixture_id,
            )
            material_digest = audit_material_sha256(material)
            revealed_at = datetime.now(timezone.utc).isoformat().replace(
                "+00:00", "Z"
            )
            receipt = build_audit_reveal_receipt(
                probe,
                args.fixture_id,
                args.response,
                review_receipt_value,
                review_receipt_raw,
                material_digest,
                revealed_at,
            )
            receipt_raw = audit_reveal_receipt_bytes(receipt)
            result = build_audit_packet_from_receipt(
                probe,
                fixtures,
                args.fixture_id,
                args.response,
                review_receipt_value,
                review_receipt_raw,
                receipt,
                receipt_raw,
            )
            save_audit_reveal_receipt(args.receipt, receipt)
        else:
            raise AssertionError(f"unhandled command: {args.command}")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
