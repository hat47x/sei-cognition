#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import verify_runtime_version_exchange_evidence as base

EXPECTED_PREFLIGHT_SCHEMA = "sei.runtime-version-exchange-preflight/v1"
PREFLIGHT_FILE = "runtime-exchange-preflight.json"
RUNNER_FILE = "runtime-exchange-runner-observation.json"


def _append_check(
    report: dict[str, Any],
    check_id: str,
    condition: bool,
    ok_detail: str,
    blocked_detail: str,
) -> None:
    status = "ok" if condition else "blocked"
    report.setdefault("checks", []).append(
        {
            "id": check_id,
            "status": status,
            "detail": ok_detail if condition else blocked_detail,
        }
    )
    if not condition:
        report.setdefault("blockers", []).append(check_id)


def _read_required_json(root: Path, name: str, report: dict[str, Any]) -> dict[str, Any] | None:
    path = root / name
    if path.is_symlink():
        _append_check(
            report,
            f"preflight.file.{name}",
            False,
            "",
            f"Evidence fileはsymlinkを許可しません: {path}",
        )
        return None
    if not path.is_file():
        _append_check(
            report,
            f"preflight.file.{name}",
            False,
            "",
            f"Evidence fileがありません: {path}",
        )
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        _append_check(
            report,
            f"preflight.json.{name}",
            False,
            "",
            f"JSONを解釈できません: {name}: {exc}",
        )
        return None
    if not isinstance(payload, dict):
        _append_check(
            report,
            f"preflight.json.{name}",
            False,
            "",
            f"JSON objectが必要です: {name}",
        )
        return None
    _append_check(
        report,
        f"preflight.file.{name}",
        True,
        f"Evidence fileを確認しました: {name}",
        "",
    )
    return payload


def _expected_fixed_artifacts(manifest: dict[str, Any]) -> dict[str, Any]:
    runtime_a = manifest["runtimeArchives"]["a"]
    runtime_b = manifest["runtimeArchives"]["b"]
    model = manifest["model"]
    return {
        "runtimeA": {
            "version": runtime_a["version"],
            "sizeBytes": runtime_a["sizeBytes"],
            "sha256": runtime_a["sha256"],
        },
        "runtimeB": {
            "version": runtime_b["version"],
            "sizeBytes": runtime_b["sizeBytes"],
            "sha256": runtime_b["sha256"],
        },
        "totalCompressedRuntimeBytes": runtime_a["sizeBytes"] + runtime_b["sizeBytes"],
        "model": {
            "name": model["name"],
            "sha256": model["sha256"],
        },
    }


def _expected_source_identity(manifest: dict[str, Any]) -> dict[str, Any]:
    return {
        "repository": manifest["methodSource"]["repository"],
        "sourceCommit": base.EXPECTED_SOURCE_COMMIT,
        "pinnedBackendTree": base.EXPECTED_PARENT_BACKEND_TREE,
        "runtimeSurfaceTree": base.EXPECTED_RUNTIME_SURFACE_TREE,
    }


def _preflight_source_mode(preflight: dict[str, Any]) -> str | None:
    checks = preflight.get("checks")
    if not isinstance(checks, list):
        return None
    for check in checks:
        if not isinstance(check, dict) or check.get("id") != "kj-atlas.source-mode":
            continue
        detail = check.get("detail")
        if not isinstance(detail, str):
            return None
        if detail.startswith("source mode: git-checkout"):
            return "git-checkout"
        if detail.startswith("source mode: verified-runtime-bundle"):
            return "verified-runtime-bundle"
        return None
    return None


def _expected_source_preparation(preflight_source_mode: str | None) -> str | None:
    if preflight_source_mode == "git-checkout":
        return "checkout-to-verified-runtime-bundle"
    if preflight_source_mode == "verified-runtime-bundle":
        return "verified-runtime-bundle"
    return None


