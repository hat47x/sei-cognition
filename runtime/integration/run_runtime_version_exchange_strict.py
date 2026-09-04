#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path

from export_kj_atlas_runtime_source import export_runtime_bundle
from prepare_runtime_version_exchange_archives import load_manifest as load_artifact_manifest
from prepare_runtime_version_exchange_archives import verify_archive
from prepare_runtime_version_exchange_model_store import prepare_model_store
from runtime_path_safety import reject_symlink_path_or_ancestors
from verify_kj_atlas_runtime_source import verify_runtime_bundle
from verify_runtime_version_exchange_model_store import verify_model_store


INTEGRATION_DIR = Path(__file__).resolve().parent
SOZA_ROOT = INTEGRATION_DIR.parents[1]
HARNESS = INTEGRATION_DIR / "run_runtime_version_exchange.sh"
RUNTIME_ARCHIVE_OPTIONS = ("--runtime-a-archive", "--runtime-b-archive")
RUNTIME_ARCHIVE_MANIFEST_LABELS = {
    "--runtime-a-archive": "a",
    "--runtime-b-archive": "b",
}
STRICT_CHILD_ENVIRONMENT_KEYS = (
    "SOZA_RUNTIME_EXCHANGE_KJ_ATLAS_BACKEND_BUNDLE",
    "SOZA_RUNTIME_EXCHANGE_WORK_DIR",
    "SOZA_RUNTIME_EXCHANGE_EVIDENCE_DIR",
    "SOZA_RUNTIME_EXCHANGE_PREPOSITIONED_ARCHIVE_A",
    "SOZA_RUNTIME_EXCHANGE_PREPOSITIONED_ARCHIVE_B",
    "SOZA_RUNTIME_EXCHANGE_MODEL_DIR",
)
STRICT_CHILD_PYTHON_ENVIRONMENT_KEYS = (
    "PYTHONPATH",
    "PYTHONHOME",
    "PYTHONSTARTUP",
    "PYTHONUSERBASE",
)
STRICT_CHILD_TEMP_ENVIRONMENT_KEYS = ("TMPDIR", "TMP", "TEMP")


def _reject_forwarded_identity_options(arguments: list[str]) -> None:
    forbidden = {
        "--kj-atlas-dir",
        "--kj-atlas-backend-bundle",
        "--model-dir",
        "--prepare-model-dir",
        "--evidence-dir",
        "--work-dir",
    }
    for argument in arguments:
        if argument in forbidden or any(
            argument.startswith(name + "=") for name in forbidden
        ):
            raise ValueError(
                "strict Evidenceのidentity / safety optionはこのentrypoint側で確定します。"
                f"harnessへ直接渡せません: {argument}"
            )


def _forwarded_runtime_archives(arguments: list[str]) -> dict[str, Path]:
    """low-level harnessへ渡す事前配置runtime archiveを曖昧さなく抽出する。"""

    selected: dict[str, Path] = {}
    index = 0
    while index < len(arguments):
        argument = arguments[index]
        matched = False
        for option in RUNTIME_ARCHIVE_OPTIONS:
            value: str | None = None
            if argument == option:
                if index + 1 >= len(arguments):
                    raise ValueError(f"{option} requires PATH")
                value = arguments[index + 1]
                index += 2
                matched = True
            elif argument.startswith(option + "="):
                value = argument.split("=", 1)[1]
                index += 1
                matched = True

            if matched:
                if not value:
                    raise ValueError(f"{option} requires PATH")
                if option in selected:
                    raise ValueError(
                        f"runtime archive optionを重複指定できません: {option}"
                    )
                selected[option] = Path(value)
                break

        if not matched:
            index += 1
    return selected


def _new_path(path: Path, label: str) -> Path:
    """新規出力pathを、symlink解決前の要求pathから検証する。"""

    requested = path.expanduser()
    reject_symlink_path_or_ancestors(requested, label)
    resolved = requested.resolve(strict=False)
    if resolved.exists():
        raise ValueError(f"{label}は新しいpathを指定してください: {resolved}")
    return resolved


def _existing_directory(path: Path, label: str) -> Path:
    """既存directory inputを、symlink解決前の要求pathから検証する。"""

    requested = path.expanduser()
    reject_symlink_path_or_ancestors(requested, label)
    try:
        resolved = requested.resolve(strict=True)
    except FileNotFoundError as exc:
        raise ValueError(f"{label}が存在しません: {requested}") from exc
    if not resolved.is_dir():
        raise ValueError(f"{label}はdirectoryを指定してください: {resolved}")
    return resolved


def _default_work_path(evidence_dir: Path) -> Path:
    """親TMPDIRへ依存せず、Evidenceと同じ安全なparentに既定work pathを置く。"""

    return evidence_dir.parent / f"{evidence_dir.name}-work"


