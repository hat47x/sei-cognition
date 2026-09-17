#!/usr/bin/env python3
"""Build stage-gated ISSUE-000078 E78.3 AI-summary-distortion packets.

The distorted summary is deliberately provisional evaluation material. The source
fixture remains authoritative for the historical comparison; neither a distorted
summary nor a human correction mutates canonical Inquiry meaning.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

SCHEMA = "sei.inquiry-continuity-summary-distortion-probe/v0"
FIXTURE_SCHEMA = "sei.inquiry-continuity-comparison-fixture/v0"
PACKET_SCHEMA = "sei.inquiry-continuity-summary-distortion-packet/v0"
REQUIRED_KINDS = {"hypothesis_to_certainty", "alternate_hypothesis_omission", "temporal_backfill"}


class SummaryDistortionProbeError(ValueError):
    pass


def load_json(path: str | Path) -> dict[str, Any]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SummaryDistortionProbeError(f"cannot load JSON: {path}") from exc
    if not isinstance(value, dict):
        raise SummaryDistortionProbeError("JSON root must be an object")
    return value


def git_blob_sha1(raw: bytes) -> str:
    return hashlib.sha1(f"blob {len(raw)}\0".encode("ascii") + raw).hexdigest()


def response_sha256(path: str | Path) -> str:
    try:
        raw = Path(path).read_bytes()
    except OSError as exc:
        raise SummaryDistortionProbeError(f"cannot load response: {path}") from exc
    if not raw.strip():
        raise SummaryDistortionProbeError("human response must not be empty")
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SummaryDistortionProbeError("human response must be valid UTF-8 JSON") from exc
    if not isinstance(value, dict) or not value:
        raise SummaryDistortionProbeError("human response must be a non-empty object")
    return hashlib.sha256(raw).hexdigest()


def validate_probe(probe: dict[str, Any]) -> None:
    if probe.get("schema") != SCHEMA:
        raise SummaryDistortionProbeError(f"schema must be {SCHEMA}")
    if probe.get("status") != "evaluation-only" or probe.get("issue") != "ISSUE-000078":
        raise SummaryDistortionProbeError("probe must remain evaluation-only for ISSUE-000078")
    stop = probe.get("semantic_stopline")
    expected_false = (
        "distorted_summary_is_canonical",
        "ai_summary_may_overwrite_source",
        "correction_may_mutate_historical_state",
        "overall_score_or_winner_allowed",
        "stable_requirement_change_authorized",
    )
    if not isinstance(stop, dict) or any(stop.get(key) is not False for key in expected_false):
        raise SummaryDistortionProbeError("semantic stopline is incomplete")

    cases = probe.get("cases")
    if not isinstance(cases, list) or len(cases) != 3:
        raise SummaryDistortionProbeError("exactly three distortion cases are required")
    ids: list[str] = []
    for case in cases:
        if not isinstance(case, dict):
            raise SummaryDistortionProbeError("case must be an object")
        for key in ("fixture_id", "path", "blob_sha1", "distorted_summary", "distortion_key"):
            if not case.get(key):
                raise SummaryDistortionProbeError(f"case missing {key}")
        kinds = {item.get("kind") for item in case["distortion_key"] if isinstance(item, dict)}
        if not REQUIRED_KINDS.issubset(kinds):
            raise SummaryDistortionProbeError(
                f"{case['fixture_id']} must cover certainty, omission, and temporal backfill"
            )
        ids.append(case["fixture_id"])
    if len(ids) != len(set(ids)):
        raise SummaryDistortionProbeError("fixture ids must be unique")
    questions = probe.get("review_questions")
    if not isinstance(questions, list) or len(questions) < 5:
        raise SummaryDistortionProbeError("review questions are incomplete")
    if not probe.get("audit_dimensions"):
        raise SummaryDistortionProbeError("audit dimensions are required")


def load_sources(probe: dict[str, Any], repo_root: str | Path) -> dict[str, dict[str, Any]]:
    validate_probe(probe)
    root = Path(repo_root)
    result: dict[str, dict[str, Any]] = {}
    for case in probe["cases"]:
        path = root / case["path"]
        try:
            raw = path.read_bytes()
        except OSError as exc:
            raise SummaryDistortionProbeError(f"cannot load source fixture: {path}") from exc
        if git_blob_sha1(raw) != case["blob_sha1"]:
            raise SummaryDistortionProbeError(
                f"source fixture changed after probe design: {case['fixture_id']}"
            )
        fixture = load_json(path)
        if fixture.get("schema") != FIXTURE_SCHEMA or fixture.get("status") != "evaluation-only":
            raise SummaryDistortionProbeError(f"invalid source fixture: {case['fixture_id']}")
        if fixture.get("fixture_id") != case["fixture_id"]:
            raise SummaryDistortionProbeError(f"fixture id mismatch: {case['fixture_id']}")
        if fixture.get("scenario", {}).get("decision_present") is not False:
            raise SummaryDistortionProbeError("E78.3 source fixture must remain Decisionless")
        result[case["fixture_id"]] = fixture
    return result


def _case(probe: dict[str, Any], fixture_id: str) -> dict[str, Any]:
    for case in probe["cases"]:
        if case["fixture_id"] == fixture_id:
            return case
    raise SummaryDistortionProbeError(f"unknown fixture: {fixture_id}")


def build_review_packet(
    probe: dict[str, Any], fixtures: dict[str, dict[str, Any]], fixture_id: str
) -> dict[str, Any]:
    case, fixture = _case(probe, fixture_id), fixtures[fixture_id]
    orientation = fixture["conditions"]["C_sei_resume"]["surface_text"]["orientation"]
    return {
        "schema": PACKET_SCHEMA,
        "status": "evaluation-only",
        "probe_id": probe["probe_id"],
        "fixture_id": fixture_id,
        "stage": "review",
        "canonical_orientation": orientation,
        "provisional_ai_summary": case["distorted_summary"],
        "summary_provenance": "deliberately fallible evaluation-only AI summary; not canonical meaning",
        "questions": probe["review_questions"],
        "semantic_stopline": probe["semantic_stopline"],
    }


def build_audit_packet(
    probe: dict[str, Any], fixtures: dict[str, dict[str, Any]], fixture_id: str, response: str | Path
) -> dict[str, Any]:
    fixed = response_sha256(response)
    case, fixture = _case(probe, fixture_id), fixtures[fixture_id]
    return {
        "schema": PACKET_SCHEMA,
        "status": "evaluation-only",
        "probe_id": probe["probe_id"],
        "fixture_id": fixture_id,
        "stage": "audit",
        "fixed_human_response_sha256": fixed,
        "distortion_key": case["distortion_key"],
        "reference_state": fixture["reference_state"],
        "post_interruption_evidence": fixture["scenario"]["post_interruption_evidence"],
        "audit_dimensions": probe["audit_dimensions"],
        "evidence_boundary": probe["evidence_boundary"],
        "semantic_stopline": probe["semantic_stopline"],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build ISSUE-000078 E78.3 summary-distortion packets")
    parser.add_argument("--probe", required=True)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--fixture-id")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate")
    sub.add_parser("review")
    audit = sub.add_parser("audit")
    audit.add_argument("--response", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    probe = load_json(args.probe)
    fixtures = load_sources(probe, args.repo_root)
    if args.command == "validate":
        result = {"valid": True, "probe_id": probe["probe_id"], "cases": len(fixtures)}
    else:
        if not args.fixture_id:
            raise SummaryDistortionProbeError("--fixture-id is required for review/audit")
        if args.fixture_id not in fixtures:
            raise SummaryDistortionProbeError(f"unknown fixture: {args.fixture_id}")
        if args.command == "review":
            result = build_review_packet(probe, fixtures, args.fixture_id)
        elif args.command == "audit":
            result = build_audit_packet(probe, fixtures, args.fixture_id, args.response)
        else:
            raise AssertionError(f"unhandled command: {args.command}")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
