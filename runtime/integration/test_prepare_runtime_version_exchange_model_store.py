import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path

import prepare_runtime_version_exchange_model_store as prepare


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class FakeOpener:
    def __init__(self, payloads: dict[str, bytes]):
        self.payloads = payloads
        self.calls: list[str] = []

    def __call__(self, url: str):
        self.calls.append(url)
        if url not in self.payloads:
            raise OSError(f"unexpected URL: {url}")
        return io.BytesIO(self.payloads[url])


class RuntimeVersionExchangeModelStorePreparationTest(unittest.TestCase):
    def fixture(self, *, duplicate: bool = False):
        config = b'{"format":"gguf"}\n'
        model = b"synthetic-model-bytes\n"
        config_digest = sha256(config)
        model_digest = sha256(model)
        layers = [
            {
                "mediaType": "application/vnd.ollama.image.model",
                "digest": f"sha256:{model_digest}",
                "size": len(model),
            }
        ]
        if duplicate:
            layers.append(
                {
                    "mediaType": "application/vnd.ollama.image.model",
                    "digest": f"sha256:{model_digest}",
                    "size": len(model),
                }
            )
        manifest = {
            "schemaVersion": 2,
            "mediaType": "application/vnd.docker.distribution.manifest.v2+json",
            "config": {
                "mediaType": "application/vnd.docker.container.image.v1+json",
                "digest": f"sha256:{config_digest}",
                "size": len(config),
            },
            "layers": layers,
        }
        raw_manifest = (
            json.dumps(manifest, separators=(",", ":"), ensure_ascii=False) + "\n"
        ).encode("utf-8")
        base = "https://registry.ollama.ai/v2/library/test"
        acquisition = {
            "name": "test:fixed",
            "sha256": sha256(raw_manifest),
            "storeManifestPath": "manifests/registry.ollama.ai/library/test/fixed",
            "digestBasis": "ollama-manifest-raw-bytes-sha256",
            "registryManifestUrl": f"{base}/manifests/fixed",
            "registryBlobBaseUrl": f"{base}/blobs",
        }
        payloads = {
            acquisition["registryManifestUrl"]: raw_manifest,
            f"{base}/blobs/sha256:{config_digest}": config,
            f"{base}/blobs/sha256:{model_digest}": model,
        }
        return acquisition, payloads, config_digest, model_digest

    def test_matching_registry_payloads_are_published_atomically(self):
        acquisition, payloads, _config_digest, _model_digest = self.fixture()
        opener = FakeOpener(payloads)
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "models"
            result = prepare.prepare_model_store(
                target,
                opener=opener,
                acquisition=acquisition,
            )
            self.assertTrue(target.is_dir())
            self.assertTrue(result["prepared"])
            self.assertEqual(acquisition["sha256"], result["manifestSha256"])
            self.assertEqual(2, result["referencedBlobCount"])
            self.assertEqual(
                len(payloads) - 1,
                len([url for url in opener.calls if "/blobs/" in url]),
            )
            self.assertIn("/api/tags", result["stopLine"])

    def test_manifest_digest_mismatch_never_publishes_target(self):
        acquisition, payloads, _config_digest, _model_digest = self.fixture()
        acquisition = dict(acquisition)
        acquisition["sha256"] = "0" * 64
        opener = FakeOpener(payloads)
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            target = parent / "models"
            with self.assertRaisesRegex(ValueError, "registry manifestのraw SHA-256"):
                prepare.prepare_model_store(
                    target,
                    opener=opener,
                    acquisition=acquisition,
                )
            self.assertFalse(target.exists())
            self.assertEqual([], list(parent.glob(".models.partial-*")))

    def test_blob_digest_mismatch_never_publishes_target(self):
        acquisition, payloads, _config_digest, model_digest = self.fixture()
        payloads = dict(payloads)
        blob_url = f"{acquisition['registryBlobBaseUrl']}/sha256:{model_digest}"
        payloads[blob_url] = b"x" * len(payloads[blob_url])
        opener = FakeOpener(payloads)
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            target = parent / "models"
            with self.assertRaisesRegex(ValueError, "model blob SHA-256"):
                prepare.prepare_model_store(
                    target,
                    opener=opener,
                    acquisition=acquisition,
                )
            self.assertFalse(target.exists())
            self.assertEqual([], list(parent.glob(".models.partial-*")))

    def test_blob_size_mismatch_never_publishes_target(self):
        acquisition, payloads, config_digest, _model_digest = self.fixture()
        payloads = dict(payloads)
        blob_url = f"{acquisition['registryBlobBaseUrl']}/sha256:{config_digest}"
        payloads[blob_url] = payloads[blob_url] + b"x"
        opener = FakeOpener(payloads)
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "models"
            with self.assertRaisesRegex(ValueError, "model blob size"):
                prepare.prepare_model_store(
                    target,
                    opener=opener,
                    acquisition=acquisition,
                )
            self.assertFalse(target.exists())

    def test_blob_size_overrun_is_rejected_before_excess_bytes_are_written(self):
        payload = b"12345"
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "blob"
            with self.assertRaisesRegex(ValueError, "固定manifestを超えました"):
                prepare._download_blob(
                    "https://registry.ollama.ai/v2/library/test/blobs/sha256:dummy",
                    target,
                    4,
                    sha256(payload[:4]),
                    lambda _url: io.BytesIO(payload),
                )
            self.assertTrue(target.is_file())
            self.assertEqual(b"", target.read_bytes())

    def test_existing_target_is_rejected_before_network_access(self):
        acquisition, payloads, _config_digest, _model_digest = self.fixture()
        opener = FakeOpener(payloads)
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "models"
            target.mkdir()
            with self.assertRaisesRegex(ValueError, "新規path"):
                prepare.prepare_model_store(
                    target,
                    opener=opener,
                    acquisition=acquisition,
                )
        self.assertEqual([], opener.calls)

    def test_target_symlink_is_rejected_before_network_access(self):
        acquisition, payloads, _config_digest, _model_digest = self.fixture()
        opener = FakeOpener(payloads)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            actual = root / "actual-model-store"
            target = root / "models"
            target.symlink_to(actual, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "model store targetにsymlink"):
                prepare.prepare_model_store(
                    target,
                    opener=opener,
                    acquisition=acquisition,
                )
            self.assertFalse(actual.exists())
        self.assertEqual([], opener.calls)

    def test_target_symlink_parent_is_rejected_before_network_access(self):
        acquisition, payloads, _config_digest, _model_digest = self.fixture()
        opener = FakeOpener(payloads)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            actual_parent = root / "actual-parent"
            actual_parent.mkdir()
            linked_parent = root / "linked-parent"
            linked_parent.symlink_to(actual_parent, target_is_directory=True)
            target = linked_parent / "models"
            with self.assertRaisesRegex(ValueError, "parentにsymlink"):
                prepare.prepare_model_store(
                    target,
                    opener=opener,
                    acquisition=acquisition,
                )
            self.assertFalse((actual_parent / "models").exists())
        self.assertEqual([], opener.calls)

    def test_target_deep_symlink_ancestor_is_rejected_before_network_access(self):
        acquisition, payloads, _config_digest, _model_digest = self.fixture()
        opener = FakeOpener(payloads)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            actual_root = root / "actual-root"
            (actual_root / "nested").mkdir(parents=True)
            linked_root = root / "linked-root"
            try:
                linked_root.symlink_to(actual_root, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("symlinkを作成できない環境です")
            target = linked_root / "nested" / "models"
            with self.assertRaisesRegex(ValueError, "ancestorにsymlink"):
                prepare.prepare_model_store(
                    target,
                    opener=opener,
                    acquisition=acquisition,
                )
            self.assertFalse((actual_root / "nested" / "models").exists())
            self.assertEqual([], list((actual_root / "nested").glob(".models.partial-*")))
        self.assertEqual([], opener.calls)

    def test_duplicate_blob_digest_is_downloaded_once(self):
        acquisition, payloads, _config_digest, model_digest = self.fixture(duplicate=True)
        opener = FakeOpener(payloads)
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "models"
            prepare.prepare_model_store(
                target,
                opener=opener,
                acquisition=acquisition,
            )
        model_url = f"{acquisition['registryBlobBaseUrl']}/sha256:{model_digest}"
        self.assertEqual(1, opener.calls.count(model_url))

    def test_target_inside_sei_repository_is_rejected(self):
        acquisition, payloads, _config_digest, _model_digest = self.fixture()
        opener = FakeOpener(payloads)
        target = prepare.SEI_ROOT / ".tmp-runtime-exchange-model-store-test"
        with self.assertRaisesRegex(ValueError, "SEI repository配下"):
            prepare.prepare_model_store(
                target,
                opener=opener,
                acquisition=acquisition,
            )
        self.assertEqual([], opener.calls)
        self.assertFalse(target.exists())

    def test_non_ollama_registry_is_rejected_before_network_access(self):
        acquisition, payloads, _config_digest, _model_digest = self.fixture()
        acquisition = dict(acquisition)
        acquisition["registryManifestUrl"] = "https://example.invalid/manifests/fixed"
        opener = FakeOpener(payloads)
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "models"
            with self.assertRaisesRegex(ValueError, "registry.ollama.ai"):
                prepare.prepare_model_store(
                    target,
                    opener=opener,
                    acquisition=acquisition,
                )
            self.assertFalse(target.exists())
        self.assertEqual([], opener.calls)

    def test_non_https_registry_is_rejected_before_network_access(self):
        acquisition, payloads, _config_digest, _model_digest = self.fixture()
        acquisition = dict(acquisition)
        acquisition["registryBlobBaseUrl"] = "http://registry.ollama.ai/v2/library/test/blobs"
        opener = FakeOpener(payloads)
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "models"
            with self.assertRaisesRegex(ValueError, "https://registry.ollama.ai"):
                prepare.prepare_model_store(
                    target,
                    opener=opener,
                    acquisition=acquisition,
                )
            self.assertFalse(target.exists())
        self.assertEqual([], opener.calls)

    def test_store_manifest_path_must_match_model_name(self):
        acquisition, payloads, _config_digest, _model_digest = self.fixture()
        acquisition = dict(acquisition)
        acquisition["storeManifestPath"] = "manifests/registry.ollama.ai/library/other/fixed"
        opener = FakeOpener(payloads)
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(ValueError, "storeManifestPath.*model.name"):
                prepare.prepare_model_store(
                    Path(temporary) / "models",
                    opener=opener,
                    acquisition=acquisition,
                )
        self.assertEqual([], opener.calls)

    def test_manifest_url_must_match_model_name_even_on_official_host(self):
        acquisition, payloads, _config_digest, _model_digest = self.fixture()
        acquisition = dict(acquisition)
        acquisition["registryManifestUrl"] = (
            "https://registry.ollama.ai/v2/library/other/manifests/fixed"
        )
        opener = FakeOpener(payloads)
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(ValueError, "registryManifestUrl.*model.name"):
                prepare.prepare_model_store(
                    Path(temporary) / "models",
                    opener=opener,
                    acquisition=acquisition,
                )
        self.assertEqual([], opener.calls)

    def test_blob_base_url_must_match_model_name_even_on_official_host(self):
        acquisition, payloads, _config_digest, _model_digest = self.fixture()
        acquisition = dict(acquisition)
        acquisition["registryBlobBaseUrl"] = "https://registry.ollama.ai/v2/library/other/blobs"
        opener = FakeOpener(payloads)
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(ValueError, "registryBlobBaseUrl.*model.name"):
                prepare.prepare_model_store(
                    Path(temporary) / "models",
                    opener=opener,
                    acquisition=acquisition,
                )
        self.assertEqual([], opener.calls)

    def test_model_name_must_include_repository_and_tag(self):
        acquisition, payloads, _config_digest, _model_digest = self.fixture()
        acquisition = dict(acquisition)
        acquisition["name"] = "test"
        opener = FakeOpener(payloads)
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(ValueError, "repository:tag"):
                prepare.prepare_model_store(
                    Path(temporary) / "models",
                    opener=opener,
                    acquisition=acquisition,
                )
        self.assertEqual([], opener.calls)


if __name__ == "__main__":
    unittest.main()
