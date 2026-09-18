#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile

MODULE_PATH = Path(__file__).with_name("verify_issue_000073_resume_first_evidence.py")
spec = importlib.util.spec_from_file_location("verify_issue_000073_resume_first_evidence", MODULE_PATH)
assert spec and spec.loader
verifier = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = verifier
spec.loader.exec_module(verifier)


def run(cmd: list[str], cwd: Path, *, text: bool = True):
    return subprocess.run(cmd, cwd=cwd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=text)


def git_text(root: Path, *args: str) -> str:
    return run(["git", *args], root).stdout.strip()


def init_repo(root: Path) -> None:
    for relative in verifier.SOURCE_FILES:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"fixture for {relative}\n", encoding="utf-8")
    run(["git", "init", "-q"], root)
    run(["git", "config", "user.email", "test@example.invalid"], root)
    run(["git", "config", "user.name", "SEI verifier test"], root)
    run(["git", "add", "."], root)
    run(["git", "commit", "-qm", "tested source"], root)


def pass_record(root: Path) -> dict:
    head = git_text(root, "rev-parse", "HEAD")
    tree = git_text(root, "rev-parse", "HEAD^{tree}")
    bindings = []
    for relative in verifier.SOURCE_FILES:
        data = run(["git", "show", f"{head}:{relative}"], root, text=False).stdout
        blob = git_text(root, "rev-parse", f"{head}:{relative}")
        bindings.append({
            "path": relative,
            "exists": True,
            "sha256": hashlib.sha256(data).hexdigest(),
            "working_tree_blob": blob,
            "head_blob": blob,
            "matches_head": True,
        })
    test_results = {
        test: "pass"
        for tests in verifier.EXPERIMENTS.values()
        for test in tests
    }
    experiments = {
        key: {
            "required_tests": tests,
            "status": "pass",
            "missing_tests": [],
            "non_pass_tests": [],
        }
        for key, tests in verifier.EXPERIMENTS.items()
    }
    return {
        "format": verifier.FORMAT,
        "issue": verifier.ISSUE,
        "observed_at": "2026-09-16T00:00:00Z",
        "scope": "Executable Evidence for E1-E8 only; H1/H2 and Product Outcome are out of scope.",
        "repository": {
            "head": head,
            "expected_head": head,
            "head_matches_expected": True,
            "head_tree": tree,
            "git_checkout_detected": True,
            "clean_required": True,
            "dirty": False,
            "status_porcelain": [],
        },
        "required_toolchain": "go1.25.x",
        "source_bindings": bindings,
        "go": {"executable": "/usr/local/go/bin/go", "version_output": "go version go1.25.1 linux/amd64"},
        "command": {
            "cwd": "runtime/go",
            "argv": ["/usr/local/go/bin/go", "test", "-count=1", "-json", "./interactionprobe"],
            "environment": {"GOTOOLCHAIN": "local"},
            "exit_code": 0,
        },
        "test_results": test_results,
        "experiments": experiments,
        "status": "pass",
        "stop_line": verifier.STOP_LINE,
    }


def finding_codes(report) -> set[str]:
    return {item.code for item in report.findings}


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        init_repo(root)
        record = pass_record(root)
        report = verifier.validate(root, record)
        assert report.passed, report.to_dict()

        # Evidence may be committed later. Verification must still bind to the recorded tested HEAD.
        (root / "evidence.json").write_text("{}\n", encoding="utf-8")
        run(["git", "add", "evidence.json"], root)
        run(["git", "commit", "-qm", "store evidence later"], root)
        report = verifier.validate(root, record)
        assert report.passed, report.to_dict()

        tampered = copy.deepcopy(record)
        tampered["source_bindings"][0]["sha256"] = "0" * 64
        report = verifier.validate(root, tampered)
        assert not report.passed and "source-sha256" in finding_codes(report), report.to_dict()

        wrong_expected = copy.deepcopy(record)
        wrong_expected["repository"]["expected_head"] = "0" * 40
        wrong_expected["repository"]["head_matches_expected"] = False
        report = verifier.validate(root, wrong_expected)
        assert not report.passed, report.to_dict()
        codes = finding_codes(report)
        assert "head-matches-expected" in codes, report.to_dict()
        assert "expected-head-mismatch" in codes, report.to_dict()

        dirty = copy.deepcopy(record)
        dirty["repository"]["dirty"] = True
        report = verifier.validate(root, dirty)
        assert not report.passed and "dirty" in finding_codes(report), report.to_dict()

        failed_e8 = copy.deepcopy(record)
        failed_e8["experiments"]["E8"]["status"] = "fail"
        report = verifier.validate(root, failed_e8)
        assert not report.passed and "experiment-status" in finding_codes(report), report.to_dict()

        missing_head = copy.deepcopy(record)
        missing_head["repository"]["head"] = "f" * 40
        report = verifier.validate(root, missing_head)
        assert not report.passed and "head-unavailable" in finding_codes(report), report.to_dict()

        old_go = copy.deepcopy(record)
        old_go["go"]["version_output"] = "go version go1.24.9 linux/amd64"
        report = verifier.validate(root, old_go)
        assert not report.passed and "go-version" in finding_codes(report), report.to_dict()

    print("PASS: ISSUE-000073 evidence verifier self-tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
