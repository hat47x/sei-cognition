from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from inquiry_continuity_summary_distortion_probe import (
    audit_material_sha256,
    build_audit_material,
    build_audit_reveal_receipt,
    build_review_start_receipt,
    probe_content_sha256,
    response_template,
    save_audit_reveal_receipt,
    save_review_start_receipt,
)

from inquiry_continuity_summary_distortion_evidence import (
    AUDIT_RESPONSE_SCHEMA,
    EVIDENCE_SCHEMA,
    SummaryDistortionEvidenceError,
    audit_response_template,
    build_evidence_bundle,
    save_bundle,
    validate_audit_response,
)


class SummaryDistortionEvidenceTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.fixture_id = "f1"
        core_key = [
            {"kind": "hypothesis_to_certainty", "detail": "x"},
            {"kind": "alternate_hypothesis_omission", "detail": "y"},
            {"kind": "temporal_backfill", "detail": "z"},
        ]
        self.probe = {
            "schema": "sei.inquiry-continuity-summary-distortion-probe/v0",
            "status": "evaluation-only",
            "issue": "ISSUE-000078",
            "probe_id": "probe-1",
            "presentation_rules": [
                "fix the human response before audit material is revealed"
            ],
            "interpretation_stoplines": [
                "human review is not Product Value evidence"
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
                    "fixture_id": f"f{i}",
                    "path": f"fixture-{i}.json",
                    "blob_sha1": chr(96 + i) * 40,
                    "distorted_summary": f"wrong summary {i}",
                    "distorted_next_question": f"wrong next question {i}?",
                    "distortion_key": core_key,
                }
                for i in range(1, 4)
            ],
            "review_questions": [
                {"id": f"D{i}", "prompt": f"question {i}"}
                for i in range(1, 6)
            ],
            "audit_dimensions": [
                "hypothesis_to_certainty_detection",
                "alternate_hypothesis_preservation",
                "correction_burden",
            ],
            "evidence_boundary": {
                "human_review": "not-yet-observed",
                "product_value": "not-established",
            },
        }
        self.fixtures = {
            self.fixture_id: {
                "reference_state": {"must_not_infer": ["certainty"]},
                "scenario": {
                    "post_interruption_evidence": [
                        {"role": "observation", "text": "later"}
                    ]
                },
            }
        }
        self.review_receipt_path = self.root / "review-start.json"
        self.review_receipt = build_review_start_receipt(
            self.probe,
            self.fixture_id,
            "reviewer-opaque-1",
            "known-material-exposure",
            "human-direct",
            "2026-09-17T09:28:00Z",
        )
        save_review_start_receipt(
            self.review_receipt_path,
            self.review_receipt,
        )
        self.review_receipt_raw = self.review_receipt_path.read_bytes()
        self.review_receipt_sha = hashlib.sha256(
            self.review_receipt_raw
        ).hexdigest()
        self.human_response = response_template(
            self.probe,
            self.review_receipt,
            self.review_receipt_raw,
        )
        self.human_response["answers"] = [
            f"answer-{i}" for i in range(1, 6)
        ]
        self.human_response["review_provenance"]["note"] = "pilot"
        self.human_response["operator_observation"] = {
            "review_completion_seconds": 10,
            "source_reopen_count": 1,
            "correction_burden": "medium",
        }
        self.human_response["notes"] = "initial review"
        self.human_path = self.root / "human.json"
        self.human_path.write_text(
            json.dumps(self.human_response, ensure_ascii=False),
            encoding="utf-8",
        )
        self.human_sha = hashlib.sha256(self.human_path.read_bytes()).hexdigest()
        self.receipt_path = self.root / "receipt.json"
        self.audit_material = build_audit_material(
            self.probe,
            self.fixtures,
            self.fixture_id,
        )
        self.audit_material_sha = audit_material_sha256(self.audit_material)
        receipt = build_audit_reveal_receipt(
            self.probe,
            self.fixture_id,
            self.human_path,
            self.review_receipt,
            self.review_receipt_raw,
            self.audit_material_sha,
            "2026-09-17T09:29:00Z",
        )
        save_audit_reveal_receipt(self.receipt_path, receipt)
        self.receipt_sha = hashlib.sha256(
            self.receipt_path.read_bytes()
        ).hexdigest()

    def tearDown(self):
        self.tmp.cleanup()

    def valid_audit(self) -> dict:
        value = audit_response_template(
            self.probe,
            self.fixture_id,
            self.human_sha,
            self.receipt_sha,
        )
        value["findings"] = {
            "hypothesis_to_certainty_detection": "pass",
            "alternate_hypothesis_preservation": "fail",
            "correction_burden": "not-observed",
        }
        value["audit_provenance"] = {
            "auditor_id": "auditor-opaque-1",
            "response_authorship": "human-direct",
            "completed_at": "2026-09-17T09:30:00Z",
            "note": "post-reveal semantic audit",
        }
        value["notes"] = "one omission remained"
        return value

    def test_audit_template_is_bound_to_fixed_human_response(self):
        value = audit_response_template(
            self.probe,
            self.fixture_id,
            self.human_sha,
            self.receipt_sha,
        )
        self.assertEqual(value["schema"], AUDIT_RESPONSE_SCHEMA)
        self.assertEqual(
            value["probe_sha256"], probe_content_sha256(self.probe)
        )
        self.assertEqual(
            value["fixed_human_response_sha256"], self.human_sha
        )
        self.assertEqual(
            value["audit_reveal_receipt_sha256"], self.receipt_sha
        )
        self.assertEqual(
            set(value["findings"]), set(self.probe["audit_dimensions"])
        )
        with self.assertRaises(SummaryDistortionEvidenceError):
            validate_audit_response(
                value,
                self.probe,
                self.fixture_id,
                self.human_sha,
                self.receipt_sha,
                "2026-09-17T09:29:00Z",
            )

    def test_audit_rejects_changed_probe_binding(self):
        value = self.valid_audit()
        changed = copy.deepcopy(self.probe)
        changed["cases"][0]["distorted_next_question"] = "changed after review?"
        with self.assertRaises(SummaryDistortionEvidenceError):
            validate_audit_response(
                value,
                changed,
                self.fixture_id,
                self.human_sha,
                self.receipt_sha,
                "2026-09-17T09:29:00Z",
            )

    def test_audit_rejects_wrong_response_binding(self):
        value = self.valid_audit()
        value["fixed_human_response_sha256"] = "b" * 64
        with self.assertRaises(SummaryDistortionEvidenceError):
            validate_audit_response(
                value,
                self.probe,
                self.fixture_id,
                self.human_sha,
                self.receipt_sha,
                "2026-09-17T09:29:00Z",
            )

    def test_audit_requires_exact_dimensions_and_human_authorship(self):
        value = self.valid_audit()
        del value["findings"]["correction_burden"]
        with self.assertRaises(SummaryDistortionEvidenceError):
            validate_audit_response(
                value,
                self.probe,
                self.fixture_id,
                self.human_sha,
                self.receipt_sha,
                "2026-09-17T09:29:00Z",
            )

        value = self.valid_audit()
        value["audit_provenance"]["response_authorship"] = "ai-generated"
        with self.assertRaises(SummaryDistortionEvidenceError):
            validate_audit_response(
                value,
                self.probe,
                self.fixture_id,
                self.human_sha,
                self.receipt_sha,
                "2026-09-17T09:29:00Z",
            )

    def test_audit_completed_at_cannot_precede_reveal(self):
        value = self.valid_audit()
        value["audit_provenance"]["completed_at"] = "2026-09-17T09:28:59Z"
        with self.assertRaises(SummaryDistortionEvidenceError):
            validate_audit_response(
                value,
                self.probe,
                self.fixture_id,
                self.human_sha,
                self.receipt_sha,
                "2026-09-17T09:29:00Z",
            )

    def test_bundle_separates_review_observation_and_semantic_audit(self):
        audit = self.valid_audit()
        audit_path = self.root / "audit.json"
        audit_path.write_text(
            json.dumps(audit, ensure_ascii=False),
            encoding="utf-8",
        )
        bundle = build_evidence_bundle(
            self.probe,
            self.fixtures,
            self.fixture_id,
            self.human_path,
            self.review_receipt_path,
            self.receipt_path,
            audit_path,
        )
        self.assertEqual(bundle["schema"], EVIDENCE_SCHEMA)
        self.assertEqual(
            bundle["probe_snapshot"]["content_sha256"],
            probe_content_sha256(self.probe),
        )
        self.assertEqual(
            bundle["probe_snapshot"]["distorted_summary"],
            self.probe["cases"][0]["distorted_summary"],
        )
        self.assertEqual(
            bundle["probe_snapshot"]["review_questions"],
            self.probe["review_questions"],
        )
        self.assertEqual(
            bundle["review_start"]["receipt_sha256"],
            self.review_receipt_sha,
        )
        self.assertEqual(
            bundle["review_start"]["prior_exposure"],
            "known-material-exposure",
        )
        self.assertEqual(
            bundle["human_review_observation"]["response_sha256"],
            self.human_sha,
        )
        self.assertEqual(
            bundle["review_provenance"]["reviewer_id"],
            "reviewer-opaque-1",
        )
        self.assertEqual(
            bundle["audit_reveal"]["receipt_sha256"],
            self.receipt_sha,
        )
        self.assertEqual(
            bundle["audit_reveal"]["review_start_receipt_sha256"],
            self.review_receipt_sha,
        )
        self.assertEqual(
            bundle["audit_reveal"]["review_started_at"],
            "2026-09-17T09:28:00Z",
        )
        self.assertEqual(
            bundle["audit_reveal"]["audit_material_sha256"],
            self.audit_material_sha,
        )
        self.assertEqual(
            bundle["audit_reveal"]["revealed_at"],
            "2026-09-17T09:29:00Z",
        )
        self.assertEqual(
            bundle["semantic_audit"]["findings"][
                "alternate_hypothesis_preservation"
            ],
            "fail",
        )
        self.assertIn("distortion_key", bundle["semantic_audit"])
        self.assertNotIn("distortion_key", bundle["human_review_observation"])
        rendered = json.dumps(bundle)
        self.assertNotIn('"winner"', rendered)
        self.assertNotIn('"score"', rendered)
        self.assertEqual(
            bundle["evidence_boundaries"]["product_value"],
            "not-established-by-this-artifact",
        )

    def test_bundle_rejects_audit_for_different_human_response(self):
        audit = self.valid_audit()
        audit["fixed_human_response_sha256"] = "c" * 64
        audit_path = self.root / "audit.json"
        audit_path.write_text(json.dumps(audit), encoding="utf-8")
        with self.assertRaises(SummaryDistortionEvidenceError):
            build_evidence_bundle(
                self.probe,
                self.fixtures,
                self.fixture_id,
                self.human_path,
                self.review_receipt_path,
                self.receipt_path,
                audit_path,
            )

    def test_bundle_rejects_material_changed_after_reveal_receipt(self):
        audit = self.valid_audit()
        audit_path = self.root / "audit.json"
        audit_path.write_text(json.dumps(audit), encoding="utf-8")
        changed = copy.deepcopy(self.fixtures)
        changed[self.fixture_id]["reference_state"] = {"changed": True}
        with self.assertRaises(SummaryDistortionEvidenceError):
            build_evidence_bundle(
                self.probe,
                changed,
                self.fixture_id,
                self.human_path,
                self.review_receipt_path,
                self.receipt_path,
                audit_path,
            )

    def test_bundle_rejects_response_provenance_changed_after_review_start(self):
        audit = self.valid_audit()
        audit_path = self.root / "audit.json"
        audit_path.write_text(json.dumps(audit), encoding="utf-8")
        changed_response = copy.deepcopy(self.human_response)
        changed_response["review_provenance"]["prior_exposure"] = "none-declared"
        changed_path = self.root / "changed-human.json"
        changed_path.write_text(json.dumps(changed_response), encoding="utf-8")
        with self.assertRaises(SummaryDistortionEvidenceError):
            build_evidence_bundle(
                self.probe,
                self.fixtures,
                self.fixture_id,
                changed_path,
                self.review_receipt_path,
                self.receipt_path,
                audit_path,
            )

    def test_save_bundle_never_overwrites_existing_evidence(self):
        target = self.root / "evidence.json"
        bundle = {"schema": EVIDENCE_SCHEMA}
        save_bundle(target, bundle)
        original = target.read_text(encoding="utf-8")
        with self.assertRaises(SummaryDistortionEvidenceError):
            save_bundle(target, {"schema": "changed"})
        self.assertEqual(target.read_text(encoding="utf-8"), original)


if __name__ == "__main__":
    unittest.main()
