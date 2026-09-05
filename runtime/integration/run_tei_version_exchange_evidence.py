#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import tarfile
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

import run_tei_bundle_adapter_compatibility as adapter_runner
import run_tei_revision_b_prepositioned as build_runner
import verify_tei_execution_source_identity as source_identity

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


def _parse_go_version(value: str) -> tuple[int, int, int]:
    token = value.strip()
    if token.startswith("go"):
        token = token[2:]
    parts = token.split(".")
    if len(parts) not in {2, 3} or not all(part.isdigit() for part in parts):
        raise ValueError(f"Go versionを解釈できません: {value!r}")
    numbers = [int(part) for part in parts]
    if len(numbers) == 2:
        numbers.append(0)
    return numbers[0], numbers[1], numbers[2]


def _read_go_directive(go_mod: Path) -> str:
    try:
        lines = go_mod.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise adapter_runner.TEIAdapterStageError(
            "soza_go_toolchain",
            f"current SOZA go.modを読めません: {exc}",
        ) from exc
    for line in lines:
        fields = line.strip().split()
        if len(fields) == 2 and fields[0] == "go":
            try:
                _parse_go_version(fields[1])
            except ValueError as exc:
                raise adapter_runner.TEIAdapterStageError(
                    "soza_go_toolchain",
                    f"current SOZA go.modのGo directiveを解釈できません: {fields[1]!r}",
                ) from exc
            return fields[1]
    raise adapter_runner.TEIAdapterStageError(
        "soza_go_toolchain",
        "current SOZA go.modにGo directiveがありません",
    )


def _verify_soza_go_requirement(soza_repo_root: Path) -> dict[str, str]:
    go_root = soza_repo_root / "runtime/go"
    go_mod = go_root / "go.mod"
    requirement = _read_go_directive(go_mod)
    env = os.environ.copy()
    env["GOWORK"] = "off"
    env["GOENV"] = "off"
    env["GOTOOLCHAIN"] = "local"
    env.pop("GOFLAGS", None)
    env.pop("GOOS", None)
    env.pop("GOARCH", None)
    process = adapter_runner._run_stage(
        "soza_go_toolchain",
        ["go", "version"],
        cwd=go_root,
        env=env,
        timeout=30,
    )
    observed = process.stdout.strip()
    fields = observed.split()
    if len(fields) < 3 or fields[0:2] != ["go", "version"]:
        raise adapter_runner.TEIAdapterStageError(
            "soza_go_toolchain",
            f"go version出力を解釈できません: {observed!r}",
            command=["go", "version"],
            stdout=process.stdout,
            stderr=process.stderr,
        )
    try:
        actual = _parse_go_version(fields[2])
        required = _parse_go_version(requirement)
    except ValueError as exc:
        raise adapter_runner.TEIAdapterStageError(
            "soza_go_toolchain",
            str(exc),
            command=["go", "version"],
            stdout=process.stdout,
            stderr=process.stderr,
        ) from exc
    if actual < required:
        raise adapter_runner.TEIAdapterStageError(
            "soza_go_toolchain",
            "current SOZA go.modのGo要件を満たしません: "
            f"required>={requirement} actual={fields[2]}",
            command=["go", "version"],
            stdout=process.stdout,
            stderr=process.stderr,
        )
    return {
        "required": requirement,
        "observed": observed,
    }


def _write_report(path: Path, value: dict[str, object]) -> None:
    candidate = path.with_name(path.name + ".tmp")
    candidate.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(candidate, path)


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


def _prepare_output_paths(
    bundle_path: Path,
    report_path: Path,
    *,
    overwrite: bool,
) -> None:
    existing = [path for path in (bundle_path, report_path) if path.exists()]
    if existing and not overwrite:
        raise ValueError(
            "既存Evidenceを無言で上書きしません。--overwriteを明示してください: "
            + ", ".join(str(path) for path in existing)
        )
    if overwrite:
        for path in existing:
            if not path.is_file() and not path.is_symlink():
                raise ValueError(f"Evidence出力先がfileではありません: {path}")
            path.unlink()


def run_version_exchange(
    source_repo: Path,
    reference_source_repo: Path,
    soza_repo_root: Path,
    output_dir: Path,
    *,
    tei_go_executable: Path,
    soza_go_executable: Path,
    expected_soza_head: str | None = None,
    overwrite: bool = False,
) -> dict[str, object]:
    source_repo = source_repo.expanduser().resolve(strict=True)
    reference_source_repo = reference_source_repo.expanduser().resolve(strict=True)
    soza_repo_root = soza_repo_root.expanduser().resolve(strict=True)
    output_dir = output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    bundle_path = output_dir / BUNDLE_NAME
    report_path = output_dir / REPORT_NAME
    _prepare_output_paths(bundle_path, report_path, overwrite=overwrite)

    comparison_axis = {
        "buildSourceCommit": source_identity.REVISION_B,
        "referenceInputSourceCommit": source_identity.REVISION_A,
        "teiGoRequirement": build_runner.EXPECTED_GO_VERSION,
        "sozaGoRequirement": "runtime/go go.mod with GOTOOLCHAIN=local",
        "teiGoExecutable": str(tei_go_executable.expanduser()),
        "sozaGoExecutable": str(soza_go_executable.expanduser()),
        "expectedSozaHead": expected_soza_head,
    }

    try:
        with _go_on_path(tei_go_executable) as tei_go:
            comparison_axis["teiGoExecutable"] = str(tei_go)
            e2 = build_runner.produce_bundle(
                source_repo,
                reference_source_repo,
                bundle_path,
            )
    except EXPECTED_RUN_ERRORS as exc:
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

    try:
        with _go_on_path(soza_go_executable) as soza_go:
            comparison_axis["sozaGoExecutable"] = str(soza_go)
            soza_go_observation = _verify_soza_go_requirement(soza_repo_root)
            comparison_axis["sozaGoRequirement"] = soza_go_observation["required"]
            comparison_axis["sozaGoObserved"] = soza_go_observation["observed"]
            e3 = adapter_runner.run_compatibility(
                bundle_path,
                soza_repo_root=soza_repo_root,
                expected_source_commit=source_identity.REVISION_B,
                expected_soza_head=expected_soza_head,
            )
    except EXPECTED_RUN_ERRORS as exc:
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
            "E2 Evidence bundle生成からE3 current SOZA Adapter live testまでを連続実行します。"
            "TEI build用Go 1.23.2とSOZA検査用Go 1.25系は別executableとして明示します。"
        ),
        allow_abbrev=False,
    )
    parser.add_argument("--source-repo", required=True, type=Path)
    parser.add_argument("--reference-source-repo", required=True, type=Path)
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
        print(f"- bundle: {result['bundleArchive']}")
        print(f"- report: {report_path}")
        print(result["stopLine"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
