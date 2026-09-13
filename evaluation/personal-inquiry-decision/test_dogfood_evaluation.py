from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

EVALUATION_DIR = Path(__file__).resolve().parent
if str(EVALUATION_DIR) not in sys.path:
    sys.path.insert(0, str(EVALUATION_DIR))

from dogfood_evaluation import (  # noqa: E402
    EvaluationRecordError,
    add_capture_observation,
    add_resume_observation,
    comparison_projection,
    load_evaluation,
    new_evaluation,
    save_evaluation,
)


class DogfoodEvaluationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.record = new_evaluation(
            "case-001",
            "local://inquiry-001.json",
            "P1-sei",
            "2026-09-14T03:30:00+09:00",
        )

    def test_resume_observation_keeps_surfaces_distinct(self) -> None:
        record = add_resume_observation(
            self.record,
            {
                "id": "resume-quiet",
                "observed_at": "2026-09-14T03:40:00+09:00",
                "surface": "sei-quiet",
                "original_concern_retention": "pass",
                "temporal_integrity": "pass",
                "source_reopens": 1,
            },
        )
        record = add_resume_observation(
            record,
            {
                "id": "resume-proactive",
                "observed_at": "2026-09-14T03:50:00+09:00",
                "surface": "sei-proactive",
                "original_concern_retention": "fail",
                "temporal_integrity": "pass",
                "source_reopens": 0,
                "attention_load": "high",
            },
        )
        view = comparison_projection(record)
        self.assertEqual(view["by_surface"]["sei-quiet"]["attempts"], 1)
        self.assertEqual(
            view["by_surface"]["sei-proactive"]["original_concern_loss_count"], 1
        )
        self.assertNotIn("winner", view)

    def test_false_continuity_is_counted_without_score(self) -> None:
        record = add_resume_observation(
            self.record,
            {
                "id": "resume-1",
                "observed_at": "2026-09-14T03:40:00+09:00",
                "surface": "generic-summary",
                "false_continuity": True,
                "temporal_integrity": "fail",
            },
        )
        view = comparison_projection(record)
        self.assertEqual(
            view["by_surface"]["generic-summary"]["false_continuity_count"], 1
        )
        self.assertEqual(
            view["by_surface"]["generic-summary"]["historical_integrity_failures"],
            1,
        )

    def test_capture_burden_is_sidecar_only(self) -> None:
        record = add_capture_observation(
            self.record,
            {
                "id": "capture-1",
                "observed_at": "2026-09-14T03:35:00+09:00",
                "semantic_corrections": 2,
                "burden": "medium",
                "notes": "本作業を中断するほどではない。",
            },
        )
        self.assertEqual(record["capture_observations"][0]["semantic_corrections"], 2)
        self.assertEqual(record["capture_observations"][0]["burden"], "medium")

    def test_duplicate_ids_are_rejected_across_observation_types(self) -> None:
        record = add_capture_observation(
            self.record,
            {
                "id": "obs-1",
                "observed_at": "2026-09-14T03:35:00+09:00",
                "burden": "low",
            },
        )
        with self.assertRaisesRegex(EvaluationRecordError, "duplicate observation id"):
            add_resume_observation(
                record,
                {
                    "id": "obs-1",
                    "observed_at": "2026-09-14T03:40:00+09:00",
                    "surface": "sei-orientation",
                },
            )

    def test_invalid_timestamp_is_rejected(self) -> None:
        with self.assertRaisesRegex(EvaluationRecordError, "invalid timestamp"):
            new_evaluation("case-bad", "local://bad", "P1-sei", "not-a-time")

    def test_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "evaluation.json"
            save_evaluation(path, self.record)
            loaded = load_evaluation(path)
        self.assertEqual(loaded, self.record)


if __name__ == "__main__":
    unittest.main()
