#!/usr/bin/env python3
"""Validate the cross-stage benchmark preregistration and explicit unlock gate."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PREREG_PATH = ROOT / "evaluation" / "sparse-associative-cognition" / "cross_stage_benchmark_preregistration.json"

EXPECTED_SCHEMA = "sei.sacs-cross-stage-benchmark-preregistration/v1alpha1"
REQUIRED_VARIANTS = {"B0", "B1", "B1-B2", "B1-B2-B3"}
REQUIRED_UNLOCKS = {
    "human_adjudication_state=frozen",
    "dataset_digest_is_frozen",
    "variant_set_is_frozen",
    "split_manifest_is_frozen",
    "b3_prior_manifest_is_frozen",
    "explicit_evaluation_run_artifact",
}
REQUIRED_DIAGNOSTICS = {"SAC-B6b", "SAC-B6c"}


def _string_set(values: object) -> set[str]:
    if not isinstance(values, list) or not all(isinstance(v, str) for v in values):
        return set()
    return set(values)


def _disjoint(left: object, right: object) -> bool:
    if not isinstance(left, list) or not isinstance(right, list):
        return False
    return set(left).isdisjoint(right)


def validate_preregistration(doc: dict) -> list[str]:
    errors: list[str] = []

    if doc.get("schema") != EXPECTED_SCHEMA:
        errors.append(f"schema must be {EXPECTED_SCHEMA}")
    if doc.get("status") != "preregistration-only":
        errors.append("status must remain preregistration-only")

    result_generation = doc.get("result_generation")
    if not isinstance(result_generation, dict):
        errors.append("result_generation must be an object")
    else:
        if result_generation.get("enabled") is not False:
            errors.append("preregistration result_generation.enabled must remain false")
        if result_generation.get("preregistration_artifact_must_never_enable_results") is not True:
            errors.append(
                "result_generation.preregistration_artifact_must_never_enable_results must remain true"
            )
        if not REQUIRED_UNLOCKS.issubset(_string_set(result_generation.get("unlock_requires"))):
            errors.append("result_generation.unlock_requires is missing required gates")

    adjudication = doc.get("adjudication")
    if not isinstance(adjudication, dict):
        errors.append("adjudication must be an object")
    else:
        if adjudication.get("required_final_state") != "frozen":
            errors.append("adjudication.required_final_state must remain frozen")
        if adjudication.get("semantic_labels_embedded_in_preregistration") is not False:
            errors.append("semantic labels must not be embedded in preregistration")
        if adjudication.get("state") not in {"pending", "frozen"}:
            errors.append("adjudication.state must be pending or frozen")

    freeze_kit = doc.get("freeze_kit")
    if not isinstance(freeze_kit, dict):
        errors.append("freeze_kit must be an object")
    else:
        if freeze_kit.get("state") not in {"draft", "frozen"}:
            errors.append("freeze_kit.state must be draft or frozen")
        required_refs = {
            "directory": "cross-stage-freeze",
            "dataset_manifest_ref": "cross-stage-freeze/dataset_manifest.json",
            "adjudication_manifest_ref": "cross-stage-freeze/adjudication_manifest.json",
            "split_manifest_ref": "cross-stage-freeze/split_manifest.json",
            "b3_prior_manifest_ref": "cross-stage-freeze/b3_prior_manifest.json",
            "freeze_bundle_ref": "cross-stage-freeze/freeze_bundle.json",
            "validator_ref": "cross-stage-freeze/freeze_manifests.py",
            "evidence_ref": "cross-stage-freeze/freeze_kit_evidence_2026-09-18.json",
        }
        for key, expected in required_refs.items():
            if freeze_kit.get(key) != expected:
                errors.append(f"freeze_kit.{key} must remain {expected}")
        frozen = freeze_kit.get("state") == "frozen"
        if freeze_kit.get("current_bundle_is_frozen") is not frozen:
            errors.append("freeze_kit.current_bundle_is_frozen must match freeze_kit.state")
        if freeze_kit.get("result_generation_enabled_after_freeze") is not False:
            errors.append("freeze kit must not enable result generation after freeze")
        if freeze_kit.get("b5_entry_gate_changed") is not False:
            errors.append("freeze kit must not change B5 entry gate")

    variants = doc.get("variants")
    if not isinstance(variants, list):
        errors.append("variants must be a list")
    else:
        ids = [item.get("id") for item in variants if isinstance(item, dict)]
        if len(ids) != len(variants) or len(ids) != len(set(ids)):
            errors.append("variant ids must be present and unique")
        if set(ids) != REQUIRED_VARIANTS:
            errors.append("variants must contain exactly B0, B1, B1-B2, and B1-B2-B3")
        b3 = next((item for item in variants if isinstance(item, dict) and item.get("id") == "B1-B2-B3"), None)
        if not b3 or b3.get("requires_prior_manifest") is not True:
            errors.append("B1-B2-B3 must require a prior manifest")

    capacity = doc.get("capacity_profiles")
    if not isinstance(capacity, dict):
        errors.append("capacity_profiles must be an object")
    else:
        if capacity.get("stage") != "SAC-B6":
            errors.append("capacity_profiles.stage must remain SAC-B6")
        if capacity.get("diagnostics_are_not_semantic_scores") is not True:
            errors.append("capacity diagnostics must not become semantic scores")
        if not REQUIRED_DIAGNOSTICS.issubset(_string_set(capacity.get("diagnostics_only"))):
            errors.append("capacity diagnostics must retain SAC-B6b and SAC-B6c")
        profiles = capacity.get("profiles")
        if not isinstance(profiles, list) or not profiles:
            errors.append("capacity_profiles.profiles must be a non-empty list")
        else:
            ids = [p.get("id") for p in profiles if isinstance(p, dict)]
            if set(ids) != {"small", "medium", "large"}:
                errors.append("capacity profiles must remain small, medium, and large")
            for profile in profiles:
                if not isinstance(profile, dict):
                    errors.append("capacity profile must be an object")
                    continue
                if not all(isinstance(profile.get(k), int) and profile[k] > 0 for k in ("dimensions", "active", "fanout")):
                    errors.append(f"capacity profile {profile.get('id')} must use positive integer dimensions/active/fanout")
                if isinstance(profile.get("dimensions"), int) and isinstance(profile.get("active"), int):
                    if profile["active"] > profile["dimensions"]:
                        errors.append(f"capacity profile {profile.get('id')} active must not exceed dimensions")

        stress = capacity.get("stress_track")
        if not isinstance(stress, dict):
            errors.append("capacity_profiles.stress_track must be an object")
        else:
            if set(stress.get("stages", [])) != {"SAC-B6d", "SAC-B6e"}:
                errors.append("capacity stress track must retain SAC-B6d and SAC-B6e")
            if stress.get("policy_set_state") != "frozen-for-preregistration":
                errors.append("capacity stress policy set must remain frozen-for-preregistration")
            if stress.get("may_not_define_production_default") is not True:
                errors.append("capacity stress track must not define production default")
            if stress.get("may_not_use_feature_cardinality_as_semantic_priority") is not True:
                errors.append("feature cardinality must not become semantic priority")
            profile = stress.get("profile")
            if not isinstance(profile, dict) or profile.get("id") != "oversized-stress":
                errors.append("capacity stress profile must remain oversized-stress")
            policies = stress.get("residual_policies")
            if not isinstance(policies, list):
                errors.append("capacity stress residual_policies must be a list")
            else:
                ids = {item.get("id") for item in policies if isinstance(item, dict)}
                if ids != {"proportional-baseline", "cap128", "cap64"}:
                    errors.append("capacity stress policies must remain proportional-baseline/cap128/cap64")

    prior = doc.get("b3_prior_manifest")
    if not isinstance(prior, dict):
        errors.append("b3_prior_manifest must be an object")
    else:
        if prior.get("provenance_required") is not True:
            errors.append("B3 prior provenance must remain required")
        if prior.get("evaluation_labels_may_not_author_prior") is not True:
            errors.append("evaluation labels must not author B3 prior")
        if prior.get("selectors") != "exact Channel + exact Key only":
            errors.append("B3 prior selectors must remain exact Channel + exact Key only")
        multiplier = prior.get("absolute_max_multiplier")
        if not isinstance(multiplier, (int, float)) or isinstance(multiplier, bool) or multiplier <= 0 or multiplier > 2:
            errors.append("B3 prior absolute_max_multiplier must remain in (0,2]")
        max_rules = prior.get("max_rules")
        if not isinstance(max_rules, int) or isinstance(max_rules, bool) or max_rules <= 0 or max_rules > 32:
            errors.append("B3 prior max_rules must remain in [1,32]")

    tracks = doc.get("tracks")
    if not isinstance(tracks, dict):
        errors.append("tracks must be an object")
    else:
        retrieval = tracks.get("retrieval")
        familiarity = tracks.get("familiarity")
        routing = tracks.get("routing")
        if not isinstance(retrieval, dict) or not isinstance(familiarity, dict) or not isinstance(routing, dict):
            errors.append("retrieval, familiarity, and routing tracks are required")
        else:
            rs = retrieval.get("split_manifest", {})
            if not _disjoint(rs.get("calibration_ids"), rs.get("evaluation_ids")):
                errors.append("retrieval calibration/evaluation ids must be disjoint")

            fs = familiarity.get("split_manifest", {})
            if not _disjoint(fs.get("calibration_ids"), fs.get("evaluation_ids")):
                errors.append("familiarity calibration/evaluation ids must be disjoint")
            if familiarity.get("caller_owned_fingerprint_required") is not True:
                errors.append("B4 caller-owned fingerprint must remain required")
            if familiarity.get("fingerprint_may_not_use_evaluation_labels") is not True:
                errors.append("B4 fingerprint must not use evaluation labels")

            rsplit = routing.get("split_manifest", {})
            if not _disjoint(rsplit.get("training_outcome_ids"), rsplit.get("holdout_replay_ids")):
                errors.append("B7 training/holdout ids must be disjoint")
            if routing.get("training_holdout_must_be_disjoint") is not True:
                errors.append("B7 training_holdout_must_be_disjoint must remain true")
            if routing.get("holdout_replay_must_be_counterfactually_complete") is not True:
                errors.append("B7 holdout replay must remain counterfactually complete")

    policy = doc.get("evaluation_policy")
    required_true = (
        "no_single_composite_score",
        "no_variant_tuning_on_evaluation_labels",
        "no_b3_prior_authoring_from_evaluation_labels",
        "no_b4_fingerprint_authoring_from_evaluation_labels",
        "no_b7_training_holdout_overlap",
    )
    required_false = ("b5_entry_gate_changed", "provider_default_changed", "production_runtime_changed")
    if not isinstance(policy, dict):
        errors.append("evaluation_policy must be an object")
    else:
        for key in required_true:
            if policy.get(key) is not True:
                errors.append(f"evaluation_policy.{key} must remain true")
        for key in required_false:
            if policy.get(key) is not False:
                errors.append(f"evaluation_policy.{key} must remain false")

    b5 = doc.get("b5_gate")
    if not isinstance(b5, dict):
        errors.append("b5_gate must be an object")
    else:
        if b5.get("state") != "closed":
            errors.append("B5 gate must remain closed in preregistration")
        if b5.get("current_evidence_satisfies_entry_condition") is not False:
            errors.append("current evidence must not satisfy B5 entry condition")

    stop_lines = doc.get("stop_lines")
    if not isinstance(stop_lines, list) or not all(isinstance(v, str) for v in stop_lines):
        errors.append("stop_lines must be a string list")
    else:
        joined = "\n".join(stop_lines)
        for fragment in ("single composite score", "B5 gate", "semantic truth"):
            if fragment not in joined:
                errors.append(f"stop line missing for {fragment}")

    return errors


def validate_unlock(doc: dict) -> list[str]:
    errors = validate_preregistration(doc)
    if errors:
        return errors

    freeze_kit = doc["freeze_kit"]
    if freeze_kit.get("state") != "frozen" or freeze_kit.get("current_bundle_is_frozen") is not True:
        errors.append("unlock requires frozen freeze-kit bundle")

    adjudication = doc["adjudication"]
    if adjudication.get("state") != "frozen":
        errors.append("unlock requires human adjudication state=frozen")
    if not adjudication.get("dataset_digest"):
        errors.append("unlock requires frozen dataset digest")
    if not adjudication.get("adjudication_manifest_ref"):
        errors.append("unlock requires adjudication manifest ref")

    prior = doc["b3_prior_manifest"]
    if prior.get("state") != "frozen":
        errors.append("unlock requires frozen B3 prior manifest")
    if not prior.get("manifest_ref"):
        errors.append("unlock requires B3 prior manifest ref")

    for track_name in ("retrieval", "familiarity"):
        split = doc["tracks"][track_name]["split_manifest"]
        if split.get("state") != "frozen":
            errors.append(f"unlock requires frozen {track_name} split manifest")
        if not split.get("calibration_ids") or not split.get("evaluation_ids"):
            errors.append(f"unlock requires non-empty {track_name} calibration/evaluation ids")

    routing = doc["tracks"]["routing"]["split_manifest"]
    if routing.get("state") != "frozen":
        errors.append("unlock requires frozen routing split manifest")
    if not routing.get("training_outcome_ids") or not routing.get("holdout_replay_ids"):
        errors.append("unlock requires non-empty B7 training/holdout ids")

    return errors


def main() -> int:
    try:
        doc = json.loads(PREREG_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"cross-stage preregistration validation failed: {exc}", file=sys.stderr)
        return 1

    errors = validate_preregistration(doc)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    unlock_errors = validate_unlock(doc)
    if not unlock_errors:
        print("ERROR: preregistration unexpectedly satisfies unlock gate", file=sys.stderr)
        return 1

    print("Cross-stage preregistration validated; evaluation remains locked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
