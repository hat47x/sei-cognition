import hashlib
import io
import json
import tarfile
import tempfile
import unittest
from pathlib import Path

import verify_tei_evidence_bundle as subject


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
                elif kind == "symlink":
                    info.type = tarfile.SYMTYPE
                    info.linkname = "metadata.json"
                    tar.addfile(info)
                else:
                    raise AssertionError(kind)
        return archive

    def test_valid_bundle_is_verified(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive = self.build_bundle(Path(tmp))
            result = subject.verify_bundle(archive, expected_source_commit="a" * 40)
        self.assertEqual("verified", result["result"])
        self.assertTrue(result["observation"]["provider_surface_recognized"])
        self.assertTrue(result["observation"]["binary_executable"])
        self.assertEqual("not_evaluated", result["qualityJudgement"])

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
