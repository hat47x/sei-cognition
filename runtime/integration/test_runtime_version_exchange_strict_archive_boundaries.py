import hashlib
import importlib.util
import os
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

    def test_omitted_work_dir_is_derived_from_evidence_and_parent_tmpdir_is_not_used(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bundle = root / "bundle"
            evidence = root / "evidence"
            expected_work = root / "evidence-work"
            bundle.mkdir()

            class Completed:
                returncode = 0

            def fake_run(command, check, env=None):
                evidence.mkdir()
                return Completed()

            with patch.dict(os.environ, {"TMPDIR": str(bundle)}, clear=False), patch.object(
                ENTRYPOINT,
                "verify_runtime_bundle",
            ), patch.object(ENTRYPOINT.subprocess, "run", side_effect=fake_run) as runner:
                result = ENTRYPOINT.run_strict_probe(
                    checkout_dir=None,
                    backend_bundle=bundle,
                    model_dir=None,
                    evidence_dir=evidence,
                    harness_arguments=[],
                    work_dir=None,
                )

            self.assertEqual(0, result)
            command = runner.call_args.args[0]
            self.assertIn("--work-dir", command)
            self.assertEqual(
                str(expected_work.resolve()),
                command[command.index("--work-dir") + 1],
            )
            child_env = runner.call_args.kwargs["env"]
            self.assertEqual(str(expected_work.resolve()), child_env["TMPDIR"])
            self.assertNotEqual(str(bundle.resolve()), child_env["TMPDIR"])

    def test_checkout_source_bundle_is_derived_from_evidence_and_cleaned_after_run(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            checkout = root / "checkout"
            evidence = root / "evidence"
            expected_source_root = root / "evidence-source"
            expected_bundle = expected_source_root / "backend"
            checkout.mkdir()
            observed_outputs: list[Path] = []

            def fake_export(source, output):
                observed_outputs.append(output.resolve())
                output.mkdir(parents=True)
                return {
                    "schema": "soza.kj-atlas-runtime-source-export/v1",
                    "sourceAcquisition": "git-archive-from-pinned-commit",
                }

            class Completed:
                returncode = 0

            def fake_run(command, check, env=None):
                evidence.mkdir()
                return Completed()

            with patch.dict(os.environ, {"TMPDIR": str(checkout)}, clear=False), patch.object(
                ENTRYPOINT,
                "export_runtime_bundle",
                side_effect=fake_export,
            ), patch.object(ENTRYPOINT.subprocess, "run", side_effect=fake_run) as runner:
                result = ENTRYPOINT.run_strict_probe(
                    checkout_dir=checkout,
                    backend_bundle=None,
                    model_dir=None,
                    evidence_dir=evidence,
                    harness_arguments=[],
                    work_dir=None,
                )

            self.assertEqual(0, result)
            self.assertEqual([expected_bundle.resolve()], observed_outputs)
            command = runner.call_args.args[0]
            self.assertEqual(
                str(expected_bundle.resolve()),
                command[command.index("--kj-atlas-backend-bundle") + 1],
            )
            self.assertFalse(expected_source_root.exists())
            self.assertTrue((evidence / "runtime-exchange-source-export.json").is_file())

    def test_dangling_evidence_symlink_is_rejected_before_source_verification(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bundle = root / "bundle"
            bundle.mkdir()
            evidence = root / "evidence"
            evidence.symlink_to(root / "missing-evidence-target")

            with patch.object(ENTRYPOINT, "verify_runtime_bundle") as source_verifier, patch.object(
                ENTRYPOINT.subprocess,
                "run",
            ) as runner:
                with self.assertRaisesRegex(ValueError, "Evidence directory.*symlink"):
                    ENTRYPOINT.run_strict_probe(
                        checkout_dir=None,
                        backend_bundle=bundle,
                        model_dir=None,
                        evidence_dir=evidence,
                        harness_arguments=[],
                    )

            source_verifier.assert_not_called()
            runner.assert_not_called()

    def test_work_path_with_symlink_parent_is_rejected_before_source_verification(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bundle = root / "bundle"
            actual_parent = root / "actual-work-parent"
            link_parent = root / "work-parent-link"
            bundle.mkdir()
            actual_parent.mkdir()
            link_parent.symlink_to(actual_parent, target_is_directory=True)

            with patch.object(ENTRYPOINT, "verify_runtime_bundle") as source_verifier, patch.object(
                ENTRYPOINT.subprocess,
                "run",
            ) as runner:
                with self.assertRaisesRegex(ValueError, "Work directory.*parent.*symlink"):
                    ENTRYPOINT.run_strict_probe(
                        checkout_dir=None,
                        backend_bundle=bundle,
                        model_dir=None,
                        evidence_dir=root / "evidence",
                        harness_arguments=[],
                        work_dir=link_parent / "work",
                    )

            source_verifier.assert_not_called()
            runner.assert_not_called()

    def test_dangling_prepared_model_symlink_is_rejected_before_preparation(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bundle = root / "bundle"
            bundle.mkdir()
            prepared = root / "prepared-model"
            prepared.symlink_to(root / "missing-model-target")

            with patch.object(ENTRYPOINT, "prepare_model_store") as preparer, patch.object(
                ENTRYPOINT,
                "verify_runtime_bundle",
            ) as source_verifier, patch.object(ENTRYPOINT.subprocess, "run") as runner:
                with self.assertRaisesRegex(ValueError, "Prepared model directory.*symlink"):
                    ENTRYPOINT.run_strict_probe(
                        checkout_dir=None,
                        backend_bundle=bundle,
                        model_dir=None,
                        prepare_model_dir=prepared,
                        evidence_dir=root / "evidence",
                        harness_arguments=[],
                    )

            preparer.assert_not_called()
            source_verifier.assert_not_called()
            runner.assert_not_called()

    def test_prepositioned_model_store_root_symlink_is_rejected_before_verification(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bundle = root / "bundle"
            actual_model = root / "actual-model"
            model_link = root / "model-link"
            bundle.mkdir()
            actual_model.mkdir()
            model_link.symlink_to(actual_model, target_is_directory=True)

            with patch.object(ENTRYPOINT, "verify_model_store") as model_verifier, patch.object(
                ENTRYPOINT,
                "verify_runtime_bundle",
            ) as source_verifier, patch.object(ENTRYPOINT.subprocess, "run") as runner:
                with self.assertRaisesRegex(ValueError, "Model directory.*symlink"):
                    ENTRYPOINT.run_strict_probe(
                        checkout_dir=None,
                        backend_bundle=bundle,
                        model_dir=model_link,
                        evidence_dir=root / "evidence",
                        harness_arguments=[],
                    )

            model_verifier.assert_not_called()
            source_verifier.assert_not_called()
            runner.assert_not_called()

    def test_new_path_rejects_deep_symlink_ancestor(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            actual_root = root / "actual"
            (actual_root / "nested").mkdir(parents=True)
            link_root = root / "linked-root"
            try:
                link_root.symlink_to(actual_root, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("symlinkを作成できない環境です")

            requested = link_root / "nested" / "new-output"
            with self.assertRaisesRegex(ValueError, "ancestorにsymlink"):
                ENTRYPOINT._new_path(requested, "Work directory")
            self.assertFalse((actual_root / "nested" / "new-output").exists())

    def test_existing_directory_rejects_deep_symlink_ancestor(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            actual_root = root / "actual"
            existing = actual_root / "nested" / "bundle"
            existing.mkdir(parents=True)
            link_root = root / "linked-root"
            try:
                link_root.symlink_to(actual_root, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("symlinkを作成できない環境です")

            requested = link_root / "nested" / "bundle"
            with self.assertRaisesRegex(ValueError, "ancestorにsymlink"):
                ENTRYPOINT._existing_directory(
                    requested,
                    "KJ Atlas verified runtime bundle",
                )

    def test_runtime_archive_rejects_deep_symlink_ancestor_before_verification(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bundle = root / "bundle"
            bundle.mkdir()
            actual_root = root / "actual"
            (actual_root / "nested").mkdir(parents=True)
            archive = actual_root / "nested" / "runtime-a.tar.zst"
            archive.write_bytes(b"runtime")
            link_root = root / "linked-root"
            try:
                link_root.symlink_to(actual_root, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("symlinkを作成できない環境です")

            requested = link_root / "nested" / "runtime-a.tar.zst"
            with patch.object(ENTRYPOINT, "verify_archive") as archive_verifier:
                with self.assertRaisesRegex(ValueError, "ancestorにsymlink"):
                    ENTRYPOINT._validate_runtime_archives(
                        ["--runtime-a-archive", str(requested)],
                        source_input=bundle,
                        source_label="KJ Atlas verified runtime bundle",
                    )
            archive_verifier.assert_not_called()


if __name__ == "__main__":
    unittest.main()
