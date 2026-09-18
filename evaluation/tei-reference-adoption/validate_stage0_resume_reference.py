#!/usr/bin/env python3
"""ISSUE-000079 Stage 0 source freeze / selector contract validator."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

SCHEMA = "sei.tei-reference-adoption-stage0-source-freeze/v1"
FIXTURE_SCHEMA = "sei.decision-continuity-comparison-fixture/v0"
EXPECTED_PATTERN_KINDS = ["browse", "record", "reference", "command", "header-detail"]
REQUIRED_INPUTS = {
    "/scenario/initial_question",
    "/scenario/phase_1",
    "/scenario/interruption_point",
    "/scenario/post_decision_evidence",
}
REQUIRED_ORACLES = {
    "/conditions/C_sei_resume/surface_text",
    "/reference_state",
}


def git_blob_sha1(payload: bytes) -> str:
    return hashlib.sha1(f"blob {len(payload)}\0".encode("ascii") + payload).hexdigest()


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def resolve_json_pointer(document: Any, pointer: str) -> Any:
    if pointer == "":
        return document
    if not pointer.startswith("/"):
        raise ValueError(f"JSON pointer must start with '/': {pointer!r}")
    current = document
    for raw in pointer[1:].split("/"):
        token = raw.replace("~1", "/").replace("~0", "~")
        if isinstance(current, dict):
            if token not in current:
                raise ValueError(f"JSON pointer does not resolve: {pointer!r}")
            current = current[token]
        elif isinstance(current, list):
            if not token.isdigit():
                raise ValueError(f"array index is not numeric in pointer: {pointer!r}")
            index = int(token)
            if index >= len(current):
                raise ValueError(f"array index is out of range in pointer: {pointer!r}")
            current = current[index]
        else:
            raise ValueError(f"JSON pointer crosses scalar value: {pointer!r}")
    return current


def pointers_overlap(left: str, right: str) -> bool:
    return left == right or left.startswith(right + "/") or right.startswith(left + "/")


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def validate_manifest(manifest: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    errors: list[str] = []

    if manifest.get("schema") != SCHEMA:
        errors.append(f"schema must be {SCHEMA}")
    if manifest.get("status") != "evaluation-only":
        errors.append("status must remain evaluation-only")
    if manifest.get("issue") != "ISSUE-000079":
        errors.append("issue must be ISSUE-000079")
    if manifest.get("artifact_role") != "evaluation-control-manifest-not-handoff-schema":
        errors.append("artifact_role must keep the manifest outside semantic handoff authority")

    source = manifest.get("source_authority")
    if not isinstance(source, dict):
        errors.append("source_authority must be an object")
        return {"valid": False, "errors": errors}

    fixture_rel = source.get("fixture_path")
    if not isinstance(fixture_rel, str) or not fixture_rel:
        errors.append("source_authority.fixture_path is required")
        return {"valid": False, "errors": errors}

    fixture_path = repo_root / fixture_rel
    if not fixture_path.is_file():
        errors.append(f"fixture does not exist: {fixture_rel}")
        return {"valid": False, "errors": errors}

    payload = fixture_path.read_bytes()
    if git_blob_sha1(payload) != source.get("git_blob_sha1"):
        errors.append("fixture Git blob SHA-1 does not match source freeze")
    if sha256(payload) != source.get("content_sha256"):
        errors.append("fixture content SHA-256 does not match source freeze")
    if len(payload) != source.get("byte_length"):
        errors.append("fixture byte length does not match source freeze")

    try:
        fixture = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        errors.append(f"fixture is not valid UTF-8 JSON: {exc}")
        return {"valid": False, "errors": errors}
    if not isinstance(fixture, dict):
        errors.append("fixture root must be an object")
        return {"valid": False, "errors": errors}

    if fixture.get("schema") != source.get("fixture_schema") or fixture.get("schema") != FIXTURE_SCHEMA:
        errors.append("fixture schema does not match frozen Decision Continuity schema")
    if fixture.get("fixture_id") != source.get("fixture_id"):
        errors.append("fixture_id does not match source freeze")

    inputs = manifest.get("input_json_pointers")
    oracles = manifest.get("oracle_json_pointers")
    if not isinstance(inputs, list) or not all(isinstance(item, str) for item in inputs):
        errors.append("input_json_pointers must be a string list")
        inputs = []
    if not isinstance(oracles, list) or not all(isinstance(item, str) for item in oracles):
        errors.append("oracle_json_pointers must be a string list")
        oracles = []

    if len(inputs) != len(set(inputs)):
        errors.append("input_json_pointers must not contain duplicates")
    if len(oracles) != len(set(oracles)):
        errors.append("oracle_json_pointers must not contain duplicates")
    if set(inputs) != REQUIRED_INPUTS:
        errors.append("input_json_pointers must equal the Stage 0 scenario selector set")
    if set(oracles) != REQUIRED_ORACLES:
        errors.append("oracle_json_pointers must equal the Stage 0 oracle selector set")
    for input_pointer in inputs:
        for oracle_pointer in oracles:
            if pointers_overlap(input_pointer, oracle_pointer):
                errors.append(
                    f"input/oracle pointers overlap: {input_pointer!r} vs {oracle_pointer!r}"
                )

    for pointer in inputs + oracles:
        try:
            resolve_json_pointer(fixture, pointer)
        except ValueError as exc:
            errors.append(str(exc))

    tei_context = manifest.get("tei_reference_context")
    if not isinstance(tei_context, dict):
        errors.append("tei_reference_context must be an object")
    else:
        if tei_context.get("application_pattern_kinds") != EXPECTED_PATTERN_KINDS:
            errors.append("TEI Application Pattern kind snapshot does not match Stage 0 baseline")
        if tei_context.get("new_pattern_kind_added_for_stage0") is not False:
            errors.append("Stage 0 must not claim a new TEI Application Pattern kind")

    scenario = fixture.get("scenario")
    if not isinstance(scenario, dict):
        errors.append("scenario must be an object")
        return {"valid": False, "errors": errors}

    phase_1 = scenario.get("phase_1")
    post = scenario.get("post_decision_evidence")
    if not isinstance(phase_1, list) or not all(isinstance(item, dict) for item in phase_1):
        errors.append("scenario.phase_1 must be an object list")
        phase_1 = []
    if not isinstance(post, list) or not all(isinstance(item, dict) for item in post):
        errors.append("scenario.post_decision_evidence must be an object list")
        post = []

    by_id: dict[str, dict[str, Any]] = {}
    for item in phase_1:
        item_id = item.get("id")
        if not isinstance(item_id, str) or not item_id:
            errors.append("every phase_1 item requires a non-empty id")
            continue
        if item_id in by_id:
            errors.append(f"duplicate phase_1 id: {item_id}")
        by_id[item_id] = item

    roles = {item.get("role") for item in phase_1}
    required_roles = manifest.get("required_semantic_roles")
    if not isinstance(required_roles, list) or set(required_roles) != {
        "observation", "recommendation", "unknown", "decision"
    }:
        errors.append("required_semantic_roles must preserve the four Stage 0 roles")
    elif not set(required_roles).issubset(roles):
        errors.append("fixture does not contain all required semantic roles")

    checks = manifest.get("reference_checks")
    if not isinstance(checks, dict):
        errors.append("reference_checks must be an object")
        checks = {}

    decision_id = checks.get("decision_id")
    recommendation_id = checks.get("recommendation_id")
    decision = by_id.get(decision_id)
    if not decision or decision.get("role") != "decision":
        errors.append("frozen decision_id must resolve to a decision")
        decision = {}
    recommendation = by_id.get(recommendation_id)
    if not recommendation or recommendation.get("role") != "recommendation":
        errors.append("frozen recommendation_id must resolve to a recommendation")

    role_expectations = (
        ("basis_refs", "observation"),
        ("recommendation_refs", "recommendation"),
        ("unresolved_refs", "unknown"),
    )
    for field, expected_role in role_expectations:
        refs = decision.get(field, [])
        if not isinstance(refs, list) or not refs:
            errors.append(f"decision.{field} must be a non-empty list")
            continue
        for ref in refs:
            target = by_id.get(ref)
            if target is None:
                errors.append(f"decision.{field} contains missing phase_1 ref: {ref}")
            elif target.get("role") != expected_role:
                errors.append(
                    f"decision.{field} ref {ref!r} must point to role {expected_role!r}"
                )

    post_ids = [item.get("id") for item in post]
    if any(not isinstance(item_id, str) or not item_id for item_id in post_ids):
        errors.append("every post_decision_evidence item requires a non-empty id")
    if set(post_ids) & set(by_id):
        errors.append("post-decision ids must not collide with phase_1 ids")
    if set(decision.get("basis_refs", [])) & set(post_ids):
        errors.append("post-decision evidence must not enter historical basis")

    reference_state = fixture.get("reference_state")
    if not isinstance(reference_state, dict):
        errors.append("reference_state must be an object")
    else:
        if reference_state.get("historical_basis_ids") != decision.get("basis_refs"):
            errors.append("reference_state historical_basis_ids must match decision.basis_refs")
        if reference_state.get("unresolved_ids") != decision.get("unresolved_refs"):
            errors.append("reference_state unresolved_ids must match decision.unresolved_refs")
        if reference_state.get("post_decision_ids") != post_ids:
            errors.append("reference_state post_decision_ids must match scenario post-decision ids")

    try:
        resume_oracle = resolve_json_pointer(
            fixture, "/conditions/C_sei_resume/surface_text"
        )
    except ValueError:
        resume_oracle = None
    expected_changes = checks.get("expected_oracle_changes_since_decision_at_interruption")
    if not isinstance(resume_oracle, dict):
        errors.append("C_sei_resume.surface_text must be an object")
    elif resume_oracle.get("changes_since_decision") != expected_changes:
        errors.append(
            "oracle changes_since_decision must reflect the interruption-time projection"
        )

    return {
        "valid": not errors,
        "errors": errors,
        "fixture": {
            "path": fixture_rel,
            "git_blob_sha1": git_blob_sha1(payload),
            "content_sha256": sha256(payload),
            "byte_length": len(payload),
            "fixture_id": fixture.get("fixture_id"),
        },
        "input_json_pointers": inputs,
        "oracle_json_pointers": oracles,
        "stop_line": (
            "Stage 0 source freeze valid != TEI Reference Executable Evidence "
            "!= human usability / Product Value Evidence"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="ISSUE-000079 Stage 0 Resume / Review source freezeを検証します。"
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path(__file__).with_name("stage0_resume_review_source_freeze_v1.json"),
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
    )
    args = parser.parse_args()

    try:
        manifest = load_json(args.manifest)
        result = validate_manifest(manifest, args.repo_root)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"valid": False, "errors": [str(exc)]}, ensure_ascii=False, indent=2))
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
