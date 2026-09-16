#!/usr/bin/env python3
"""Safely run ISSUE-000078 Inquiry Continuity human reviews.

This wrapper keeps the generic matched-review session reusable while enforcing
Inquiry Continuity response semantics before a stage can advance. Reviewer
bundles intentionally hide condition labels and never expose later-stage
material before the shared stage gate opens it.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from inquiry_continuity_packet import (
    INQUIRY_MANIFEST_SCHEMA,
    PacketError,
    load_manifest_fixtures,
)
from inquiry_continuity_review_analysis import (
    InquiryReviewError,
    response_template,
    validate_inquiry_response,
    validate_inquiry_session,
)
from matched_review_session import (
    COMPLETE,
    REVIEW_STAGES,
    ReviewSessionError,
    build_current_packets,
    current_stage,
    load_session,
    new_session,
    record_response,
    save_session,
)

DEFAULT_MANIFEST = (
    "evaluation/personal-inquiry-decision/"
    "inquiry_continuity_counterfactual_matched_set_v1.json"
)


class InquiryReviewRunnerError(ValueError):
    """Raised when the Issue 78 review runner cannot safely continue."""


def load_context(
    manifest_path: str | Path,
    repo_root: str | Path,
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    try:
        manifest, fixtures = load_manifest_fixtures(
            Path(manifest_path),
            Path(repo_root),
        )
    except PacketError as exc:
        raise InquiryReviewRunnerError(str(exc)) from exc
    if manifest.get("schema") != INQUIRY_MANIFEST_SCHEMA:
        raise InquiryReviewRunnerError(
            "manifest is not an Inquiry Continuity matched set"
        )
    return manifest, fixtures


def _reviewer_packet(packet: dict[str, Any]) -> dict[str, Any]:
    """Strip operator-only assignment information from one review packet."""
    hidden = {"condition", "set_id"}
    return {
        key: value
        for key, value in packet.items()
        if key not in hidden
    }


def reviewer_bundle(
    session: dict[str, Any],
    manifest: dict[str, Any],
    fixtures_by_id: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Return only the material a reviewer may see at the current stage."""
    try:
        validate_inquiry_session(session, manifest, fixtures_by_id)
        stage = current_stage(session)
    except (InquiryReviewError, ReviewSessionError) as exc:
        raise InquiryReviewRunnerError(str(exc)) from exc

    if stage == COMPLETE:
        return {
            "schema": "sei.inquiry-continuity-reviewer-bundle/v0",
            "status": "evaluation-only",
            "session_id": session["session_id"],
            "stage": COMPLETE,
            "items": [],
            "reviewer_stoplines": [
                "The review session is complete; do not reopen hidden conditions in-place.",
                "Use the analysis projection only after completed responses remain fixed.",
            ],
        }

    try:
        packets = build_current_packets(session, manifest, fixtures_by_id)
    except ReviewSessionError as exc:
        raise InquiryReviewRunnerError(str(exc)) from exc

    items = []
    for packet in packets:
        fixture_id = packet["fixture_id"]
        items.append(
            {
                "fixture_id": fixture_id,
                "packet": _reviewer_packet(packet),
                "response_template": response_template(
                    stage,
                    fixtures_by_id[fixture_id],
                ),
            }
        )

    return {
        "schema": "sei.inquiry-continuity-reviewer-bundle/v0",
        "status": "evaluation-only",
        "session_id": session["session_id"],
        "stage": stage,
        "items": items,
        "reviewer_stoplines": [
            "Do not inspect the manifest, unassigned condition surfaces, reference state, or audit key beyond what this bundle exposes.",
            "Responses must be authored from the presented material; AI/operator may transcribe but must not invent human observations.",
            "Condition labels remain operator-only during review and are intentionally absent from this bundle.",
            "A response is not Evidence merely because it is syntactically valid.",
        ],
    }


