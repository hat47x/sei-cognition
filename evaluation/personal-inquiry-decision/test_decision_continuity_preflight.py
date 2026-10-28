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


    # Fixture-specific parity checks. These guard identified content drift,
    # not general semantic equivalence between different Surface formats.
    def test_ticket_routing_plural_low_confidence_basis_in_each_surface(self):
        _, fixtures = load_real_set()
        fixture = fixtures["e73-decision-continuity-002-ticket-routing"]
        original = next(
            event for event in fixture["scenario"]["phase_1"]
            if event["id"] == "obs-billing-low-confidence"
        )
        self.assertIn("複数", original["text"])
        surfaces = fixture["conditions"]
        self.assertIn("複数", " ".join(surfaces["A_raw_chat"]["surface_text"]))
        self.assertIn("複数", " ".join(surfaces["B_chronological_note"]["surface_text"]))
        self.assertIn(
            "複数",
            " ".join(surfaces["C_sei_resume"]["surface_text"]["historical_basis"]),
        )

    def test_import_dedupe_future_unknown_and_dry_run_in_each_surface(self):
        _, fixtures = load_real_set()
        fixture = fixtures["e73-decision-continuity-003-import-dedupe"]
        events = {event["id"]: event for event in fixture["scenario"]["phase_1"]}
        self.assertIn("今後安定", events["unk-source-id-quality"]["text"])
        self.assertIn("row hash", events["dec-dry-run"]["text"])

        surfaces = fixture["conditions"]
        raw = " ".join(surfaces["A_raw_chat"]["surface_text"])
        note = " ".join(surfaces["B_chronological_note"]["surface_text"])
        resume = surfaces["C_sei_resume"]["surface_text"]
        self.assertIn("今後安定", raw)
        self.assertIn("将来品質", note)
        self.assertTrue(any("今後安定" in x for x in resume["unresolved"]))
        self.assertIn("row hash", raw)
        self.assertIn("row hash", note)
        self.assertIn("row hash", resume["decision"]["text"])


if __name__ == "__main__":
    unittest.main()
