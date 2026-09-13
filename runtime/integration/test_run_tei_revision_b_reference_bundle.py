import json
import subprocess
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import run_tei_revision_b_prepositioned as subject
import verify_tei_execution_source_identity as source_identity


class TEIRevisionBReferenceBundleRunnerTest(unittest.TestCase):
    def make_source(self, root: Path) -> Path:
        source = root / "tei-b"
        source.mkdir()
        return source

    def fake_materialize(self, archive: Path, output_root: Path):
        (output_root / subject.FIXED_WORKSPACE / ".tei").mkdir(parents=True)
        (output_root / subject.FIXED_WORKSPACE / "input.txt").write_text(
            "fixed-a-input\n", encoding="utf-8"
        )
        (output_root / subject.FIXED_PLUGIN_LOCK).write_text("{}\n", encoding="utf-8")
        run = output_root / subject.FIXED_RUN
        run.parent.mkdir(parents=True, exist_ok=True)
        run.write_text("{}\n", encoding="utf-8")
        return {
            "schema": "sei.tei-fixed-reference-input-bundle/v1",
            "result": "verified",
            "acquisitionMode": "historical_evidence_bundle",
            "archive": str(archive),
            "archiveSha256": "a" * 64,
            "sourceCommit": source_identity.REVISION_A,
            "head": source_identity.REVISION_A,
            "executionSourceObjects": dict(source_identity.REVISION_A_REFERENCE_OBJECTS),
            "materializedRoot": str(output_root),
            "qualityJudgement": "not_evaluated",
        }

    def fake_run(self, argv, *, cwd, env):
        if argv == ["go", "version"]:
            return subprocess.CompletedProcess(
                argv, 0, "go version go1.23.2 linux/amd64\n", ""
            )
        if argv == ["go", "env", "GOOS", "GOARCH"]:
            return subprocess.CompletedProcess(argv, 0, "linux\namd64\n", "")
        if argv[:2] == ["go", "build"]:
            output = Path(argv[argv.index("-o") + 1])
            output.write_bytes(b"fake-tei-binary")
            output.chmod(0o755)
            return subprocess.CompletedProcess(argv, 0, "", "")
        if len(argv) > 1 and argv[1] == "deployment-provider-plan":
            self.provider_argv = argv
            return subprocess.CompletedProcess(
                argv,
                0,
                json.dumps({"executors": [{"executorId": "reference"}]}) + "\n",
                "",
            )
        raise AssertionError(argv)

    @mock.patch.object(subject.bundle_verifier, "verify_bundle")
    @mock.patch.object(subject, "_ensure_linux_amd64")
    @mock.patch.object(subject.fixed_reference, "materialize_fixed_reference_input_bundle")
    @mock.patch.object(subject.source_identity, "verify_repository")
    @mock.patch.object(subject, "_run")
    def test_verified_historical_bundle_supplies_exact_a_fixed_input(
        self, run, verify_source, materialize, ensure_platform, verify_bundle
    ):
        run.side_effect = self.fake_run
        verify_source.return_value = {
            "result": "verified",
            "head": source_identity.REVISION_B,
        }
        materialize.side_effect = self.fake_materialize
        verify_bundle.return_value = {
            "result": "verified",
            "observation": {"source_commit": source_identity.REVISION_B},
        }

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = self.make_source(root)
            reference_bundle = root / "revision-a.tar.gz"
            reference_bundle.write_bytes(b"historical-bundle")
            output = root / "revision-b.tar.gz"

            result = subject.produce_bundle(
                source,
                None,
                output,
                reference_evidence_bundle=reference_bundle,
            )
            self.assertTrue(output.is_file())
            with tarfile.open(output, "r:gz") as tar:
                metadata_file = tar.extractfile("metadata.json")
                self.assertIsNotNone(metadata_file)
                metadata = json.load(metadata_file)
                input_file = tar.extractfile("reference/workspace/input.txt")
                self.assertIsNotNone(input_file)
                self.assertEqual(b"fixed-a-input\n", input_file.read())

        self.assertEqual("bundle_produced", result["result"])
        reference = result["referenceInput"]
        self.assertEqual("historical_evidence_bundle", reference["acquisitionMode"])
        self.assertEqual(source_identity.REVISION_A, reference["sourceCommit"])
        self.assertNotIn("materializedRoot", reference)
        self.assertEqual(
            source_identity.REVISION_B,
            result["postExecutionIdentity"]["source"]["head"],
        )
        self.assertIsNone(result["postExecutionIdentity"]["referenceInput"])
        self.assertEqual(
            "historical_evidence_bundle",
            metadata["reference_input_acquisition_mode"],
        )
        self.assertEqual("a" * 64, metadata["reference_input_bundle_archive_sha256"])
        self.assertEqual(
            [
                mock.call(source.resolve(), expected_head=source_identity.REVISION_B),
                mock.call(source.resolve(), expected_head=source_identity.REVISION_B),
            ],
            verify_source.call_args_list,
        )
        self.assertIn("fixed-reference-input", " ".join(self.provider_argv))
        self.assertNotIn(str(source / subject.FIXED_WORKSPACE), self.provider_argv)
        verify_bundle.assert_called_once()
        self.assertEqual(
            source_identity.REVISION_B,
            verify_bundle.call_args.kwargs["expected_source_commit"],
        )

    @mock.patch.object(subject.fixed_reference, "materialize_fixed_reference_input_bundle")
    @mock.patch.object(subject.source_identity, "verify_repository")
    @mock.patch.object(subject, "_run")
    def test_reference_bundle_identity_failure_keeps_existing_stage(
        self, run, verify_source, materialize
    ):
        verify_source.return_value = {
            "result": "verified",
            "head": source_identity.REVISION_B,
        }
        materialize.side_effect = ValueError("fixed reference Git object identity mismatch")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = self.make_source(root)
            reference_bundle = root / "revision-a.tar.gz"
            reference_bundle.write_bytes(b"historical-bundle")
            with self.assertRaises(subject.TEIEvidenceStageError) as raised:
                subject.produce_bundle(
                    source,
                    None,
                    root / "out.tar.gz",
                    reference_evidence_bundle=reference_bundle,
                )
        self.assertEqual("revision_a_fixed_reference_identity", raised.exception.stage)
        run.assert_not_called()

    def test_reference_checkout_and_bundle_are_mutually_exclusive(self):
        parser = subject.build_parser()
        with self.assertRaises(SystemExit):
            parser.parse_args(
                [
                    "--source-repo", "/b",
                    "--reference-source-repo", "/a",
                    "--reference-evidence-bundle", "/a.tar.gz",
                    "--output-archive", "/out.tar.gz",
                ]
            )
        with self.assertRaises(SystemExit):
            parser.parse_args(
                [
                    "--source-repo", "/b",
                    "--output-archive", "/out.tar.gz",
                ]
            )


if __name__ == "__main__":
    unittest.main()
