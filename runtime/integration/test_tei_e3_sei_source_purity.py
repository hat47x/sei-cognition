import subprocess
import tempfile
import unittest
from pathlib import Path

import run_tei_bundle_adapter_compatibility as subject


class TEIE3SEISourcePurityTest(unittest.TestCase):
    def make_repo(self, root: Path) -> Path:
        repo = root / "sei"
        go_root = repo / "runtime/go"
        go_root.mkdir(parents=True)
        (go_root / "go.mod").write_text("module example.invalid/sei\n\ngo 1.25\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True)
        subprocess.run(
            ["git", "-C", str(repo), "config", "user.email", "test@example.invalid"],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(repo), "config", "user.name", "test"],
            check=True,
        )
        subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-qm", "fixture"], check=True)
        return repo

    def test_clean_runtime_boundary_is_verified(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self.make_repo(Path(tmp))
            result = subject._verify_sei_source_identity(repo, paths=["runtime/go"])
        self.assertTrue(result["worktreeCleanWithinBoundary"])

    def test_ignored_runtime_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self.make_repo(Path(tmp))
            exclude = repo / ".git/info/exclude"
            exclude.write_text("runtime/go/ignored.go\n", encoding="utf-8")
            ignored = repo / "runtime/go/ignored.go"
            ignored.write_text("package ignored\n", encoding="utf-8")

            without_ignored = subprocess.run(
                [
                    "git",
                    "-C",
                    str(repo),
                    "status",
                    "--porcelain=v1",
                    "--untracked-files=all",
                    "--",
                    "runtime/go",
                ],
                check=True,
                text=True,
                stdout=subprocess.PIPE,
            ).stdout
            self.assertEqual("", without_ignored)

            with self.assertRaisesRegex(ValueError, "ignored"):
                subject._verify_sei_source_identity(repo, paths=["runtime/go"])


if __name__ == "__main__":
    unittest.main()
