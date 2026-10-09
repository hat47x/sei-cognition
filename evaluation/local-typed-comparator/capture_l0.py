#!/usr/bin/env python3
"""Capture one exact local Laya L0 run against the frozen typed comparator fixture."""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import importlib.util
import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

RUN_SCHEMA = "sei.local-typed-comparator-run/v1alpha1"
DEFAULT_ENDPOINT = "http://127.0.0.1:8000/v1/systemone"
PINNED_MODEL_REPOSITORY = "convaiinnovations/laya-typed-decisions"
PINNED_REQUEST_MODEL = "convaiinnovations/laya-typed-decisions"
PINNED_LOGICAL_MODEL = "typed-decisions"
PINNED_RESPONSE_MODEL = "laya-rl-agent"
PINNED_HUB_REVISION = "f9ab0b228f0fc0f14d873dbc99038f135c2da1b2"
PINNED_MODEL_SHA256 = "4fa56de72383a9d3efa9cfa78955733c81b9fc8067a587ca4beb82c78107a24e"
PINNED_MODEL_SIZE = 842_609_220
PINNED_LAYA_VERSION = "0.3.20"
PINNED_LAYA_SOURCE_REVISION = "23a17522aa4942da6cce53a995a275760320b691"
PINNED_LAYA_WHEEL_SHA256 = "6039e802fa5effb8dd492061cd7ad39a43087beadc4a4fa4a649614e77eb83d4"
MAX_RESPONSE_BYTES = 2 * 1024 * 1024
LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}


class CaptureError(ValueError):
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


def require_pinned_artifact(
    path: Path, expected_sha256: str, expected_size: int | None, label: str
) -> dict[str, Any]:
    if not path.is_file():
        raise CaptureError(f"{label} not found: {path}")
    digest, size = sha256_file(path)
    if digest != expected_sha256:
        raise CaptureError(f"{label} sha256 mismatch: {digest}")
    if expected_size is not None and size != expected_size:
        raise CaptureError(f"{label} size mismatch: {size}")
    return {"file": path.name, "sha256": digest, "size_bytes": size}


def require_local_endpoint(endpoint: str) -> str:
    parsed = urlparse(endpoint)
    if parsed.scheme != "http":
        raise CaptureError("endpoint must use http for this loopback-only capture")
    if parsed.hostname not in LOOPBACK_HOSTS:
        raise CaptureError(
            "endpoint must be loopback-only (127.0.0.1, localhost, or ::1)"
        )
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise CaptureError("endpoint must not contain credentials, query, or fragment")
    if parsed.path.rstrip("/") != "/v1/systemone":
        raise CaptureError("endpoint path must be /v1/systemone")
    return endpoint


def health_url(endpoint: str) -> str:
    parsed = urlparse(endpoint)
    host = parsed.hostname or ""
    if ":" in host and not host.startswith("["):
        host = f"[{host}]"
    authority = host if parsed.port is None else f"{host}:{parsed.port}"
    return f"http://{authority}/health"


def serialize_request(value: dict[str, Any]) -> bytes:
    # Do not sort keys: Choice criteria order is part of the frozen perturbation pair.
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def read_capped(response: Any) -> bytes:
    raw = response.read(MAX_RESPONSE_BYTES + 1)
    if len(raw) > MAX_RESPONSE_BYTES:
        raise CaptureError("response exceeds capture limit")
    return raw


def request_bytes(
    url: str,
    method: str,
    body: bytes | None = None,
    api_key: str | None = None,
    timeout: float = 120.0,
) -> tuple[int, dict[str, str], bytes, float]:
    headers = {"Accept": "application/json"}
    if body is not None:
        headers["Content-Type"] = "application/json"
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    req = Request(url, data=body, headers=headers, method=method)
    start = time.perf_counter_ns()
    try:
        with urlopen(req, timeout=timeout) as response:
            raw = read_capped(response)
            status = int(response.status)
            response_headers = {k: v for k, v in response.headers.items()}
    except HTTPError as exc:
        raw = read_capped(exc)
        status = int(exc.code)
        response_headers = {k: v for k, v in exc.headers.items()}
    except (URLError, OSError) as exc:
        raise CaptureError(f"transport failure: {exc}") from exc
    elapsed_ms = (time.perf_counter_ns() - start) / 1_000_000.0
    return status, response_headers, raw, elapsed_ms


