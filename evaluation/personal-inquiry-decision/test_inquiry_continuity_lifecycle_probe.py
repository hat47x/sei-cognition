#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from inquiry_continuity_lifecycle_probe import (
    LifecycleProbeError,
    build_audit_packet,
    build_audit_receipt,
    build_review_packets,
    build_review_start_receipt,
    probe_content_sha256,
    response_template,
    save_receipt,
    validate_audit_receipt_data,
    validate_probe,
    validate_response,
)


def make_probe() -> dict:
    snapshots = [
        {
            "stage": "active",
            "canonical_decision_present": False,
            "unresolved_preserved": True,
            "canonical_inquiry_meaning_rewritten": False,
        },
        {
            "stage": "dormant",
            "canonical_decision_present": False,
            "unresolved_preserved": True,
            "canonical_inquiry_meaning_rewritten": False,
        },
        {
            "stage": "closed_without_decision",
            "canonical_decision_present": False,
            "unresolved_preserved": True,
            "canonical_inquiry_meaning_rewritten": False,
        },
        {
            "stage": "linked_later_decision",
            "canonical_decision_present": False,
            "unresolved_preserved": True,
            "canonical_inquiry_meaning_rewritten": False,
            "later_decision_ref": "decision-1",
            "historical_link_role": "prior_unresolved_context",
        },
    ]
    return {
        "schema": "sei.inquiry-continuity-lifecycle-probe/v1",
        "status": "evaluation-only",
        "issue": "ISSUE-000078",
        "probe_id": "probe-1",
        "semantic_stopline": {
            "attention_projection_is_canonical": False,
            "universal_status_type": "not-proposed",
        },
        "presentation_rules": {
            "condition_identifiers_hidden_until_audit": True,
            "intended_tradeoff_hidden_until_audit": True,
            "response_fixed_before_audit": True,
            "audit_reveals_condition_mapping": True,
        },
        "assignment_rotations": {
            "R1": [
                "A_always_open",
                "B_age_hidden",
                "C_explicit_attention_projection",
            ],
            "R2": [
                "B_age_hidden",
                "C_explicit_attention_projection",
                "A_always_open",
            ],
            "R3": [
                "C_explicit_attention_projection",
                "A_always_open",
                "B_age_hidden",
            ],
        },
        "scenario": {"decision_present": False},
        "lifecycle_snapshots": snapshots,
        "handling_conditions": {
            "A_always_open": {
                "automatic_transition": False,
                "canonical_authority": False,
                "surface": ["always open"],
                "intended_tradeoff": "recoverability vs burden",
            },
            "B_age_hidden": {
                "automatic_transition": True,
                "canonical_authority": False,
                "surface": ["age hidden"],
                "intended_tradeoff": "quiet vs rediscovery",
            },
            "C_explicit_attention_projection": {
                "automatic_transition": False,
                "canonical_authority": False,
                "surface": ["explicit"],
                "intended_tradeoff": "control vs capture",
            },
        },
        "human_review_questions": [
            {"id": "L1", "prompt": "review"}
        ],
        "audit_key": {
            "semantic_hard_failures": ["do not rewrite"],
            "product_failure_signals": ["burden"],
            "acceptable_outcomes": ["no extra state"],
        },
        "evidence_boundary": ["design only"],
    }


