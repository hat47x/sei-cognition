#!/usr/bin/env python3
"""Evaluation-only sidecar records for Personal Inquiry Continuity dogfooding.

This module records observations about a dogfood session. It intentionally does
not modify or interpret canonical inquiry state.
"""

from __future__ import annotations

import copy
import json
from datetime import datetime
from pathlib import Path
from typing import Any

SCHEMA = "sei.personal-inquiry-continuity-evaluation/v0"
PROFILES = {"B0-chat-only", "B1-final-note", "P1-sei"}
SURFACES = {
    "chat-only",
    "final-note",
    "generic-summary",
    "sei-orientation",
    "sei-quiet",
    "sei-proactive",
}
TRISTATE = {"pass", "fail", "not-applicable", "not-observed"}
ATTENTION_LOAD = {"low", "medium", "high", "not-observed"}
EVIDENCE_ROLES = {"calibration", "resumption", "not-observed"}
CONTEXT_GAPS = {
    "same-session",
    "same-day",
    "multi-day",
    "multi-week",
    "not-observed",
}


class EvaluationRecordError(ValueError):
    pass


def parse_time(value: str) -> datetime:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, TypeError, ValueError) as exc:
        raise EvaluationRecordError(f"invalid timestamp: {value!r}") from exc


def new_evaluation(
    case_id: str,
    inquiry_ref: str,
    profile: str,
    created_at: str,
) -> dict[str, Any]:
    if not case_id.strip():
        raise EvaluationRecordError("case_id must not be empty")
    if not inquiry_ref.strip():
        raise EvaluationRecordError("inquiry_ref must not be empty")
    if profile not in PROFILES:
        raise EvaluationRecordError(f"invalid profile: {profile!r}")
    parse_time(created_at)
    return {
        "schema": SCHEMA,
        "status": "evaluation-only",
        "case_id": case_id.strip(),
        "inquiry_ref": inquiry_ref.strip(),
        "profile": profile,
        "created_at": created_at,
        "capture_observations": [],
        "resume_observations": [],
    }


def _require_nonnegative_int(item: dict[str, Any], field: str) -> None:
    value = item.get(field, 0)
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise EvaluationRecordError(f"{field} must be a non-negative integer")


def _validate_tri(item: dict[str, Any], field: str) -> None:
    value = item.get(field, "not-observed")
    if value not in TRISTATE:
        raise EvaluationRecordError(f"{field} has invalid value: {value!r}")


def validate_evaluation(record: dict[str, Any]) -> None:
    if record.get("schema") != SCHEMA:
        raise EvaluationRecordError(f"schema must be {SCHEMA}")
    if record.get("status") != "evaluation-only":
        raise EvaluationRecordError("status must remain evaluation-only")
    if record.get("profile") not in PROFILES:
        raise EvaluationRecordError(f"invalid profile: {record.get('profile')!r}")
    if not record.get("case_id") or not record.get("inquiry_ref") or not record.get("created_at"):
        raise EvaluationRecordError("case_id, inquiry_ref, and created_at are required")
    parse_time(record["created_at"])

    ids: set[str] = set()
    for section in ("capture_observations", "resume_observations"):
        items = record.get(section, [])
        if not isinstance(items, list):
            raise EvaluationRecordError(f"{section} must be a list")
        for item in items:
            item_id = item.get("id")
            if not isinstance(item_id, str) or not item_id:
                raise EvaluationRecordError(f"{section} item requires non-empty id")
            if item_id in ids:
                raise EvaluationRecordError(f"duplicate observation id: {item_id}")
            ids.add(item_id)
            if not item.get("observed_at"):
                raise EvaluationRecordError(f"{item_id} requires observed_at")
            parse_time(item["observed_at"])

    for item in record.get("capture_observations", []):
        _require_nonnegative_int(item, "semantic_corrections")
        if item.get("burden") not in ATTENTION_LOAD:
            raise EvaluationRecordError(
                f"capture burden has invalid value: {item.get('burden')!r}"
            )

    for item in record.get("resume_observations", []):
        if item.get("surface") not in SURFACES:
            raise EvaluationRecordError(f"invalid surface: {item.get('surface')!r}")
        if item.get("evidence_role", "not-observed") not in EVIDENCE_ROLES:
            raise EvaluationRecordError(
                f"invalid evidence_role: {item.get('evidence_role')!r}"
            )
        if item.get("context_gap", "not-observed") not in CONTEXT_GAPS:
            raise EvaluationRecordError(
                f"invalid context_gap: {item.get('context_gap')!r}"
            )
        for field in ("source_reopens", "chat_reopens", "detail_descents"):
            _require_nonnegative_int(item, field)
        for field in (
            "original_concern_retention",
            "unresolved_preservation",
            "temporal_integrity",
            "recommendation_decision_integrity",
            "suggestion_attribution_integrity",
            "material_change_visibility",
        ):
            _validate_tri(item, field)
        if item.get("attention_load") not in ATTENTION_LOAD:
            raise EvaluationRecordError(
                f"attention_load has invalid value: {item.get('attention_load')!r}"
            )
        if not isinstance(item.get("false_continuity", False), bool):
            raise EvaluationRecordError("false_continuity must be boolean")