def _default_source_bundle_root(evidence_dir: Path) -> Path:
    """checkout起点の一時source bundleもEvidenceと同じ安全なparentへ固定する。"""

    return evidence_dir.parent / f"{evidence_dir.name}-source"


def _is_within(candidate: Path, root: Path) -> bool:
    return candidate == root or root in candidate.parents


def _reject_overlap(
    candidate: Path,
    candidate_label: str,
    roots: tuple[tuple[str, Path], ...],
) -> None:
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


def _validate_runtime_archives(
    arguments: list[str],
    *,
    source_input: Path,
    source_label: str,
) -> dict[str, Path]:
    roots = (("SOZA repository", SOZA_ROOT), (source_label, source_input))
    validated: dict[str, Path] = {}
    for option, requested in _forwarded_runtime_archives(arguments).items():
        expanded = requested.expanduser()
        reject_symlink_path_or_ancestors(expanded, option)
        try:
            resolved = expanded.resolve(strict=True)
        except FileNotFoundError as exc:
            raise ValueError(
                f"{option}のarchive fileが存在しません: {expanded}"
            ) from exc
        if not resolved.is_file():
            raise ValueError(f"{option}はregular fileを指定してください: {resolved}")
        _reject_overlap(resolved, f"{option} runtime archive", roots)
        if resolved in validated.values():
            raise ValueError(
                "runtime A / Bへ同じarchive pathを指定できません: "
                f"option={option} path={resolved}"
            )
        validated[option] = resolved
    return validated


def _verify_runtime_archive_identities(runtime_archives: dict[str, Path]) -> None:
    """事前配置archiveのactual bytesを固定manifestへ照合する。"""

    if not runtime_archives:
        return

    manifest = load_artifact_manifest()
    archives = manifest.get("runtimeArchives")
    if not isinstance(archives, dict):
        raise ValueError("runtime artifact manifestにruntimeArchivesがありません")

    for option, resolved in runtime_archives.items():
        label = RUNTIME_ARCHIVE_MANIFEST_LABELS[option]
        metadata = archives.get(label)
        if not isinstance(metadata, dict):
            raise ValueError(
                f"runtime artifact manifestにruntimeArchives.{label}がありません"
            )
        expected_size = metadata.get("sizeBytes")
        expected_sha256 = metadata.get("sha256")
        if not isinstance(expected_size, int) or isinstance(expected_size, bool):
            raise ValueError(f"runtimeArchives.{label}.sizeBytesが不正です")
        if not isinstance(expected_sha256, str):
            raise ValueError(f"runtimeArchives.{label}.sha256が不正です")
        verify_archive(resolved, expected_size, expected_sha256)


