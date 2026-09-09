#!/usr/bin/env python3
"""Run deterministic ISSUE-000072 failure probes without external services.

The report is evaluation-only.  It deliberately omits provider-specific status
codes, retry timing and secret material so it cannot be mistaken for a
Universal Contract or an operational retry policy.
"""

from __future__ import annotations

import hashlib
import json
import socket
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Callable

from validate_failure_behavior_case_catalog import validate_catalog

REPORT_SCHEMA = "soza.failure-behavior-probe-report/v1"
CATALOG_PATH = Path(__file__).with_name("case_catalog.json")
TEST_SECRET = "EVALUATION_ONLY_TEST_SECRET"


class SyntheticAdmissionRejected(RuntimeError):
    pass


class SyntheticCredentialRejected(RuntimeError):
    pass


def _attempt(number: int, outcome: str, execution_started: bool, observation: str) -> dict:
    return {
        "attempt": number,
        "outcome": outcome,
        "executionStarted": execution_started,
        "observation": observation,
    }


def _case_result(case_id: str, stage: str, attempts: list[dict], **extra: object) -> dict:
    result = {
        "caseId": case_id,
        "failureStage": stage,
        "attempts": attempts,
        "semanticStateChanged": False,
    }
    result.update(extra)
    return result


def probe_transport_timeout() -> dict:
    left, right = socket.socketpair()
    try:
        left.settimeout(0.01)
        try:
            left.recv(1)
        except TimeoutError:
            return _case_result(
                "FB-C01",
                "reachability-transport",
                [_attempt(1, "failure", False, "transport-timeout")],
            )
    finally:
        left.close()
        right.close()
    raise AssertionError("transport timeout probe unexpectedly completed")


def _synthetic_provider_admission(attempt_number: int) -> str:
    if attempt_number == 1:
        raise SyntheticAdmissionRejected("temporary admission rejection")
    return "accepted"


def probe_provider_admission() -> dict:
    try:
        _synthetic_provider_admission(1)
    except SyntheticAdmissionRejected:
        return _case_result(
            "FB-C02",
            "provider-admission",
            [_attempt(1, "failure", False, "provider-admission-rejected")],
        )
    raise AssertionError("provider admission probe unexpectedly succeeded")


def _synthetic_credential_boundary(supplied: str | None) -> None:
    if supplied != TEST_SECRET:
        raise SyntheticCredentialRejected("credential rejected")


def probe_credential_rejection() -> dict:
    try:
        _synthetic_credential_boundary(None)
    except SyntheticCredentialRejected:
        return _case_result(
            "FB-C03",
            "credential",
            [_attempt(1, "failure", False, "credential-rejected")],
        )
    raise AssertionError("credential probe unexpectedly succeeded")


def probe_artifact_unavailable(workdir: Path) -> dict:
    missing = workdir / "missing-artifact.bin"
    try:
        missing.read_bytes()
    except FileNotFoundError:
        return _case_result(
            "FB-C04",
            "artifact-acquisition",
            [_attempt(1, "failure", False, "artifact-unavailable")],
        )
    raise AssertionError("artifact acquisition probe unexpectedly succeeded")


def probe_artifact_integrity(workdir: Path) -> dict:
    artifact = workdir / "artifact.bin"
    artifact.write_bytes(b"deterministic-artifact")
    observed = hashlib.sha256(artifact.read_bytes()).hexdigest()
    expected = "0" * 64
    if observed == expected:
        raise AssertionError("integrity probe fixture unexpectedly matched")
    return _case_result(
        "FB-C05",
        "artifact-identity-integrity",
        [_attempt(1, "failure", False, "artifact-identity-mismatch")],
        failClosed=True,
        expectedIdentity=expected,
        observedIdentity=observed,
    )


def probe_process_start_failure(workdir: Path) -> dict:
    missing_executable = workdir / "missing-runtime"
    try:
        subprocess.run([str(missing_executable)], check=False, capture_output=True)
    except FileNotFoundError:
        return _case_result(
            "FB-C06",
            "runtime-execution",
            [_attempt(1, "failure", False, "process-start-failed")],
        )
    raise AssertionError("process start probe unexpectedly succeeded")


def probe_runtime_failure() -> dict:
    completed = subprocess.run(
        [sys.executable, "-c", "raise SystemExit(7)"],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode == 0:
        raise AssertionError("runtime failure probe unexpectedly succeeded")
    return _case_result(
        "FB-C07",
        "runtime-execution",
        [_attempt(1, "failure", True, "runtime-execution-failed")],
    )


def probe_semantic_mapping_rejection() -> dict:
    completed = subprocess.run(
        [sys.executable, "-c", "import json; print(json.dumps({'unexpected': True}))"],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)
    if isinstance(payload, dict) and payload.get("accepted") is True:
        raise AssertionError("semantic mapping probe unexpectedly accepted payload")
    return _case_result(
        "FB-C08",
        "semantic-mapping",
        [_attempt(1, "failure", True, "semantic-mapping-rejected")],
    )


def probe_retry_preserves_initial_failure() -> dict:
    attempts: list[dict] = []
    try:
        _synthetic_provider_admission(1)
    except SyntheticAdmissionRejected:
        attempts.append(_attempt(1, "failure", False, "provider-admission-rejected"))

    outcome = _synthetic_provider_admission(2)
    if outcome != "accepted":
        raise AssertionError("retry probe did not return accepted outcome")
    attempts.append(_attempt(2, "success", True, "provider-admission-accepted"))

    return _case_result(
        "FB-C09",
        "provider-admission",
        attempts,
        initialFailurePreserved=True,
        retryOutcomeSeparate=True,
    )


def _load_catalog() -> dict:
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    errors = validate_catalog(catalog)
    if errors:
        raise ValueError("invalid failure behavior case catalog: " + "; ".join(errors))
    return catalog


def run_probe() -> dict:
    catalog = _load_catalog()
    catalog_by_id = {case["caseId"]: case for case in catalog["cases"]}

    with tempfile.TemporaryDirectory(prefix="soza-failure-probe-") as temp_dir:
        workdir = Path(temp_dir)
        probes: list[Callable[[], dict]] = [
            probe_transport_timeout,
            probe_provider_admission,
            probe_credential_rejection,
            lambda: probe_artifact_unavailable(workdir),
            lambda: probe_artifact_integrity(workdir),
            lambda: probe_process_start_failure(workdir),
            probe_runtime_failure,
            probe_semantic_mapping_rejection,
            probe_retry_preserves_initial_failure,
        ]
        results = [probe() for probe in probes]

    result_ids = {result["caseId"] for result in results}
    if result_ids != set(catalog_by_id):
        raise AssertionError("probe coverage does not match case catalog")
    for result in results:
        expected_stage = catalog_by_id[result["caseId"]]["failureStage"]
        if result["failureStage"] != expected_stage:
            raise AssertionError(
                f"failure stage mismatch for {result['caseId']}: "
                f"{result['failureStage']} != {expected_stage}"
            )

    return {
        "schema": REPORT_SCHEMA,
        "scope": "evaluation-only",
        "authority": "non-universal",
        "sourceCatalogSchema": catalog["schema"],
        "cases": results,
    }


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    report = run_probe()
    text = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args:
        Path(args[0]).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
