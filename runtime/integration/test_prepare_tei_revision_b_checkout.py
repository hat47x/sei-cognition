import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import prepare_tei_revision_b_checkout as subject


class TEIRevisionBCheckoutPreparationTest(unittest.TestCase):
    def git(self, repo: Path, *args: str, check: bool = True):
        return subprocess.run(
            ["git", "-C", str(repo), *args],
            check=check,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def make_source(self, root: Path) -> tuple[Path, str]:
        source = root / "tei-source"
        source.mkdir()
        self.git(source, "init", "-q")
        self.git(source, "config", "user.email", "test@example.invalid")
        self.git(source, "config", "user.name", "test")
        (source / "cmd/tei").mkdir(parents=True)
        (source / "internal/example").mkdir(parents=True)
        (source / "reference").mkdir(parents=True)
        (source / "cmd/tei/main.go").write_text(
            "package main\n", encoding="utf-8"
        )
        (source / "internal/example/model.go").write_text(
            "package example\n", encoding="utf-8"
        )
        (source / "reference/input.json").write_text("{}\n", encoding="utf-8")
        (source / "go.mod").write_text("module tei\n\ngo 1.23.2\n", encoding="utf-8")
        (source / "go.sum").write_text("", encoding="utf-8")
        self.git(source, "add", ".")
        self.git(source, "commit", "-qm", "fixture")
        head = self.git(source, "rev-parse", "HEAD").stdout.strip()
        return source, head

    @mock.patch.object(subject.source_identity, "verify_repository")
    def test_prepares_independent_detached_checkout_without_touching_dirty_source(
        self, verify_repository
    ):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, head = self.make_source(root)
            dirty = source / "local-note.txt"
            dirty.write_text("do not copy\n", encoding="utf-8")
            output = root / "tei-revision-b"
            observation = {"result": "verified", "head": head}
            verify_repository.side_effect = [observation, observation]

            with mock.patch.object(subject.source_identity, "REVISION_B", head):
                result = subject.prepare_checkout(source, output)

            self.assertTrue(output.is_dir())
            self.assertFalse((output / "local-note.txt").exists())
            self.assertTrue(dirty.is_file())
            self.assertEqual(head, self.git(output, "rev-parse", "HEAD").stdout.strip())
            symbolic = self.git(output, "symbolic-ref", "-q", "HEAD", check=False)
            self.assertNotEqual(0, symbolic.returncode)
            self.assertEqual("prepared_verified", result["result"])
            self.assertEqual(result["sourceStateBefore"], result["sourceStateAfter"])
            self.assertTrue(result["sourceHeadAndStatusUnchanged"])
            self.assertTrue(result["prePublishIdentityVerified"])
            self.assertTrue(result["detachedHead"])
            self.assertEqual("local_no_hardlinks_no_checkout", result["cloneMode"])
            self.assertEqual(2, verify_repository.call_count)
            self.assertEqual(head, verify_repository.call_args_list[0].kwargs["expected_head"])
            self.assertEqual(head, verify_repository.call_args_list[1].kwargs["expected_head"])
            self.assertEqual(output.resolve(), verify_repository.call_args_list[1].args[0])

    def test_missing_revision_is_rejected_before_output_creation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, _ = self.make_source(root)
            output = root / "tei-revision-b"
            with mock.patch.object(subject.source_identity, "REVISION_B", "f" * 40):
                with self.assertRaisesRegex(ValueError, "commit objectがありません"):
                    subject.prepare_checkout(source, output)
            self.assertFalse(output.exists())

    @mock.patch.object(subject.source_identity, "verify_repository")
    def test_output_under_source_is_rejected(self, verify_repository):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, head = self.make_source(root)
            output = source / "generated/revision-b"
            output.parent.mkdir()
            with mock.patch.object(subject.source_identity, "REVISION_B", head):
                with self.assertRaisesRegex(ValueError, "source clone配下"):
                    subject.prepare_checkout(source, output)
            verify_repository.assert_not_called()
            self.assertFalse(output.exists())

    @mock.patch.object(subject.source_identity, "verify_repository")
    def test_pre_publish_verification_failure_leaves_no_final_checkout(
        self, verify_repository
    ):
        verify_repository.side_effect = ValueError("identity mismatch")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, head = self.make_source(root)
            output = root / "tei-revision-b"
            with mock.patch.object(subject.source_identity, "REVISION_B", head):
                with self.assertRaisesRegex(ValueError, "identity mismatch"):
                    subject.prepare_checkout(source, output)
            self.assertFalse(output.exists())
            self.assertFalse(
                any(path.name.startswith(f".{output.name}.prepare-") for path in root.iterdir())
            )

    @mock.patch.object(subject.source_identity, "verify_repository")
    def test_post_publish_verification_failure_removes_published_checkout(
        self, verify_repository
    ):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, head = self.make_source(root)
            output = root / "tei-revision-b"
            verify_repository.side_effect = [
                {"result": "verified", "head": head},
                ValueError("post publish mismatch"),
            ]
            with mock.patch.object(subject.source_identity, "REVISION_B", head):
                with self.assertRaisesRegex(ValueError, "post publish mismatch"):
                    subject.prepare_checkout(source, output)
            self.assertFalse(output.exists())
            self.assertFalse(
                any(path.name.startswith(f".{output.name}.prepare-") for path in root.iterdir())
            )

    def test_existing_output_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, head = self.make_source(root)
            output = root / "tei-revision-b"
            output.mkdir()
            with mock.patch.object(subject.source_identity, "REVISION_B", head):
                with self.assertRaisesRegex(ValueError, "新規path"):
                    subject.prepare_checkout(source, output)


if __name__ == "__main__":
    unittest.main()
