import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import run_tei_bundle_adapter_compatibility as subject


class TEISozaSourceGitEnvironmentTest(unittest.TestCase):
    def git(self, repo: Path, *args: str) -> str:
        process = subprocess.run(
            ["git", "-C", str(repo), *args],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return process.stdout.strip()

    def make_repo(self, root: Path) -> tuple[Path, str]:
        repo = root / "soza"
        helper = repo / "runtime/integration/git_object_environment.py"
        helper.parent.mkdir(parents=True)
        helper.write_text("VALUE = 'fixed'\n", encoding="utf-8")
        self.git(repo, "init", "-q")
        self.git(repo, "config", "user.email", "test@example.invalid")
        self.git(repo, "config", "user.name", "test")
        self.git(repo, "add", ".")
        self.git(repo, "commit", "-qm", "fixture")
        return repo, self.git(repo, "rev-parse", "HEAD")

    def test_git_environment_helper_is_in_default_soza_evidence_boundary(self):
        self.assertIn(
            "runtime/integration/git_object_environment.py",
            subject.SOZA_EVIDENCE_PATHS,
        )

    def test_soza_source_identity_ignores_ambient_object_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo, head = self.make_repo(root)
            empty_objects = root / "external-objects"
            empty_objects.mkdir()

            with mock.patch.dict(
                os.environ,
                {"GIT_OBJECT_DIRECTORY": str(empty_objects)},
                clear=False,
            ):
                observation = subject._verify_soza_source_identity(
                    repo,
                    paths=["runtime/integration/git_object_environment.py"],
                    expected_head=head,
                )

        self.assertEqual(head, observation["head"])
        self.assertTrue(observation["gitObjectEnvironmentControlled"])
        self.assertTrue(observation["replaceObjectsDisabled"])

    def test_dirty_git_environment_helper_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo, _ = self.make_repo(root)
            helper = repo / "runtime/integration/git_object_environment.py"
            helper.write_text("VALUE = 'changed'\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "未commit変更"):
                subject._verify_soza_source_identity(
                    repo,
                    paths=["runtime/integration/git_object_environment.py"],
                )


if __name__ == "__main__":
    unittest.main()
