#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Callable

import prepare_tei_revision_b_source as prepare
from prepare_tei_revision_b_source_from_snapshot import (
    CANONICAL_CREDENTIAL_SOURCE,
    CANONICAL_SOURCE_ACQUISITION,
    SNAPSHOT_SCHEMA,
)
from runtime_path_safety import reject_symlink_path_or_ancestors

JsonRequester = Callable[[str, str], dict[str, object]]


class RecordingRequester:
    def __init__(self, request_json: JsonRequester = prepare._github_json):
        self.request_json = request_json
        self.responses: dict[str, dict[str, object]] = {}

    def __call__(self, url: str, token: str) -> dict[str, object]:
        if not url.startswith(prepare.API_REPOSITORY_BASE):
            raise ValueError(f"snapshot captureで未承認URLが要求されました: {url}")
        key = url[len(prepare.API_REPOSITORY_BASE) :]
        payload = self.request_json(url, token)
        previous = self.responses.get(key)
        if previous is not None and previous != payload:
            raise ValueError(
                "同一Git Data pathがcapture中に異なるresponseを返しました: "
                f"{key}"
            )
        self.responses[key] = payload
        return payload


def _prepare_snapshot_output(path: Path, source_output: Path) -> Path:
    requested = path.expanduser()
    reject_symlink_path_or_ancestors(requested, "TEI Git Data snapshot出力")
    output = requested.resolve(strict=False)
    if output.exists():
        raise ValueError(
            f"TEI Git Data snapshot出力は新規pathを指定してください: {output}"
        )
    if prepare._paths_overlap(output, source_output):
        raise ValueError(
            "TEI Git Data snapshotとmaterialized source pathを分離してください: "
            f"snapshot={output} source={source_output}"
        )
    if output == prepare.SOZA_ROOT or prepare.SOZA_ROOT in output.parents:
        raise ValueError(
            f"TEI Git Data snapshotをSEI repository配下には置けません: {output}"
        )
    return output


def _write_json_atomically(path: Path, value: dict[str, object]) -> tuple[str, int]:
    rendered = (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    reject_symlink_path_or_ancestors(path, "TEI Git Data snapshot出力")
    if path.exists():
        raise ValueError(
            f"TEI Git Data snapshot出力がcapture中に作成されました: {path}"
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
        reject_symlink_path_or_ancestors(path, "TEI Git Data snapshot出力")
        if path.exists():
            raise ValueError(
                f"TEI Git Data snapshot出力がcapture中に作成されました: {path}"
            )
        temporary_path.rename(path)
        temporary_name = None
    finally:
        if temporary_name is not None:
            Path(temporary_name).unlink(missing_ok=True)

    return hashlib.sha256(rendered).hexdigest(), len(rendered)


def capture_revision_b_source_and_snapshot(
    source_output: Path,
    snapshot_output: Path,
    *,
    token: str,
    request_json: JsonRequester = prepare._github_json,
) -> dict[str, object]:
    if not token:
        raise ValueError("GitHub API tokenがありません")
    source = prepare._prepare_output_path(source_output)
    snapshot = _prepare_snapshot_output(snapshot_output, source)
    recorder = RecordingRequester(request_json)

    result = prepare.materialize_revision_b_source(
        source,
        token=token,
        repository=prepare.GITHUB_REPOSITORY,
        expected_commit=prepare.REVISION_B,
        expected_root_tree=prepare.REVISION_B_ROOT_TREE,
        expected_objects=prepare.EXPECTED_OBJECTS,
        request_json=recorder,
    )
    if result.get("sourceAcquisition") != CANONICAL_SOURCE_ACQUISITION:
        raise ValueError(
            "materialized source acquisition provenanceが固定経路と一致しません: "
            f"actual={result.get('sourceAcquisition')}"
        )
    if result.get("credentialSource") != CANONICAL_CREDENTIAL_SOURCE:
        raise ValueError(
            "materialized source credential provenanceが固定経路と一致しません: "
            f"actual={result.get('credentialSource')}"
        )

    snapshot_value: dict[str, object] = {
        "schema": SNAPSHOT_SCHEMA,
        "repository": prepare.GITHUB_REPOSITORY,
        "sourceCommit": prepare.REVISION_B,
        "rootTree": prepare.REVISION_B_ROOT_TREE,
        "sourceAcquisition": CANONICAL_SOURCE_ACQUISITION,
        "credentialSource": CANONICAL_CREDENTIAL_SOURCE,
        "responses": recorder.responses,
    }
    snapshot_sha256, snapshot_bytes = _write_json_atomically(
        snapshot,
        snapshot_value,
    )
    result["transportSnapshotExport"] = {
        "schema": SNAPSHOT_SCHEMA,
        "path": str(snapshot),
        "sha256": snapshot_sha256,
        "bytes": snapshot_bytes,
        "responses": len(recorder.responses),
        "containsRuntimeCredential": False,
        "preservesSourceAcquisitionProvenance": True,
    }
    return result


def _token_from_environment() -> str:
    return os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "GitHub Git Data APIからexact TEI revision Bを既存content-addressed materializerで"
            "検証・checkoutし、その取得responseとbounded acquisition provenanceだけを"
            "credential-free snapshotとして別pathへ保存します。snapshotはoffline環境で"
            "prepare_tei_revision_b_source_from_snapshot.pyへ渡せます。"
        )
    )
    parser.add_argument("--source-output", required=True, type=Path)
    parser.add_argument("--snapshot-output", required=True, type=Path)
    parser.add_argument("--report-output", type=Path)
    args = parser.parse_args()

    try:
        source = prepare._prepare_output_path(args.source_output)
        snapshot = _prepare_snapshot_output(args.snapshot_output, source)
        report = (
            prepare._prepare_report_path(args.report_output, source)
            if args.report_output is not None
            else None
        )
        if report is not None and prepare._paths_overlap(report, snapshot):
            raise ValueError(
                "TEI source acquisition reportとGit Data snapshotを分離してください: "
                f"report={report} snapshot={snapshot}"
            )
        token = _token_from_environment()
        if not token:
            raise ValueError(
                "GITHUB_TOKENまたはGH_TOKENをenvironmentへ設定してください"
            )

        result = capture_revision_b_source_and_snapshot(
            source,
            snapshot,
            token=token,
        )
        rendered = json.dumps(
            result,
            ensure_ascii=False,
            sort_keys=True,
            indent=2,
        ) + "\n"
        if report is not None:
            report.parent.mkdir(parents=True, exist_ok=True)
            report.write_text(rendered, encoding="utf-8")
        print(rendered, end="")
        return 0
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        parser.exit(1, f"TEI revision B Git Data snapshot capture failed: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
