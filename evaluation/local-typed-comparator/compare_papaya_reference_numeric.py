#!/usr/bin/env python3
"""Compare complete managed Python-Laya and Papaya captures without collapsing provenance.

This comparator measures retained numeric differences only after both live-run
artifacts pass their provider-specific provenance gates. It intentionally does
not define a parity acceptance threshold or promote either provider.
"""
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
REFERENCE_RUN_SCHEMA = "sei.local-typed-comparator-reference-managed-run/v1"
PAPAYA_RUN_SCHEMA = "sei.local-typed-comparator-papaya-run/v1"
FIXTURE_SCHEMA = "sei.local-typed-comparator-fixture/v1alpha1"
CHOICE11_ATTESTATION_SCHEMA = (
    "sei.local-typed-comparator-choice11-sequence-attestation/v1"
)

REFERENCE_PROVIDER = "laya"
REFERENCE_RESPONSE_MODEL = "laya-rl-agent"
REFERENCE_LOGICAL_MODEL = "typed-decisions"
REFERENCE_REPOSITORY = "convaiinnovations/laya-typed-decisions"
REFERENCE_REVISION = "f9ab0b228f0fc0f14d873dbc99038f135c2da1b2"
REFERENCE_MODEL_SHA256 = (
    "4fa56de72383a9d3efa9cfa78955733c81b9fc8067a587ca4beb82c78107a24e"
)
REFERENCE_MODEL_BYTES = 842_609_220
REFERENCE_LAYA_VERSION = "0.3.20"
REFERENCE_LAYA_SOURCE_REVISION = (
    "23a17522aa4942da6cce53a995a275760320b691"
)
REFERENCE_LAYA_WHEEL_SHA256 = (
    "6039e802fa5effb8dd492061cd7ad39a43087beadc4a4fa4a649614e77eb83d4"
)
REFERENCE_LAYA_WHEEL_BYTES = 118_520

