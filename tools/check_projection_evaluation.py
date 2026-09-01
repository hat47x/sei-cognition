#!/usr/bin/env python3
"""Evaluate V6/V7 projection semantics against one canonical Decision Memory fixture.

This tool provides evaluation-harness scoped executable evidence only. A PASS is
not release, operational, usability, adoption, or outcome evidence.
"""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any

import check_contract_conformance as contract_check


ROOT = Path(__file__).resolve().parents[1]
EVAL_DIR = ROOT / "fixtures" / "evaluation" / "v1alpha1"
SOURCE_PATH = EVAL_DIR / "decision-projection-source.json"
EXPECTED_LIGHT_PATH = EVAL_DIR / "expected" / "light.md"
EXPECTED_AUDIT_PATH = EVAL_DIR / "expected" / "audit.json"

AUDIT_FIELDS = {
    "projection",
    "source_contract",
    "source_ref",
    "statement",
    "context_refs",
    "basis_refs",
    "unresolved_refs",
    "responsibility_refs",
    "rationale",
}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def decision_body(source: dict[str, Any]) -> dict[str, Any]:
    if source.get("record_type") != "decision":
        raise ValueError("evaluation source must be a Decision record")
    body = source.get("decision")
    if not isinstance(body, dict):
        raise ValueError("evaluation source must contain a decision object")
    return body


def logical_ref(ref: Any) -> dict[str, Any] | None:
    if not isinstance(ref, dict):
        return None
    candidate = ref.get("logical_ref") if "logical_ref" in ref else ref
    return candidate if isinstance(candidate, dict) else None


def ref_kind(ref: Any) -> str | None:
    candidate = logical_ref(ref)
    value = candidate.get("kind") if candidate else None
    return value if isinstance(value, str) else None


def render_light(source: dict[str, Any]) -> str:
    body = decision_body(source)
    basis = body.get("basis_refs", [])
    unresolved = body.get("unresolved_refs", [])
    responsibility = body.get("responsibility_refs", [])
    unknown_count = sum(ref_kind(ref) == "unknown" for ref in unresolved)
    conflict_count = sum(ref_kind(ref) == "conflict" for ref in unresolved)

    lines = [
        "# 判断概要",
        "",
        str(body["statement"]),
        "",
        f"- 根拠: {len(basis)}件の参照あり",
        (
            f"- 未解決: {len(unresolved)}件"
            f"（unknown {unknown_count}件 / conflict {conflict_count}件）"
        ),
        f"- 責任: {len(responsibility)}件の参照あり",
        "- 権限: このDecision record単独からAuthorizationの成立を判断しない",
        "- 詳細: 監査用ProjectionでReferenceとRationaleを確認できる",
        "",
    ]
    return "\n".join(lines)


def render_audit(source: dict[str, Any]) -> dict[str, Any]:
    body = decision_body(source)
    return {
        "projection": "audit/v1alpha1",
        "source_contract": source["contract"],
        "source_ref": copy.deepcopy(body["ref"]),
        "statement": body["statement"],
        "context_refs": copy.deepcopy(body.get("context_refs", [])),
        "basis_refs": copy.deepcopy(body.get("basis_refs", [])),
        "unresolved_refs": copy.deepcopy(body.get("unresolved_refs", [])),
        "responsibility_refs": copy.deepcopy(body.get("responsibility_refs", [])),
        "rationale": body.get("rationale"),
    }


def semantic_answers_from_source(source: dict[str, Any]) -> dict[str, Any]:
    body = decision_body(source)
    return {
        "decision": body["statement"],
        "context_refs": copy.deepcopy(body.get("context_refs", [])),
        "basis_refs": copy.deepcopy(body.get("basis_refs", [])),
        "unresolved_refs": copy.deepcopy(body.get("unresolved_refs", [])),
        "responsibility_refs": copy.deepcopy(body.get("responsibility_refs", [])),
        "rationale": body.get("rationale"),
    }


def semantic_answers_from_audit(audit: dict[str, Any]) -> dict[str, Any]:
    return {
        "decision": audit.get("statement"),
        "context_refs": copy.deepcopy(audit.get("context_refs", [])),
        "basis_refs": copy.deepcopy(audit.get("basis_refs", [])),
        "unresolved_refs": copy.deepcopy(audit.get("unresolved_refs", [])),
        "responsibility_refs": copy.deepcopy(audit.get("responsibility_refs", [])),
        "rationale": audit.get("rationale"),
    }


def validate_light(source: dict[str, Any], light: str) -> list[str]:
    body = decision_body(source)
    basis = body.get("basis_refs", [])
    unresolved = body.get("unresolved_refs", [])
    responsibility = body.get("responsibility_refs", [])
    unknown_count = sum(ref_kind(ref) == "unknown" for ref in unresolved)
    conflict_count = sum(ref_kind(ref) == "conflict" for ref in unresolved)

    required_fragments = [
        str(body["statement"]),
        f"- 根拠: {len(basis)}件の参照あり",
        (
            f"- 未解決: {len(unresolved)}件"
            f"（unknown {unknown_count}件 / conflict {conflict_count}件）"
        ),
        f"- 責任: {len(responsibility)}件の参照あり",
        "- 権限: このDecision record単独からAuthorizationの成立を判断しない",
        "- 詳細: 監査用ProjectionでReferenceとRationaleを確認できる",
    ]
    return [f"light projection is missing: {fragment}" for fragment in required_fragments if fragment not in light]


