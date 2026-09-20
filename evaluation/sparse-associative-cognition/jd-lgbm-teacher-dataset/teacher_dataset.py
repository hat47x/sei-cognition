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
    answer = answers.get(qid)
    if not isinstance(answer, dict):
        raise ContractError(f"missing answer for {qid}")
    qtype = question["type"]
    if answer.get("type") != qtype:
        raise ContractError(f"answer type mismatch for {qid}")
    if qtype == "noul":
        value = answer.get("noul")
        if not isinstance(value, (int, float)) or not 0.0 <= float(value) <= 1.0:
            raise ContractError("noul must be in [0,1]")
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
        if not isinstance(probs, dict) or set(probs) != {str(i) for i in range(len(question["criteria"]))}:
            raise ContractError("score probabilities must cover every score level")
        _validate_probabilities(probs)
        score = answer.get("score")
        if not isinstance(score, (int, float)) or not 0.0 <= float(score) <= len(question["criteria"]) - 1:
            raise ContractError("score outside declared level range")
        _validate_confidence(answer)
    return model, answer


def _validate_probabilities(probs: dict[str, Any]) -> None:
    values = []
    for key, value in probs.items():
        if not isinstance(value, (int, float)) or not 0.0 <= float(value) <= 1.0:
            raise ContractError(f"invalid probability for {key}")
        values.append(float(value))
    if abs(sum(values) - 1.0) > 1e-6:
        raise ContractError("probabilities must sum to 1")


def _validate_confidence(answer: dict[str, Any]) -> None:
    confidence = answer.get("confidence")
    if not isinstance(confidence, (int, float)) or not 0.0 <= float(confidence) <= 1.0:
        raise ContractError("confidence must be in [0,1]")


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
    usage = response.get("usage") if isinstance(response.get("usage"), dict) else None
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


def collect_case(
    case: dict[str, Any],
    api_key: str,
    timeout: float = 30.0,
    *,
    max_attempts: int = 4,
    backoff_base_seconds: float = 0.5,
) -> tuple[dict[str, Any], float]:
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
    return parsed, latency_ms


def plan(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    return [request_descriptor(case, manifest["model"]) for case in manifest["cases"]]


def run_collection(manifest: dict[str, Any], output_dir: Path, *, api_key: str, force: bool = False) -> int:
    if not api_key:
        raise CollectionBlocked("TYPESAFE_API_KEY is absent; no teacher request was sent")
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_dir = output_dir / "raw"
    raw_dir.mkdir(exist_ok=True)
    rows_path = output_dir / "teacher_rows.jsonl"
    if rows_path.exists() and not force:
        raise CollectionBlocked(f"refusing to overwrite {rows_path}; pass --force for an intentional rerun")
    rows: list[dict[str, Any]] = []
    for case in manifest["cases"]:
        response, latency_ms = collect_case(case, api_key)
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        raw_path = raw_dir / f"{case['case_id']}.json"
        raw_path.write_text(json.dumps(response, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        rows.append(dataset_row(case, response, generated_at=now, latency_ms=latency_ms))
    rows_path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows), encoding="utf-8")
    return len(rows)


def normalize_raw_directory(
    manifest: dict[str, Any],
    raw_dir: Path,
    rows_path: Path,
    *,
    force: bool = False,
    generated_at: str | None = None,
) -> int:
    if rows_path.exists() and not force:
        raise CollectionBlocked(f"refusing to overwrite {rows_path}; pass --force for an intentional re-import")
    rows: list[dict[str, Any]] = []
    for case in manifest["cases"]:
        raw_path = raw_dir / f"{case['case_id']}.json"
        if not raw_path.is_file():
            raise CollectionBlocked(f"missing raw response: {raw_path}")
        try:
            response = json.loads(raw_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ContractError(f"invalid JSON in {raw_path}") from exc
        now = generated_at or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        rows.append(dataset_row(case, response, generated_at=now, latency_ms=None))
    rows_path.parent.mkdir(parents=True, exist_ok=True)
    rows_path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )
    return len(rows)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--mode", choices=("plan", "run", "import"), default="plan")
    parser.add_argument("--output-dir", type=Path, default=Path("jd-lgbm0-output"))
    parser.add_argument("--raw-dir", type=Path)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    try:
        manifest = load_manifest(args.manifest)
        if args.mode == "plan":
            print(json.dumps({"model": manifest["model"], "requests": plan(manifest)}, ensure_ascii=False, indent=2))
            return 0
        if args.mode == "import":
            if args.raw_dir is None:
                raise CollectionBlocked("--raw-dir is required for import mode")
            count = normalize_raw_directory(
                manifest,
                args.raw_dir,
                args.output_dir / "teacher_rows.jsonl",
                force=args.force,
            )
            print(f"imported {count} validated Jev teacher rows")
            return 0
        count = run_collection(manifest, args.output_dir, api_key=os.environ.get("TYPESAFE_API_KEY", ""), force=args.force)
        print(f"collected {count} Jev teacher rows")
        return 0
    except (ContractError, CollectionBlocked) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
