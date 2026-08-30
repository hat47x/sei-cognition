#!/usr/bin/env python3
"""SOZA plan/ の次のADR / Issue IDを表示する。"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


ADR_FILE_RE = re.compile(r"ADR-(\d{4})-[^.]+\.md$")
ISSUE_FILE_RE = re.compile(r"ISSUE-(\d{6})-[^.]+\.md$")


def next_id(kind: str, repo_root: Path) -> str:
    if kind == "adr":
        directory = repo_root / "plan" / "adr"
        pattern = ADR_FILE_RE
        prefix = "ADR"
        width = 4
    else:
        directory = repo_root / "plan" / "issue"
        pattern = ISSUE_FILE_RE
        prefix = "ISSUE"
        width = 6

    numbers: list[int] = []
    for path in directory.glob("*.md"):
        match = pattern.fullmatch(path.name)
        if match:
            numbers.append(int(match.group(1)))

    number = max(numbers, default=0) + 1
    limit = 10**width - 1
    if number > limit:
        raise SystemExit(f"{prefix} IDの採番上限を超えました: {number}")

    return f"{prefix}-{number:0{width}d}"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="plan/adr または plan/issue のactual treeから次のIDを算出します。"
    )
    parser.add_argument("kind", choices=("adr", "issue"))
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    print(next_id(args.kind, repo_root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
