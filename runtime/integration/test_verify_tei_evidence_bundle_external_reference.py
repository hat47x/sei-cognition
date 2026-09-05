import hashlib
import io
import json
import subprocess
import tarfile
import tempfile
import unittest
from pathlib import Path

import verify_tei_evidence_bundle as subject


class TEIEvidenceBundleExternalReferenceTest(unittest.TestCase):
    def make_reference_repo(self, root: Path) -> tuple[Path, dict[str, str]]:
        repo = root / "reference-repo"
        (repo / "reference/workspace/.tei").mkdir(parents=True)
        (repo / "reference/workspace/input.txt").write_text(
            "fixed input\n", encoding="utf-8"
        )
        (repo / "reference/workspace/.tei/plugin-lock.json").write_text(
            '{"plugins":[]}\n', encoding="utf-8"
        )
        (repo / "reference/order_rollout.durable-run.m0.21.start.json").write_text(
            '{"run":"fixed"}\n', encoding="utf-8"
        )
        subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True)
        subprocess.run(
            ["git", "-C", str(repo), "config", "user.email", "test@example.invalid"],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(repo), "config", "user.name", "test"], check=True
        )
        subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-qm", "fixture"], check=True)

        def object_id(path: str) -> str:
            return subprocess.run(
                ["git", "-C", str(repo), "rev-parse", f"HEAD:{path}"],
                check=True,
                text=True,
                stdout=subprocess.PIPE,
            ).stdout.strip()

        expected = {
            "source_commit": "a" * 40,
            "workspace_tree": object_id("reference/workspace"),
            "run_blob": object_id(
                "reference/order_rollout.durable-run.m0.21.start.json"
            ),
            "plugin_lock_blob": object_id(
                "reference/workspace/.tei/plugin-lock.json"
            ),
        }
        return repo, expected

    def build_legacy_bundle(
        self,
        root: Path,
        reference_repo: Path,
        *,
        mutate_run: bool = False,
    ) -> Path:
        archive = root / "legacy-a.tar.gz"
        binary = b"historical-tei-binary"
        provider = b'{"executors":[{"executorId":"reference"}]}\n'
        metadata = {
            "schema": subject.SCHEMA,
            "repository": subject.REPOSITORY,
            "source_commit": "a" * 40,
            "entry_point": subject.ENTRY_POINT,
            "binary_sha256": hashlib.sha256(binary).hexdigest(),
            "provider_plan_sha256": hashlib.sha256(provider).hexdigest(),
        }

        with tarfile.open(archive, "w:gz") as tar:
            def add_file(name: str, raw: bytes, mode: int = 0o644) -> None:
                info = tarfile.TarInfo(name)
                info.size = len(raw)
                info.mode = mode
                tar.addfile(info, io.BytesIO(raw))

            def add_dir(name: str) -> None:
                info = tarfile.TarInfo(name)
                info.type = tarfile.DIRTYPE
                info.mode = 0o755
                tar.addfile(info)

            add_file("metadata.json", json.dumps(metadata).encode("utf-8"))
            add_file("provider-plan.json", provider)
            add_file("bin/tei", binary, 0o755)
            add_dir("reference")
            add_dir("reference/workspace")
            add_dir("reference/workspace/.tei")
            add_file(
                "reference/workspace/input.txt",
                (reference_repo / "reference/workspace/input.txt").read_bytes(),
            )
            add_file(
                "reference/workspace/.tei/plugin-lock.json",
                (
                    reference_repo
                    / "reference/workspace/.tei/plugin-lock.json"
                ).read_bytes(),
            )
            run = (
                reference_repo
                / "reference/order_rollout.durable-run.m0.21.start.json"
            ).read_bytes()
            if mutate_run:
                run = b'{"run":"mutated"}\n'
            add_file(
                "reference/order_rollout.durable-run.m0.21.start.json",
                run,
            )
        return archive

    def test_legacy_bundle_reference_bytes_can_be_bound_to_external_fixed_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo, expected = self.make_reference_repo(root)
            archive = self.build_legacy_bundle(root, repo)
            result = subject.verify_bundle(
                archive,
                expected_source_commit="a" * 40,
                expected_reference_input=expected,
            )
        self.assertEqual(expected, result["referenceInput"])

    def test_legacy_bundle_reference_byte_drift_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo, expected = self.make_reference_repo(root)
            archive = self.build_legacy_bundle(root, repo, mutate_run=True)
            with self.assertRaisesRegex(ValueError, "期待値と一致しません"):
                subject.verify_bundle(
                    archive,
                    expected_source_commit="a" * 40,
                    expected_reference_input=expected,
                )

    def test_external_fixed_identity_must_be_complete(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo, expected = self.make_reference_repo(root)
            archive = self.build_legacy_bundle(root, repo)
            expected.pop("plugin_lock_blob")
            with self.assertRaisesRegex(ValueError, "不足"):
                subject.verify_bundle(
                    archive,
                    expected_source_commit="a" * 40,
                    expected_reference_input=expected,
                )


if __name__ == "__main__":
    unittest.main()
