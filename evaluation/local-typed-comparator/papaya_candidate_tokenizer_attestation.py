#!/usr/bin/env python3
"""Validate the retained Papaya candidate-tokenizer byte attestation.

This packet proves candidate tokenizer byte identity through an immutable
Hugging Face Git-blob ETag that exactly matches the independently hashed
reference Git blob. It does not prove Papaya sequence-builder replay, model
numeric parity, or live inference.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

SCHEMA = "sei.local-typed-comparator-papaya-tokenizer-attestation/v1"
CANDIDATE_REPOSITORY = "fr0stbit3/laya-typed-decisions-gguf"
CANDIDATE_REVISION = "75300646cddbac2b47409fc1ca839c95bec004c8"
CANDIDATE_PATH = "tokenizer.json"
REFERENCE_REPOSITORY = "MatteoGauthier/laya-portable"
REFERENCE_REVISION = "3dc028023929432b4a3d76b1a8ee050d0e5ccd7f"
REFERENCE_PATH = "packages/laya-js/src/tokenizer/tokenizer.json"
TOKENIZER_BYTES = 3_583_228
TOKENIZER_GIT_BLOB = "2f4d8583e507b7466d2490e2d6c045647a822698"
TOKENIZER_SHA256 = "6c8aaa9a542084f2457eab775d4eeb51f92a70c0fd9de28d5edb0ddec3c08d30"
SHA256_BASIS = "byte identity via immutable Git blob equality to independently hashed reference"
IMMUTABLE_FILE_URL = "https://huggingface.co/fr0stbit3/laya-typed-decisions-gguf/blob/75300646cddbac2b47409fc1ca839c95bec004c8/tokenizer.json"
RESOLVE_CACHE_URL = "https://huggingface.co/api/resolve-cache/models/fr0stbit3/laya-typed-decisions-gguf/75300646cddbac2b47409fc1ca839c95bec004c8/tokenizer.json?download=true&etag=%222f4d8583e507b7466d2490e2d6c045647a822698%22"
ETAG_SEMANTICS_SOURCE = "https://huggingface.co/docs/huggingface_hub/package_reference/file_download"


class CandidateTokenizerAttestationError(ValueError):
    pass


def _object(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise CandidateTokenizerAttestationError(f"{field} must be an object")
    return value


def validate_candidate_tokenizer_attestation(packet: dict[str, Any]) -> None:
    if packet.get("schema") != SCHEMA:
        raise CandidateTokenizerAttestationError(f"schema must be {SCHEMA}")

    candidate = _object(packet.get("candidate"), "candidate")
    reference = _object(packet.get("reference"), "reference")
    proof = _object(packet.get("proof"), "proof")
    scope = _object(packet.get("scope"), "scope")

    expected_candidate = {
        "repository": CANDIDATE_REPOSITORY,
        "revision": CANDIDATE_REVISION,
        "path": CANDIDATE_PATH,
        "bytes": TOKENIZER_BYTES,
        "huggingface_resolve_etag": TOKENIZER_GIT_BLOB,
        "git_blob": TOKENIZER_GIT_BLOB,
        "sha256": TOKENIZER_SHA256,
        "sha256_basis": SHA256_BASIS,
        "immutable_file_url": IMMUTABLE_FILE_URL,
        "resolve_cache_etag_observed_url": RESOLVE_CACHE_URL,
        "etag_semantics_source": ETAG_SEMANTICS_SOURCE,
    }
    for field, expected in expected_candidate.items():
        if candidate.get(field) != expected:
            raise CandidateTokenizerAttestationError(f"candidate.{field} drift")

    expected_reference = {
        "repository": REFERENCE_REPOSITORY,
        "revision": REFERENCE_REVISION,
        "path": REFERENCE_PATH,
        "bytes": TOKENIZER_BYTES,
        "git_blob": TOKENIZER_GIT_BLOB,
        "sha256": TOKENIZER_SHA256,
    }
    for field, expected in expected_reference.items():
        if reference.get(field) != expected:
            raise CandidateTokenizerAttestationError(f"reference.{field} drift")

    if candidate["huggingface_resolve_etag"] != candidate["git_blob"]:
        raise CandidateTokenizerAttestationError("candidate ETag / Git blob mismatch")
    if candidate["git_blob"] != reference["git_blob"]:
        raise CandidateTokenizerAttestationError("candidate/reference Git blob mismatch")
    if candidate["bytes"] != reference["bytes"]:
        raise CandidateTokenizerAttestationError("candidate/reference byte-size mismatch")
    if candidate["sha256"] != reference["sha256"]:
        raise CandidateTokenizerAttestationError("candidate/reference SHA-256 mismatch")

    expected_proof = {
        "candidate_git_blob_equals_reference_git_blob": True,
        "candidate_bytes_equal_reference_bytes": True,
        "candidate_sha256_equals_reference_sha256": True,
        "candidate_sha256_independently_recomputed": False,
    }
    for field, expected in expected_proof.items():
        if proof.get(field) is not expected:
            raise CandidateTokenizerAttestationError(f"proof.{field} drift")

    if scope.get("candidate_side_tokenizer_attested") is not True:
        raise CandidateTokenizerAttestationError(
            "candidate_side_tokenizer_attested must be true for this packet"
        )
    for field in (
        "candidate_token_id_marker_parity",
        "numeric_model_parity",
        "live_l0_inference",
    ):
        if scope.get(field) is not False:
            raise CandidateTokenizerAttestationError(
                f"scope.{field} must remain false in tokenizer-only attestation"
            )


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CandidateTokenizerAttestationError(f"cannot read JSON: {path}") from exc
    if not isinstance(value, dict):
        raise CandidateTokenizerAttestationError(f"JSON root must be an object: {path}")
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("packet", type=Path)
    args = parser.parse_args(argv)
    try:
        packet = load_json(args.packet)
        validate_candidate_tokenizer_attestation(packet)
    except CandidateTokenizerAttestationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(
        json.dumps(
            {
                "valid": True,
                "schema": packet["schema"],
                "candidate_side_tokenizer_attested": True,
                "candidate_token_id_marker_parity": False,
                "numeric_model_parity": False,
                "live_l0_inference": False,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
