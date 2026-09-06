#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path

import prepare_tei_revision_b_source as source_acquisition
import run_tei_version_exchange_evidence as version_exchange
from runtime_path_safety import reject_symlink_path_or_ancestors

SCHEMA = "soza.tei-version-exchange-github-acquisition-run/v1"
REPORT_NAME = "tei-version-exchange-github-acquisition.json"
SOURCE_TEMP_ENV_VARS = ("TMPDIR", "TEMP", "TMP")
SOURCE_TEMP_FALLBACK = "/tmp"
STOP_LINE = (
    "GitHub source acquisition + fixed-scope E2/E3 verified "
    "!= arbitrary TEI version compatibility != formal TEI distribution "
    "!= Operational Evidence != ISSUE-000072 Resolved"
)


class GitHubAcquiredVersionExchangeFailed(RuntimeError):
    def __init__(
        self,
        stage: str,
        report_path: Path,
        cause: Exception,
    ) -> None:
        super().__init__(f"{stage} failed: {cause}")
        self.stage = stage
        self.report_path = report_path
        self.cause = cause


class GitHubAcquiredVersionExchangePreflightBlocked(ValueError):
    def __init__(self, result: dict[str, object]) -> None:
        blocked = result.get("blockedChecks")
        blocked_checks = (
            [str(value) for value in blocked]
            if isinstance(blocked, list)
            else ["unknown"]
        )
        super().__init__("preflight blocked: " + ", ".join(blocked_checks))
        self.result = result
        self.blocked_checks = blocked_checks


def _token_from_environment() -> str:
    return os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""


def _credential_environment_for_preflight(token: str) -> dict[str, str]:
    if token and os.environ.get("GITHUB_TOKEN") == token:
        return {"GITHUB_TOKEN": token}
    if token and os.environ.get("GH_TOKEN") == token:
        return {"GH_TOKEN": token}
    # Programmatic callers may pass the already-resolved token directly. The
    # preflight only needs presence; the value is never included in its result.
    return {"GITHUB_TOKEN": token}


def _is_within(candidate: Path, root: Path) -> bool:
    return candidate == root or root in candidate.parents


def _requested_source_temp_parent() -> Path:
    for name in SOURCE_TEMP_ENV_VARS:
        value = os.environ.get(name)
        if value:
            return Path(value).expanduser()
    return Path(SOURCE_TEMP_FALLBACK)


def _prepare_source_temp_parent(
    output_dir: Path,
    soza_repo_root: Path,
    reference_source_repo: Path | None,
) -> Path:
    # tempfile.gettempdir() intentionally is not used here. Its first resolution
    # probes candidate directories by creating and deleting a file, which would
    # violate the side-effect-free preflight contract. Linux/amd64 is already an
    # execution precondition, so use the documented environment preference and
    # /tmp fallback without a write probe, then pass the verified path explicitly
    # to TemporaryDirectory during the actual run.
    requested = _requested_source_temp_parent()
    reject_symlink_path_or_ancestors(
        requested,
        "TEI GitHub source temporary parent",
    )
    resolved = requested.resolve(strict=True)
    if not resolved.is_dir():
        raise ValueError(
            f"TEI GitHub source temporary parentがdirectoryではありません: {resolved}"
        )
    if not os.access(resolved, os.W_OK | os.X_OK):
        raise ValueError(
            "TEI GitHub source temporary parentへwrite/traverseできません: "
            f"{resolved}"
        )

    roots: list[tuple[str, Path]] = [
        ("SOZA repository", soza_repo_root.expanduser().resolve(strict=False)),
        ("Evidence directory", output_dir.expanduser().resolve(strict=False)),
    ]
    if reference_source_repo is not None:
        roots.append(
            (
                "revision A reference checkout",
                reference_source_repo.expanduser().resolve(strict=False),
            )
        )

    for label, root in roots:
        if _is_within(resolved, root):
            raise ValueError(
                f"TEI GitHub source temporary parentを{label}配下には置けません: "
                f"temporaryParent={resolved} root={root}"
            )
    return resolved


