#!/usr/bin/env python3
"""Validate the ISSUE-000072 failure-behavior evaluation case catalog.

The catalog is intentionally evaluation-only.  This validator protects that
boundary: it checks coverage and evidence-shape invariants without turning
provider-specific error vocabulary or retry policy into Universal semantics.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

SCHEMA = "soza.failure-behavior-case-catalog/v1"
ALLOWED_STAGES = {
    "reachability-transport",
    "provider-admission",
    "credential",
    "artifact-acquisition",
    "artifact-identity-integrity",
    "runtime-execution",
    "semantic-mapping",
}
REQUIRED_STAGES = {
    "reachability-transport",
    "provider-admission",
    "credential",
    "artifact-acquisition",
    "artifact-identity-integrity",
    "runtime-execution",
    "semantic-mapping",
}
FORBIDDEN_KEYS = {
    "httpStatus",
    "providerErrorCode",
    "retryDelaySeconds",
    "retrySchedule",
    "credential",
    "credentials",
    "token",
    "accessToken",
    "apiKey",
    "password",
    "secret",
}


def _walk_keys(value: Any, path: str = "$") -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            found.append((key, f"{path}.{key}"))
            found.extend(_walk_keys(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(_walk_keys(child, f"{path}[{index}]"))
    return found


def validate_catalog(data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["catalog root must be an object"]

    if data.get("schema") != SCHEMA:
        errors.append(f"schema must be {SCHEMA!r}")
    if data.get("scope") != "evaluation-only":
        errors.append("scope must remain 'evaluation-only'")
    if data.get("authority") != "non-universal":
        errors.append("authority must remain 'non-universal'")

    for key, path in _walk_keys(data):
        if key in FORBIDDEN_KEYS:
            errors.append(f"provider/retry/secret-specific key is forbidden at {path}: {key}")

    cases = data.get("cases")
    if not isinstance(cases, list) or not cases:
        errors.append("cases must be a non-empty array")
        return errors

    case_ids: set[str] = set()
    observed_stages: set[str] = set()
    retry_case_count = 0
    integrity_case_count = 0

    for index, case in enumerate(cases):
        prefix = f"cases[{index}]"
        if not isinstance(case, dict):
            errors.append(f"{prefix} must be an object")
            continue

        case_id = case.get("caseId")
        if not isinstance(case_id, str) or not case_id:
            errors.append(f"{prefix}.caseId must be a non-empty string")
        elif case_id in case_ids:
            errors.append(f"duplicate caseId: {case_id}")
        else:
            case_ids.add(case_id)

        title = case.get("title")
        if not isinstance(title, str) or not title.strip():
            errors.append(f"{prefix}.title must be a non-empty string")

        stage = case.get("failureStage")
        if stage not in ALLOWED_STAGES:
            errors.append(f"{prefix}.failureStage is not an allowed candidate stage: {stage!r}")
        else:
            observed_stages.add(stage)

        if not isinstance(case.get("executionStarted"), bool):
            errors.append(f"{prefix}.executionStarted must be boolean")
        if case.get("preserveInitialFailure") is not True:
            errors.append(f"{prefix}.preserveInitialFailure must be true")

        observes = case.get("observes")
        if not isinstance(observes, list) or not observes or not all(isinstance(item, str) and item for item in observes):
            errors.append(f"{prefix}.observes must be a non-empty string array")

        if case.get("retryScenario") is True:
            retry_case_count += 1
            if case.get("retryOutcomeSeparate") is not True:
                errors.append(f"{prefix}.retryOutcomeSeparate must be true for retry scenarios")
        elif case.get("retryScenario") is not False:
            errors.append(f"{prefix}.retryScenario must be boolean")

        if stage == "artifact-identity-integrity":
            integrity_case_count += 1
            if "fail-closed" not in (observes or []):
                errors.append(f"{prefix} must observe fail-closed for identity/integrity failure")

    missing_stages = sorted(REQUIRED_STAGES - observed_stages)
    if missing_stages:
        errors.append("missing required candidate stages: " + ", ".join(missing_stages))
    if retry_case_count < 1:
        errors.append("at least one retry scenario is required")
    if integrity_case_count < 1:
        errors.append("at least one artifact identity/integrity case is required")

    return errors


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    catalog_path = Path(args[0]) if args else Path(__file__).with_name("case_catalog.json")
    try:
        data = json.loads(catalog_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"failure behavior case catalog: FAILED\n- {exc}", file=sys.stderr)
        return 1

    errors = validate_catalog(data)
    if errors:
        print("failure behavior case catalog: FAILED", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"failure behavior case catalog: PASS ({len(data['cases'])} cases)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
