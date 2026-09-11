#!/usr/bin/env python3
"""Reproducible V6/V7 projection evaluation for ISSUE-000039.

The harness checks a projection boundary; it does not define a new SOZA Contract.
A PASS is evaluation-harness scoped Executable Evidence only.
"""

from __future__ import annotations

import copy
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.check_contract_conformance import (  # noqa: E402
    load_schemas,
    schema_errors,
    semantic_errors,
)

HERE = Path(__file__).resolve().parent
RICH_FIXTURE = ROOT / "fixtures" / "contracts" / "v1alpha1" / "evaluation" / "E1-projection-rich-decision.json"
LOW_FIXTURE = ROOT / "fixtures" / "contracts" / "v1alpha1" / "evaluation" / "E2-low-impact-minimal-decision.json"
NEGATIVE_CASES = HERE / "negative-cases.json"
LIGHT_SNAPSHOT = HERE / "projections" / "light.md"
AUDIT_SNAPSHOT = HERE / "projections" / "audit.md"


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def ref_key(ref: Any) -> str:
    if not isinstance(ref, dict):
        return "<invalid>"
    candidate = ref.get("logical_ref") if isinstance(ref.get("logical_ref"), dict) else ref
    kind = candidate.get("kind")
    ident = candidate.get("id")
    scope = candidate.get("scope")
    if scope:
        return f"{scope}:{kind}/{ident}"
    return f"{kind}/{ident}"


