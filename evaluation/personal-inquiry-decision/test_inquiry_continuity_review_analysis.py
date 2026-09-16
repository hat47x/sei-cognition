from __future__ import annotations

import copy
import unittest

from inquiry_continuity_review_analysis import (
    FINDING_FIELDS,
    InquiryReviewError,
    comparison_projection,
    response_template,
    validate_inquiry_response,
    validate_inquiry_session,
)

CONDITIONS = ("A_raw_chat", "B_chronological_note", "C_sei_resume")
FIXTURES = ("f1", "f2", "f3")


def fixture(fid: str) -> dict:
    return {
        "schema": "sei.inquiry-continuity-comparison-fixture/v0",
        "status": "evaluation-only",
        "fixture_id": fid,
        "human_review_template": {
            "before_post_interruption_evidence": [
                {"id": "R1"}, {"id": "R2"}
            ],
            "after_post_interruption_evidence": [
                {"id": "R3"}
            ],
        },
    }


def manifest() -> dict:
    return {
        "schema": "sei.inquiry-continuity-matched-set/v0",
        "set_id": "set-1",
        "condition_codes": {name: name for name in CONDITIONS},
    }


def phase1_response(reader_context: str = "original") -> dict:
    return {
        "answers": ["a1", "a2"],
        "operator_observation": {
            "time_to_orientation_seconds": 12.5,
            "source_reopen_count": 1,
            "attention_load": "medium",
            "first_useful_action_reached": True,
            "reader_context": reader_context,
        },
    }


def post_response() -> dict:
    return {"answers": ["post"]}


def audit_response() -> dict:
    return {
        "findings": {field: "pass" for field in FINDING_FIELDS},
        "operator_observation": {
            "historical_misattribution_count": 0,
            "role_confusion_count": 0,
            "unresolved_omission_count": 0,
            "correction_burden": "low",
        },
        "notes": "",
    }


def session(session_id: str, rotation: str, offset: int, handoff: bool = False) -> dict:
    assignments = []
    for i, fid in enumerate(FIXTURES):
        condition = CONDITIONS[(i + offset) % len(CONDITIONS)]
        assignments.append({
            "fixture_id": fid,
            "condition": condition,
            "records": {
                "phase1": {
                    "recorded_at": "2031-01-01T00:00:00+00:00",
                    "response": phase1_response(
                        "handoff" if handoff and i == 0 else "original"
                    ),
                },
                "post": {
                    "recorded_at": "2031-01-01T00:01:00+00:00",
                    "response": post_response(),
                },
                "audit": {
                    "recorded_at": "2031-01-01T00:02:00+00:00",
                    "response": audit_response(),
                },
            },
        })
    return {
        "schema": "sei.matched-review-session/v0",
        "status": "evaluation-only",
        "session_id": session_id,
        "manifest_schema": "sei.inquiry-continuity-matched-set/v0",
        "set_id": "set-1",
        "rotation": rotation,
        "created_at": "2031-01-01T00:00:00+00:00",
        "source_snapshot": {},
        "assignments": assignments,
    }


class InquiryContinuityReviewAnalysisTest(unittest.TestCase):
    def setUp(self):
        self.manifest = manifest()
        self.fixtures = {fid: fixture(fid) for fid in FIXTURES}

    def test_response_templates_do_not_fabricate_answers(self):
        phase1 = response_template("phase1", self.fixtures["f1"])
        self.assertEqual(phase1["answers"], ["", ""])
        self.assertEqual(
            phase1["operator_observation"]["reader_context"],
            "not-observed",
        )
        audit = response_template("audit", self.fixtures["f1"])
        self.assertTrue(all(v == "not-observed" for v in audit["findings"].values()))

    def test_phase1_requires_valid_attention_and_reader_context(self):
        response = phase1_response()
        validate_inquiry_response("phase1", response, self.fixtures["f1"])
        bad = copy.deepcopy(response)
        bad["operator_observation"]["attention_load"] = "tiny"
        with self.assertRaises(InquiryReviewError):
            validate_inquiry_response("phase1", bad, self.fixtures["f1"])
        bad = copy.deepcopy(response)
        bad["operator_observation"]["reader_context"] = "same-session"
        with self.assertRaises(InquiryReviewError):
            validate_inquiry_response("phase1", bad, self.fixtures["f1"])

    def test_audit_findings_are_exact_and_non_scored(self):
        response = audit_response()
        validate_inquiry_response("audit", response, self.fixtures["f1"])
        bad = copy.deepcopy(response)
        bad["findings"]["overall_score"] = "pass"
        with self.assertRaises(InquiryReviewError):
            validate_inquiry_response("audit", bad, self.fixtures["f1"])

    def test_complete_three_rotation_projection_has_full_pair_coverage(self):
        sessions = [
            session("s1", "R1", 0, handoff=True),
            session("s2", "R2", 1),
            session("s3", "R3", 2),
        ]
        projection = comparison_projection(
            sessions,
            self.manifest,
            self.fixtures,
        )
        self.assertTrue(projection["counterbalance_coverage"]["complete"])
        self.assertEqual(
            projection["counterbalance_coverage"]["observed_pairs"], 9
        )
        self.assertEqual(
            projection["handoff_observation"]["synthetic_handoff_attempts"], 1
        )
        self.assertNotIn("winner", projection)
        self.assertNotIn("score", projection)
        self.assertEqual(
            projection["evidence_boundaries"]["product_value"],
            "not-established-by-this-artifact",
        )

    def test_single_rotation_remains_incomplete_coverage(self):
        projection = comparison_projection(
            [session("s1", "R1", 0)],
            self.manifest,
            self.fixtures,
        )
        self.assertFalse(projection["counterbalance_coverage"]["complete"])
        self.assertEqual(
            projection["counterbalance_coverage"]["observed_pairs"], 3
        )

    def test_duplicate_session_id_is_rejected(self):
        sessions = [
            session("same", "R1", 0),
            session("same", "R2", 1),
        ]
        with self.assertRaises(InquiryReviewError):
            comparison_projection(sessions, self.manifest, self.fixtures)

    def test_invalid_nested_response_is_attributed_to_fixture_and_stage(self):
        broken = session("s1", "R1", 0)
        broken["assignments"][0]["records"]["phase1"]["response"]["answers"] = [""]
        with self.assertRaisesRegex(
            InquiryReviewError, "f1/phase1"
        ):
            validate_inquiry_session(
                broken,
                self.manifest,
                self.fixtures,
                require_complete=True,
            )


if __name__ == "__main__":
    unittest.main()
