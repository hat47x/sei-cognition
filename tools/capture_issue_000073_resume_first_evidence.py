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

    # Keep temporary artifacts outside the repository. The runner requires a clean working tree,
    # so creating an untracked temp JSON under the checkout before it starts would self-block.
    temp_root = tempfile.TemporaryDirectory(prefix="issue-000073-evidence-")
    evidence_temp = Path(temp_root.name) / "e1-e8.json"
    verification_temp = Path(temp_root.name) / "e1-e8-verification.json"

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

        # The runner must always publish a readable machine record before its exit code is interpreted.
        # A Python exception, startup failure, or malformed output must not make this wrapper crash while
        # attempting to publish a nonexistent temp file, and must never inherit a stale prior PASS.
        if runner_record is None:
            if args.replace:
                evidence.unlink(missing_ok=True)
                verification.unlink(missing_ok=True)
            detail = "runner did not publish a readable JSON evidence record; verifier was not invoked"
            if runner_proc.stderr.strip():
                detail += f"; runner stderr: {runner_proc.stderr.strip()}"
            sys.stdout.write(summary(
                status="fail", evidence=evidence, verification=None, tested_head=None,
                runner_exit=runner_proc.returncode, detail=detail,
            ))
            return 1

        # A blocked or failing actual run is still useful diagnostic evidence, but is never verified/prompted as PASS.
        if runner_proc.returncode != 0:
            publish(evidence_temp, evidence)
            if args.replace:
                verification.unlink(missing_ok=True)
            runner_status = runner_record.get("status")
            blocked = runner_proc.returncode == 2 and runner_status == "blocked"
            status = "blocked" if blocked else "fail"
            detail = "runner did not PASS; verifier was not invoked"
            if runner_proc.returncode == 2 and not blocked:
                detail += "; exit code 2 was not accepted as blocked without a status=blocked evidence record"
            if runner_proc.stderr.strip():
                detail += f"; runner stderr: {runner_proc.stderr.strip()}"
            sys.stdout.write(summary(
                status=status, evidence=evidence, verification=None, tested_head=tested_head,
                runner_exit=runner_proc.returncode, detail=detail,
            ))
            return 2 if blocked else 1

        if runner_record.get("status") != "pass":
            publish(evidence_temp, evidence)
            if args.replace:
                verification.unlink(missing_ok=True)
            sys.stdout.write(summary(
                status="fail", evidence=evidence, verification=None, tested_head=tested_head,
                runner_exit=0,
                detail="runner exited zero but its evidence record did not declare status=pass; verifier was not invoked",
            ))
            return 1

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
        temp_root.cleanup()


if __name__ == "__main__":
    raise SystemExit(main())
