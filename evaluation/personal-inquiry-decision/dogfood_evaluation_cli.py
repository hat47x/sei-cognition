#!/usr/bin/env python3
"""Evaluation-only CLI for Personal Inquiry Continuity dogfood observations."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from dogfood_evaluation import (
    add_capture_observation,
    add_resume_observation,
    comparison_projection,
    load_evaluation,
    new_evaluation,
    save_evaluation,
)


def _dump(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Evaluation-only Personal Inquiry Continuity observation recorder"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("init")
    p.add_argument("path")
    p.add_argument("--case-id", required=True)
    p.add_argument("--inquiry-ref", required=True)
    p.add_argument(
        "--profile",
        required=True,
        choices=["B0-chat-only", "B1-final-note", "P1-sei"],
    )
    p.add_argument("--created-at", required=True)

    p = sub.add_parser("capture-add")
    p.add_argument("path")
    p.add_argument("--id", required=True)
    p.add_argument("--observed-at", required=True)
    p.add_argument("--semantic-corrections", type=int, default=0)
    p.add_argument(
        "--burden",
        default="not-observed",
        choices=["low", "medium", "high", "not-observed"],
    )
    p.add_argument("--notes")

    p = sub.add_parser("resume-add")
    p.add_argument("path")
    p.add_argument("--id", required=True)
    p.add_argument("--observed-at", required=True)
    p.add_argument(
        "--surface",
        required=True,
        choices=[
            "chat-only",
            "final-note",
            "generic-summary",
            "sei-orientation",
            "sei-quiet",
            "sei-proactive",
        ],
    )
    p.add_argument("--source-reopens", type=int, default=0)
    p.add_argument("--chat-reopens", type=int, default=0)
    p.add_argument("--detail-descents", type=int, default=0)
    p.add_argument("--false-continuity", action="store_true")
    p.add_argument(
        "--attention-load",
        default="not-observed",
        choices=["low", "medium", "high", "not-observed"],
    )
    for field in (
        "original-concern-retention",
        "unresolved-preservation",
        "temporal-integrity",
        "recommendation-decision-integrity",
        "suggestion-attribution-integrity",
        "material-change-visibility",
    ):
        p.add_argument(
            f"--{field}",
            default="not-observed",
            choices=["pass", "fail", "not-applicable", "not-observed"],
        )
    p.add_argument("--first-useful-action")
    p.add_argument("--notes")

    for name in ("compare", "show"):
        p = sub.add_parser(name)
        p.add_argument("path")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    path = Path(args.path)

    if args.command == "init":
        save_evaluation(
            path,
            new_evaluation(
                args.case_id,
                args.inquiry_ref,
                args.profile,
                args.created_at,
            ),
        )
        return 0

    record = load_evaluation(path)

    if args.command == "capture-add":
        observation = {
            "id": args.id,
            "observed_at": args.observed_at,
            "semantic_corrections": args.semantic_corrections,
            "burden": args.burden,
        }
        if args.notes:
            observation["notes"] = args.notes
        save_evaluation(path, add_capture_observation(record, observation))
        return 0

    if args.command == "resume-add":
        observation = {
            "id": args.id,
            "observed_at": args.observed_at,
            "surface": args.surface,
            "source_reopens": args.source_reopens,
            "chat_reopens": args.chat_reopens,
            "detail_descents": args.detail_descents,
            "false_continuity": args.false_continuity,
            "attention_load": args.attention_load,
            "original_concern_retention": args.original_concern_retention,
            "unresolved_preservation": args.unresolved_preservation,
            "temporal_integrity": args.temporal_integrity,
            "recommendation_decision_integrity": args.recommendation_decision_integrity,
            "suggestion_attribution_integrity": args.suggestion_attribution_integrity,
            "material_change_visibility": args.material_change_visibility,
        }
        if args.first_useful_action:
            observation["first_useful_action"] = args.first_useful_action
        if args.notes:
            observation["notes"] = args.notes
        save_evaluation(path, add_resume_observation(record, observation))
        return 0

    if args.command == "compare":
        _dump(comparison_projection(record))
        return 0

    if args.command == "show":
        _dump(record)
        return 0

    raise AssertionError(f"unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
