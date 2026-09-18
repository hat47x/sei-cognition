#!/usr/bin/env python3
"""Safely run Inquiry/Decision Continuity matched human reviews.

This wrapper keeps the generic matched-review session reusable while enforcing
Issue-specific response semantics before a stage can advance. Reviewer
bundles intentionally hide condition labels and never expose later-stage
material before the shared stage gate opens it.

Human-review provenance is evaluation-only metadata. It records an opaque
reviewer id, declared prior material exposure, and human response authorship so
known or uncertain exposure cannot silently become "clean blinded" evidence.
"""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

from inquiry_continuity_packet import (
    DECISION_MANIFEST_SCHEMA,
    INQUIRY_MANIFEST_SCHEMA,
    PacketError,
    load_manifest_fixtures,
)
from inquiry_continuity_review_analysis import (
    InquiryReviewError,
    response_template as inquiry_response_template,
    validate_inquiry_response,
    validate_inquiry_session,
)
from decision_continuity_review_analysis import (
    DecisionReviewError,
    response_template as decision_response_template,
    validate_decision_response,
    validate_decision_session,
)
from inquiry_continuity_review_evidence import (
    InquiryEvidenceBundleError,
    build_evidence_bundle,
    save_bundle,
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
PROVENANCE_SCHEMA = "sei.inquiry-continuity-review-provenance/v0"
PRIOR_EXPOSURE_VALUES = (
    "none-declared",
    "known-material-exposure",
    "unknown",
)
RESPONSE_AUTHORSHIP_VALUES = (
    "human-direct",
    "human-transcribed",
)


class InquiryReviewRunnerError(ValueError):
    """Raised when the shared matched-review runner cannot safely continue."""


def new_review_provenance(
    reviewer_id: str,
    prior_exposure: str,
    response_authorship: str,
    note: str = "",
) -> dict[str, Any]:
    """Build privacy-minimal provenance for one human review session."""
    value = {
        "schema": PROVENANCE_SCHEMA,
        "status": "evaluation-only",
        "reviewer_id": reviewer_id.strip() if isinstance(reviewer_id, str) else "",
        "prior_exposure": prior_exposure,
        "response_authorship": response_authorship,
        "note": note,
    }
    _validate_provenance_value(value)
    return value


def _validate_provenance_value(value: Any) -> None:
    if not isinstance(value, dict):
        raise InquiryReviewRunnerError("review_provenance must be an object")
    required = {
        "schema",
        "status",
        "reviewer_id",
        "prior_exposure",
        "response_authorship",
        "note",
    }
    if set(value) != required:
        raise InquiryReviewRunnerError(
            "review_provenance must contain schema/status/reviewer_id/"
            "prior_exposure/response_authorship/note exactly"
        )
    if value["schema"] != PROVENANCE_SCHEMA:
        raise InquiryReviewRunnerError(
            f"review_provenance schema must be {PROVENANCE_SCHEMA}"
        )
    if value["status"] != "evaluation-only":
        raise InquiryReviewRunnerError(
            "review_provenance status must remain evaluation-only"
        )
    reviewer_id = value["reviewer_id"]
    if not isinstance(reviewer_id, str) or not reviewer_id.strip():
        raise InquiryReviewRunnerError("reviewer_id must be a non-empty opaque id")
    if value["prior_exposure"] not in PRIOR_EXPOSURE_VALUES:
        raise InquiryReviewRunnerError("prior_exposure has invalid value")
    if value["response_authorship"] not in RESPONSE_AUTHORSHIP_VALUES:
        raise InquiryReviewRunnerError("response_authorship has invalid value")
    if not isinstance(value["note"], str):
        raise InquiryReviewRunnerError("review_provenance note must be a string")


def attach_review_provenance(
    session: dict[str, Any],
    reviewer_id: str,
    prior_exposure: str,
    response_authorship: str,
    note: str = "",
) -> dict[str, Any]:
    """Attach immutable-at-review-start provenance to a fresh session."""
    if "review_provenance" in session:
        raise InquiryReviewRunnerError(
            "review_provenance is already fixed for this session"
        )
    updated = copy.deepcopy(session)
    updated["review_provenance"] = new_review_provenance(
        reviewer_id,
        prior_exposure,
        response_authorship,
        note,
    )
    return updated


def validate_review_provenance(session: dict[str, Any]) -> None:
    """Require provenance before any reviewer packet or response is accepted."""
    if "review_provenance" not in session:
        raise InquiryReviewRunnerError(
            "review_provenance is required; initialize human review via "
            "inquiry_continuity_review_runner.py"
        )
    _validate_provenance_value(session["review_provenance"])


def provenance_projection(session: dict[str, Any]) -> dict[str, Any]:
    validate_review_provenance(session)
    value = session["review_provenance"]
    clean = value["prior_exposure"] == "none-declared"
    return {
        "reviewer_id": value["reviewer_id"],
        "prior_exposure": value["prior_exposure"],
        "response_authorship": value["response_authorship"],
        "clean_blinded_candidate": clean,
        "evidence_stopline": (
            "declared no prior material exposure; still not Product Value evidence"
            if clean
            else "not eligible to be described as clean blinded review"
        ),
    }


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
    if manifest.get("schema") not in {
        INQUIRY_MANIFEST_SCHEMA,
        DECISION_MANIFEST_SCHEMA,
    }:
        raise InquiryReviewRunnerError(
            "manifest is not a supported Inquiry/Decision Continuity matched set"
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


def _validate_safe_session(
    session: dict[str, Any],
    manifest: dict[str, Any],
    fixtures_by_id: dict[str, dict[str, Any]],
    *,
    require_complete: bool = False,
) -> None:
    try:
        if manifest.get("schema") == INQUIRY_MANIFEST_SCHEMA:
            validate_inquiry_session(
                session,
                manifest,
                fixtures_by_id,
                require_complete=require_complete,
            )
        elif manifest.get("schema") == DECISION_MANIFEST_SCHEMA:
            validate_decision_session(
                session,
                manifest,
                fixtures_by_id,
                require_complete=require_complete,
            )
        else:
            raise InquiryReviewRunnerError(
                "unsupported matched-review manifest schema"
            )
    except (InquiryReviewError, DecisionReviewError) as exc:
        raise InquiryReviewRunnerError(str(exc)) from exc
    validate_review_provenance(session)


def _response_template(
    manifest: dict[str, Any],
    stage: str,
    fixture: dict[str, Any],
) -> dict[str, Any]:
    if manifest.get("schema") == INQUIRY_MANIFEST_SCHEMA:
        return inquiry_response_template(stage, fixture)
    if manifest.get("schema") == DECISION_MANIFEST_SCHEMA:
        return decision_response_template(stage, fixture)
    raise InquiryReviewRunnerError("unsupported matched-review manifest schema")


def _reviewer_bundle_schema(manifest: dict[str, Any]) -> str:
    if manifest.get("schema") == DECISION_MANIFEST_SCHEMA:
        return "sei.decision-continuity-reviewer-bundle/v0"
    return "sei.inquiry-continuity-reviewer-bundle/v0"


def reviewer_bundle(
    session: dict[str, Any],
    manifest: dict[str, Any],
    fixtures_by_id: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Return only the material a reviewer may see at the current stage."""
    _validate_safe_session(session, manifest, fixtures_by_id)
    try:
        stage = current_stage(session)
    except ReviewSessionError as exc:
        raise InquiryReviewRunnerError(str(exc)) from exc

    review_context = provenance_projection(session)
    if stage == COMPLETE:
        return {
            "schema": _reviewer_bundle_schema(manifest),
            "status": "evaluation-only",
            "session_id": session["session_id"],
            "stage": COMPLETE,
            "review_context": review_context,
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
                "response_template": _response_template(
                    manifest,
                    stage,
                    fixtures_by_id[fixture_id],
                ),
            }
        )

    return {
        "schema": _reviewer_bundle_schema(manifest),
        "status": "evaluation-only",
        "session_id": session["session_id"],
        "stage": stage,
        "review_context": review_context,
        "items": items,
        "reviewer_stoplines": [
            "Use only an opaque local reviewer_id; do not store personal name, email, or account identifiers here.",
            "Do not inspect the manifest, unassigned condition surfaces, reference state, or audit key beyond what this bundle exposes.",
            "Responses must be authored by the human reviewer; AI/operator may transcribe but must not invent human observations.",
            "Condition labels remain operator-only during review and are intentionally absent from this bundle.",
            "Known or uncertain prior exposure may still be recorded as pilot observation but must not be called clean blinded review.",
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
    """Validate provenance and Issue-specific semantics before the stage gate moves."""
    _validate_safe_session(session, manifest, fixtures_by_id)

    if fixture_id not in fixtures_by_id:
        raise InquiryReviewRunnerError(
            f"fixture is not part of this matched set: {fixture_id}"
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
        if manifest.get("schema") == INQUIRY_MANIFEST_SCHEMA:
            validate_inquiry_response(
                stage,
                response,
                fixtures_by_id[fixture_id],
            )
        elif manifest.get("schema") == DECISION_MANIFEST_SCHEMA:
            validate_decision_response(
                stage,
                response,
                fixtures_by_id[fixture_id],
            )
        else:
            raise InquiryReviewRunnerError(
                "unsupported matched-review manifest schema"
            )
        updated = record_response(
            session,
            fixture_id,
            stage,
            recorded_at,
            response,
        )
        _validate_safe_session(updated, manifest, fixtures_by_id)
    except (InquiryReviewError, DecisionReviewError, ReviewSessionError) as exc:
        raise InquiryReviewRunnerError(str(exc)) from exc
    return updated


def evidence_bundle(
    session: dict[str, Any],
    manifest: dict[str, Any],
    fixtures_by_id: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Export a completed review together with its fixed human-review provenance."""
    _validate_safe_session(
        session,
        manifest,
        fixtures_by_id,
        require_complete=True,
    )
    try:
        bundle = build_evidence_bundle(session, manifest, fixtures_by_id)
    except InquiryEvidenceBundleError as exc:
        raise InquiryReviewRunnerError(str(exc)) from exc

    exported = copy.deepcopy(bundle)
    exported["review_provenance"] = copy.deepcopy(session["review_provenance"])
    exported.setdefault("evidence_boundaries", {})[
        "clean_blinded_review"
    ] = (
        "declared-no-prior-material-exposure"
        if session["review_provenance"]["prior_exposure"] == "none-declared"
        else "not-clean-blinded"
    )
    return exported


def _load_response(path: str | Path) -> Any:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise InquiryReviewRunnerError(
            f"cannot load response JSON: {path}"
        ) from exc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run Inquiry/Decision Continuity matched human reviews safely"
    )
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST)
    parser.add_argument("--repo-root", default=".")
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init")
    init.add_argument("session_path")
    init.add_argument("--rotation", required=True)
    init.add_argument("--session-id", required=True)
    init.add_argument("--created-at", required=True)
    init.add_argument("--reviewer-id", required=True)
    init.add_argument(
        "--prior-exposure",
        choices=PRIOR_EXPOSURE_VALUES,
        required=True,
    )
    init.add_argument(
        "--response-authorship",
        choices=RESPONSE_AUTHORSHIP_VALUES,
        required=True,
    )
    init.add_argument("--provenance-note", default="")

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

    export = sub.add_parser("export-evidence")
    export.add_argument("session_path")
    export.add_argument("--output")
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
            session = attach_review_provenance(
                session,
                args.reviewer_id,
                args.prior_exposure,
                args.response_authorship,
                args.provenance_note,
            )
            _validate_safe_session(session, manifest, fixtures)
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
            "review_context": provenance_projection(updated),
        }
    elif args.command == "validate":
        _validate_safe_session(
            session,
            manifest,
            fixtures,
            require_complete=args.require_complete,
        )
        result = {
            "valid": True,
            "session_id": session["session_id"],
            "stage": current_stage(session),
            "review_context": provenance_projection(session),
            "evidence": (
                "evaluation observation only; actual long-gap/Product Value "
                "not established"
            ),
        }
    elif args.command == "export-evidence":
        bundle = evidence_bundle(session, manifest, fixtures)
        if args.output:
            save_bundle(args.output, bundle)
            result = {
                "exported": True,
                "session_id": session["session_id"],
                "schema": bundle["schema"],
                "output": str(args.output),
                "review_context": provenance_projection(session),
                "evidence": (
                    "human-review observations, semantic audit, and declared "
                    "review provenance remain separate; actual long-gap/Product "
                    "Value not established"
                ),
            }
        else:
            result = bundle
    else:
        raise AssertionError(f"unhandled command: {args.command}")

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
