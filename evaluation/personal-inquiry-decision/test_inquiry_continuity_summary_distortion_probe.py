from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from inquiry_continuity_summary_distortion_probe import (
    AUDIT_REVEAL_RECEIPT_SCHEMA,
    REVIEW_START_RECEIPT_SCHEMA,
    REQUIRED_KINDS,
    RESPONSE_SCHEMA,
    SummaryDistortionProbeError,
    audit_material_sha256,
    build_audit_material,
    build_audit_packet,
    build_audit_reveal_receipt,
    build_review_packet,
    build_review_start_receipt,
    git_blob_sha1,
    load_sources,
    probe_content_sha256,
    response_sha256,
    response_template,
    review_start_receipt_bytes,
    save_audit_reveal_receipt,
    save_review_start_receipt,
    validate_human_response,
    validate_human_response_against_review_start,
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
                "post_interruption_evidence": [
                    {"role": "observation", "text": "later"}
                ],
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
            "presentation_rules": [
                "matched review first when the same reader is used",
                "fix the human response before audit material is revealed",
            ],
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
                    "distorted_next_question": "wrong next question?",
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
                    "distorted_next_question": "wrong next question 2?",
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
                    "distorted_next_question": "wrong next question 3?",
                    "distortion_key": [
                        {"kind": "hypothesis_to_certainty", "detail": "x"},
                        {"kind": "alternate_hypothesis_omission", "detail": "x"},
                        {"kind": "temporal_backfill", "detail": "x"},
                    ],
                },
            ],
            "review_questions": [
                {"id": f"D{i}", "prompt": "q"} for i in range(1, 6)
            ],
            "audit_dimensions": [
                "temporal_backfill_detection",
                "correction_burden",
            ],
            "interpretation_stoplines": [
                "do not collapse detections into one score",
                "human review is not yet Product Value evidence",
            ],
            "evidence_boundary": {"human_review": "not-yet-observed"},
        }
        self.review_receipt_path = self.root / "review-start.json"
        self.review_receipt = build_review_start_receipt(
            self.probe,
            self.fixture_id,
            "reviewer-opaque-1",
            "known-material-exposure",
            "human-direct",
            "2026-09-18T02:50:00Z",
        )
        save_review_start_receipt(
            self.review_receipt_path,
            self.review_receipt,
        )
        self.review_receipt_raw = self.review_receipt_path.read_bytes()
        self.review_receipt_sha = hashlib.sha256(
            self.review_receipt_raw
        ).hexdigest()

    def tearDown(self):
        self.tmp.cleanup()

    def valid_response(self) -> dict:
        response = response_template(
            self.probe,
            self.review_receipt,
            self.review_receipt_raw,
        )
        response["answers"] = [f"answer-{i}" for i in range(1, 6)]
        response["review_provenance"]["note"] = "pilot"
        response["operator_observation"] = {
            "review_completion_seconds": 42.5,
            "source_reopen_count": 1,
            "correction_burden": "medium",
        }
        response["notes"] = "reviewed without treating the stimulus as canonical"
        return response

    def test_probe_requires_three_core_distortion_types(self):
        validate_probe(self.probe)
        kinds = {
            item["kind"]
            for item in self.probe["cases"][0]["distortion_key"]
        }
        self.assertTrue(REQUIRED_KINDS.issubset(kinds))

    def test_probe_requires_next_question_and_presentation_rules(self):
        no_question = copy.deepcopy(self.probe)
        del no_question["cases"][0]["distorted_next_question"]
        with self.assertRaises(SummaryDistortionProbeError):
            validate_probe(no_question)

        no_rules = copy.deepcopy(self.probe)
        no_rules["presentation_rules"] = []
        with self.assertRaises(SummaryDistortionProbeError):
            validate_probe(no_rules)

    def test_semantic_stopline_cannot_make_summary_canonical(self):
        bad = copy.deepcopy(self.probe)
        bad["semantic_stopline"]["distorted_summary_is_canonical"] = True
        with self.assertRaises(SummaryDistortionProbeError):
            validate_probe(bad)

    def test_source_freeze_rejects_changed_fixture(self):
        single = copy.deepcopy(self.probe)
        for idx, case in enumerate(single["cases"]):
            case["fixture_id"] = f"x{idx}"
        self.fixture_path.write_text("{}", encoding="utf-8")
        with self.assertRaises(SummaryDistortionProbeError):
            load_sources(single, self.root)

    def test_review_packet_exposes_stimulus_template_but_hides_audit_material(self):
        fixture = json.loads(
            self.fixture_path.read_text(encoding="utf-8")
        )
        packet = build_review_packet(
            self.probe,
            {self.fixture_id: fixture},
            self.fixture_id,
            self.review_receipt_path,
        )
        self.assertEqual(packet["stage"], "review")
        self.assertEqual(
            packet["review_start_receipt_sha256"],
            self.review_receipt_sha,
        )
        self.assertEqual(
            packet["review_provenance_declaration"]["prior_exposure"],
            "known-material-exposure",
        )
        self.assertIn("canonical_orientation", packet)
        self.assertIn("provisional_ai_summary", packet)
        self.assertIn("provisional_ai_next_question", packet)
        self.assertEqual(
            packet["presentation_rules"],
            self.probe["presentation_rules"],
        )
        self.assertIn("interpretation_stoplines", packet)
        self.assertEqual(packet["response_template"]["schema"], RESPONSE_SCHEMA)
        self.assertEqual(
            packet["probe_sha256"],
            probe_content_sha256(self.probe),
        )
        self.assertEqual(
            packet["response_template"]["probe_sha256"],
            probe_content_sha256(self.probe),
        )
        self.assertEqual(len(packet["response_template"]["answers"]), 5)
        self.assertNotIn("distortion_key", packet)
        self.assertNotIn("reference_state", packet)
        self.assertNotIn("post_interruption_evidence", packet)

    def test_response_template_is_intentionally_invalid_until_human_fields_are_filled(self):
        template = response_template(
            self.probe,
            self.review_receipt,
            self.review_receipt_raw,
        )
        with self.assertRaises(SummaryDistortionProbeError):
            validate_human_response(template, self.probe)

    def test_response_requires_one_nonempty_answer_per_question(self):
        response = self.valid_response()
        response["answers"] = response["answers"][:-1]
        with self.assertRaises(SummaryDistortionProbeError):
            validate_human_response(response, self.probe)

        response = self.valid_response()
        response["answers"][2] = ""
        with self.assertRaises(SummaryDistortionProbeError):
            validate_human_response(response, self.probe)

    def test_response_is_bound_to_exact_probe_content(self):
        response = self.valid_response()
        changed = copy.deepcopy(self.probe)
        changed["cases"][0]["distorted_summary"] = "changed after review"
        with self.assertRaises(SummaryDistortionProbeError):
            validate_human_response(response, changed)

    def test_response_requires_declared_human_provenance(self):
        response = self.valid_response()
        response["review_provenance"]["response_authorship"] = "ai-generated"
        with self.assertRaises(SummaryDistortionProbeError):
            validate_human_response(response, self.probe)

        response = self.valid_response()
        response["review_provenance"]["reviewer_id"] = ""
        with self.assertRaises(SummaryDistortionProbeError):
            validate_human_response(response, self.probe)

    def test_response_validates_correction_burden_observations(self):
        response = self.valid_response()
        response["operator_observation"]["source_reopen_count"] = -1
        with self.assertRaises(SummaryDistortionProbeError):
            validate_human_response(response, self.probe)

        response = self.valid_response()
        response["operator_observation"]["correction_burden"] = "tiny"
        with self.assertRaises(SummaryDistortionProbeError):
            validate_human_response(response, self.probe)

    def test_audit_requires_fixed_structured_human_response(self):
        fixture = json.loads(
            self.fixture_path.read_text(encoding="utf-8")
        )
        response = self.root / "response.json"
        response.write_text(
            json.dumps({"answers": ["human"]}),
            encoding="utf-8",
        )
        with self.assertRaises(SummaryDistortionProbeError):
            build_audit_packet(
                self.probe,
                {self.fixture_id: fixture},
                self.fixture_id,
                response,
                self.review_receipt_path,
                self.root / "missing-receipt.json",
            )

        value = self.valid_response()
        response.write_text(json.dumps(value), encoding="utf-8")
        receipt_path = self.root / "receipt.json"
        material = build_audit_material(
            self.probe,
            {self.fixture_id: fixture},
            self.fixture_id,
        )
        receipt = build_audit_reveal_receipt(
            self.probe,
            self.fixture_id,
            response,
            audit_material_sha256(material),
            "2026-09-18T02:55:00Z",
        )
        save_audit_reveal_receipt(receipt_path, receipt)
        packet = build_audit_packet(
            self.probe,
            {self.fixture_id: fixture},
            self.fixture_id,
            response,
            self.review_receipt_path,
            receipt_path,
        )
        self.assertEqual(packet["stage"], "audit")
        self.assertEqual(receipt["schema"], AUDIT_REVEAL_RECEIPT_SCHEMA)
        self.assertEqual(
            packet["audit_revealed_at"],
            "2026-09-18T02:55:00Z",
        )
        self.assertEqual(
            packet["audit_reveal_receipt_sha256"],
            hashlib.sha256(receipt_path.read_bytes()).hexdigest(),
        )
        self.assertEqual(
            packet["audit_material_sha256"],
            audit_material_sha256(material),
        )
        self.assertEqual(
            packet["probe_sha256"],
            probe_content_sha256(self.probe),
        )
        self.assertEqual(
            packet["fixed_human_response_sha256"],
            hashlib.sha256(response.read_bytes()).hexdigest(),
        )
        self.assertEqual(
            packet["review_provenance"]["reviewer_id"],
            "reviewer-opaque-1",
        )
        self.assertEqual(
            packet["operator_observation"]["correction_burden"],
            "medium",
        )
        self.assertIn("not independent proof", packet["provenance_stopline"])
        self.assertIn("distortion_key", packet)
        self.assertIn("reference_state", packet)
        self.assertIn("interpretation_stoplines", packet)

    def test_audit_reveal_receipt_never_overwrites(self):
        response = self.root / "response.json"
        response.write_text(json.dumps(self.valid_response()), encoding="utf-8")
        fixture = json.loads(
            self.fixture_path.read_text(encoding="utf-8")
        )
        material = build_audit_material(
            self.probe,
            {self.fixture_id: fixture},
            self.fixture_id,
        )
        receipt = build_audit_reveal_receipt(
            self.probe,
            self.fixture_id,
            response,
            audit_material_sha256(material),
            "2026-09-18T02:55:00Z",
        )
        target = self.root / "receipt.json"
        save_audit_reveal_receipt(target, receipt)
        original = target.read_text(encoding="utf-8")
        with self.assertRaises(SummaryDistortionProbeError):
            save_audit_reveal_receipt(target, receipt)
        self.assertEqual(target.read_text(encoding="utf-8"), original)

    def test_receipt_rejects_changed_audit_material(self):
        fixture = json.loads(
            self.fixture_path.read_text(encoding="utf-8")
        )
        response = self.root / "response.json"
        response.write_text(json.dumps(self.valid_response()), encoding="utf-8")
        material = build_audit_material(
            self.probe,
            {self.fixture_id: fixture},
            self.fixture_id,
        )
        receipt = build_audit_reveal_receipt(
            self.probe,
            self.fixture_id,
            response,
            audit_material_sha256(material),
            "2026-09-18T02:55:00Z",
        )
        target = self.root / "receipt.json"
        save_audit_reveal_receipt(target, receipt)
        changed = copy.deepcopy(fixture)
        changed["reference_state"] = {"changed": True}
        with self.assertRaises(SummaryDistortionProbeError):
            build_audit_packet(
                self.probe,
                {self.fixture_id: changed},
                self.fixture_id,
                response,
                self.review_receipt_path,
                target,
            )

    def test_review_start_receipt_never_overwrites(self):
        target = self.root / "other-review-start.json"
        save_review_start_receipt(target, self.review_receipt)
        original = target.read_bytes()
        with self.assertRaises(SummaryDistortionProbeError):
            save_review_start_receipt(target, self.review_receipt)
        self.assertEqual(target.read_bytes(), original)

    def test_response_rejects_post_stimulus_provenance_rewrite(self):
        response = self.valid_response()
        response["review_provenance"]["prior_exposure"] = "none-declared"
        with self.assertRaises(SummaryDistortionProbeError):
            validate_human_response_against_review_start(
                response,
                self.probe,
                self.fixture_id,
                self.review_receipt,
                self.review_receipt_raw,
            )

    def test_response_hash_rejects_non_object(self):
        response = self.root / "response.json"
        response.write_text("[]", encoding="utf-8")
        with self.assertRaises(SummaryDistortionProbeError):
            response_sha256(response, self.probe)


if __name__ == "__main__":
    unittest.main()
