#!/usr/bin/env python3
"""Capture one fail-closed Papaya live run against SEI's frozen comparator inputs.

This is a Papaya-provider capture, not the pinned Python Laya reference capture.
It verifies the local SEI checkout, the exact Papaya source checkout, the
prepared #620/#621 compatibility overlay, and an SEI-pinned llama-server binary
before starting a loopback-only Papaya process.

The normal four-case fixture and the separate 12-option clamp-path diagnostic
are captured independently. A successful run is protocol/runtime Evidence only;
it is not numeric parity with Python Laya, task-quality Evidence, or Jev identity.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import importlib.util
import json
import os
import platform
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

RUN_SCHEMA = "sei.local-typed-comparator-papaya-run/v1"
PAPAYA_PROVIDER = "papaya"
PAPAYA_RESPONSE_MODEL = "papaya/typed-decisions-v1"
PAPAYA_SOURCE_REPOSITORY = "m0rphtail/papaya"
PAPAYA_SOURCE_REVISION = "a76bc99bddafdac32863b2edc5319773e0cd3532"
PAPAYA_SOURCE_BLOBS = {
    "pyproject.toml": "a6a1add0f0140edfeb97ac275b01c43198dba89e",
    "src/papaya/__init__.py": "113d22f84ba917b032cf030353b55cdef305acdf",
    "src/papaya/cli.py": "f504ef110dbe5e49a6e80520fa685d225053e646",
    "src/papaya/head.py": "a38529ca7a07c130460754200e834bfd3f1c3d5b",
    "src/papaya/questions.py": "7b1fe73f23b225a04f4b2ac53fd0011a4fdf90bf",
    "src/papaya/runtime.py": "b3999b7f1e02d4761ffba63b7f846b210f3e27dd",
    "src/papaya/sequences.py": "f21139970d6d288114213db8f917f0cead9c082f",
    "src/papaya/server.py": "dde92287bbf68c590952df7aadb9d8d61c2868df",
}

LLAMA_RUNTIME_EVIDENCE_PATH = (
    "evaluation/local-model-probe/"
    "first_actual_runtime_materialization_evidence_2026-09-23.json"
)
LLAMA_RUNTIME_EVIDENCE_BLOB = "c554fd1a646494ce3880679894e360364d7b79ab"
LLAMA_RELEASE_TAG = "b10964"
LLAMA_SOURCE_REVISION = "b29c606e28a01b1bc8c1351026a0fa6e616bf6c4"
LLAMA_SERVER_SHA256 = (
    "79e312188dc1d75c28201771f106e91de470b5cebdd838d31bb4db25eecf5d39"
)
LLAMA_VERSION_SUBSTRING = "0.4.1-dev (build 10964, commit b29c606e2)"

OVERLAY_SCHEMA = "sei.local-typed-comparator-papaya-compat-overlay/v1"
SEQUENCE_REPLAY_SCHEMA = "sei.local-typed-comparator-papaya-sequence-replay/v1"
DIAGNOSTIC_CASE_ID = "choice-12-clamp-path"
DIAGNOSTIC_QUESTION_ID = "choice12"
DIAGNOSTIC_OPTION_COUNT = 12
EXPECTED_CLAMP_CHANGE = {
    "path": "temperature_by_options.choice:11+",
    "raw": 0.10058280825614929,
    "applied": 0.5,
}

MAX_RESPONSE_BYTES = 2 * 1024 * 1024
MAX_LOG_CAPTURE_BYTES = 1024 * 1024
LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}


class PapayaCaptureError(ValueError):
    pass


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> tuple[str, int]:
    h = hashlib.sha256()
    size = 0
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
            size += len(chunk)
    return h.hexdigest(), size


def git_blob_sha1_bytes(value: bytes) -> str:
    header = f"blob {len(value)}\0".encode("ascii")
    return hashlib.sha1(header + value).hexdigest()


def require_git_checkout(
    root: Path,
    expected_sha: str,
    expected_blobs: dict[str, str] | None = None,
    *,
    label: str,
) -> dict[str, Any]:
    root = root.resolve()
    if not root.is_dir():
        raise PapayaCaptureError(f"{label} checkout not found: {root}")
    try:
        actual_sha = subprocess.check_output(
            ["git", "-C", str(root), "rev-parse", "HEAD"], text=True
        ).strip()
        dirty = subprocess.check_output(
            [
                "git",
                "-C",
                str(root),
                "status",
                "--porcelain=v1",
                "--untracked-files=all",
            ],
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise PapayaCaptureError(f"{label} must be a Git checkout") from exc
    if actual_sha != expected_sha:
        raise PapayaCaptureError(
            f"{label} HEAD mismatch: expected {expected_sha}, got {actual_sha}"
        )
    if dirty:
        raise PapayaCaptureError(f"{label} working tree must be clean")

    observed_blobs: dict[str, str] = {}
    if expected_blobs:
        for relative, expected_blob in expected_blobs.items():
            path = root / relative
            if not path.is_file():
                raise PapayaCaptureError(f"{label} source file missing: {relative}")
            observed = git_blob_sha1_bytes(path.read_bytes())
            if observed != expected_blob:
                raise PapayaCaptureError(
                    f"{label} Git blob mismatch for {relative}: "
                    f"expected {expected_blob}, got {observed}"
                )
            observed_blobs[relative] = observed
    return {
        "checkout_dir_name": root.name,
        "git_sha": actual_sha,
        "clean": True,
        "source_blobs": observed_blobs,
    }


def package_version(name: str) -> str | None:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return None


def require_papaya_import(source_root: Path) -> dict[str, Any]:
    source_root = source_root.resolve()
    expected = (source_root / "src" / "papaya" / "__init__.py").resolve()
    env = child_environment(source_root)
    code = (
        "import pathlib, papaya; "
        "print(pathlib.Path(papaya.__file__).resolve())"
    )
    try:
        proc = subprocess.run(
            [sys.executable, "-c", code],
            cwd=source_root,
            env=env,
            text=True,
            capture_output=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise PapayaCaptureError("cannot verify Papaya import source") from exc
    if proc.returncode != 0:
        raise PapayaCaptureError(
            f"Papaya import check failed: {proc.stderr.strip()}"
        )
    observed = Path(proc.stdout.strip()).resolve()
    if observed != expected:
        raise PapayaCaptureError(
            f"Papaya imported from unexpected path: {observed}"
        )
    return {
        "module_relative_path": "src/papaya/__init__.py",
        "source_checkout_imported": True,
    }


def child_environment(source_root: Path) -> dict[str, str]:
    env = dict(os.environ)
    source_dir = str((source_root / "src").resolve())
    previous = env.get("PYTHONPATH")
    env["PYTHONPATH"] = (
        source_dir if not previous else source_dir + os.pathsep + previous
    )
    env["HF_HUB_OFFLINE"] = "1"
    env["TRANSFORMERS_OFFLINE"] = "1"
    env.pop("PAPAYA_API_KEY", None)
    return env


def require_llama_server(path: Path) -> dict[str, Any]:
    path = path.resolve()
    if not path.is_file():
        raise PapayaCaptureError(f"llama-server not found: {path}")
    digest, size = sha256_file(path)
    if digest != LLAMA_SERVER_SHA256:
        raise PapayaCaptureError(
            f"llama-server SHA-256 mismatch: expected {LLAMA_SERVER_SHA256}, got {digest}"
        )
    env = dict(os.environ)
    binary_dir = str(path.parent)
    env["LD_LIBRARY_PATH"] = (
        binary_dir
        + os.pathsep
        + env.get("LD_LIBRARY_PATH", "")
    )
    try:
        proc = subprocess.run(
            [str(path), "--version"],
            text=True,
            capture_output=True,
            env=env,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise PapayaCaptureError("cannot execute llama-server --version") from exc
    output = (proc.stdout + proc.stderr).strip()
    if proc.returncode != 0:
        raise PapayaCaptureError(
            f"llama-server --version failed with code {proc.returncode}: {output}"
        )
    if LLAMA_VERSION_SUBSTRING not in output:
        raise PapayaCaptureError(
            f"unexpected llama-server version output: {output!r}"
        )
    return {
        "file_name": path.name,
        "sha256": digest,
        "size_bytes": size,
        "release_tag": LLAMA_RELEASE_TAG,
        "source_revision": LLAMA_SOURCE_REVISION,
        "version_output": output,
        "version_verified": True,
        "pin_role": "SEI first Papaya live-run runtime pin; not an upstream Papaya requirement",
        "evidence_path": LLAMA_RUNTIME_EVIDENCE_PATH,
        "evidence_git_blob": LLAMA_RUNTIME_EVIDENCE_BLOB,
    }


def require_sei_evidence_blob(sei_root: Path) -> dict[str, Any]:
    path = sei_root.resolve() / LLAMA_RUNTIME_EVIDENCE_PATH
    if not path.is_file():
        raise PapayaCaptureError(
            f"llama runtime Evidence missing from SEI checkout: {LLAMA_RUNTIME_EVIDENCE_PATH}"
        )
    observed = git_blob_sha1_bytes(path.read_bytes())
    if observed != LLAMA_RUNTIME_EVIDENCE_BLOB:
        raise PapayaCaptureError(
            "llama runtime Evidence Git blob drift: "
            f"expected {LLAMA_RUNTIME_EVIDENCE_BLOB}, got {observed}"
        )
    return {
        "relative_path": LLAMA_RUNTIME_EVIDENCE_PATH,
        "git_blob": observed,
        "binding_verified": True,
    }


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise PapayaCaptureError(f"cannot import module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def load_json(path: Path, label: str) -> tuple[dict[str, Any], bytes]:
    try:
        raw = path.read_bytes()
        value = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PapayaCaptureError(f"cannot read {label}: {path}") from exc
    if not isinstance(value, dict):
        raise PapayaCaptureError(f"{label} root must be an object")
    return value, raw


def verify_overlay(here: Path, overlay_dir: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    module = load_module(
        here / "prepare_papaya_compat_overlay.py",
        "prepare_papaya_compat_overlay_capture",
    )
    try:
        verification = module.verify_prepared_overlay(overlay_dir)
    except Exception as exc:
        raise PapayaCaptureError(f"prepared overlay verification failed: {exc}") from exc
    receipt_path = overlay_dir / "sei_compat_overlay_receipt.json"
    receipt, _raw = load_json(receipt_path, "overlay receipt")
    if receipt.get("schema") != OVERLAY_SCHEMA:
        raise PapayaCaptureError("overlay receipt schema drift")
    runtime = receipt.get("papaya_runtime")
    scope = receipt.get("scope")
    policy = receipt.get("temperature_policy")
    if not isinstance(runtime, dict) or runtime.get("revision") != PAPAYA_SOURCE_REVISION:
        raise PapayaCaptureError("overlay Papaya source revision drift")
    if not isinstance(scope, dict) or scope.get("runtime_source_verified") is not False:
        raise PapayaCaptureError("overlay must not pre-claim runtime source verification")
    if not isinstance(policy, dict) or policy.get("changes") != [EXPECTED_CLAMP_CHANGE]:
        raise PapayaCaptureError("overlay clamp delta drift")
    return verification, receipt


def verify_replay_inputs(
    here: Path, fixture: dict[str, Any]
) -> tuple[dict[str, int], dict[str, Any]]:
    reference, _ = load_json(
        here / "reference_token_fixture.v1.json", "reference token fixture"
    )
    attestation, _ = load_json(
        here / "papaya_candidate_tokenizer_attestation.v1.json",
        "candidate tokenizer attestation",
    )
    replay, _ = load_json(
        here / "papaya_sequence_replay.v1.json", "Papaya sequence replay"
    )
    module = load_module(
        here / "papaya_sequence_replay.py",
        "papaya_sequence_replay_capture",
    )
    try:
        module.validate_papaya_sequence_replay(
            fixture, reference, attestation, replay
        )
    except Exception as exc:
        raise PapayaCaptureError(f"Papaya sequence replay verification failed: {exc}") from exc
    if replay.get("schema") != SEQUENCE_REPLAY_SCHEMA:
        raise PapayaCaptureError("Papaya sequence replay schema drift")
    cases = replay.get("cases")
    if not isinstance(cases, list):
        raise PapayaCaptureError("Papaya sequence replay cases must be an array")
    expected: dict[str, int] = {}
    for case in cases:
        if not isinstance(case, dict):
            raise PapayaCaptureError("invalid Papaya replay case")
        case_id = case.get("case_id")
        token_count = case.get("token_count")
        if not isinstance(case_id, str) or not isinstance(token_count, int):
            raise PapayaCaptureError("invalid Papaya replay case identity/count")
        expected[case_id] = token_count
    return expected, replay


def validate_choice11_diagnostic(
    diagnostic: dict[str, Any], protocol: Any
) -> None:
    protocol.validate_fixture(diagnostic)
    cases = diagnostic.get("cases")
    if not isinstance(cases, list) or len(cases) != 1:
        raise PapayaCaptureError("choice11 diagnostic must contain exactly one case")
    case = cases[0]
    if case.get("case_id") != DIAGNOSTIC_CASE_ID:
        raise PapayaCaptureError("choice11 diagnostic case id drift")
    request = case.get("request")
    if not isinstance(request, dict):
        raise PapayaCaptureError("choice11 diagnostic request must be an object")
    questions = request.get("questions")
    if not isinstance(questions, dict) or set(questions) != {DIAGNOSTIC_QUESTION_ID}:
        raise PapayaCaptureError("choice11 diagnostic question identity drift")
    question = questions[DIAGNOSTIC_QUESTION_ID]
    if question.get("type") != "choice":
        raise PapayaCaptureError("choice11 diagnostic must be a choice question")
    criteria = question.get("criteria")
    if not isinstance(criteria, dict) or len(criteria) != DIAGNOSTIC_OPTION_COUNT:
        raise PapayaCaptureError(
            f"choice11 diagnostic must contain exactly {DIAGNOSTIC_OPTION_COUNT} options"
        )


def free_loopback_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def require_loopback_endpoint(endpoint: str) -> str:
    parsed = urlparse(endpoint)
    if parsed.scheme != "http":
        raise PapayaCaptureError("Papaya capture endpoint must use http")
    if parsed.hostname not in LOOPBACK_HOSTS:
        raise PapayaCaptureError("Papaya capture endpoint must be loopback-only")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise PapayaCaptureError(
            "Papaya capture endpoint must not contain credentials/query/fragment"
        )
    if parsed.path.rstrip("/") != "/v1/systemone":
        raise PapayaCaptureError("Papaya capture endpoint path must be /v1/systemone")
    return endpoint


def read_capped(response: Any) -> bytes:
    raw = response.read(MAX_RESPONSE_BYTES + 1)
    if len(raw) > MAX_RESPONSE_BYTES:
        raise PapayaCaptureError("response exceeds capture limit")
    return raw


def request_bytes(
    url: str,
    method: str,
    body: bytes | None = None,
    timeout: float = 180.0,
) -> tuple[int, dict[str, str], bytes, float]:
    headers = {"Accept": "application/json"}
    if body is not None:
        headers["Content-Type"] = "application/json"
    request = Request(url, data=body, headers=headers, method=method)
    started = time.perf_counter_ns()
    try:
        with urlopen(request, timeout=timeout) as response:
            raw = read_capped(response)
            status = int(response.status)
            response_headers = dict(response.headers.items())
    except HTTPError as exc:
        raw = read_capped(exc)
        status = int(exc.code)
        response_headers = dict(exc.headers.items())
    except (URLError, OSError) as exc:
        raise PapayaCaptureError(f"transport failure: {exc}") from exc
    elapsed_ms = (time.perf_counter_ns() - started) / 1_000_000.0
    return status, response_headers, raw, elapsed_ms


def decode_json(raw: bytes, label: str) -> dict[str, Any]:
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PapayaCaptureError(f"{label} must be UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise PapayaCaptureError(f"{label} must be a JSON object")
    return value


def compact_request(value: dict[str, Any]) -> bytes:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def wait_for_health(
    base_url: str,
    process: subprocess.Popen[Any],
    *,
    timeout: float,
    transport: Callable[..., tuple[int, dict[str, str], bytes, float]] = request_bytes,
) -> dict[str, Any]:
    deadline = time.monotonic() + timeout
    last_error: str | None = None
    while time.monotonic() < deadline:
        code = process.poll()
        if code is not None:
            raise PapayaCaptureError(f"Papaya process exited early with code {code}")
        try:
            status, _headers, raw, latency = transport(
                f"{base_url}/health", "GET", None, min(5.0, timeout)
            )
            payload = decode_json(raw, "Papaya health response")
            if status == 200 and payload.get("status") == "ok":
                return {
                    "http_status": status,
                    "latency_ms": round(latency, 3),
                    "response_sha256": sha256_bytes(raw),
                    "response_utf8": raw.decode("utf-8"),
                }
            last_error = f"HTTP {status}: {payload!r}"
        except Exception as exc:
            last_error = str(exc)
        time.sleep(0.25)
    raise PapayaCaptureError(
        "Papaya endpoint did not become healthy"
        + (f": {last_error}" if last_error else "")
    )


def capture_fixture_cases(
    fixture: dict[str, Any],
    endpoint: str,
    protocol: Any,
    *,
    expected_token_counts: dict[str, int] | None = None,
    transport: Callable[..., tuple[int, dict[str, str], bytes, float]] = request_bytes,
    diagnostic: bool = False,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for case in fixture["cases"]:
        request_value = json.loads(json.dumps(case["request"], ensure_ascii=False))
        request_value["model"] = PAPAYA_RESPONSE_MODEL
        body = compact_request(request_value)
        status, _headers, raw, elapsed_ms = transport(endpoint, "POST", body)
        record: dict[str, Any] = {
            "case_id": case["case_id"],
            "diagnostic": diagnostic,
            "http_status": status,
            "request_sha256": sha256_bytes(body),
            "request_utf8": body.decode("utf-8"),
            "response_sha256": sha256_bytes(raw),
            "response_utf8": raw.decode("utf-8", errors="replace"),
            "round_trip_latency_ms": round(elapsed_ms, 3),
        }
        records.append(record)
        if status != 200:
            raise PapayaCaptureError(f"{case['case_id']}: HTTP {status}")
        response = decode_json(raw, f"{case['case_id']} response")
        protocol.validate_response(request_value, response)
        if response.get("model") != PAPAYA_RESPONSE_MODEL:
            raise PapayaCaptureError(
                f"{case['case_id']}: unexpected Papaya response model "
                f"{response.get('model')!r}"
            )
        usage = response["usage"]["input_tokens"]
        record["response_model"] = response["model"]
        record["input_tokens"] = usage
        record["contract"] = "pass"
        if expected_token_counts is not None:
            expected = expected_token_counts.get(case["case_id"])
            if expected is None:
                raise PapayaCaptureError(
                    f"{case['case_id']}: no retained replay token count"
                )
            if usage != expected:
                raise PapayaCaptureError(
                    f"{case['case_id']}: live input_tokens drift: "
                    f"expected {expected}, got {usage}"
                )
            record["retained_replay_input_tokens"] = expected
            record["live_token_count_matches_replay"] = True
        if diagnostic:
            questions = request_value["questions"]
            question = questions[DIAGNOSTIC_QUESTION_ID]
            record["diagnostic_contract"] = {
                "question_id": DIAGNOSTIC_QUESTION_ID,
                "question_type": "choice",
                "option_count": len(question["criteria"]),
                "temperature_bucket": "choice:11+",
                "compat_temperature": EXPECTED_CLAMP_CHANGE["applied"],
                "expected_answer": None,
                "quality_claim": False,
            }
    return records


def stop_process(process: subprocess.Popen[Any] | None) -> dict[str, Any]:
    if process is None:
        return {"started": False}
    observed_before = process.poll()
    if observed_before is None:
        process.terminate()
        try:
            return_code = process.wait(timeout=15)
        except subprocess.TimeoutExpired:
            process.kill()
            return_code = process.wait(timeout=10)
    else:
        return_code = observed_before
    return {
        "started": True,
        "return_code_before_stop": observed_before,
        "return_code_after_stop": return_code,
    }


def capture_log(path: Path) -> dict[str, Any]:
    digest, size = sha256_file(path)
    with path.open("rb") as f:
        prefix = f.read(MAX_LOG_CAPTURE_BYTES)
    return {
        "size_bytes": size,
        "sha256": digest,
        "captured_prefix_bytes": len(prefix),
        "truncated": size > len(prefix),
        "utf8_prefix": prefix.decode("utf-8", errors="replace"),
    }


def write_artifact(path: Path, artifact: dict[str, Any]) -> None:
    text = json.dumps(artifact, ensure_ascii=False, indent=2) + "\n"
    try:
        with path.open("x", encoding="utf-8") as f:
            f.write(text)
    except FileExistsError as exc:
        raise PapayaCaptureError(f"output already exists: {path}") from exc


def main(argv: list[str] | None = None) -> int:
    here = Path(__file__).resolve().parent
    default_sei_root = here.parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", type=Path, default=here / "fixture.v1.json")
    parser.add_argument(
        "--diagnostic",
        type=Path,
        default=here / "papaya_choice11_diagnostic.v1.json",
    )
    parser.add_argument("--source-git-sha", required=True)
    parser.add_argument("--sei-source-dir", type=Path, default=default_sei_root)
    parser.add_argument("--papaya-source-dir", type=Path, required=True)
    parser.add_argument("--overlay-dir", type=Path, required=True)
    parser.add_argument("--llama-binary", type=Path, required=True)
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--startup-timeout", type=float, default=240.0)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)

    process: subprocess.Popen[Any] | None = None
    artifact: dict[str, Any] | None = None
    failure: Exception | None = None

    try:
        if args.threads < 1:
            raise PapayaCaptureError("threads must be >= 1")
        if args.startup_timeout <= 0:
            raise PapayaCaptureError("startup-timeout must be positive")
        if args.output.exists():
            raise PapayaCaptureError(f"output already exists: {args.output}")

        sei_source = require_git_checkout(
            args.sei_source_dir,
            args.source_git_sha.lower(),
            label="SEI source",
        )
        papaya_source = require_git_checkout(
            args.papaya_source_dir,
            PAPAYA_SOURCE_REVISION,
            PAPAYA_SOURCE_BLOBS,
            label="Papaya source",
        )
        papaya_import = require_papaya_import(args.papaya_source_dir)
        llama_evidence = require_sei_evidence_blob(args.sei_source_dir)
        llama_runtime = require_llama_server(args.llama_binary)
        llama_runtime["evidence_binding"] = llama_evidence

        protocol = load_module(here / "protocol_contract.py", "protocol_contract_papaya_capture")
        fixture, fixture_raw = load_json(args.fixture, "frozen fixture")
        protocol.validate_fixture(fixture)
        expected_token_counts, replay = verify_replay_inputs(here, fixture)

        diagnostic, diagnostic_raw = load_json(args.diagnostic, "choice11 diagnostic")
        validate_choice11_diagnostic(diagnostic, protocol)

        overlay_verification, overlay_receipt = verify_overlay(
            here, args.overlay_dir.resolve()
        )

        port = free_loopback_port()
        base_url = f"http://127.0.0.1:{port}"
        endpoint = require_loopback_endpoint(base_url + "/v1/systemone")

        artifact = {
            "schema": RUN_SCHEMA,
            "status": "incomplete",
            "run_id": args.run_id,
            "source": sei_source,
            "provider": {
                "name": PAPAYA_PROVIDER,
                "identity": PAPAYA_RESPONSE_MODEL,
                "independent_runtime": True,
                "jev_provider_identity": False,
                "python_laya_reference_identity": False,
                "endpoint": endpoint,
            },
            "papaya_runtime": {
                "repository": PAPAYA_SOURCE_REPOSITORY,
                "revision": PAPAYA_SOURCE_REVISION,
                "checkout": papaya_source,
                "import_binding": papaya_import,
                "installed_dependencies": {
                    "numpy": package_version("numpy"),
                    "torch": package_version("torch"),
                    "transformers": package_version("transformers"),
                    "safetensors": package_version("safetensors"),
                    "huggingface_hub": package_version("huggingface-hub"),
                },
                "network_mode": {
                    "HF_HUB_OFFLINE": "1",
                    "TRANSFORMERS_OFFLINE": "1",
                },
            },
            "llama_runtime": llama_runtime,
            "overlay": {
                "verification": overlay_verification,
                "receipt": overlay_receipt,
                "verified_immediately_before_launch": True,
            },
            "fixture": {
                "file": args.fixture.name,
                "schema": fixture.get("schema"),
                "sha256": sha256_bytes(fixture_raw),
                "case_count": len(fixture.get("cases", [])),
                "retained_replay_schema": replay.get("schema"),
            },
            "choice11_diagnostic": {
                "file": args.diagnostic.name,
                "schema": diagnostic.get("schema"),
                "sha256": sha256_bytes(diagnostic_raw),
                "case_count": 1,
                "option_count": DIAGNOSTIC_OPTION_COUNT,
                "temperature_bucket": "choice:11+",
                "compat_temperature": EXPECTED_CLAMP_CHANGE["applied"],
                "expected_answer": None,
                "quality_claim": False,
            },
            "host": {
                "python": platform.python_version(),
                "python_executable_name": Path(sys.executable).name,
                "platform": platform.platform(),
                "threads_requested": args.threads,
            },
            "health": None,
            "frozen_cases": [],
            "diagnostic_cases": [],
            "process": None,
            "logs": {},
            "scope": {
                "papaya_runtime_source_verified": True,
                "papaya_live_inference": False,
                "frozen_protocol_contract": False,
                "frozen_live_token_count_matches_replay": False,
                "choice11_overlay_path_exercised": False,
                "numeric_parity_with_python_laya": False,
                "task_quality": False,
                "calibration_validity": False,
                "jev_provider_identity": False,
                "reference_provider_promotion": False,
            },
        }

        args.output.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(
            prefix=".papaya-live-capture-", dir=args.output.parent
        ) as temp_dir:
            temp_root = Path(temp_dir)
            stdout_path = temp_root / "papaya.stdout.log"
            stderr_path = temp_root / "papaya.stderr.log"
            env = child_environment(args.papaya_source_dir)
            command = [
                sys.executable,
                "-m",
                "papaya.cli",
                "serve",
                "--host",
                "127.0.0.1",
                "--port",
                str(port),
                "--model-dir",
                str(args.overlay_dir.resolve()),
                "--llama-binary",
                str(args.llama_binary.resolve()),
                "--threads",
                str(args.threads),
            ]
            artifact["process"] = {
                "command_shape": [
                    "<capture-python>",
                    "-m",
                    "papaya.cli",
                    "serve",
                    "--host",
                    "127.0.0.1",
                    "--port",
                    "<ephemeral-loopback-port>",
                    "--model-dir",
                    "<verified-overlay-dir>",
                    "--llama-binary",
                    "<verified-llama-server>",
                    "--threads",
                    str(args.threads),
                ],
                "cwd_binding": "verified Papaya source checkout",
                "papaya_api_key_present": False,
                "started": False,
            }
            try:
                with stdout_path.open("wb") as stdout_file, stderr_path.open("wb") as stderr_file:
                    process = subprocess.Popen(
                        command,
                        cwd=args.papaya_source_dir.resolve(),
                        env=env,
                        stdout=stdout_file,
                        stderr=stderr_file,
                    )
                    artifact["process"]["started"] = True

                    artifact["health"] = wait_for_health(
                        base_url,
                        process,
                        timeout=args.startup_timeout,
                    )
                    artifact["frozen_cases"] = capture_fixture_cases(
                        fixture,
                        endpoint,
                        protocol,
                        expected_token_counts=expected_token_counts,
                    )
                    artifact["diagnostic_cases"] = capture_fixture_cases(
                        diagnostic,
                        endpoint,
                        protocol,
                        diagnostic=True,
                    )
                    artifact["scope"]["papaya_live_inference"] = True
                    artifact["scope"]["frozen_protocol_contract"] = True
                    artifact["scope"][
                        "frozen_live_token_count_matches_replay"
                    ] = True
                    artifact["scope"]["choice11_overlay_path_exercised"] = True
                    artifact["status"] = "complete"
            except Exception as exc:
                failure = exc
                artifact["error"] = f"{type(exc).__name__}: {exc}"
            finally:
                artifact["process"]["termination"] = stop_process(process)
                process = None
                artifact["logs"] = {
                    "stdout": capture_log(stdout_path),
                    "stderr": capture_log(stderr_path),
                }

        write_artifact(args.output, artifact)
        if failure is not None:
            raise failure

        print(
            json.dumps(
                {
                    "status": "complete",
                    "run_id": args.run_id,
                    "output": str(args.output),
                    "frozen_cases": len(artifact["frozen_cases"]),
                    "diagnostic_cases": len(artifact["diagnostic_cases"]),
                    "numeric_parity_with_python_laya": False,
                },
                indent=2,
            )
        )
        return 0
    except Exception as exc:
        if process is not None:
            stop_process(process)
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
