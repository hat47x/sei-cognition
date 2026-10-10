import json
import tempfile
import unittest
from pathlib import Path

import check_runtime_version_exchange_manifest_consistency as consistency
import prepare_runtime_version_exchange_model_store as model_store


class RuntimeVersionExchangeManifestConsistencyTest(unittest.TestCase):
    def write_manifest(self, root: Path, mutate) -> Path:
        payload = json.loads(consistency.ARTIFACT_MANIFEST.read_text(encoding="utf-8"))
        mutate(payload)
        path = root / "manifest.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def write_release_snapshot(self, root: Path, mutate) -> Path:
        payload = json.loads(
            consistency.OFFICIAL_RELEASE_SNAPSHOT.read_text(encoding="utf-8")
        )
        mutate(payload)
        path = root / "official-release-snapshot.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def test_current_manifest_is_consistent(self):
        result = consistency.report()
        self.assertEqual("consistent", result["result"])
        self.assertEqual([], result["blockers"])
        self.assertIn("official release metadata snapshot agreement", result["stopLine"])
        self.assertIn("!= actual runtime A/B inference PASS", result["stopLine"])

    def test_official_release_snapshot_records_mutability_without_claiming_immutability(self):
        snapshot = json.loads(
            consistency.OFFICIAL_RELEASE_SNAPSHOT.read_text(encoding="utf-8")
        )
        self.assertFalse(snapshot["archives"]["a"]["releaseImmutable"])
        self.assertFalse(snapshot["archives"]["b"]["releaseImmutable"])
        self.assertIn("将来の公式metadata不変性を証明するものではない", snapshot["note"])

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
        self.assertIn("release-snapshot.a.digest", result["blockers"])

    def test_official_release_snapshot_digest_drift_is_blocked(self):
        with tempfile.TemporaryDirectory() as temporary:
            snapshot = self.write_release_snapshot(
                Path(temporary),
                lambda payload: payload["archives"]["b"].__setitem__(
                    "digest", "sha256:" + "0" * 64
                ),
            )
            result = consistency.report(
                consistency.ARTIFACT_MANIFEST,
                snapshot,
            )
        self.assertEqual("blocked", result["result"])
        self.assertIn("release-snapshot.b.digest", result["blockers"])

    def test_official_release_snapshot_source_repository_drift_is_blocked(self):
        with tempfile.TemporaryDirectory() as temporary:
            snapshot = self.write_release_snapshot(
                Path(temporary),
                lambda payload: payload.__setitem__("sourceRepository", "example/ollama"),
            )
            result = consistency.report(
                consistency.ARTIFACT_MANIFEST,
                snapshot,
            )
        self.assertEqual("blocked", result["result"])
        self.assertEqual(["release-snapshot.schema"], result["blockers"])

    def test_official_release_snapshot_asset_state_drift_is_blocked(self):
        with tempfile.TemporaryDirectory() as temporary:
            snapshot = self.write_release_snapshot(
                Path(temporary),
                lambda payload: payload["archives"]["a"].__setitem__(
                    "assetState", "deleted"
                ),
            )
            result = consistency.report(
                consistency.ARTIFACT_MANIFEST,
                snapshot,
            )
        self.assertEqual("blocked", result["result"])
        self.assertIn("release-snapshot.a.assetState", result["blockers"])

    def test_model_name_drift_is_blocked(self):
        def mutate(payload):
            # Keep the derived acquisition locations consistent with the new name so
            # that the acquisition boundary passes and the consumer comparison
            # (model.name vs the preflight MODEL_NAME) is what blocks the drift.
            name = "other:latest"
            store_path, manifest_url, blob_base_url = (
                model_store._expected_model_acquisition_locations(name)
            )
            payload["model"].update(
                name=name,
                storeManifestPath=store_path,
                registryManifestUrl=manifest_url,
                registryBlobBaseUrl=blob_base_url,
            )

        with tempfile.TemporaryDirectory() as temporary:
            path = self.write_manifest(Path(temporary), mutate)
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
