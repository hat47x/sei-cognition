#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import tarfile
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

import run_tei_bundle_adapter_compatibility as adapter_runner
import run_tei_revision_b_prepositioned as build_runner
import verify_tei_execution_source_identity as source_identity
from runtime_path_safety import reject_symlink_path_or_ancestors

SCHEMA = "soza.tei-version-exchange-evidence-run/v1"
BUNDLE_NAME = "tei-e3b-p2-revision-b.tar.gz"
REPORT_NAME = "tei-version-exchange-evidence.json"
EXPECTED_RUN_ERRORS = (
    OSError,
    ValueError,
    RuntimeError,
    subprocess.SubprocessError,
    tarfile.TarError,
)
STOP_LINE = (
    "fixed-scope E2/E3 verified != arbitrary TEI version compatibility "
    "!= Release Evidence != Operational Evidence != ISSUE-000072 Resolved"
)


class VersionExchangeRunFailed(RuntimeError):
    def __init__(self, stage: str, report_path: Path, cause: Exception):
        super().__init__(f"{stage} failed: {cause}")
        self.stage = stage
        self.report_path = report_path
        self.cause = cause


@contextmanager
def _go_on_path(executable: Path) -> Iterator[Path]:
    requested = executable.expanduser()
    if requested.name != "go":
        raise ValueError(
            "Linux actual EvidenceではGo executableのbasenameを'go'に固定します: "
            f"{requested}"
        )
    resolved = requested.resolve(strict=True)
    if not resolved.is_file() or not os.access(resolved, os.X_OK):
        raise ValueError(f"Go executableではありません: {resolved}")

    bin_dir = requested.parent.resolve(strict=True)
    original_present = "PATH" in os.environ
    original_path = os.environ.get("PATH", "")
    os.environ["PATH"] = str(bin_dir) + os.pathsep + original_path
    try:
        discovered = shutil.which("go")
        if discovered is None or Path(discovered).resolve() != resolved:
            raise ValueError(
                "指定したGo executableをPATH先頭へ固定できません: "
                f"expected={resolved} actual={discovered}"
            )
        yield resolved
    finally:
        if original_present:
            os.environ["PATH"] = original_path
        else:
            os.environ.pop("PATH", None)


def _write_report(path: Path, value: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    reject_symlink_path_or_ancestors(
        path,
        "TEI version exchange Evidence report",
    )

    candidate: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            candidate = Path(handle.name)
            json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())

        reject_symlink_path_or_ancestors(
            path,
            "TEI version exchange Evidence report",
        )
        os.replace(candidate, path)
        candidate = None
    finally:
        if candidate is not None and candidate.exists() and not candidate.is_symlink():
            candidate.unlink()


def _failure(stage: str, exc: Exception) -> dict[str, object]:
    result: dict[str, object] = {
        "stage": stage,
        "type": type(exc).__name__,
        "message": str(exc),
    }
    detail_builder = getattr(exc, "as_dict", None)
    if callable(detail_builder):
        detail = detail_builder()
        if isinstance(detail, dict):
            substage = detail.get("stage")
            if isinstance(substage, str) and substage:
                result["substage"] = substage
            result["detail"] = detail
    return result


def _is_within(candidate: Path, root: Path) -> bool:
    return candidate == root or root in candidate.parents


def _prepare_reference_input_paths(
    reference_source_repo: Path | None,
    reference_evidence_bundle: Path | None,
) -> tuple[Path | None, Path | None]:
    if (reference_source_repo is None) == (reference_evidence_bundle is None):
        raise ValueError(
            "exact revision A fixed inputは--reference-source-repoまたは"
            "--reference-evidence-bundleのどちらか一方で指定してください"
        )
    if reference_source_repo is not None:
        return reference_source_repo.expanduser().resolve(strict=True), None

    assert reference_evidence_bundle is not None
    requested = reference_evidence_bundle.expanduser()
    reject_symlink_path_or_ancestors(
        requested,
        "TEI historical reference Evidence bundle",
    )
    resolved = requested.resolve(strict=True)
    if not resolved.is_file():
        raise ValueError(
            "TEI historical reference Evidence bundleがfileではありません: "
            f"{resolved}"
        )
    return None, resolved


