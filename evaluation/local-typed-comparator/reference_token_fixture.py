#!/usr/bin/env python3
"""Validate retained reference-side token Evidence for the local typed comparator.

This validator proves structural integrity and fixture binding of the retained
input-token/marker packet. It does not recreate the tokenizer, attest a
candidate runtime, load a model, or claim numeric parity.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

SCHEMA = "sei.local-typed-comparator-reference-token-fixture/v1"


class ReferenceTokenFixtureError(ValueError):
    pass


def _positive_int(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ReferenceTokenFixtureError(f"{field} must be a positive integer")
    return value


def _nonnegative_int(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ReferenceTokenFixtureError(f"{field} must be a non-negative integer")
    return value


def _expected_option_count(question: dict[str, Any]) -> int:
    qtype = question.get("type")
    criteria = question.get("criteria")
    if qtype == "choice":
        if not isinstance(criteria, dict):
            raise ReferenceTokenFixtureError("choice criteria must be an object")
        return len(criteria)
    if qtype == "score":
        if not isinstance(criteria, list):
            raise ReferenceTokenFixtureError("score criteria must be an array")
        return len(criteria)
    if qtype == "noul":
        return 2
    raise ReferenceTokenFixtureError(f"unsupported question type: {qtype!r}")


def validate_reference_token_fixture(
    fixture: dict[str, Any], token_fixture: dict[str, Any]
) -> None:
    if token_fixture.get("schema") != SCHEMA:
        raise ReferenceTokenFixtureError(f"schema must be {SCHEMA}")

    fixture_meta = token_fixture.get("fixture")
    if not isinstance(fixture_meta, dict):
        raise ReferenceTokenFixtureError("fixture metadata must be an object")
    if fixture_meta.get("schema") != fixture.get("schema"):
        raise ReferenceTokenFixtureError("fixture schema binding does not match")

    tokenizer = token_fixture.get("tokenizer")
    if not isinstance(tokenizer, dict):
        raise ReferenceTokenFixtureError("tokenizer metadata must be an object")
    _positive_int(tokenizer.get("bytes"), "tokenizer.bytes")
    sha256 = tokenizer.get("sha256")
    if (
        not isinstance(sha256, str)
        or len(sha256) != 64
        or any(c not in "0123456789abcdef" for c in sha256)
    ):
        raise ReferenceTokenFixtureError("tokenizer.sha256 must be lowercase hex SHA-256")

    implementation = token_fixture.get("tokenizer_implementation")
    if not isinstance(implementation, dict):
        raise ReferenceTokenFixtureError("tokenizer_implementation must be an object")
    fuzz_cases = _positive_int(
        implementation.get("fuzz_cases"), "tokenizer_implementation.fuzz_cases"
    )
    fuzz_pass = _positive_int(
        implementation.get("fuzz_pass"), "tokenizer_implementation.fuzz_pass"
    )
    if fuzz_pass != fuzz_cases:
        raise ReferenceTokenFixtureError("tokenizer fuzz replay must be complete")

    scope = token_fixture.get("scope")
    if not isinstance(scope, dict):
        raise ReferenceTokenFixtureError("scope must be an object")
    if scope.get("candidate_side_tokenizer_attested") is not False:
        raise ReferenceTokenFixtureError(
            "reference token fixture must not attest the candidate-side tokenizer"
        )
    if scope.get("numeric_model_parity") is not False:
        raise ReferenceTokenFixtureError(
            "reference token fixture must not claim numeric model parity"
        )

    special = token_fixture.get("special_token_ids")
    if not isinstance(special, dict):
        raise ReferenceTokenFixtureError("special_token_ids must be an object")
    special_ids = {}
    for name in ("cls", "sep", "mask", "pad"):
        special_ids[name] = _nonnegative_int(
            special.get(name), f"special_token_ids.{name}"
        )
    if len(set(special_ids.values())) != len(special_ids):
        raise ReferenceTokenFixtureError("special token ids must be distinct")

    fixture_cases = fixture.get("cases")
    if not isinstance(fixture_cases, list) or not fixture_cases:
        raise ReferenceTokenFixtureError("fixture cases must be a non-empty array")
    source_by_id = {}
    for case in fixture_cases:
        if not isinstance(case, dict) or not isinstance(case.get("case_id"), str):
            raise ReferenceTokenFixtureError("fixture cases require string case_id")
        source_by_id[case["case_id"]] = case

    retained_cases = token_fixture.get("cases")
    if not isinstance(retained_cases, list):
        raise ReferenceTokenFixtureError("token fixture cases must be an array")
    retained_ids = [case.get("case_id") for case in retained_cases if isinstance(case, dict)]
    if set(retained_ids) != set(source_by_id) or len(retained_ids) != len(source_by_id):
        raise ReferenceTokenFixtureError("retained case ids must exactly match frozen fixture")

    for retained in retained_cases:
        if not isinstance(retained, dict):
            raise ReferenceTokenFixtureError("each retained case must be an object")
        case_id = retained["case_id"]
        source = source_by_id[case_id]
        request = source.get("request")
        questions = request.get("questions") if isinstance(request, dict) else None
        if not isinstance(questions, dict) or len(questions) != 1:
            raise ReferenceTokenFixtureError(
                f"{case_id}: reference token fixture requires exactly one question"
            )
        question_id, question = next(iter(questions.items()))
        if retained.get("question_id") != question_id:
            raise ReferenceTokenFixtureError(f"{case_id}: question id drift")
        if retained.get("question_type") != question.get("type"):
            raise ReferenceTokenFixtureError(f"{case_id}: question type drift")

        expected_options = _expected_option_count(question)
        if retained.get("option_count") != expected_options:
            raise ReferenceTokenFixtureError(f"{case_id}: option count drift")

        ids = retained.get("input_ids")
        if (
            not isinstance(ids, list)
            or not ids
            or any(isinstance(v, bool) or not isinstance(v, int) or v < 0 for v in ids)
        ):
            raise ReferenceTokenFixtureError(
                f"{case_id}: input_ids must be non-negative integers"
            )
        if retained.get("token_count") != len(ids):
            raise ReferenceTokenFixtureError(f"{case_id}: token_count mismatch")
        if ids[0] != special_ids["cls"] or ids[-1] != special_ids["sep"]:
            raise ReferenceTokenFixtureError(
                f"{case_id}: sequence must be bounded by CLS/SEP"
            )

        markers = retained.get("marker_positions")
        if (
            not isinstance(markers, list)
            or len(markers) != expected_options
            or any(isinstance(v, bool) or not isinstance(v, int) for v in markers)
        ):
            raise ReferenceTokenFixtureError(f"{case_id}: marker count/type mismatch")
        if markers != sorted(set(markers)):
            raise ReferenceTokenFixtureError(
                f"{case_id}: markers must be unique and strictly increasing"
            )
        for position in markers:
            if not 0 < position < len(ids) - 1:
                raise ReferenceTokenFixtureError(
                    f"{case_id}: marker position outside sequence"
                )
            if ids[position] != special_ids["mask"]:
                raise ReferenceTokenFixtureError(
                    f"{case_id}: marker position does not point to MASK"
                )

        _nonnegative_int(
            retained.get("head_token_count"), f"{case_id}: head_token_count"
        )
        _nonnegative_int(
            retained.get("state_token_count"), f"{case_id}: state_token_count"
        )


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReferenceTokenFixtureError(f"cannot read JSON: {path}") from exc
    if not isinstance(value, dict):
        raise ReferenceTokenFixtureError(f"JSON root must be an object: {path}")
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("fixture", type=Path)
    parser.add_argument("token_fixture", type=Path)
    args = parser.parse_args(argv)
    try:
        fixture = load_json(args.fixture)
        token_fixture = load_json(args.token_fixture)
        validate_reference_token_fixture(fixture, token_fixture)
    except ReferenceTokenFixtureError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(
        json.dumps(
            {
                "valid": True,
                "schema": token_fixture["schema"],
                "cases": len(token_fixture["cases"]),
                "candidate_side_tokenizer_attested": False,
                "numeric_model_parity": False,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
