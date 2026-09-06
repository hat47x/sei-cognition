import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import prepare_tei_revision_b_source as prepare


class RevisionBSourceAcquisitionGitEnvironmentTest(unittest.TestCase):
    def test_initialize_repository_ignores_ambient_default_hash(self):
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary) / "repo"
            repo.mkdir()

            with mock.patch.dict(
                os.environ,
                {"GIT_DEFAULT_HASH": "sha256"},
                clear=False,
            ):
                prepare._initialize_repository(repo)
                observed = prepare._require_git_success(
                    prepare._run_git(repo, "rev-parse", "--show-object-format"),
                    "Git object format確認",
                ).decode().strip()

        self.assertEqual("sha1", observed)

    def test_hash_object_write_ignores_ambient_object_directory(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repo = root / "repo"
            repo.mkdir()
            external_objects = root / "external-objects"
            external_objects.mkdir()

            with mock.patch.dict(
                os.environ,
                {
                    "GIT_OBJECT_DIRECTORY": str(external_objects),
                    "GIT_DEFAULT_HASH": "sha256",
                },
                clear=False,
            ):
                prepare._initialize_repository(repo)
                digest = prepare._hash_blob(repo, b"controlled object\n")

            local_object = repo / ".git" / "objects" / digest[:2] / digest[2:]
            self.assertTrue(local_object.is_file())
            self.assertEqual([], list(external_objects.rglob("*")))
            self.assertEqual(40, len(digest))


if __name__ == "__main__":
    unittest.main()