def _run_preflight(
    reference_source_repo: Path | None,
    soza_repo_root: Path,
    output_dir: Path,
    *,
    reference_evidence_bundle: Path | None,
    tei_go_executable: Path,
    soza_go_executable: Path,
    token: str,
    expected_soza_head: str | None,
    overwrite: bool,
) -> dict[str, object]:
    # Lazy import keeps standalone preflight importable: that module references this
    # wrapper only for REPORT_NAME, while the actual one-shot path reaches here only
    # after this module has completed initialization.
    import preflight_tei_version_exchange_from_github as preflight

    return preflight.run_preflight(
        reference_source_repo,
        soza_repo_root,
        output_dir,
        reference_evidence_bundle=reference_evidence_bundle,
        tei_go_executable=tei_go_executable,
        soza_go_executable=soza_go_executable,
        expected_soza_head=expected_soza_head,
        overwrite=overwrite,
        env=_credential_environment_for_preflight(token),
    )


def _prepare_wrapper_report_path(output_dir: Path, *, overwrite: bool) -> Path:
    requested_dir = output_dir.expanduser()
    reject_symlink_path_or_ancestors(
        requested_dir,
        "TEI GitHub-acquired version exchange Evidence directory",
    )
    report = requested_dir.resolve(strict=False) / REPORT_NAME
    reject_symlink_path_or_ancestors(
        report,
        "TEI GitHub-acquired version exchange report",
    )
    if report.exists():
        if not overwrite:
            raise ValueError(
                "既存GitHub acquisition reportを無言で上書きしません。"
                f"--overwriteを明示してください: {report}"
            )
        if not report.is_file() and not report.is_symlink():
            raise ValueError(f"GitHub acquisition report出力先がfileではありません: {report}")
    return report


