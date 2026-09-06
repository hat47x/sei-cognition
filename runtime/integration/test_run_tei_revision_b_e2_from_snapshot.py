import tempfile
import unittest
from contextlib import nullcontext
from pathlib import Path
from unittest import mock

import run_tei_revision_b_e2_from_snapshot as subject


class TEIRevisionBE2FromSnapshotTest(unittest.TestCase):
    def setUp(self):
        self.reference_input_patch = mock.patch.object(
            subject.github_preflight,
            "_check_reference_input",
            return_value={
                "mode": "historical_evidence_bundle",
                "sourceCommit": subject.github_e2.e2_runner.source_identity.REVISION_A,
            },
        )
        self.reference_input_patch.start()
        self.addCleanup(self.reference_input_patch.stop)

    def _fixture(self, root: Path):
        evidence = root / "evidence"
        go = root / "go123" / "go"
        snapshot = root / "tei-b-git-data.json"
        snapshot.write_text("{}", encoding="utf-8")
        reference = root / "a.tar.gz"
        reference.write_bytes(b"placeholder")
        acquisition = {
            "result": "verified",
            "sourceTransport": {
                "mode": subject.snapshot_source.SNAPSHOT_TRANSPORT_MODE,
                "schema": subject.snapshot_source.SNAPSHOT_SCHEMA,
                "sha256": "a" * 64,
                "responsesAvailable": 4,
                "responsesConsumed": 4,
                "allConsumedResponsesUnique": True,
                "runtimeCredentialUsed": False,
            },
        }
        base_provenance = {
            "mode": subject.snapshot_source.CANONICAL_SOURCE_ACQUISITION,
            "repository": "hat47x/tei-platform",
            "sourceCommit": subject.github_e2.e2_runner.source_identity.REVISION_B,
            "rootTree": subject.snapshot_source.prepare.REVISION_B_ROOT_TREE,
            "credentialSource": subject.snapshot_source.CANONICAL_CREDENTIAL_SOURCE,
        }
        return evidence, go, snapshot, reference, acquisition, base_provenance

    def test_success_preserves_existing_partial_schema_and_snapshot_transport(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            evidence, go, snapshot, reference, acquisition, base_provenance = self._fixture(root)

            with mock.patch.object(
                subject.github_e2,
                "_prepare_output_dir_before_source",
                return_value=evidence,
            ), mock.patch.object(
                subject.github_e2,
                "_precheck_partial_output_paths",
            ), mock.patch.object(
                subject.github_e2,
                "_verify_e2_prerequisites_before_source",
                return_value={"executable": str(go)},
            ), mock.patch.object(
                subject.github_runner,
                "_prepare_source_temp_parent",
                return_value=root,
            ), mock.patch.object(
                subject.snapshot_source,
                "materialize_revision_b_source_from_snapshot",
                return_value=acquisition,
            ) as materialize, mock.patch.object(
                subject.github_runner,
                "_source_provenance",
                return_value=base_provenance,
            ), mock.patch.object(
                subject.version_exchange,
                "_prepare_output_dir",
                return_value=evidence,
            ), mock.patch.object(
                subject.version_exchange,
                "_prepare_output_paths",
            ), mock.patch.object(
                subject.version_exchange,
                "_go_on_path",
                return_value=nullcontext(go),
            ), mock.patch.object(
                subject.github_e2.e2_runner,
                "produce_bundle",
                return_value={"result": "bundle_produced"},
            ) as produce, mock.patch.object(
                subject.github_runner,
                "_write_report",
            ) as write_report:
                result = subject.run_e2_from_snapshot(
                    snapshot,
                    None,
                    evidence,
                    reference_evidence_bundle=reference,
                    tei_go_executable=go,
                )

            materialize.assert_called_once()
            produce.assert_called_once()
            self.assertEqual(subject.github_e2.SCHEMA, result["schema"])
            self.assertEqual("e2_bundle_verified_e3_not_run", result["result"])
            self.assertIsNone(result["e3"])
            self.assertEqual(
                subject.snapshot_source.SNAPSHOT_TRANSPORT_MODE,
                result["sourceAcquisition"]["sourceTransport"]["mode"],
            )
            self.assertFalse(
                result["sourceAcquisition"]["sourceTransport"][
                    "runtimeCredentialUsed"
                ]
            )
            self.assertEqual(
                subject.snapshot_source.CANONICAL_SOURCE_ACQUISITION,
                result["sourceAcquisition"]["mode"],
            )
            written = write_report.call_args.args[1]
            self.assertEqual(subject.github_e2.SCHEMA, written["schema"])

    def test_wrong_go_stops_before_snapshot_materialization(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            evidence, go, snapshot, reference, _acquisition, _base = self._fixture(root)

            with mock.patch.object(
                subject.github_e2,
                "_prepare_output_dir_before_source",
                return_value=evidence,
            ), mock.patch.object(
                subject.github_e2,
                "_precheck_partial_output_paths",
            ), mock.patch.object(
                subject.github_e2,
                "_verify_e2_prerequisites_before_source",
                side_effect=ValueError("wrong Go"),
            ), mock.patch.object(
                subject.snapshot_source,
                "materialize_revision_b_source_from_snapshot",
            ) as materialize:
                with self.assertRaisesRegex(ValueError, "wrong Go"):
                    subject.run_e2_from_snapshot(
                        snapshot,
                        None,
                        evidence,
                        reference_evidence_bundle=reference,
                        tei_go_executable=go,
                    )

            materialize.assert_not_called()
            self.assertFalse(evidence.exists())

    def test_snapshot_cannot_be_inside_evidence_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            evidence = root / "evidence"
            evidence.mkdir()
            snapshot = evidence / "snapshot.json"
            snapshot.write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "包含"):
                subject._prepare_snapshot_input(snapshot, evidence)

    def test_source_transport_requires_no_runtime_credential(self):
        acquisition = {
            "sourceTransport": {
                "mode": subject.snapshot_source.SNAPSHOT_TRANSPORT_MODE,
                "runtimeCredentialUsed": True,
            }
        }
        with mock.patch.object(
            subject.github_runner,
            "_source_provenance",
            return_value={"mode": subject.snapshot_source.CANONICAL_SOURCE_ACQUISITION},
        ):
            with self.assertRaisesRegex(ValueError, "credential未使用"):
                subject._source_provenance(acquisition)

    def test_e2_failure_report_keeps_snapshot_transport(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            evidence, go, snapshot, reference, acquisition, base_provenance = self._fixture(root)
            failure = subject.github_e2.e2_runner.TEIEvidenceStageError(
                "deployment_provider_plan_execution",
                "provider failed",
                command=["tei", "deployment-provider-plan"],
                returncode=2,
                stderr="failure",
            )

            with mock.patch.object(
                subject.github_e2,
                "_prepare_output_dir_before_source",
                return_value=evidence,
            ), mock.patch.object(
                subject.github_e2,
                "_precheck_partial_output_paths",
            ), mock.patch.object(
                subject.github_e2,
                "_verify_e2_prerequisites_before_source",
                return_value={"executable": str(go)},
            ), mock.patch.object(
                subject.github_runner,
                "_prepare_source_temp_parent",
                return_value=root,
            ), mock.patch.object(
                subject.snapshot_source,
                "materialize_revision_b_source_from_snapshot",
                return_value=acquisition,
            ), mock.patch.object(
                subject.github_runner,
                "_source_provenance",
                return_value=base_provenance,
            ), mock.patch.object(
                subject.version_exchange,
                "_prepare_output_dir",
                return_value=evidence,
            ), mock.patch.object(
                subject.version_exchange,
                "_prepare_output_paths",
            ), mock.patch.object(
                subject.version_exchange,
                "_go_on_path",
                return_value=nullcontext(go),
            ), mock.patch.object(
                subject.github_e2.e2_runner,
                "produce_bundle",
                side_effect=failure,
            ), mock.patch.object(
                subject.github_runner,
                "_write_report",
            ) as write_report:
                with self.assertRaises(subject.SnapshotE2RunFailed):
                    subject.run_e2_from_snapshot(
                        snapshot,
                        None,
                        evidence,
                        reference_evidence_bundle=reference,
                        tei_go_executable=go,
                    )

            report = write_report.call_args.args[1]
            self.assertEqual("e2_failed", report["result"])
            self.assertEqual(
                subject.snapshot_source.SNAPSHOT_TRANSPORT_MODE,
                report["sourceAcquisition"]["sourceTransport"]["mode"],
            )
            self.assertEqual("E2", report["failure"]["stage"])
            self.assertEqual(
                "deployment_provider_plan_execution",
                report["failure"]["substage"],
            )


if __name__ == "__main__":
    unittest.main()