def add_capture_observation(
    record: dict[str, Any], observation: dict[str, Any]
) -> dict[str, Any]:
    updated = copy.deepcopy(record)
    item = copy.deepcopy(observation)
    item.setdefault("semantic_corrections", 0)
    item.setdefault("burden", "not-observed")
    updated["capture_observations"].append(item)
    validate_evaluation(updated)
    return updated


def add_resume_observation(
    record: dict[str, Any], observation: dict[str, Any]
) -> dict[str, Any]:
    updated = copy.deepcopy(record)
    item = copy.deepcopy(observation)
    item.setdefault("evidence_role", "not-observed")
    item.setdefault("context_gap", "not-observed")
    item.setdefault("source_reopens", 0)
    item.setdefault("chat_reopens", 0)
    item.setdefault("detail_descents", 0)
    item.setdefault("false_continuity", False)
    item.setdefault("attention_load", "not-observed")
    for field in (
        "original_concern_retention",
        "unresolved_preservation",
        "temporal_integrity",
        "recommendation_decision_integrity",
        "suggestion_attribution_integrity",
        "material_change_visibility",
    ):
        item.setdefault(field, "not-observed")
    updated["resume_observations"].append(item)
    validate_evaluation(updated)
    return updated


def _empty_surface_summary() -> dict[str, Any]:
    return {
        "attempts": 0,
        "context_gap_counts": {},
        "source_reopens": 0,
        "chat_reopens": 0,
        "detail_descents": 0,
        "false_continuity_count": 0,
        "historical_integrity_failures": 0,
        "original_concern_loss_count": 0,
    }


def comparison_projection(record: dict[str, Any]) -> dict[str, Any]:
    """Return a non-scored comparison view without mixing evidence heights."""
    validate_evaluation(record)
    by_evidence_role: dict[str, dict[str, dict[str, Any]]] = {}
    for item in record["resume_observations"]:
        evidence_role = item.get("evidence_role", "not-observed")
        surface = item["surface"]
        role_group = by_evidence_role.setdefault(evidence_role, {})
        summary = role_group.setdefault(surface, _empty_surface_summary())
        summary["attempts"] += 1
        context_gap = item.get("context_gap", "not-observed")
        summary["context_gap_counts"][context_gap] = (
            summary["context_gap_counts"].get(context_gap, 0) + 1
        )
        summary["source_reopens"] += item["source_reopens"]
        summary["chat_reopens"] += item["chat_reopens"]
        summary["detail_descents"] += item["detail_descents"]
        summary["false_continuity_count"] += int(item["false_continuity"])
        summary["historical_integrity_failures"] += int(
            item["temporal_integrity"] == "fail"
            or item["recommendation_decision_integrity"] == "fail"
        )
        summary["original_concern_loss_count"] += int(
            item["original_concern_retention"] == "fail"
        )
    return {
        "projection": "sei-personal-inquiry-evaluation-comparison/v0",
        "case_id": record["case_id"],
        "profile": record["profile"],
        "by_evidence_role": by_evidence_role,
        "notes": [
            "calibration and resumption observations are never aggregated together",
            "context gap remains visible inside each surface summary",
            "no aggregate winner or score is computed",
            "short-cycle calibration is not long-gap resumption evidence",
            "quiet-first and proactive-first are both falsifiable hypotheses",
        ],
    }


def save_evaluation(path: str | Path, record: dict[str, Any]) -> None:
    validate_evaluation(record)
    Path(path).write_text(
        json.dumps(record, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def load_evaluation(path: str | Path) -> dict[str, Any]:
    record = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_evaluation(record)
    return record
