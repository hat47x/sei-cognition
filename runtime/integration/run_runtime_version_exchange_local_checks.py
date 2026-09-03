#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


INTEGRATION_DIR = Path(__file__).resolve().parent
SOZA_ROOT = INTEGRATION_DIR.parents[1]
RESULT_SCHEMA = "soza.runtime-version-exchange-focused-local-check-result/v1"

# actual Ollama / KJ Atlas A/B実行を含めず、固定identity、準備、preflight、
# strict入口、failure Evidence、保存済みEvidence verifierのfocused regressionだけを並べる。
CHECK_FILES = (
    "test_prepare_runtime_version_exchange_archives.py",
    "test_verify_kj_atlas_runtime_source.py",
    "test_export_kj_atlas_runtime_source.py",
    "test_prepare_runtime_version_exchange_model_store.py",
    "test_verify_runtime_version_exchange_model_store.py",
    "test_check_runtime_version_exchange_preflight.py",
    "test_runtime_version_exchange_preflight_model_store.py",
    "test_run_runtime_version_exchange_strict.py",
    "test_run_runtime_version_exchange_strict_model_preparation.py",
    "test_run_runtime_version_exchange.py",
    "test_run_runtime_version_exchange_with_verification.py",
    "test_run_runtime_version_exchange_local_checks.py",
    "test_runtime_version_exchange_blocked_preflight_evidence.py",
    "test_verify_runtime_version_exchange_evidence.py",
    "test_verify_runtime_version_exchange_provenance.py",
    "test_runtime_version_exchange_provenance_wiring.py",
    "test_runtime_version_exchange_identity_consistency.py",
)

# ファイル名だけではruntime version exchangeとの関係を判定できないsource identity testを
# 明示的に候補へ含める。runner自身のself-testも通常のfocused checkとして実行する。
SUPPLEMENTAL_FOCUSED_TESTS = {
    "test_verify_kj_atlas_runtime_source.py",
    "test_export_kj_atlas_runtime_source.py",
}

STOP_LINE = (
    "focused local checks PASS != actual Ollama A/B inference PASS "
    "!= runtime-version-exchange Scoped Executable Evidence"
)


def sanitized_environment() -> dict[str, str]:
    """親shellのlive probe設定をfocused testへ暗黙継承させない。"""

    environment = os.environ.copy()
    for key in tuple(environment):
        if key.startswith("SOZA_RUNTIME_EXCHANGE_") or key.startswith(
            "SOZA_E3B_RUNTIME_EXCHANGE_"
        ):
            environment.pop(key, None)
    environment.pop("OLLAMA_HOST", None)
    environment.pop("OLLAMA_MODELS", None)
    return environment


def canonical_path(path: Path) -> Path:
    return path.expanduser().resolve(strict=False)


def is_within(candidate: Path, parent: Path) -> bool:
    candidate = canonical_path(candidate)
    parent = canonical_path(parent)
    return candidate == parent or parent in candidate.parents


def prepare_result_output(path: Path) -> Path:
    requested = path.expanduser()
    if requested.is_symlink():
        raise ValueError(f"focused check result outputにsymlinkは利用できません: {requested}")
    if requested.parent.is_symlink():
        raise ValueError(
            "focused check result outputのparentにsymlinkは利用できません: "
            f"{requested.parent}"
        )

    resolved = canonical_path(requested)
    if is_within(resolved, SOZA_ROOT):
        raise ValueError(
            "focused check result outputはSOZA repository外へ保存してください: "
            f"{resolved}"
        )
    if resolved.exists():
        raise ValueError(f"focused check result outputは新規pathを指定してください: {resolved}")
    parent = resolved.parent
    if not parent.is_dir():
        raise ValueError(
            "focused check result outputのparent directoryが存在しません: "
            f"{parent}"
        )
    return resolved


def repository_observation() -> dict[str, object]:
    commit = subprocess.run(
        ["git", "-C", str(SOZA_ROOT), "rev-parse", "HEAD"],
        check=False,
        capture_output=True,
        text=True,
    )
    status = subprocess.run(
        ["git", "-C", str(SOZA_ROOT), "status", "--porcelain", "--untracked-files=all"],
        check=False,
        capture_output=True,
        text=True,
    )
    return {
        "commit": commit.stdout.strip() if commit.returncode == 0 else None,
        "clean": status.returncode == 0 and not status.stdout.strip(),
        "commitObserved": commit.returncode == 0,
        "cleanlinessObserved": status.returncode == 0,
    }


def discover_focused_candidate_names() -> set[str]:
    """命名規則から、allowlistへ登録すべきfocused testを検出する。"""

    candidates: set[str] = set()
    for path in INTEGRATION_DIR.glob("test_*.py"):
        name = path.name
        if "runtime_version_exchange" in name or name in SUPPLEMENTAL_FOCUSED_TESTS:
            candidates.add(name)
    return candidates


