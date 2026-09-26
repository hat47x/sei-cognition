#!/usr/bin/env python3
"""Validate retained reference-side token Evidence for the local typed comparator.

This validator proves structural integrity and fixture binding of the retained
input-token/marker packet. It does not recreate the tokenizer, attest a
candidate runtime, load a model, or claim numeric parity.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

SCHEMA = "sei.local-typed-comparator-reference-token-fixture/v1"
EXPECTED_SOURCE_GIT_SHA = "eb92c515bc1aa741e5de58c364e9a3628cf6dac3"
EXPECTED_FIXTURE_BLOB = "2bed0f232ea845e2bda43ffd113d5cd86a9f770e"
EXPECTED_REFERENCE_RUNTIME_SHA = "23a17522aa4942da6cce53a995a275760320b691"
EXPECTED_SEQUENCE_BUILDER_BLOB = "6c4c426e64eb9660c97d40bc64c227e8c7e71361"
EXPECTED_TOKENIZER_BLOB = "2f4d8583e507b7466d2490e2d6c045647a822698"
EXPECTED_TOKENIZER_BYTES = 3_583_228
EXPECTED_TOKENIZER_SHA256 = (
    "6c8aaa9a542084f2457eab775d4eeb51f92a70c0fd9de28d5edb0ddec3c08d30"
)
EXPECTED_TOKENIZER_IMPL_BLOB = "58cabadbab133e162d4e4e7e792ec63932ab86c7"
EXPECTED_FUZZ_FIXTURE_BLOB = "be6c2982f2d088c5d249cd69d65e4695dc126040"
EXPECTED_FUZZ_CASES = 206


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
    if token_fixture.get("source_git_sha") != EXPECTED_SOURCE_GIT_SHA:
        raise ReferenceTokenFixtureError("source_git_sha drift")

    fixture_meta = token_fixture.get("fixture")
    if not isinstance(fixture_meta, dict):
        raise ReferenceTokenFixtureError("fixture metadata must be an object")
    if fixture_meta.get("schema") != fixture.get("schema"):
        raise ReferenceTokenFixtureError("fixture schema binding does not match")
    if fixture_meta.get("git_blob") != EXPECTED_FIXTURE_BLOB:
        raise ReferenceTokenFixtureError("fixture Git blob drift")

    runtime = token_fixture.get("reference_runtime")
    if not isinstance(runtime, dict):
        raise ReferenceTokenFixtureError("reference_runtime must be an object")
    if runtime.get("git_sha") != EXPECTED_REFERENCE_RUNTIME_SHA:
        raise ReferenceTokenFixtureError("reference runtime SHA drift")
    if runtime.get("sequence_builder_git_blob") != EXPECTED_SEQUENCE_BUILDER_BLOB:
        raise ReferenceTokenFixtureError("sequence builder Git blob drift")

    tokenizer = token_fixture.get("tokenizer")
    if not isinstance(tokenizer, dict):
        raise ReferenceTokenFixtureError("tokenizer metadata must be an object")
    tokenizer_bytes = _positive_int(tokenizer.get("bytes"), "tokenizer.bytes")
    if tokenizer_bytes != EXPECTED_TOKENIZER_BYTES:
        raise ReferenceTokenFixtureError("tokenizer byte-size drift")
    if tokenizer.get("git_blob") != EXPECTED_TOKENIZER_BLOB:
        raise ReferenceTokenFixtureError("tokenizer Git blob drift")
    sha256 = tokenizer.get("sha256")
    if (
        not isinstance(sha256, str)
        or len(sha256) != 64
        or any(c not in "0123456789abcdef" for c in sha256)
    ):
        raise ReferenceTokenFixtureError("tokenizer.sha256 must be lowercase hex SHA-256")
    if sha256 != EXPECTED_TOKENIZER_SHA256:
        raise ReferenceTokenFixtureError("tokenizer SHA-256 drift")

    implementation = token_fixture.get("tokenizer_implementation")
    if not isinstance(implementation, dict):
        raise ReferenceTokenFixtureError("tokenizer_implementation must be an object")
    if implementation.get("git_blob") != EXPECTED_TOKENIZER_IMPL_BLOB:
        raise ReferenceTokenFixtureError("tokenizer implementation Git blob drift")
    if implementation.get("fuzz_fixture_git_blob") != EXPECTED_FUZZ_FIXTURE_BLOB:
        raise ReferenceTokenFixtureError("tokenizer fuzz fixture Git blob drift")
    fuzz_cases = _positive_int(
        implementation.get("fuzz_cases"), "tokenizer_implementation.fuzz_cases"
    )
    fuzz_pass = _positive_int(
        implementation.get("fuzz_pass"), "tokenizer_implementation.fuzz_pass"
    )
    if fuzz_cases != EXPECTED_FUZZ_CASES:
        raise ReferenceTokenFixtureError("tokenizer fuzz case-count drift")
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
        request_bytes = json.dumps(
            request, ensure_ascii=False, separators=(",", ":")
        ).encode("utf-8")
        request_sha256 = retained.get("request_sha256")
        if (
            not isinstance(request_sha256, str)
            or request_sha256 != hashlib.sha256(request_bytes).hexdigest()
        ):
            raise ReferenceTokenFixtureError(f"{case_id}: request SHA-256 drift")

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
