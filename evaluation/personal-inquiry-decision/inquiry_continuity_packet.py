#!/usr/bin/env python3
"""Build blinded human-review packets for SEI matched comparisons.

This is evaluation-only tooling. It supports both ISSUE-000078 Inquiry Continuity
and ISSUE-000073 Decision Continuity fixtures without merging their evaluation
semantics. It never mutates canonical state and it does not turn a synthetic
comparison into Product Value evidence.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

INQUIRY_MANIFEST_SCHEMA = "sei.inquiry-continuity-matched-set/v0"
INQUIRY_FIXTURE_SCHEMA = "sei.inquiry-continuity-comparison-fixture/v0"
INQUIRY_PACKET_SCHEMA = "sei.inquiry-continuity-review-packet/v0"

DECISION_MANIFEST_SCHEMA = "sei.decision-continuity-matched-set/v0"
DECISION_FIXTURE_SCHEMA = "sei.decision-continuity-comparison-fixture/v0"
DECISION_PACKET_SCHEMA = "sei.decision-continuity-review-packet/v0"

# Backward-compatible names used by the original ISSUE-000078 tests/importers.
MANIFEST_SCHEMA = INQUIRY_MANIFEST_SCHEMA
FIXTURE_SCHEMA = INQUIRY_FIXTURE_SCHEMA
PACKET_SCHEMA = INQUIRY_PACKET_SCHEMA

CONDITIONS = {"A_raw_chat", "B_chronological_note", "C_sei_resume"}
STAGES = {"phase1", "post", "audit"}

_SCHEMA_PROFILES: dict[str, dict[str, Any]] = {
    INQUIRY_MANIFEST_SCHEMA: {
        "fixture_schema": INQUIRY_FIXTURE_SCHEMA,
        "packet_schema": INQUIRY_PACKET_SCHEMA,
        "post_evidence_key": "post_interruption_evidence",
        "before_questions_key": "before_post_interruption_evidence",
        "after_questions_key": "after_post_interruption_evidence",
        "require_review_key": True,
    },
    DECISION_MANIFEST_SCHEMA: {
        "fixture_schema": DECISION_FIXTURE_SCHEMA,
        "packet_schema": DECISION_PACKET_SCHEMA,
        "post_evidence_key": "post_decision_evidence",
        "before_questions_key": "before_post_decision_evidence",
        "after_questions_key": "after_post_decision_evidence",
        "require_review_key": False,
    },
}


class PacketError(ValueError):
    pass


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PacketError(f"cannot load JSON: {path}") from exc
    if not isinstance(value, dict):
        raise PacketError(f"JSON root must be an object: {path}")
    return value


def _require_keys(value: dict[str, Any], *keys: str) -> None:
    missing = [key for key in keys if key not in value]
    if missing:
        raise PacketError(f"missing required keys: {', '.join(missing)}")


def _profile_for_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    schema = manifest.get("schema")
    try:
        return _SCHEMA_PROFILES[schema]
    except KeyError as exc:
        raise PacketError(f"invalid manifest schema: {schema!r}") from exc


def _profile_for_fixture(fixture: dict[str, Any]) -> dict[str, Any]:
    schema = fixture.get("schema")
    for profile in _SCHEMA_PROFILES.values():
        if profile["fixture_schema"] == schema:
            return profile
    raise PacketError(f"invalid fixture schema: {schema!r}")


def validate_fixture(
    fixture: dict[str, Any],
    profile: dict[str, Any] | None = None,
) -> None:
    profile = profile or _profile_for_fixture(fixture)
    if fixture.get("schema") != profile["fixture_schema"]:
        raise PacketError(f"invalid fixture schema: {fixture.get('schema')!r}")
    if fixture.get("status") != "evaluation-only":
        raise PacketError("fixture status must remain evaluation-only")

    required = [
        "fixture_id",
        "title",
        "scenario",
        "conditions",
        "reference_state",
        "human_review_template",
    ]
    if profile["require_review_key"]:
        required.append("review_key")
    _require_keys(fixture, *required)

    scenario = fixture["scenario"]
    if not isinstance(scenario, dict):
        raise PacketError("scenario must be an object")
    _require_keys(scenario, profile["post_evidence_key"])

    conditions = fixture["conditions"]
    if not isinstance(conditions, dict) or set(conditions) != CONDITIONS:
        raise PacketError("fixture must contain exactly A/B/C conditions")
    for name in CONDITIONS:
        condition = conditions[name]
        if not isinstance(condition, dict) or "surface_text" not in condition:
            raise PacketError(f"{name} requires surface_text")

    review = fixture["human_review_template"]
    if not isinstance(review, dict):
        raise PacketError("human_review_template must be an object")
    _require_keys(
        review,
        profile["before_questions_key"],
        profile["after_questions_key"],
    )


def validate_matched_set(
    manifest: dict[str, Any],
    fixtures_by_id: dict[str, dict[str, Any]],
) -> None:
    profile = _profile_for_manifest(manifest)
    if manifest.get("status") != "evaluation-only":
        raise PacketError("manifest status must remain evaluation-only")
    _require_keys(manifest, "set_id", "fixtures", "assignment_rotations")

    expected_ids: list[str] = []
    for item in manifest["fixtures"]:
        if not isinstance(item, dict) or not item.get("id") or not item.get("path"):
            raise PacketError("each manifest fixture requires id and path")
        expected_ids.append(item["id"])
    if len(expected_ids) != len(set(expected_ids)):
        raise PacketError("duplicate fixture id in manifest")

    if set(expected_ids) != set(fixtures_by_id):
        raise PacketError("loaded fixture set does not match manifest")
    for fixture_id, fixture in fixtures_by_id.items():
        validate_fixture(fixture, profile)
        if fixture["fixture_id"] != fixture_id:
            raise PacketError(f"fixture id mismatch: {fixture_id}")

    rotations = manifest["assignment_rotations"]
    if not isinstance(rotations, dict) or not rotations:
        raise PacketError("assignment_rotations must be a non-empty object")

    seen_by_fixture = {fixture_id: set() for fixture_id in expected_ids}
    for rotation, assignments in rotations.items():
        if not isinstance(assignments, list):
            raise PacketError(f"rotation {rotation} must be a list")
        assigned_ids = []
        assigned_conditions = []
        for assignment in assignments:
            if not isinstance(assignment, dict):
                raise PacketError(f"rotation {rotation} contains invalid assignment")
            fixture_id = assignment.get("fixture")
            condition = assignment.get("condition")
            if fixture_id not in fixtures_by_id:
                raise PacketError(f"rotation {rotation} references unknown fixture")
            if condition not in CONDITIONS:
                raise PacketError(f"rotation {rotation} has invalid condition")
            assigned_ids.append(fixture_id)
            assigned_conditions.append(condition)
            seen_by_fixture[fixture_id].add(condition)
        if set(assigned_ids) != set(expected_ids) or len(assigned_ids) != len(expected_ids):
            raise PacketError(f"rotation {rotation} must assign each fixture exactly once")
        if set(assigned_conditions) != CONDITIONS or len(assigned_conditions) != len(CONDITIONS):
            raise PacketError(f"rotation {rotation} must use each condition exactly once")

    for fixture_id, seen in seen_by_fixture.items():
        if seen != CONDITIONS:
            raise PacketError(
                f"fixture {fixture_id} must receive every condition across rotations"
            )


def build_packet(
    manifest: dict[str, Any],
    fixture: dict[str, Any],
    condition: str,
    stage: str,
) -> dict[str, Any]:
    if condition not in CONDITIONS:
        raise PacketError(f"invalid condition: {condition}")
    if stage not in STAGES:
        raise PacketError(f"invalid stage: {stage}")

    profile = _profile_for_manifest(manifest)
    validate_fixture(fixture, profile)

    packet: dict[str, Any] = {
        "schema": profile["packet_schema"],
        "status": "evaluation-only",
        "set_id": manifest["set_id"],
        "fixture_id": fixture["fixture_id"],
        "title": fixture["title"],
        "condition": condition,
        "stage": stage,
    }

    review = fixture["human_review_template"]
    if stage == "phase1":
        packet["surface"] = fixture["conditions"][condition]["surface_text"]
        packet["questions"] = review[profile["before_questions_key"]]
    elif stage == "post":
        evidence_key = profile["post_evidence_key"]
        packet[evidence_key] = fixture["scenario"][evidence_key]
        packet["questions"] = review[profile["after_questions_key"]]
    else:
        packet["reference_state"] = fixture["reference_state"]
        if "review_key" in fixture:
            packet["review_key"] = fixture["review_key"]
        if "operator_metrics" in review:
            packet["operator_metrics"] = review["operator_metrics"]

    return packet


def build_rotation_packets(
    manifest: dict[str, Any],
    fixtures_by_id: dict[str, dict[str, Any]],
    rotation: str,
    stage: str,
) -> list[dict[str, Any]]:
    validate_matched_set(manifest, fixtures_by_id)
    try:
        assignments = manifest["assignment_rotations"][rotation]
    except KeyError as exc:
        raise PacketError(f"unknown rotation: {rotation}") from exc
    return [
        build_packet(
            manifest,
            fixtures_by_id[assignment["fixture"]],
            assignment["condition"],
            stage,
        )
        for assignment in assignments
    ]


def load_manifest_fixtures(
    manifest_path: Path,
    repo_root: Path,
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    manifest = load_json(manifest_path)
    fixtures: dict[str, dict[str, Any]] = {}
    for item in manifest.get("fixtures", []):
        if not isinstance(item, dict) or "id" not in item or "path" not in item:
            raise PacketError("each manifest fixture requires id and path")
        path = repo_root / item["path"]
        fixtures[item["id"]] = load_json(path)
    validate_matched_set(manifest, fixtures)
    return manifest, fixtures


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build blinded SEI matched-comparison review packets"
    )
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--rotation")
    parser.add_argument("--stage", choices=sorted(STAGES))
    parser.add_argument("--validate-only", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    manifest, fixtures = load_manifest_fixtures(
        Path(args.manifest), Path(args.repo_root)
    )
    if args.validate_only:
        print(
            json.dumps(
                {
                    "valid": True,
                    "schema": manifest["schema"],
                    "set_id": manifest["set_id"],
                    "fixtures": len(fixtures),
                    "rotations": len(manifest["assignment_rotations"]),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0
    if not args.rotation or not args.stage:
        raise PacketError("--rotation and --stage are required unless --validate-only")
    packets = build_rotation_packets(
        manifest, fixtures, args.rotation, args.stage
    )
    print(json.dumps(packets, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
