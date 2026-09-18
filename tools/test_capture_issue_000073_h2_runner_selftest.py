#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

CAPTURE = Path(__file__).with_name("capture_issue_000073_h2_runner_selftest.py")
CAPTURE_REL = Path("tools/capture_issue_000073_h2_runner_selftest.py")
TEST_REL = Path("evaluation/personal-inquiry-decision/test_decision_continuity_review_runner.py")
DEPENDENCIES = (
    "inquiry_continuity_review_runner.py",
    "matched_review_session.py",
    "decision_continuity_review_analysis.py",
    "inquiry_continuity_review_analysis.py",
    "inquiry_continuity_review_evidence.py",
    "inquiry_continuity_packet.py",
    "decision_continuity_preflight.py",
)
FIXTURES = (
    "decision_continuity_counterfactual_matched_set_v1.json",
    "decision_continuity_counterfactual_001.json",
    "decision_continuity_counterfactual_002.json",
    "decision_continuity_counterfactual_003.json",
)


def run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def setup_repo(root: Path, *, failing_test: bool = False) -> None:
    capture = root / CAPTURE_REL
    capture.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(CAPTURE, capture)

    eval_dir = root / "evaluation/personal-inquiry-decision"
    eval_dir.mkdir(parents=True, exist_ok=True)
    for name in DEPENDENCIES:
        (eval_dir / name).write_text("# synthetic dependency\n", encoding="utf-8")
    test_path = root / TEST_REL
    test_path.write_text(
        "raise SystemExit(1)\n" if failing_test else "print('decision runner synthetic PASS')\n",
        encoding="utf-8",
    )
    for name in FIXTURES:
        (eval_dir / name).write_text("{}\n", encoding="utf-8")

    for cmd in (
        ["git", "init", "-q"],
        ["git", "config", "user.email", "test@example.invalid"],
        ["git", "config", "user.name", "SEI test"],
        ["git", "add", "."],
        ["git", "commit", "-qm", "fixture"],
    ):
        proc = run(cmd, root)
        assert proc.returncode == 0, proc.stderr


def invoke(
    root: Path,
    *extra: str,
    expected_head: str | None = None,
) -> tuple[int, dict]:
    capture = root / CAPTURE_REL
    head = expected_head or run(["git", "rev-parse", "HEAD"], root).stdout.strip()
    proc = run(
        [
            sys.executable,
            str(capture),
            "--repo",
            str(root),
            "--expected-head",
            head,
            *extra,
        ],
        root,
    )
    assert proc.stderr == "", proc.stderr
    return proc.returncode, json.loads(proc.stdout)


def evidence_path(root: Path) -> Path:
    return root / "evaluation/personal-inquiry-decision/evidence/issue-000073/h2-shared-runner-selftest.json"


def test_clean_pass_records_head_and_sources() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        setup_repo(root)
        head = run(["git", "rev-parse", "HEAD"], root).stdout.strip()
        code, out = invoke(root)
        assert code == 0, out
        assert out["status"] == "pass", out
        data = json.loads(evidence_path(root).read_text(encoding="utf-8"))
        assert data["status"] == "pass"
        assert data["repository"]["head"] == head
        assert data["repository"]["clean"] is True
        assert data["execution"]["exit_code"] == 0
        assert data["repository"]["expected_head"] == head
        assert data["repository"]["head_matches_expected"] is True
        assert len(data["source_binding"]) == 13
        assert all(item["matches_head"] for item in data["source_binding"])


def test_expected_head_mismatch_blocks_without_publishing() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        setup_repo(root)
        code, out = invoke(root, expected_head="0" * 40)
        assert code == 2, out
        assert out["status"] == "blocked", out
        assert out["repository"]["head_matches_expected"] is False
        assert "does not match" in out["detail"]
        assert not evidence_path(root).exists()


def test_dirty_checkout_blocks_without_publishing() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        setup_repo(root)
        (root / "dirty.txt").write_text("dirty", encoding="utf-8")
        code, out = invoke(root)
        assert code == 2, out
        assert out["status"] == "blocked", out
        assert not evidence_path(root).exists()


def test_missing_required_source_blocks() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        setup_repo(root)
        target = root / "evaluation/personal-inquiry-decision/decision_continuity_preflight.py"
        target.unlink()
        run(["git", "add", "-u"], root)
        run(["git", "commit", "-qm", "remove dependency"], root)
        code, out = invoke(root)
        assert code == 2, out
        assert out["status"] == "blocked", out
        assert "required source not found" in out["detail"]


def test_missing_fixture_blocks() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        setup_repo(root)
        target = root / "evaluation/personal-inquiry-decision/decision_continuity_counterfactual_003.json"
        target.unlink()
        run(["git", "add", "-u"], root)
        run(["git", "commit", "-qm", "remove fixture"], root)
        code, out = invoke(root)
        assert code == 2, out
        assert out["status"] == "blocked", out
        assert "required source not found" in out["detail"]


def test_test_failure_is_recorded_as_fail() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        setup_repo(root, failing_test=True)
        code, out = invoke(root)
        assert code == 1, out
        assert out["status"] == "fail", out
        data = json.loads(evidence_path(root).read_text(encoding="utf-8"))
        assert data["status"] == "fail"
        assert data["execution"]["exit_code"] == 1


def test_existing_output_requires_replace() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        setup_repo(root)
        output = evidence_path(root)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text("old", encoding="utf-8")
        run(["git", "add", "."], root)
        run(["git", "commit", "-qm", "prior output"], root)
        code, out = invoke(root)
        assert code == 2, out
        assert out["status"] == "blocked", out
        code, out = invoke(root, "--replace")
        assert code == 0, out
        assert out["status"] == "pass", out
        assert json.loads(output.read_text(encoding="utf-8"))["status"] == "pass"


def main() -> int:
    test_clean_pass_records_head_and_sources()
    test_expected_head_mismatch_blocks_without_publishing()
    test_dirty_checkout_blocks_without_publishing()
    test_missing_required_source_blocks()
    test_missing_fixture_blocks()
    test_test_failure_is_recorded_as_fail()
    test_existing_output_requires_replace()
    print("PASS: ISSUE-000073 H2 runner self-test capture workflow")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
