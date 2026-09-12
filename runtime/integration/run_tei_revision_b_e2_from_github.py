#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path

import preflight_tei_version_exchange_from_github as github_preflight
import prepare_tei_revision_b_source as source_acquisition
import run_tei_revision_b_prepositioned as e2_runner
import run_tei_version_exchange_evidence as version_exchange
import run_tei_version_exchange_from_github as github_runner
from runtime_path_safety import reject_symlink_path_or_ancestors

SCHEMA = "sei.tei-revision-b-e2-github-run/v1"
REPORT_NAME = "tei-revision-b-e2-github.json"
BUNDLE_NAME = "tei-e3b-p2-revision-b-e2-partial.tar.gz"
SEI_ROOT = Path(__file__).resolve().parents[2]
STOP_LINE = (
    "revision B GitHub acquisition + fixed-scope E2 verified != E3 SEI Adapter compatibility "
    "!= arbitrary TEI version compatibility != Operational Evidence != ISSUE-000072 Resolved"
)


class GitHubE2RunFailed(RuntimeError):
    def __init__(self, report_path: Path, cause: Exception) -> None:
        super().__init__(f"E2 failed: {cause}")
        self.report_path = report_path
        self.cause = cause


def _token_from_environment() -> str:
    return os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""


def _is_within(candidate: Path, root: Path) -> bool:
    return candidate == root or root in candidate.parents


def _prepare_output_dir_before_source(
    output_dir: Path,
    reference_source_repo: Path | None,
    reference_evidence_bundle: Path | None,
) -> Path:
    requested = output_dir.expanduser()
    reject_symlink_path_or_ancestors(
        requested,
        "TEI revision B E2 partial Evidence directory",
    )
    resolved = requested.resolve(strict=False)
    if resolved.exists() and not resolved.is_dir():
        raise ValueError(
            "TEI revision B E2 partial Evidence出力先がdirectoryではありません: "
            f"{resolved}"
        )

    roots: list[tuple[str, Path]] = [("SEI repository", SEI_ROOT)]
    if reference_source_repo is not None:
        roots.append(
            (
                "revision A reference checkout",
                reference_source_repo.expanduser().resolve(strict=True),
            )
        )
    for label, root in roots:
        if _is_within(resolved, root):
            raise ValueError(
                f"E2 partial Evidence directoryを{label}配下には置けません: "
                f"output={resolved} root={root}"
            )
        if _is_within(root, resolved):
            raise ValueError(
                f"E2 partial Evidence directoryで{label}を包含できません: "
                f"output={resolved} root={root}"
            )

    if reference_evidence_bundle is not None:
        bundle = reference_evidence_bundle.expanduser().resolve(strict=True)
        if _is_within(bundle, resolved):
            raise ValueError(
                "E2 partial Evidence directoryでhistorical reference bundleを包含できません: "
                f"output={resolved} bundle={bundle}"
            )
    return resolved


def _precheck_partial_output_paths(
    output_dir: Path,
    *,
    overwrite: bool,
) -> tuple[Path, Path]:
    bundle_path = output_dir / BUNDLE_NAME
    report_path = output_dir / REPORT_NAME
    paths = (bundle_path, report_path)

    for path in paths:
        reject_symlink_path_or_ancestors(
            path,
            "TEI revision B E2 partial Evidence output",
        )

    existing = [path for path in paths if os.path.lexists(path)]
    if existing and not overwrite:
        raise ValueError(
            "既存E2 partial Evidenceを無言で上書きしません。"
            "--overwriteを明示してください: "
            + ", ".join(str(path) for path in existing)
        )
    for path in existing:
        if not path.is_file():
            raise ValueError(f"E2 partial Evidence出力先がfileではありません: {path}")

    # This is intentionally read-only. Actual overwrite/removal remains in the
    # canonical output preparation after exact-B source acquisition.
    return bundle_path, report_path


def _comparison_axis(
    reference_source_repo: Path | None,
    reference_evidence_bundle: Path | None,
    tei_go_executable: Path,
) -> dict[str, object]:
    return {
        "buildSourceCommit": e2_runner.source_identity.REVISION_B,
        "referenceInputSourceCommit": e2_runner.source_identity.REVISION_A,
        "referenceInputAcquisition": (
            "git_checkout"
            if reference_source_repo is not None
            else "historical_evidence_bundle"
        ),
        "referenceInputBundle": (
            str(reference_evidence_bundle.expanduser().resolve(strict=True))
            if reference_evidence_bundle is not None
            else None
        ),
        "teiGoRequirement": e2_runner.EXPECTED_GO_VERSION,
        "teiGoExecutable": str(tei_go_executable.expanduser()),
        "e3IntentionallyNotRun": True,
    }


def _verify_e2_prerequisites_before_source(
    tei_go_executable: Path,
) -> dict[str, str]:
    e2_runner._ensure_linux_amd64()
    with version_exchange._go_on_path(tei_go_executable) as resolved_go:
        env = e2_runner._controlled_go_env()
        observation = e2_runner._verify_tei_go_toolchain(SEI_ROOT, env=env)
        observation["executable"] = str(resolved_go)
        return observation


