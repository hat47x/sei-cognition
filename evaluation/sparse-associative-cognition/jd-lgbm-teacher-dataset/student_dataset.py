#!/usr/bin/env python3
"""Validate Jev teacher rows and join them to structured student inputs.

This is a readiness gate only. It does not train LightGBM or any other student.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
_SPEC = importlib.util.spec_from_file_location("teacher_dataset", HERE / "teacher_dataset.py")
td = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(td)

STUDENT_ROW_SCHEMA = "sei.jd-lgbm-student-record/v1alpha1"
DATASET_MANIFEST_SCHEMA = "sei.jd-lgbm-student-dataset-manifest/v1alpha1"


class StudentDatasetError(ValueError):
    pass


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(65536), b""):
            h.update(block)
    return h.hexdigest()


def load_teacher_rows(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        raise StudentDatasetError(f"teacher row file does not exist: {path}")
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise StudentDatasetError(f"invalid JSON at teacher row line {line_number}") from exc
        if not isinstance(row, dict):
            raise StudentDatasetError(f"teacher row line {line_number} must be an object")
        rows.append(row)
    if not rows:
        raise StudentDatasetError("teacher row file is empty; no student dataset can be prepared")
    return rows


def _validate_probability_map(probs: Any, expected_keys: set[str]) -> None:
    if not isinstance(probs, dict) or set(probs) != expected_keys:
        raise StudentDatasetError("teacher distribution keys do not match the task contract")
    values: list[float] = []
    for value in probs.values():
        if not isinstance(value, (int, float)) or not 0.0 <= float(value) <= 1.0:
            raise StudentDatasetError("teacher distribution contains an invalid probability")
        values.append(float(value))
    if abs(sum(values) - 1.0) > 1e-6:
        raise StudentDatasetError("teacher distribution probabilities must sum to 1")


def validate_teacher_row(case: dict[str, Any], row: dict[str, Any]) -> None:
    if row.get("schema") != td.ROW_SCHEMA:
        raise StudentDatasetError(f"{case['case_id']}: unexpected teacher row schema")
    exact_fields = {
        "case_id": case["case_id"],
        "task_id": case["task_id"],
        "feature_schema_version": case["feature_schema_version"],
        "task_schema_version": case["task_schema_version"],
        "source_provenance_class": case["source_provenance_class"],
        "split": case["split"],
        "split_group_identity": case["split_group_identity"],
        "teacher_provider": "typesafe",
        "teacher_model_alias": td.DEFAULT_MODEL,
        "teacher_request_hash": td.sha256_json(td.request_for(case)),
    }
    for field, expected in exact_fields.items():
        if row.get(field) != expected:
            raise StudentDatasetError(f"{case['case_id']}: teacher row {field} does not match manifest/request identity")

    model = row.get("teacher_model_version")
    if not isinstance(model, str) or not model.startswith("jev-") or model == td.DEFAULT_MODEL:
        raise StudentDatasetError(f"{case['case_id']}: immutable Jev teacher model version is required")
    response_hash = row.get("teacher_response_hash")
    if not isinstance(response_hash, str) or len(response_hash) != 64:
        raise StudentDatasetError(f"{case['case_id']}: teacher_response_hash must be a SHA-256 hex digest")
    if not row.get("generation_time"):
        raise StudentDatasetError(f"{case['case_id']}: generation_time is required")

    _, question = next(iter(case["questions"].items()))
    qtype = question["type"]
    if row.get("question_type") != qtype:
        raise StudentDatasetError(f"{case['case_id']}: question_type mismatch")
    target = row.get("typed_output")
    payload = row.get("teacher_probability_or_score")
    if not isinstance(payload, dict):
        raise StudentDatasetError(f"{case['case_id']}: teacher probability/score payload is required")
    if qtype == "noul":
        if not isinstance(target, (int, float)) or not 0.0 <= float(target) <= 1.0:
            raise StudentDatasetError(f"{case['case_id']}: invalid Noul target")
        if payload.get("p_yes") != target:
            raise StudentDatasetError(f"{case['case_id']}: Noul probability payload does not match target")
    elif qtype == "choice":
        criteria = set(question["criteria"])
        if target not in criteria:
            raise StudentDatasetError(f"{case['case_id']}: Choice target is outside criteria")
        _validate_probability_map(payload.get("probabilities"), criteria)
        confidence = payload.get("confidence")
        if not isinstance(confidence, (int, float)) or not 0.0 <= float(confidence) <= 1.0:
            raise StudentDatasetError(f"{case['case_id']}: invalid Choice confidence")
    else:
        if not isinstance(target, (int, float)) or not 0.0 <= float(target) <= len(question["criteria"]) - 1:
            raise StudentDatasetError(f"{case['case_id']}: invalid Score target")
        if payload.get("score") != target:
            raise StudentDatasetError(f"{case['case_id']}: Score payload does not match target")
        _validate_probability_map(payload.get("probabilities"), {str(i) for i in range(len(question["criteria"]))})
        confidence = payload.get("confidence")
        if not isinstance(confidence, (int, float)) or not 0.0 <= float(confidence) <= 1.0:
            raise StudentDatasetError(f"{case['case_id']}: invalid Score confidence")


def prepare_student_records(manifest: dict[str, Any], teacher_rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], str]:
    td.validate_manifest(manifest)
    cases = {case["case_id"]: case for case in manifest["cases"]}
    rows_by_case: dict[str, dict[str, Any]] = {}
    for row in teacher_rows:
        case_id = row.get("case_id")
        if case_id not in cases:
            raise StudentDatasetError(f"unknown teacher row case_id: {case_id}")
        if case_id in rows_by_case:
            raise StudentDatasetError(f"duplicate teacher row case_id: {case_id}")
        rows_by_case[case_id] = row
    missing = sorted(set(cases) - set(rows_by_case))
    if missing:
        raise StudentDatasetError(f"teacher rows are incomplete; missing cases: {', '.join(missing)}")

    versions: set[str] = set()
    records: list[dict[str, Any]] = []
    for case in manifest["cases"]:
        row = rows_by_case[case["case_id"]]
        validate_teacher_row(case, row)
        versions.add(row["teacher_model_version"])
        records.append({
            "schema": STUDENT_ROW_SCHEMA,
            "case_id": case["case_id"],
            "task_id": case["task_id"],
            "question_type": row["question_type"],
            "feature_schema_version": case["feature_schema_version"],
            "task_schema_version": case["task_schema_version"],
            "split": case["split"],
            "split_group_identity": case["split_group_identity"],
            "source_provenance_class": case["source_provenance_class"],
            "features": copy.deepcopy(case["state"]),
            "target": row["typed_output"],
            "teacher_distribution": row["teacher_probability_or_score"],
            "teacher_model_version": row["teacher_model_version"],
            "teacher_request_hash": row["teacher_request_hash"],
            "teacher_response_hash": row["teacher_response_hash"],
        })
    if len(versions) != 1:
        raise StudentDatasetError(f"mixed Jev teacher model versions are not allowed in JD-LGBM-0 readiness: {sorted(versions)}")
    return records, next(iter(versions))


def write_student_dataset(manifest_path: Path, teacher_rows_path: Path, output_dir: Path, *, force: bool = False) -> dict[str, Any]:
    manifest = td.load_manifest(manifest_path)
    teacher_rows = load_teacher_rows(teacher_rows_path)
    records, teacher_version = prepare_student_records(manifest, teacher_rows)
    output_dir.mkdir(parents=True, exist_ok=True)
    records_path = output_dir / "student_records.jsonl"
    summary_path = output_dir / "dataset_manifest.json"
    if (records_path.exists() or summary_path.exists()) and not force:
        raise StudentDatasetError("refusing to overwrite existing student dataset artifacts; pass --force for an intentional rebuild")
    records_path.write_text("".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in records), encoding="utf-8")
    split_counts = {name: sum(r["split"] == name for r in records) for name in ("train", "valid", "test")}
    summary = {
        "schema": DATASET_MANIFEST_SCHEMA,
        "record_count": len(records),
        "split_counts": split_counts,
        "teacher_model_version": teacher_version,
        "source_manifest_sha256": sha256_file(manifest_path),
        "source_teacher_rows_sha256": sha256_file(teacher_rows_path),
        "student_records_sha256": sha256_file(records_path),
        "lightgbm_training_performed": False,
    }
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("teacher_rows", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("jd-lgbm-student-dataset"))
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    try:
        summary = write_student_dataset(args.manifest, args.teacher_rows, args.output_dir, force=args.force)
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0
    except (td.ContractError, StudentDatasetError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
