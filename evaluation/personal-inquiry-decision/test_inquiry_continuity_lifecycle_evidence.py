#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from inquiry_continuity_lifecycle_probe import (
    build_audit_receipt,
    build_review_start_receipt,
    load_json,
    probe_content_sha256,
    response_template,
    save_receipt,
)
from inquiry_continuity_lifecycle_evidence import (
    AUDIT_RESPONSE_SCHEMA,
    EVIDENCE_SCHEMA,
    LifecycleEvidenceError,
    audit_response_template,
    build_evidence_bundle,
    save_bundle,
    validate_audit_response,
    validate_evidence_bundle,
)


class LifecycleEvidenceTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.repo_root = Path(__file__).resolve().parents[2]
        self.probe = load_json(
            self.repo_root
            / "evaluation/personal-inquiry-decision/"
            "inquiry_continuity_lifecycle_probe_v1.json"
        )
        self.rotation = "R1"

        self.review = build_review_start_receipt(
            self.probe,
            self.rotation,
            "reviewer-test-fixture",
            "known-material-exposure",
            "human-transcribed",
            "2026-09-19T03:00:00+09:00",
        )
        self.review_path = self.root / "review.json"
        save_receipt(
            self.review_path,
            self.review,
            "review-start receipt",
        )
        self.review_raw = self.review_path.read_bytes()
        self.review_sha = hashlib.sha256(
            self.review_raw
        ).hexdigest()

        response = response_template(
            self.probe,
            self.rotation,
            self.review_sha,
        )
        for entry in response["entries"]:
            for question_id in entry["answers"]:
                entry["answers"][question_id] = (
                    "synthetic mechanics fixture response"
                )
        self.response_path = self.root / "response.json"
        self.response_path.write_text(
            json.dumps(
                response,
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )

        self.audit_receipt = build_audit_receipt(
            self.probe,
            self.rotation,
            self.review,
            self.review_raw,
            self.response_path,
            "2026-09-19T03:05:00+09:00",
        )
        self.audit_receipt_path = (
            self.root / "audit-receipt.json"
        )
        save_receipt(
            self.audit_receipt_path,
            self.audit_receipt,
            "audit receipt",
        )
        self.audit_raw = self.audit_receipt_path.read_bytes()
        self.audit_sha = hashlib.sha256(
            self.audit_raw
        ).hexdigest()

        self.audit_response = audit_response_template(
            self.probe,
            self.rotation,
            self.audit_sha,
        )
        for presentation in self.audit_response[
            "presentations"
        ]:
            for finding in presentation[
                "semantic_hard_failure_findings"
            ]:
                finding["finding"] = "not-present"
            for finding in presentation[
                "product_failure_signal_findings"
            ]:
                finding["finding"] = "not-indicated"
        self.audit_response["audit_provenance"] = {
            "auditor_id": "auditor-test-fixture",
            "response_authorship": "human-transcribed",
            "completed_at": "2026-09-19T03:10:00+09:00",
            "note": "synthetic mechanics fixture only",
        }
        self.audit_response_path = (
            self.root / "audit-response.json"
        )
        self.audit_response_path.write_text(
            json.dumps(
                self.audit_response,
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )

    def tearDown(self):
        self.tmp.cleanup()

    def valid_bundle(self) -> dict:
        return build_evidence_bundle(
            self.probe,
            self.rotation,
            self.review_path,
            self.response_path,
            self.audit_receipt_path,
            self.audit_response_path,
        )

    def test_audit_template_is_typed_without_winner(self):
        template = audit_response_template(
            self.probe,
            self.rotation,
            self.audit_sha,
        )
        self.assertEqual(
            template["schema"],
            AUDIT_RESPONSE_SCHEMA,
        )
        self.assertEqual(
            template["audit_receipt_sha256"],
            self.audit_sha,
        )
        self.assertEqual(
            template["finding_contract"],
            {
                "semantic_hard_failure": [
                    "present",
                    "not-present",
                    "not-applicable",
                ],
                "product_failure_signal": [
                    "risk-indicated",
                    "not-indicated",
                    "not-assessable",
                ],
            },
        )
        self.assertEqual(
            [item["condition"] for item in template["presentations"]],
            self.probe["assignment_rotations"][self.rotation],
        )
        rendered = json.dumps(template)
        self.assertNotIn('"winner"', rendered)
        self.assertNotIn('"score"', rendered)
        self.assertNotIn('"preferred_condition"', rendered)

    def test_audit_response_rejects_wrong_receipt_and_time(self):
        changed = copy.deepcopy(self.audit_response)
        changed["audit_receipt_sha256"] = "a" * 64
        with self.assertRaises(LifecycleEvidenceError):
            validate_audit_response(
                changed,
                self.probe,
                self.rotation,
                self.audit_sha,
                self.audit_receipt["revealed_at"],
            )

        changed = copy.deepcopy(self.audit_response)
        changed["audit_provenance"]["completed_at"] = (
            "2026-09-19T03:04:59+09:00"
        )
        with self.assertRaises(LifecycleEvidenceError):
            validate_audit_response(
                changed,
                self.probe,
                self.rotation,
                self.audit_sha,
                self.audit_receipt["revealed_at"],
            )

    def test_audit_response_keeps_semantic_and_product_signal_values_distinct(self):
        changed = copy.deepcopy(self.audit_response)
        changed["presentations"][0][
            "product_failure_signal_findings"
        ][0]["finding"] = "present"
        with self.assertRaises(LifecycleEvidenceError):
            validate_audit_response(
                changed,
                self.probe,
                self.rotation,
                self.audit_sha,
                self.audit_receipt["revealed_at"],
            )

        changed = copy.deepcopy(self.audit_response)
        changed["presentations"][0][
            "semantic_hard_failure_findings"
        ][0]["finding"] = "risk-indicated"
        with self.assertRaises(LifecycleEvidenceError):
            validate_audit_response(
                changed,
                self.probe,
                self.rotation,
                self.audit_sha,
                self.audit_receipt["revealed_at"],
            )

    def test_bundle_is_self_checking_and_preserves_stoplines(self):
        bundle = self.valid_bundle()
        validate_evidence_bundle(bundle)
        self.assertEqual(
            bundle["schema"],
            EVIDENCE_SCHEMA,
        )
        self.assertEqual(
            bundle["probe_snapshot"]["content_sha256"],
            probe_content_sha256(self.probe),
        )
        self.assertEqual(
            bundle["review_response"]["value"][
                "review_start_receipt_sha256"
            ],
            bundle["review_start"]["raw_sha256"],
        )
        self.assertEqual(
            bundle["audit_gate"]["value"][
                "fixed_response_sha256"
            ],
            bundle["review_response"]["raw_sha256"],
        )
        self.assertEqual(
            bundle["semantic_audit"]["value"][
                "audit_receipt_sha256"
            ],
            bundle["audit_gate"]["raw_sha256"],
        )
        for field in (
            "review_start",
            "review_response",
            "audit_gate",
            "semantic_audit",
        ):
            snapshot = bundle[field]
            self.assertEqual(
                hashlib.sha256(
                    snapshot["raw_json"].encode("utf-8")
                ).hexdigest(),
                snapshot["raw_sha256"],
            )
            self.assertEqual(
                json.loads(snapshot["raw_json"]),
                snapshot["value"],
            )
        self.assertEqual(
            bundle["evidence_boundaries"][
                "universal_status_type"
            ],
            "not-authorized-by-this-artifact",
        )
        self.assertIn(
            "synthetic-review assessments",
            bundle["evidence_boundaries"][
                "product_failure_signal_interpretation"
            ],
        )
        rendered = json.dumps(bundle)
        self.assertNotIn('"winner"', rendered)
        self.assertNotIn('"score"', rendered)

    def test_bundle_rejects_tampering_even_if_semantic_digest_refreshed(self):
        bundle = self.valid_bundle()

        changed = copy.deepcopy(bundle)
        changed["semantic_audit"]["value"][
            "presentations"
        ][0]["semantic_hard_failure_findings"][0][
            "finding"
        ] = "pass"
        changed["semantic_audit"]["semantic_sha256"] = hashlib.sha256(
            json.dumps(
                changed["semantic_audit"]["value"],
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
        with self.assertRaises(LifecycleEvidenceError):
            validate_evidence_bundle(changed)

        changed = copy.deepcopy(bundle)
        changed["review_start"]["raw_json"] += " "
        with self.assertRaises(LifecycleEvidenceError):
            validate_evidence_bundle(changed)

        changed = copy.deepcopy(bundle)
        changed["probe_snapshot"]["canonical_probe"][
            "semantic_stopline"
        ]["universal_status_type"] = "proposed"
        with self.assertRaises(LifecycleEvidenceError):
            validate_evidence_bundle(changed)

    def test_save_bundle_is_exclusive_and_validated(self):
        bundle = self.valid_bundle()
        target = self.root / "evidence.json"
        save_bundle(target, bundle)
        original = target.read_bytes()
        with self.assertRaises(LifecycleEvidenceError):
            save_bundle(target, bundle)
        self.assertEqual(
            target.read_bytes(),
            original,
        )

        changed = copy.deepcopy(bundle)
        changed["evidence_boundaries"][
            "product_value"
        ] = "established"
        bad = self.root / "bad.json"
        with self.assertRaises(LifecycleEvidenceError):
            save_bundle(bad, changed)
        self.assertFalse(bad.exists())


if __name__ == "__main__":
    unittest.main()
