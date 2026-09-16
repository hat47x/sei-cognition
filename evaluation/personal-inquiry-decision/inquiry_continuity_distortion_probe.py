#!/usr/bin/env python3
"""Validate and present ISSUE-000078 AI-summary distortion probes.

This module is evaluation-only. It exposes an intentionally flawed AI
suggestion separately from its audit key. The audit command requires a fixed
human-response JSON file and only reports its hash; it never mutates canonical
SEI state.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

SCHEMA = "sei.inquiry-continuity-distortion-probe-set/v0"
PACKET_SCHEMA = "sei.inquiry-continuity-distortion-packet/v0"
REQUIRED_DISTORTIONS = {
    "certainty_inflation",
    "alternative_omission",
    "temporal_backfill",
}
STAGES = {"suggestion", "audit"}


class DistortionProbeError(ValueError):
    pass


def load_json(path: str | Path) -> dict[str, Any]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DistortionProbeError(f"cannot load JSON: {path}") from exc
    if not isinstance(value, dict):
        raise DistortionProbeError(f"JSON root must be an object: {path}")
    return value


def _sha256_file(path: str | Path) -> str:
    try:
        data = Path(path).read_bytes()
    except OSError as exc:
        raise DistortionProbeError(f"cannot load response: {path}") from exc
    if not data.strip():
        raise DistortionProbeError("human response file must not be empty")
    try:
        response = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise DistortionProbeError("human response must be valid UTF-8 JSON") from exc
    if response is None:
        raise DistortionProbeError("human response must not be null")
    return hashlib.sha256(data).hexdigest()


def validate_probe_set(
    probe_set: dict[str, Any],
    matched_manifest: dict[str, Any],
) -> None:
    if probe_set.get("schema") != SCHEMA:
        raise DistortionProbeError(f"schema must be {SCHEMA}")
    if probe_set.get("status") != "evaluation-only":
        raise DistortionProbeError("status must remain evaluation-only")
    if probe_set.get("issue") != "ISSUE-000078":
        raise DistortionProbeError("probe set must belong to ISSUE-000078")

    for key in (
        "probe_set_id",
        "base_matched_set",
        "required_distortions",
        "canonical_write_policy",
        "human_review_questions",
        "probes",
        "interpretation_stoplines",
    ):
        if key not in probe_set:
            raise DistortionProbeError(f"missing required key: {key}")

    required = set(probe_set["required_distortions"])
    if required != REQUIRED_DISTORTIONS:
        raise DistortionProbeError(
            "required_distortions must contain certainty_inflation, "
            "alternative_omission, and temporal_backfill exactly"
        )

    policy = probe_set["canonical_write_policy"]
    if not isinstance(policy, dict) or policy.get("automatic_write") is not False:
        raise DistortionProbeError("automatic canonical write must be false")

    if matched_manifest.get("status") != "evaluation-only":
        raise DistortionProbeError("base matched set must remain evaluation-only")
    base = probe_set["base_matched_set"]
    if not isinstance(base, dict) or base.get("set_id") != matched_manifest.get("set_id"):
        raise DistortionProbeError("base matched set id does not match manifest")

    fixture_ids = {
        item.get("id")
        for item in matched_manifest.get("fixtures", [])
        if isinstance(item, dict)
    }
    probes = probe_set["probes"]
    if not isinstance(probes, list) or not probes:
        raise DistortionProbeError("probes must be a non-empty list")

    probe_ids: set[str] = set()
    referenced_fixtures: set[str] = set()
    for probe in probes:
        if not isinstance(probe, dict):
            raise DistortionProbeError("each probe must be an object")
        for key in (
            "probe_id",
            "fixture_id",
            "presentation_timing",
            "flawed_ai_suggestion",
            "injected_distortions",
            "audit_key",
        ):
            if key not in probe:
                raise DistortionProbeError(f"probe missing required key: {key}")
        probe_id = probe["probe_id"]
        fixture_id = probe["fixture_id"]
        if not isinstance(probe_id, str) or not probe_id:
            raise DistortionProbeError("probe_id must be non-empty")
        if probe_id in probe_ids:
            raise DistortionProbeError(f"duplicate probe_id: {probe_id}")
        probe_ids.add(probe_id)
        if fixture_id not in fixture_ids:
            raise DistortionProbeError(f"unknown fixture_id: {fixture_id}")
        if fixture_id in referenced_fixtures:
            raise DistortionProbeError(f"fixture referenced more than once: {fixture_id}")
        referenced_fixtures.add(fixture_id)

        distortions = probe["injected_distortions"]
        if not isinstance(distortions, dict) or set(distortions) != REQUIRED_DISTORTIONS:
            raise DistortionProbeError(
                f"{probe_id} must inject exactly the three required distortion classes"
            )
        if any(not isinstance(items, list) or not items for items in distortions.values()):
            raise DistortionProbeError(
                f"{probe_id} must describe at least one injected error per distortion class"
            )
        suggestion = probe["flawed_ai_suggestion"]
        if not isinstance(suggestion, dict):
            raise DistortionProbeError(f"{probe_id} suggestion must be an object")
        if not suggestion.get("summary") or not suggestion.get("next_question"):
            raise DistortionProbeError(
                f"{probe_id} suggestion requires summary and next_question"
            )

    if referenced_fixtures != fixture_ids:
        raise DistortionProbeError(
            "probe set must cover each base matched-set fixture exactly once"
        )


def _find_probe(probe_set: dict[str, Any], probe_id: str) -> dict[str, Any]:
    for probe in probe_set["probes"]:
        if probe["probe_id"] == probe_id:
            return probe
    raise DistortionProbeError(f"unknown probe_id: {probe_id}")


def build_packet(
    probe_set: dict[str, Any],
    matched_manifest: dict[str, Any],
    probe_id: str,
    stage: str,
    response_path: str | Path | None = None,
) -> dict[str, Any]:
    validate_probe_set(probe_set, matched_manifest)
    if stage not in STAGES:
        raise DistortionProbeError(f"invalid stage: {stage}")
    probe = _find_probe(probe_set, probe_id)
    packet: dict[str, Any] = {
        "schema": PACKET_SCHEMA,
        "status": "evaluation-only",
        "probe_set_id": probe_set["probe_set_id"],
        "probe_id": probe_id,
        "fixture_id": probe["fixture_id"],
        "stage": stage,
    }
    if stage == "suggestion":
        packet["flawed_ai_suggestion"] = probe["flawed_ai_suggestion"]
        packet["questions"] = probe_set["human_review_questions"]
        packet["canonical_write_policy"] = probe_set["canonical_write_policy"]
        return packet

    if response_path is None:
        raise DistortionProbeError(
            "audit requires a fixed human-response JSON file"
        )
    packet["fixed_response_sha256"] = _sha256_file(response_path)
    packet["audit_key"] = probe["audit_key"]
    packet["injected_distortions"] = probe["injected_distortions"]
    packet["canonical_write_policy"] = probe_set["canonical_write_policy"]
    return packet


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate or present ISSUE-000078 AI-summary distortion probes"
    )
    parser.add_argument("--probe-set", required=True)
    parser.add_argument("--matched-manifest", required=True)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("validate")

    p = sub.add_parser("suggestion")
    p.add_argument("--probe-id", required=True)

    p = sub.add_parser("audit")
    p.add_argument("--probe-id", required=True)
    p.add_argument("--response", required=True)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    probe_set = load_json(args.probe_set)
    matched_manifest = load_json(args.matched_manifest)
    validate_probe_set(probe_set, matched_manifest)

    if args.command == "validate":
        print(
            json.dumps(
                {
                    "valid": True,
                    "probe_set_id": probe_set["probe_set_id"],
                    "probes": len(probe_set["probes"]),
                    "automatic_canonical_write": False,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    if args.command == "suggestion":
        packet = build_packet(
            probe_set, matched_manifest, args.probe_id, "suggestion"
        )
    elif args.command == "audit":
        packet = build_packet(
            probe_set,
            matched_manifest,
            args.probe_id,
            "audit",
            args.response,
        )
    else:
        raise AssertionError(f"unhandled command: {args.command}")

    print(json.dumps(packet, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
