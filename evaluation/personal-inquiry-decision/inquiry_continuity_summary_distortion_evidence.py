#!/usr/bin/env python3
"""Export durable ISSUE-000078 E78.3 review evidence without collapsing layers.

The initial reviewer response is fixed before audit material is revealed by the
summary-distortion probe. This module records the later semantic audit as a
separate artifact and exports both layers together without inventing missing
observations, computing a score/winner, or promoting the result to Product Value
evidence.
"""
from __future__ import annotations

import argparse
import copy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
from typing import Any

from inquiry_continuity_summary_distortion_probe import (
    RESPONSE_AUTHORSHIP_VALUES,
    SummaryDistortionProbeError,
    audit_material_sha256,
    build_audit_material,
    load_audit_reveal_receipt,
    load_human_response,
    load_review_start_receipt,
    load_json,
    load_sources,
    probe_content_sha256,
    validate_human_response_against_review_start,
    validate_probe,
)

AUDIT_RESPONSE_SCHEMA = "sei.inquiry-continuity-summary-distortion-audit-response/v0"
EVIDENCE_SCHEMA = "sei.inquiry-continuity-summary-distortion-evidence/v0"
FINDING_VALUES = {"pass", "fail", "not-observed"}


class SummaryDistortionEvidenceError(ValueError):
    """Raised when E78.3 evidence cannot be recorded without weakening boundaries."""


def _case(probe: dict[str, Any], fixture_id: str) -> dict[str, Any]:
    for case in probe["cases"]:
        if case["fixture_id"] == fixture_id:
            return case
    raise SummaryDistortionEvidenceError(f"unknown fixture: {fixture_id}")


