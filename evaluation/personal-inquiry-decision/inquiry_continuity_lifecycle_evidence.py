#!/usr/bin/env python3
"""Persist ISSUE-000078 E78.7 lifecycle review Evidence without ranking.

The exporter revalidates the review-start -> structured response -> audit-reveal
chain before accepting post-reveal semantic/product failure observations.
Product-local lifecycle handling remains distinct from canonical Inquiry status.
No overall score, winner, preferred condition, Universal status promotion,
Product Value conclusion, or Stable Requirement authorization is produced.
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

from inquiry_continuity_lifecycle_probe import (
    RESPONSE_AUTHORSHIP_VALUES,
    LifecycleProbeError,
    audit_material,
    load_json,
    load_response,
    load_review_start_receipt,
    probe_content_sha256,
    validate_audit_receipt_data,
    validate_probe,
    validate_response,
    validate_review_start_receipt,
)


AUDIT_RESPONSE_SCHEMA = "sei.inquiry-continuity-lifecycle-audit-response/v1"
EVIDENCE_SCHEMA = "sei.inquiry-continuity-lifecycle-evidence/v1"
FINDING_VALUES = {
    "observed",
    "not-observed",
    "not-applicable",
}


class LifecycleEvidenceError(ValueError):
    pass


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


def _parse_timestamp(
    value: Any,
    field: str,
) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise LifecycleEvidenceError(
            f"{field} must be a non-empty timestamp"
        )
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise LifecycleEvidenceError(
            f"{field} must be ISO-8601"
        ) from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise LifecycleEvidenceError(
            f"{field} must include a timezone offset"
        )
    return parsed.astimezone(timezone.utc)


def _load_json_raw(
    path: str | Path,
    label: str,
) -> tuple[dict[str, Any], bytes]:
    try:
        raw = Path(path).read_bytes()
    except OSError as exc:
        raise LifecycleEvidenceError(
            f"cannot load {label}: {path}"
        ) from exc
    if not raw.strip():
        raise LifecycleEvidenceError(
            f"{label} must not be empty"
        )
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise LifecycleEvidenceError(
            f"{label} must be UTF-8 JSON"
        ) from exc
    if not isinstance(value, dict):
        raise LifecycleEvidenceError(
            f"{label} root must be an object"
        )
    return value, raw


def _rotation(
    probe: dict[str, Any],
    rotation: str,
) -> list[str]:
    validate_probe(probe)
    try:
        return probe["assignment_rotations"][rotation]
    except KeyError as exc:
        raise LifecycleEvidenceError(
            f"unknown rotation: {rotation}"
        ) from exc


def _presentation_id(
    rotation: str,
    index: int,
) -> str:
    return f"{rotation}-P{index + 1}"


def audit_response_template(
    probe: dict[str, Any],
    rotation: str,
    audit_receipt_sha256: str,
) -> dict[str, Any]:
    if not _is_sha256(audit_receipt_sha256):
        raise LifecycleEvidenceError(
            "audit receipt SHA-256 is required"
        )
    conditions = _rotation(probe, rotation)
    hard_failures = probe["audit_key"][
        "semantic_hard_failures"
    ]
    failure_signals = probe["audit_key"][
        "product_failure_signals"
    ]
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
                "condition": condition,
                "semantic_hard_failure_findings": [
                    {
                        "failure": failure,
                        "finding": "",
                        "note": "",
                    }
                    for failure in hard_failures
                ],
                "product_failure_signal_findings": [
                    {
                        "signal": signal,
                        "finding": "",
                        "note": "",
                    }
                    for signal in failure_signals
                ],
                "notes": "",
            }
            for index, condition in enumerate(conditions)
        ],
        "acceptable_outcome_notes": [
            {
                "outcome": outcome,
                "note": "",
            }
            for outcome in probe["audit_key"][
                "acceptable_outcomes"
            ]
        ],
        "audit_provenance": {
            "auditor_id": "",
            "response_authorship": "",
            "completed_at": "",
            "note": "",
        },
        "notes": "",
    }


def _validate_findings(
    findings: Any,
    expected: list[str],
    label_key: str,
    label: str,
) -> None:
    if (
        not isinstance(findings, list)
        or len(findings) != len(expected)
    ):
        raise LifecycleEvidenceError(
            f"{label} findings are incomplete"
        )
    for finding, expected_label in zip(
        findings,
        expected,
    ):
        if not isinstance(finding, dict) or set(finding) != {
            label_key,
            "finding",
            "note",
        }:
            raise LifecycleEvidenceError(
                f"{label} finding has invalid shape"
            )
        if finding[label_key] != expected_label:
            raise LifecycleEvidenceError(
                f"{label} finding order/content mismatch"
            )
        if finding["finding"] not in FINDING_VALUES:
            raise LifecycleEvidenceError(
                f"{label} finding has invalid value"
            )
        if not isinstance(finding["note"], str):
            raise LifecycleEvidenceError(
                f"{label} finding note must be a string"
            )


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
        "acceptable_outcome_notes",
        "audit_provenance",
        "notes",
    }
    if not isinstance(value, dict) or set(value) != required:
        raise LifecycleEvidenceError(
            "lifecycle audit response has invalid top-level shape"
        )
    if value["schema"] != AUDIT_RESPONSE_SCHEMA:
        raise LifecycleEvidenceError(
            f"audit response schema must be {AUDIT_RESPONSE_SCHEMA}"
        )
    if (
        value["probe_sha256"] != probe_content_sha256(probe)
        or value["rotation"] != rotation
        or value["audit_receipt_sha256"]
        != audit_receipt_sha256
        or not _is_sha256(audit_receipt_sha256)
    ):
        raise LifecycleEvidenceError(
            "lifecycle audit response binding mismatch"
        )
    if not isinstance(value["notes"], str):
        raise LifecycleEvidenceError(
            "lifecycle audit response notes must be a string"
        )

    conditions = _rotation(probe, rotation)
    presentations = value["presentations"]
    if (
        not isinstance(presentations, list)
        or len(presentations) != len(conditions)
    ):
        raise LifecycleEvidenceError(
            "audit response requires one presentation per condition"
        )
    hard_failures = probe["audit_key"][
        "semantic_hard_failures"
    ]
    failure_signals = probe["audit_key"][
        "product_failure_signals"
    ]
    for index, (presentation, condition) in enumerate(
        zip(presentations, conditions)
    ):
        if not isinstance(presentation, dict) or set(presentation) != {
            "presentation_id",
            "condition",
            "semantic_hard_failure_findings",
            "product_failure_signal_findings",
            "notes",
        }:
            raise LifecycleEvidenceError(
                "audit presentation has invalid shape"
            )
        if (
            presentation["presentation_id"]
            != _presentation_id(rotation, index)
            or presentation["condition"] != condition
        ):
            raise LifecycleEvidenceError(
                "audit presentation binding mismatch"
            )
        _validate_findings(
            presentation[
                "semantic_hard_failure_findings"
            ],
            hard_failures,
            "failure",
            "semantic hard-failure",
        )
        _validate_findings(
            presentation[
                "product_failure_signal_findings"
            ],
            failure_signals,
            "signal",
            "Product failure signal",
        )
        if not isinstance(presentation["notes"], str):
            raise LifecycleEvidenceError(
                "audit presentation notes must be a string"
            )

    outcomes = value["acceptable_outcome_notes"]
    expected_outcomes = probe["audit_key"][
        "acceptable_outcomes"
    ]
    if (
        not isinstance(outcomes, list)
        or len(outcomes) != len(expected_outcomes)
    ):
        raise LifecycleEvidenceError(
            "acceptable outcome notes are incomplete"
        )
    for item, outcome in zip(
        outcomes,
        expected_outcomes,
    ):
        if (
            not isinstance(item, dict)
            or set(item) != {"outcome", "note"}
            or item["outcome"] != outcome
            or not isinstance(item["note"], str)
        ):
            raise LifecycleEvidenceError(
                "acceptable outcome note has invalid shape/order"
            )

    provenance = value["audit_provenance"]
    if not isinstance(provenance, dict) or set(provenance) != {
        "auditor_id",
        "response_authorship",
        "completed_at",
        "note",
    }:
        raise LifecycleEvidenceError(
            "audit provenance has invalid shape"
        )
    if (
        not isinstance(provenance["auditor_id"], str)
        or not provenance["auditor_id"].strip()
        or provenance["response_authorship"]
        not in RESPONSE_AUTHORSHIP_VALUES
        or not isinstance(provenance["note"], str)
    ):
        raise LifecycleEvidenceError(
            "audit provenance is invalid"
        )
    if _parse_timestamp(
        provenance["completed_at"],
        "audit_provenance.completed_at",
    ) < _parse_timestamp(
        audit_revealed_at,
        "audit_revealed_at",
    ):
        raise LifecycleEvidenceError(
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
        "lifecycle audit response",
    )
    validate_audit_response(
        value,
        probe,
        rotation,
        audit_receipt_sha256,
        audit_revealed_at,
    )
    return value, raw


def _snapshot(
    value: dict[str, Any],
    raw: bytes,
) -> dict[str, Any]:
    try:
        raw_json = raw.decode("utf-8")
        decoded = json.loads(raw_json)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise LifecycleEvidenceError(
            "snapshot raw bytes must be UTF-8 JSON"
        ) from exc
    if decoded != value:
        raise LifecycleEvidenceError(
            "snapshot raw JSON differs from semantic value"
        )
    return {
        "raw_json": raw_json,
        "raw_sha256": _sha256(raw),
        "semantic_sha256": _canonical_sha256(value),
        "value": copy.deepcopy(value),
    }


def _load_chain(
    probe: dict[str, Any],
    rotation: str,
    review_start_path: str | Path,
    response_path: str | Path,
    audit_receipt_path: str | Path,
) -> dict[str, tuple[dict[str, Any], bytes]]:
    review_value, review_raw = load_review_start_receipt(
        review_start_path,
        probe,
        rotation,
    )
    review_sha = _sha256(review_raw)
    response_value, response_raw = load_response(
        response_path,
        probe,
        rotation,
        review_sha,
    )
    audit_value, audit_raw = _load_json_raw(
        audit_receipt_path,
        "lifecycle audit receipt",
    )
    try:
        validate_audit_receipt_data(
            audit_value,
            probe,
            rotation,
            review_value,
            review_raw,
            response_value,
            response_raw,
        )
    except LifecycleProbeError as exc:
        raise LifecycleEvidenceError(
            f"invalid lifecycle audit receipt: {exc}"
        ) from exc
    return {
        "review_start": (review_value, review_raw),
        "response": (response_value, response_raw),
        "audit_gate": (audit_value, audit_raw),
    }


def build_evidence_bundle(
    probe: dict[str, Any],
    rotation: str,
    review_start_path: str | Path,
    response_path: str | Path,
    audit_receipt_path: str | Path,
    audit_response_path: str | Path,
) -> dict[str, Any]:
    validate_probe(probe)
    chain = _load_chain(
        probe,
        rotation,
        review_start_path,
        response_path,
        audit_receipt_path,
    )
    audit_value, audit_raw = chain["audit_gate"]
    audit_sha = _sha256(audit_raw)
    semantic, semantic_raw = load_audit_response(
        audit_response_path,
        probe,
        rotation,
        audit_sha,
        audit_value["revealed_at"],
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
        "review_start": _snapshot(*chain["review_start"]),
        "review_response": _snapshot(*chain["response"]),
        "audit_gate": _snapshot(*chain["audit_gate"]),
        "semantic_audit": _snapshot(
            semantic,
            semantic_raw,
        ),
        "evidence_boundaries": {
            "review_provenance": (
                "declared reviewer/auditor metadata is preserved but "
                "does not independently prove blinding or human authorship"
            ),
            "condition_comparison": (
                "per-condition observations are preserved without "
                "winner, ranking, or preferred condition"
            ),
            "universal_status_type": "not-authorized-by-this-artifact",
            "product_value": "not-established-by-this-artifact",
            "stable_requirement_change": "not-authorized-by-this-artifact",
        },
        "interpretation_stoplines": [
            "Product-local attention state is not canonical Inquiry status",
            "closed without Decision is not resolution, Decision, or truth",
            "acceptable outcome notes are not a ranking or selected winner",
            "a single reviewer cannot separate presentation-order effects from condition effects",
            "this synthetic lifecycle comparison is not actual long-gap resumption",
            "this artifact does not establish Product Value",
            "this artifact does not authorize Stable Requirement or Universal status changes",
        ],
    }


def validate_evidence_bundle(
    bundle: Any,
) -> None:
    required = {
        "schema",
        "status",
        "probe_id",
        "rotation",
        "probe_snapshot",
        "review_start",
        "review_response",
        "audit_gate",
        "semantic_audit",
        "evidence_boundaries",
        "interpretation_stoplines",
    }
    if not isinstance(bundle, dict) or set(bundle) != required:
        raise LifecycleEvidenceError(
            "lifecycle Evidence bundle has invalid top-level shape"
        )
    if (
        bundle["schema"] != EVIDENCE_SCHEMA
        or bundle["status"] != "evaluation-only"
    ):
        raise LifecycleEvidenceError(
            "lifecycle Evidence identity is invalid"
        )
    probe_snapshot = bundle["probe_snapshot"]
    if not isinstance(probe_snapshot, dict) or set(probe_snapshot) != {
        "content_sha256",
        "canonical_probe",
    }:
        raise LifecycleEvidenceError(
            "probe_snapshot has invalid shape"
        )
    probe = probe_snapshot["canonical_probe"]
    if not isinstance(probe, dict):
        raise LifecycleEvidenceError(
            "canonical_probe must be an object"
        )
    try:
        validate_probe(probe)
    except LifecycleProbeError as exc:
        raise LifecycleEvidenceError(
            f"canonical probe is invalid: {exc}"
        ) from exc
    if (
        probe_snapshot["content_sha256"]
        != probe_content_sha256(probe)
        or bundle["probe_id"] != probe["probe_id"]
    ):
        raise LifecycleEvidenceError(
            "probe snapshot binding mismatch"
        )
    _rotation(probe, bundle["rotation"])

    for field in (
        "review_start",
        "review_response",
        "audit_gate",
        "semantic_audit",
    ):
        snapshot = bundle[field]
        if not isinstance(snapshot, dict) or set(snapshot) != {
            "raw_json",
            "raw_sha256",
            "semantic_sha256",
            "value",
        }:
            raise LifecycleEvidenceError(
                f"{field} snapshot has invalid shape"
            )
        raw_json = snapshot["raw_json"]
        if not isinstance(raw_json, str):
            raise LifecycleEvidenceError(
                f"{field}.raw_json must be a string"
            )
        raw = raw_json.encode("utf-8")
        if (
            not _is_sha256(snapshot["raw_sha256"])
            or snapshot["raw_sha256"] != _sha256(raw)
        ):
            raise LifecycleEvidenceError(
                f"{field} raw SHA-256 mismatch"
            )
        try:
            decoded = json.loads(raw_json)
        except json.JSONDecodeError as exc:
            raise LifecycleEvidenceError(
                f"{field}.raw_json must be valid JSON"
            ) from exc
        if decoded != snapshot["value"]:
            raise LifecycleEvidenceError(
                f"{field} raw JSON differs from semantic value"
            )
        if (
            snapshot["semantic_sha256"]
            != _canonical_sha256(snapshot["value"])
        ):
            raise LifecycleEvidenceError(
                f"{field} semantic digest mismatch"
            )

    review = bundle["review_start"]["value"]
    review_raw = bundle["review_start"][
        "raw_json"
    ].encode("utf-8")
    try:
        validate_review_start_receipt(
            review,
            probe,
            bundle["rotation"],
        )
    except LifecycleProbeError as exc:
        raise LifecycleEvidenceError(
            f"review-start snapshot is invalid: {exc}"
        ) from exc
    review_sha = bundle["review_start"]["raw_sha256"]

    response = bundle["review_response"]["value"]
    response_raw = bundle["review_response"][
        "raw_json"
    ].encode("utf-8")
    try:
        validate_response(
            response,
            probe,
            bundle["rotation"],
            review_sha,
        )
    except LifecycleProbeError as exc:
        raise LifecycleEvidenceError(
            f"review response snapshot is invalid: {exc}"
        ) from exc

    audit_gate = bundle["audit_gate"]["value"]
    try:
        validate_audit_receipt_data(
            audit_gate,
            probe,
            bundle["rotation"],
            review,
            review_raw,
            response,
            response_raw,
        )
    except LifecycleProbeError as exc:
        raise LifecycleEvidenceError(
            f"audit gate snapshot is invalid: {exc}"
        ) from exc
    audit_sha = bundle["audit_gate"]["raw_sha256"]

    semantic = bundle["semantic_audit"]["value"]
    validate_audit_response(
        semantic,
        probe,
        bundle["rotation"],
        audit_sha,
        audit_gate["revealed_at"],
    )

    boundaries = bundle["evidence_boundaries"]
    expected = {
        "universal_status_type": "not-authorized-by-this-artifact",
        "product_value": "not-established-by-this-artifact",
        "stable_requirement_change": "not-authorized-by-this-artifact",
    }
    if not isinstance(boundaries, dict) or set(boundaries) != {
        "review_provenance",
        "condition_comparison",
        *expected,
    }:
        raise LifecycleEvidenceError(
            "lifecycle Evidence boundaries have invalid shape"
        )
    for field, value in expected.items():
        if boundaries[field] != value:
            raise LifecycleEvidenceError(
                f"lifecycle Evidence boundary {field} changed"
            )
    for field in (
        "review_provenance",
        "condition_comparison",
    ):
        if (
            not isinstance(boundaries[field], str)
            or not boundaries[field].strip()
        ):
            raise LifecycleEvidenceError(
                f"{field} boundary must be non-empty"
            )

    stoplines = bundle["interpretation_stoplines"]
    if (
        not isinstance(stoplines, list)
        or not stoplines
        or any(
            not isinstance(line, str) or not line.strip()
            for line in stoplines
        )
        or not any(
            "not canonical Inquiry status" in line
            for line in stoplines
        )
        or not any(
            "does not establish Product Value" in line
            for line in stoplines
        )
        or not any(
            "does not authorize Stable Requirement" in line
            for line in stoplines
        )
    ):
        raise LifecycleEvidenceError(
            "lifecycle Evidence stoplines are incomplete"
        )


def save_bundle(
    path: str | Path,
    bundle: dict[str, Any],
) -> None:
    validate_evidence_bundle(bundle)
    target = Path(path)
    payload = (
        json.dumps(
            bundle,
            ensure_ascii=False,
            indent=2,
        )
        + "\n"
    ).encode("utf-8")
    try:
        with target.open("xb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError as exc:
        raise LifecycleEvidenceError(
            f"refusing to overwrite existing lifecycle Evidence: {target}"
        ) from exc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Build post-audit response and durable Evidence for "
            "ISSUE-000078 E78.7 lifecycle comparison"
        ),
        allow_abbrev=False,
    )
    parser.add_argument("--probe", required=True)
    parser.add_argument("--rotation", required=True)
    parser.add_argument(
        "--review-start-receipt",
        required=True,
    )
    parser.add_argument("--response", required=True)
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


def main(
    argv: list[str] | None = None,
) -> int:
    args = build_parser().parse_args(argv)
    probe = load_json(args.probe)
    chain = _load_chain(
        probe,
        args.rotation,
        args.review_start_receipt,
        args.response,
        args.audit_receipt,
    )
    audit_value, audit_raw = chain["audit_gate"]
    audit_sha = _sha256(audit_raw)

    if args.command == "audit-template":
        print(
            json.dumps(
                audit_response_template(
                    probe,
                    args.rotation,
                    audit_sha,
                ),
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    if args.command == "export-evidence":
        bundle = build_evidence_bundle(
            probe,
            args.rotation,
            args.review_start_receipt,
            args.response,
            args.audit_receipt,
            args.audit_response,
        )
        save_bundle(
            args.output,
            bundle,
        )
        print(
            json.dumps(
                {
                    "saved": str(Path(args.output)),
                    "schema": bundle["schema"],
                    "probe_id": bundle["probe_id"],
                    "rotation": bundle["rotation"],
                    "audit_receipt_sha256": audit_sha,
                    "evidence_boundaries": bundle[
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