def verify_run_evidence(
    evidence_dir: Path,
    *,
    manifest_path: Path = base.ARTIFACT_MANIFEST,
) -> dict[str, Any]:
    root = evidence_dir.expanduser().resolve(strict=False)
    report = base.verify_evidence_directory(root, manifest_path=manifest_path)
    report["checks"] = list(report.get("checks", []))
    report["blockers"] = list(report.get("blockers", []))

    manifest = base._load_manifest(manifest_path)
    preflight = _read_required_json(root, PREFLIGHT_FILE, report)
    runner = _read_required_json(root, RUNNER_FILE, report)
    preflight_source_mode: str | None = None

    if preflight is not None:
        _append_check(
            report,
            "preflight.schema",
            preflight.get("schema") == EXPECTED_PREFLIGHT_SCHEMA,
            "preflight schemaを確認しました",
            f"preflight schemaが固定値と一致しません: {preflight.get('schema')!r}",
        )
        _append_check(
            report,
            "preflight.result",
            preflight.get("result") == "ready" and preflight.get("blockers") == [],
            "actual処理前preflightがreadyだったことを確認しました",
            "preflightがreadyではない、またはblockerを保持しています",
        )
        checks = preflight.get("checks")
        consistent_checks = (
            isinstance(checks, list)
            and bool(checks)
            and all(
                isinstance(check, dict) and check.get("status") in {"ok", "deferred"}
                for check in checks
            )
        )
        _append_check(
            report,
            "preflight.check-consistency",
            consistent_checks,
            "preflight checksがok / deferredだけで構成されていることを確認しました",
            "preflight resultと個別checkの状態が整合しません",
        )
        _append_check(
            report,
            "preflight.fixed-artifacts",
            preflight.get("fixedArtifacts") == _expected_fixed_artifacts(manifest),
            "preflightの固定runtime / model条件がartifact manifestと一致します",
            "preflightの固定runtime / model条件がartifact manifestと一致しません",
        )
        _append_check(
            report,
            "preflight.pinned-source",
            preflight.get("pinnedSourceIdentity") == _expected_source_identity(manifest),
            "preflightの固定KJ Atlas source identityがcurrent固定条件と一致します",
            "preflightの固定KJ Atlas source identityがcurrent固定条件と一致しません",
        )
        preflight_source_mode = _preflight_source_mode(preflight)
        _append_check(
            report,
            "preflight.source-mode",
            preflight_source_mode in {"git-checkout", "verified-runtime-bundle"},
            f"preflightのsource acquisition modeを確認しました: {preflight_source_mode}",
            "preflightのKJ Atlas source acquisition modeを解釈できません",
        )

    if runner is not None:
        _append_check(
            report,
            "runner.preflight-result",
            runner.get("preflightResult") == "ready",
            "runner observationがpreflight readyを保持しています",
            f"runner observationのpreflightResultがreadyではありません: {runner.get('preflightResult')!r}",
        )
        expected_preparation = _expected_source_preparation(preflight_source_mode)
        _append_check(
            report,
            "runner.source-preparation",
            expected_preparation is not None
            and runner.get("sourcePreparation") == expected_preparation,
            "preflightのsource acquisition modeとrunnerのsource preparationが整合しています",
            "preflight source acquisitionとrunner source preparationが整合しません: "
            f"preflight={preflight_source_mode!r} "
            f"runner={runner.get('sourcePreparation')!r} expected={expected_preparation!r}",
        )

    report["blockers"] = list(dict.fromkeys(report["blockers"]))
    report["result"] = "ready-to-review" if not report["blockers"] else "not-sufficient"
    report["stopLine"] = (
        "mechanical run Evidence verification PASS != Requirement / Contract assessment complete "
        "!= outcome quality satisfied != ISSUE-000070 Resolved"
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "ISSUE-000070のruntime version exchange Evidenceを、actual run本体に加えて"
            "実行前preflightの保存結果まで含めて副作用なく再検証します。"
        )
    )
    parser.add_argument("--evidence-dir", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--json", action="store_true", help="構造化JSONだけを出力します。")
    args = parser.parse_args()

    try:
        output = (
            base._prepare_output_path(args.output, args.evidence_dir)
            if args.output is not None
            else None
        )
        report = verify_run_evidence(args.evidence_dir)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        parser.exit(2, f"runtime version exchange run Evidence verification failed: {exc}\n")

    rendered = json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    if args.json or output is None:
        print(rendered, end="")
    else:
        print(f"Run Evidence verification result: {report['result']}")
        if report["blockers"]:
            print("Blockers: " + ", ".join(report["blockers"]))
    return 0 if report["result"] == "ready-to-review" else 1


if __name__ == "__main__":
    raise SystemExit(main())
