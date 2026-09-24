#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

MATRIX_SCHEMA = "sei-cognition.local-model-matrix-run/v1"
PAIR_SCHEMA = "sei-cognition.local-model-compute-pair-verification/v1"
MODES = ("raw", "workspace", "staged")


def load_matrix(path):
    with open(path, encoding="utf-8") as f:
        value = json.load(f)
    if not isinstance(value, dict):
        raise ValueError(f"matrix must be a JSON object: {path}")
    return value


def fixture_ids(matrix, mode):
    artifact = matrix.get(mode) or {}
    telemetry = artifact.get("telemetry") or {}
    observations = telemetry.get("observations") or []
    return sorted(item.get("fixture_id", "") for item in observations)


def validate_pair(cpu, gpu, cpu_layers, gpu_layers):
    if cpu.get("schema") != MATRIX_SCHEMA or gpu.get("schema") != MATRIX_SCHEMA:
        raise ValueError("both inputs must use the current matrix schema")
    if cpu.get("status") != "complete" or gpu.get("status") != "complete":
        raise ValueError("both inputs must be complete matrices")
    if cpu_layers != 0:
        raise ValueError(f"CPU run requested GPU offload: {cpu_layers}")
    if gpu_layers <= 0:
        raise ValueError("GPU run must record positive gpu_layers_requested")
    if cpu.get("source_git_sha") != gpu.get("source_git_sha"):
        raise ValueError("source_git_sha mismatch")
    if cpu.get("model") != gpu.get("model"):
        raise ValueError("model identifier mismatch")

    ca, ga = cpu.get("model_artifact") or {}, gpu.get("model_artifact") or {}
    if ca.get("status") != "observed" or ga.get("status") != "observed":
        raise ValueError("both runs require observed model artifact identity")
    if (ca.get("sha256"), ca.get("size_bytes")) != (ga.get("sha256"), ga.get("size_bytes")):
        raise ValueError("model artifact identity mismatch")

    ch, gh = cpu.get("host") or {}, gpu.get("host") or {}
    if tuple(ch.get(k) for k in ("os", "arch", "go_version")) != tuple(gh.get(k) for k in ("os", "arch", "go_version")):
        raise ValueError("host software identity mismatch")

    cp, gp = cpu.get("preflights") or [], gpu.get("preflights") or []
    if len(cp) != 3 or len(gp) != 3:
        raise ValueError("both matrices require three preflights")
    keys = ("runtime_name", "runtime_version", "quantization", "context_size", "threads", "fixture", "mode")
    for index, (left, right) in enumerate(zip(cp, gp)):
        if tuple(left.get(k) for k in keys) != tuple(right.get(k) for k in keys):
            raise ValueError(f"preflight {index} identity/config mismatch")

    for mode in MODES:
        if fixture_ids(cpu, mode) != fixture_ids(gpu, mode):
            raise ValueError(f"{mode} fixture set mismatch")
    if not isinstance(cpu.get("comparison"), dict) or not isinstance(gpu.get("comparison"), dict):
        raise ValueError("both matrices require comparison evidence")


def build_report(cpu, gpu, cpu_layers, gpu_layers):
    cfg = cpu["preflights"][0]
    modes = []
    for mode in MODES:
        ca = cpu["comparison"].get(mode) or {}
        ga = gpu["comparison"].get(mode) or {}
        cpu_latency = ca.get("total_latency_ms", 0)
        gpu_latency = ga.get("total_latency_ms", 0)
        modes.append({
            "mode": mode,
            "cpu_total_latency_ms": cpu_latency,
            "gpu_total_latency_ms": gpu_latency,
            "gpu_minus_cpu_total_latency_ms": gpu_latency - cpu_latency,
            "cpu_first_token_latency_ms_mean": ca.get("first_token_latency_ms_mean", 0),
            "gpu_first_token_latency_ms_mean": ga.get("first_token_latency_ms_mean", 0),
            "cpu_total_tokens": ca.get("total_tokens", 0),
            "gpu_total_tokens": ga.get("total_tokens", 0),
        })
    return {
        "schema": PAIR_SCHEMA,
        "status": "comparable-complete-pair",
        "source_git_sha": cpu["source_git_sha"],
        "model": cpu["model"],
        "model_artifact": cpu["model_artifact"],
        "runtime_name": cfg.get("runtime_name", ""),
        "runtime_version": cfg.get("runtime_version", ""),
        "quantization": cfg.get("quantization", ""),
        "context_size": cfg.get("context_size", 0),
        "threads": cfg.get("threads", 0),
        "cpu_host": cpu.get("host", {}),
        "gpu_host": gpu.get("host", {}),
        "cpu_gpu_layers_requested": cpu_layers,
        "gpu_gpu_layers_requested": gpu_layers,
        "modes": modes,
        "notes": [
            "pair comparability requires matching source/model/runtime/config/fixture identity",
            "gpu_layers_requested is an operator request, not proof of observed CUDA offload",
            "logical CPU count may differ and remains visible execution-environment evidence",
            "latency deltas are descriptive evidence, not a deployment recommendation",
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cpu", required=True)
    parser.add_argument("--gpu", required=True)
    parser.add_argument("--cpu-gpu-layers-requested", type=int, default=0)
    parser.add_argument("--gpu-gpu-layers-requested", type=int, required=True)
    parser.add_argument("--output")
    args = parser.parse_args()

    cpu, gpu = load_matrix(args.cpu), load_matrix(args.gpu)
    validate_pair(cpu, gpu, args.cpu_gpu_layers_requested, args.gpu_gpu_layers_requested)
    report = build_report(cpu, gpu, args.cpu_gpu_layers_requested, args.gpu_gpu_layers_requested)
    text = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        Path(args.output).open("x", encoding="utf-8").write(text)
    else:
        print(text, end="")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise SystemExit(str(exc))
