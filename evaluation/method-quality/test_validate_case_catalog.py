import json
import tempfile
import unittest
from pathlib import Path

from validate_case_catalog import validate_catalog


class ValidateCaseCatalogTest(unittest.TestCase):
    def valid_catalog(self):
        return {
            "schema": "sei.method-quality-case-catalog/v1",
            "rules": {
                "goldenGrouping": False,
                "machineScoring": False,
                "humanReviewRequiredForOutcomeQuality": True,
            },
            "cases": [
                {
                    "id": "MQC-TEST-001",
                    "title": "test case",
                    "cards": [
                        {"id": "c-1", "text": "first"},
                        {"id": "c-2", "text": "second", "holdState": "held"},
                    ],
                    "reviewFocus": ["observe semantic tension"],
                }
            ],
        }

    def test_valid_catalog_is_accepted(self):
        validate_catalog(self.valid_catalog())

    def test_duplicate_case_id_is_rejected(self):
        catalog = self.valid_catalog()
        catalog["cases"].append(dict(catalog["cases"][0]))
        with self.assertRaisesRegex(ValueError, "duplicate case id"):
            validate_catalog(catalog)

    def test_duplicate_card_id_is_rejected(self):
        catalog = self.valid_catalog()
        catalog["cases"][0]["cards"][1]["id"] = "c-1"
        with self.assertRaisesRegex(ValueError, "duplicate card id"):
            validate_catalog(catalog)

    def test_non_held_hold_state_is_rejected(self):
        catalog = self.valid_catalog()
        catalog["cases"][0]["cards"][1]["holdState"] = "resolved"
        with self.assertRaisesRegex(ValueError, "holdState"):
            validate_catalog(catalog)

    def test_empty_review_focus_is_rejected(self):
        catalog = self.valid_catalog()
        catalog["cases"][0]["reviewFocus"] = []
        with self.assertRaisesRegex(ValueError, "reviewFocus"):
            validate_catalog(catalog)

    def test_expected_groups_are_rejected(self):
        catalog = self.valid_catalog()
        catalog["cases"][0]["expectedGroups"] = [["c-1", "c-2"]]
        with self.assertRaisesRegex(ValueError, "golden fields"):
            validate_catalog(catalog)

    def test_expected_label_is_rejected(self):
        catalog = self.valid_catalog()
        catalog["cases"][0]["expectedLabel"] = "answer"
        with self.assertRaisesRegex(ValueError, "golden fields"):
            validate_catalog(catalog)

    def test_quality_score_is_rejected(self):
        catalog = self.valid_catalog()
        catalog["cases"][0]["qualityScore"] = 1.0
        with self.assertRaisesRegex(ValueError, "golden fields"):
            validate_catalog(catalog)

    def test_machine_scoring_must_remain_disabled(self):
        catalog = self.valid_catalog()
        catalog["rules"]["machineScoring"] = True
        with self.assertRaisesRegex(ValueError, "machineScoring"):
            validate_catalog(catalog)

    def test_human_review_requirement_cannot_be_disabled(self):
        catalog = self.valid_catalog()
        catalog["rules"]["humanReviewRequiredForOutcomeQuality"] = False
        with self.assertRaisesRegex(ValueError, "humanReviewRequiredForOutcomeQuality"):
            validate_catalog(catalog)


if __name__ == "__main__":
    unittest.main()
