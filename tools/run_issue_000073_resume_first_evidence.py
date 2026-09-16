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
    "runtime/go/go.mod",
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
    blob = git_text(repo, "hash-object", "--", relative)
    if blob:
        result["git_blob"] = blob
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


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture ISSUE-000073 E1-E8 executable evidence.")
    parser.add_argument("--output", help="Write the JSON evidence record to this path; stdout when omitted.")
    parser.add_argument("--go", dest="go_executable", help="Go executable to use; defaults to PATH lookup.")
    args = parser.parse_args()

    repo = Path(__file__).resolve().parents[1]
    runtime_go = repo / "runtime" / "go"
    go = args.go_executable or shutil.which("go")
    head = git_text(repo, "rev-parse", "HEAD")
    status = git_text(repo, "status", "--porcelain=v1")

    record: dict[str, Any] = {
        "format": "issue-000073-resume-first-execution-record/v1",
        "issue": "ISSUE-000073",
        "observed_at": now_utc(),
        "scope": "Executable Evidence for E1-E8 only; H1/H2 and Product Outcome are out of scope.",
        "repository": {
            "head": head,
            "dirty": bool(status),
            "status_porcelain": status.splitlines() if status else [],
        },
        "required_toolchain": "go1.25.x",
        "source_bindings": [source_binding(repo, p) for p in SOURCE_FILES],
        "experiments": {key: {"required_tests": tests, "status": "not_run"} for key, tests in EXPERIMENTS.items()},
        "stop_line": "Executable E1-E8 PASS != H1/H2 human review != Decision Continuity Product Value established.",
    }

    if not runtime_go.is_dir():
        record.update({"status": "blocked", "blocked_reason": "runtime/go directory not found"})
        write_evidence(record, args.output)
        return 2
    if not go:
        record.update({"status": "blocked", "blocked_reason": "go executable not found"})
        write_evidence(record, args.output)
        return 2

    version_proc = run([go, "version"], repo)
    version_text = (version_proc.stdout or version_proc.stderr).strip()
    record["go"] = {"executable": go, "version_output": version_text}
    if version_proc.returncode != 0 or not re.search(r"\bgo1\.25(?:\.\d+)?\b", version_text):
        record.update({
            "status": "blocked",
            "blocked_reason": "declared Go 1.25.x toolchain is not active; lower-version execution is not accepted as ISSUE-000073 PASS",
        })
        write_evidence(record, args.output)
        return 2

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
