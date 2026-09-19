#!/usr/bin/env python3
"""Run repository-local ISSUE-000078 E78.7 lifecycle mechanics checks.

PASS verifies mechanics only. It does not establish human review, Product Value,
Universal Inquiry status, or Stable Requirement authorization.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Sequence


EVALUATION_DIR = Path(__file__).resolve().parent
SEI_ROOT = EVALUATION_DIR.parents[1]
PROBE = (
    "evaluation/personal-inquiry-decision/"
    "inquiry_continuity_lifecycle_probe.py"
)
PROBE_SET = (
    "evaluation/personal-inquiry-decision/"
    "inquiry_continuity_lifecycle_probe_v1.json"
)
EVIDENCE_TOOL = (
    "evaluation/personal-inquiry-decision/"
    "inquiry_continuity_lifecycle_evidence.py"
)
RESULT_SCHEMA = "sei.inquiry-continuity-lifecycle-local-check-result/v1"
DEFAULT_TIMEOUT_SECONDS = 120
TIMEOUT_EXIT_CODE = 124
LAUNCH_ERROR_EXIT_CODE = 127
MECHANICS_PATHS = (
    PROBE_SET,
    PROBE,
    EVIDENCE_TOOL,
    "evaluation/personal-inquiry-decision/"
    "test_inquiry_continuity_lifecycle_probe.py",
    "evaluation/personal-inquiry-decision/"
    "test_inquiry_continuity_lifecycle_evidence.py",
    "evaluation/personal-inquiry-decision/"
    "run_inquiry_continuity_lifecycle_checks.py",
    "evaluation/personal-inquiry-decision/"
    "test_run_inquiry_continuity_lifecycle_checks.py",
)
STOP_LINE = (
    "E78.7 local checks PASS != human review result "
    "!= Product Value decision != Universal status authorization "
    "!= Stable Requirement authorization"
)


@dataclass(frozen=True)
class Check:
    name: str
    command: tuple[str, ...]
    cwd: Path


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _canonical_json_sha256(value: object) -> str:
    return _sha256(
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    )


def _read_json(path: Path, label: str) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(
            f"cannot load {label}: {path}"
        ) from exc
    if not isinstance(value, dict):
        raise ValueError(
            f"{label} must be a JSON object"
        )
    return value


def build_contract_snapshot(
    repo_root: str | Path = SEI_ROOT,
) -> dict[str, object]:
    root = Path(repo_root)
    probe = _read_json(
        root / PROBE_SET,
        "canonical E78.7 lifecycle probe",
    )
    if (
        probe.get("schema")
        != "sei.inquiry-continuity-lifecycle-probe/v2"
        or probe.get("status") != "evaluation-only"
        or probe.get("issue") != "ISSUE-000078"
    ):
        raise ValueError(
            "canonical E78.7 probe identity is invalid"
        )
    probe_id = probe.get("probe_id")
    if not isinstance(probe_id, str) or not probe_id:
        raise ValueError(
            "canonical E78.7 probe_id must be non-empty"
        )
    reader_rules = probe.get("reader_assignment_rules")
    if reader_rules != {
        "one_rotation_per_reviewer": True,
        "multi_reader_balance_rotations": True,
        "repeated_rotation_same_reviewer_allowed": False,
        "single_reader_separates_order_from_condition": False,
    }:
        raise ValueError(
            "canonical E78.7 reader-assignment safeguards changed"
        )

    mechanics: list[dict[str, str]] = []
    for relative in MECHANICS_PATHS:
        path = root / relative
        try:
            raw = path.read_bytes()
        except OSError as exc:
            raise ValueError(
                f"cannot read E78.7 mechanics file: {relative}"
            ) from exc
        mechanics.append(
            {
                "path": relative,
                "sha256": _sha256(raw),
            }
        )
    return {
        "probeId": probe_id,
        "probeSchema": probe["schema"],
        "probeContentSha256": _canonical_json_sha256(probe),
        "mechanicsFiles": mechanics,
        "python": {
            "implementation": sys.implementation.name,
            "version": platform.python_version(),
        },
    }


def configured_checks() -> tuple[Check, ...]:
    python = sys.executable
    return (
        Check(
            "lifecycle-probe-tests",
            (
                python,
                "evaluation/personal-inquiry-decision/"
                "test_inquiry_continuity_lifecycle_probe.py",
            ),
            SEI_ROOT,
        ),
        Check(
            "lifecycle-evidence-tests",
            (
                python,
                "evaluation/personal-inquiry-decision/"
                "test_inquiry_continuity_lifecycle_evidence.py",
            ),
            SEI_ROOT,
        ),
        Check(
            "lifecycle-local-runner-tests",
            (
                python,
                "evaluation/personal-inquiry-decision/"
                "test_run_inquiry_continuity_lifecycle_checks.py",
            ),
            SEI_ROOT,
        ),
        Check(
            "lifecycle-probe-validate",
            (
                python,
                PROBE,
                "--probe",
                PROBE_SET,
                "validate",
            ),
            SEI_ROOT,
        ),
    )


def sanitized_environment(
    source: dict[str, str] | None = None,
) -> dict[str, str]:
    env = dict(os.environ if source is None else source)
    for key in tuple(env):
        if key.startswith(("SEI_", "SOZA_", "KJ_ATLAS_")):
            env.pop(key, None)
    for key in (
        "OLLAMA_HOST",
        "OLLAMA_MODELS",
        "OPENAI_API_KEY",
        "OPENROUTER_API_KEY",
        "DEEPSEEK_API_KEY",
        "PYTHONPATH",
        "PYTHONHOME",
        "PYTHONSTARTUP",
        "PYTHONUSERBASE",
    ):
        env.pop(key, None)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONNOUSERSITE"] = "1"
    return env


def _repo_relative_cwd(cwd: Path) -> str:
    try:
        relative = cwd.resolve().relative_to(
            SEI_ROOT.resolve()
        )
    except ValueError as exc:
        raise ValueError(
            "local check cwd escapes repository root"
        ) from exc
    return "." if relative == Path(".") else relative.as_posix()


def _portable_command(
    command: Sequence[str],
) -> list[str]:
    result: list[str] = []
    root = SEI_ROOT.resolve()
    python = Path(sys.executable).resolve()
    for token in command:
        path = Path(token)
        if path.is_absolute():
            resolved = path.resolve()
            if resolved == python:
                result.append("<python>")
                continue
            try:
                relative = resolved.relative_to(root)
            except ValueError as exc:
                raise ValueError(
                    "local check command contains an absolute "
                    "path outside the repository"
                ) from exc
            result.append(relative.as_posix())
        else:
            if ".." in path.parts:
                raise ValueError(
                    "local check command escapes repository root"
                )
            result.append(token)
    return result


def validate_checks(
    checks: Sequence[Check],
) -> None:
    if not checks:
        raise ValueError(
            "at least one local check is required"
        )
    seen: set[str] = set()
    for check in checks:
        if check.name in seen:
            raise ValueError(
                f"duplicate local check name: {check.name}"
            )
        seen.add(check.name)
        if not check.command:
            raise ValueError(
                f"empty local check command: {check.name}"
            )
        if not check.cwd.is_dir():
            raise ValueError(
                f"local check cwd does not exist: {check.cwd}"
            )
        _repo_relative_cwd(check.cwd)
        _portable_command(check.command)


def _stream_evidence(
    value: str | bytes | None,
) -> dict[str, object]:
    if value is None:
        raw = b""
    elif isinstance(value, bytes):
        raw = value
    else:
        raw = value.encode("utf-8")
    return {
        "sha256": _sha256(raw),
        "bytes": len(raw),
    }


def _default_runner(
    command: Sequence[str],
    *,
    cwd: Path,
    env: dict[str, str],
    timeout: int,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(command),
        cwd=cwd,
        env=env,
        timeout=timeout,
        check=False,
        text=True,
        capture_output=True,
    )


def run_checks(
    checks: Sequence[Check],
    *,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    stop_on_failure: bool = False,
    runner: Callable[..., subprocess.CompletedProcess[str]] = _default_runner,
    snapshot_builder: Callable[
        [],
        dict[str, object],
    ] = build_contract_snapshot,
) -> tuple[int, dict[str, object]]:
    validate_checks(checks)
    snapshot = snapshot_builder()
    env = sanitized_environment()
    executions: list[dict[str, object]] = []
    stopped_early = False

    for index, check in enumerate(checks, start=1):
        print(
            f"[{index}/{len(checks)}] {check.name}",
            flush=True,
        )
        try:
            completed = runner(
                check.command,
                cwd=check.cwd,
                env=env,
                timeout=timeout_seconds,
            )
            item: dict[str, object] = {
                "name": check.name,
                "command": _portable_command(check.command),
                "cwdRelativeToRepo": _repo_relative_cwd(
                    check.cwd
                ),
                "exitCode": completed.returncode,
                "timedOut": False,
                "timeoutSeconds": timeout_seconds,
                "stdout": _stream_evidence(
                    completed.stdout
                ),
                "stderr": _stream_evidence(
                    completed.stderr
                ),
            }
        except subprocess.TimeoutExpired as exc:
            item = {
                "name": check.name,
                "command": _portable_command(check.command),
                "cwdRelativeToRepo": _repo_relative_cwd(
                    check.cwd
                ),
                "exitCode": TIMEOUT_EXIT_CODE,
                "timedOut": True,
                "timeoutSeconds": timeout_seconds,
                "stdout": _stream_evidence(exc.stdout),
                "stderr": _stream_evidence(exc.stderr),
            }
        except OSError as exc:
            item = {
                "name": check.name,
                "command": _portable_command(check.command),
                "cwdRelativeToRepo": _repo_relative_cwd(
                    check.cwd
                ),
                "exitCode": LAUNCH_ERROR_EXIT_CODE,
                "timedOut": False,
                "timeoutSeconds": timeout_seconds,
                "stdout": _stream_evidence(None),
                "stderr": _stream_evidence(None),
                "launchError": {
                    "type": type(exc).__name__,
                    "errno": exc.errno,
                },
            }
        executions.append(item)
        if item["exitCode"] != 0 and stop_on_failure:
            stopped_early = index < len(checks)
            break

    failed = sum(
        item["exitCode"] != 0
        for item in executions
    )
    complete = len(executions) == len(checks)
    result: dict[str, object] = {
        "schema": RESULT_SCHEMA,
        "result": (
            "ok" if complete and failed == 0 else "failed"
        ),
        "selected": [check.name for check in checks],
        "selectedCount": len(checks),
        "executed": executions,
        "executedCount": len(executions),
        "failedCount": failed,
        "stoppedEarly": stopped_early,
        "contractSnapshot": snapshot,
        "humanReviewObserved": False,
        "productValueEstablished": False,
        "universalStatusAuthorized": False,
        "stableRequirementAuthorized": False,
        "stopLine": STOP_LINE,
    }
    return (
        0 if result["result"] == "ok" else 1,
        result,
    )


def _is_lower_hex(
    value: object,
    length: int,
) -> bool:
    return (
        isinstance(value, str)
        and len(value) == length
        and all(
            character in "0123456789abcdef"
            for character in value
        )
    )


def _validate_stream(
    value: object,
    field: str,
) -> None:
    if (
        not isinstance(value, dict)
        or set(value) != {"sha256", "bytes"}
        or not _is_lower_hex(
            value.get("sha256"),
            64,
        )
        or isinstance(value.get("bytes"), bool)
        or not isinstance(value.get("bytes"), int)
        or value["bytes"] < 0
    ):
        raise ValueError(
            f"{field} stream evidence is invalid"
        )


def validate_result(
    result: dict[str, object],
) -> None:
    required = {
        "schema",
        "result",
        "selected",
        "selectedCount",
        "executed",
        "executedCount",
        "failedCount",
        "stoppedEarly",
        "contractSnapshot",
        "humanReviewObserved",
        "productValueEstablished",
        "universalStatusAuthorized",
        "stableRequirementAuthorized",
        "stopLine",
    }
    if not isinstance(result, dict) or set(result) != required:
        raise ValueError(
            "E78.7 local-check result has invalid shape"
        )
    if (
        result["schema"] != RESULT_SCHEMA
        or result["result"] not in {"ok", "failed"}
    ):
        raise ValueError(
            "E78.7 local-check identity/status is invalid"
        )
    selected = result["selected"]
    executed = result["executed"]
    if (
        not isinstance(selected, list)
        or not selected
        or len(selected) != len(set(selected))
        or any(
            not isinstance(name, str) or not name
            for name in selected
        )
        or result["selectedCount"] != len(selected)
        or not isinstance(executed, list)
        or result["executedCount"] != len(executed)
        or len(executed) > len(selected)
    ):
        raise ValueError(
            "E78.7 selected/executed counts are invalid"
        )
    if [
        item.get("name")
        for item in executed
        if isinstance(item, dict)
    ] != selected[: len(executed)]:
        raise ValueError(
            "E78.7 executed order differs from selection"
        )
    failed = 0
    base_keys = {
        "name",
        "command",
        "cwdRelativeToRepo",
        "exitCode",
        "timedOut",
        "timeoutSeconds",
        "stdout",
        "stderr",
    }
    for item in executed:
        if not isinstance(item, dict) or set(item) not in (
            base_keys,
            base_keys | {"launchError"},
        ):
            raise ValueError(
                "E78.7 execution entry has invalid shape"
            )
        command = item["command"]
        if (
            not isinstance(command, list)
            or not command
            or any(
                not isinstance(token, str) or not token
                for token in command
            )
        ):
            raise ValueError(
                "E78.7 command is invalid"
            )
        for token in command:
            if token == "<python>":
                continue
            path = Path(token)
            if path.is_absolute() or ".." in path.parts:
                raise ValueError(
                    "E78.7 command contains host-escaping path"
                )
        cwd_relative = item["cwdRelativeToRepo"]
        if not isinstance(cwd_relative, str) or not cwd_relative:
            raise ValueError(
                "E78.7 cwdRelativeToRepo is invalid"
            )
        if cwd_relative != ".":
            path = Path(cwd_relative)
            if (
                path.is_absolute()
                or ".." in path.parts
            ):
                raise ValueError(
                    "E78.7 cwdRelativeToRepo is invalid"
                )
        if (
            isinstance(item["exitCode"], bool)
            or not isinstance(item["exitCode"], int)
            or not isinstance(item["timedOut"], bool)
            or isinstance(item["timeoutSeconds"], bool)
            or not isinstance(
                item["timeoutSeconds"],
                int,
            )
            or item["timeoutSeconds"] <= 0
        ):
            raise ValueError(
                "E78.7 execution status is invalid"
            )
        _validate_stream(item["stdout"], "stdout")
        _validate_stream(item["stderr"], "stderr")
        if "launchError" in item:
            launch = item["launchError"]
            if (
                not isinstance(launch, dict)
                or set(launch) != {"type", "errno"}
                or not isinstance(launch["type"], str)
                or not launch["type"]
                or (
                    launch["errno"] is not None
                    and (
                        isinstance(launch["errno"], bool)
                        or not isinstance(launch["errno"], int)
                    )
                )
            ):
                raise ValueError(
                    "E78.7 launchError is invalid"
                )
        if item["exitCode"] != 0:
            failed += 1

    if result["failedCount"] != failed:
        raise ValueError(
            "E78.7 failedCount mismatch"
        )
    complete = len(executed) == len(selected)
    expected = (
        "ok" if complete and failed == 0 else "failed"
    )
    if result["result"] != expected:
        raise ValueError(
            "E78.7 result is inconsistent with executions"
        )
    if (
        not isinstance(result["stoppedEarly"], bool)
        or (
            result["stoppedEarly"]
            and complete
        )
    ):
        raise ValueError(
            "E78.7 stoppedEarly is invalid"
        )

    snapshot = result["contractSnapshot"]
    if not isinstance(snapshot, dict) or set(snapshot) != {
        "probeId",
        "probeSchema",
        "probeContentSha256",
        "mechanicsFiles",
        "python",
    }:
        raise ValueError(
            "E78.7 contractSnapshot has invalid shape"
        )
    if (
        not isinstance(snapshot["probeId"], str)
        or not snapshot["probeId"]
        or snapshot["probeSchema"]
        != "sei.inquiry-continuity-lifecycle-probe/v2"
        or not _is_lower_hex(
            snapshot["probeContentSha256"],
            64,
        )
    ):
        raise ValueError(
            "E78.7 contractSnapshot probe identity is invalid"
        )
    mechanics = snapshot["mechanicsFiles"]
    if (
        not isinstance(mechanics, list)
        or tuple(
            item.get("path")
            if isinstance(item, dict)
            else None
            for item in mechanics
        )
        != MECHANICS_PATHS
    ):
        raise ValueError(
            "E78.7 mechanics paths differ from runner contract"
        )
    for item in mechanics:
        if (
            not isinstance(item, dict)
            or set(item) != {"path", "sha256"}
            or not isinstance(item.get("path"), str)
            or not item["path"]
            or Path(item["path"]).is_absolute()
            or ".." in Path(item["path"]).parts
            or not _is_lower_hex(
                item["sha256"],
                64,
            )
        ):
            raise ValueError(
                "E78.7 mechanics file evidence is invalid"
            )
    runtime = snapshot["python"]
    if (
        not isinstance(runtime, dict)
        or set(runtime) != {"implementation", "version"}
        or not isinstance(runtime["implementation"], str)
        or not runtime["implementation"]
        or not isinstance(runtime["version"], str)
        or not runtime["version"]
    ):
        raise ValueError(
            "E78.7 Python runtime evidence is invalid"
        )

    for field in (
        "humanReviewObserved",
        "productValueEstablished",
        "universalStatusAuthorized",
        "stableRequirementAuthorized",
    ):
        if result[field] is not False:
            raise ValueError(
                f"{field} must remain false for mechanics evidence"
            )
    if result["stopLine"] != STOP_LINE:
        raise ValueError(
            "E78.7 stop line mismatch"
        )


def save_result(
    path: str | Path,
    result: dict[str, object],
) -> None:
    validate_result(result)
    target = Path(path).expanduser()
    payload = (
        json.dumps(
            result,
            ensure_ascii=False,
            sort_keys=True,
            indent=2,
        )
        + "\n"
    )
    try:
        with target.open("x", encoding="utf-8") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError as exc:
        raise ValueError(
            "refusing to overwrite existing E78.7 local-check result: "
            f"{target}"
        ) from exc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run repository-local ISSUE-000078 "
            "E78.7 lifecycle mechanics checks."
        ),
        allow_abbrev=False,
    )
    parser.add_argument(
        "--list",
        action="store_true",
    )
    parser.add_argument(
        "--stop-on-failure",
        action="store_true",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=DEFAULT_TIMEOUT_SECONDS,
    )
    parser.add_argument(
        "--result-output",
        type=Path,
    )
    return parser


def main(
    argv: list[str] | None = None,
) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.timeout_seconds <= 0:
        parser.error(
            "--timeout-seconds must be >= 1"
        )
    checks = configured_checks()
    validate_checks(checks)
    if args.list:
        for check in checks:
            print(
                f"- {check.name}: {' '.join(check.command)}"
            )
        print(f"- stop line: {STOP_LINE}")
        return 0

    exit_code, result = run_checks(
        checks,
        timeout_seconds=args.timeout_seconds,
        stop_on_failure=args.stop_on_failure,
    )
    print("E78.7 local check summary")
    print(f"- selected: {result['selectedCount']}")
    print(f"- executed: {result['executedCount']}")
    print(f"- failed: {result['failedCount']}")
    print(
        "- probe content sha256: "
        f"{result['contractSnapshot']['probeContentSha256']}"
    )
    print(f"- stop line: {STOP_LINE}")
    if args.result_output is not None:
        save_result(
            args.result_output,
            result,
        )
        print(
            f"- result output: {args.result_output.expanduser()}"
        )
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
