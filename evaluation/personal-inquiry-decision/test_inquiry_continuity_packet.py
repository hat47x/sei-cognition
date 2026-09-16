#!/usr/bin/env python3
from __future__ import annotations

import copy
import unittest
from pathlib import Path

from inquiry_continuity_packet import (
    CONDITIONS,
    PacketError,
    build_rotation_packets,
    load_json,
    validate_matched_set,
)

HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "inquiry_continuity_counterfactual_matched_set_v1.json"


def load_real_set():
    manifest = load_json(MANIFEST)
    fixtures = {
        item["id"]: load_json(HERE / Path(item["path"]).name)
        for item in manifest["fixtures"]
    }
    return manifest, fixtures


class InquiryContinuityPacketTest(unittest.TestCase):
    def test_real_matched_set_is_balanced(self):
        manifest, fixtures = load_real_set()
        validate_matched_set(manifest, fixtures)

        for rotation, assignments in manifest["assignment_rotations"].items():
            with self.subTest(rotation=rotation):
                self.assertEqual(
                    {assignment["condition"] for assignment in assignments},
                    CONDITIONS,
                )
                self.assertEqual(len(assignments), len(fixtures))

    def test_phase1_packet_does_not_leak_answer_key_or_later_evidence(self):
        manifest, fixtures = load_real_set()
        packets = build_rotation_packets(manifest, fixtures, "R1", "phase1")

        self.assertEqual(len(packets), 3)
        for packet in packets:
            with self.subTest(fixture_id=packet["fixture_id"]):
                self.assertIn("surface", packet)
                self.assertIn("questions", packet)
                self.assertNotIn("post_interruption_evidence", packet)
                self.assertNotIn("reference_state", packet)
                self.assertNotIn("review_key", packet)

    def test_post_packet_does_not_leak_audit_key(self):
        manifest, fixtures = load_real_set()
        packets = build_rotation_packets(manifest, fixtures, "R2", "post")

        for packet in packets:
            with self.subTest(fixture_id=packet["fixture_id"]):
                self.assertIn("post_interruption_evidence", packet)
                self.assertIn("questions", packet)
                self.assertNotIn("surface", packet)
                self.assertNotIn("reference_state", packet)
                self.assertNotIn("review_key", packet)

    def test_audit_packet_contains_only_review_material(self):
        manifest, fixtures = load_real_set()
        packets = build_rotation_packets(manifest, fixtures, "R3", "audit")

        for packet in packets:
            with self.subTest(fixture_id=packet["fixture_id"]):
                self.assertIn("reference_state", packet)
                self.assertIn("review_key", packet)
                self.assertNotIn("surface", packet)
                self.assertNotIn("post_interruption_evidence", packet)
                self.assertNotIn("questions", packet)

    def test_rotation_with_duplicate_condition_is_rejected(self):
        manifest, fixtures = load_real_set()
        broken = copy.deepcopy(manifest)
        assignments = broken["assignment_rotations"]["R1"]
        assignments[1]["condition"] = assignments[0]["condition"]

        with self.assertRaises(PacketError):
            validate_matched_set(broken, fixtures)


if __name__ == "__main__":
    unittest.main()