def validate_check_files() -> list[Path]:
    paths: list[Path] = []
    seen: set[str] = set()
    for name in CHECK_FILES:
        if name in seen:
            raise ValueError(f"focused checkが重複しています: {name}")
        seen.add(name)

        path = INTEGRATION_DIR / name
        if path.is_symlink():
            raise ValueError(f"focused checkにsymlinkは利用できません: {path}")
        if not path.is_file():
            raise ValueError(f"focused check fileがありません: {path}")
        paths.append(path)

    registered = set(CHECK_FILES)
    discovered = discover_focused_candidate_names()
    missing = sorted(discovered - registered)
    stale = sorted(registered - discovered)
    if missing:
        raise ValueError(
            "runtime交換testがfocused check allowlistへ未登録です: " + ", ".join(missing)
        )
    if stale:
        raise ValueError(
            "focused check allowlistに候補外のtestが残っています: " + ", ".join(stale)
        )
    return paths


def select_checks(requested: list[str] | None) -> list[Path]:
    paths = validate_check_files()
    if not requested:
        return paths

    requested_set = set(requested)
    unknown = sorted(requested_set - set(CHECK_FILES))
    if unknown:
        raise ValueError(f"未登録のfocused checkです: {', '.join(unknown)}")
    return [path for path in paths if path.name in requested_set]


def build_result(
    *,
    selected: list[Path],
    executions: list[dict[str, object]],
    stopped_early: bool,
) -> dict[str, object]:
    failures = [item for item in executions if item["exitCode"] != 0]
    return {
        "schema": RESULT_SCHEMA,
        "result": "ok" if not failures and len(executions) == len(selected) else "failed",
        "repository": repository_observation(),
        "selected": [path.name for path in selected],
        "executed": executions,
        "selectedCount": len(selected),
        "executedCount": len(executions),
        "failedCount": len(failures),
        "stoppedEarly": stopped_early,
        "actualRuntimeExchangeEvidence": False,
        "qualityJudgement": "not_evaluated",
        "stopLine": STOP_LINE,
    }


def write_result(path: Path, payload: dict[str, object]) -> None:
    with path.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2))
        handle.write("\n")


def run_checks(
    paths: list[Path],
    *,
    stop_on_failure: bool,
    result_output: Path | None = None,
) -> int:
    environment = sanitized_environment()
    executions: list[dict[str, object]] = []
    stopped_early = False

    for index, path in enumerate(paths, start=1):
        print(f"\n[{index}/{len(paths)}] {path.name}", flush=True)
        completed = subprocess.run(
            [sys.executable, str(path)],
            cwd=INTEGRATION_DIR,
            env=environment,
            check=False,
        )
        executions.append({"name": path.name, "exitCode": completed.returncode})
        if completed.returncode != 0 and stop_on_failure:
            stopped_early = index < len(paths)
            break

    payload = build_result(
        selected=paths,
        executions=executions,
        stopped_early=stopped_early,
    )

    print("\nfocused local check summary")
    print(f"- selected: {payload['selectedCount']}")
    print(f"- executed: {payload['executedCount']}")
    print(f"- failed: {payload['failedCount']}")
    for item in executions:
        if item["exitCode"] != 0:
            print(f"  - {item['name']}: exit {item['exitCode']}")
    print(f"- stop line: {STOP_LINE}")

    if result_output is not None:
        write_result(result_output, payload)
        print(f"- result output: {result_output}")

    return 0 if payload["result"] == "ok" else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "ISSUE-000070のactual A/B processを起動せず、repository-localのfocused "
            "Python regressionを明示的なallowlistから順番に実行します。"
        ),
        allow_abbrev=False,
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="登録済みfocused checkを表示して終了します。",
    )
    parser.add_argument(
        "--only",
        action="append",
        metavar="TEST_FILE",
        help="指定した登録済みtestだけを実行します。複数回指定できます。",
    )
    parser.add_argument(
        "--stop-on-failure",
        action="store_true",
        help="最初のnon-zero終了で残りのcheckを実行せず停止します。",
    )
    parser.add_argument(
        "--result-output",
        type=Path,
        help=(
            "focused regression結果を保存する新規JSON path。"
            "SOZA repository外の既存parent directory配下を指定します。"
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.list and args.result_output is not None:
        parser.error("--listと--result-outputは同時に指定できません")

    try:
        paths = select_checks(args.only)
        result_output = (
            prepare_result_output(args.result_output)
            if args.result_output is not None
            else None
        )
    except ValueError as exc:
        parser.exit(2, f"focused local check runner: {exc}\n")

    if args.list:
        print("runtime version exchange focused local checks")
        for path in paths:
            print(f"- {path.name}")
        print(f"- stop line: {STOP_LINE}")
        return 0

    return run_checks(
        paths,
        stop_on_failure=args.stop_on_failure,
        result_output=result_output,
    )


if __name__ == "__main__":
    raise SystemExit(main())
