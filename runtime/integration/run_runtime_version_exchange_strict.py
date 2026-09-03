#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from pathlib import Path

from export_kj_atlas_runtime_source import export_runtime_bundle
from verify_kj_atlas_runtime_source import verify_runtime_bundle
from verify_runtime_version_exchange_model_store import verify_model_store


INTEGRATION_DIR = Path(__file__).resolve().parent
HARNESS = INTEGRATION_DIR / "run_runtime_version_exchange.sh"


def _reject_forwarded_identity_options(arguments: list[str]) -> None:
    forbidden = {
        "--kj-atlas-dir",
        "--kj-atlas-backend-bundle",
        "--model-dir",
        "--evidence-dir",
        "--work-dir",
    }
    for argument in arguments:
        if argument in forbidden or any(argument.startswith(name + "=") for name in forbidden):
            raise ValueError(
                "strict Evidenceのidentity / safety optionはこのentrypoint側で確定します。"
                f"harnessへ直接渡せません: {argument}"
            )


def _new_path(path: Path, label: str) -> Path:
    resolved = path.expanduser().resolve(strict=False)
    if resolved.exists():
        raise ValueError(f"{label}は新しいpathを指定してください: {resolved}")
    return resolved


def _is_within(candidate: Path, root: Path) -> bool:
    return candidate == root or root in candidate.parents


def _reject_overlap(candidate: Path, candidate_label: str, roots: tuple[tuple[str, Path], ...]) -> None:
    for root_label, root in roots:
        if _is_within(candidate, root):
            raise ValueError(
                f"{candidate_label}を{root_label}配下には置けません: "
                f"candidate={candidate} root={root}"
            )
        if _is_within(root, candidate):
            raise ValueError(
                f"{candidate_label}で{root_label}を包含できません: "
                f"candidate={candidate} root={root}"
            )


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )


def run_strict_probe(
    *,
    checkout_dir: Path | None,
    backend_bundle: Path | None,
    model_dir: Path | None,
    evidence_dir: Path,
    harness_arguments: list[str],
    work_dir: Path | None = None,
) -> int:
    _reject_forwarded_identity_options(harness_arguments)

    if (checkout_dir is None) == (backend_bundle is None):
        raise ValueError("--kj-atlas-dirまたは--kj-atlas-backend-bundleのどちらか一方を指定してください")

    if checkout_dir is not None:
        source_input = checkout_dir.expanduser().resolve(strict=True)
        source_label = "KJ Atlas checkout"
    else:
        assert backend_bundle is not None
        source_input = backend_bundle.expanduser().resolve(strict=True)
        source_label = "KJ Atlas verified runtime bundle"

    resolved_model_dir: Path | None = None
    if model_dir is not None:
        resolved_model_dir = model_dir.expanduser().resolve(strict=True)
        _reject_overlap(resolved_model_dir, "model directory", ((source_label, source_input),))

    evidence_dir = _new_path(evidence_dir, "Evidence directory")
    evidence_roots: list[tuple[str, Path]] = [(source_label, source_input)]
    if resolved_model_dir is not None:
        evidence_roots.append(("model directory", resolved_model_dir))
    _reject_overlap(evidence_dir, "Evidence directory", tuple(evidence_roots))

    resolved_work_dir: Path | None = None
    if work_dir is not None:
        resolved_work_dir = _new_path(work_dir, "Work directory")
        work_roots = list(evidence_roots)
        work_roots.append(("Evidence directory", evidence_dir))
        _reject_overlap(resolved_work_dir, "Work directory", tuple(work_roots))

    model_verification: dict[str, object] | None = None
    if resolved_model_dir is not None:
        model_verification = verify_model_store(resolved_model_dir)

    temporary: tempfile.TemporaryDirectory[str] | None = None
    source_export: dict[str, object] | None = None
    completed: subprocess.CompletedProcess[bytes] | subprocess.CompletedProcess[str] | None = None
    try:
        if checkout_dir is not None:
            temporary = tempfile.TemporaryDirectory(prefix="soza-runtime-exchange-strict-source-")
            verified_bundle = Path(temporary.name) / "backend"
            source_export = export_runtime_bundle(source_input, verified_bundle)
        else:
            verified_bundle = source_input
            verify_runtime_bundle(verified_bundle)

        command = [
            "bash",
            str(HARNESS),
            "--kj-atlas-backend-bundle",
            str(verified_bundle),
            "--evidence-dir",
            str(evidence_dir),
        ]
        if resolved_model_dir is not None:
            command.extend(["--model-dir", str(resolved_model_dir)])
        if resolved_work_dir is not None:
            command.extend(["--work-dir", str(resolved_work_dir)])
        command.extend(harness_arguments)

        completed = subprocess.run(command, check=False)
    finally:
        if evidence_dir.is_dir():
            if model_verification is not None:
                _write_json(
                    evidence_dir / "runtime-exchange-model-store-static-verification.json",
                    model_verification,
                )
            if source_export is not None:
                _write_json(
                    evidence_dir / "runtime-exchange-source-export.json",
                    source_export,
                )
        if temporary is not None:
            temporary.cleanup()

    if completed is None:
        raise RuntimeError("runtime exchange harnessが開始されませんでした")
    return completed.returncode


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "ISSUE-000070のstrict runtime交換を開始します。KJ Atlas sourceをverified runtime "
            "bundleへ固定し、事前配置model storeを指定した場合はOllama起動前にmanifest / blob "
            "bytesを静的検証してからrepository-local harnessへ委譲します。"
        ),
        allow_abbrev=False,
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--kj-atlas-dir", type=Path)
    source.add_argument("--kj-atlas-backend-bundle", type=Path)
    parser.add_argument("--model-dir", type=Path)
    parser.add_argument("--evidence-dir", required=True, type=Path)
    parser.add_argument("--work-dir", type=Path)
    return parser


def main() -> int:
    parser = build_parser()
    args, harness_arguments = parser.parse_known_args()
    if harness_arguments and harness_arguments[0] == "--":
        harness_arguments = harness_arguments[1:]

    try:
        return run_strict_probe(
            checkout_dir=args.kj_atlas_dir,
            backend_bundle=args.kj_atlas_backend_bundle,
            model_dir=args.model_dir,
            evidence_dir=args.evidence_dir,
            harness_arguments=harness_arguments,
            work_dir=args.work_dir,
        )
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
        parser.exit(1, f"strict runtime version exchange entrypoint failed: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
