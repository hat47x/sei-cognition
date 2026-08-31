#!/usr/bin/env python3
"""Check current SOZA Contract v1alpha1 schemas, fixtures, and semantic invariants.

This checker deliberately separates three layers:

1. JSON Schema representation checks.
2. Semantic invariants that are awkward or misleading to encode in JSON Schema.
3. Boundary cases that are structurally valid but cannot be fully verified by this
   Contract version, such as an unknown nested Contract version.

A PASS from this tool is executable evidence for the checked fixtures only. It is
not release or operational evidence, and it does not stabilize a Representation
Profile tracked by ISSUE-000009.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    from jsonschema import Draft202012Validator, FormatChecker
    from referencing import Registry, Resource
except ImportError as exc:  # pragma: no cover - environment boundary
    raise SystemExit(
        "jsonschema and referencing are required. Install the dependency declared in "
        "tools/contract-check-requirements.txt"
    ) from exc


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "contracts" / "schemas" / "v1alpha1"
FIXTURE_DIR = ROOT / "fixtures" / "contracts" / "v1alpha1"


SCHEMA_FILES = {
    "semantic-reference": SCHEMA_DIR / "semantic-reference.schema.json",
    "decision-memory": SCHEMA_DIR / "decision-memory.schema.json",
    "capability-observation": SCHEMA_DIR / "capability-observation.schema.json",
    "semantic-interchange": SCHEMA_DIR / "semantic-interchange.schema.json",
}

KNOWN_RECORD_CONTRACTS = {
    ("soza.semantic-reference", "v1alpha1"): "semantic-reference",
    ("soza.decision-memory", "v1alpha1"): "decision-memory",
    ("soza.capability-observation", "v1alpha1"): "capability-observation",
}


@dataclass(frozen=True)
class FixtureExpectation:
    path: str
    schema: str
    expected: str  # pass | schema_fail | semantic_fail | not_verified


FIXTURES = [
    FixtureExpectation("capability/F1-tei-partial-degradation.json", "capability-observation", "pass"),
    FixtureExpectation("capability/F2-proposed-state-vs-actual.json", "capability-observation", "pass"),
    FixtureExpectation("capability/F3-release-without-environment-binding.json", "capability-observation", "pass"),
    FixtureExpectation("capability/F4-observation-gap.json", "capability-observation", "pass"),
    FixtureExpectation("capability/F5-cross-provider-comparison.json", "semantic-interchange", "pass"),
    FixtureExpectation("capability/F6-historical-reconstruction.json", "semantic-interchange", "pass"),
    FixtureExpectation("capability/F7-selective-disclosure.json", "capability-observation", "pass"),
    FixtureExpectation("negative/decision-authority-field.json", "decision-memory", "schema_fail"),
    FixtureExpectation("negative/capability-missing-observed-at.json", "capability-observation", "schema_fail"),
    FixtureExpectation("negative/same-logical-lineage-without-exact.json", "semantic-reference", "semantic_fail"),
    FixtureExpectation("negative/interchange-mismatched-exact-binding.json", "semantic-interchange", "semantic_fail"),
    FixtureExpectation("boundary/unknown-contract-version.json", "semantic-interchange", "not_verified"),
    FixtureExpectation("boundary/verification-not-verified.json", "semantic-reference", "pass"),
    FixtureExpectation("boundary/verification-failed.json", "semantic-reference", "pass"),
    FixtureExpectation("boundary/recommendation-without-decision.json", "decision-memory", "pass"),
    FixtureExpectation("boundary/decision-with-unresolved.json", "decision-memory", "pass"),
    FixtureExpectation("boundary/partial-knowledge-interchange.json", "semantic-interchange", "pass"),
]


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_schemas() -> tuple[dict[str, dict[str, Any]], Registry]:
    schemas = {name: load_json(path) for name, path in SCHEMA_FILES.items()}
    resources: list[tuple[str, Resource[Any]]] = []
    for schema in schemas.values():
        schema_id = schema.get("$id")
        if not isinstance(schema_id, str) or not schema_id:
            raise ValueError("every schema must declare a non-empty $id")
        resources.append((schema_id, Resource.from_contents(schema)))
    registry = Registry().with_resources(resources)
    return schemas, registry


def schema_errors(
    schema_name: str,
    document: Any,
    schemas: dict[str, dict[str, Any]],
    registry: Registry,
) -> list[str]:
    schema = schemas[schema_name]
    validator = Draft202012Validator(
        schema,
        registry=registry,
        format_checker=FormatChecker(),
    )
    errors = sorted(validator.iter_errors(document), key=lambda error: list(error.path))
    rendered: list[str] = []
    for error in errors:
        location = "/".join(str(part) for part in error.absolute_path) or "<root>"
        rendered.append(f"{location}: {error.message}")
    return rendered


def is_exact_endpoint(endpoint: Any) -> bool:
    return isinstance(endpoint, dict) and "logical_ref" in endpoint and "content_digest" in endpoint


def logical_identity(endpoint: Any) -> tuple[str | None, str | None, str | None]:
    if not isinstance(endpoint, dict):
        return (None, None, None)
    candidate = endpoint.get("logical_ref") if is_exact_endpoint(endpoint) else endpoint
    if not isinstance(candidate, dict):
        return (None, None, None)
    return (candidate.get("scope"), candidate.get("kind"), candidate.get("id"))


def binding_signature(binding: Any) -> tuple[Any, ...] | None:
    if not is_exact_endpoint(binding):
        return None
    profile = binding.get("representation_profile")
    if not isinstance(profile, dict):
        return None
    return (
        logical_identity(binding),
        binding.get("content_digest"),
        profile.get("profile_id"),
        profile.get("version"),
    )


def semantic_reference_errors(document: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(document, dict):
        return errors
    if document.get("record_type") != "semantic_lineage":
        return errors

    lineage = document.get("semantic_lineage")
    if not isinstance(lineage, dict):
        return errors

    source = lineage.get("from")
    target = lineage.get("to")
    source_id = logical_identity(source)
    target_id = logical_identity(target)

    if source_id != (None, None, None) and source_id == target_id:
        if not (is_exact_endpoint(source) and is_exact_endpoint(target)):
            errors.append(
                "same logical identity lineage requires exact endpoints on both sides"
            )
    return errors


def decision_basis_exact_bindings(payload: Any) -> list[Any]:
    if not isinstance(payload, dict):
        return []
    record_type = payload.get("record_type")
    if record_type == "decision":
        body = payload.get("decision")
    elif record_type == "recommendation":
        body = payload.get("recommendation")
    else:
        return []
    if not isinstance(body, dict):
        return []
    refs = body.get("basis_refs")
    if not isinstance(refs, list):
        return []
    return [ref for ref in refs if is_exact_endpoint(ref)]


def nested_interchange_status(
    document: Any,
    schemas: dict[str, dict[str, Any]],
    registry: Registry,
) -> tuple[list[str], bool]:
    """Return nested errors and whether any record is intentionally not verified."""
    errors: list[str] = []
    not_verified = False

    if not isinstance(document, dict):
        return errors, not_verified

    records = document.get("records")
    if not isinstance(records, list):
        return errors, not_verified

    local_exact: dict[tuple[str | None, str | None, str | None], tuple[Any, ...]] = {}
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            continue
        record_ref = record.get("logical_ref")
        exact = record.get("exact_binding")
        if record_ref is not None and exact is not None:
            if logical_identity(record_ref) != logical_identity(exact):
                errors.append(
                    f"records/{index}: exact_binding logical_ref does not match record logical_ref"
                )
        signature = binding_signature(exact)
        if signature is not None:
            local_exact[logical_identity(exact)] = signature

    for index, record in enumerate(records):
        if not isinstance(record, dict):
            continue
        contract = record.get("contract")
        if not isinstance(contract, dict):
            continue
        key = (contract.get("contract_id"), contract.get("version"))
        schema_name = KNOWN_RECORD_CONTRACTS.get(key)
        if schema_name is None:
            not_verified = True
            continue

        payload = record.get("payload")
        nested_schema_errors = schema_errors(schema_name, payload, schemas, registry)
        errors.extend(f"records/{index}/payload: {message}" for message in nested_schema_errors)

        if schema_name == "semantic-reference" and not nested_schema_errors:
            errors.extend(
                f"records/{index}/payload: {message}"
                for message in semantic_reference_errors(payload)
            )

        if schema_name == "decision-memory" and not nested_schema_errors:
            for basis in decision_basis_exact_bindings(payload):
                basis_identity = logical_identity(basis)
                local_signature = local_exact.get(basis_identity)
                if local_signature is None:
                    continue
                if binding_signature(basis) != local_signature:
                    errors.append(
                        f"records/{index}/payload: exact basis for {basis_identity} does not "
                        "match the exact record included in this interchange bundle"
                    )

        declared = payload.get("contract") if isinstance(payload, dict) else None
        expected_contract = f"{key[0]}/{key[1]}"
        if declared != expected_contract:
            errors.append(
                f"records/{index}/payload: declared contract {declared!r} does not "
                f"match envelope contract {expected_contract!r}"
            )

    return errors, not_verified


def semantic_errors(
    schema_name: str,
    document: Any,
    schemas: dict[str, dict[str, Any]],
    registry: Registry,
) -> tuple[list[str], bool]:
    errors: list[str] = []
    not_verified = False

    if schema_name == "semantic-reference":
        errors.extend(semantic_reference_errors(document))
    elif schema_name == "semantic-interchange":
        nested_errors, nested_not_verified = nested_interchange_status(document, schemas, registry)
        errors.extend(nested_errors)
        not_verified = nested_not_verified

    return errors, not_verified


def classify_fixture(
    expectation: FixtureExpectation,
    schemas: dict[str, dict[str, Any]],
    registry: Registry,
) -> tuple[str, list[str]]:
    document = load_json(FIXTURE_DIR / expectation.path)
    representation_errors = schema_errors(expectation.schema, document, schemas, registry)
    if representation_errors:
        return "schema_fail", representation_errors

    invariant_errors, not_verified = semantic_errors(expectation.schema, document, schemas, registry)
    if invariant_errors:
        return "semantic_fail", invariant_errors
    if not_verified:
        return "not_verified", ["contains an unknown nested Contract version"]
    return "pass", []


def main() -> int:
    schemas, registry = load_schemas()
    failures: list[str] = []
    results: list[dict[str, Any]] = []

    for expectation in FIXTURES:
        actual, details = classify_fixture(expectation, schemas, registry)
        ok = actual == expectation.expected
        results.append(
            {
                "fixture": expectation.path,
                "expected": expectation.expected,
                "actual": actual,
                "pass": ok,
                "details": details,
            }
        )
        if not ok:
            failures.append(
                f"{expectation.path}: expected {expectation.expected}, got {actual}: "
                + "; ".join(details)
            )

    summary = {
        "schema": "soza.contract-conformance-summary/v1",
        "contract_versions": [
            "soza.semantic-reference/v1alpha1",
            "soza.decision-memory/v1alpha1",
            "soza.capability-observation/v1alpha1",
            "soza.semantic-interchange/v1alpha1",
        ],
        "fixture_count": len(results),
        "passed": not failures,
        "results": results,
        "claims": {
            "design": "current Contract schemas and fixtures checked",
            "executable": "fixture-scoped only when this command completes successfully",
            "release": False,
            "operational": False,
            "stable_representation_profile": False,
        },
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))

    if failures:
        print("\nContract conformance failures:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
