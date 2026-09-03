import json
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
OBSERVATION_PATH = BASE_DIR / "historical" / "ai-supplemental-comparison.json"


class AISupplementalComparisonTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.observation = json.loads(OBSERVATION_PATH.read_text(encoding="utf-8"))

    def test_ai_observation_does_not_claim_human_review_or_quality_judgement(self):
        self.assertEqual(
            self.observation["reviewAuthority"], "non_authoritative_ai_supplement"
        )
        self.assertFalse(self.observation["humanReviewCompleted"])
        self.assertEqual(self.observation["qualityJudgement"], "not_evaluated")
        self.assertFalse(self.observation["rules"]["humanJudgementSubstitution"])

    def test_ai_observation_does_not_select_winner_or_golden_label(self):
        self.assertFalse(self.observation["rules"]["winnerSelection"])
        self.assertFalse(self.observation["rules"]["goldenLabel"])
        self.assertFalse(self.observation["rules"]["machineScore"])

        forbidden_keys = {
            "winner",
            "preferred",
            "expectedLabel",
            "expectedGroups",
            "qualityScore",
        }

        def walk(value):
            if isinstance(value, dict):
                self.assertTrue(forbidden_keys.isdisjoint(value.keys()), value)
                for child in value.values():
                    walk(child)
            elif isinstance(value, list):
                for child in value:
                    walk(child)

        walk(self.observation)

    def test_ai_observation_points_back_to_human_review_template(self):
        handoff = self.observation["humanReviewHandoff"]
        self.assertEqual(
            handoff["template"], "evaluation/method-quality/HUMAN_REVIEW_TEMPLATE.md"
        )
        self.assertTrue(set(handoff["focusQuestionIds"]).issubset({f"Q{i}" for i in range(1, 9)}))


if __name__ == "__main__":
    unittest.main()
