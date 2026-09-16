#!/usr/bin/env python3
"""Export completed ISSUE-000078 reviews without collapsing evidence layers.

The matched-review session intentionally stores reviewer/operator observations and
post-review semantic audit in one immutable session so the stage gate can protect
their order. This module projects that completed session into two explicitly
separate collections for durable recording. It never invents missing responses,
computes a score/winner, or upgrades synthetic review to Product Value evidence.
"""
from __future__ import annotations

import argparse
import copy
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
    validate_inquiry_session,
)
from matched_review_session import load_session

SCHEMA = "sei.inquiry-continuity-review-evidence-bundle/v0"
DEFAULT_MANIFEST = (
    "evaluation/personal-inquiry-decision/"
    "inquiry_continuity_counterfactual_matched_set_v1.json"
)


class InquiryEvidenceBundleError(ValueError):
    """Raised when a review cannot be exported without weakening its boundary."""


def _load_context(
    manifest_path: str | Path,
    repo_root: str | Path,
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    try:
        manifest, fixtures = load_manifest_fixtures(
            Path(manifest_path),
            Path(repo_root),
        )
    except PacketError as exc:
        raise InquiryEvidenceBundleError(str(exc)) from exc
    if manifest.get("schema") != INQUIRY_MANIFEST_SCHEMA:
        raise InquiryEvidenceBundleError(
            "manifest is not an Inquiry Continuity matched set"
        )
    return manifest, fixtures


def build_evidence_bundle(
    session: dict[str, Any],
    manifest: dict[str, Any],
    fixtures_by_id: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Project one complete review into separate observation and audit layers."""
    try:
        validate_inquiry_session(
            session,
            manifest,
            fixtures_by_id,
            require_complete=True,
        )
    except InquiryReviewError as exc:
        raise InquiryEvidenceBundleError(str(exc)) from exc

    observations: list[dict[str, Any]] = []
    audits: list[dict[str, Any]] = []
    for assignment in session["assignments"]:
        fixture_id = assignment["fixture_id"]
        condition = assignment["condition"]
        records = assignment["records"]
        observations.append(
            {
                "fixture_id": fixture_id,
                "condition": condition,
                "phase1": copy.deepcopy(records["phase1"]),
                "post": copy.deepcopy(records["post"]),
            }
        )
        audits.append(
            {
                "fixture_id": fixture_id,
                "condition": condition,
                "audit": copy.deepcopy(records["audit"]),
            }
        )

    return {
        "schema": SCHEMA,
        "status": "evaluation-only",
        "provenance": {
            "session_id": session["session_id"],
            "session_schema": session["schema"],
            "manifest_schema": session["manifest_schema"],
            "set_id": session["set_id"],
            "rotation": session["rotation"],
            "created_at": session["created_at"],
            "source_snapshot": copy.deepcopy(session["source_snapshot"]),
        },
        "human_review_observations": observations,
        "semantic_audits": audits,
        "evidence_boundaries": {
            "human_review_observations": (
                "recorded reviewer/operator observations; not semantic audit"
            ),
            "semantic_audits": (
                "post-review audit against revealed reference material; "
                "not reviewer answer"
            ),
            "actual_long_gap_resumption": "not-established-by-this-artifact",
            "actual_team_handoff": "not-established-by-synthetic-reader-context",
            "product_value": "not-established-by-this-artifact",
            "stable_requirement_change": "not-authorized-by-this-artifact",
        },
        "interpretation_stoplines": [
            "human review observation and semantic audit remain separate evidence layers",
            "condition labels are operator-side metadata revealed only after completion",
            "no overall score, ranking, winner, or preferred condition is computed",
            "synthetic matched review does not substitute for actual long-gap resumption",
            "synthetic reader_context=handoff does not establish actual team handoff",
            "this bundle does not authorize Product Value or Stable Requirement changes",
        ],
    }


def save_bundle(path: str | Path, bundle: dict[str, Any]) -> None:
    Path(path).write_text(
        json.dumps(bundle, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Export a completed ISSUE-000078 review while keeping human "
            "observations separate from semantic audit"
        )
    )
    parser.add_argument("session")
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--output")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    manifest, fixtures = _load_context(args.manifest, args.repo_root)
    session = load_session(args.session)
    result = build_evidence_bundle(session, manifest, fixtures)
    if args.output:
        save_bundle(args.output, result)
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
