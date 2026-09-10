#!/usr/bin/env python3
"""Evaluation-only Personal Inquiry Continuity dogfood core.

This module exercises a local Source / Meaning / Resume slice. It is not a
Universal SOZA Contract, a supported production storage format, or a workflow
state machine.
"""

from __future__ import annotations

import copy
import json
from datetime import datetime
from pathlib import Path
from typing import Any

SCHEMA = "soza.personal-inquiry-continuity-dogfood/v0"
RECORD_KINDS = {"observation", "unknown", "conflict", "hypothesis", "recommendation"}


class DogfoodStateError(ValueError):
    pass


def parse_time(value: str) -> datetime:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise DogfoodStateError(f"invalid timestamp: {value!r}") from exc


def new_state(question: str, created_at: str) -> dict[str, Any]:
    if not question.strip():
        raise DogfoodStateError("question must not be empty")
    parse_time(created_at)
    return {
        "schema": SCHEMA,
        "status": "evaluation-only",
        "inquiry": {
            "id": "inquiry",
            "question": question.strip(),
            "created_at": created_at,
        },
        "sources": [],
        "records": [],
        "decisions": [],
        "reviews": [],
    }


def load_state(path: str | Path) -> dict[str, Any]:
    state = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_state(state)
    return state


def save_state(path: str | Path, state: dict[str, Any]) -> None:
    validate_state(state)
    Path(path).write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _all_ids(state: dict[str, Any]) -> set[str]:
    ids: set[str] = set()
    for section in ("sources", "records", "decisions", "reviews"):
        for item in state.get(section, []):
            item_id = item.get("id")
            if not isinstance(item_id, str) or not item_id:
                raise DogfoodStateError(f"{section} item requires non-empty id")
            if item_id in ids:
                raise DogfoodStateError(f"duplicate id: {item_id}")
            ids.add(item_id)
    return ids


