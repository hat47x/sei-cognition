import json
import tempfile
import unittest
from pathlib import Path

import check_runtime_version_exchange_manifest_consistency as consistency


class RuntimeVersionExchangeManifestConsistencyTest(unittest.TestCase):
    def write_manifest(self, root: Path, mutate) -> Path:
        payload = json.loads(consistency.ARTIFACT_MANIFEST.read_text(encoding="utf-8"))
        mutate(payload)
        path = root / "manifest.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def test_current_manifest_is_consistent(self):
        result = consistency.report()
        self.assertEqual("consistent", result["result"])
        self.assertEqual([], result["blockers"])
        self.assertIn("!= actual runtime A/B inference PASS", result["stopLine"])

    def test_source_commit_drift_is_blocked(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = self.write_manifest(
                Path(temporary),
                lambda payload: payload["methodSource"].__setitem__("commit", "0" * 40),
            )
            result = consistency.report(path)
        self.assertEqual("blocked", result["result"])
        self.assertIn("method-source.commit", result["blockers"])

    def test_runtime_digest_drift_is_blocked_even_when_digest_format_is_valid(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = self.write_manifest(
                Path(temporary),
                lambda payload: payload["runtimeArchives"]["a"].__setitem__(
                    "sha256", "0" * 64
                ),
            )
            result = consistency.report(path)
        self.assertEqual("blocked", result["result"])
        self.assertIn("runtime-a.sha256", result["blockers"])

    def test_model_name_drift_is_blocked(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = self.write_manifest(
                Path(temporary),
                lambda payload: payload["model"].__setitem__("name", "other:latest"),
            )
            result = consistency.report(path)
        self.assertEqual("blocked", result["result"])
        self.assertIn("model.name", result["blockers"])

    def test_invalid_model_acquisition_boundary_is_blocked(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = self.write_manifest(
                Path(temporary),
                lambda payload: payload["model"].__setitem__(
                    "registryManifestUrl", "https://example.invalid/model"
                ),
            )
            result = consistency.report(path)
        self.assertEqual("blocked", result["result"])
        self.assertIn("model.acquisition", result["blockers"])

    def test_invalid_runtime_archive_schema_stops_before_consumer_comparison(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = self.write_manifest(
                Path(temporary),
                lambda payload: payload["runtimeArchives"]["a"].__setitem__(
                    "platform", {"os": "darwin", "arch": "arm64"}
                ),
            )
            result = consistency.report(path)
        self.assertEqual("blocked", result["result"])
        self.assertEqual(["manifest.runtime-archive-schema"], result["blockers"])


if __name__ == "__main__":
    unittest.main()
