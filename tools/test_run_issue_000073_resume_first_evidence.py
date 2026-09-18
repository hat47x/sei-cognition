#!/usr/bin/env python3
"""Self-tests for the ISSUE-000073 resume-first evidence runner preflight."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
from pathlib import Path
import stat
import subprocess
import sys
import tempfile

MODULE_PATH = Path(__file__).with_name("run_issue_000073_resume_first_evidence.py")
spec = importlib.util.spec_from_file_location("run_issue_000073_resume_first_evidence", MODULE_PATH)
assert spec and spec.loader
runner = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = runner
spec.loader.exec_module(runner)


def run(cmd: list[str], cwd: Path) -> None:
    subprocess.run(cmd, cwd=cwd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def init_repo(root: Path, *, include_all_sources: bool = True) -> None:
    (root / "tools").mkdir(parents=True, exist_ok=True)
    (root / "runtime" / "go").mkdir(parents=True, exist_ok=True)

    paths = runner.SOURCE_FILES if include_all_sources else runner.SOURCE_FILES[:3]
    for relative in paths:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"fixture for {relative}\n", encoding="utf-8")

    run(["git", "init", "-q"], root)
    run(["git", "config", "user.email", "test@example.invalid"], root)
    run(["git", "config", "user.name", "SEI test"], root)
    run(["git", "add", "."], root)
    run(["git", "commit", "-qm", "fixture"], root)


def fake_go(root: Path, version: str) -> Path:
    path = root / "fake-go"
    path.write_text(
        "#!/bin/sh\n"
        "if [ \"$1\" = \"version\" ]; then\n"
        f"  echo 'go version {version} linux/amd64'\n"
        "  exit 0\n"
        "fi\n"
        "echo 'unexpected fake go invocation' >&2\n"
        "exit 99\n",
        encoding="utf-8",
    )
    path.chmod(path.stat().st_mode | stat.S_IXUSR)
    return path


def invoke(
    root: Path,
    argv: list[str],
    *,
    expected_head: str | None = None,
) -> tuple[int, dict]:
    original_file = runner.__file__
    original_argv = sys.argv[:]
    stdout = io.StringIO()
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    ).stdout.strip()
    try:
        runner.__file__ = str(root / "tools" / "run_issue_000073_resume_first_evidence.py")
        sys.argv = [
            "run_issue_000073_resume_first_evidence.py",
            "--expected-head",
            expected_head or head,
            *argv,
        ]
        with contextlib.redirect_stdout(stdout):
            code = runner.main()
    finally:
        runner.__file__ = original_file
        sys.argv = original_argv

    payload = json.loads(stdout.getvalue())
    return code, payload


def test_expected_head_mismatch_blocks() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        init_repo(root)

        code, payload = invoke(root, [], expected_head="0" * 40)
        assert code == 2, payload
        assert payload["status"] == "blocked", payload
        assert payload["repository"]["head_matches_expected"] is False, payload
        assert "expected HEAD" in payload["blocked_reason"], payload


def test_dirty_checkout_blocks() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        init_repo(root)
        dirty = root / runner.SOURCE_FILES[-1]
        dirty.write_text(dirty.read_text(encoding="utf-8") + "dirty\n", encoding="utf-8")

        code, payload = invoke(root, [])
        assert code == 2, payload
        assert payload["status"] == "blocked", payload
        assert payload["repository"]["dirty"] is True, payload
        assert "dirty" in payload["blocked_reason"], payload


def test_missing_required_binding_blocks() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        init_repo(root, include_all_sources=False)

        code, payload = invoke(root, [])
        assert code == 2, payload
        assert payload["status"] == "blocked", payload
        assert payload["missing_source_bindings"], payload
        assert "missing" in payload["blocked_reason"], payload


def test_lower_go_version_blocks() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        init_repo(root)
        go = fake_go(root, "go1.24.9")
        run(["git", "add", "fake-go"], root)
        run(["git", "commit", "-qm", "fake go"], root)

        code, payload = invoke(root, ["--go", str(go)])
        assert code == 2, payload
        assert payload["status"] == "blocked", payload
        assert payload["repository"]["dirty"] is False, payload
        assert all(binding.get("matches_head") is True for binding in payload["source_bindings"]), payload
        assert payload["go"]["version_output"].startswith("go version go1.24.9"), payload
        assert "Go 1.25.x" in payload["blocked_reason"], payload


def main() -> int:
    test_expected_head_mismatch_blocks()
    test_dirty_checkout_blocks()
    test_missing_required_binding_blocks()
    test_lower_go_version_blocks()
    print("PASS: ISSUE-000073 evidence runner preflight self-tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
