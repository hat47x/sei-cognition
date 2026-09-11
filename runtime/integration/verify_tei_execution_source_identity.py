#!/usr/bin/env python3
import argparse
import json
import subprocess
from pathlib import Path
from typing import Mapping

import git_object_environment

REVISION_A = "48a7ca1fe8a9538e9e9be3e1ee08ef14804c8f67"
REVISION_B = "1a7028d444fcae60a1c4f2f2d247456f4c7c35be"
EXPECTED_OBJECTS = {
    "cmd": "ac4d4406dfa590a2078cf91217c4fe30797e7f8e",
    "internal": "10d2bfea4932c308fa6537e3b081bc6ea5501205",
    "reference": "57fafb742988ecb936b9ab261fa8a991e37ed5c7",
    "go.mod": "f8763f8fb2d64d73f1b40b905f62b5e09c44493b",
    "go.sum": "c7cd14781271dca2b014daf2f53d49d95b8e8826",
}
REVISION_A_REFERENCE_OBJECTS = {
    "reference/workspace": "5d596cfa5387b201cd733a07160307332d29a382",
    "reference/workspace/.tei/plugin-lock.json": "0fa63ad634c72395781eaaae5ee0132f73d03541",
    "reference/order_rollout.durable-run.m0.21.start.json": "6fe7b1586fcfd17f23f3b659df5632b31a6baf1f",
}
STOP_LINE = (
    "TEI execution-source Git identity verified != actual TEI binary built "
    "!= Provider Plan observed != SEI Adapter compatibility verified"
)


def _git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=check,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=git_object_environment.controlled_git_environment(),
    )


def _ensure_git_repository(repo: Path) -> None:
    result = _git(repo, "rev-parse", "--is-inside-work-tree", check=False)
    if result.returncode != 0 or result.stdout.strip() != "true":
        raise ValueError(f"Git repositoryではありません: {repo}")


def _worktree_status(repo: Path, paths: list[str]) -> list[str]:
    result = _git(
        repo,
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
        "--ignored=matching",
        "--",
        *paths,
    )
    return [line for line in result.stdout.splitlines() if line.strip()]


def verify_repository(
    repo: Path,
    *,
    expected_objects: Mapping[str, str] = EXPECTED_OBJECTS,
    expected_head: str | None = None,
) -> dict[str, object]:
    repo = repo.resolve()
    _ensure_git_repository(repo)

    paths = list(expected_objects)
    dirty = _worktree_status(repo, paths)
    if dirty:
        raise ValueError(
            "execution-source境界に未commit変更、untracked file、またはignored entryがあります: "
            + " | ".join(dirty)
        )

    head = _git(repo, "rev-parse", "HEAD").stdout.strip()
    if expected_head is not None and head != expected_head:
        raise ValueError(f"HEADが期待値と一致しません: expected={expected_head} actual={head}")

    observed: dict[str, str] = {}
    for path, expected_sha in expected_objects.items():
        result = _git(repo, "rev-parse", f"HEAD:{path}", check=False)
        if result.returncode != 0:
            raise ValueError(f"Git objectを取得できません: {path}")
        actual_sha = result.stdout.strip()
        observed[path] = actual_sha
        if actual_sha != expected_sha:
            raise ValueError(
                f"Git object identityが期待値と一致しません: path={path} "
                f"expected={expected_sha} actual={actual_sha}"
            )

    return {
        "schema": "soza.tei-execution-source-identity/v1",
        "result": "verified",
        "repositoryRoot": str(repo),
        "head": head,
        "expectedHead": expected_head,
        "expectedHeadMatched": expected_head is None or head == expected_head,
        "revisionBExactHead": head == REVISION_B,
        "executionSourceObjects": observed,
        "worktreeCleanWithinBoundary": True,
        "gitObjectEnvironmentControlled": True,
        "replaceObjectsDisabled": True,
        "qualityJudgement": "not_evaluated",
        "stopLine": STOP_LINE,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "TEI checkoutのcmd/internal/reference/go.mod/go.sumが、"
            "ISSUE-000072 revision Bの固定Git object identityと一致するか検証します。"
        )
    )
    parser.add_argument("--repo", required=True, type=Path, help="TEI Git repository root")
    parser.add_argument(
        "--require-head",
        help="必要な場合のみHEAD commitも固定する。省略時はexecution-source object identityだけを検証する。",
    )
    args = parser.parse_args()

    try:
        result = verify_repository(args.repo, expected_head=args.require_head)
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(json.dumps({"result": "rejected", "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
