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
        self.assertEqual(validate_unlock(doc), [])


if __name__ == "__main__":
    unittest.main()
