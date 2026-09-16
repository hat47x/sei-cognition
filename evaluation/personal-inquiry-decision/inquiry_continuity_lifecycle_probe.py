#!/usr/bin/env python3
"""Validate and present ISSUE-000078 closure/dormancy lifecycle probes.

The lifecycle labels in this probe are Product-local attention projections.
They are never treated as canonical Inquiry status, Resolution, or Decision.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

SCHEMA = "sei.inquiry-continuity-lifecycle-probe/v0"
PACKET_SCHEMA = "sei.inquiry-continuity-lifecycle-packet/v0"
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


class LifecycleProbeError(ValueError):
    pass


def load_json(path: str | Path) -> dict[str, Any]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise LifecycleProbeError(f"cannot load JSON: {path}") from exc
    if not isinstance(value, dict):
        raise LifecycleProbeError(f"JSON root must be an object: {path}")
    return value


def _response_sha256(path: str | Path) -> str:
    try:
        raw = Path(path).read_bytes()
    except OSError as exc:
        raise LifecycleProbeError(f"cannot load response: {path}") from exc
    if not raw.strip():
        raise LifecycleProbeError("human response must not be empty")
    try:
        response = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise LifecycleProbeError("human response must be valid UTF-8 JSON") from exc
    if response is None:
        raise LifecycleProbeError("human response must not be null")
    return hashlib.sha256(raw).hexdigest()


def validate_probe(probe: dict[str, Any]) -> None:
    if probe.get("schema") != SCHEMA:
        raise LifecycleProbeError(f"schema must be {SCHEMA}")
    if probe.get("status") != "evaluation-only":
        raise LifecycleProbeError("status must remain evaluation-only")
    if probe.get("issue") != "ISSUE-000078":
        raise LifecycleProbeError("probe must belong to ISSUE-000078")

    stopline = probe.get("semantic_stopline")
    if not isinstance(stopline, dict):
        raise LifecycleProbeError("semantic_stopline must be an object")
    if stopline.get("attention_projection_is_canonical") is not False:
        raise LifecycleProbeError("attention projection must not be canonical")
    if stopline.get("universal_status_type") != "not-proposed":
        raise LifecycleProbeError("Universal Inquiry status type must not be proposed")

    scenario = probe.get("scenario")
    if not isinstance(scenario, dict) or scenario.get("decision_present") is not False:
        raise LifecycleProbeError("base scenario must remain Decisionless")

    snapshots = probe.get("lifecycle_snapshots")
    if not isinstance(snapshots, list) or len(snapshots) != len(STAGES):
        raise LifecycleProbeError("exactly four lifecycle snapshots are required")
    if [item.get("stage") for item in snapshots] != list(STAGES):
        raise LifecycleProbeError("lifecycle snapshots must follow active/dormant/closed/linked order")
    for item in snapshots:
        stage = item["stage"]
        if item.get("canonical_decision_present") is not False:
            raise LifecycleProbeError(
                f"{stage} must not create a Decision on the original Inquiry"
            )
        if item.get("unresolved_preserved") is not True:
            raise LifecycleProbeError(f"{stage} must preserve unresolved meaning")
        if item.get("canonical_inquiry_meaning_rewritten") is not False:
            raise LifecycleProbeError(
                f"{stage} must not rewrite canonical Inquiry meaning"
            )
    linked = snapshots[-1]
    if not linked.get("later_decision_ref"):
        raise LifecycleProbeError("linked_later_decision requires a separate decision reference")
    if linked.get("historical_link_role") != "prior_unresolved_context":
        raise LifecycleProbeError(
            "later Decision link must remain prior unresolved context"
        )

    conditions = probe.get("handling_conditions")
    if not isinstance(conditions, dict) or set(conditions) != CONDITIONS:
        raise LifecycleProbeError("probe must contain exactly A/B/C handling conditions")
    for condition_id, condition in conditions.items():
        if condition.get("canonical_authority") is not False:
            raise LifecycleProbeError(
                f"{condition_id} must not become canonical authority"
            )
        if not condition.get("surface"):
            raise LifecycleProbeError(f"{condition_id} requires surface material")
    if conditions["C_explicit_attention_projection"].get("automatic_transition") is not False:
        raise LifecycleProbeError(
            "explicit attention projection must remain human-controlled"
        )

    if not probe.get("human_review_questions"):
        raise LifecycleProbeError("human_review_questions are required")
    audit_key = probe.get("audit_key")
    if not isinstance(audit_key, dict) or not audit_key.get("semantic_hard_failures"):
        raise LifecycleProbeError("audit_key with semantic_hard_failures is required")


def build_review_packet(
    probe: dict[str, Any],
    condition_id: str,
) -> dict[str, Any]:
    validate_probe(probe)
    if condition_id not in CONDITIONS:
        raise LifecycleProbeError(f"unknown condition: {condition_id}")
    return {
        "schema": PACKET_SCHEMA,
        "status": "evaluation-only",
        "probe_id": probe["probe_id"],
        "condition": condition_id,
        "scenario": probe["scenario"],
        "lifecycle_snapshots": probe["lifecycle_snapshots"],
        "handling": probe["handling_conditions"][condition_id],
        "questions": probe["human_review_questions"],
        "semantic_stopline": probe["semantic_stopline"],
    }


def build_audit_packet(
    probe: dict[str, Any],
    condition_id: str,
    response_path: str | Path,
) -> dict[str, Any]:
    validate_probe(probe)
    if condition_id not in CONDITIONS:
        raise LifecycleProbeError(f"unknown condition: {condition_id}")
    return {
        "schema": PACKET_SCHEMA,
        "status": "evaluation-only",
        "probe_id": probe["probe_id"],
        "condition": condition_id,
        "stage": "audit",
        "fixed_response_sha256": _response_sha256(response_path),
        "audit_key": probe["audit_key"],
        "evidence_boundary": probe["evidence_boundary"],
        "semantic_stopline": probe["semantic_stopline"],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate or present ISSUE-000078 closure/dormancy probes"
    )
    parser.add_argument("--probe", required=True)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("validate")

    p = sub.add_parser("review")
    p.add_argument("--condition", choices=sorted(CONDITIONS), required=True)

    p = sub.add_parser("audit")
    p.add_argument("--condition", choices=sorted(CONDITIONS), required=True)
    p.add_argument("--response", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    probe = load_json(args.probe)
    validate_probe(probe)

    if args.command == "validate":
        print(
            json.dumps(
                {
                    "valid": True,
                    "probe_id": probe["probe_id"],
                    "conditions": sorted(CONDITIONS),
                    "universal_status_type": "not-proposed",
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    if args.command == "review":
        packet = build_review_packet(probe, args.condition)
    elif args.command == "audit":
        packet = build_audit_packet(probe, args.condition, args.response)
    else:
        raise AssertionError(f"unhandled command: {args.command}")
    print(json.dumps(packet, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
