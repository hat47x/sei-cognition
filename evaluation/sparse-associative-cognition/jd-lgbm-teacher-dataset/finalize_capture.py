#!/usr/bin/env python3
"""Finalize a JD-LGBM-0 authenticated capture without training a student.

This command is network-free. It consumes already-normalized teacher Evidence,
builds the student-ready dataset in a temporary directory, verifies the complete
retained evidence chain, and only then publishes a final verification receipt.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


td = _load_module("teacher_dataset", HERE / "teacher_dataset.py")
sd = _load_module("student_dataset", HERE / "student_dataset.py")
eg = _load_module("evidence_gate", HERE / "evidence_gate.py")

RECEIPT_SCHEMA = "sei.jd-lgbm0-post-capture-receipt/v1alpha1"


class FinalizeError(ValueError):
    pass


def _validate_git_sha(value: str) -> str:
    value = value.strip().lower()
    if len(value) != 40 or any(ch not in "0123456789abcdef" for ch in value):
        raise FinalizeError("expected source Git SHA must be a 40-character SHA-1 hex string")
    return value


def _prepare_output_parent(output_dir: Path) -> None:
    if output_dir.exists():
        raise FinalizeError(f"refusing to overwrite existing finalization output: {output_dir}")
    output_dir.parent.mkdir(parents=True, exist_ok=True)


def finalize_capture(
    manifest_path: Path,
    capture_manifest_path: Path,
    raw_dir: Path,
    raw_response_manifest_path: Path,
    teacher_rows_path: Path,
    output_dir: Path,
    *,
    expected_source_git_sha: str,
) -> dict[str, Any]:
    expected_source_git_sha = _validate_git_sha(expected_source_git_sha)
    _prepare_output_parent(output_dir)

    manifest = td.load_manifest(manifest_path)
    capture = td.load_capture_bundle(manifest_path, manifest, capture_manifest_path)
    if capture.get("source_git_sha") != expected_source_git_sha:
        raise FinalizeError(
            "capture bundle source_git_sha does not match the explicitly expected checkout SHA"
        )

    with tempfile.TemporaryDirectory(prefix=".jd-lgbm0-finalize-", dir=output_dir.parent) as tmp:
        work = Path(tmp)
        student_dir = work / "student-ready"
        student_summary = sd.write_student_dataset(
            manifest_path,
            teacher_rows_path,
            student_dir,
            force=False,
        )

        verification = eg.verify_evidence_chain(
            manifest_path,
            capture_manifest_path,
            raw_dir,
            raw_response_manifest_path,
            teacher_rows_path,
            student_dir / "student_records.jsonl",
            student_dir / "dataset_manifest.json",
        )

        verification_path = work / "evidence_chain_verification.json"
        verification_path.write_text(
            json.dumps(verification, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        receipt = {
            "schema": RECEIPT_SCHEMA,
            "status": "PASS",
            "source_git_sha": expected_source_git_sha,
            "capture_mode": verification["capture_mode"],
            "case_count": verification["case_count"],
            "teacher_model_version": verification["teacher_model_version"],
            "hashes": {
                **verification["hashes"],
                "verification_sha256": eg.sha256_file(verification_path),
            },
            "student_dataset": {
                "record_count": student_summary["record_count"],
                "split_counts": student_summary["split_counts"],
                "teacher_model_version": student_summary["teacher_model_version"],
                "lightgbm_training_performed": student_summary["lightgbm_training_performed"],
            },
            "network_requests_sent": 0,
            "lightgbm_training_performed": False,
            "boundaries": [
                "post-capture finalization PASS != authenticated-origin attestation by this command",
                "post-capture finalization PASS != teacher correctness or ground truth",
                "post-capture finalization PASS != model quality or Product Value",
                "post-capture finalization PASS != permission to activate a student",
            ],
        }
        receipt_path = work / "capture_verification_receipt.json"
        receipt_path.write_text(
            json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        os.replace(work, output_dir)

    return receipt


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("capture_manifest", type=Path)
    parser.add_argument("raw_dir", type=Path)
    parser.add_argument("raw_response_manifest", type=Path)
    parser.add_argument("teacher_rows", type=Path)
    parser.add_argument("--expected-source-git-sha", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)

    try:
        receipt = finalize_capture(
            args.manifest,
            args.capture_manifest,
            args.raw_dir,
            args.raw_response_manifest,
            args.teacher_rows,
            args.output_dir,
            expected_source_git_sha=args.expected_source_git_sha,
        )
        print(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    except (
        FinalizeError,
        td.ContractError,
        td.CollectionBlocked,
        sd.StudentDatasetError,
        eg.GateError,
        OSError,
    ) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
