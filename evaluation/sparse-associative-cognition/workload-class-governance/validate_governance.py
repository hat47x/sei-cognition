#!/usr/bin/env python3
"""Validate the evaluation-only workload-class declaration governance contract."""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
MANIFEST_PATH = BASE_DIR / "governance.json"

EXPECTED_SCHEMA = "sei.sacs-workload-class-governance/v1alpha1"
EXPECTED_ENVELOPE_REF = "../workload_policy_envelope_evidence_2026-09-19.json"
EXPECTED_ENVELOPE_ID = "b6g-grid-eval-v1"
EXPECTED_POLICIES = {"baseline", "cap128", "cap64"}
EXPECTED_CLASS_POLICY = {
    "general": "cap128",
    "structure-preserving": "baseline",
}
ALLOWED_STATES = {"candidate", "reviewed", "expired", "superseded"}
CLASS_ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

TOP_KEYS = {
    "schema",
    "status",
    "validation_as_of",
    "envelope_ref",
    "envelope_id",
    "allowed_policy_ids",
    "required_class_policy_map",
    "governance",
    "classes",
    "stop_flags",
}
GOVERNANCE_KEYS = {
    "exact_class_match_required",
    "caller_owned_provenance_required",
    "review_required_before_resolution",
    "expiry_fail_closed",
    "superseded_version_fail_closed",
    "automatic_class_inference_implemented",
    "probabilistic_classifier_implemented",
    "automatic_activation_implemented",
    "semantic_correctness_inferred",
    "production_activation_allowed",
}
ENTRY_KEYS = {
    "class_id",
    "policy_id",
    "version",
    "state",
    "owner_ref",
    "provenance_ref",
    "declared_at",
    "valid_from",
    "review_due_at",
    "expires_at",
    "review",
    "supersedes_version",
    "superseded_by_version",
    "resolution_allowed",
}
REVIEW_KEYS = {
    "state",
    "reviewer_ref",
    "reviewed_at",
    "change_review_ref",
    "evidence_refs",
}
STOP_KEYS = {
    "semantic_correctness_claimed",
    "real_world_declaration_error_rate_claimed",
    "production_activation_enabled",
    "b5_entry_gate_changed",
}


def parse_utc_second(value: object, label: str, errors: list[str]) -> datetime | None:
    if not isinstance(value, str):
        errors.append(f"{label} must be a UTC-second timestamp")
        return None
    try:
        parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=timezone.utc
        )
    except ValueError:
        errors.append(f"{label} must be a UTC-second timestamp")
        return None
    return parsed


def nonempty_canonical_ref(value: object) -> bool:
    return isinstance(value, str) and value != "" and value == value.strip()


