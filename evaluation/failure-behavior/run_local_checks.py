#!/usr/bin/env python3
"""Run repository-local ISSUE-000076 failure-behavior focused checks.

This runner deliberately stops at deterministic / fixture-scoped evidence. It
must not be used to claim actual Provider failure behavior or Operational
Evidence.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Sequence


EVALUATION_DIR = Path(__file__).resolve().parent
SEI_ROOT = EVALUATION_DIR.parents[1]
GO_RUNTIME_DIR = SEI_ROOT / "runtime" / "go"
RESULT_SCHEMA = "sei.failure-behavior-local-check-result/v1"
DEFAULT_TIMEOUT_SECONDS = 120
TIMEOUT_EXIT_CODE = 124
LAUNCH_ERROR_EXIT_CODE = 127
STOP_LINE = (
    "failure behavior local checks PASS != actual Provider failure Evidence "
    "!= actual deployment failure Evidence != Operational Evidence"
)


@dataclass(frozen=True)
class Check:
    name: str
    command: tuple[str, ...]
    cwd: Path


def configured_checks() -> tuple[Check, ...]:
    return (
        Check(
            name="case-catalog-validator-tests",
            command=(sys.executable, "test_validate_failure_behavior_case_catalog.py"),
            cwd=EVALUATION_DIR,
        ),
        Check(
            name="deterministic-probe-tests",
            command=(sys.executable, "test_run_deterministic_failure_probe.py"),
            cwd=EVALUATION_DIR,
        ),
        Check(
            name="local-runner-tests",
            command=(sys.executable, "test_run_local_checks.py"),
            cwd=EVALUATION_DIR,
        ),
        Check(
            name="live-provider-runner-tests",
            command=(sys.executable, "test_run_live_provider_failure_probe.py"),
            cwd=EVALUATION_DIR,
        ),
        Check(
            name="requirement-audit-tests",
            command=(sys.executable, "test_requirement_audit.py"),
            cwd=EVALUATION_DIR,
        ),
        Check(
            name="scoped-go-evidence-tests",
            command=(sys.executable, "test_scoped_go_failure_execution_evidence.py"),
            cwd=EVALUATION_DIR,
        ),
        Check(
            name="scoped-go-source-delta-audit-tests",
            command=(sys.executable, "test_scoped_go_failure_source_delta_audit.py"),
            cwd=EVALUATION_DIR,
        ),
        Check(
            name="actual-provider-service-observation-tests",
            command=(sys.executable, "test_actual_provider_missing_revision_observation.py"),
            cwd=EVALUATION_DIR,
        ),
        Check(
            name="go-toolchain-preflight-tests",
            command=(sys.executable, "test_check_go_toolchain.py"),
            cwd=EVALUATION_DIR,
        ),
        Check(
            name="go-toolchain-preflight",
            command=(sys.executable, "check_go_toolchain.py"),
            cwd=EVALUATION_DIR,
        ),
        Check(
            name="provider-adapter-go-tests",
            command=("go", "test", "./provideradapter"),
            cwd=GO_RUNTIME_DIR,
        ),
        Check(
            name="live-provider-integration-go-tests",
            command=("go", "test", "./liveintegration"),
            cwd=GO_RUNTIME_DIR,
        ),
    )


def sanitized_environment(source: dict[str, str] | None = None) -> dict[str, str]:
    environment = dict(os.environ if source is None else source)
    # `SOZA_`はADR-0031による改名前の接頭辞である。互換のためではなく、
    # 手元に残った旧名の秘匿値がchild processへ漏れないよう除去する。
    for key in tuple(environment):
        if key.startswith(("SEI_", "SOZA_", "KJ_ATLAS_")):
            environment.pop(key, None)

    for key in (
        "OLLAMA_HOST",
        "OLLAMA_MODELS",
        "OPENAI_API_KEY",
        "DEEPSEEK_API_KEY",
        "PYTHONPATH",
        "PYTHONHOME",
        "PYTHONSTARTUP",
        "PYTHONUSERBASE",
    ):
        environment.pop(key, None)

    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONNOUSERSITE"] = "1"
    return environment


def validate_checks(checks: Sequence[Check]) -> None:
    names: set[str] = set()
    for check in checks:
        if check.name in names:
            raise ValueError(f"duplicate local check name: {check.name}")
        names.add(check.name)
        if not check.command:
            raise ValueError(f"local check command is empty: {check.name}")
        if not check.cwd.is_dir():
            raise ValueError(f"local check cwd does not exist: {check.name}: {check.cwd}")


def build_result(
    checks: Sequence[Check], executions: Sequence[dict[str, object]], *, stopped_early: bool
) -> dict[str, object]:
    failed = [item for item in executions if item["exitCode"] != 0]
    complete = len(executions) == len(checks)
    return {
        "schema": RESULT_SCHEMA,
        "result": "ok" if complete and not failed else "failed",
        "selected": [check.name for check in checks],
        "selectedCount": len(checks),
        "executed": list(executions),
        "executedCount": len(executions),
        "failedCount": len(failed),
        "stoppedEarly": stopped_early,
        "actualProviderFailureEvidence": False,
        "actualDeploymentFailureEvidence": False,
        "operationalEvidence": False,
        "stopLine": STOP_LINE,
    }


def _default_runner(
    command: Sequence[str], *, cwd: Path, env: dict[str, str], timeout: int
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(command),
        cwd=cwd,
        env=env,
        check=False,
        timeout=timeout,
        text=True,
    )


def run_checks(
    checks: Sequence[Check],
    *,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    stop_on_failure: bool = False,
    runner: Callable[..., subprocess.CompletedProcess[str]] = _default_runner,
) -> tuple[int, dict[str, object]]:
    validate_checks(checks)
    environment = sanitized_environment()
    executions: list[dict[str, object]] = []
    stopped_early = False

    for index, check in enumerate(checks, start=1):
        print(f"[{index}/{len(checks)}] {check.name}", flush=True)
        try:
            completed = runner(
                check.command,
                cwd=check.cwd,
                env=environment,
                timeout=timeout_seconds,
            )
            execution: dict[str, object] = {
                "name": check.name,
                "exitCode": completed.returncode,
                "timedOut": False,
                "timeoutSeconds": timeout_seconds,
            }
        except subprocess.TimeoutExpired:
            execution = {
                "name": check.name,
                "exitCode": TIMEOUT_EXIT_CODE,
                "timedOut": True,
                "timeoutSeconds": timeout_seconds,
            }
        except OSError as exc:
            execution = {
                "name": check.name,
                "exitCode": LAUNCH_ERROR_EXIT_CODE,
                "timedOut": False,
                "timeoutSeconds": timeout_seconds,
                "launchError": str(exc),
            }

        executions.append(execution)
        if execution["exitCode"] != 0 and stop_on_failure:
            stopped_early = index < len(checks)
            break

    result = build_result(checks, executions, stopped_early=stopped_early)
    return (0 if result["result"] == "ok" else 1), result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ISSUE-000076のrepository-local failure-behavior focused checksを実行します。",
        allow_abbrev=False,
    )
    parser.add_argument("--list", action="store_true", help="check一覧を表示して終了します。")
    parser.add_argument(
        "--stop-on-failure",
        action="store_true",
        help="最初の失敗、timeout、起動不能で残りのcheckを停止します。",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=DEFAULT_TIMEOUT_SECONDS,
        help=f"各checkの最大実行秒数。既定は{DEFAULT_TIMEOUT_SECONDS}秒です。",
    )
    parser.add_argument(
        "--result-output",
        type=Path,
        help="結果JSONを書き出すpath。既存ファイルは上書きしません。",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.timeout_seconds <= 0:
        parser.error("--timeout-secondsには1以上の整数を指定してください")

    checks = configured_checks()
    try:
        validate_checks(checks)
    except ValueError as exc:
        parser.exit(2, f"failure behavior local checks: {exc}\n")

    if args.list:
        for check in checks:
            print(f"- {check.name}: {' '.join(check.command)}")
        print(f"- stop line: {STOP_LINE}")
        return 0

    exit_code, result = run_checks(
        checks,
        timeout_seconds=args.timeout_seconds,
        stop_on_failure=args.stop_on_failure,
    )

    print("failure behavior local check summary")
    print(f"- selected: {result['selectedCount']}")
    print(f"- executed: {result['executedCount']}")
    print(f"- failed: {result['failedCount']}")
    print(f"- stop line: {STOP_LINE}")

    if args.result_output is not None:
        output = args.result_output.expanduser()
        if output.exists():
            parser.exit(2, f"result output already exists: {output}\n")
        output.write_text(
            json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"- result output: {output}")

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
