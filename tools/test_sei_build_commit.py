import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "sei_build_commit.sh"
HAVE = shutil.which("sh") and shutil.which("git")


def git(root, *args):
    subprocess.run(
        ["git", "-C", root, "-c", "user.name=t", "-c", "user.email=t@example.com", *args],
        check=True, capture_output=True,
    )


def label(root):
    out = subprocess.run(["sh", SCRIPT.as_posix(), root], check=True, capture_output=True, text=True)
    return out.stdout.strip()


@unittest.skipUnless(HAVE, "sh and git are required")
class BuildCommitTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.dir, ignore_errors=True)
        git(self.dir, "init", "-q")
        Path(self.dir, "a.txt").write_text("a\n")
        git(self.dir, "add", "a.txt")
        git(self.dir, "commit", "-q", "-m", "init")

    def test_clean_tree_is_full_length_without_dirty(self):
        self.assertRegex(label(self.dir), r"^[0-9a-f]{40}$")

    def test_modified_tracked_file_adds_dirty(self):
        Path(self.dir, "a.txt").write_text("b\n")
        self.assertRegex(label(self.dir), r"^[0-9a-f]{40}\+dirty$")

    def test_untracked_file_adds_dirty(self):
        Path(self.dir, "new.txt").write_text("x\n")
        self.assertRegex(label(self.dir), r"^[0-9a-f]{40}\+dirty$")

    def test_not_a_repository_is_unknown(self):
        other = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, other, ignore_errors=True)
        env_before = os.environ.get("GIT_CEILING_DIRECTORIES")
        os.environ["GIT_CEILING_DIRECTORIES"] = os.path.dirname(other)
        try:
            self.assertEqual(label(other), "unknown")
        finally:
            if env_before is None:
                del os.environ["GIT_CEILING_DIRECTORIES"]
            else:
                os.environ["GIT_CEILING_DIRECTORIES"] = env_before


if __name__ == "__main__":
    unittest.main()
