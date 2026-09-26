#!/usr/bin/env python3
"""Validate retained Papaya source-equivalent sequence replay Evidence.

The replay compares the pinned Papaya question/sequence construction against
SEI's frozen four-case reference token fixture using a tokenizer whose byte
identity is separately attested. It does not execute upstream Papaya Python,
Transformers AutoTokenizer, model weights, or live inference.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

SCHEMA = "sei.local-typed-comparator-papaya-sequence-replay/v1"
SOURCE_GIT_SHA = "e996b8c6072996091b0c59de2ba84010e4de91b2"
FIXTURE_BLOB = "2bed0f232ea845e2bda43ffd113d5cd86a9f770e"
REFERENCE_TOKEN_FIXTURE_BLOB = "75dff1a1bd19fbaa895c569f0a8dbca67734af49"
CANDIDATE_ATTESTATION_BLOB = "d66f432e73ff55c0ccbf7c375d6b2ad19c34d75e"
CANDIDATE_TOKENIZER_REVISION = "75300646cddbac2b47409fc1ca839c95bec004c8"
TOKENIZER_BLOB = "2f4d8583e507b7466d2490e2d6c045647a822698"
TOKENIZER_SHA256 = "6c8aaa9a542084f2457eab775d4eeb51f92a70c0fd9de28d5edb0ddec3c08d30"
TOKENIZER_BYTES = 3_583_228
PAPAYA_REPOSITORY = "m0rphtail/papaya"
PAPAYA_REVISION = "a76bc99bddafdac32863b2edc5319773e0cd3532"
PAPAYA_QUESTIONS_BLOB = "7b1fe73f23b225a04f4b2ac53fd0011a4fdf90bf"
PAPAYA_SEQUENCES_BLOB = "f21139970d6d288114213db8f917f0cead9c082f"
PAPAYA_RUNTIME_BLOB = "b3999b7f1e02d4761ffba63b7f846b210f3e27dd"
CANDIDATE_CONFIG_SHA256 = "ebf0cd524d92342a6be5e48e9fca3d7c2babfb5a56ccd79d2171ef5d8c7f7be8"
TOKENIZER_IMPL_BLOB = "58cabadbab133e162d4e4e7e792ec63932ab86c7"
TOKENIZER_FUZZ_BLOB = "be6c2982f2d088c5d249cd69d65e4695dc126040"


class PapayaSequenceReplayError(ValueError):
    pass


def _object(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise PapayaSequenceReplayError(f"{field} must be an object")
    return value


def _load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PapayaSequenceReplayError(f"cannot read JSON: {path}") from exc
    if not isinstance(value, dict):
        raise PapayaSequenceReplayError(f"JSON root must be an object: {path}")
    return value


def _request_sha256(request: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            request, ensure_ascii=False, separators=(",", ":")
        ).encode("utf-8")
    ).hexdigest()


def validate_papaya_sequence_replay(
    fixture: dict[str, Any],
    reference: dict[str, Any],
    attestation: dict[str, Any],
    replay: dict[str, Any],
) -> None:
    if replay.get("schema") != SCHEMA:
        raise PapayaSequenceReplayError(f"schema must be {SCHEMA}")
    if replay.get("source_git_sha") != SOURCE_GIT_SHA:
        raise PapayaSequenceReplayError("source_git_sha drift")

    fixture_meta = _object(replay.get("fixture"), "fixture")
    if fixture_meta.get("git_blob") != FIXTURE_BLOB:
        raise PapayaSequenceReplayError("fixture Git blob drift")
    if fixture_meta.get("schema") != fixture.get("schema"):
        raise PapayaSequenceReplayError("fixture schema drift")

    reference_meta = _object(
        replay.get("reference_token_fixture"), "reference_token_fixture"
    )
    if reference_meta.get("git_blob") != REFERENCE_TOKEN_FIXTURE_BLOB:
        raise PapayaSequenceReplayError("reference token fixture Git blob drift")
    if reference_meta.get("schema") != reference.get("schema"):
        raise PapayaSequenceReplayError("reference token fixture schema drift")

    candidate_meta = _object(
        replay.get("candidate_tokenizer_attestation"),
        "candidate_tokenizer_attestation",
    )
    if candidate_meta.get("git_blob") != CANDIDATE_ATTESTATION_BLOB:
        raise PapayaSequenceReplayError("candidate attestation Git blob drift")
    if candidate_meta.get("schema") != attestation.get("schema"):
        raise PapayaSequenceReplayError("candidate attestation schema drift")
    att_scope = _object(attestation.get("scope"), "attestation.scope")
    att_candidate = _object(attestation.get("candidate"), "attestation.candidate")
    if att_scope.get("candidate_side_tokenizer_attested") is not True:
        raise PapayaSequenceReplayError("candidate tokenizer is not byte-attested")
    if att_candidate.get("git_blob") != TOKENIZER_BLOB:
        raise PapayaSequenceReplayError("attested candidate tokenizer blob drift")
    if att_candidate.get("sha256") != TOKENIZER_SHA256:
        raise PapayaSequenceReplayError("attested candidate tokenizer SHA-256 drift")
    if candidate_meta.get("candidate_revision") != CANDIDATE_TOKENIZER_REVISION:
        raise PapayaSequenceReplayError("candidate tokenizer revision drift")
    if candidate_meta.get("tokenizer_bytes") != TOKENIZER_BYTES:
        raise PapayaSequenceReplayError("candidate tokenizer byte-size drift")
    if candidate_meta.get("tokenizer_bytes") != att_candidate.get("bytes"):
        raise PapayaSequenceReplayError("replay/attestation tokenizer byte-size mismatch")
    if candidate_meta.get("tokenizer_git_blob") != att_candidate.get("git_blob"):
        raise PapayaSequenceReplayError("replay/attestation tokenizer blob mismatch")
    if candidate_meta.get("tokenizer_sha256") != att_candidate.get("sha256"):
        raise PapayaSequenceReplayError("replay/attestation tokenizer SHA mismatch")

    papaya = _object(replay.get("papaya_source"), "papaya_source")
    expected_papaya = {
        "repository": PAPAYA_REPOSITORY,
        "revision": PAPAYA_REVISION,
        "questions_git_blob": PAPAYA_QUESTIONS_BLOB,
        "sequences_git_blob": PAPAYA_SEQUENCES_BLOB,
        "runtime_git_blob": PAPAYA_RUNTIME_BLOB,
    }
    for field, expected in expected_papaya.items():
        if papaya.get(field) != expected:
            raise PapayaSequenceReplayError(f"papaya_source.{field} drift")

    config = _object(replay.get("candidate_config"), "candidate_config")
    if config.get("bytes") != 847:
        raise PapayaSequenceReplayError("candidate config byte-size drift")
    if config.get("sha256") != CANDIDATE_CONFIG_SHA256:
        raise PapayaSequenceReplayError("candidate config SHA-256 drift")
    if config.get("max_len") != 1024 or config.get("head_max_len") != 256:
        raise PapayaSequenceReplayError("candidate sequence budget drift")

    basis = _object(replay.get("replay_basis"), "replay_basis")
    expected_basis = {
        "method": "source-equivalent deterministic replay",
        "tokenizer_byte_identity_attested": True,
        "tokenizer_git_blob": TOKENIZER_BLOB,
        "tokenizer_implementation_git_blob": TOKENIZER_IMPL_BLOB,
        "tokenizer_fuzz_fixture_git_blob": TOKENIZER_FUZZ_BLOB,
        "tokenizer_fuzz_cases": 206,
        "tokenizer_fuzz_pass": 206,
        "upstream_python_executed": False,
        "transformers_auto_tokenizer_executed": False,
        "model_weights_loaded": False,
    }
    for field, expected in expected_basis.items():
        if basis.get(field) != expected:
            raise PapayaSequenceReplayError(f"replay_basis.{field} drift")

    scope = _object(replay.get("scope"), "scope")
    if scope.get("candidate_token_id_marker_parity") is not True:
        raise PapayaSequenceReplayError("candidate token/marker parity must be true")
    if scope.get("parity_scope") != "frozen SEI four-case source-equivalent sequence replay":
        raise PapayaSequenceReplayError("candidate token/marker parity scope drift")
    for field in (
        "numeric_model_parity",
        "temperature_semantics_parity",
        "live_l0_inference",
        "provider_identity_equivalence",
        "reference_provider_promotion",
    ):
        if scope.get(field) is not False:
            raise PapayaSequenceReplayError(f"scope.{field} must remain false")

    fixture_cases = fixture.get("cases")
    reference_cases = reference.get("cases")
    replay_cases = replay.get("cases")
    if not isinstance(fixture_cases, list) or not isinstance(reference_cases, list):
        raise PapayaSequenceReplayError("source cases must be arrays")
    if not isinstance(replay_cases, list):
        raise PapayaSequenceReplayError("replay cases must be an array")

    fixture_by_id = {
        c.get("case_id"): c for c in fixture_cases if isinstance(c, dict)
    }
    reference_by_id = {
        c.get("case_id"): c for c in reference_cases if isinstance(c, dict)
    }
    replay_by_id = {
        c.get("case_id"): c for c in replay_cases if isinstance(c, dict)
    }
    if (
        set(fixture_by_id)
        != set(reference_by_id)
        or set(fixture_by_id) != set(replay_by_id)
        or len(replay_cases) != len(fixture_by_id)
    ):
        raise PapayaSequenceReplayError("case identity drift")

    for case_id, source_case in fixture_by_id.items():
        request = _object(source_case.get("request"), f"{case_id}.request")
        questions = _object(request.get("questions"), f"{case_id}.questions")
        if len(questions) != 1:
            raise PapayaSequenceReplayError(
                f"{case_id}: replay requires exactly one question"
            )
        question_id = next(iter(questions))
        request_sha = _request_sha256(request)

        ref_case = reference_by_id[case_id]
        got = replay_by_id[case_id]
        if got.get("question_id") != question_id:
            raise PapayaSequenceReplayError(f"{case_id}: question id drift")
        if got.get("request_sha256") != request_sha:
            raise PapayaSequenceReplayError(f"{case_id}: request SHA-256 drift")
        if ref_case.get("request_sha256") != request_sha:
            raise PapayaSequenceReplayError(f"{case_id}: reference request drift")

        input_ids = got.get("input_ids")
        markers = got.get("marker_positions")
        if input_ids != ref_case.get("input_ids"):
            raise PapayaSequenceReplayError(f"{case_id}: input IDs differ from reference")
        if markers != ref_case.get("marker_positions"):
            raise PapayaSequenceReplayError(
                f"{case_id}: marker positions differ from reference"
            )
        if got.get("token_count") != len(input_ids):
            raise PapayaSequenceReplayError(f"{case_id}: token_count mismatch")
        if got.get("token_count") != ref_case.get("token_count"):
            raise PapayaSequenceReplayError(
                f"{case_id}: token count differs from reference"
            )
        if got.get("reference_input_ids_equal") is not True:
            raise PapayaSequenceReplayError(f"{case_id}: ID parity flag drift")
        if got.get("reference_marker_positions_equal") is not True:
            raise PapayaSequenceReplayError(f"{case_id}: marker parity flag drift")
        if got.get("truncation_exercised") is not False:
            raise PapayaSequenceReplayError(
                f"{case_id}: frozen replay must remain outside truncation paths"
            )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("fixture", type=Path)
    parser.add_argument("reference", type=Path)
    parser.add_argument("attestation", type=Path)
    parser.add_argument("replay", type=Path)
    args = parser.parse_args(argv)
    try:
        fixture = _load(args.fixture)
        reference = _load(args.reference)
        attestation = _load(args.attestation)
        replay = _load(args.replay)
        validate_papaya_sequence_replay(
            fixture, reference, attestation, replay
        )
    except PapayaSequenceReplayError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(
        json.dumps(
            {
                "valid": True,
                "schema": replay["schema"],
                "cases": len(replay["cases"]),
                "candidate_token_id_marker_parity": True,
                "numeric_model_parity": False,
                "temperature_semantics_parity": False,
                "live_l0_inference": False,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
