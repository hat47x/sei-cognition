from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from inquiry_continuity_summary_distortion_probe import (
    REQUIRED_KINDS,
    SummaryDistortionProbeError,
    build_audit_packet,
    build_review_packet,
    git_blob_sha1,
    load_sources,
    response_sha256,
    validate_probe,
)


class SummaryDistortionProbeTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.fixture_id = "f1"
        self.fixture_path = self.root / "fixture.json"
        fixture = {
            "schema": "sei.inquiry-continuity-comparison-fixture/v0",
            "status": "evaluation-only",
            "fixture_id": self.fixture_id,
            "scenario": {
                "decision_present": False,
                "post_interruption_evidence": [{"role": "observation", "text": "later"}],
            },
            "conditions": {
                "C_sei_resume": {
                    "surface_text": {
                        "orientation": {
                            "current_question": "q",
                            "open_unknowns": ["u"],
                            "hypotheses": ["h"],
                            "decision": None,
                        }
                    }
                }
            },
            "reference_state": {"must_not_infer": ["certainty"]},
        }
        self.fixture_path.write_text(json.dumps(fixture), encoding="utf-8")
        raw = self.fixture_path.read_bytes()
        self.probe = {
            "schema": "sei.inquiry-continuity-summary-distortion-probe/v0",
            "status": "evaluation-only",
            "issue": "ISSUE-000078",
            "probe_id": "test-probe",
            "semantic_stopline": {
                "distorted_summary_is_canonical": False,
                "ai_summary_may_overwrite_source": False,
                "correction_may_mutate_historical_state": False,
                "overall_score_or_winner_allowed": False,
                "stable_requirement_change_authorized": False,
            },
            "cases": [
                {
                    "fixture_id": self.fixture_id,
                    "path": "fixture.json",
                    "blob_sha1": git_blob_sha1(raw),
                    "distorted_summary": "wrong summary",
                    "distortion_key": [
                        {"kind": "hypothesis_to_certainty", "detail": "x"},
                        {"kind": "alternate_hypothesis_omission", "detail": "x"},
                        {"kind": "temporal_backfill", "detail": "x"},
                    ],
                },
                {
                    "fixture_id": "f2",
                    "path": "fixture.json",
                    "blob_sha1": git_blob_sha1(raw),
                    "distorted_summary": "wrong summary 2",
                    "distortion_key": [
                        {"kind": "hypothesis_to_certainty", "detail": "x"},
                        {"kind": "alternate_hypothesis_omission", "detail": "x"},
                        {"kind": "temporal_backfill", "detail": "x"},
                    ],
                },
                {
                    "fixture_id": "f3",
                    "path": "fixture.json",
                    "blob_sha1": git_blob_sha1(raw),
                    "distorted_summary": "wrong summary 3",
                    "distortion_key": [
                        {"kind": "hypothesis_to_certainty", "detail": "x"},
                        {"kind": "alternate_hypothesis_omission", "detail": "x"},
                        {"kind": "temporal_backfill", "detail": "x"},
                    ],
                },
            ],
            "review_questions": [{"id": f"D{i}", "prompt": "q"} for i in range(1, 6)],
            "audit_dimensions": ["temporal_backfill_detection"],
            "evidence_boundary": {"human_review": "not-yet-observed"},
        }

    def tearDown(self):
        self.tmp.cleanup()

    def test_probe_requires_three_core_distortion_types(self):
        validate_probe(self.probe)
        kinds = {item["kind"] for item in self.probe["cases"][0]["distortion_key"]}
        self.assertTrue(REQUIRED_KINDS.issubset(kinds))

    def test_semantic_stopline_cannot_make_summary_canonical(self):
        bad = copy.deepcopy(self.probe)
        bad["semantic_stopline"]["distorted_summary_is_canonical"] = True
        with self.assertRaises(SummaryDistortionProbeError):
            validate_probe(bad)

    def test_source_freeze_rejects_changed_fixture(self):
        single = copy.deepcopy(self.probe)
        for idx, case in enumerate(single["cases"]):
            case["fixture_id"] = f"x{idx}"
        # Validation is independent from source loading; changed bytes must fail before use.
        self.fixture_path.write_text("{}", encoding="utf-8")
        with self.assertRaises(SummaryDistortionProbeError):
            load_sources(single, self.root)

    def test_review_packet_hides_audit_key_and_later_evidence(self):
        fixture = json.loads(self.fixture_path.read_text(encoding="utf-8"))
        packet = build_review_packet(self.probe, {self.fixture_id: fixture}, self.fixture_id)
        self.assertEqual(packet["stage"], "review")
        self.assertIn("canonical_orientation", packet)
        self.assertIn("provisional_ai_summary", packet)
        self.assertNotIn("distortion_key", packet)
        self.assertNotIn("reference_state", packet)
        self.assertNotIn("post_interruption_evidence", packet)

    def test_audit_requires_fixed_nonempty_human_response(self):
        fixture = json.loads(self.fixture_path.read_text(encoding="utf-8"))
        response = self.root / "response.json"
        response.write_text("{}", encoding="utf-8")
        with self.assertRaises(SummaryDistortionProbeError):
            build_audit_packet(self.probe, {self.fixture_id: fixture}, self.fixture_id, response)
        response.write_text(json.dumps({"answers": ["human"]}), encoding="utf-8")
        packet = build_audit_packet(
            self.probe, {self.fixture_id: fixture}, self.fixture_id, response
        )
        self.assertEqual(packet["stage"], "audit")
        self.assertEqual(
            packet["fixed_human_response_sha256"],
            hashlib.sha256(response.read_bytes()).hexdigest(),
        )
        self.assertIn("distortion_key", packet)
        self.assertIn("reference_state", packet)

    def test_response_hash_rejects_non_object(self):
        response = self.root / "response.json"
        response.write_text("[]", encoding="utf-8")
        with self.assertRaises(SummaryDistortionProbeError):
            response_sha256(response)


if __name__ == "__main__":
    unittest.main()
