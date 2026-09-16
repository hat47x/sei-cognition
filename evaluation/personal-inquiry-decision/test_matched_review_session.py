#!/usr/bin/env python3
from __future__ import annotations

import copy
import unittest

from matched_review_session import (
    ReviewSessionError,
    build_current_packets,
    current_stage,
    new_session,
    record_response,
    validate_session,
)


def fixture(fid: str) -> dict:
    return {
        "schema": "sei.inquiry-continuity-comparison-fixture/v0",
        "status": "evaluation-only",
        "fixture_id": fid,
        "title": fid,
        "scenario": {"post_interruption_evidence": [{"id": "late"}]},
        "conditions": {
            "A_raw_chat": {"surface_text": "raw"},
            "B_chronological_note": {"surface_text": "note"},
            "C_sei_resume": {"surface_text": "sei"},
        },
        "reference_state": {"must_not_infer": ["certainty"]},
        "human_review_template": {
            "before_post_interruption_evidence": [{"id": "R1"}],
            "after_post_interruption_evidence": [{"id": "R2"}],
        },
        "review_key": {"hard_failures": ["retroactive rewrite"]},
    }


def matched_set():
    ids = ["f1", "f2", "f3"]
    manifest = {
        "schema": "sei.inquiry-continuity-matched-set/v0",
        "status": "evaluation-only",
        "set_id": "set-1",
        "fixtures": [{"id": fid, "path": f"{fid}.json"} for fid in ids],
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


class MatchedReviewSessionTest(unittest.TestCase):
    def setUp(self):
        self.manifest, self.fixtures = matched_set()
        self.session = new_session(
            self.manifest,
            self.fixtures,
            "R1",
            "session-1",
            "2026-09-16T03:00:00Z",
        )

    def _record_all(self, session, stage):
        updated = session
        for index, assignment in enumerate(session["assignments"], start=1):
            updated = record_response(
                updated,
                assignment["fixture_id"],
                stage,
                f"2026-09-16T03:{index:02d}:00Z",
                {"answer": f"{stage}-{index}"},
            )
        return updated

    def test_initial_packets_are_phase1_only(self):
        self.assertEqual(current_stage(self.session), "phase1")
        packets = build_current_packets(self.session, self.manifest, self.fixtures)
        self.assertEqual(len(packets), 3)
        for packet in packets:
            self.assertEqual(packet["stage"], "phase1")
            self.assertIn("surface", packet)
            self.assertNotIn("post_interruption_evidence", packet)
            self.assertNotIn("reference_state", packet)

    def test_post_is_blocked_until_all_phase1_responses_are_fixed(self):
        first = self.session["assignments"][0]["fixture_id"]
        with self.assertRaises(ReviewSessionError):
            record_response(
                self.session,
                first,
                "post",
                "2026-09-16T03:01:00Z",
                {"answer": "too early"},
            )

        partial = record_response(
            self.session,
            first,
            "phase1",
            "2026-09-16T03:01:00Z",
            {"answer": "fixed"},
        )
        self.assertEqual(current_stage(partial), "phase1")
        self.assertEqual(
            len(build_current_packets(partial, self.manifest, self.fixtures)),
            2,
        )

    def test_global_stage_gate_reaches_post_then_audit_then_complete(self):
        phase1_done = self._record_all(self.session, "phase1")
        self.assertEqual(current_stage(phase1_done), "post")
        post_packets = build_current_packets(
            phase1_done, self.manifest, self.fixtures
        )
        self.assertTrue(post_packets)
        for packet in post_packets:
            self.assertIn("post_interruption_evidence", packet)
            self.assertNotIn("reference_state", packet)

        post_done = self._record_all(phase1_done, "post")
        self.assertEqual(current_stage(post_done), "audit")
        audit_packets = build_current_packets(post_done, self.manifest, self.fixtures)
        for packet in audit_packets:
            self.assertIn("reference_state", packet)
            self.assertIn("review_key", packet)

        audit_done = self._record_all(post_done, "audit")
        self.assertEqual(current_stage(audit_done), "complete")
        self.assertEqual(
            build_current_packets(audit_done, self.manifest, self.fixtures), []
        )

    def test_fixed_response_cannot_be_overwritten(self):
        first = self.session["assignments"][0]["fixture_id"]
        updated = record_response(
            self.session,
            first,
            "phase1",
            "2026-09-16T03:01:00Z",
            {"answer": "first"},
        )
        with self.assertRaises(ReviewSessionError):
            record_response(
                updated,
                first,
                "phase1",
                "2026-09-16T03:02:00Z",
                {"answer": "overwrite"},
            )

    def test_source_snapshot_detects_fixture_change(self):
        changed = copy.deepcopy(self.fixtures)
        changed["f1"]["title"] = "changed after init"
        with self.assertRaises(ReviewSessionError):
            validate_session(self.session, self.manifest, changed)

    def test_source_snapshot_detects_manifest_change(self):
        changed = copy.deepcopy(self.manifest)
        changed["set_id"] = "set-2"
        with self.assertRaises(ReviewSessionError):
            validate_session(self.session, changed, self.fixtures)


if __name__ == "__main__":
    unittest.main()
