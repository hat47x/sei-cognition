#!/usr/bin/env python3

from __future__ import annotations

import json
import unittest
from pathlib import Path
from typing import Any


EVIDENCE_PATH = Path(__file__).with_name(
    "actual_provider_missing_revision_observation_20260910.json"
)
FORBIDDEN_SECRET_KEYS = {
    "token",
    "accessToken",
    "apiKey",
    "password",
    "secret",
    "authorization",
}


def legacy_name(name: str) -> str:
    """ADR-0031の3。改名前に記録されたEvidenceが持つ旧名を返す。

    このEvidenceはADR-0031の4-aによりbyte単位で不変である。当時のprobeは
    `Soza` / `SOZA`のままclaim keyとstop lineを書いた。読み取り側だけが
    新旧双方を受け付ける。記録が存在する限り必要な恒久措置である。
    """
    return name.replace("Sei", "Soza").replace("SEI", "SOZA")


def load_evidence() -> dict:
    return json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))


def walk_keys(value: Any) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            keys.add(key)
            keys.update(walk_keys(child))
    elif isinstance(value, list):
        for child in value:
            keys.update(walk_keys(child))
    return keys


class ActualProviderMissingRevisionObservationTest(unittest.TestCase):
    def test_observation_is_provider_local_and_non_universal(self) -> None:
        evidence = load_evidence()
        self.assertEqual(evidence["scope"], "actual-provider-service-observation")
        self.assertEqual(evidence["authority"], "non-universal")
        self.assertEqual(evidence["provider"], "github-rest-api")
        self.assertNotIn("universalFailureCode", evidence)
        self.assertIn("not Universal failure semantics", evidence["providerVocabularyBoundary"])

    def test_control_revision_confirms_endpoint_family_is_reachable(self) -> None:
        control = load_evidence()["controlObservation"]
        self.assertEqual(control["outcome"], "success")
        self.assertEqual(control["requestedRevision"], control["observedRevision"])
        self.assertEqual(
            control["observedRevision"],
            "aa3651f3460a6db7dc70bd848f93b600f149ffe8",
        )

    def test_missing_revision_is_recorded_as_provider_rejection(self) -> None:
        negative = load_evidence()["negativeObservation"]
        self.assertEqual(negative["outcome"], "provider-rejection")
        self.assertEqual(
            negative["requestedRevision"],
            "0000000000000000000000000000000000000000",
        )
        self.assertEqual(negative["providerLocalStatus"], 422)
        self.assertEqual(
            negative["candidateEvaluationRelation"],
            "artifact-acquisition-requested-revision-unavailable",
        )

    def test_no_secret_material_is_persisted(self) -> None:
        evidence = load_evidence()
        self.assertTrue(FORBIDDEN_SECRET_KEYS.isdisjoint(walk_keys(evidence)))
        self.assertFalse(evidence["secretHandling"]["credentialMaterialPersisted"])
        self.assertFalse(evidence["secretHandling"]["rawAuthorizationPersisted"])

    def test_provider_service_observation_does_not_claim_sei_integration(self) -> None:
        claims = load_evidence()["claims"]
        self.assertTrue(claims["actualProviderServiceObservation"])
        self.assertTrue(claims["actualProviderServiceMissingRevisionEvidence"])
        for key in (
            "actualSeiGitHubCommitServiceExecution",
            "actualSeiLiveFailureRunnerExecution",
            "credentialRejectionEvidence",
            "actualProviderIntegrationFailureEvidence",
            "actualDeploymentFailureEvidence",
            "operationalEvidence",
            "adoptionOutcomeEvidence",
        ):
            recorded = key if key in claims else legacy_name(key)
            self.assertIn(recorded, claims, key)
            self.assertFalse(claims[recorded], key)

    def test_stop_line_keeps_higher_evidence_separate(self) -> None:
        stop_line = load_evidence()["stopLine"]
        self.assertIn("missing-revision rejection observed", stop_line)
        probe_claim = "SEI GitHubCommitService negative probe executed"
        self.assertTrue(
            probe_claim in stop_line or legacy_name(probe_claim) in stop_line,
            stop_line,
        )
        self.assertIn("Operational Evidence", stop_line)


if __name__ == "__main__":
    unittest.main()
