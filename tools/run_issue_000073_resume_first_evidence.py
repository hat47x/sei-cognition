#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import Any

EXPERIMENTS: dict[str, list[str]] = {
    "E1": [
        "TestResumeProjectionRebuildsFromCanonicalStateAfterSurfaceLoss",
        "TestResumeProjectionDoesNotRewriteHistoricalBasisWithLaterObservation",
        "TestChangeReviewProjectionSeparatesHistoricalBasisFromCanonicalChanges",
        "TestChangeReviewProjectionReconstructsFromCanonicalRecordsAfterStoreRebuild",
    ],
    "E2": [
        "TestProvisionalRecommendationDoesNotBecomeCanonicalUntilCommit",
        "TestDismissedProvisionalRecommendationLeavesCanonicalStateUntouched",
        "TestProvisionalRecommendationCanBeReclassifiedAsObservationBeforeCommit",
    ],
    "E3": ["TestAIUnavailableKeepsHumanCanonicalPathUsable"],
    "E4": ["TestProgressiveExplicitnessPreservesInquiryIdentityAsDetailAccumulates"],
    "E5": ["TestWorkingSetProjectionRebuildsFromCanonicalRelationsAfterLocalStateLoss"],
    "E6": [
        "TestCommitCoordinatorPublishesSemanticChangesTogether",
        "TestCommitCoordinatorDoesNotExposePartialStateOnInjectedFailure",
        "TestCommitCoordinatorDoesNotPublishEarlierChangesWhenLaterValidationFails",
    ],
    "E7": [
        "TestStaleDraftCommitRequiresFreshProposal",
        "TestReclassifiedObservationKeepsOriginalSnapshotPrecondition",
    ],
    "E8": [
        "TestContextEgressPlanContainsOnlySelectedCanonicalRecords",
        "TestExternalRecommendationRemainsProvisionalUntilExplicitCommit",
        "TestExternalRecommendationUsesEgressSnapshotForStaleProtection",
    ],
}

SOURCE_FILES = [
    "tools/run_issue_000073_resume_first_evidence.py",
    "runtime/go/go.mod",
    "runtime/go/go.sum",
    "runtime/go/interactionprobe/resume_test.go",
    "runtime/go/interactionprobe/review_test.go",
    "runtime/go/interactionprobe/provisional_test.go",
    "runtime/go/interactionprobe/provisional_observation_test.go",
    "runtime/go/interactionprobe/graceful_degradation_test.go",
    "runtime/go/interactionprobe/progressive_test.go",
    "runtime/go/interactionprobe/working_set_test.go",
    "runtime/go/interactionprobe/commit_test.go",
    "runtime/go/interactionprobe/egress_test.go",
]


