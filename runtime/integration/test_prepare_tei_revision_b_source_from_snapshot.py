import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import prepare_tei_revision_b_source as prepare
import prepare_tei_revision_b_source_from_snapshot as snapshot_prepare


class RevisionBSnapshotTransportTest(unittest.TestCase):
    def snapshot_payload(self):
        return {
            "schema": snapshot_prepare.SNAPSHOT_SCHEMA,
            "repository": prepare.GITHUB_REPOSITORY,
            "sourceCommit": prepare.REVISION_B,
            "rootTree": prepare.REVISION_B_ROOT_TREE,
            "sourceAcquisition": snapshot_prepare.CANONICAL_SOURCE_ACQUISITION,
            "credentialSource": snapshot_prepare.CANONICAL_CREDENTIAL_SOURCE,
            "responses": {
                f"git/commits/{prepare.REVISION_B}": {
                    "sha": prepare.REVISION_B,
                    "tree": {"sha": prepare.REVISION_B_ROOT_TREE},
                }
            },
        }

    def write_snapshot(self, root: Path, payload=None) -> Path:
        path = root / "snapshot.json"
        path.write_text(
            json.dumps(payload or self.snapshot_payload(), ensure_ascii=False),
            encoding="utf-8",
        )
        return path

    def test_valid_snapshot_is_loaded_with_sha256(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = self.write_snapshot(root)
            snapshot, sha256 = snapshot_prepare._load_snapshot(path)
            self.assertEqual(snapshot_prepare.SNAPSHOT_SCHEMA, snapshot["schema"])
            self.assertEqual(64, len(sha256))
            self.assertEqual(
                snapshot_prepare.CANONICAL_SOURCE_ACQUISITION,
                snapshot["sourceAcquisition"],
            )
            self.assertEqual(
                prepare.REVISION_B,
                snapshot["responses"][f"git/commits/{prepare.REVISION_B}"]["sha"],
            )

    def test_snapshot_transport_reuses_existing_content_addressed_materializer(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = self.write_snapshot(root)
            output = root / "tei-b"
            observed = {}

            def fake_materialize(output_dir, **kwargs):
                observed.update(kwargs)
                requester = kwargs["request_json"]
                payload = requester(
                    prepare._api(f"git/commits/{prepare.REVISION_B}"),
                    kwargs["token"],
                )
                self.assertEqual(prepare.REVISION_B, payload["sha"])
                return {
                    "schema": "soza.tei-revision-b-source-acquisition/v1",
                    "result": "verified",
                    "sourceAcquisition": snapshot_prepare.CANONICAL_SOURCE_ACQUISITION,
                    "credentialSource": snapshot_prepare.CANONICAL_CREDENTIAL_SOURCE,
                    "sourceCommit": prepare.REVISION_B,
                    "rootTree": prepare.REVISION_B_ROOT_TREE,
                    "outputDirectory": str(output_dir),
                    "objectAcquisition": {"apiRequests": 1},
                    "revisionBBuildPass": False,
                    "providerPlanExecutionPass": False,
                    "sozaAdapterCompatibilityPass": False,
                    "issue000072Resolved": False,
                    "qualityJudgement": "not_evaluated",
                    "stopLine": prepare.STOP_LINE,
                }

            with mock.patch.object(
                prepare,
                "materialize_revision_b_source",
                side_effect=fake_materialize,
            ):
                result = snapshot_prepare.materialize_revision_b_source_from_snapshot(
                    output,
                    snapshot_path=path,
                )

            self.assertEqual(
                snapshot_prepare.SNAPSHOT_TRANSPORT_TOKEN,
                observed["token"],
            )
            self.assertEqual(prepare.REVISION_B, observed["expected_commit"])
            self.assertEqual(
                prepare.REVISION_B_ROOT_TREE,
                observed["expected_root_tree"],
            )
            self.assertEqual(
                snapshot_prepare.CANONICAL_SOURCE_ACQUISITION,
                result["sourceAcquisition"],
            )
            self.assertEqual(
                snapshot_prepare.CANONICAL_CREDENTIAL_SOURCE,
                result["credentialSource"],
            )
            self.assertEqual(
                snapshot_prepare.SNAPSHOT_TRANSPORT_MODE,
                result["sourceTransport"]["mode"],
            )
            self.assertEqual(1, result["sourceTransport"]["responsesAvailable"])
            self.assertEqual(1, result["sourceTransport"]["responsesConsumed"])
            self.assertTrue(result["sourceTransport"]["allConsumedResponsesUnique"])
            self.assertFalse(result["sourceTransport"]["runtimeCredentialUsed"])
            rendered = json.dumps(result, ensure_ascii=False)
            self.assertNotIn("GITHUB_TOKEN", rendered)
            self.assertNotIn("GH_TOKEN", rendered)

    def test_snapshot_requester_rejects_runtime_credential(self):
        payload = self.snapshot_payload()
        requester = snapshot_prepare.SnapshotRequester(payload["responses"])
        with self.assertRaisesRegex(ValueError, "runtime credential"):
            requester(
                prepare._api(f"git/commits/{prepare.REVISION_B}"),
                "real-secret-token",
            )

    def test_missing_required_response_is_rejected_at_request_boundary(self):
        requester = snapshot_prepare.SnapshotRequester({})
        with self.assertRaisesRegex(ValueError, "responseがありません"):
            requester(
                prepare._api(f"git/commits/{prepare.REVISION_B}"),
                snapshot_prepare.SNAPSHOT_TRANSPORT_TOKEN,
            )

    def test_wrong_repository_is_rejected_before_materialization(self):
        payload = self.snapshot_payload()
        payload["repository"] = "other/repository"
        with tempfile.TemporaryDirectory() as temporary:
            path = self.write_snapshot(Path(temporary), payload)
            with self.assertRaisesRegex(ValueError, "repository"):
                snapshot_prepare._load_snapshot(path)

    def test_wrong_fixed_commit_is_rejected_before_materialization(self):
        payload = self.snapshot_payload()
        payload["sourceCommit"] = "0" * 40
        with tempfile.TemporaryDirectory() as temporary:
            path = self.write_snapshot(Path(temporary), payload)
            with self.assertRaisesRegex(ValueError, "sourceCommit"):
                snapshot_prepare._load_snapshot(path)

    def test_wrong_acquisition_provenance_is_rejected(self):
        payload = self.snapshot_payload()
        payload["sourceAcquisition"] = "other-acquisition"
        with tempfile.TemporaryDirectory() as temporary:
            path = self.write_snapshot(Path(temporary), payload)
            with self.assertRaisesRegex(ValueError, "acquisition provenance"):
                snapshot_prepare._load_snapshot(path)

    def test_wrong_credential_provenance_is_rejected(self):
        payload = self.snapshot_payload()
        payload["credentialSource"] = "snapshot"
        with tempfile.TemporaryDirectory() as temporary:
            path = self.write_snapshot(Path(temporary), payload)
            with self.assertRaisesRegex(ValueError, "credential provenance"):
                snapshot_prepare._load_snapshot(path)

    def test_response_path_and_payload_sha_must_match(self):
        payload = self.snapshot_payload()
        key = f"git/commits/{prepare.REVISION_B}"
        payload["responses"][key]["sha"] = "0" * 40
        with tempfile.TemporaryDirectory() as temporary:
            path = self.write_snapshot(Path(temporary), payload)
            with self.assertRaisesRegex(ValueError, "response SHA"):
                snapshot_prepare._load_snapshot(path)

    def test_unexpected_top_level_field_is_rejected(self):
        payload = self.snapshot_payload()
        payload["token"] = "must-not-be-accepted"
        with tempfile.TemporaryDirectory() as temporary:
            path = self.write_snapshot(Path(temporary), payload)
            with self.assertRaisesRegex(ValueError, "top-level field"):
                snapshot_prepare._load_snapshot(path)

    def test_snapshot_and_output_path_must_not_overlap(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = self.write_snapshot(root)
            output = path / "tei-b"
            with self.assertRaisesRegex(ValueError, "分離"):
                snapshot_prepare.materialize_revision_b_source_from_snapshot(
                    output,
                    snapshot_path=path,
                )


if __name__ == "__main__":
    unittest.main()
