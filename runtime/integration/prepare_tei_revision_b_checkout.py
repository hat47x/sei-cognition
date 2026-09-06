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
    if normalized.exists():
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

        if output_repo.exists():
            raise ValueError(
                "publish直前にrevision B checkout output pathが作成されています: "
                f"{output_repo}"
            )
        staging_repo.rename(output_repo)
        published = True

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
            "outputRepository": str(output_repo),
            "revision": source_identity.REVISION_B,
            "detachedHead": True,
            "cloneMode": "local_no_hardlinks_no_checkout",
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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "既存TEI Git worktreeを変更せず、そのlocal Git object databaseから独立した"
            "ISSUE-000072 exact revision B detached checkoutを作成し、canonical source identityを検証します。"
        ),
        allow_abbrev=False,
    )
    parser.add_argument("--source-repo", required=True, type=Path)
    parser.add_argument("--output-repo", required=True, type=Path)
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = prepare_checkout(args.source_repo, args.output_repo)
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
        print(result["stopLine"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