def run(cmd: list[str], cwd: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def git_text(repo: Path, *args: str) -> str | None:
    proc = run(["git", *args], repo)
    return proc.stdout.strip() if proc.returncode == 0 else None


def source_binding(repo: Path, relative: str) -> dict[str, Any]:
    path = repo / relative
    result: dict[str, Any] = {"path": relative, "exists": path.is_file()}
    if not path.is_file():
        return result
    data = path.read_bytes()
    result["sha256"] = hashlib.sha256(data).hexdigest()
    working_blob = git_text(repo, "hash-object", "--", relative)
    head_blob = git_text(repo, "rev-parse", f"HEAD:{relative}")
    if working_blob:
        result["working_tree_blob"] = working_blob
    if head_blob:
        result["head_blob"] = head_blob
    if working_blob and head_blob:
        result["matches_head"] = working_blob == head_blob
    return result


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def write_evidence(record: dict[str, Any], output: str | None) -> None:
    text = json.dumps(record, ensure_ascii=False, indent=2) + "\n"
    if output:
        path = Path(output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        print(f"wrote {path}")
    else:
        sys.stdout.write(text)


def block(record: dict[str, Any], reason: str, output: str | None) -> int:
    record.update({"status": "blocked", "blocked_reason": reason})
    write_evidence(record, output)
    return 2


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture ISSUE-000073 E1-E8 executable evidence.")
    parser.add_argument("--output", help="Write the JSON evidence record to this path; stdout when omitted.")
    parser.add_argument("--go", dest="go_executable", help="Go executable to use; defaults to PATH lookup.")
    args = parser.parse_args()

    repo = Path(__file__).resolve().parents[1]
    runtime_go = repo / "runtime" / "go"
    go = args.go_executable or shutil.which("go")
    head = git_text(repo, "rev-parse", "HEAD")
    head_tree = git_text(repo, "rev-parse", "HEAD^{tree}")
    status = git_text(repo, "status", "--porcelain=v1")
    source_bindings = [source_binding(repo, p) for p in SOURCE_FILES]

    record: dict[str, Any] = {
        "format": "issue-000073-resume-first-execution-record/v1",
        "issue": "ISSUE-000073",
        "observed_at": now_utc(),
        "scope": "Executable Evidence for E1-E8 only; H1/H2 and Product Outcome are out of scope.",
        "repository": {
            "head": head,
            "head_tree": head_tree,
            "git_checkout_detected": head is not None and status is not None,
            "clean_required": True,
            "dirty": bool(status),
            "status_porcelain": status.splitlines() if status else [],
        },
        "required_toolchain": "go1.25.x",
        "source_bindings": source_bindings,
        "experiments": {key: {"required_tests": tests, "status": "not_run"} for key, tests in EXPERIMENTS.items()},
        "stop_line": "Executable E1-E8 PASS != H1/H2 human review != Decision Continuity Product Value established.",
    }

    if head is None or status is None:
        return block(record, "runner must execute inside a Git checkout with a readable HEAD and working-tree status", args.output)
    if status:
        return block(
            record,
            "working tree is dirty; executable evidence must be bound to a clean committed HEAD before E1-E8 can PASS",
            args.output,
        )

    missing_bindings = [item["path"] for item in source_bindings if not item.get("exists")]
    mismatched_bindings = [
        item["path"]
        for item in source_bindings
        if item.get("exists") and item.get("matches_head") is not True
    ]
    if missing_bindings:
        record["missing_source_bindings"] = missing_bindings
        return block(record, "one or more required evidence source files are missing", args.output)
    if mismatched_bindings:
        record["mismatched_source_bindings"] = mismatched_bindings
        return block(record, "one or more required evidence source files do not match HEAD", args.output)

    if not runtime_go.is_dir():
        return block(record, "runtime/go directory not found", args.output)
    if not go:
        return block(record, "go executable not found", args.output)

    version_proc = run([go, "version"], repo)
    version_text = (version_proc.stdout or version_proc.stderr).strip()
    record["go"] = {"executable": go, "version_output": version_text}
    if version_proc.returncode != 0 or not re.search(r"\bgo1\.25(?:\.\d+)?\b", version_text):
        return block(
            record,
            "declared Go 1.25.x toolchain is not active; lower-version execution is not accepted as ISSUE-000073 PASS",
            args.output,
        )

    env = os.environ.copy()
    env["GOTOOLCHAIN"] = "local"
    command = [go, "test", "-count=1", "-json", "./interactionprobe"]
    test_proc = run(command, runtime_go, env=env)
    record["command"] = {
        "cwd": "runtime/go",
        "argv": command,
        "environment": {"GOTOOLCHAIN": "local"},
        "exit_code": test_proc.returncode,
    }

    test_results: dict[str, str] = {}
    parse_errors: list[str] = []
    for line in test_proc.stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            parse_errors.append(line)
            continue
        test = event.get("Test")
        action = event.get("Action")
        if test and action in {"pass", "fail", "skip"}:
            test_results[test] = action

    record["test_results"] = test_results
    if parse_errors:
        record["unparsed_stdout_lines"] = parse_errors
    if test_proc.stderr:
        record["stderr"] = test_proc.stderr

    all_experiments_pass = True
    for key, required in EXPERIMENTS.items():
        missing = [name for name in required if name not in test_results]
        failed = [name for name in required if test_results.get(name) != "pass" and name not in missing]
        if missing or failed:
            state = "fail"
            all_experiments_pass = False
        else:
            state = "pass"
        record["experiments"][key].update({"status": state, "missing_tests": missing, "non_pass_tests": failed})

    if test_proc.returncode == 0 and all_experiments_pass:
        record["status"] = "pass"
        write_evidence(record, args.output)
        return 0

    record["status"] = "fail"
    record["failure_boundary"] = "interactionprobe executable verification did not satisfy every required E1-E8 test"
    write_evidence(record, args.output)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