def _write_report(
    path: Path,
    value: dict[str, object],
    *,
    overwrite: bool,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    reject_symlink_path_or_ancestors(
        path,
        "TEI GitHub-acquired version exchange report",
    )
    if path.exists():
        if not overwrite:
            raise ValueError(
                "GitHub acquisition reportが実行中に作成されました。暗黙上書きしません: "
                f"{path}"
            )
        if not path.is_file():
            raise ValueError(f"GitHub acquisition report出力先がfileではありません: {path}")

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
            json.dump(value, handle, ensure_ascii=False, sort_keys=True, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())

        reject_symlink_path_or_ancestors(
            path,
            "TEI GitHub-acquired version exchange report",
        )
        if path.exists():
            if not overwrite:
                raise ValueError(
                    "GitHub acquisition reportがpublish直前に作成されました。"
                    f"暗黙上書きしません: {path}"
                )
            if not path.is_file():
                raise ValueError(
                    f"GitHub acquisition report出力先がfileではありません: {path}"
                )
        os.replace(candidate, path)
        candidate = None
    finally:
        if candidate is not None and candidate.exists() and not candidate.is_symlink():
            candidate.unlink()


def _source_provenance(acquisition: dict[str, object]) -> dict[str, object]:
    canonical = acquisition.get("canonicalSourceVerification")
    canonical_summary: dict[str, object] | None = None
    if isinstance(canonical, dict):
        canonical_summary = {
            key: canonical.get(key)
            for key in (
                "head",
                "expectedHead",
                "expectedHeadMatched",
                "revisionBExactHead",
                "executionSourceObjects",
                "worktreeCleanWithinBoundary",
            )
            if key in canonical
        }

    return {
        "mode": acquisition.get("sourceAcquisition"),
        "repository": acquisition.get("repository"),
        "sourceCommit": acquisition.get("sourceCommit"),
        "rootTree": acquisition.get("rootTree"),
        "credentialSource": acquisition.get("credentialSource"),
        "objectAcquisition": acquisition.get("objectAcquisition"),
        "canonicalSourceVerification": canonical_summary,
    }


def run_from_github(
    reference_source_repo: Path | None,
    soza_repo_root: Path,
    output_dir: Path,
    *,
    reference_evidence_bundle: Path | None = None,
    tei_go_executable: Path,
    soza_go_executable: Path,
    token: str,
    expected_soza_head: str | None = None,
    overwrite: bool = False,
) -> dict[str, object]:
    if not token:
        raise ValueError("GitHub API tokenがありません")

    preflight_result = _run_preflight(
        reference_source_repo,
        soza_repo_root,
        output_dir,
        reference_evidence_bundle=reference_evidence_bundle,
        tei_go_executable=tei_go_executable,
        soza_go_executable=soza_go_executable,
        token=token,
        expected_soza_head=expected_soza_head,
        overwrite=overwrite,
    )
    if preflight_result.get("ready") is not True:
        raise GitHubAcquiredVersionExchangePreflightBlocked(preflight_result)

    source_temp_parent = _prepare_source_temp_parent(
        output_dir,
        soza_repo_root,
        reference_source_repo,
    )
    requested_report = _prepare_wrapper_report_path(output_dir, overwrite=overwrite)

    with tempfile.TemporaryDirectory(
        prefix="soza-tei-b-github-source-",
        dir=source_temp_parent,
    ) as tmp:
        source_repo = Path(tmp) / "tei-revision-b"
        acquisition = source_acquisition.materialize_revision_b_source(
            source_repo,
            token=token,
        )
        provenance = _source_provenance(acquisition)

        try:
            exchange = version_exchange.run_version_exchange(
                source_repo,
                reference_source_repo,
                soza_repo_root,
                output_dir,
                reference_evidence_bundle=reference_evidence_bundle,
                tei_go_executable=tei_go_executable,
                soza_go_executable=soza_go_executable,
                expected_soza_head=expected_soza_head,
                overwrite=overwrite,
            )
        except version_exchange.VersionExchangeRunFailed as exc:
            report_path = exc.report_path.parent / REPORT_NAME
            report = {
                "schema": SCHEMA,
                "result": "version_exchange_failed",
                "sourceAcquisition": provenance,
                "canonicalVersionExchangeReport": str(exc.report_path),
                "failure": {
                    "stage": exc.stage,
                    "type": type(exc.cause).__name__,
                    "message": str(exc.cause),
                },
                "qualityJudgement": "not_evaluated",
                "stopLine": STOP_LINE,
            }
            _write_report(report_path, report, overwrite=overwrite)
            raise GitHubAcquiredVersionExchangeFailed(
                exc.stage,
                report_path,
                exc.cause,
            ) from exc

    report_path = requested_report
    report = {
        "schema": SCHEMA,
        "result": exchange["result"],
        "sourceAcquisition": provenance,
        "canonicalVersionExchangeReport": str(
            output_dir.expanduser().resolve(strict=False) / version_exchange.REPORT_NAME
        ),
        "versionExchange": {
            "result": exchange["result"],
            "comparisonAxis": exchange.get("comparisonAxis"),
            "bundleArchive": exchange.get("bundleArchive"),
        },
        "qualityJudgement": "not_evaluated",
        "stopLine": STOP_LINE,
    }
    _write_report(report_path, report, overwrite=overwrite)
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "GitHub Git Data APIからexact revision B sourceをcontent-addressedに取得し、"
            "副作用なしpreflightがreadyであることを確認してから、取得済みexact-B checkoutを"
            "既存canonical E2→E3 runnerへそのまま渡します。credentialは"
            "GITHUB_TOKEN/GH_TOKENからのみ取得し、reportへ保存しません。"
        ),
        allow_abbrev=False,
    )
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
        token = _token_from_environment()
        if not token:
            raise ValueError(
                "GITHUB_TOKENまたはGH_TOKENをenvironmentへ設定してください"
            )
        result = run_from_github(
            args.reference_source_repo,
            args.soza_repo_root,
            args.output_dir,
            reference_evidence_bundle=args.reference_evidence_bundle,
            tei_go_executable=args.tei_go_executable,
            soza_go_executable=args.soza_go_executable,
            token=token,
            expected_soza_head=args.expected_soza_head,
            overwrite=args.overwrite,
        )
    except GitHubAcquiredVersionExchangePreflightBlocked as exc:
        print(
            "TEI GitHub-acquired version exchange preflight blocked: "
            + ", ".join(exc.blocked_checks)
        )
        return 1
    except GitHubAcquiredVersionExchangeFailed as exc:
        print(
            "TEI GitHub-acquired version exchange run failed at "
            f"{exc.stage}: {exc.cause}"
        )
        print(f"- report: {exc.report_path}")
        return 1
    except (OSError, ValueError) as exc:
        print(f"TEI GitHub-acquired version exchange run rejected: {exc}")
        return 1

    report_path = args.output_dir.expanduser().resolve(strict=False) / REPORT_NAME
    if args.json:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    else:
        print("TEI GitHub acquisition + fixed-scope E2/E3: verified")
        print(f"- source acquisition: {result['sourceAcquisition']['mode']}")
        print(f"- report: {report_path}")
        print(result["stopLine"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
