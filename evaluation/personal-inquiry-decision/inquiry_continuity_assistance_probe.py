#!/usr/bin/env python3
"""Build stage-gated ISSUE-000078 Quiet/Proactive assistance review packets.

This evaluation-only tool overlays provisional AI assistance on existing Inquiry
Continuity fixtures. Initial/reveal packets blind condition labels, responses are
bound to the exact probe/rotation/presentation order, and condition mapping is
revealed only at audit after both response stages are fixed.

It never mutates canonical meaning, never treats suggestion visibility as a
Stable Requirement, and never computes an overall winner.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
from typing import Any


SCHEMA = "sei.inquiry-continuity-assistance-probe/v1"
FIXTURE_SCHEMA = "sei.inquiry-continuity-comparison-fixture/v0"
PACKET_SCHEMA = "sei.inquiry-continuity-assistance-packet/v2"
RESPONSE_SCHEMA = "sei.inquiry-continuity-assistance-response/v3"
MATCHED_SET_SCHEMA = "sei.inquiry-continuity-matched-set/v0"
REVIEW_START_RECEIPT_SCHEMA = (
    "sei.inquiry-continuity-assistance-review-start-receipt/v1"
)
REVEAL_RECEIPT_SCHEMA = "sei.inquiry-continuity-assistance-reveal-receipt/v2"
AUDIT_RECEIPT_SCHEMA = "sei.inquiry-continuity-assistance-audit-receipt/v2"

CONDITIONS = {"A_proactive_first", "B_quiet_first", "C_adaptive_progressive"}
RESPONSE_STAGES = {"initial", "reveal"}
BURDEN_VALUES = {"low", "medium", "high", "not-observed"}
PRIOR_EXPOSURE_VALUES = {
    "none-declared",
    "known-material-exposure",
    "unknown",
}
RESPONSE_AUTHORSHIP_VALUES = {
    "human-direct",
    "human-transcribed",
}


class AssistanceProbeError(ValueError):
    pass


def load_json(path: str | Path) -> dict[str, Any]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AssistanceProbeError(f"cannot load JSON: {path}") from exc
    if not isinstance(value, dict):
        raise AssistanceProbeError(f"JSON root must be an object: {path}")
    return value


def git_blob_sha1(raw: bytes) -> str:
    header = f"blob {len(raw)}\0".encode("ascii")
    return hashlib.sha1(header + raw).hexdigest()


def probe_content_sha256(probe: dict[str, Any]) -> str:
    payload = json.dumps(
        probe,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _validate_questions(value: Any, stage: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise AssistanceProbeError(f"{stage} review questions are required")
    ids: list[str] = []
    for question in value:
        if not isinstance(question, dict):
            raise AssistanceProbeError(f"{stage} review question must be an object")
        question_id = question.get("id")
        if not isinstance(question_id, str) or not question_id.strip():
            raise AssistanceProbeError(
                f"{stage} review question id must be non-empty"
            )
        ids.append(question_id)
    if len(ids) != len(set(ids)):
        raise AssistanceProbeError(f"{stage} review question ids must be unique")
    return value


def _validate_rotations(probe: dict[str, Any], case_ids: list[str]) -> None:
    rotations = probe.get("assignment_rotations")
    if not isinstance(rotations, dict) or not rotations:
        raise AssistanceProbeError(
            "assignment_rotations must be a non-empty object"
        )
    seen = {case_id: set() for case_id in case_ids}
    for rotation, assignments in rotations.items():
        if not isinstance(assignments, list):
            raise AssistanceProbeError(f"rotation {rotation} must be a list")
        ids, conditions = [], []
        for item in assignments:
            if not isinstance(item, dict):
                raise AssistanceProbeError(
                    f"rotation {rotation} contains invalid assignment"
                )
            case_id, condition = item.get("fixture"), item.get("condition")
            if case_id not in seen or condition not in CONDITIONS:
                raise AssistanceProbeError(
                    f"rotation {rotation} contains invalid assignment"
                )
            ids.append(case_id)
            conditions.append(condition)
            seen[case_id].add(condition)
        if set(ids) != set(case_ids) or len(ids) != len(case_ids):
            raise AssistanceProbeError(
                f"rotation {rotation} must assign each case exactly once"
            )
        if set(conditions) != CONDITIONS or len(conditions) != len(CONDITIONS):
            raise AssistanceProbeError(
                f"rotation {rotation} must use each condition exactly once"
            )
    for case_id, values in seen.items():
        if values != CONDITIONS:
            raise AssistanceProbeError(
                f"{case_id} must receive every condition across rotations"
            )


def validate_probe(probe: dict[str, Any]) -> None:
    if probe.get("schema") != SCHEMA:
        raise AssistanceProbeError(f"schema must be {SCHEMA}")
    if (
        probe.get("status") != "evaluation-only"
        or probe.get("issue") != "ISSUE-000078"
    ):
        raise AssistanceProbeError(
            "probe must remain evaluation-only for ISSUE-000078"
        )

    stop = probe.get("semantic_stopline")
    if not isinstance(stop, dict):
        raise AssistanceProbeError("semantic_stopline must be an object")
    if stop.get("suggestions_are_canonical") is not False:
        raise AssistanceProbeError("AI suggestions must not be canonical")
    if stop.get("quiet_may_hide_canonical_orientation") is not False:
        raise AssistanceProbeError(
            "Quiet mode must not hide canonical orientation"
        )
    if stop.get("surface_choice_is_stable_requirement") is not False:
        raise AssistanceProbeError(
            "surface choice must not be a Stable Requirement"
        )
    if stop.get("overall_winner_allowed") is not False:
        raise AssistanceProbeError("overall winner must remain disallowed")

    rules = probe.get("presentation_rules")
    if not isinstance(rules, dict) or set(rules) != {
        "condition_labels_hidden_until_audit",
        "response_stages",
        "audit_reveals_condition_mapping",
        "same_fixture_multiple_conditions_before_fixed_response",
    }:
        raise AssistanceProbeError("presentation_rules has invalid shape")
    if rules["condition_labels_hidden_until_audit"] is not True:
        raise AssistanceProbeError(
            "condition labels must remain hidden until audit"
        )
    if rules["audit_reveals_condition_mapping"] is not True:
        raise AssistanceProbeError(
            "audit must reveal condition mapping for interpretation"
        )
    if rules["same_fixture_multiple_conditions_before_fixed_response"] is not False:
        raise AssistanceProbeError(
            "same fixture must not expose multiple conditions before fixed response"
        )
    if rules["response_stages"] != ["initial", "reveal"]:
        raise AssistanceProbeError(
            "response stages must be initial then reveal"
        )

    source_set = probe.get("source_set")
    if not isinstance(source_set, dict) or set(source_set) != {
        "path",
        "blob_sha1",
    }:
        raise AssistanceProbeError("source_set has invalid shape")
    if (
        not isinstance(source_set["path"], str)
        or not source_set["path"].strip()
        or Path(source_set["path"]).is_absolute()
        or ".." in Path(source_set["path"]).parts
        or not isinstance(source_set["blob_sha1"], str)
        or len(source_set["blob_sha1"]) != 40
        or any(
            character not in "0123456789abcdef"
            for character in source_set["blob_sha1"]
        )
    ):
        raise AssistanceProbeError("source_set path/blob binding is invalid")

    conditions = probe.get("conditions")
    if not isinstance(conditions, dict) or set(conditions) != CONDITIONS:
        raise AssistanceProbeError(
            "probe must define exactly three assistance conditions"
        )
    visibility = {
        name: value.get("initial_visibility")
        for name, value in conditions.items()
    }
    expected = {
        "A_proactive_first": "all",
        "B_quiet_first": "none",
        "C_adaptive_progressive": "primary-only",
    }
    if visibility != expected:
        raise AssistanceProbeError(
            "assistance visibility contract is invalid"
        )

    cases = probe.get("cases")
    if not isinstance(cases, list) or len(cases) != 3:
        raise AssistanceProbeError(
            "exactly three matched cases are required"
        )
    ids: list[str] = []
    for case in cases:
        if not isinstance(case, dict):
            raise AssistanceProbeError("case must be an object")
        for key in ("fixture_id", "path", "blob_sha1", "suggestions"):
            if not case.get(key):
                raise AssistanceProbeError(f"case missing {key}")
        suggestions = case["suggestions"]
        if not isinstance(suggestions, list) or len(suggestions) < 5:
            raise AssistanceProbeError(
                "each case requires at least five suggestions"
            )
        suggestion_ids = [item.get("id") for item in suggestions]
        if (
            len(suggestion_ids) != len(set(suggestion_ids))
            or None in suggestion_ids
        ):
            raise AssistanceProbeError(
                "suggestion ids must be unique and non-empty"
            )
        if sum(
            item.get("priority") == "primary"
            for item in suggestions
        ) != 1:
            raise AssistanceProbeError(
                "each case requires exactly one primary suggestion"
            )
        ids.append(case["fixture_id"])
    if len(ids) != len(set(ids)):
        raise AssistanceProbeError("fixture ids must be unique")
    _validate_rotations(probe, ids)

    questions = probe.get("review_questions")
    if not isinstance(questions, dict) or set(questions) != RESPONSE_STAGES:
        raise AssistanceProbeError(
            "review_questions must contain initial/reveal exactly"
        )
    for stage in ("initial", "reveal"):
        _validate_questions(questions[stage], stage)

    audit = probe.get("audit_key")
    if (
        not isinstance(audit, dict)
        or not audit.get("semantic_hard_failures")
    ):
        raise AssistanceProbeError(
            "audit_key with semantic hard failures is required"
        )
    boundary = probe.get("evidence_boundary")
    if not isinstance(boundary, dict):
        raise AssistanceProbeError(
            "evidence_boundary must be an object"
        )
    if boundary.get("human_review") != "not-yet-observed":
        raise AssistanceProbeError(
            "probe must not claim human review evidence"
        )
    if boundary.get("stable_requirement_change") != "not-authorized":
        raise AssistanceProbeError(
            "probe must not authorize Stable Requirement change"
        )


def load_sources(
    probe: dict[str, Any],
    repo_root: str | Path,
) -> dict[str, dict[str, Any]]:
    validate_probe(probe)
    root = Path(repo_root)
    source_set = probe["source_set"]
    source_set_path = root / source_set["path"]
    try:
        source_set_raw = source_set_path.read_bytes()
    except OSError as exc:
        raise AssistanceProbeError(
            f"cannot load source-set manifest: {source_set_path}"
        ) from exc
    if git_blob_sha1(source_set_raw) != source_set["blob_sha1"]:
        raise AssistanceProbeError(
            "source-set manifest changed after probe design"
        )
    try:
        source_set_value = json.loads(source_set_raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AssistanceProbeError(
            "source-set manifest must be valid UTF-8 JSON"
        ) from exc
    if (
        not isinstance(source_set_value, dict)
        or source_set_value.get("schema") != MATCHED_SET_SCHEMA
        or source_set_value.get("status") != "evaluation-only"
        or source_set_value.get("issue") != "ISSUE-000078"
    ):
        raise AssistanceProbeError(
            "source-set manifest has invalid identity"
        )
    manifest_fixtures = source_set_value.get("fixtures")
    if not isinstance(manifest_fixtures, list):
        raise AssistanceProbeError(
            "source-set manifest fixtures must be a list"
        )
    manifest_pairs = [
        (item.get("id"), item.get("path"))
        for item in manifest_fixtures
        if isinstance(item, dict)
    ]
    probe_pairs = [
        (case["fixture_id"], case["path"])
        for case in probe["cases"]
    ]
    if manifest_pairs != probe_pairs:
        raise AssistanceProbeError(
            "source-set manifest fixture identity/path differs from probe"
        )

    fixtures: dict[str, dict[str, Any]] = {}
    for case in probe["cases"]:
        path = root / case["path"]
        try:
            raw = path.read_bytes()
        except OSError as exc:
            raise AssistanceProbeError(
                f"cannot load source fixture: {path}"
            ) from exc
        if git_blob_sha1(raw) != case["blob_sha1"]:
            raise AssistanceProbeError(
                f"source fixture changed after probe design: "
                f"{case['fixture_id']}"
            )
        fixture = load_json(path)
        if (
            fixture.get("schema") != FIXTURE_SCHEMA
            or fixture.get("status") != "evaluation-only"
        ):
            raise AssistanceProbeError(
                f"invalid source fixture: {case['fixture_id']}"
            )
        if fixture.get("fixture_id") != case["fixture_id"]:
            raise AssistanceProbeError(
                f"source fixture id mismatch: {case['fixture_id']}"
            )
        scenario = fixture.get("scenario")
        if (
            not isinstance(scenario, dict)
            or scenario.get("decision_present") is not False
        ):
            raise AssistanceProbeError(
                f"source fixture must remain Decisionless: "
                f"{case['fixture_id']}"
            )
        try:
            orientation = fixture["conditions"]["C_sei_resume"][
                "surface_text"
            ]["orientation"]
        except (KeyError, TypeError) as exc:
            raise AssistanceProbeError(
                f"source fixture lacks SEI orientation: "
                f"{case['fixture_id']}"
            ) from exc
        if not isinstance(orientation, dict):
            raise AssistanceProbeError(
                f"orientation must be an object: {case['fixture_id']}"
            )
        fixtures[case["fixture_id"]] = fixture
    return fixtures


def _case_by_id(
    probe: dict[str, Any],
    fixture_id: str,
) -> dict[str, Any]:
    for case in probe["cases"]:
        if case["fixture_id"] == fixture_id:
            return case
    raise AssistanceProbeError(f"unknown fixture: {fixture_id}")


def _assignments(
    probe: dict[str, Any],
    rotation: str,
) -> list[dict[str, Any]]:
    try:
        return probe["assignment_rotations"][rotation]
    except KeyError as exc:
        raise AssistanceProbeError(f"unknown rotation: {rotation}") from exc


def _presentation_id(rotation: str, index: int) -> str:
    return f"{rotation}-P{index + 1}"


def _visible_suggestions(
    case: dict[str, Any],
    condition: str,
) -> list[dict[str, Any]]:
    suggestions = case["suggestions"]
    if condition == "A_proactive_first":
        return suggestions
    if condition == "B_quiet_first":
        return []
    return [
        item
        for item in suggestions
        if item.get("priority") == "primary"
    ]


def response_template(
    probe: dict[str, Any],
    rotation: str,
    stage: str,
    review_start_receipt_sha256: str,
    stage_gate_sha256: str | None = None,
) -> dict[str, Any]:
    validate_probe(probe)
    if stage not in RESPONSE_STAGES:
        raise AssistanceProbeError(
            "response stage must be initial or reveal"
        )
    if not _is_sha256(review_start_receipt_sha256):
        raise AssistanceProbeError(
            "response requires review-start receipt SHA-256"
        )
    if stage == "initial":
        if stage_gate_sha256 is not None:
            raise AssistanceProbeError(
                "initial response must not have a prior stage gate"
            )
    else:
        if not _is_sha256(stage_gate_sha256):
            raise AssistanceProbeError(
                "reveal response requires reveal receipt SHA-256"
            )
    assignments = _assignments(probe, rotation)
    questions = probe["review_questions"][stage]
    question_ids = [item["id"] for item in questions]
    return {
        "schema": RESPONSE_SCHEMA,
        "probe_sha256": probe_content_sha256(probe),
        "rotation": rotation,
        "stage": stage,
        "review_start_receipt_sha256": review_start_receipt_sha256,
        "stage_gate_sha256": stage_gate_sha256,
        "entries": [
            {
                "presentation_id": _presentation_id(rotation, index),
                "fixture_id": assignment["fixture"],
                "answers": {
                    question_id: ""
                    for question_id in question_ids
                },
                "operator_observation": {
                    "completion_seconds": "not-observed",
                    "source_reopen_count": "not-observed",
                    "attention_load": "not-observed",
                },
                "notes": "",
            }
            for index, assignment in enumerate(assignments)
        ],
        "notes": "",
    }

def _nonnegative_number_or_not_observed(
    value: Any,
    field: str,
) -> None:
    if value == "not-observed":
        return
    if (
        not isinstance(value, (int, float))
        or isinstance(value, bool)
        or value < 0
    ):
        raise AssistanceProbeError(
            f"{field} must be nonnegative or not-observed"
        )


def _nonnegative_int_or_not_observed(
    value: Any,
    field: str,
) -> None:
    if value == "not-observed":
        return
    if (
        not isinstance(value, int)
        or isinstance(value, bool)
        or value < 0
    ):
        raise AssistanceProbeError(
            f"{field} must be nonnegative integer or not-observed"
        )


def validate_response(
    value: Any,
    probe: dict[str, Any],
    rotation: str,
    stage: str,
    expected_review_start_receipt_sha256: str,
    expected_stage_gate_sha256: str | None = None,
) -> None:
    validate_probe(probe)
    if stage not in RESPONSE_STAGES:
        raise AssistanceProbeError(
            "response stage must be initial or reveal"
        )
    required = {
        "schema",
        "probe_sha256",
        "rotation",
        "stage",
        "review_start_receipt_sha256",
        "stage_gate_sha256",
        "entries",
        "notes",
    }
    if not isinstance(value, dict) or set(value) != required:
        raise AssistanceProbeError(
            "assistance response has invalid top-level shape"
        )
    if value["schema"] != RESPONSE_SCHEMA:
        raise AssistanceProbeError(
            f"assistance response schema must be {RESPONSE_SCHEMA}"
        )
    if value["probe_sha256"] != probe_content_sha256(probe):
        raise AssistanceProbeError(
            "assistance response is bound to different probe content"
        )
    if value["rotation"] != rotation or value["stage"] != stage:
        raise AssistanceProbeError(
            "assistance response rotation/stage mismatch"
        )
    if (
        not _is_sha256(expected_review_start_receipt_sha256)
        or value["review_start_receipt_sha256"]
        != expected_review_start_receipt_sha256
    ):
        raise AssistanceProbeError(
            "assistance response is bound to a different review-start receipt"
        )
    gate = value["stage_gate_sha256"]
    if stage == "initial":
        if gate is not None or expected_stage_gate_sha256 is not None:
            raise AssistanceProbeError(
                "initial response must not carry a prior stage gate"
            )
    else:
        if not _is_sha256(gate):
            raise AssistanceProbeError(
                "reveal response stage_gate_sha256 must be SHA-256"
            )
        if not _is_sha256(expected_stage_gate_sha256):
            raise AssistanceProbeError(
                "reveal response validation requires receipt SHA-256"
            )
        if gate != expected_stage_gate_sha256:
            raise AssistanceProbeError(
                "reveal response is bound to a different reveal receipt"
            )
    if not isinstance(value["notes"], str):
        raise AssistanceProbeError(
            "assistance response notes must be a string"
        )

    assignments = _assignments(probe, rotation)
    entries = value["entries"]
    if (
        not isinstance(entries, list)
        or len(entries) != len(assignments)
    ):
        raise AssistanceProbeError(
            "assistance response requires one entry per presentation"
        )
    question_ids = [
        item["id"]
        for item in probe["review_questions"][stage]
    ]
    for index, (entry, assignment) in enumerate(
        zip(entries, assignments)
    ):
        if not isinstance(entry, dict) or set(entry) != {
            "presentation_id",
            "fixture_id",
            "answers",
            "operator_observation",
            "notes",
        }:
            raise AssistanceProbeError(
                "assistance response entry has invalid shape"
            )
        if entry["presentation_id"] != _presentation_id(
            rotation,
            index,
        ):
            raise AssistanceProbeError(
                "assistance response presentation order mismatch"
            )
        if entry["fixture_id"] != assignment["fixture"]:
            raise AssistanceProbeError(
                "assistance response fixture order mismatch"
            )
        answers = entry["answers"]
        if (
            not isinstance(answers, dict)
            or list(answers) != question_ids
            or any(
                not isinstance(answer, str) or not answer.strip()
                for answer in answers.values()
            )
        ):
            raise AssistanceProbeError(
                "assistance response requires one non-empty answer "
                "per stage question"
            )
        observation = entry["operator_observation"]
        if not isinstance(observation, dict) or set(observation) != {
            "completion_seconds",
            "source_reopen_count",
            "attention_load",
        }:
            raise AssistanceProbeError(
                "operator_observation has invalid shape"
            )
        _nonnegative_number_or_not_observed(
            observation["completion_seconds"],
            "completion_seconds",
        )
        _nonnegative_int_or_not_observed(
            observation["source_reopen_count"],
            "source_reopen_count",
        )
        if observation["attention_load"] not in BURDEN_VALUES:
            raise AssistanceProbeError(
                "attention_load has invalid value"
            )
        if not isinstance(entry["notes"], str):
            raise AssistanceProbeError(
                "response entry notes must be a string"
            )


def load_response(
    path: str | Path,
    probe: dict[str, Any],
    rotation: str,
    stage: str,
    expected_review_start_receipt_sha256: str,
    expected_stage_gate_sha256: str | None = None,
) -> tuple[dict[str, Any], bytes]:
    try:
        raw = Path(path).read_bytes()
    except OSError as exc:
        raise AssistanceProbeError(
            f"cannot load {stage} response: {path}"
        ) from exc
    if not raw.strip():
        raise AssistanceProbeError(
            f"{stage} response must not be empty"
        )
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AssistanceProbeError(
            f"{stage} response must be valid UTF-8 JSON"
        ) from exc
    validate_response(
        value,
        probe,
        rotation,
        stage,
        expected_review_start_receipt_sha256,
        expected_stage_gate_sha256,
    )
    return value, raw


def response_sha256(
    path: str | Path,
    probe: dict[str, Any],
    rotation: str,
    stage: str,
    expected_review_start_receipt_sha256: str,
    expected_stage_gate_sha256: str | None = None,
) -> str:
    _, raw = load_response(
        path,
        probe,
        rotation,
        stage,
        expected_review_start_receipt_sha256,
        expected_stage_gate_sha256,
    )
    return hashlib.sha256(raw).hexdigest()


def _parse_timestamp(value: Any, field: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise AssistanceProbeError(
            f"{field} must be a non-empty timestamp"
        )
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise AssistanceProbeError(
            f"{field} must be ISO-8601"
        ) from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise AssistanceProbeError(
            f"{field} must include a timezone offset"
        )
    return parsed.astimezone(timezone.utc)


def _canonical_sha256(value: Any) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def stage_receipt_bytes(receipt: dict[str, Any]) -> bytes:
    return (
        json.dumps(receipt, ensure_ascii=False, indent=2) + "\n"
    ).encode("utf-8")


def _validate_receipt_value_raw_pair(
    value: dict[str, Any],
    raw: bytes,
    label: str,
) -> None:
    if not isinstance(raw, bytes) or not raw.strip():
        raise AssistanceProbeError(
            f"{label} raw bytes must not be empty"
        )
    try:
        decoded = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AssistanceProbeError(
            f"{label} raw bytes must be valid UTF-8 JSON"
        ) from exc
    if decoded != value:
        raise AssistanceProbeError(
            f"{label} value/raw bytes mismatch"
        )


def save_stage_receipt(
    path: str | Path,
    receipt: dict[str, Any],
    label: str,
) -> None:
    target = Path(path)
    payload = stage_receipt_bytes(receipt)
    try:
        with target.open("xb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError as exc:
        raise AssistanceProbeError(
            f"refusing to overwrite existing {label}: {target}"
        ) from exc


def _is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(
            character in "0123456789abcdef"
            for character in value
        )
    )


def build_review_start_receipt(
    probe: dict[str, Any],
    rotation: str,
    reviewer_id: str,
    prior_exposure: str,
    response_authorship: str,
    started_at: str,
) -> dict[str, Any]:
    validate_probe(probe)
    _assignments(probe, rotation)
    if (
        not isinstance(reviewer_id, str)
        or not reviewer_id.strip()
    ):
        raise AssistanceProbeError(
            "reviewer_id must be a non-empty opaque id"
        )
    if prior_exposure not in PRIOR_EXPOSURE_VALUES:
        raise AssistanceProbeError(
            "prior_exposure has invalid value"
        )
    if response_authorship not in RESPONSE_AUTHORSHIP_VALUES:
        raise AssistanceProbeError(
            "response_authorship must be human-direct or human-transcribed"
        )
    _parse_timestamp(started_at, "started_at")
    return {
        "schema": REVIEW_START_RECEIPT_SCHEMA,
        "status": "evaluation-only",
        "probe_id": probe["probe_id"],
        "probe_sha256": probe_content_sha256(probe),
        "rotation": rotation,
        "reviewer_id": reviewer_id,
        "prior_exposure": prior_exposure,
        "response_authorship": response_authorship,
        "started_at": started_at,
    }


def validate_review_start_receipt(
    value: Any,
    probe: dict[str, Any],
    rotation: str,
) -> None:
    required = {
        "schema",
        "status",
        "probe_id",
        "probe_sha256",
        "rotation",
        "reviewer_id",
        "prior_exposure",
        "response_authorship",
        "started_at",
    }
    if not isinstance(value, dict) or set(value) != required:
        raise AssistanceProbeError(
            "review-start receipt has invalid shape"
        )
    if value["schema"] != REVIEW_START_RECEIPT_SCHEMA:
        raise AssistanceProbeError(
            f"review-start receipt schema must be "
            f"{REVIEW_START_RECEIPT_SCHEMA}"
        )
    if (
        value["status"] != "evaluation-only"
        or value["probe_id"] != probe["probe_id"]
        or value["probe_sha256"] != probe_content_sha256(probe)
        or value["rotation"] != rotation
    ):
        raise AssistanceProbeError(
            "review-start receipt probe/rotation binding mismatch"
        )
    if (
        not isinstance(value["reviewer_id"], str)
        or not value["reviewer_id"].strip()
    ):
        raise AssistanceProbeError(
            "review-start reviewer_id must be a non-empty opaque id"
        )
    if value["prior_exposure"] not in PRIOR_EXPOSURE_VALUES:
        raise AssistanceProbeError(
            "review-start prior_exposure has invalid value"
        )
    if value["response_authorship"] not in RESPONSE_AUTHORSHIP_VALUES:
        raise AssistanceProbeError(
            "review-start response_authorship has invalid value"
        )
    _parse_timestamp(value["started_at"], "started_at")


def load_review_start_receipt(
    path: str | Path,
    probe: dict[str, Any],
    rotation: str,
) -> tuple[dict[str, Any], bytes]:
    try:
        raw = Path(path).read_bytes()
    except OSError as exc:
        raise AssistanceProbeError(
            f"cannot load review-start receipt: {path}"
        ) from exc
    if not raw.strip():
        raise AssistanceProbeError(
            "review-start receipt must not be empty"
        )
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AssistanceProbeError(
            "review-start receipt must be valid UTF-8 JSON"
        ) from exc
    validate_review_start_receipt(value, probe, rotation)
    _validate_receipt_value_raw_pair(
        value,
        raw,
        "review-start receipt",
    )
    return value, raw


def _reveal_material(
    probe: dict[str, Any],
    fixtures: dict[str, dict[str, Any]],
    rotation: str,
) -> list[dict[str, Any]]:
    assignments = _assignments(probe, rotation)
    result: list[dict[str, Any]] = []
    for index, assignment in enumerate(assignments):
        fixture_id = assignment["fixture"]
        fixture = fixtures[fixture_id]
        case = _case_by_id(probe, fixture_id)
        result.append(
            {
                "presentation_id": _presentation_id(rotation, index),
                "fixture_id": fixture_id,
                "title": fixture["title"],
                "all_ai_suggestions": case["suggestions"],
                "suggestion_provenance": (
                    "evaluation-only provisional AI suggestion; "
                    "not canonical meaning"
                ),
                "questions": probe["review_questions"]["reveal"],
                "semantic_stopline": probe["semantic_stopline"],
            }
        )
    return result


def _audit_material(
    probe: dict[str, Any],
    fixtures: dict[str, dict[str, Any]],
    rotation: str,
) -> list[dict[str, Any]]:
    assignments = _assignments(probe, rotation)
    result: list[dict[str, Any]] = []
    for index, assignment in enumerate(assignments):
        fixture_id = assignment["fixture"]
        condition = assignment["condition"]
        result.append(
            {
                "presentation_id": _presentation_id(rotation, index),
                "fixture_id": fixture_id,
                "condition": condition,
                "condition_contract": probe["conditions"][condition],
                "reference_state": fixtures[fixture_id]["reference_state"],
                "audit_key": probe["audit_key"],
                "evidence_boundary": probe["evidence_boundary"],
                "semantic_stopline": probe["semantic_stopline"],
            }
        )
    return result


def build_initial_packets(
    probe: dict[str, Any],
    fixtures: dict[str, dict[str, Any]],
    rotation: str,
    review_start_receipt_sha256: str,
) -> list[dict[str, Any]]:
    validate_probe(probe)
    if not _is_sha256(review_start_receipt_sha256):
        raise AssistanceProbeError(
            "initial packet requires review-start receipt SHA-256"
        )
    assignments = _assignments(probe, rotation)
    packets: list[dict[str, Any]] = []
    for index, assignment in enumerate(assignments):
        fixture_id = assignment["fixture"]
        condition = assignment["condition"]
        fixture = fixtures[fixture_id]
        case = _case_by_id(probe, fixture_id)
        visible = _visible_suggestions(case, condition)
        packets.append(
            {
                "schema": PACKET_SCHEMA,
                "status": "evaluation-only",
                "probe_id": probe["probe_id"],
                "probe_sha256": probe_content_sha256(probe),
                "presentation_id": _presentation_id(rotation, index),
                "fixture_id": fixture_id,
                "title": fixture["title"],
                "stage": "initial",
                "review_start_receipt_sha256": review_start_receipt_sha256,
                "canonical_orientation": fixture["conditions"][
                    "C_sei_resume"
                ]["surface_text"]["orientation"],
                "visible_ai_suggestions": visible,
                "more_suggestions_available": (
                    len(visible) < len(case["suggestions"])
                ),
                "suggestion_provenance": (
                    "evaluation-only provisional AI suggestion; "
                    "not canonical meaning"
                ),
                "questions": probe["review_questions"]["initial"],
                "semantic_stopline": probe["semantic_stopline"],
            }
        )
    return packets


def build_reveal_receipt(
    probe: dict[str, Any],
    fixtures: dict[str, dict[str, Any]],
    rotation: str,
    review_start_receipt_sha256: str,
    initial_response: str | Path,
    revealed_at: str,
) -> dict[str, Any]:
    validate_probe(probe)
    if not _is_sha256(review_start_receipt_sha256):
        raise AssistanceProbeError(
            "reveal receipt requires review-start receipt SHA-256"
        )
    initial_hash = response_sha256(
        initial_response,
        probe,
        rotation,
        "initial",
        review_start_receipt_sha256,
    )
    material_digest = _canonical_sha256(
        _reveal_material(probe, fixtures, rotation)
    )
    _parse_timestamp(revealed_at, "revealed_at")
    return {
        "schema": REVEAL_RECEIPT_SCHEMA,
        "status": "evaluation-only",
        "probe_id": probe["probe_id"],
        "probe_sha256": probe_content_sha256(probe),
        "rotation": rotation,
        "review_start_receipt_sha256": review_start_receipt_sha256,
        "fixed_initial_response_sha256": initial_hash,
        "reveal_material_sha256": material_digest,
        "revealed_at": revealed_at,
    }


def validate_reveal_receipt(
    value: Any,
    probe: dict[str, Any],
    fixtures: dict[str, dict[str, Any]],
    rotation: str,
    review_start_receipt_sha256: str,
    initial_response: str | Path,
) -> None:
    required = {
        "schema",
        "status",
        "probe_id",
        "probe_sha256",
        "rotation",
        "review_start_receipt_sha256",
        "fixed_initial_response_sha256",
        "reveal_material_sha256",
        "revealed_at",
    }
    if not isinstance(value, dict) or set(value) != required:
        raise AssistanceProbeError(
            "reveal receipt has invalid shape"
        )
    if value["schema"] != REVEAL_RECEIPT_SCHEMA:
        raise AssistanceProbeError(
            f"reveal receipt schema must be {REVEAL_RECEIPT_SCHEMA}"
        )
    if (
        value["status"] != "evaluation-only"
        or value["probe_id"] != probe["probe_id"]
        or value["probe_sha256"] != probe_content_sha256(probe)
        or value["rotation"] != rotation
    ):
        raise AssistanceProbeError(
            "reveal receipt probe/rotation binding mismatch"
        )
    if (
        not _is_sha256(review_start_receipt_sha256)
        or value["review_start_receipt_sha256"]
        != review_start_receipt_sha256
    ):
        raise AssistanceProbeError(
            "reveal receipt review-start binding mismatch"
        )
    expected_initial = response_sha256(
        initial_response,
        probe,
        rotation,
        "initial",
        review_start_receipt_sha256,
    )
    if value["fixed_initial_response_sha256"] != expected_initial:
        raise AssistanceProbeError(
            "reveal receipt is bound to a different initial response"
        )
    expected_material = _canonical_sha256(
        _reveal_material(probe, fixtures, rotation)
    )
    if value["reveal_material_sha256"] != expected_material:
        raise AssistanceProbeError(
            "reveal receipt is bound to different reveal material"
        )
    _parse_timestamp(value["revealed_at"], "revealed_at")


def load_reveal_receipt(
    path: str | Path,
    probe: dict[str, Any],
    fixtures: dict[str, dict[str, Any]],
    rotation: str,
    review_start_receipt_sha256: str,
    initial_response: str | Path,
) -> tuple[dict[str, Any], bytes]:
    try:
        raw = Path(path).read_bytes()
    except OSError as exc:
        raise AssistanceProbeError(
            f"cannot load reveal receipt: {path}"
        ) from exc
    if not raw.strip():
        raise AssistanceProbeError(
            "reveal receipt must not be empty"
        )
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AssistanceProbeError(
            "reveal receipt must be valid UTF-8 JSON"
        ) from exc
    validate_reveal_receipt(
        value,
        probe,
        fixtures,
        rotation,
        review_start_receipt_sha256,
        initial_response,
    )
    return value, raw


def build_reveal_packets(
    probe: dict[str, Any],
    fixtures: dict[str, dict[str, Any]],
    rotation: str,
    review_start_receipt_sha256: str,
    initial_response: str | Path,
    receipt_value: dict[str, Any],
    receipt_raw: bytes,
) -> list[dict[str, Any]]:
    validate_reveal_receipt(
        receipt_value,
        probe,
        fixtures,
        rotation,
        review_start_receipt_sha256,
        initial_response,
    )
    _validate_receipt_value_raw_pair(
        receipt_value,
        receipt_raw,
        "reveal receipt",
    )
    receipt_sha = hashlib.sha256(receipt_raw).hexdigest()
    result: list[dict[str, Any]] = []
    for item in _reveal_material(probe, fixtures, rotation):
        result.append(
            {
                "schema": PACKET_SCHEMA,
                "status": "evaluation-only",
                "probe_id": probe["probe_id"],
                "probe_sha256": probe_content_sha256(probe),
                **item,
                "stage": "reveal",
                "review_start_receipt_sha256": review_start_receipt_sha256,
                "fixed_initial_response_sha256": receipt_value[
                    "fixed_initial_response_sha256"
                ],
                "reveal_receipt_sha256": receipt_sha,
                "reveal_material_sha256": receipt_value[
                    "reveal_material_sha256"
                ],
            }
        )
    return result


def build_audit_receipt(
    probe: dict[str, Any],
    fixtures: dict[str, dict[str, Any]],
    rotation: str,
    review_start_receipt_sha256: str,
    initial_response: str | Path,
    reveal_response: str | Path,
    reveal_receipt_value: dict[str, Any],
    reveal_receipt_raw: bytes,
    revealed_at: str,
) -> dict[str, Any]:
    validate_reveal_receipt(
        reveal_receipt_value,
        probe,
        fixtures,
        rotation,
        review_start_receipt_sha256,
        initial_response,
    )
    _validate_receipt_value_raw_pair(
        reveal_receipt_value,
        reveal_receipt_raw,
        "reveal receipt",
    )
    reveal_receipt_sha = hashlib.sha256(
        reveal_receipt_raw
    ).hexdigest()
    reveal_response_hash = response_sha256(
        reveal_response,
        probe,
        rotation,
        "reveal",
        review_start_receipt_sha256,
        reveal_receipt_sha,
    )
    reveal_time = _parse_timestamp(
        reveal_receipt_value["revealed_at"],
        "reveal_revealed_at",
    )
    audit_time = _parse_timestamp(
        revealed_at,
        "audit_revealed_at",
    )
    if audit_time < reveal_time:
        raise AssistanceProbeError(
            "audit reveal must not precede reveal stage"
        )
    return {
        "schema": AUDIT_RECEIPT_SCHEMA,
        "status": "evaluation-only",
        "probe_id": probe["probe_id"],
        "probe_sha256": probe_content_sha256(probe),
        "rotation": rotation,
        "review_start_receipt_sha256": review_start_receipt_sha256,
        "reveal_receipt_sha256": reveal_receipt_sha,
        "fixed_initial_response_sha256": reveal_receipt_value[
            "fixed_initial_response_sha256"
        ],
        "fixed_reveal_response_sha256": reveal_response_hash,
        "audit_material_sha256": _canonical_sha256(
            _audit_material(probe, fixtures, rotation)
        ),
        "revealed_at": revealed_at,
    }


def validate_audit_receipt(
    value: Any,
    probe: dict[str, Any],
    fixtures: dict[str, dict[str, Any]],
    rotation: str,
    review_start_receipt_sha256: str,
    initial_response: str | Path,
    reveal_response: str | Path,
    reveal_receipt_value: dict[str, Any],
    reveal_receipt_raw: bytes,
) -> None:
    required = {
        "schema",
        "status",
        "probe_id",
        "probe_sha256",
        "rotation",
        "review_start_receipt_sha256",
        "reveal_receipt_sha256",
        "fixed_initial_response_sha256",
        "fixed_reveal_response_sha256",
        "audit_material_sha256",
        "revealed_at",
    }
    if not isinstance(value, dict) or set(value) != required:
        raise AssistanceProbeError(
            "audit receipt has invalid shape"
        )
    if value["schema"] != AUDIT_RECEIPT_SCHEMA:
        raise AssistanceProbeError(
            f"audit receipt schema must be {AUDIT_RECEIPT_SCHEMA}"
        )
    if (
        value["status"] != "evaluation-only"
        or value["probe_id"] != probe["probe_id"]
        or value["probe_sha256"] != probe_content_sha256(probe)
        or value["rotation"] != rotation
    ):
        raise AssistanceProbeError(
            "audit receipt probe/rotation binding mismatch"
        )
    validate_reveal_receipt(
        reveal_receipt_value,
        probe,
        fixtures,
        rotation,
        review_start_receipt_sha256,
        initial_response,
    )
    _validate_receipt_value_raw_pair(
        reveal_receipt_value,
        reveal_receipt_raw,
        "reveal receipt",
    )
    if (
        not _is_sha256(review_start_receipt_sha256)
        or value["review_start_receipt_sha256"]
        != review_start_receipt_sha256
    ):
        raise AssistanceProbeError(
            "audit receipt review-start binding mismatch"
        )
    expected_reveal_receipt_sha = hashlib.sha256(
        reveal_receipt_raw
    ).hexdigest()
    if value["reveal_receipt_sha256"] != expected_reveal_receipt_sha:
        raise AssistanceProbeError(
            "audit receipt is bound to a different reveal receipt"
        )
    if value["fixed_initial_response_sha256"] != reveal_receipt_value[
        "fixed_initial_response_sha256"
    ]:
        raise AssistanceProbeError(
            "audit receipt initial response binding mismatch"
        )
    expected_reveal_response = response_sha256(
        reveal_response,
        probe,
        rotation,
        "reveal",
        review_start_receipt_sha256,
        expected_reveal_receipt_sha,
    )
    if value["fixed_reveal_response_sha256"] != expected_reveal_response:
        raise AssistanceProbeError(
            "audit receipt is bound to a different reveal response"
        )
    expected_material = _canonical_sha256(
        _audit_material(probe, fixtures, rotation)
    )
    if value["audit_material_sha256"] != expected_material:
        raise AssistanceProbeError(
            "audit receipt is bound to different audit material"
        )
    if _parse_timestamp(
        value["revealed_at"],
        "audit_revealed_at",
    ) < _parse_timestamp(
        reveal_receipt_value["revealed_at"],
        "reveal_revealed_at",
    ):
        raise AssistanceProbeError(
            "audit reveal must not precede reveal stage"
        )


def build_audit_packets(
    probe: dict[str, Any],
    fixtures: dict[str, dict[str, Any]],
    rotation: str,
    review_start_receipt_sha256: str,
    initial_response: str | Path,
    reveal_response: str | Path,
    reveal_receipt_value: dict[str, Any],
    reveal_receipt_raw: bytes,
    audit_receipt_value: dict[str, Any],
    audit_receipt_raw: bytes,
) -> list[dict[str, Any]]:
    validate_audit_receipt(
        audit_receipt_value,
        probe,
        fixtures,
        rotation,
        review_start_receipt_sha256,
        initial_response,
        reveal_response,
        reveal_receipt_value,
        reveal_receipt_raw,
    )
    _validate_receipt_value_raw_pair(
        audit_receipt_value,
        audit_receipt_raw,
        "audit receipt",
    )
    audit_receipt_sha = hashlib.sha256(
        audit_receipt_raw
    ).hexdigest()
    result: list[dict[str, Any]] = []
    for item in _audit_material(probe, fixtures, rotation):
        result.append(
            {
                "schema": PACKET_SCHEMA,
                "status": "evaluation-only",
                "probe_id": probe["probe_id"],
                "probe_sha256": probe_content_sha256(probe),
                **item,
                "stage": "audit",
                "review_start_receipt_sha256": review_start_receipt_sha256,
                "fixed_initial_response_sha256": audit_receipt_value[
                    "fixed_initial_response_sha256"
                ],
                "fixed_reveal_response_sha256": audit_receipt_value[
                    "fixed_reveal_response_sha256"
                ],
                "reveal_receipt_sha256": audit_receipt_value[
                    "reveal_receipt_sha256"
                ],
                "audit_receipt_sha256": audit_receipt_sha,
                "audit_material_sha256": audit_receipt_value[
                    "audit_material_sha256"
                ],
            }
        )
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Build ISSUE-000078 blinded Quiet/Proactive "
            "assistance packets"
        )
    )
    parser.add_argument("--probe", required=True)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--rotation")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate")
    p = sub.add_parser("initial")
    p.add_argument("--receipt-output", required=True)
    p.add_argument("--reviewer-id", required=True)
    p.add_argument(
        "--prior-exposure",
        choices=sorted(PRIOR_EXPOSURE_VALUES),
        required=True,
    )
    p.add_argument(
        "--response-authorship",
        choices=sorted(RESPONSE_AUTHORSHIP_VALUES),
        required=True,
    )
    p.add_argument("--started-at", required=True)

    p = sub.add_parser("response-template")
    p.add_argument(
        "--stage",
        choices=sorted(RESPONSE_STAGES),
        required=True,
    )
    p.add_argument("--review-start-receipt", required=True)
    p.add_argument("--reveal-receipt")
    p.add_argument("--initial-response")

    p = sub.add_parser("reveal")
    p.add_argument("--review-start-receipt", required=True)
    p.add_argument("--initial-response", required=True)
    p.add_argument("--receipt-output", required=True)
    p.add_argument("--revealed-at", required=True)

    p = sub.add_parser("audit")
    p.add_argument("--review-start-receipt", required=True)
    p.add_argument("--initial-response", required=True)
    p.add_argument("--reveal-response", required=True)
    p.add_argument("--reveal-receipt", required=True)
    p.add_argument("--receipt-output", required=True)
    p.add_argument("--revealed-at", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    probe = load_json(args.probe)
    fixtures = load_sources(probe, args.repo_root)

    if args.command == "validate":
        print(
            json.dumps(
                {
                    "valid": True,
                    "probe_id": probe["probe_id"],
                    "probe_schema": probe["schema"],
                    "probe_sha256": probe_content_sha256(probe),
                    "packet_schema": PACKET_SCHEMA,
                    "response_schema": RESPONSE_SCHEMA,
                    "review_start_receipt_schema": REVIEW_START_RECEIPT_SCHEMA,
                    "reveal_receipt_schema": REVEAL_RECEIPT_SCHEMA,
                    "audit_receipt_schema": AUDIT_RECEIPT_SCHEMA,
                    "cases": len(fixtures),
                    "rotations": len(
                        probe["assignment_rotations"]
                    ),
                    "condition_labels_hidden_until_audit": True,
                    "evidence_boundary": probe["evidence_boundary"],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    if not args.rotation:
        raise AssistanceProbeError(
            "--rotation is required for packet/response generation"
        )

    if args.command == "initial":
        review_receipt = build_review_start_receipt(
            probe,
            args.rotation,
            args.reviewer_id,
            args.prior_exposure,
            args.response_authorship,
            args.started_at,
        )
        review_receipt_raw = stage_receipt_bytes(review_receipt)
        review_receipt_sha = hashlib.sha256(
            review_receipt_raw
        ).hexdigest()
        payload: Any = build_initial_packets(
            probe,
            fixtures,
            args.rotation,
            review_receipt_sha,
        )
        save_stage_receipt(
            args.receipt_output,
            review_receipt,
            "review-start receipt",
        )
    elif args.command == "response-template":
        _, review_receipt_raw = load_review_start_receipt(
            args.review_start_receipt,
            probe,
            args.rotation,
        )
        review_receipt_sha = hashlib.sha256(
            review_receipt_raw
        ).hexdigest()
        stage_gate_sha256 = None
        if args.stage == "reveal":
            if not args.reveal_receipt or not args.initial_response:
                raise AssistanceProbeError(
                    "reveal response-template requires "
                    "--reveal-receipt and --initial-response"
                )
            _, reveal_receipt_raw = load_reveal_receipt(
                args.reveal_receipt,
                probe,
                fixtures,
                args.rotation,
                review_receipt_sha,
                args.initial_response,
            )
            stage_gate_sha256 = hashlib.sha256(
                reveal_receipt_raw
            ).hexdigest()
        elif args.reveal_receipt or args.initial_response:
            raise AssistanceProbeError(
                "initial response-template must not receive "
                "reveal-stage receipt arguments"
            )
        payload = response_template(
            probe,
            args.rotation,
            args.stage,
            review_receipt_sha,
            stage_gate_sha256,
        )
    elif args.command == "reveal":
        _, review_receipt_raw = load_review_start_receipt(
            args.review_start_receipt,
            probe,
            args.rotation,
        )
        review_receipt_sha = hashlib.sha256(
            review_receipt_raw
        ).hexdigest()
        receipt = build_reveal_receipt(
            probe,
            fixtures,
            args.rotation,
            review_receipt_sha,
            args.initial_response,
            args.revealed_at,
        )
        receipt_raw = stage_receipt_bytes(receipt)
        payload = build_reveal_packets(
            probe,
            fixtures,
            args.rotation,
            review_receipt_sha,
            args.initial_response,
            receipt,
            receipt_raw,
        )
        save_stage_receipt(
            args.receipt_output,
            receipt,
            "reveal receipt",
        )
    elif args.command == "audit":
        _, review_receipt_raw = load_review_start_receipt(
            args.review_start_receipt,
            probe,
            args.rotation,
        )
        review_receipt_sha = hashlib.sha256(
            review_receipt_raw
        ).hexdigest()
        reveal_receipt, reveal_receipt_raw = load_reveal_receipt(
            args.reveal_receipt,
            probe,
            fixtures,
            args.rotation,
            review_receipt_sha,
            args.initial_response,
        )
        receipt = build_audit_receipt(
            probe,
            fixtures,
            args.rotation,
            review_receipt_sha,
            args.initial_response,
            args.reveal_response,
            reveal_receipt,
            reveal_receipt_raw,
            args.revealed_at,
        )
        receipt_raw = stage_receipt_bytes(receipt)
        payload = build_audit_packets(
            probe,
            fixtures,
            args.rotation,
            review_receipt_sha,
            args.initial_response,
            args.reveal_response,
            reveal_receipt,
            reveal_receipt_raw,
            receipt,
            receipt_raw,
        )
        save_stage_receipt(
            args.receipt_output,
            receipt,
            "audit receipt",
        )
    else:
        raise AssertionError(
            f"unhandled command: {args.command}"
        )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
