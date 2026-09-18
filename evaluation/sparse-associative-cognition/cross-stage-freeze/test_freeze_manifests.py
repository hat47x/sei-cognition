from __future__ import annotations

import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from freeze_manifests import (  # noqa: E402
    FILES,
    canonical_digest,
    freeze_documents,
    load_directory,
    validate_all,
    write_directory,
)


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def synthetic_draft() -> dict[str, dict]:
    ids = [
        "retrieval-cal",
        "retrieval-eval",
        "familiarity-cal",
        "familiarity-eval",
        "routing-train",
        "routing-holdout",
    ]
    dataset = {
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
    }
    adjudication = {
        "schema": "sei.sacs-cross-stage-adjudication-manifest/v1alpha1",
        "state": "draft",
        "frozen_at": None,
        "dataset_digest": "",
        "adjudication_policy_version": "v1alpha1",
        "reviewer_refs": ["reviewer:r1", "reviewer:r2"],
        "judgments": [
            {
                "id": f"judgment:{item_id}",
                "item_id": item_id,
                "reviewer_ref": "reviewer:r1",
                "kind": "fixture-label",
                "value": "accepted",
            }
            for item_id in ids
        ],
        "unresolved": [],
        "manifest_digest": "",
    }
    split = {
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
    }
    prior = {
        "schema": "sei.sacs-cross-stage-b3-prior-manifest/v1alpha1",
        "state": "draft",
        "frozen_at": None,
        "dataset_digest": "",
        "adjudication_manifest_digest": "",
        "evaluation_labels_used_for_authoring": False,
        "rules": [
            {
                "channel": "graph:relationType",
                "key": "causal",
                "multiplier": 1.01,
                "provenance_ref": "policy:pre-evaluation-domain-prior",
                "authoring_source": "domain-policy-before-evaluation",
            }
        ],
        "manifest_digest": "",
    }
    bundle = {
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
    }
    return {
        "dataset": dataset,
        "adjudication": adjudication,
        "split": split,
        "prior": prior,
        "bundle": bundle,
    }


