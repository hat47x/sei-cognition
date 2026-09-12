#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import BinaryIO, Callable

from prepare_runtime_version_exchange_archives import (
    Verification,
    download_archive,
    load_manifest as load_runtime_manifest,
    selected_archives,
    validate_output_dir,
    verify_archive,
)
from prepare_runtime_version_exchange_model_store import prepare_model_store
from runtime_path_safety import reject_symlink_path_or_ancestors
from verify_runtime_version_exchange_model_store import verify_model_store


INTEGRATION_DIR = Path(__file__).resolve().parent
SEI_ROOT = INTEGRATION_DIR.parents[1]
RESULT_SCHEMA = "sei.runtime-version-exchange-prepositioned-input-preparation/v1"
STOP_LINE = (
    "prepositioned input preparation PASS != actual Ollama /api/tags observation PASS "
    "!= actual runtime A/B inference PASS != runtime-version-exchange Scoped Executable Evidence"
)


def _is_within(candidate: Path, root: Path) -> bool:
    candidate = candidate.expanduser().resolve(strict=False)
    root = root.expanduser().resolve(strict=True)
    return candidate == root or root in candidate.parents


def validate_preparation_root(root: Path) -> Path:
    requested = root.expanduser()
    reject_symlink_path_or_ancestors(requested, "prepositioned input root")
    resolved = requested.resolve(strict=False)
    if _is_within(resolved, SEI_ROOT):
        raise ValueError(
            "prepositioned input rootをSEI repository配下には配置できません: "
            f"{resolved}"
        )
    if resolved.exists() and not resolved.is_dir():
        raise ValueError(
            "prepositioned input rootはdirectoryまたは新規pathである必要があります: "
            f"{resolved}"
        )
    return resolved


def _prepare_runtime_archives(
    root: Path,
    *,
    verify_only: bool,
    opener: Callable[..., BinaryIO] | None = None,
) -> list[dict[str, object]]:
    manifest = load_runtime_manifest()
    archive_dir = validate_output_dir(root / "runtime-archives")
    results: list[dict[str, object]] = []

    for label, archive in selected_archives(manifest, "all"):
        target = archive_dir / str(archive["localFileName"])
        expected_size = int(archive["sizeBytes"])
        expected_sha256 = str(archive["sha256"])
        existed = target.exists()
        verification: Verification
        if verify_only:
            verification = verify_archive(target, expected_size, expected_sha256)
            acquisition = "verified-existing"
        else:
            verification = download_archive(
                str(archive["downloadUrl"]),
                target,
                expected_size,
                expected_sha256,
                opener=opener,
            )
            acquisition = "verified-existing" if existed else "downloaded"
        results.append(
            {
                "label": label,
                "runtime": archive["runtime"],
                "version": archive["version"],
                "path": str(verification.path),
                "sizeBytes": verification.size_bytes,
                "sha256": verification.sha256,
                "acquisition": acquisition,
            }
        )
    return results


def _prepare_model(
    model_dir: Path,
    *,
    verify_only: bool,
    opener: Callable[..., BinaryIO] | None = None,
) -> tuple[dict[str, object], str]:
    if model_dir.exists():
        return verify_model_store(model_dir), "verified-existing"
    if verify_only:
        raise ValueError(
            "verify-onlyでは固定model storeを事前配置してください: "
            f"{model_dir}"
        )

    if opener is None:
        prepare_model_store(model_dir)
    else:
        prepare_model_store(model_dir, opener=opener)
    return verify_model_store(model_dir), "downloaded"


def prepare_prepositioned_inputs(
    root: Path,
    *,
    verify_only: bool = False,
    runtime_opener: Callable[..., BinaryIO] | None = None,
    model_opener: Callable[..., BinaryIO] | None = None,
) -> dict[str, object]:
    root = validate_preparation_root(root)
    runtime_archives = _prepare_runtime_archives(
        root,
        verify_only=verify_only,
        opener=runtime_opener,
    )
    model_dir = root / "ollama-models"
    model, model_acquisition = _prepare_model(
        model_dir,
        verify_only=verify_only,
        opener=model_opener,
    )

    by_label = {str(item["label"]): item for item in runtime_archives}
    if set(by_label) != {"a", "b"}:
        raise ValueError(
            "runtime archive preparation resultにA/Bの両方がありません: "
            f"labels={sorted(by_label)}"
        )

    return {
        "schema": RESULT_SCHEMA,
        "result": "ok",
        "root": str(root),
        "runtimeArchives": runtime_archives,
        "model": {
            "name": model["model"],
            "modelStore": model["modelStore"],
            "manifestSha256": model["manifestSha256"],
            "referencedBlobCount": model["referencedBlobCount"],
            "referencedBytesTotal": model["referencedBytesTotal"],
            "acquisition": model_acquisition,
        },
        "verifiedRunnerInputs": {
            "modelDir": str(model_dir.resolve(strict=True)),
            "runtimeAArchive": by_label["a"]["path"],
            "runtimeBArchive": by_label["b"]["path"],
            "requirePrepositionedArtifacts": True,
        },
        "qualityJudgement": "not_evaluated",
        "stopLine": STOP_LINE,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "ISSUE-000070のactual runtime A/B実行に必要な固定runtime archiveと"
            "固定Ollama model storeを一つのrootへ事前配置または再検証します。"
            "実行source、Evidence、workは作らず、actual runtime processも起動しません。"
        ),
        allow_abbrev=False,
    )
    parser.add_argument(
        "--root",
        required=True,
        type=Path,
        help=(
            "SEI repository外のartifact root。runtime-archives/とollama-models/を利用します。"
            "既存rootは固定artifactの再利用に使えます。"
        ),
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="network取得を行わず、既に事前配置済みのruntime A/B archiveとmodel storeだけを検証します。",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        payload = prepare_prepositioned_inputs(
            args.root,
            verify_only=args.verify_only,
        )
    except (OSError, ValueError) as exc:
        build_parser().exit(
            1,
            f"runtime exchange prepositioned input preparation failed: {exc}\n",
        )

    print(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