def _prepare_output_dir(
    output_dir: Path,
    *,
    source_repo: Path,
    reference_source_repo: Path | None,
    reference_evidence_bundle: Path | None,
    soza_repo_root: Path,
) -> Path:
    requested = output_dir.expanduser()
    reject_symlink_path_or_ancestors(
        requested,
        "TEI version exchange Evidence directory",
    )
    resolved = requested.resolve(strict=False)
    if resolved.exists() and not resolved.is_dir():
        raise ValueError(
            "TEI version exchange Evidence出力先がdirectoryではありません: "
            f"{resolved}"
        )

    roots: list[tuple[str, Path]] = [
        ("revision B source checkout", source_repo),
        ("SEI repository", soza_repo_root),
    ]
    if reference_source_repo is not None:
        roots.insert(1, ("revision A reference checkout", reference_source_repo))
    for label, root in roots:
        if _is_within(resolved, root):
            raise ValueError(
                f"TEI version exchange Evidence directoryを{label}配下には置けません: "
                f"output={resolved} root={root}"
            )
        if _is_within(root, resolved):
            raise ValueError(
                f"TEI version exchange Evidence directoryで{label}を包含できません: "
                f"output={resolved} root={root}"
            )

    if reference_evidence_bundle is not None and _is_within(
        reference_evidence_bundle, resolved
    ):
        raise ValueError(
            "TEI version exchange Evidence directoryでhistorical reference bundleを"
            "包含できません: "
            f"output={resolved} bundle={reference_evidence_bundle}"
        )
    return resolved


def _prepare_output_paths(
    bundle_path: Path,
    report_path: Path,
    *,
    overwrite: bool,
) -> None:
    paths = (bundle_path, report_path)
    for path in paths:
        reject_symlink_path_or_ancestors(
            path,
            "TEI version exchange Evidence output",
        )

    existing = [path for path in paths if path.exists()]
    if existing and not overwrite:
        raise ValueError(
            "既存Evidenceを無言で上書きしません。--overwriteを明示してください: "
            + ", ".join(str(path) for path in existing)
        )
    if overwrite:
        for path in existing:
            if not path.is_file():
                raise ValueError(f"Evidence出力先がfileではありません: {path}")
            path.unlink()


