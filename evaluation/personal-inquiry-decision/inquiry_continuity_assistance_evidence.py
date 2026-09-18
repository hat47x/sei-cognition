#!/usr/bin/env python3
"""Persist ISSUE-000078 E78.6 assistance review Evidence without scoring.

The exporter revalidates the complete review-start -> initial response ->
reveal receipt -> reveal response -> audit receipt chain before accepting a
post-reveal semantic audit. It preserves human observations, declared
provenance, condition mapping, and semantic hard-failure findings as separate
layers. It never computes a winner, ranking, or Product Value conclusion.
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

from inquiry_continuity_assistance_probe import (
    AUDIT_RECEIPT_SCHEMA,
    REVEAL_RECEIPT_SCHEMA,
    RESPONSE_AUTHORSHIP_VALUES,
    AssistanceProbeError,
    load_review_start_receipt,
    load_response,
    load_reveal_receipt,
    load_json,
    load_sources,
    probe_content_sha256,
    validate_audit_receipt,
    validate_probe,
    validate_response,
    validate_review_start_receipt,
)


AUDIT_RESPONSE_SCHEMA = "sei.inquiry-continuity-assistance-audit-response/v1"
EVIDENCE_SCHEMA = "sei.inquiry-continuity-assistance-evidence/v1"
FINDING_VALUES = {"observed", "not-observed", "not-applicable"}


class AssistanceEvidenceError(ValueError):
    pass


def _parse_timestamp(value: Any, field: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise AssistanceEvidenceError(
            f"{field} must be a non-empty timestamp"
        )
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise AssistanceEvidenceError(
            f"{field} must be ISO-8601"
        ) from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise AssistanceEvidenceError(
            f"{field} must include a timezone offset"
        )
    return parsed.astimezone(timezone.utc)


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _canonical_sha256(value: Any) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return _sha256(payload)


def _is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(
            character in "0123456789abcdef"
            for character in value
        )
    )


def _load_json_raw(
    path: str | Path,
    label: str,
) -> tuple[dict[str, Any], bytes]:
    try:
        raw = Path(path).read_bytes()
    except OSError as exc:
        raise AssistanceEvidenceError(
            f"cannot load {label}: {path}"
        ) from exc
    if not raw.strip():
        raise AssistanceEvidenceError(
            f"{label} must not be empty"
        )
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AssistanceEvidenceError(
            f"{label} must be valid UTF-8 JSON"
        ) from exc
    if not isinstance(value, dict):
        raise AssistanceEvidenceError(
            f"{label} root must be an object"
        )
    return value, raw


def _assignments(
    probe: dict[str, Any],
    rotation: str,
) -> list[dict[str, Any]]:
    validate_probe(probe)
    try:
        assignments = probe["assignment_rotations"][rotation]
    except KeyError as exc:
        raise AssistanceEvidenceError(
            f"unknown rotation: {rotation}"
        ) from exc
    return assignments


def _presentation_id(rotation: str, index: int) -> str:
    return f"{rotation}-P{index + 1}"


def audit_response_template(
    probe: dict[str, Any],
    rotation: str,
    audit_receipt_sha256: str,
) -> dict[str, Any]:
    if not _is_sha256(audit_receipt_sha256):
        raise AssistanceEvidenceError(
            "audit receipt SHA-256 is required"
        )
    assignments = _assignments(probe, rotation)
    failures = probe["audit_key"]["semantic_hard_failures"]
    return {
        "schema": AUDIT_RESPONSE_SCHEMA,
        "probe_sha256": probe_content_sha256(probe),
        "rotation": rotation,
        "audit_receipt_sha256": audit_receipt_sha256,
        "presentations": [
            {
                "presentation_id": _presentation_id(
                    rotation,
                    index,
                ),
                "fixture_id": assignment["fixture"],
                "condition": assignment["condition"],
                "hard_failure_findings": [
                    {
                        "failure": failure,
                        "finding": "",
                        "note": "",
                    }
                    for failure in failures
                ],
                "notes": "",
            }
            for index, assignment in enumerate(assignments)
        ],
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
    rotation: str,
    audit_receipt_sha256: str,
    audit_revealed_at: str,
) -> None:
    validate_probe(probe)
    required = {
        "schema",
        "probe_sha256",
        "rotation",
        "audit_receipt_sha256",
        "presentations",
        "audit_provenance",
        "notes",
    }
    if not isinstance(value, dict) or set(value) != required:
        raise AssistanceEvidenceError(
            "assistance audit response has invalid top-level shape"
        )
    if value["schema"] != AUDIT_RESPONSE_SCHEMA:
        raise AssistanceEvidenceError(
            f"audit response schema must be {AUDIT_RESPONSE_SCHEMA}"
        )
    if value["probe_sha256"] != probe_content_sha256(probe):
        raise AssistanceEvidenceError(
            "audit response is bound to different probe content"
        )
    if value["rotation"] != rotation:
        raise AssistanceEvidenceError(
            "audit response rotation mismatch"
        )
    if (
        not _is_sha256(audit_receipt_sha256)
        or value["audit_receipt_sha256"]
        != audit_receipt_sha256
    ):
        raise AssistanceEvidenceError(
            "audit response is bound to a different audit receipt"
        )
    if not isinstance(value["notes"], str):
        raise AssistanceEvidenceError(
            "audit response notes must be a string"
        )

    assignments = _assignments(probe, rotation)
    presentations = value["presentations"]
    if (
        not isinstance(presentations, list)
        or len(presentations) != len(assignments)
    ):
        raise AssistanceEvidenceError(
            "audit response requires one presentation per assignment"
        )
    failures = probe["audit_key"]["semantic_hard_failures"]
    for index, (presentation, assignment) in enumerate(
        zip(presentations, assignments)
    ):
        if not isinstance(presentation, dict) or set(presentation) != {
            "presentation_id",
            "fixture_id",
            "condition",
            "hard_failure_findings",
            "notes",
        }:
            raise AssistanceEvidenceError(
                "audit presentation has invalid shape"
            )
        if presentation["presentation_id"] != _presentation_id(
            rotation,
            index,
        ):
            raise AssistanceEvidenceError(
                "audit presentation order mismatch"
            )
        if presentation["fixture_id"] != assignment["fixture"]:
            raise AssistanceEvidenceError(
                "audit presentation fixture mismatch"
            )
        if presentation["condition"] != assignment["condition"]:
            raise AssistanceEvidenceError(
                "audit presentation condition mismatch"
            )
        findings = presentation["hard_failure_findings"]
        if (
            not isinstance(findings, list)
            or len(findings) != len(failures)
        ):
            raise AssistanceEvidenceError(
                "audit hard-failure findings are incomplete"
            )
        for finding, failure in zip(findings, failures):
            if not isinstance(finding, dict) or set(finding) != {
                "failure",
                "finding",
                "note",
            }:
                raise AssistanceEvidenceError(
                    "hard-failure finding has invalid shape"
                )
            if finding["failure"] != failure:
                raise AssistanceEvidenceError(
                    "hard-failure finding order/content mismatch"
                )
            if finding["finding"] not in FINDING_VALUES:
                raise AssistanceEvidenceError(
                    "hard-failure finding has invalid value"
                )
            if not isinstance(finding["note"], str):
                raise AssistanceEvidenceError(
                    "hard-failure note must be a string"
                )
        if not isinstance(presentation["notes"], str):
            raise AssistanceEvidenceError(
                "audit presentation notes must be a string"
            )

    provenance = value["audit_provenance"]
    if not isinstance(provenance, dict) or set(provenance) != {
        "auditor_id",
        "response_authorship",
        "completed_at",
        "note",
    }:
        raise AssistanceEvidenceError(
            "audit provenance has invalid shape"
        )
    if (
        not isinstance(provenance["auditor_id"], str)
        or not provenance["auditor_id"].strip()
    ):
        raise AssistanceEvidenceError(
            "audit auditor_id must be a non-empty opaque id"
        )
    if (
        provenance["response_authorship"]
        not in RESPONSE_AUTHORSHIP_VALUES
    ):
        raise AssistanceEvidenceError(
            "audit response_authorship must be human-direct or human-transcribed"
        )
    if not isinstance(provenance["note"], str):
        raise AssistanceEvidenceError(
            "audit provenance note must be a string"
        )
    completed_at = _parse_timestamp(
        provenance["completed_at"],
        "audit_provenance.completed_at",
    )
    if completed_at < _parse_timestamp(
        audit_revealed_at,
        "audit_revealed_at",
    ):
        raise AssistanceEvidenceError(
            "audit completion must not precede audit reveal"
        )


def load_audit_response(
    path: str | Path,
    probe: dict[str, Any],
    rotation: str,
    audit_receipt_sha256: str,
    audit_revealed_at: str,
) -> tuple[dict[str, Any], bytes]:
    value, raw = _load_json_raw(
        path,
        "assistance audit response",
    )
    validate_audit_response(
        value,
        probe,
        rotation,
        audit_receipt_sha256,
        audit_revealed_at,
    )
    return value, raw


def _artifact_snapshot(
    value: dict[str, Any],
    raw: bytes,
) -> dict[str, Any]:
    return {
        "raw_sha256": _sha256(raw),
        "semantic_sha256": _canonical_sha256(value),
        "value": copy.deepcopy(value),
    }


def _load_chain(
    probe: dict[str, Any],
    fixtures: dict[str, dict[str, Any]],
    rotation: str,
    review_start_receipt_path: str | Path,
    initial_response_path: str | Path,
    reveal_receipt_path: str | Path,
    reveal_response_path: str | Path,
    audit_receipt_path: str | Path,
) -> dict[str, Any]:
    review_value, review_raw = load_review_start_receipt(
        review_start_receipt_path,
        probe,
        rotation,
    )
    review_sha = _sha256(review_raw)

    initial_value, initial_raw = load_response(
        initial_response_path,
        probe,
        rotation,
        "initial",
        review_sha,
    )

    reveal_value, reveal_raw = load_reveal_receipt(
        reveal_receipt_path,
        probe,
        fixtures,
        rotation,
        review_sha,
        initial_response_path,
    )
    reveal_sha = _sha256(reveal_raw)

    reveal_response_value, reveal_response_raw = load_response(
        reveal_response_path,
        probe,
        rotation,
        "reveal",
        review_sha,
        reveal_sha,
    )

    audit_value, audit_raw = _load_json_raw(
        audit_receipt_path,
        "assistance audit receipt",
    )
    try:
        validate_audit_receipt(
            audit_value,
            probe,
            fixtures,
            rotation,
            review_sha,
            initial_response_path,
            reveal_response_path,
            reveal_value,
            reveal_raw,
        )
    except AssistanceProbeError as exc:
        raise AssistanceEvidenceError(
            f"invalid assistance audit receipt: {exc}"
        ) from exc

    return {
        "review_start_receipt": (
            review_value,
            review_raw,
        ),
        "initial_response": (
            initial_value,
            initial_raw,
        ),
        "reveal_receipt": (
            reveal_value,
            reveal_raw,
        ),
        "reveal_response": (
            reveal_response_value,
            reveal_response_raw,
        ),
        "audit_receipt": (
            audit_value,
            audit_raw,
        ),
    }


def build_evidence_bundle(
    probe: dict[str, Any],
    fixtures: dict[str, dict[str, Any]],
    rotation: str,
    review_start_receipt_path: str | Path,
    initial_response_path: str | Path,
    reveal_receipt_path: str | Path,
    reveal_response_path: str | Path,
    audit_receipt_path: str | Path,
    audit_response_path: str | Path,
) -> dict[str, Any]:
    validate_probe(probe)
    chain = _load_chain(
        probe,
        fixtures,
        rotation,
        review_start_receipt_path,
        initial_response_path,
        reveal_receipt_path,
        reveal_response_path,
        audit_receipt_path,
    )
    audit_receipt_value, audit_receipt_raw = chain[
        "audit_receipt"
    ]
    audit_receipt_sha = _sha256(audit_receipt_raw)
    audit_response, audit_response_raw = load_audit_response(
        audit_response_path,
        probe,
        rotation,
        audit_receipt_sha,
        audit_receipt_value["revealed_at"],
    )

    return {
        "schema": EVIDENCE_SCHEMA,
        "status": "evaluation-only",
        "probe_id": probe["probe_id"],
        "rotation": rotation,
        "probe_snapshot": {
            "content_sha256": probe_content_sha256(probe),
            "canonical_probe": copy.deepcopy(probe),
        },
        "source_snapshot": {
            "source_set": copy.deepcopy(probe["source_set"]),
            "cases": [
                {
                    "fixture_id": case["fixture_id"],
                    "path": case["path"],
                    "blob_sha1": case["blob_sha1"],
                }
                for case in probe["cases"]
            ],
        },
        "review_start": _artifact_snapshot(
            *chain["review_start_receipt"]
        ),
        "initial_response": _artifact_snapshot(
            *chain["initial_response"]
        ),
        "reveal_gate": _artifact_snapshot(
            *chain["reveal_receipt"]
        ),
        "reveal_response": _artifact_snapshot(
            *chain["reveal_response"]
        ),
        "audit_gate": _artifact_snapshot(
            *chain["audit_receipt"]
        ),
        "semantic_audit": _artifact_snapshot(
            audit_response,
            audit_response_raw,
        ),
        "evidence_boundaries": {
            "declared_review_provenance": (
                "opaque reviewer id, prior-exposure declaration, and "
                "human authorship declaration are metadata, not independent proof"
            ),
            "condition_comparison": (
                "preserve per-presentation observations and semantic findings; "
                "do not compute a winner, ranking, or preferred condition"
            ),
            "actual_long_gap_resumption": (
                "not-established-by-this-artifact"
            ),
            "actual_team_handoff": (
                "not-established-by-this-artifact"
            ),
            "product_value": (
                "not-established-by-this-artifact"
            ),
            "stable_requirement_change": (
                "not-authorized-by-this-artifact"
            ),
        },
        "interpretation_stoplines": [
            "initial/reveal human observations remain distinct from post-reveal semantic audit",
            "declared reviewer provenance does not independently prove blinding or human authorship",
            "no overall score, ranking, winner, or preferred assistance condition is computed",
            "synthetic assistance comparison is not actual long-gap resumption",
            "this artifact does not establish Product Value",
            "this artifact does not authorize Stable Requirement changes",
        ],
    }


def validate_evidence_bundle(bundle: Any) -> None:
    required = {
        "schema",
        "status",
        "probe_id",
        "rotation",
        "probe_snapshot",
        "source_snapshot",
        "review_start",
        "initial_response",
        "reveal_gate",
        "reveal_response",
        "audit_gate",
        "semantic_audit",
        "evidence_boundaries",
        "interpretation_stoplines",
    }
    if not isinstance(bundle, dict) or set(bundle) != required:
        raise AssistanceEvidenceError(
            "assistance Evidence bundle has invalid top-level shape"
        )
    if bundle["schema"] != EVIDENCE_SCHEMA:
        raise AssistanceEvidenceError(
            f"Evidence schema must be {EVIDENCE_SCHEMA}"
        )
    if bundle["status"] != "evaluation-only":
        raise AssistanceEvidenceError(
            "assistance Evidence must remain evaluation-only"
        )

    probe_snapshot = bundle["probe_snapshot"]
    if not isinstance(probe_snapshot, dict) or set(probe_snapshot) != {
        "content_sha256",
        "canonical_probe",
    }:
        raise AssistanceEvidenceError(
            "probe_snapshot has invalid shape"
        )
    probe = probe_snapshot["canonical_probe"]
    if not isinstance(probe, dict):
        raise AssistanceEvidenceError(
            "canonical_probe must be an object"
        )
    try:
        validate_probe(probe)
    except AssistanceProbeError as exc:
        raise AssistanceEvidenceError(
            f"canonical_probe is invalid: {exc}"
        ) from exc
    if (
        probe_snapshot["content_sha256"]
        != probe_content_sha256(probe)
    ):
        raise AssistanceEvidenceError(
            "probe snapshot digest mismatch"
        )
    if bundle["probe_id"] != probe["probe_id"]:
        raise AssistanceEvidenceError(
            "bundle probe_id differs from canonical probe"
        )
    assignments = _assignments(
        probe,
        bundle["rotation"],
    )

    source = bundle["source_snapshot"]
    expected_source = {
        "source_set": probe["source_set"],
        "cases": [
            {
                "fixture_id": case["fixture_id"],
                "path": case["path"],
                "blob_sha1": case["blob_sha1"],
            }
            for case in probe["cases"]
        ],
    }
    if source != expected_source:
        raise AssistanceEvidenceError(
            "source_snapshot differs from canonical probe"
        )

    artifact_fields = (
        "review_start",
        "initial_response",
        "reveal_gate",
        "reveal_response",
        "audit_gate",
        "semantic_audit",
    )
    for field in artifact_fields:
        snapshot = bundle[field]
        if not isinstance(snapshot, dict) or set(snapshot) != {
            "raw_sha256",
            "semantic_sha256",
            "value",
        }:
            raise AssistanceEvidenceError(
                f"{field} snapshot has invalid shape"
            )
        if not _is_sha256(snapshot["raw_sha256"]):
            raise AssistanceEvidenceError(
                f"{field} raw_sha256 must be SHA-256"
            )
        if (
            snapshot["semantic_sha256"]
            != _canonical_sha256(snapshot["value"])
        ):
            raise AssistanceEvidenceError(
                f"{field} semantic digest mismatch"
            )

    review = bundle["review_start"]["value"]
    try:
        validate_review_start_receipt(
            review,
            probe,
            bundle["rotation"],
        )
    except AssistanceProbeError as exc:
        raise AssistanceEvidenceError(
            f"review-start snapshot is invalid: {exc}"
        ) from exc
    if (
        review.get("probe_sha256")
        != probe_snapshot["content_sha256"]
        or review.get("rotation") != bundle["rotation"]
    ):
        raise AssistanceEvidenceError(
            "review-start snapshot binding mismatch"
        )
    review_raw_sha = bundle["review_start"]["raw_sha256"]

    initial = bundle["initial_response"]["value"]
    try:
        validate_response(
            initial,
            probe,
            bundle["rotation"],
            "initial",
            review_raw_sha,
        )
    except AssistanceProbeError as exc:
        raise AssistanceEvidenceError(
            f"initial response snapshot is invalid: {exc}"
        ) from exc
    if (
        initial.get("review_start_receipt_sha256")
        != review_raw_sha
        or initial.get("stage") != "initial"
        or initial.get("stage_gate_sha256") is not None
    ):
        raise AssistanceEvidenceError(
            "initial response chain binding mismatch"
        )
    initial_raw_sha = bundle["initial_response"]["raw_sha256"]

    reveal_gate = bundle["reveal_gate"]["value"]
    if (
        not isinstance(reveal_gate, dict)
        or reveal_gate.get("schema") != REVEAL_RECEIPT_SCHEMA
        or reveal_gate.get("status") != "evaluation-only"
        or reveal_gate.get("probe_id") != probe["probe_id"]
        or reveal_gate.get("probe_sha256")
        != probe_snapshot["content_sha256"]
        or reveal_gate.get("rotation") != bundle["rotation"]
        or not _is_sha256(
            reveal_gate.get("reveal_material_sha256")
        )
    ):
        raise AssistanceEvidenceError(
            "reveal gate semantic identity is invalid"
        )
    _parse_timestamp(
        reveal_gate.get("revealed_at"),
        "reveal_gate.revealed_at",
    )
    if (
        reveal_gate.get("review_start_receipt_sha256")
        != review_raw_sha
        or reveal_gate.get("fixed_initial_response_sha256")
        != initial_raw_sha
    ):
        raise AssistanceEvidenceError(
            "reveal gate chain binding mismatch"
        )
    reveal_gate_raw_sha = bundle["reveal_gate"]["raw_sha256"]

    reveal_response = bundle["reveal_response"]["value"]
    try:
        validate_response(
            reveal_response,
            probe,
            bundle["rotation"],
            "reveal",
            review_raw_sha,
            reveal_gate_raw_sha,
        )
    except AssistanceProbeError as exc:
        raise AssistanceEvidenceError(
            f"reveal response snapshot is invalid: {exc}"
        ) from exc
    if (
        reveal_response.get("review_start_receipt_sha256")
        != review_raw_sha
        or reveal_response.get("stage") != "reveal"
        or reveal_response.get("stage_gate_sha256")
        != reveal_gate_raw_sha
    ):
        raise AssistanceEvidenceError(
            "reveal response chain binding mismatch"
        )
    reveal_response_raw_sha = bundle[
        "reveal_response"
    ]["raw_sha256"]

    audit_gate = bundle["audit_gate"]["value"]
    if (
        not isinstance(audit_gate, dict)
        or audit_gate.get("schema") != AUDIT_RECEIPT_SCHEMA
        or audit_gate.get("status") != "evaluation-only"
        or audit_gate.get("probe_id") != probe["probe_id"]
        or audit_gate.get("probe_sha256")
        != probe_snapshot["content_sha256"]
        or audit_gate.get("rotation") != bundle["rotation"]
        or not _is_sha256(
            audit_gate.get("audit_material_sha256")
        )
    ):
        raise AssistanceEvidenceError(
            "audit gate semantic identity is invalid"
        )
    audit_revealed_at = _parse_timestamp(
        audit_gate.get("revealed_at"),
        "audit_gate.revealed_at",
    )
    if audit_revealed_at < _parse_timestamp(
        reveal_gate.get("revealed_at"),
        "reveal_gate.revealed_at",
    ):
        raise AssistanceEvidenceError(
            "audit gate cannot precede reveal gate"
        )
    if (
        audit_gate.get("review_start_receipt_sha256")
        != review_raw_sha
        or audit_gate.get("reveal_receipt_sha256")
        != reveal_gate_raw_sha
        or audit_gate.get("fixed_initial_response_sha256")
        != initial_raw_sha
        or audit_gate.get("fixed_reveal_response_sha256")
        != reveal_response_raw_sha
    ):
        raise AssistanceEvidenceError(
            "audit gate chain binding mismatch"
        )
    audit_gate_raw_sha = bundle["audit_gate"]["raw_sha256"]

    semantic = bundle["semantic_audit"]["value"]
    try:
        validate_audit_response(
            semantic,
            probe,
            bundle["rotation"],
            audit_gate_raw_sha,
            audit_gate["revealed_at"],
        )
    except AssistanceEvidenceError:
        raise
    if (
        semantic.get("audit_receipt_sha256")
        != audit_gate_raw_sha
        or semantic.get("probe_sha256")
        != probe_snapshot["content_sha256"]
        or semantic.get("rotation") != bundle["rotation"]
    ):
        raise AssistanceEvidenceError(
            "semantic audit chain binding mismatch"
        )
    presentations = semantic.get("presentations")
    if not isinstance(presentations, list) or len(presentations) != len(
        assignments
    ):
        raise AssistanceEvidenceError(
            "semantic audit presentation count mismatch"
        )
    for index, (presentation, assignment) in enumerate(
        zip(presentations, assignments)
    ):
        if (
            not isinstance(presentation, dict)
            or presentation.get("presentation_id")
            != _presentation_id(bundle["rotation"], index)
            or presentation.get("fixture_id")
            != assignment["fixture"]
            or presentation.get("condition")
            != assignment["condition"]
        ):
            raise AssistanceEvidenceError(
                "semantic audit presentation binding mismatch"
            )

    expected_boundaries = {
        "actual_long_gap_resumption": "not-established-by-this-artifact",
        "actual_team_handoff": "not-established-by-this-artifact",
        "product_value": "not-established-by-this-artifact",
        "stable_requirement_change": "not-authorized-by-this-artifact",
    }
    boundaries = bundle["evidence_boundaries"]
    if not isinstance(boundaries, dict) or set(boundaries) != {
        "declared_review_provenance",
        "condition_comparison",
        *expected_boundaries,
    }:
        raise AssistanceEvidenceError(
            "Evidence boundaries have invalid shape"
        )
    for field, expected in expected_boundaries.items():
        if boundaries[field] != expected:
            raise AssistanceEvidenceError(
                f"Evidence boundary {field} must remain {expected}"
            )
    if (
        not isinstance(boundaries["declared_review_provenance"], str)
        or not boundaries["declared_review_provenance"].strip()
        or not isinstance(boundaries["condition_comparison"], str)
        or not boundaries["condition_comparison"].strip()
    ):
        raise AssistanceEvidenceError(
            "Evidence explanatory boundaries must be non-empty"
        )

    stoplines = bundle["interpretation_stoplines"]
    if (
        not isinstance(stoplines, list)
        or not stoplines
        or any(
            not isinstance(line, str) or not line.strip()
            for line in stoplines
        )
        or not any("no overall score" in line for line in stoplines)
        or not any("does not establish Product Value" in line for line in stoplines)
        or not any("does not authorize Stable Requirement" in line for line in stoplines)
    ):
        raise AssistanceEvidenceError(
            "Evidence interpretation stoplines are incomplete"
        )


def save_bundle(
    path: str | Path,
    bundle: dict[str, Any],
) -> None:
    validate_evidence_bundle(bundle)
    target = Path(path)
    payload = (
        json.dumps(bundle, ensure_ascii=False, indent=2)
        + "\n"
    ).encode("utf-8")
    try:
        with target.open("xb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError as exc:
        raise AssistanceEvidenceError(
            f"refusing to overwrite existing E78.6 Evidence: {target}"
        ) from exc


def _chain_for_cli(args: argparse.Namespace) -> tuple[
    dict[str, Any],
    dict[str, dict[str, Any]],
    dict[str, Any],
]:
    probe = load_json(args.probe)
    fixtures = load_sources(probe, args.repo_root)
    chain = _load_chain(
        probe,
        fixtures,
        args.rotation,
        args.review_start_receipt,
        args.initial_response,
        args.reveal_receipt,
        args.reveal_response,
        args.audit_receipt,
    )
    return probe, fixtures, chain


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Build post-audit response and durable Evidence for "
            "ISSUE-000078 E78.6 assistance comparison"
        ),
        allow_abbrev=False,
    )
    parser.add_argument("--probe", required=True)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--rotation", required=True)
    parser.add_argument(
        "--review-start-receipt",
        required=True,
    )
    parser.add_argument("--initial-response", required=True)
    parser.add_argument("--reveal-receipt", required=True)
    parser.add_argument("--reveal-response", required=True)
    parser.add_argument("--audit-receipt", required=True)

    sub = parser.add_subparsers(
        dest="command",
        required=True,
    )
    sub.add_parser("audit-template")

    export = sub.add_parser("export-evidence")
    export.add_argument("--audit-response", required=True)
    export.add_argument("--output", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    probe, fixtures, chain = _chain_for_cli(args)
    audit_value, audit_raw = chain["audit_receipt"]
    audit_sha = _sha256(audit_raw)

    if args.command == "audit-template":
        payload = audit_response_template(
            probe,
            args.rotation,
            audit_sha,
        )
        print(
            json.dumps(
                payload,
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    if args.command == "export-evidence":
        bundle = build_evidence_bundle(
            probe,
            fixtures,
            args.rotation,
            args.review_start_receipt,
            args.initial_response,
            args.reveal_receipt,
            args.reveal_response,
            args.audit_receipt,
            args.audit_response,
        )
        save_bundle(args.output, bundle)
        print(
            json.dumps(
                {
                    "saved": str(Path(args.output)),
                    "schema": bundle["schema"],
                    "probe_id": bundle["probe_id"],
                    "rotation": bundle["rotation"],
                    "audit_receipt_sha256": audit_sha,
                    "evidence_boundary": bundle[
                        "evidence_boundaries"
                    ],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    raise AssertionError(
        f"unhandled command: {args.command}"
    )


if __name__ == "__main__":
    raise SystemExit(main())
