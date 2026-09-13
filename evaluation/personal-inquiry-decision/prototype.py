#!/usr/bin/env python3
"""Evaluation-only prototype for the Personal Inquiry / Decision Workspace.

This module is not a Universal SEI Contract and does not define a production
workflow. It exercises a minimal individual reorientation value slice using
concepts already present in the current SEI semantics.
"""

from __future__ import annotations

import copy
from datetime import datetime
from typing import Any


class PrototypeStateError(ValueError):
    pass


def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _records_by_id(state: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for key in ("observations", "unknowns", "conflicts", "recommendations", "decisions"):
        for record in state.get(key, []):
            record_id = record.get("id")
            if not isinstance(record_id, str) or not record_id:
                raise PrototypeStateError(f"{key} record requires non-empty id")
            if record_id in result:
                raise PrototypeStateError(f"duplicate record id: {record_id}")
            result[record_id] = record
    return result


def validate_state(state: dict[str, Any]) -> None:
    inquiry = state.get("inquiry")
    if not isinstance(inquiry, dict) or not inquiry.get("question"):
        raise PrototypeStateError("inquiry.question is required")

    records = _records_by_id(state)
    observation_ids = {item["id"] for item in state.get("observations", [])}
    unresolved_ids = {
        item["id"] for item in state.get("unknowns", []) + state.get("conflicts", [])
    }

    for decision in state.get("decisions", []):
        decided_at = decision.get("decided_at")
        if not decided_at:
            raise PrototypeStateError(f"decision {decision['id']} requires decided_at")
        decision_time = _parse_time(decided_at)

        for ref in decision.get("basis_refs", []):
            if ref not in records:
                raise PrototypeStateError(f"decision {decision['id']} has unknown basis ref: {ref}")
            if ref in observation_ids:
                observation = records[ref]
                observed_at = observation.get("observed_at") or observation.get("added_at")
                if observed_at and _parse_time(observed_at) > decision_time:
                    raise PrototypeStateError(
                        f"decision {decision['id']} cannot use post-decision observation {ref} as historical basis"
                    )

        for ref in decision.get("unresolved_refs", []):
            if ref not in unresolved_ids:
                raise PrototypeStateError(
                    f"decision {decision['id']} unresolved ref must point to unknown/conflict: {ref}"
                )


def latest_decision(state: dict[str, Any]) -> dict[str, Any] | None:
    decisions = state.get("decisions", [])
    if not decisions:
        return None
    return max(decisions, key=lambda item: _parse_time(item["decided_at"]))


def latest_recommendation(state: dict[str, Any]) -> dict[str, Any] | None:
    recommendations = state.get("recommendations", [])
    if not recommendations:
        return None
    return recommendations[-1]


def unresolved_items(state: dict[str, Any]) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    for kind, key in (("unknown", "unknowns"), ("conflict", "conflicts")):
        for item in state.get(key, []):
            if item.get("status", "open") == "open":
                result.append({"id": item["id"], "kind": kind, "summary": item["summary"]})
    return result


def decision_basis(state: dict[str, Any], decision: dict[str, Any] | None) -> list[dict[str, str]]:
    if decision is None:
        return []
    records = _records_by_id(state)
    result: list[dict[str, str]] = []
    for ref in decision.get("basis_refs", []):
        record = records[ref]
        result.append({"id": ref, "summary": record.get("summary", "")})
    return result


def post_decision_observations(state: dict[str, Any]) -> list[dict[str, Any]]:
    decision = latest_decision(state)
    if decision is None:
        return []
    decision_time = _parse_time(decision["decided_at"])
    return [
        copy.deepcopy(item)
        for item in state.get("observations", [])
        if _parse_time(item.get("observed_at") or item["added_at"]) > decision_time
    ]


def reorientation_view(state: dict[str, Any]) -> dict[str, Any]:
    """Return the five-question light view without changing canonical state."""
    validate_state(state)
    decision = latest_decision(state)
    recommendation = latest_recommendation(state)

    observations = [
        {"id": item["id"], "summary": item["summary"]}
        for item in state.get("observations", [])
        if item.get("status", "current") != "withdrawn"
    ]

    return {
        "what_am_i_considering": state["inquiry"]["question"],
        "important_observations": observations,
        "what_is_unresolved": unresolved_items(state),
        "recommendation": None
        if recommendation is None
        else {"id": recommendation["id"], "summary": recommendation["summary"]},
        "decision": None
        if decision is None
        else {"id": decision["id"], "statement": decision["statement"]},
        "decision_basis": decision_basis(state, decision),
        "revisit_when": [] if decision is None else list(decision.get("revisit_when", [])),
        "new_since_decision": [
            {"id": item["id"], "summary": item["summary"]}
            for item in post_decision_observations(state)
        ],
    }


def add_observation(state: dict[str, Any], observation: dict[str, Any]) -> dict[str, Any]:
    """Append a new observation without mutating a historical Decision."""
    updated = copy.deepcopy(state)
    updated.setdefault("observations", []).append(copy.deepcopy(observation))
    validate_state(updated)
    return updated
