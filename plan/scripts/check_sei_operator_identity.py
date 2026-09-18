#!/usr/bin/env python3
"""current operator / production integration surfaceへ旧SOZA操作tokenが再流入していないことを検査する。"""

from __future__ import annotations

import sys
from pathlib import Path

TARGET_GLOBS = (
    "runtime/TEI_VERSION_EXCHANGE_*.md",
    "runtime/TEI_PROVIDER_SURFACE_STATIC_COMPATIBILITY_*.md",
    "runtime/TEI_E2_PARTIAL_ACTUAL_RUNBOOK_*.md",
    "runtime/TEI_GITHUB_HOSTED_JOB_START_DELTA_*.md",
    "runtime/integration/*.py",
    "runtime/integration/*tei_version_exchange*.py",
    "runtime/integration/run_tei_bundle_adapter_compatibility.py",
    "runtime/integration/preflight_tei_version_exchange*.py",
    "runtime/integration/audit_tei_version_exchange*.py",
    "runtime/integration/reconcile_tei_e2_partial*.py",
)

OBSOLETE_OPERATIONAL_TOKENS = {
    "--soza-repo-root": "--sei-repo-root",
    "--soza-go-executable": "--sei-go-executable",
    "--expected-soza-head": "--expected-sei-head",
    "SOZA_REPO": "SEI_REPO",
    "SOZA_GO": "SEI_GO",
    "SOZA_HEAD": "SEI_HEAD",
    "soza_runtime_layout": "sei_runtime_layout",
    "soza_source_identity": "sei_source_identity",
    "soza_go_toolchain": "sei_go_toolchain",
    "soza_teiintegration_live_test": "sei_teiintegration_live_test",
    "sozaGoRequirement": "seiGoRequirement",
    "sozaGoVersion": "seiGoVersion",
    "sozaSource": "seiSource",
    "postLiveTestSozaSource": "postLiveTestSeiSource",
}


def operator_surface_files(repo_root: Path) -> list[Path]:
    paths: set[Path] = set()
    for pattern in TARGET_GLOBS:
        for path in repo_root.glob(pattern):
            if path.is_file() and not path.name.startswith("test_"):
                paths.add(path)
    return sorted(paths, key=lambda path: path.relative_to(repo_root).as_posix())


def check_repo(repo_root: Path) -> list[str]:
    errors: list[str] = []
    for path in operator_surface_files(repo_root):
        relative = path.relative_to(repo_root).as_posix()
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError as exc:
            errors.append(f"{relative}: UTF-8で読めません: {exc}")
            continue
        for line_number, line in enumerate(lines, start=1):
            for obsolete, replacement in OBSOLETE_OPERATIONAL_TOKENS.items():
                if obsolete in line:
                    errors.append(
                        f"{relative}:{line_number}: 旧operator token {obsolete!r} が残っています。"
                        f"{replacement!r} を使用してください"
                    )
    return errors


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    errors = check_repo(repo_root)
    if errors:
        print("SEI operator identity check: FAILED", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("SEI operator identity check: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
