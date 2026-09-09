#!/usr/bin/env python3
"""Current baselineでGitHub Actions workflowが再導入されていないことを検査する。"""

from __future__ import annotations

import sys
from pathlib import Path


def workflow_files(repo_root: Path) -> list[str]:
    workflows = repo_root / ".github" / "workflows"
    if not workflows.is_dir():
        return []
    return sorted(
        path.relative_to(repo_root).as_posix()
        for path in workflows.rglob("*")
        if path.is_file()
    )


def check_repo(repo_root: Path) -> list[str]:
    return [
        f"GitHub Actions workflowがcurrent baselineに存在します: {path}"
        for path in workflow_files(repo_root)
    ]


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    errors = check_repo(repo_root)
    if errors:
        print("GitHub Actions disabled baseline check: FAILED", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("GitHub Actions disabled baseline check: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
