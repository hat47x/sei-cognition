from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("check_grouping_structure.py")
SPEC = importlib.util.spec_from_file_location("method_quality_checker", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
CHECKER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECKER)


def request_body() -> dict:
    return {
        "cards": [
            {"id": "c-a", "text": "A"},
            {"id": "c-b", "text": "B"},
            {"id": "c-c", "text": "C"},
            {"id": "c-held", "text": "held"},
        ],
        "doc": {
            "cards": [
                {"id": "c-a", "text": "A"},
                {"id": "c-b", "text": "B"},
                {"id": "c-c", "text": "C"},
                {"id": "c-held", "text": "held", "holdState": "held"},
            ]
        },
    }


def valid_result() -> dict:
    return {
        "groups": [
            {
                "label": "束の表札",
                "cardIds": ["c-a", "c-b"],
                "rationale": "意味内容はこのcheckerでは採点しない",
            }
        ],
        "excludedCardIds": ["c-held"],
        "truncated": False,
    }


class GroupingStructureTest(unittest.TestCase):
    def inspect(self, result: dict, request: dict | None = None) -> dict:
        return CHECKER.inspect_grouping_structure(request or request_body(), result)

    def violation_codes(self, report: dict) -> set[str]:
        return {item["code"] for item in report["violations"]}

    def test_valid_grouping_passes(self) -> None:
        report = self.inspect(valid_result())
        self.assertEqual("passed", report["status"])
        self.assertEqual("not_evaluated", report["qualityJudgement"])
        self.assertEqual([], report["violations"])

    def test_ungrouped_non_held_card_is_allowed(self) -> None:
        # c-cが孤立したままでも構造違反にしない。checkerが「全cardを束ねる」ことを
        # 品質基準として先取りしないための制御ケース。
        report = self.inspect(valid_result())
        self.assertEqual("passed", report["status"])
        self.assertEqual(2, report["groupedCardCount"])
        self.assertEqual(4, report["inputCardCount"])

    def test_held_card_reintroduction_fails(self) -> None:
        result = valid_result()
        result["groups"][0]["cardIds"].append("c-held")
        report = self.inspect(result)
        self.assertEqual("failed", report["status"])
        self.assertIn("held_card_reintroduced", self.violation_codes(report))

    def test_hallucinated_card_id_fails(self) -> None:
        result = valid_result()
        result["groups"][0]["cardIds"].append("c-made-up")
        report = self.inspect(result)
        self.assertIn("group_card_not_in_request", self.violation_codes(report))

    def test_duplicate_group_membership_fails(self) -> None:
        result = valid_result()
        result["groups"].append({"label": "別の束", "cardIds": ["c-b", "c-c"]})
        report = self.inspect(result)
        self.assertIn("duplicate_group_membership", self.violation_codes(report))

    def test_missing_held_card_from_excluded_fails(self) -> None:
        result = valid_result()
        result["excludedCardIds"] = []
        report = self.inspect(result)
        self.assertIn("held_card_missing_from_excluded", self.violation_codes(report))

    def test_card_cannot_be_grouped_and_excluded_at_the_same_time(self) -> None:
        result = valid_result()
        result["excludedCardIds"].append("c-a")
        report = self.inspect(result)
        self.assertIn("card_both_grouped_and_excluded", self.violation_codes(report))

    def test_empty_label_fails_without_judging_wording(self) -> None:
        result = valid_result()
        result["groups"][0]["label"] = "   "
        report = self.inspect(result)
        self.assertIn("empty_group_label", self.violation_codes(report))

    def test_different_nonempty_wording_is_structurally_equivalent(self) -> None:
        first = valid_result()
        second = valid_result()
        first["groups"][0]["label"] = "生活習慣"
        second["groups"][0]["label"] = "在宅勤務"
        first["groups"][0]["rationale"] = "第一の生成文"
        second["groups"][0]["rationale"] = "異なる生成文"

        self.assertEqual("passed", self.inspect(first)["status"])
        self.assertEqual("passed", self.inspect(second)["status"])

    def test_unknown_excluded_card_fails(self) -> None:
        result = valid_result()
        result["excludedCardIds"].append("c-unknown")
        report = self.inspect(result)
        self.assertIn("excluded_card_not_in_request", self.violation_codes(report))


if __name__ == "__main__":
    unittest.main()
