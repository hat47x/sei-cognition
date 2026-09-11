#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

import preflight_tei_version_exchange_from_github as github_preflight
import prepare_tei_revision_b_source_from_snapshot as snapshot_source
import run_tei_revision_b_e2_from_github as github_e2
import run_tei_version_exchange_evidence as version_exchange
import run_tei_version_exchange_from_github as github_runner
from runtime_path_safety import reject_symlink_path_or_ancestors

SCHEMA = github_e2.SCHEMA
REPORT_NAME = github_e2.REPORT_NAME
BUNDLE_NAME = github_e2.BUNDLE_NAME
STOP_LINE = github_e2.STOP_LINE
SOZA_ROOT = github_e2.SOZA_ROOT


class SnapshotE2RunFailed(RuntimeError):
    def __init__(self, report_path: Path, cause: Exception) -> None:
        super().__init__(f"E2 failed: {cause}")
        self.report_path = report_path
        self.cause = cause


def _prepare_snapshot_input(snapshot: Path, output_dir: Path) -> Path:
    requested = snapshot.expanduser()
    reject_symlink_path_or_ancestors(requested, "TEI revision B Git Data snapshot")
    resolved = requested.resolve(strict=True)
    if not resolved.is_file():
        raise ValueError(f"TEI revision B Git Data snapshotがfileではありません: {resolved}")

    output = output_dir.expanduser().resolve(strict=False)
    if github_e2._is_within(resolved, output):
        raise ValueError(
            "E2 partial Evidence directoryでGit Data snapshot入力を包含できません: "
            f"output={output} snapshot={resolved}"
        )
    soza = SOZA_ROOT.expanduser().resolve(strict=False)
    if github_e2._is_within(resolved, soza):
        raise ValueError(
            "TEI Git Data snapshotをSEI repository配下から実行入力にできません: "
            f"snapshot={resolved} soza={soza}"
        )
    return resolved


def _source_provenance(acquisition: dict[str, object]) -> dict[str, object]:
    provenance = github_runner._source_provenance(acquisition)
    transport = acquisition.get("sourceTransport")
    if not isinstance(transport, dict):
        raise ValueError("snapshot materialization resultにsourceTransportがありません")
    if transport.get("mode") != snapshot_source.SNAPSHOT_TRANSPORT_MODE:
        raise ValueError(
            "snapshot source transport modeが固定値と一致しません: "
            f"expected={snapshot_source.SNAPSHOT_TRANSPORT_MODE} "
            f"actual={transport.get('mode')}"
        )
    if transport.get("runtimeCredentialUsed") is not False:
        raise ValueError(
            "snapshot E2 source transportでruntime credential未使用を確認できません"
        )
    provenance["sourceTransport"] = {
        key: transport.get(key)
        for key in (
            "mode",
            "schema",
            "sha256",
            "responsesAvailable",
            "responsesConsumed",
            "allConsumedResponsesUnique",
            "runtimeCredentialUsed",
        )
        if key in transport
    }
    return provenance


def run_e2_from_snapshot(
    snapshot: Path,
    reference_source_repo: Path | None,
    output_dir: Path,
    *,
    reference_evidence_bundle: Path | None = None,
    tei_go_executable: Path,
    overwrite: bool = False,
) -> dict[str, object]:
    reference_source_repo, reference_evidence_bundle = (
        version_exchange._prepare_reference_input_paths(
            reference_source_repo,
            reference_evidence_bundle,
        )
    )
    output_dir = github_e2._prepare_output_dir_before_source(
        output_dir,
        reference_source_repo,
        reference_evidence_bundle,
    )
    snapshot = _prepare_snapshot_input(snapshot, output_dir)
    github_e2._precheck_partial_output_paths(output_dir, overwrite=overwrite)
    github_preflight._check_reference_input(
        reference_source_repo,
        reference_evidence_bundle,
    )

    # E3 remains intentionally independent. This path only verifies the exact
    # historical E2 toolchain before touching revision B source bytes.
    go_toolchain = github_e2._verify_e2_prerequisites_before_source(
        tei_go_executable
    )
    comparison_axis = github_e2._comparison_axis(
        reference_source_repo,
        reference_evidence_bundle,
        Path(go_toolchain["executable"]),
    )

    source_temp_parent = github_runner._prepare_source_temp_parent(
        output_dir,
        SOZA_ROOT,
        reference_source_repo,
    )

    with tempfile.TemporaryDirectory(
        prefix="soza-tei-b-e2-snapshot-source-",
        dir=source_temp_parent,
    ) as tmp:
        source_repo = Path(tmp) / "tei-revision-b"
        acquisition = snapshot_source.materialize_revision_b_source_from_snapshot(
            source_repo,
            snapshot_path=snapshot,
        )
        provenance = _source_provenance(acquisition)

        verified_output_dir = version_exchange._prepare_output_dir(
            output_dir,
            source_repo=source_repo,
            reference_source_repo=reference_source_repo,
            reference_evidence_bundle=reference_evidence_bundle,
            soza_repo_root=SOZA_ROOT,
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
                    e2 = github_e2.e2_runner.produce_bundle(
                        source_repo,
                        reference_source_repo,
                        bundle_path,
                    )
                else:
                    assert reference_evidence_bundle is not None
                    e2 = github_e2.e2_runner.produce_bundle(
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
            raise SnapshotE2RunFailed(report_path, exc) from exc

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
            "credential-free Git Data snapshot transportからexact revision B sourceを再構成し、"
            "既存ISSUE-000072 E2 partial contractのままactual build / deployment-provider-plan / "
            "Evidence bundleまでを回収します。E3は意図的に実行しません。"
        ),
        allow_abbrev=False,
    )
    parser.add_argument("--snapshot", required=True, type=Path)
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
        result = run_e2_from_snapshot(
            args.snapshot,
            args.reference_source_repo,
            args.output_dir,
            reference_evidence_bundle=args.reference_evidence_bundle,
            tei_go_executable=args.tei_go_executable,
            overwrite=args.overwrite,
        )
    except SnapshotE2RunFailed as exc:
        print(f"TEI revision B snapshot E2 run failed: {exc.cause}")
        print(f"- report: {exc.report_path}")
        return 1
    except version_exchange.EXPECTED_RUN_ERRORS as exc:
        print(f"TEI revision B snapshot E2 run rejected: {exc}")
        return 1

    report_path = args.output_dir.expanduser().resolve(strict=False) / REPORT_NAME
    if args.json:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    else:
        print("TEI revision B snapshot E2 partial Evidence: verified")
        print(f"- bundle: {result['bundleArchive']}")
        print(f"- report: {report_path}")
        print(result["stopLine"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
