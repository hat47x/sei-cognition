import subprocess
import tempfile
import unittest
from pathlib import Path

import verify_tei_execution_source_identity as subject


class TEIExecutionSourceIdentityVerificationTest(unittest.TestCase):
    def make_repo(self, root: Path) -> tuple[Path, dict[str, str], str]:
        repo = root / "tei"
        repo.mkdir()
        subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True)
        subprocess.run(["git", "-C", str(repo), "config", "user.email", "test@example.invalid"], check=True)
        subprocess.run(["git", "-C", str(repo), "config", "user.name", "test"], check=True)

        for directory in ["cmd", "internal", "reference"]:
            path = repo / directory
            path.mkdir()
            (path / "fixture.txt").write_text(directory + "\n", encoding="utf-8")
        (repo / "go.mod").write_text("module example.invalid/tei\n", encoding="utf-8")
        (repo / "go.sum").write_text("fixture\n", encoding="utf-8")

        subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-qm", "fixture"], check=True)
        head = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
        objects = {
            path: subprocess.check_output(
                ["git", "-C", str(repo), "rev-parse", f"HEAD:{path}"], text=True
            ).strip()
            for path in subject.EXPECTED_OBJECTS
        }
        return repo, objects, head

    def test_matching_clean_checkout_is_verified(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, objects, head = self.make_repo(Path(tmp))
            result = subject.verify_repository(repo, expected_objects=objects, expected_head=head)
        self.assertEqual("verified", result["result"])
        self.assertTrue(result["worktreeCleanWithinBoundary"])
        self.assertEqual("not_evaluated", result["qualityJudgement"])

    def test_object_identity_drift_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, objects, _ = self.make_repo(Path(tmp))
            wrong = dict(objects)
            wrong["go.mod"] = "0" * 40
            with self.assertRaisesRegex(ValueError, "Git object identity"):
                subject.verify_repository(repo, expected_objects=wrong)

    def test_modified_tracked_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, objects, _ = self.make_repo(Path(tmp))
            (repo / "go.mod").write_text("changed\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "未commit変更"):
                subject.verify_repository(repo, expected_objects=objects)

    def test_untracked_go_file_in_boundary_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, objects, _ = self.make_repo(Path(tmp))
            (repo / "cmd" / "unexpected.go").write_text("package main\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "untracked file"):
                subject.verify_repository(repo, expected_objects=objects)

    def test_expected_head_mismatch_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, objects, _ = self.make_repo(Path(tmp))
            with self.assertRaisesRegex(ValueError, "HEADが期待値"):
                subject.verify_repository(repo, expected_objects=objects, expected_head="f" * 40)


if __name__ == "__main__":
    unittest.main()
