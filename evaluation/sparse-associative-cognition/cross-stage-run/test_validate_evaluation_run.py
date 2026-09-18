from __future__ import annotations

import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SACS_DIR = HERE.parent
FREEZE_DIR = SACS_DIR / "cross-stage-freeze"
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
if str(SACS_DIR) not in sys.path:
    sys.path.insert(0, str(SACS_DIR))
if str(FREEZE_DIR) not in sys.path:
    sys.path.insert(0, str(FREEZE_DIR))

from freeze_manifests import freeze_documents, load_directory  # noqa: E402
from validate_evaluation_run import (  # noqa: E402
    validate_authorized_run,
    validate_run_structure,
)

PREREG_PATH = SACS_DIR / "cross_stage_benchmark_preregistration.json"
RUN_PATH = HERE / "evaluation_run.json"


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def synthetic_freeze_draft() -> dict[str, dict]:
    ids = [
        "retrieval-cal",
        "retrieval-eval",
        "familiarity-cal",
        "familiarity-eval",
        "routing-train",
        "routing-holdout",
    ]
    return {
        "dataset": {
            "schema": "sei.sacs-cross-stage-dataset-manifest/v1alpha1",
            "state": "draft",
            "frozen_at": None,
            "items": [
                {
                    "id": item_id,
                    "source_ref": f"fixture:{item_id}",
                    "content_digest": sha(f"content:{item_id}"),
                }
                for item_id in ids
            ],
            "dataset_digest": "",
        },
        "adjudication": {
            "schema": "sei.sacs-cross-stage-adjudication-manifest/v1alpha1",
            "state": "draft",
            "frozen_at": None,
            "dataset_digest": "",
            "adjudication_policy_version": "v1alpha1",
            "reviewer_refs": ["reviewer:r1"],
            "judgments": [
                {
                    "id": f"j:{item_id}",
                    "item_id": item_id,
                    "reviewer_ref": "reviewer:r1",
                    "kind": "fixture-label",
                    "value": "accepted",
                }
                for item_id in ids
            ],
            "unresolved": [],
            "manifest_digest": "",
        },
        "split": {
            "schema": "sei.sacs-cross-stage-split-manifest/v1alpha1",
            "state": "draft",
            "frozen_at": None,
            "dataset_digest": "",
            "retrieval": {
                "calibration_ids": ["retrieval-cal"],
                "evaluation_ids": ["retrieval-eval"],
            },
            "familiarity": {
                "calibration_ids": ["familiarity-cal"],
                "evaluation_ids": ["familiarity-eval"],
            },
            "routing": {
                "training_outcome_ids": ["routing-train"],
                "holdout_replay_ids": ["routing-holdout"],
            },
            "manifest_digest": "",
        },
        "prior": {
            "schema": "sei.sacs-cross-stage-b3-prior-manifest/v1alpha1",
            "state": "draft",
            "frozen_at": None,
            "dataset_digest": "",
            "adjudication_manifest_digest": "",
            "evaluation_labels_used_for_authoring": False,
            "rules": [{
                "channel": "graph:relationType",
                "key": "causal",
                "multiplier": 1.01,
                "provenance_ref": "policy:pre-evaluation",
                "authoring_source": "domain-policy-before-evaluation",
            }],
            "manifest_digest": "",
        },
        "bundle": {
            "schema": "sei.sacs-cross-stage-freeze-bundle/v1alpha1",
            "state": "draft",
            "frozen_at": None,
            "dataset_manifest": {"ref": "dataset_manifest.json", "digest": ""},
            "adjudication_manifest": {"ref": "adjudication_manifest.json", "digest": ""},
            "split_manifest": {"ref": "split_manifest.json", "digest": ""},
            "b3_prior_manifest": {"ref": "b3_prior_manifest.json", "digest": ""},
            "result_generation_enabled": False,
            "b5_entry_gate_changed": False,
            "bundle_digest": "",
        },
    }


