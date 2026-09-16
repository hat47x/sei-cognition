from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from inquiry_continuity_packet import load_manifest_fixtures
from inquiry_continuity_review_analysis import FINDING_FIELDS
from inquiry_continuity_review_runner import (
    InquiryReviewRunnerError,
    load_context,
    record_checked_response,
    reviewer_bundle,
)
from matched_review_session import current_stage, new_session


CONDITIONS = ("A_raw_chat", "B_chronological_note", "C_sei_resume")


def fixture(fid: str) -> dict:
    return {
        "schema": "sei.inquiry-continuity-comparison-fixture/v0",
        "status": "evaluation-only",
        "issue": "ISSUE-000078",
        "fixture_id": fid,
        "title": fid,
        "scenario": {
            "decision_present": False,
            "post_interruption_evidence": [
                {"at": "2031-01-02T09:00:00+09:00", "role": "observation", "text": "later"}
            ],
        },
        "conditions": {
            "A_raw_chat": {"surface_text": ["raw"]},
            "B_chronological_note": {"surface_text": ["note"]},
            "C_sei_resume": {"surface_text": {"orientation": {"current_question": "q"}}},
        },
        "reference_state": {"must_not_infer": ["certainty"]},
        "human_review_template": {
            "before_post_interruption_evidence": [
                {"id": "R1", "prompt": "before"}
            ],
            "after_post_interruption_evidence": [
                {"id": "R2", "prompt": "after"}
            ],
        },
        "review_key": {"hard_failures": ["rewrite"]},
    }


def phase1_response() -> dict:
    return {
        "answers": ["human answer"],
        "operator_observation": {
            "time_to_orientation_seconds": 1,
            "source_reopen_count": 0,
            "attention_load": "low",
            "first_useful_action_reached": True,
            "reader_context": "original",
        },
    }


def post_response() -> dict:
    return {"answers": ["human answer"]}


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


class InquiryContinuityReviewRunnerTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        entries = []
        for idx in range(1, 4):
            fid = f"f{idx}"
            path = self.root / f"{fid}.json"
            path.write_text(
                json.dumps(fixture(fid), ensure_ascii=False),
                encoding="utf-8",
            )
            entries.append({"id": fid, "path": path.name})
        self.manifest_path = self.root / "manifest.json"
        self.manifest_path.write_text(
            json.dumps(
                {
                    "schema": "sei.inquiry-continuity-matched-set/v0",
                    "status": "evaluation-only",
                    "issue": "ISSUE-000078",
                    "set_id": "runner-test-set",
                    "fixtures": entries,
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
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        self.manifest, self.fixtures = load_manifest_fixtures(
            self.manifest_path,
            self.root,
        )
        self.session = new_session(
            self.manifest,
            self.fixtures,
            "R1",
            "runner-test-session",
            "2026-09-16T21:00:00+09:00",
        )

    def tearDown(self):
        self.tmp.cleanup()

    def _record_all(self, stage: str, response: dict) -> None:
        for fid in ("f1", "f2", "f3"):
            self.session = record_checked_response(
                self.session,
                self.manifest,
                self.fixtures,
                fid,
                stage,
                "2026-09-16T21:01:00+09:00",
                response,
            )

    def test_phase1_bundle_hides_condition_and_later_material(self):
        bundle = reviewer_bundle(self.session, self.manifest, self.fixtures)
        self.assertEqual(bundle["stage"], "phase1")
        self.assertEqual(len(bundle["items"]), 3)
        for item in bundle["items"]:
            packet = item["packet"]
            self.assertNotIn("condition", packet)
            self.assertNotIn("set_id", packet)
            self.assertNotIn("post_interruption_evidence", packet)
            self.assertNotIn("reference_state", packet)
            self.assertEqual(item["response_template"]["answers"], [""])

    def test_empty_phase1_response_cannot_advance_stage(self):
        response = phase1_response()
        response["answers"] = [""]
        with self.assertRaises(InquiryReviewRunnerError):
            record_checked_response(
                self.session,
                self.manifest,
                self.fixtures,
                "f1",
                "phase1",
                "2026-09-16T21:01:00+09:00",
                response,
            )
        self.assertEqual(current_stage(self.session), "phase1")

    def test_post_opens_only_after_all_valid_phase1_responses(self):
        self._record_all("phase1", phase1_response())
        bundle = reviewer_bundle(self.session, self.manifest, self.fixtures)
        self.assertEqual(bundle["stage"], "post")
        for item in bundle["items"]:
            self.assertIn("post_interruption_evidence", item["packet"])
            self.assertNotIn("reference_state", item["packet"])
            self.assertNotIn("condition", item["packet"])

    def test_audit_opens_only_after_all_valid_post_responses(self):
        self._record_all("phase1", phase1_response())
        self._record_all("post", post_response())
        bundle = reviewer_bundle(self.session, self.manifest, self.fixtures)
        self.assertEqual(bundle["stage"], "audit")
        for item in bundle["items"]:
            self.assertIn("reference_state", item["packet"])
            self.assertIn("review_key", item["packet"])
            self.assertNotIn("condition", item["packet"])

    def test_invalid_audit_cannot_complete_session(self):
        self._record_all("phase1", phase1_response())
        self._record_all("post", post_response())
        bad = audit_response()
        bad["findings"][FINDING_FIELDS[0]] = "unknown"
        with self.assertRaises(InquiryReviewRunnerError):
            record_checked_response(
                self.session,
                self.manifest,
                self.fixtures,
                "f1",
                "audit",
                "2026-09-16T21:02:00+09:00",
                bad,
            )
        self.assertEqual(current_stage(self.session), "audit")

    def test_complete_bundle_is_empty(self):
        self._record_all("phase1", phase1_response())
        self._record_all("post", post_response())
        self._record_all("audit", audit_response())
        bundle = reviewer_bundle(self.session, self.manifest, self.fixtures)
        self.assertEqual(bundle["stage"], "complete")
        self.assertEqual(bundle["items"], [])

    def test_non_inquiry_manifest_is_rejected(self):
        bad = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        bad["schema"] = "other/v0"
        path = self.root / "bad-manifest.json"
        path.write_text(json.dumps(bad), encoding="utf-8")
        with self.assertRaises(InquiryReviewRunnerError):
            load_context(path, self.root)


if __name__ == "__main__":
    unittest.main()
