import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import capture_tei_revision_b_git_data_snapshot as capture
import prepare_tei_revision_b_source as prepare
import prepare_tei_revision_b_source_from_snapshot as snapshot_prepare


class RevisionBSnapshotCaptureTest(unittest.TestCase):
    def commit_response(self):
        return {
            "sha": prepare.REVISION_B,
            "tree": {"sha": prepare.REVISION_B_ROOT_TREE},
            "verification": {
                "verified": True,
                "payload": "synthetic",
                "signature": "synthetic",
            },
        }

    def test_recording_requester_records_response_without_token(self):
        observed_tokens = []

        def request_json(url: str, token: str):
            observed_tokens.append(token)
            return self.commit_response()

        recorder = capture.RecordingRequester(request_json)
        response = recorder(
            prepare._api(f"git/commits/{prepare.REVISION_B}"),
            "secret-token",
        )
        self.assertEqual(prepare.REVISION_B, response["sha"])
        self.assertEqual(["secret-token"], observed_tokens)
        rendered = json.dumps(recorder.responses, ensure_ascii=False)
        self.assertNotIn("secret-token", rendered)

    def test_same_path_response_drift_is_rejected(self):
        calls = 0

        def request_json(url: str, token: str):
            nonlocal calls
            calls += 1
            response = self.commit_response()
            if calls == 2:
                response["tree"] = {"sha": "0" * 40}
            return response

        recorder = capture.RecordingRequester(request_json)
        url = prepare._api(f"git/commits/{prepare.REVISION_B}")
        recorder(url, "secret-token")
        with self.assertRaisesRegex(ValueError, "異なるresponse"):
            recorder(url, "secret-token")

    def test_capture_writes_snapshot_consumable_by_offline_loader(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "tei-b"
            snapshot = root / "tei-b-git-data.json"
            response = self.commit_response()

            def request_json(url: str, token: str):
                self.assertEqual("secret-token", token)
                return response

            def fake_materialize(output_dir, **kwargs):
                requester = kwargs["request_json"]
                actual = requester(
                    prepare._api(f"git/commits/{prepare.REVISION_B}"),
                    kwargs["token"],
                )
                self.assertEqual(prepare.REVISION_B, actual["sha"])
                Path(output_dir).mkdir()
                return {
                    "schema": "soza.tei-revision-b-source-acquisition/v1",
                    "result": "verified",
                    "sourceAcquisition": snapshot_prepare.CANONICAL_SOURCE_ACQUISITION,
                    "credentialSource": snapshot_prepare.CANONICAL_CREDENTIAL_SOURCE,
                    "sourceCommit": prepare.REVISION_B,
                    "rootTree": prepare.REVISION_B_ROOT_TREE,
                    "outputDirectory": str(output_dir),
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
                result = capture.capture_revision_b_source_and_snapshot(
                    source,
                    snapshot,
                    token="secret-token",
                    request_json=request_json,
                )

            self.assertTrue(source.is_dir())
            self.assertTrue(snapshot.is_file())
            loaded, sha256 = snapshot_prepare._load_snapshot(snapshot)
            self.assertEqual(snapshot_prepare.SNAPSHOT_SCHEMA, loaded["schema"])
            self.assertEqual(prepare.REVISION_B, loaded["sourceCommit"])
            self.assertEqual(prepare.REVISION_B_ROOT_TREE, loaded["rootTree"])
            self.assertEqual(
                snapshot_prepare.CANONICAL_SOURCE_ACQUISITION,
                loaded["sourceAcquisition"],
            )
            self.assertEqual(
                snapshot_prepare.CANONICAL_CREDENTIAL_SOURCE,
                loaded["credentialSource"],
            )
            self.assertEqual(
                prepare.REVISION_B,
                loaded["responses"][f"git/commits/{prepare.REVISION_B}"]["sha"],
            )
            self.assertEqual(sha256, result["transportSnapshotExport"]["sha256"])
            self.assertEqual(1, result["transportSnapshotExport"]["responses"])
            self.assertFalse(
                result["transportSnapshotExport"]["containsRuntimeCredential"]
            )
            self.assertTrue(
                result["transportSnapshotExport"][
                    "preservesSourceAcquisitionProvenance"
                ]
            )
            rendered_snapshot = snapshot.read_text(encoding="utf-8")
            self.assertNotIn("secret-token", rendered_snapshot)
            self.assertIn(
                snapshot_prepare.CANONICAL_SOURCE_ACQUISITION,
                rendered_snapshot,
            )

    def test_materializer_provenance_drift_prevents_snapshot_publish(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "tei-b"
            snapshot = root / "snapshot.json"

            def fake_materialize(output_dir, **kwargs):
                Path(output_dir).mkdir()
                return {
                    "sourceAcquisition": "other-acquisition",
                    "credentialSource": snapshot_prepare.CANONICAL_CREDENTIAL_SOURCE,
                }

            with mock.patch.object(
                prepare,
                "materialize_revision_b_source",
                side_effect=fake_materialize,
            ):
                with self.assertRaisesRegex(ValueError, "acquisition provenance"):
                    capture.capture_revision_b_source_and_snapshot(
                        source,
                        snapshot,
                        token="secret-token",
                        request_json=lambda url, token: self.commit_response(),
                    )
            self.assertFalse(snapshot.exists())

    def test_snapshot_output_collision_is_rejected_before_acquisition(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "tei-b"
            snapshot = root / "snapshot.json"
            snapshot.write_text("keep", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "新規path"):
                capture.capture_revision_b_source_and_snapshot(
                    source,
                    snapshot,
                    token="secret-token",
                    request_json=lambda url, token: self.commit_response(),
                )
            self.assertFalse(source.exists())
            self.assertEqual("keep", snapshot.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
