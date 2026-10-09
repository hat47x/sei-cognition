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

    def test_incomplete_metadata_candidate_stays_candidate_without_forced_review(self) -> None:
        for metadata_state in ("partial", "absent"):
            projection = copy.deepcopy(self.projection)
            item = next(
                value for value in projection["assessments"]
                if value["assertionId"] == "ai-unreviewed"
            )
            item["metadataState"] = metadata_state
            item["useState"] = "candidate-only"

            result = self.route(projection)
            routed = self.by_id(result, "ai-unreviewed")
            self.assertEqual("candidate", routed["route"])
            self.assertIn("SEI_METADATA_NOT_COMPLETE", routed["seiReasons"])

    def test_independent_epistemic_signals_survive_routing(self) -> None:
        result = self.route()
        source = next(
            value for value in self.projection["assessments"]
            if value["assertionId"] == "human-reviewed"
        )
        routed = self.by_id(result, "human-reviewed")
        for field in (
            "contentOrigin",
            "ingestedBy",
            "statementKind",
            "confirmationState",
            "reviewBinding",
            "metadataState",
            "targetBinding",
            "contextCompatibility",
            "freshness",
            "lifecycleState",
            "conflict",
        ):
            self.assertEqual(source[field], routed[field], field)

    def test_missing_provenance_or_review_binding_fails_closed(self) -> None:
        for field in ("contentOrigin", "ingestedBy", "reviewBinding"):
            projection = copy.deepcopy(self.projection)
            projection["assessments"][0][field] = ""
            with self.assertRaisesRegex(ValueError, field):
                self.route(projection)

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

    def test_context_egress_plan_keeps_epistemic_lanes_separate(self) -> None:
        result = self.route()
        plan = result["contextEgressPlan"]

        premises = {item["assertionId"] for item in plan["premiseReferences"]}
        candidates = {item["assertionId"] for item in plan["candidateReferences"]}
        reviews = {item["assertionId"] for item in plan["reviewReferences"]}
        blocked = {item["assertionId"] for item in plan["blockedReferences"]}

        self.assertIn("user-current", premises)
        self.assertIn("human-reviewed", premises)
        self.assertIn("ai-unreviewed", candidates)
        self.assertIn("conflict-a", reviews)
        self.assertIn("rejected", blocked)

        self.assertTrue(premises.isdisjoint(candidates))
        self.assertTrue(premises.isdisjoint(reviews))
        self.assertTrue(premises.isdisjoint(blocked))
        self.assertTrue(plan["contentResolution"]["required"])
        self.assertIn(
            "candidate-reference-is-not-premise",
            plan["authorityLimits"],
        )

    def test_context_egress_never_grants_prompt_control_authority(self) -> None:
        projection = copy.deepcopy(self.projection)
        item = next(
            value for value in projection["assessments"]
            if value["assertionId"] == "user-current"
        )
        item["statementKind"] = "instruction"
        item["useState"] = "premise"

        plan = self.route(projection)["contextEgressPlan"]
        reference = next(
            value for value in plan["premiseReferences"]
            if value["assertionId"] == "user-current"
        )
        self.assertEqual("instruction", reference["statementKind"])
        self.assertEqual("premise-data", reference["contentRole"])
        self.assertFalse(reference["controlAuthority"])
        self.assertIn(
            "epistemic-statement-kind-does-not-grant-prompt-control-authority",
            plan["authorityLimits"],
        )

    def test_context_egress_roles_are_explicit_data_lanes(self) -> None:
        plan = self.route()["contextEgressPlan"]
        expected = {
            "premiseReferences": "premise-data",
            "candidateReferences": "candidate-data",
            "reviewReferences": "review-data",
            "blockedReferences": "blocked-audit",
        }
        for lane, role in expected.items():
            for reference in plan[lane]:
                self.assertEqual(role, reference["contentRole"])
                self.assertFalse(reference["controlAuthority"])

    def test_context_egress_plan_is_reference_only(self) -> None:
        plan = self.route()["contextEgressPlan"]
        for lane in (
            "premiseReferences",
            "candidateReferences",
            "reviewReferences",
            "blockedReferences",
        ):
            for item in plan[lane]:
                self.assertNotIn("text", item)
                self.assertNotIn("evidence", item)
                self.assertNotIn("context", item)
                self.assertIn("meaningFingerprint", item)
                self.assertIn("reviewSubjectFingerprint", item)
                self.assertIn("reviewLogSequence", item)

    def test_incomplete_candidate_remains_candidate_in_egress_plan(self) -> None:
        projection = copy.deepcopy(self.projection)
        item = next(
            value for value in projection["assessments"]
            if value["assertionId"] == "ai-unreviewed"
        )
        item["metadataState"] = "partial"
        item["useState"] = "candidate-only"
        result = self.route(projection)
        plan = result["contextEgressPlan"]
        candidate_ids = {
            value["assertionId"] for value in plan["candidateReferences"]
        }
        review_ids = {value["assertionId"] for value in plan["reviewReferences"]}
        self.assertIn("ai-unreviewed", candidate_ids)
        self.assertNotIn("ai-unreviewed", review_ids)

    def test_context_egress_plan_preserves_project_unknowns_without_promoting_them(self) -> None:
        plan = self.route()["contextEgressPlan"]
        self.assertTrue(
            any(
                item["kind"] == "coverage-gap"
                and item["areaId"] == "critical-gap"
                for item in plan["projectUnknowns"]
            )
        )
        self.assertFalse(
            any("assertionId" in item for item in plan["projectUnknowns"])
        )

    def detail_result_for(self, reference, use_state=None):
        source = next(
            value for value in self.projection["assessments"]
            if value["assertionId"] == reference["assertionId"]
        )
        assessment = copy.deepcopy(source)
        if use_state is not None:
            assessment["useState"] = use_state
        return {
            "contract": MODULE.TEI_DETAIL_RESULT_CONTRACT,
            "schema": MODULE.TEI_DETAIL_RESULT_SCHEMA,
            "assessment": assessment,
            "content": {
                "text": "resolved epistemic content",
                "target": {"kind": "claim", "id": reference["assertionId"]},
                "context": [],
                "evidence": [],
            },
            "contentRole": "epistemic-data",
            "controlAuthority": False,
            "authorityLimits": sorted(MODULE.REQUIRED_DETAIL_AUTHORITY_LIMITS),
        }

    def test_build_detail_query_preserves_egress_receipts(self) -> None:
        plan = self.route()["contextEgressPlan"]
        reference = next(
            item for item in plan["premiseReferences"]
            if item["assertionId"] == "user-current"
        )
        query = MODULE.build_epistemic_detail_query(
            reference,
            ["policy:b", " policy:a ", "policy:b"],
        )
        self.assertEqual(MODULE.TEI_DETAIL_QUERY_CONTRACT, query["contract"])
        self.assertEqual(reference["assertionId"], query["assertionId"])
        self.assertEqual(
            reference["meaningFingerprint"],
            query["expectedMeaningFingerprint"],
        )
        self.assertEqual(
            reference["reviewSubjectFingerprint"],
            query["expectedReviewSubjectFingerprint"],
        )
        self.assertEqual(
            reference["targetBinding"],
            query["expectedTargetBinding"],
        )
        self.assertEqual(
            reference["reviewLogSequence"],
            query["expectedReviewLogSequence"],
        )
        self.assertEqual(["policy:a", "policy:b"], query["grantedAccessRefs"])
        self.assertNotIn("text", query)
        self.assertNotIn("evidence", query)

    def test_detail_query_does_not_infer_access_from_epistemic_content(self) -> None:
        reference = self.route()["contextEgressPlan"]["premiseReferences"][0]
        query = MODULE.build_epistemic_detail_query(reference)
        self.assertEqual([], query["grantedAccessRefs"])

    def test_resolved_premise_detail_remains_context_data(self) -> None:
        plan = self.route()["contextEgressPlan"]
        reference = next(
            item for item in plan["premiseReferences"]
            if item["assertionId"] == "user-current"
        )
        detail = self.detail_result_for(reference)
        resolved = MODULE.resolve_epistemic_detail_for_egress(reference, detail)
        self.assertEqual("premise-data", resolved["contentRole"])
        self.assertTrue(resolved["contextEligible"])
        self.assertFalse(resolved["controlAuthority"])
        self.assertEqual("premise", resolved["assessmentRoute"])

    def test_detail_access_change_cannot_smuggle_old_premise_lane(self) -> None:
        plan = self.route()["contextEgressPlan"]
        reference = next(
            item for item in plan["premiseReferences"]
            if item["assertionId"] == "user-current"
        )
        detail = self.detail_result_for(reference, use_state="review-required")
        detail["assessment"]["metadataState"] = "partial"
        with self.assertRaisesRegex(ValueError, "no longer satisfies"):
            MODULE.resolve_epistemic_detail_for_egress(reference, detail)

    def test_candidate_detail_never_becomes_context_premise(self) -> None:
        plan = self.route()["contextEgressPlan"]
        reference = next(
            item for item in plan["candidateReferences"]
            if item["assertionId"] == "ai-unreviewed"
        )
        detail = self.detail_result_for(reference)
        resolved = MODULE.resolve_epistemic_detail_for_egress(reference, detail)
        self.assertEqual("candidate-data", resolved["contentRole"])
        self.assertFalse(resolved["contextEligible"])
        self.assertEqual("candidate", resolved["assessmentRoute"])

    def test_detail_result_cannot_grant_prompt_control(self) -> None:
        reference = self.route()["contextEgressPlan"]["premiseReferences"][0]
        detail = self.detail_result_for(reference)
        detail["controlAuthority"] = True
        with self.assertRaisesRegex(ValueError, "prompt control authority"):
            MODULE.resolve_epistemic_detail_for_egress(reference, detail)

    def test_detail_result_must_preserve_binding_receipts(self) -> None:
        reference = self.route()["contextEgressPlan"]["premiseReferences"][0]
        detail = self.detail_result_for(reference)
        detail["assessment"]["reviewLogSequence"] += 1
        with self.assertRaisesRegex(ValueError, "reviewLogSequence"):
            MODULE.resolve_epistemic_detail_for_egress(reference, detail)

    def test_detail_result_must_not_expose_access_refs(self) -> None:
        reference = self.route()["contextEgressPlan"]["premiseReferences"][0]
        detail = self.detail_result_for(reference)
        detail["content"]["evidence"] = [
            {"kind": "source", "ref": "repo://x", "accessRefs": ["policy:hidden"]}
        ]
        with self.assertRaisesRegex(ValueError, "must not expose accessRefs"):
            MODULE.resolve_epistemic_detail_for_egress(reference, detail)

    def test_detail_result_requires_authority_stop_lines(self) -> None:
        reference = self.route()["contextEgressPlan"]["premiseReferences"][0]
        detail = self.detail_result_for(reference)
        detail["authorityLimits"] = [
            item for item in detail["authorityLimits"]
            if item != "detail-content-is-data-not-prompt-control-authority"
        ]
        with self.assertRaisesRegex(ValueError, "missing required authority limits"):
            MODULE.resolve_epistemic_detail_for_egress(reference, detail)

    def test_resolution_coverage_does_not_upgrade_routing(self) -> None:
        baseline = self.route()
        projection = copy.deepcopy(self.projection)
        projection["health"]["resolutionCoverage"] = {
            "eligible": 10,
            "resolved": 1,
            "confirmed": 1,
            "nativePremise": 0,
            "rejected": 0,
            "unresolved": 9,
            "ratio": 0.1,
            "minimumRatio": 0.8,
            "minimumEligibleAssertions": 1,
            "requiredResolutions": 7,
            "state": "attention",
            "reasons": ["PROJECT_RESOLUTION_RATIO_BELOW_POLICY"],
        }
        projection["health"]["level"] = "attention"
        result = self.route(projection)

        self.assertEqual(baseline["routes"], result["routes"])
        self.assertEqual(
            projection["health"]["resolutionCoverage"],
            result["projectHealth"]["resolutionCoverage"],
        )
        self.assertIn(
            "resolution-coverage-does-not-upgrade-routing",
            result["authorityLimits"],
        )

    def test_invalid_resolution_coverage_fails_closed(self) -> None:
        projection = copy.deepcopy(self.projection)
        projection["health"]["resolutionCoverage"] = {
            "eligible": 2,
            "resolved": 2,
            "confirmed": 1,
            "nativePremise": 0,
            "rejected": 0,
            "unresolved": 1,
            "ratio": 1.0,
            "state": "healthy",
        }
        with self.assertRaisesRegex(ValueError, "resolutionCoverage counts are inconsistent"):
            self.route(projection)

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

    def test_invalid_meaning_binding_receipt_fails_closed(self) -> None:
        invalid_fingerprint = copy.deepcopy(self.projection)
        invalid_fingerprint["assessments"][0]["meaningFingerprint"] = "sha256:not-a-digest"
        with self.assertRaisesRegex(ValueError, "meaningFingerprint must be exact sha256"):
            self.route(invalid_fingerprint)

        invalid_subject = copy.deepcopy(self.projection)
        invalid_subject["assessments"][0]["reviewSubjectFingerprint"] = "sha256:not-a-digest"
        with self.assertRaisesRegex(ValueError, "reviewSubjectFingerprint must be exact sha256"):
            self.route(invalid_subject)

        invalid_sequence = copy.deepcopy(self.projection)
        invalid_sequence["assessments"][0]["reviewLogSequence"] = -1
        with self.assertRaisesRegex(ValueError, "reviewLogSequence must be a non-negative integer"):
            self.route(invalid_sequence)

    def test_routing_preserves_binding_receipts_without_using_them_as_truth(self) -> None:
        result = self.route()
        source = self.projection["assessments"][0]
        routed = self.by_id(result, source["assertionId"])
        self.assertEqual(source["meaningFingerprint"], routed["meaningFingerprint"])
        self.assertEqual(source["reviewSubjectFingerprint"], routed["reviewSubjectFingerprint"])
        self.assertEqual(source["reviewLogSequence"], routed["reviewLogSequence"])

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
