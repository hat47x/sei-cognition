#!/usr/bin/env python3
"""Atomically materialize the exact Python-Laya reference model directory.

The transport manifest may list multiple acquisition paths, but every path is
bound to the same already-attested runtime-consumed file bytes. Downloaded
content is never published to the destination until every file passes exact
size/SHA-256 checks and the existing model-directory verifier accepts the staged
directory.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
import urllib.request
from contextlib import closing
from pathlib import Path, PurePosixPath
from typing import Any, BinaryIO, Callable, ContextManager

import verify_reference_model_directory as reference_verify

SCHEMA = "sei.local-typed-comparator-reference-model-transport/v1"
STATUS = "transport-candidate"
HF_ID = "huggingface-immutable"
MIRROR_ID = "truespar-paddock-mirror"
HF_BASE = (
    "https://huggingface.co/convaiinnovations/laya-typed-decisions/resolve/"
    "f9ab0b228f0fc0f14d873dbc99038f135c2da1b2"
)
MIRROR_BASE = "https://models.truespar.io/models/laya/typed-decisions"
DEFAULT_ATTEMPTS = 3
MIRROR_PROVENANCE = {
    "repository": "truespar/paddock",
    "revision": "610cd8f5ea72e7421a99ca418d51de804d312730",
    "path": "crates/paddock-manager/models.toml",
    "git_blob": "330a4ce13bd17fda07f6945123b3635bf548c95c",
}


class ReferenceModelTransportError(ValueError):
    pass


class ReferenceModelDownloadError(ReferenceModelTransportError):
    """Retryable transport/read failure before byte-contract validation."""


def _lower_hex(value: Any, length: int, field: str) -> str:
    if not isinstance(value, str) or len(value) != length:
        raise ReferenceModelTransportError(
            f"{field} must be {length}-character lowercase hex"
        )
    if value != value.lower() or any(c not in "0123456789abcdef" for c in value):
        raise ReferenceModelTransportError(
            f"{field} must be {length}-character lowercase hex"
        )
    return value


def _positive_int(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ReferenceModelTransportError(f"{field} must be a positive integer")
    return value


def _safe_relative_path(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise ReferenceModelTransportError(f"{field} must be a non-empty string")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or "." in path.parts:
        raise ReferenceModelTransportError(f"{field} must be a safe relative path")
    return path.as_posix()


def load_manifest(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ReferenceModelTransportError(f"cannot read manifest: {path}") from exc
    if not isinstance(value, dict):
        raise ReferenceModelTransportError("manifest root must be an object")
    return value


def _expected_files() -> dict[str, tuple[int, str]]:
    return {
        spec.relative_path: (spec.bytes, spec.sha256)
        for spec in reference_verify.DEFAULT_FILE_SPECS
    }


def validate_manifest(manifest: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    if manifest.get("schema") != SCHEMA:
        raise ReferenceModelTransportError(f"schema must be {SCHEMA}")
    if manifest.get("status") != STATUS:
        raise ReferenceModelTransportError(f"status must remain {STATUS}")
    _lower_hex(
        manifest.get("observed_from_sei_source_sha"),
        40,
        "observed_from_sei_source_sha",
    )

    contract = manifest.get("reference_contract")
    if not isinstance(contract, dict):
        raise ReferenceModelTransportError("reference_contract must be an object")
    if contract.get("attestation_schema") != reference_verify.SCHEMA:
        raise ReferenceModelTransportError("reference attestation schema drift")
    if contract.get("repository") != reference_verify.SOURCE_REPOSITORY:
        raise ReferenceModelTransportError("reference repository drift")
    if contract.get("revision") != reference_verify.SOURCE_REVISION:
        raise ReferenceModelTransportError("reference revision drift")

    transports = manifest.get("transports")
    if not isinstance(transports, list) or len(transports) != 2:
        raise ReferenceModelTransportError("exactly two transports are required")
    by_id: dict[str, list[dict[str, Any]]] = {}
    expected = _expected_files()
    for index, transport in enumerate(transports):
        if not isinstance(transport, dict):
            raise ReferenceModelTransportError(
                f"transports[{index}] must be an object"
            )
        tid = transport.get("id")
        if tid not in (HF_ID, MIRROR_ID) or tid in by_id:
            raise ReferenceModelTransportError("transport id drift or duplicate")
        if transport.get("requires_post_download_verification") is not True:
            raise ReferenceModelTransportError(
                f"{tid}: verification gate must remain true"
            )
        if tid == HF_ID:
            if transport.get("kind") != "huggingface-resolve":
                raise ReferenceModelTransportError(
                    "Hugging Face transport kind drift"
                )
            if transport.get("content_addressed_url") is not True:
                raise ReferenceModelTransportError(
                    "Hugging Face revision URL must remain pinned"
                )
            provenance = transport.get("provenance")
            if provenance != {
                "repository": reference_verify.SOURCE_REPOSITORY,
                "revision": reference_verify.SOURCE_REVISION,
            }:
                raise ReferenceModelTransportError(
                    "Hugging Face provenance drift"
                )
            base = HF_BASE
        else:
            if transport.get("kind") != "https-mirror":
                raise ReferenceModelTransportError(
                    "mirror transport kind drift"
                )
            if transport.get("content_addressed_url") is not False:
                raise ReferenceModelTransportError(
                    "mirror URL must not be relabelled content-addressed"
                )
            if transport.get("provenance") != MIRROR_PROVENANCE:
                raise ReferenceModelTransportError(
                    "mirror catalog provenance drift"
                )
            base = MIRROR_BASE

        files = transport.get("files")
        if not isinstance(files, list) or len(files) != len(expected):
            raise ReferenceModelTransportError(f"{tid}: file count drift")
        normalized: list[dict[str, Any]] = []
        seen: set[str] = set()
        for file_index, entry in enumerate(files):
            if not isinstance(entry, dict):
                raise ReferenceModelTransportError(
                    f"{tid}.files[{file_index}] must be an object"
                )
            relative = _safe_relative_path(
                entry.get("path"),
                f"{tid}.files[{file_index}].path",
            )
            if relative in seen or relative not in expected:
                raise ReferenceModelTransportError(f"{tid}: file-set drift")
            seen.add(relative)
            expected_bytes, expected_sha = expected[relative]
            if _positive_int(
                entry.get("bytes"), f"{tid}.{relative}.bytes"
            ) != expected_bytes:
                raise ReferenceModelTransportError(
                    f"{tid}.{relative}: byte-size drift"
                )
            if _lower_hex(
                entry.get("sha256"), 64, f"{tid}.{relative}.sha256"
            ) != expected_sha:
                raise ReferenceModelTransportError(
                    f"{tid}.{relative}: SHA-256 drift"
                )
            expected_url = f"{base}/{relative}"
            if entry.get("url") != expected_url:
                raise ReferenceModelTransportError(
                    f"{tid}.{relative}: URL drift"
                )
            normalized.append(
                {
                    "path": relative,
                    "url": expected_url,
                    "bytes": expected_bytes,
                    "sha256": expected_sha,
                }
            )
        if seen != set(expected):
            raise ReferenceModelTransportError(
                f"{tid}: incomplete file set"
            )
        by_id[tid] = normalized

    scope = manifest.get("scope")
    if not isinstance(scope, dict):
        raise ReferenceModelTransportError("scope must be an object")
    if scope.get("reference_contract_matches_all_transports") is not True:
        raise ReferenceModelTransportError(
            "transport/reference contract match must remain true"
        )
    if scope.get("transport_candidate_only") is not True:
        raise ReferenceModelTransportError(
            "transport candidate scope must remain true"
        )
    for field in (
        "current_chat_transport_succeeded",
        "model_bytes_materialized",
        "model_weights_loaded",
        "live_inference",
        "numeric_parity",
        "shipping_decision",
    ):
        if scope.get(field) is not False:
            raise ReferenceModelTransportError(
                f"scope.{field} must remain false"
            )
    return by_id


def _url_stream(url: str, timeout: float) -> ContextManager[BinaryIO]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "sei-cognition-reference-materializer/1"
        },
    )
    return closing(urllib.request.urlopen(request, timeout=timeout))


def _download_once(
    entry: dict[str, Any],
    destination: Path,
    *,
    timeout: float,
    stream_factory: Callable[
        [str, float], ContextManager[BinaryIO]
    ],
) -> dict[str, Any]:
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise ReferenceModelTransportError(
            f"cannot prepare staging directory for {entry['path']}: {exc}"
        ) from exc

    digest = hashlib.sha256()
    size = 0
    try:
        target = destination.open("xb")
    except FileExistsError as exc:
        raise ReferenceModelTransportError(
            f"staged file already exists: {destination}"
        ) from exc
    except OSError as exc:
        raise ReferenceModelTransportError(
            f"cannot create staged file for {entry['path']}: {exc}"
        ) from exc

    try:
        with target:
            try:
                stream = stream_factory(entry["url"], timeout)
            except OSError as exc:
                raise ReferenceModelDownloadError(
                    f"download failed for {entry['path']}: {exc}"
                ) from exc

            try:
                with stream as source:
                    while True:
                        try:
                            block = source.read(8 * 1024 * 1024)
                        except OSError as exc:
                            raise ReferenceModelDownloadError(
                                f"download read failed for {entry['path']}: {exc}"
                            ) from exc
                        if not block:
                            break
                        if not isinstance(block, (bytes, bytearray)):
                            raise ReferenceModelTransportError(
                                "download stream returned non-bytes"
                            )
                        try:
                            target.write(block)
                        except OSError as exc:
                            raise ReferenceModelTransportError(
                                f"staged write failed for {entry['path']}: {exc}"
                            ) from exc
                        digest.update(block)
                        size += len(block)
            except ReferenceModelTransportError:
                raise
            except OSError as exc:
                raise ReferenceModelDownloadError(
                    f"download stream failed for {entry['path']}: {exc}"
                ) from exc
    except ReferenceModelTransportError:
        raise
    except OSError as exc:
        raise ReferenceModelTransportError(
            f"staged file I/O failed for {entry['path']}: {exc}"
        ) from exc

    observed_sha = digest.hexdigest()
    if size != entry["bytes"]:
        raise ReferenceModelTransportError(
            f"{entry['path']}: expected {entry['bytes']} bytes, got {size}"
        )
    if observed_sha != entry["sha256"]:
        raise ReferenceModelTransportError(
            f"{entry['path']}: SHA-256 mismatch"
        )
    return {
        "path": entry["path"],
        "bytes": size,
        "sha256": observed_sha,
    }


def _download_verified(
    entry: dict[str, Any],
    destination: Path,
    *,
    timeout: float,
    attempts: int,
    stream_factory: Callable[
        [str, float], ContextManager[BinaryIO]
    ],
) -> dict[str, Any]:
    if isinstance(attempts, bool) or not isinstance(attempts, int) or attempts < 1:
        raise ReferenceModelTransportError("attempts must be an integer >= 1")

    last_error: ReferenceModelDownloadError | None = None
    for attempt in range(1, attempts + 1):
        try:
            destination.unlink(missing_ok=True)
            result = _download_once(
                entry,
                destination,
                timeout=timeout,
                stream_factory=stream_factory,
            )
            result["download_attempts"] = attempt
            return result
        except ReferenceModelDownloadError as exc:
            last_error = exc
            destination.unlink(missing_ok=True)

    assert last_error is not None
    raise ReferenceModelDownloadError(
        f"{entry['path']}: failed after {attempts} download attempts: {last_error}"
    ) from last_error


def materialize_entries(
    entries: list[dict[str, Any]],
    output_dir: Path,
    *,
    transport_id: str,
    timeout: float = 300.0,
    attempts: int = DEFAULT_ATTEMPTS,
    stream_factory: Callable[
        [str, float], ContextManager[BinaryIO]
    ] = _url_stream,
    directory_verifier: Callable[
        [Path], dict[str, Any]
    ] = reference_verify.verify_model_directory,
) -> dict[str, Any]:
    if timeout <= 0:
        raise ReferenceModelTransportError("timeout must be positive")
    if isinstance(attempts, bool) or not isinstance(attempts, int) or attempts < 1:
        raise ReferenceModelTransportError("attempts must be an integer >= 1")
    output = output_dir.expanduser().resolve()
    if output.exists():
        raise ReferenceModelTransportError(
            f"output already exists: {output}"
        )
    output.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(
        tempfile.mkdtemp(
            prefix=f".{output.name}.staging-",
            dir=output.parent,
        )
    )
    receipts: list[dict[str, Any]] = []
    try:
        for entry in entries:
            relative = _safe_relative_path(
                entry.get("path"), "download path"
            )
            receipts.append(
                _download_verified(
                    entry,
                    staging / relative,
                    timeout=timeout,
                    attempts=attempts,
                    stream_factory=stream_factory,
                )
            )
        directory_receipt = directory_verifier(staging)
        if directory_receipt.get("valid") is not True:
            raise ReferenceModelTransportError(
                "reference directory verifier did not return valid=true"
            )
        os.replace(staging, output)
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise

    return {
        "schema": SCHEMA,
        "status": "materialized-and-verified",
        "transport_id": transport_id,
        "output_dir": str(output),
        "files": receipts,
        "directory_verification": directory_receipt,
        "scope": {
            "model_bytes_materialized": True,
            "model_directory_verified": True,
            "model_weights_loaded": False,
            "live_inference": False,
            "numeric_parity": False,
            "shipping_decision": False,
        },
    }


def materialize_reference_model(
    manifest: dict[str, Any],
    transport_id: str,
    output_dir: Path,
    *,
    timeout: float = 300.0,
    attempts: int = DEFAULT_ATTEMPTS,
) -> dict[str, Any]:
    transports = validate_manifest(manifest)
    try:
        entries = transports[transport_id]
    except KeyError as exc:
        raise ReferenceModelTransportError(
            f"unknown transport: {transport_id}"
        ) from exc
    return materialize_entries(
        entries,
        output_dir,
        transport_id=transport_id,
        timeout=timeout,
        attempts=attempts,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument(
        "--transport",
        choices=(HF_ID, MIRROR_ID),
        required=True,
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--timeout", type=float, default=300.0)
    parser.add_argument("--attempts", type=int, default=DEFAULT_ATTEMPTS)
    args = parser.parse_args(argv)
    try:
        receipt = materialize_reference_model(
            load_manifest(args.manifest),
            args.transport,
            args.output_dir,
            timeout=args.timeout,
            attempts=args.attempts,
        )
    except (
        ReferenceModelTransportError,
        reference_verify.ReferenceModelDirectoryError,
    ) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(receipt, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