def _record_map(state: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {item["id"]: item for item in state.get("records", [])}


def validate_state(state: dict[str, Any]) -> None:
    if state.get("schema") != SCHEMA:
        raise DogfoodStateError(f"schema must be {SCHEMA}")
    if state.get("status") != "evaluation-only":
        raise DogfoodStateError("status must remain evaluation-only")

    inquiry = state.get("inquiry")
    if not isinstance(inquiry, dict) or not inquiry.get("question"):
        raise DogfoodStateError("inquiry.question is required")
    parse_time(inquiry.get("created_at"))

    _all_ids(state)
    source_ids = {item["id"] for item in state.get("sources", [])}
    records = _record_map(state)

    for source in state.get("sources", []):
        if not source.get("locator"):
            raise DogfoodStateError(f"source {source['id']} requires locator")
        parse_time(source.get("captured_at"))

    for record in state.get("records", []):
        kind = record.get("kind")
        if kind not in RECORD_KINDS:
            raise DogfoodStateError(f"record {record['id']} has invalid kind: {kind!r}")
        if not record.get("summary"):
            raise DogfoodStateError(f"record {record['id']} requires summary")
        parse_time(record.get("captured_at"))
        subject_at = record.get("subject_at")
        if subject_at is not None:
            parse_time(subject_at)
        for source_ref in record.get("source_refs", []):
            if source_ref not in source_ids:
                raise DogfoodStateError(
                    f"record {record['id']} has unknown source ref: {source_ref}"
                )
        if kind in {"unknown", "conflict"}:
            status = record.get("status", "open")
            if status not in {"open", "resolved"}:
                raise DogfoodStateError(
                    f"record {record['id']} has invalid unresolved status: {status!r}"
                )

    unresolved_ids = {
        record_id
        for record_id, record in records.items()
        if record["kind"] in {"unknown", "conflict"}
    }

    for decision in state.get("decisions", []):
        if not decision.get("statement"):
            raise DogfoodStateError(f"decision {decision['id']} requires statement")
        decision_time = parse_time(decision.get("decided_at"))
        for ref in decision.get("basis_refs", []):
            if ref not in records:
                raise DogfoodStateError(
                    f"decision {decision['id']} has unknown basis ref: {ref}"
                )
            if parse_time(records[ref]["captured_at"]) > decision_time:
                raise DogfoodStateError(
                    f"decision {decision['id']} cannot use later-captured record {ref} "
                    "as historical basis"
                )
        for ref in decision.get("unresolved_refs", []):
            if ref not in unresolved_ids:
                raise DogfoodStateError(
                    f"decision {decision['id']} unresolved ref must point to unknown/conflict: {ref}"
                )

    for review in state.get("reviews", []):
        parse_time(review.get("reviewed_at"))


def add_source(state: dict[str, Any], source: dict[str, Any]) -> dict[str, Any]:
    updated = copy.deepcopy(state)
    updated.setdefault("sources", []).append(copy.deepcopy(source))
    validate_state(updated)
    return updated


def add_record(state: dict[str, Any], record: dict[str, Any]) -> dict[str, Any]:
    updated = copy.deepcopy(state)
    updated.setdefault("records", []).append(copy.deepcopy(record))
    validate_state(updated)
    return updated


def add_decision(state: dict[str, Any], decision: dict[str, Any]) -> dict[str, Any]:
    updated = copy.deepcopy(state)
    updated.setdefault("decisions", []).append(copy.deepcopy(decision))
    validate_state(updated)
    return updated


def add_review(state: dict[str, Any], review: dict[str, Any]) -> dict[str, Any]:
    updated = copy.deepcopy(state)
    updated.setdefault("reviews", []).append(copy.deepcopy(review))
    validate_state(updated)
    return updated


def latest_decision(state: dict[str, Any]) -> dict[str, Any] | None:
    decisions = state.get("decisions", [])
    if not decisions:
        return None
    return max(decisions, key=lambda item: parse_time(item["decided_at"]))


def latest_review(state: dict[str, Any]) -> dict[str, Any] | None:
    reviews = state.get("reviews", [])
    if not reviews:
        return None
    return max(reviews, key=lambda item: parse_time(item["reviewed_at"]))


def _record_projection(record: dict[str, Any]) -> dict[str, Any]:
    result = {
        "id": record["id"],
        "kind": record["kind"],
        "summary": record["summary"],
        "captured_at": record["captured_at"],
    }
    if "subject_at" in record:
        result["subject_at"] = record["subject_at"]
    if record.get("source_refs"):
        result["source_refs"] = list(record["source_refs"])
    if record["kind"] in {"unknown", "conflict"}:
        result["status"] = record.get("status", "open")
    return result


def _current_records(state: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        record
        for record in state.get("records", [])
        if record["kind"] not in {"unknown", "conflict"}
        or record.get("status", "open") == "open"
    ]


def _records_after(state: dict[str, Any], timestamp: str | None) -> list[dict[str, Any]]:
    if timestamp is None:
        return []
    threshold = parse_time(timestamp)
    return [
        record
        for record in state.get("records", [])
        if parse_time(record["captured_at"]) > threshold
    ]


def orientation_projection(state: dict[str, Any]) -> dict[str, Any]:
    """Generate a queryless resumption cue without mutating durable state."""
    validate_state(state)
    decision = latest_decision(state)
    review = latest_review(state)
    record_map = _record_map(state)

    unresolved = [
        _record_projection(record)
        for record in state.get("records", [])
        if record["kind"] in {"unknown", "conflict"}
        and record.get("status", "open") == "open"
    ]
    current = [
        _record_projection(record)
        for record in _current_records(state)
        if record["kind"] in {"observation", "hypothesis"}
    ]
    recommendations = [
        _record_projection(record)
        for record in _current_records(state)
        if record["kind"] == "recommendation"
    ]

    decision_projection = None
    if decision is not None:
        decision_projection = {
            "id": decision["id"],
            "statement": decision["statement"],
            "decided_at": decision["decided_at"],
            "basis": [
                _record_projection(record_map[ref])
                for ref in decision.get("basis_refs", [])
            ],
            "unresolved_at_decision": [
                _record_projection(record_map[ref])
                for ref in decision.get("unresolved_refs", [])
            ],
            "revisit_when": list(decision.get("revisit_when", [])),
        }

    review_time = None if review is None else review["reviewed_at"]
    decision_time = None if decision is None else decision["decided_at"]

    return {
        "projection": "soza-orientation/v0",
        "inquiry": copy.deepcopy(state["inquiry"]),
        "current_observations_and_hypotheses": current,
        "current_unresolved": unresolved,
        "recommendations": recommendations,
        "latest_decision": decision_projection,
        "since_last_review": [
            _record_projection(record) for record in _records_after(state, review_time)
        ],
        "since_latest_decision": [
            _record_projection(record) for record in _records_after(state, decision_time)
        ],
        "resume_anchor": None if review is None else review.get("resume_anchor"),
        "last_reviewed_at": review_time,
    }


def baseline_material_projection(state: dict[str, Any]) -> dict[str, Any]:
    """Return neutral flat material for a generic-summary baseline."""
    validate_state(state)
    events: list[dict[str, Any]] = []
    for record in state.get("records", []):
        events.append(
            {
                "captured_at": record["captured_at"],
                "text": record["summary"],
            }
        )
    for decision in state.get("decisions", []):
        events.append(
            {
                "captured_at": decision["decided_at"],
                "text": decision["statement"],
            }
        )
    events.sort(key=lambda item: parse_time(item["captured_at"]))
    return {
        "projection": "generic-summary-baseline-material/v0",
        "question": state["inquiry"]["question"],
        "materials": events,
    }


def handoff_projection(state: dict[str, Any]) -> dict[str, Any]:
    """Generate a structured portable AI/tool handoff projection."""
    orientation = orientation_projection(state)
    return {
        "projection": "soza-handoff/v0",
        "inquiry": orientation["inquiry"],
        "observations_and_hypotheses": orientation[
            "current_observations_and_hypotheses"
        ],
        "unresolved": orientation["current_unresolved"],
        "recommendations": orientation["recommendations"],
        "user_decision": orientation["latest_decision"],
        "change_since_review": orientation["since_last_review"],
        "resume_anchor": orientation["resume_anchor"],
        "boundary_notes": [
            "recommendation != user decision",
            "subject_at != captured_at",
            "later-captured material != historical decision basis",
            "this projection is not canonical authority",
        ],
    }
