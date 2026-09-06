import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import git_object_environment as git_env
import verify_tei_execution_source_identity as source_identity


class GitObjectEnvironmentTest(unittest.TestCase):
    def git(self, repo: Path, *args: str, env=None) -> str:
        process = subprocess.run(
            ["git", "-C", str(repo), *args],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
        )
        return process.stdout.strip()

    def make_repo(self, root: Path) -> tuple[Path, str, str]:
        repo = root / "repo"
        repo.mkdir()
        self.git(repo, "init", "-q")
        self.git(repo, "config", "user.email", "test@example.invalid")
        self.git(repo, "config", "user.name", "test")
        (repo / "f.txt").write_text("base\n", encoding="utf-8")
        self.git(repo, "add", "f.txt")
        self.git(repo, "commit", "-qm", "base")
        head = self.git(repo, "rev-parse", "HEAD")
        blob = self.git(repo, "rev-parse", "HEAD:f.txt")
        return repo, head, blob

    def test_controlled_environment_removes_object_graph_overrides(self):
        base = {
            "PATH": os.environ.get("PATH", ""),
            "GIT_DIR": "/tmp/not-the-repo",
            "GIT_WORK_TREE": "/tmp/not-the-worktree",
            "GIT_COMMON_DIR": "/tmp/not-the-common-dir",
            "GIT_OBJECT_DIRECTORY": "/tmp/not-the-object-dir",
            "GIT_ALTERNATE_OBJECT_DIRECTORIES": "/tmp/not-the-alternate-dir",
            "GIT_INDEX_FILE": "/tmp/not-the-index",
            "GIT_NAMESPACE": "other",
            "GIT_REPLACE_REF_BASE": "refs/other-replace/",
            "GIT_GRAFT_FILE": "/tmp/not-the-graft-file",
            "GIT_DEFAULT_HASH": "sha256",
        }

        env = git_env.controlled_git_environment(base)

        for key in git_env.UNTRUSTED_GIT_ENVIRONMENT:
            self.assertNotIn(key, env)
        self.assertEqual("1", env["GIT_NO_REPLACE_OBJECTS"])
        self.assertEqual("sha1", env["GIT_DEFAULT_HASH"])
        self.assertEqual(base["PATH"], env["PATH"])

    def test_verifier_ignores_ambient_git_object_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo, head, blob = self.make_repo(root)
            empty_objects = root / "empty-objects"
            empty_objects.mkdir()

            poisoned = dict(os.environ)
            poisoned["GIT_OBJECT_DIRECTORY"] = str(empty_objects)
            direct = subprocess.run(
                ["git", "-C", str(repo), "cat-file", "-e", f"{head}^{{commit}}"],
                check=False,
                env=poisoned,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.assertNotEqual(0, direct.returncode)

            with mock.patch.dict(
                os.environ,
                {"GIT_OBJECT_DIRECTORY": str(empty_objects)},
                clear=False,
            ):
                observation = source_identity.verify_repository(
                    repo,
                    expected_objects={"f.txt": blob},
                    expected_head=head,
                )

        self.assertEqual(head, observation["head"])
        self.assertEqual(blob, observation["executionSourceObjects"]["f.txt"])
        self.assertTrue(observation["gitObjectEnvironmentControlled"])
        self.assertTrue(observation["replaceObjectsDisabled"])

    def test_verifier_ignores_replace_ref_for_literal_commit_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo, base_head, base_blob = self.make_repo(root)

            (repo / "f.txt").write_text("replacement\n", encoding="utf-8")
            self.git(repo, "add", "f.txt")
            self.git(repo, "commit", "-qm", "replacement")
            replacement_head = self.git(repo, "rev-parse", "HEAD")
            replacement_blob = self.git(repo, "rev-parse", "HEAD:f.txt")
            self.assertNotEqual(base_blob, replacement_blob)

            self.git(repo, "checkout", "--detach", "-q", base_head)
            self.git(repo, "replace", base_head, replacement_head)

            # Normal Git resolution now substitutes replacement content for the same
            # base commit name.  The source-identity verifier must not do so.
            substituted = self.git(repo, "rev-parse", f"{base_head}:f.txt")
            self.assertEqual(replacement_blob, substituted)

            observation = source_identity.verify_repository(
                repo,
                expected_objects={"f.txt": base_blob},
                expected_head=base_head,
            )

        self.assertEqual(base_blob, observation["executionSourceObjects"]["f.txt"])
        self.assertTrue(observation["replaceObjectsDisabled"])


if __name__ == "__main__":
    unittest.main()