def validate_governance(doc: dict) -> list[str]:
    errors: list[str] = []

    if set(doc) != TOP_KEYS:
        errors.append("top-level schema must remain strict")
    if doc.get("schema") != EXPECTED_SCHEMA:
        errors.append(f"schema must be {EXPECTED_SCHEMA}")
    if doc.get("status") != "evaluation-only":
        errors.append("status must remain evaluation-only")

    validation_as_of = parse_utc_second(
        doc.get("validation_as_of"), "validation_as_of", errors
    )
    if doc.get("envelope_ref") != EXPECTED_ENVELOPE_REF:
        errors.append(f"envelope_ref must remain {EXPECTED_ENVELOPE_REF}")
    if doc.get("envelope_id") != EXPECTED_ENVELOPE_ID:
        errors.append(f"envelope_id must remain {EXPECTED_ENVELOPE_ID}")

    allowed = doc.get("allowed_policy_ids")
    if (
        not isinstance(allowed, list)
        or len(allowed) != len(set(allowed))
        or set(allowed) != EXPECTED_POLICIES
    ):
        errors.append("allowed_policy_ids must remain baseline / cap128 / cap64")

    required_map = doc.get("required_class_policy_map")
    if required_map != EXPECTED_CLASS_POLICY:
        errors.append("required_class_policy_map must remain the B6g exact mapping")

    governance = doc.get("governance")
    if not isinstance(governance, dict) or set(governance) != GOVERNANCE_KEYS:
        errors.append("governance schema must remain strict")
    else:
        required_true = (
            "exact_class_match_required",
            "caller_owned_provenance_required",
            "review_required_before_resolution",
            "expiry_fail_closed",
            "superseded_version_fail_closed",
        )
        for key in required_true:
            if governance.get(key) is not True:
                errors.append(f"governance.{key} must remain true")
        required_false = (
            "automatic_class_inference_implemented",
            "probabilistic_classifier_implemented",
            "automatic_activation_implemented",
            "semantic_correctness_inferred",
            "production_activation_allowed",
        )
        for key in required_false:
            if governance.get(key) is not False:
                errors.append(f"governance.{key} must remain false")

    classes = doc.get("classes")
    if not isinstance(classes, list) or not classes:
        errors.append("classes must be a non-empty list")
        classes = []

    indexed: dict[tuple[str, int], dict] = {}
    versions_by_class: dict[str, set[int]] = {}

    for index, entry in enumerate(classes):
        label = f"classes[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{label} must be an object")
            continue
        if set(entry) != ENTRY_KEYS:
            errors.append(f"{label} schema must remain strict")

        class_id = entry.get("class_id")
        if not isinstance(class_id, str) or not CLASS_ID_RE.fullmatch(class_id):
            errors.append(f"{label}.class_id must be canonical lower-kebab-case")
            continue
        if class_id not in EXPECTED_CLASS_POLICY:
            errors.append(f"{label}.class_id must be a registered B6g class")

        policy_id = entry.get("policy_id")
        if policy_id not in EXPECTED_POLICIES:
            errors.append(f"{label}.policy_id must be an allowed static policy")
        if class_id in EXPECTED_CLASS_POLICY and policy_id != EXPECTED_CLASS_POLICY[class_id]:
            errors.append(f"{label}.policy_id must match required_class_policy_map")

        version = entry.get("version")
        if isinstance(version, bool) or not isinstance(version, int) or version < 1:
            errors.append(f"{label}.version must be an integer >= 1")
            continue

        key = (class_id, version)
        if key in indexed:
            errors.append(f"{label} duplicates class_id/version")
        indexed[key] = entry
        versions_by_class.setdefault(class_id, set()).add(version)

        state = entry.get("state")
        if state not in ALLOWED_STATES:
            errors.append(f"{label}.state must be candidate/reviewed/expired/superseded")

        for ref_key in ("owner_ref", "provenance_ref"):
            if not nonempty_canonical_ref(entry.get(ref_key)):
                errors.append(f"{label}.{ref_key} must be a non-empty canonical ref")

        declared_at = parse_utc_second(
            entry.get("declared_at"), f"{label}.declared_at", errors
        )
        valid_from = parse_utc_second(
            entry.get("valid_from"), f"{label}.valid_from", errors
        )
        review_due_at = parse_utc_second(
            entry.get("review_due_at"), f"{label}.review_due_at", errors
        )
        expires_at = parse_utc_second(
            entry.get("expires_at"), f"{label}.expires_at", errors
        )
        if declared_at and valid_from and declared_at > valid_from:
            errors.append(f"{label}.declared_at must be <= valid_from")
        if valid_from and review_due_at and review_due_at <= valid_from:
            errors.append(f"{label}.review_due_at must be later than valid_from")
        if review_due_at and expires_at and expires_at <= review_due_at:
            errors.append(f"{label}.expires_at must be later than review_due_at")

        if validation_as_of and expires_at:
            if state == "candidate" and validation_as_of >= expires_at:
                errors.append(f"{label}.candidate state cannot remain after expiry")
            if state == "reviewed":
                if valid_from and validation_as_of < valid_from:
                    errors.append(f"{label}.reviewed state cannot resolve before valid_from")
                if review_due_at and validation_as_of >= review_due_at:
                    errors.append(f"{label}.reviewed state cannot remain after review_due_at")
                if validation_as_of >= expires_at:
                    errors.append(f"{label}.reviewed state cannot remain at/after expiry")
            if state == "expired" and validation_as_of < expires_at:
                errors.append(f"{label}.expired state requires validation_as_of >= expires_at")

        resolution_allowed = entry.get("resolution_allowed")
        if not isinstance(resolution_allowed, bool):
            errors.append(f"{label}.resolution_allowed must be bool")

        review = entry.get("review")
        if state == "reviewed":
            if not isinstance(review, dict) or set(review) != REVIEW_KEYS:
                errors.append(f"{label}.reviewed state requires strict review metadata")
            else:
                if review.get("state") != "reviewed":
                    errors.append(f"{label}.review.state must be reviewed")
                for ref_key in ("reviewer_ref", "change_review_ref"):
                    if not nonempty_canonical_ref(review.get(ref_key)):
                        errors.append(f"{label}.review.{ref_key} must be a canonical ref")
                evidence_refs = review.get("evidence_refs")
                if (
                    not isinstance(evidence_refs, list)
                    or not evidence_refs
                    or len(evidence_refs) != len(set(evidence_refs))
                    or not all(nonempty_canonical_ref(ref) for ref in evidence_refs)
                ):
                    errors.append(
                        f"{label}.review.evidence_refs must be a non-empty unique canonical ref list"
                    )
                reviewed_at = parse_utc_second(
                    review.get("reviewed_at"), f"{label}.review.reviewed_at", errors
                )
                if (
                    reviewed_at
                    and declared_at
                    and reviewed_at < declared_at
                ):
                    errors.append(f"{label}.review.reviewed_at cannot predate declared_at")
                if (
                    reviewed_at
                    and validation_as_of
                    and reviewed_at > validation_as_of
                ):
                    errors.append(f"{label}.review.reviewed_at cannot follow validation_as_of")
                if (
                    reviewed_at
                    and review_due_at
                    and reviewed_at >= review_due_at
                ):
                    errors.append(f"{label}.review.reviewed_at must predate review_due_at")
            if resolution_allowed is not True:
                errors.append(f"{label}.reviewed state requires resolution_allowed=true")
        else:
            if review is not None:
                errors.append(f"{label}.{state} state must not carry active review metadata")
            if resolution_allowed is not False:
                errors.append(f"{label}.{state} state must fail closed")

        supersedes = entry.get("supersedes_version")
        superseded_by = entry.get("superseded_by_version")
        for field, value in (
            ("supersedes_version", supersedes),
            ("superseded_by_version", superseded_by),
        ):
            if value is not None and (
                isinstance(value, bool) or not isinstance(value, int) or value < 1
            ):
                errors.append(f"{label}.{field} must be null or integer >= 1")

        if version > 1 and supersedes is None:
            errors.append(f"{label}.version > 1 requires supersedes_version")
        if isinstance(supersedes, int) and not isinstance(supersedes, bool):
            if supersedes >= version:
                errors.append(f"{label}.supersedes_version must be lower than version")
        if state == "superseded":
            if not isinstance(superseded_by, int) or isinstance(superseded_by, bool):
                errors.append(f"{label}.superseded state requires superseded_by_version")
            elif superseded_by <= version:
                errors.append(f"{label}.superseded_by_version must be greater than version")
        elif superseded_by is not None:
            errors.append(f"{label}.superseded_by_version requires superseded state")

    for (class_id, version), entry in indexed.items():
        supersedes = entry.get("supersedes_version")
        if isinstance(supersedes, int) and not isinstance(supersedes, bool):
            if (class_id, supersedes) not in indexed:
                errors.append(
                    f"{class_id} v{version} supersedes missing version {supersedes}"
                )
        superseded_by = entry.get("superseded_by_version")
        if isinstance(superseded_by, int) and not isinstance(superseded_by, bool):
            target = indexed.get((class_id, superseded_by))
            if target is None:
                errors.append(
                    f"{class_id} v{version} points to missing superseding version {superseded_by}"
                )
            elif target.get("supersedes_version") != version:
                errors.append(
                    f"{class_id} v{version} supersession must be bidirectionally linked"
                )

    for class_id, versions in versions_by_class.items():
        latest = max(versions)
        for version in versions:
            entry = indexed[(class_id, version)]
            if version != latest and entry.get("resolution_allowed") is True:
                errors.append(
                    f"{class_id} v{version} is not latest and must fail closed"
                )

    stop_flags = doc.get("stop_flags")
    if not isinstance(stop_flags, dict) or set(stop_flags) != STOP_KEYS:
        errors.append("stop_flags schema must remain strict")
    else:
        for key in STOP_KEYS:
            if stop_flags.get(key) is not False:
                errors.append(f"stop_flags.{key} must remain false")

    return errors


def main() -> int:
    try:
        doc = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"workload class governance validation failed: {exc}", file=sys.stderr)
        return 1

    errors = validate_governance(doc)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("Workload class governance validated; current declarations remain candidate / fail-closed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
