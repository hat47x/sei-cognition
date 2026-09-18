#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any

DEFAULT_OUTPUT = Path(
    "evaluation/personal-inquiry-decision/evidence/issue-000073/"
    "h2-shared-runner-selftest.json"
)
TEST_PATH = Path(
    "evaluation/personal-inquiry-decision/"
    "test_decision_continuity_review_runner.py"
)
SOURCE_FILES = (
    Path("tools/capture_issue_000073_h2_runner_selftest.py"),
    TEST_PATH,
    Path("evaluation/personal-inquiry-decision/inquiry_continuity_review_runner.py"),
    Path("evaluation/personal-inquiry-decision/matched_review_session.py"),
    Path("evaluation/personal-inquiry-decision/decision_continuity_review_analysis.py"),
    Path("evaluation/personal-inquiry-decision/inquiry_continuity_review_analysis.py"),
    Path("evaluation/personal-inquiry-decision/inquiry_continuity_review_evidence.py"),
    Path("evaluation/personal-inquiry-decision/inquiry_continuity_packet.py"),
    Path("evaluation/personal-inquiry-decision/decision_continuity_preflight.py"),
    Path("evaluation/personal-inquiry-decision/decision_continuity_counterfactual_matched_set_v1.json"),
    Path("evaluation/personal-inquiry-decision/decision_continuity_counterfactual_001.json"),
    Path("evaluation/personal-inquiry-decision/decision_continuity_counterfactual_002.json"),
    Path("evaluation/personal-inquiry-decision/decision_continuity_counterfactual_003.json"),
)
SCHEMA = "issue-000073-h2-shared-runner-selftest-evidence/v1"
STOP_LINE = (
    "H2 shared-runner regression PASS != H2 human review != H1 actual resume "
    "usability != Decision Continuity Product Value established."
)


def run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def git_text(repo: Path, *args: str) -> str:
    proc = run(["git", *args], repo)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "git command failed")
    return proc.stdout.strip()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_binding(repo: Path, rel: Path) -> dict[str, Any]:
    absolute = repo / rel
    working_blob = git_text(repo, "hash-object", "--", str(rel))
    head_blob = git_text(repo, "rev-parse", f"HEAD:{rel.as_posix()}")
    return {
        "path": rel.as_posix(),
        "git_blob": head_blob,
        "sha256": sha256_file(absolute),
        "working_tree_blob": working_blob,
        "matches_head": working_blob == head_blob,
    }


def record(
    *,
    status: str,
    repository: dict[str, Any] | None,
    environment: dict[str, str],
    sources: list[dict[str, Any]],
    execution: dict[str, Any] | None,
    detail: str | None = None,
) -> dict[str, Any]:
    value: dict[str, Any] = {
        "schema": SCHEMA,
        "issue": "ISSUE-000073",
        "status": status,
        "scope": (
            "Executable Evidence for the H2 shared-runner Decision regression "
            "test only; not H2 human review, not H1 actual resume usability, "
            "not Decision Continuity Product Value."
        ),
        "repository": repository,
        "environment": environment,
        "source_binding": sources,
        "execution": execution,
        "stop_line": STOP_LINE,
    }
    if detail:
        value["detail"] = detail
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Capture fail-closed executable evidence for the ISSUE-000073 "
            "H2 shared-runner Decision regression test."
        )
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--expected-head",
        required=True,
        help=(
            "Canonical repository commit SHA obtained independently of this checkout. "
            "The capture blocks unless git HEAD matches it exactly."
        ),
    )
    parser.add_argument("--replace", action="store_true")
    parser.add_argument("--repo", type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    repo = (args.repo or Path(__file__).resolve().parents[1]).resolve()
    output = args.output if args.output.is_absolute() else repo / args.output
    output = output.resolve()

    if output.exists() and not args.replace:
        print(json.dumps({
            "schema": SCHEMA,
            "status": "blocked",
            "output": str(output),
            "detail": "output already exists; use --replace only for an intentional rerun",
            "stop_line": STOP_LINE,
        }, ensure_ascii=False, indent=2))
        return 2

    python_version = run([sys.executable, "--version"], repo)
    git_version = run(["git", "--version"], repo)
    environment = {
        "python": (python_version.stdout or python_version.stderr).strip(),
        "git": (git_version.stdout or git_version.stderr).strip(),
    }

    try:
        head = git_text(repo, "rev-parse", "HEAD")
        head_tree = git_text(repo, "rev-parse", "HEAD^{tree}")
        dirty = git_text(repo, "status", "--porcelain=v1")
    except RuntimeError as exc:
        if args.replace:
            output.unlink(missing_ok=True)
        value = record(
            status="blocked",
            repository=None,
            environment=environment,
            sources=[],
            execution=None,
            detail=f"Git preflight failed: {exc}",
        )
        print(json.dumps(value, ensure_ascii=False, indent=2))
        return 2

    repository = {
        "head": head,
        "expected_head": args.expected_head,
        "head_matches_expected": head == args.expected_head,
        "head_tree": head_tree,
        "clean": dirty == "",
    }
    if head != args.expected_head:
        if args.replace:
            output.unlink(missing_ok=True)
        value = record(
            status="blocked",
            repository=repository,
            environment=environment,
            sources=[],
            execution=None,
            detail=(
                "checkout HEAD does not match independently supplied canonical "
                f"expected HEAD: actual={head} expected={args.expected_head}"
            ),
        )
        print(json.dumps(value, ensure_ascii=False, indent=2))
        return 2

    if dirty:
        if args.replace:
            output.unlink(missing_ok=True)
        value = record(
            status="blocked",
            repository=repository,
            environment=environment,
            sources=[],
            execution=None,
            detail="working tree is not clean",
        )
        print(json.dumps(value, ensure_ascii=False, indent=2))
        return 2

    sources: list[dict[str, Any]] = []
    try:
        for rel in SOURCE_FILES:
            absolute = repo / rel
            if not absolute.is_file():
                raise RuntimeError(f"required source not found: {rel.as_posix()}")
            bound = source_binding(repo, rel)
            if not bound["matches_head"]:
                raise RuntimeError(
                    f"required source does not match HEAD: {rel.as_posix()}"
                )
            sources.append(bound)
    except RuntimeError as exc:
        if args.replace:
            output.unlink(missing_ok=True)
        value = record(
            status="blocked",
            repository=repository,
            environment=environment,
            sources=sources,
            execution=None,
            detail=str(exc),
        )
        print(json.dumps(value, ensure_ascii=False, indent=2))
        return 2

    test_cmd = [sys.executable, TEST_PATH.as_posix()]
    test_proc = run(test_cmd, repo)
    execution = {
        "command": test_cmd,
        "cwd": str(repo),
        "exit_code": test_proc.returncode,
        "stdout": test_proc.stdout,
        "stderr": test_proc.stderr,
        "status": "pass" if test_proc.returncode == 0 else "fail",
    }
    status = "pass" if test_proc.returncode == 0 else "fail"
    value = record(
        status=status,
        repository=repository,
        environment=environment,
        sources=sources,
        execution=execution,
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=output.parent,
        prefix=output.name + ".tmp-",
        delete=False,
    ) as handle:
        temp = Path(handle.name)
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temp, output)

    print(json.dumps({
        "schema": "issue-000073-h2-shared-runner-selftest-capture/v1",
        "status": status,
        "output": str(output),
        "tested_head": head,
        "test_exit_code": test_proc.returncode,
        "stop_line": STOP_LINE,
    }, ensure_ascii=False, indent=2))
    return 0 if status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
