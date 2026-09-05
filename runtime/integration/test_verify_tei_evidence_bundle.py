import hashlib
import io
import json
import tarfile
import tempfile
import unittest
from pathlib import Path

import verify_tei_evidence_bundle as subject


def git_blob(raw: bytes) -> str:
    header = f"blob {len(raw)}\0".encode("ascii")
    return hashlib.sha1(header + raw).hexdigest()


def git_tree(entries: list[tuple[str, str, str]]) -> str:
    body = bytearray()
    sortable: list[tuple[bytes, str, str, str]] = []
    for mode, name, digest in entries:
        sort_key = name.encode("utf-8") + (b"/" if mode == "40000" else b"")
        sortable.append((sort_key, mode, name, digest))
    for _, mode, name, digest in sorted(sortable, key=lambda entry: entry[0]):
        body.extend(mode.encode("ascii"))
        body.extend(b" ")
        body.extend(name.encode("utf-8"))
        body.extend(b"\0")
        body.extend(bytes.fromhex(digest))
    header = f"tree {len(body)}\0".encode("ascii")
    return hashlib.sha1(header + body).hexdigest()


class TEIEvidenceBundleVerificationTest(unittest.TestCase):
    def build_bundle(
        self,
        root: Path,
        *,
        source_commit: str = "a" * 40,
        provider_plan: dict[str, object] | None = None,
        metadata_override: dict[str, object] | None = None,
        extra_members: list[tuple[str, bytes, str]] | None = None,
        executable: bool = True,
    ) -> Path:
        binary = b"fake-tei-binary"
        plan = provider_plan or {"executors": [{"executorId": "reference"}]}
        plan_bytes = json.dumps(plan, sort_keys=True).encode("utf-8")
        metadata = {
            "schema": subject.SCHEMA,
            "repository": subject.REPOSITORY,
            "source_commit": source_commit,
            "entry_point": subject.ENTRY_POINT,
            "binary_sha256": hashlib.sha256(binary).hexdigest(),
            "provider_plan_sha256": hashlib.sha256(plan_bytes).hexdigest(),
            "go_version": "go version test linux/amd64",
        }
        if metadata_override:
            metadata.update(metadata_override)

        archive = root / "bundle.tar.gz"
        with tarfile.open(archive, "w:gz") as tar:
            files = [
                ("metadata.json", json.dumps(metadata).encode("utf-8"), 0o644),
                ("provider-plan.json", plan_bytes, 0o644),
                ("bin/tei", binary, 0o755 if executable else 0o644),
            ]
            for name, data, mode in files:
                info = tarfile.TarInfo(name)
                info.size = len(data)
                info.mode = mode
                tar.addfile(info, io.BytesIO(data))
            for name, data, kind in extra_members or []:
                info = tarfile.TarInfo(name)
                if kind == "file":
                    info.size = len(data)
                    info.mode = 0o644
                    tar.addfile(info, io.BytesIO(data))
                elif kind == "dir":
                    info.type = tarfile.DIRTYPE
                    info.mode = 0o755
                    tar.addfile(info)
                elif kind == "symlink":
                    info.type = tarfile.SYMTYPE
                    info.linkname = "metadata.json"
                    tar.addfile(info)
                else:
                    raise AssertionError(kind)
        return archive

    def fixed_reference_fixture(
        self, *, run_bytes: bytes = b'{"run":"fixed"}\n'
    ) -> tuple[dict[str, object], list[tuple[str, bytes, str]], dict[str, str]]:
        input_bytes = b"fixed input\n"
        plugin_lock = b'{"plugins":[]}\n'
        plugin_blob = git_blob(plugin_lock)
        tei_tree = git_tree([("100644", "plugin-lock.json", plugin_blob)])
        input_blob = git_blob(input_bytes)
        workspace_tree = git_tree(
            [
                ("40000", ".tei", tei_tree),
                ("100644", "input.txt", input_blob),
            ]
        )
        run_blob = git_blob(run_bytes)
        source_commit = "c" * 40
        metadata = {
            "reference_input_source_commit": source_commit,
            "reference_workspace_tree": workspace_tree,
            "reference_run_blob": run_blob,
            "reference_plugin_lock_blob": plugin_blob,
        }
        members = [
            ("reference", b"", "dir"),
            ("reference/workspace", b"", "dir"),
            ("reference/workspace/.tei", b"", "dir"),
            ("reference/workspace/.tei/plugin-lock.json", plugin_lock, "file"),
            ("reference/workspace/input.txt", input_bytes, "file"),
            ("reference/order_rollout.durable-run.m0.21.start.json", run_bytes, "file"),
        ]
        expected = {
            "source_commit": source_commit,
            "workspace_tree": workspace_tree,
            "run_blob": run_blob,
            "plugin_lock_blob": plugin_blob,
        }
        return metadata, members, expected

    def test_valid_bundle_is_verified(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive = self.build_bundle(Path(tmp))
            result = subject.verify_bundle(archive, expected_source_commit="a" * 40)
        self.assertEqual("verified", result["result"])
        self.assertTrue(result["observation"]["provider_surface_recognized"])
        self.assertTrue(result["observation"]["binary_executable"])
        self.assertNotIn("referenceInput", result)
        self.assertEqual("not_evaluated", result["qualityJudgement"])

    def test_fixed_reference_bytes_are_reverified(self):
        with tempfile.TemporaryDirectory() as tmp:
            metadata, members, expected = self.fixed_reference_fixture()
            archive = self.build_bundle(
                Path(tmp), metadata_override=metadata, extra_members=members
            )
            result = subject.verify_bundle(archive)
        self.assertEqual(expected, result["referenceInput"])

    def test_fixed_reference_run_byte_drift_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            metadata, members, _ = self.fixed_reference_fixture()
            mutated = []
            for name, data, kind in members:
                if name == "reference/order_rollout.durable-run.m0.21.start.json":
                    data = b'{"run":"mutated"}\n'
                mutated.append((name, data, kind))
            archive = self.build_bundle(
                Path(tmp), metadata_override=metadata, extra_members=mutated
            )
            with self.assertRaisesRegex(ValueError, "fixed reference input Git object identity"):
                subject.verify_bundle(archive)

    def test_fixed_reference_workspace_byte_drift_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            metadata, members, _ = self.fixed_reference_fixture()
            mutated = []
            for name, data, kind in members:
                if name == "reference/workspace/input.txt":
                    data = b"mutated input\n"
                mutated.append((name, data, kind))
            archive = self.build_bundle(
                Path(tmp), metadata_override=metadata, extra_members=mutated
            )
            with self.assertRaisesRegex(ValueError, "fixed reference input Git object identity"):
                subject.verify_bundle(archive)

    def test_partial_fixed_reference_metadata_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive = self.build_bundle(
                Path(tmp),
                metadata_override={"reference_input_source_commit": "c" * 40},
            )
            with self.assertRaisesRegex(ValueError, "metadataが部分的"):
                subject.verify_bundle(archive)

    def test_binary_digest_drift_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive = self.build_bundle(
                Path(tmp), metadata_override={"binary_sha256": "b" * 64}
            )
            with self.assertRaisesRegex(ValueError, "actual binary SHA-256"):
                subject.verify_bundle(archive)

    def test_unknown_provider_plan_field_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive = self.build_bundle(Path(tmp), provider_plan={"unknown": True})
            with self.assertRaisesRegex(ValueError, "unknown top-level field"):
                subject.verify_bundle(archive)

    def test_path_traversal_member_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive = self.build_bundle(
                Path(tmp), extra_members=[("../escape", b"x", "file")]
            )
            with self.assertRaisesRegex(ValueError, "member pathが不正"):
                subject.verify_bundle(archive)

    def test_symlink_member_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive = self.build_bundle(
                Path(tmp), extra_members=[("link", b"", "symlink")]
            )
            with self.assertRaisesRegex(ValueError, "link/device member"):
                subject.verify_bundle(archive)

    def test_non_executable_binary_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive = self.build_bundle(Path(tmp), executable=False)
            with self.assertRaisesRegex(ValueError, "executable bit"):
                subject.verify_bundle(archive)

    def test_expected_source_commit_mismatch_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive = self.build_bundle(Path(tmp))
            with self.assertRaisesRegex(ValueError, "source commitが期待値"):
                subject.verify_bundle(archive, expected_source_commit="b" * 40)


if __name__ == "__main__":
    unittest.main()
