#!/usr/bin/env python3
"""Export durable ISSUE-000078 E78.3 review evidence without collapsing layers.

The initial reviewer response is fixed before audit material is revealed by the
summary-distortion probe. This module records the later semantic audit as a
separate artifact and exports both layers together without inventing missing
observations, computing a score/winner, or promoting the result to Product Value
evidence.
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

from inquiry_continuity_summary_distortion_probe import (
    PRIOR_EXPOSURE_VALUES,
    RESPONSE_AUTHORSHIP_VALUES,
    SummaryDistortionProbeError,
    audit_material_sha256,
    build_audit_material,
    load_audit_reveal_receipt,
    load_human_response,
    load_review_start_receipt,
    load_json,
    load_sources,
    probe_content_sha256,
    validate_human_response_against_review_start,
    validate_probe,
)

AUDIT_RESPONSE_SCHEMA = "sei.inquiry-continuity-summary-distortion-audit-response/v1"
EVIDENCE_SCHEMA = "sei.inquiry-continuity-summary-distortion-evidence/v1"


class SummaryDistortionEvidenceError(ValueError):
    """Raised when E78.3 evidence cannot be recorded without weakening boundaries."""


def _case(probe: dict[str, Any], fixture_id: str) -> dict[str, Any]:
    for case in probe["cases"]:
        if case["fixture_id"] == fixture_id:
            return case
    raise SummaryDistortionEvidenceError(f"unknown fixture: {fixture_id}")


def _parse_timestamp(value: Any, field: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise SummaryDistortionEvidenceError(
            f"{field} must be a non-empty timestamp"
        )
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise SummaryDistortionEvidenceError(
            f"{field} must be ISO-8601"
        ) from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise SummaryDistortionEvidenceError(
            f"{field} must include a timezone offset"
        )
    return parsed.astimezone(timezone.utc)


def audit_response_template(
    probe: dict[str, Any],
    fixture_id: str,
    fixed_human_response_sha256: str,
    audit_reveal_receipt_sha256: str,
) -> dict[str, Any]:
    """Return an intentionally incomplete post-reveal semantic-audit template."""
    validate_probe(probe)
    _case(probe, fixture_id)
    if (
        not isinstance(fixed_human_response_sha256, str)
        or len(fixed_human_response_sha256) != 64
        or any(c not in "0123456789abcdef" for c in fixed_human_response_sha256)
    ):
        raise SummaryDistortionEvidenceError(
            "fixed_human_response_sha256 must be a lowercase SHA-256 hex digest"
        )
    if (
        not isinstance(audit_reveal_receipt_sha256, str)
        or len(audit_reveal_receipt_sha256) != 64
        or any(c not in "0123456789abcdef" for c in audit_reveal_receipt_sha256)
    ):
        raise SummaryDistortionEvidenceError(
            "audit_reveal_receipt_sha256 must be a lowercase SHA-256 hex digest"
        )
    return {
        "schema": AUDIT_RESPONSE_SCHEMA,
        "fixture_id": fixture_id,
        "probe_sha256": probe_content_sha256(probe),
        "fixed_human_response_sha256": fixed_human_response_sha256,
        "audit_reveal_receipt_sha256": audit_reveal_receipt_sha256,
        "findings": {
            dimension["id"]: "not-observed"
            for dimension in probe["audit_dimensions"]
        },
        "audit_provenance": {
            "auditor_id": "",
            "response_authorship": "",
            "completed_at": "",
            "note": "",
        },
        "notes": "",
    }


def validate_audit_response(
    value: Any,
    probe: dict[str, Any],
    fixture_id: str,
    fixed_human_response_sha256: str,
    audit_reveal_receipt_sha256: str,
    audit_revealed_at: str,
) -> None:
    validate_probe(probe)
    _case(probe, fixture_id)
    required = {
        "schema",
        "fixture_id",
        "probe_sha256",
        "fixed_human_response_sha256",
        "audit_reveal_receipt_sha256",
        "findings",
        "audit_provenance",
        "notes",
    }
    if not isinstance(value, dict) or set(value) != required:
        raise SummaryDistortionEvidenceError(
            "audit response must contain schema/fixture_id/"
            "fixed_human_response_sha256/findings/audit_provenance/notes exactly"
        )
    if value["schema"] != AUDIT_RESPONSE_SCHEMA:
        raise SummaryDistortionEvidenceError(
            f"audit response schema must be {AUDIT_RESPONSE_SCHEMA}"
        )
    if value["fixture_id"] != fixture_id:
        raise SummaryDistortionEvidenceError("audit response fixture_id mismatch")
    if value["probe_sha256"] != probe_content_sha256(probe):
        raise SummaryDistortionEvidenceError(
            "audit response is bound to a different probe content"
        )
    if value["fixed_human_response_sha256"] != fixed_human_response_sha256:
        raise SummaryDistortionEvidenceError(
            "audit response is bound to a different human response"
        )
    if value["audit_reveal_receipt_sha256"] != audit_reveal_receipt_sha256:
        raise SummaryDistortionEvidenceError(
            "audit response is bound to a different audit-reveal receipt"
        )

    dimension_contracts = {
        dimension["id"]: set(dimension["allowed_values"])
        for dimension in probe["audit_dimensions"]
    }
    findings = value["findings"]
    if not isinstance(findings, dict) or set(findings) != set(dimension_contracts):
        raise SummaryDistortionEvidenceError(
            "audit findings must contain each audit dimension exactly"
        )
    for dimension_id, result in findings.items():
        if result not in dimension_contracts[dimension_id]:
            allowed = "/".join(sorted(dimension_contracts[dimension_id]))
            raise SummaryDistortionEvidenceError(
                f"audit finding {dimension_id} must be one of: {allowed}"
            )

    provenance = value["audit_provenance"]
    provenance_keys = {
        "auditor_id",
        "response_authorship",
        "completed_at",
        "note",
    }
    if not isinstance(provenance, dict) or set(provenance) != provenance_keys:
        raise SummaryDistortionEvidenceError("audit_provenance has invalid shape")
    if (
        not isinstance(provenance["auditor_id"], str)
        or not provenance["auditor_id"].strip()
    ):
        raise SummaryDistortionEvidenceError(
            "auditor_id must be a non-empty opaque id"
        )
    if provenance["response_authorship"] not in RESPONSE_AUTHORSHIP_VALUES:
        raise SummaryDistortionEvidenceError(
            "audit response authorship must be human-direct or human-transcribed"
        )
    completed_at = _parse_timestamp(
        provenance["completed_at"],
        "completed_at",
    )
    revealed_at = _parse_timestamp(audit_revealed_at, "audit_revealed_at")
    if completed_at < revealed_at:
        raise SummaryDistortionEvidenceError(
            "completed_at must not precede audit reveal"
        )
    if not isinstance(provenance["note"], str):
        raise SummaryDistortionEvidenceError("audit_provenance note must be a string")
    if not isinstance(value["notes"], str):
        raise SummaryDistortionEvidenceError("audit notes must be a string")


def load_audit_response(
    path: str | Path,
    probe: dict[str, Any],
    fixture_id: str,
    fixed_human_response_sha256: str,
    audit_reveal_receipt_sha256: str,
    audit_revealed_at: str,
) -> tuple[dict[str, Any], bytes]:
    try:
        raw = Path(path).read_bytes()
    except OSError as exc:
        raise SummaryDistortionEvidenceError(
            f"cannot load audit response: {path}"
        ) from exc
    if not raw.strip():
        raise SummaryDistortionEvidenceError("audit response must not be empty")
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SummaryDistortionEvidenceError(
            "audit response must be valid UTF-8 JSON"
        ) from exc
    validate_audit_response(
        value,
        probe,
        fixture_id,
        fixed_human_response_sha256,
        audit_reveal_receipt_sha256,
        audit_revealed_at,
    )
    return value, raw


def build_evidence_bundle(
    probe: dict[str, Any],
    fixtures: dict[str, dict[str, Any]],
    fixture_id: str,
    human_response_path: str | Path,
    review_start_receipt_path: str | Path,
    audit_reveal_receipt_path: str | Path,
    audit_response_path: str | Path,
) -> dict[str, Any]:
    """Build one E78.3 bundle with reviewer observation and semantic audit separated."""
    if fixture_id not in fixtures:
        raise SummaryDistortionEvidenceError(f"unknown fixture: {fixture_id}")
    case = _case(probe, fixture_id)
    try:
        human_response, human_raw = load_human_response(
            human_response_path,
            probe,
        )
    except SummaryDistortionProbeError as exc:
        raise SummaryDistortionEvidenceError(str(exc)) from exc
    fixed_human_response_sha256 = hashlib.sha256(human_raw).hexdigest()
    try:
        review_receipt_value, review_receipt_raw = load_review_start_receipt(
            review_start_receipt_path,
            probe,
            fixture_id,
        )
        validate_human_response_against_review_start(
            human_response,
            probe,
            fixture_id,
            review_receipt_value,
            review_receipt_raw,
        )
    except SummaryDistortionProbeError as exc:
        raise SummaryDistortionEvidenceError(str(exc)) from exc
    review_start_receipt_sha256 = hashlib.sha256(
        review_receipt_raw
    ).hexdigest()
    material = build_audit_material(probe, fixtures, fixture_id)
    material_digest = audit_material_sha256(material)
    try:
        receipt_value, receipt_raw = load_audit_reveal_receipt(
            audit_reveal_receipt_path,
            probe,
            fixture_id,
            fixed_human_response_sha256,
            review_start_receipt_sha256,
            review_receipt_value["started_at"],
            material_digest,
        )
    except SummaryDistortionProbeError as exc:
        raise SummaryDistortionEvidenceError(str(exc)) from exc
    audit_reveal_receipt_sha256 = hashlib.sha256(receipt_raw).hexdigest()
    audit_response, audit_raw = load_audit_response(
        audit_response_path,
        probe,
        fixture_id,
        fixed_human_response_sha256,
        audit_reveal_receipt_sha256,
        receipt_value["revealed_at"],
    )

    return {
        "schema": EVIDENCE_SCHEMA,
        "status": "evaluation-only",
        "probe_id": probe["probe_id"],
        "fixture_id": fixture_id,
        "probe_snapshot": {
            "content_sha256": probe_content_sha256(probe),
            "distorted_summary": case["distorted_summary"],
            "distorted_next_question": case["distorted_next_question"],
            "review_questions": copy.deepcopy(probe["review_questions"]),
            "audit_dimensions": copy.deepcopy(probe["audit_dimensions"]),
        },
        "source_snapshot": {
            "path": case["path"],
            "blob_sha1": case["blob_sha1"],
        },
        "review_start": {
            "receipt_sha256": review_start_receipt_sha256,
            "started_at": review_receipt_value["started_at"],
            "reviewer_id": review_receipt_value["reviewer_id"],
            "prior_exposure": review_receipt_value["prior_exposure"],
            "response_authorship": review_receipt_value["response_authorship"],
            "boundary": (
                "declared reviewer conditions persisted before review stimulus "
                "was emitted; declarations are not independent proof"
            ),
        },
        "human_review_observation": {
            "response_sha256": fixed_human_response_sha256,
            "answers": copy.deepcopy(human_response["answers"]),
            "operator_observation": copy.deepcopy(
                human_response["operator_observation"]
            ),
            "notes": human_response["notes"],
        },
        "review_provenance": copy.deepcopy(
            human_response["review_provenance"]
        ),
        "audit_reveal": {
            "receipt_sha256": audit_reveal_receipt_sha256,
            "review_start_receipt_sha256": review_start_receipt_sha256,
            "review_started_at": review_receipt_value["started_at"],
            "audit_material_sha256": material_digest,
            "revealed_at": receipt_value["revealed_at"],
            "boundary": (
                "machine-generated receipt persisted before audit/reference "
                "material was emitted"
            ),
        },
        "semantic_audit": {
            "audit_response_sha256": hashlib.sha256(audit_raw).hexdigest(),
            "findings": copy.deepcopy(audit_response["findings"]),
            "audit_provenance": copy.deepcopy(
                audit_response["audit_provenance"]
            ),
            "notes": audit_response["notes"],
            "distortion_key": copy.deepcopy(case["distortion_key"]),
            "reference_state": copy.deepcopy(fixtures[fixture_id]["reference_state"]),
            "post_interruption_evidence": copy.deepcopy(
                fixtures[fixture_id]["scenario"]["post_interruption_evidence"]
            ),
        },
        "evidence_boundaries": {
            "human_review_observation": (
                "reviewer response fixed before distortion key/reference material reveal"
            ),
            "semantic_audit": (
                "post-reveal audit; not part of the original reviewer response"
            ),
            "declared_provenance": (
                "opaque ids and authorship/exposure declarations are metadata, "
                "not independent proof of blinding or human authorship"
            ),
            "actual_long_gap_resumption": "not-established-by-this-artifact",
            "actual_team_handoff": "not-established-by-this-artifact",
            "product_value": "not-established-by-this-artifact",
            "stable_requirement_change": "not-authorized-by-this-artifact",
        },
        "interpretation_stoplines": [
            "review start, review observation, audit reveal, and semantic audit remain separate evidence layers",
            "review-start receipt fixes declared reviewer conditions before stimulus output",
            "audit-reveal receipt binds the fixed response before reference material is emitted",
            "probe content digest binds the review and audit to the exact evaluation stimulus",
            "no overall score, ranking, winner, or preferred condition is computed",
            "a completed synthetic distortion review is not actual long-gap resumption",
            "correction success alone does not establish SEI-specific value over raw chat or notes",
            "this artifact does not authorize Product Value or Stable Requirement changes",
        ],
    }


def _is_lower_hex(value: Any, length: int) -> bool:
    return (
        isinstance(value, str)
        and len(value) == length
        and all(character in "0123456789abcdef" for character in value)
    )


def validate_evidence_bundle(bundle: Any) -> None:
    required = {
        "schema",
        "status",
        "probe_id",
        "fixture_id",
        "probe_snapshot",
        "source_snapshot",
        "review_start",
        "human_review_observation",
        "review_provenance",
        "audit_reveal",
        "semantic_audit",
        "evidence_boundaries",
        "interpretation_stoplines",
    }
    if not isinstance(bundle, dict) or set(bundle) != required:
        raise SummaryDistortionEvidenceError(
            "E78.3 evidence bundle has invalid top-level shape"
        )
    if bundle["schema"] != EVIDENCE_SCHEMA:
        raise SummaryDistortionEvidenceError(
            f"E78.3 evidence schema must be {EVIDENCE_SCHEMA}"
        )
    if bundle["status"] != "evaluation-only":
        raise SummaryDistortionEvidenceError(
            "E78.3 evidence must remain evaluation-only"
        )
    for field in ("probe_id", "fixture_id"):
        if not isinstance(bundle[field], str) or not bundle[field].strip():
            raise SummaryDistortionEvidenceError(
                f"{field} must be a non-empty string"
            )

    probe_snapshot = bundle["probe_snapshot"]
    if not isinstance(probe_snapshot, dict) or set(probe_snapshot) != {
        "content_sha256",
        "distorted_summary",
        "distorted_next_question",
        "review_questions",
        "audit_dimensions",
    }:
        raise SummaryDistortionEvidenceError(
            "probe_snapshot has invalid shape"
        )
    if not _is_lower_hex(probe_snapshot["content_sha256"], 64):
        raise SummaryDistortionEvidenceError(
            "probe_snapshot content_sha256 must be SHA-256"
        )
    if (
        not isinstance(probe_snapshot["distorted_summary"], str)
        or not probe_snapshot["distorted_summary"].strip()
        or not isinstance(probe_snapshot["distorted_next_question"], str)
        or not probe_snapshot["distorted_next_question"].strip()
    ):
        raise SummaryDistortionEvidenceError(
            "probe_snapshot stimulus text must be non-empty"
        )
    questions = probe_snapshot["review_questions"]
    if (
        not isinstance(questions, list)
        or not questions
        or any(not isinstance(question, dict) for question in questions)
    ):
        raise SummaryDistortionEvidenceError(
            "probe_snapshot review_questions must be non-empty objects"
        )

    dimensions = probe_snapshot["audit_dimensions"]
    if not isinstance(dimensions, list) or not dimensions:
        raise SummaryDistortionEvidenceError(
            "probe_snapshot audit_dimensions must be non-empty"
        )
    dimension_contracts: dict[str, set[str]] = {}
    for dimension in dimensions:
        if not isinstance(dimension, dict) or set(dimension) != {
            "id",
            "value_kind",
            "allowed_values",
        }:
            raise SummaryDistortionEvidenceError(
                "audit dimension has invalid shape"
            )
        dimension_id = dimension["id"]
        allowed_values = dimension["allowed_values"]
        if (
            not isinstance(dimension_id, str)
            or not dimension_id.strip()
            or dimension_id in dimension_contracts
            or not isinstance(dimension["value_kind"], str)
            or not dimension["value_kind"].strip()
            or not isinstance(allowed_values, list)
            or not allowed_values
            or any(
                not isinstance(value, str) or not value.strip()
                for value in allowed_values
            )
            or len(allowed_values) != len(set(allowed_values))
            or "not-observed" not in allowed_values
        ):
            raise SummaryDistortionEvidenceError(
                "audit dimension contract is invalid"
            )
        dimension_contracts[dimension_id] = set(allowed_values)

    source_snapshot = bundle["source_snapshot"]
    if not isinstance(source_snapshot, dict) or set(source_snapshot) != {
        "path",
        "blob_sha1",
    }:
        raise SummaryDistortionEvidenceError(
            "source_snapshot has invalid shape"
        )
    source_path = source_snapshot["path"]
    if (
        not isinstance(source_path, str)
        or not source_path.strip()
        or Path(source_path).is_absolute()
        or ".." in Path(source_path).parts
        or not _is_lower_hex(source_snapshot["blob_sha1"], 40)
    ):
        raise SummaryDistortionEvidenceError(
            "source_snapshot path/blob binding is invalid"
        )

    review_start = bundle["review_start"]
    if not isinstance(review_start, dict) or set(review_start) != {
        "receipt_sha256",
        "started_at",
        "reviewer_id",
        "prior_exposure",
        "response_authorship",
        "boundary",
    }:
        raise SummaryDistortionEvidenceError("review_start has invalid shape")
    if not _is_lower_hex(review_start["receipt_sha256"], 64):
        raise SummaryDistortionEvidenceError(
            "review_start receipt_sha256 must be SHA-256"
        )
    review_started_at = _parse_timestamp(
        review_start["started_at"],
        "review_start.started_at",
    )
    if (
        not isinstance(review_start["reviewer_id"], str)
        or not review_start["reviewer_id"].strip()
        or review_start["prior_exposure"] not in PRIOR_EXPOSURE_VALUES
        or review_start["response_authorship"] not in RESPONSE_AUTHORSHIP_VALUES
        or not isinstance(review_start["boundary"], str)
        or not review_start["boundary"].strip()
    ):
        raise SummaryDistortionEvidenceError(
            "review_start provenance is invalid"
        )

    human = bundle["human_review_observation"]
    if not isinstance(human, dict) or set(human) != {
        "response_sha256",
        "answers",
        "operator_observation",
        "notes",
    }:
        raise SummaryDistortionEvidenceError(
            "human_review_observation has invalid shape"
        )
    if not _is_lower_hex(human["response_sha256"], 64):
        raise SummaryDistortionEvidenceError(
            "human response_sha256 must be SHA-256"
        )
    if (
        not isinstance(human["answers"], list)
        or not human["answers"]
        or any(
            not isinstance(answer, str) or not answer.strip()
            for answer in human["answers"]
        )
        or not isinstance(human["operator_observation"], dict)
        or not isinstance(human["notes"], str)
    ):
        raise SummaryDistortionEvidenceError(
            "human_review_observation content is invalid"
        )

    review_provenance = bundle["review_provenance"]
    if not isinstance(review_provenance, dict) or set(review_provenance) != {
        "reviewer_id",
        "prior_exposure",
        "response_authorship",
        "note",
    }:
        raise SummaryDistortionEvidenceError(
            "review_provenance has invalid shape"
        )
    for field in ("reviewer_id", "prior_exposure", "response_authorship"):
        if review_provenance[field] != review_start[field]:
            raise SummaryDistortionEvidenceError(
                f"review_provenance {field} differs from review_start"
            )
    if not isinstance(review_provenance["note"], str):
        raise SummaryDistortionEvidenceError(
            "review_provenance note must be a string"
        )

    reveal = bundle["audit_reveal"]
    if not isinstance(reveal, dict) or set(reveal) != {
        "receipt_sha256",
        "review_start_receipt_sha256",
        "review_started_at",
        "audit_material_sha256",
        "revealed_at",
        "boundary",
    }:
        raise SummaryDistortionEvidenceError(
            "audit_reveal has invalid shape"
        )
    for field in (
        "receipt_sha256",
        "review_start_receipt_sha256",
        "audit_material_sha256",
    ):
        if not _is_lower_hex(reveal[field], 64):
            raise SummaryDistortionEvidenceError(
                f"audit_reveal {field} must be SHA-256"
            )
    if reveal["review_start_receipt_sha256"] != review_start["receipt_sha256"]:
        raise SummaryDistortionEvidenceError(
            "audit_reveal review-start receipt binding mismatch"
        )
    if reveal["review_started_at"] != review_start["started_at"]:
        raise SummaryDistortionEvidenceError(
            "audit_reveal review_started_at mismatch"
        )
    revealed_at = _parse_timestamp(
        reveal["revealed_at"],
        "audit_reveal.revealed_at",
    )
    if revealed_at < review_started_at:
        raise SummaryDistortionEvidenceError(
            "audit reveal must not precede review start"
        )
    if (
        not isinstance(reveal["boundary"], str)
        or not reveal["boundary"].strip()
    ):
        raise SummaryDistortionEvidenceError(
            "audit_reveal boundary must be non-empty"
        )

    semantic = bundle["semantic_audit"]
    if not isinstance(semantic, dict) or set(semantic) != {
        "audit_response_sha256",
        "findings",
        "audit_provenance",
        "notes",
        "distortion_key",
        "reference_state",
        "post_interruption_evidence",
    }:
        raise SummaryDistortionEvidenceError(
            "semantic_audit has invalid shape"
        )
    if not _is_lower_hex(semantic["audit_response_sha256"], 64):
        raise SummaryDistortionEvidenceError(
            "semantic_audit audit_response_sha256 must be SHA-256"
        )
    findings = semantic["findings"]
    if not isinstance(findings, dict) or set(findings) != set(dimension_contracts):
        raise SummaryDistortionEvidenceError(
            "semantic_audit findings do not match audit dimensions"
        )
    for dimension_id, finding in findings.items():
        if finding not in dimension_contracts[dimension_id]:
            raise SummaryDistortionEvidenceError(
                f"semantic_audit finding {dimension_id} violates its contract"
            )
    audit_provenance = semantic["audit_provenance"]
    if not isinstance(audit_provenance, dict) or set(audit_provenance) != {
        "auditor_id",
        "response_authorship",
        "completed_at",
        "note",
    }:
        raise SummaryDistortionEvidenceError(
            "semantic audit provenance has invalid shape"
        )
    if (
        not isinstance(audit_provenance["auditor_id"], str)
        or not audit_provenance["auditor_id"].strip()
        or audit_provenance["response_authorship"] not in RESPONSE_AUTHORSHIP_VALUES
        or not isinstance(audit_provenance["note"], str)
        or not isinstance(semantic["notes"], str)
        or not isinstance(semantic["distortion_key"], list)
        or not isinstance(semantic["reference_state"], dict)
        or not isinstance(semantic["post_interruption_evidence"], list)
    ):
        raise SummaryDistortionEvidenceError(
            "semantic_audit content is invalid"
        )
    completed_at = _parse_timestamp(
        audit_provenance["completed_at"],
        "semantic_audit.completed_at",
    )
    if completed_at < revealed_at:
        raise SummaryDistortionEvidenceError(
            "semantic audit completion must not precede audit reveal"
        )

    boundaries = bundle["evidence_boundaries"]
    expected_boundary_values = {
        "actual_long_gap_resumption": "not-established-by-this-artifact",
        "actual_team_handoff": "not-established-by-this-artifact",
        "product_value": "not-established-by-this-artifact",
        "stable_requirement_change": "not-authorized-by-this-artifact",
    }
    expected_boundary_keys = {
        "human_review_observation",
        "semantic_audit",
        "declared_provenance",
        *expected_boundary_values,
    }
    if not isinstance(boundaries, dict) or set(boundaries) != expected_boundary_keys:
        raise SummaryDistortionEvidenceError(
            "evidence_boundaries have invalid shape"
        )
    for field in (
        "human_review_observation",
        "semantic_audit",
        "declared_provenance",
    ):
        if not isinstance(boundaries[field], str) or not boundaries[field].strip():
            raise SummaryDistortionEvidenceError(
                f"evidence boundary {field} must be non-empty"
            )
    for field, expected in expected_boundary_values.items():
        if boundaries[field] != expected:
            raise SummaryDistortionEvidenceError(
                f"evidence boundary {field} must remain {expected}"
            )
    stoplines = bundle["interpretation_stoplines"]
    if (
        not isinstance(stoplines, list)
        or not stoplines
        or any(not isinstance(line, str) or not line.strip() for line in stoplines)
        or not any("no overall score" in line for line in stoplines)
        or not any("does not authorize Product Value" in line for line in stoplines)
    ):
        raise SummaryDistortionEvidenceError(
            "interpretation stoplines are incomplete"
        )


def save_bundle(path: str | Path, bundle: dict[str, Any]) -> None:
    """Persist one validated E78.3 evidence artifact without replacing earlier evidence."""
    validate_evidence_bundle(bundle)
    target = Path(path)
    payload = json.dumps(bundle, ensure_ascii=False, indent=2) + "\n"
    try:
        with target.open("x", encoding="utf-8") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError as exc:
        raise SummaryDistortionEvidenceError(
            f"refusing to overwrite existing E78.3 evidence: {target}"
        ) from exc


def evidence_contract_summary(
    probe: dict[str, Any],
    fixtures: dict[str, dict[str, Any]],
    fixture_id: str,
) -> dict[str, Any]:
    """Return the post-reveal artifact contract without creating review artifacts."""
    validate_probe(probe)
    expected_fixture_ids = {
        case["fixture_id"] for case in probe["cases"]
    }
    if set(fixtures) != expected_fixture_ids:
        raise SummaryDistortionEvidenceError(
            "validated fixture set must match all probe cases exactly"
        )
    _case(probe, fixture_id)
    if fixture_id not in fixtures:
        raise SummaryDistortionEvidenceError(
            f"unknown fixture: {fixture_id}"
        )
    return {
        "valid": True,
        "probe_id": probe["probe_id"],
        "probe_schema": probe["schema"],
        "probe_sha256": probe_content_sha256(probe),
        "fixture_id": fixture_id,
        "source_fixture": {
            "path": _case(probe, fixture_id)["path"],
            "blob_sha1": _case(probe, fixture_id)["blob_sha1"],
        },
        "audit_response_schema": AUDIT_RESPONSE_SCHEMA,
        "evidence_schema": EVIDENCE_SCHEMA,
        "audit_dimensions": copy.deepcopy(probe["audit_dimensions"]),
        "compatibility": (
            "v1 evaluation artifacts only; pre-v1 review/audit artifacts are "
            "not accepted by the current contract"
        ),
        "evidence_boundary": copy.deepcopy(probe["evidence_boundary"]),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Record ISSUE-000078 E78.3 human-review and semantic-audit evidence "
            "without collapsing the two layers"
        )
    )
    parser.add_argument("--probe", required=True)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--fixture-id", required=True)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("preflight")
    template = sub.add_parser("audit-template")
    template.add_argument("--response", required=True)
    template.add_argument("--review-receipt", required=True)
    template.add_argument("--receipt", required=True)

    export = sub.add_parser("export-evidence")
    export.add_argument("--response", required=True)
    export.add_argument("--review-receipt", required=True)
    export.add_argument("--receipt", required=True)
    export.add_argument("--audit-response", required=True)
    export.add_argument("--output")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    probe = load_json(args.probe)
    try:
        fixtures = load_sources(probe, args.repo_root)
    except SummaryDistortionProbeError as exc:
        raise SummaryDistortionEvidenceError(str(exc)) from exc
    if args.fixture_id not in fixtures:
        raise SummaryDistortionEvidenceError(
            f"unknown fixture: {args.fixture_id}"
        )
    if args.command == "preflight":
        print(
            json.dumps(
                evidence_contract_summary(
                    probe,
                    fixtures,
                    args.fixture_id,
                ),
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    try:
        _, human_raw = load_human_response(args.response, probe)
    except SummaryDistortionProbeError as exc:
        raise SummaryDistortionEvidenceError(str(exc)) from exc
    fixed_human_response_sha256 = hashlib.sha256(human_raw).hexdigest()
    try:
        review_receipt_value, review_receipt_raw = load_review_start_receipt(
            args.review_receipt,
            probe,
            args.fixture_id,
        )
        validate_human_response_against_review_start(
            json.loads(human_raw.decode("utf-8")),
            probe,
            args.fixture_id,
            review_receipt_value,
            review_receipt_raw,
        )
    except SummaryDistortionProbeError as exc:
        raise SummaryDistortionEvidenceError(str(exc)) from exc
    material = build_audit_material(probe, fixtures, args.fixture_id)
    material_digest = audit_material_sha256(material)
    try:
        review_start_receipt_sha256 = hashlib.sha256(
            review_receipt_raw
        ).hexdigest()
        receipt_value, receipt_raw = load_audit_reveal_receipt(
            args.receipt,
            probe,
            args.fixture_id,
            fixed_human_response_sha256,
            review_start_receipt_sha256,
            review_receipt_value["started_at"],
            material_digest,
        )
    except SummaryDistortionProbeError as exc:
        raise SummaryDistortionEvidenceError(str(exc)) from exc
    audit_reveal_receipt_sha256 = hashlib.sha256(receipt_raw).hexdigest()

    if args.command == "audit-template":
        result = audit_response_template(
            probe,
            args.fixture_id,
            fixed_human_response_sha256,
            audit_reveal_receipt_sha256,
        )
    elif args.command == "export-evidence":
        result = build_evidence_bundle(
            probe,
            fixtures,
            args.fixture_id,
            args.response,
            args.review_receipt,
            args.receipt,
            args.audit_response,
        )
    else:
        raise AssertionError(f"unhandled command: {args.command}")

    if args.command == "export-evidence" and args.output:
        save_bundle(args.output, result)
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
