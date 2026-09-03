import hashlib
import io
import re
import tempfile
import unittest
from pathlib import Path

import check_runtime_version_exchange_preflight as preflight
import prepare_runtime_version_exchange_archives as prepare


INTEGRATION_DIR = Path(__file__).resolve().parent
HARNESS = INTEGRATION_DIR / "run_runtime_version_exchange.sh"
GO_EXCHANGE_TEST = (
    INTEGRATION_DIR.parent
    / "go"
    / "livemethodintegration"
    / "runtime_version_exchange_test.go"
)


def shell_value(text: str, name: str) -> str:
    match = re.search(rf'^{re.escape(name)}="([^"]+)"$', text, re.MULTILINE)
    if match is None:
        raise AssertionError(f"shell constant not found: {name}")
    return match.group(1)


def go_value(text: str, name: str) -> str:
    match = re.search(rf'^\s*{re.escape(name)}\s*=\s*"([^"]+)"$', text, re.MULTILINE)
    if match is None:
        raise AssertionError(f"Go constant not found: {name}")
    return match.group(1)


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
        return False


class RuntimeVersionExchangeArchivePreparationTest(unittest.TestCase):
    def test_manifest_contains_fixed_runtime_and_model_identity(self):
        manifest = prepare.load_manifest()
        self.assertEqual(
            "4f28c13abe4176503c6fed863383a2d1db2299e9",
            manifest["methodSource"]["commit"],
        )
        self.assertEqual("0.32.13", manifest["runtimeArchives"]["a"]["version"])
        self.assertEqual("0.32.14", manifest["runtimeArchives"]["b"]["version"])
        self.assertEqual(
            "a8b0c51577010a279d933d14c2a8ab4b268079d44c5c8830c0a93900f1827c67",
            manifest["model"]["sha256"],
        )

    def test_manifest_runtime_identity_matches_preflight_harness_and_go(self):
        manifest = prepare.load_manifest()
        harness = HARNESS.read_text(encoding="utf-8")
        go_exchange = GO_EXCHANGE_TEST.read_text(encoding="utf-8")
        pairs = (
            (
                "a",
                "RUNTIME_VERSION_A",
                "RUNTIME_SHA256_A",
                "runtimeExchangeVersionA",
                "runtimeExchangeArtifactA",
            ),
            (
                "b",
                "RUNTIME_VERSION_B",
                "RUNTIME_SHA256_B",
                "runtimeExchangeVersionB",
                "runtimeExchangeArtifactB",
            ),
        )
        for label, shell_version, shell_sha, go_version, go_sha in pairs:
            archive = manifest["runtimeArchives"][label]
            with self.subTest(runtime=label):
                self.assertEqual(archive["version"], shell_value(harness, shell_version))
                self.assertEqual(archive["sha256"], shell_value(harness, shell_sha))
                self.assertEqual(archive["version"], go_value(go_exchange, go_version))
                self.assertEqual(archive["sha256"], go_value(go_exchange, go_sha))

        self.assertEqual(
            manifest["runtimeArchives"]["a"]["sizeBytes"],
            preflight.RUNTIME_SIZE_BYTES_A,
        )
        self.assertEqual(
            manifest["runtimeArchives"]["b"]["sizeBytes"],
            preflight.RUNTIME_SIZE_BYTES_B,
        )
        self.assertEqual(manifest["model"]["name"], preflight.MODEL_NAME)
        self.assertEqual(manifest["model"]["sha256"], preflight.MODEL_SHA256)

    def test_plan_reports_exact_compressed_total_without_network_access(self):
        manifest = prepare.load_manifest()
        with tempfile.TemporaryDirectory() as temp:
            plan = prepare.build_plan(manifest, Path(temp), "all")
        self.assertEqual(2842984585, plan["compressedBytesTotal"])
        self.assertIn("!= actual runtime A/B inference PASS", plan["stopLine"])

    def test_verify_archive_accepts_exact_size_and_digest(self):
        data = b"fixed-runtime"
        with tempfile.TemporaryDirectory() as temp:
            archive = Path(temp) / "runtime.tar.zst"
            archive.write_bytes(data)
            verification = prepare.verify_archive(
                archive, len(data), hashlib.sha256(data).hexdigest()
            )
        self.assertEqual(len(data), verification.size_bytes)

    def test_verify_archive_rejects_size_before_digest(self):
        data = b"wrong-size"
        with tempfile.TemporaryDirectory() as temp:
            archive = Path(temp) / "runtime.tar.zst"
            archive.write_bytes(data)
            with self.assertRaisesRegex(ValueError, "archive size"):
                prepare.verify_archive(archive, len(data) + 1, "0" * 64)

    def test_existing_valid_archive_is_reused_without_opening_network(self):
        data = b"already-present"
        opened = []

        def opener(_url):
            opened.append(True)
            raise AssertionError("network opener should not be called")

        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "runtime.tar.zst"
            target.write_bytes(data)
            verification = prepare.download_archive(
                "https://example.invalid/runtime",
                target,
                len(data),
                hashlib.sha256(data).hexdigest(),
                opener=opener,
            )
        self.assertEqual([], opened)
        self.assertEqual(len(data), verification.size_bytes)

    def test_download_uses_partial_file_then_atomically_promotes_verified_bytes(self):
        data = b"downloaded-runtime"
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "runtime.tar.zst"
            verification = prepare.download_archive(
                "https://example.invalid/runtime",
                target,
                len(data),
                hashlib.sha256(data).hexdigest(),
                opener=lambda _url: FakeResponse(data),
            )
            self.assertTrue(target.is_file())
            self.assertFalse(target.with_name(target.name + ".part").exists())
            self.assertEqual(data, target.read_bytes())
        self.assertEqual(len(data), verification.size_bytes)

    def test_existing_partial_file_is_not_silently_reused_or_overwritten(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "runtime.tar.zst"
            partial = target.with_name(target.name + ".part")
            partial.write_bytes(b"partial")
            with self.assertRaisesRegex(ValueError, "途中download"):
                prepare.download_archive(
                    "https://example.invalid/runtime",
                    target,
                    1,
                    hashlib.sha256(b"x").hexdigest(),
                    opener=lambda _url: FakeResponse(b"x"),
                )
            self.assertEqual(b"partial", partial.read_bytes())
            self.assertFalse(target.exists())

    def test_failed_download_preserves_partial_for_diagnosis_but_not_final_target(self):
        data = b"wrong"
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "runtime.tar.zst"
            with self.assertRaisesRegex(ValueError, "downloadしたarchive size"):
                prepare.download_archive(
                    "https://example.invalid/runtime",
                    target,
                    len(data) + 10,
                    hashlib.sha256(data).hexdigest(),
                    opener=lambda _url: FakeResponse(data),
                )
            self.assertFalse(target.exists())
            self.assertEqual(
                data, target.with_name(target.name + ".part").read_bytes()
            )

    def test_manifest_urls_are_exact_versioned_official_release_assets(self):
        manifest = prepare.load_manifest()
        for label, archive in manifest["runtimeArchives"].items():
            with self.subTest(runtime=label):
                expected = (
                    "https://github.com/ollama/ollama/releases/download/"
                    f"v{archive['version']}/{archive['assetName']}"
                )
                self.assertEqual(expected, archive["downloadUrl"])


if __name__ == "__main__":
    unittest.main()
