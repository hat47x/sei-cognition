import hashlib
import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "run_runtime_version_exchange_strict_archive_boundaries",
    HERE / "run_runtime_version_exchange_strict.py",
)
ENTRYPOINT = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(ENTRYPOINT)


class StrictRuntimeArchiveBoundaryTest(unittest.TestCase):
    def test_same_archive_path_cannot_be_used_for_runtime_a_and_b(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bundle = root / "bundle"
            bundle.mkdir()
            archive = root / "runtime.tar.zst"
            archive.write_bytes(b"runtime")

            with patch.object(ENTRYPOINT, "verify_runtime_bundle") as source_verifier, patch.object(
                ENTRYPOINT.subprocess,
                "run",
            ) as runner:
                with self.assertRaisesRegex(ValueError, "同じarchive path"):
                    ENTRYPOINT.run_strict_probe(
                        checkout_dir=None,
                        backend_bundle=bundle,
                        model_dir=None,
                        evidence_dir=root / "evidence",
                        harness_arguments=[
                            "--runtime-a-archive",
                            str(archive),
                            "--runtime-b-archive",
                            str(archive),
                        ],
                    )

            source_verifier.assert_not_called()
            runner.assert_not_called()

    def test_runtime_archive_inside_prepositioned_model_store_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bundle = root / "bundle"
            model = root / "model"
            bundle.mkdir()
            model.mkdir()
            archive = model / "runtime-a.tar.zst"
            archive.write_bytes(b"runtime")

            with patch.object(ENTRYPOINT, "verify_model_store") as model_verifier, patch.object(
                ENTRYPOINT,
                "verify_runtime_bundle",
            ) as source_verifier, patch.object(ENTRYPOINT.subprocess, "run") as runner:
                with self.assertRaisesRegex(ValueError, "runtime archive.*model directory"):
                    ENTRYPOINT.run_strict_probe(
                        checkout_dir=None,
                        backend_bundle=bundle,
                        model_dir=model,
                        evidence_dir=root / "evidence",
                        harness_arguments=["--runtime-a-archive", str(archive)],
                    )

            model_verifier.assert_not_called()
            source_verifier.assert_not_called()
            runner.assert_not_called()

    def test_distinct_external_runtime_archives_remain_accepted_by_path_validation(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bundle = root / "bundle"
            bundle.mkdir()
            archive_a = root / "runtime-a.tar.zst"
            archive_b = root / "runtime-b.tar.zst"
            archive_a.write_bytes(b"runtime-a")
            archive_b.write_bytes(b"runtime-b")

            validated = ENTRYPOINT._validate_runtime_archives(
                [
                    "--runtime-a-archive",
                    str(archive_a),
                    "--runtime-b-archive",
                    str(archive_b),
                ],
                source_input=bundle,
                source_label="KJ Atlas verified runtime bundle",
            )

            self.assertEqual(archive_a.resolve(), validated["--runtime-a-archive"])
            self.assertEqual(archive_b.resolve(), validated["--runtime-b-archive"])

    def test_runtime_archive_identity_uses_fixed_manifest_metadata(self):
        data = b"runtime-a"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive = root / "runtime-a.tar.zst"
            archive.write_bytes(data)
            manifest = {
                "runtimeArchives": {
                    "a": {
                        "sizeBytes": len(data),
                        "sha256": hashlib.sha256(data).hexdigest(),
                    }
                }
            }
            with patch.object(ENTRYPOINT, "load_artifact_manifest", return_value=manifest):
                ENTRYPOINT._verify_runtime_archive_identities(
                    {"--runtime-a-archive": archive.resolve()}
                )

    def test_wrong_runtime_archive_identity_stops_before_source_or_model_verification(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bundle = root / "bundle"
            model = root / "model"
            bundle.mkdir()
            model.mkdir()
            archive = root / "runtime-a.tar.zst"
            archive.write_bytes(b"wrong-runtime")

            with patch.object(ENTRYPOINT, "verify_model_store") as model_verifier, patch.object(
                ENTRYPOINT,
                "verify_runtime_bundle",
            ) as source_verifier, patch.object(ENTRYPOINT.subprocess, "run") as runner:
                with self.assertRaisesRegex(ValueError, "archive size"):
                    ENTRYPOINT.run_strict_probe(
                        checkout_dir=None,
                        backend_bundle=bundle,
                        model_dir=model,
                        evidence_dir=root / "evidence",
                        harness_arguments=["--runtime-a-archive", str(archive)],
                    )

            model_verifier.assert_not_called()
            source_verifier.assert_not_called()
            runner.assert_not_called()

    def test_source_bundle_inside_soza_repository_is_rejected_before_verification(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            soza = root / "soza"
            bundle = soza / "bundle"
            soza.mkdir()
            bundle.mkdir()

            with patch.object(ENTRYPOINT, "SOZA_ROOT", soza), patch.object(
                ENTRYPOINT,
                "verify_runtime_bundle",
            ) as source_verifier, patch.object(ENTRYPOINT.subprocess, "run") as runner:
                with self.assertRaisesRegex(ValueError, "KJ Atlas verified runtime bundle.*SOZA repository"):
                    ENTRYPOINT.run_strict_probe(
                        checkout_dir=None,
                        backend_bundle=bundle,
                        model_dir=None,
                        evidence_dir=root / "evidence",
                        harness_arguments=[],
                    )

            source_verifier.assert_not_called()
            runner.assert_not_called()

    def test_model_store_inside_soza_repository_is_rejected_before_verification(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            soza = root / "soza"
            bundle = root / "bundle"
            model = soza / "models"
            soza.mkdir()
            bundle.mkdir()
            model.mkdir()

            with patch.object(ENTRYPOINT, "SOZA_ROOT", soza), patch.object(
                ENTRYPOINT,
                "verify_model_store",
            ) as model_verifier, patch.object(ENTRYPOINT, "verify_runtime_bundle") as source_verifier, patch.object(
                ENTRYPOINT.subprocess,
                "run",
            ) as runner:
                with self.assertRaisesRegex(ValueError, "model directory.*SOZA repository"):
                    ENTRYPOINT.run_strict_probe(
                        checkout_dir=None,
                        backend_bundle=bundle,
                        model_dir=model,
                        evidence_dir=root / "evidence",
                        harness_arguments=[],
                    )

            model_verifier.assert_not_called()
            source_verifier.assert_not_called()
            runner.assert_not_called()

    def test_evidence_inside_soza_repository_is_rejected_before_verification(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            soza = root / "soza"
            bundle = root / "bundle"
            soza.mkdir()
            bundle.mkdir()

            with patch.object(ENTRYPOINT, "SOZA_ROOT", soza), patch.object(
                ENTRYPOINT,
                "verify_runtime_bundle",
            ) as source_verifier, patch.object(ENTRYPOINT.subprocess, "run") as runner:
                with self.assertRaisesRegex(ValueError, "Evidence directory.*SOZA repository"):
                    ENTRYPOINT.run_strict_probe(
                        checkout_dir=None,
                        backend_bundle=bundle,
                        model_dir=None,
                        evidence_dir=soza / "evidence",
                        harness_arguments=[],
                    )

            source_verifier.assert_not_called()
            runner.assert_not_called()

    def test_work_inside_soza_repository_is_rejected_before_verification(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            soza = root / "soza"
            bundle = root / "bundle"
            soza.mkdir()
            bundle.mkdir()

            with patch.object(ENTRYPOINT, "SOZA_ROOT", soza), patch.object(
                ENTRYPOINT,
                "verify_runtime_bundle",
            ) as source_verifier, patch.object(ENTRYPOINT.subprocess, "run") as runner:
                with self.assertRaisesRegex(ValueError, "Work directory.*SOZA repository"):
                    ENTRYPOINT.run_strict_probe(
                        checkout_dir=None,
                        backend_bundle=bundle,
                        model_dir=None,
                        evidence_dir=root / "evidence",
                        harness_arguments=[],
                        work_dir=soza / "work",
                    )

            source_verifier.assert_not_called()
            runner.assert_not_called()


if __name__ == "__main__":
    unittest.main()