def decode_json(raw: bytes, label: str) -> dict[str, Any]:
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CaptureError(f"{label} must be valid UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise CaptureError(f"{label} must be a JSON object")
    return value


def provider_inference_ms(headers: dict[str, str]) -> float | None:
    raw = next(
        (v for k, v in headers.items() if k.lower() == "x-inference-time-ms"),
        None,
    )
    if raw is None:
        return None
    try:
        value = float(raw)
    except ValueError:
        return None
    return value if value >= 0 else None


def package_version(distribution: str) -> str | None:
    try:
        return importlib.metadata.version(distribution)
    except importlib.metadata.PackageNotFoundError:
        return None


def capture_health(
    endpoint: str,
    transport: Callable[..., tuple[int, dict[str, str], bytes, float]] = request_bytes,
    api_key: str | None = None,
) -> dict[str, Any]:
    status, _headers, raw, elapsed_ms = transport(
        health_url(endpoint), "GET", None, api_key
    )
    parsed = decode_json(raw, "health response")
    if status != 200 or parsed.get("status") != "ok":
        raise CaptureError(f"health check failed with HTTP {status}")
    loaded = parsed.get("loaded")
    if not isinstance(loaded, list) or PINNED_LOGICAL_MODEL not in loaded:
        raise CaptureError(
            "health response does not report the pinned logical checkpoint as loaded"
        )
    return {
        "http_status": status,
        "latency_ms": round(elapsed_ms, 3),
        "response_sha256": sha256_bytes(raw),
        "response_utf8": raw.decode("utf-8"),
        "loaded": loaded,
        "device": parsed.get("device"),
    }


def capture_cases(
    fixture: dict[str, Any],
    endpoint: str,
    model: str,
    validate_response: Callable[[dict[str, Any], dict[str, Any]], None],
    transport: Callable[..., tuple[int, dict[str, str], bytes, float]] = request_bytes,
    api_key: str | None = None,
    records: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    if records is None:
        records = []
    for case in fixture["cases"]:
        request_value = json.loads(json.dumps(case["request"], ensure_ascii=False))
        request_value["model"] = model
        body = serialize_request(request_value)
        status, headers, raw, elapsed_ms = transport(
            endpoint, "POST", body, api_key
        )
        record: dict[str, Any] = {
            "case_id": case["case_id"],
            "http_status": status,
            "request_sha256": sha256_bytes(body),
            "request_utf8": body.decode("utf-8"),
            "response_sha256": sha256_bytes(raw),
            "response_utf8": raw.decode("utf-8", errors="replace"),
            "round_trip_latency_ms": round(elapsed_ms, 3),
            "provider_inference_time_ms": provider_inference_ms(headers),
        }
        records.append(record)
        if status != 200:
            raise CaptureError(f"{case['case_id']}: HTTP {status}")
        response_value = decode_json(raw, f"{case['case_id']} response")
        validate_response(request_value, response_value)
        response_model = response_value.get("model")
        if response_model != PINNED_RESPONSE_MODEL:
            raise CaptureError(
                f"{case['case_id']}: unexpected response model: {response_model!r}"
            )
        routing = response_value.get("routing")
        if not isinstance(routing, dict) or routing.get("model") != PINNED_LOGICAL_MODEL:
            raise CaptureError(
                f"{case['case_id']}: endpoint did not report routing through "
                f"{PINNED_LOGICAL_MODEL!r}"
            )
        record["response_model"] = response_model
        record["routing_model"] = routing["model"]
        record["contract"] = "pass"
    return records


def require_clean_source(expected_sha: str) -> dict[str, str]:
    if len(expected_sha) != 40 or any(
        c not in "0123456789abcdef" for c in expected_sha.lower()
    ):
        raise CaptureError(
            "source_git_sha must be a full 40-character hexadecimal SHA"
        )
    try:
        root = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"], text=True
        ).strip()
        actual = subprocess.check_output(
            ["git", "-C", root, "rev-parse", "HEAD"], text=True
        ).strip()
        dirty = subprocess.check_output(
            [
                "git",
                "-C",
                root,
                "status",
                "--porcelain=v1",
                "--untracked-files=all",
            ],
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise CaptureError("capture must run from a Git working tree") from exc
    if actual != expected_sha:
        raise CaptureError(
            f"source HEAD mismatch: expected {expected_sha}, observed {actual}"
        )
    if dirty:
        raise CaptureError("source working tree must be clean before capture")
    return {"git_sha": actual}


def load_protocol_module(directory: Path):
    path = directory / "protocol_contract.py"
    spec = importlib.util.spec_from_file_location("protocol_contract", path)
    if spec is None or spec.loader is None:
        raise CaptureError(f"cannot import protocol contract: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_artifact(path: Path, artifact: dict[str, Any]) -> None:
    text = json.dumps(artifact, indent=2, ensure_ascii=False) + "\n"
    try:
        with path.open("x", encoding="utf-8") as f:
            f.write(text)
    except FileExistsError as exc:
        raise CaptureError(f"output already exists: {path}") from exc


def main(argv: list[str] | None = None) -> int:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", type=Path, default=here / "fixture.v1.json")
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--source-git-sha", required=True)
    parser.add_argument("--model-artifact", type=Path, required=True)
    parser.add_argument("--runtime-wheel", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)

    try:
        endpoint = require_local_endpoint(args.endpoint)
        if args.output.exists():
            raise CaptureError(f"output already exists: {args.output}")
        source = require_clean_source(args.source_git_sha.lower())
        model_artifact = require_pinned_artifact(
            args.model_artifact,
            PINNED_MODEL_SHA256,
            PINNED_MODEL_SIZE,
            "model artifact",
        )
        runtime_artifact = require_pinned_artifact(
            args.runtime_wheel,
            PINNED_LAYA_WHEEL_SHA256,
            None,
            "laya runtime wheel",
        )
        try:
            observed_laya_version = importlib.metadata.version("laya")
        except importlib.metadata.PackageNotFoundError as exc:
            raise CaptureError(
                "laya is not installed in the capture interpreter"
            ) from exc
        if observed_laya_version != PINNED_LAYA_VERSION:
            raise CaptureError(
                "laya version mismatch: "
                f"expected {PINNED_LAYA_VERSION}, observed {observed_laya_version}"
            )

        protocol = load_protocol_module(here)
        fixture_raw = args.fixture.read_bytes()
        fixture = json.loads(fixture_raw.decode("utf-8"))
        protocol.validate_fixture(fixture)
        api_key = os.environ.get("LAYA_API_KEY") or None

        artifact: dict[str, Any] = {
            "schema": RUN_SCHEMA,
            "status": "incomplete",
            "run_id": args.run_id,
            "source": source,
            "provider": {
                "name": "laya",
                "endpoint": endpoint,
                "pypi_source_revision": PINNED_LAYA_SOURCE_REVISION,
                "runtime_wheel": runtime_artifact,
                "capture_interpreter": {
                    "laya_version": observed_laya_version,
                    "dependencies": {
                        "torch": package_version("torch"),
                        "transformers": package_version("transformers"),
                        "safetensors": package_version("safetensors"),
                        "huggingface_hub": package_version("huggingface_hub"),
                        "numpy": package_version("numpy"),
                        "fastapi": package_version("fastapi"),
                        "uvicorn": package_version("uvicorn"),
                    },
                },
                "runtime_binding": {
                    "supplied_runtime_wheel_digest_verified": True,
                    "capture_interpreter_exact_wheel_attested": False,
                    "endpoint_exact_runtime_wheel_attested": False,
                    "note": (
                        "The capture verifies supplied wheel bytes and observes the "
                        "capture interpreter package version separately. Laya 0.3.20 "
                        "HTTP health/response metadata do not attest endpoint wheel bytes."
                    ),
                },
            },
            "checkpoint": {
                "repository": PINNED_MODEL_REPOSITORY,
                "request_model": PINNED_REQUEST_MODEL,
                "logical_model": PINNED_LOGICAL_MODEL,
                "hub_revision": PINNED_HUB_REVISION,
                "model_artifact": model_artifact,
                "runtime_binding": {
                    "logical_checkpoint_observed": False,
                    "exact_artifact_bytes_attested_by_endpoint": False,
                    "note": (
                        "Laya 0.3.20 health/routing surfaces expose logical "
                        "checkpoint identity but not the loaded model-file digest"
                    ),
                },
            },
            "fixture": {
                "file": args.fixture.name,
                "schema": fixture.get("schema"),
                "sha256": sha256_bytes(fixture_raw),
                "case_count": len(fixture.get("cases", [])),
            },
            "host": {
                "python": platform.python_version(),
                "platform": platform.platform(),
            },
            "auth": {"bearer_present": bool(api_key)},
            "health": None,
            "cases": [],
        }
        try:
            artifact["health"] = capture_health(endpoint, api_key=api_key)
            capture_cases(
                fixture,
                endpoint,
                PINNED_REQUEST_MODEL,
                protocol.validate_response,
                api_key=api_key,
                records=artifact["cases"],
            )
            artifact["checkpoint"]["runtime_binding"][
                "logical_checkpoint_observed"
            ] = True
            artifact["status"] = "complete"
        except Exception as exc:
            artifact["error"] = f"{type(exc).__name__}: {exc}"
            write_artifact(args.output, artifact)
            raise

        write_artifact(args.output, artifact)
        print(
            json.dumps(
                {
                    "status": "complete",
                    "run_id": args.run_id,
                    "output": str(args.output),
                },
                indent=2,
            )
        )
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
