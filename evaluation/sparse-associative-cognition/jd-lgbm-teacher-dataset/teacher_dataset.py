#!/usr/bin/env python3
"""JD-LGBM-0 TypeSafe/Jev teacher dataset harness.

This module intentionally does not provide a fake teacher. Plan/validation operations are
network-free. Actual collection requires TYPESAFE_API_KEY and POSTs to the documented
System One endpoint.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

API_URL = "https://api.typesafe.ai/v1/systemone"
DEFAULT_MODEL = "jev-latest"
ROW_SCHEMA = "sei.jd-lgbm-teacher-row/v1alpha1"
CAPTURE_BUNDLE_SCHEMA = "sei.jd-lgbm-teacher-capture-bundle/v1alpha1"
RAW_RESPONSE_MANIFEST_SCHEMA = "sei.jd-lgbm-raw-response-manifest/v1alpha1"
REQUIRED_CASE_FIELDS = {
    "case_id",
    "task_id",
    "feature_schema_version",
    "task_schema_version",
    "source_provenance_class",
    "split",
    "split_group_identity",
    "state",
    "questions",
}
QUESTION_TYPES = {"choice", "score", "noul"}


class ContractError(ValueError):
    pass


class CollectionBlocked(RuntimeError):
    pass


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(65536), b""):
            h.update(block)
    return h.hexdigest()


def load_manifest(path: Path) -> dict[str, Any]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    validate_manifest(obj)
    return obj


def validate_manifest(manifest: dict[str, Any]) -> None:
    if manifest.get("schema") != "sei.jd-lgbm-teacher-manifest/v1alpha1":
        raise ContractError("unexpected manifest schema")
    if manifest.get("model") != DEFAULT_MODEL:
        raise ContractError("manifest model must remain jev-latest for JD-LGBM-0")
    cases = manifest.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ContractError("manifest cases must be a non-empty list")
    ids: set[str] = set()
    seen_types: set[str] = set()
    group_splits: dict[str, str] = {}
    for case in cases:
        if not isinstance(case, dict):
            raise ContractError("every case must be an object")
        missing = REQUIRED_CASE_FIELDS - set(case)
        if missing:
            raise ContractError(f"case missing fields: {sorted(missing)}")
        case_id = case["case_id"]
        if case_id in ids:
            raise ContractError(f"duplicate case_id: {case_id}")
        ids.add(case_id)
        if not isinstance(case["state"], (dict, list)):
            raise ContractError(f"{case_id}: state must be structured object/array, not raw text")
        if case["split"] not in {"train", "valid", "test"}:
            raise ContractError(f"{case_id}: invalid split")
        if not case["split_group_identity"]:
            raise ContractError(f"{case_id}: split_group_identity is required")
        group = case["split_group_identity"]
        previous_split = group_splits.get(group)
        if previous_split is not None and previous_split != case["split"]:
            raise ContractError(
                f"{case_id}: split_group_identity {group} crosses {previous_split}/{case['split']} splits"
            )
        group_splits[group] = case["split"]
        questions = case["questions"]
        if not isinstance(questions, dict) or len(questions) != 1:
            raise ContractError(f"{case_id}: JD-LGBM-0 cases must contain exactly one typed question")
        qid, question = next(iter(questions.items()))
        qtype = question.get("type")
        if qtype not in QUESTION_TYPES:
            raise ContractError(f"{case_id}/{qid}: unsupported question type")
        seen_types.add(qtype)
        if not question.get("instructions"):
            raise ContractError(f"{case_id}/{qid}: instructions required")
        criteria = question.get("criteria")
        if qtype == "choice" and (not isinstance(criteria, dict) or len(criteria) < 2):
            raise ContractError(f"{case_id}/{qid}: choice requires >=2 criteria")
        if qtype == "score" and (not isinstance(criteria, list) or not 2 <= len(criteria) <= 10):
            raise ContractError(f"{case_id}/{qid}: score requires 2..10 levels")
    if seen_types != QUESTION_TYPES:
        raise ContractError(f"manifest must cover Choice/Score/Noul; got {sorted(seen_types)}")


def request_for(case: dict[str, Any], model: str = DEFAULT_MODEL) -> dict[str, Any]:
    return {"state": case["state"], "model": model, "questions": case["questions"]}


def request_descriptor(case: dict[str, Any], model: str = DEFAULT_MODEL) -> dict[str, Any]:
    req = request_for(case, model)
    return {
        "case_id": case["case_id"],
        "task_id": case["task_id"],
        "request_sha256": sha256_json(req),
        "question_type": next(iter(case["questions"].values()))["type"],
        "split": case["split"],
        "split_group_identity": case["split_group_identity"],
        "source_provenance_class": case["source_provenance_class"],
    }


def validate_response(case: dict[str, Any], response: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    model = response.get("model")
    if not isinstance(model, str) or not model.startswith("jev-") or model == DEFAULT_MODEL:
        raise ContractError("response must bind an immutable Jev model version, not only jev-latest")
    answers = response.get("answers")
    if not isinstance(answers, dict):
        raise ContractError("response.answers must be an object")
    qid, question = next(iter(case["questions"].items()))
    if set(answers) != {qid}:
        raise ContractError("response.answers must contain exactly the requested question")
    answer = answers.get(qid)
    if not isinstance(answer, dict):
        raise ContractError(f"missing answer for {qid}")
    qtype = question["type"]
    if answer.get("type") != qtype:
        raise ContractError(f"answer type mismatch for {qid}")
    if qtype == "noul":
        value = answer.get("noul")
        if not _is_real_number(value) or not 0.0 <= float(value) <= 1.0:
            raise ContractError("noul must be a numeric value in [0,1]")
    elif qtype == "choice":
        probs = answer.get("probabilities")
        if not isinstance(probs, dict) or set(probs) != set(question["criteria"]):
            raise ContractError("choice probabilities must match criteria keys")
        _validate_probabilities(probs)
        if answer.get("choice") not in probs:
            raise ContractError("choice must be one of the declared options")
        _validate_confidence(answer)
    else:
        probs = answer.get("probabilities")
        expected_keys = {str(i) for i in range(len(question["criteria"]))}
        if not isinstance(probs, dict) or set(probs) != expected_keys:
            raise ContractError("score probabilities must cover every score level")
        _validate_probabilities(probs)
        score = answer.get("score")
        if not _is_real_number(score) or not 0.0 <= float(score) <= len(question["criteria"]) - 1:
            raise ContractError("score must be numeric and inside the declared level range")
        legend = answer.get("legend")
        if not isinstance(legend, dict) or set(legend) != expected_keys:
            raise ContractError("score legend must cover every declared score level")
        expected_legend = {str(i): str(value) for i, value in enumerate(question["criteria"])}
        if legend != expected_legend:
            raise ContractError("score legend must match the declared criteria")
        _validate_confidence(answer)
    _validate_usage(response)
    return model, answer


def _is_real_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _validate_probabilities(probs: dict[str, Any]) -> None:
    values = []
    for key, value in probs.items():
        if not _is_real_number(value) or not 0.0 <= float(value) <= 1.0:
            raise ContractError(f"invalid probability for {key}")
        values.append(float(value))
    if abs(sum(values) - 1.0) > 1e-6:
        raise ContractError("probabilities must sum to 1")


def _validate_confidence(answer: dict[str, Any]) -> None:
    confidence = answer.get("confidence")
    if not _is_real_number(confidence) or not 0.0 <= float(confidence) <= 1.0:
        raise ContractError("confidence must be a numeric value in [0,1]")


def _validate_usage(response: dict[str, Any]) -> None:
    usage = response.get("usage")
    if not isinstance(usage, dict):
        raise ContractError("response.usage must be an object")
    for field in ("input_tokens", "output_tokens"):
        value = usage.get(field)
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise ContractError(f"response.usage.{field} must be a non-negative integer")


def dataset_row(
    case: dict[str, Any],
    response: dict[str, Any],
    *,
    generated_at: str,
    latency_ms: float | None,
) -> dict[str, Any]:
    model, answer = validate_response(case, response)
    qid, question = next(iter(case["questions"].items()))
    qtype = question["type"]
    if qtype == "noul":
        typed_output: Any = float(answer["noul"])
        payload: Any = {"p_yes": float(answer["noul"])}
    elif qtype == "choice":
        typed_output = answer["choice"]
        payload = {
            "probabilities": answer["probabilities"],
            "confidence": float(answer["confidence"]),
        }
    else:
        typed_output = float(answer["score"])
        payload = {
            "score": float(answer["score"]),
            "probabilities": answer["probabilities"],
            "confidence": float(answer["confidence"]),
            "legend": answer.get("legend"),
        }
    req = request_for(case)
    usage = response["usage"]
    return {
        "schema": ROW_SCHEMA,
        "case_id": case["case_id"],
        "task_id": case["task_id"],
        "question_id": qid,
        "question_type": qtype,
        "feature_schema_version": case["feature_schema_version"],
        "task_schema_version": case["task_schema_version"],
        "teacher_provider": "typesafe",
        "teacher_model_alias": DEFAULT_MODEL,
        "teacher_model_version": model,
        "teacher_request_hash": sha256_json(req),
        "teacher_response_hash": sha256_json(response),
        "typed_output": typed_output,
        "teacher_probability_or_score": payload,
        "source_provenance_class": case["source_provenance_class"],
        "generation_time": generated_at,
        "split": case["split"],
        "split_group_identity": case["split_group_identity"],
        "teacher_latency_ms": latency_ms,
        "usage": usage,
    }


def collect_case_raw(
    case: dict[str, Any],
    api_key: str,
    timeout: float = 30.0,
    *,
    max_attempts: int = 4,
    backoff_base_seconds: float = 0.5,
) -> tuple[dict[str, Any], float, bytes]:
    if not api_key:
        raise CollectionBlocked("TYPESAFE_API_KEY is required for an actual Jev teacher call")
    if max_attempts < 1:
        raise ContractError("max_attempts must be >= 1")
    body = canonical_json(request_for(case))
    request = urllib.request.Request(
        API_URL,
        data=body,
        method="POST",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
    )
    started = time.perf_counter()
    raw: bytes | None = None
    for attempt in range(max_attempts):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as resp:
                raw = resp.read()
            break
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            if exc.code in {429, 529} and attempt + 1 < max_attempts:
                time.sleep(backoff_base_seconds * (2**attempt))
                continue
            raise CollectionBlocked(f"TypeSafe HTTP {exc.code}: {detail[:500]}") from exc
        except OSError as exc:
            raise CollectionBlocked(f"TypeSafe transport failure: {exc}") from exc
    if raw is None:
        raise CollectionBlocked("TypeSafe collection exhausted retry attempts without a response")
    latency_ms = (time.perf_counter() - started) * 1000.0
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ContractError("TypeSafe response was not valid JSON") from exc
    validate_response(case, parsed)
    return parsed, latency_ms, raw


def collect_case(
    case: dict[str, Any],
    api_key: str,
    timeout: float = 30.0,
    *,
    max_attempts: int = 4,
    backoff_base_seconds: float = 0.5,
) -> tuple[dict[str, Any], float]:
    parsed, latency_ms, _ = collect_case_raw(
        case,
        api_key,
        timeout,
        max_attempts=max_attempts,
        backoff_base_seconds=backoff_base_seconds,
    )
    return parsed, latency_ms


def plan(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    return [request_descriptor(case, manifest["model"]) for case in manifest["cases"]]


def write_capture_bundle(
    manifest_path: Path,
    manifest: dict[str, Any],
    output_dir: Path,
    *,
    source_git_sha: str,
) -> dict[str, Any]:
    validate_manifest(manifest)
    source_git_sha = source_git_sha.strip().lower()
    if len(source_git_sha) != 40 or any(ch not in "0123456789abcdef" for ch in source_git_sha):
        raise ContractError("source_git_sha must be a 40-character Git SHA-1 hex string")
    if output_dir.exists() and not output_dir.is_dir():
        raise CollectionBlocked(f"capture bundle output path is not a directory: {output_dir}")
    if output_dir.exists() and any(output_dir.iterdir()):
        raise CollectionBlocked(
            f"capture bundle output must be a new or empty directory: {output_dir}"
        )

    requests_dir = output_dir / "requests"
    requests_dir.mkdir(parents=True, exist_ok=True)
    descriptors: list[dict[str, Any]] = []
    for case in manifest["cases"]:
        request = request_for(case, manifest["model"])
        request_bytes = canonical_json(request) + b"\n"
        request_path = requests_dir / f"{case['case_id']}.json"
        try:
            with request_path.open("xb") as fh:
                fh.write(request_bytes)
        except FileExistsError as exc:
            raise CollectionBlocked(f"refusing to overwrite capture request: {request_path}") from exc
        descriptors.append({
            **request_descriptor(case, manifest["model"]),
            "request_path": f"requests/{case['case_id']}.json",
            "request_file_sha256": hashlib.sha256(request_bytes).hexdigest(),
        })

    bundle = {
        "schema": CAPTURE_BUNDLE_SCHEMA,
        "api_url": API_URL,
        "method": "POST",
        "content_type": "application/json",
        "model_alias": manifest["model"],
        "source_git_sha": source_git_sha,
        "source_manifest_name": manifest_path.name,
        "source_manifest_sha256": sha256_file(manifest_path),
        "request_count": len(descriptors),
        "requests": descriptors,
        "boundaries": [
            "request bundle creation sends no network request",
            "bundle request identity != Jev response Evidence",
            "first 12-row bundle is the fixed passive baseline; active curriculum may only add later acquisition",
        ],
    }
    bundle_path = output_dir / "capture_manifest.json"
    try:
        with bundle_path.open("x", encoding="utf-8") as fh:
            json.dump(bundle, fh, ensure_ascii=False, indent=2, sort_keys=True)
            fh.write("\n")
    except FileExistsError as exc:
        raise CollectionBlocked(f"refusing to overwrite capture manifest: {bundle_path}") from exc
    return bundle


def load_capture_bundle(
    manifest_path: Path,
    manifest: dict[str, Any],
    capture_manifest_path: Path,
) -> dict[str, Any]:
    validate_manifest(manifest)
    try:
        bundle = json.loads(capture_manifest_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise CollectionBlocked(f"capture manifest does not exist: {capture_manifest_path}") from exc
    except json.JSONDecodeError as exc:
        raise ContractError("capture manifest is not valid JSON") from exc

    if bundle.get("schema") != CAPTURE_BUNDLE_SCHEMA:
        raise ContractError("unexpected capture bundle schema")
    if bundle.get("api_url") != API_URL or bundle.get("method") != "POST":
        raise ContractError("capture bundle endpoint/method does not match the teacher contract")
    if bundle.get("content_type") != "application/json":
        raise ContractError("capture bundle content type must be application/json")
    if bundle.get("model_alias") != manifest["model"]:
        raise ContractError("capture bundle model alias does not match the manifest")
    if bundle.get("source_manifest_sha256") != sha256_file(manifest_path):
        raise ContractError("capture bundle source manifest hash does not match current manifest")
    source_git_sha = bundle.get("source_git_sha")
    if not isinstance(source_git_sha, str) or len(source_git_sha) != 40 or any(
        ch not in "0123456789abcdef" for ch in source_git_sha.lower()
    ):
        raise ContractError("capture bundle source_git_sha is invalid")

    entries = bundle.get("requests")
    if (
        not isinstance(entries, list)
        or bundle.get("request_count") != len(manifest["cases"])
        or len(entries) != len(manifest["cases"])
    ):
        raise ContractError("capture bundle request count does not match the manifest")
    by_case: dict[str, dict[str, Any]] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            raise ContractError("capture bundle request entry must be an object")
        case_id = entry.get("case_id")
        if not isinstance(case_id, str) or case_id in by_case:
            raise ContractError("capture bundle contains missing/duplicate case_id")
        by_case[case_id] = entry

    expected_ids = {case["case_id"] for case in manifest["cases"]}
    if set(by_case) != expected_ids:
        raise ContractError("capture bundle case set does not match the manifest")

    bundle_root = capture_manifest_path.parent
    for case in manifest["cases"]:
        case_id = case["case_id"]
        entry = by_case[case_id]
        expected_descriptor = request_descriptor(case, manifest["model"])
        for field, expected in expected_descriptor.items():
            if entry.get(field) != expected:
                raise ContractError(f"{case_id}: capture bundle {field} does not match current request")
        expected_relative_path = f"requests/{case_id}.json"
        if entry.get("request_path") != expected_relative_path:
            raise ContractError(f"{case_id}: capture bundle request_path is not canonical")
        request_path = bundle_root / "requests" / f"{case_id}.json"
        try:
            request_bytes = request_path.read_bytes()
        except FileNotFoundError as exc:
            raise CollectionBlocked(f"missing frozen request file: {request_path}") from exc
        expected_bytes = canonical_json(request_for(case, manifest["model"])) + b"\n"
        if request_bytes != expected_bytes:
            raise ContractError(f"{case_id}: frozen request bytes do not match the current canonical request")
        if entry.get("request_file_sha256") != hashlib.sha256(request_bytes).hexdigest():
            raise ContractError(f"{case_id}: frozen request file SHA-256 mismatch")
    return bundle


def build_raw_response_manifest(
    manifest_path: Path,
    capture_manifest_path: Path,
    capture_bundle: dict[str, Any],
    raw_descriptors: list[dict[str, Any]],
    *,
    capture_mode: str,
    capture_latency_observed: bool,
) -> dict[str, Any]:
    if capture_mode not in {"direct-run", "external-import"}:
        raise ContractError(f"unsupported capture_mode: {capture_mode}")
    return {
        "schema": RAW_RESPONSE_MANIFEST_SCHEMA,
        "source_git_sha": capture_bundle["source_git_sha"],
        "source_manifest_sha256": sha256_file(manifest_path),
        "capture_manifest_sha256": sha256_file(capture_manifest_path),
        "capture_mode": capture_mode,
        "capture_latency_observed": capture_latency_observed,
        "response_count": len(raw_descriptors),
        "responses": raw_descriptors,
        "raw_response_set_sha256": sha256_json(raw_descriptors),
        "teacher_model_versions": sorted({item["teacher_model_version"] for item in raw_descriptors}),
        "external_capture_latency_observed": capture_mode == "external-import" and capture_latency_observed,
        "boundaries": [
            "raw response bytes are teacher Evidence, not semantic truth or ground truth",
            "capture latency is recorded only when this harness directly observed it",
            "raw response manifest completeness != single-version student readiness",
            "raw response manifest creation != permission to train or activate a student",
        ],
    }


def run_collection(
    manifest: dict[str, Any],
    output_dir: Path,
    *,
    api_key: str,
    manifest_path: Path | None = None,
    capture_manifest_path: Path | None = None,
    raw_manifest_path: Path | None = None,
    force: bool = False,
) -> int:
    if not api_key:
        raise CollectionBlocked("TYPESAFE_API_KEY is absent; no teacher request was sent")
    if manifest_path is None or capture_manifest_path is None:
        raise CollectionBlocked("direct collection requires manifest_path and capture_manifest_path")
    capture_bundle = load_capture_bundle(manifest_path, manifest, capture_manifest_path)
    capture_by_case = {entry["case_id"]: entry for entry in capture_bundle["requests"]}
    raw_manifest_path = raw_manifest_path or output_dir / "raw_response_manifest.json"

    output_dir.mkdir(parents=True, exist_ok=True)
    raw_dir = output_dir / "raw"
    raw_dir.mkdir(exist_ok=True)
    rows_path = output_dir / "teacher_rows.jsonl"
    protected_paths = [rows_path, raw_manifest_path] + [
        raw_dir / f"{case['case_id']}.json" for case in manifest["cases"]
    ]
    existing = [path for path in protected_paths if path.exists()]
    if existing and not force:
        raise CollectionBlocked(
            f"refusing to overwrite existing direct-capture artifacts: {', '.join(str(path) for path in existing)}"
        )

    rows: list[dict[str, Any]] = []
    raw_descriptors: list[dict[str, Any]] = []
    for case in manifest["cases"]:
        response, latency_ms, raw_bytes = collect_case_raw(case, api_key)
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        raw_path = raw_dir / f"{case['case_id']}.json"
        raw_path.write_bytes(raw_bytes)
        row = dataset_row(case, response, generated_at=now, latency_ms=latency_ms)
        rows.append(row)
        raw_descriptors.append({
            "case_id": case["case_id"],
            "request_sha256": capture_by_case[case["case_id"]]["request_sha256"],
            "raw_response_path": f"raw/{case['case_id']}.json",
            "raw_response_file_sha256": hashlib.sha256(raw_bytes).hexdigest(),
            "canonical_response_sha256": sha256_json(response),
            "teacher_model_version": row["teacher_model_version"],
            "teacher_latency_ms": latency_ms,
        })

    rows_path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )
    raw_manifest = build_raw_response_manifest(
        manifest_path,
        capture_manifest_path,
        capture_bundle,
        raw_descriptors,
        capture_mode="direct-run",
        capture_latency_observed=True,
    )
    raw_manifest_path.write_text(
        json.dumps(raw_manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return len(rows)


def normalize_raw_directory(
    manifest: dict[str, Any],
    raw_dir: Path,
    rows_path: Path,
    *,
    force: bool = False,
    generated_at: str | None = None,
    manifest_path: Path | None = None,
    capture_manifest_path: Path | None = None,
    raw_manifest_path: Path | None = None,
) -> int:
    if rows_path.exists() and not force:
        raise CollectionBlocked(f"refusing to overwrite {rows_path}; pass --force for an intentional re-import")
    if raw_manifest_path is not None and raw_manifest_path.exists() and not force:
        raise CollectionBlocked(
            f"refusing to overwrite {raw_manifest_path}; pass --force for an intentional re-import"
        )

    capture_bundle: dict[str, Any] | None = None
    capture_by_case: dict[str, dict[str, Any]] = {}
    if capture_manifest_path is not None:
        if manifest_path is None:
            raise ContractError("manifest_path is required when capture_manifest_path is supplied")
        capture_bundle = load_capture_bundle(manifest_path, manifest, capture_manifest_path)
        capture_by_case = {entry["case_id"]: entry for entry in capture_bundle["requests"]}
        expected_names = {f"{case['case_id']}.json" for case in manifest["cases"]}
        actual_names = {path.name for path in raw_dir.glob("*.json")}
        extras = sorted(actual_names - expected_names)
        if extras:
            raise CollectionBlocked(f"unexpected raw response files: {', '.join(extras)}")
    elif raw_manifest_path is not None:
        raise ContractError("raw_manifest_path requires capture_manifest_path")

    rows: list[dict[str, Any]] = []
    raw_descriptors: list[dict[str, Any]] = []
    for case in manifest["cases"]:
        raw_path = raw_dir / f"{case['case_id']}.json"
        if not raw_path.is_file():
            raise CollectionBlocked(f"missing raw response: {raw_path}")
        raw_bytes = raw_path.read_bytes()
        try:
            response = json.loads(raw_bytes)
        except json.JSONDecodeError as exc:
            raise ContractError(f"invalid JSON in {raw_path}") from exc
        now = generated_at or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        row = dataset_row(case, response, generated_at=now, latency_ms=None)
        rows.append(row)
        if capture_bundle is not None:
            raw_descriptors.append({
                "case_id": case["case_id"],
                "request_sha256": capture_by_case[case["case_id"]]["request_sha256"],
                "raw_response_path": f"raw/{case['case_id']}.json",
                "raw_response_file_sha256": hashlib.sha256(raw_bytes).hexdigest(),
                "canonical_response_sha256": sha256_json(response),
                "teacher_model_version": row["teacher_model_version"],
                "teacher_latency_ms": None,
            })
    rows_path.parent.mkdir(parents=True, exist_ok=True)
    rows_path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )
    if raw_manifest_path is not None:
        raw_manifest_path.parent.mkdir(parents=True, exist_ok=True)
        raw_manifest = build_raw_response_manifest(
            manifest_path,
            capture_manifest_path,
            capture_bundle,
            raw_descriptors,
            capture_mode="external-import",
            capture_latency_observed=False,
        )
        raw_manifest_path.write_text(
            json.dumps(raw_manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    return len(rows)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--mode", choices=("plan", "bundle", "run", "import"), default="plan")
    parser.add_argument("--output-dir", type=Path, default=Path("jd-lgbm0-output"))
    parser.add_argument("--raw-dir", type=Path)
    parser.add_argument("--capture-manifest", type=Path)
    parser.add_argument("--source-git-sha")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    try:
        manifest = load_manifest(args.manifest)
        if args.mode == "plan":
            print(json.dumps({"model": manifest["model"], "requests": plan(manifest)}, ensure_ascii=False, indent=2))
            return 0
        if args.mode == "bundle":
            if args.force:
                raise CollectionBlocked("capture bundle is exclusive-create; use a fresh output directory instead of --force")
            if not args.source_git_sha:
                raise CollectionBlocked("--source-git-sha is required for bundle mode")
            bundle = write_capture_bundle(
                args.manifest,
                manifest,
                args.output_dir,
                source_git_sha=args.source_git_sha,
            )
            print(json.dumps({
                "schema": bundle["schema"],
                "request_count": bundle["request_count"],
                "source_git_sha": bundle["source_git_sha"],
                "capture_manifest_sha256": sha256_file(args.output_dir / "capture_manifest.json"),
            }, ensure_ascii=False, indent=2))
            return 0
        if args.mode == "import":
            if args.raw_dir is None:
                raise CollectionBlocked("--raw-dir is required for import mode")
            if args.capture_manifest is None:
                raise CollectionBlocked("--capture-manifest is required for import mode")
            count = normalize_raw_directory(
                manifest,
                args.raw_dir,
                args.output_dir / "teacher_rows.jsonl",
                force=args.force,
                manifest_path=args.manifest,
                capture_manifest_path=args.capture_manifest,
                raw_manifest_path=args.output_dir / "raw_response_manifest.json",
            )
            print(f"imported {count} validated Jev teacher rows")
            return 0
        if args.capture_manifest is None:
            raise CollectionBlocked("--capture-manifest is required for run mode")
        count = run_collection(
            manifest,
            args.output_dir,
            api_key=os.environ.get("TYPESAFE_API_KEY", ""),
            manifest_path=args.manifest,
            capture_manifest_path=args.capture_manifest,
            raw_manifest_path=args.output_dir / "raw_response_manifest.json",
            force=args.force,
        )
        print(f"collected {count} Jev teacher rows")
        return 0
    except (ContractError, CollectionBlocked) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