def validate_audit(source: dict[str, Any], audit: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    fields = set(audit)
    missing = AUDIT_FIELDS - fields
    extra = fields - AUDIT_FIELDS
    if missing:
        errors.append("audit projection is missing fields: " + ", ".join(sorted(missing)))
    if extra:
        errors.append("audit projection adds non-canonical fields: " + ", ".join(sorted(extra)))
    if audit.get("source_contract") != source.get("contract"):
        errors.append("audit source_contract does not match canonical source")

    if semantic_answers_from_audit(audit) != semantic_answers_from_source(source):
        errors.append("audit semantic answers do not match canonical source")
    return errors


def unchanged_errors(before: dict[str, Any], after: dict[str, Any]) -> list[str]:
    return [] if before == after else ["projection processing mutated the canonical source"]


def projection_allowed(impact: str, projection: str) -> bool:
    if impact == "low-impact":
        return projection in {"light", "audit"}
    if impact == "high-impact":
        return projection == "audit"
    return False


def require_errors(name: str, errors: list[str], failures: list[str]) -> None:
    if not errors:
        failures.append(f"negative case did not fail: {name}")


def main() -> int:
    failures: list[str] = []
    checks: list[str] = []

    source = load_json(SOURCE_PATH)
    schemas, registry = contract_check.load_schemas()
    representation_errors = contract_check.schema_errors(
        "decision-memory", source, schemas, registry
    )
    if representation_errors:
        failures.extend(
            f"canonical source schema error: {message}" for message in representation_errors
        )
    else:
        checks.append("canonical Decision Memory schema")

    before = copy.deepcopy(source)
    light = render_light(source)
    audit = render_audit(source)
    source_mutation_errors = unchanged_errors(before, source)
    if source_mutation_errors:
        failures.extend(source_mutation_errors)
    else:
        checks.append("projection generation leaves canonical source unchanged")

    light_errors = validate_light(source, light)
    audit_errors = validate_audit(source, audit)
    failures.extend(light_errors)
    failures.extend(audit_errors)
    if not light_errors:
        checks.append("light projection semantic visibility")
    if not audit_errors:
        checks.append("audit projection semantic equivalence")

    expected_light = EXPECTED_LIGHT_PATH.read_text(encoding="utf-8")
    if light != expected_light:
        failures.append("generated light projection differs from expected/light.md")
    else:
        checks.append("light projection snapshot")

    expected_audit = load_json(EXPECTED_AUDIT_PATH)
    if audit != expected_audit:
        failures.append("generated audit projection differs from expected/audit.json")
    else:
        checks.append("audit projection snapshot")

    # E4: discarding one projection must not affect the canonical source or another projection.
    discarded_light = light
    del discarded_light
    audit_again = render_audit(source)
    if audit_again != audit or unchanged_errors(before, source):
        failures.append("projection replacement changed canonical meaning")
    else:
        checks.append("projection replacement preserves canonical source")

    # E3: evaluation policy exercises progressive explicitness without introducing a universal risk level.
    policy_expectations = [
        ("low-impact light", projection_allowed("low-impact", "light"), True),
        ("low-impact audit", projection_allowed("low-impact", "audit"), True),
        ("high-impact light", projection_allowed("high-impact", "light"), False),
        ("high-impact audit", projection_allowed("high-impact", "audit"), True),
    ]
    for name, actual, expected in policy_expectations:
        if actual != expected:
            failures.append(f"progressive explicitness policy mismatch: {name}")
    if all(actual == expected for _, actual, expected in policy_expectations):
        checks.append("low-impact / high-impact progressive explicitness policy")

    # E5 negative cases. Each bad projection must be rejected by an invariant that the good path passes.
    light_without_unresolved = "\n".join(
        line for line in light.splitlines() if not line.startswith("- 未解決:")
    ) + "\n"
    require_errors(
        "light hides unresolved state",
        validate_light(source, light_without_unresolved),
        failures,
    )

    light_without_responsibility = "\n".join(
        line for line in light.splitlines() if not line.startswith("- 責任:")
    ) + "\n"
    require_errors(
        "light hides responsibility",
        validate_light(source, light_without_responsibility),
        failures,
    )

    audit_without_basis = copy.deepcopy(audit)
    audit_without_basis.pop("basis_refs", None)
    require_errors(
        "audit drops basis",
        validate_audit(source, audit_without_basis),
        failures,
    )

    audit_with_invented_authority = copy.deepcopy(audit)
    audit_with_invented_authority["authority_granted"] = True
    require_errors(
        "audit invents authority",
        validate_audit(source, audit_with_invented_authority),
        failures,
    )

    mutated_source = copy.deepcopy(source)
    mutated_source["decision"]["statement"] = "Projectionがcanonical sourceを書き換えた。"
    require_errors(
        "projection mutates canonical source",
        unchanged_errors(source, mutated_source),
        failures,
    )

    if projection_allowed("high-impact", "light"):
        failures.append("high-impact case incorrectly accepts light-only projection")
    if not projection_allowed("low-impact", "light"):
        failures.append("low-impact case incorrectly requires maximal audit detail")

    if not failures:
        checks.append("negative cases reject semantic loss / semantic invention")

    result = {
        "status": "pass" if not failures else "fail",
        "evidence_scope": "evaluation-harness scoped executable evidence only",
        "checks": checks,
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