PAPAYA_PROVIDER = "papaya"
PAPAYA_RESPONSE_MODEL = "papaya/typed-decisions-v1"
PAPAYA_SOURCE_REPOSITORY = "m0rphtail/papaya"
PAPAYA_SOURCE_REVISION = "a76bc99bddafdac32863b2edc5319773e0cd3532"
PAPAYA_LLAMA_SERVER_SHA256 = (
    "79e312188dc1d75c28201771f106e91de470b5cebdd838d31bb4db25eecf5d39"
)
PAPAYA_COMPAT_CONFIG_SHA256 = (
    "279207d55fefd56b2c6738dd141a3e10ab1d3f46b755c43faee42364ce1cc892"
)
EXPECTED_CLAMP_CHANGE = {
    "path": "temperature_by_options.choice:11+",
    "raw": 0.10058280825614929,
    "applied": 0.5,
}
CHOICE11_CASE_ID = "choice-12-clamp-path"
CHOICE11_QUESTION_ID = "choice12"
CHOICE11_TOKEN_COUNT = 155

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


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise NumericComparisonError(f"cannot import module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _protocol_module():
    return _load_module(
        Path(__file__).resolve().parent / "protocol_contract.py",
        "protocol_contract_cross_provider_numeric",
    )


def _choice11_module():
    return _load_module(
        Path(__file__).resolve().parent / "choice11_sequence_attestation.py",
        "choice11_sequence_attestation_cross_provider_numeric",
    )


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


def _ordered_request_bytes(request: dict[str, Any]) -> bytes:
    value = json.loads(json.dumps(request, ensure_ascii=False))
    value.pop("model", None)
    return json.dumps(
        value, ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")


def _expected_request_bytes(request: dict[str, Any]) -> bytes:
    return json.dumps(
        request, ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")


def _decode_record(
    record: dict[str, Any], case_id: str
) -> tuple[dict[str, Any], dict[str, Any]]:
    if record.get("case_id") != case_id:
        raise NumericComparisonError(f"{case_id}: case-id drift")
    if record.get("http_status") != 200 or record.get("contract") != "pass":
        raise NumericComparisonError(
            f"{case_id}: capture is not a complete contract pass"
        )
    request_utf8 = record.get("request_utf8")
    response_utf8 = record.get("response_utf8")
    if not isinstance(request_utf8, str) or not isinstance(response_utf8, str):
        raise NumericComparisonError(
            f"{case_id}: missing retained request/response UTF-8"
        )
    request_bytes = request_utf8.encode("utf-8")
    response_bytes = response_utf8.encode("utf-8")
    if record.get("request_sha256") != _sha256_bytes(request_bytes):
        raise NumericComparisonError(
            f"{case_id}: retained request SHA-256 drift"
        )
    if record.get("response_sha256") != _sha256_bytes(response_bytes):
        raise NumericComparisonError(
            f"{case_id}: retained response SHA-256 drift"
        )
    try:
        request = json.loads(request_utf8)
        response = json.loads(response_utf8)
    except json.JSONDecodeError as exc:
        raise NumericComparisonError(
            f"{case_id}: retained UTF-8 is not JSON"
        ) from exc
    if not isinstance(request, dict) or not isinstance(response, dict):
        raise NumericComparisonError(
            f"{case_id}: retained JSON root must be an object"
        )
    return request, response


def _case_map(
    records: Any, field: str, expected: tuple[str, ...] = EXPECTED_CASE_IDS
) -> dict[str, dict[str, Any]]:
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
    if set(result) != set(expected) or len(values) != len(expected):
        raise NumericComparisonError(
            f"{field}: expected exactly {list(expected)}, got {sorted(result)}"
        )
    return result


def _validate_fixture(
    fixture: dict[str, Any], raw: bytes
) -> tuple[str, dict[str, dict[str, Any]]]:
    if fixture.get("schema") != FIXTURE_SCHEMA:
        raise NumericComparisonError("fixture schema drift")
    cases = _array(fixture.get("cases"), "fixture.cases")
    if tuple(c.get("case_id") for c in cases if isinstance(c, dict)) != EXPECTED_CASE_IDS:
        raise NumericComparisonError("fixture case order/identity drift")
    by_id: dict[str, dict[str, Any]] = {}
    for case in cases:
        if not isinstance(case, dict):
            raise NumericComparisonError("fixture case must be an object")
        cid = case.get("case_id")
        if not isinstance(cid, str) or cid in by_id:
            raise NumericComparisonError(f"duplicate/invalid fixture case {cid!r}")
        by_id[cid] = case
    return _sha256_bytes(raw), by_id


def _valid_source_sha(run: dict[str, Any], field: str) -> str:
    source = _object(run.get("source"), field)
    sha = source.get("git_sha")
    if (
        not isinstance(sha, str)
        or len(sha) != 40
        or any(c not in "0123456789abcdef" for c in sha)
    ):
        raise NumericComparisonError(f"{field}.git_sha must be a full lowercase SHA")
    return sha


def _validate_reference_verification(value: Any, field: str) -> dict[str, Any]:
    verification = _object(value, field)
    if verification.get("valid") is not True:
        raise NumericComparisonError(f"{field}.valid must be true")
    if verification.get("source_repository") != REFERENCE_REPOSITORY:
        raise NumericComparisonError(f"{field} repository drift")
    if verification.get("source_revision") != REFERENCE_REVISION:
        raise NumericComparisonError(f"{field} revision drift")
    files = _object(
        verification.get("runtime_consumed_files"),
        f"{field}.runtime_consumed_files",
    )
    weights = _object(files.get("model.safetensors"), f"{field}.model.safetensors")
    if (
        weights.get("sha256") != REFERENCE_MODEL_SHA256
        or weights.get("bytes") != REFERENCE_MODEL_BYTES
    ):
        raise NumericComparisonError(f"{field} reference weight identity drift")
    if verification.get("tokenizer_config_rewrite_required") is not False:
        raise NumericComparisonError(f"{field} tokenizer rewrite scope drift")
    if verification.get("laya_0_3_20_applied_choice_11_plus_temperature") != 0.5:
        raise NumericComparisonError(f"{field} choice:11+ temperature drift")
    return verification


def _validate_reference(
    run: dict[str, Any],
    fixture_sha: str,
    fixture_cases: dict[str, dict[str, Any]],
) -> tuple[
    dict[str, tuple[dict[str, Any], dict[str, Any], dict[str, Any]]],
    dict[str, Any],
]:
    if run.get("schema") != REFERENCE_RUN_SCHEMA or run.get("status") != "complete":
        raise NumericComparisonError(
            "reference run must be complete managed pinned capture"
        )
    source_sha = _valid_source_sha(run, "reference.source")
    provider = _object(run.get("provider"), "reference.provider")
    if provider.get("name") != REFERENCE_PROVIDER:
        raise NumericComparisonError("reference provider identity drift")
    if provider.get("managed_endpoint") is not True:
        raise NumericComparisonError("reference endpoint must be managed by capture")
    if provider.get("runtime_source_revision") != REFERENCE_LAYA_SOURCE_REVISION:
        raise NumericComparisonError("reference Laya source revision drift")
    wheel = _object(provider.get("runtime_wheel"), "reference.provider.runtime_wheel")
    if (
        wheel.get("sha256") != REFERENCE_LAYA_WHEEL_SHA256
        or wheel.get("bytes") != REFERENCE_LAYA_WHEEL_BYTES
    ):
        raise NumericComparisonError("reference runtime wheel identity drift")

    runtime_identity = _object(run.get("runtime_identity"), "reference.runtime_identity")
    if runtime_identity.get("laya_version") != REFERENCE_LAYA_VERSION:
        raise NumericComparisonError("reference runtime Laya version drift")
    if runtime_identity.get("imported_from_extracted_wheel") is not True:
        raise NumericComparisonError("reference runtime wheel was not actually imported")
    if runtime_identity.get("loaded") != [REFERENCE_LOGICAL_MODEL]:
        raise NumericComparisonError("reference loaded checkpoint identity drift")
    if runtime_identity.get("model_binding_local_directory") is not True:
        raise NumericComparisonError("reference local model-directory binding missing")

    checkpoint = _object(run.get("checkpoint"), "reference.checkpoint")
    if checkpoint.get("repository") != REFERENCE_REPOSITORY:
        raise NumericComparisonError("reference checkpoint repository drift")
    if checkpoint.get("revision") != REFERENCE_REVISION:
        raise NumericComparisonError("reference checkpoint revision drift")
    before = _validate_reference_verification(
        checkpoint.get("verification_immediately_before_launch"),
        "reference.checkpoint.verification_immediately_before_launch",
    )
    after_health = _validate_reference_verification(
        checkpoint.get("verification_after_health_before_inference"),
        "reference.checkpoint.verification_after_health_before_inference",
    )
    after_inference = _validate_reference_verification(
        checkpoint.get("verification_after_inference"),
        "reference.checkpoint.verification_after_inference",
    )
    if before != after_health or after_health != after_inference:
        raise NumericComparisonError("reference model-directory verification changed during run")

    fixture = _object(run.get("fixture"), "reference.fixture")
    if (
        fixture.get("sha256") != fixture_sha
        or fixture.get("case_count") != len(EXPECTED_CASE_IDS)
    ):
        raise NumericComparisonError("reference fixture binding drift")

    scope = _object(run.get("scope"), "reference.scope")
    for field in (
        "reference_runtime_wheel_bytes_verified",
        "reference_runtime_imported_from_verified_wheel",
        "reference_model_directory_verified",
        "endpoint_loaded_exact_directory_attested",
        "endpoint_exact_runtime_wheel_attested",
        "reference_live_inference",
        "frozen_protocol_contract",
        "frozen_live_token_count_matches_reference",
        "choice11_reference_path_exercised",
    ):
        if scope.get(field) is not True:
            raise NumericComparisonError(f"reference scope.{field} must be true")
    for field in (
        "numeric_parity_with_papaya",
        "task_quality",
        "calibration_validity",
        "jev_provider_identity",
    ):
        if scope.get(field) is not False:
            raise NumericComparisonError(f"reference scope.{field} must remain false")

    records = _case_map(run.get("frozen_cases"), "reference.frozen_cases")
    result = {}
    for cid in EXPECTED_CASE_IDS:
        record = records[cid]
        req, resp = _decode_record(record, cid)
        _revalidate_contract(req, resp, cid)
        if record.get("response_model") != REFERENCE_RESPONSE_MODEL:
            raise NumericComparisonError(f"{cid}: reference response model drift")
        if record.get("routing_model") != REFERENCE_LOGICAL_MODEL:
            raise NumericComparisonError(f"{cid}: reference routing model drift")
        if record.get("live_token_count_matches_reference") is not True:
            raise NumericComparisonError(f"{cid}: reference token-count binding missing")
        if record.get("input_tokens") != record.get("expected_reference_input_tokens"):
            raise NumericComparisonError(f"{cid}: reference token-count receipt drift")
        expected = _object(fixture_cases[cid].get("request"), f"fixture.{cid}.request")
        if _ordered_request_bytes(req) != _expected_request_bytes(expected):
            raise NumericComparisonError(f"{cid}: reference request/order drift")
        result[cid] = (record, req, resp)

    return result, {"source_git_sha": source_sha}


def _validate_papaya(
    run: dict[str, Any],
    fixture_sha: str,
    fixture_cases: dict[str, dict[str, Any]],
) -> tuple[
    dict[str, tuple[dict[str, Any], dict[str, Any], dict[str, Any]]],
    dict[str, Any],
]:
    if run.get("schema") != PAPAYA_RUN_SCHEMA or run.get("status") != "complete":
        raise NumericComparisonError("Papaya run must be complete pinned capture")
    source_sha = _valid_source_sha(run, "papaya.source")
    provider = _object(run.get("provider"), "papaya.provider")
    if (
        provider.get("name") != PAPAYA_PROVIDER
        or provider.get("identity") != PAPAYA_RESPONSE_MODEL
    ):
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
    import_binding = _object(
        papaya_runtime.get("import_binding"), "papaya.papaya_runtime.import_binding"
    )
    if import_binding.get("source_checkout_imported") is not True:
        raise NumericComparisonError("Papaya source checkout import binding missing")

    llama = _object(run.get("llama_runtime"), "papaya.llama_runtime")
    if llama.get("sha256") != PAPAYA_LLAMA_SERVER_SHA256:
        raise NumericComparisonError("Papaya llama-server identity drift")
    if llama.get("version_verified") is not True:
        raise NumericComparisonError("Papaya llama-server version was not verified")

    fixture = _object(run.get("fixture"), "papaya.fixture")
    if (
        fixture.get("sha256") != fixture_sha
        or fixture.get("case_count") != len(EXPECTED_CASE_IDS)
    ):
        raise NumericComparisonError("Papaya fixture binding drift")

    scope = _object(run.get("scope"), "papaya.scope")
    for field in (
        "papaya_runtime_source_verified",
        "papaya_live_inference",
        "frozen_protocol_contract",
        "frozen_live_token_count_matches_replay",
        "choice11_overlay_path_exercised",
    ):
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
    before = _object(
        overlay.get("verification_before_launch"),
        "papaya.overlay.verification_before_launch",
    )
    after = _object(
        overlay.get("verification_after_health_before_inference"),
        "papaya.overlay.verification_after_health_before_inference",
    )
    if before.get("valid") is not True or after.get("valid") is not True:
        raise NumericComparisonError("Papaya overlay verification must be valid")
    receipt = _object(overlay.get("receipt"), "papaya.overlay.receipt")
    policy = _object(
        receipt.get("temperature_policy"),
        "papaya.overlay.receipt.temperature_policy",
    )
    if policy.get("changes") != [EXPECTED_CLAMP_CHANGE]:
        raise NumericComparisonError("Papaya compatibility clamp receipt drift")
    if policy.get("compat_config_sha256") != PAPAYA_COMPAT_CONFIG_SHA256:
        raise NumericComparisonError("Papaya compatibility config digest drift")

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
        if record.get("input_tokens") != record.get("retained_replay_input_tokens"):
            raise NumericComparisonError(f"{cid}: Papaya token-count receipt drift")
        expected = _object(fixture_cases[cid].get("request"), f"fixture.{cid}.request")
        if _ordered_request_bytes(req) != _expected_request_bytes(expected):
            raise NumericComparisonError(f"{cid}: Papaya request/order drift")
        result[cid] = (record, req, resp)

    return result, {"source_git_sha": source_sha}


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
    if list(left) != list(right):
        raise NumericComparisonError(f"{field}: probability key/order drift")
    deltas = []
    for key in left:
        a = _finite_number(left[key], f"{field}.reference.{key}")
        b = _finite_number(right[key], f"{field}.papaya.{key}")
        deltas.append(abs(a - b))
    return {
        "keys": list(left),
        "max_abs_delta": max(deltas) if deltas else 0.0,
        "mean_abs_delta": sum(deltas) / len(deltas) if deltas else 0.0,
        "total_variation_distance": 0.5 * sum(deltas),
    }


def _question_comparison(
    qid: str,
    question: dict[str, Any],
    ref_answer: dict[str, Any],
    pap_answer: dict[str, Any],
) -> dict[str, Any]:
    qtype = question.get("type")
    if ref_answer.get("type") != qtype or pap_answer.get("type") != qtype:
        raise NumericComparisonError(f"{qid}: response type drift")
    result: dict[str, Any] = {"question_id": qid, "type": qtype}

    if qtype in ("choice", "score"):
        ref_probs = _object(
            ref_answer.get("probabilities"), f"{qid}.reference.probabilities"
        )
        pap_probs = _object(
            pap_answer.get("probabilities"), f"{qid}.papaya.probabilities"
        )
        result["probabilities"] = _probability_metrics(ref_probs, pap_probs, qid)
        result["confidence_abs_delta"] = abs(
            _finite_number(
                ref_answer.get("confidence"), f"{qid}.reference.confidence"
            )
            - _finite_number(
                pap_answer.get("confidence"), f"{qid}.papaya.confidence"
            )
        )

    if qtype == "choice":
        result["reference_selected"] = ref_answer.get("choice")
        result["papaya_selected"] = pap_answer.get("choice")
        result["selected_equal"] = (
            ref_answer.get("choice") == pap_answer.get("choice")
        )
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
        raise NumericComparisonError(
            f"{qid}: unsupported question type {qtype!r}"
        )
    return result


def _validate_choice11_attestation(
    diagnostic_fixture: dict[str, Any],
    diagnostic_raw: bytes,
    attestation: dict[str, Any],
) -> None:
    if attestation.get("schema") != CHOICE11_ATTESTATION_SCHEMA:
        raise NumericComparisonError("choice11 sequence attestation schema drift")
    try:
        _choice11_module().validate_choice11_sequence(
            diagnostic_fixture,
            attestation,
            fixture_raw=diagnostic_raw,
        )
    except Exception as exc:
        raise NumericComparisonError(
            f"choice11 sequence attestation invalid: {exc}"
        ) from exc


def _validate_diagnostic_record(
    run: dict[str, Any],
    *,
    provider: str,
    diagnostic_fixture: dict[str, Any],
    diagnostic_sha: str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    meta = _object(run.get("choice11_diagnostic"), f"{provider}.choice11_diagnostic")
    if meta.get("sha256") != diagnostic_sha or meta.get("case_count") != 1:
        raise NumericComparisonError(f"{provider} diagnostic fixture binding drift")
    values = _array(run.get("diagnostic_cases"), f"{provider}.diagnostic_cases")
    if len(values) != 1 or not isinstance(values[0], dict):
        raise NumericComparisonError(f"{provider} must retain one diagnostic case")
    record = values[0]
    req, resp = _decode_record(record, CHOICE11_CASE_ID)
    _revalidate_contract(req, resp, CHOICE11_CASE_ID)

    fixture_case = _object(
        _array(diagnostic_fixture.get("cases"), "choice11.fixture.cases")[0],
        "choice11.fixture.case",
    )
    expected_request = _object(
        fixture_case.get("request"), "choice11.fixture.request"
    )
    if _ordered_request_bytes(req) != _expected_request_bytes(expected_request):
        raise NumericComparisonError(f"{provider} diagnostic request/order drift")
    usage = _object(resp.get("usage"), f"{provider}.diagnostic.response.usage")
    if usage.get("input_tokens") != CHOICE11_TOKEN_COUNT:
        raise NumericComparisonError(
            f"{provider} diagnostic live input_tokens must be {CHOICE11_TOKEN_COUNT}"
        )

    contract = _object(
        record.get("diagnostic_contract"), f"{provider}.diagnostic_contract"
    )
    if (
        contract.get("option_count") != 12
        or contract.get("temperature_bucket") != "choice:11+"
        or contract.get("expected_answer") is not None
        or contract.get("quality_claim") is not False
    ):
        raise NumericComparisonError(f"{provider} diagnostic contract drift")

    if provider == "reference":
        if record.get("response_model") != REFERENCE_RESPONSE_MODEL:
            raise NumericComparisonError("reference diagnostic response model drift")
        if record.get("routing_model") != REFERENCE_LOGICAL_MODEL:
            raise NumericComparisonError("reference diagnostic routing drift")
        if contract.get("reference_applied_temperature") != 0.5:
            raise NumericComparisonError("reference diagnostic temperature drift")
    else:
        if record.get("diagnostic") is not True:
            raise NumericComparisonError("Papaya diagnostic flag drift")
        if record.get("response_model") != PAPAYA_RESPONSE_MODEL:
            raise NumericComparisonError("Papaya diagnostic response model drift")
        if contract.get("compat_temperature") != 0.5:
            raise NumericComparisonError("Papaya diagnostic temperature drift")

    return record, req, resp


def _numeric_row(
    case_id: str,
    questions: dict[str, Any],
    ref_response: dict[str, Any],
    pap_response: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[float], list[float], list[float], list[bool]]:
    ref_answers = _object(ref_response.get("answers"), f"{case_id}.reference.answers")
    pap_answers = _object(pap_response.get("answers"), f"{case_id}.papaya.answers")
    if list(ref_answers) != list(questions) or list(pap_answers) != list(questions):
        raise NumericComparisonError(f"{case_id}: answer-id/order drift")

    rows: list[dict[str, Any]] = []
    probability_maxima: list[float] = []
    tv_values: list[float] = []
    scalar_deltas: list[float] = []
    selected_results: list[bool] = []
    for qid, question in questions.items():
        row = _question_comparison(
            qid,
            _object(question, f"{case_id}.{qid}.question"),
            _object(ref_answers[qid], f"{case_id}.{qid}.reference"),
            _object(pap_answers[qid], f"{case_id}.{qid}.papaya"),
        )
        rows.append(row)
        probs = row.get("probabilities")
        if isinstance(probs, dict):
            probability_maxima.append(float(probs["max_abs_delta"]))
            tv_values.append(float(probs["total_variation_distance"]))
        for field in ("score_abs_delta", "noul_abs_delta"):
            if field in row:
                scalar_deltas.append(float(row[field]))
        if "selected_equal" in row:
            selected_results.append(bool(row["selected_equal"]))
    return rows, probability_maxima, tv_values, scalar_deltas, selected_results


def compare_runs(
    fixture: dict[str, Any],
    fixture_raw: bytes,
    reference_run: dict[str, Any],
    papaya_run: dict[str, Any],
    diagnostic_fixture: dict[str, Any],
    diagnostic_raw: bytes,
    choice11_attestation: dict[str, Any],
    *,
    reference_file_sha256: str | None = None,
    papaya_file_sha256: str | None = None,
) -> dict[str, Any]:
    fixture_sha, fixture_cases = _validate_fixture(fixture, fixture_raw)
    _validate_choice11_attestation(
        diagnostic_fixture, diagnostic_raw, choice11_attestation
    )
    diagnostic_sha = _sha256_bytes(diagnostic_raw)

    reference, reference_meta = _validate_reference(
        reference_run, fixture_sha, fixture_cases
    )
    papaya, papaya_meta = _validate_papaya(
        papaya_run, fixture_sha, fixture_cases
    )
    if reference_meta["source_git_sha"] != papaya_meta["source_git_sha"]:
        raise NumericComparisonError(
            "reference and Papaya captures must use the same SEI source Git SHA"
        )

    cases = []
    probability_maxima: list[float] = []
    tv_values: list[float] = []
    scalar_deltas: list[float] = []
    selected_results: list[bool] = []

    for cid in EXPECTED_CASE_IDS:
        ref_record, _ref_req, ref_response = reference[cid]
        pap_record, _pap_req, pap_response = papaya[cid]
        questions = _object(
            fixture_cases[cid]["request"].get("questions"), f"{cid}.questions"
        )
        qrows, pmax, tv, scalars, selected = _numeric_row(
            cid, questions, ref_response, pap_response
        )
        probability_maxima.extend(pmax)
        tv_values.extend(tv)
        scalar_deltas.extend(scalars)
        selected_results.extend(selected)
        cases.append(
            {
                "case_id": cid,
                "questions": qrows,
                "input_sequence_precondition": "frozen four-case exact token/marker parity",
                "latency_observation_ms": {
                    "reference": _finite_number(
                        ref_record.get("round_trip_latency_ms"),
                        f"{cid}.reference.latency",
                    ),
                    "papaya": _finite_number(
                        pap_record.get("round_trip_latency_ms"),
                        f"{cid}.papaya.latency",
                    ),
                    "cross_runtime_performance_comparable": False,
                },
            }
        )

    ref_diag_record, _ref_diag_req, ref_diag_response = _validate_diagnostic_record(
        reference_run,
        provider="reference",
        diagnostic_fixture=diagnostic_fixture,
        diagnostic_sha=diagnostic_sha,
    )
    pap_diag_record, _pap_diag_req, pap_diag_response = _validate_diagnostic_record(
        papaya_run,
        provider="papaya",
        diagnostic_fixture=diagnostic_fixture,
        diagnostic_sha=diagnostic_sha,
    )
    diag_case = _object(
        _array(diagnostic_fixture.get("cases"), "choice11.fixture.cases")[0],
        "choice11.fixture.case",
    )
    diag_questions = _object(
        _object(diag_case.get("request"), "choice11.fixture.request").get("questions"),
        "choice11.fixture.questions",
    )
    diag_rows, dpmax, dtv, dscalars, dselected = _numeric_row(
        CHOICE11_CASE_ID,
        diag_questions,
        ref_diag_response,
        pap_diag_response,
    )
    probability_maxima.extend(dpmax)
    tv_values.extend(dtv)
    scalar_deltas.extend(dscalars)
    selected_results.extend(dselected)

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
        "choice11_sequence_precondition": {
            "schema": CHOICE11_ATTESTATION_SCHEMA,
            "diagnostic_sha256": diagnostic_sha,
            "token_count": CHOICE11_TOKEN_COUNT,
            "source_equivalent_exact_sequence_attested": True,
            "live_input_token_count_matched": True,
            "live_input_ids_observed": False,
            "live_marker_positions_observed": False,
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
            "same_sei_source_git_sha": reference_meta["source_git_sha"],
            "provider_provenance_merged": False,
        },
        "cases": cases,
        "choice11_diagnostic": {
            "case_id": CHOICE11_CASE_ID,
            "questions": diag_rows,
            "input_sequence_precondition": (
                "source-equivalent exact token/marker replay + live token-count match"
            ),
            "latency_observation_ms": {
                "reference": _finite_number(
                    ref_diag_record.get("round_trip_latency_ms"),
                    "choice11.reference.latency",
                ),
                "papaya": _finite_number(
                    pap_diag_record.get("round_trip_latency_ms"),
                    "choice11.papaya.latency",
                ),
                "cross_runtime_performance_comparable": False,
            },
            "expected_answer": None,
            "quality_claim": False,
        },
        "aggregate": {
            "includes_choice11_diagnostic": True,
            "max_probability_abs_delta": (
                max(probability_maxima) if probability_maxima else None
            ),
            "mean_total_variation_distance": (
                sum(tv_values) / len(tv_values) if tv_values else None
            ),
            "max_score_or_noul_abs_delta": (
                max(scalar_deltas) if scalar_deltas else None
            ),
            "selected_output_equal_count": sum(
                1 for value in selected_results if value
            ),
            "selected_output_compared_count": len(selected_results),
        },
        "scope": {
            "complete_managed_capture_inputs_required": True,
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
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser()
    parser.add_argument("reference_run", type=Path)
    parser.add_argument("papaya_run", type=Path)
    parser.add_argument("--fixture", type=Path, default=here / "fixture.v1.json")
    parser.add_argument(
        "--diagnostic",
        type=Path,
        default=here / "papaya_choice11_diagnostic.v1.json",
    )
    parser.add_argument(
        "--choice11-attestation",
        type=Path,
        default=here / "choice11_sequence_attestation.v1.json",
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)

    try:
        if args.output.exists():
            raise NumericComparisonError(f"output already exists: {args.output}")
        fixture, fixture_raw = _load(args.fixture, "fixture")
        diagnostic, diagnostic_raw = _load(args.diagnostic, "choice11 diagnostic")
        choice11, _ = _load(args.choice11_attestation, "choice11 attestation")
        reference, reference_raw = _load(args.reference_run, "reference run")
        papaya, papaya_raw = _load(args.papaya_run, "Papaya run")
        report = compare_runs(
            fixture,
            fixture_raw,
            reference,
            papaya,
            diagnostic,
            diagnostic_raw,
            choice11,
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

    print(
        json.dumps(
            {
                "status": "complete",
                "output": str(args.output),
                "numeric_parity_threshold_defined": False,
                "numeric_parity_decision": False,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
