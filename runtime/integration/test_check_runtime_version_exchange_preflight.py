import hashlib
import re
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import check_runtime_version_exchange_preflight as preflight


INTEGRATION_DIR = Path(__file__).resolve().parent
HARNESS = INTEGRATION_DIR / "run_runtime_version_exchange.sh"


def shell_value(text: str, name: str) -> str:
    match = re.search(rf'^{re.escape(name)}="([^"]+)"$', text, re.MULTILINE)
    if match is None:
        raise AssertionError(f"shell constant not found: {name}")
    return match.group(1)


class RuntimeVersionExchangePreflightTest(unittest.TestCase):
    def test_is_within_distinguishes_source_tree_and_sibling(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "repo"
            child = root / "runtime" / "evidence"
            sibling = Path(temp) / "repo-output"
            self.assertTrue(preflight.is_within(child, root))
            self.assertFalse(preflight.is_within(sibling, root))

    def test_output_path_check_rejects_deep_symlink_ancestor(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            actual_root = root / "actual"
            (actual_root / "nested").mkdir(parents=True)
            linked_root = root / "linked-root"
            try:
                linked_root.symlink_to(actual_root, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("symlinkを作成できない環境です")

            checks = preflight.output_path_check(
                "work",
                linked_root / "nested" / "work",
                (),
                must_be_new=True,
            )

        self.assertEqual("blocked", checks[0].status)
        self.assertEqual("path.work", checks[0].id)
        self.assertIn("ancestor", checks[0].detail)
        self.assertIn("symlink", checks[0].detail)

    def test_archive_check_accepts_exact_size_and_digest(self):
        with tempfile.TemporaryDirectory() as temp:
            archive = Path(temp) / "runtime.tar.zst"
            data = b"fixed-runtime-artifact"
            archive.write_bytes(data)
            expected = hashlib.sha256(data).hexdigest()
            checks = preflight.archive_check("runtime-a", archive, expected, len(data), True)
            self.assertEqual("ok", checks[0].status)
            self.assertIn("size=", checks[0].detail)
            self.assertIn("sha256=", checks[0].detail)

    def test_archive_check_rejects_size_mismatch_before_digest(self):
        with tempfile.TemporaryDirectory() as temp:
            archive = Path(temp) / "runtime.tar.zst"
            data = b"fixed-runtime-artifact"
            archive.write_bytes(data)
            expected = hashlib.sha256(data).hexdigest()
            checks = preflight.archive_check("runtime-a", archive, expected, len(data) + 1, True)
            self.assertEqual("blocked", checks[0].status)
            self.assertIn("size", checks[0].detail)

    def test_archive_check_rejects_digest_mismatch_after_size_match(self):
        with tempfile.TemporaryDirectory() as temp:
            archive = Path(temp) / "runtime.tar.zst"
            data = b"different-runtime-artifact"
            archive.write_bytes(data)
            checks = preflight.archive_check("runtime-a", archive, "0" * 64, len(data), True)
            self.assertEqual("blocked", checks[0].status)
            self.assertIn("digest", checks[0].detail)

    def test_archive_check_rejects_source_tree_location(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "source"
            source.mkdir()
            archive = source / "runtime.tar.zst"
            data = b"fixed-runtime-artifact"
            archive.write_bytes(data)
            expected = hashlib.sha256(data).hexdigest()
            checks = preflight.archive_check(
                "runtime-a",
                archive,
                expected,
                len(data),
                True,
                (source,),
            )
            self.assertEqual("blocked", checks[0].status)
            self.assertEqual("archive.runtime-a.path", checks[0].id)
            self.assertIn("source配下", checks[0].detail)

    def test_archive_check_rejects_symlink(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            actual = root / "actual.tar.zst"
            data = b"fixed-runtime-artifact"
            actual.write_bytes(data)
            archive = root / "runtime.tar.zst"
            archive.symlink_to(actual)
            expected = hashlib.sha256(data).hexdigest()
            checks = preflight.archive_check("runtime-a", archive, expected, len(data), True)
            self.assertEqual("blocked", checks[0].status)
            self.assertEqual("archive.runtime-a.path", checks[0].id)
            self.assertIn("symlink", checks[0].detail)

    def test_archive_check_rejects_deep_symlink_ancestor_before_digest(self):
        data = b"fixed-runtime-artifact"
        expected = hashlib.sha256(data).hexdigest()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            actual_root = root / "actual"
            (actual_root / "nested").mkdir(parents=True)
            actual_archive = actual_root / "nested" / "runtime.tar.zst"
            actual_archive.write_bytes(data)
            linked_root = root / "linked-root"
            try:
                linked_root.symlink_to(actual_root, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("symlinkを作成できない環境です")

            with patch.object(preflight, "sha256_file") as digest:
                checks = preflight.archive_check(
                    "runtime-a",
                    linked_root / "nested" / "runtime.tar.zst",
                    expected,
                    len(data),
                    True,
                )

            digest.assert_not_called()
            self.assertEqual("blocked", checks[0].status)
            self.assertEqual("archive.runtime-a.path", checks[0].id)
            self.assertIn("ancestor", checks[0].detail)

    def test_missing_archive_is_deferred_when_download_is_allowed(self):
        checks = preflight.archive_check("runtime-a", None, "0" * 64, 123, False)
        self.assertEqual("deferred", checks[0].status)
        self.assertIn("123", checks[0].detail)

    def test_missing_archive_blocks_prepositioned_only_preflight(self):
        checks = preflight.archive_check("runtime-a", None, "0" * 64, 123, True)
        self.assertEqual("blocked", checks[0].status)

    def test_model_store_requires_static_identity_verification(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "source"
            model = Path(temp) / "model"
            source.mkdir()
            model.mkdir()
            payload = {
                "model": preflight.MODEL_NAME,
                "manifestSha256": preflight.MODEL_SHA256,
                "referencedBlobCount": 4,
            }
            with patch.object(preflight, "verify_model_store", return_value=payload):
                checks = preflight.model_store_check(model, (source,), True)

        self.assertEqual(["ok", "ok"], [check.status for check in checks])
        self.assertIn("静的に再検証", checks[1].detail)
        self.assertIn(preflight.MODEL_SHA256, checks[1].detail)
        self.assertIn("/api/tags", checks[1].detail)

    def test_model_store_rejects_location_inside_source_before_identity_verification(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "source"
            model = source / "model"
            model.mkdir(parents=True)
            with patch.object(preflight, "verify_model_store") as verifier:
                checks = preflight.model_store_check(model, (source,), True)

        verifier.assert_not_called()
        self.assertEqual("blocked", checks[0].status)
        self.assertEqual("model.store", checks[0].id)
        self.assertIn("source配下", checks[0].detail)

    def test_model_store_rejects_parent_containing_source_before_identity_verification(self):
        with tempfile.TemporaryDirectory() as temp:
            model = Path(temp) / "model"
            source = model / "kj-atlas"
            source.mkdir(parents=True)
            with patch.object(preflight, "verify_model_store") as verifier:
                checks = preflight.model_store_check(model, (source,), True)

        verifier.assert_not_called()
        self.assertEqual("blocked", checks[0].status)
        self.assertEqual("model.store", checks[0].id)
        self.assertIn("sourceを包含できません", checks[0].detail)

    def test_model_store_rejects_deep_symlink_ancestor_before_identity_verification(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            actual_root = root / "actual"
            model = actual_root / "nested" / "model"
            model.mkdir(parents=True)
            linked_root = root / "linked-root"
            try:
                linked_root.symlink_to(actual_root, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("symlinkを作成できない環境です")

            requested = linked_root / "nested" / "model"
            with patch.object(preflight, "verify_model_store") as verifier:
                checks = preflight.model_store_check(requested, (), True)

            verifier.assert_not_called()
            self.assertEqual("blocked", checks[0].status)
            self.assertEqual("model.store.path", checks[0].id)
            self.assertIn("ancestor", checks[0].detail)

    def test_model_store_blocks_when_static_identity_verification_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "source"
            model = Path(temp) / "model"
            source.mkdir()
            model.mkdir()
            with patch.object(
                preflight,
                "verify_model_store",
                side_effect=ValueError("model manifest digest mismatch"),
            ):
                checks = preflight.model_store_check(model, (source,), True)

        self.assertEqual(["ok", "blocked"], [check.status for check in checks])
        self.assertIn("固定model artifact identity", checks[1].detail)

    def test_source_repository_check_uses_pinned_commit_object_not_head_or_tree_state(self):
        calls: list[tuple[str, ...]] = []

        def fake_run_git(path: Path, *args: str) -> subprocess.CompletedProcess[str]:
            calls.append(args)
            if args == ("rev-parse", "--is-inside-work-tree"):
                return subprocess.CompletedProcess([], 0, stdout="true\n", stderr="")
            if args == ("cat-file", "-e", f"{preflight.KJ_ATLAS_COMMIT}^{{commit}}"):
                return subprocess.CompletedProcess([], 0, stdout="", stderr="")
            raise AssertionError(f"unexpected git call: {args}")

        with patch.object(preflight, "run_git", side_effect=fake_run_git):
            checks = preflight.repository_commit_object_check(
                "kj-atlas",
                Path("/tmp/kj-atlas"),
                preflight.KJ_ATLAS_COMMIT,
            )

        self.assertEqual(["ok", "ok"], [check.status for check in checks])
        self.assertEqual(
            [
                ("rev-parse", "--is-inside-work-tree"),
                ("cat-file", "-e", f"{preflight.KJ_ATLAS_COMMIT}^{{commit}}"),
            ],
            calls,
        )
        self.assertIn("HEADやworking treeの内容はstrict runtime sourceに使用しません", checks[1].detail)

    def test_source_repository_check_rejects_missing_pinned_commit_object(self):
        results = [
            subprocess.CompletedProcess([], 0, stdout="true\n", stderr=""),
            subprocess.CompletedProcess([], 1, stdout="", stderr="missing object"),
        ]
        with patch.object(preflight, "run_git", side_effect=results):
            checks = preflight.repository_commit_object_check(
                "kj-atlas",
                Path("/tmp/kj-atlas"),
                preflight.KJ_ATLAS_COMMIT,
            )

        self.assertEqual(["ok", "blocked"], [check.status for check in checks])
        self.assertEqual("kj-atlas.commit-object", checks[1].id)

    def test_source_repository_check_rejects_deep_symlink_ancestor_before_git(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            actual_root = root / "actual"
            checkout = actual_root / "nested" / "checkout"
            checkout.mkdir(parents=True)
            linked_root = root / "linked-root"
            try:
                linked_root.symlink_to(actual_root, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("symlinkを作成できない環境です")

            with patch.object(preflight, "run_git") as run_git:
                checks = preflight.repository_commit_object_check(
                    "kj-atlas",
                    linked_root / "nested" / "checkout",
                    preflight.KJ_ATLAS_COMMIT,
                )

            run_git.assert_not_called()
            self.assertEqual("blocked", checks[0].status)
            self.assertEqual("kj-atlas.path", checks[0].id)
            self.assertIn("ancestor", checks[0].detail)

    def test_disk_capacity_check_is_observational_only(self):
        with tempfile.TemporaryDirectory() as temp:
            check = preflight.disk_capacity_check(Path(temp) / "future-work")
            self.assertEqual("ok", check.status)
            self.assertIn(str(preflight.TOTAL_COMPRESSED_RUNTIME_BYTES), check.detail)
            self.assertIn("十分とは判定しません", check.detail)

    def test_fixed_runtime_sizes_match_official_metadata_values(self):
        self.assertEqual(1421793186, preflight.RUNTIME_SIZE_A)
        self.assertEqual(1421191399, preflight.RUNTIME_SIZE_B)
        self.assertEqual(2842984585, preflight.TOTAL_COMPRESSED_RUNTIME_BYTES)

    def test_parser_rejects_checkout_and_bundle_together(self):
        parser = preflight.build_parser()
        with self.assertRaises(SystemExit):
            parser.parse_args(
                [
                    "--kj-atlas-dir",
                    "/tmp/kj-atlas",
                    "--kj-atlas-backend-bundle",
                    "/tmp/kj-atlas-bundle",
                ]
            )

    def test_runtime_bundle_check_accepts_verified_identity(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            soza = root / "soza"
            bundle = root / "bundle"
            soza.mkdir()
            bundle.mkdir()
            payload = {
                "sourceCommit": preflight.PINNED_IDENTITY.source_commit,
                "pinnedBackendTree": preflight.PINNED_IDENTITY.backend_tree,
                "runtimeSurfaceTree": preflight.PINNED_IDENTITY.runtime_surface_tree,
            }
            with patch.object(preflight, "verify_runtime_bundle", return_value=payload):
                checks = preflight.runtime_bundle_check(bundle, soza)
            self.assertEqual(["ok", "ok"], [check.status for check in checks])
            self.assertIn(preflight.PINNED_IDENTITY.runtime_surface_tree, checks[1].detail)

    def test_runtime_bundle_check_rejects_identity_mismatch(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            soza = root / "soza"
            bundle = root / "bundle"
            soza.mkdir()
            bundle.mkdir()
            with patch.object(
                preflight,
                "verify_runtime_bundle",
                side_effect=ValueError("runtime source bundle identity mismatch"),
            ):
                checks = preflight.runtime_bundle_check(bundle, soza)
            self.assertEqual("blocked", checks[0].status)
            self.assertIn("identity", checks[0].detail)

    def test_runtime_bundle_check_rejects_bundle_inside_soza(self):
        with tempfile.TemporaryDirectory() as temp:
            soza = Path(temp) / "soza"
            bundle = soza / "bundle"
            bundle.mkdir(parents=True)
            checks = preflight.runtime_bundle_check(bundle, soza)
            self.assertEqual("blocked", checks[0].status)
            self.assertIn("SEI repository配下", checks[0].detail)

    def test_runtime_bundle_check_rejects_deep_symlink_ancestor_before_identity_verification(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            soza = root / "soza"
            actual_root = root / "actual"
            bundle = actual_root / "nested" / "bundle"
            soza.mkdir()
            bundle.mkdir(parents=True)
            linked_root = root / "linked-root"
            try:
                linked_root.symlink_to(actual_root, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("symlinkを作成できない環境です")

            with patch.object(preflight, "verify_runtime_bundle") as verifier:
                checks = preflight.runtime_bundle_check(
                    linked_root / "nested" / "bundle",
                    soza,
                )

            verifier.assert_not_called()
            self.assertEqual("blocked", checks[0].status)
            self.assertEqual("kj-atlas.bundle.path", checks[0].id)
            self.assertIn("ancestor", checks[0].detail)

    def test_preflight_and_harness_use_the_same_fixed_identity(self):
        text = HARNESS.read_text(encoding="utf-8")
        pairs = [
            ("KJ_ATLAS_COMMIT", preflight.KJ_ATLAS_COMMIT),
            ("MODEL_NAME", preflight.MODEL_NAME),
            ("MODEL_SHA256", preflight.MODEL_SHA256),
            ("RUNTIME_VERSION_A", preflight.RUNTIME_VERSION_A),
            ("RUNTIME_VERSION_B", preflight.RUNTIME_VERSION_B),
            ("RUNTIME_SHA256_A", preflight.RUNTIME_SHA256_A),
            ("RUNTIME_SHA256_B", preflight.RUNTIME_SHA256_B),
        ]
        for shell_name, expected in pairs:
            with self.subTest(shell=shell_name):
                self.assertEqual(expected, shell_value(text, shell_name))
        self.assertEqual(preflight.KJ_ATLAS_COMMIT, preflight.PINNED_IDENTITY.source_commit)

    def test_report_exposes_fixed_artifact_sizes_without_promoting_evidence(self):
        result = preflight.report([preflight.Check("sample", "ok", "ok")])
        self.assertEqual("ready", result["result"])
        self.assertEqual(1421793186, result["fixedArtifacts"]["runtimeA"]["sizeBytes"])
        self.assertEqual(1421191399, result["fixedArtifacts"]["runtimeB"]["sizeBytes"])
        self.assertEqual(2842984585, result["fixedArtifacts"]["totalCompressedRuntimeBytes"])
        self.assertIn("!= actual runtime A/B inference PASS", result["stopLine"])

    def test_report_exposes_pinned_source_identity_without_claiming_verification(self):
        result = preflight.report([preflight.Check("sample", "ok", "ok")])
        pinned = result["pinnedSourceIdentity"]
        self.assertEqual(preflight.PINNED_IDENTITY.source_commit, pinned["sourceCommit"])
        self.assertEqual(preflight.PINNED_IDENTITY.backend_tree, pinned["pinnedBackendTree"])
        self.assertEqual(
            preflight.PINNED_IDENTITY.runtime_surface_tree,
            pinned["runtimeSurfaceTree"],
        )
        self.assertNotIn("verified", pinned)

    def test_report_is_blocked_when_any_check_is_blocked(self):
        result = preflight.report(
            [
                preflight.Check("ok", "ok", "ok"),
                preflight.Check("blocked", "blocked", "blocked"),
            ]
        )
        self.assertEqual("blocked", result["result"])
        self.assertEqual(["blocked"], result["blockers"])


if __name__ == "__main__":
    unittest.main()
