import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import verify_runtime_version_exchange_model_store as verifier


DEFAULT_MANIFEST_PATH = Path(
    "manifests/registry.ollama.ai/library/qwen2.5/0.5b"
)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class RuntimeVersionExchangeModelStoreVerifierTest(unittest.TestCase):
    def make_store(self, root: Path) -> tuple[str, dict[str, bytes], Path]:
        blobs = {
            "config": b'{"model_format":"gguf"}\n',
            "weights": b"synthetic-model-weights\n",
            "template": b"{{ .Prompt }}\n",
        }
        layers = []
        for name in ("weights", "template"):
            data = blobs[name]
            layers.append(
                {
                    "mediaType": "application/vnd.ollama.image.model",
                    "digest": f"sha256:{digest(data)}",
                    "size": len(data),
                }
            )
        manifest = {
            "schemaVersion": 2,
            "mediaType": "application/vnd.docker.distribution.manifest.v2+json",
            "config": {
                "mediaType": "application/vnd.docker.container.image.v1+json",
                "digest": f"sha256:{digest(blobs['config'])}",
                "size": len(blobs["config"]),
            },
            "layers": layers,
        }
        raw_manifest = (
            json.dumps(manifest, ensure_ascii=False, separators=(",", ":")) + "\n"
        ).encode("utf-8")

        manifest_path = root / DEFAULT_MANIFEST_PATH
        manifest_path.parent.mkdir(parents=True)
        manifest_path.write_bytes(raw_manifest)
        blob_dir = root / "blobs"
        blob_dir.mkdir()
        for data in blobs.values():
            (blob_dir / f"sha256-{digest(data)}").write_bytes(data)
        return digest(raw_manifest), blobs, manifest_path

    def verify_fixture(self, root: Path, manifest_sha: str):
        return verifier.verify_model_store(
            root,
            expected_model_name="qwen2.5:0.5b",
            expected_manifest_sha256=manifest_sha,
            manifest_relative_path=DEFAULT_MANIFEST_PATH.as_posix(),
        )

    def test_fixed_artifact_manifest_declares_ollama_store_digest_basis(self):
        fixed = verifier._load_fixed_model_identity()
        self.assertEqual("qwen2.5:0.5b", fixed["name"])
        self.assertEqual(
            "a8b0c51577010a279d933d14c2a8ab4b268079d44c5c8830c0a93900f1827c67",
            fixed["sha256"],
        )
        self.assertEqual(DEFAULT_MANIFEST_PATH.as_posix(), fixed["storeManifestPath"])
        self.assertEqual("ollama-manifest-raw-bytes-sha256", fixed["digestBasis"])

    def test_matching_store_verifies_manifest_and_all_referenced_blobs(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest_sha, blobs, _manifest_path = self.make_store(root)
            result = self.verify_fixture(root, manifest_sha)

        self.assertTrue(result["verified"])
        self.assertEqual(manifest_sha, result["manifestSha256"])
        self.assertEqual(len(blobs), result["referencedBlobCount"])
        self.assertEqual(
            sum(len(data) for data in blobs.values()), result["referencedBytesTotal"]
        )
        self.assertEqual("declared-size+actual-sha256", result["blobVerification"])

    def test_manifest_raw_bytes_are_identity_even_when_json_meaning_is_same(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest_sha, _blobs, manifest_path = self.make_store(root)
            parsed = json.loads(manifest_path.read_bytes())
            manifest_path.write_text(
                json.dumps(parsed, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "manifestのraw SHA-256"):
                self.verify_fixture(root, manifest_sha)

    def test_missing_referenced_blob_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest_sha, blobs, _manifest_path = self.make_store(root)
            target = root / "blobs" / f"sha256-{digest(blobs['weights'])}"
            target.unlink()
            with self.assertRaises((FileNotFoundError, ValueError)):
                self.verify_fixture(root, manifest_sha)

    def test_blob_size_mismatch_is_rejected_before_digest_acceptance(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest_sha, blobs, _manifest_path = self.make_store(root)
            target = root / "blobs" / f"sha256-{digest(blobs['weights'])}"
            target.write_bytes(blobs["weights"] + b"x")
            with self.assertRaisesRegex(ValueError, "blob size"):
                self.verify_fixture(root, manifest_sha)

    def test_same_size_blob_tampering_is_rejected_by_sha256(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest_sha, blobs, _manifest_path = self.make_store(root)
            target = root / "blobs" / f"sha256-{digest(blobs['weights'])}"
            target.write_bytes(b"x" * len(blobs["weights"]))
            with self.assertRaisesRegex(ValueError, "blob SHA-256"):
                self.verify_fixture(root, manifest_sha)

    def test_symlinked_manifest_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest_sha, _blobs, manifest_path = self.make_store(root)
            real_manifest = root / "real-manifest"
            real_manifest.write_bytes(manifest_path.read_bytes())
            manifest_path.unlink()
            try:
                manifest_path.symlink_to(real_manifest)
            except (OSError, NotImplementedError):
                self.skipTest("symlinkを作成できない環境です")
            with self.assertRaisesRegex(ValueError, "symlink"):
                self.verify_fixture(root, manifest_sha)

    def test_model_store_root_symlink_is_rejected_before_identity_verification(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            actual_store = base / "actual-models"
            actual_store.mkdir()
            manifest_sha, _blobs, _manifest_path = self.make_store(actual_store)
            model_link = base / "models-link"
            try:
                model_link.symlink_to(actual_store, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("symlinkを作成できない環境です")

            with self.assertRaisesRegex(ValueError, "model store root.*symlink"):
                self.verify_fixture(model_link, manifest_sha)

    def test_model_store_root_with_symlink_parent_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            actual_parent = base / "actual-parent"
            actual_parent.mkdir()
            actual_store = actual_parent / "models"
            actual_store.mkdir()
            manifest_sha, _blobs, _manifest_path = self.make_store(actual_store)
            link_parent = base / "model-parent-link"
            try:
                link_parent.symlink_to(actual_parent, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("symlinkを作成できない環境です")

            with self.assertRaisesRegex(ValueError, "rootのparent.*symlink"):
                self.verify_fixture(link_parent / "models", manifest_sha)

    def test_unreferenced_blob_does_not_change_fixed_model_identity(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest_sha, _blobs, _manifest_path = self.make_store(root)
            extra = b"another-model-layer"
            (root / "blobs" / f"sha256-{digest(extra)}").write_bytes(extra)
            result = self.verify_fixture(root, manifest_sha)
        self.assertTrue(result["verified"])

    def test_manifest_entry_with_invalid_digest_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            _manifest_sha, _blobs, manifest_path = self.make_store(root)
            parsed = json.loads(manifest_path.read_bytes())
            parsed["layers"][0]["digest"] = "sha256:not-a-digest"
            raw = (json.dumps(parsed, separators=(",", ":")) + "\n").encode()
            manifest_path.write_bytes(raw)
            with self.assertRaisesRegex(ValueError, "sha256形式"):
                self.verify_fixture(root, digest(raw))

    def test_duplicate_digest_with_conflicting_size_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            _manifest_sha, _blobs, manifest_path = self.make_store(root)
            parsed = json.loads(manifest_path.read_bytes())
            duplicate = dict(parsed["layers"][0])
            duplicate["size"] += 1
            parsed["layers"].append(duplicate)
            raw = (json.dumps(parsed, separators=(",", ":")) + "\n").encode()
            manifest_path.write_bytes(raw)
            with self.assertRaisesRegex(ValueError, "異なるsize"):
                self.verify_fixture(root, digest(raw))

    def test_output_path_inside_model_store_is_detected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.assertTrue(verifier._is_within(root / "verification.json", root))
            self.assertFalse(verifier._is_within(root.parent / "verification.json", root))

    def test_output_path_through_existing_symlink_into_model_store_is_detected(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            root = base / "models"
            root.mkdir()
            link = base / "model-link"
            try:
                link.symlink_to(root, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("symlinkを作成できない環境です")
            self.assertTrue(verifier._is_within(link / "verification.json", root))

    def test_verification_output_dangling_symlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            model_store = base / "models"
            model_store.mkdir()
            output = base / "verification.json"
            try:
                output.symlink_to(base / "missing-verification-target.json")
            except (OSError, NotImplementedError):
                self.skipTest("symlinkを作成できない環境です")

            with self.assertRaisesRegex(ValueError, "verification output.*symlink"):
                verifier._prepare_output_path(output, model_store)

    def test_verification_output_with_symlink_parent_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            model_store = base / "models"
            model_store.mkdir()
            actual_parent = base / "actual-output-parent"
            actual_parent.mkdir()
            link_parent = base / "output-parent-link"
            try:
                link_parent.symlink_to(actual_parent, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("symlinkを作成できない環境です")

            with self.assertRaisesRegex(ValueError, "outputのparent.*symlink"):
                verifier._prepare_output_path(
                    link_parent / "verification.json",
                    model_store,
                )

    def test_verification_output_external_new_path_is_accepted(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            model_store = base / "models"
            model_store.mkdir()
            output = base / "verification.json"

            prepared = verifier._prepare_output_path(output, model_store)

        self.assertEqual(output.resolve(strict=False), prepared)


if __name__ == "__main__":
    unittest.main()
