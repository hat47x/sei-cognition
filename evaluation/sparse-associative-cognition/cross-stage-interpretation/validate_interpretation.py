#!/usr/bin/env python3
"""Validate non-decisional cross-stage benchmark interpretation artifacts.

This module validates provenance and interpretation boundaries. It does not
choose a winning variant, make a recommendation, open B5, or change production
defaults.
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
RESULT_DIR = SACS_DIR / "cross-stage-result"
RUN_DIR = SACS_DIR / "cross-stage-run"
FREEZE_DIR = SACS_DIR / "cross-stage-freeze"

INTERPRETATION_PATH = HERE / "interpretation.json"
RESULT_PATH = RESULT_DIR / "result.json"
RUN_PATH = RUN_DIR / "evaluation_run.json"
PREREG_PATH = SACS_DIR / "cross_stage_benchmark_preregistration.json"

for path in (SACS_DIR, RESULT_DIR, RUN_DIR, FREEZE_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from freeze_manifests import load_directory  # noqa: E402
from validate_cross_stage_preregistration import (  # noqa: E402
    validate_preregistration,
    validate_unlock,
)
from validate_evaluation_run import validate_authorized_run  # noqa: E402
from validate_result import validate_completed_result  # noqa: E402

EXPECTED_SCHEMA = "sei.sacs-cross-stage-interpretation/v1alpha1"
UTC_SECOND = re.compile(r"^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}Z$")
COMMIT_SHA = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")

TOP_LEVEL_KEYS = {
    "schema",
    "issue",
    "state",
    "interpretation_id",
    "generated_at",
    "result_binding",
    "analyst_provenance",
    "scope",
    "findings",
    "limitations",
    "unresolved_questions",
    "semantic_truth_claimed",
    "variant_winner_declared",
    "recommendation_generated",
    "b5_decision_generated",
    "production_default_changed",
    "interpretation_digest",
}
RESULT_BINDING_KEYS = {"ref", "digest"}
ANALYST_KEYS = {"ref", "commit"}
SCOPE_KEYS = {"track", "variant", "capacity_profile", "stress_policy"}
FINDING_KEYS = {"id", "kind", "claim_strength", "evidence_metrics", "statement"}
FINDING_KINDS = {
    "metric-observation",
    "cross-metric-observation",
    "limitation-aware-hypothesis",
}
CLAIM_STRENGTHS = {"observation", "hypothesis"}
STOP_FLAGS = {
    "semantic_truth_claimed",
    "variant_winner_declared",
    "recommendation_generated",
    "b5_decision_generated",
    "production_default_changed",
}


def _canonical_string(value: object) -> bool:
    return isinstance(value, str) and value != "" and value == value.strip()


def canonical_interpretation_digest(document: dict[str, Any]) -> str:
    payload = copy.deepcopy(document)
    payload.pop("interpretation_digest", None)
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def validate_interpretation_structure(document: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if set(document) != TOP_LEVEL_KEYS:
        missing = sorted(TOP_LEVEL_KEYS - set(document))
        extra = sorted(set(document) - TOP_LEVEL_KEYS)
        errors.append(
            f"interpretation top-level keys mismatch: missing={missing}, extra={extra}"
        )

    if document.get("schema") != EXPECTED_SCHEMA:
        errors.append(f"interpretation.schema must be {EXPECTED_SCHEMA}")
    if document.get("state") not in {"draft", "interpreted"}:
        errors.append("interpretation.state must be draft or interpreted")
    if not _canonical_string(document.get("interpretation_id")):
        errors.append("interpretation.interpretation_id must be canonical and non-empty")

    binding = document.get("result_binding")
    if not isinstance(binding, dict) or set(binding) != RESULT_BINDING_KEYS:
        errors.append("interpretation.result_binding must contain exactly ref and digest")
    elif binding.get("ref") != "../cross-stage-result/result.json":
        errors.append(
            "interpretation.result_binding.ref must remain ../cross-stage-result/result.json"
        )

    analyst = document.get("analyst_provenance")
    if not isinstance(analyst, dict) or set(analyst) != ANALYST_KEYS:
        errors.append(
            "interpretation.analyst_provenance must contain exactly ref and commit"
        )

    scope = document.get("scope")
    if not isinstance(scope, dict) or set(scope) != SCOPE_KEYS:
        errors.append(
            "interpretation.scope must contain exactly track, variant, capacity_profile, stress_policy"
        )

    findings = document.get("findings")
    if not isinstance(findings, list):
        errors.append("interpretation.findings must be a list")
    else:
        for index, finding in enumerate(findings):
            if not isinstance(finding, dict) or set(finding) != FINDING_KEYS:
                errors.append(
                    f"interpretation.findings[{index}] keys do not match the registered contract"
                )

    for key in ("limitations", "unresolved_questions"):
        values = document.get(key)
        if (
            not isinstance(values, list)
            or not all(_canonical_string(value) for value in values)
        ):
            errors.append(f"interpretation.{key} must be a canonical string list")

    for key in STOP_FLAGS:
        if document.get(key) is not False:
            errors.append(f"interpretation.{key} must remain false")

    if document.get("state") == "draft":
        if document.get("generated_at") is not None:
            errors.append("draft interpretation generated_at must be null")
        if isinstance(binding, dict) and binding.get("digest") != "":
            errors.append("draft interpretation result_binding.digest must be empty")
        if isinstance(analyst, dict):
            if analyst.get("ref") != "" or analyst.get("commit") != "":
                errors.append("draft interpretation analyst provenance must be empty")
        if document.get("interpretation_digest") != "":
            errors.append("draft interpretation interpretation_digest must be empty")

    return errors


def validate_interpreted_artifact(
    document: dict[str, Any],
    result: dict[str, Any],
    run: dict[str, Any],
    prereg: dict[str, Any],
    freeze_documents: dict[str, dict[str, Any]],
) -> list[str]:
    errors = validate_interpretation_structure(document)
    errors.extend(
        f"preregistration: {error}"
        for error in validate_preregistration(prereg)
    )
    errors.extend(
        f"authorized run: {error}"
        for error in validate_authorized_run(run, prereg, freeze_documents)
    )
    errors.extend(
        f"full unlock: {error}"
        for error in validate_unlock(prereg)
    )
    errors.extend(
        f"completed result: {error}"
        for error in validate_completed_result(
            result,
            run,
            prereg,
            freeze_documents,
        )
    )

    if document.get("state") != "interpreted":
        errors.append("interpreted validation requires interpretation.state=interpreted")
        return errors

    if document.get("interpretation_id") == "cross-stage-interpretation-template":
        errors.append("interpreted artifact must replace the template interpretation_id")

    generated_at = document.get("generated_at")
    if not isinstance(generated_at, str) or UTC_SECOND.fullmatch(generated_at) is None:
        errors.append(
            "interpreted artifact generated_at must use UTC second format YYYY-MM-DDTHH:MM:SSZ"
        )

    digest = document.get("interpretation_digest")
    if not isinstance(digest, str) or HEX64.fullmatch(digest) is None:
        errors.append(
            "interpreted artifact requires interpretation_digest as lowercase SHA-256 hex"
        )
    elif digest != canonical_interpretation_digest(document):
        errors.append(
            "interpreted artifact interpretation_digest does not match canonical content"
        )

    result_digest = result.get("result_digest")
    binding = document.get("result_binding", {})
    if not isinstance(result_digest, str) or HEX64.fullmatch(result_digest) is None:
        errors.append("interpreted artifact requires completed result with valid result_digest")
    elif binding.get("digest") != result_digest:
        errors.append(
            "interpretation result_binding.digest does not match completed result digest"
        )

    scope = document.get("scope", {})
    for key in ("track", "variant", "capacity_profile", "stress_policy"):
        if scope.get(key) != result.get(key):
            errors.append(f"interpretation.scope.{key} must match completed result")

    analyst = document.get("analyst_provenance", {})
    if not _canonical_string(analyst.get("ref")):
        errors.append("interpreted artifact requires canonical analyst_provenance.ref")
    commit = analyst.get("commit")
    if not isinstance(commit, str) or COMMIT_SHA.fullmatch(commit) is None:
        errors.append(
            "interpreted artifact analyst_provenance.commit must be a 40-char lowercase git SHA"
        )

    result_generated_at = result.get("generated_at")
    if (
        isinstance(result_generated_at, str)
        and isinstance(generated_at, str)
        and UTC_SECOND.fullmatch(result_generated_at)
        and UTC_SECOND.fullmatch(generated_at)
        and generated_at < result_generated_at
    ):
        errors.append("interpretation.generated_at must not precede result.generated_at")

    metric_names = {
        metric.get("name")
        for metric in result.get("metrics", [])
        if isinstance(metric, dict) and isinstance(metric.get("name"), str)
    }

    findings = document.get("findings", [])
    if not findings:
        errors.append("interpreted artifact requires at least one finding")

    seen_ids: set[str] = set()
    for index, finding in enumerate(findings):
        if not isinstance(finding, dict):
            continue

        finding_id = finding.get("id")
        if not _canonical_string(finding_id):
            errors.append(
                f"interpretation.findings[{index}].id must be canonical and non-empty"
            )
        elif finding_id in seen_ids:
            errors.append(f"interpretation finding id must be unique: {finding_id}")
        else:
            seen_ids.add(finding_id)

        if finding.get("kind") not in FINDING_KINDS:
            errors.append(
                f"interpretation.findings[{index}].kind is not registered"
            )
        if finding.get("claim_strength") not in CLAIM_STRENGTHS:
            errors.append(
                f"interpretation.findings[{index}].claim_strength must be observation or hypothesis"
            )

        evidence_metrics = finding.get("evidence_metrics")
        if (
            not isinstance(evidence_metrics, list)
            or not evidence_metrics
            or not all(_canonical_string(value) for value in evidence_metrics)
        ):
            errors.append(
                f"interpretation.findings[{index}].evidence_metrics must be a non-empty canonical string list"
            )
        else:
            if len(evidence_metrics) != len(set(evidence_metrics)):
                errors.append(
                    f"interpretation.findings[{index}].evidence_metrics must be unique"
                )
            unknown = sorted(set(evidence_metrics) - metric_names)
            if unknown:
                errors.append(
                    f"interpretation finding references unknown result metrics: {unknown}"
                )

        if not _canonical_string(finding.get("statement")):
            errors.append(
                f"interpretation.findings[{index}].statement must be canonical and non-empty"
            )

    limitations = document.get("limitations")
    if not isinstance(limitations, list) or not limitations:
        errors.append("interpreted artifact requires at least one explicit limitation")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--interpretation", type=Path, default=INTERPRETATION_PATH)
    parser.add_argument("--result", type=Path, default=RESULT_PATH)
    parser.add_argument("--run", type=Path, default=RUN_PATH)
    parser.add_argument("--prereg", type=Path, default=PREREG_PATH)
    parser.add_argument("--freeze-dir", type=Path, default=FREEZE_DIR)
    args = parser.parse_args()

    try:
        interpretation = json.loads(args.interpretation.read_text(encoding="utf-8"))
        result = json.loads(args.result.read_text(encoding="utf-8"))
        run = json.loads(args.run.read_text(encoding="utf-8"))
        prereg = json.loads(args.prereg.read_text(encoding="utf-8"))
        frozen = load_directory(args.freeze_dir)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"cross-stage interpretation load failed: {exc}", file=sys.stderr)
        return 1

    structural = validate_interpretation_structure(interpretation)
    if structural:
        for error in structural:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    if interpretation.get("state") == "draft":
        print(
            "Cross-stage interpretation validated; current interpretation remains draft/empty"
        )
        return 0

    errors = validate_interpreted_artifact(
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
        "Cross-stage interpretation validated; artifact remains non-decisional and provenance-bound"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