class CrossStageFreezeManifestTests(unittest.TestCase):
    def test_repository_draft_templates_are_valid_and_locked(self) -> None:
        docs = load_directory(HERE)
        self.assertEqual(validate_all(docs), [])
        with self.assertRaisesRegex(ValueError, "empty dataset"):
            freeze_documents(docs, "2026-09-18T00:00:00Z")

    def test_synthetic_complete_draft_can_freeze(self) -> None:
        docs = synthetic_draft()
        self.assertEqual(validate_all(docs), [])
        frozen = freeze_documents(docs, "2026-09-18T00:00:00Z")
        self.assertEqual(validate_all(frozen), [])
        self.assertEqual(frozen["bundle"]["state"], "frozen")
        self.assertFalse(frozen["bundle"]["result_generation_enabled"])
        self.assertFalse(frozen["bundle"]["b5_entry_gate_changed"])

    def test_freeze_is_deterministic_for_same_content_and_timestamp(self) -> None:
        left = freeze_documents(synthetic_draft(), "2026-09-18T00:00:00Z")
        right = freeze_documents(synthetic_draft(), "2026-09-18T00:00:00Z")
        self.assertEqual(left, right)
        self.assertEqual(
            left["bundle"]["bundle_digest"],
            right["bundle"]["bundle_digest"],
        )

    def test_freeze_rejects_mixed_draft_and_frozen_input(self) -> None:
        docs = synthetic_draft()
        docs["dataset"]["state"] = "frozen"
        docs["dataset"]["frozen_at"] = "2026-09-18T00:00:00Z"
        docs["dataset"]["dataset_digest"] = canonical_digest(
            docs["dataset"], "dataset_digest"
        )
        with self.assertRaisesRegex(ValueError, "only draft manifests"):
            freeze_documents(docs, "2026-09-18T00:00:00Z")

    def test_freeze_rejects_stale_digest_in_draft(self) -> None:
        docs = synthetic_draft()
        docs["dataset"]["dataset_digest"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "must be empty while draft"):
            freeze_documents(docs, "2026-09-18T00:00:00Z")

    def test_freeze_rejects_non_utc_second_timestamp(self) -> None:
        for value in (
            "2026-09-18",
            "2026-09-18T00:00:00+09:00",
            "2026-09-18T00:00:00.123Z",
            "not-a-timestamp",
        ):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "UTC second format"):
                    freeze_documents(synthetic_draft(), value)

    def test_dataset_digest_detects_post_freeze_mutation(self) -> None:
        frozen = freeze_documents(synthetic_draft(), "2026-09-18T00:00:00Z")
        frozen["dataset"]["items"][0]["source_ref"] = "fixture:mutated"
        errors = validate_all(frozen)
        self.assertTrue(any("dataset.dataset_digest does not match" in e for e in errors), errors)

    def test_adjudication_digest_detects_post_freeze_mutation(self) -> None:
        frozen = freeze_documents(synthetic_draft(), "2026-09-18T00:00:00Z")
        frozen["adjudication"]["judgments"][0]["value"] = "mutated"
        errors = validate_all(frozen)
        self.assertTrue(any("adjudication.manifest_digest does not match" in e for e in errors), errors)

    def test_split_overlap_is_rejected(self) -> None:
        docs = synthetic_draft()
        docs["split"]["retrieval"]["evaluation_ids"] = ["retrieval-cal"]
        errors = validate_all(docs)
        self.assertTrue(any("retrieval partitions overlap" in e for e in errors), errors)

    def test_split_unknown_id_is_rejected(self) -> None:
        docs = synthetic_draft()
        docs["split"]["retrieval"]["evaluation_ids"] = ["unknown"]
        errors = validate_all(docs)
        self.assertTrue(any("unknown dataset ids" in e for e in errors), errors)

    def test_evaluation_label_derived_prior_is_rejected(self) -> None:
        docs = synthetic_draft()
        docs["prior"]["rules"][0]["authoring_source"] = "evaluation-label-derived"
        errors = validate_all(docs)
        self.assertTrue(any("evaluation-label-derived is forbidden" in e for e in errors), errors)

    def test_nonfinite_or_out_of_range_prior_is_rejected(self) -> None:
        for value in (float("nan"), float("inf"), 0, -1, 2.01):
            with self.subTest(value=value):
                docs = synthetic_draft()
                docs["prior"]["rules"][0]["multiplier"] = value
                errors = validate_all(docs)
                self.assertTrue(any("multiplier must be finite" in e for e in errors), errors)

    def test_nonopaque_reviewer_ref_is_rejected(self) -> None:
        docs = synthetic_draft()
        docs["adjudication"]["reviewer_refs"] = ["Alice Example"]
        docs["adjudication"]["judgments"][0]["reviewer_ref"] = "Alice Example"
        errors = validate_all(docs)
        self.assertTrue(any("opaque reviewer:*" in e for e in errors), errors)

    def test_unresolved_item_can_be_preserved_instead_of_forced_to_consensus(self) -> None:
        docs = synthetic_draft()
        item_id = "retrieval-eval"
        docs["adjudication"]["judgments"] = [
            j for j in docs["adjudication"]["judgments"] if j["item_id"] != item_id
        ]
        docs["adjudication"]["unresolved"] = [
            {"item_id": item_id, "reason": "reviewers-disagree"}
        ]
        frozen = freeze_documents(docs, "2026-09-18T00:00:00Z")
        self.assertEqual(validate_all(frozen), [])
        self.assertEqual(
            frozen["adjudication"]["unresolved"],
            [{"item_id": item_id, "reason": "reviewers-disagree"}],
        )

    def test_frozen_adjudication_requires_full_item_coverage(self) -> None:
        docs = synthetic_draft()
        docs["adjudication"]["judgments"] = docs["adjudication"]["judgments"][:-1]
        with self.assertRaisesRegex(ValueError, "coverage mismatch"):
            freeze_documents(docs, "2026-09-18T00:00:00Z")

    def test_bundle_binding_detects_component_replacement(self) -> None:
        frozen = freeze_documents(synthetic_draft(), "2026-09-18T00:00:00Z")
        frozen["bundle"]["dataset_manifest"]["digest"] = "0" * 64
        frozen["bundle"]["bundle_digest"] = canonical_digest(
            frozen["bundle"], "bundle_digest"
        )
        errors = validate_all(frozen)
        self.assertTrue(any("dataset_manifest.digest binding mismatch" in e for e in errors), errors)

    def test_bundle_cannot_enable_results_or_open_b5(self) -> None:
        for key in ("result_generation_enabled", "b5_entry_gate_changed"):
            with self.subTest(key=key):
                docs = synthetic_draft()
                docs["bundle"][key] = True
                errors = validate_all(docs)
                self.assertTrue(errors)

    def test_freeze_output_is_written_to_new_directory(self) -> None:
        frozen = freeze_documents(synthetic_draft(), "2026-09-18T00:00:00Z")
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / "frozen"
            write_directory(out, frozen)
            loaded = load_directory(out)
            self.assertEqual(validate_all(loaded), [])
            self.assertEqual(
                set(path.name for path in out.iterdir()),
                set(FILES.values()),
            )


if __name__ == "__main__":
    unittest.main()
