#!/usr/bin/env python3
"""Validate provenance-bound cross-stage B5 review decision records.

The artifact records an evidence disposition after interpretation. It does not
open the B5 gate, select a winning variant, claim semantic truth, or modify a
production default.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
SACS_DIR = HERE.parent
INTERPRETATION_DIR = SACS_DIR / "cross-stage-interpretation"
RESULT_DIR = SACS_DIR / "cross-stage-result"
RUN_DIR = SACS_DIR / "cross-stage-run"
FREEZE_DIR = SACS_DIR / "cross-stage-freeze"

DECISION_PATH = HERE / "decision.json"
INTERPRETATION_PATH = INTERPRETATION_DIR / "interpretation.json"
RESULT_PATH = RESULT_DIR / "result.json"
RUN_PATH = RUN_DIR / "evaluation_run.json"
PREREG_PATH = SACS_DIR / "cross_stage_benchmark_preregistration.json"

for path in (
    SACS_DIR,
    INTERPRETATION_DIR,
    RESULT_DIR,
    RUN_DIR,
    FREEZE_DIR,
):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from freeze_manifests import load_directory  # noqa: E402
from validate_interpretation import validate_interpreted_artifact  # noqa: E402

EXPECTED_SCHEMA = "sei.sacs-cross-stage-decision/v1alpha1"
UTC_SECOND = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
COMMIT_SHA = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
FIXED_INTERPRETATION_REF = "../cross-stage-interpretation/interpretation.json"
FIXED_DECISION_KIND = "b5-review-disposition"
TEMPLATE_DECISION_ID = "cross-stage-decision-template"
DISPOSITIONS = {
    "defer-for-evidence",
    "retain-current-stage",
    "request-b5-review",
}

TOP_LEVEL_KEYS = {
    "schema",
    "issue",
    "state",
    "decision_id",
    "decided_at",
    "interpretation_binding",
    "decision_authority",
    "decision_kind",
    "disposition",
    "scope",
    "rationale_refs",
    "limitations_acknowledged",
    "b5_entry_condition_assessed",
    "b5_review_requested",
    "semantic_truth_claimed",
    "variant_winner_selected",
    "b5_gate_opened",
    "production_default_changed",
    "decision_digest",
}
BINDING_KEYS = {"ref", "digest"}
AUTHORITY_KEYS = {"ref", "commit"}
SCOPE_KEYS = {"track", "variant", "capacity_profile", "stress_policy"}
ALWAYS_FALSE_FLAGS = {
    "semantic_truth_claimed",
    "variant_winner_selected",
    "b5_gate_opened",
    "production_default_changed",
}


def _canonical_string(value: object) -> bool:
    return isinstance(value, str) and value != "" and value == value.strip()


def canonical_decision_digest(document: dict[str, Any]) -> str:
    payload = copy.deepcopy(document)
    payload.pop("decision_digest", None)
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def validate_decision_structure(document: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if set(document) != TOP_LEVEL_KEYS:
        missing = sorted(TOP_LEVEL_KEYS - set(document))
        extra = sorted(set(document) - TOP_LEVEL_KEYS)
        errors.append(
            f"decision top-level keys mismatch: missing={missing}, extra={extra}"
        )

    if document.get("schema") != EXPECTED_SCHEMA:
        errors.append(f"decision.schema must be {EXPECTED_SCHEMA}")
    if document.get("state") not in {"draft", "decided"}:
        errors.append("decision.state must be draft or decided")
    if not _canonical_string(document.get("decision_id")):
        errors.append("decision.decision_id must be canonical and non-empty")

    binding = document.get("interpretation_binding")
    if not isinstance(binding, dict) or set(binding) != BINDING_KEYS:
        errors.append(
            "decision.interpretation_binding must contain exactly ref and digest"
        )
    elif binding.get("ref") != FIXED_INTERPRETATION_REF:
        errors.append(
            f"decision.interpretation_binding.ref must remain {FIXED_INTERPRETATION_REF}"
        )

    authority = document.get("decision_authority")
    if not isinstance(authority, dict) or set(authority) != AUTHORITY_KEYS:
        errors.append(
            "decision.decision_authority must contain exactly ref and commit"
        )

    scope = document.get("scope")
    if not isinstance(scope, dict) or set(scope) != SCOPE_KEYS:
        errors.append(
            "decision.scope must contain exactly track, variant, capacity_profile, stress_policy"
        )

    if document.get("decision_kind") != FIXED_DECISION_KIND:
        errors.append(
            f"decision.decision_kind must remain {FIXED_DECISION_KIND}"
        )

    disposition = document.get("disposition")
    if document.get("state") == "draft":
        if disposition != "not-assessed":
            errors.append("draft decision disposition must be not-assessed")
    elif disposition not in DISPOSITIONS:
        errors.append("decided decision disposition is not registered")

    for key in (
        "rationale_refs",
        "limitations_acknowledged",
    ):
        values = document.get(key)
        if (
            not isinstance(values, list)
            or not all(_canonical_string(value) for value in values)
        ):
            errors.append(f"decision.{key} must be a canonical string list")
        elif len(values) != len(set(values)):
            errors.append(f"decision.{key} must not contain duplicates")

    for key in (
        "b5_entry_condition_assessed",
        "b5_review_requested",
        *ALWAYS_FALSE_FLAGS,
    ):
        if not isinstance(document.get(key), bool):
            errors.append(f"decision.{key} must be boolean")

    for key in ALWAYS_FALSE_FLAGS:
        if document.get(key) is not False:
            errors.append(f"decision.{key} must remain false")

    if document.get("state") == "draft":
        if document.get("decided_at") is not None:
            errors.append("draft decision decided_at must be null")
        if isinstance(binding, dict) and binding.get("digest") != "":
            errors.append("draft decision interpretation_binding.digest must be empty")
        if isinstance(authority, dict):
            if authority.get("ref") != "" or authority.get("commit") != "":
                errors.append("draft decision authority must be empty")
        if isinstance(scope, dict):
            if (
                scope.get("track") != ""
                or scope.get("variant") != ""
                or scope.get("capacity_profile") is not None
                or scope.get("stress_policy") is not None
            ):
                errors.append("draft decision scope must remain empty")
        if document.get("rationale_refs") != []:
            errors.append("draft decision rationale_refs must be empty")
        if document.get("limitations_acknowledged") != []:
            errors.append("draft decision limitations_acknowledged must be empty")
        if document.get("b5_entry_condition_assessed") is not False:
            errors.append("draft decision cannot assess B5 entry condition")
        if document.get("b5_review_requested") is not False:
            errors.append("draft decision cannot request B5 review")
        if document.get("decision_digest") != "":
            errors.append("draft decision decision_digest must be empty")

    return errors


def validate_decided_artifact(
    document: dict[str, Any],
    interpretation: dict[str, Any],
    result: dict[str, Any],
    run: dict[str, Any],
    prereg: dict[str, Any],
    freeze_documents: dict[str, dict[str, Any]],
) -> list[str]:
    errors = validate_decision_structure(document)
    errors.extend(
        f"interpreted artifact: {error}"
        for error in validate_interpreted_artifact(
            interpretation,
            result,
            run,
            prereg,
            freeze_documents,
        )
    )

    if document.get("state") != "decided":
        errors.append("decided validation requires decision.state=decided")
        return errors

    if document.get("decision_id") == TEMPLATE_DECISION_ID:
        errors.append("decided artifact must replace the template decision_id")

    decided_at = document.get("decided_at")
    if not isinstance(decided_at, str) or UTC_SECOND.fullmatch(decided_at) is None:
        errors.append(
            "decided artifact decided_at must use UTC second format YYYY-MM-DDTHH:MM:SSZ"
        )

    digest = document.get("decision_digest")
    if not isinstance(digest, str) or HEX64.fullmatch(digest) is None:
        errors.append(
            "decided artifact requires decision_digest as lowercase SHA-256 hex"
        )
    elif digest != canonical_decision_digest(document):
        errors.append(
            "decided artifact decision_digest does not match canonical content"
        )

    interpretation_digest = interpretation.get("interpretation_digest")
    binding = document.get("interpretation_binding", {})
    if (
        not isinstance(interpretation_digest, str)
        or HEX64.fullmatch(interpretation_digest) is None
    ):
        errors.append(
            "decided artifact requires interpreted artifact with valid interpretation_digest"
        )
    elif binding.get("digest") != interpretation_digest:
        errors.append(
            "decision interpretation_binding.digest does not match interpreted artifact digest"
        )

    scope = document.get("scope", {})
    interpretation_scope = interpretation.get("scope", {})
    for key in ("track", "variant", "capacity_profile", "stress_policy"):
        if scope.get(key) != interpretation_scope.get(key):
            errors.append(
                f"decision.scope.{key} must match interpreted artifact scope"
            )

    authority = document.get("decision_authority", {})
    if not _canonical_string(authority.get("ref")):
        errors.append("decided artifact requires canonical decision_authority.ref")
    commit = authority.get("commit")
    if not isinstance(commit, str) or COMMIT_SHA.fullmatch(commit) is None:
        errors.append(
            "decided artifact decision_authority.commit must be a 40-char lowercase git SHA"
        )

    interpretation_generated_at = interpretation.get("generated_at")
    if (
        isinstance(interpretation_generated_at, str)
        and isinstance(decided_at, str)
        and UTC_SECOND.fullmatch(interpretation_generated_at)
        and UTC_SECOND.fullmatch(decided_at)
        and decided_at < interpretation_generated_at
    ):
        errors.append(
            "decision.decided_at must not precede interpretation.generated_at"
        )

    rationale_refs = document.get("rationale_refs")
    if not isinstance(rationale_refs, list) or not rationale_refs:
        errors.append("decided artifact requires at least one rationale_ref")

    acknowledged = document.get("limitations_acknowledged")
    expected_limitations = interpretation.get("limitations")
    if acknowledged != expected_limitations:
        errors.append(
            "decision.limitations_acknowledged must exactly preserve interpreted artifact limitations"
        )

    if document.get("b5_entry_condition_assessed") is not True:
        errors.append(
            "decided artifact requires b5_entry_condition_assessed=true"
        )

    expected_review_request = document.get("disposition") == "request-b5-review"
    if document.get("b5_review_requested") is not expected_review_request:
        errors.append(
            "decision.b5_review_requested must match request-b5-review disposition"
        )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--decision", type=Path, default=DECISION_PATH)
    parser.add_argument(
        "--interpretation",
        type=Path,
        default=INTERPRETATION_PATH,
    )
    parser.add_argument("--result", type=Path, default=RESULT_PATH)
    parser.add_argument("--run", type=Path, default=RUN_PATH)
    parser.add_argument("--prereg", type=Path, default=PREREG_PATH)
    parser.add_argument("--freeze-dir", type=Path, default=FREEZE_DIR)
    args = parser.parse_args()

    try:
        decision = json.loads(args.decision.read_text(encoding="utf-8"))
        interpretation = json.loads(
            args.interpretation.read_text(encoding="utf-8")
        )
        result = json.loads(args.result.read_text(encoding="utf-8"))
        run = json.loads(args.run.read_text(encoding="utf-8"))
        prereg = json.loads(args.prereg.read_text(encoding="utf-8"))
        frozen = load_directory(args.freeze_dir)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"cross-stage decision load failed: {exc}", file=sys.stderr)
        return 1

    structural = validate_decision_structure(decision)
    if structural:
        for error in structural:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    if decision.get("state") == "draft":
        print(
            "Cross-stage decision validated; current decision remains draft/not-assessed"
        )
        return 0

    errors = validate_decided_artifact(
        decision,
        interpretation,
        result,
        run,
        prereg,
        frozen,
    )
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(
        "Cross-stage decision validated; disposition is provenance-bound and does not open B5"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
