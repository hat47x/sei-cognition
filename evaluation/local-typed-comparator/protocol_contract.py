#!/usr/bin/env python3
"""Validate frozen typed-decision fixtures and Jev-compatible response payloads.

This module is provider-neutral. It validates the bounded protocol shape used by
the local Laya comparator research lane; it does not call a model or assert that
any returned decision is correct.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

FIXTURE_SCHEMA = "sei.local-typed-comparator-fixture/v1alpha1"
ALLOWED_QTYPES = {"choice", "score", "noul"}


class ProtocolContractError(ValueError):
    pass


def _real(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ProtocolContractError(f"{field} must be a real number")
    number = float(value)
    if not math.isfinite(number):
        raise ProtocolContractError(f"{field} must be finite")
    return number


def _probability(value: Any, field: str) -> float:
    number = _real(value, field)
    if not 0.0 <= number <= 1.0:
        raise ProtocolContractError(f"{field} must be within [0,1]")
    return number


def _nonempty_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ProtocolContractError(f"{field} must be a non-empty string")
    return value


def _validate_request(case_id: str, request: Any) -> None:
    if not isinstance(request, dict):
        raise ProtocolContractError(f"{case_id}: request must be an object")
    if "state" not in request or request["state"] is None:
        raise ProtocolContractError(f"{case_id}: state is required and must not be null")
    if isinstance(request["state"], str) and not request["state"].strip():
        raise ProtocolContractError(f"{case_id}: string state must not be empty")
    questions = request.get("questions")
    if not isinstance(questions, dict) or not questions:
        raise ProtocolContractError(f"{case_id}: questions must be a non-empty object")

    for qid, q in questions.items():
        _nonempty_text(qid, f"{case_id}: question id")
        if not isinstance(q, dict):
            raise ProtocolContractError(f"{case_id}/{qid}: question must be an object")
        qtype = q.get("type")
        if qtype not in ALLOWED_QTYPES:
            raise ProtocolContractError(f"{case_id}/{qid}: unsupported question type: {qtype!r}")
        _nonempty_text(q.get("instructions"), f"{case_id}/{qid}: instructions")
        criteria = q.get("criteria")
        if qtype == "choice":
            if not isinstance(criteria, dict) or len(criteria) < 2:
                raise ProtocolContractError(
                    f"{case_id}/{qid}: choice criteria must have at least two named options"
                )
            for key in criteria:
                _nonempty_text(key, f"{case_id}/{qid}: choice option")
        elif qtype == "score":
            if not isinstance(criteria, list) or len(criteria) < 2:
                raise ProtocolContractError(
                    f"{case_id}/{qid}: score criteria must have at least two ordered levels"
                )
            for index, label in enumerate(criteria):
                _nonempty_text(label, f"{case_id}/{qid}: score level {index}")
        elif criteria is not None and not isinstance(criteria, dict):
            raise ProtocolContractError(
                f"{case_id}/{qid}: noul criteria, when present, must be an object"
            )


def validate_fixture(fixture: dict[str, Any]) -> None:
    if fixture.get("schema") != FIXTURE_SCHEMA:
        raise ProtocolContractError(f"schema must be {FIXTURE_SCHEMA}")
    cases = fixture.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ProtocolContractError("cases must be a non-empty array")

    seen: set[str] = set()
    by_group: dict[str, list[dict[str, Any]]] = {}
    for case in cases:
        if not isinstance(case, dict):
            raise ProtocolContractError("every case must be an object")
        case_id = _nonempty_text(case.get("case_id"), "case_id")
        if case_id in seen:
            raise ProtocolContractError(f"duplicate case_id: {case_id}")
        seen.add(case_id)
        _validate_request(case_id, case.get("request"))
        group = case.get("perturbation_group")
        if group is not None:
            group = _nonempty_text(group, f"{case_id}: perturbation_group")
            by_group.setdefault(group, []).append(case)

    for group, members in by_group.items():
        if len(members) != 2:
            raise ProtocolContractError(
                f"perturbation group {group!r} must contain exactly two cases"
            )
        a, b = members
        ra, rb = a["request"], b["request"]
        if ra["state"] != rb["state"]:
            raise ProtocolContractError(
                f"perturbation group {group!r} must preserve state"
            )
        if set(ra["questions"]) != set(rb["questions"]):
            raise ProtocolContractError(
                f"perturbation group {group!r} must preserve question ids"
            )
        changed_order = False
        for qid in ra["questions"]:
            qa, qb = ra["questions"][qid], rb["questions"][qid]
            if qa["type"] != qb["type"] or qa["instructions"] != qb["instructions"]:
                raise ProtocolContractError(
                    f"perturbation group {group!r} changed question semantics"
                )
            if qa["type"] == "choice":
                if set(qa["criteria"]) != set(qb["criteria"]):
                    raise ProtocolContractError(
                        f"perturbation group {group!r} changed choice options"
                    )
                changed_order |= list(qa["criteria"]) != list(qb["criteria"])
            elif qa.get("criteria") != qb.get("criteria"):
                raise ProtocolContractError(
                    f"perturbation group {group!r} changed non-choice criteria"
                )
        if not changed_order:
            raise ProtocolContractError(
                f"perturbation group {group!r} did not actually change choice option order"
            )


def _validate_probability_map(probs: Any, keys: set[str], field: str) -> None:
    if not isinstance(probs, dict) or set(probs) != keys:
        raise ProtocolContractError(
            f"{field} keys must exactly match the question contract"
        )
    total = 0.0
    for key, value in probs.items():
        total += _probability(value, f"{field}.{key}")
    if abs(total - 1.0) > 1e-3:
        raise ProtocolContractError(
            f"{field} probabilities must sum to 1 within 1e-3"
        )


def validate_response(request: dict[str, Any], response: dict[str, Any]) -> None:
    _validate_request("response-contract", request)
    if not isinstance(response, dict):
        raise ProtocolContractError("response must be an object")
    _nonempty_text(response.get("model"), "response.model")
    answers = response.get("answers")
    if not isinstance(answers, dict) or set(answers) != set(request["questions"]):
        raise ProtocolContractError(
            "response.answers must contain exactly the requested question ids"
        )

    for qid, q in request["questions"].items():
        answer = answers[qid]
        if not isinstance(answer, dict) or answer.get("type") != q["type"]:
            raise ProtocolContractError(
                f"response.answers.{qid}.type must match the request"
            )
        if q["type"] == "choice":
            keys = set(q["criteria"])
            if answer.get("choice") not in keys:
                raise ProtocolContractError(
                    f"response.answers.{qid}.choice is outside the declared options"
                )
            _validate_probability_map(
                answer.get("probabilities"),
                keys,
                f"response.answers.{qid}.probabilities",
            )
            _probability(
                answer.get("confidence"), f"response.answers.{qid}.confidence"
            )
        elif q["type"] == "score":
            n = len(q["criteria"])
            score = _real(answer.get("score"), f"response.answers.{qid}.score")
            if not 0.0 <= score <= n - 1:
                raise ProtocolContractError(
                    f"response.answers.{qid}.score is outside the declared range"
                )
            expected_legend = {
                str(i): label for i, label in enumerate(q["criteria"])
            }
            if answer.get("legend") != expected_legend:
                raise ProtocolContractError(
                    f"response.answers.{qid}.legend must exactly match ordered criteria"
                )
            _validate_probability_map(
                answer.get("probabilities"),
                set(expected_legend),
                f"response.answers.{qid}.probabilities",
            )
            _probability(
                answer.get("confidence"), f"response.answers.{qid}.confidence"
            )
        else:
            _probability(answer.get("noul"), f"response.answers.{qid}.noul")

    usage = response.get("usage")
    if not isinstance(usage, dict):
        raise ProtocolContractError("response.usage must be an object")
    for field in ("input_tokens", "output_tokens"):
        value = usage.get(field)
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ProtocolContractError(
                f"response.usage.{field} must be a non-negative integer"
            )


def load_fixture(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProtocolContractError(f"cannot read fixture: {path}") from exc
    if not isinstance(value, dict):
        raise ProtocolContractError("fixture root must be an object")
    validate_fixture(value)
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("fixture", type=Path)
    args = parser.parse_args(argv)
    try:
        fixture = load_fixture(args.fixture)
    except ProtocolContractError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(
        json.dumps(
            {
                "valid": True,
                "schema": fixture["schema"],
                "cases": len(fixture["cases"]),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