def frozen_prereg(frozen: dict[str, dict]) -> dict:
    prereg = json.loads(PREREG_PATH.read_text(encoding="utf-8"))
    prereg["adjudication"].update({
        "state": "frozen",
        "dataset_digest": frozen["dataset"]["dataset_digest"],
        "adjudication_manifest_ref": "cross-stage-freeze/adjudication_manifest.json",
    })
    prereg["b3_prior_manifest"].update({
        "state": "frozen",
        "manifest_ref": "cross-stage-freeze/b3_prior_manifest.json",
    })
    prereg["tracks"]["retrieval"]["split_manifest"].update({
        "state": "frozen",
        "calibration_ids": ["retrieval-cal"],
        "evaluation_ids": ["retrieval-eval"],
    })
    prereg["tracks"]["familiarity"]["split_manifest"].update({
        "state": "frozen",
        "calibration_ids": ["familiarity-cal"],
        "evaluation_ids": ["familiarity-eval"],
    })
    prereg["tracks"]["routing"]["split_manifest"].update({
        "state": "frozen",
        "training_outcome_ids": ["routing-train"],
        "holdout_replay_ids": ["routing-holdout"],
    })
    prereg["freeze_kit"].update({
        "state": "frozen",
        "current_bundle_is_frozen": True,
    })
    return prereg


def authorized_run(
    frozen: dict[str, dict],
    *,
    track: str = "retrieval",
    variant: str = "B1-B2",
    capacity_profile: str | None = "medium",
    stress_policy: str | None = None,
    metrics: list[str] | None = None,
) -> dict:
    run = json.loads(RUN_PATH.read_text(encoding="utf-8"))
    run.update({
        "state": "authorized",
        "run_id": "run:fixture:001",
        "authorized_at": "2026-09-18T11:30:00Z",
        "track": track,
        "variant": variant,
        "capacity_profile": capacity_profile,
        "stress_policy": stress_policy,
        "requested_metrics": metrics or ["recall_at_k"],
        "output_ref": "result:fixture:001",
    })
    run["freeze_bundle"]["digest"] = frozen["bundle"]["bundle_digest"]
    run["implementation"] = {
        "ref": "develop/v0.2.0",
        "commit": "a" * 40,
    }
    run["environment"] = {
        "os": "linux",
        "arch": "amd64",
        "runtime": "go1.25",
    }
    for key in run["authorization"]:
        run["authorization"][key] = True
    return run


