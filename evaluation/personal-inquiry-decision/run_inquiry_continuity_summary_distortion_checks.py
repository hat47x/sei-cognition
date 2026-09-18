#!/usr/bin/env python3
"""Run repository-local ISSUE-000078 E78.3 focused checks.

This runner verifies the evaluation mechanics only. A PASS does not establish
human review, actual long-gap resumption, Product Value, or Stable Requirement
authorization.
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
PROBE = "evaluation/personal-inquiry-decision/inquiry_continuity_summary_distortion_probe.py"
PROBE_SET = (
    "evaluation/personal-inquiry-decision/"
    "inquiry_continuity_summary_distortion_probe_v1.json"
)
EVIDENCE_TOOL = (
    "evaluation/personal-inquiry-decision/"
    "inquiry_continuity_summary_distortion_evidence.py"
)
RESULT_SCHEMA = "sei.inquiry-continuity-summary-distortion-local-check-result/v2"
DEFAULT_TIMEOUT_SECONDS = 120
TIMEOUT_EXIT_CODE = 124
LAUNCH_ERROR_EXIT_CODE = 127
FIXTURE_IDS = (
    "e78-counterfactual-001-nightly-batch",
    "e78-counterfactual-002-support-response",
    "e78-counterfactual-003-import-duplicates",
)
MECHANICS_PATHS = (
    PROBE_SET,
    PROBE,
    EVIDENCE_TOOL,
    "evaluation/personal-inquiry-decision/"
    "test_inquiry_continuity_summary_distortion_probe.py",
    "evaluation/personal-inquiry-decision/"
    "test_inquiry_continuity_summary_distortion_evidence.py",
    "evaluation/personal-inquiry-decision/"
    "run_inquiry_continuity_summary_distortion_checks.py",
    "evaluation/personal-inquiry-decision/"
    "test_run_inquiry_continuity_summary_distortion_checks.py",
)
STOP_LINE = (
    "E78.3 local checks PASS != human review result "
    "!= actual long-gap Evidence != Product Value decision "
    "!= Stable Requirement authorization"
)


@dataclass(frozen=True)
class Check:
    name: str
    command: tuple[str, ...]
    cwd: Path


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _git_blob_sha1(payload: bytes) -> str:
    header = f"blob {len(payload)}\0".encode("ascii")
    return hashlib.sha1(header + payload).hexdigest()


def _canonical_json_sha256(value: object) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return _sha256_bytes(payload)


def build_contract_snapshot(repo_root: str | Path = SEI_ROOT) -> dict[str, object]:
    root = Path(repo_root)
    probe_path = root / PROBE_SET
    try:
        probe = json.loads(probe_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot load canonical E78.3 probe: {probe_path}") from exc
    if not isinstance(probe, dict):
        raise ValueError("canonical E78.3 probe must be a JSON object")

    mechanics_files: list[dict[str, str]] = []
    for relative in MECHANICS_PATHS:
        path = root / relative
        try:
            payload = path.read_bytes()
        except OSError as exc:
            raise ValueError(f"cannot read E78.3 mechanics file: {relative}") from exc
        mechanics_files.append(
            {
                "path": relative,
                "sha256": _sha256_bytes(payload),
            }
        )

    cases = probe.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("canonical E78.3 probe must contain cases")
    source_fixtures: list[dict[str, str]] = []
    seen_fixture_ids: set[str] = set()
    for case in cases:
        if not isinstance(case, dict):
            raise ValueError("E78.3 probe case must be an object")
        fixture_id = case.get("fixture_id")
        path_text = case.get("path")
        expected_blob = case.get("blob_sha1")
        if (
            not isinstance(fixture_id, str)
            or not fixture_id
            or fixture_id in seen_fixture_ids
            or not isinstance(path_text, str)
            or not path_text
            or not isinstance(expected_blob, str)
            or len(expected_blob) != 40
        ):
            raise ValueError("E78.3 probe case has invalid source binding")
        seen_fixture_ids.add(fixture_id)
        path = root / path_text
        try:
            payload = path.read_bytes()
        except OSError as exc:
            raise ValueError(
                f"cannot read E78.3 source fixture: {path_text}"
            ) from exc
        actual_blob = _git_blob_sha1(payload)
        if actual_blob != expected_blob:
            raise ValueError(
                f"E78.3 source fixture blob mismatch: {fixture_id}: "
                f"expected {expected_blob}, got {actual_blob}"
            )
        source_fixtures.append(
            {
                "fixtureId": fixture_id,
                "path": path_text,
                "expectedBlobSha1": expected_blob,
                "actualBlobSha1": actual_blob,
            }
        )

    if tuple(item["fixtureId"] for item in source_fixtures) != FIXTURE_IDS:
        raise ValueError(
            "E78.3 probe fixture ordering/identity differs from runner contract"
        )

    probe_id = probe.get("probe_id")
    probe_schema = probe.get("schema")
    if not isinstance(probe_id, str) or not probe_id:
        raise ValueError("canonical E78.3 probe_id must be non-empty")
    if not isinstance(probe_schema, str) or not probe_schema:
        raise ValueError("canonical E78.3 probe schema must be non-empty")

    return {
        "probeId": probe_id,
        "probeSchema": probe_schema,
        "probeContentSha256": _canonical_json_sha256(probe),
        "mechanicsFiles": mechanics_files,
        "sourceFixtures": source_fixtures,
        "python": {
            "implementation": sys.implementation.name,
            "version": platform.python_version(),
        },
    }


def configured_checks() -> tuple[Check, ...]:
    python = sys.executable
    checks: list[Check] = [
        Check(
            name="summary-distortion-probe-tests",
            command=(
                python,
                "evaluation/personal-inquiry-decision/"
                "test_inquiry_continuity_summary_distortion_probe.py",
            ),
            cwd=SEI_ROOT,
        ),
        Check(
            name="summary-distortion-evidence-tests",
            command=(
                python,
                "evaluation/personal-inquiry-decision/"
                "test_inquiry_continuity_summary_distortion_evidence.py",
            ),
            cwd=SEI_ROOT,
        ),
        Check(
            name="summary-distortion-local-runner-tests",
            command=(
                python,
                "evaluation/personal-inquiry-decision/"
                "test_run_inquiry_continuity_summary_distortion_checks.py",
            ),
            cwd=SEI_ROOT,
        ),
        Check(
            name="summary-distortion-probe-validate",
            command=(
                python,
                PROBE,
                "--probe",
                PROBE_SET,
                "--repo-root",
                ".",
                "validate",
            ),
            cwd=SEI_ROOT,
        ),
    ]
    for fixture_id in FIXTURE_IDS:
        checks.append(
            Check(
                name=f"summary-distortion-preflight-{fixture_id}",
                command=(
                    python,
                    EVIDENCE_TOOL,
                    "--probe",
                    PROBE_SET,
                    "--repo-root",
                    ".",
                    "--fixture-id",
                    fixture_id,
                    "preflight",
                ),
                cwd=SEI_ROOT,
            )
        )
    return tuple(checks)


def sanitized_environment(source: dict[str, str] | None = None) -> dict[str, str]:
    environment = dict(os.environ if source is None else source)
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
    if not checks:
        raise ValueError("at least one local check is required")
    names: set[str] = set()
    for check in checks:
        if check.name in names:
            raise ValueError(f"duplicate local check name: {check.name}")
        names.add(check.name)
        if not check.command:
            raise ValueError(f"local check command is empty: {check.name}")
        if not check.cwd.is_dir():
            raise ValueError(
                f"local check cwd does not exist: {check.name}: {check.cwd}"
            )
        _repo_relative_cwd(check.cwd)
        _portable_command(check.command)


def build_result(
    checks: Sequence[Check],
    executions: Sequence[dict[str, object]],
    *,
    stopped_early: bool,
    contract_snapshot: dict[str, object],
) -> dict[str, object]:
    validate_checks(checks)
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
        "contractSnapshot": contract_snapshot,
        "humanReviewObserved": False,
        "actualLongGapResumptionEstablished": False,
        "productValueEstablished": False,
        "stableRequirementAuthorized": False,
        "stopLine": STOP_LINE,
    }


def _stream_evidence(value: str | bytes | None) -> dict[str, object]:
    if value is None:
        payload = b""
    elif isinstance(value, bytes):
        payload = value
    else:
        payload = value.encode("utf-8")
    return {
        "sha256": _sha256_bytes(payload),
        "bytes": len(payload),
    }


def _repo_relative_cwd(cwd: Path) -> str:
    try:
        relative = cwd.resolve().relative_to(SEI_ROOT.resolve())
    except ValueError as exc:
        raise ValueError(
            "local check cwd escapes repository root"
        ) from exc
    return "." if relative == Path(".") else relative.as_posix()


def _portable_command(command: Sequence[str]) -> list[str]:
    portable: list[str] = []
    repo_root = SEI_ROOT.resolve()
    python_path = Path(sys.executable).resolve()
    for token in command:
        path = Path(token)
        if path.is_absolute():
            resolved = path.resolve()
            if resolved == python_path:
                portable.append("<python>")
                continue
            try:
                relative = resolved.relative_to(repo_root)
            except ValueError as exc:
                raise ValueError(
                    "local check command contains an absolute path outside "
                    "the repository"
                ) from exc
            portable.append(relative.as_posix())
            continue
        portable.append(token)
    return portable


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
        check=False,
        timeout=timeout,
        text=True,
        capture_output=True,
    )


def run_checks(
    checks: Sequence[Check],
    *,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    stop_on_failure: bool = False,
    runner: Callable[..., subprocess.CompletedProcess[str]] = _default_runner,
    snapshot_builder: Callable[[], dict[str, object]] = build_contract_snapshot,
) -> tuple[int, dict[str, object]]:
    validate_checks(checks)
    contract_snapshot = snapshot_builder()
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
                "command": _portable_command(check.command),
                "cwdRelativeToRepo": _repo_relative_cwd(check.cwd),
                "exitCode": completed.returncode,
                "timedOut": False,
                "timeoutSeconds": timeout_seconds,
                "stdout": _stream_evidence(completed.stdout),
                "stderr": _stream_evidence(completed.stderr),
            }
        except subprocess.TimeoutExpired as exc:
            execution = {
                "name": check.name,
                "command": _portable_command(check.command),
                "cwdRelativeToRepo": _repo_relative_cwd(check.cwd),
                "exitCode": TIMEOUT_EXIT_CODE,
                "timedOut": True,
                "timeoutSeconds": timeout_seconds,
                "stdout": _stream_evidence(exc.stdout),
                "stderr": _stream_evidence(exc.stderr),
            }
        except OSError as exc:
            execution = {
                "name": check.name,
                "command": _portable_command(check.command),
                "cwdRelativeToRepo": _repo_relative_cwd(check.cwd),
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

        executions.append(execution)
        if execution["exitCode"] != 0 and stop_on_failure:
            stopped_early = index < len(checks)
            break

    result = build_result(
        checks,
        executions,
        stopped_early=stopped_early,
        contract_snapshot=contract_snapshot,
    )
    return (0 if result["result"] == "ok" else 1), result


def save_result(path: str | Path, result: dict[str, object]) -> None:
    target = Path(path).expanduser()
    payload = json.dumps(
        result,
        ensure_ascii=False,
        sort_keys=True,
        indent=2,
    ) + "\n"
    try:
        with target.open("x", encoding="utf-8") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError as exc:
        raise ValueError(
            f"refusing to overwrite existing E78.3 local-check result: {target}"
        ) from exc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run repository-local ISSUE-000078 E78.3 evaluation-mechanics checks."
        ),
        allow_abbrev=False,
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="list configured checks and exit",
    )
    parser.add_argument(
        "--stop-on-failure",
        action="store_true",
        help="stop after the first failed, timed-out, or unlaunchable check",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=DEFAULT_TIMEOUT_SECONDS,
        help=f"per-check timeout; default {DEFAULT_TIMEOUT_SECONDS}s",
    )
    parser.add_argument(
        "--result-output",
        type=Path,
        help="exclusive-create path for the local-check result JSON",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.timeout_seconds <= 0:
        parser.error("--timeout-seconds must be >= 1")

    checks = configured_checks()
    try:
        validate_checks(checks)
    except ValueError as exc:
        parser.exit(2, f"E78.3 local checks: {exc}\n")

    if args.list:
        for check in checks:
            print(f"- {check.name}: {' '.join(check.command)}")
        print(f"- stop line: {STOP_LINE}")
        return 0

    try:
        exit_code, result = run_checks(
            checks,
            timeout_seconds=args.timeout_seconds,
            stop_on_failure=args.stop_on_failure,
        )
    except ValueError as exc:
        parser.exit(2, f"E78.3 local checks: {exc}\n")

    print("E78.3 local check summary")
    print(f"- selected: {result['selectedCount']}")
    print(f"- executed: {result['executedCount']}")
    print(f"- failed: {result['failedCount']}")
    print(
        "- probe content sha256: "
        f"{result['contractSnapshot']['probeContentSha256']}"
    )
    print(f"- stop line: {STOP_LINE}")

    if args.result_output is not None:
        try:
            save_result(args.result_output, result)
        except ValueError as exc:
            parser.exit(2, f"{exc}\n")
        print(f"- result output: {args.result_output.expanduser()}")

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
