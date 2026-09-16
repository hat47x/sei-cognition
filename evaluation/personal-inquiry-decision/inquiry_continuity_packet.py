#!/usr/bin/env python3
"""Build blinded human-review packets for ISSUE-000078 matched comparisons.

This is evaluation-only tooling. It never mutates canonical Inquiry state and it
does not turn a synthetic comparison into Product Value evidence.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

MANIFEST_SCHEMA = "sei.inquiry-continuity-matched-set/v0"
FIXTURE_SCHEMA = "sei.inquiry-continuity-comparison-fixture/v0"
PACKET_SCHEMA = "sei.inquiry-continuity-review-packet/v0"
CONDITIONS = {"A_raw_chat", "B_chronological_note", "C_sei_resume"}
STAGES = {"phase1", "post", "audit"}


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


def validate_fixture(fixture: dict[str, Any]) -> None:
    if fixture.get("schema") != FIXTURE_SCHEMA:
        raise PacketError(f"invalid fixture schema: {fixture.get('schema')!r}")
    if fixture.get("status") != "evaluation-only":
        raise PacketError("fixture status must remain evaluation-only")
    _require_keys(
        fixture,
        "fixture_id",
        "title",
        "scenario",
        "conditions",
        "reference_state",
        "human_review_template",
        "review_key",
    )
    scenario = fixture["scenario"]
    if not isinstance(scenario, dict):
        raise PacketError("scenario must be an object")
    _require_keys(scenario, "post_interruption_evidence")
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
        "before_post_interruption_evidence",
        "after_post_interruption_evidence",
    )


def validate_matched_set(
    manifest: dict[str, Any],
    fixtures_by_id: dict[str, dict[str, Any]],
) -> None:
    if manifest.get("schema") != MANIFEST_SCHEMA:
        raise PacketError(f"invalid manifest schema: {manifest.get('schema')!r}")
    if manifest.get("status") != "evaluation-only":
        raise PacketError("manifest status must remain evaluation-only")
    _require_keys(manifest, "set_id", "fixtures", "assignment_rotations")

    expected_ids: list[str] = []
    for item in manifest["fixtures"]:
        if not isinstance(item, dict) or not item.get("id"):
            raise PacketError("each manifest fixture requires id")
        expected_ids.append(item["id"])
    if len(expected_ids) != len(set(expected_ids)):
        raise PacketError("duplicate fixture id in manifest")

    if set(expected_ids) != set(fixtures_by_id):
        raise PacketError("loaded fixture set does not match manifest")
    for fixture_id, fixture in fixtures_by_id.items():
        validate_fixture(fixture)
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
    validate_fixture(fixture)

    packet: dict[str, Any] = {
        "schema": PACKET_SCHEMA,
        "status": "evaluation-only",
        "set_id": manifest["set_id"],
        "fixture_id": fixture["fixture_id"],
        "title": fixture["title"],
        "condition": condition,
        "stage": stage,
    }

    if stage == "phase1":
        packet["surface"] = fixture["conditions"][condition]["surface_text"]
        packet["questions"] = fixture["human_review_template"][
            "before_post_interruption_evidence"
        ]
    elif stage == "post":
        packet["post_interruption_evidence"] = fixture["scenario"][
            "post_interruption_evidence"
        ]
        packet["questions"] = fixture["human_review_template"][
            "after_post_interruption_evidence"
        ]
    else:
        packet["reference_state"] = fixture["reference_state"]
        packet["review_key"] = fixture["review_key"]

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
        path = repo_root / item["path"]
        fixtures[item["id"]] = load_json(path)
    validate_matched_set(manifest, fixtures)
    return manifest, fixtures


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build blinded ISSUE-000078 matched-comparison packets"
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
