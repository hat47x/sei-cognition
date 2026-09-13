#!/usr/bin/env python3

from __future__ import annotations

import json
import unittest
from pathlib import Path


AUDIT_PATH = Path(__file__).with_name("requirement_audit.json")
EXPECTED_REQUIREMENTS = {
    "REQ-0002",
    "REQ-0006",
    "REQ-0007",
    "REQ-0020",
    "REQ-0021",
    "REQ-0022",
}
EXPECTED_SCENARIOS = {"SCN-0010", "SCN-0011", "SCN-0017", "SCN-0018"}


def load_audit() -> dict:
    return json.loads(AUDIT_PATH.read_text(encoding="utf-8"))


class FailureBehaviorRequirementAuditTest(unittest.TestCase):
    def test_audit_is_completed_no_change_for_issue_000072(self) -> None:
        audit = load_audit()
        self.assertEqual(audit["schema"], "sei.failure-behavior-requirement-audit/v1")
        self.assertEqual(audit["issue"], "ISSUE-000072")
        self.assertEqual(audit["status"], "completed-no-change-at-current-evidence-height")
        self.assertEqual(audit["decision"]["conclusion"], "no-change")

    def test_audit_reviews_existing_requirements_and_scenarios(self) -> None:
        audit = load_audit()
        self.assertEqual(set(audit["reviewedRequirements"]), EXPECTED_REQUIREMENTS)
        self.assertEqual(set(audit["reviewedScenarios"]), EXPECTED_SCENARIOS)

    def test_audit_does_not_silently_create_stable_semantics(self) -> None:
        decision = load_audit()["decision"]
        for key in (
            "newStableRequirement",
            "modifyExistingStableRequirement",
            "newAcceptanceScenario",
            "modifyExistingAcceptanceScenario",
            "newUniversalContractField",
        ):
            self.assertIs(decision[key], False, key)

    def test_scoped_go_execution_is_recorded_without_full_baseline_claim(self) -> None:
        audit = load_audit()
        claims = audit["evidenceClaims"]
        evidence = audit["currentEvidence"]
        self.assertTrue(claims["scopedMainSourceGoEvidence"])
        self.assertEqual(
            evidence["providerAdapterFailureTests"],
            "scoped-main-source-slice-pass-go1.23.2",
        )
        self.assertEqual(
            evidence["liveProviderSecretSafeDeterministicTest"],
            "scoped-main-source-slice-pass-go1.23.2",
        )
        self.assertFalse(claims["fullRepositoryRegression"])
        self.assertFalse(claims["go125BaselineVerified"])
        self.assertEqual(evidence["fullRepositoryGoRegression"], "not-yet-verified")
        self.assertEqual(evidence["go125Baseline"], "not-yet-verified")

    def test_actual_provider_service_observation_is_not_integration_evidence(self) -> None:
        audit = load_audit()
        claims = audit["evidenceClaims"]
        evidence = audit["currentEvidence"]
        self.assertTrue(claims["actualProviderServiceObservation"])
        self.assertEqual(
            evidence["actualProviderServiceMissingRevision"],
            "observed-provider-rejection-connected-github-api",
        )
        self.assertFalse(claims["actualProviderIntegrationFailureEvidence"])
        self.assertFalse(claims["credentialRejectionEvidence"])
        self.assertEqual(
            evidence["actualProviderIntegrationFailureProbe"],
            "not-yet-executed",
        )
        self.assertEqual(evidence["credentialRejectionProbe"], "not-yet-executed")

    def test_operational_and_adoption_evidence_remain_unverified(self) -> None:
        audit = load_audit()
        claims = audit["evidenceClaims"]
        self.assertTrue(claims["designEvidence"])
        self.assertTrue(claims["fixtureScopedExecutableEvidence"])
        self.assertFalse(claims["operationalEvidence"])
        self.assertFalse(claims["adoptionOutcomeEvidence"])
        self.assertEqual(
            audit["currentEvidence"]["operationalEvidence"],
            "not-yet-verified",
        )

    def test_no_change_has_explicit_revisit_triggers(self) -> None:
        audit = load_audit()
        triggers = audit["revisitTriggers"]
        self.assertGreaterEqual(len(triggers), 4)
        self.assertTrue(all(isinstance(item, str) and item.strip() for item in triggers))


if __name__ == "__main__":
    unittest.main()
