#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Iterable

import prepare_tei_revision_b_source as prepare
import prepare_tei_revision_b_source_from_snapshot as snapshot
from runtime_path_safety import reject_symlink_path_or_ancestors


ASSEMBLY_REPORT_SCHEMA = "sei.github-git-data-snapshot-assembly-report/v1"


def _prepare_output_path(path: Path, fragment_paths: Iterable[Path]) -> Path:
    requested = path.expanduser()
    reject_symlink_path_or_ancestors(requested, "TEI Git Data assembled snapshot出力")
    output = requested.resolve(strict=False)
    if output.exists():
        raise ValueError(
            f"TEI Git Data assembled snapshot出力は新規pathを指定してください: {output}"
        )
    if output == prepare.SEI_ROOT or prepare.SEI_ROOT in output.parents:
        raise ValueError(
            f"TEI Git Data assembled snapshotをSEI repository配下には置けません: {output}"
        )
    for fragment_path in fragment_paths:
        fragment = fragment_path.expanduser().resolve(strict=False)
        if prepare._paths_overlap(output, fragment):
            raise ValueError(
                "TEI Git Data fragmentとassembled snapshot出力を分離してください: "
                f"fragment={fragment} output={output}"
            )
    return output


def _write_json_atomically(path: Path, value: dict[str, object]) -> tuple[str, int]:
    rendered = (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    reject_symlink_path_or_ancestors(path, "TEI Git Data assembled snapshot出力")
    if path.exists():
        raise ValueError(
            f"TEI Git Data assembled snapshot出力がassembly中に作成されました: {path}"
        )

    temporary_name = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            prefix=f".{path.name}.tmp-",
            dir=path.parent,
            delete=False,
        ) as temporary:
            temporary.write(rendered)
            temporary.flush()
            os.fsync(temporary.fileno())
            temporary_name = temporary.name
        temporary_path = Path(temporary_name)
        reject_symlink_path_or_ancestors(path, "TEI Git Data assembled snapshot出力")
        if path.exists():
            raise ValueError(
                f"TEI Git Data assembled snapshot出力がassembly中に作成されました: {path}"
            )
        temporary_path.rename(path)
        temporary_name = None
    finally:
        if temporary_name is not None:
            Path(temporary_name).unlink(missing_ok=True)

    return hashlib.sha256(rendered).hexdigest(), len(rendered)


def assemble_snapshot_fragments(
    fragment_paths: list[Path],
    output_path: Path,
) -> dict[str, object]:
    if not fragment_paths:
        raise ValueError("少なくとも1つのTEI Git Data snapshot fragmentが必要です")

    output = _prepare_output_path(output_path, fragment_paths)
    merged_responses: dict[str, object] = {}
    fragment_reports: list[dict[str, object]] = []
    duplicate_identical = 0

    for fragment_path in fragment_paths:
        value, fragment_sha256 = snapshot._load_snapshot(fragment_path)
        responses = value["responses"]
        assert isinstance(responses, dict)

        for key, payload in responses.items():
            previous = merged_responses.get(key)
            if previous is None:
                merged_responses[key] = payload
                continue
            if previous != payload:
                raise ValueError(
                    "同一Git Data response pathがfragment間で異なるpayloadを持ちます: "
                    f"{key}"
                )
            duplicate_identical += 1

        fragment_reports.append(
            {
                "path": str(fragment_path.expanduser().resolve(strict=True)),
                "sha256": fragment_sha256,
                "responses": len(responses),
            }
        )

    assembled: dict[str, object] = {
        "schema": snapshot.SNAPSHOT_SCHEMA,
        "repository": prepare.GITHUB_REPOSITORY,
        "sourceCommit": prepare.REVISION_B,
        "rootTree": prepare.REVISION_B_ROOT_TREE,
        "sourceAcquisition": snapshot.CANONICAL_SOURCE_ACQUISITION,
        "credentialSource": snapshot.CANONICAL_CREDENTIAL_SOURCE,
        "responses": merged_responses,
    }
    assembled_sha256, assembled_bytes = _write_json_atomically(output, assembled)

    return {
        "schema": ASSEMBLY_REPORT_SCHEMA,
        "snapshot": {
            "schema": snapshot.SNAPSHOT_SCHEMA,
            "path": str(output),
            "sha256": assembled_sha256,
            "bytes": assembled_bytes,
            "responses": len(merged_responses),
            "containsRuntimeCredential": False,
            "preservesSourceAcquisitionProvenance": True,
            "completeness": "not_evaluated_by_assembler",
            "consumerValidationRequired": True,
        },
        "fragments": fragment_reports,
        "identicalDuplicateResponses": duplicate_identical,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "同じsei.github-git-data-snapshot/v1 metadataを持つcredential-free partial snapshotを"
            "mergeし、既存snapshot consumerへそのまま渡せるcanonical snapshot JSONを生成します。"
            "assemblerはresponse completenessを判定せず、exact-B materializationとGit identity検証は"
            "prepare_tei_revision_b_source_from_snapshot.pyへ委ねます。"
        )
    )
    parser.add_argument("--fragment", action="append", required=True, type=Path)
    parser.add_argument("--snapshot-output", required=True, type=Path)
    args = parser.parse_args()

    try:
        result = assemble_snapshot_fragments(args.fragment, args.snapshot_output)
        print(
            json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
            end="",
        )
        return 0
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        parser.exit(1, f"TEI revision B Git Data snapshot assembly failed: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
