#!/usr/bin/env python3

from __future__ import annotations

import json
import unittest
from pathlib import Path

from validate_failure_behavior_case_catalog import validate_catalog


CATALOG_PATH = Path(__file__).with_name("case_catalog.json")


def load_catalog() -> dict:
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


class FailureBehaviorCaseCatalogTest(unittest.TestCase):
    def test_current_catalog_is_valid(self) -> None:
        self.assertEqual(validate_catalog(load_catalog()), [])

    def test_duplicate_case_id_is_rejected(self) -> None:
        data = load_catalog()
        data["cases"][1]["caseId"] = data["cases"][0]["caseId"]
        self.assertTrue(any("duplicate caseId" in error for error in validate_catalog(data)))

    def test_provider_specific_error_code_is_rejected(self) -> None:
        data = load_catalog()
        data["cases"][0]["httpStatus"] = 504
        self.assertTrue(any("httpStatus" in error for error in validate_catalog(data)))

    def test_secret_material_field_is_rejected(self) -> None:
        data = load_catalog()
        data["cases"][2]["token"] = "must-not-be-persisted"
        self.assertTrue(any("token" in error for error in validate_catalog(data)))

    def test_missing_stage_coverage_is_rejected(self) -> None:
        data = load_catalog()
        data["cases"] = [case for case in data["cases"] if case["failureStage"] != "credential"]
        self.assertTrue(any("credential" in error for error in validate_catalog(data)))

    def test_retry_must_preserve_initial_failure(self) -> None:
        data = load_catalog()
        retry_case = next(case for case in data["cases"] if case["retryScenario"])
        retry_case["preserveInitialFailure"] = False
        errors = validate_catalog(data)
        self.assertTrue(any("preserveInitialFailure" in error for error in errors))

    def test_retry_outcome_must_be_separate(self) -> None:
        data = load_catalog()
        retry_case = next(case for case in data["cases"] if case["retryScenario"])
        retry_case["retryOutcomeSeparate"] = False
        errors = validate_catalog(data)
        self.assertTrue(any("retryOutcomeSeparate" in error for error in errors))

    def test_identity_integrity_case_must_be_fail_closed(self) -> None:
        data = load_catalog()
        integrity_case = next(
            case for case in data["cases"] if case["failureStage"] == "artifact-identity-integrity"
        )
        integrity_case["observes"] = [item for item in integrity_case["observes"] if item != "fail-closed"]
        errors = validate_catalog(data)
        self.assertTrue(any("fail-closed" in error for error in errors))

    def test_catalog_cannot_claim_universal_authority(self) -> None:
        data = load_catalog()
        data["authority"] = "universal-contract"
        self.assertTrue(any("non-universal" in error for error in validate_catalog(data)))


if __name__ == "__main__":
    unittest.main()
