#!/usr/bin/env python3
"""Evaluation-only CLI for Personal Inquiry Continuity dogfooding."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from dogfood_core import (
    add_decision,
    add_record,
    add_review,
    add_source,
    baseline_material_projection,
    handoff_projection,
    load_state,
    new_state,
    orientation_projection,
    save_state,
)


def _dump(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Evaluation-only local Personal Inquiry Continuity dogfood CLI"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("init")
    p.add_argument("path")
    p.add_argument("--question", required=True)
    p.add_argument("--at", required=True)

    p = sub.add_parser("source-add")
    p.add_argument("path")
    p.add_argument("--id", required=True)
    p.add_argument("--locator", required=True)
    p.add_argument("--captured-at", required=True)
    p.add_argument("--title")
    p.add_argument("--kind", default="reference")

    p = sub.add_parser("record-add")
    p.add_argument("path")
    p.add_argument(
        "--kind",
        required=True,
        choices=["observation", "unknown", "conflict", "hypothesis", "recommendation"],
    )
    p.add_argument("--id", required=True)
    p.add_argument("--summary", required=True)
    p.add_argument("--captured-at", required=True)
    p.add_argument("--subject-at")
    p.add_argument("--source-ref", action="append", default=[])
    p.add_argument("--status", choices=["open", "resolved"])

    p = sub.add_parser("decision-add")
    p.add_argument("path")
    p.add_argument("--id", required=True)
    p.add_argument("--statement", required=True)
    p.add_argument("--decided-at", required=True)
    p.add_argument("--basis-ref", action="append", default=[])
    p.add_argument("--unresolved-ref", action="append", default=[])
    p.add_argument("--revisit-when", action="append", default=[])

    p = sub.add_parser("review")
    p.add_argument("path")
    p.add_argument("--id", required=True)
    p.add_argument("--reviewed-at", required=True)
    p.add_argument("--resume-anchor")

    for name in ("orient", "baseline-material", "handoff", "show"):
        p = sub.add_parser(name)
        p.add_argument("path")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    path = Path(args.path)

    if args.command == "init":
        save_state(path, new_state(args.question, args.at))
        return 0

    state = load_state(path)

    if args.command == "source-add":
        source = {
            "id": args.id,
            "kind": args.kind,
            "locator": args.locator,
            "captured_at": args.captured_at,
        }
        if args.title:
            source["title"] = args.title
        save_state(path, add_source(state, source))
        return 0

    if args.command == "record-add":
        record = {
            "id": args.id,
            "kind": args.kind,
            "summary": args.summary,
            "captured_at": args.captured_at,
            "source_refs": args.source_ref,
        }
        if args.subject_at:
            record["subject_at"] = args.subject_at
        if args.status:
            record["status"] = args.status
        save_state(path, add_record(state, record))
        return 0

    if args.command == "decision-add":
        decision = {
            "id": args.id,
            "statement": args.statement,
            "decided_at": args.decided_at,
            "basis_refs": args.basis_ref,
            "unresolved_refs": args.unresolved_ref,
            "revisit_when": args.revisit_when,
        }
        save_state(path, add_decision(state, decision))
        return 0

    if args.command == "review":
        review = {
            "id": args.id,
            "reviewed_at": args.reviewed_at,
        }
        if args.resume_anchor:
            review["resume_anchor"] = args.resume_anchor
        save_state(path, add_review(state, review))
        return 0

    if args.command == "orient":
        _dump(orientation_projection(state))
        return 0

    if args.command == "baseline-material":
        _dump(baseline_material_projection(state))
        return 0

    if args.command == "handoff":
        _dump(handoff_projection(state))
        return 0

    if args.command == "show":
        _dump(state)
        return 0

    raise AssertionError(f"unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
