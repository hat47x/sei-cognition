#!/usr/bin/env python3
"""Validate retained exact-sequence Evidence for the choice:11+ diagnostic."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

SCHEMA = "sei.local-typed-comparator-choice11-sequence-attestation/v1"
FIXTURE_SCHEMA = "sei.local-typed-comparator-fixture/v1alpha1"
FIXTURE_BLOB = "f622f7144ab827600e7c7c10d8ea632582fa7ad9"
CASE_ID = "choice-12-clamp-path"
QUESTION_ID = "choice12"
REQUEST_SHA256 = "cbec246b276315886ebf04ba00a6498bb3e9905b4bd8d209c40b5b0abb8a2568"
TOKENIZER_BLOB = "2f4d8583e507b7466d2490e2d6c045647a822698"
TOKENIZER_BYTES = 3_583_228
TOKENIZER_SHA256 = "6c8aaa9a542084f2457eab775d4eeb51f92a70c0fd9de28d5edb0ddec3c08d30"
TOKENIZER_IMPL_BLOB = "58cabadbab133e162d4e4e7e792ec63932ab86c7"
FUZZ_BLOB = "be6c2982f2d088c5d249cd69d65e4695dc126040"
REFERENCE_REVISION = "23a17522aa4942da6cce53a995a275760320b691"
REFERENCE_COMMON_BLOB = "6c4c426e64eb9660c97d40bc64c227e8c7e71361"
PAPAYA_REVISION = "a76bc99bddafdac32863b2edc5319773e0cd3532"
PAPAYA_QUESTIONS_BLOB = "7b1fe73f23b225a04f4b2ac53fd0011a4fdf90bf"
PAPAYA_SEQUENCES_BLOB = "f21139970d6d288114213db8f917f0cead9c082f"
TOKEN_COUNT = 155
MARKERS = [16, 25, 34, 43, 52, 61, 70, 79, 88, 97, 106, 115]
CLS_ID = 50281
SEP_ID = 50282
MASK_ID = 50284


class Choice11SequenceError(ValueError):
    pass


def _object(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise Choice11SequenceError(f"{field} must be an object")
    return value


def git_blob_oid(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def canonical_request_sha256(request: dict[str, Any]) -> str:
    raw = json.dumps(
        request, ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def validate_choice11_sequence(
    fixture: dict[str, Any],
    packet: dict[str, Any],
    *,
    fixture_raw: bytes | None = None,
) -> None:
    if packet.get("schema") != SCHEMA:
        raise Choice11SequenceError(f"schema must be {SCHEMA}")
    if fixture.get("schema") != FIXTURE_SCHEMA:
        raise Choice11SequenceError("diagnostic fixture schema drift")
    if fixture_raw is not None and git_blob_oid(fixture_raw) != FIXTURE_BLOB:
        raise Choice11SequenceError("diagnostic fixture Git blob drift")

    cases = fixture.get("cases")
    if not isinstance(cases, list) or len(cases) != 1:
        raise Choice11SequenceError("diagnostic fixture must contain one case")
    source_case = _object(cases[0], "fixture.case")
    if source_case.get("case_id") != CASE_ID:
        raise Choice11SequenceError("diagnostic case id drift")
    request = _object(source_case.get("request"), "fixture.request")
    if canonical_request_sha256(request) != REQUEST_SHA256:
        raise Choice11SequenceError("diagnostic request SHA-256 drift")
    questions = _object(request.get("questions"), "fixture.questions")
    if list(questions) != [QUESTION_ID]:
        raise Choice11SequenceError("diagnostic question identity/order drift")
    question = _object(questions[QUESTION_ID], "fixture.question")
    criteria = _object(question.get("criteria"), "fixture.question.criteria")
    if question.get("type") != "choice" or len(criteria) != 12:
        raise Choice11SequenceError("diagnostic must remain a 12-option Choice")
    expected_keys = [f"option_{i:02d}" for i in range(12)]
    if list(criteria) != expected_keys:
        raise Choice11SequenceError("diagnostic Choice option order drift")

    meta = _object(packet.get("diagnostic_fixture"), "diagnostic_fixture")
    expected_meta = {
        "git_blob": FIXTURE_BLOB,
        "schema": FIXTURE_SCHEMA,
        "case_id": CASE_ID,
        "question_id": QUESTION_ID,
        "request_sha256": REQUEST_SHA256,
    }
    for field, expected in expected_meta.items():
        if meta.get(field) != expected:
            raise Choice11SequenceError(f"diagnostic_fixture.{field} drift")

    tokenizer = _object(packet.get("tokenizer"), "tokenizer")
    expected_tokenizer = {
        "git_blob": TOKENIZER_BLOB,
        "bytes": TOKENIZER_BYTES,
        "sha256": TOKENIZER_SHA256,
        "implementation_git_blob": TOKENIZER_IMPL_BLOB,
        "fuzz_fixture_git_blob": FUZZ_BLOB,
        "fuzz_cases": 206,
        "fuzz_pass": 206,
    }
    for field, expected in expected_tokenizer.items():
        if tokenizer.get(field) != expected:
            raise Choice11SequenceError(f"tokenizer.{field} drift")

    builders = _object(packet.get("sequence_builders"), "sequence_builders")
    reference = _object(builders.get("reference"), "sequence_builders.reference")
    papaya = _object(builders.get("papaya"), "sequence_builders.papaya")
    if reference.get("revision") != REFERENCE_REVISION:
        raise Choice11SequenceError("reference sequence revision drift")
    if reference.get("common_git_blob") != REFERENCE_COMMON_BLOB:
        raise Choice11SequenceError("reference sequence-builder blob drift")
    if papaya.get("revision") != PAPAYA_REVISION:
        raise Choice11SequenceError("Papaya sequence revision drift")
    if papaya.get("questions_git_blob") != PAPAYA_QUESTIONS_BLOB:
        raise Choice11SequenceError("Papaya questions blob drift")
    if papaya.get("sequences_git_blob") != PAPAYA_SEQUENCES_BLOB:
        raise Choice11SequenceError("Papaya sequence-builder blob drift")
    for side, value in (("reference", reference), ("papaya", papaya)):
        if value.get("max_len") != 1024 or value.get("head_max_len") != 256:
            raise Choice11SequenceError(f"{side} sequence budget drift")

    replay = _object(packet.get("replay_validation"), "replay_validation")
    for field in (
        "frozen_four_case_sanity_cases",
        "frozen_four_case_full_input_ids_exact",
        "frozen_four_case_marker_positions_exact",
        "frozen_four_case_token_counts_exact",
    ):
        if replay.get(field) != 4:
            raise Choice11SequenceError(f"replay_validation.{field} drift")
    for field in (
        "upstream_python_executed",
        "transformers_auto_tokenizer_executed",
        "model_weights_loaded",
    ):
        if replay.get(field) is not False:
            raise Choice11SequenceError(f"replay_validation.{field} must remain false")

    special = _object(packet.get("special_token_ids"), "special_token_ids")
    if special != {"cls": CLS_ID, "sep": SEP_ID, "mask": MASK_ID}:
        raise Choice11SequenceError("special-token identity drift")

    retained = _object(packet.get("case"), "case")
    if retained.get("case_id") != CASE_ID or retained.get("question_id") != QUESTION_ID:
        raise Choice11SequenceError("retained diagnostic identity drift")
    if retained.get("question_type") != "choice" or retained.get("option_count") != 12:
        raise Choice11SequenceError("retained diagnostic question shape drift")
    if retained.get("temperature_bucket") != "choice:11+":
        raise Choice11SequenceError("retained temperature bucket drift")
    ids = retained.get("input_ids")
    markers = retained.get("marker_positions")
    if (
        not isinstance(ids, list)
        or len(ids) != TOKEN_COUNT
        or any(isinstance(v, bool) or not isinstance(v, int) or v < 0 for v in ids)
    ):
        raise Choice11SequenceError("retained input_ids/token_count drift")
    if retained.get("token_count") != TOKEN_COUNT:
        raise Choice11SequenceError("retained token_count drift")
    if markers != MARKERS:
        raise Choice11SequenceError("retained marker positions drift")
    if ids[0] != CLS_ID or ids[-1] != SEP_ID:
        raise Choice11SequenceError("retained sequence boundary drift")
    if any(ids[position] != MASK_ID for position in MARKERS):
        raise Choice11SequenceError("retained marker does not point to MASK")
    if retained.get("head_token_count") != 14:
        raise Choice11SequenceError("retained head-token count drift")
    if retained.get("state_token_count") != 29:
        raise Choice11SequenceError("retained state-token count drift")
    if retained.get("truncation_exercised") is not False:
        raise Choice11SequenceError("diagnostic truncation scope drift")

    scope = _object(packet.get("scope"), "scope")
    if scope.get("reference_papaya_source_equivalent_sequence_parity") is not True:
        raise Choice11SequenceError("source-equivalent sequence parity must be true")
    for field in (
        "live_runtime_input_ids_observed",
        "live_runtime_marker_positions_observed",
        "live_inference",
        "numeric_model_parity",
        "calibration_validity",
        "task_quality",
        "reference_provider_promotion",
    ):
        if scope.get(field) is not False:
            raise Choice11SequenceError(f"scope.{field} must remain false")


def load_object(path: Path) -> tuple[dict[str, Any], bytes]:
    try:
        raw = path.read_bytes()
        value = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise Choice11SequenceError(f"cannot read JSON: {path}") from exc
    if not isinstance(value, dict):
        raise Choice11SequenceError(f"JSON root must be an object: {path}")
    return value, raw


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("fixture", type=Path)
    parser.add_argument("attestation", type=Path)
    args = parser.parse_args(argv)
    try:
        fixture, fixture_raw = load_object(args.fixture)
        packet, _ = load_object(args.attestation)
        validate_choice11_sequence(fixture, packet, fixture_raw=fixture_raw)
    except Choice11SequenceError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(
        json.dumps(
            {
                "valid": True,
                "schema": packet["schema"],
                "case_id": CASE_ID,
                "token_count": TOKEN_COUNT,
                "marker_positions": MARKERS,
                "numeric_model_parity": False,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
