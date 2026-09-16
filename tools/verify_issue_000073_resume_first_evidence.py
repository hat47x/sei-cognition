#!/usr/bin/env python3
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any

from run_issue_000073_resume_first_evidence import EXPERIMENTS, SOURCE_FILES

FORMAT = "issue-000073-resume-first-execution-record/v1"
ISSUE = "ISSUE-000073"
STOP_LINE = "Executable E1-E8 PASS != H1/H2 human review != Decision Continuity Product Value established."
GO_VERSION_RE = re.compile(r"\bgo1\.25(?:\.\d+)?\b")
HEX40_RE = re.compile(r"^[0-9a-f]{40}$")


@dataclass(frozen=True)
class Finding:
    code: str
    message: str


@dataclass
class Report:
    schema: str
    passed: bool
    tested_head: str | None
    findings: list[Finding]

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["findings"] = [asdict(item) for item in self.findings]
        return data


def run_bytes(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def git_text(repo: Path, *args: str) -> str | None:
    proc = run_bytes(["git", *args], repo)
    if proc.returncode != 0:
        return None
    return proc.stdout.decode("utf-8", errors="strict").strip()


def git_bytes(repo: Path, *args: str) -> bytes | None:
    proc = run_bytes(["git", *args], repo)
    return proc.stdout if proc.returncode == 0 else None


def validate(repo: Path, record: dict[str, Any]) -> Report:
    findings: list[Finding] = []

    def add(code: str, message: str) -> None:
        findings.append(Finding(code, message))

    if record.get("format") != FORMAT:
        add("format", f"unexpected format: {record.get('format')!r}")
    if record.get("issue") != ISSUE:
        add("issue", f"unexpected issue: {record.get('issue')!r}")
    if record.get("status") != "pass":
        add("status", f"evidence status is not pass: {record.get('status')!r}")
    if record.get("required_toolchain") != "go1.25.x":
        add("toolchain-declaration", "required_toolchain must be go1.25.x")
    if record.get("stop_line") != STOP_LINE:
        add("stop-line", "required Evidence stop line is missing or changed")

    repository = record.get("repository")
    if not isinstance(repository, dict):
        repository = {}
        add("repository", "repository metadata is missing")

    head = repository.get("head")
    if not isinstance(head, str) or not HEX40_RE.fullmatch(head):
        add("head", f"repository.head is not a full commit SHA: {head!r}")
        head = None

    if repository.get("clean_required") is not True:
        add("clean-required", "clean_required must be true")
    if repository.get("dirty") is not False:
        add("dirty", "tested checkout was not recorded as clean")
    if repository.get("status_porcelain") not in ([], None):
        add("status-porcelain", "status_porcelain must be empty for PASS evidence")
    if repository.get("git_checkout_detected") is not True:
        add("git-checkout", "git checkout was not positively detected")

    head_available = False
    if head is not None:
        head_available = git_text(repo, "cat-file", "-t", head) == "commit"
        if not head_available:
            add("head-unavailable", f"recorded tested commit is not available locally: {head}")
        else:
            expected_tree = git_text(repo, "rev-parse", f"{head}^{{tree}}")
            recorded_tree = repository.get("head_tree")
            if not isinstance(recorded_tree, str) or not HEX40_RE.fullmatch(recorded_tree):
                add("head-tree", f"repository.head_tree is invalid: {recorded_tree!r}")
            elif recorded_tree != expected_tree:
                add("head-tree-mismatch", f"recorded tree {recorded_tree} != tested HEAD tree {expected_tree}")

    go = record.get("go")
    if not isinstance(go, dict):
        go = {}
        add("go", "go metadata is missing")
    version_output = go.get("version_output")
    if not isinstance(version_output, str) or not GO_VERSION_RE.search(version_output):
        add("go-version", f"Go 1.25.x was not recorded: {version_output!r}")

    command = record.get("command")
    if not isinstance(command, dict):
        command = {}
        add("command", "command metadata is missing")
    if command.get("cwd") != "runtime/go":
        add("command-cwd", f"unexpected command cwd: {command.get('cwd')!r}")
    argv = command.get("argv")
    if not isinstance(argv, list) or len(argv) < 5 or argv[1:] != ["test", "-count=1", "-json", "./interactionprobe"]:
        add("command-argv", f"unexpected test command: {argv!r}")
    if command.get("environment") != {"GOTOOLCHAIN": "local"}:
        add("command-env", "GOTOOLCHAIN=local was not recorded exactly")
    if command.get("exit_code") != 0:
        add("command-exit", f"go test exit code was not zero: {command.get('exit_code')!r}")

    bindings = record.get("source_bindings")
    if not isinstance(bindings, list):
        bindings = []
        add("source-bindings", "source_bindings is missing")

    by_path: dict[str, dict[str, Any]] = {}
    for item in bindings:
        if not isinstance(item, dict) or not isinstance(item.get("path"), str):
            add("source-binding-entry", "source binding entry is malformed")
            continue
        path = item["path"]
        if path in by_path:
            add("source-binding-duplicate", f"duplicate source binding: {path}")
        by_path[path] = item

    expected_paths = set(SOURCE_FILES)
    actual_paths = set(by_path)
    for path in sorted(expected_paths - actual_paths):
        add("source-binding-missing", f"required source binding missing: {path}")
    for path in sorted(actual_paths - expected_paths):
        add("source-binding-extra", f"unexpected source binding present: {path}")

    if head_available and head is not None:
        for path in SOURCE_FILES:
            item = by_path.get(path)
            if item is None:
                continue
            if item.get("exists") is not True or item.get("matches_head") is not True:
                add("source-binding-state", f"{path} was not recorded as present and HEAD-matching")
                continue

            expected_blob = git_text(repo, "rev-parse", f"{head}:{path}")
            if expected_blob is None:
                add("source-at-head", f"{path} is not present at recorded HEAD")
                continue

            for field in ("working_tree_blob", "head_blob"):
                value = item.get(field)
                if not isinstance(value, str) or not HEX40_RE.fullmatch(value):
                    add("source-blob-format", f"{path} {field} is invalid: {value!r}")
                elif value != expected_blob:
                    add("source-blob-mismatch", f"{path} {field} {value} != recorded HEAD blob {expected_blob}")

            data = git_bytes(repo, "show", f"{head}:{path}")
            if data is None:
                add("source-bytes", f"could not read {path} bytes from recorded HEAD")
            else:
                expected_sha256 = hashlib.sha256(data).hexdigest()
                if item.get("sha256") != expected_sha256:
                    add("source-sha256", f"{path} sha256 does not match recorded HEAD bytes")

    test_results = record.get("test_results")
    if not isinstance(test_results, dict):
        test_results = {}
        add("test-results", "test_results is missing")

    experiments = record.get("experiments")
    if not isinstance(experiments, dict):
        experiments = {}
        add("experiments", "experiments is missing")
    if set(experiments) != set(EXPERIMENTS):
        add("experiment-set", f"experiment set differs: {sorted(experiments)}")

    for key, required in EXPERIMENTS.items():
        exp = experiments.get(key)
        if not isinstance(exp, dict):
            add("experiment-missing", f"{key} result is missing")
            continue
        if exp.get("required_tests") != required:
            add("required-tests", f"{key} required_tests differs from current runner mapping")
        if exp.get("status") != "pass":
            add("experiment-status", f"{key} is not pass: {exp.get('status')!r}")
        if exp.get("missing_tests") not in ([], None):
            add("experiment-missing-tests", f"{key} has missing tests: {exp.get('missing_tests')!r}")
        if exp.get("non_pass_tests") not in ([], None):
            add("experiment-non-pass", f"{key} has non-pass tests: {exp.get('non_pass_tests')!r}")
        for test in required:
            if test_results.get(test) != "pass":
                add("test-not-pass", f"{key} required test did not pass: {test}={test_results.get(test)!r}")

    return Report(
        schema="issue-000073-resume-first-evidence-verification/v1",
        passed=not findings,
        tested_head=head,
        findings=findings,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify captured ISSUE-000073 E1-E8 executable evidence.")
    parser.add_argument("evidence", type=Path)
    parser.add_argument("--repo", type=Path, help="Repository checkout used to resolve the recorded tested commit.")
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()

    repo = (args.repo or Path(__file__).resolve().parents[1]).resolve()
    try:
        record = json.loads(args.evidence.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        report = Report(
            schema="issue-000073-resume-first-evidence-verification/v1",
            passed=False,
            tested_head=None,
            findings=[Finding("evidence-read", str(exc))],
        )
    else:
        report = validate(repo, record if isinstance(record, dict) else {})

    text = json.dumps(report.to_dict(), ensure_ascii=False, indent=2) + "\n"
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text, encoding="utf-8")
        print(f"wrote {args.json_out}")
    else:
        sys.stdout.write(text)
    return 0 if report.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