def run_version_exchange(
    source_repo: Path,
    reference_source_repo: Path | None,
    soza_repo_root: Path,
    output_dir: Path,
    *,
    reference_evidence_bundle: Path | None = None,
    tei_go_executable: Path,
    soza_go_executable: Path,
    expected_soza_head: str | None = None,
    overwrite: bool = False,
) -> dict[str, object]:
    source_repo = source_repo.expanduser().resolve(strict=True)
    reference_source_repo, reference_evidence_bundle = _prepare_reference_input_paths(
        reference_source_repo,
        reference_evidence_bundle,
    )
    soza_repo_root = soza_repo_root.expanduser().resolve(strict=True)
    output_dir = _prepare_output_dir(
        output_dir,
        source_repo=source_repo,
        reference_source_repo=reference_source_repo,
        reference_evidence_bundle=reference_evidence_bundle,
        soza_repo_root=soza_repo_root,
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    bundle_path = output_dir / BUNDLE_NAME
    report_path = output_dir / REPORT_NAME
    _prepare_output_paths(bundle_path, report_path, overwrite=overwrite)

    acquisition_mode = (
        "git_checkout" if reference_source_repo is not None else "historical_evidence_bundle"
    )
    comparison_axis = {
        "buildSourceCommit": source_identity.REVISION_B,
        "referenceInputSourceCommit": source_identity.REVISION_A,
        "referenceInputAcquisition": acquisition_mode,
        "referenceInputBundle": (
            str(reference_evidence_bundle)
            if reference_evidence_bundle is not None
            else None
        ),
        "teiGoRequirement": build_runner.EXPECTED_GO_VERSION,
        "sozaGoRequirement": "runtime/go go.mod with GOTOOLCHAIN=local",
        "teiGoExecutable": str(tei_go_executable.expanduser()),
        "sozaGoExecutable": str(soza_go_executable.expanduser()),
        "expectedSozaHead": expected_soza_head,
    }

    e2_runner_started = False
    try:
        with _go_on_path(tei_go_executable) as tei_go:
            comparison_axis["teiGoExecutable"] = str(tei_go)
            e2_runner_started = True
            if reference_source_repo is not None:
                e2 = build_runner.produce_bundle(
                    source_repo,
                    reference_source_repo,
                    bundle_path,
                )
            else:
                assert reference_evidence_bundle is not None
                e2 = build_runner.produce_bundle(
                    source_repo,
                    None,
                    bundle_path,
                    reference_evidence_bundle=reference_evidence_bundle,
                )
    except EXPECTED_RUN_ERRORS as exc:
        if not e2_runner_started and not isinstance(
            exc, build_runner.TEIEvidenceStageError
        ):
            exc = build_runner.TEIEvidenceStageError(
                "tei_go_toolchain",
                str(exc),
            )
        report = {
            "schema": SCHEMA,
            "result": "e2_failed",
            "comparisonAxis": comparison_axis,
            "bundleArchive": str(bundle_path),
            "e2": None,
            "e3": None,
            "failure": _failure("E2", exc),
            "qualityJudgement": "not_evaluated",
            "stopLine": STOP_LINE,
        }
        _write_report(report_path, report)
        raise VersionExchangeRunFailed("E2", report_path, exc) from exc

    interim = {
        "schema": SCHEMA,
        "result": "e2_bundle_verified_e3_not_run",
        "comparisonAxis": comparison_axis,
        "bundleArchive": str(bundle_path),
        "e2": e2,
        "e3": None,
        "qualityJudgement": "not_evaluated",
        "stopLine": STOP_LINE,
    }
    _write_report(report_path, interim)

    e3_toolchain_entered = False
    try:
        with _go_on_path(soza_go_executable) as soza_go:
            e3_toolchain_entered = True
            comparison_axis["sozaGoExecutable"] = str(soza_go)
            e3 = adapter_runner.run_compatibility(
                bundle_path,
                soza_repo_root=soza_repo_root,
                expected_source_commit=source_identity.REVISION_B,
                expected_soza_head=expected_soza_head,
            )
            comparison_axis["sozaGoRequirement"] = e3["sozaGoRequirement"]
            comparison_axis["sozaGoObserved"] = e3["sozaGoVersion"]
    except EXPECTED_RUN_ERRORS as exc:
        if not e3_toolchain_entered and not isinstance(
            exc, adapter_runner.TEIAdapterStageError
        ):
            exc = adapter_runner.TEIAdapterStageError(
                "soza_go_toolchain",
                str(exc),
            )
        report = {
            **interim,
            "result": "e2_verified_e3_failed",
            "comparisonAxis": comparison_axis,
            "failure": _failure("E3", exc),
        }
        _write_report(report_path, report)
        raise VersionExchangeRunFailed("E3", report_path, exc) from exc

    report = {
        "schema": SCHEMA,
        "result": "fixed_scope_e2_e3_verified",
        "comparisonAxis": comparison_axis,
        "bundleArchive": str(bundle_path),
        "e2": e2,
        "e3": e3,
        "qualityJudgement": "not_evaluated",
        "stopLine": STOP_LINE,
    }
    _write_report(report_path, report)
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "exact revision B build sourceとexact revision A fixed reference inputを使い、"
            "E2 Evidence bundle生成からE3 current SEI Adapter live testまでを連続実行します。"
            "A fixed inputはexact Git checkoutまたはverified historical Evidence bundleから取得し、"
            "TEI build用Go 1.23.2とSEI検査用Go 1.25系は別executableとして明示します。"
        ),
        allow_abbrev=False,
    )
    parser.add_argument("--source-repo", required=True, type=Path)
    reference_group = parser.add_mutually_exclusive_group(required=True)
    reference_group.add_argument("--reference-source-repo", type=Path)
    reference_group.add_argument("--reference-evidence-bundle", type=Path)
    parser.add_argument(
        "--soza-repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
    )
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--tei-go-executable", required=True, type=Path)
    parser.add_argument("--soza-go-executable", required=True, type=Path)
    parser.add_argument("--expected-soza-head")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = run_version_exchange(
            args.source_repo,
            args.reference_source_repo,
            args.soza_repo_root,
            args.output_dir,
            reference_evidence_bundle=args.reference_evidence_bundle,
            tei_go_executable=args.tei_go_executable,
            soza_go_executable=args.soza_go_executable,
            expected_soza_head=args.expected_soza_head,
            overwrite=args.overwrite,
        )
    except VersionExchangeRunFailed as exc:
        print(f"TEI version exchange Evidence run failed at {exc.stage}: {exc.cause}")
        print(f"- report: {exc.report_path}")
        return 1
    except (OSError, ValueError) as exc:
        print(f"TEI version exchange Evidence run rejected: {exc}")
        return 1

    report_path = args.output_dir.expanduser().resolve() / REPORT_NAME
    if args.json:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    else:
        print("TEI version exchange fixed-scope E2/E3: verified")
        print(f"- reference input acquisition: {result['comparisonAxis']['referenceInputAcquisition']}")
        print(f"- bundle: {result['bundleArchive']}")
        print(f"- report: {report_path}")
        print(result["stopLine"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
