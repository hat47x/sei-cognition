from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVALUATION_DIR = ROOT / "evaluation" / "personal-inquiry-decision"
if str(EVALUATION_DIR) not in sys.path:
    sys.path.insert(0, str(EVALUATION_DIR))

from prototype import (  # noqa: E402
    PrototypeStateError,
    add_observation,
    reorientation_view,
    validate_state,
)

FIXTURE_PATH = EVALUATION_DIR / "fixture_personal_project.json"


class PersonalInquiryDecisionPrototypeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.state = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    def test_fixture_is_valid(self) -> None:
        validate_state(self.state)

    def test_light_view_answers_reorientation_questions(self) -> None:
        view = reorientation_view(self.state)
        self.assertTrue(view["what_am_i_considering"])
        self.assertTrue(view["important_observations"])
        self.assertTrue(view["what_is_unresolved"])
        self.assertIsNotNone(view["recommendation"])
        self.assertIsNotNone(view["decision"])
        self.assertTrue(view["decision_basis"])
        self.assertTrue(view["revisit_when"])

    def test_recommendation_and_decision_remain_distinct(self) -> None:
        view = reorientation_view(self.state)
        self.assertNotEqual(view["recommendation"]["id"], view["decision"]["id"])
        self.assertNotEqual(view["recommendation"]["summary"], view["decision"]["statement"])

    def test_unknown_remains_open_after_decision(self) -> None:
        view = reorientation_view(self.state)
        unresolved_ids = {item["id"] for item in view["what_is_unresolved"]}
        self.assertIn("unk-mobile-frequency", unresolved_ids)

    def test_post_decision_observation_does_not_rewrite_historical_basis(self) -> None:
        original_basis = copy.deepcopy(self.state["decisions"][0]["basis_refs"])
        updated = add_observation(
            self.state,
            {
                "id": "obs-later-mobile-use",
                "summary": "その後、外出先で設計メモを編集する機会が増えた。",
                "observed_at": "2026-09-09T12:00:00+09:00",
                "added_at": "2026-09-09T12:05:00+09:00",
            },
        )

        self.assertEqual(updated["decisions"][0]["basis_refs"], original_basis)
        view = reorientation_view(updated)
        self.assertEqual(
            [item["id"] for item in view["new_since_decision"]],
            ["obs-later-mobile-use"],
        )
        self.assertNotIn(
            "obs-later-mobile-use",
            [item["id"] for item in view["decision_basis"]],
        )

    def test_post_decision_observation_cannot_be_backfilled_into_basis(self) -> None:
        state = add_observation(
            self.state,
            {
                "id": "obs-future",
                "summary": "Decision後に初めて得られた情報。",
                "observed_at": "2026-09-02T12:00:00+09:00",
                "added_at": "2026-09-02T12:01:00+09:00",
            },
        )
        state["decisions"][0]["basis_refs"].append("obs-future")

        with self.assertRaisesRegex(PrototypeStateError, "post-decision observation"):
            validate_state(state)

    def test_missing_llm_identity_does_not_block_reorientation(self) -> None:
        state = copy.deepcopy(self.state)
        state["recommendations"] = []
        view = reorientation_view(state)
        self.assertIsNone(view["recommendation"])
        self.assertTrue(view["decision"])
        self.assertTrue(view["decision_basis"])
        self.assertTrue(view["what_is_unresolved"])

    def test_invalid_unresolved_reference_is_rejected(self) -> None:
        state = copy.deepcopy(self.state)
        state["decisions"][0]["unresolved_refs"] = ["obs-local-portability"]
        with self.assertRaisesRegex(PrototypeStateError, "unresolved ref"):
            validate_state(state)

    def test_projection_does_not_mutate_state(self) -> None:
        before = copy.deepcopy(self.state)
        reorientation_view(self.state)
        self.assertEqual(self.state, before)


if __name__ == "__main__":
    unittest.main()
