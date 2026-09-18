#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile

WRAPPER = Path(__file__).with_name("capture_issue_000073_resume_first_evidence.py")


def write_tool(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("#!/usr/bin/env python3\n" + body, encoding="utf-8")


def setup_repo(
    root: Path,
    *,
    runner_exit: int = 0,
    runner_writes_record: bool = True,
    verifier_exit: int = 0,
    verifier_passed: bool = True,
) -> None:
    tools = root / "tools"
    tools.mkdir(parents=True, exist_ok=True)
    runner_write = 'a.output.write_text(json.dumps(record), encoding="utf-8")' if runner_writes_record else ""
    write_tool(
        tools / "run_issue_000073_resume_first_evidence.py",
        f'''import argparse, json, subprocess\nfrom pathlib import Path\np=argparse.ArgumentParser(); p.add_argument("--output", type=Path); p.add_argument("--go"); a=p.parse_args()\ndirty = bool(subprocess.run(["git", "status", "--porcelain=v1"], text=True, stdout=subprocess.PIPE, check=True).stdout.strip())\nexit_code = 2 if dirty else {runner_exit}\nstatus = "blocked" if exit_code == 2 else ("pass" if exit_code == 0 else "fail")\nrecord={{"status": status, "repository": {{"head": "0123456789abcdef0123456789abcdef01234567"}}}}\n{runner_write}\nraise SystemExit(exit_code)\n''',
    )
    write_tool(
        tools / "verify_issue_000073_resume_first_evidence.py",
        f'''import argparse, json\nfrom pathlib import Path\np=argparse.ArgumentParser(); p.add_argument("evidence", type=Path); p.add_argument("--repo"); p.add_argument("--json-out", type=Path); a=p.parse_args()\na.json_out.write_text(json.dumps({{"passed": {repr(verifier_passed)}}}), encoding="utf-8")\nraise SystemExit({verifier_exit})\n''',
    )
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "SEI test"], cwd=root, check=True)
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    subprocess.run(["git", "commit", "-qm", "fixture"], cwd=root, check=True)


def invoke(root: Path, *extra: str) -> tuple[int, dict]:
    cmd = [sys.executable, str(WRAPPER), "--repo", str(root), *extra]
    proc = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert proc.stderr == "", proc.stderr
    return proc.returncode, json.loads(proc.stdout)


def test_pass_publishes_both() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        setup_repo(root)
        code, out = invoke(root)
        assert code == 0, out
        assert out["status"] == "pass", out
        evidence = root / "evaluation/personal-inquiry-decision/evidence/issue-000073/e1-e8.json"
        verification = root / "evaluation/personal-inquiry-decision/evidence/issue-000073/e1-e8-verification.json"
        assert evidence.is_file()
        assert verification.is_file()
        assert json.loads(verification.read_text())["passed"] is True


def test_runner_blocked_keeps_raw_only() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        setup_repo(root, runner_exit=2)
        code, out = invoke(root)
        assert code == 2, out
        assert out["status"] == "blocked", out
        evidence = root / "evaluation/personal-inquiry-decision/evidence/issue-000073/e1-e8.json"
        verification = root / "evaluation/personal-inquiry-decision/evidence/issue-000073/e1-e8-verification.json"
        assert evidence.is_file()
        assert not verification.exists()


def test_runner_zero_without_record_is_fail_closed() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        setup_repo(root, runner_exit=0, runner_writes_record=False)
        code, out = invoke(root)
        assert code == 1, out
        assert out["status"] == "fail", out
        assert out["runner_exit"] == 0, out
        assert "readable JSON evidence record" in out["detail"], out
        evidence = root / "evaluation/personal-inquiry-decision/evidence/issue-000073/e1-e8.json"
        verification = root / "evaluation/personal-inquiry-decision/evidence/issue-000073/e1-e8-verification.json"
        assert not evidence.exists()
        assert not verification.exists()


def test_runner_block_code_without_record_is_not_accepted_as_blocked() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        setup_repo(root, runner_exit=2, runner_writes_record=False)
        code, out = invoke(root)
        assert code == 1, out
        assert out["status"] == "fail", out
        assert out["runner_exit"] == 2, out
        assert "readable JSON evidence record" in out["detail"], out
        evidence = root / "evaluation/personal-inquiry-decision/evidence/issue-000073/e1-e8.json"
        verification = root / "evaluation/personal-inquiry-decision/evidence/issue-000073/e1-e8-verification.json"
        assert not evidence.exists()
        assert not verification.exists()


def test_replace_runner_without_record_removes_stale_outputs() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        setup_repo(root, runner_exit=0, runner_writes_record=False)
        evidence = root / "evaluation/personal-inquiry-decision/evidence/issue-000073/e1-e8.json"
        verification = root / "evaluation/personal-inquiry-decision/evidence/issue-000073/e1-e8-verification.json"
        evidence.parent.mkdir(parents=True, exist_ok=True)
        evidence.write_text('{"status":"pass"}', encoding="utf-8")
        verification.write_text('{"passed":true}', encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=root, check=True)
        subprocess.run(["git", "commit", "-qm", "prior evidence"], cwd=root, check=True)

        code, out = invoke(root, "--replace")
        assert code == 1, out
        assert out["status"] == "fail", out
        assert not evidence.exists()
        assert not verification.exists()


def test_verifier_failure_is_not_pass() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        setup_repo(root, verifier_exit=1, verifier_passed=False)
        code, out = invoke(root)
        assert code == 1, out
        assert out["status"] == "verification_failed", out
        evidence = root / "evaluation/personal-inquiry-decision/evidence/issue-000073/e1-e8.json"
        verification = root / "evaluation/personal-inquiry-decision/evidence/issue-000073/e1-e8-verification.json"
        assert evidence.is_file()
        assert verification.is_file()
        assert json.loads(verification.read_text())["passed"] is False


def test_existing_outputs_require_replace() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        setup_repo(root)
        evidence = root / "evaluation/personal-inquiry-decision/evidence/issue-000073/e1-e8.json"
        evidence.parent.mkdir(parents=True, exist_ok=True)
        evidence.write_text("old", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=root, check=True)
        subprocess.run(["git", "commit", "-qm", "existing evidence"], cwd=root, check=True)
        code, out = invoke(root)
        assert code == 2, out
        assert out["status"] == "blocked", out
        assert evidence.read_text(encoding="utf-8") == "old"
        code, out = invoke(root, "--replace")
        assert code == 0, out
        assert out["status"] == "pass", out
        assert evidence.read_text(encoding="utf-8") != "old"


def test_same_output_path_is_rejected() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        setup_repo(root)
        same = "out/same.json"
        code, out = invoke(root, "--evidence", same, "--verification", same)
        assert code == 2, out
        assert out["status"] == "blocked", out


def main() -> int:
    test_pass_publishes_both()
    test_runner_blocked_keeps_raw_only()
    test_runner_zero_without_record_is_fail_closed()
    test_runner_block_code_without_record_is_not_accepted_as_blocked()
    test_replace_runner_without_record_removes_stale_outputs()
    test_verifier_failure_is_not_pass()
    test_existing_outputs_require_replace()
    test_same_output_path_is_rejected()
    print("PASS: ISSUE-000073 capture workflow self-tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