def run_e2_from_github(
    reference_source_repo: Path | None,
    output_dir: Path,
    *,
    reference_evidence_bundle: Path | None = None,
    tei_go_executable: Path,
    token: str,
    overwrite: bool = False,
) -> dict[str, object]:
    if not token:
        raise ValueError("GitHub API tokenがありません")

    reference_source_repo, reference_evidence_bundle = (
        version_exchange._prepare_reference_input_paths(
            reference_source_repo,
            reference_evidence_bundle,
        )
    )
    output_dir = _prepare_output_dir_before_source(
        output_dir,
        reference_source_repo,
        reference_evidence_bundle,
    )
    _precheck_partial_output_paths(output_dir, overwrite=overwrite)
    github_preflight._check_reference_input(
        reference_source_repo,
        reference_evidence_bundle,
    )

    # E3 toolchain is deliberately not checked here. ISSUE-000072 defines E2 and E3
    # as separate experiments, and this entry point exists to preserve partial E2
    # Evidence when E3 prerequisites are unavailable.
    go_toolchain = _verify_e2_prerequisites_before_source(tei_go_executable)
    comparison_axis = _comparison_axis(
        reference_source_repo,
        reference_evidence_bundle,
        Path(go_toolchain["executable"]),
    )

    source_temp_parent = github_runner._prepare_source_temp_parent(
        output_dir,
        SEI_ROOT,
        reference_source_repo,
    )

    with tempfile.TemporaryDirectory(
        prefix="sei-tei-b-e2-github-source-",
        dir=source_temp_parent,
    ) as tmp:
        source_repo = Path(tmp) / "tei-revision-b"
        acquisition = source_acquisition.materialize_revision_b_source(
            source_repo,
            token=token,
        )
        provenance = github_runner._source_provenance(acquisition)

        verified_output_dir = version_exchange._prepare_output_dir(
            output_dir,
            source_repo=source_repo,
            reference_source_repo=reference_source_repo,
            reference_evidence_bundle=reference_evidence_bundle,
            sei_repo_root=SEI_ROOT,
        )
        verified_output_dir.mkdir(parents=True, exist_ok=True)
        bundle_path = verified_output_dir / BUNDLE_NAME
        report_path = verified_output_dir / REPORT_NAME
        version_exchange._prepare_output_paths(
            bundle_path,
            report_path,
            overwrite=overwrite,
        )

        try:
            with version_exchange._go_on_path(
                Path(go_toolchain["executable"])
            ) as resolved_go:
                comparison_axis["teiGoExecutable"] = str(resolved_go)
                if reference_source_repo is not None:
                    e2 = e2_runner.produce_bundle(
                        source_repo,
                        reference_source_repo,
                        bundle_path,
                    )
                else:
                    assert reference_evidence_bundle is not None
                    e2 = e2_runner.produce_bundle(
                        source_repo,
                        None,
                        bundle_path,
                        reference_evidence_bundle=reference_evidence_bundle,
                    )
        except version_exchange.EXPECTED_RUN_ERRORS as exc:
            report = {
                "schema": SCHEMA,
                "result": "e2_failed",
                "sourceAcquisition": provenance,
                "comparisonAxis": comparison_axis,
                "bundleArchive": str(bundle_path),
                "e2": None,
                "e3": None,
                "failure": version_exchange._failure("E2", exc),
                "qualityJudgement": "not_evaluated",
                "stopLine": STOP_LINE,
            }
            github_runner._write_report(report_path, report, overwrite=overwrite)
            raise GitHubE2RunFailed(report_path, exc) from exc

        report = {
            "schema": SCHEMA,
            "result": "e2_bundle_verified_e3_not_run",
            "sourceAcquisition": provenance,
            "comparisonAxis": comparison_axis,
            "bundleArchive": str(bundle_path),
            "e2": e2,
            "e3": None,
            "qualityJudgement": "not_evaluated",
            "stopLine": STOP_LINE,
        }
        github_runner._write_report(report_path, report, overwrite=overwrite)
        return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "GitHub Git Data APIからexact revision B sourceを取得し、E3 toolchainの有無とは"
            "独立してISSUE-000072 E2（actual build / deployment-provider-plan / Evidence bundle）"
            "までを回収します。E3 SEI Adapter live testは意図的に実行しません。"
        ),
        allow_abbrev=False,
    )
    reference_group = parser.add_mutually_exclusive_group(required=True)
    reference_group.add_argument("--reference-source-repo", type=Path)
    reference_group.add_argument("--reference-evidence-bundle", type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--tei-go-executable", required=True, type=Path)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        token = _token_from_environment()
        if not token:
            raise ValueError(
                "GITHUB_TOKENまたはGH_TOKENをenvironmentへ設定してください"
            )
        result = run_e2_from_github(
            args.reference_source_repo,
            args.output_dir,
            reference_evidence_bundle=args.reference_evidence_bundle,
            tei_go_executable=args.tei_go_executable,
            token=token,
            overwrite=args.overwrite,
        )
    except GitHubE2RunFailed as exc:
        print(f"TEI revision B GitHub E2 run failed: {exc.cause}")
        print(f"- report: {exc.report_path}")
        return 1
    except version_exchange.EXPECTED_RUN_ERRORS as exc:
        print(f"TEI revision B GitHub E2 run rejected: {exc}")
        return 1

    report_path = args.output_dir.expanduser().resolve(strict=False) / REPORT_NAME
    if args.json:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    else:
        print("TEI revision B GitHub E2 partial Evidence: verified")
        print(f"- bundle: {result['bundleArchive']}")
        print(f"- report: {report_path}")
        print(result["stopLine"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
