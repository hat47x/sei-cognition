#!/usr/bin/env python3
"""Validate and freeze cross-stage benchmark manifests without generating results."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

DIR = Path(__file__).resolve().parent
FILES = {
    "dataset": "dataset_manifest.json",
    "adjudication": "adjudication_manifest.json",
    "split": "split_manifest.json",
    "prior": "b3_prior_manifest.json",
    "bundle": "freeze_bundle.json",
}
SCHEMAS = {
    "dataset": "sei.sacs-cross-stage-dataset-manifest/v1alpha1",
    "adjudication": "sei.sacs-cross-stage-adjudication-manifest/v1alpha1",
    "split": "sei.sacs-cross-stage-split-manifest/v1alpha1",
    "prior": "sei.sacs-cross-stage-b3-prior-manifest/v1alpha1",
    "bundle": "sei.sacs-cross-stage-freeze-bundle/v1alpha1",
}
DIGEST_FIELDS = {
    "dataset": "dataset_digest",
    "adjudication": "manifest_digest",
    "split": "manifest_digest",
    "prior": "manifest_digest",
    "bundle": "bundle_digest",
}
HEX64 = re.compile(r"^[0-9a-f]{64}$")
UTC_SECOND = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
REVIEWER_REF = re.compile(r"^reviewer:[A-Za-z0-9._:-]+$")


def canonical_bytes(document: dict[str, Any], digest_field: str) -> bytes:
    payload = copy.deepcopy(document)
    payload.pop(digest_field, None)
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def canonical_digest(document: dict[str, Any], digest_field: str) -> str:
    return hashlib.sha256(canonical_bytes(document, digest_field)).hexdigest()


def _is_digest(value: object) -> bool:
    return isinstance(value, str) and HEX64.fullmatch(value) is not None


def _canonical_string(value: object) -> bool:
    return isinstance(value, str) and value != "" and value == value.strip()


def _validate_state(document: dict[str, Any], name: str, errors: list[str]) -> None:
    state = document.get("state")
    if state not in {"draft", "frozen"}:
        errors.append(f"{name}.state must be draft or frozen")
        return
    frozen_at = document.get("frozen_at")
    digest_field = DIGEST_FIELDS[name]
    digest = document.get(digest_field)
    if state == "draft":
        if frozen_at is not None:
            errors.append(f"{name}.frozen_at must be null while draft")
        if digest != "":
            errors.append(f"{name}.{digest_field} must be empty while draft")
    else:
        if not isinstance(frozen_at, str) or UTC_SECOND.fullmatch(frozen_at) is None:
            errors.append(
                f"{name}.frozen_at must use explicit UTC second format YYYY-MM-DDTHH:MM:SSZ"
            )
        if not _is_digest(digest):
            errors.append(f"{name}.{digest_field} must be a sha256 hex digest when frozen")
        elif digest != canonical_digest(document, digest_field):
            errors.append(f"{name}.{digest_field} does not match canonical content")


def validate_dataset(document: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if document.get("schema") != SCHEMAS["dataset"]:
        errors.append(f"dataset.schema must be {SCHEMAS['dataset']}")
    _validate_state(document, "dataset", errors)

    items = document.get("items")
    if not isinstance(items, list):
        errors.append("dataset.items must be a list")
        return errors

    seen: set[str] = set()
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            errors.append(f"dataset.items[{index}] must be an object")
            continue
        item_id = item.get("id")
        if not _canonical_string(item_id):
            errors.append(f"dataset.items[{index}].id must be canonical and non-empty")
        elif item_id in seen:
            errors.append(f"dataset item id must be unique: {item_id}")
        else:
            seen.add(item_id)
        if not _canonical_string(item.get("source_ref")):
            errors.append(f"dataset.items[{index}].source_ref must be canonical and non-empty")
        if not _is_digest(item.get("content_digest")):
            errors.append(f"dataset.items[{index}].content_digest must be sha256 hex")

    if document.get("state") == "frozen" and not items:
        errors.append("frozen dataset must contain at least one item")
    return errors


def validate_adjudication(
    document: dict[str, Any],
    dataset: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    if document.get("schema") != SCHEMAS["adjudication"]:
        errors.append(f"adjudication.schema must be {SCHEMAS['adjudication']}")
    _validate_state(document, "adjudication", errors)

    if not _canonical_string(document.get("adjudication_policy_version")):
        errors.append("adjudication.adjudication_policy_version must be canonical and non-empty")

    reviewer_refs = document.get("reviewer_refs")
    if not isinstance(reviewer_refs, list):
        errors.append("adjudication.reviewer_refs must be a list")
        reviewer_refs = []
    else:
        if len(set(reviewer_refs)) != len(reviewer_refs):
            errors.append("adjudication reviewer refs must be unique")
        for ref in reviewer_refs:
            if not isinstance(ref, str) or REVIEWER_REF.fullmatch(ref) is None:
                errors.append("adjudication reviewer refs must be opaque reviewer:* identifiers")

    dataset_ids = {
        item.get("id")
        for item in dataset.get("items", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }

    judgments = document.get("judgments")
    if not isinstance(judgments, list):
        errors.append("adjudication.judgments must be a list")
        judgments = []
    seen_judgment_ids: set[str] = set()
    covered: set[str] = set()
    for index, judgment in enumerate(judgments):
        if not isinstance(judgment, dict):
            errors.append(f"adjudication.judgments[{index}] must be an object")
            continue
        jid = judgment.get("id")
        if not _canonical_string(jid):
            errors.append(f"adjudication.judgments[{index}].id must be canonical and non-empty")
        elif jid in seen_judgment_ids:
            errors.append(f"adjudication judgment id must be unique: {jid}")
        else:
            seen_judgment_ids.add(jid)
        item_id = judgment.get("item_id")
        if item_id not in dataset_ids:
            errors.append(f"adjudication judgment references unknown dataset item: {item_id}")
        else:
            covered.add(item_id)
        if judgment.get("reviewer_ref") not in reviewer_refs:
            errors.append(f"adjudication judgment references unknown reviewer: {judgment.get('reviewer_ref')}")
        if not _canonical_string(judgment.get("kind")):
            errors.append(f"adjudication.judgments[{index}].kind must be canonical and non-empty")
        if "value" not in judgment:
            errors.append(f"adjudication.judgments[{index}].value must be present")

    unresolved = document.get("unresolved")
    if not isinstance(unresolved, list):
        errors.append("adjudication.unresolved must be a list")
        unresolved = []
    seen_unresolved: set[str] = set()
    for index, entry in enumerate(unresolved):
        if not isinstance(entry, dict):
            errors.append(f"adjudication.unresolved[{index}] must be an object")
            continue
        item_id = entry.get("item_id")
        if item_id not in dataset_ids:
            errors.append(f"adjudication unresolved references unknown dataset item: {item_id}")
        elif item_id in seen_unresolved:
            errors.append(f"adjudication unresolved item must be unique: {item_id}")
        else:
            seen_unresolved.add(item_id)
            covered.add(item_id)
        if not _canonical_string(entry.get("reason")):
            errors.append(f"adjudication.unresolved[{index}].reason must be canonical and non-empty")

    if document.get("state") == "frozen":
        if document.get("dataset_digest") != dataset.get("dataset_digest"):
            errors.append("frozen adjudication dataset digest binding mismatch")
        if not reviewer_refs:
            errors.append("frozen adjudication requires at least one reviewer ref")
        if not judgments and not unresolved:
            errors.append("frozen adjudication requires judgments or unresolved entries")
        if covered != dataset_ids:
            missing = sorted(dataset_ids - covered)
            extra = sorted(covered - dataset_ids)
            errors.append(f"frozen adjudication coverage mismatch: missing={missing}, extra={extra}")
    return errors


def validate_split(document: dict[str, Any], dataset: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if document.get("schema") != SCHEMAS["split"]:
        errors.append(f"split.schema must be {SCHEMAS['split']}")
    _validate_state(document, "split", errors)

    dataset_ids = {
        item.get("id")
        for item in dataset.get("items", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    pairs = (
        ("retrieval", "calibration_ids", "evaluation_ids"),
        ("familiarity", "calibration_ids", "evaluation_ids"),
        ("routing", "training_outcome_ids", "holdout_replay_ids"),
    )
    all_selected: set[str] = set()
    for track, left_key, right_key in pairs:
        section = document.get(track)
        if not isinstance(section, dict):
            errors.append(f"split.{track} must be an object")
            continue
        left = section.get(left_key)
        right = section.get(right_key)
        if not isinstance(left, list) or not all(isinstance(v, str) for v in left):
            errors.append(f"split.{track}.{left_key} must be a string list")
            left = []
        if not isinstance(right, list) or not all(isinstance(v, str) for v in right):
            errors.append(f"split.{track}.{right_key} must be a string list")
            right = []
        if len(set(left)) != len(left) or len(set(right)) != len(right):
            errors.append(f"split.{track} ids must be unique within each partition")
        overlap = set(left) & set(right)
        if overlap:
            errors.append(f"split.{track} partitions overlap: {sorted(overlap)}")
        unknown = (set(left) | set(right)) - dataset_ids
        if unknown:
            errors.append(f"split.{track} references unknown dataset ids: {sorted(unknown)}")
        all_selected |= set(left) | set(right)

    if document.get("state") == "frozen":
        if document.get("dataset_digest") != dataset.get("dataset_digest"):
            errors.append("frozen split dataset digest binding mismatch")
        for track, left_key, right_key in pairs:
            section = document.get(track, {})
            if not section.get(left_key) or not section.get(right_key):
                errors.append(f"frozen split requires non-empty {track} partitions")
        if all_selected != dataset_ids:
            errors.append(
                "frozen split must assign every dataset item to at least one registered track partition"
            )
    return errors


def validate_prior(
    document: dict[str, Any],
    dataset: dict[str, Any],
    adjudication: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    if document.get("schema") != SCHEMAS["prior"]:
        errors.append(f"prior.schema must be {SCHEMAS['prior']}")
    _validate_state(document, "prior", errors)

    if document.get("evaluation_labels_used_for_authoring") is not False:
        errors.append("B3 prior must declare evaluation_labels_used_for_authoring=false")

    rules = document.get("rules")
    if not isinstance(rules, list):
        errors.append("prior.rules must be a list")
        rules = []
    if len(rules) > 32:
        errors.append("prior.rules must not exceed 32")
    seen: set[tuple[str, str]] = set()
    for index, rule in enumerate(rules):
        if not isinstance(rule, dict):
            errors.append(f"prior.rules[{index}] must be an object")
            continue
        channel = rule.get("channel")
        key = rule.get("key")
        if not _canonical_string(channel):
            errors.append(f"prior.rules[{index}].channel must be canonical and non-empty")
        if not _canonical_string(key):
            errors.append(f"prior.rules[{index}].key must be canonical and non-empty")
        pair = (channel, key)
        if pair in seen:
            errors.append(f"prior selector must be unique: {pair}")
        seen.add(pair)
        multiplier = rule.get("multiplier")
        if (
            not isinstance(multiplier, (int, float))
            or isinstance(multiplier, bool)
            or not math.isfinite(multiplier)
            or multiplier <= 0
            or multiplier > 2
        ):
            errors.append(f"prior.rules[{index}].multiplier must be finite and in (0,2]")
        if not _canonical_string(rule.get("provenance_ref")):
            errors.append(f"prior.rules[{index}].provenance_ref must be canonical and non-empty")
        source = rule.get("authoring_source")
        if source == "evaluation-label-derived":
            errors.append("prior authoring_source evaluation-label-derived is forbidden")
        if not _canonical_string(source):
            errors.append(f"prior.rules[{index}].authoring_source must be canonical and non-empty")

    if document.get("state") == "frozen":
        if document.get("dataset_digest") != dataset.get("dataset_digest"):
            errors.append("frozen prior dataset digest binding mismatch")
        if document.get("adjudication_manifest_digest") != adjudication.get("manifest_digest"):
            errors.append("frozen prior adjudication digest binding mismatch")
    return errors


def validate_bundle(
    document: dict[str, Any],
    dataset: dict[str, Any],
    adjudication: dict[str, Any],
    split: dict[str, Any],
    prior: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    if document.get("schema") != SCHEMAS["bundle"]:
        errors.append(f"bundle.schema must be {SCHEMAS['bundle']}")
    _validate_state(document, "bundle", errors)
    if document.get("result_generation_enabled") is not False:
        errors.append("freeze bundle must never enable result generation")
    if document.get("b5_entry_gate_changed") is not False:
        errors.append("freeze bundle must not change B5 entry gate")

    bindings = (
        ("dataset_manifest", FILES["dataset"], dataset.get("dataset_digest")),
        ("adjudication_manifest", FILES["adjudication"], adjudication.get("manifest_digest")),
        ("split_manifest", FILES["split"], split.get("manifest_digest")),
        ("b3_prior_manifest", FILES["prior"], prior.get("manifest_digest")),
    )
    for key, expected_ref, expected_digest in bindings:
        binding = document.get(key)
        if not isinstance(binding, dict):
            errors.append(f"bundle.{key} must be an object")
            continue
        if binding.get("ref") != expected_ref:
            errors.append(f"bundle.{key}.ref must be {expected_ref}")
        if document.get("state") == "frozen" and binding.get("digest") != expected_digest:
            errors.append(f"bundle.{key}.digest binding mismatch")

    if document.get("state") == "frozen":
        states = {
            "dataset": dataset.get("state"),
            "adjudication": adjudication.get("state"),
            "split": split.get("state"),
            "prior": prior.get("state"),
        }
        not_frozen = sorted(name for name, state in states.items() if state != "frozen")
        if not_frozen:
            errors.append(f"frozen bundle requires frozen component manifests: {not_frozen}")
    return errors


def validate_all(documents: dict[str, dict[str, Any]]) -> list[str]:
    dataset = documents["dataset"]
    adjudication = documents["adjudication"]
    split = documents["split"]
    prior = documents["prior"]
    bundle = documents["bundle"]
    errors: list[str] = []
    errors.extend(validate_dataset(dataset))
    errors.extend(validate_adjudication(adjudication, dataset))
    errors.extend(validate_split(split, dataset))
    errors.extend(validate_prior(prior, dataset, adjudication))
    errors.extend(validate_bundle(bundle, dataset, adjudication, split, prior))
    return errors


def load_directory(directory: Path) -> dict[str, dict[str, Any]]:
    documents: dict[str, dict[str, Any]] = {}
    for name, filename in FILES.items():
        documents[name] = json.loads((directory / filename).read_text(encoding="utf-8"))
    return documents


def freeze_documents(
    documents: dict[str, dict[str, Any]],
    frozen_at: str,
) -> dict[str, dict[str, Any]]:
    if not isinstance(frozen_at, str) or UTC_SECOND.fullmatch(frozen_at) is None:
        raise ValueError(
            "frozen_at must use explicit UTC second format YYYY-MM-DDTHH:MM:SSZ"
        )

    draft_errors = validate_all(documents)
    if draft_errors:
        raise ValueError("input manifests are invalid: " + "; ".join(draft_errors))
    non_draft = sorted(
        name for name, document in documents.items()
        if document.get("state") != "draft"
    )
    if non_draft:
        raise ValueError(
            "freeze input must contain only draft manifests: " + ", ".join(non_draft)
        )

    frozen = copy.deepcopy(documents)

    dataset = frozen["dataset"]
    if not dataset.get("items"):
        raise ValueError("cannot freeze an empty dataset")
    dataset["state"] = "frozen"
    dataset["frozen_at"] = frozen_at
    dataset["dataset_digest"] = canonical_digest(dataset, "dataset_digest")

    adjudication = frozen["adjudication"]
    adjudication["state"] = "frozen"
    adjudication["frozen_at"] = frozen_at
    adjudication["dataset_digest"] = dataset["dataset_digest"]
    adjudication["manifest_digest"] = canonical_digest(adjudication, "manifest_digest")

    split = frozen["split"]
    split["state"] = "frozen"
    split["frozen_at"] = frozen_at
    split["dataset_digest"] = dataset["dataset_digest"]
    split["manifest_digest"] = canonical_digest(split, "manifest_digest")

    prior = frozen["prior"]
    prior["state"] = "frozen"
    prior["frozen_at"] = frozen_at
    prior["dataset_digest"] = dataset["dataset_digest"]
    prior["adjudication_manifest_digest"] = adjudication["manifest_digest"]
    prior["manifest_digest"] = canonical_digest(prior, "manifest_digest")

    bundle = frozen["bundle"]
    bundle["state"] = "frozen"
    bundle["frozen_at"] = frozen_at
    bundle["dataset_manifest"]["digest"] = dataset["dataset_digest"]
    bundle["adjudication_manifest"]["digest"] = adjudication["manifest_digest"]
    bundle["split_manifest"]["digest"] = split["manifest_digest"]
    bundle["b3_prior_manifest"]["digest"] = prior["manifest_digest"]
    bundle["bundle_digest"] = canonical_digest(bundle, "bundle_digest")

    errors = validate_all(frozen)
    if errors:
        raise ValueError("frozen manifests are invalid: " + "; ".join(errors))
    return frozen


def write_directory(directory: Path, documents: dict[str, dict[str, Any]]) -> None:
    directory.mkdir(parents=True, exist_ok=False)
    for name, filename in FILES.items():
        (directory / filename).write_text(
            json.dumps(documents[name], ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, default=DIR)
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--freeze-output-dir", type=Path)
    parser.add_argument("--frozen-at")
    args = parser.parse_args()

    try:
        documents = load_directory(args.input_dir)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"freeze manifest load failed: {exc}", file=sys.stderr)
        return 1

    errors = validate_all(documents)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    if args.freeze_output_dir is None:
        print("Cross-stage freeze manifests validated; current bundle remains draft/locked")
        return 0

    if not args.frozen_at:
        print("ERROR: --frozen-at is required when freezing", file=sys.stderr)
        return 1

    try:
        frozen = freeze_documents(documents, args.frozen_at)
        write_directory(args.freeze_output_dir, frozen)
    except (OSError, ValueError) as exc:
        print(f"freeze failed: {exc}", file=sys.stderr)
        return 1

    print(f"Frozen manifest bundle written to {args.freeze_output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