class LifecycleProbeTest(unittest.TestCase):
    def setUp(self):
        self.probe = make_probe()
        self.review_receipt = build_review_start_receipt(
            self.probe,
            "R1",
            "reviewer-opaque-1",
            "none-declared",
            "human-direct",
            "2026-09-19T02:00:00+09:00",
        )
        self.review_raw = (
            json.dumps(
                self.review_receipt,
                ensure_ascii=False,
                indent=2,
            )
            + "\n"
        ).encode("utf-8")
        self.review_sha = hashlib.sha256(
            self.review_raw
        ).hexdigest()

    def _response_value(self) -> dict:
        value = response_template(
            self.probe,
            "R1",
            self.review_sha,
        )
        for entry in value["entries"]:
            entry["answers"]["L1"] = "answer"
        return value

    def test_valid_probe_keeps_attention_projection_noncanonical(self):
        validate_probe(self.probe)

    def test_review_packets_blind_condition_and_tradeoff(self):
        packets = build_review_packets(
            self.probe,
            "R1",
            self.review_sha,
        )
        self.assertEqual(
            [packet["presentation_id"] for packet in packets],
            ["R1-P1", "R1-P2", "R1-P3"],
        )
        rendered = json.dumps(packets)
        for condition in (
            "A_always_open",
            "B_age_hidden",
            "C_explicit_attention_projection",
        ):
            self.assertNotIn(condition, rendered)
        self.assertNotIn("intended_tradeoff", rendered)
        self.assertNotIn("audit_key", rendered)

    def test_review_start_receipt_binds_provenance(self):
        self.assertEqual(
            self.review_receipt["probe_sha256"],
            probe_content_sha256(self.probe),
        )
        self.assertEqual(
            self.review_receipt["prior_exposure"],
            "none-declared",
        )

    def test_response_is_structured_and_receipt_bound(self):
        value = self._response_value()
        validate_response(
            value,
            self.probe,
            "R1",
            self.review_sha,
        )
        changed = copy.deepcopy(value)
        changed["review_start_receipt_sha256"] = "a" * 64
        with self.assertRaises(LifecycleProbeError):
            validate_response(
                changed,
                self.probe,
                "R1",
                self.review_sha,
            )

    def test_rotation_counterbalances_positions(self):
        validate_probe(self.probe)
        rotations = self.probe["assignment_rotations"]
        for index in range(3):
            self.assertEqual(
                {
                    rotations[rotation][index]
                    for rotation in ("R1", "R2", "R3")
                },
                {
                    "A_always_open",
                    "B_age_hidden",
                    "C_explicit_attention_projection",
                },
            )

    def test_original_inquiry_cannot_gain_decision(self):
        broken = copy.deepcopy(self.probe)
        broken["lifecycle_snapshots"][2][
            "canonical_decision_present"
        ] = True
        with self.assertRaises(LifecycleProbeError):
            validate_probe(broken)

    def test_unresolved_cannot_disappear_on_close(self):
        broken = copy.deepcopy(self.probe)
        broken["lifecycle_snapshots"][2][
            "unresolved_preserved"
        ] = False
        with self.assertRaises(LifecycleProbeError):
            validate_probe(broken)

    def test_later_decision_must_be_separate_context_link(self):
        broken = copy.deepcopy(self.probe)
        broken["lifecycle_snapshots"][-1][
            "historical_link_role"
        ] = "resolves_prior_inquiry"
        with self.assertRaises(LifecycleProbeError):
            validate_probe(broken)

    def test_explicit_projection_cannot_auto_transition(self):
        broken = copy.deepcopy(self.probe)
        broken["handling_conditions"][
            "C_explicit_attention_projection"
        ]["automatic_transition"] = True
        with self.assertRaises(LifecycleProbeError):
            validate_probe(broken)

    def test_audit_requires_fixed_structured_response_then_reveals_mapping(self):
        with tempfile.TemporaryDirectory() as tmp:
            response_path = Path(tmp) / "response.json"
            response_path.write_text(
                json.dumps(
                    self._response_value(),
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )
            receipt = build_audit_receipt(
                self.probe,
                "R1",
                self.review_receipt,
                self.review_raw,
                response_path,
                "2026-09-19T02:05:00+09:00",
            )
            raw = (
                json.dumps(
                    receipt,
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n"
            ).encode("utf-8")
            packet = build_audit_packet(
                self.probe,
                "R1",
                self.review_receipt,
                self.review_raw,
                response_path,
                receipt,
                raw,
            )
        self.assertEqual(
            [
                item["condition"]
                for item in packet["condition_mapping"]
            ],
            self.probe["assignment_rotations"]["R1"],
        )
        self.assertIn("audit_key", packet)
        self.assertIn("intended_tradeoff", json.dumps(packet))
        self.assertEqual(
            packet["fixed_response_sha256"],
            receipt["fixed_response_sha256"],
        )

    def test_audit_data_validator_rejects_response_raw_mismatch(self):
        response_value = self._response_value()
        response_raw = (
            json.dumps(
                response_value,
                ensure_ascii=False,
            )
            + "\n"
        ).encode("utf-8")
        with tempfile.TemporaryDirectory() as tmp:
            response_path = Path(tmp) / "response.json"
            response_path.write_bytes(response_raw)
            receipt = build_audit_receipt(
                self.probe,
                "R1",
                self.review_receipt,
                self.review_raw,
                response_path,
                "2026-09-19T02:05:00+09:00",
            )
        with self.assertRaises(LifecycleProbeError):
            validate_audit_receipt_data(
                receipt,
                self.probe,
                "R1",
                self.review_receipt,
                self.review_raw,
                response_value,
                response_raw + b" ",
            )

    def test_audit_cannot_precede_review_start(self):
        with tempfile.TemporaryDirectory() as tmp:
            response_path = Path(tmp) / "response.json"
            response_path.write_text(
                json.dumps(
                    self._response_value(),
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )
            with self.assertRaises(LifecycleProbeError):
                build_audit_receipt(
                    self.probe,
                    "R1",
                    self.review_receipt,
                    self.review_raw,
                    response_path,
                    "2026-09-19T01:59:59+09:00",
                )

    def test_receipt_save_is_exclusive(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "receipt.json"
            save_receipt(
                target,
                self.review_receipt,
                "review-start receipt",
            )
            original = target.read_bytes()
            with self.assertRaises(LifecycleProbeError):
                save_receipt(
                    target,
                    self.review_receipt,
                    "review-start receipt",
                )
            self.assertEqual(
                target.read_bytes(),
                original,
            )


if __name__ == "__main__":
    unittest.main()
