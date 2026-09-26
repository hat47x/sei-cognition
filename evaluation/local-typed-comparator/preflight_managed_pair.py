#!/usr/bin/env python3
"""Verify all managed pair inputs before either provider loads model weights."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Callable

SCHEMA = "sei.local-typed-comparator-managed-pair-preflight/v1"
FIXTURE_SHA256 = "cb070bfa342a2ca7329538620541fa32588130d3d1b67f21c8b3c4e3494d8ed5"
CHOICE11_DIAGNOSTIC_SHA256 = (
    "6c572390e91d662864d9ef2b43cd147e698773649531e798a3a55179e35a5a32"
)


class PairPreflightError(ValueError):
    pass


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise PairPreflightError(f"cannot import module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _load_json(path: Path, label: str) -> tuple[dict[str, Any], bytes]:
    try:
        raw = path.read_bytes()
        value = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PairPreflightError(f"cannot read {label}: {path}") from exc
    if not isinstance(value, dict):
        raise PairPreflightError(f"{label} root must be an object")
    return value, raw


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _full_sha(value: str) -> str:
    sha = value.lower()
    if len(sha) != 40 or any(c not in "0123456789abcdef" for c in sha):
        raise PairPreflightError(
            "source-git-sha must be a full 40-character hexadecimal SHA"
        )
    return sha


def _require_script_source_binding(here: Path, sei_source_dir: Path) -> Path:
    script_root = here.parents[1].resolve()
    supplied_root = sei_source_dir.expanduser().resolve()
    if script_root != supplied_root:
        raise PairPreflightError(
            "preflight script checkout must equal --sei-source-dir"
        )
    return script_root


def _external_output(
    path: Path, *, sei_source_dir: Path, papaya_source_dir: Path
) -> Path:
    resolved = path.expanduser().resolve()
    if resolved.exists():
        raise PairPreflightError(f"output already exists: {resolved}")
    for label, root in (
        ("SEI source", sei_source_dir),
        ("Papaya source", papaya_source_dir),
    ):
        parent = root.expanduser().resolve()
        try:
            resolved.relative_to(parent)
        except ValueError:
            continue
        raise PairPreflightError(f"output must be outside {label}: {resolved}")
    return resolved


def _write_atomic(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".tmp")
    temp.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temp.replace(path)


def run_preflight(
    *,
    here: Path,
    source_sha: str,
    sei_source_dir: Path,
    reference_model_dir: Path,
    laya_runtime_wheel: Path,
    papaya_source_dir: Path,
    papaya_overlay_dir: Path,
    llama_binary: Path,
    loader: Callable[[Path, str], Any] = _load_module,
) -> dict[str, Any]:
    source_sha = _full_sha(source_sha)
    reference = loader(here / "capture_reference_l0.py", "pair_preflight_reference")
    papaya = loader(here / "capture_papaya_l0.py", "pair_preflight_papaya")
    verifier = loader(
        here / "verify_reference_model_directory.py",
        "pair_preflight_reference_model",
    )
    protocol = loader(here / "protocol_contract.py", "pair_preflight_protocol")
    token_verifier = loader(
        here / "reference_token_fixture.py",
        "pair_preflight_reference_tokens",
    )
    choice11 = loader(
        here / "choice11_sequence_attestation.py",
        "pair_preflight_choice11",
    )
    parity = loader(
        here / "evaluate_papaya_numeric_parity.py",
        "pair_preflight_parity_policy",
    )

    sei = papaya.require_git_checkout(
        sei_source_dir, source_sha, label="SEI source"
    )
    if sei.get("git_sha") != source_sha or sei.get("clean") is not True:
        raise PairPreflightError("SEI source checkout receipt drift")

    wheel = reference.require_pinned_file(
        laya_runtime_wheel,
        expected_sha256=reference.PINNED_LAYA_WHEEL_SHA256,
        expected_size=reference.PINNED_LAYA_WHEEL_SIZE,
        label="Laya runtime wheel",
    )
    reference_dependencies = reference.require_runtime_dependencies()

    model_attestation, _ = _load_json(
        here / "reference_model_directory_attestation.v1.json",
        "reference model attestation",
    )
    verifier.validate_attestation(model_attestation)
    model = verifier.verify_model_directory(reference_model_dir)
    if model.get("valid") is not True:
        raise PairPreflightError("reference model-directory verification failed")

    fixture, fixture_raw = _load_json(here / "fixture.v1.json", "frozen fixture")
    protocol.validate_fixture(fixture)
    fixture_sha = _sha256(fixture_raw)
    if fixture_sha != FIXTURE_SHA256:
        raise PairPreflightError("frozen fixture SHA-256 drift")

    token_packet, _ = _load_json(
        here / "reference_token_fixture.v1.json", "reference token fixture"
    )
    token_verifier.validate_reference_token_fixture(fixture, token_packet)
    reference_counts = reference.expected_token_counts(token_packet)

    diagnostic, diagnostic_raw = _load_json(
        here / "papaya_choice11_diagnostic.v1.json", "choice11 diagnostic"
    )
    diagnostic_sha = _sha256(diagnostic_raw)
    if diagnostic_sha != CHOICE11_DIAGNOSTIC_SHA256:
        raise PairPreflightError("choice11 diagnostic SHA-256 drift")
    reference.validate_choice11_diagnostic(diagnostic, protocol)
    papaya.validate_choice11_diagnostic(diagnostic, protocol)

    choice_packet, _ = _load_json(
        here / "choice11_sequence_attestation.v1.json",
        "choice11 sequence attestation",
    )
    choice11.validate_choice11_sequence(
        diagnostic, choice_packet, fixture_raw=diagnostic_raw
    )

    policy, policy_raw = _load_json(
        here / "papaya_numeric_parity_policy.v1.json",
        "numeric parity policy",
    )
    parity._validate_policy(policy)

    papaya_source = papaya.require_git_checkout(
        papaya_source_dir,
        papaya.PAPAYA_SOURCE_REVISION,
        papaya.PAPAYA_SOURCE_BLOBS,
        label="Papaya source",
    )
    papaya_dependencies = papaya.require_runtime_dependencies()
    papaya_import = papaya.require_papaya_import(papaya_source_dir)
    llama_evidence = papaya.require_sei_evidence_blob(sei_source_dir)
    llama_runtime = papaya.require_llama_server(llama_binary)
    overlay_verification, overlay_receipt = papaya.verify_overlay(
        here, papaya_overlay_dir.resolve()
    )
    replay_counts, replay = papaya.verify_replay_inputs(here, fixture)
    if replay_counts != reference_counts:
        raise PairPreflightError(
            "reference/Papaya frozen token-count maps diverge"
        )

    return {
        "schema": SCHEMA,
        "status": "ready",
        "source": {
            "git_sha": source_sha,
            "clean": True,
        },
        "reference": {
            "runtime_wheel": wheel,
            "runtime_dependencies": reference_dependencies,
            "model_directory": model,
            "model_attestation_schema": model_attestation.get("schema"),
        },
        "papaya": {
            "source": papaya_source,
            "runtime_dependencies": papaya_dependencies,
            "import_binding": papaya_import,
            "llama_runtime": llama_runtime,
            "llama_evidence": llama_evidence,
            "overlay": {
                "verification": overlay_verification,
                "receipt_schema": overlay_receipt.get("schema"),
            },
        },
        "contracts": {
            "fixture_sha256": fixture_sha,
            "reference_token_fixture_schema": token_packet.get("schema"),
            "frozen_token_counts": reference_counts,
            "papaya_sequence_replay_schema": replay.get("schema"),
            "choice11_diagnostic_sha256": diagnostic_sha,
            "choice11_sequence_attestation_schema": choice_packet.get("schema"),
            "numeric_parity_policy_sha256": _sha256(policy_raw),
            "numeric_parity_policy_schema": policy.get("schema"),
        },
        "scope": {
            "all_required_inputs_verified": True,
            "model_weights_loaded": False,
            "live_reference_inference": False,
            "live_papaya_inference": False,
            "numeric_difference_observed": False,
            "numeric_parity_decision_observed": False,
            "task_quality": False,
            "calibration_validity": False,
            "shipping_decision": False,
        },
    }


def main(argv: list[str] | None = None) -> int:
    here = Path(__file__).resolve().parent
    default_sei_root = here.parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-git-sha", required=True)
    parser.add_argument("--sei-source-dir", type=Path, default=default_sei_root)
    parser.add_argument("--reference-model-dir", type=Path, required=True)
    parser.add_argument("--laya-runtime-wheel", type=Path, required=True)
    parser.add_argument("--papaya-source-dir", type=Path, required=True)
    parser.add_argument("--papaya-overlay-dir", type=Path, required=True)
    parser.add_argument("--llama-binary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)

    try:
        _require_script_source_binding(here, args.sei_source_dir)
        output = _external_output(
            args.output,
            sei_source_dir=args.sei_source_dir,
            papaya_source_dir=args.papaya_source_dir,
        )
        receipt = run_preflight(
            here=here,
            source_sha=args.source_git_sha,
            sei_source_dir=args.sei_source_dir.resolve(),
            reference_model_dir=args.reference_model_dir.resolve(),
            laya_runtime_wheel=args.laya_runtime_wheel.resolve(),
            papaya_source_dir=args.papaya_source_dir.resolve(),
            papaya_overlay_dir=args.papaya_overlay_dir.resolve(),
            llama_binary=args.llama_binary.resolve(),
        )
        _write_atomic(output, receipt)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(
        json.dumps(
            {
                "status": "ready",
                "source_git_sha": receipt["source"]["git_sha"],
                "output": str(output),
                "model_weights_loaded": False,
                "live_inference": False,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
