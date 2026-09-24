import copy
import importlib.util
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("burst_run_manifest", HERE / "burst_run_manifest.py")
brm = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(brm)

H = "a" * 64
G = "b" * 40


def valid_manifest():
    return {
        "schema": brm.SCHEMA,
        "purpose": "fine-tune",
        "source_git_sha": G,
        "inputs": {
            "dataset_sha256": H,
            "split_manifest_sha256": H,
            "preregistered_metrics_sha256": H,
        },
        "model": {"provider": "laya", "name": "laya-bounded-typed", "revision": "checkpoint-1"},
        "runtime": {
            "environment": "kaggle",
            "accelerator_observed": "2x NVIDIA T4",
            "dependency_lock_sha256": H,
            "python_version": "3.11.13",
            "seed": 7,
        },
        "execution": {
            "started_at": "2026-09-24T00:00:00Z",
            "ended_at": "2026-09-24T04:00:00Z",
            "elapsed_seconds": 14400,
            "cost_observed": False,
            "cost": None,
        },
        "outputs": [
            {"name": "checkpoint", "kind": "model", "sha256": H},
            {"name": "calibration", "kind": "temperature", "sha256": H},
        ],
        "evaluation": {
            "held_out_metrics": {"brier": 0.12, "ece": 0.03},
            "local_export_compatible": True,
            "promotion_decision": "local-validation",
        },
        "claims": {"semantic_truth": False, "production_authority": False},
    }


class BurstRunManifestTest(unittest.TestCase):
    def test_valid_manifest_passes(self):
        brm.validate_manifest(valid_manifest())

    def test_typesafe_identity_cannot_label_laya(self):
        m = valid_manifest()
        m["model"] = {"provider": "typesafe", "name": "laya-bounded-typed", "revision": "x"}
        with self.assertRaises(brm.BurstRunManifestError):
            brm.validate_manifest(m)

    def test_missing_preregistered_metrics_hash_is_rejected(self):
        m = valid_manifest()
        del m["inputs"]["preregistered_metrics_sha256"]
        with self.assertRaises(brm.BurstRunManifestError):
            brm.validate_manifest(m)

    def test_unobserved_cost_cannot_invent_amount(self):
        m = valid_manifest()
        m["execution"]["cost"] = {"unit": "USD", "amount": 9.99}
        with self.assertRaises(brm.BurstRunManifestError):
            brm.validate_manifest(m)

    def test_observed_cost_requires_amount_and_unit(self):
        m = valid_manifest()
        m["execution"]["cost_observed"] = True
        m["execution"]["cost"] = {"unit": "USD"}
        with self.assertRaises(brm.BurstRunManifestError):
            brm.validate_manifest(m)

    def test_duplicate_artifact_names_are_rejected(self):
        m = valid_manifest()
        m["outputs"].append(copy.deepcopy(m["outputs"][0]))
        with self.assertRaises(brm.BurstRunManifestError):
            brm.validate_manifest(m)

    def test_boolean_metric_is_rejected(self):
        m = valid_manifest()
        m["evaluation"]["held_out_metrics"]["brier"] = True
        with self.assertRaises(brm.BurstRunManifestError):
            brm.validate_manifest(m)

    def test_authority_claim_is_rejected(self):
        m = valid_manifest()
        m["claims"]["production_authority"] = True
        with self.assertRaises(brm.BurstRunManifestError):
            brm.validate_manifest(m)


if __name__ == "__main__":
    unittest.main()
