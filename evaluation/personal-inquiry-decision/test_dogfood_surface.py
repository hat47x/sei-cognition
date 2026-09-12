from __future__ import annotations

import copy
import sys
import tempfile
import unittest
from pathlib import Path

EVALUATION_DIR = Path(__file__).resolve().parent
if str(EVALUATION_DIR) not in sys.path:
    sys.path.insert(0, str(EVALUATION_DIR))

from dogfood_core import (  # noqa: E402
    DogfoodStateError,
    add_decision,
    add_record,
    add_review,
    add_source,
    baseline_material_projection,
    handoff_projection,
    load_state,
    new_state,
    orientation_projection,
    save_state,
)


class PersonalInquiryContinuityDogfoodTests(unittest.TestCase):
    def setUp(self) -> None:
        state = new_state(
            "ローカル主体の設計メモ運用を続けるか",
            "2026-09-01T09:00:00+09:00",
        )
        state = add_source(
            state,
            {
                "id": "src-note",
                "kind": "note",
                "locator": "file:///notes/design.md",
                "title": "design memo",
                "captured_at": "2026-09-01T09:10:00+09:00",
            },
        )
        state = add_record(
            state,
            {
                "id": "obs-portable",
                "kind": "observation",
                "summary": "Markdownは別環境へ持ち運びやすい。",
                "captured_at": "2026-09-01T09:20:00+09:00",
                "source_refs": ["src-note"],
            },
        )
        state = add_record(
            state,
            {
                "id": "unk-mobile",
                "kind": "unknown",
                "summary": "外出先で編集する頻度はまだ分からない。",
                "captured_at": "2026-09-01T09:30:00+09:00",
                "status": "open",
                "source_refs": [],
            },
        )
        state = add_record(
            state,
            {
                "id": "rec-local",
                "kind": "recommendation",
                "summary": "当面はローカルMarkdownを正本にする。",
                "captured_at": "2026-09-01T09:40:00+09:00",
                "source_refs": [],
            },
        )
        state = add_decision(
            state,
            {
                "id": "dec-local",
                "statement": "ローカルMarkdownを正本にする。",
                "decided_at": "2026-09-01T10:00:00+09:00",
                "basis_refs": ["obs-portable"],
                "unresolved_refs": ["unk-mobile"],
                "revisit_when": ["外出先編集が増えたとき"],
            },
        )
        state = add_review(
            state,
            {
                "id": "review-1",
                "reviewed_at": "2026-09-02T10:00:00+09:00",
                "resume_anchor": "次は外出先編集の実頻度を確認する。",
            },
        )
        self.state = state

    def test_orientation_is_queryless_and_role_preserving(self) -> None:
        before = copy.deepcopy(self.state)
        view = orientation_projection(self.state)

        self.assertEqual(view["inquiry"]["question"], self.state["inquiry"]["question"])
        self.assertEqual(view["current_unresolved"][0]["id"], "unk-mobile")
        self.assertEqual(view["recommendations"][0]["id"], "rec-local")
        self.assertEqual(view["latest_decision"]["id"], "dec-local")
        self.assertEqual(view["latest_decision"]["basis"][0]["id"], "obs-portable")
        self.assertEqual(view["resume_anchor"], "次は外出先編集の実頻度を確認する。")
        self.assertEqual(self.state, before)

    def test_since_review_delta_uses_capture_time(self) -> None:
        updated = add_record(
            self.state,
            {
                "id": "obs-later",
                "kind": "observation",
                "summary": "外出先編集が週3回に増えた。",
                "subject_at": "2026-08-31T12:00:00+09:00",
                "captured_at": "2026-09-05T12:00:00+09:00",
                "source_refs": [],
            },
        )
        view = orientation_projection(updated)
        self.assertEqual([item["id"] for item in view["since_last_review"]], ["obs-later"])
        self.assertEqual([item["id"] for item in view["since_latest_decision"]], ["obs-later"])

    def test_late_arriving_evidence_cannot_enter_historical_basis(self) -> None:
        updated = add_record(
            self.state,
            {
                "id": "obs-late",
                "kind": "observation",
                "summary": "Decision前から料金体系は変更されていた。",
                "subject_at": "2026-08-30T12:00:00+09:00",
                "captured_at": "2026-09-05T12:00:00+09:00",
                "source_refs": [],
            },
        )

        with self.assertRaisesRegex(DogfoodStateError, "later-captured"):
            add_decision(
                updated,
                {
                    "id": "dec-invalid",
                    "statement": "過去時点でこの情報を根拠にしていたことにする。",
                    "decided_at": "2026-09-01T10:30:00+09:00",
                    "basis_refs": ["obs-late"],
                    "unresolved_refs": [],
                    "revisit_when": [],
                },
            )

    def test_subject_time_does_not_override_capture_time_for_knowledge(self) -> None:
        updated = add_record(
            self.state,
            {
                "id": "obs-old-subject-new-capture",
                "kind": "observation",
                "summary": "対象世界では以前から成立していた事実。",
                "subject_at": "2026-08-01T12:00:00+09:00",
                "captured_at": "2026-09-03T12:00:00+09:00",
                "source_refs": [],
            },
        )
        view = orientation_projection(updated)
        later = [
            item
            for item in view["since_latest_decision"]
            if item["id"] == "obs-old-subject-new-capture"
        ]
        self.assertEqual(len(later), 1)
        self.assertEqual(later[0]["subject_at"], "2026-08-01T12:00:00+09:00")

    def test_recommendation_and_decision_are_not_collapsed(self) -> None:
        view = orientation_projection(self.state)
        self.assertNotEqual(view["recommendations"][0]["id"], view["latest_decision"]["id"])

    def test_open_unknown_survives_decision(self) -> None:
        view = orientation_projection(self.state)
        self.assertIn("unk-mobile", {item["id"] for item in view["current_unresolved"]})
        self.assertIn(
            "unk-mobile",
            {item["id"] for item in view["latest_decision"]["unresolved_at_decision"]},
        )

    def test_baseline_material_is_flat_and_does_not_claim_generic_summary(self) -> None:
        baseline = baseline_material_projection(self.state)
        self.assertEqual(baseline["projection"], "generic-summary-baseline-material/v0")
        self.assertTrue(all(set(item) == {"captured_at", "text"} for item in baseline["materials"]))
        self.assertNotIn("latest_decision", baseline)
        self.assertNotIn("current_unresolved", baseline)

    def test_handoff_preserves_boundary_notes(self) -> None:
        handoff = handoff_projection(self.state)
        self.assertIsNotNone(handoff["user_decision"])
        self.assertTrue(handoff["recommendations"])
        self.assertTrue(handoff["unresolved"])
        self.assertIn(
            "later-captured material != historical decision basis",
            handoff["boundary_notes"],
        )

    def test_local_json_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "inquiry.json"
            save_state(path, self.state)
            loaded = load_state(path)
        self.assertEqual(loaded, self.state)

    def test_projection_does_not_require_llm_or_source_content(self) -> None:
        state = copy.deepcopy(self.state)
        state["sources"][0].pop("title", None)
        view = orientation_projection(state)
        self.assertEqual(view["latest_decision"]["id"], "dec-local")

    def test_duplicate_ids_across_planes_are_rejected(self) -> None:
        with self.assertRaisesRegex(DogfoodStateError, "duplicate id"):
            add_record(
                self.state,
                {
                    "id": "src-note",
                    "kind": "observation",
                    "summary": "重複ID。",
                    "captured_at": "2026-09-06T12:00:00+09:00",
                    "source_refs": [],
                },
            )


if __name__ == "__main__":
    unittest.main()
