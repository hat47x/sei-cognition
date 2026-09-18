#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from inquiry_continuity_assistance_probe import (
    build_audit_receipt,
    build_reveal_receipt,
    build_review_start_receipt,
    load_json,
    load_sources,
    probe_content_sha256,
    response_template,
    save_stage_receipt,
    stage_receipt_bytes,
)
from inquiry_continuity_assistance_evidence import (
    AssistanceEvidenceError,
    EVIDENCE_SCHEMA,
    audit_response_template,
    build_evidence_bundle,
    save_bundle,
    validate_audit_response,
    validate_evidence_bundle,
)


class AssistanceEvidenceTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.repo_root = Path(__file__).resolve().parents[2]
        self.probe_path = (
            self.repo_root
            / "evaluation/personal-inquiry-decision/"
            "inquiry_continuity_assistance_probe_v1.json"
        )
        self.probe = load_json(self.probe_path)
        self.fixtures = load_sources(
            self.probe,
            self.repo_root,
        )
        self.rotation = "R1"

        self.review_receipt = build_review_start_receipt(
            self.probe,
            self.rotation,
            "reviewer-test-fixture",
            "known-material-exposure",
            "human-transcribed",
            "2026-09-19T01:00:00+09:00",
        )
        self.review_receipt_path = (
            self.root / "review-start.json"
        )
        save_stage_receipt(
            self.review_receipt_path,
            self.review_receipt,
            "review-start receipt",
        )
        self.review_raw = self.review_receipt_path.read_bytes()
        self.review_sha = hashlib.sha256(
            self.review_raw
        ).hexdigest()

        initial = response_template(
            self.probe,
            self.rotation,
            "initial",
            self.review_sha,
        )
        self._fill_response(initial)
        self.initial_path = self.root / "initial.json"
        self.initial_path.write_text(
            json.dumps(initial, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

        self.reveal_receipt = build_reveal_receipt(
            self.probe,
            self.fixtures,
            self.rotation,
            self.review_sha,
            self.initial_path,
            "2026-09-19T01:05:00+09:00",
        )
        self.reveal_receipt_path = (
            self.root / "reveal-receipt.json"
        )
        save_stage_receipt(
            self.reveal_receipt_path,
            self.reveal_receipt,
            "reveal receipt",
        )
        self.reveal_raw = self.reveal_receipt_path.read_bytes()
        self.reveal_sha = hashlib.sha256(
            self.reveal_raw
        ).hexdigest()

        reveal = response_template(
            self.probe,
            self.rotation,
            "reveal",
            self.review_sha,
            self.reveal_sha,
        )
        self._fill_response(reveal)
        self.reveal_path = self.root / "reveal.json"
        self.reveal_path.write_text(
            json.dumps(reveal, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

        self.audit_receipt = build_audit_receipt(
            self.probe,
            self.fixtures,
            self.rotation,
            self.review_sha,
            self.initial_path,
            self.reveal_path,
            self.reveal_receipt,
            self.reveal_raw,
            "2026-09-19T01:10:00+09:00",
        )
        self.audit_receipt_path = (
            self.root / "audit-receipt.json"
        )
        save_stage_receipt(
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
                "hard_failure_findings"
            ]:
                finding["finding"] = "not-observed"
        self.audit_response["audit_provenance"] = {
            "auditor_id": "auditor-test-fixture",
            "response_authorship": "human-transcribed",
            "completed_at": "2026-09-19T01:15:00+09:00",
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

    def _fill_response(self, value: dict) -> None:
        for entry in value["entries"]:
            for question_id in entry["answers"]:
                entry["answers"][question_id] = (
                    "synthetic mechanics fixture response"
                )

    def valid_bundle(self) -> dict:
        return build_evidence_bundle(
            self.probe,
            self.fixtures,
            self.rotation,
            self.review_receipt_path,
            self.initial_path,
            self.reveal_receipt_path,
            self.reveal_path,
            self.audit_receipt_path,
            self.audit_response_path,
        )

    def test_audit_template_is_receipt_bound_without_winner(self):
        template = audit_response_template(
            self.probe,
            self.rotation,
            self.audit_sha,
        )
        self.assertEqual(
            template["audit_receipt_sha256"],
            self.audit_sha,
        )
        rendered = json.dumps(template)
        self.assertNotIn('"winner"', rendered)
        self.assertNotIn('"score"', rendered)
        self.assertEqual(
            [
                item["condition"]
                for item in template["presentations"]
            ],
            [
                assignment["condition"]
                for assignment in self.probe[
                    "assignment_rotations"
                ][self.rotation]
            ],
        )

    def test_audit_response_rejects_wrong_receipt_and_time(self):
        changed = copy.deepcopy(self.audit_response)
        changed["audit_receipt_sha256"] = "a" * 64
        with self.assertRaises(AssistanceEvidenceError):
            validate_audit_response(
                changed,
                self.probe,
                self.rotation,
                self.audit_sha,
                self.audit_receipt["revealed_at"],
            )

        changed = copy.deepcopy(self.audit_response)
        changed["audit_provenance"][
            "completed_at"
        ] = "2026-09-19T01:09:59+09:00"
        with self.assertRaises(AssistanceEvidenceError):
            validate_audit_response(
                changed,
                self.probe,
                self.rotation,
                self.audit_sha,
                self.audit_receipt["revealed_at"],
            )

    def test_bundle_preserves_chain_and_stoplines(self):
        bundle = self.valid_bundle()
        validate_evidence_bundle(bundle)
        self.assertEqual(bundle["schema"], EVIDENCE_SCHEMA)
        self.assertEqual(
            bundle["probe_snapshot"]["content_sha256"],
            probe_content_sha256(self.probe),
        )
        self.assertEqual(
            bundle["initial_response"]["value"][
                "review_start_receipt_sha256"
            ],
            bundle["review_start"]["raw_sha256"],
        )
        self.assertEqual(
            bundle["reveal_response"]["value"][
                "stage_gate_sha256"
            ],
            bundle["reveal_gate"]["raw_sha256"],
        )
        self.assertEqual(
            bundle["semantic_audit"]["value"][
                "audit_receipt_sha256"
            ],
            bundle["audit_gate"]["raw_sha256"],
        )
        rendered = json.dumps(bundle)
        self.assertNotIn('"winner"', rendered)
        self.assertNotIn('"score"', rendered)
        self.assertEqual(
            bundle["evidence_boundaries"]["product_value"],
            "not-established-by-this-artifact",
        )

    def _refresh_semantic_digest(
        self,
        snapshot: dict,
    ) -> None:
        snapshot["semantic_sha256"] = hashlib.sha256(
            json.dumps(
                snapshot["value"],
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()

    def test_bundle_rejects_semantically_invalid_artifact_even_with_refreshed_digest(self):
        bundle = self.valid_bundle()

        changed = copy.deepcopy(bundle)
        changed["semantic_audit"]["value"][
            "presentations"
        ][0]["hard_failure_findings"][0][
            "finding"
        ] = "pass"
        self._refresh_semantic_digest(
            changed["semantic_audit"]
        )
        with self.assertRaises(AssistanceEvidenceError):
            validate_evidence_bundle(changed)

        changed = copy.deepcopy(bundle)
        changed["review_start"]["value"][
            "prior_exposure"
        ] = "clean"
        self._refresh_semantic_digest(
            changed["review_start"]
        )
        with self.assertRaises(AssistanceEvidenceError):
            validate_evidence_bundle(changed)

    def test_bundle_rejects_semantic_snapshot_tampering(self):
        bundle = self.valid_bundle()

        changed = copy.deepcopy(bundle)
        changed["probe_snapshot"]["canonical_probe"][
            "purpose"
        ] = "tampered"
        with self.assertRaises(AssistanceEvidenceError):
            validate_evidence_bundle(changed)

        changed = copy.deepcopy(bundle)
        changed["reveal_response"]["value"][
            "stage_gate_sha256"
        ] = "a" * 64
        with self.assertRaises(AssistanceEvidenceError):
            validate_evidence_bundle(changed)

        changed = copy.deepcopy(bundle)
        changed["semantic_audit"]["value"][
            "presentations"
        ][0]["condition"] = "B_quiet_first"
        with self.assertRaises(AssistanceEvidenceError):
            validate_evidence_bundle(changed)

    def test_save_bundle_is_exclusive_and_validated(self):
        target = self.root / "evidence.json"
        bundle = self.valid_bundle()
        save_bundle(target, bundle)
        original = target.read_bytes()
        with self.assertRaises(AssistanceEvidenceError):
            save_bundle(target, bundle)
        self.assertEqual(target.read_bytes(), original)

        tampered_target = self.root / "tampered.json"
        changed = copy.deepcopy(bundle)
        changed["evidence_boundaries"][
            "product_value"
        ] = "established"
        with self.assertRaises(AssistanceEvidenceError):
            save_bundle(tampered_target, changed)
        self.assertFalse(tampered_target.exists())


if __name__ == "__main__":
    unittest.main()
