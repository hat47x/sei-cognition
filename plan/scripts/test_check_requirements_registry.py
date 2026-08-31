#!/usr/bin/env python3
"""Self-tests for check_requirements_registry.py using only the Python stdlib."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("check_requirements_registry.py")
spec = importlib.util.spec_from_file_location("check_requirements_registry", MODULE_PATH)
assert spec and spec.loader
checker = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = checker
spec.loader.exec_module(checker)

VALID_REQUIREMENTS = """# Product Requirements

## 2. Current Requirement一覧

| ID | 要求 | 主なValue Axis | Status | Design Acceptance |
|---|---|---|---|---|
| REQ-0001 | A | V1, V3 | Accepted | Satisfied |
| REQ-0002 | B | V2 | Accepted | Satisfied |

---

## REQ-0001 — A

**Status:** Accepted  
**Value:** V1, V3  
**Related Scenarios:** SCN-0001  

### Current Evidence

- Design: **Satisfied**
- Executable / Release / Operational: **Not Yet Verified**

## REQ-0002 — B

**Status:** Accepted  
**Value:** V2  
**Related Scenarios:** SCN-0001  

### Current Evidence

- Design: **Satisfied**
- Executable / Release / Operational: **Not Yet Verified**
"""

VALID_SCENARIOS = """# Acceptance Scenarios

## 2. Scenario一覧

| ID | Scenario | 主なValue Axis | 主なRequirement |
|---|---|---|---|
| SCN-0001 | S | V1, V2 | REQ-0001, 0002 |

---

## SCN-0001 — S

### Current Evidence

- Design: **Satisfied**
- Executable / Release / Operational: **Not Yet Verified**
"""


def codes(report):
    return {finding.code for finding in report.findings}


def assert_pass(req=VALID_REQUIREMENTS, scn=VALID_SCENARIOS):
    report = checker.validate(req, scn)
    assert report.passed, report.to_dict()


def assert_fails(code, req=VALID_REQUIREMENTS, scn=VALID_SCENARIOS):
    report = checker.validate(req, scn)
    assert not report.passed, report.to_dict()
    assert code in codes(report), report.to_dict()


def main() -> int:
    assert_pass()

    assert_fails(
        "duplicate-requirement-id",
        req=VALID_REQUIREMENTS + "\n## REQ-0001 — duplicate\n**Status:** Accepted\n**Value:** V1\n",
    )

    assert_fails(
        "duplicate-scenario-id",
        scn=VALID_SCENARIOS + "\n## SCN-0001 — duplicate\n",
    )

    assert_fails(
        "requirement-scenario-reference-missing",
        req=VALID_REQUIREMENTS.replace("SCN-0001", "SCN-9999", 1),
    )

    assert_fails(
        "scenario-requirement-reference-missing",
        scn=VALID_SCENARIOS.replace("REQ-0001, 0002", "REQ-0001, 9999"),
    )

    assert_fails(
        "requirement-value-axis-invalid",
        req=VALID_REQUIREMENTS.replace("**Value:** V2", "**Value:** V9"),
    )

    assert_fails(
        "scenario-value-axis-invalid",
        scn=VALID_SCENARIOS.replace("| SCN-0001 | S | V1, V2 |", "| SCN-0001 | S | V9 |"),
    )

    assert_fails(
        "requirement-status-invalid",
        req=VALID_REQUIREMENTS.replace("**Status:** Accepted", "**Status:** Done", 1),
    )

    assert_fails(
        "requirement-acceptance-state-invalid",
        req=VALID_REQUIREMENTS.replace("- Design: **Satisfied**", "- Design: **Verified**", 1),
    )

    print("PASS: requirements registry checker self-tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
