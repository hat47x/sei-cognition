#!/usr/bin/env python3
"""Verify the JD-LGBM-0 artifact provenance chain before any student training.

This gate proves internal artifact identity/consistency only. It does not establish
teacher correctness, ground truth, Product Value, or authorization to train/activate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

TEACHER_MANIFEST_SCHEMA = "sei.jd-lgbm-teacher-manifest/v1alpha1"
CAPTURE_BUNDLE_SCHEMA = "sei.jd-lgbm-teacher-capture-bundle/v1alpha1"
RAW_RESPONSE_MANIFEST_SCHEMA = "sei.jd-lgbm-raw-response-manifest/v1alpha1"
TEACHER_ROW_SCHEMA = "sei.jd-lgbm-teacher-row/v1alpha1"
STUDENT_ROW_SCHEMA = "sei.jd-lgbm-student-record/v1alpha1"
DATASET_MANIFEST_SCHEMA = "sei.jd-lgbm-student-dataset-manifest/v1alpha1"
VERIFICATION_SCHEMA = "sei.jd-lgbm-evidence-chain-verification/v1alpha1"
DEFAULT_MODEL = "jev-latest"
EXPECTED_CASE_COUNT = 12


class GateError(ValueError):
    pass


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def sha256_file(path: Path) -> str:
    if not path.is_file():
        raise GateError(f"required file does not exist: {path}")
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(65536), b""):
            h.update(block)
    return h.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise GateError(f"required JSON file does not exist: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise GateError(f"invalid JSON: {path}") from exc
    if not isinstance(value, dict):
        raise GateError(f"JSON root must be an object: {path}")
    return value


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        raise GateError(f"required JSONL file does not exist: {path}")
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise GateError(f"invalid JSONL at {path}:{line_number}") from exc
        if not isinstance(value, dict):
            raise GateError(f"JSONL row must be an object at {path}:{line_number}")
        rows.append(value)
    if not rows:
        raise GateError(f"JSONL file is empty: {path}")
    return rows


def is_sha256_hex(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(ch in "0123456789abcdef" for ch in value.lower())
    )


def is_git_sha1(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 40
        and all(ch in "0123456789abcdef" for ch in value.lower())
    )


def is_real_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def project_raw_teacher_response(case: dict[str, Any], response: dict[str, Any]) -> dict[str, Any]:
    model = response.get("model")
    if not isinstance(model, str) or not model.startswith("jev-") or model == DEFAULT_MODEL:
        raise GateError(f"{case.get('case_id')}: immutable Jev model version is required")
    questions = case.get("questions")
    if not isinstance(questions, dict) or len(questions) != 1:
        raise GateError(f"{case.get('case_id')}: manifest must contain exactly one question")
    qid, question = next(iter(questions.items()))
    answers = response.get("answers")
    if not isinstance(answers, dict) or set(answers) != {qid}:
        raise GateError(f"{case.get('case_id')}: raw response answers must match the single requested question")
    answer = answers.get(qid)
    if not isinstance(answer, dict):
        raise GateError(f"{case.get('case_id')}: raw answer must be an object")
    qtype = question.get("type")
    if answer.get("type") != qtype:
        raise GateError(f"{case.get('case_id')}: raw answer type mismatch")

    usage = response.get("usage")
    if not isinstance(usage, dict):
        raise GateError(f"{case.get('case_id')}: raw response usage is required")
    for field in ("input_tokens", "output_tokens"):
        value = usage.get(field)
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise GateError(f"{case.get('case_id')}: raw response usage.{field} must be a non-negative integer")

    if qtype == "noul":
        value = answer.get("noul")
        if not is_real_number(value) or not 0.0 <= float(value) <= 1.0:
            raise GateError(f"{case.get('case_id')}: invalid raw Noul value")
        typed_output: Any = float(value)
        payload: dict[str, Any] = {"p_yes": float(value)}
    elif qtype == "choice":
        criteria = question.get("criteria")
        probs = answer.get("probabilities")
        confidence = answer.get("confidence")
        if not isinstance(criteria, dict) or answer.get("choice") not in criteria:
            raise GateError(f"{case.get('case_id')}: invalid raw Choice target")
        if (
            not isinstance(probs, dict)
            or set(probs) != set(criteria)
            or any(not is_real_number(v) or not 0.0 <= float(v) <= 1.0 for v in probs.values())
            or abs(sum(float(v) for v in probs.values()) - 1.0) > 1e-6
            or not is_real_number(confidence)
            or not 0.0 <= float(confidence) <= 1.0
        ):
            raise GateError(f"{case.get('case_id')}: invalid raw Choice distribution")
        typed_output = answer["choice"]
        payload = {"probabilities": probs, "confidence": float(confidence)}
    elif qtype == "score":
        criteria = question.get("criteria")
        probs = answer.get("probabilities")
        score = answer.get("score")
        confidence = answer.get("confidence")
        legend = answer.get("legend")
        if not isinstance(criteria, list) or not 2 <= len(criteria) <= 10:
            raise GateError(f"{case.get('case_id')}: invalid Score criteria")
        expected_keys = {str(i) for i in range(len(criteria))}
        expected_legend = {str(i): str(value) for i, value in enumerate(criteria)}
        if (
            not is_real_number(score)
            or not 0.0 <= float(score) <= len(criteria) - 1
            or not isinstance(probs, dict)
            or set(probs) != expected_keys
            or any(not is_real_number(v) or not 0.0 <= float(v) <= 1.0 for v in probs.values())
            or abs(sum(float(v) for v in probs.values()) - 1.0) > 1e-6
            or not is_real_number(confidence)
            or not 0.0 <= float(confidence) <= 1.0
            or legend != expected_legend
        ):
            raise GateError(f"{case.get('case_id')}: invalid raw Score answer")
        typed_output = float(score)
        payload = {
            "score": float(score),
            "probabilities": probs,
            "confidence": float(confidence),
            "legend": legend,
        }
    else:
        raise GateError(f"{case.get('case_id')}: unsupported question type: {qtype}")

    return {
        "teacher_model_version": model,
        "question_id": qid,
        "question_type": qtype,
        "typed_output": typed_output,
        "teacher_probability_or_score": payload,
        "usage": usage,
    }


def unique_by_case(rows: list[dict[str, Any]], expected_ids: list[str], label: str) -> dict[str, dict[str, Any]]:
    by_case: dict[str, dict[str, Any]] = {}
    for row in rows:
        case_id = row.get("case_id")
        if not isinstance(case_id, str) or not case_id:
            raise GateError(f"{label}: missing case_id")
        if case_id in by_case:
            raise GateError(f"{label}: duplicate case_id: {case_id}")
        by_case[case_id] = row
    if list(by_case) != expected_ids:
        raise GateError(f"{label}: case order/set does not match the fixed manifest")
    return by_case


def verify_evidence_chain(
    manifest_path: Path,
    capture_manifest_path: Path,
    raw_dir: Path,
    raw_response_manifest_path: Path,
    teacher_rows_path: Path,
    student_records_path: Path,
    dataset_manifest_path: Path,
) -> dict[str, Any]:
    manifest = load_json(manifest_path)
    if manifest.get("schema") != TEACHER_MANIFEST_SCHEMA:
        raise GateError("unexpected teacher manifest schema")
    if manifest.get("model") != DEFAULT_MODEL:
        raise GateError("JD-LGBM-0 manifest model must remain jev-latest")
    cases = manifest.get("cases")
    if not isinstance(cases, list) or len(cases) != EXPECTED_CASE_COUNT:
        raise GateError(f"JD-LGBM-0 requires exactly {EXPECTED_CASE_COUNT} fixed baseline cases")
    if any(not isinstance(case, dict) for case in cases):
        raise GateError("manifest case must be an object")
    case_ids = [case.get("case_id") for case in cases]
    if any(not isinstance(case_id, str) or not case_id for case_id in case_ids):
        raise GateError("manifest case_id must be a non-empty string")
    if len(set(case_ids)) != len(case_ids):
        raise GateError("manifest contains duplicate case_id")

    manifest_sha = sha256_file(manifest_path)
    capture = load_json(capture_manifest_path)
    if capture.get("schema") != CAPTURE_BUNDLE_SCHEMA:
        raise GateError("unexpected capture bundle schema")
    if capture.get("source_manifest_sha256") != manifest_sha:
        raise GateError("capture bundle does not bind the exact teacher manifest bytes")
    if capture.get("model_alias") != manifest["model"]:
        raise GateError("capture bundle model alias mismatch")
    if not is_git_sha1(capture.get("source_git_sha")):
        raise GateError("capture bundle source_git_sha is invalid")
    requests = capture.get("requests")
    if not isinstance(requests, list) or capture.get("request_count") != EXPECTED_CASE_COUNT:
        raise GateError("capture bundle request count does not match the fixed baseline")
    request_by_case = unique_by_case(requests, case_ids, "capture bundle")

    capture_root = capture_manifest_path.parent
    cases_by_id = {case["case_id"]: case for case in cases}
    for case_id in case_ids:
        case = cases_by_id[case_id]
        entry = request_by_case[case_id]
        expected_path = f"requests/{case_id}.json"
        if entry.get("request_path") != expected_path:
            raise GateError(f"{case_id}: non-canonical capture request path")
        request_path = capture_root / "requests" / f"{case_id}.json"
        request_obj = load_json(request_path)
        expected_request = {
            "state": case.get("state"),
            "model": manifest["model"],
            "questions": case.get("questions"),
        }
        if request_obj != expected_request:
            raise GateError(f"{case_id}: frozen request does not match the manifest")
        if entry.get("request_sha256") != sha256_json(request_obj):
            raise GateError(f"{case_id}: canonical request SHA-256 mismatch")
        if entry.get("request_file_sha256") != sha256_file(request_path):
            raise GateError(f"{case_id}: request file SHA-256 mismatch")
        for field in ("task_id", "split", "split_group_identity", "source_provenance_class"):
            if entry.get(field) != case.get(field):
                raise GateError(f"{case_id}: capture {field} mismatch")
        qvalues = case.get("questions")
        if not isinstance(qvalues, dict) or len(qvalues) != 1:
            raise GateError(f"{case_id}: manifest must contain exactly one question")
        if entry.get("question_type") != next(iter(qvalues.values())).get("type"):
            raise GateError(f"{case_id}: capture question_type mismatch")

    raw_manifest = load_json(raw_response_manifest_path)
    if raw_manifest.get("schema") != RAW_RESPONSE_MANIFEST_SCHEMA:
        raise GateError("unexpected raw response manifest schema")
    if raw_manifest.get("source_git_sha") != capture["source_git_sha"]:
        raise GateError("raw response manifest source_git_sha mismatch")
    if raw_manifest.get("source_manifest_sha256") != manifest_sha:
        raise GateError("raw response manifest teacher manifest hash mismatch")
    if raw_manifest.get("capture_manifest_sha256") != sha256_file(capture_manifest_path):
        raise GateError("raw response manifest capture manifest hash mismatch")
    mode = raw_manifest.get("capture_mode")
    if mode not in {"direct-run", "external-import"}:
        raise GateError("unsupported capture_mode")
    expected_latency_observed = mode == "direct-run"
    if raw_manifest.get("capture_latency_observed") is not expected_latency_observed:
        raise GateError("capture latency observation flag contradicts capture_mode")
    if raw_manifest.get("external_capture_latency_observed") is not False:
        raise GateError("external capture latency must not be inferred")
    responses = raw_manifest.get("responses")
    if not isinstance(responses, list) or raw_manifest.get("response_count") != EXPECTED_CASE_COUNT:
        raise GateError("raw response count does not match the fixed baseline")
    response_by_case = unique_by_case(responses, case_ids, "raw response manifest")
    if raw_manifest.get("raw_response_set_sha256") != sha256_json(responses):
        raise GateError("raw response descriptor-set SHA-256 mismatch")

    observed_models: list[str] = []
    raw_projection_by_case: dict[str, dict[str, Any]] = {}
    for case_id in case_ids:
        entry = response_by_case[case_id]
        if entry.get("request_sha256") != request_by_case[case_id].get("request_sha256"):
            raise GateError(f"{case_id}: raw response request identity mismatch")
        if entry.get("raw_response_path") != f"raw/{case_id}.json":
            raise GateError(f"{case_id}: non-canonical raw response path")
        raw_path = raw_dir / f"{case_id}.json"
        raw_sha = sha256_file(raw_path)
        if entry.get("raw_response_file_sha256") != raw_sha:
            raise GateError(f"{case_id}: raw response file SHA-256 mismatch")
        try:
            raw_obj = json.loads(raw_path.read_bytes())
        except json.JSONDecodeError as exc:
            raise GateError(f"{case_id}: raw response is invalid JSON") from exc
        if not isinstance(raw_obj, dict):
            raise GateError(f"{case_id}: raw response root must be an object")
        if entry.get("canonical_response_sha256") != sha256_json(raw_obj):
            raise GateError(f"{case_id}: canonical raw response SHA-256 mismatch")
        projection = project_raw_teacher_response(cases_by_id[case_id], raw_obj)
        raw_projection_by_case[case_id] = projection
        model = projection["teacher_model_version"]
        if entry.get("teacher_model_version") != model:
            raise GateError(f"{case_id}: raw response model version mismatch")
        latency = entry.get("teacher_latency_ms")
        if mode == "direct-run":
            if not is_real_number(latency) or float(latency) < 0.0:
                raise GateError(f"{case_id}: direct-run latency must be an observed non-negative number")
        elif latency is not None:
            raise GateError(f"{case_id}: external-import latency must remain null")
        observed_models.append(model)
    if raw_manifest.get("teacher_model_versions") != sorted(set(observed_models)):
        raise GateError("raw response manifest model-version summary mismatch")

    teacher_rows = load_jsonl(teacher_rows_path)
    teacher_by_case = unique_by_case(teacher_rows, case_ids, "teacher rows")
    teacher_versions: set[str] = set()
    for case_id in case_ids:
        case = cases_by_id[case_id]
        row = teacher_by_case[case_id]
        response_entry = response_by_case[case_id]
        if row.get("schema") != TEACHER_ROW_SCHEMA:
            raise GateError(f"{case_id}: unexpected teacher row schema")
        projection = raw_projection_by_case[case_id]
        expected_fields = {
            "task_id": case.get("task_id"),
            "question_id": projection["question_id"],
            "question_type": projection["question_type"],
            "feature_schema_version": case.get("feature_schema_version"),
            "task_schema_version": case.get("task_schema_version"),
            "source_provenance_class": case.get("source_provenance_class"),
            "split": case.get("split"),
            "split_group_identity": case.get("split_group_identity"),
            "teacher_provider": "typesafe",
            "teacher_model_alias": DEFAULT_MODEL,
            "teacher_request_hash": request_by_case[case_id].get("request_sha256"),
            "teacher_response_hash": response_entry.get("canonical_response_sha256"),
            "teacher_model_version": response_entry.get("teacher_model_version"),
            "teacher_latency_ms": response_entry.get("teacher_latency_ms"),
            "usage": projection["usage"],
        }
        for field, expected in expected_fields.items():
            if row.get(field) != expected:
                raise GateError(f"{case_id}: teacher row {field} breaks the evidence chain")
        if row.get("typed_output") != projection["typed_output"]:
            raise GateError(f"{case_id}: teacher typed_output does not match the raw Jev answer")
        if row.get("teacher_probability_or_score") != projection["teacher_probability_or_score"]:
            raise GateError(f"{case_id}: teacher distribution does not match the raw Jev answer")
        teacher_versions.add(row["teacher_model_version"])
    if len(teacher_versions) != 1:
        raise GateError(f"JD-LGBM-0 requires one immutable teacher model version; got {sorted(teacher_versions)}")
    teacher_version = next(iter(teacher_versions))

    student_rows = load_jsonl(student_records_path)
    student_by_case = unique_by_case(student_rows, case_ids, "student records")
    for case_id in case_ids:
        case = cases_by_id[case_id]
        teacher = teacher_by_case[case_id]
        student = student_by_case[case_id]
        if student.get("schema") != STUDENT_ROW_SCHEMA:
            raise GateError(f"{case_id}: unexpected student row schema")
        expected_fields = {
            "task_id": case.get("task_id"),
            "question_type": teacher.get("question_type"),
            "feature_schema_version": case.get("feature_schema_version"),
            "task_schema_version": case.get("task_schema_version"),
            "split": case.get("split"),
            "split_group_identity": case.get("split_group_identity"),
            "source_provenance_class": case.get("source_provenance_class"),
            "features": case.get("state"),
            "target": teacher.get("typed_output"),
            "teacher_distribution": teacher.get("teacher_probability_or_score"),
            "teacher_model_version": teacher.get("teacher_model_version"),
            "teacher_request_hash": teacher.get("teacher_request_hash"),
            "teacher_response_hash": teacher.get("teacher_response_hash"),
        }
        for field, expected in expected_fields.items():
            if student.get(field) != expected:
                raise GateError(f"{case_id}: student record {field} breaks the evidence chain")

    dataset = load_json(dataset_manifest_path)
    if dataset.get("schema") != DATASET_MANIFEST_SCHEMA:
        raise GateError("unexpected student dataset manifest schema")
    split_counts = {name: sum(case.get("split") == name for case in cases) for name in ("train", "valid", "test")}
    expected_dataset = {
        "record_count": EXPECTED_CASE_COUNT,
        "split_counts": split_counts,
        "teacher_model_version": teacher_version,
        "source_manifest_sha256": manifest_sha,
        "source_teacher_rows_sha256": sha256_file(teacher_rows_path),
        "student_records_sha256": sha256_file(student_records_path),
        "lightgbm_training_performed": False,
    }
    for field, expected in expected_dataset.items():
        if field == "lightgbm_training_performed":
            if dataset.get(field) is not False:
                raise GateError("student dataset manifest lightgbm_training_performed must be boolean false")
        elif dataset.get(field) != expected:
            raise GateError(f"student dataset manifest {field} mismatch")

    return {
        "schema": VERIFICATION_SCHEMA,
        "status": "PASS",
        "case_count": EXPECTED_CASE_COUNT,
        "source_git_sha": capture["source_git_sha"],
        "capture_mode": mode,
        "teacher_model_version": teacher_version,
        "hashes": {
            "teacher_manifest_sha256": manifest_sha,
            "capture_manifest_sha256": sha256_file(capture_manifest_path),
            "raw_response_manifest_sha256": sha256_file(raw_response_manifest_path),
            "raw_response_set_sha256": raw_manifest["raw_response_set_sha256"],
            "teacher_rows_sha256": sha256_file(teacher_rows_path),
            "student_records_sha256": sha256_file(student_records_path),
            "dataset_manifest_sha256": sha256_file(dataset_manifest_path),
        },
        "lightgbm_training_performed": False,
        "boundaries": [
            "integrity PASS != authenticated-origin attestation by this verifier",
            "integrity PASS != teacher correctness or ground truth",
            "integrity PASS != model quality or Product Value",
            "integrity PASS != automatic permission to train or activate a student",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("capture_manifest", type=Path)
    parser.add_argument("raw_dir", type=Path)
    parser.add_argument("raw_response_manifest", type=Path)
    parser.add_argument("teacher_rows", type=Path)
    parser.add_argument("student_records", type=Path)
    parser.add_argument("dataset_manifest", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = verify_evidence_chain(
            args.manifest,
            args.capture_manifest,
            args.raw_dir,
            args.raw_response_manifest,
            args.teacher_rows,
            args.student_records,
            args.dataset_manifest,
        )
        if args.output is not None:
            if args.output.exists() and not args.force:
                raise GateError(f"refusing to overwrite {args.output}; pass --force for an intentional rewrite")
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(
                json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    except GateError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
