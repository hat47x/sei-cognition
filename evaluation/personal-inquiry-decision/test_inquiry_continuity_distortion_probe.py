#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from inquiry_continuity_distortion_probe import (
    DistortionProbeError,
    REQUIRED_DISTORTIONS,
    build_packet,
    validate_probe_set,
)


def matched_manifest():
    return {
        "schema": "sei.inquiry-continuity-matched-set/v0",
        "status": "evaluation-only",
        "set_id": "e78-matched-set-v1",
        "fixtures": [
            {"id": "f1", "path": "f1.json"},
            {"id": "f2", "path": "f2.json"},
            {"id": "f3", "path": "f3.json"},
        ],
    }


def probe(pid: str, fid: str):
    return {
        "probe_id": pid,
        "fixture_id": fid,
        "presentation_timing": "after_base_review_is_fixed",
        "flawed_ai_suggestion": {
            "summary": "intentionally flawed",
            "next_question": "biased next question",
        },
        "injected_distortions": {
            "certainty_inflation": ["certainty"],
            "alternative_omission": ["omission"],
            "temporal_backfill": ["backfill"],
        },
        "audit_key": {"expected_detection": ["detect"]},
    }


def probe_set():
    return {
        "schema": "sei.inquiry-continuity-distortion-probe-set/v0",
        "status": "evaluation-only",
        "issue": "ISSUE-000078",
        "probe_set_id": "distortion-v1",
        "base_matched_set": {"set_id": "e78-matched-set-v1", "path": "manifest.json"},
        "required_distortions": sorted(REQUIRED_DISTORTIONS),
        "canonical_write_policy": {
            "automatic_write": False,
            "rule": "explicit human action required",
        },
        "human_review_questions": [{"id": "D1", "prompt": "find errors"}],
        "probes": [
            probe("p1", "f1"),
            probe("p2", "f2"),
            probe("p3", "f3"),
        ],
        "interpretation_stoplines": ["no winner"],
    }


class DistortionProbeTest(unittest.TestCase):
    def setUp(self):
        self.probes = probe_set()
        self.manifest = matched_manifest()

    def test_valid_set_covers_each_fixture_once(self):
        validate_probe_set(self.probes, self.manifest)

    def test_suggestion_packet_hides_audit_key(self):
        packet = build_packet(self.probes, self.manifest, "p1", "suggestion")
        self.assertIn("flawed_ai_suggestion", packet)
        self.assertIn("questions", packet)
        self.assertNotIn("audit_key", packet)
        self.assertNotIn("injected_distortions", packet)
        self.assertFalse(packet["canonical_write_policy"]["automatic_write"])

    def test_audit_requires_fixed_human_response(self):
        with self.assertRaises(DistortionProbeError):
            build_packet(self.probes, self.manifest, "p1", "audit")

    def test_audit_reveals_key_only_after_response_file_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            response = Path(tmp) / "response.json"
            response.write_text(json.dumps({"D1": "found"}), encoding="utf-8")
            packet = build_packet(
                self.probes, self.manifest, "p1", "audit", response
            )
        self.assertIn("fixed_response_sha256", packet)
        self.assertIn("audit_key", packet)
        self.assertIn("injected_distortions", packet)
        self.assertNotIn("flawed_ai_suggestion", packet)
        self.assertNotIn("questions", packet)

    def test_missing_distortion_class_is_rejected(self):
        broken = copy.deepcopy(self.probes)
        del broken["probes"][0]["injected_distortions"]["temporal_backfill"]
        with self.assertRaises(DistortionProbeError):
            validate_probe_set(broken, self.manifest)

    def test_unknown_fixture_is_rejected(self):
        broken = copy.deepcopy(self.probes)
        broken["probes"][2]["fixture_id"] = "unknown"
        with self.assertRaises(DistortionProbeError):
            validate_probe_set(broken, self.manifest)

    def test_automatic_canonical_write_is_rejected(self):
        broken = copy.deepcopy(self.probes)
        broken["canonical_write_policy"]["automatic_write"] = True
        with self.assertRaises(DistortionProbeError):
            validate_probe_set(broken, self.manifest)


if __name__ == "__main__":
    unittest.main()
