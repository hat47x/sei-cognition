#!/usr/bin/env python3
"""Run repository-local ISSUE-000078 E78.6 focused mechanics checks.

This runner verifies evaluation mechanics only. A PASS does not establish
human review, actual long-gap comparison, Product Value, or Stable Requirement
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
PROBE = (
    "evaluation/personal-inquiry-decision/"
    "inquiry_continuity_assistance_probe.py"
)
PROBE_SET = (
    "evaluation/personal-inquiry-decision/"
    "inquiry_continuity_assistance_probe_v1.json"
)
EVIDENCE_TOOL = (
    "evaluation/personal-inquiry-decision/"
    "inquiry_continuity_assistance_evidence.py"
)
RESULT_SCHEMA = "sei.inquiry-continuity-assistance-local-check-result/v1"
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
    "test_inquiry_continuity_assistance_probe.py",
    "evaluation/personal-inquiry-decision/"
    "test_inquiry_continuity_assistance_evidence.py",
    "evaluation/personal-inquiry-decision/"
    "run_inquiry_continuity_assistance_checks.py",
    "evaluation/personal-inquiry-decision/"
    "test_run_inquiry_continuity_assistance_checks.py",
)
STOP_LINE = (
    "E78.6 local checks PASS != human review result "
    "!= actual long-gap comparison != Product Value decision "
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


def _read_json(path: Path, label: str) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot load {label}: {path}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    return value


def build_contract_snapshot(
    repo_root: str | Path = SEI_ROOT,
) -> dict[str, object]:
    root = Path(repo_root)
    probe_path = root / PROBE_SET
    probe = _read_json(probe_path, "canonical E78.6 probe")

    probe_id = probe.get("probe_id")
    probe_schema = probe.get("schema")
    if not isinstance(probe_id, str) or not probe_id:
        raise ValueError("canonical E78.6 probe_id must be non-empty")
    if probe_schema != "sei.inquiry-continuity-assistance-probe/v2":
        raise ValueError(
            "canonical E78.6 probe schema must be "
            "sei.inquiry-continuity-assistance-probe/v2"
        )

    mechanics_files: list[dict[str, str]] = []
    for relative in MECHANICS_PATHS:
        path = root / relative
        try:
            payload = path.read_bytes()
        except OSError as exc:
            raise ValueError(
                f"cannot read E78.6 mechanics file: {relative}"
            ) from exc
        mechanics_files.append(
            {
                "path": relative,
                "sha256": _sha256_bytes(payload),
            }
        )

    source_set = probe.get("source_set")
    if not isinstance(source_set, dict) or set(source_set) != {
        "path",
        "blob_sha1",
    }:
        raise ValueError("canonical E78.6 source_set has invalid shape")
    source_set_path = source_set["path"]
    expected_source_set_blob = source_set["blob_sha1"]
    if (
        not isinstance(source_set_path, str)
        or not source_set_path
        or not _is_lower_hex(expected_source_set_blob, 40)
    ):
        raise ValueError("canonical E78.6 source_set binding is invalid")
    _validate_relative_path(
        source_set_path,
        "canonical E78.6 source_set.path",
    )

    source_manifest_path = root / source_set_path
    try:
        source_manifest_raw = source_manifest_path.read_bytes()
    except OSError as exc:
        raise ValueError(
            f"cannot read E78.6 source-set manifest: {source_set_path}"
        ) from exc
    actual_source_set_blob = _git_blob_sha1(source_manifest_raw)
    if actual_source_set_blob != expected_source_set_blob:
        raise ValueError(
            "E78.6 source-set manifest blob mismatch: "
            f"expected {expected_source_set_blob}, "
            f"got {actual_source_set_blob}"
        )
    try:
        manifest = json.loads(source_manifest_raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(
            "E78.6 source-set manifest must be UTF-8 JSON"
        ) from exc
    if (
        not isinstance(manifest, dict)
        or manifest.get("schema")
        != "sei.inquiry-continuity-matched-set/v0"
        or manifest.get("status") != "evaluation-only"
        or manifest.get("issue") != "ISSUE-000078"
    ):
        raise ValueError(
            "E78.6 source-set manifest has invalid identity"
        )
    manifest_fixtures = manifest.get("fixtures")
    if not isinstance(manifest_fixtures, list):
        raise ValueError(
            "E78.6 source-set manifest fixtures must be a list"
        )

    cases = probe.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("canonical E78.6 probe must contain cases")
    probe_pairs: list[tuple[str, str]] = []
    source_fixtures: list[dict[str, str]] = []
    seen_fixture_ids: set[str] = set()
    for case in cases:
        if not isinstance(case, dict):
            raise ValueError("E78.6 probe case must be an object")
        fixture_id = case.get("fixture_id")
        path_text = case.get("path")
        expected_blob = case.get("blob_sha1")
        if (
            not isinstance(fixture_id, str)
            or not fixture_id
            or fixture_id in seen_fixture_ids
            or not isinstance(path_text, str)
            or not path_text
            or not _is_lower_hex(expected_blob, 40)
        ):
            raise ValueError(
                "E78.6 probe case has invalid source binding"
            )
        _validate_relative_path(
            path_text,
            "E78.6 source fixture path",
        )
        seen_fixture_ids.add(fixture_id)
        probe_pairs.append((fixture_id, path_text))
        path = root / path_text
        try:
            payload = path.read_bytes()
        except OSError as exc:
            raise ValueError(
                f"cannot read E78.6 source fixture: {path_text}"
            ) from exc
        actual_blob = _git_blob_sha1(payload)
        if actual_blob != expected_blob:
            raise ValueError(
                f"E78.6 source fixture blob mismatch: {fixture_id}: "
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

    manifest_pairs = [
        (item.get("id"), item.get("path"))
        for item in manifest_fixtures
        if isinstance(item, dict)
    ]
    if manifest_pairs != probe_pairs:
        raise ValueError(
            "E78.6 source-set manifest fixture identity/path "
            "differs from probe"
        )
    if tuple(item["fixtureId"] for item in source_fixtures) != FIXTURE_IDS:
        raise ValueError(
            "E78.6 probe fixture ordering/identity differs from "
            "runner contract"
        )

    return {
        "probeId": probe_id,
        "probeSchema": probe_schema,
        "probeContentSha256": _canonical_json_sha256(probe),
        "mechanicsFiles": mechanics_files,
        "sourceSet": {
            "path": source_set_path,
            "expectedBlobSha1": expected_source_set_blob,
            "actualBlobSha1": actual_source_set_blob,
        },
        "sourceFixtures": source_fixtures,
        "python": {
            "implementation": sys.implementation.name,
            "version": platform.python_version(),
        },
    }


def configured_checks() -> tuple[Check, ...]:
    python = sys.executable
    return (
        Check(
            name="assistance-probe-tests",
            command=(
                python,
                "evaluation/personal-inquiry-decision/"
                "test_inquiry_continuity_assistance_probe.py",
            ),
            cwd=SEI_ROOT,
        ),
        Check(
            name="assistance-evidence-tests",
            command=(
                python,
                "evaluation/personal-inquiry-decision/"
                "test_inquiry_continuity_assistance_evidence.py",
            ),
            cwd=SEI_ROOT,
        ),
        Check(
            name="assistance-local-runner-tests",
            command=(
                python,
                "evaluation/personal-inquiry-decision/"
                "test_run_inquiry_continuity_assistance_checks.py",
            ),
            cwd=SEI_ROOT,
        ),
        Check(
            name="assistance-probe-validate",
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
    )


def sanitized_environment(
    source: dict[str, str] | None = None,
) -> dict[str, str]:
    environment = dict(os.environ if source is None else source)
    for key in tuple(environment):
        if key.startswith(("SEI_", "SOZA_", "KJ_ATLAS_")):
            environment.pop(key, None)
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
        environment.pop(key, None)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONNOUSERSITE"] = "1"
    return environment


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
                    "local check command contains an absolute path "
                    "outside the repository"
                ) from exc
            portable.append(relative.as_posix())
            continue
        portable.append(token)
    return portable


def validate_checks(checks: Sequence[Check]) -> None:
    if not checks:
        raise ValueError("at least one local check is required")
    names: set[str] = set()
    for check in checks:
        if check.name in names:
            raise ValueError(
                f"duplicate local check name: {check.name}"
            )
        names.add(check.name)
        if not check.command:
            raise ValueError(
                f"local check command is empty: {check.name}"
            )
        if not check.cwd.is_dir():
            raise ValueError(
                f"local check cwd does not exist: "
                f"{check.name}: {check.cwd}"
            )
        _repo_relative_cwd(check.cwd)
        _portable_command(check.command)


def _stream_evidence(
    value: str | bytes | None,
) -> dict[str, object]:
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


def build_result(
    checks: Sequence[Check],
    executions: Sequence[dict[str, object]],
    *,
    stopped_early: bool,
    contract_snapshot: dict[str, object],
) -> dict[str, object]:
    validate_checks(checks)
    failed = [
        item
        for item in executions
        if item["exitCode"] != 0
    ]
    complete = len(executions) == len(checks)
    return {
        "schema": RESULT_SCHEMA,
        "result": (
            "ok"
            if complete and not failed
            else "failed"
        ),
        "selected": [check.name for check in checks],
        "selectedCount": len(checks),
        "executed": list(executions),
        "executedCount": len(executions),
        "failedCount": len(failed),
        "stoppedEarly": stopped_early,
        "contractSnapshot": contract_snapshot,
        "humanReviewObserved": False,
        "actualLongGapComparisonEstablished": False,
        "productValueEstablished": False,
        "stableRequirementAuthorized": False,
        "stopLine": STOP_LINE,
    }


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
    contract_snapshot = snapshot_builder()
    environment = sanitized_environment()
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
                env=environment,
                timeout=timeout_seconds,
            )
            execution: dict[str, object] = {
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
            execution = {
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
            execution = {
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
    return (
        0 if result["result"] == "ok" else 1,
        result,
    )


def _is_lower_hex(value: object, length: int) -> bool:
    return (
        isinstance(value, str)
        and len(value) == length
        and all(
            character in "0123456789abcdef"
            for character in value
        )
    )


def _validate_relative_path(
    value: object,
    field: str,
) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(
            f"{field} must be a non-empty string"
        )
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(
            f"{field} must stay relative to the repository"
        )
    return value


def _validate_stream_evidence(
    value: object,
    field: str,
) -> None:
    if (
        not isinstance(value, dict)
        or set(value) != {"sha256", "bytes"}
    ):
        raise ValueError(
            f"{field} must contain sha256/bytes exactly"
        )
    if not _is_lower_hex(value["sha256"], 64):
        raise ValueError(
            f"{field}.sha256 must be lowercase SHA-256"
        )
    byte_count = value["bytes"]
    if (
        isinstance(byte_count, bool)
        or not isinstance(byte_count, int)
        or byte_count < 0
    ):
        raise ValueError(
            f"{field}.bytes must be a nonnegative integer"
        )


def validate_result(result: dict[str, object]) -> None:
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
        "actualLongGapComparisonEstablished",
        "productValueEstablished",
        "stableRequirementAuthorized",
        "stopLine",
    }
    if not isinstance(result, dict) or set(result) != required:
        raise ValueError(
            "E78.6 local-check result has invalid top-level shape"
        )
    if result["schema"] != RESULT_SCHEMA:
        raise ValueError(
            f"E78.6 local-check result schema must be "
            f"{RESULT_SCHEMA}"
        )
    if result["result"] not in {"ok", "failed"}:
        raise ValueError(
            "E78.6 local-check result must be ok or failed"
        )

    selected = result["selected"]
    if (
        not isinstance(selected, list)
        or not selected
        or any(
            not isinstance(name, str) or not name
            for name in selected
        )
        or len(selected) != len(set(selected))
    ):
        raise ValueError(
            "selected checks must be unique non-empty strings"
        )
    if result["selectedCount"] != len(selected):
        raise ValueError("selectedCount mismatch")

    executed = result["executed"]
    if not isinstance(executed, list):
        raise ValueError("executed must be a list")
    if result["executedCount"] != len(executed):
        raise ValueError("executedCount mismatch")
    if len(executed) > len(selected):
        raise ValueError(
            "executed checks exceed selected checks"
        )
    if [
        item.get("name")
        for item in executed
        if isinstance(item, dict)
    ] != selected[: len(executed)]:
        raise ValueError(
            "executed checks must match selected order"
        )

    failed_count = 0
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
        if not isinstance(item, dict):
            raise ValueError(
                "executed entry must be an object"
            )
        keys = set(item)
        if (
            keys != base_keys
            and keys != base_keys | {"launchError"}
        ):
            raise ValueError(
                "executed entry has invalid shape"
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
                "executed command must contain non-empty strings"
            )
        for token in command:
            if token == "<python>":
                continue
            token_path = Path(token)
            if (
                token_path.is_absolute()
                or ".." in token_path.parts
            ):
                raise ValueError(
                    "executed command must not contain "
                    "host-escaping paths"
                )
        _validate_relative_path(
            item["cwdRelativeToRepo"],
            "cwdRelativeToRepo",
        )
        if (
            isinstance(item["exitCode"], bool)
            or not isinstance(item["exitCode"], int)
        ):
            raise ValueError("exitCode must be an integer")
        if not isinstance(item["timedOut"], bool):
            raise ValueError("timedOut must be boolean")
        timeout_seconds = item["timeoutSeconds"]
        if (
            isinstance(timeout_seconds, bool)
            or not isinstance(timeout_seconds, int)
            or timeout_seconds <= 0
        ):
            raise ValueError(
                "timeoutSeconds must be a positive integer"
            )
        _validate_stream_evidence(
            item["stdout"],
            "stdout",
        )
        _validate_stream_evidence(
            item["stderr"],
            "stderr",
        )
        if "launchError" in item:
            launch_error = item["launchError"]
            if (
                not isinstance(launch_error, dict)
                or set(launch_error) != {"type", "errno"}
                or not isinstance(
                    launch_error["type"],
                    str,
                )
                or not launch_error["type"]
                or (
                    launch_error["errno"] is not None
                    and (
                        isinstance(
                            launch_error["errno"],
                            bool,
                        )
                        or not isinstance(
                            launch_error["errno"],
                            int,
                        )
                    )
                )
            ):
                raise ValueError(
                    "launchError must contain sanitized type/errno"
                )
        if item["exitCode"] != 0:
            failed_count += 1

    if result["failedCount"] != failed_count:
        raise ValueError("failedCount mismatch")
    complete = len(executed) == len(selected)
    expected = (
        "ok"
        if complete and failed_count == 0
        else "failed"
    )
    if result["result"] != expected:
        raise ValueError(
            "result status is inconsistent with executed checks"
        )
    if not isinstance(result["stoppedEarly"], bool):
        raise ValueError("stoppedEarly must be boolean")
    if result["stoppedEarly"] and complete:
        raise ValueError(
            "stoppedEarly cannot be true for a complete run"
        )

    snapshot = result["contractSnapshot"]
    if not isinstance(snapshot, dict) or set(snapshot) != {
        "probeId",
        "probeSchema",
        "probeContentSha256",
        "mechanicsFiles",
        "sourceSet",
        "sourceFixtures",
        "python",
    }:
        raise ValueError(
            "contractSnapshot has invalid shape"
        )
    if (
        not isinstance(snapshot["probeId"], str)
        or not snapshot["probeId"]
        or snapshot["probeSchema"]
        != "sei.inquiry-continuity-assistance-probe/v2"
        or not _is_lower_hex(
            snapshot["probeContentSha256"],
            64,
        )
    ):
        raise ValueError(
            "contractSnapshot probe identity is invalid"
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
            "mechanics file paths differ from runner contract"
        )
    for item in mechanics:
        if (
            not isinstance(item, dict)
            or set(item) != {"path", "sha256"}
        ):
            raise ValueError(
                "mechanics file entry has invalid shape"
            )
        _validate_relative_path(
            item["path"],
            "mechanics file path",
        )
        if not _is_lower_hex(item["sha256"], 64):
            raise ValueError(
                "mechanics file sha256 must be lowercase SHA-256"
            )

    source_set = snapshot["sourceSet"]
    if (
        not isinstance(source_set, dict)
        or set(source_set) != {
            "path",
            "expectedBlobSha1",
            "actualBlobSha1",
        }
    ):
        raise ValueError(
            "sourceSet snapshot has invalid shape"
        )
    _validate_relative_path(
        source_set["path"],
        "sourceSet.path",
    )
    for field in (
        "expectedBlobSha1",
        "actualBlobSha1",
    ):
        if not _is_lower_hex(source_set[field], 40):
            raise ValueError(
                f"sourceSet.{field} must be Git blob SHA-1"
            )
    if (
        source_set["expectedBlobSha1"]
        != source_set["actualBlobSha1"]
    ):
        raise ValueError(
            "sourceSet expected/actual blob SHA-1 mismatch"
        )

    sources = snapshot["sourceFixtures"]
    if (
        not isinstance(sources, list)
        or tuple(
            item.get("fixtureId")
            if isinstance(item, dict)
            else None
            for item in sources
        )
        != FIXTURE_IDS
    ):
        raise ValueError(
            "source fixture ids differ from runner contract"
        )
    for item in sources:
        if (
            not isinstance(item, dict)
            or set(item) != {
                "fixtureId",
                "path",
                "expectedBlobSha1",
                "actualBlobSha1",
            }
        ):
            raise ValueError(
                "source fixture entry has invalid shape"
            )
        _validate_relative_path(
            item["path"],
            "source fixture path",
        )
        for field in (
            "expectedBlobSha1",
            "actualBlobSha1",
        ):
            if not _is_lower_hex(item[field], 40):
                raise ValueError(
                    f"{field} must be Git blob SHA-1"
                )
        if (
            item["expectedBlobSha1"]
            != item["actualBlobSha1"]
        ):
            raise ValueError(
                "source fixture expected/actual blob mismatch"
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
            "contractSnapshot.python has invalid shape"
        )

    for field in (
        "humanReviewObserved",
        "actualLongGapComparisonEstablished",
        "productValueEstablished",
        "stableRequirementAuthorized",
    ):
        if result[field] is not False:
            raise ValueError(
                f"{field} must remain false for local mechanics evidence"
            )
    if result["stopLine"] != STOP_LINE:
        raise ValueError(
            "local mechanics stop line mismatch"
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
            "refusing to overwrite existing E78.6 "
            f"local-check result: {target}"
        ) from exc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run repository-local ISSUE-000078 "
            "E78.6 evaluation-mechanics checks."
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
        help=(
            "stop after the first failed, timed-out, "
            "or unlaunchable check"
        ),
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=DEFAULT_TIMEOUT_SECONDS,
        help=(
            "per-check timeout; default "
            f"{DEFAULT_TIMEOUT_SECONDS}s"
        ),
    )
    parser.add_argument(
        "--result-output",
        type=Path,
        help=(
            "exclusive-create path for local-check result JSON"
        ),
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
        parser.exit(
            2,
            f"E78.6 local checks: {exc}\n",
        )

    if args.list:
        for check in checks:
            print(
                f"- {check.name}: {' '.join(check.command)}"
            )
        print(f"- stop line: {STOP_LINE}")
        return 0

    try:
        exit_code, result = run_checks(
            checks,
            timeout_seconds=args.timeout_seconds,
            stop_on_failure=args.stop_on_failure,
        )
    except ValueError as exc:
        parser.exit(
            2,
            f"E78.6 local checks: {exc}\n",
        )

    print("E78.6 local check summary")
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
            save_result(
                args.result_output,
                result,
            )
        except ValueError as exc:
            parser.exit(2, f"{exc}\n")
        print(
            "- result output: "
            f"{args.result_output.expanduser()}"
        )

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
