import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import run_tei_version_exchange_evidence as subject


class TEIVersionExchangeReferenceBundleTest(unittest.TestCase):
    def make_go(self, root: Path, name: str, version: str) -> Path:
        path = root / name / "bin/go"
        path.parent.mkdir(parents=True)
        path.write_text(
            "#!/bin/sh\n"
            "if [ \"${1:-}\" = version ]; then\n"
            f"  echo 'go version {version} linux/amd64'\n"
            "fi\n"
            "exit 0\n",
            encoding="utf-8",
        )
        path.chmod(0o755)
        return path

    def make_inputs(self, root: Path):
        source = root / "tei-b"
        sei = root / "sei"
        source.mkdir()
        sei.mkdir()
        go_root = sei / "runtime/go"
        go_root.mkdir(parents=True)
        (go_root / "go.mod").write_text(
            "module example.invalid/sei-test\n\ngo 1.25\n",
            encoding="utf-8",
        )
        reference_bundle = root / "revision-a.tar.gz"
        reference_bundle.write_bytes(b"historical-bundle")
        return source, sei, reference_bundle

    @mock.patch.object(subject.adapter_runner, "run_compatibility")
    @mock.patch.object(subject.build_runner, "produce_bundle")
    def test_historical_bundle_acquisition_is_forwarded_to_e2_and_reported(
        self, build, adapter
    ):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, sei, reference_bundle = self.make_inputs(root)
            tei_go = self.make_go(root, "go123", "go1.23.2")
            sei_go = self.make_go(root, "go125", "go1.25.0")
            output = root / "evidence"
            observed = {}

            def build_side_effect(source_repo, reference_repo, archive, **kwargs):
                observed["e2_go"] = Path(shutil.which("go")).resolve()
                observed["source_repo"] = source_repo
                observed["reference_repo"] = reference_repo
                observed["reference_bundle"] = kwargs.get("reference_evidence_bundle")
                archive.write_bytes(b"bundle")
                return {
                    "result": "bundle_produced",
                    "referenceInput": {
                        "acquisitionMode": "historical_evidence_bundle"
                    },
                }

            def adapter_side_effect(archive, **kwargs):
                observed["e3_go"] = Path(shutil.which("go")).resolve()
                return {
                    "result": "adapter_compatible",
                    "seiGoRequirement": "1.25",
                    "seiGoVersion": "go version go1.25.0 linux/amd64",
                }

            build.side_effect = build_side_effect
            adapter.side_effect = adapter_side_effect
            original_path = os.environ.get("PATH")
            result = subject.run_version_exchange(
                source,
                None,
                sei,
                output,
                reference_evidence_bundle=reference_bundle,
                tei_go_executable=tei_go,
                sei_go_executable=sei_go,
                expected_sei_head="f" * 40,
            )

            self.assertEqual(tei_go.resolve(), observed["e2_go"])
            self.assertEqual(sei_go.resolve(), observed["e3_go"])
            self.assertEqual(original_path, os.environ.get("PATH"))
            self.assertEqual(source.resolve(), observed["source_repo"])
            self.assertIsNone(observed["reference_repo"])
            self.assertEqual(reference_bundle.resolve(), observed["reference_bundle"])
            self.assertEqual(
                "historical_evidence_bundle",
                result["comparisonAxis"]["referenceInputAcquisition"],
            )
            self.assertEqual(
                str(reference_bundle.resolve()),
                result["comparisonAxis"]["referenceInputBundle"],
            )
            self.assertEqual("fixed_scope_e2_e3_verified", result["result"])

    @mock.patch.object(subject.adapter_runner, "run_compatibility")
    @mock.patch.object(subject.build_runner, "produce_bundle")
    def test_output_directory_cannot_contain_reference_bundle(self, build, adapter):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = root / "evidence"
            output.mkdir()
            source = root / "tei-b"
            sei = root / "sei"
            source.mkdir()
            sei.mkdir()
            reference_bundle = output / "revision-a.tar.gz"
            reference_bundle.write_bytes(b"historical-bundle")
            tei_go = self.make_go(root, "go123", "go1.23.2")
            sei_go = self.make_go(root, "go125", "go1.25.0")

            with self.assertRaisesRegex(ValueError, "reference bundle"):
                subject.run_version_exchange(
                    source,
                    None,
                    sei,
                    output,
                    reference_evidence_bundle=reference_bundle,
                    tei_go_executable=tei_go,
                    sei_go_executable=sei_go,
                )
            build.assert_not_called()
            adapter.assert_not_called()

    def test_reference_checkout_and_bundle_are_mutually_exclusive(self):
        parser = subject.build_parser()
        common = [
            "--source-repo", "/b",
            "--sei-repo-root", "/sei",
            "--output-dir", "/out",
            "--tei-go-executable", "/go123/bin/go",
            "--sei-go-executable", "/go125/bin/go",
        ]
        with self.assertRaises(SystemExit):
            parser.parse_args(
                common
                + [
                    "--reference-source-repo", "/a",
                    "--reference-evidence-bundle", "/a.tar.gz",
                ]
            )
        with self.assertRaises(SystemExit):
            parser.parse_args(common)


if __name__ == "__main__":
    unittest.main()
