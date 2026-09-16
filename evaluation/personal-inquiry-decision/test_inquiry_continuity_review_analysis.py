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
from matched_review_session import new_session, record_response

CONDITIONS = ("A_raw_chat", "B_chronological_note", "C_sei_resume")
FIXTURES = ("f1", "f2", "f3")


def fixture(fid: str) -> dict:
    return {
        "schema": "sei.inquiry-continuity-comparison-fixture/v0",
        "status": "evaluation-only",
        "fixture_id": fid,
        "title": fid,
        "scenario": {
            "post_interruption_evidence": [
                {"at": "2031-01-02T00:00:00+00:00", "text": "later evidence"}
            ],
        },
        "conditions": {
            "A_raw_chat": {"surface_text": ["raw"]},
            "B_chronological_note": {"surface_text": ["note"]},
            "C_sei_resume": {"surface_text": {"orientation": "resume"}},
        },
        "reference_state": {"unresolved": ["still open"]},
        "human_review_template": {
            "before_post_interruption_evidence": [
                {"id": "R1"}, {"id": "R2"}
            ],
            "after_post_interruption_evidence": [
                {"id": "R3"}
            ],
        },
        "review_key": {"hard_failures": ["false continuity"]},
    }


def manifest() -> dict:
    return {
        "schema": "sei.inquiry-continuity-matched-set/v0",
        "status": "evaluation-only",
        "set_id": "set-1",
        "fixtures": [
            {"id": fid, "path": f"{fid}.json"}
            for fid in FIXTURES
        ],
        "condition_codes": {name: name for name in CONDITIONS},
        "assignment_rotations": {
            "R1": [
                {"fixture": "f1", "condition": CONDITIONS[0]},
                {"fixture": "f2", "condition": CONDITIONS[1]},
                {"fixture": "f3", "condition": CONDITIONS[2]},
            ],
            "R2": [
                {"fixture": "f1", "condition": CONDITIONS[1]},
                {"fixture": "f2", "condition": CONDITIONS[2]},
                {"fixture": "f3", "condition": CONDITIONS[0]},
            ],
            "R3": [
                {"fixture": "f1", "condition": CONDITIONS[2]},
                {"fixture": "f2", "condition": CONDITIONS[0]},
                {"fixture": "f3", "condition": CONDITIONS[1]},
            ],
        },
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


def completed_session(
    manifest_value: dict,
    fixtures: dict[str, dict],
    session_id: str,
    rotation: str,
    *,
    handoff: bool = False,
) -> dict:
    value = new_session(
        manifest_value,
        fixtures,
        rotation,
        session_id,
        "2031-01-01T00:00:00+00:00",
    )
    fixture_ids = [item["fixture_id"] for item in value["assignments"]]
    for index, fid in enumerate(fixture_ids):
        value = record_response(
            value,
            fid,
            "phase1",
            f"2031-01-01T00:00:{index + 1:02d}+00:00",
            phase1_response("handoff" if handoff and index == 0 else "original"),
        )
    for index, fid in enumerate(fixture_ids):
        value = record_response(
            value,
            fid,
            "post",
            f"2031-01-01T00:01:{index + 1:02d}+00:00",
            post_response(),
        )
    for index, fid in enumerate(fixture_ids):
        value = record_response(
            value,
            fid,
            "audit",
            f"2031-01-01T00:02:{index + 1:02d}+00:00",
            audit_response(),
        )
    return value


class InquiryContinuityReviewAnalysisTest(unittest.TestCase):
    def setUp(self):
        self.manifest = manifest()
        self.fixtures = {fid: fixture(fid) for fid in FIXTURES}

    def make_session(
        self,
        session_id: str,
        rotation: str,
        *,
        handoff: bool = False,
    ) -> dict:
        return completed_session(
            self.manifest,
            self.fixtures,
            session_id,
            rotation,
            handoff=handoff,
        )

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
            self.make_session("s1", "R1", handoff=True),
            self.make_session("s2", "R2"),
            self.make_session("s3", "R3"),
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
            [self.make_session("s1", "R1")],
            self.manifest,
            self.fixtures,
        )
        self.assertFalse(projection["counterbalance_coverage"]["complete"])
        self.assertEqual(
            projection["counterbalance_coverage"]["observed_pairs"], 3
        )

    def test_duplicate_session_id_is_rejected(self):
        sessions = [
            self.make_session("same", "R1"),
            self.make_session("same", "R2"),
        ]
        with self.assertRaises(InquiryReviewError):
            comparison_projection(sessions, self.manifest, self.fixtures)

    def test_invalid_nested_response_is_attributed_to_fixture_and_stage(self):
        broken = self.make_session("s1", "R1")
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
