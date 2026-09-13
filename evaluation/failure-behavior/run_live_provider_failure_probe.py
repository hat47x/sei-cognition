#!/usr/bin/env python3
"""Run the opt-in actual GitHub Provider failure probes for ISSUE-000072.

This runner requires an explicit --allow-live flag. It validates the two exact
Go test cases from ``runtime/go/liveintegration`` by parsing ``go test -json``;
a zero process exit alone is not sufficient evidence.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Callable, Sequence


EVALUATION_DIR = Path(__file__).resolve().parent
SEI_ROOT = EVALUATION_DIR.parents[1]
GO_RUNTIME_DIR = SEI_ROOT / "runtime" / "go"
RESULT_SCHEMA = "sei.live-provider-failure-probe-result/v1"
DEFAULT_TIMEOUT_SECONDS = 120
TIMEOUT_EXIT_CODE = 124
LAUNCH_ERROR_EXIT_CODE = 127
LIVE_FLAG = "SEI_E3B_FAILURE_LIVE"
EXPECTED_TESTS = (
    "TestLiveGitHubCommitServiceMissingRevisionFailure",
    "TestLiveGitHubCommitServiceInvalidCredentialFailure",
)
TEST_RUN_PATTERN = "^(" + "|".join(EXPECTED_TESTS) + ")$"
STOP_LINE = "actual Provider failure probe PASS != Operational Evidence"


def sanitized_live_environment(source: dict[str, str] | None = None) -> dict[str, str]:
    """Build a credential-minimal environment for the intentional live probe."""

    environment = dict(os.environ if source is None else source)
    for key in tuple(environment):
        if key.startswith("SEI_") or key.startswith("KJ_ATLAS_"):
            environment.pop(key, None)

    for key in (
        "OLLAMA_HOST",
        "OLLAMA_MODELS",
        "OPENAI_API_KEY",
        "DEEPSEEK_API_KEY",
        "GITHUB_TOKEN",
        "GH_TOKEN",
        "PYTHONPATH",
        "PYTHONHOME",
        "PYTHONSTARTUP",
        "PYTHONUSERBASE",
    ):
        environment.pop(key, None)

    # The live failure tests use an unauthenticated missing-revision request and
    # one fixed intentionally-invalid token. No real Provider credential is
    # required or inherited from the parent shell.
    environment[LIVE_FLAG] = "1"
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONNOUSERSITE"] = "1"
    return environment


def live_command() -> tuple[str, ...]:
    return (
        "go",
        "test",
        "./liveintegration",
        "-run",
        TEST_RUN_PATTERN,
        "-count=1",
        "-json",
    )


def parse_go_test_json(output: str) -> tuple[dict[str, str], list[str]]:
    """Return terminal actions for expected tests and parse diagnostics."""

    terminal: dict[str, str] = {}
    errors: list[str] = []
    for line_number, raw_line in enumerate(output.splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"line {line_number}: invalid go test JSON: {exc.msg}")
            continue
        if not isinstance(event, dict):
            errors.append(f"line {line_number}: go test event must be an object")
            continue
        test = event.get("Test")
        action = event.get("Action")
        if test in EXPECTED_TESTS and action in {"pass", "fail", "skip"}:
            terminal[str(test)] = str(action)
    return terminal, errors


def evaluate_execution(returncode: int, output: str) -> dict[str, object]:
    terminal, parse_errors = parse_go_test_json(output)
    missing = [name for name in EXPECTED_TESTS if name not in terminal]
    non_pass = {
        name: terminal[name]
        for name in EXPECTED_TESTS
        if name in terminal and terminal[name] != "pass"
    }
    passed = (
        returncode == 0
        and not parse_errors
        and not missing
        and not non_pass
        and all(terminal.get(name) == "pass" for name in EXPECTED_TESTS)
    )
    return {
        "schema": RESULT_SCHEMA,
        "result": "ok" if passed else "failed",
        "commandExitCode": returncode,
        "expectedTests": list(EXPECTED_TESTS),
        "observedTerminalActions": {
            name: terminal[name] for name in EXPECTED_TESTS if name in terminal
        },
        "missingTests": missing,
        "nonPassTests": non_pass,
        "parseErrors": parse_errors,
        "actualProviderFailureEvidence": passed,
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
        capture_output=True,
        text=True,
    )


def run_live_probe(
    *,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    runner: Callable[..., subprocess.CompletedProcess[str]] = _default_runner,
) -> tuple[int, dict[str, object]]:
    command = live_command()
    environment = sanitized_live_environment()
    try:
        completed = runner(
            command,
            cwd=GO_RUNTIME_DIR,
            env=environment,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired:
        result = {
            "schema": RESULT_SCHEMA,
            "result": "failed",
            "commandExitCode": TIMEOUT_EXIT_CODE,
            "timedOut": True,
            "timeoutSeconds": timeout_seconds,
            "expectedTests": list(EXPECTED_TESTS),
            "observedTerminalActions": {},
            "missingTests": list(EXPECTED_TESTS),
            "nonPassTests": {},
            "parseErrors": [],
            "actualProviderFailureEvidence": False,
            "operationalEvidence": False,
            "stopLine": STOP_LINE,
        }
        return 1, result
    except OSError as exc:
        result = {
            "schema": RESULT_SCHEMA,
            "result": "failed",
            "commandExitCode": LAUNCH_ERROR_EXIT_CODE,
            "timedOut": False,
            "timeoutSeconds": timeout_seconds,
            "launchError": str(exc),
            "expectedTests": list(EXPECTED_TESTS),
            "observedTerminalActions": {},
            "missingTests": list(EXPECTED_TESTS),
            "nonPassTests": {},
            "parseErrors": [],
            "actualProviderFailureEvidence": False,
            "operationalEvidence": False,
            "stopLine": STOP_LINE,
        }
        return 1, result

    result = evaluate_execution(completed.returncode, completed.stdout)
    result["timedOut"] = False
    result["timeoutSeconds"] = timeout_seconds
    if completed.returncode != 0 and completed.stderr.strip():
        # stderr is useful for local diagnosis but is deliberately not copied
        # into the machine-readable result because external tooling can include
        # environment- or platform-specific details there.
        result["stderrAvailable"] = True
    return (0 if result["result"] == "ok" else 1), result


def prepare_result_output(path: Path) -> Path:
    requested = path.expanduser()
    if requested.exists():
        raise ValueError(f"result output already exists: {requested}")
    parent = requested.parent.resolve(strict=False)
    if not parent.is_dir():
        raise ValueError(f"result output parent does not exist: {parent}")
    resolved = requested.resolve(strict=False)
    repository = SEI_ROOT.resolve(strict=False)
    if resolved == repository or repository in resolved.parents:
        raise ValueError("result output must be outside the SEI repository")
    return resolved


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "ISSUE-000072のactual GitHub Provider failure probeを明示的opt-inで実行します。"
        ),
        allow_abbrev=False,
    )
    parser.add_argument(
        "--allow-live",
        action="store_true",
        help="外部GitHub APIへのnegative probe実行を明示的に許可します。",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=DEFAULT_TIMEOUT_SECONDS,
        help=f"go testの最大実行秒数。既定は{DEFAULT_TIMEOUT_SECONDS}秒です。",
    )
    parser.add_argument(
        "--result-output",
        type=Path,
        help="repository外へ保存する新規result JSON path。",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.allow_live:
        parser.error("actual Providerへ通信するため --allow-live が必要です")
    if args.timeout_seconds <= 0:
        parser.error("--timeout-secondsには1以上の整数を指定してください")

    try:
        result_output = (
            prepare_result_output(args.result_output)
            if args.result_output is not None
            else None
        )
    except ValueError as exc:
        parser.exit(2, f"live Provider failure runner: {exc}\n")

    exit_code, result = run_live_probe(timeout_seconds=args.timeout_seconds)
    print("live Provider failure probe summary")
    print(f"- result: {result['result']}")
    print(f"- command exit: {result['commandExitCode']}")
    print(f"- observed tests: {result['observedTerminalActions']}")
    print(f"- actual Provider failure Evidence: {result['actualProviderFailureEvidence']}")
    print(f"- stop line: {STOP_LINE}")

    if result_output is not None:
        with result_output.open("x", encoding="utf-8") as handle:
            handle.write(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
            handle.write("\n")
        print(f"- result output: {result_output}")

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
