#!/usr/bin/env python3
"""Fail closed when the local Go toolchain is below runtime/go/go.mod.

This preflight is intentionally repository-local. It disables automatic
toolchain switching so an environment that only has an older Go executable
cannot silently download a newer toolchain and be mistaken for an already
provisioned baseline.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Callable, Sequence


EVALUATION_DIR = Path(__file__).resolve().parent
SEI_ROOT = EVALUATION_DIR.parents[1]
GO_RUNTIME_DIR = SEI_ROOT / "runtime" / "go"
GO_MOD = GO_RUNTIME_DIR / "go.mod"
DEFAULT_TIMEOUT_SECONDS = 30


def parse_go_version(value: str) -> tuple[int, int, int]:
    token = value.strip()
    if token.startswith("go"):
        token = token[2:]
    parts = token.split(".")
    if len(parts) not in {2, 3} or not all(part.isdigit() for part in parts):
        raise ValueError(f"Go versionを解釈できません: {value!r}")
    numbers = [int(part) for part in parts]
    if len(numbers) == 2:
        numbers.append(0)
    return numbers[0], numbers[1], numbers[2]


def read_required_go_version(path: Path = GO_MOD) -> str:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise ValueError(f"go.modを読めません: {exc}") from exc

    for line in lines:
        fields = line.strip().split()
        if len(fields) == 2 and fields[0] == "go":
            parse_go_version(fields[1])
            return fields[1]
    raise ValueError("go.modにGo directiveがありません")


def controlled_environment(source: dict[str, str] | None = None) -> dict[str, str]:
    environment = dict(os.environ if source is None else source)
    environment["GOWORK"] = "off"
    environment["GOENV"] = "off"
    environment["GOTOOLCHAIN"] = "local"
    for key in (
        "GOFLAGS",
        "GOOS",
        "GOARCH",
        "GOAMD64",
        "GOEXPERIMENT",
        "CGO_ENABLED",
    ):
        environment.pop(key, None)
    return environment


def evaluate_go_version(required: str, output: str) -> dict[str, object]:
    fields = output.strip().split()
    if len(fields) < 3 or fields[0:2] != ["go", "version"]:
        raise ValueError(f"go version出力を解釈できません: {output.strip()!r}")

    observed_token = fields[2]
    observed = parse_go_version(observed_token)
    required_tuple = parse_go_version(required)
    passed = observed >= required_tuple
    return {
        "required": required,
        "observed": observed_token,
        "result": "ok" if passed else "failed",
        "automaticToolchainSwitching": False,
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


def run_preflight(
    *,
    runner: Callable[..., subprocess.CompletedProcess[str]] = _default_runner,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
) -> tuple[int, dict[str, object]]:
    required = read_required_go_version()
    try:
        completed = runner(
            ("go", "version"),
            cwd=GO_RUNTIME_DIR,
            env=controlled_environment(),
            timeout=timeout_seconds,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 1, {
            "required": required,
            "result": "failed",
            "automaticToolchainSwitching": False,
            "error": str(exc),
        }

    if completed.returncode != 0:
        return 1, {
            "required": required,
            "result": "failed",
            "automaticToolchainSwitching": False,
            "commandExitCode": completed.returncode,
        }

    try:
        result = evaluate_go_version(required, completed.stdout)
    except ValueError as exc:
        return 1, {
            "required": required,
            "result": "failed",
            "automaticToolchainSwitching": False,
            "error": str(exc),
        }
    return (0 if result["result"] == "ok" else 1), result


def main() -> int:
    exit_code, result = run_preflight()
    print("Go toolchain preflight")
    print(f"- required: >= {result['required']}")
    print(f"- observed: {result.get('observed', '<unavailable>')}")
    print(f"- result: {result['result']}")
    print("- GOTOOLCHAIN: local")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
