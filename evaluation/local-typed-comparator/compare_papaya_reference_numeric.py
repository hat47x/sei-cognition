#!/usr/bin/env python3
"""Compare complete Python-Laya and Papaya capture artifacts without collapsing provenance."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path
from typing import Any

REPORT_SCHEMA = "sei.local-typed-comparator-cross-provider-numeric-report/v1"
REFERENCE_RUN_SCHEMA = "sei.local-typed-comparator-run/v1alpha1"
PAPAYA_RUN_SCHEMA = "sei.local-typed-comparator-papaya-run/v1"
FIXTURE_SCHEMA = "sei.local-typed-comparator-fixture/v1alpha1"

REFERENCE_PROVIDER = "laya"
REFERENCE_RESPONSE_MODEL = "laya-rl-agent"
REFERENCE_LOGICAL_MODEL = "typed-decisions"
REFERENCE_REPOSITORY = "convaiinnovations/laya-typed-decisions"
REFERENCE_REVISION = "f9ab0b228f0fc0f14d873dbc99038f135c2da1b2"
REFERENCE_MODEL_SHA256 = "4fa56de72383a9d3efa9cfa78955733c81b9fc8067a587ca4beb82c78107a24e"
REFERENCE_MODEL_BYTES = 842_609_220
REFERENCE_LAYA_VERSION = "0.3.20"
REFERENCE_LAYA_SOURCE_REVISION = "23a17522aa4942da6cce53a995a275760320b691"
REFERENCE_LAYA_WHEEL_SHA256 = "6039e802fa5effb8dd492061cd7ad39a43087beadc4a4fa4a649614e77eb83d4"

PAPAYA_PROVIDER = "papaya"
PAPAYA_RESPONSE_MODEL = "papaya/typed-decisions-v1"
PAPAYA_SOURCE_REPOSITORY = "m0rphtail/papaya"
PAPAYA_SOURCE_REVISION = "a76bc99bddafdac32863b2edc5319773e0cd3532"
EXPECTED_CLAMP_CHANGE = {
    "path": "temperature_by_options.choice:11+",
    "raw": 0.10058280825614929,
    "applied": 0.5,
}
EXPECTED_CASE_IDS = (
    "choice-route-a",
    "choice-route-b",
    "score-urgency",
    "noul-review",
)


class NumericComparisonError(ValueError):
    pass


def _object(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise NumericComparisonError(f"{field} must be an object")
    return value


def _array(value: Any, field: str) -> list[Any]:
    if not isinstance(value, list):
        raise NumericComparisonError(f"{field} must be an array")
    return value


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _protocol_module():
    path = Path(__file__).resolve().parent / "protocol_contract.py"
    spec = importlib.util.spec_from_file_location(
        "protocol_contract_cross_provider_numeric", path
    )
    if spec is None or spec.loader is None:
        raise NumericComparisonError(f"cannot import protocol contract: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _revalidate_contract(
    request: dict[str, Any], response: dict[str, Any], case_id: str
) -> None:
    try:
        _protocol_module().validate_response(request, response)
    except Exception as exc:
        raise NumericComparisonError(
            f"{case_id}: retained response no longer passes protocol contract: {exc}"
        ) from exc


def _load(path: Path, label: str) -> tuple[dict[str, Any], bytes]:
    try:
        raw = path.read_bytes()
        value = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise NumericComparisonError(f"cannot read {label}: {path}") from exc
    if not isinstance(value, dict):
        raise NumericComparisonError(f"{label} root must be an object")
    return value, raw


def _canonical_request(request: dict[str, Any]) -> dict[str, Any]:
    result = json.loads(json.dumps(request, ensure_ascii=False))
    result.pop("model", None)
    return result


def _decode_record(record: dict[str, Any], case_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    if record.get("case_id") != case_id:
        raise NumericComparisonError(f"{case_id}: case-id drift")
    if record.get("http_status") != 200 or record.get("contract") != "pass":
        raise NumericComparisonError(f"{case_id}: capture is not a complete contract pass")
    request_utf8 = record.get("request_utf8")
    response_utf8 = record.get("response_utf8")
    if not isinstance(request_utf8, str) or not isinstance(response_utf8, str):
        raise NumericComparisonError(f"{case_id}: missing retained request/response UTF-8")
    request_bytes = request_utf8.encode("utf-8")
    response_bytes = response_utf8.encode("utf-8")
    if record.get("request_sha256") != _sha256_bytes(request_bytes):
        raise NumericComparisonError(f"{case_id}: retained request SHA-256 drift")
    if record.get("response_sha256") != _sha256_bytes(response_bytes):
        raise NumericComparisonError(f"{case_id}: retained response SHA-256 drift")
    try:
        request = json.loads(request_utf8)
        response = json.loads(response_utf8)
    except json.JSONDecodeError as exc:
        raise NumericComparisonError(f"{case_id}: retained UTF-8 is not JSON") from exc
    if not isinstance(request, dict) or not isinstance(response, dict):
        raise NumericComparisonError(f"{case_id}: retained JSON root must be an object")
    return request, response


def _case_map(records: Any, field: str) -> dict[str, dict[str, Any]]:
    values = _array(records, field)
    result: dict[str, dict[str, Any]] = {}
    for item in values:
        if not isinstance(item, dict):
            raise NumericComparisonError(f"{field} entries must be objects")
        case_id = item.get("case_id")
        if not isinstance(case_id, str) or not case_id:
            raise NumericComparisonError(f"{field} entry missing case_id")
        if case_id in result:
            raise NumericComparisonError(f"{field}: duplicate case {case_id}")
        result[case_id] = item
    if set(result) != set(EXPECTED_CASE_IDS):
        raise NumericComparisonError(
            f"{field}: expected exactly {list(EXPECTED_CASE_IDS)}, got {sorted(result)}"
        )
    return result


def _validate_fixture(fixture: dict[str, Any], raw: bytes) -> tuple[str, dict[str, dict[str, Any]]]:
    if fixture.get("schema") != FIXTURE_SCHEMA:
        raise NumericComparisonError("fixture schema drift")
    cases = _array(fixture.get("cases"), "fixture.cases")
    by_id: dict[str, dict[str, Any]] = {}
    for case in cases:
        if not isinstance(case, dict):
            raise NumericComparisonError("fixture case must be an object")
        cid = case.get("case_id")
        if cid in by_id:
            raise NumericComparisonError(f"duplicate fixture case {cid!r}")
        by_id[cid] = case
    if tuple(c.get("case_id") for c in cases) != EXPECTED_CASE_IDS:
        raise NumericComparisonError("fixture case order/identity drift")
    return _sha256_bytes(raw), by_id


def _validate_reference(
    run: dict[str, Any],
    fixture_sha: str,
    fixture_cases: dict[str, dict[str, Any]],
) -> dict[str, tuple[dict[str, Any], dict[str, Any], dict[str, Any]]]:
    if run.get("schema") != REFERENCE_RUN_SCHEMA or run.get("status") != "complete":
        raise NumericComparisonError("reference run must be complete pinned capture")
    provider = _object(run.get("provider"), "reference.provider")
    if provider.get("name") != REFERENCE_PROVIDER:
        raise NumericComparisonError("reference provider identity drift")
    if provider.get("pypi_source_revision") != REFERENCE_LAYA_SOURCE_REVISION:
        raise NumericComparisonError("reference Laya source revision drift")
    runtime_wheel = _object(provider.get("runtime_wheel"), "reference.provider.runtime_wheel")
    if runtime_wheel.get("sha256") != REFERENCE_LAYA_WHEEL_SHA256:
        raise NumericComparisonError("reference runtime wheel digest drift")
    capture_interpreter = _object(
        provider.get("capture_interpreter"), "reference.provider.capture_interpreter"
    )
    if capture_interpreter.get("laya_version") != REFERENCE_LAYA_VERSION:
        raise NumericComparisonError("reference capture Laya version drift")
    runtime_binding = _object(
        provider.get("runtime_binding"), "reference.provider.runtime_binding"
    )
    if runtime_binding.get("supplied_runtime_wheel_digest_verified") is not True:
        raise NumericComparisonError("reference supplied runtime wheel was not verified")
    if runtime_binding.get("endpoint_exact_runtime_wheel_attested") is not False:
        raise NumericComparisonError(
            "reference endpoint runtime-wheel attestation scope drift"
        )
    checkpoint = _object(run.get("checkpoint"), "reference.checkpoint")
    if checkpoint.get("repository") != REFERENCE_REPOSITORY:
        raise NumericComparisonError("reference checkpoint repository drift")
    if checkpoint.get("hub_revision") != REFERENCE_REVISION:
        raise NumericComparisonError("reference checkpoint revision drift")
    if checkpoint.get("logical_model") != REFERENCE_LOGICAL_MODEL:
        raise NumericComparisonError("reference logical model drift")
    artifact = _object(checkpoint.get("model_artifact"), "reference.checkpoint.model_artifact")
    if artifact.get("sha256") != REFERENCE_MODEL_SHA256 or artifact.get("size_bytes") != REFERENCE_MODEL_BYTES:
        raise NumericComparisonError("reference model artifact identity drift")
    binding = _object(checkpoint.get("runtime_binding"), "reference.checkpoint.runtime_binding")
    if binding.get("logical_checkpoint_observed") is not True:
        raise NumericComparisonError("reference logical checkpoint was not observed")
    fixture = _object(run.get("fixture"), "reference.fixture")
    if fixture.get("sha256") != fixture_sha or fixture.get("case_count") != len(EXPECTED_CASE_IDS):
        raise NumericComparisonError("reference fixture binding drift")

    records = _case_map(run.get("cases"), "reference.cases")
    result = {}
    for cid in EXPECTED_CASE_IDS:
        record = records[cid]
        req, resp = _decode_record(record, cid)
        _revalidate_contract(req, resp, cid)
        if record.get("response_model") != REFERENCE_RESPONSE_MODEL:
            raise NumericComparisonError(f"{cid}: reference response model drift")
        if record.get("routing_model") != REFERENCE_LOGICAL_MODEL:
            raise NumericComparisonError(f"{cid}: reference routing model drift")
        expected_request = _object(fixture_cases[cid].get("request"), f"fixture.{cid}.request")
        if _canonical_request(req) != expected_request:
            raise NumericComparisonError(f"{cid}: reference request semantics drift")
        result[cid] = (record, req, resp)
    return result


def _validate_papaya(
    run: dict[str, Any],
    fixture_sha: str,
    fixture_cases: dict[str, dict[str, Any]],
) -> dict[str, tuple[dict[str, Any], dict[str, Any], dict[str, Any]]]:
    if run.get("schema") != PAPAYA_RUN_SCHEMA or run.get("status") != "complete":
        raise NumericComparisonError("Papaya run must be complete pinned capture")
    provider = _object(run.get("provider"), "papaya.provider")
    if provider.get("name") != PAPAYA_PROVIDER or provider.get("identity") != PAPAYA_RESPONSE_MODEL:
        raise NumericComparisonError("Papaya provider identity drift")
    if provider.get("jev_provider_identity") is not False:
        raise NumericComparisonError("Papaya run must not claim Jev provider identity")
    if provider.get("python_laya_reference_identity") is not False:
        raise NumericComparisonError("Papaya run must not claim Python-Laya identity")
    papaya_runtime = _object(run.get("papaya_runtime"), "papaya.papaya_runtime")
    if papaya_runtime.get("repository") != PAPAYA_SOURCE_REPOSITORY:
        raise NumericComparisonError("Papaya source repository drift")
    if papaya_runtime.get("revision") != PAPAYA_SOURCE_REVISION:
        raise NumericComparisonError("Papaya source revision drift")
    fixture = _object(run.get("fixture"), "papaya.fixture")
    if fixture.get("sha256") != fixture_sha or fixture.get("case_count") != len(EXPECTED_CASE_IDS):
        raise NumericComparisonError("Papaya fixture binding drift")
    scope = _object(run.get("scope"), "papaya.scope")
    required_true = (
        "papaya_runtime_source_verified",
        "papaya_live_inference",
        "frozen_protocol_contract",
        "frozen_live_token_count_matches_replay",
        "choice11_overlay_path_exercised",
    )
    for field in required_true:
        if scope.get(field) is not True:
            raise NumericComparisonError(f"Papaya scope.{field} must be true")
    for field in (
        "numeric_parity_with_python_laya",
        "task_quality",
        "calibration_validity",
        "jev_provider_identity",
        "reference_provider_promotion",
    ):
        if scope.get(field) is not False:
            raise NumericComparisonError(f"Papaya scope.{field} must remain false")
    overlay = _object(run.get("overlay"), "papaya.overlay")
    if overlay.get("verification_after_health_before_inference") is None:
        raise NumericComparisonError("Papaya overlay was not reverified after health")
    receipt = _object(overlay.get("receipt"), "papaya.overlay.receipt")
    policy = _object(receipt.get("temperature_policy"), "papaya.overlay.receipt.temperature_policy")
    if policy.get("changes") != [EXPECTED_CLAMP_CHANGE]:
        raise NumericComparisonError("Papaya compatibility clamp receipt drift")

    records = _case_map(run.get("frozen_cases"), "papaya.frozen_cases")
    result = {}
    for cid in EXPECTED_CASE_IDS:
        record = records[cid]
        req, resp = _decode_record(record, cid)
        _revalidate_contract(req, resp, cid)
        if record.get("diagnostic") is not False:
            raise NumericComparisonError(f"{cid}: frozen case mislabeled diagnostic")
        if record.get("response_model") != PAPAYA_RESPONSE_MODEL:
            raise NumericComparisonError(f"{cid}: Papaya response model drift")
        if record.get("live_token_count_matches_replay") is not True:
            raise NumericComparisonError(f"{cid}: Papaya token-count replay binding missing")
        expected_request = _object(fixture_cases[cid].get("request"), f"fixture.{cid}.request")
        if _canonical_request(req) != expected_request:
            raise NumericComparisonError(f"{cid}: Papaya request semantics drift")
        result[cid] = (record, req, resp)

    diagnostics = _array(run.get("diagnostic_cases"), "papaya.diagnostic_cases")
    if len(diagnostics) != 1 or diagnostics[0].get("diagnostic") is not True:
        raise NumericComparisonError("Papaya choice:11+ diagnostic must be retained separately")
    return result


def _finite_number(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise NumericComparisonError(f"{field} must be numeric")
    number = float(value)
    if not math.isfinite(number):
        raise NumericComparisonError(f"{field} must be finite")
    return number


def _probability_metrics(
    left: dict[str, Any], right: dict[str, Any], field: str
) -> dict[str, Any]:
    if set(left) != set(right):
        raise NumericComparisonError(f"{field}: probability key drift")
    keys = sorted(left)
    deltas = []
    for key in keys:
        a = _finite_number(left[key], f"{field}.reference.{key}")
        b = _finite_number(right[key], f"{field}.papaya.{key}")
        deltas.append(abs(a - b))
    return {
        "keys": keys,
        "max_abs_delta": max(deltas) if deltas else 0.0,
        "mean_abs_delta": sum(deltas) / len(deltas) if deltas else 0.0,
        "total_variation_distance": 0.5 * sum(deltas),
    }


def _question_comparison(
    qid: str, question: dict[str, Any], ref_answer: dict[str, Any], pap_answer: dict[str, Any]
) -> dict[str, Any]:
    qtype = question.get("type")
    if ref_answer.get("type") != qtype or pap_answer.get("type") != qtype:
        raise NumericComparisonError(f"{qid}: response type drift")
    result: dict[str, Any] = {"question_id": qid, "type": qtype}
    if qtype in ("choice", "score"):
        ref_probs = _object(ref_answer.get("probabilities"), f"{qid}.reference.probabilities")
        pap_probs = _object(pap_answer.get("probabilities"), f"{qid}.papaya.probabilities")
        result["probabilities"] = _probability_metrics(ref_probs, pap_probs, qid)
        result["confidence_abs_delta"] = abs(
            _finite_number(ref_answer.get("confidence"), f"{qid}.reference.confidence")
            - _finite_number(pap_answer.get("confidence"), f"{qid}.papaya.confidence")
        )
    if qtype == "choice":
        result["reference_selected"] = ref_answer.get("choice")
        result["papaya_selected"] = pap_answer.get("choice")
        result["selected_equal"] = ref_answer.get("choice") == pap_answer.get("choice")
    elif qtype == "score":
        a = _finite_number(ref_answer.get("score"), f"{qid}.reference.score")
        b = _finite_number(pap_answer.get("score"), f"{qid}.papaya.score")
        result["reference_score"] = a
        result["papaya_score"] = b
        result["score_abs_delta"] = abs(a - b)
        result["selected_equal"] = a == b
    elif qtype == "noul":
        a = _finite_number(ref_answer.get("noul"), f"{qid}.reference.noul")
        b = _finite_number(pap_answer.get("noul"), f"{qid}.papaya.noul")
        result["reference_noul"] = a
        result["papaya_noul"] = b
        result["noul_abs_delta"] = abs(a - b)
    else:
        raise NumericComparisonError(f"{qid}: unsupported question type {qtype!r}")
    return result


def compare_runs(
    fixture: dict[str, Any],
    fixture_raw: bytes,
    reference_run: dict[str, Any],
    papaya_run: dict[str, Any],
    *,
    reference_file_sha256: str | None = None,
    papaya_file_sha256: str | None = None,
) -> dict[str, Any]:
    fixture_sha, fixture_cases = _validate_fixture(fixture, fixture_raw)
    reference = _validate_reference(reference_run, fixture_sha, fixture_cases)
    papaya = _validate_papaya(papaya_run, fixture_sha, fixture_cases)

    cases = []
    probability_maxima: list[float] = []
    tv_values: list[float] = []
    scalar_deltas: list[float] = []
    selected_results: list[bool] = []

    for cid in EXPECTED_CASE_IDS:
        ref_record, _ref_req, ref_response = reference[cid]
        pap_record, _pap_req, pap_response = papaya[cid]
        ref_answers = _object(ref_response.get("answers"), f"{cid}.reference.answers")
        pap_answers = _object(pap_response.get("answers"), f"{cid}.papaya.answers")
        questions = _object(fixture_cases[cid]["request"].get("questions"), f"{cid}.questions")
        if set(ref_answers) != set(questions) or set(pap_answers) != set(questions):
            raise NumericComparisonError(f"{cid}: answer-id drift")
        qrows = []
        for qid, question in questions.items():
            row = _question_comparison(
                qid,
                _object(question, f"{cid}.{qid}.question"),
                _object(ref_answers[qid], f"{cid}.{qid}.reference"),
                _object(pap_answers[qid], f"{cid}.{qid}.papaya"),
            )
            qrows.append(row)
            probs = row.get("probabilities")
            if isinstance(probs, dict):
                probability_maxima.append(float(probs["max_abs_delta"]))
                tv_values.append(float(probs["total_variation_distance"]))
            for field in ("score_abs_delta", "noul_abs_delta"):
                if field in row:
                    scalar_deltas.append(float(row[field]))
            if "selected_equal" in row:
                selected_results.append(bool(row["selected_equal"]))
        ref_latency = _finite_number(ref_record.get("round_trip_latency_ms"), f"{cid}.reference.latency")
        pap_latency = _finite_number(pap_record.get("round_trip_latency_ms"), f"{cid}.papaya.latency")
        cases.append(
            {
                "case_id": cid,
                "questions": qrows,
                "latency_observation_ms": {
                    "reference": ref_latency,
                    "papaya": pap_latency,
                    "cross_runtime_performance_comparable": False,
                },
            }
        )

    numeric_difference_observed = (
        any(value > 0.0 for value in probability_maxima)
        or any(value > 0.0 for value in scalar_deltas)
        or any(not value for value in selected_results)
    )

    return {
        "schema": REPORT_SCHEMA,
        "fixture": {
            "schema": FIXTURE_SCHEMA,
            "sha256": fixture_sha,
            "case_ids": list(EXPECTED_CASE_IDS),
        },
        "inputs": {
            "reference": {
                "schema": REFERENCE_RUN_SCHEMA,
                "run_id": reference_run.get("run_id"),
                "provider": REFERENCE_PROVIDER,
                "artifact_sha256": reference_file_sha256,
            },
            "papaya": {
                "schema": PAPAYA_RUN_SCHEMA,
                "run_id": papaya_run.get("run_id"),
                "provider": PAPAYA_PROVIDER,
                "artifact_sha256": papaya_file_sha256,
            },
            "provider_provenance_merged": False,
        },
        "cases": cases,
        "aggregate": {
            "max_probability_abs_delta": max(probability_maxima) if probability_maxima else None,
            "mean_total_variation_distance": (
                sum(tv_values) / len(tv_values) if tv_values else None
            ),
            "max_score_or_noul_abs_delta": max(scalar_deltas) if scalar_deltas else None,
            "selected_output_equal_count": sum(1 for x in selected_results if x),
            "selected_output_compared_count": len(selected_results),
        },
        "scope": {
            "complete_capture_inputs_required": True,
            "numeric_difference_observed": numeric_difference_observed,
            "numeric_parity_threshold_defined": False,
            "numeric_parity_decision": False,
            "task_quality": False,
            "calibration_validity": False,
            "cross_runtime_performance_comparison": False,
            "jev_provider_identity_equivalence": False,
            "reference_provider_promotion": False,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("reference_run", type=Path)
    parser.add_argument("papaya_run", type=Path)
    parser.add_argument(
        "--fixture",
        type=Path,
        default=Path(__file__).resolve().parent / "fixture.v1.json",
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.output.exists():
            raise NumericComparisonError(f"output already exists: {args.output}")
        fixture, fixture_raw = _load(args.fixture, "fixture")
        reference, reference_raw = _load(args.reference_run, "reference run")
        papaya, papaya_raw = _load(args.papaya_run, "Papaya run")
        report = compare_runs(
            fixture,
            fixture_raw,
            reference,
            papaya,
            reference_file_sha256=_sha256_bytes(reference_raw),
            papaya_file_sha256=_sha256_bytes(papaya_raw),
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"status": "complete", "output": str(args.output)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
