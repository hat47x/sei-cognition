#!/usr/bin/env python3
"""Evaluation-only stage gate for blinded matched-review sessions.

A session freezes one manifest/fixture snapshot and one assignment rotation.  It
prevents later-evidence and audit material from being exposed before earlier
responses have been fixed.  It intentionally records review observations only;
it does not mutate canonical SEI meaning and it does not compute a winner.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from inquiry_continuity_packet import (
    CONDITIONS,
    PacketError,
    build_rotation_packets,
    load_manifest_fixtures,
    validate_matched_set,
)

SCHEMA = "sei.matched-review-session/v0"
REVIEW_STAGES = ("phase1", "post", "audit")
COMPLETE = "complete"


class ReviewSessionError(ValueError):
    pass


def _parse_time(value: str) -> datetime:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, TypeError, ValueError) as exc:
        raise ReviewSessionError(f"invalid timestamp: {value!r}") from exc


def _digest_json(value: Any) -> str:
    canonical = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _snapshot_sources(
    manifest: dict[str, Any],
    fixtures_by_id: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    return {
        "manifest_sha256": _digest_json(manifest),
        "fixture_sha256": {
            fixture_id: _digest_json(fixtures_by_id[fixture_id])
            for fixture_id in sorted(fixtures_by_id)
        },
    }


def new_session(
    manifest: dict[str, Any],
    fixtures_by_id: dict[str, dict[str, Any]],
    rotation: str,
    session_id: str,
    created_at: str,
) -> dict[str, Any]:
    validate_matched_set(manifest, fixtures_by_id)
    if not session_id.strip():
        raise ReviewSessionError("session_id must not be empty")
    _parse_time(created_at)
    try:
        assignments = manifest["assignment_rotations"][rotation]
    except KeyError as exc:
        raise ReviewSessionError(f"unknown rotation: {rotation}") from exc

    session = {
        "schema": SCHEMA,
        "status": "evaluation-only",
        "session_id": session_id.strip(),
        "manifest_schema": manifest["schema"],
        "set_id": manifest["set_id"],
        "rotation": rotation,
        "created_at": created_at,
        "source_snapshot": _snapshot_sources(manifest, fixtures_by_id),
        "assignments": [
            {
                "fixture_id": assignment["fixture"],
                "condition": assignment["condition"],
                "records": {stage: None for stage in REVIEW_STAGES},
            }
            for assignment in assignments
        ],
        "interpretation_stoplines": [
            "This session is evaluation-only and is not Product Value evidence by itself.",
            "Do not expose post material before every phase1 response is fixed.",
            "Do not expose audit material before every post response is fixed.",
            "Do not compute an aggregate winner or score from this session.",
        ],
    }
    validate_session(session, manifest, fixtures_by_id)
    return session


def _validate_record(record: Any, stage: str, fixture_id: str) -> None:
    if record is None:
        return
    if not isinstance(record, dict):
        raise ReviewSessionError(f"{fixture_id}/{stage} record must be an object")
    if set(record) != {"recorded_at", "response"}:
        raise ReviewSessionError(
            f"{fixture_id}/{stage} record must contain recorded_at and response only"
        )
    _parse_time(record["recorded_at"])
    if record["response"] is None:
        raise ReviewSessionError(f"{fixture_id}/{stage} response must not be null")


def validate_session(
    session: dict[str, Any],
    manifest: dict[str, Any] | None = None,
    fixtures_by_id: dict[str, dict[str, Any]] | None = None,
) -> None:
    if session.get("schema") != SCHEMA:
        raise ReviewSessionError(f"schema must be {SCHEMA}")
    if session.get("status") != "evaluation-only":
        raise ReviewSessionError("status must remain evaluation-only")
    for key in (
        "session_id",
        "manifest_schema",
        "set_id",
        "rotation",
        "created_at",
        "source_snapshot",
        "assignments",
    ):
        if key not in session:
            raise ReviewSessionError(f"missing required key: {key}")
    if not isinstance(session["session_id"], str) or not session["session_id"].strip():
        raise ReviewSessionError("session_id must not be empty")
    _parse_time(session["created_at"])

    assignments = session["assignments"]
    if not isinstance(assignments, list) or not assignments:
        raise ReviewSessionError("assignments must be a non-empty list")
    fixture_ids: list[str] = []
    for assignment in assignments:
        if not isinstance(assignment, dict):
            raise ReviewSessionError("assignment must be an object")
        if set(assignment) != {"fixture_id", "condition", "records"}:
            raise ReviewSessionError(
                "assignment must contain fixture_id, condition, and records only"
            )
        fixture_id = assignment["fixture_id"]
        if not isinstance(fixture_id, str) or not fixture_id:
            raise ReviewSessionError("assignment fixture_id must be non-empty")
        if assignment["condition"] not in CONDITIONS:
            raise ReviewSessionError(f"invalid condition for {fixture_id}")
        records = assignment["records"]
        if not isinstance(records, dict) or set(records) != set(REVIEW_STAGES):
            raise ReviewSessionError(
                f"{fixture_id} records must contain phase1/post/audit exactly"
            )
        for stage in REVIEW_STAGES:
            _validate_record(records[stage], stage, fixture_id)
        fixture_ids.append(fixture_id)
    if len(fixture_ids) != len(set(fixture_ids)):
        raise ReviewSessionError("duplicate fixture assignment")

    all_phase1 = all(item["records"]["phase1"] is not None for item in assignments)
    any_post = any(item["records"]["post"] is not None for item in assignments)
    all_post = all(item["records"]["post"] is not None for item in assignments)
    any_audit = any(item["records"]["audit"] is not None for item in assignments)
    if any_post and not all_phase1:
        raise ReviewSessionError("post record exists before all phase1 responses are fixed")
    if any_audit and not all_post:
        raise ReviewSessionError("audit record exists before all post responses are fixed")

    if manifest is None and fixtures_by_id is None:
        return
    if manifest is None or fixtures_by_id is None:
        raise ReviewSessionError("manifest and fixtures must be supplied together")

    try:
        validate_matched_set(manifest, fixtures_by_id)
    except PacketError as exc:
        raise ReviewSessionError(str(exc)) from exc
    if session["manifest_schema"] != manifest.get("schema"):
        raise ReviewSessionError("manifest schema changed after session initialization")
    if session["set_id"] != manifest.get("set_id"):
        raise ReviewSessionError("matched set changed after session initialization")
    try:
        expected_assignments = manifest["assignment_rotations"][session["rotation"]]
    except KeyError as exc:
        raise ReviewSessionError("session rotation no longer exists in manifest") from exc
    expected_pairs = [
        (item["fixture"], item["condition"]) for item in expected_assignments
    ]
    actual_pairs = [
        (item["fixture_id"], item["condition"]) for item in assignments
    ]
    if actual_pairs != expected_pairs:
        raise ReviewSessionError("session assignments no longer match the manifest rotation")
    if session["source_snapshot"] != _snapshot_sources(manifest, fixtures_by_id):
        raise ReviewSessionError("manifest or fixture content changed after session initialization")


def current_stage(session: dict[str, Any]) -> str:
    validate_session(session)
    assignments = session["assignments"]
    for stage in REVIEW_STAGES:
        if any(item["records"][stage] is None for item in assignments):
            return stage
    return COMPLETE


def record_response(
    session: dict[str, Any],
    fixture_id: str,
    stage: str,
    recorded_at: str,
    response: Any,
) -> dict[str, Any]:
    validate_session(session)
    if stage not in REVIEW_STAGES:
        raise ReviewSessionError(f"invalid review stage: {stage}")
    expected_stage = current_stage(session)
    if stage != expected_stage:
        raise ReviewSessionError(
            f"cannot record {stage}; current session stage is {expected_stage}"
        )
    _parse_time(recorded_at)
    if response is None:
        raise ReviewSessionError("response must not be null")

    updated = copy.deepcopy(session)
    for assignment in updated["assignments"]:
        if assignment["fixture_id"] != fixture_id:
            continue
        if assignment["records"][stage] is not None:
            raise ReviewSessionError(f"{fixture_id}/{stage} is already fixed")
        assignment["records"][stage] = {
            "recorded_at": recorded_at,
            "response": copy.deepcopy(response),
        }
        validate_session(updated)
        return updated
    raise ReviewSessionError(f"fixture is not assigned to this session: {fixture_id}")


def build_current_packets(
    session: dict[str, Any],
    manifest: dict[str, Any],
    fixtures_by_id: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    validate_session(session, manifest, fixtures_by_id)
    stage = current_stage(session)
    if stage == COMPLETE:
        return []
    packets = build_rotation_packets(
        manifest,
        fixtures_by_id,
        session["rotation"],
        stage,
    )
    pending = {
        assignment["fixture_id"]
        for assignment in session["assignments"]
        if assignment["records"][stage] is None
    }
    return [packet for packet in packets if packet["fixture_id"] in pending]


def save_session(path: str | Path, session: dict[str, Any]) -> None:
    validate_session(session)
    Path(path).write_text(
        json.dumps(session, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def load_session(path: str | Path) -> dict[str, Any]:
    try:
        session = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReviewSessionError(f"cannot load session: {path}") from exc
    if not isinstance(session, dict):
        raise ReviewSessionError("session root must be an object")
    validate_session(session)
    return session


def guard_provenance_fixed_cli(session: dict[str, Any], command: str) -> None:
    """Prevent low-level CLI bypass once a human-review provenance boundary exists."""
    if "review_provenance" in session and command in {"packets", "record"}:
        raise ReviewSessionError(
            "provenance-fixed human review must use "
            "inquiry_continuity_review_runner.py for bundle/record operations"
        )


def _load_response(path: str | Path) -> Any:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReviewSessionError(f"cannot load response JSON: {path}") from exc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a blinded, stage-gated matched review session"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("init")
    p.add_argument("session_path")
    p.add_argument("--manifest", required=True)
    p.add_argument("--repo-root", default=".")
    p.add_argument("--rotation", required=True)
    p.add_argument("--session-id", required=True)
    p.add_argument("--created-at", required=True)

    p = sub.add_parser("packets")
    p.add_argument("session_path")
    p.add_argument("--manifest", required=True)
    p.add_argument("--repo-root", default=".")

    p = sub.add_parser("record")
    p.add_argument("session_path")
    p.add_argument("--fixture-id", required=True)
    p.add_argument("--stage", choices=REVIEW_STAGES, required=True)
    p.add_argument("--recorded-at", required=True)
    p.add_argument("--response", required=True)

    p = sub.add_parser("show")
    p.add_argument("session_path")

    p = sub.add_parser("stage")
    p.add_argument("session_path")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "init":
        manifest, fixtures = load_manifest_fixtures(
            Path(args.manifest), Path(args.repo_root)
        )
        session = new_session(
            manifest,
            fixtures,
            args.rotation,
            args.session_id,
            args.created_at,
        )
        save_session(args.session_path, session)
        return 0

    session = load_session(args.session_path)
    guard_provenance_fixed_cli(session, args.command)

    if args.command == "packets":
        manifest, fixtures = load_manifest_fixtures(
            Path(args.manifest), Path(args.repo_root)
        )
        print(
            json.dumps(
                build_current_packets(session, manifest, fixtures),
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    if args.command == "record":
        updated = record_response(
            session,
            args.fixture_id,
            args.stage,
            args.recorded_at,
            _load_response(args.response),
        )
        save_session(args.session_path, updated)
        return 0

    if args.command == "show":
        print(json.dumps(session, ensure_ascii=False, indent=2))
        return 0

    if args.command == "stage":
        print(current_stage(session))
        return 0

    raise AssertionError(f"unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
