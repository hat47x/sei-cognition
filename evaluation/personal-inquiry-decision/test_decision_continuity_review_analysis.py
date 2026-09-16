#!/usr/bin/env python3
from __future__ import annotations

import copy
import unittest
from pathlib import Path

from decision_continuity_preflight import load_decision_set
from decision_continuity_review_analysis import (
    DecisionReviewError,
    comparison_projection,
    validate_decision_session,
)
from matched_review_session import (
    current_stage,
    new_session,
    record_response,
)

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
MANIFEST = HERE / "decision_continuity_counterfactual_matched_set_v1.json"


def load_real_set():
    return load_decision_set(MANIFEST, REPO_ROOT)


def phase1_response(fixture):
    questions = fixture["human_review_template"]["before_post_decision_evidence"]
    return {
        "answers": [f"phase1-answer-{index}" for index, _ in enumerate(questions, 1)],
        "operator_observation": {
            "time_to_orientation_seconds": 12.5,
            "source_reopen_count": 0,
            "mental_effort_1_to_5": 2,
        },
    }


def post_response(fixture):
    questions = fixture["human_review_template"]["after_post_decision_evidence"]
    return {
        "answers": [f"post-answer-{index}" for index, _ in enumerate(questions, 1)]
    }


def audit_response():
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


def complete_session(manifest, fixtures, rotation):
    session = new_session(
        manifest,
        fixtures,
        rotation,
        f"decision-{rotation}",
        "2026-09-16T12:00:00+09:00",
    )
    minute = 0
    for stage in ("phase1", "post", "audit"):
        for assignment in session["assignments"]:
            minute += 1
            fixture = fixtures[assignment["fixture_id"]]
            if stage == "phase1":
                response = phase1_response(fixture)
            elif stage == "post":
                response = post_response(fixture)
            else:
                response = audit_response()
            session = record_response(
                session,
                assignment["fixture_id"],
                stage,
                f"2026-09-16T12:{minute:02d}:00+09:00",
                response,
            )
    return session


class DecisionContinuityReviewAnalysisTest(unittest.TestCase):
    def test_generic_stage_gate_accepts_actual_decision_set(self):
        manifest, fixtures = load_real_set()
        session = new_session(
            manifest,
            fixtures,
            "R1",
            "decision-r1",
            "2026-09-16T12:00:00+09:00",
        )

        validate_decision_session(session, manifest, fixtures)
        self.assertEqual(current_stage(session), "phase1")

    def test_phase1_answer_count_must_match_fixture_questions(self):
        manifest, fixtures = load_real_set()
        session = new_session(
            manifest,
            fixtures,
            "R1",
            "decision-r1",
            "2026-09-16T12:00:00+09:00",
        )
        first = session["assignments"][0]
        fixture = fixtures[first["fixture_id"]]
        bad = phase1_response(fixture)
        bad["answers"] = bad["answers"][:-1]
        session = record_response(
            session,
            first["fixture_id"],
            "phase1",
            "2026-09-16T12:01:00+09:00",
            bad,
        )

        with self.assertRaises(DecisionReviewError):
            validate_decision_session(session, manifest, fixtures)

    def test_audit_requires_post_decision_temporal_integrity_finding(self):
        manifest, fixtures = load_real_set()
        session = complete_session(manifest, fixtures, "R1")
        broken = copy.deepcopy(session)
        del broken["assignments"][0]["records"]["audit"]["response"]["findings"][
            "post_decision_temporal_integrity"
        ]

        with self.assertRaises(DecisionReviewError):
            validate_decision_session(
                broken,
                manifest,
                fixtures,
                require_complete=True,
            )

    def test_full_rotation_projection_is_non_scored_and_counterbalanced(self):
        manifest, fixtures = load_real_set()
        sessions = [
            complete_session(manifest, fixtures, rotation)
            for rotation in ("R1", "R2", "R3")
        ]

        projection = comparison_projection(sessions, manifest, fixtures)

        self.assertTrue(projection["counterbalance_coverage"]["complete"])
        self.assertEqual(
            set(projection["by_condition"]),
            {"A_raw_chat", "B_chronological_note", "C_sei_resume"},
        )
        for group in projection["by_condition"].values():
            self.assertEqual(group["audited_attempts"], 3)
        self.assertNotIn("winner", projection)
        self.assertNotIn("score", projection)
        self.assertEqual(
            projection["evidence_boundaries"]["h1_actual_resume_usability"],
            "not-established-by-this-artifact",
        )

    def test_single_rotation_remains_partial_counterbalance(self):
        manifest, fixtures = load_real_set()
        projection = comparison_projection(
            [complete_session(manifest, fixtures, "R1")],
            manifest,
            fixtures,
        )

        self.assertFalse(projection["counterbalance_coverage"]["complete"])
        self.assertEqual(projection["completed_sessions"], 1)
        self.assertTrue(projection["counterbalance_coverage"]["missing_pairs"])


if __name__ == "__main__":
    unittest.main()
