from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from validate_governance import validate_governance  # noqa: E402

MANIFEST_PATH = HERE / "governance.json"


class WorkloadClassGovernanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.doc = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    def assert_error(self, doc: dict, fragment: str) -> None:
        errors = validate_governance(doc)
        self.assertTrue(
            any(fragment in error for error in errors),
            f"expected error containing {fragment!r}; got {errors!r}",
        )

    def test_current_candidate_manifest_is_valid(self) -> None:
        self.assertEqual(validate_governance(self.doc), [])

    def test_top_level_schema_is_strict(self) -> None:
        doc = copy.deepcopy(self.doc)
        doc["inferred_confidence"] = 0.9
        self.assert_error(doc, "top-level schema must remain strict")

    def test_validation_as_of_requires_utc_second(self) -> None:
        for value in ("2026-09-20T00:00:00", "2026-09-20", None):
            with self.subTest(value=value):
                doc = copy.deepcopy(self.doc)
                doc["validation_as_of"] = value
                self.assert_error(doc, "validation_as_of must be a UTC-second timestamp")

    def test_policy_allowlist_is_exact(self) -> None:
        doc = copy.deepcopy(self.doc)
        doc["allowed_policy_ids"].append("adaptive")
        self.assert_error(doc, "allowed_policy_ids must remain")

    def test_class_policy_map_is_exact(self) -> None:
        doc = copy.deepcopy(self.doc)
        doc["required_class_policy_map"]["general"] = "cap64"
        self.assert_error(doc, "required_class_policy_map must remain")

    def test_governance_fail_closed_flags_cannot_weaken(self) -> None:
        for key in (
            "exact_class_match_required",
            "caller_owned_provenance_required",
            "review_required_before_resolution",
            "expiry_fail_closed",
            "superseded_version_fail_closed",
        ):
            with self.subTest(key=key):
                doc = copy.deepcopy(self.doc)
                doc["governance"][key] = False
                self.assert_error(doc, f"governance.{key} must remain true")

    def test_governance_cannot_enable_inference_or_activation(self) -> None:
        for key in (
            "automatic_class_inference_implemented",
            "probabilistic_classifier_implemented",
            "automatic_activation_implemented",
            "semantic_correctness_inferred",
            "production_activation_allowed",
        ):
            with self.subTest(key=key):
                doc = copy.deepcopy(self.doc)
                doc["governance"][key] = True
                self.assert_error(doc, f"governance.{key} must remain false")

    def test_unknown_class_is_rejected(self) -> None:
        doc = copy.deepcopy(self.doc)
        doc["classes"][0]["class_id"] = "unknown"
        self.assert_error(doc, "must be a registered B6g class")

    def test_noncanonical_class_is_rejected(self) -> None:
        doc = copy.deepcopy(self.doc)
        doc["classes"][0]["class_id"] = " General"
        self.assert_error(doc, "canonical lower-kebab-case")

    def test_policy_must_match_registered_class(self) -> None:
        doc = copy.deepcopy(self.doc)
        doc["classes"][0]["policy_id"] = "baseline"
        self.assert_error(doc, "policy_id must match required_class_policy_map")

    def test_version_rejects_bool_zero_and_negative(self) -> None:
        for value in (True, 0, -1):
            with self.subTest(value=value):
                doc = copy.deepcopy(self.doc)
                doc["classes"][0]["version"] = value
                self.assert_error(doc, "version must be an integer >= 1")

    def test_owner_and_provenance_refs_are_required(self) -> None:
        for key in ("owner_ref", "provenance_ref"):
            with self.subTest(key=key):
                doc = copy.deepcopy(self.doc)
                doc["classes"][0][key] = " "
                self.assert_error(doc, f"{key} must be a non-empty canonical ref")

    def test_declared_at_cannot_follow_valid_from(self) -> None:
        doc = copy.deepcopy(self.doc)
        doc["classes"][0]["declared_at"] = "2026-09-20T00:00:00Z"
        self.assert_error(doc, "declared_at must be <= valid_from")

    def test_review_due_must_follow_valid_from(self) -> None:
        doc = copy.deepcopy(self.doc)
        doc["classes"][0]["review_due_at"] = doc["classes"][0]["valid_from"]
        self.assert_error(doc, "review_due_at must be later than valid_from")

    def test_expiry_must_follow_review_due(self) -> None:
        doc = copy.deepcopy(self.doc)
        doc["classes"][0]["expires_at"] = doc["classes"][0]["review_due_at"]
        self.assert_error(doc, "expires_at must be later than review_due_at")

    def test_candidate_is_fail_closed(self) -> None:
        for entry in self.doc["classes"]:
            self.assertEqual(entry["state"], "candidate")
            self.assertFalse(entry["resolution_allowed"])
            self.assertIsNone(entry["review"])

    def test_candidate_cannot_remain_after_expiry(self) -> None:
        doc = copy.deepcopy(self.doc)
        doc["validation_as_of"] = "2026-12-18T00:00:00Z"
        self.assert_error(doc, "candidate state cannot remain after expiry")

    def test_reviewed_state_requires_strict_review_metadata(self) -> None:
        doc = copy.deepcopy(self.doc)
        entry = doc["classes"][0]
        entry["state"] = "reviewed"
        entry["resolution_allowed"] = True
        entry["review"] = {}
        self.assert_error(doc, "reviewed state requires strict review metadata")

    def _make_reviewed(self, doc: dict, index: int = 0) -> dict:
        entry = doc["classes"][index]
        entry["state"] = "reviewed"
        entry["resolution_allowed"] = True
        entry["review"] = {
            "state": "reviewed",
            "reviewer_ref": "reviewer:synthetic-governance",
            "reviewed_at": "2026-09-19T12:00:00Z",
            "change_review_ref": "review:synthetic-b6i-v1",
            "evidence_refs": [
                "workload_policy_envelope_evidence_2026-09-19.json",
                "workload_policy_declaration_sensitivity_evidence_2026-09-19.json",
            ],
        }
        return entry

    def test_reviewed_state_can_resolve_with_complete_review(self) -> None:
        doc = copy.deepcopy(self.doc)
        self._make_reviewed(doc)
        self.assertEqual(validate_governance(doc), [])

    def test_reviewed_state_requires_evidence_refs(self) -> None:
        doc = copy.deepcopy(self.doc)
        entry = self._make_reviewed(doc)
        entry["review"]["evidence_refs"] = []
        self.assert_error(doc, "review.evidence_refs must be a non-empty")

    def test_reviewed_at_cannot_predate_declaration(self) -> None:
        doc = copy.deepcopy(self.doc)
        entry = self._make_reviewed(doc)
        entry["review"]["reviewed_at"] = "2026-09-18T23:59:59Z"
        self.assert_error(doc, "reviewed_at cannot predate declared_at")

    def test_reviewed_at_cannot_follow_logical_as_of(self) -> None:
        doc = copy.deepcopy(self.doc)
        entry = self._make_reviewed(doc)
        entry["review"]["reviewed_at"] = "2026-09-21T00:00:00Z"
        self.assert_error(doc, "reviewed_at cannot follow validation_as_of")

    def test_reviewed_state_cannot_resolve_before_valid_from(self) -> None:
        doc = copy.deepcopy(self.doc)
        self._make_reviewed(doc)
        doc["validation_as_of"] = "2026-09-18T23:59:59Z"
        self.assert_error(doc, "reviewed state cannot resolve before valid_from")

    def test_reviewed_state_fails_closed_when_review_is_due(self) -> None:
        doc = copy.deepcopy(self.doc)
        self._make_reviewed(doc)
        doc["validation_as_of"] = "2026-10-19T00:00:00Z"
        self.assert_error(doc, "reviewed state cannot remain after review_due_at")

    def test_reviewed_state_fails_closed_at_expiry(self) -> None:
        doc = copy.deepcopy(self.doc)
        self._make_reviewed(doc)
        doc["validation_as_of"] = "2026-12-18T00:00:00Z"
        self.assert_error(doc, "reviewed state cannot remain at/after expiry")

    def test_expired_state_requires_expired_as_of(self) -> None:
        doc = copy.deepcopy(self.doc)
        entry = doc["classes"][0]
        entry["state"] = "expired"
        self.assert_error(doc, "expired state requires validation_as_of >= expires_at")

    def test_expired_state_is_valid_at_expiry_and_fails_closed(self) -> None:
        doc = copy.deepcopy(self.doc)
        doc["validation_as_of"] = doc["classes"][0]["expires_at"]
        for entry in doc["classes"]:
            entry["state"] = "expired"
            self.assertFalse(entry["resolution_allowed"])
        self.assertEqual(validate_governance(doc), [])

    def test_version_above_one_requires_supersedes_version(self) -> None:
        doc = copy.deepcopy(self.doc)
        doc["classes"][0]["version"] = 2
        self.assert_error(doc, "version > 1 requires supersedes_version")

    def test_superseded_state_requires_newer_version(self) -> None:
        doc = copy.deepcopy(self.doc)
        entry = doc["classes"][0]
        entry["state"] = "superseded"
        self.assert_error(doc, "superseded state requires superseded_by_version")

    def test_supersession_must_be_bidirectional(self) -> None:
        doc = copy.deepcopy(self.doc)
        old = doc["classes"][0]
        old["state"] = "superseded"
        old["superseded_by_version"] = 2
        new = copy.deepcopy(old)
        new["version"] = 2
        new["state"] = "candidate"
        new["superseded_by_version"] = None
        new["supersedes_version"] = None
        doc["classes"].append(new)
        self.assert_error(doc, "version > 1 requires supersedes_version")

    def test_valid_supersession_chain_keeps_old_version_closed(self) -> None:
        doc = copy.deepcopy(self.doc)
        old = doc["classes"][0]
        old["state"] = "superseded"
        old["superseded_by_version"] = 2
        new = copy.deepcopy(old)
        new["version"] = 2
        new["state"] = "candidate"
        new["superseded_by_version"] = None
        new["supersedes_version"] = 1
        new["resolution_allowed"] = False
        doc["classes"].append(new)
        self.assertEqual(validate_governance(doc), [])

    def test_nonlatest_version_cannot_resolve(self) -> None:
        doc = copy.deepcopy(self.doc)
        old = self._make_reviewed(doc)
        old["state"] = "superseded"
        old["review"] = None
        old["resolution_allowed"] = True
        old["superseded_by_version"] = 2
        new = copy.deepcopy(old)
        new["version"] = 2
        new["state"] = "candidate"
        new["resolution_allowed"] = False
        new["supersedes_version"] = 1
        new["superseded_by_version"] = None
        doc["classes"].append(new)
        self.assert_error(doc, "must fail closed")

    def test_stop_flags_cannot_claim_truth_or_production(self) -> None:
        for key in (
            "semantic_correctness_claimed",
            "real_world_declaration_error_rate_claimed",
            "production_activation_enabled",
            "b5_entry_gate_changed",
        ):
            with self.subTest(key=key):
                doc = copy.deepcopy(self.doc)
                doc["stop_flags"][key] = True
                self.assert_error(doc, f"stop_flags.{key} must remain false")


if __name__ == "__main__":
    unittest.main()
