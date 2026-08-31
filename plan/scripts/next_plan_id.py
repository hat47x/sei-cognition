#!/usr/bin/env python3
"""actual treeから次のADR / Issue候補IDを表示する。

これは予約機構ではない。並行branchが同じ候補IDを取得する可能性があるため、
PR作成前・merge前には check_plan_registry.py と最新developとの差分を再確認する。
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def next_number(directory: Path, pattern: re.Pattern[str]) -> int:
    numbers: list[int] = []
    for path in directory.iterdir():
        if not path.is_file():
            continue
        match = pattern.fullmatch(path.name)
        if match:
            numbers.append(int(match.group(1)))
    return max(numbers, default=0) + 1


def main() -> int:
    parser = argparse.ArgumentParser(description="次のSOZA plan ID候補を表示する")
    parser.add_argument("kind", choices=("adr", "issue", "all"), nargs="?", default="all")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    adr_next = next_number(repo_root / "plan" / "adr", re.compile(r"ADR-(\d{4})-[^.]+\.md"))
    issue_next = next_number(repo_root / "plan" / "issue", re.compile(r"ISSUE-(\d{6})-[^.]+\.md"))

    if args.kind in ("adr", "all"):
        if adr_next > 9999:
            raise SystemExit("ADR ID空間を使い切っています。")
        print(f"ADR-{adr_next:04d}")
    if args.kind in ("issue", "all"):
        if issue_next > 999999:
            raise SystemExit("Issue ID空間を使い切っています。")
        print(f"ISSUE-{issue_next:06d}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
