#!/usr/bin/env python3
"""Cognitive Method human review bundleの再構成用manifestを作る。

このscriptは品質を採点しない。workflow runとreview対象ファイルのidentity / digestを
一つのmanifestへまとめ、人間が後から同じrequest / result / Evidence / structure reportを
対応付けて確認できるようにするだけである。
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

MANIFEST_SCHEMA = "soza.method-quality-review-bundle/v1"


def _file_record(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {
        "name": path.name,
        "sha256": hashlib.sha256(data).hexdigest(),
        "bytes": len(data),
    }


def build_manifest(
    *,
    workflow_run_id: str,
    workflow_run_attempt: str,
    repository_commit: str,
    method_source_commit: str,
    request_path: Path,
    result_path: Path,
    model_evidence_path: Path,
    structure_report_path: Path,
    runtime_version_path: Path,
    model_list_path: Path,
) -> dict[str, Any]:
    files = {
        "request": _file_record(request_path),
        "result": _file_record(result_path),
        "modelEvidence": _file_record(model_evidence_path),
        "structureReport": _file_record(structure_report_path),
        "runtimeVersion": _file_record(runtime_version_path),
        "modelList": _file_record(model_list_path),
    }

    structure = json.loads(structure_report_path.read_text(encoding="utf-8"))
    request_digest = files["request"]["sha256"]
    result_digest = files["result"]["sha256"]

    if structure.get("requestSha256") != request_digest:
        raise ValueError(
            "structure report requestSha256 does not match the review bundle request"
        )
    if structure.get("resultSha256") != result_digest:
        raise ValueError(
            "structure report resultSha256 does not match the review bundle result"
        )

    return {
        "schema": MANIFEST_SCHEMA,
        "workflowRunId": workflow_run_id,
        "workflowRunAttempt": workflow_run_attempt,
        "repositoryCommit": repository_commit,
        "methodSourceCommit": method_source_commit,
        "files": files,
        "structureStatus": structure.get("status"),
        "qualityJudgement": structure.get("qualityJudgement"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "human review bundleのrun identityとfile digestをmanifestへ記録します。"
            "意味的品質は採点しません。"
        )
    )
    parser.add_argument("--workflow-run-id", required=True)
    parser.add_argument("--workflow-run-attempt", required=True)
    parser.add_argument("--repository-commit", required=True)
    parser.add_argument("--method-source-commit", required=True)
    parser.add_argument("--request", required=True, type=Path)
    parser.add_argument("--result", required=True, type=Path)
    parser.add_argument("--model-evidence", required=True, type=Path)
    parser.add_argument("--structure-report", required=True, type=Path)
    parser.add_argument("--runtime-version", required=True, type=Path)
    parser.add_argument("--model-list", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    try:
        manifest = build_manifest(
            workflow_run_id=args.workflow_run_id,
            workflow_run_attempt=args.workflow_run_attempt,
            repository_commit=args.repository_commit,
            method_source_commit=args.method_source_commit,
            request_path=args.request,
            result_path=args.result,
            model_evidence_path=args.model_evidence,
            structure_report_path=args.structure_report,
            runtime_version_path=args.runtime_version,
            model_list_path=args.model_list,
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise SystemExit(f"review bundle manifestを作成できません: {exc}") from exc

    encoded = json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
