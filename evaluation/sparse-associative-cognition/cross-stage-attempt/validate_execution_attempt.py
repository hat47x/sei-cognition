#!/usr/bin/env python3
"""Validate immutable cross-stage execution-attempt artifacts.

An execution attempt records one authorized benchmark execution try.  It does not
contain benchmark metrics, interpretation, a winner, a B5 decision, or a
production-default decision.  Failed attempts remain first-class evidence and
must never be wrapped as successful result artifacts.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Callable

HERE = Path(__file__).resolve().parent
SACS_DIR = HERE.parent
RUN_DIR = SACS_DIR / "cross-stage-run"
FREEZE_DIR = SACS_DIR / "cross-stage-freeze"

ATTEMPT_PATH = HERE / "execution_attempt.json"
RUN_PATH = RUN_DIR / "evaluation_run.json"
PREREG_PATH = SACS_DIR / "cross_stage_benchmark_preregistration.json"

EXPECTED_SCHEMA = "sei.sacs-cross-stage-execution-attempt/v1alpha1"
UTC_SECOND = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
COMMIT_SHA = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")

TOP_LEVEL_KEYS = {
    "schema",
    "issue",
    "state",
    "attempt_id",
    "run_binding",
    "executor",
    "started_at",
    "completed_at",
    "exit_code",
    "outcome",
    "observed_environment",
    "raw_evidence",
    "results_generated",
    "attempt_digest",
}
RUN_BINDING_KEYS = {"ref", "digest"}
EXECUTOR_KEYS = {"ref", "commit"}
ENVIRONMENT_KEYS = {"os", "arch", "runtime"}
RAW_EVIDENCE_KEYS = {"kind", "ref", "digest"}
RAW_EVIDENCE_KINDS = {"runner-log", "environment-capture", "raw-output"}
REQUIRED_EVIDENCE_ALWAYS = {"runner-log", "environment-capture"}
TEMPLATE_ATTEMPT_ID = "cross-stage-attempt-template"
FIXED_RUN_REF = "../cross-stage-run/evaluation_run.json"

UpstreamValidator = Callable[[dict[str, Any], dict[str, Any], dict[str, dict[str, Any]]], list[str]]


def _canonical_string(value: object) -> bool:
    return isinstance(value, str) and value != "" and value == value.strip()


def canonical_attempt_digest(attempt: dict[str, Any]) -> str:
    payload = copy.deepcopy(attempt)
    payload.pop("attempt_digest", None)
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def validate_attempt_structure(attempt: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if set(attempt) != TOP_LEVEL_KEYS:
        missing = sorted(TOP_LEVEL_KEYS - set(attempt))
        extra = sorted(set(attempt) - TOP_LEVEL_KEYS)
        errors.append(f"attempt top-level keys mismatch: missing={missing}, extra={extra}")

    if attempt.get("schema") != EXPECTED_SCHEMA:
        errors.append(f"attempt.schema must be {EXPECTED_SCHEMA}")
    if attempt.get("state") not in {"draft", "completed"}:
        errors.append("attempt.state must be draft or completed")
    if not _canonical_string(attempt.get("attempt_id")):
        errors.append("attempt.attempt_id must be canonical and non-empty")

    run_binding = attempt.get("run_binding")
    if not isinstance(run_binding, dict) or set(run_binding) != RUN_BINDING_KEYS:
        errors.append("attempt.run_binding must contain exactly ref and digest")
    elif run_binding.get("ref") != FIXED_RUN_REF:
        errors.append(f"attempt.run_binding.ref must remain {FIXED_RUN_REF}")

    executor = attempt.get("executor")
    if not isinstance(executor, dict) or set(executor) != EXECUTOR_KEYS:
        errors.append("attempt.executor must contain exactly ref and commit")

    environment = attempt.get("observed_environment")
    if not isinstance(environment, dict) or set(environment) != ENVIRONMENT_KEYS:
        errors.append("attempt.observed_environment must contain exactly os, arch, runtime")

    evidence = attempt.get("raw_evidence")
    if not isinstance(evidence, list):
        errors.append("attempt.raw_evidence must be a list")
    else:
        for index, item in enumerate(evidence):
            if not isinstance(item, dict) or set(item) != RAW_EVIDENCE_KEYS:
                errors.append(
                    f"attempt.raw_evidence[{index}] keys do not match the registered evidence contract"
                )

    if attempt.get("results_generated") is not False:
        errors.append("execution-attempt artifact must keep results_generated=false")

    if attempt.get("state") == "draft":
        if attempt.get("started_at") is not None:
            errors.append("draft attempt started_at must be null")
        if attempt.get("completed_at") is not None:
            errors.append("draft attempt completed_at must be null")
        if attempt.get("exit_code") is not None:
            errors.append("draft attempt exit_code must be null")
        if attempt.get("outcome") != "not-started":
            errors.append("draft attempt outcome must be not-started")
        if attempt.get("attempt_digest") != "":
            errors.append("draft attempt attempt_digest must be empty")
        if isinstance(run_binding, dict) and run_binding.get("digest") != "":
            errors.append("draft attempt run_binding.digest must be empty")
        if isinstance(executor, dict):
            if executor.get("ref") != "" or executor.get("commit") != "":
                errors.append("draft attempt executor identity must be empty")
        if isinstance(environment, dict) and any(environment.get(k) != "" for k in ENVIRONMENT_KEYS):
            errors.append("draft attempt observed_environment must remain empty")
        if isinstance(evidence, list) and evidence:
            errors.append("draft attempt raw_evidence must be empty")

    return errors


def _default_upstream_validator(
    run: dict[str, Any],
    prereg: dict[str, Any],
    freeze_documents: dict[str, dict[str, Any]],
) -> list[str]:
    for path in (SACS_DIR, RUN_DIR, FREEZE_DIR):
        if str(path) not in sys.path:
            sys.path.insert(0, str(path))

    from validate_cross_stage_preregistration import validate_unlock  # noqa: E402
    from validate_evaluation_run import validate_authorized_run  # noqa: E402

    errors = [
        f"authorized run: {error}"
        for error in validate_authorized_run(run, prereg, freeze_documents)
    ]
    errors.extend(f"full unlock: {error}" for error in validate_unlock(prereg))
    return errors


def validate_completed_attempt(
    attempt: dict[str, Any],
    run: dict[str, Any],
    prereg: dict[str, Any],
    freeze_documents: dict[str, dict[str, Any]],
    *,
    upstream_validator: UpstreamValidator | None = None,
) -> list[str]:
    errors = validate_attempt_structure(attempt)
    if attempt.get("state") != "completed":
        errors.append("completed attempt validation requires attempt.state=completed")
        return errors

    validator = upstream_validator or _default_upstream_validator
    errors.extend(validator(run, prereg, freeze_documents))

    if attempt.get("attempt_id") == TEMPLATE_ATTEMPT_ID:
        errors.append("completed attempt must replace the template attempt_id")

    run_digest = run.get("run_digest")
    run_binding = attempt.get("run_binding", {})
    if not isinstance(run_digest, str) or HEX64.fullmatch(run_digest) is None:
        errors.append("completed attempt requires authorized run with valid run_digest")
    elif run_binding.get("digest") != run_digest:
        errors.append("attempt run_binding.digest does not match authorized run digest")

    executor = attempt.get("executor", {})
    if not _canonical_string(executor.get("ref")):
        errors.append("completed attempt requires canonical executor.ref")
    commit = executor.get("commit")
    if not isinstance(commit, str) or COMMIT_SHA.fullmatch(commit) is None:
        errors.append("completed attempt executor.commit must be a 40-char lowercase git SHA")

    environment = attempt.get("observed_environment", {})
    run_environment = run.get("environment")
    if environment != run_environment:
        errors.append("attempt observed_environment must exactly match authorized run environment")
    for key in ENVIRONMENT_KEYS:
        if not _canonical_string(environment.get(key)):
            errors.append(f"completed attempt requires canonical observed_environment.{key}")

    started_at = attempt.get("started_at")
    completed_at = attempt.get("completed_at")
    for key, value in (("started_at", started_at), ("completed_at", completed_at)):
        if not isinstance(value, str) or UTC_SECOND.fullmatch(value) is None:
            errors.append(
                f"completed attempt {key} must use UTC second format YYYY-MM-DDTHH:MM:SSZ"
            )
    if (
        isinstance(started_at, str)
        and isinstance(completed_at, str)
        and UTC_SECOND.fullmatch(started_at)
        and UTC_SECOND.fullmatch(completed_at)
        and started_at > completed_at
    ):
        errors.append("attempt.started_at must not be after attempt.completed_at")

    exit_code = attempt.get("exit_code")
    if not isinstance(exit_code, int) or isinstance(exit_code, bool):
        errors.append("completed attempt exit_code must be an integer")
    else:
        expected_outcome = "succeeded" if exit_code == 0 else "failed"
        if attempt.get("outcome") != expected_outcome:
            errors.append(
                f"attempt.outcome must be {expected_outcome} when exit_code={exit_code}"
            )

    evidence = attempt.get("raw_evidence", [])
    kinds: set[str] = set()
    refs: set[str] = set()
    if isinstance(evidence, list):
        for index, item in enumerate(evidence):
            if not isinstance(item, dict):
                continue
            kind = item.get("kind")
            if kind not in RAW_EVIDENCE_KINDS:
                errors.append(f"attempt.raw_evidence[{index}].kind is not registered: {kind}")
            elif kind in kinds:
                errors.append(f"attempt raw evidence kind must be unique: {kind}")
            else:
                kinds.add(kind)

            ref = item.get("ref")
            if not _canonical_string(ref):
                errors.append(
                    f"attempt.raw_evidence[{index}].ref must be canonical and non-empty"
                )
            elif ref in refs:
                errors.append(f"attempt raw evidence ref must be unique: {ref}")
            else:
                refs.add(ref)

            digest = item.get("digest")
            if not isinstance(digest, str) or HEX64.fullmatch(digest) is None:
                errors.append(
                    f"attempt.raw_evidence[{index}].digest must be lowercase SHA-256 hex"
                )

    missing = sorted(REQUIRED_EVIDENCE_ALWAYS - kinds)
    if missing:
        errors.append(f"completed attempt is missing required raw evidence kinds: {missing}")
    if attempt.get("outcome") == "succeeded" and "raw-output" not in kinds:
        errors.append("successful attempt requires raw_evidence kind=raw-output")

    digest = attempt.get("attempt_digest")
    if not isinstance(digest, str) or HEX64.fullmatch(digest) is None:
        errors.append("completed attempt requires attempt_digest as lowercase SHA-256 hex")
    elif digest != canonical_attempt_digest(attempt):
        errors.append("completed attempt attempt_digest does not match canonical content")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempt", type=Path, default=ATTEMPT_PATH)
    parser.add_argument("--run", type=Path, default=RUN_PATH)
    parser.add_argument("--prereg", type=Path, default=PREREG_PATH)
    parser.add_argument("--freeze-dir", type=Path, default=FREEZE_DIR)
    args = parser.parse_args()

    try:
        attempt = json.loads(args.attempt.read_text(encoding="utf-8"))
        run = json.loads(args.run.read_text(encoding="utf-8"))
        prereg = json.loads(args.prereg.read_text(encoding="utf-8"))
        if str(FREEZE_DIR) not in sys.path:
            sys.path.insert(0, str(FREEZE_DIR))
        from freeze_manifests import load_directory  # noqa: E402

        freeze_documents = load_directory(args.freeze_dir)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"execution-attempt load failed: {exc}", file=sys.stderr)
        return 1

    structural = validate_attempt_structure(attempt)
    if structural:
        for error in structural:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    if attempt.get("state") == "draft":
        print("Cross-stage execution attempt validated; current attempt remains draft/not-started")
        return 0

    errors = validate_completed_attempt(attempt, run, prereg, freeze_documents)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("Cross-stage execution attempt validated; completed attempt is provenance-bound")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
