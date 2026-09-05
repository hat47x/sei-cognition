import io
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import prepare_tei_fixed_reference_input as subject


class TEIFixedReferenceInputPreparationTest(unittest.TestCase):
    def make_archive(self, root: Path, *, symlink: bool = False) -> Path:
        archive = root / "historical-a.tar.gz"
        with tarfile.open(archive, "w:gz") as tar:
            def add_dir(name: str) -> None:
                info = tarfile.TarInfo(name)
                info.type = tarfile.DIRTYPE
                info.mode = 0o755
                tar.addfile(info)

            def add_file(name: str, raw: bytes) -> None:
                info = tarfile.TarInfo(name)
                info.size = len(raw)
                info.mode = 0o644
                tar.addfile(info, io.BytesIO(raw))

            add_dir("reference")
            add_dir("reference/workspace")
            add_dir("reference/workspace/.tei")
            add_file("reference/workspace/input.txt", b"fixed input\n")
            add_file(
                "reference/workspace/.tei/plugin-lock.json",
                b'{"plugins":[]}\n',
            )
            add_file(
                "reference/order_rollout.durable-run.m0.21.start.json",
                b'{"run":"fixed"}\n',
            )
            add_file("bin/tei", b"do-not-materialize")
            if symlink:
                info = tarfile.TarInfo("reference/workspace/link")
                info.type = tarfile.SYMTYPE
                info.linkname = "input.txt"
                tar.addfile(info)
        return archive

    def verified_result(self, archive: Path) -> dict[str, object]:
        return {
            "result": "verified",
            "observation": {"archive_sha256": "f" * 64},
            "referenceInput": dict(subject.EXPECTED_REFERENCE),
        }

    @mock.patch.object(subject.bundle_verifier, "verify_bundle")
    def test_verification_binds_historical_bundle_to_exact_a_identity(self, verify):
        with tempfile.TemporaryDirectory() as tmp:
            archive = self.make_archive(Path(tmp))
            verify.return_value = self.verified_result(archive)
            result = subject.verify_fixed_reference_input_bundle(archive)

        self.assertEqual("historical_evidence_bundle", result["acquisitionMode"])
        self.assertEqual(subject.source_identity.REVISION_A, result["sourceCommit"])
        self.assertEqual(
            subject.source_identity.REVISION_A_REFERENCE_OBJECTS,
            result["executionSourceObjects"],
        )
        verify.assert_called_once()
        kwargs = verify.call_args.kwargs
        self.assertEqual(subject.source_identity.REVISION_A, kwargs["expected_source_commit"])
        self.assertEqual(subject.REVISION_A_BINARY_SHA256, kwargs["expected_binary_sha256"])
        self.assertEqual(
            subject.REVISION_A_PROVIDER_PLAN_SHA256,
            kwargs["expected_provider_plan_sha256"],
        )
        self.assertEqual(subject.EXPECTED_REFERENCE, kwargs["expected_reference_input"])

    @mock.patch.object(subject.bundle_verifier, "verify_bundle")
    def test_materialize_copies_only_fixed_reference_input(self, verify):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive = self.make_archive(root)
            verify.return_value = self.verified_result(archive)
            output = root / "materialized"
            result = subject.materialize_fixed_reference_input_bundle(archive, output)

            self.assertEqual(b"fixed input\n", (output / "reference/workspace/input.txt").read_bytes())
            self.assertTrue((output / subject.FIXED_RUN).is_file())
            self.assertTrue((output / subject.FIXED_PLUGIN_LOCK).is_file())
            self.assertFalse((output / "bin/tei").exists())
            self.assertEqual(str(output.resolve()), result["materializedRoot"])

    @mock.patch.object(subject.bundle_verifier, "verify_bundle")
    def test_link_member_is_rejected_even_after_identity_verifier(self, verify):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive = self.make_archive(root, symlink=True)
            verify.return_value = self.verified_result(archive)
            output = root / "materialized"
            with self.assertRaisesRegex(ValueError, "link/device"):
                subject.materialize_fixed_reference_input_bundle(archive, output)
            self.assertFalse(output.exists())

    @mock.patch.object(subject.bundle_verifier, "verify_bundle")
    def test_existing_output_is_not_overwritten(self, verify):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive = self.make_archive(root)
            verify.return_value = self.verified_result(archive)
            output = root / "materialized"
            output.mkdir()
            marker = output / "keep.txt"
            marker.write_text("keep\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "新規path"):
                subject.materialize_fixed_reference_input_bundle(archive, output)
            self.assertEqual("keep\n", marker.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