def structural_digest(document: Any) -> str:
    encoded = json.dumps(document, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def extract_semantics(document: dict[str, Any]) -> dict[str, Any]:
    decision_doc: dict[str, Any] | None = None
    observations: dict[str, dict[str, Any]] = {}

    if document.get("contract") == "sei.semantic-interchange/v1alpha1":
        for record in document.get("records", []):
            if not isinstance(record, dict):
                continue
            contract = record.get("contract")
            payload = record.get("payload")
            if not isinstance(contract, dict) or not isinstance(payload, dict):
                continue
            contract_id = contract.get("contract_id")
            if contract_id == "sei.decision-memory" and payload.get("record_type") == "decision":
                decision_doc = payload
            elif contract_id == "sei.capability-observation":
                observation = payload.get("observation")
                if isinstance(observation, dict) and isinstance(observation.get("ref"), dict):
                    observations[ref_key(observation["ref"])] = observation
    elif document.get("contract") == "sei.decision-memory/v1alpha1":
        decision_doc = document

    if not isinstance(decision_doc, dict):
        raise ValueError("canonical source contains no Decision Memory decision")
    decision = decision_doc.get("decision")
    if not isinstance(decision, dict):
        raise ValueError("Decision Memory document contains no decision body")

    basis = [ref_key(ref) for ref in decision.get("basis_refs", [])]
    unresolved = [ref_key(ref) for ref in decision.get("unresolved_refs", [])]
    responsibility = [ref_key(ref) for ref in decision.get("responsibility_refs", [])]

    provenance: list[str] = []
    for basis_ref in basis:
        observation = observations.get(basis_ref)
        if not observation:
            continue
        for ref in observation.get("provenance_refs", []):
            key = ref_key(ref)
            if key not in provenance:
                provenance.append(key)
        mapping = observation.get("mapping_provenance")
        if isinstance(mapping, dict) and isinstance(mapping.get("mapping_ref"), dict):
            key = ref_key(mapping["mapping_ref"])
            if key not in provenance:
                provenance.append(key)

    authorization_status = (
        "unresolved"
        if any(item.startswith("authorization-evidence/") for item in unresolved)
        else "not_represented"
    )

    return {
        "decision": decision.get("statement", ""),
        "basis": basis,
        "unresolved": unresolved,
        "responsibility": responsibility,
        "authorization_evidence_status": authorization_status,
        "provenance": provenance,
        "rationale": decision.get("rationale", ""),
    }


def build_light(semantics: dict[str, Any]) -> dict[str, Any]:
    return {
        "profile": "light",
        "decision": semantics["decision"],
        "unresolved": list(semantics["unresolved"]),
        "attention": "needs_attention" if semantics["unresolved"] else "no_unresolved_recorded",
        "detail_access": {
            "basis_count": len(semantics["basis"]),
            "responsibility_count": len(semantics["responsibility"]),
            "provenance_count": len(semantics["provenance"]),
            "audit_projection_available": True,
        },
        "authorization_evidence_status": semantics["authorization_evidence_status"],
    }


def build_audit(semantics: dict[str, Any]) -> dict[str, Any]:
    return {
        "profile": "audit",
        "decision": semantics["decision"],
        "basis": list(semantics["basis"]),
        "unresolved": list(semantics["unresolved"]),
        "responsibility": list(semantics["responsibility"]),
        "authorization_evidence_status": semantics["authorization_evidence_status"],
        "provenance": list(semantics["provenance"]),
        "rationale": semantics["rationale"],
    }


def bullet_lines(items: list[str]) -> list[str]:
    return [f"- {item}" for item in items] if items else ["- （記録なし）"]


def render_light(view: dict[str, Any]) -> str:
    detail = view["detail_access"]
    lines = [
        "# Light Projection",
        "",
        "## Decision",
        view["decision"],
        "",
        "## Unresolved",
        *bullet_lines(view["unresolved"]),
        "",
        "## Attention",
        view["attention"],
        "",
        "## Detail access",
        f"- Basis: {detail['basis_count']} item(s) — audit projection",
        f"- Responsibility: {detail['responsibility_count']} item(s) — audit projection",
        f"- Provenance: {detail['provenance_count']} item(s) — audit projection",
        f"- Authorization Evidence: {view['authorization_evidence_status']}",
        "",
    ]
    return "\n".join(lines)


def render_audit(view: dict[str, Any]) -> str:
    lines = [
        "# Audit Projection",
        "",
        "## Decision",
        view["decision"],
        "",
        "## Basis",
        *bullet_lines(view["basis"]),
        "",
        "## Unresolved",
        *bullet_lines(view["unresolved"]),
        "",
        "## Responsibility",
        *bullet_lines(view["responsibility"]),
        "",
        "## Authorization Evidence",
        view["authorization_evidence_status"],
        "",
        "## Provenance",
        *bullet_lines(view["provenance"]),
        "",
        "## Rationale",
        view["rationale"] or "（記録なし）",
        "",
    ]
    return "\n".join(lines)


def validate_projection(
    view: dict[str, Any],
    semantics: dict[str, Any],
    impact: str,
) -> list[str]:
    errors: list[str] = []
    if view.get("decision") != semantics["decision"]:
        errors.append("E_DECISION_MISMATCH")
    if view.get("unresolved") != semantics["unresolved"]:
        errors.append("E_UNRESOLVED_HIDDEN")

    actual_authorization = view.get("authorization_evidence_status")
    if actual_authorization != semantics["authorization_evidence_status"]:
        if actual_authorization == "verified" and semantics["authorization_evidence_status"] != "verified":
            errors.append("E_AUTHORIZATION_INVENTED")
        else:
            errors.append("E_AUTHORIZATION_STATE_MISMATCH")

    profile = view.get("profile")
    if profile == "light":
        detail = view.get("detail_access")
        if not isinstance(detail, dict):
            errors.append("E_DETAIL_PATH_MISSING")
        else:
            if detail.get("basis_count") != len(semantics["basis"]):
                errors.append("E_BASIS_UNTRACEABLE")
            if detail.get("responsibility_count") != len(semantics["responsibility"]):
                errors.append("E_RESPONSIBILITY_UNTRACEABLE")
            if detail.get("provenance_count") != len(semantics["provenance"]):
                errors.append("E_PROVENANCE_UNTRACEABLE")
            if any(
                len(semantics[name]) > 0
                for name in ("basis", "responsibility", "provenance")
            ) and not detail.get("audit_projection_available"):
                errors.append("E_DETAIL_PATH_MISSING")
        if impact == "high":
            errors.append("E_HIGH_IMPACT_DETAIL_MISSING")
    elif profile == "audit":
        if view.get("basis") != semantics["basis"]:
            errors.append("E_BASIS_UNTRACEABLE")
        if view.get("responsibility") != semantics["responsibility"]:
            errors.append("E_RESPONSIBILITY_UNTRACEABLE")
        if view.get("provenance") != semantics["provenance"]:
            errors.append("E_PROVENANCE_UNTRACEABLE")
        if view.get("rationale") != semantics["rationale"]:
            errors.append("E_RATIONALE_MISMATCH")
    else:
        errors.append("E_UNKNOWN_PROJECTION_PROFILE")
    return errors


def validate_policy(impact: str, required_profile: str) -> list[str]:
    if impact == "high" and required_profile != "audit":
        return ["E_HIGH_IMPACT_DETAIL_MISSING"]
    if impact == "low" and required_profile == "audit":
        return ["E_LOW_IMPACT_OVEREXPLICIT"]
    return []


def question_answers_from_semantics(semantics: dict[str, Any]) -> dict[str, Any]:
    return {
        "Q1": semantics["decision"],
        "Q2": semantics["unresolved"],
        "Q3": semantics["basis"],
        "Q4": semantics["responsibility"],
        "Q5": semantics["authorization_evidence_status"],
        "Q6": semantics["provenance"],
    }


def question_answers_from_audit(view: dict[str, Any]) -> dict[str, Any]:
    return {
        "Q1": view["decision"],
        "Q2": view["unresolved"],
        "Q3": view["basis"],
        "Q4": view["responsibility"],
        "Q5": view["authorization_evidence_status"],
        "Q6": view["provenance"],
    }


def validate_contract_sources() -> None:
    schemas, registry = load_schemas()
    cases = [
        (RICH_FIXTURE, "semantic-interchange"),
        (LOW_FIXTURE, "decision-memory"),
    ]
    failures: list[str] = []
    for path, schema_name in cases:
        document = load_json(path)
        representation = schema_errors(schema_name, document, schemas, registry)
        semantic, not_verified = semantic_errors(schema_name, document, schemas, registry)
        if representation or semantic or not_verified:
            details = representation + semantic
            if not_verified:
                details.append("source contains an unknown nested Contract")
            failures.append(f"{path.name}: " + "; ".join(details))
    if failures:
        raise AssertionError("evaluation canonical source is not current-Contract conformant: " + " | ".join(failures))


def negative_case_errors(
    case_id: str,
    rich_document: dict[str, Any],
    rich_semantics: dict[str, Any],
    light: dict[str, Any],
) -> list[str]:
    if case_id == "N1-hide-unresolved":
        candidate = copy.deepcopy(light)
        candidate["unresolved"] = []
        candidate["attention"] = "no_unresolved_recorded"
        return validate_projection(candidate, rich_semantics, "low")
    if case_id == "N2-hide-basis-access":
        candidate = copy.deepcopy(light)
        candidate["detail_access"]["basis_count"] = 0
        return validate_projection(candidate, rich_semantics, "low")
    if case_id == "N3-hide-responsibility-access":
        candidate = copy.deepcopy(light)
        candidate["detail_access"]["responsibility_count"] = 0
        return validate_projection(candidate, rich_semantics, "low")
    if case_id == "N4-invent-authorization":
        candidate = copy.deepcopy(light)
        candidate["authorization_evidence_status"] = "verified"
        return validate_projection(candidate, rich_semantics, "low")
    if case_id == "N5-mutate-canonical":
        original = structural_digest(rich_document)
        mutated = copy.deepcopy(rich_document)
        for record in mutated["records"]:
            contract = record.get("contract", {})
            if contract.get("contract_id") == "sei.decision-memory":
                record["payload"]["decision"]["statement"] = "Projection由来の書換え"
        return ["E_CANONICAL_MUTATED"] if structural_digest(mutated) != original else []
    if case_id == "N6-high-impact-light-only":
        return validate_projection(copy.deepcopy(light), rich_semantics, "high")
    if case_id == "N7-low-impact-force-audit":
        return validate_policy("low", "audit")
    return ["E_UNKNOWN_NEGATIVE_CASE"]


def main() -> int:
    validate_contract_sources()

    rich_document = load_json(RICH_FIXTURE)
    low_document = load_json(LOW_FIXTURE)
    rich_semantics = extract_semantics(rich_document)
    low_semantics = extract_semantics(low_document)

    source_digest = structural_digest(rich_document)
    light = build_light(rich_semantics)
    audit = build_audit(rich_semantics)

    failures: list[str] = []

    if validate_projection(light, rich_semantics, "low"):
        failures.append("rich light Projection failed its low-impact visibility boundary")
    if validate_projection(audit, rich_semantics, "high"):
        failures.append("rich audit Projection failed its high-impact detail boundary")

    low_light = build_light(low_semantics)
    if validate_projection(low_light, low_semantics, "low"):
        failures.append("low-impact minimal Decision did not pass light Projection")
    if validate_policy("low", "light"):
        failures.append("low-impact policy unexpectedly rejected light Projection")
    if validate_policy("high", "audit"):
        failures.append("high-impact policy unexpectedly rejected audit Projection")

    machine_answers = question_answers_from_semantics(rich_semantics)
    audit_answers = question_answers_from_audit(audit)
    if audit_answers != machine_answers:
        failures.append("audit Projection and machine-readable semantic questions diverged")

    light_required = {
        "Q1": light["decision"],
        "Q2": light["unresolved"],
        "Q5": light["authorization_evidence_status"],
    }
    machine_light_required = {key: machine_answers[key] for key in ("Q1", "Q2", "Q5")}
    if light_required != machine_light_required:
        failures.append("light Projection lost a required foreground semantic question")

    rendered_light = render_light(light)
    rendered_audit = render_audit(audit)
    if LIGHT_SNAPSHOT.read_text(encoding="utf-8") != rendered_light:
        failures.append("light Projection snapshot differs from deterministic renderer")
    if AUDIT_SNAPSHOT.read_text(encoding="utf-8") != rendered_audit:
        failures.append("audit Projection snapshot differs from deterministic renderer")

    rebuilt_light = build_light(extract_semantics(rich_document))
    if render_light(rebuilt_light) != rendered_light:
        failures.append("light Projection could not be reproduced after replacement")
    if structural_digest(rich_document) != source_digest:
        failures.append("canonical source changed while generating or replacing Projections")

    negative_spec = load_json(NEGATIVE_CASES)
    negative_results: list[dict[str, Any]] = []
    for case in negative_spec.get("cases", []):
        case_id = case["id"]
        expected = case["expected_error"]
        actual_errors = negative_case_errors(case_id, rich_document, rich_semantics, light)
        passed = expected in actual_errors
        negative_results.append(
            {
                "id": case_id,
                "expected_error": expected,
                "actual_errors": actual_errors,
                "pass": passed,
            }
        )
        if not passed:
            failures.append(f"{case_id}: expected {expected}, got {actual_errors}")

    summary = {
        "schema": "soza.v6-v7-projection-evaluation/v1",
        "canonical_sources": 2,
        "projection_profiles": ["light", "audit"],
        "semantic_questions": 6,
        "negative_cases": negative_results,
        "passed": not failures,
        "evidence": {
            "design": "V6/V7 evaluation protocol traced to current Product Value and Requirements",
            "executable": "evaluation-harness scoped only when this command succeeds",
            "release": False,
            "operational": False,
            "adoption_outcome": False,
        },
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))

    if failures:
        print("\nV6/V7 projection evaluation failures:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
