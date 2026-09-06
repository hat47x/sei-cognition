#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import runtime_path_safety as path_safety
import verify_tei_execution_source_identity as source_identity

STOP_LINE = (
    "independent exact revision B checkout prepared and source identity verified "
    "!= revision B build PASS != Provider Plan execution PASS "
    "!= SOZA Adapter compatibility PASS != ISSUE-000072 Resolved"
)


def _git(
    repo: Path,
    *args: str,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=check,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def _run(argv: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        argv,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def _ensure_git_worktree(repo: Path) -> None:
    result = _git(repo, "rev-parse", "--is-inside-work-tree", check=False)
    if result.returncode != 0 or result.stdout.strip() != "true":
        raise ValueError(f"TEI Git worktreeではありません: {repo}")


def _git_path(repo: Path, path: str) -> Path:
    result = _git(repo, "rev-parse", "--git-path", path)
    value = Path(result.stdout.strip())
    if not value.is_absolute():
        value = repo / value
    return value


def _alternate_object_databases(repo: Path) -> list[str]:
    alternates = _git_path(repo, "objects/info/alternates")
    if not alternates.exists():
        return []
    if not alternates.is_file():
        raise ValueError(
            "Git object alternates pathがregular fileではありません: "
            f"{alternates}"
        )
    try:
        lines = alternates.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise ValueError(
            f"Git object alternatesを読み取れません: path={alternates} error={exc}"
        ) from exc
    return [line.strip() for line in lines if line.strip()]


def _ensure_self_contained_object_database(repo: Path, label: str) -> None:
    alternates = _alternate_object_databases(repo)
    if alternates:
        raise ValueError(
            f"{label} Git object databaseがalternate object databaseへ依存しています: "
            + " | ".join(alternates)
        )


def _source_state(repo: Path) -> dict[str, object]:
    head = _git(repo, "rev-parse", "HEAD").stdout.strip()
    status = _git(
        repo,
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
    ).stdout.splitlines()
    return {
        "head": head,
        "status": [line for line in status if line.strip()],
    }


def _ensure_revision_available(repo: Path) -> None:
    result = _git(
        repo,
        "cat-file",
        "-e",
        f"{source_identity.REVISION_B}^{{commit}}",
        check=False,
    )
    if result.returncode != 0:
        raise ValueError(
            "source cloneにISSUE-000072 revision B commit objectがありません: "
            f"revision={source_identity.REVISION_B}. "
            "このhelperはsource cloneをfetchしません。必要なobjectをsource側へ取得してから再実行してください。"
        )


def _normalized_new_output(path: Path) -> Path:
    requested = path_safety.lexical_absolute_path(path)
    path_safety.reject_symlink_path_or_ancestors(
        requested,
        "revision B checkout output",
    )
    normalized = Path(os.path.abspath(str(requested)))
    if normalized.exists() or normalized.is_symlink():
        raise ValueError(f"revision B checkout outputは新規pathである必要があります: {normalized}")
    if not normalized.parent.is_dir():
        raise ValueError(
            "revision B checkout outputのparent directoryが存在しません: "
            f"{normalized.parent}"
        )
    return normalized


def _reject_source_output_overlap(source_repo: Path, output_repo: Path) -> None:
    if source_repo == output_repo:
        raise ValueError("source cloneとrevision B checkout outputを同じpathにはできません")
    if source_repo in output_repo.parents:
        raise ValueError(
            "revision B checkout outputをsource clone配下へ作成できません: "
            f"source={source_repo} output={output_repo}"
        )
    if output_repo in source_repo.parents:
        raise ValueError(
            "source cloneを包含するpathをrevision B checkout outputにはできません: "
            f"source={source_repo} output={output_repo}"
        )


def _prepare_report_output(
    report_output: Path,
    *,
    source_repo: Path,
    output_repo: Path,
) -> Path:
    requested = path_safety.lexical_absolute_path(report_output)
    path_safety.reject_symlink_path_or_ancestors(
        requested,
        "revision B checkout preparation report",
    )
    report = Path(os.path.abspath(str(requested)))
    if os.path.lexists(report):
        raise ValueError(
            "checkout preparation reportは新規pathである必要があります: "
            f"{report}"
        )
    if not report.parent.is_dir():
        raise ValueError(
            "checkout preparation reportのparent directoryが存在しません: "
            f"{report.parent}"
        )
    for label, root in (
        ("source clone", source_repo),
        ("revision B checkout output", output_repo),
    ):
        if report == root or root in report.parents:
            raise ValueError(
                f"checkout preparation reportを{label}配下には置けません: "
                f"report={report} root={root}"
            )
    return report


def _write_json_no_overwrite(path: Path, value: dict[str, object]) -> None:
    path_safety.reject_symlink_path_or_ancestors(
        path,
        "revision B checkout preparation report",
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
            json.dump(value, handle, ensure_ascii=False, sort_keys=True, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())

        path_safety.reject_symlink_path_or_ancestors(
            path,
            "revision B checkout preparation report",
        )
        try:
            os.link(candidate, path)
        except FileExistsError as exc:
            raise ValueError(
                "checkout preparation reportがpublish前に作成されています。暗黙上書きしません: "
                f"{path}"
            ) from exc
        candidate.unlink()
        candidate = None
    finally:
        if candidate is not None and candidate.exists() and not candidate.is_symlink():
            candidate.unlink()


def _ensure_detached_head(repo: Path) -> None:
    symbolic = _git(repo, "symbolic-ref", "-q", "HEAD", check=False)
    if symbolic.returncode == 0:
        raise ValueError(
            "prepared revision B checkoutがdetached HEADではありません: "
            f"symbolic={symbolic.stdout.strip()}"
        )


def prepare_checkout(source_repo: Path, output_repo: Path) -> dict[str, object]:
    source_repo = source_repo.expanduser().resolve(strict=True)
    _ensure_git_worktree(source_repo)
    _ensure_self_contained_object_database(source_repo, "source clone")
    _ensure_revision_available(source_repo)
    source_before = _source_state(source_repo)

    output_repo = _normalized_new_output(output_repo)
    _reject_source_output_overlap(source_repo, output_repo)

    staging_root = Path(
        tempfile.mkdtemp(
            prefix=f".{output_repo.name}.prepare-",
            dir=output_repo.parent,
        )
    )
    staging_repo = staging_root / "checkout"
    published = False

    try:
        _run(
            [
                "git",
                "clone",
                "--local",
                "--no-hardlinks",
                "--no-checkout",
                "--quiet",
                str(source_repo),
                str(staging_repo),
            ]
        )
        _ensure_self_contained_object_database(staging_repo, "staging checkout")
        _git(staging_repo, "config", "core.autocrlf", "false")
        _git(
            staging_repo,
            "checkout",
            "--detach",
            "--quiet",
            source_identity.REVISION_B,
        )
        _ensure_detached_head(staging_repo)

        source_identity.verify_repository(
            staging_repo,
            expected_head=source_identity.REVISION_B,
        )

        source_after_checkout = _source_state(source_repo)
        if source_after_checkout != source_before:
            raise ValueError(
                "checkout preparation中にsource cloneのHEADまたはworking-tree statusが変化しました"
            )

        if output_repo.exists() or output_repo.is_symlink():
            raise ValueError(
                "publish直前にrevision B checkout output pathが作成されています: "
                f"{output_repo}"
            )
        staging_repo.rename(output_repo)
        published = True

        _ensure_self_contained_object_database(output_repo, "published checkout")
        verification = source_identity.verify_repository(
            output_repo,
            expected_head=source_identity.REVISION_B,
        )
        _ensure_detached_head(output_repo)

        source_after_publish = _source_state(source_repo)
        if source_after_publish != source_before:
            raise ValueError(
                "checkout publish中にsource cloneのHEADまたはworking-tree statusが変化しました"
            )

        return {
            "schema": "soza.tei-revision-b-checkout-preparation/v1",
            "result": "prepared_verified",
            "sourceRepository": str(source_repo),
            "sourceStateBefore": source_before,
            "sourceStateAfter": source_after_publish,
            "sourceHeadAndStatusUnchanged": True,
            "sourceObjectDatabaseSelfContained": True,
            "outputRepository": str(output_repo),
            "revision": source_identity.REVISION_B,
            "detachedHead": True,
            "cloneMode": "local_no_hardlinks_no_checkout",
            "outputObjectDatabaseSelfContained": True,
            "prePublishIdentityVerified": True,
            "verification": verification,
            "qualityJudgement": "not_evaluated",
            "stopLine": STOP_LINE,
        }
    except (OSError, ValueError, subprocess.SubprocessError):
        if published and output_repo.exists() and not output_repo.is_symlink():
            shutil.rmtree(output_repo)
        raise
    finally:
        if staging_root.exists() and not staging_root.is_symlink():
            shutil.rmtree(staging_root)


def prepare_checkout_with_report(
    source_repo: Path,
    output_repo: Path,
    report_output: Path,
) -> dict[str, object]:
    source = source_repo.expanduser().resolve(strict=True)
    output = _normalized_new_output(output_repo)
    _reject_source_output_overlap(source, output)
    report = _prepare_report_output(
        report_output,
        source_repo=source,
        output_repo=output,
    )

    result = prepare_checkout(source, output)
    try:
        _write_json_no_overwrite(report, result)
    except (OSError, ValueError):
        if output.exists() and output.is_dir() and not output.is_symlink():
            shutil.rmtree(output)
        raise
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "既存TEI Git worktreeを変更せず、そのself-containedなlocal Git object databaseから"
            "独立したISSUE-000072 exact revision B detached checkoutを作成し、"
            "canonical source identityを検証します。"
        ),
        allow_abbrev=False,
    )
    parser.add_argument("--source-repo", required=True, type=Path)
    parser.add_argument("--output-repo", required=True, type=Path)
    parser.add_argument(
        "--report-output",
        type=Path,
        help=(
            "checkout preparation provenance JSONを安全な新規pathへ保存する。"
            "source / output checkout配下は拒否する。"
        ),
    )
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.report_output is None:
            result = prepare_checkout(args.source_repo, args.output_repo)
        else:
            result = prepare_checkout_with_report(
                args.source_repo,
                args.output_repo,
                args.report_output,
            )
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(f"TEI revision B checkout preparation failed: {exc}")
        return 1

    if args.json:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    else:
        print("TEI revision B checkout preparation: verified")
        print(f"- source repository: {result['sourceRepository']}")
        print(f"- output repository: {result['outputRepository']}")
        print(f"- revision: {result['revision']}")
        if args.report_output is not None:
            print(f"- report: {args.report_output.expanduser().resolve()}")
        print(result["stopLine"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
