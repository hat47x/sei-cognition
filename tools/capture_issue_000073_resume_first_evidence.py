#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any

DEFAULT_EVIDENCE = Path("evaluation/personal-inquiry-decision/evidence/issue-000073/e1-e8.json")
DEFAULT_VERIFICATION = Path("evaluation/personal-inquiry-decision/evidence/issue-000073/e1-e8-verification.json")


def run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def read_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def publish(temp: Path, final: Path) -> None:
    final.parent.mkdir(parents=True, exist_ok=True)
    os.replace(temp, final)


def summary(*, status: str, evidence: Path, verification: Path | None, tested_head: str | None = None,
            runner_exit: int | None = None, verifier_exit: int | None = None, detail: str | None = None) -> str:
    data: dict[str, Any] = {
        "schema": "issue-000073-resume-first-capture/v1",
        "status": status,
        "evidence": str(evidence),
        "verification": str(verification) if verification is not None else None,
        "tested_head": tested_head,
        "runner_exit": runner_exit,
        "verifier_exit": verifier_exit,
        "stop_line": "Verified E1-E8 executable evidence != H1/H2 human review != Decision Continuity Product Value established.",
    }
    if detail:
        data["detail"] = detail
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run and verify ISSUE-000073 E1-E8 evidence in one fail-closed workflow."
    )
    parser.add_argument("--evidence", type=Path, default=DEFAULT_EVIDENCE)
    parser.add_argument("--verification", type=Path, default=DEFAULT_VERIFICATION)
    parser.add_argument("--go", dest="go_executable", help="Go executable forwarded to the evidence runner.")
    parser.add_argument("--replace", action="store_true", help="Replace existing evidence outputs intentionally.")
    parser.add_argument("--repo", type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()

    repo = (args.repo or Path(__file__).resolve().parents[1]).resolve()
    evidence = args.evidence if args.evidence.is_absolute() else repo / args.evidence
    verification = args.verification if args.verification.is_absolute() else repo / args.verification
    evidence = evidence.resolve()
    verification = verification.resolve()

    if evidence == verification:
        sys.stdout.write(summary(
            status="blocked", evidence=evidence, verification=verification,
            detail="evidence and verification outputs must be different files",
        ))
        return 2

    existing = [path for path in (evidence, verification) if path.exists()]
    if existing and not args.replace:
        sys.stdout.write(summary(
            status="blocked", evidence=evidence, verification=verification,
            detail="output already exists; use --replace only for an intentional rerun: " + ", ".join(map(str, existing)),
        ))
        return 2

    tools = repo / "tools"
    runner = tools / "run_issue_000073_resume_first_evidence.py"
    verifier = tools / "verify_issue_000073_resume_first_evidence.py"
    for path in (runner, verifier):
        if not path.is_file():
            sys.stdout.write(summary(
                status="blocked", evidence=evidence, verification=verification,
                detail=f"required tool not found: {path}",
            ))
            return 2

    evidence.parent.mkdir(parents=True, exist_ok=True)
    verification.parent.mkdir(parents=True, exist_ok=True)

    temp_dir = evidence.parent
    evidence_fd, evidence_temp_name = tempfile.mkstemp(prefix=".e1-e8.", suffix=".json.tmp", dir=temp_dir)
    os.close(evidence_fd)
    evidence_temp = Path(evidence_temp_name)
    verification_fd, verification_temp_name = tempfile.mkstemp(
        prefix=".e1-e8-verification.", suffix=".json.tmp", dir=verification.parent
    )
    os.close(verification_fd)
    verification_temp = Path(verification_temp_name)
    verification_temp.unlink(missing_ok=True)

    try:
        runner_cmd = [sys.executable, str(runner), "--output", str(evidence_temp)]
        if args.go_executable:
            runner_cmd.extend(["--go", args.go_executable])
        runner_proc = run(runner_cmd, repo)
        runner_record = read_json(evidence_temp)
        tested_head = None
        if runner_record:
            repository = runner_record.get("repository")
            if isinstance(repository, dict) and isinstance(repository.get("head"), str):
                tested_head = repository["head"]

        # A blocked or failing actual run is still useful diagnostic evidence, but is never verified/prompted as PASS.
        if runner_proc.returncode != 0:
            publish(evidence_temp, evidence)
            verification_temp.unlink(missing_ok=True)
            if args.replace:
                verification.unlink(missing_ok=True)
            status = "blocked" if runner_proc.returncode == 2 else "fail"
            detail = "runner did not PASS; verifier was not invoked"
            if runner_proc.stderr.strip():
                detail += f"; runner stderr: {runner_proc.stderr.strip()}"
            sys.stdout.write(summary(
                status=status, evidence=evidence, verification=None, tested_head=tested_head,
                runner_exit=runner_proc.returncode, detail=detail,
            ))
            return runner_proc.returncode

        verifier_cmd = [
            sys.executable,
            str(verifier),
            str(evidence_temp),
            "--repo",
            str(repo),
            "--json-out",
            str(verification_temp),
        ]
        verifier_proc = run(verifier_cmd, repo)

        publish(evidence_temp, evidence)
        if verification_temp.exists():
            publish(verification_temp, verification)
        elif args.replace:
            verification.unlink(missing_ok=True)

        if verifier_proc.returncode != 0:
            detail = "runner PASS was captured, but independent verification did not PASS"
            if verifier_proc.stderr.strip():
                detail += f"; verifier stderr: {verifier_proc.stderr.strip()}"
            sys.stdout.write(summary(
                status="verification_failed", evidence=evidence,
                verification=verification if verification.exists() else None,
                tested_head=tested_head, runner_exit=0, verifier_exit=verifier_proc.returncode,
                detail=detail,
            ))
            return 1

        report = read_json(verification)
        if not report or report.get("passed") is not True:
            sys.stdout.write(summary(
                status="verification_failed", evidence=evidence,
                verification=verification if verification.exists() else None,
                tested_head=tested_head, runner_exit=0, verifier_exit=0,
                detail="verifier exited zero but did not publish a passed=true report",
            ))
            return 1

        sys.stdout.write(summary(
            status="pass", evidence=evidence, verification=verification,
            tested_head=tested_head, runner_exit=0, verifier_exit=0,
        ))
        return 0
    finally:
        evidence_temp.unlink(missing_ok=True)
        verification_temp.unlink(missing_ok=True)


if __name__ == "__main__":
    raise SystemExit(main())
