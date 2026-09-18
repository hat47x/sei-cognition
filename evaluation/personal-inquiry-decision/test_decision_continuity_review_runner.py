#!/usr/bin/env python3
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from inquiry_continuity_review_runner import (
    InquiryReviewRunnerError,
    attach_review_provenance,
    evidence_bundle,
    provenance_projection,
    record_checked_response,
    reviewer_bundle,
    save_new_session,
)
from matched_review_session import current_stage, new_session


def fixture(fid: str) -> dict:
    basis_a = f"{fid}-basis-a"
    basis_b = f"{fid}-basis-b"
    recommendation = f"{fid}-recommendation"
    unknown_a = f"{fid}-unknown-a"
    unknown_b = f"{fid}-unknown-b"
    decision = f"{fid}-decision"
    late = f"{fid}-late"
    return {
        "schema": "sei.decision-continuity-comparison-fixture/v0",
        "status": "evaluation-only",
        "issue": "ISSUE-000073",
        "fixture_id": fid,
        "title": fid,
        "scenario": {
            "phase_1": [
                {"role": "observation", "id": basis_a, "text": "basis a"},
                {"role": "observation", "id": basis_b, "text": "basis b"},
                {
                    "role": "recommendation",
                    "id": recommendation,
                    "text": "recommendation",
                },
                {"role": "unknown", "id": unknown_a, "text": "unknown a"},
                {"role": "unknown", "id": unknown_b, "text": "unknown b"},
                {
                    "role": "decision",
                    "id": decision,
                    "text": "decision",
                    "basis_refs": [basis_a, basis_b],
                    "recommendation_refs": [recommendation],
                    "unresolved_refs": [unknown_a, unknown_b],
                },
            ],
            "post_decision_evidence": [
                {"role": "observation", "id": late, "text": "later evidence"}
            ],
        },
        "conditions": {
            "A_raw_chat": {"surface_text": ["raw"]},
            "B_chronological_note": {"surface_text": ["note"]},
            "C_sei_resume": {"surface_text": {"question": "q"}},
        },
        "reference_state": {
            "decision": "decision",
            "recommendation": "recommendation",
            "historical_basis_ids": [basis_a, basis_b],
            "unresolved_ids": [unknown_a, unknown_b],
            "post_decision_ids": [late],
            "temporal_stopline": "late evidence is not historical basis",
        },
        "human_review_template": {
            "before_post_decision_evidence": [
                "decision?",
                "recommendation difference?",
                "basis?",
                "unresolved?",
                "next?",
            ],
            "after_post_decision_evidence": [
                "new evidence?",
                "review relevance?",
                "not historical basis?",
                "reopen?",
            ],
            "operator_metrics": [
                "time_to_orientation",
                "source_reopen_count",
                "mental_effort_1_to_5",
            ],
        },
    }


def matched_set() -> tuple[dict, dict[str, dict]]:
    ids = ["f1", "f2", "f3"]
    manifest = {
        "schema": "sei.decision-continuity-matched-set/v0",
        "status": "evaluation-only",
        "issue": "ISSUE-000073",
        "set_id": "decision-runner-test",
        "fixtures": [{"id": fid, "path": f"{fid}.json"} for fid in ids],
        "condition_codes": {
            "A_raw_chat": "raw",
            "B_chronological_note": "note",
            "C_sei_resume": "sei",
        },
        "interpretation_stoplines": [
            "synthetic review is not H1 actual-resumption evidence",
            "no overall winner is computed",
        ],
        "assignment_rotations": {
            "R1": [
                {"fixture": "f1", "condition": "A_raw_chat"},
                {"fixture": "f2", "condition": "B_chronological_note"},
                {"fixture": "f3", "condition": "C_sei_resume"},
            ],
            "R2": [
                {"fixture": "f1", "condition": "B_chronological_note"},
                {"fixture": "f2", "condition": "C_sei_resume"},
                {"fixture": "f3", "condition": "A_raw_chat"},
            ],
            "R3": [
                {"fixture": "f1", "condition": "C_sei_resume"},
                {"fixture": "f2", "condition": "A_raw_chat"},
                {"fixture": "f3", "condition": "B_chronological_note"},
            ],
        },
    }
    return manifest, {fid: fixture(fid) for fid in ids}


def phase1_response() -> dict:
    return {
        "answers": ["a1", "a2", "a3", "a4", "a5"],
        "operator_observation": {
            "time_to_orientation_seconds": 10.0,
            "source_reopen_count": 0,
            "mental_effort_1_to_5": 2,
        },
    }


def post_response() -> dict:
    return {"answers": ["p1", "p2", "p3", "p4"]}


def audit_response() -> dict:
    return {
        "findings": {
            "current_question_correct": "pass",
            "decision_correct": "pass",
            "recommendation_decision_integrity": "pass",
            "historical_basis_integrity": "pass",
            "unresolved_preservation": "pass",
            "post_decision_temporal_integrity": "pass",
        },
        "operator_observation": {
            "historical_misattribution_count": 0,
            "recommendation_decision_confusion": False,
            "correction_burden": "low",
        },
        "continued_use": "not-observed",
        "continued_use_reason": "",
        "notes": "",
    }


class DecisionContinuityReviewRunnerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest, self.fixtures = matched_set()
        base = new_session(
            self.manifest,
            self.fixtures,
            "R1",
            "decision-review-session",
            "2026-09-18T13:30:00+09:00",
        )
        self.session = attach_review_provenance(
            base,
            "reviewer-opaque-1",
            "none-declared",
            "human-direct",
        )

    def _record_all(self, stage: str, response: dict) -> None:
        for fid in ("f1", "f2", "f3"):
            self.session = record_checked_response(
                self.session,
                self.manifest,
                self.fixtures,
                fid,
                stage,
                "2026-09-18T13:31:00+09:00",
                response,
            )

    def test_phase1_bundle_hides_condition_and_later_material(self) -> None:
        bundle = reviewer_bundle(self.session, self.manifest, self.fixtures)
        self.assertEqual(
            bundle["schema"], "sei.decision-continuity-reviewer-bundle/v0"
        )
        self.assertEqual(bundle["stage"], "phase1")
        self.assertTrue(bundle["review_context"]["clean_blinded_candidate"])
        for item in bundle["items"]:
            packet = item["packet"]
            self.assertNotIn("condition", packet)
            self.assertNotIn("set_id", packet)
            self.assertNotIn("post_decision_evidence", packet)
            self.assertNotIn("reference_state", packet)
            self.assertEqual(len(item["response_template"]["answers"]), 5)
            self.assertEqual(
                item["response_template"]["operator_observation"][
                    "mental_effort_1_to_5"
                ],
                "not-observed",
            )

    def test_known_exposure_is_not_clean_blinded(self) -> None:
        base = new_session(
            self.manifest,
            self.fixtures,
            "R1",
            "known-exposure",
            "2026-09-18T13:30:00+09:00",
        )
        session = attach_review_provenance(
            base,
            "reviewer-opaque-2",
            "known-material-exposure",
            "human-direct",
            "Reviewer saw Decision case material before provenance was fixed.",
        )
        projection = provenance_projection(session)
        self.assertFalse(projection["clean_blinded_candidate"])

    def test_review_start_session_cannot_be_reinitialized_in_place(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "session.json"
            save_new_session(path, self.session)
            with self.assertRaises(InquiryReviewRunnerError):
                save_new_session(path, self.session)

    def test_missing_provenance_cannot_open_bundle(self) -> None:
        session = new_session(
            self.manifest,
            self.fixtures,
            "R1",
            "missing-provenance",
            "2026-09-18T13:30:00+09:00",
        )
        with self.assertRaises(InquiryReviewRunnerError):
            reviewer_bundle(session, self.manifest, self.fixtures)

    def test_decision_validation_and_stage_gate(self) -> None:
        self._record_all("phase1", phase1_response())
        self.assertEqual(current_stage(self.session), "post")
        bundle = reviewer_bundle(self.session, self.manifest, self.fixtures)
        for item in bundle["items"]:
            self.assertIn("post_decision_evidence", item["packet"])
            self.assertNotIn("reference_state", item["packet"])

        self._record_all("post", post_response())
        self.assertEqual(current_stage(self.session), "audit")
        bundle = reviewer_bundle(self.session, self.manifest, self.fixtures)
        for item in bundle["items"]:
            self.assertIn("reference_state", item["packet"])

    def test_invalid_decision_response_is_wrapped_by_shared_runner(self) -> None:
        bad = phase1_response()
        bad["operator_observation"]["mental_effort_1_to_5"] = 9
        with self.assertRaises(InquiryReviewRunnerError):
            record_checked_response(
                self.session,
                self.manifest,
                self.fixtures,
                "f1",
                "phase1",
                "2026-09-18T13:31:00+09:00",
                bad,
            )

    def test_complete_decision_review_exports_separate_evidence_layers(self) -> None:
        self._record_all("phase1", phase1_response())
        self._record_all("post", post_response())
        self._record_all("audit", audit_response())
        self.assertEqual(current_stage(self.session), "complete")

        bundle = evidence_bundle(self.session, self.manifest, self.fixtures)
        self.assertEqual(
            bundle["schema"],
            "sei.decision-continuity-review-evidence-bundle/v0",
        )
        self.assertEqual(len(bundle["human_review_observations"]), 3)
        self.assertEqual(len(bundle["semantic_audits"]), 3)
        self.assertEqual(
            bundle["review_provenance"]["reviewer_id"],
            "reviewer-opaque-1",
        )
        self.assertEqual(
            bundle["evidence_boundaries"]["h1_actual_resume_usability"],
            "not-established-by-this-artifact",
        )
        self.assertEqual(
            bundle["evidence_boundaries"]["product_value"],
            "not-established-by-this-artifact",
        )


if __name__ == "__main__":
    unittest.main()
