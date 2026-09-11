import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import prepare_runtime_version_exchange_inputs as subject
from prepare_runtime_version_exchange_archives import Verification


RUNTIME_MANIFEST = {
    "runtimeArchives": {
        "a": {
            "runtime": "ollama",
            "version": "0.32.13",
            "localFileName": "runtime-a.tar.zst",
            "sizeBytes": 3,
            "sha256": "a" * 64,
            "downloadUrl": "https://example.invalid/runtime-a",
        },
        "b": {
            "runtime": "ollama",
            "version": "0.32.14",
            "localFileName": "runtime-b.tar.zst",
            "sizeBytes": 4,
            "sha256": "b" * 64,
            "downloadUrl": "https://example.invalid/runtime-b",
        },
    }
}


def model_verification(model_dir: Path) -> dict[str, object]:
    return {
        "model": "qwen2.5:0.5b",
        "modelStore": str(model_dir.resolve(strict=True)),
        "manifestSha256": "c" * 64,
        "referencedBlobCount": 2,
        "referencedBytesTotal": 10,
    }


class RuntimeExchangePrepositionedInputPreparationTest(unittest.TestCase):
    def test_new_root_prepares_both_archives_and_model_store(self):
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            soza_root = parent / "soza-repository"
            soza_root.mkdir()
            root = parent / "inputs"

            def download(_url, target, size, sha256, opener=None):
                del opener
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(b"x")
                return Verification(target.resolve(strict=True), size, sha256)

            def prepare_model(model_dir, **_kwargs):
                model_dir.mkdir(parents=True)

            with (
                patch.object(subject, "SOZA_ROOT", soza_root),
                patch.object(subject, "load_runtime_manifest", return_value=RUNTIME_MANIFEST),
                patch.object(subject, "download_archive", side_effect=download),
                patch.object(subject, "prepare_model_store", side_effect=prepare_model),
                patch.object(subject, "verify_model_store", side_effect=model_verification),
            ):
                result = subject.prepare_prepositioned_inputs(root)

            self.assertEqual("ok", result["result"])
            self.assertEqual(
                ["downloaded", "downloaded"],
                [item["acquisition"] for item in result["runtimeArchives"]],
            )
            self.assertEqual("downloaded", result["model"]["acquisition"])
            runner = result["verifiedRunnerInputs"]
            self.assertTrue(runner["requirePrepositionedArtifacts"])
            self.assertTrue(runner["runtimeAArchive"].endswith("runtime-a.tar.zst"))
            self.assertTrue(runner["runtimeBArchive"].endswith("runtime-b.tar.zst"))

    def test_existing_model_store_is_reverified_without_preparation(self):
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            soza_root = parent / "soza-repository"
            soza_root.mkdir()
            root = parent / "inputs"
            model_dir = root / "ollama-models"
            model_dir.mkdir(parents=True)

            def download(_url, target, size, sha256, opener=None):
                del opener
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(b"x")
                return Verification(target.resolve(strict=True), size, sha256)

            with (
                patch.object(subject, "SOZA_ROOT", soza_root),
                patch.object(subject, "load_runtime_manifest", return_value=RUNTIME_MANIFEST),
                patch.object(subject, "download_archive", side_effect=download),
                patch.object(subject, "prepare_model_store") as prepare_model,
                patch.object(subject, "verify_model_store", side_effect=model_verification),
            ):
                result = subject.prepare_prepositioned_inputs(root)

            prepare_model.assert_not_called()
            self.assertEqual("verified-existing", result["model"]["acquisition"])

    def test_verify_only_does_not_download_or_prepare(self):
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            soza_root = parent / "soza-repository"
            soza_root.mkdir()
            root = parent / "inputs"
            archive_dir = root / "runtime-archives"
            archive_dir.mkdir(parents=True)
            (archive_dir / "runtime-a.tar.zst").write_bytes(b"a")
            (archive_dir / "runtime-b.tar.zst").write_bytes(b"b")
            model_dir = root / "ollama-models"
            model_dir.mkdir()

            def verify_archive(target, size, sha256):
                return Verification(target.resolve(strict=True), size, sha256)

            with (
                patch.object(subject, "SOZA_ROOT", soza_root),
                patch.object(subject, "load_runtime_manifest", return_value=RUNTIME_MANIFEST),
                patch.object(subject, "verify_archive", side_effect=verify_archive),
                patch.object(subject, "download_archive") as download,
                patch.object(subject, "prepare_model_store") as prepare_model,
                patch.object(subject, "verify_model_store", side_effect=model_verification),
            ):
                result = subject.prepare_prepositioned_inputs(root, verify_only=True)

            download.assert_not_called()
            prepare_model.assert_not_called()
            self.assertEqual(
                ["verified-existing", "verified-existing"],
                [item["acquisition"] for item in result["runtimeArchives"]],
            )
            self.assertEqual("verified-existing", result["model"]["acquisition"])

    def test_root_inside_soza_repository_is_rejected_before_acquisition(self):
        with tempfile.TemporaryDirectory() as temporary:
            soza_root = Path(temporary) / "soza-repository"
            soza_root.mkdir()
            with (
                patch.object(subject, "SOZA_ROOT", soza_root),
                patch.object(subject, "download_archive") as download,
                patch.object(subject, "prepare_model_store") as prepare_model,
            ):
                with self.assertRaisesRegex(ValueError, "SEI repository配下"):
                    subject.prepare_prepositioned_inputs(soza_root / "inputs")
            download.assert_not_called()
            prepare_model.assert_not_called()


if __name__ == "__main__":
    unittest.main()
