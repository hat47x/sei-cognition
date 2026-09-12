#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Mapping

import prepare_tei_revision_b_source as prepare
from runtime_path_safety import reject_symlink_path_or_ancestors

SNAPSHOT_SCHEMA = "sei.github-git-data-snapshot/v1"
SNAPSHOT_TRANSPORT_TOKEN = "__preacquired_git_data_snapshot__"
CANONICAL_SOURCE_ACQUISITION = "github-git-data-api-content-addressed"
CANONICAL_CREDENTIAL_SOURCE = "environment"
SNAPSHOT_TRANSPORT_MODE = "preacquired-github-git-data-snapshot"
_ALLOWED_RESPONSE_PATH = re.compile(r"git/(?:blobs|trees|commits)/[0-9a-f]{40}")
_REQUIRED_TOP_LEVEL = {
    "schema",
    "repository",
    "sourceCommit",
    "rootTree",
    "sourceAcquisition",
    "credentialSource",
    "responses",
}


def _load_snapshot(path: Path) -> tuple[dict[str, object], str]:
    requested = path.expanduser()
    reject_symlink_path_or_ancestors(requested, "TEI Git Data snapshot")
    resolved = requested.resolve(strict=True)
    if not resolved.is_file():
        raise ValueError(f"TEI Git Data snapshotがfileではありません: {resolved}")

    raw = resolved.read_bytes()
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("TEI Git Data snapshotをJSONとして解釈できません") from exc
    if not isinstance(value, dict):
        raise ValueError("TEI Git Data snapshotのtop-levelがobjectではありません")

    keys = set(value)
    if keys != _REQUIRED_TOP_LEVEL:
        missing = sorted(_REQUIRED_TOP_LEVEL - keys)
        unexpected = sorted(keys - _REQUIRED_TOP_LEVEL)
        raise ValueError(
            "TEI Git Data snapshotのtop-level fieldが固定schemaと一致しません: "
            f"missing={missing} unexpected={unexpected}"
        )
    if value.get("schema") != SNAPSHOT_SCHEMA:
        raise ValueError(
            "TEI Git Data snapshot schemaが不正です: "
            f"expected={SNAPSHOT_SCHEMA} actual={value.get('schema')}"
        )
    if value.get("repository") != prepare.GITHUB_REPOSITORY:
        raise ValueError(
            "TEI Git Data snapshot repositoryが固定値と一致しません: "
            f"expected={prepare.GITHUB_REPOSITORY} actual={value.get('repository')}"
        )
    if value.get("sourceCommit") != prepare.REVISION_B:
        raise ValueError(
            "TEI Git Data snapshot sourceCommitがfixed revision Bと一致しません: "
            f"expected={prepare.REVISION_B} actual={value.get('sourceCommit')}"
        )
    if value.get("rootTree") != prepare.REVISION_B_ROOT_TREE:
        raise ValueError(
            "TEI Git Data snapshot rootTreeがfixed revision Bと一致しません: "
            f"expected={prepare.REVISION_B_ROOT_TREE} actual={value.get('rootTree')}"
        )
    if value.get("sourceAcquisition") != CANONICAL_SOURCE_ACQUISITION:
        raise ValueError(
            "TEI Git Data snapshot source acquisition provenanceが固定経路と一致しません: "
            f"expected={CANONICAL_SOURCE_ACQUISITION} "
            f"actual={value.get('sourceAcquisition')}"
        )
    if value.get("credentialSource") != CANONICAL_CREDENTIAL_SOURCE:
        raise ValueError(
            "TEI Git Data snapshot credential provenanceが固定経路と一致しません: "
            f"expected={CANONICAL_CREDENTIAL_SOURCE} "
            f"actual={value.get('credentialSource')}"
        )

    responses = value.get("responses")
    if not isinstance(responses, dict) or not responses:
        raise ValueError("TEI Git Data snapshot responsesが空またはobjectではありません")
    for key, payload in responses.items():
        if not isinstance(key, str) or _ALLOWED_RESPONSE_PATH.fullmatch(key) is None:
            raise ValueError(f"TEI Git Data snapshot response pathが不正です: {key!r}")
        if not isinstance(payload, dict):
            raise ValueError(
                f"TEI Git Data snapshot responseがobjectではありません: {key}"
            )
        expected_sha = key.rsplit("/", 1)[1]
        if payload.get("sha") != expected_sha:
            raise ValueError(
                "TEI Git Data snapshot response SHAがpathと一致しません: "
                f"path={key} payload.sha={payload.get('sha')}"
            )

    return value, hashlib.sha256(raw).hexdigest()


