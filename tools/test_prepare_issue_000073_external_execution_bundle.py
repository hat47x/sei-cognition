#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).with_name("prepare_issue_000073_external_execution_bundle.py")


def run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def make_repo(root: Path) -> tuple[Path, str]:
    repo = root / "repo"
    repo.mkdir()
    run(["git", "init", "-q"], repo).check_returncode()
    run(["git", "config", "user.name", "Test User"], repo).check_returncode()
    run(["git", "config", "user.email", "test@example.com"], repo).check_returncode()
    (repo / "README.md").write_text("hello\n", encoding="utf-8")
    run(["git", "add", "README.md"], repo).check_returncode()
    run(["git", "commit", "-q", "-m", "initial"], repo).check_returncode()
    head = run(["git", "rev-parse", "HEAD"], repo).stdout.strip()
    return repo, head


@unittest.skipUnless(shutil.which("git"), "git required")
class PrepareBundleTests(unittest.TestCase):
    def invoke(self, repo: Path, head: str, out: Path, *extra: str) -> subprocess.CompletedProcess[str]:
        return run(
            [
                sys.executable,
                str(SCRIPT),
                "--repo",
                str(repo),
                "--expected-head",
                head,
                "--output-dir",
                str(out),
                *extra,
            ],
            repo,
        )

    def test_prepare_bundle_clones_exact_head(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            repo, head = make_repo(root)
            out = root / "out"
            proc = self.invoke(repo, head, out)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            summary = json.loads(proc.stdout)
            bundle = Path(summary["bundle"])
            manifest = json.loads(Path(summary["manifest"]).read_text(encoding="utf-8"))
            self.assertEqual(manifest["source"]["head"], head)
            self.assertEqual(manifest["bundle"]["sha256"], summary["bundle_sha256"])
            clone = root / "clone"
            cp = run(["git", "clone", "-q", str(bundle), str(clone)], root)
            self.assertEqual(cp.returncode, 0, cp.stderr)
            cloned_head = run(["git", "-C", str(clone), "rev-parse", "HEAD"], root).stdout.strip()
            self.assertEqual(cloned_head, head)
            status = run(
                ["git", "-C", str(clone), "status", "--porcelain=v1", "--untracked-files=all"],
                root,
            ).stdout
            self.assertEqual(status, "")

    def test_expected_head_mismatch_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            repo, _head = make_repo(root)
            proc = self.invoke(repo, "0" * 40, root / "out")
            self.assertEqual(proc.returncode, 2)
            self.assertIn("does not match expected canonical HEAD", proc.stderr)

    def test_dirty_repo_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            repo, head = make_repo(root)
            (repo / "README.md").write_text("changed\n", encoding="utf-8")
            proc = self.invoke(repo, head, root / "out")
            self.assertEqual(proc.returncode, 2)
            self.assertIn("working tree is not clean", proc.stderr)

    def test_output_inside_repo_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            repo, head = make_repo(root)
            proc = self.invoke(repo, head, repo / "out")
            self.assertEqual(proc.returncode, 2)
            self.assertIn("outside the source repository", proc.stderr)

    def test_existing_outputs_require_replace(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            repo, head = make_repo(root)
            out = root / "out"
            first = self.invoke(repo, head, out)
            self.assertEqual(first.returncode, 0, first.stderr)
            second = self.invoke(repo, head, out)
            self.assertEqual(second.returncode, 2)
            self.assertIn("output already exists", second.stderr)
            third = self.invoke(repo, head, out, "--replace")
            self.assertEqual(third.returncode, 0, third.stderr)


if __name__ == "__main__":
    unittest.main()
