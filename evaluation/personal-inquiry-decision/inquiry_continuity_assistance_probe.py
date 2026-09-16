#!/usr/bin/env python3
"""Build stage-gated ISSUE-000078 Quiet/Proactive assistance review packets.

This evaluation-only tool overlays provisional AI assistance on existing Inquiry
Continuity fixtures. It never mutates canonical meaning, never treats suggestion
visibility as a Stable Requirement, and never computes an overall winner.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

SCHEMA = "sei.inquiry-continuity-assistance-probe/v0"
FIXTURE_SCHEMA = "sei.inquiry-continuity-comparison-fixture/v0"
PACKET_SCHEMA = "sei.inquiry-continuity-assistance-packet/v0"
CONDITIONS = {"A_proactive_first", "B_quiet_first", "C_adaptive_progressive"}
STAGES = {"initial", "reveal", "audit"}


class AssistanceProbeError(ValueError):
    pass


def load_json(path: str | Path) -> dict[str, Any]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AssistanceProbeError(f"cannot load JSON: {path}") from exc
    if not isinstance(value, dict):
        raise AssistanceProbeError(f"JSON root must be an object: {path}")
    return value


def git_blob_sha1(raw: bytes) -> str:
    header = f"blob {len(raw)}\0".encode("ascii")
    return hashlib.sha1(header + raw).hexdigest()


def response_sha256(path: str | Path) -> str:
    try:
        raw = Path(path).read_bytes()
    except OSError as exc:
        raise AssistanceProbeError(f"cannot load response: {path}") from exc
    if not raw.strip():
        raise AssistanceProbeError("human response must not be empty")
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AssistanceProbeError("human response must be valid UTF-8 JSON") from exc
    if value is None:
        raise AssistanceProbeError("human response must not be null")
    return hashlib.sha256(raw).hexdigest()


def _validate_rotations(probe: dict[str, Any], case_ids: list[str]) -> None:
    rotations = probe.get("assignment_rotations")
    if not isinstance(rotations, dict) or not rotations:
        raise AssistanceProbeError("assignment_rotations must be a non-empty object")
    seen = {case_id: set() for case_id in case_ids}
    for rotation, assignments in rotations.items():
        if not isinstance(assignments, list):
            raise AssistanceProbeError(f"rotation {rotation} must be a list")
        ids, conditions = [], []
        for item in assignments:
            if not isinstance(item, dict):
                raise AssistanceProbeError(f"rotation {rotation} contains invalid assignment")
            case_id, condition = item.get("fixture"), item.get("condition")
            if case_id not in seen or condition not in CONDITIONS:
                raise AssistanceProbeError(f"rotation {rotation} contains invalid assignment")
            ids.append(case_id)
            conditions.append(condition)
            seen[case_id].add(condition)
        if set(ids) != set(case_ids) or len(ids) != len(case_ids):
            raise AssistanceProbeError(f"rotation {rotation} must assign each case exactly once")
        if set(conditions) != CONDITIONS or len(conditions) != len(CONDITIONS):
            raise AssistanceProbeError(f"rotation {rotation} must use each condition exactly once")
    for case_id, values in seen.items():
        if values != CONDITIONS:
            raise AssistanceProbeError(f"{case_id} must receive every condition across rotations")


def validate_probe(probe: dict[str, Any]) -> None:
    if probe.get("schema") != SCHEMA:
        raise AssistanceProbeError(f"schema must be {SCHEMA}")
    if probe.get("status") != "evaluation-only" or probe.get("issue") != "ISSUE-000078":
        raise AssistanceProbeError("probe must remain evaluation-only for ISSUE-000078")
    stop = probe.get("semantic_stopline")
    if not isinstance(stop, dict):
        raise AssistanceProbeError("semantic_stopline must be an object")
    if stop.get("suggestions_are_canonical") is not False:
        raise AssistanceProbeError("AI suggestions must not be canonical")
    if stop.get("quiet_may_hide_canonical_orientation") is not False:
        raise AssistanceProbeError("Quiet mode must not hide canonical orientation")
    if stop.get("surface_choice_is_stable_requirement") is not False:
        raise AssistanceProbeError("surface choice must not be a Stable Requirement")
    if stop.get("overall_winner_allowed") is not False:
        raise AssistanceProbeError("overall winner must remain disallowed")

    conditions = probe.get("conditions")
    if not isinstance(conditions, dict) or set(conditions) != CONDITIONS:
        raise AssistanceProbeError("probe must define exactly three assistance conditions")
    visibility = {name: value.get("initial_visibility") for name, value in conditions.items()}
    expected = {
        "A_proactive_first": "all",
        "B_quiet_first": "none",
        "C_adaptive_progressive": "primary-only",
    }
    if visibility != expected:
        raise AssistanceProbeError("assistance visibility contract is invalid")

    cases = probe.get("cases")
    if not isinstance(cases, list) or len(cases) != 3:
        raise AssistanceProbeError("exactly three matched cases are required")
    ids = []
    for case in cases:
        if not isinstance(case, dict):
            raise AssistanceProbeError("case must be an object")
        for key in ("fixture_id", "path", "blob_sha1", "suggestions"):
            if not case.get(key):
                raise AssistanceProbeError(f"case missing {key}")
        suggestions = case["suggestions"]
        if not isinstance(suggestions, list) or len(suggestions) < 5:
            raise AssistanceProbeError("each case requires at least five suggestions")
        suggestion_ids = [item.get("id") for item in suggestions]
        if len(suggestion_ids) != len(set(suggestion_ids)) or None in suggestion_ids:
            raise AssistanceProbeError("suggestion ids must be unique and non-empty")
        if sum(item.get("priority") == "primary" for item in suggestions) != 1:
            raise AssistanceProbeError("each case requires exactly one primary suggestion")
        ids.append(case["fixture_id"])
    if len(ids) != len(set(ids)):
        raise AssistanceProbeError("fixture ids must be unique")
    _validate_rotations(probe, ids)

    questions = probe.get("review_questions")
    if not isinstance(questions, dict) or not questions.get("initial") or not questions.get("reveal"):
        raise AssistanceProbeError("initial and reveal review questions are required")
    audit = probe.get("audit_key")
    if not isinstance(audit, dict) or not audit.get("semantic_hard_failures"):
        raise AssistanceProbeError("audit_key with semantic hard failures is required")


def load_sources(probe: dict[str, Any], repo_root: str | Path) -> dict[str, dict[str, Any]]:
    validate_probe(probe)
    root = Path(repo_root)
    fixtures: dict[str, dict[str, Any]] = {}
    for case in probe["cases"]:
        path = root / case["path"]
        try:
            raw = path.read_bytes()
        except OSError as exc:
            raise AssistanceProbeError(f"cannot load source fixture: {path}") from exc
        if git_blob_sha1(raw) != case["blob_sha1"]:
            raise AssistanceProbeError(f"source fixture changed after probe design: {case['fixture_id']}")
        fixture = load_json(path)
        if fixture.get("schema") != FIXTURE_SCHEMA or fixture.get("status") != "evaluation-only":
            raise AssistanceProbeError(f"invalid source fixture: {case['fixture_id']}")
        if fixture.get("fixture_id") != case["fixture_id"]:
            raise AssistanceProbeError(f"source fixture id mismatch: {case['fixture_id']}")
        scenario = fixture.get("scenario")
        if not isinstance(scenario, dict) or scenario.get("decision_present") is not False:
            raise AssistanceProbeError(f"source fixture must remain Decisionless: {case['fixture_id']}")
        try:
            orientation = fixture["conditions"]["C_sei_resume"]["surface_text"]["orientation"]
        except (KeyError, TypeError) as exc:
            raise AssistanceProbeError(f"source fixture lacks SEI orientation: {case['fixture_id']}") from exc
        if not isinstance(orientation, dict):
            raise AssistanceProbeError(f"orientation must be an object: {case['fixture_id']}")
        fixtures[case["fixture_id"]] = fixture
    return fixtures


def _case_by_id(probe: dict[str, Any], fixture_id: str) -> dict[str, Any]:
    for case in probe["cases"]:
        if case["fixture_id"] == fixture_id:
            return case
    raise AssistanceProbeError(f"unknown fixture: {fixture_id}")


def _visible_suggestions(case: dict[str, Any], condition: str) -> list[dict[str, Any]]:
    suggestions = case["suggestions"]
    if condition == "A_proactive_first":
        return suggestions
    if condition == "B_quiet_first":
        return []
    return [item for item in suggestions if item.get("priority") == "primary"]


def build_initial_packets(
    probe: dict[str, Any], fixtures: dict[str, dict[str, Any]], rotation: str
) -> list[dict[str, Any]]:
    validate_probe(probe)
    try:
        assignments = probe["assignment_rotations"][rotation]
    except KeyError as exc:
        raise AssistanceProbeError(f"unknown rotation: {rotation}") from exc
    packets = []
    for assignment in assignments:
        fixture_id, condition = assignment["fixture"], assignment["condition"]
        fixture, case = fixtures[fixture_id], _case_by_id(probe, fixture_id)
        visible = _visible_suggestions(case, condition)
        packets.append({
            "schema": PACKET_SCHEMA,
            "status": "evaluation-only",
            "probe_id": probe["probe_id"],
            "fixture_id": fixture_id,
            "title": fixture["title"],
            "condition": condition,
            "stage": "initial",
            "canonical_orientation": fixture["conditions"]["C_sei_resume"]["surface_text"]["orientation"],
            "visible_ai_suggestions": visible,
            "more_suggestions_available": len(visible) < len(case["suggestions"]),
            "suggestion_provenance": "evaluation-only provisional AI suggestion; not canonical meaning",
            "questions": probe["review_questions"]["initial"],
            "semantic_stopline": probe["semantic_stopline"],
        })
    return packets


def build_reveal_packets(
    probe: dict[str, Any], fixtures: dict[str, dict[str, Any]], rotation: str, initial_response: str | Path
) -> list[dict[str, Any]]:
    fixed = response_sha256(initial_response)
    packets = build_initial_packets(probe, fixtures, rotation)
    result = []
    for packet in packets:
        case = _case_by_id(probe, packet["fixture_id"])
        result.append({
            "schema": PACKET_SCHEMA,
            "status": "evaluation-only",
            "probe_id": probe["probe_id"],
            "fixture_id": packet["fixture_id"],
            "title": packet["title"],
            "condition": packet["condition"],
            "stage": "reveal",
            "fixed_initial_response_sha256": fixed,
            "all_ai_suggestions": case["suggestions"],
            "suggestion_provenance": packet["suggestion_provenance"],
            "questions": probe["review_questions"]["reveal"],
            "semantic_stopline": probe["semantic_stopline"],
        })
    return result


def build_audit_packets(
    probe: dict[str, Any], fixtures: dict[str, dict[str, Any]], rotation: str,
    initial_response: str | Path, reveal_response: str | Path
) -> list[dict[str, Any]]:
    initial_hash = response_sha256(initial_response)
    reveal_hash = response_sha256(reveal_response)
    try:
        assignments = probe["assignment_rotations"][rotation]
    except KeyError as exc:
        raise AssistanceProbeError(f"unknown rotation: {rotation}") from exc
    result = []
    for assignment in assignments:
        fixture_id, condition = assignment["fixture"], assignment["condition"]
        fixture = fixtures[fixture_id]
        result.append({
            "schema": PACKET_SCHEMA,
            "status": "evaluation-only",
            "probe_id": probe["probe_id"],
            "fixture_id": fixture_id,
            "condition": condition,
            "stage": "audit",
            "fixed_initial_response_sha256": initial_hash,
            "fixed_reveal_response_sha256": reveal_hash,
            "reference_state": fixture["reference_state"],
            "audit_key": probe["audit_key"],
            "evidence_boundary": probe["evidence_boundary"],
            "semantic_stopline": probe["semantic_stopline"],
        })
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build ISSUE-000078 Quiet/Proactive assistance packets")
    parser.add_argument("--probe", required=True)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--rotation")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate")
    sub.add_parser("initial")
    p = sub.add_parser("reveal")
    p.add_argument("--initial-response", required=True)
    p = sub.add_parser("audit")
    p.add_argument("--initial-response", required=True)
    p.add_argument("--reveal-response", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    probe = load_json(args.probe)
    fixtures = load_sources(probe, args.repo_root)
    if args.command == "validate":
        print(json.dumps({"valid": True, "probe_id": probe["probe_id"], "cases": len(fixtures), "rotations": len(probe["assignment_rotations"])}, ensure_ascii=False, indent=2))
        return 0
    if not args.rotation:
        raise AssistanceProbeError("--rotation is required for packet generation")
    if args.command == "initial":
        packets = build_initial_packets(probe, fixtures, args.rotation)
    elif args.command == "reveal":
        packets = build_reveal_packets(probe, fixtures, args.rotation, args.initial_response)
    elif args.command == "audit":
        packets = build_audit_packets(probe, fixtures, args.rotation, args.initial_response, args.reveal_response)
    else:
        raise AssertionError(f"unhandled command: {args.command}")
    print(json.dumps(packets, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
