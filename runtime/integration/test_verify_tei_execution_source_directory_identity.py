import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import verify_tei_execution_source_directory_identity as subject


class TEIExecutionSourceDirectoryIdentityVerificationTest(unittest.TestCase):
    def make_fixture(self, root: Path) -> tuple[Path, dict[str, str]]:
        repo = root / "repo"
        repo.mkdir()
        subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True)
        subprocess.run(
            ["git", "-C", str(repo), "config", "user.email", "test@example.invalid"],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(repo), "config", "user.name", "test"],
            check=True,
        )

        (repo / "cmd" / "tei").mkdir(parents=True)
        (repo / "internal" / "nested").mkdir(parents=True)
        (repo / "reference" / "workspace").mkdir(parents=True)
        (repo / "cmd" / "tei" / "main.go").write_text(
            "package main\n",
            encoding="utf-8",
        )
        tool = repo / "internal" / "nested" / "tool.sh"
        tool.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        tool.chmod(0o755)
        (repo / "reference" / "workspace" / "input.txt").write_text(
            "input\n",
            encoding="utf-8",
        )
        (repo / "go.mod").write_text(
            "module example.invalid/tei\n",
            encoding="utf-8",
        )
        (repo / "go.sum").write_text("fixture\n", encoding="utf-8")

        subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
        subprocess.run(
            ["git", "-C", str(repo), "commit", "-qm", "fixture"],
            check=True,
        )
        objects = {
            path: subprocess.check_output(
                ["git", "-C", str(repo), "rev-parse", f"HEAD:{path}"],
                text=True,
            ).strip()
            for path in subject.EXPECTED_OBJECTS
        }

        content_root = root / "content"
        content_root.mkdir()
        for directory in ["cmd", "internal", "reference"]:
            shutil.copytree(
                repo / directory,
                content_root / directory,
                copy_function=shutil.copy2,
            )
        for filename in ["go.mod", "go.sum"]:
            shutil.copy2(repo / filename, content_root / filename)
        return content_root, objects

    def test_matching_non_git_directory_is_verified_against_git_oracle(self):
        with tempfile.TemporaryDirectory() as tmp:
            content_root, objects = self.make_fixture(Path(tmp))
            result = subject.verify_directory(
                content_root,
                expected_objects=objects,
            )

        self.assertEqual("verified", result["result"])
        self.assertEqual(objects, result["executionSourceObjects"])
        self.assertEqual("content_directory", result["acquisitionMode"])
        self.assertFalse(result["gitCheckoutHeadVerified"])
        self.assertFalse(result["gitCheckoutWorkingTreePurityVerified"])
        self.assertFalse(result["revisionBExecutionSourceObjectSetMatched"])
        self.assertEqual("not_evaluated", result["qualityJudgement"])

    def test_byte_drift_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            content_root, objects = self.make_fixture(Path(tmp))
            (content_root / "go.mod").write_text("changed\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Git object identity"):
                subject.verify_directory(content_root, expected_objects=objects)

    def test_extra_file_in_tree_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            content_root, objects = self.make_fixture(Path(tmp))
            (content_root / "cmd" / "extra.go").write_text(
                "package extra\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "Git object identity"):
                subject.verify_directory(content_root, expected_objects=objects)

    def test_executable_mode_drift_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            content_root, objects = self.make_fixture(Path(tmp))
            tool = content_root / "internal" / "nested" / "tool.sh"
            tool.chmod(0o644)
            with self.assertRaisesRegex(ValueError, "Git object identity"):
                subject.verify_directory(content_root, expected_objects=objects)

    def test_symlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            content_root, objects = self.make_fixture(Path(tmp))
            original = content_root / "reference" / "workspace" / "input.txt"
            original.unlink()
            original.symlink_to(content_root / "go.sum")
            with self.assertRaisesRegex(ValueError, "symlink"):
                subject.verify_directory(content_root, expected_objects=objects)

    def test_missing_boundary_path_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            content_root, objects = self.make_fixture(Path(tmp))
            (content_root / "go.sum").unlink()
            with self.assertRaisesRegex(ValueError, "ありません"):
                subject.verify_directory(content_root, expected_objects=objects)


if __name__ == "__main__":
    unittest.main()
