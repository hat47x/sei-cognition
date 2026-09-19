from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVALUATION_DIR = ROOT / "evaluation" / "sparse-associative-cognition"
if str(EVALUATION_DIR) not in sys.path:
    sys.path.insert(0, str(EVALUATION_DIR))

from validate_cross_stage_preregistration import (  # noqa: E402
    validate_pre_run_prerequisites,
    validate_preregistration,
    validate_unlock,
)

PREREG_PATH = EVALUATION_DIR / "cross_stage_benchmark_preregistration.json"


class CrossStagePreregistrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.doc = json.loads(PREREG_PATH.read_text(encoding="utf-8"))

    def assert_has_error(self, errors: list[str], fragment: str) -> None:
        self.assertTrue(
            any(fragment in error for error in errors),
            f"expected error containing {fragment!r}; got {errors!r}",
        )

    def test_current_preregistration_is_structurally_valid_and_locked(self) -> None:
        self.assertEqual(validate_preregistration(self.doc), [])
        self.assertTrue(validate_unlock(self.doc))

    def test_preregistration_can_never_enable_result_generation(self) -> None:
        doc = copy.deepcopy(self.doc)
        doc["result_generation"]["enabled"] = True
        self.assert_has_error(validate_preregistration(doc), "enabled must remain false")

    def test_unfrozen_adjudication_cannot_unlock(self) -> None:
        self.assert_has_error(validate_unlock(self.doc), "human adjudication state=frozen")

    def test_freeze_kit_draft_keeps_unlock_closed(self) -> None:
        self.assert_has_error(validate_unlock(self.doc), "frozen freeze-kit bundle")

    def test_freeze_kit_cannot_enable_results_after_freeze(self) -> None:
        doc = copy.deepcopy(self.doc)
        doc["freeze_kit"]["result_generation_enabled_after_freeze"] = True
        self.assert_has_error(
            validate_preregistration(doc),
            "must not enable result generation after freeze",
        )

    def test_freeze_kit_cannot_open_b5(self) -> None:
        doc = copy.deepcopy(self.doc)
        doc["freeze_kit"]["b5_entry_gate_changed"] = True
        self.assert_has_error(validate_preregistration(doc), "must not change B5 entry gate")

    def test_freeze_kit_state_and_frozen_flag_must_match(self) -> None:
        doc = copy.deepcopy(self.doc)
        doc["freeze_kit"]["state"] = "frozen"
        self.assert_has_error(
            validate_preregistration(doc),
            "current_bundle_is_frozen must match",
        )

    def test_evaluation_run_draft_keeps_full_unlock_closed(self) -> None:
        doc = copy.deepcopy(self.doc)
        self.assertEqual(doc["evaluation_run"]["state"], "draft")
        self.assertFalse(doc["evaluation_run"]["current_run_authorized"])

    def test_evaluation_run_state_and_authorized_flag_must_match(self) -> None:
        doc = copy.deepcopy(self.doc)
        doc["evaluation_run"]["state"] = "authorized"
        self.assert_has_error(
            validate_preregistration(doc),
            "current_run_authorized must match",
        )

    def test_evaluation_run_cannot_embed_executor_or_results_in_this_slice(self) -> None:
        for key in ("executor_implemented", "result_artifact_generated"):
            with self.subTest(key=key):
                doc = copy.deepcopy(self.doc)
                doc["evaluation_run"][key] = True
                self.assert_has_error(validate_preregistration(doc), key)

    def test_evaluation_run_cannot_open_b5_or_change_production_default(self) -> None:
        for key in ("b5_entry_gate_changed", "production_default_changed"):
            with self.subTest(key=key):
                doc = copy.deepcopy(self.doc)
                doc["evaluation_run"][key] = True
                self.assertTrue(validate_preregistration(doc))

    def test_result_artifact_draft_is_registered_without_results(self) -> None:
        self.assertEqual(self.doc["result_artifact"]["state"], "draft")
        self.assertFalse(self.doc["result_artifact"]["current_result_completed"])
        self.assertFalse(self.doc["result_artifact"]["semantic_interpretation_generated"])

    def test_result_artifact_state_and_completed_flag_must_match(self) -> None:
        doc = copy.deepcopy(self.doc)
        doc["result_artifact"]["state"] = "completed"
        self.assert_has_error(
            validate_preregistration(doc),
            "current_result_completed must match",
        )

    def test_result_artifact_cannot_generate_interpretation_in_this_slice(self) -> None:
        doc = copy.deepcopy(self.doc)
        doc["result_artifact"]["semantic_interpretation_generated"] = True
        self.assert_has_error(
            validate_preregistration(doc),
            "semantic_interpretation_generated must remain false",
        )

    def test_result_artifact_cannot_open_b5_or_change_production_default(self) -> None:
        for key in ("b5_entry_gate_changed", "production_default_changed"):
            with self.subTest(key=key):
                doc = copy.deepcopy(self.doc)
                doc["result_artifact"][key] = True
                self.assertTrue(validate_preregistration(doc))

    def test_interpretation_artifact_draft_is_registered(self) -> None:
        artifact = self.doc["interpretation_artifact"]
        self.assertEqual(artifact["state"], "draft")
        self.assertFalse(artifact["current_interpretation_generated"])
        self.assertTrue(artifact["requires_completed_result"])

    def test_interpretation_artifact_state_and_generated_flag_must_match(self) -> None:
        doc = copy.deepcopy(self.doc)
        doc["interpretation_artifact"]["state"] = "interpreted"
        self.assert_has_error(
            validate_preregistration(doc),
            "current_interpretation_generated must match",
        )

    def test_interpretation_artifact_requires_completed_result_contract(self) -> None:
        doc = copy.deepcopy(self.doc)
        doc["interpretation_artifact"]["requires_completed_result"] = False
        self.assert_has_error(
            validate_preregistration(doc),
            "requires_completed_result must remain true",
        )

    def test_interpreted_state_requires_completed_result_state(self) -> None:
        doc = copy.deepcopy(self.doc)
        doc["interpretation_artifact"].update({
            "state": "interpreted",
            "current_interpretation_generated": True,
        })
        self.assert_has_error(
            validate_preregistration(doc),
            "requires result_artifact.state=completed",
        )

    def test_interpretation_artifact_cannot_become_decision(self) -> None:
        for key in (
            "semantic_truth_claimed",
            "variant_winner_declared",
            "recommendation_generated",
            "b5_decision_generated",
            "production_default_changed",
        ):
            with self.subTest(key=key):
                doc = copy.deepcopy(self.doc)
                doc["interpretation_artifact"][key] = True
                self.assert_has_error(
                    validate_preregistration(doc),
                    f"interpretation_artifact.{key} must remain false",
                )

    def test_decision_artifact_draft_is_registered(self) -> None:
        artifact = self.doc["decision_artifact"]
        self.assertEqual(artifact["state"], "draft")
        self.assertFalse(artifact["current_decision_generated"])
        self.assertEqual(artifact["current_disposition"], "not-assessed")
        self.assertTrue(artifact["requires_interpreted_artifact"])
        self.assertFalse(artifact["b5_review_requested"])

    def test_decision_artifact_state_and_generated_flag_must_match(self) -> None:
        doc = copy.deepcopy(self.doc)
        doc["decision_artifact"]["state"] = "decided"
        self.assert_has_error(
            validate_preregistration(doc),
            "current_decision_generated must match",
        )

    def test_decision_artifact_requires_interpreted_artifact_contract(self) -> None:
        doc = copy.deepcopy(self.doc)
        doc["decision_artifact"]["requires_interpreted_artifact"] = False
        self.assert_has_error(
            validate_preregistration(doc),
            "requires_interpreted_artifact must remain true",
        )

    def test_decided_state_requires_interpreted_upstream_state(self) -> None:
        doc = copy.deepcopy(self.doc)
        doc["decision_artifact"].update({
            "state": "decided",
            "current_decision_generated": True,
            "current_disposition": "retain-current-stage",
        })
        self.assert_has_error(
            validate_preregistration(doc),
            "requires interpretation_artifact.state=interpreted",
        )

    def test_request_b5_review_does_not_open_b5_gate(self) -> None:
        doc = copy.deepcopy(self.doc)
        doc["interpretation_artifact"].update({
            "state": "interpreted",
            "current_interpretation_generated": True,
        })
        doc["result_artifact"].update({
            "state": "completed",
            "current_result_completed": True,
        })
        doc["decision_artifact"].update({
            "state": "decided",
            "current_decision_generated": True,
            "current_disposition": "request-b5-review",
            "b5_review_requested": True,
        })
        self.assertEqual(validate_preregistration(doc), [])
        self.assertFalse(doc["decision_artifact"]["b5_gate_opened"])

    def test_decision_artifact_cannot_become_truth_winner_gate_or_production(self) -> None:
        for key in (
            "semantic_truth_claimed",
            "variant_winner_selected",
            "b5_gate_opened",
            "production_default_changed",
        ):
            with self.subTest(key=key):
                doc = copy.deepcopy(self.doc)
                doc["decision_artifact"][key] = True
                self.assert_has_error(
                    validate_preregistration(doc),
                    f"decision_artifact.{key} must remain false",
                )

    def test_semantic_labels_cannot_be_embedded_in_preregistration(self) -> None:
        doc = copy.deepcopy(self.doc)
        doc["adjudication"]["semantic_labels_embedded_in_preregistration"] = True
        self.assert_has_error(validate_preregistration(doc), "semantic labels")

    def test_b3_prior_cannot_be_authored_from_evaluation_labels(self) -> None:
        doc = copy.deepcopy(self.doc)
        doc["b3_prior_manifest"]["evaluation_labels_may_not_author_prior"] = False
        self.assert_has_error(validate_preregistration(doc), "evaluation labels must not author B3 prior")

    def test_b4_fingerprint_cannot_use_evaluation_labels(self) -> None:
        doc = copy.deepcopy(self.doc)
        doc["tracks"]["familiarity"]["fingerprint_may_not_use_evaluation_labels"] = False
        self.assert_has_error(validate_preregistration(doc), "B4 fingerprint")

    def test_retrieval_split_overlap_is_rejected(self) -> None:
        doc = copy.deepcopy(self.doc)
        doc["tracks"]["retrieval"]["split_manifest"]["calibration_ids"] = ["x"]
        doc["tracks"]["retrieval"]["split_manifest"]["evaluation_ids"] = ["x"]
        self.assert_has_error(validate_preregistration(doc), "retrieval calibration/evaluation ids")

    def test_familiarity_split_overlap_is_rejected(self) -> None:
        doc = copy.deepcopy(self.doc)
        doc["tracks"]["familiarity"]["split_manifest"]["calibration_ids"] = ["x"]
        doc["tracks"]["familiarity"]["split_manifest"]["evaluation_ids"] = ["x"]
        self.assert_has_error(validate_preregistration(doc), "familiarity calibration/evaluation ids")

    def test_b7_training_holdout_overlap_is_rejected(self) -> None:
        doc = copy.deepcopy(self.doc)
        doc["tracks"]["routing"]["split_manifest"]["training_outcome_ids"] = ["x"]
        doc["tracks"]["routing"]["split_manifest"]["holdout_replay_ids"] = ["x"]
        self.assert_has_error(validate_preregistration(doc), "B7 training/holdout ids")

    def test_b6_diagnostics_cannot_be_promoted_to_semantic_scores(self) -> None:
        doc = copy.deepcopy(self.doc)
        doc["capacity_profiles"]["diagnostics_are_not_semantic_scores"] = False
        self.assert_has_error(validate_preregistration(doc), "must not become semantic scores")

    def test_b6d_b6e_stress_track_cannot_define_production_default(self) -> None:
        doc = copy.deepcopy(self.doc)
        doc["capacity_profiles"]["stress_track"]["may_not_define_production_default"] = False
        self.assert_has_error(validate_preregistration(doc), "must not define production default")

    def test_feature_cardinality_cannot_become_semantic_priority(self) -> None:
        doc = copy.deepcopy(self.doc)
        doc["capacity_profiles"]["stress_track"]["may_not_use_feature_cardinality_as_semantic_priority"] = False
        self.assert_has_error(validate_preregistration(doc), "feature cardinality must not become semantic priority")

    def test_single_composite_score_remains_prohibited(self) -> None:
        doc = copy.deepcopy(self.doc)
        doc["evaluation_policy"]["no_single_composite_score"] = False
        self.assert_has_error(validate_preregistration(doc), "no_single_composite_score")

    def test_b5_gate_cannot_be_opened_by_preregistration(self) -> None:
        doc = copy.deepcopy(self.doc)
        doc["b5_gate"]["state"] = "open"
        self.assert_has_error(validate_preregistration(doc), "B5 gate must remain closed")

    def test_frozen_unlock_still_requires_all_manifests_and_splits(self) -> None:
        doc = copy.deepcopy(self.doc)
        doc["adjudication"].update({
            "state": "frozen",
            "dataset_digest": "sha256:fixture",
            "adjudication_manifest_ref": "fixture:adjudication",
        })
        doc["b3_prior_manifest"].update({
            "state": "frozen",
            "manifest_ref": "fixture:b3-prior",
        })
        for track in ("retrieval", "familiarity"):
            doc["tracks"][track]["split_manifest"].update({
                "state": "frozen",
                "calibration_ids": [f"{track}-cal"],
                "evaluation_ids": [f"{track}-eval"],
            })
        doc["tracks"]["routing"]["split_manifest"].update({
            "state": "frozen",
            "training_outcome_ids": ["route-train"],
            "holdout_replay_ids": ["route-holdout"],
        })
        doc["freeze_kit"].update({
            "state": "frozen",
            "current_bundle_is_frozen": True,
        })
        self.assertEqual(validate_pre_run_prerequisites(doc), [])
        self.assert_has_error(
            validate_unlock(doc),
            "authorized explicit evaluation-run artifact",
        )
        doc["evaluation_run"].update({
            "state": "authorized",
            "current_run_authorized": True,
        })
        self.assertEqual(validate_unlock(doc), [])


if __name__ == "__main__":
    unittest.main()