def record_checked_response(
    session: dict[str, Any],
    manifest: dict[str, Any],
    fixtures_by_id: dict[str, dict[str, Any]],
    fixture_id: str,
    stage: str,
    recorded_at: str,
    response: Any,
) -> dict[str, Any]:
    """Validate Issue 78 semantics before allowing the generic stage gate to move."""
    try:
        validate_inquiry_session(session, manifest, fixtures_by_id)
    except InquiryReviewError as exc:
        raise InquiryReviewRunnerError(str(exc)) from exc

    if fixture_id not in fixtures_by_id:
        raise InquiryReviewRunnerError(
            f"fixture is not part of this Inquiry matched set: {fixture_id}"
        )
    if stage not in REVIEW_STAGES:
        raise InquiryReviewRunnerError(f"invalid review stage: {stage}")

    expected = current_stage(session)
    if expected == COMPLETE:
        raise InquiryReviewRunnerError("review session is already complete")
    if stage != expected:
        raise InquiryReviewRunnerError(
            f"cannot record {stage}; current session stage is {expected}"
        )

    try:
        validate_inquiry_response(
            stage,
            response,
            fixtures_by_id[fixture_id],
        )
        updated = record_response(
            session,
            fixture_id,
            stage,
            recorded_at,
            response,
        )
        validate_inquiry_session(updated, manifest, fixtures_by_id)
    except (InquiryReviewError, ReviewSessionError) as exc:
        raise InquiryReviewRunnerError(str(exc)) from exc
    return updated


def _load_response(path: str | Path) -> Any:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise InquiryReviewRunnerError(
            f"cannot load response JSON: {path}"
        ) from exc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run ISSUE-000078 Inquiry Continuity human reviews safely"
    )
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST)
    parser.add_argument("--repo-root", default=".")
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init")
    init.add_argument("session_path")
    init.add_argument("--rotation", required=True)
    init.add_argument("--session-id", required=True)
    init.add_argument("--created-at", required=True)

    bundle = sub.add_parser("bundle")
    bundle.add_argument("session_path")

    record = sub.add_parser("record")
    record.add_argument("session_path")
    record.add_argument("--fixture-id", required=True)
    record.add_argument("--stage", choices=REVIEW_STAGES, required=True)
    record.add_argument("--recorded-at", required=True)
    record.add_argument("--response", required=True)

    validate = sub.add_parser("validate")
    validate.add_argument("session_path")
    validate.add_argument("--require-complete", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    manifest, fixtures = load_context(args.manifest, args.repo_root)

    if args.command == "init":
        try:
            session = new_session(
                manifest,
                fixtures,
                args.rotation,
                args.session_id,
                args.created_at,
            )
            validate_inquiry_session(session, manifest, fixtures)
        except (InquiryReviewError, ReviewSessionError) as exc:
            raise InquiryReviewRunnerError(str(exc)) from exc
        save_session(args.session_path, session)
        return 0

    session = load_session(args.session_path)

    if args.command == "bundle":
        result = reviewer_bundle(session, manifest, fixtures)
    elif args.command == "record":
        updated = record_checked_response(
            session,
            manifest,
            fixtures,
            args.fixture_id,
            args.stage,
            args.recorded_at,
            _load_response(args.response),
        )
        save_session(args.session_path, updated)
        result = {
            "recorded": True,
            "session_id": updated["session_id"],
            "next_stage": current_stage(updated),
        }
    elif args.command == "validate":
        try:
            validate_inquiry_session(
                session,
                manifest,
                fixtures,
                require_complete=args.require_complete,
            )
        except InquiryReviewError as exc:
            raise InquiryReviewRunnerError(str(exc)) from exc
        result = {
            "valid": True,
            "session_id": session["session_id"],
            "stage": current_stage(session),
            "evidence": (
                "evaluation observation only; actual long-gap/Product Value "
                "not established"
            ),
        }
    else:
        raise AssertionError(f"unhandled command: {args.command}")

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