def _parse_timestamp(value: Any, field: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise SummaryDistortionEvidenceError(
            f"{field} must be a non-empty timestamp"
        )
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise SummaryDistortionEvidenceError(
            f"{field} must be ISO-8601"
        ) from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise SummaryDistortionEvidenceError(
            f"{field} must include a timezone offset"
        )
    return parsed.astimezone(timezone.utc)


def audit_response_template(
    probe: dict[str, Any],
    fixture_id: str,
    fixed_human_response_sha256: str,
    audit_reveal_receipt_sha256: str,
) -> dict[str, Any]:
    """Return an intentionally incomplete post-reveal semantic-audit template."""
    validate_probe(probe)
    _case(probe, fixture_id)
    if (
        not isinstance(fixed_human_response_sha256, str)
        or len(fixed_human_response_sha256) != 64
        or any(c not in "0123456789abcdef" for c in fixed_human_response_sha256)
    ):
        raise SummaryDistortionEvidenceError(
            "fixed_human_response_sha256 must be a lowercase SHA-256 hex digest"
        )
    if (
        not isinstance(audit_reveal_receipt_sha256, str)
        or len(audit_reveal_receipt_sha256) != 64
        or any(c not in "0123456789abcdef" for c in audit_reveal_receipt_sha256)
    ):
        raise SummaryDistortionEvidenceError(
            "audit_reveal_receipt_sha256 must be a lowercase SHA-256 hex digest"
        )
    return {
        "schema": AUDIT_RESPONSE_SCHEMA,
        "fixture_id": fixture_id,
        "probe_sha256": probe_content_sha256(probe),
        "fixed_human_response_sha256": fixed_human_response_sha256,
        "audit_reveal_receipt_sha256": audit_reveal_receipt_sha256,
        "findings": {
            dimension: "not-observed" for dimension in probe["audit_dimensions"]
        },
        "audit_provenance": {
            "auditor_id": "",
            "response_authorship": "",
            "completed_at": "",
            "note": "",
        },
        "notes": "",
    }


def validate_audit_response(
    value: Any,
    probe: dict[str, Any],
    fixture_id: str,
    fixed_human_response_sha256: str,
    audit_reveal_receipt_sha256: str,
    audit_revealed_at: str,
) -> None:
    validate_probe(probe)
    _case(probe, fixture_id)
    required = {
        "schema",
        "fixture_id",
        "probe_sha256",
        "fixed_human_response_sha256",
        "audit_reveal_receipt_sha256",
        "findings",
        "audit_provenance",
        "notes",
    }
    if not isinstance(value, dict) or set(value) != required:
        raise SummaryDistortionEvidenceError(
            "audit response must contain schema/fixture_id/"
            "fixed_human_response_sha256/findings/audit_provenance/notes exactly"
        )
    if value["schema"] != AUDIT_RESPONSE_SCHEMA:
        raise SummaryDistortionEvidenceError(
            f"audit response schema must be {AUDIT_RESPONSE_SCHEMA}"
        )
    if value["fixture_id"] != fixture_id:
        raise SummaryDistortionEvidenceError("audit response fixture_id mismatch")
    if value["probe_sha256"] != probe_content_sha256(probe):
        raise SummaryDistortionEvidenceError(
            "audit response is bound to a different probe content"
        )
    if value["fixed_human_response_sha256"] != fixed_human_response_sha256:
        raise SummaryDistortionEvidenceError(
            "audit response is bound to a different human response"
        )
    if value["audit_reveal_receipt_sha256"] != audit_reveal_receipt_sha256:
        raise SummaryDistortionEvidenceError(
            "audit response is bound to a different audit-reveal receipt"
        )

    expected_dimensions = set(probe["audit_dimensions"])
    findings = value["findings"]
    if not isinstance(findings, dict) or set(findings) != expected_dimensions:
        raise SummaryDistortionEvidenceError(
            "audit findings must contain each audit dimension exactly"
        )
    if any(result not in FINDING_VALUES for result in findings.values()):
        raise SummaryDistortionEvidenceError(
            "audit findings must be pass/fail/not-observed"
        )

    provenance = value["audit_provenance"]
    provenance_keys = {
        "auditor_id",
        "response_authorship",
        "completed_at",
        "note",
    }
    if not isinstance(provenance, dict) or set(provenance) != provenance_keys:
        raise SummaryDistortionEvidenceError("audit_provenance has invalid shape")
    if (
        not isinstance(provenance["auditor_id"], str)
        or not provenance["auditor_id"].strip()
    ):
        raise SummaryDistortionEvidenceError(
            "auditor_id must be a non-empty opaque id"
        )
    if provenance["response_authorship"] not in RESPONSE_AUTHORSHIP_VALUES:
        raise SummaryDistortionEvidenceError(
            "audit response authorship must be human-direct or human-transcribed"
        )
    completed_at = _parse_timestamp(
        provenance["completed_at"],
        "completed_at",
    )
    revealed_at = _parse_timestamp(audit_revealed_at, "audit_revealed_at")
    if completed_at < revealed_at:
        raise SummaryDistortionEvidenceError(
            "completed_at must not precede audit reveal"
        )
    if not isinstance(provenance["note"], str):
        raise SummaryDistortionEvidenceError("audit_provenance note must be a string")
    if not isinstance(value["notes"], str):
        raise SummaryDistortionEvidenceError("audit notes must be a string")


def load_audit_response(
    path: str | Path,
    probe: dict[str, Any],
    fixture_id: str,
    fixed_human_response_sha256: str,
    audit_reveal_receipt_sha256: str,
    audit_revealed_at: str,
) -> tuple[dict[str, Any], bytes]:
    try:
        raw = Path(path).read_bytes()
    except OSError as exc:
        raise SummaryDistortionEvidenceError(
            f"cannot load audit response: {path}"
        ) from exc
    if not raw.strip():
        raise SummaryDistortionEvidenceError("audit response must not be empty")
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SummaryDistortionEvidenceError(
            "audit response must be valid UTF-8 JSON"
        ) from exc
    validate_audit_response(
        value,
        probe,
        fixture_id,
        fixed_human_response_sha256,
        audit_reveal_receipt_sha256,
        audit_revealed_at,
    )
    return value, raw


def build_evidence_bundle(
    probe: dict[str, Any],
    fixtures: dict[str, dict[str, Any]],
    fixture_id: str,
    human_response_path: str | Path,
    review_start_receipt_path: str | Path,
    audit_reveal_receipt_path: str | Path,
    audit_response_path: str | Path,
) -> dict[str, Any]:
    """Build one E78.3 bundle with reviewer observation and semantic audit separated."""
    if fixture_id not in fixtures:
        raise SummaryDistortionEvidenceError(f"unknown fixture: {fixture_id}")
    case = _case(probe, fixture_id)
    try:
        human_response, human_raw = load_human_response(
            human_response_path,
            probe,
        )
    except SummaryDistortionProbeError as exc:
        raise SummaryDistortionEvidenceError(str(exc)) from exc
    fixed_human_response_sha256 = hashlib.sha256(human_raw).hexdigest()
    try:
        review_receipt_value, review_receipt_raw = load_review_start_receipt(
            review_start_receipt_path,
            probe,
            fixture_id,
        )
        validate_human_response_against_review_start(
            human_response,
            probe,
            fixture_id,
            review_receipt_value,
            review_receipt_raw,
        )
    except SummaryDistortionProbeError as exc:
        raise SummaryDistortionEvidenceError(str(exc)) from exc
    review_start_receipt_sha256 = hashlib.sha256(
        review_receipt_raw
    ).hexdigest()
    material = build_audit_material(probe, fixtures, fixture_id)
    material_digest = audit_material_sha256(material)
    try:
        receipt_value, receipt_raw = load_audit_reveal_receipt(
            audit_reveal_receipt_path,
            probe,
            fixture_id,
            fixed_human_response_sha256,
            material_digest,
        )
    except SummaryDistortionProbeError as exc:
        raise SummaryDistortionEvidenceError(str(exc)) from exc
    audit_reveal_receipt_sha256 = hashlib.sha256(receipt_raw).hexdigest()
    audit_response, audit_raw = load_audit_response(
        audit_response_path,
        probe,
        fixture_id,
        fixed_human_response_sha256,
        audit_reveal_receipt_sha256,
        receipt_value["revealed_at"],
    )

    return {
        "schema": EVIDENCE_SCHEMA,
        "status": "evaluation-only",
        "probe_id": probe["probe_id"],
        "fixture_id": fixture_id,
        "probe_snapshot": {
            "content_sha256": probe_content_sha256(probe),
            "distorted_summary": case["distorted_summary"],
            "distorted_next_question": case["distorted_next_question"],
            "review_questions": copy.deepcopy(probe["review_questions"]),
            "audit_dimensions": copy.deepcopy(probe["audit_dimensions"]),
        },
        "source_snapshot": {
            "path": case["path"],
            "blob_sha1": case["blob_sha1"],
        },
        "review_start": {
            "receipt_sha256": review_start_receipt_sha256,
            "started_at": review_receipt_value["started_at"],
            "reviewer_id": review_receipt_value["reviewer_id"],
            "prior_exposure": review_receipt_value["prior_exposure"],
            "response_authorship": review_receipt_value["response_authorship"],
            "boundary": (
                "declared reviewer conditions persisted before review stimulus "
                "was emitted; declarations are not independent proof"
            ),
        },
        "human_review_observation": {
            "response_sha256": fixed_human_response_sha256,
            "answers": copy.deepcopy(human_response["answers"]),
            "operator_observation": copy.deepcopy(
                human_response["operator_observation"]
            ),
            "notes": human_response["notes"],
        },
        "review_provenance": copy.deepcopy(
            human_response["review_provenance"]
        ),
        "audit_reveal": {
            "receipt_sha256": audit_reveal_receipt_sha256,
            "audit_material_sha256": material_digest,
            "revealed_at": receipt_value["revealed_at"],
            "boundary": (
                "machine-generated receipt persisted before audit/reference "
                "material was emitted"
            ),
        },
        "semantic_audit": {
            "audit_response_sha256": hashlib.sha256(audit_raw).hexdigest(),
            "findings": copy.deepcopy(audit_response["findings"]),
            "audit_provenance": copy.deepcopy(
                audit_response["audit_provenance"]
            ),
            "notes": audit_response["notes"],
            "distortion_key": copy.deepcopy(case["distortion_key"]),
            "reference_state": copy.deepcopy(fixtures[fixture_id]["reference_state"]),
            "post_interruption_evidence": copy.deepcopy(
                fixtures[fixture_id]["scenario"]["post_interruption_evidence"]
            ),
        },
        "evidence_boundaries": {
            "human_review_observation": (
                "reviewer response fixed before distortion key/reference material reveal"
            ),
            "semantic_audit": (
                "post-reveal audit; not part of the original reviewer response"
            ),
            "declared_provenance": (
                "opaque ids and authorship/exposure declarations are metadata, "
                "not independent proof of blinding or human authorship"
            ),
            "actual_long_gap_resumption": "not-established-by-this-artifact",
            "actual_team_handoff": "not-established-by-this-artifact",
            "product_value": "not-established-by-this-artifact",
            "stable_requirement_change": "not-authorized-by-this-artifact",
        },
        "interpretation_stoplines": [
            "review start, review observation, audit reveal, and semantic audit remain separate evidence layers",
            "review-start receipt fixes declared reviewer conditions before stimulus output",
            "audit-reveal receipt binds the fixed response before reference material is emitted",
            "probe content digest binds the review and audit to the exact evaluation stimulus",
            "no overall score, ranking, winner, or preferred condition is computed",
            "a completed synthetic distortion review is not actual long-gap resumption",
            "correction success alone does not establish SEI-specific value over raw chat or notes",
            "this artifact does not authorize Product Value or Stable Requirement changes",
        ],
    }


def save_bundle(path: str | Path, bundle: dict[str, Any]) -> None:
    """Persist one E78.3 evidence artifact without replacing earlier evidence."""
    target = Path(path)
    payload = json.dumps(bundle, ensure_ascii=False, indent=2) + "\n"
    try:
        with target.open("x", encoding="utf-8") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError as exc:
        raise SummaryDistortionEvidenceError(
            f"refusing to overwrite existing E78.3 evidence: {target}"
        ) from exc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Record ISSUE-000078 E78.3 human-review and semantic-audit evidence "
            "without collapsing the two layers"
        )
    )
    parser.add_argument("--probe", required=True)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--fixture-id", required=True)
    sub = parser.add_subparsers(dest="command", required=True)

    template = sub.add_parser("audit-template")
    template.add_argument("--response", required=True)
    template.add_argument("--review-receipt", required=True)
    template.add_argument("--receipt", required=True)

    export = sub.add_parser("export-evidence")
    export.add_argument("--response", required=True)
    export.add_argument("--review-receipt", required=True)
    export.add_argument("--receipt", required=True)
    export.add_argument("--audit-response", required=True)
    export.add_argument("--output")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    probe = load_json(args.probe)
    try:
        fixtures = load_sources(probe, args.repo_root)
    except SummaryDistortionProbeError as exc:
        raise SummaryDistortionEvidenceError(str(exc)) from exc
    if args.fixture_id not in fixtures:
        raise SummaryDistortionEvidenceError(
            f"unknown fixture: {args.fixture_id}"
        )

    try:
        _, human_raw = load_human_response(args.response, probe)
    except SummaryDistortionProbeError as exc:
        raise SummaryDistortionEvidenceError(str(exc)) from exc
    fixed_human_response_sha256 = hashlib.sha256(human_raw).hexdigest()
    try:
        review_receipt_value, review_receipt_raw = load_review_start_receipt(
            args.review_receipt,
            probe,
            args.fixture_id,
        )
        validate_human_response_against_review_start(
            json.loads(human_raw.decode("utf-8")),
            probe,
            args.fixture_id,
            review_receipt_value,
            review_receipt_raw,
        )
    except SummaryDistortionProbeError as exc:
        raise SummaryDistortionEvidenceError(str(exc)) from exc
    material = build_audit_material(probe, fixtures, args.fixture_id)
    material_digest = audit_material_sha256(material)
    try:
        receipt_value, receipt_raw = load_audit_reveal_receipt(
            args.receipt,
            probe,
            args.fixture_id,
            fixed_human_response_sha256,
            material_digest,
        )
    except SummaryDistortionProbeError as exc:
        raise SummaryDistortionEvidenceError(str(exc)) from exc
    audit_reveal_receipt_sha256 = hashlib.sha256(receipt_raw).hexdigest()

    if args.command == "audit-template":
        result = audit_response_template(
            probe,
            args.fixture_id,
            fixed_human_response_sha256,
            audit_reveal_receipt_sha256,
        )
    elif args.command == "export-evidence":
        result = build_evidence_bundle(
            probe,
            fixtures,
            args.fixture_id,
            args.response,
            args.review_receipt,
            args.receipt,
            args.audit_response,
        )
    else:
        raise AssertionError(f"unhandled command: {args.command}")

    if args.command == "export-evidence" and args.output:
        save_bundle(args.output, result)
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
