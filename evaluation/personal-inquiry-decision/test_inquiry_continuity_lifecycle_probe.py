#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from inquiry_continuity_lifecycle_probe import (
    LifecycleProbeError,
    build_audit_packet,
    build_review_packet,
    validate_probe,
)


def make_probe():
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
        "schema": "sei.inquiry-continuity-lifecycle-probe/v0",
        "status": "evaluation-only",
        "issue": "ISSUE-000078",
        "probe_id": "probe-1",
        "semantic_stopline": {
            "attention_projection_is_canonical": False,
            "universal_status_type": "not-proposed",
        },
        "scenario": {"decision_present": False},
        "lifecycle_snapshots": snapshots,
        "handling_conditions": {
            "A_always_open": {
                "automatic_transition": False,
                "canonical_authority": False,
                "surface": ["always open"],
            },
            "B_age_hidden": {
                "automatic_transition": True,
                "canonical_authority": False,
                "surface": ["age hidden"],
            },
            "C_explicit_attention_projection": {
                "automatic_transition": False,
                "canonical_authority": False,
                "surface": ["explicit"],
            },
        },
        "human_review_questions": [{"id": "L1", "prompt": "review"}],
        "audit_key": {"semantic_hard_failures": ["do not rewrite"]},
        "evidence_boundary": ["design only"],
    }


class LifecycleProbeTest(unittest.TestCase):
    def setUp(self):
        self.probe = make_probe()

    def test_valid_probe_keeps_attention_projection_noncanonical(self):
        validate_probe(self.probe)

    def test_review_packet_does_not_expose_audit_key(self):
        packet = build_review_packet(self.probe, "C_explicit_attention_projection")
        self.assertIn("handling", packet)
        self.assertIn("questions", packet)
        self.assertNotIn("audit_key", packet)
        self.assertFalse(packet["semantic_stopline"]["attention_projection_is_canonical"])

    def test_original_inquiry_cannot_gain_decision(self):
        broken = copy.deepcopy(self.probe)
        broken["lifecycle_snapshots"][2]["canonical_decision_present"] = True
        with self.assertRaises(LifecycleProbeError):
            validate_probe(broken)

    def test_unresolved_cannot_disappear_on_close(self):
        broken = copy.deepcopy(self.probe)
        broken["lifecycle_snapshots"][2]["unresolved_preserved"] = False
        with self.assertRaises(LifecycleProbeError):
            validate_probe(broken)

    def test_later_decision_must_be_separate_context_link(self):
        broken = copy.deepcopy(self.probe)
        broken["lifecycle_snapshots"][-1]["historical_link_role"] = "resolves_prior_inquiry"
        with self.assertRaises(LifecycleProbeError):
            validate_probe(broken)

    def test_explicit_projection_cannot_auto_transition(self):
        broken = copy.deepcopy(self.probe)
        broken["handling_conditions"]["C_explicit_attention_projection"][
            "automatic_transition"
        ] = True
        with self.assertRaises(LifecycleProbeError):
            validate_probe(broken)

    def test_audit_requires_fixed_response_and_hides_review_surface(self):
        with tempfile.TemporaryDirectory() as tmp:
            response = Path(tmp) / "response.json"
            response.write_text(json.dumps({"L1": "answer"}), encoding="utf-8")
            packet = build_audit_packet(
                self.probe, "A_always_open", response
            )
        self.assertIn("fixed_response_sha256", packet)
        self.assertIn("audit_key", packet)
        self.assertNotIn("handling", packet)
        self.assertNotIn("questions", packet)


if __name__ == "__main__":
    unittest.main()