class SnapshotRequester:
    def __init__(self, responses: Mapping[str, object]):
        self.responses = responses
        self.calls: list[str] = []

    def __call__(self, url: str, token: str) -> dict[str, object]:
        if token != SNAPSHOT_TRANSPORT_TOKEN:
            raise ValueError("snapshot transportへruntime credentialを渡してはいけません")
        if not url.startswith(prepare.API_REPOSITORY_BASE):
            raise ValueError(f"snapshot transportで未承認URLが要求されました: {url}")
        key = url[len(prepare.API_REPOSITORY_BASE) :]
        if _ALLOWED_RESPONSE_PATH.fullmatch(key) is None:
            raise ValueError(f"snapshot transportで未承認Git Data pathが要求されました: {key}")
        payload = self.responses.get(key)
        if not isinstance(payload, dict):
            raise ValueError(f"snapshotに必要なGit Data responseがありません: {key}")
        self.calls.append(key)
        return payload


def materialize_revision_b_source_from_snapshot(
    output_dir: Path,
    *,
    snapshot_path: Path,
) -> dict[str, object]:
    output = prepare._prepare_output_path(output_dir)
    snapshot_file = snapshot_path.expanduser().resolve(strict=False)
    if prepare._paths_overlap(output, snapshot_file):
        raise ValueError(
            "TEI Git Data snapshotとmaterialized source pathを分離してください: "
            f"snapshot={snapshot_file} source={output}"
        )

    snapshot, snapshot_sha256 = _load_snapshot(snapshot_path)
    responses = snapshot["responses"]
    assert isinstance(responses, dict)
    requester = SnapshotRequester(responses)

    result = prepare.materialize_revision_b_source(
        output,
        token=SNAPSHOT_TRANSPORT_TOKEN,
        repository=prepare.GITHUB_REPOSITORY,
        expected_commit=prepare.REVISION_B,
        expected_root_tree=prepare.REVISION_B_ROOT_TREE,
        expected_objects=prepare.EXPECTED_OBJECTS,
        request_json=requester,
    )

    # Acquisition provenance describes how the Git Data bytes originally came
    # from GitHub. Snapshot is only the cross-environment transport. Keeping
    # those two facts separate preserves the existing E2/E3 resume contract.
    result["sourceAcquisition"] = snapshot["sourceAcquisition"]
    result["credentialSource"] = snapshot["credentialSource"]
    result["sourceTransport"] = {
        "mode": SNAPSHOT_TRANSPORT_MODE,
        "schema": SNAPSHOT_SCHEMA,
        "sha256": snapshot_sha256,
        "responsesAvailable": len(responses),
        "responsesConsumed": len(requester.calls),
        "allConsumedResponsesUnique": len(set(requester.calls)) == len(requester.calls),
        "runtimeCredentialUsed": False,
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "事前取得済みGitHub Git Data JSON snapshotをnetwork/credentialなしのtransportとして使い、"
            "既存content-addressed reconstructionとcanonical source verifierでexact TEI revision Bを"
            "materializeします。snapshot自体は信頼せず、blob/tree/signed commitのGit identityを再計算します。"
        )
    )
    parser.add_argument("--snapshot", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--report-output", type=Path)
    args = parser.parse_args()

    try:
        output = prepare._prepare_output_path(args.output_dir)
        report = (
            prepare._prepare_report_path(args.report_output, output)
            if args.report_output is not None
            else None
        )
        snapshot = args.snapshot.expanduser().resolve(strict=False)
        if report is not None and prepare._paths_overlap(report, snapshot):
            raise ValueError(
                "TEI source acquisition reportとGit Data snapshotを分離してください: "
                f"report={report} snapshot={snapshot}"
            )

        result = materialize_revision_b_source_from_snapshot(
            output,
            snapshot_path=args.snapshot,
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
        parser.exit(1, f"TEI revision B snapshot source acquisition failed: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