class EvaluationRunTests(unittest.TestCase):
    def setUp(self) -> None:
        self.current_run = json.loads(RUN_PATH.read_text(encoding="utf-8"))
        self.current_prereg = json.loads(PREREG_PATH.read_text(encoding="utf-8"))
        self.current_freeze = load_directory(FREEZE_DIR)
        self.frozen = freeze_documents(
            synthetic_freeze_draft(),
            "2026-09-18T11:20:00Z",
        )
        self.prereg = frozen_prereg(self.frozen)

    def assert_error(self, errors: list[str], fragment: str) -> None:
        self.assertTrue(
            any(fragment in error for error in errors),
            f"expected {fragment!r}; got {errors!r}",
        )

    def test_current_draft_run_is_structurally_valid(self) -> None:
        self.assertEqual(validate_run_structure(self.current_run), [])

    def test_current_draft_bundle_cannot_authorize_run(self) -> None:
        run = copy.deepcopy(self.current_run)
        run.update({
            "state": "authorized",
            "run_id": "run:invalid-current",
            "authorized_at": "2026-09-18T11:30:00Z",
            "track": "retrieval",
            "variant": "B0",
            "capacity_profile": "small",
            "requested_metrics": ["recall_at_k"],
            "output_ref": "result:invalid-current",
        })
        run["implementation"] = {"ref": "develop/v0.2.0", "commit": "a" * 40}
        run["environment"] = {"os": "linux", "arch": "amd64", "runtime": "go1.25"}
        for key in run["authorization"]:
            run["authorization"][key] = True
        errors = validate_authorized_run(run, self.current_prereg, self.current_freeze)
        self.assert_error(errors, "frozen freeze bundle")

    def test_synthetic_frozen_primary_retrieval_run_can_authorize(self) -> None:
        run = authorized_run(self.frozen)
        self.assertEqual(validate_authorized_run(run, self.prereg, self.frozen), [])

    def test_synthetic_oversized_stress_run_can_authorize(self) -> None:
        run = authorized_run(
            self.frozen,
            capacity_profile="oversized-stress",
            stress_policy="cap128",
            metrics=["recall_at_k", "oversized_residual_policy_stress"],
        )
        self.assertEqual(validate_authorized_run(run, self.prereg, self.frozen), [])

    def test_primary_profile_cannot_set_stress_policy(self) -> None:
        run = authorized_run(self.frozen, stress_policy="cap64")
        self.assert_error(
            validate_authorized_run(run, self.prereg, self.frozen),
            "primary capacity profile cannot set stress_policy",
        )

    def test_stress_profile_requires_registered_policy(self) -> None:
        run = authorized_run(
            self.frozen,
            capacity_profile="oversized-stress",
            stress_policy="cap999",
            metrics=["oversized_residual_policy_stress"],
        )
        self.assert_error(
            validate_authorized_run(run, self.prereg, self.frozen),
            "requires a preregistered stress_policy",
        )

    def test_unknown_retrieval_variant_is_rejected(self) -> None:
        run = authorized_run(self.frozen, variant="B5")
        self.assert_error(
            validate_authorized_run(run, self.prereg, self.frozen),
            "variant is not preregistered",
        )

    def test_unknown_metric_is_rejected(self) -> None:
        run = authorized_run(self.frozen, metrics=["magic_score"])
        self.assert_error(
            validate_authorized_run(run, self.prereg, self.frozen),
            "metrics are not preregistered",
        )

    def test_primary_profile_cannot_request_stress_metric(self) -> None:
        run = authorized_run(
            self.frozen,
            metrics=["recall_at_k", "oversized_residual_policy_stress"],
        )
        self.assert_error(
            validate_authorized_run(run, self.prereg, self.frozen),
            "must not request oversized stress metric",
        )

    def test_familiarity_run_has_track_specific_variant(self) -> None:
        run = authorized_run(
            self.frozen,
            track="familiarity",
            variant="SAC-B4",
            capacity_profile=None,
            metrics=["missed_change_rate"],
        )
        self.assertEqual(validate_authorized_run(run, self.prereg, self.frozen), [])

    def test_routing_run_has_track_specific_variant(self) -> None:
        run = authorized_run(
            self.frozen,
            track="routing",
            variant="SEI-B7",
            capacity_profile=None,
            metrics=["regret_against_static_policy"],
        )
        self.assertEqual(validate_authorized_run(run, self.prereg, self.frozen), [])

    def test_familiarity_cannot_smuggle_capacity_policy(self) -> None:
        run = authorized_run(
            self.frozen,
            track="familiarity",
            variant="SAC-B4",
            capacity_profile="small",
            metrics=["missed_change_rate"],
        )
        self.assert_error(
            validate_authorized_run(run, self.prereg, self.frozen),
            "must not set capacity_profile",
        )

    def test_authorized_run_requires_exact_bundle_digest(self) -> None:
        run = authorized_run(self.frozen)
        run["freeze_bundle"]["digest"] = "0" * 64
        self.assert_error(
            validate_authorized_run(run, self.prereg, self.frozen),
            "digest does not match",
        )

    def test_authorized_run_requires_git_commit_sha(self) -> None:
        run = authorized_run(self.frozen)
        run["implementation"]["commit"] = "main"
        self.assert_error(
            validate_authorized_run(run, self.prereg, self.frozen),
            "40-char lowercase git SHA",
        )

    def test_authorized_run_requires_all_verification_flags(self) -> None:
        run = authorized_run(self.frozen)
        run["authorization"]["prior_boundary_verified"] = False
        self.assert_error(
            validate_authorized_run(run, self.prereg, self.frozen),
            "prior_boundary_verified=true",
        )

    def test_run_artifact_never_contains_results(self) -> None:
        run = authorized_run(self.frozen)
        run["results_generated"] = True
        self.assert_error(validate_authorized_run(run, self.prereg, self.frozen), "results_generated=false")

    def test_run_artifact_never_opens_b5_or_production_by_flags(self) -> None:
        for key in ("b5_gate_unchanged", "production_default_unchanged"):
            with self.subTest(key=key):
                run = authorized_run(self.frozen)
                run["authorization"][key] = False
                self.assert_error(
                    validate_authorized_run(run, self.prereg, self.frozen),
                    f"{key} must remain true",
                )

    def test_extra_top_level_field_is_rejected(self) -> None:
        run = copy.deepcopy(self.current_run)
        run["semantic_labels"] = []
        self.assert_error(validate_run_structure(run), "top-level keys mismatch")


if __name__ == "__main__":
    unittest.main()
