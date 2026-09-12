#!/usr/bin/env python3

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


EVIDENCE_PATH = Path(__file__).with_name("scoped_go_failure_execution_20260910.json")
SHA40 = re.compile(r"^[0-9a-f]{40}$")


def load_evidence() -> dict:
    return json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))


class ScopedGoFailureExecutionEvidenceTest(unittest.TestCase):
    def test_scope_and_source_commit_are_explicit(self) -> None:
        data = load_evidence()
        self.assertEqual(data["scope"], "scoped-main-source-slice")
        self.assertEqual(
            data["sourceMainCommit"],
            "fc9c7b41d8c6cae60ff1549ebb679a9888efc2a1",
        )
        self.assertTrue(SHA40.fullmatch(data["sourceMainCommit"]))
        self.assertFalse(data["reconstruction"]["fullRepositoryCheckout"])
        self.assertTrue(data["reconstruction"]["connectorFetchedMainSource"])

    def test_source_identity_includes_both_failure_test_files(self) -> None:
        data = load_evidence()
        source_files = {
            item["path"]: item["blobSha"]
            for item in data["reconstruction"]["sourceFiles"]
        }
        self.assertEqual(
            source_files["runtime/go/provideradapter/failure_behavior_test.go"],
            "38f7f89c38b6efc3655cc43d93f552c2081d2886",
        )
        self.assertEqual(
            source_files["runtime/go/liveintegration/github_failure_probe_test.go"],
            "7ab829873fb189763eb2c71cbc0954733fe8a0b7",
        )
        self.assertTrue(all(SHA40.fullmatch(sha) for sha in source_files.values()))

    def test_execution_toolchain_does_not_claim_repository_baseline(self) -> None:
        environment = load_evidence()["executionEnvironment"]
        self.assertEqual(environment["goVersion"], "go1.23.2")
        self.assertEqual(environment["repositoryBaselineGo"], "1.25")
        self.assertFalse(environment["baselineToolchainVerified"])
        self.assertFalse(environment["outboundNetworkAvailable"])

    def test_scoped_failure_slices_pass(self) -> None:
        results = load_evidence()["results"]
        self.assertEqual(results["providerAdapterFailureSlice"]["status"], "pass")
        self.assertEqual(
            set(results["providerAdapterFailureSlice"]["tests"]),
            {
                "TestFailureBehaviorMappingFailureDoesNotEmitPartialObservation",
                "TestFailureBehaviorSemanticValidationRejectsInvalidMappedObservation",
                "TestFailureBehaviorRetryKeepsInitialMappingFailureDistinct",
            },
        )
        self.assertEqual(
            results["liveIntegrationSecretSafeDeterministic"]["status"], "pass"
        )
        self.assertEqual(
            results["liveIntegrationSecretSafeDeterministic"]["tests"],
            ["TestGitHubCommitServiceHTTPFailureDoesNotLeakToken"],
        )

    def test_actual_live_provider_tests_remain_unexecuted(self) -> None:
        actual = load_evidence()["results"]["actualLiveProviderTests"]
        self.assertEqual(actual["status"], "not-executed")
        self.assertEqual(
            set(actual["tests"]),
            {
                "TestLiveGitHubCommitServiceMissingRevisionFailure",
                "TestLiveGitHubCommitServiceInvalidCredentialFailure",
            },
        )

    def test_evidence_claims_fail_closed_at_higher_levels(self) -> None:
        data = load_evidence()
        claims = data["claims"]
        self.assertTrue(claims["scopedExecutableEvidence"])
        for key in (
            "fullRepositoryRegression",
            "go125BaselineVerified",
            "actualProviderFailureEvidence",
            "actualDeploymentFailureEvidence",
            "operationalEvidence",
            "adoptionOutcomeEvidence",
        ):
            self.assertFalse(claims[key], key)
        self.assertIn("scoped main-source failure slice PASS", data["stopLine"])
        self.assertIn("actual Provider failure Evidence", data["stopLine"])


if __name__ == "__main__":
    unittest.main()
