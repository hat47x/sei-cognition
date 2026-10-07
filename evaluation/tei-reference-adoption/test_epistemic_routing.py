#!/usr/bin/env python3
"""Self-tests for ISSUE #660 epistemic routing evaluation."""

from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("epistemic_routing.py")
SPEC = importlib.util.spec_from_file_location("epistemic_routing", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class EpistemicRoutingEvaluationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        fixture_path = Path(__file__).with_name("epistemic_projection_fixture_v0.json")
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        cls.projection = fixture["projection"]

    def route(self, projection=None):
        value = copy.deepcopy(self.projection if projection is None else projection)
        return MODULE.route_projection(value)

    def by_id(self, result, assertion_id):
        return next(item for item in result["routes"] if item["assertionId"] == assertion_id)

    def test_direct_user_premise_is_preserved(self) -> None:
        result = self.route()
        item = self.by_id(result, "user-current")
        self.assertEqual("premise", item["route"])

    def test_ai_unreviewed_candidate_is_not_promoted(self) -> None:
        result = self.route()
        item = self.by_id(result, "ai-unreviewed")
        self.assertEqual("candidate", item["route"])

    def test_reanchored_premise_stays_premise_but_is_flagged(self) -> None:
        result = self.route()
        item = self.by_id(result, "reanchored-requirement")
        self.assertEqual("premise", item["route"])
        self.assertTrue(item["targetReanchored"])
        self.assertIn(
            "reanchored-target-is-not-semantic-identity-proof",
            result["authorityLimits"],
        )

    def test_partial_metadata_cannot_be_smuggled_as_premise(self) -> None:
        projection = copy.deepcopy(self.projection)
        item = next(
            value for value in projection["assessments"]
            if value["assertionId"] == "user-current"
        )
        item["metadataState"] = "partial"
        item["useState"] = "premise"

        result = self.route(projection)
        routed = self.by_id(result, "user-current")
        self.assertEqual("review", routed["route"])
        self.assertIn("SEI_METADATA_NOT_COMPLETE", routed["seiReasons"])

    def test_ambiguous_or_detached_target_never_enters_premise(self) -> None:
        for state in ("ambiguous", "detached"):
            projection = copy.deepcopy(self.projection)
            item = next(
                value for value in projection["assessments"]
                if value["assertionId"] == "user-current"
            )
            item["targetBinding"] = state
            item["useState"] = "premise"
            result = self.route(projection)
            routed = self.by_id(result, "user-current")
            self.assertEqual("review", routed["route"])
            self.assertIn("SEI_TARGET_NOT_STABLY_BOUND", routed["seiReasons"])

    def test_incompatible_context_is_blocked_even_if_source_claims_premise(self) -> None:
        projection = copy.deepcopy(self.projection)
        item = next(
            value for value in projection["assessments"]
            if value["assertionId"] == "user-current"
        )
        item["contextCompatibility"] = "incompatible"
        item["useState"] = "premise"
        result = self.route(projection)
        routed = self.by_id(result, "user-current")
        self.assertEqual("blocked", routed["route"])
        self.assertIn("SEI_CONTEXT_INCOMPATIBLE", routed["seiReasons"])

    def test_partial_health_view_is_not_project_wide_health(self) -> None:
        projection = copy.deepcopy(self.projection)
        projection["health"]["viewMetadataState"] = "partial"
        result = self.route(projection)
        self.assertEqual("partial", result["projectHealth"]["scope"])
        self.assertTrue(
            any(item["kind"] == "partial-health-view" for item in result["unknowns"])
        )

    def test_coverage_gap_remains_unknown_and_escalates_when_critical(self) -> None:
        result = self.route()
        self.assertTrue(
            any(
                item["kind"] == "coverage-gap" and item["areaId"] == "critical-gap"
                for item in result["unknowns"]
            )
        )
        self.assertTrue(
            any(
                item["kind"] == "coverage-gap" and item["areaId"] == "critical-gap"
                for item in result["escalations"]
            )
        )

    def test_consumer_freshness_escalates_without_mutating_base_route(self) -> None:
        result = self.route()
        base = self.by_id(result, "human-reviewed")
        self.assertEqual("premise", base["route"])
        issue = next(
            item for item in result["escalations"]
            if item["kind"] == "health-issue"
            and item["assertionId"] == "human-reviewed"
        )
        self.assertEqual("stale", issue["consumerFreshness"])

    def test_conflict_stays_review_required(self) -> None:
        result = self.route()
        item = self.by_id(result, "conflict-a")
        self.assertEqual("review", item["route"])

    def test_source_blocked_remains_blocked_even_with_partial_metadata(self) -> None:
        projection = copy.deepcopy(self.projection)
        item = next(
            value for value in projection["assessments"]
            if value["assertionId"] == "rejected"
        )
        item["metadataState"] = "partial"
        result = self.route(projection)
        routed = self.by_id(result, "rejected")
        self.assertEqual("blocked", routed["route"])
        self.assertIn("SEI_SOURCE_BLOCKED", routed["seiReasons"])

    def test_unknown_semantic_contract_fails_closed(self) -> None:
        projection = copy.deepcopy(self.projection)
        projection["contract"] = "tei.epistemic-projection/v999"
        with self.assertRaisesRegex(ValueError, "contract must be"):
            self.route(projection)

    def test_unsupported_schema_fails_closed(self) -> None:
        projection = copy.deepcopy(self.projection)
        projection["schema"] = "tei.reference.epistemic-assessment/v999"
        with self.assertRaisesRegex(ValueError, "schema must be"):
            self.route(projection)

    def test_duplicate_assertion_id_fails_closed(self) -> None:
        projection = copy.deepcopy(self.projection)
        projection["assessments"].append(copy.deepcopy(projection["assessments"][0]))
        with self.assertRaisesRegex(ValueError, "duplicate assertionId"):
            self.route(projection)

    def test_missing_authority_limit_fails_closed(self) -> None:
        projection = copy.deepcopy(self.projection)
        projection["authorityLimits"] = [
            value for value in projection["authorityLimits"]
            if value != "partial-transport-health-is-not-project-wide-health"
        ]
        with self.assertRaisesRegex(ValueError, "missing required authority limits"):
            self.route(projection)


if __name__ == "__main__":
    unittest.main()
