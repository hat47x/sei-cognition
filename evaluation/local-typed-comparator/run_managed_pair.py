#!/usr/bin/env python3
"""Run the managed Python-Laya/Papaya pair from one exact SEI revision."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable, Sequence

PAIR_SCHEMA = "sei.local-typed-comparator-managed-pair-run/v1"
PREFLIGHT_SCHEMA = "sei.local-typed-comparator-managed-pair-preflight/v1"
REFERENCE_SCHEMA = "sei.local-typed-comparator-reference-managed-run/v1"
PAPAYA_SCHEMA = "sei.local-typed-comparator-papaya-run/v1"
REPORT_SCHEMA = "sei.local-typed-comparator-cross-provider-numeric-report/v1"
DECISION_SCHEMA = "sei.local-typed-comparator-numeric-parity-decision/v1"

PREFLIGHT_FILE = "pair-preflight.json"
REFERENCE_FILE = "reference-run.json"
PAPAYA_FILE = "papaya-run.json"
REPORT_FILE = "numeric-difference-report.json"
DECISION_FILE = "numeric-parity-decision.json"
RECEIPT_FILE = "pair-run-receipt.json"


class ManagedPairError(ValueError):
    pass


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ManagedPairError(f"cannot read {label}: {path}") from exc
    if not isinstance(value, dict):
        raise ManagedPairError(f"{label} root must be an object")
    return value


def _require_full_sha(value: str) -> str:
    sha = value.lower()
    if len(sha) != 40 or any(c not in "0123456789abcdef" for c in sha):
        raise ManagedPairError(
            "source-git-sha must be a full 40-character hexadecimal SHA"
        )
    return sha


def _is_within(child: Path, parent: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def _require_script_source_binding(here: Path, sei_source_dir: Path) -> Path:
    script_root = here.parents[1].resolve()
    supplied_root = sei_source_dir.expanduser().resolve()
    if script_root != supplied_root:
        raise ManagedPairError(
            "paired-run script checkout must equal --sei-source-dir"
        )
    return script_root


def _require_external_new_output_dir(
    output_dir: Path, *, sei_source_dir: Path, papaya_source_dir: Path
) -> Path:
    resolved = output_dir.expanduser().resolve()
    if resolved.exists():
        raise ManagedPairError(f"output-dir already exists: {resolved}")
    for label, root in (
        ("SEI source", sei_source_dir),
        ("Papaya source", papaya_source_dir),
    ):
        parent = root.expanduser().resolve()
        if resolved == parent or _is_within(resolved, parent):
            raise ManagedPairError(
                f"output-dir must be outside {label}: {resolved}"
            )
    return resolved


def _preflight_summary(path: Path, source_sha: str) -> dict[str, Any]:
    value = _load_json(path, "pair preflight")
    if value.get("schema") != PREFLIGHT_SCHEMA or value.get("status") != "ready":
        raise ManagedPairError("pair preflight must be ready")
    source = value.get("source")
    scope = value.get("scope")
    if not isinstance(source, dict) or source.get("git_sha") != source_sha:
        raise ManagedPairError("pair preflight source Git SHA drift")
    if not isinstance(scope, dict):
        raise ManagedPairError("pair preflight scope missing")
    if scope.get("all_required_inputs_verified") is not True:
        raise ManagedPairError("pair preflight input verification missing")
    wheelhouse = value.get("runtime_wheelhouse")
    if not isinstance(wheelhouse, dict):
        raise ManagedPairError("pair preflight runtime wheelhouse receipt missing")
    wheelhouse_provided = wheelhouse.get("provided")
    if not isinstance(wheelhouse_provided, bool):
        raise ManagedPairError(
            "pair preflight runtime wheelhouse provided flag missing"
        )
    if wheelhouse_provided:
        verification = wheelhouse.get("verification")
        wheel_scope = wheelhouse.get("scope")
        if (
            not isinstance(verification, dict)
            or verification.get("valid") is not True
        ):
            raise ManagedPairError(
                "pair preflight runtime wheelhouse verification missing"
            )
        if not isinstance(wheel_scope, dict):
            raise ManagedPairError(
                "pair preflight runtime wheelhouse scope missing"
            )
        if wheel_scope.get("transport_candidate_only") is not True:
            raise ManagedPairError(
                "pair preflight wheelhouse transport scope drift"
            )
        if wheel_scope.get("host_assisted_transport") is not True:
            raise ManagedPairError(
                "pair preflight wheelhouse host-assisted scope drift"
            )
        if wheel_scope.get("self_contained_wheelhouse") is not False:
            raise ManagedPairError(
                "pair preflight wheelhouse self-contained overclaim"
            )
        if wheel_scope.get("host_dependency_versions_pinned") is not False:
            raise ManagedPairError(
                "pair preflight wheelhouse host dependency pin overclaim"
            )
        if wheel_scope.get("runtime_installation_origin_attested") is not False:
            raise ManagedPairError(
                "pair preflight wheelhouse installation-origin overclaim"
            )
        runtime_environment = wheelhouse.get("runtime_environment")
        if not isinstance(runtime_environment, dict):
            raise ManagedPairError(
                "pair preflight runtime environment receipt missing"
            )
        environment_provided = runtime_environment.get("provided")
        if not isinstance(environment_provided, bool):
            raise ManagedPairError(
                "pair preflight runtime environment provided flag missing"
            )
        transported_origin = wheel_scope.get(
            "transported_wheel_installation_origin_attested"
        )
        if transported_origin is not environment_provided:
            raise ManagedPairError(
                "pair preflight transported-wheel origin scope drift"
            )
        if environment_provided:
            environment_verification = runtime_environment.get("verification")
            if (
                not isinstance(environment_verification, dict)
                or environment_verification.get("valid") is not True
            ):
                raise ManagedPairError(
                    "pair preflight runtime environment verification missing"
                )
            environment_scope = environment_verification.get("scope")
            environment_python = environment_verification.get("python")
            if not isinstance(environment_scope, dict):
                raise ManagedPairError(
                    "pair preflight runtime environment scope missing"
                )
            if not isinstance(environment_python, dict):
                raise ManagedPairError(
                    "pair preflight runtime environment Python receipt missing"
                )
            if (
                environment_scope.get(
                    "transported_wheel_installation_origin_attested"
                )
                is not True
            ):
                raise ManagedPairError(
                    "pair preflight transported-wheel origin attestation missing"
                )
            if (
                environment_scope.get("runtime_installation_origin_attested")
                is not False
            ):
                raise ManagedPairError(
                    "pair preflight runtime environment full-origin overclaim"
                )
            if (
                environment_scope.get("host_dependency_versions_pinned")
                is not False
            ):
                raise ManagedPairError(
                    "pair preflight runtime environment host-pin overclaim"
                )
            if environment_scope.get("self_contained_runtime") is not False:
                raise ManagedPairError(
                    "pair preflight runtime environment self-contained overclaim"
                )
            if environment_scope.get("environment_relocatable") is not False:
                raise ManagedPairError(
                    "pair preflight runtime environment relocatability drift"
                )
            if (
                environment_python.get("current_interpreter_matches")
                is not True
            ):
                raise ManagedPairError(
                    "pair preflight runtime interpreter binding missing"
                )
    else:
        environment_provided = False
    for field in (
        "model_weights_loaded",
        "live_reference_inference",
        "live_papaya_inference",
        "numeric_difference_observed",
        "numeric_parity_decision_observed",
        "task_quality",
        "calibration_validity",
        "shipping_decision",
    ):
        if scope.get(field) is not False:
            raise ManagedPairError(f"pair preflight overclaims {field}")
    return {
        "file": path.name,
        "sha256": _sha256_file(path),
        "schema": PREFLIGHT_SCHEMA,
        "status": "ready",
        "runtime_wheelhouse_provided": wheelhouse_provided,
        "runtime_environment_provided": environment_provided,
        "transported_wheel_installation_origin_attested": (
            environment_provided
        ),
    }


def _artifact_summary(
    path: Path, *, expected_schema: str, source_sha: str, label: str
) -> dict[str, Any]:
    value = _load_json(path, label)
    if value.get("schema") != expected_schema:
        raise ManagedPairError(f"{label} schema drift")
    if value.get("status") != "complete":
        raise ManagedPairError(f"{label} must be complete")
    source = value.get("source")
    if not isinstance(source, dict) or source.get("git_sha") != source_sha:
        raise ManagedPairError(f"{label} source Git SHA drift")
    return {
        "file": path.name,
        "sha256": _sha256_file(path),
        "schema": expected_schema,
        "status": "complete",
    }


def _report_summary(path: Path, source_sha: str) -> dict[str, Any]:
    report = _load_json(path, "numeric report")
    if report.get("schema") != REPORT_SCHEMA:
        raise ManagedPairError("numeric report schema drift")
    inputs = report.get("inputs")
    scope = report.get("scope")
    if (
        not isinstance(inputs, dict)
        or inputs.get("same_sei_source_git_sha") != source_sha
    ):
        raise ManagedPairError("numeric report source Git SHA drift")
    if not isinstance(scope, dict):
        raise ManagedPairError("numeric report scope missing")
    if scope.get("numeric_parity_threshold_defined") is not False:
        raise ManagedPairError("raw numeric report must not define a threshold")
    if scope.get("numeric_parity_decision") is not False:
        raise ManagedPairError("raw numeric report must not contain a decision")
    return {
        "file": path.name,
        "sha256": _sha256_file(path),
        "schema": REPORT_SCHEMA,
        "numeric_parity_threshold_defined": False,
        "numeric_parity_decision": False,
    }


def _decision_summary(
    path: Path,
    *,
    source_sha: str,
    report_sha: str,
    reference_sha: str,
    papaya_sha: str,
) -> dict[str, Any]:
    decision = _load_json(path, "numeric parity decision")
    if decision.get("schema") != DECISION_SCHEMA:
        raise ManagedPairError("numeric parity decision schema drift")
    report = decision.get("numeric_report")
    scope = decision.get("scope")
    if not isinstance(report, dict) or not isinstance(scope, dict):
        raise ManagedPairError("numeric parity decision binding missing")
    if report.get("sha256") != report_sha:
        raise ManagedPairError("numeric parity decision report digest drift")
    if report.get("same_sei_source_git_sha") != source_sha:
        raise ManagedPairError("numeric parity decision source Git SHA drift")
    if report.get("reference_artifact_sha256") != reference_sha:
        raise ManagedPairError("numeric parity decision reference digest drift")
    if report.get("papaya_artifact_sha256") != papaya_sha:
        raise ManagedPairError("numeric parity decision Papaya digest drift")
    result = decision.get("decision")
    if result not in ("pass", "fail"):
        raise ManagedPairError("numeric parity decision must be pass or fail")
    if scope.get("bounded_numeric_parity_on_preregistered_surface") is not (
        result == "pass"
    ):
        raise ManagedPairError("numeric parity decision scope/result drift")
    for field in (
        "task_quality",
        "calibration_validity",
        "cross_runtime_performance_comparison",
        "jev_provider_identity_equivalence",
        "reference_provider_promotion",
        "shipping_decision",
    ):
        if scope.get(field) is not False:
            raise ManagedPairError(f"numeric parity decision overclaims {field}")
    return {
        "file": path.name,
        "sha256": _sha256_file(path),
        "schema": DECISION_SCHEMA,
        "decision": result,
        "failure_count": len(decision.get("failures", [])),
    }


def _write_receipt(path: Path, receipt: dict[str, Any]) -> None:
    temp = path.with_name(path.name + ".tmp")
    temp.write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temp.replace(path)


def _partial_artifact_summary(path: Path) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "file": path.name,
        "present": path.exists(),
    }
    if not path.exists():
        return summary

    try:
        summary["bytes"] = path.stat().st_size
        summary["sha256"] = _sha256_file(path)
        raw = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        summary["readable_utf8"] = False
        return summary

    summary["readable_utf8"] = True
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        summary["json_object"] = False
        return summary
    if not isinstance(value, dict):
        summary["json_object"] = False
        return summary

    summary["json_object"] = True
    for field in ("schema", "status", "run_id"):
        value_field = value.get(field)
        if isinstance(value_field, str):
            summary[field] = value_field
    source = value.get("source")
    if isinstance(source, dict):
        git_sha = source.get("git_sha")
        if isinstance(git_sha, str):
            summary["source_git_sha"] = git_sha
    return summary


def _record_failure(
    *,
    receipt_path: Path,
    receipt: dict[str, Any],
    stage: str,
    kind: str,
    output_path: Path,
    returncode: int | None = None,
    error_type: str | None = None,
) -> None:
    receipt["status"] = "failed"
    if kind == "process_exit":
        receipt["stage"] = f"{stage}_failed"
    elif kind == "runner_exception":
        receipt["stage"] = f"{stage}_launch_failed"
    else:
        receipt["stage"] = f"{stage}_validation_failed"
    failure: dict[str, Any] = {
        "stage": stage,
        "kind": kind,
        "stage_output": _partial_artifact_summary(output_path),
    }
    if returncode is not None:
        failure["returncode"] = returncode
    if error_type is not None:
        failure["error_type"] = error_type
    receipt["failure"] = failure
    _write_receipt(receipt_path, receipt)


def _output_arg(command: Sequence[str]) -> Path:
    try:
        index = command.index("--output")
    except ValueError as exc:
        raise ManagedPairError("internal command missing --output") from exc
    if index + 1 >= len(command):
        raise ManagedPairError("internal command has empty --output")
    return Path(command[index + 1])


def build_commands(
    *,
    python_executable: str,
    here: Path,
    source_sha: str,
    sei_source_dir: Path,
    reference_model_dir: Path,
    laya_runtime_wheel: Path,
    papaya_source_dir: Path,
    papaya_overlay_dir: Path,
    llama_binary: Path,
    output_dir: Path,
    run_id: str,
    threads: int,
    reference_startup_timeout: float,
    papaya_startup_timeout: float,
    runtime_wheelhouse_dir: Path | None = None,
    runtime_environment_dir: Path | None = None,
) -> tuple[list[str], list[str], list[str], list[str], list[str]]:
    preflight_output = output_dir / PREFLIGHT_FILE
    reference_output = output_dir / REFERENCE_FILE
    papaya_output = output_dir / PAPAYA_FILE
    report_output = output_dir / REPORT_FILE
    decision_output = output_dir / DECISION_FILE

    preflight = [
        python_executable,
        str(here / "preflight_managed_pair.py"),
        "--source-git-sha",
        source_sha,
        "--sei-source-dir",
        str(sei_source_dir),
        "--reference-model-dir",
        str(reference_model_dir),
        "--laya-runtime-wheel",
        str(laya_runtime_wheel),
        "--papaya-source-dir",
        str(papaya_source_dir),
        "--papaya-overlay-dir",
        str(papaya_overlay_dir),
        "--llama-binary",
        str(llama_binary),
    ]
    if runtime_environment_dir is not None and runtime_wheelhouse_dir is None:
        raise ManagedPairError(
            "runtime environment requires runtime wheelhouse"
        )
    if runtime_wheelhouse_dir is not None:
        preflight.extend(
            [
                "--runtime-wheelhouse-dir",
                str(runtime_wheelhouse_dir),
            ]
        )
    if runtime_environment_dir is not None:
        preflight.extend(
            [
                "--runtime-environment-dir",
                str(runtime_environment_dir),
            ]
        )
    preflight.extend(
        [
            "--output",
            str(preflight_output),
        ]
    )
    reference = [
        python_executable,
        str(here / "capture_reference_l0.py"),
        "--source-git-sha",
        source_sha,
        "--model-dir",
        str(reference_model_dir),
        "--runtime-wheel",
        str(laya_runtime_wheel),
        "--run-id",
        f"{run_id}-reference",
        "--output",
        str(reference_output),
        "--threads",
        str(threads),
        "--startup-timeout",
        str(reference_startup_timeout),
    ]
    papaya = [
        python_executable,
        str(here / "capture_papaya_l0.py"),
        "--source-git-sha",
        source_sha,
        "--sei-source-dir",
        str(sei_source_dir),
        "--papaya-source-dir",
        str(papaya_source_dir),
        "--overlay-dir",
        str(papaya_overlay_dir),
        "--llama-binary",
        str(llama_binary),
        "--run-id",
        f"{run_id}-papaya",
        "--output",
        str(papaya_output),
        "--threads",
        str(threads),
        "--startup-timeout",
        str(papaya_startup_timeout),
    ]
    compare = [
        python_executable,
        str(here / "compare_papaya_reference_numeric.py"),
        str(reference_output),
        str(papaya_output),
        "--output",
        str(report_output),
    ]
    decide = [
        python_executable,
        str(here / "evaluate_papaya_numeric_parity.py"),
        str(report_output),
        "--output",
        str(decision_output),
    ]
    return preflight, reference, papaya, compare, decide


def execute_pair(
    *,
    source_sha: str,
    output_dir: Path,
    commands: Sequence[tuple[str, Sequence[str]]],
    run_id: str,
    cwd: Path,
    runner: Callable[..., subprocess.CompletedProcess[Any]] = subprocess.run,
) -> dict[str, Any]:
    receipt_path = output_dir / RECEIPT_FILE
    receipt: dict[str, Any] = {
        "schema": PAIR_SCHEMA,
        "status": "incomplete",
        "stage": "initialized",
        "source_git_sha": source_sha,
        "run_id": run_id,
        "run_ids": {
            "reference": f"{run_id}-reference",
            "papaya": f"{run_id}-papaya",
        },
        "artifacts": {},
        "scope": {
            "single_sei_source_git_sha": True,
            "preflight_all_required_inputs_verified": False,
            "transported_wheel_installation_origin_attested": False,
            "provider_provenance_merged": False,
            "raw_comparator_threshold_defined": False,
            "preregistered_numeric_policy_applied": False,
            "task_quality": False,
            "calibration_validity": False,
            "cross_runtime_performance_comparison": False,
            "jev_provider_identity_equivalence": False,
            "reference_provider_promotion": False,
            "shipping_decision": False,
        },
    }
    _write_receipt(receipt_path, receipt)

    for stage, command in commands:
        receipt["stage"] = f"{stage}_running"
        _write_receipt(receipt_path, receipt)
        path = _output_arg(command)
        try:
            completed = runner(list(command), cwd=str(cwd), check=False)
        except Exception as exc:
            _record_failure(
                receipt_path=receipt_path,
                receipt=receipt,
                stage=stage,
                kind="runner_exception",
                output_path=path,
                error_type=type(exc).__name__,
            )
            raise
        if completed.returncode != 0:
            _record_failure(
                receipt_path=receipt_path,
                receipt=receipt,
                stage=stage,
                kind="process_exit",
                output_path=path,
                returncode=completed.returncode,
            )
            raise ManagedPairError(
                f"{stage} stage failed with exit code {completed.returncode}"
            )

        try:
            if stage == "preflight":
                preflight_summary = _preflight_summary(
                    path, source_sha
                )
                receipt["artifacts"]["preflight"] = preflight_summary
                receipt["scope"]["preflight_all_required_inputs_verified"] = True
                receipt["scope"][
                    "transported_wheel_installation_origin_attested"
                ] = preflight_summary[
                    "transported_wheel_installation_origin_attested"
                ]
            elif stage == "reference":
                receipt["artifacts"]["reference"] = _artifact_summary(
                    path,
                    expected_schema=REFERENCE_SCHEMA,
                    source_sha=source_sha,
                    label="reference run",
                )
            elif stage == "papaya":
                receipt["artifacts"]["papaya"] = _artifact_summary(
                    path,
                    expected_schema=PAPAYA_SCHEMA,
                    source_sha=source_sha,
                    label="Papaya run",
                )
            elif stage == "comparison":
                receipt["artifacts"]["comparison"] = _report_summary(
                    path, source_sha
                )
            elif stage == "decision":
                receipt["artifacts"]["decision"] = _decision_summary(
                    path,
                    source_sha=source_sha,
                    report_sha=receipt["artifacts"]["comparison"]["sha256"],
                    reference_sha=receipt["artifacts"]["reference"]["sha256"],
                    papaya_sha=receipt["artifacts"]["papaya"]["sha256"],
                )
                receipt["scope"]["preregistered_numeric_policy_applied"] = True
            else:
                raise ManagedPairError(f"unknown stage: {stage}")
        except Exception as exc:
            _record_failure(
                receipt_path=receipt_path,
                receipt=receipt,
                stage=stage,
                kind="artifact_validation",
                output_path=path,
                error_type=type(exc).__name__,
            )
            raise

        receipt["stage"] = f"{stage}_complete"
        _write_receipt(receipt_path, receipt)

    receipt["status"] = "complete"
    receipt["stage"] = "complete"
    _write_receipt(receipt_path, receipt)
    return receipt


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
    parser.add_argument("--runtime-wheelhouse-dir", type=Path)
    parser.add_argument("--runtime-environment-dir", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--reference-startup-timeout", type=float, default=300.0)
    parser.add_argument("--papaya-startup-timeout", type=float, default=240.0)
    args = parser.parse_args(argv)

    try:
        source_sha = _require_full_sha(args.source_git_sha)
        _require_script_source_binding(here, args.sei_source_dir)
        if (
            args.runtime_environment_dir is not None
            and args.runtime_wheelhouse_dir is None
        ):
            raise ManagedPairError(
                "--runtime-environment-dir requires --runtime-wheelhouse-dir"
            )
        if not args.run_id.strip():
            raise ManagedPairError("run-id must be non-empty")
        if args.threads < 1:
            raise ManagedPairError("threads must be >= 1")
        if (
            args.reference_startup_timeout <= 0
            or args.papaya_startup_timeout <= 0
        ):
            raise ManagedPairError("startup timeouts must be positive")
        output_dir = _require_external_new_output_dir(
            args.output_dir,
            sei_source_dir=args.sei_source_dir,
            papaya_source_dir=args.papaya_source_dir,
        )
        output_dir.mkdir(parents=True)

        preflight, reference, papaya, compare, decide = build_commands(
            python_executable=sys.executable,
            here=here,
            source_sha=source_sha,
            sei_source_dir=args.sei_source_dir.resolve(),
            reference_model_dir=args.reference_model_dir.resolve(),
            laya_runtime_wheel=args.laya_runtime_wheel.resolve(),
            papaya_source_dir=args.papaya_source_dir.resolve(),
            papaya_overlay_dir=args.papaya_overlay_dir.resolve(),
            llama_binary=args.llama_binary.resolve(),
            output_dir=output_dir,
            run_id=args.run_id.strip(),
            threads=args.threads,
            reference_startup_timeout=args.reference_startup_timeout,
            papaya_startup_timeout=args.papaya_startup_timeout,
            runtime_wheelhouse_dir=(
                args.runtime_wheelhouse_dir.resolve()
                if args.runtime_wheelhouse_dir is not None
                else None
            ),
            runtime_environment_dir=(
                args.runtime_environment_dir.resolve()
                if args.runtime_environment_dir is not None
                else None
            ),
        )
        receipt = execute_pair(
            source_sha=source_sha,
            output_dir=output_dir,
            commands=(
                ("preflight", preflight),
                ("reference", reference),
                ("papaya", papaya),
                ("comparison", compare),
                ("decision", decide),
            ),
            run_id=args.run_id.strip(),
            cwd=args.sei_source_dir.resolve(),
        )
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(
        json.dumps(
            {
                "status": receipt["status"],
                "output_dir": str(output_dir),
                "receipt": RECEIPT_FILE,
                "numeric_parity_decision": receipt["artifacts"]["decision"][
                    "decision"
                ],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
