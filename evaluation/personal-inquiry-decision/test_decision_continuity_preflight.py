#!/usr/bin/env python3
from __future__ import annotations

import copy
import unittest
from pathlib import Path

from decision_continuity_preflight import (
    PacketError,
    validate_decision_fixture_semantics,
    validate_decision_matched_set,
)
from inquiry_continuity_packet import load_json


HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "decision_continuity_counterfactual_matched_set_v1.json"


def load_real_set():
    manifest = load_json(MANIFEST)
    fixtures = {
        item["id"]: load_json(HERE / Path(item["path"]).name)
        for item in manifest["fixtures"]
    }
    return manifest, fixtures


class DecisionContinuityPreflightTest(unittest.TestCase):
    def test_real_matched_set_passes_decision_semantic_preflight(self):
        manifest, fixtures = load_real_set()
        validate_decision_matched_set(manifest, fixtures)

    def test_post_decision_fact_cannot_become_historical_basis(self):
        _, fixtures = load_real_set()
        fixture = copy.deepcopy(next(iter(fixtures.values())))
        post_id = fixture["reference_state"]["post_decision_ids"][0]
        fixture["reference_state"]["historical_basis_ids"][0] = post_id

        with self.assertRaises(PacketError):
            validate_decision_fixture_semantics(fixture)

    def test_recommendation_ref_must_point_to_recommendation(self):
        _, fixtures = load_real_set()
        fixture = copy.deepcopy(next(iter(fixtures.values())))
        decision = next(
            event
            for event in fixture["scenario"]["phase_1"]
            if event["role"] == "decision"
        )
        decision["recommendation_refs"] = [decision["basis_refs"][0]]

        with self.assertRaises(PacketError):
            validate_decision_fixture_semantics(fixture)

    def test_unresolved_ref_must_exist_at_decision_time(self):
        _, fixtures = load_real_set()
        fixture = copy.deepcopy(next(iter(fixtures.values())))
        decision = next(
            event
            for event in fixture["scenario"]["phase_1"]
            if event["role"] == "decision"
        )
        decision["unresolved_refs"] = [
            fixture["reference_state"]["post_decision_ids"][0]
        ]
        fixture["reference_state"]["unresolved_ids"] = decision["unresolved_refs"]

        with self.assertRaises(PacketError):
            validate_decision_fixture_semantics(fixture)

    def test_phase1_must_have_exactly_one_decision(self):
        _, fixtures = load_real_set()
        fixture = copy.deepcopy(next(iter(fixtures.values())))
        fixture["scenario"]["phase_1"] = [
            event
            for event in fixture["scenario"]["phase_1"]
            if event["role"] != "decision"
        ]

        with self.assertRaises(PacketError):
            validate_decision_fixture_semantics(fixture)


if __name__ == "__main__":
    unittest.main()
