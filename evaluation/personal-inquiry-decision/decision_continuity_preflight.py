#!/usr/bin/env python3
"""Validate ISSUE-000073 Decision Continuity fixtures before blinded review.

This is evaluation-only preflight tooling. It complements the shared matched
packet builder by checking Decision-specific semantic stoplines. It never
mutates canonical state and does not make human-review or Product Value claims.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from inquiry_continuity_packet import (
    DECISION_MANIFEST_SCHEMA,
    PacketError,
    load_json,
    validate_matched_set,
)


def _require_keys(value: dict[str, Any], *keys: str) -> None:
    missing = [key for key in keys if key not in value]
    if missing:
        raise PacketError(f"missing required keys: {', '.join(missing)}")


def _events_by_id(events: Any, label: str) -> dict[str, dict[str, Any]]:
    if not isinstance(events, list):
        raise PacketError(f"{label} must be a list")

    indexed: dict[str, dict[str, Any]] = {}
    for event in events:
        if not isinstance(event, dict):
            raise PacketError(f"{label} event must be an object")
        _require_keys(event, "id", "role")
        event_id = event["id"]
        if not isinstance(event_id, str) or not event_id:
            raise PacketError(f"{label} event requires non-empty id")
        if event_id in indexed:
            raise PacketError(f"duplicate event id in {label}: {event_id}")
        indexed[event_id] = event
    return indexed


def validate_decision_fixture_semantics(fixture: dict[str, Any]) -> None:
    if fixture.get("schema") != "sei.decision-continuity-comparison-fixture/v0":
        raise PacketError(f"invalid Decision fixture schema: {fixture.get('schema')!r}")
    if fixture.get("status") != "evaluation-only":
        raise PacketError("Decision fixture status must remain evaluation-only")
    if fixture.get("issue") != "ISSUE-000073":
        raise PacketError("Decision fixture issue must be ISSUE-000073")

    _require_keys(
        fixture,
        "scenario",
        "reference_state",
        "conditions",
        "human_review_template",
    )
    scenario = fixture["scenario"]
    if not isinstance(scenario, dict):
        raise PacketError("scenario must be an object")
    _require_keys(scenario, "phase_1", "post_decision_evidence")

    phase1 = _events_by_id(scenario["phase_1"], "phase_1")
    post = _events_by_id(
        scenario["post_decision_evidence"], "post_decision_evidence"
    )
    overlap = set(phase1) & set(post)
    if overlap:
        raise PacketError(
            "event id must not exist both before and after Decision: "
            + ", ".join(sorted(overlap))
        )

    decisions = [event for event in phase1.values() if event["role"] == "decision"]
    if len(decisions) != 1:
        raise PacketError("phase_1 must contain exactly one Decision")
    decision = decisions[0]
    _require_keys(decision, "basis_refs", "recommendation_refs", "unresolved_refs")

    basis_refs = decision["basis_refs"]
    recommendation_refs = decision["recommendation_refs"]
    unresolved_refs = decision["unresolved_refs"]
    for name, refs in (
        ("basis_refs", basis_refs),
        ("recommendation_refs", recommendation_refs),
        ("unresolved_refs", unresolved_refs),
    ):
        if not isinstance(refs, list) or not all(
            isinstance(ref, str) and ref for ref in refs
        ):
            raise PacketError(f"Decision {name} must be a list of non-empty ids")
        if len(refs) != len(set(refs)):
            raise PacketError(f"Decision {name} contains duplicates")

    for ref in basis_refs:
        if ref not in phase1:
            raise PacketError(f"Decision basis ref not found in phase_1: {ref}")
        if phase1[ref]["role"] in {"decision", "recommendation"}:
            raise PacketError(
                f"Decision basis ref must not point to {phase1[ref]['role']}: {ref}"
            )
    for ref in recommendation_refs:
        if ref not in phase1 or phase1[ref]["role"] != "recommendation":
            raise PacketError(f"Decision recommendation ref is invalid: {ref}")
    for ref in unresolved_refs:
        if ref not in phase1 or phase1[ref]["role"] not in {"unknown", "conflict"}:
            raise PacketError(f"Decision unresolved ref is invalid: {ref}")

    reference = fixture["reference_state"]
    if not isinstance(reference, dict):
        raise PacketError("reference_state must be an object")
    _require_keys(
        reference,
        "decision",
        "recommendation",
        "historical_basis_ids",
        "unresolved_ids",
        "post_decision_ids",
        "temporal_stopline",
    )

    historical_basis_ids = reference["historical_basis_ids"]
    unresolved_ids = reference["unresolved_ids"]
    post_decision_ids = reference["post_decision_ids"]
    if historical_basis_ids != basis_refs:
        raise PacketError(
            "reference historical_basis_ids must exactly match Decision basis_refs"
        )
    if unresolved_ids != unresolved_refs:
        raise PacketError(
            "reference unresolved_ids must exactly match Decision unresolved_refs"
        )
    if post_decision_ids != list(post):
        raise PacketError(
            "reference post_decision_ids must exactly match post_decision_evidence"
        )

    post_refs = set(post)
    leaked = post_refs & set(historical_basis_ids)
    if leaked:
        raise PacketError(
            "post-decision ids must not appear in historical basis: "
            + ", ".join(sorted(leaked))
        )
    if post_refs & set(unresolved_ids):
        raise PacketError(
            "post-decision ids must not be presented as Decision-time unresolved"
        )

    if not isinstance(reference["temporal_stopline"], str) or not reference[
        "temporal_stopline"
    ].strip():
        raise PacketError("reference temporal_stopline must be non-empty")


def validate_decision_matched_set(
    manifest: dict[str, Any],
    fixtures_by_id: dict[str, dict[str, Any]],
) -> None:
    if manifest.get("schema") != DECISION_MANIFEST_SCHEMA:
        raise PacketError(f"invalid Decision manifest schema: {manifest.get('schema')!r}")
    if manifest.get("status") != "evaluation-only":
        raise PacketError("Decision manifest status must remain evaluation-only")
    if manifest.get("issue") != "ISSUE-000073":
        raise PacketError("Decision manifest issue must be ISSUE-000073")

    # Reuse the shared structural/blinding validation first.
    validate_matched_set(manifest, fixtures_by_id)

    _require_keys(manifest, "interpretation_stoplines")
    stoplines = manifest["interpretation_stoplines"]
    if not isinstance(stoplines, list) or not stoplines:
        raise PacketError("interpretation_stoplines must be a non-empty list")

    for fixture_id, fixture in fixtures_by_id.items():
        try:
            validate_decision_fixture_semantics(fixture)
        except PacketError as exc:
            raise PacketError(f"{fixture_id}: {exc}") from exc


def load_decision_set(
    manifest_path: Path,
    repo_root: Path,
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    manifest = load_json(manifest_path)
    fixtures: dict[str, dict[str, Any]] = {}
    for item in manifest.get("fixtures", []):
        if not isinstance(item, dict) or "id" not in item or "path" not in item:
            raise PacketError("each manifest fixture requires id and path")
        fixtures[item["id"]] = load_json(repo_root / item["path"])
    validate_decision_matched_set(manifest, fixtures)
    return manifest, fixtures


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Preflight ISSUE-000073 Decision Continuity matched fixtures"
    )
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--repo-root", default=".")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    manifest, fixtures = load_decision_set(
        Path(args.manifest), Path(args.repo_root)
    )
    print(
        json.dumps(
            {
                "valid": True,
                "schema": manifest["schema"],
                "set_id": manifest["set_id"],
                "fixtures": len(fixtures),
                "evidence": "Design Evidence only; human review not executed",
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
