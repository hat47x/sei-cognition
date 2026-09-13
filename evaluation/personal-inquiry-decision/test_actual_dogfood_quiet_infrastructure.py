from __future__ import annotations

import sys
import unittest
from pathlib import Path

EVALUATION_DIR = Path(__file__).resolve().parent
if str(EVALUATION_DIR) not in sys.path:
    sys.path.insert(0, str(EVALUATION_DIR))

from dogfood_core import load_state, orientation_projection  # noqa: E402
from dogfood_evaluation import load_evaluation  # noqa: E402


INQUIRY_PATH = EVALUATION_DIR / "actual_dogfood_quiet_infrastructure_2026-09-14.inquiry.json"
EVALUATION_PATH = (
    EVALUATION_DIR / "actual_dogfood_quiet_infrastructure_2026-09-14.evaluation.json"
)


class ActualQuietInfrastructureDogfoodSeedTests(unittest.TestCase):
    def test_seed_is_open_inquiry_without_decision(self) -> None:
        state = load_state(INQUIRY_PATH)

        self.assertEqual(state["decisions"], [])
        self.assertEqual(state["reviews"], [])
        self.assertEqual(len(state["sources"]), 4)

        kinds = [record["kind"] for record in state["records"]]
        self.assertEqual(kinds.count("observation"), 3)
        self.assertEqual(kinds.count("unknown"), 3)
        self.assertEqual(kinds.count("hypothesis"), 3)
        self.assertEqual(kinds.count("recommendation"), 0)

    def test_orientation_preserves_uncertainty_without_inventing_decision(self) -> None:
        state = load_state(INQUIRY_PATH)
        orientation = orientation_projection(state)

        self.assertIsNone(orientation["latest_decision"])
        self.assertEqual(len(orientation["current_unresolved"]), 3)
        self.assertEqual(len(orientation["recommendations"]), 0)

        projected_kinds = {
            item["kind"] for item in orientation["current_observations_and_hypotheses"]
        }
        self.assertEqual(projected_kinds, {"observation", "hypothesis"})

    def test_evaluation_sidecar_starts_without_human_observations(self) -> None:
        evaluation = load_evaluation(EVALUATION_PATH)

        self.assertEqual(evaluation["case_id"], "pic-quiet-001")
        self.assertEqual(evaluation["profile"], "P1-sei")
        self.assertEqual(evaluation["capture_observations"], [])
        self.assertEqual(evaluation["resume_observations"], [])


if __name__ == "__main__":
    unittest.main()