def _strict_child_environment(work_dir: Path | None = None) -> dict[str, str]:
    """strict入口が確定するidentity / safety / Python / Git / temp境界を親環境から分離する。"""

    environment = os.environ.copy()
    for key in tuple(environment):
        if key in STRICT_CHILD_ENVIRONMENT_KEYS:
            environment.pop(key, None)
        elif key in STRICT_CHILD_PYTHON_ENVIRONMENT_KEYS:
            environment.pop(key, None)
        elif key in STRICT_CHILD_TEMP_ENVIRONMENT_KEYS:
            environment.pop(key, None)
        elif key.startswith("GIT_"):
            environment.pop(key, None)

    # Python helper/KJ Atlas/adapterのimportを親shellのuser siteやbytecode副作用へ委ねない。
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONNOUSERSITE"] = "1"

    if work_dir is not None:
        resolved_work = str(work_dir)
        for key in STRICT_CHILD_TEMP_ENVIRONMENT_KEYS:
            environment[key] = resolved_work
    return environment


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
    prepare_model_dir: Path | None = None,
) -> int:
    _reject_forwarded_identity_options(harness_arguments)

    if (checkout_dir is None) == (backend_bundle is None):
        raise ValueError(
            "--kj-atlas-dirまたは--kj-atlas-backend-bundleのどちらか一方を指定してください"
        )
    if model_dir is not None and prepare_model_dir is not None:
        raise ValueError("--model-dirと--prepare-model-dirは同時に指定できません")

    if checkout_dir is not None:
        source_input = _existing_directory(checkout_dir, "KJ Atlas checkout")
        source_label = "KJ Atlas checkout"
    else:
        assert backend_bundle is not None
        source_input = _existing_directory(
            backend_bundle,
            "KJ Atlas verified runtime bundle",
        )
        source_label = "KJ Atlas verified runtime bundle"

    _reject_overlap(
        source_input,
        source_label,
        (("SOZA repository", SOZA_ROOT),),
    )
    strict_input_roots = (
        ("SOZA repository", SOZA_ROOT),
        (source_label, source_input),
    )

    # 事前配置runtime archiveは、source/model準備やharness起動より前にpath境界を固定する。
    runtime_archives = _validate_runtime_archives(
        harness_arguments,
        source_input=source_input,
        source_label=source_label,
    )

    resolved_model_dir: Path | None = None
    model_will_be_prepared = prepare_model_dir is not None
    if model_dir is not None:
        resolved_model_dir = _existing_directory(model_dir, "Model directory")
    elif prepare_model_dir is not None:
        resolved_model_dir = _new_path(
            prepare_model_dir,
            "Prepared model directory",
        )
    if resolved_model_dir is not None:
        _reject_overlap(resolved_model_dir, "model directory", strict_input_roots)
        for option, archive in runtime_archives.items():
            _reject_overlap(
                archive,
                f"{option} runtime archive",
                (("model directory", resolved_model_dir),),
            )

    evidence_dir = _new_path(evidence_dir, "Evidence directory")
    evidence_roots: list[tuple[str, Path]] = list(strict_input_roots)
    if resolved_model_dir is not None:
        evidence_roots.append(("model directory", resolved_model_dir))
    _reject_overlap(evidence_dir, "Evidence directory", tuple(evidence_roots))

    requested_work_dir = (
        work_dir if work_dir is not None else _default_work_path(evidence_dir)
    )
    resolved_work_dir = _new_path(requested_work_dir, "Work directory")
    work_roots = list(evidence_roots)
    work_roots.append(("Evidence directory", evidence_dir))
    _reject_overlap(resolved_work_dir, "Work directory", tuple(work_roots))

    temporary_source_root: Path | None = None
    if checkout_dir is not None:
        temporary_source_root = _new_path(
            _default_source_bundle_root(evidence_dir),
            "Temporary source directory",
        )
        source_temp_roots = list(work_roots)
        source_temp_roots.append(("Work directory", resolved_work_dir))
        _reject_overlap(
            temporary_source_root,
            "Temporary source directory",
            tuple(source_temp_roots),
        )

    # 明白なpath blockerをすべて除いた後、重いsource exportやmodel準備より前にactual archive bytesを固定する。
    _verify_runtime_archive_identities(runtime_archives)

    model_verification: dict[str, object] | None = None
    model_preparation: dict[str, object] | None = None
    if resolved_model_dir is not None and not model_will_be_prepared:
        model_verification = verify_model_store(resolved_model_dir)

    source_export: dict[str, object] | None = None
    completed: subprocess.CompletedProcess[bytes] | subprocess.CompletedProcess[str] | None = None
    try:
        if checkout_dir is not None:
            assert temporary_source_root is not None
            verified_bundle = temporary_source_root / "backend"
            source_export = export_runtime_bundle(source_input, verified_bundle)
        else:
            verified_bundle = source_input
            verify_runtime_bundle(verified_bundle)

        if resolved_model_dir is not None and model_will_be_prepared:
            model_preparation = prepare_model_store(resolved_model_dir)
            model_verification = verify_model_store(resolved_model_dir)

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
        command.extend(["--work-dir", str(resolved_work_dir)])
        command.extend(harness_arguments)

        completed = subprocess.run(
            command,
            check=False,
            env=_strict_child_environment(resolved_work_dir),
        )
    finally:
        if evidence_dir.is_dir():
            if model_preparation is not None:
                _write_json(
                    evidence_dir / "runtime-exchange-model-store-preparation.json",
                    model_preparation,
                )
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
        if temporary_source_root is not None:
            shutil.rmtree(temporary_source_root, ignore_errors=True)

    if completed is None:
        raise RuntimeError("runtime exchange harnessが開始されませんでした")
    return completed.returncode


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "ISSUE-000070のstrict runtime交換を開始します。KJ Atlas sourceをverified runtime "
            "bundleへ固定し、事前配置runtime archiveはharness起動前に固定size / SHA-256を再検証し、"
            "事前配置model storeはOllama起動前にmanifest / blob bytesを静的検証します。"
            "work directoryとcheckout起点の一時source bundleをEvidence directory側へ明示固定し、"
            "親processのTMPDIRやPython/Git内部指定へ実行surfaceを委ねません。"
            "--prepare-model-dirを指定した場合は固定model storeをregistryから新規に準備し、"
            "再検証してからrepository-local harnessへ委譲します。"
        ),
        allow_abbrev=False,
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--kj-atlas-dir", type=Path)
    source.add_argument("--kj-atlas-backend-bundle", type=Path)
    model = parser.add_mutually_exclusive_group()
    model.add_argument("--model-dir", type=Path)
    model.add_argument("--prepare-model-dir", type=Path)
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
            prepare_model_dir=args.prepare_model_dir,
        )
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
        parser.exit(1, f"strict runtime version exchange entrypoint failed: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
