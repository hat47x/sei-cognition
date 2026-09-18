#!/usr/bin/env python3
"""Run stage-gated ISSUE-000078 closure/dormancy lifecycle review.

Lifecycle labels remain Product-local attention projections. Review packets hide
condition identifiers and intended trade-off framing. Reviewer provenance is
fixed before stimulus, the structured response is fixed before audit, and only
then are the condition mapping, full handling contracts, and audit key revealed.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
from typing import Any


SCHEMA = "sei.inquiry-continuity-lifecycle-probe/v1"
PACKET_SCHEMA = "sei.inquiry-continuity-lifecycle-packet/v1"
RESPONSE_SCHEMA = "sei.inquiry-continuity-lifecycle-response/v1"
REVIEW_START_RECEIPT_SCHEMA = (
    "sei.inquiry-continuity-lifecycle-review-start-receipt/v1"
)
AUDIT_RECEIPT_SCHEMA = (
    "sei.inquiry-continuity-lifecycle-audit-receipt/v1"
)
STAGES = (
    "active",
    "dormant",
    "closed_without_decision",
    "linked_later_decision",
)
CONDITIONS = {
    "A_always_open",
    "B_age_hidden",
    "C_explicit_attention_projection",
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
BURDEN_VALUES = {
    "low",
    "medium",
    "high",
    "not-observed",
}


class LifecycleProbeError(ValueError):
    pass


def load_json(path: str | Path) -> dict[str, Any]:
    try:
        value = json.loads(
            Path(path).read_text(encoding="utf-8")
        )
    except (OSError, json.JSONDecodeError) as exc:
        raise LifecycleProbeError(
            f"cannot load JSON: {path}"
        ) from exc
    if not isinstance(value, dict):
        raise LifecycleProbeError(
            f"JSON root must be an object: {path}"
        )
    return value


def probe_content_sha256(probe: dict[str, Any]) -> str:
    payload = json.dumps(
        probe,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(
            character in "0123456789abcdef"
            for character in value
        )
    )


def _parse_timestamp(
    value: Any,
    field: str,
) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise LifecycleProbeError(
            f"{field} must be a non-empty timestamp"
        )
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise LifecycleProbeError(
            f"{field} must be ISO-8601"
        ) from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise LifecycleProbeError(
            f"{field} must include a timezone offset"
        )
    return parsed.astimezone(timezone.utc)


def _canonical_sha256(value: Any) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _receipt_bytes(
    receipt: dict[str, Any],
) -> bytes:
    return (
        json.dumps(
            receipt,
            ensure_ascii=False,
            indent=2,
        )
        + "\n"
    ).encode("utf-8")


def _validate_value_raw_pair(
    value: dict[str, Any],
    raw: bytes,
    label: str,
) -> None:
    if not isinstance(raw, bytes) or not raw.strip():
        raise LifecycleProbeError(
            f"{label} raw bytes must not be empty"
        )
    try:
        decoded = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise LifecycleProbeError(
            f"{label} raw bytes must be UTF-8 JSON"
        ) from exc
    if decoded != value:
        raise LifecycleProbeError(
            f"{label} value/raw mismatch"
        )


def save_receipt(
    path: str | Path,
    receipt: dict[str, Any],
    label: str,
) -> None:
    target = Path(path)
    payload = _receipt_bytes(receipt)
    try:
        with target.open("xb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError as exc:
        raise LifecycleProbeError(
            f"refusing to overwrite existing {label}: {target}"
        ) from exc


def _validate_questions(
    questions: Any,
) -> list[dict[str, Any]]:
    if not isinstance(questions, list) or not questions:
        raise LifecycleProbeError(
            "human_review_questions are required"
        )
    ids: list[str] = []
    for question in questions:
        if (
            not isinstance(question, dict)
            or set(question) != {"id", "prompt"}
            or not isinstance(question["id"], str)
            or not question["id"].strip()
            or not isinstance(question["prompt"], str)
            or not question["prompt"].strip()
        ):
            raise LifecycleProbeError(
                "human review question has invalid shape"
            )
        ids.append(question["id"])
    if len(ids) != len(set(ids)):
        raise LifecycleProbeError(
            "human review question ids must be unique"
        )
    return questions


def _validate_rotations(
    probe: dict[str, Any],
) -> None:
    rotations = probe.get("assignment_rotations")
    if (
        not isinstance(rotations, dict)
        or set(rotations) != {"R1", "R2", "R3"}
    ):
        raise LifecycleProbeError(
            "assignment_rotations must contain R1/R2/R3"
        )
    positions = [
        set()
        for _ in range(len(CONDITIONS))
    ]
    for rotation, values in rotations.items():
        if (
            not isinstance(values, list)
            or len(values) != len(CONDITIONS)
            or set(values) != CONDITIONS
        ):
            raise LifecycleProbeError(
                f"{rotation} must present each condition exactly once"
            )
        for index, condition in enumerate(values):
            positions[index].add(condition)
    if any(values != CONDITIONS for values in positions):
        raise LifecycleProbeError(
            "each condition must occupy every presentation position "
            "across rotations"
        )


def validate_probe(
    probe: dict[str, Any],
) -> None:
    if probe.get("schema") != SCHEMA:
        raise LifecycleProbeError(
            f"schema must be {SCHEMA}"
        )
    if (
        probe.get("status") != "evaluation-only"
        or probe.get("issue") != "ISSUE-000078"
    ):
        raise LifecycleProbeError(
            "probe must remain evaluation-only for ISSUE-000078"
        )

    stopline = probe.get("semantic_stopline")
    if not isinstance(stopline, dict):
        raise LifecycleProbeError(
            "semantic_stopline must be an object"
        )
    if (
        stopline.get("attention_projection_is_canonical")
        is not False
    ):
        raise LifecycleProbeError(
            "attention projection must not be canonical"
        )
    if (
        stopline.get("universal_status_type")
        != "not-proposed"
    ):
        raise LifecycleProbeError(
            "Universal Inquiry status type must not be proposed"
        )

    rules = probe.get("presentation_rules")
    if not isinstance(rules, dict) or set(rules) != {
        "condition_identifiers_hidden_until_audit",
        "intended_tradeoff_hidden_until_audit",
        "response_fixed_before_audit",
        "audit_reveals_condition_mapping",
    }:
        raise LifecycleProbeError(
            "presentation_rules has invalid shape"
        )
    if any(
        rules[field] is not True
        for field in rules
    ):
        raise LifecycleProbeError(
            "all lifecycle presentation rules must remain enabled"
        )
    _validate_rotations(probe)

    scenario = probe.get("scenario")
    if (
        not isinstance(scenario, dict)
        or scenario.get("decision_present") is not False
    ):
        raise LifecycleProbeError(
            "base scenario must remain Decisionless"
        )

    snapshots = probe.get("lifecycle_snapshots")
    if (
        not isinstance(snapshots, list)
        or len(snapshots) != len(STAGES)
    ):
        raise LifecycleProbeError(
            "exactly four lifecycle snapshots are required"
        )
    if [
        item.get("stage")
        for item in snapshots
        if isinstance(item, dict)
    ] != list(STAGES):
        raise LifecycleProbeError(
            "lifecycle snapshots must follow "
            "active/dormant/closed/linked order"
        )
    for item in snapshots:
        if not isinstance(item, dict):
            raise LifecycleProbeError(
                "lifecycle snapshot must be an object"
            )
        stage = item["stage"]
        if item.get("canonical_decision_present") is not False:
            raise LifecycleProbeError(
                f"{stage} must not create a Decision "
                "on the original Inquiry"
            )
        if item.get("unresolved_preserved") is not True:
            raise LifecycleProbeError(
                f"{stage} must preserve unresolved meaning"
            )
        if (
            item.get("canonical_inquiry_meaning_rewritten")
            is not False
        ):
            raise LifecycleProbeError(
                f"{stage} must not rewrite canonical Inquiry meaning"
            )
    linked = snapshots[-1]
    if not linked.get("later_decision_ref"):
        raise LifecycleProbeError(
            "linked_later_decision requires a separate decision reference"
        )
    if (
        linked.get("historical_link_role")
        != "prior_unresolved_context"
    ):
        raise LifecycleProbeError(
            "later Decision link must remain prior unresolved context"
        )

    conditions = probe.get("handling_conditions")
    if (
        not isinstance(conditions, dict)
        or set(conditions) != CONDITIONS
    ):
        raise LifecycleProbeError(
            "probe must contain exactly A/B/C handling conditions"
        )
    for condition_id, condition in conditions.items():
        if not isinstance(condition, dict):
            raise LifecycleProbeError(
                f"{condition_id} handling must be an object"
            )
        if condition.get("canonical_authority") is not False:
            raise LifecycleProbeError(
                f"{condition_id} must not become canonical authority"
            )
        surface = condition.get("surface")
        if (
            not isinstance(surface, list)
            or not surface
            or any(
                not isinstance(line, str) or not line.strip()
                for line in surface
            )
        ):
            raise LifecycleProbeError(
                f"{condition_id} requires surface material"
            )
        if (
            not isinstance(
                condition.get("intended_tradeoff"),
                str,
            )
            or not condition["intended_tradeoff"].strip()
        ):
            raise LifecycleProbeError(
                f"{condition_id} requires intended_tradeoff"
            )
    if (
        conditions["C_explicit_attention_projection"].get(
            "automatic_transition"
        )
        is not False
    ):
        raise LifecycleProbeError(
            "explicit attention projection must remain human-controlled"
        )

    _validate_questions(
        probe.get("human_review_questions")
    )
    audit_key = probe.get("audit_key")
    if (
        not isinstance(audit_key, dict)
        or not audit_key.get("semantic_hard_failures")
        or not audit_key.get("product_failure_signals")
        or not audit_key.get("acceptable_outcomes")
    ):
        raise LifecycleProbeError(
            "audit_key semantic/product/acceptable material is required"
        )
    boundary = probe.get("evidence_boundary")
    if (
        not isinstance(boundary, list)
        or not boundary
        or any(
            not isinstance(line, str) or not line.strip()
            for line in boundary
        )
    ):
        raise LifecycleProbeError(
            "evidence_boundary must be a non-empty string list"
        )


def _rotation(
    probe: dict[str, Any],
    rotation: str,
) -> list[str]:
    try:
        return probe["assignment_rotations"][rotation]
    except KeyError as exc:
        raise LifecycleProbeError(
            f"unknown rotation: {rotation}"
        ) from exc


def _presentation_id(
    rotation: str,
    index: int,
) -> str:
    return f"{rotation}-P{index + 1}"


def build_review_start_receipt(
    probe: dict[str, Any],
    rotation: str,
    reviewer_id: str,
    prior_exposure: str,
    response_authorship: str,
    started_at: str,
) -> dict[str, Any]:
    validate_probe(probe)
    _rotation(probe, rotation)
    if (
        not isinstance(reviewer_id, str)
        or not reviewer_id.strip()
    ):
        raise LifecycleProbeError(
            "reviewer_id must be a non-empty opaque id"
        )
    if prior_exposure not in PRIOR_EXPOSURE_VALUES:
        raise LifecycleProbeError(
            "prior_exposure has invalid value"
        )
    if response_authorship not in RESPONSE_AUTHORSHIP_VALUES:
        raise LifecycleProbeError(
            "response_authorship must be human-direct or human-transcribed"
        )
    _parse_timestamp(started_at, "started_at")
    return {
        "schema": REVIEW_START_RECEIPT_SCHEMA,
        "status": "evaluation-only",
        "probe_id": probe["probe_id"],
        "probe_sha256": probe_content_sha256(probe),
        "rotation": rotation,
        "reviewer_id": reviewer_id,
        "prior_exposure": prior_exposure,
        "response_authorship": response_authorship,
        "started_at": started_at,
    }


def validate_review_start_receipt(
    value: Any,
    probe: dict[str, Any],
    rotation: str,
) -> None:
    required = {
        "schema",
        "status",
        "probe_id",
        "probe_sha256",
        "rotation",
        "reviewer_id",
        "prior_exposure",
        "response_authorship",
        "started_at",
    }
    if not isinstance(value, dict) or set(value) != required:
        raise LifecycleProbeError(
            "review-start receipt has invalid shape"
        )
    if value["schema"] != REVIEW_START_RECEIPT_SCHEMA:
        raise LifecycleProbeError(
            "review-start receipt schema mismatch"
        )
    if (
        value["status"] != "evaluation-only"
        or value["probe_id"] != probe["probe_id"]
        or value["probe_sha256"] != probe_content_sha256(probe)
        or value["rotation"] != rotation
    ):
        raise LifecycleProbeError(
            "review-start receipt probe/rotation binding mismatch"
        )
    if (
        not isinstance(value["reviewer_id"], str)
        or not value["reviewer_id"].strip()
        or value["prior_exposure"]
        not in PRIOR_EXPOSURE_VALUES
        or value["response_authorship"]
        not in RESPONSE_AUTHORSHIP_VALUES
    ):
        raise LifecycleProbeError(
            "review-start receipt provenance is invalid"
        )
    _parse_timestamp(value["started_at"], "started_at")


def load_review_start_receipt(
    path: str | Path,
    probe: dict[str, Any],
    rotation: str,
) -> tuple[dict[str, Any], bytes]:
    try:
        raw = Path(path).read_bytes()
    except OSError as exc:
        raise LifecycleProbeError(
            f"cannot load review-start receipt: {path}"
        ) from exc
    if not raw.strip():
        raise LifecycleProbeError(
            "review-start receipt must not be empty"
        )
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise LifecycleProbeError(
            "review-start receipt must be UTF-8 JSON"
        ) from exc
    validate_review_start_receipt(
        value,
        probe,
        rotation,
    )
    _validate_value_raw_pair(
        value,
        raw,
        "review-start receipt",
    )
    return value, raw


def build_review_packets(
    probe: dict[str, Any],
    rotation: str,
    review_start_receipt_sha256: str,
) -> list[dict[str, Any]]:
    validate_probe(probe)
    if not _is_sha256(review_start_receipt_sha256):
        raise LifecycleProbeError(
            "review packet requires review-start receipt SHA-256"
        )
    packets: list[dict[str, Any]] = []
    for index, condition_id in enumerate(
        _rotation(probe, rotation)
    ):
        condition = probe["handling_conditions"][condition_id]
        packets.append(
            {
                "schema": PACKET_SCHEMA,
                "status": "evaluation-only",
                "probe_id": probe["probe_id"],
                "probe_sha256": probe_content_sha256(probe),
                "presentation_id": _presentation_id(
                    rotation,
                    index,
                ),
                "stage": "review",
                "review_start_receipt_sha256": (
                    review_start_receipt_sha256
                ),
                "scenario": probe["scenario"],
                "lifecycle_snapshots": probe[
                    "lifecycle_snapshots"
                ],
                "handling_surface": copy_surface(
                    condition["surface"]
                ),
                "questions": probe["human_review_questions"],
                "semantic_stopline": probe[
                    "semantic_stopline"
                ],
            }
        )
    return packets


def copy_surface(
    value: list[str],
) -> list[str]:
    return list(value)


def response_template(
    probe: dict[str, Any],
    rotation: str,
    review_start_receipt_sha256: str,
) -> dict[str, Any]:
    validate_probe(probe)
    if not _is_sha256(review_start_receipt_sha256):
        raise LifecycleProbeError(
            "response requires review-start receipt SHA-256"
        )
    question_ids = [
        item["id"]
        for item in probe["human_review_questions"]
    ]
    return {
        "schema": RESPONSE_SCHEMA,
        "probe_sha256": probe_content_sha256(probe),
        "rotation": rotation,
        "review_start_receipt_sha256": (
            review_start_receipt_sha256
        ),
        "entries": [
            {
                "presentation_id": _presentation_id(
                    rotation,
                    index,
                ),
                "answers": {
                    question_id: ""
                    for question_id in question_ids
                },
                "operator_observation": {
                    "completion_seconds": "not-observed",
                    "attention_load": "not-observed",
                },
                "notes": "",
            }
            for index, _ in enumerate(
                _rotation(probe, rotation)
            )
        ],
        "notes": "",
    }


def _validate_nonnegative_or_not_observed(
    value: Any,
    field: str,
) -> None:
    if value == "not-observed":
        return
    if (
        not isinstance(value, (int, float))
        or isinstance(value, bool)
        or value < 0
    ):
        raise LifecycleProbeError(
            f"{field} must be nonnegative or not-observed"
        )


def validate_response(
    value: Any,
    probe: dict[str, Any],
    rotation: str,
    review_start_receipt_sha256: str,
) -> None:
    validate_probe(probe)
    required = {
        "schema",
        "probe_sha256",
        "rotation",
        "review_start_receipt_sha256",
        "entries",
        "notes",
    }
    if not isinstance(value, dict) or set(value) != required:
        raise LifecycleProbeError(
            "lifecycle response has invalid top-level shape"
        )
    if value["schema"] != RESPONSE_SCHEMA:
        raise LifecycleProbeError(
            f"response schema must be {RESPONSE_SCHEMA}"
        )
    if (
        value["probe_sha256"] != probe_content_sha256(probe)
        or value["rotation"] != rotation
        or value["review_start_receipt_sha256"]
        != review_start_receipt_sha256
    ):
        raise LifecycleProbeError(
            "lifecycle response binding mismatch"
        )
    if not isinstance(value["notes"], str):
        raise LifecycleProbeError(
            "lifecycle response notes must be a string"
        )
    entries = value["entries"]
    rotation_values = _rotation(probe, rotation)
    if (
        not isinstance(entries, list)
        or len(entries) != len(rotation_values)
    ):
        raise LifecycleProbeError(
            "lifecycle response requires one entry per presentation"
        )
    question_ids = [
        item["id"]
        for item in probe["human_review_questions"]
    ]
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict) or set(entry) != {
            "presentation_id",
            "answers",
            "operator_observation",
            "notes",
        }:
            raise LifecycleProbeError(
                "lifecycle response entry has invalid shape"
            )
        if entry["presentation_id"] != _presentation_id(
            rotation,
            index,
        ):
            raise LifecycleProbeError(
                "lifecycle response presentation order mismatch"
            )
        answers = entry["answers"]
        if (
            not isinstance(answers, dict)
            or list(answers) != question_ids
            or any(
                not isinstance(answer, str)
                or not answer.strip()
                for answer in answers.values()
            )
        ):
            raise LifecycleProbeError(
                "lifecycle response requires one non-empty "
                "answer per question"
            )
        observation = entry["operator_observation"]
        if not isinstance(observation, dict) or set(observation) != {
            "completion_seconds",
            "attention_load",
        }:
            raise LifecycleProbeError(
                "lifecycle operator observation has invalid shape"
            )
        _validate_nonnegative_or_not_observed(
            observation["completion_seconds"],
            "completion_seconds",
        )
        if observation["attention_load"] not in BURDEN_VALUES:
            raise LifecycleProbeError(
                "attention_load has invalid value"
            )
        if not isinstance(entry["notes"], str):
            raise LifecycleProbeError(
                "lifecycle response entry notes must be a string"
            )


def load_response(
    path: str | Path,
    probe: dict[str, Any],
    rotation: str,
    review_start_receipt_sha256: str,
) -> tuple[dict[str, Any], bytes]:
    try:
        raw = Path(path).read_bytes()
    except OSError as exc:
        raise LifecycleProbeError(
            f"cannot load lifecycle response: {path}"
        ) from exc
    if not raw.strip():
        raise LifecycleProbeError(
            "lifecycle response must not be empty"
        )
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise LifecycleProbeError(
            "lifecycle response must be UTF-8 JSON"
        ) from exc
    validate_response(
        value,
        probe,
        rotation,
        review_start_receipt_sha256,
    )
    return value, raw


def _audit_material(
    probe: dict[str, Any],
    rotation: str,
) -> dict[str, Any]:
    return {
        "condition_mapping": [
            {
                "presentation_id": _presentation_id(
                    rotation,
                    index,
                ),
                "condition": condition_id,
                "handling_contract": probe[
                    "handling_conditions"
                ][condition_id],
            }
            for index, condition_id in enumerate(
                _rotation(probe, rotation)
            )
        ],
        "audit_key": probe["audit_key"],
        "evidence_boundary": probe["evidence_boundary"],
        "semantic_stopline": probe["semantic_stopline"],
    }


def build_audit_receipt(
    probe: dict[str, Any],
    rotation: str,
    review_start_receipt_value: dict[str, Any],
    review_start_receipt_raw: bytes,
    response_path: str | Path,
    revealed_at: str,
) -> dict[str, Any]:
    validate_review_start_receipt(
        review_start_receipt_value,
        probe,
        rotation,
    )
    _validate_value_raw_pair(
        review_start_receipt_value,
        review_start_receipt_raw,
        "review-start receipt",
    )
    review_start_receipt_sha256 = hashlib.sha256(
        review_start_receipt_raw
    ).hexdigest()
    _, response_raw = load_response(
        response_path,
        probe,
        rotation,
        review_start_receipt_sha256,
    )
    started_at = review_start_receipt_value["started_at"]
    if _parse_timestamp(
        revealed_at,
        "revealed_at",
    ) < _parse_timestamp(
        started_at,
        "review_started_at",
    ):
        raise LifecycleProbeError(
            "audit reveal must not precede review start"
        )
    return {
        "schema": AUDIT_RECEIPT_SCHEMA,
        "status": "evaluation-only",
        "probe_id": probe["probe_id"],
        "probe_sha256": probe_content_sha256(probe),
        "rotation": rotation,
        "review_start_receipt_sha256": (
            review_start_receipt_sha256
        ),
        "review_started_at": started_at,
        "fixed_response_sha256": hashlib.sha256(
            response_raw
        ).hexdigest(),
        "audit_material_sha256": _canonical_sha256(
            _audit_material(
                probe,
                rotation,
            )
        ),
        "revealed_at": revealed_at,
    }


def validate_audit_receipt(
    value: Any,
    probe: dict[str, Any],
    rotation: str,
    review_start_receipt_value: dict[str, Any],
    review_start_receipt_raw: bytes,
    response_path: str | Path,
) -> None:
    validate_review_start_receipt(
        review_start_receipt_value,
        probe,
        rotation,
    )
    _validate_value_raw_pair(
        review_start_receipt_value,
        review_start_receipt_raw,
        "review-start receipt",
    )
    review_start_receipt_sha256 = hashlib.sha256(
        review_start_receipt_raw
    ).hexdigest()
    required = {
        "schema",
        "status",
        "probe_id",
        "probe_sha256",
        "rotation",
        "review_start_receipt_sha256",
        "review_started_at",
        "fixed_response_sha256",
        "audit_material_sha256",
        "revealed_at",
    }
    if not isinstance(value, dict) or set(value) != required:
        raise LifecycleProbeError(
            "audit receipt has invalid shape"
        )
    if value["schema"] != AUDIT_RECEIPT_SCHEMA:
        raise LifecycleProbeError(
            "audit receipt schema mismatch"
        )
    if (
        value["status"] != "evaluation-only"
        or value["probe_id"] != probe["probe_id"]
        or value["probe_sha256"] != probe_content_sha256(probe)
        or value["rotation"] != rotation
        or value["review_start_receipt_sha256"]
        != review_start_receipt_sha256
        or value["review_started_at"]
        != review_start_receipt_value["started_at"]
    ):
        raise LifecycleProbeError(
            "audit receipt binding mismatch"
        )
    _, response_raw = load_response(
        response_path,
        probe,
        rotation,
        review_start_receipt_sha256,
    )
    if (
        value["fixed_response_sha256"]
        != hashlib.sha256(response_raw).hexdigest()
    ):
        raise LifecycleProbeError(
            "audit receipt is bound to a different response"
        )
    if (
        value["audit_material_sha256"]
        != _canonical_sha256(
            _audit_material(
                probe,
                rotation,
            )
        )
    ):
        raise LifecycleProbeError(
            "audit receipt is bound to different audit material"
        )
    if _parse_timestamp(
        value["revealed_at"],
        "revealed_at",
    ) < _parse_timestamp(
        value["review_started_at"],
        "review_started_at",
    ):
        raise LifecycleProbeError(
            "audit reveal must not precede review start"
        )


def build_audit_packet(
    probe: dict[str, Any],
    rotation: str,
    review_start_receipt_value: dict[str, Any],
    review_start_receipt_raw: bytes,
    response_path: str | Path,
    receipt_value: dict[str, Any],
    receipt_raw: bytes,
) -> dict[str, Any]:
    validate_audit_receipt(
        receipt_value,
        probe,
        rotation,
        review_start_receipt_value,
        review_start_receipt_raw,
        response_path,
    )
    review_start_receipt_sha256 = hashlib.sha256(
        review_start_receipt_raw
    ).hexdigest()
    try:
        decoded = json.loads(receipt_raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise LifecycleProbeError(
            "audit receipt raw bytes must be UTF-8 JSON"
        ) from exc
    if decoded != receipt_value:
        raise LifecycleProbeError(
            "audit receipt value/raw mismatch"
        )
    return {
        "schema": PACKET_SCHEMA,
        "status": "evaluation-only",
        "probe_id": probe["probe_id"],
        "probe_sha256": probe_content_sha256(probe),
        "stage": "audit",
        "review_start_receipt_sha256": (
            review_start_receipt_sha256
        ),
        "audit_receipt_sha256": hashlib.sha256(
            receipt_raw
        ).hexdigest(),
        "fixed_response_sha256": receipt_value[
            "fixed_response_sha256"
        ],
        "audit_material_sha256": receipt_value[
            "audit_material_sha256"
        ],
        **_audit_material(probe, rotation),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run ISSUE-000078 closure/dormancy "
            "condition-blinded review"
        ),
        allow_abbrev=False,
    )
    parser.add_argument("--probe", required=True)
    parser.add_argument("--rotation")
    sub = parser.add_subparsers(
        dest="command",
        required=True,
    )

    sub.add_parser("validate")

    review = sub.add_parser("review")
    review.add_argument("--receipt-output", required=True)
    review.add_argument("--reviewer-id", required=True)
    review.add_argument(
        "--prior-exposure",
        choices=sorted(PRIOR_EXPOSURE_VALUES),
        required=True,
    )
    review.add_argument(
        "--response-authorship",
        choices=sorted(RESPONSE_AUTHORSHIP_VALUES),
        required=True,
    )
    review.add_argument("--started-at", required=True)

    template = sub.add_parser("response-template")
    template.add_argument(
        "--review-start-receipt",
        required=True,
    )

    audit = sub.add_parser("audit")
    audit.add_argument(
        "--review-start-receipt",
        required=True,
    )
    audit.add_argument("--response", required=True)
    audit.add_argument("--receipt-output", required=True)
    audit.add_argument("--revealed-at", required=True)
    return parser


def main(
    argv: list[str] | None = None,
) -> int:
    args = build_parser().parse_args(argv)
    probe = load_json(args.probe)
    validate_probe(probe)

    if args.command == "validate":
        print(
            json.dumps(
                {
                    "valid": True,
                    "probe_id": probe["probe_id"],
                    "probe_schema": probe["schema"],
                    "probe_sha256": probe_content_sha256(probe),
                    "packet_schema": PACKET_SCHEMA,
                    "response_schema": RESPONSE_SCHEMA,
                    "review_start_receipt_schema": (
                        REVIEW_START_RECEIPT_SCHEMA
                    ),
                    "audit_receipt_schema": (
                        AUDIT_RECEIPT_SCHEMA
                    ),
                    "rotations": sorted(
                        probe["assignment_rotations"]
                    ),
                    "condition_identifiers_hidden_until_audit": True,
                    "universal_status_type": "not-proposed",
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    if not args.rotation:
        raise LifecycleProbeError(
            "--rotation is required for review execution"
        )

    if args.command == "review":
        receipt = build_review_start_receipt(
            probe,
            args.rotation,
            args.reviewer_id,
            args.prior_exposure,
            args.response_authorship,
            args.started_at,
        )
        receipt_raw = _receipt_bytes(receipt)
        receipt_sha = hashlib.sha256(
            receipt_raw
        ).hexdigest()
        payload: Any = build_review_packets(
            probe,
            args.rotation,
            receipt_sha,
        )
        save_receipt(
            args.receipt_output,
            receipt,
            "review-start receipt",
        )
    elif args.command == "response-template":
        _, receipt_raw = load_review_start_receipt(
            args.review_start_receipt,
            probe,
            args.rotation,
        )
        payload = response_template(
            probe,
            args.rotation,
            hashlib.sha256(
                receipt_raw
            ).hexdigest(),
        )
    elif args.command == "audit":
        review_value, review_raw = load_review_start_receipt(
            args.review_start_receipt,
            probe,
            args.rotation,
        )
        review_sha = hashlib.sha256(
            review_raw
        ).hexdigest()
        receipt = build_audit_receipt(
            probe,
            args.rotation,
            review_value,
            review_raw,
            args.response,
            args.revealed_at,
        )
        receipt_raw = _receipt_bytes(receipt)
        payload = build_audit_packet(
            probe,
            args.rotation,
            review_value,
            review_raw,
            args.response,
            receipt,
            receipt_raw,
        )
        save_receipt(
            args.receipt_output,
            receipt,
            "audit receipt",
        )
    else:
        raise AssertionError(
            f"unhandled command: {args.command}"
        )

    print(
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
