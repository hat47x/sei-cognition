import tempfile
import unittest
from pathlib import Path
from unittest import mock

import check_runtime_version_exchange_preflight as preflight


class RuntimeVersionExchangePreflightModelStoreTest(unittest.TestCase):
    def test_explicit_model_store_requires_static_identity_verification(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            model_store = base / "models"
            model_store.mkdir()
            source_root = base / "source"
            source_root.mkdir()
            payload = {
                "model": preflight.MODEL_NAME,
                "manifestSha256": preflight.MODEL_SHA256,
                "referencedBlobCount": 5,
            }
            with mock.patch.object(preflight, "verify_model_store", return_value=payload) as verify:
                checks = preflight.model_store_check(model_store, (source_root,), True)

        verify.assert_called_once_with(model_store.resolve())
        self.assertEqual(["ok", "ok"], [check.status for check in checks])
        self.assertEqual("model.store.identity", checks[1].id)
        self.assertIn(preflight.MODEL_SHA256, checks[1].detail)
        self.assertIn("/api/tags", checks[1].detail)

    def test_static_identity_mismatch_blocks_preflight(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            model_store = base / "models"
            model_store.mkdir()
            with mock.patch.object(
                preflight,
                "verify_model_store",
                side_effect=ValueError("manifest digest mismatch"),
            ):
                checks = preflight.model_store_check(model_store, (), True)

        self.assertEqual(["ok", "blocked"], [check.status for check in checks])
        self.assertEqual("model.store.identity", checks[1].id)
        self.assertIn("manifest digest mismatch", checks[1].detail)

    def test_missing_prepositioned_store_remains_blocked(self):
        checks = preflight.model_store_check(None, (), True)
        self.assertEqual(1, len(checks))
        self.assertEqual("model.store", checks[0].id)
        self.assertEqual("blocked", checks[0].status)

    def test_work_local_store_without_explicit_path_remains_deferred(self):
        checks = preflight.model_store_check(None, (), False)
        self.assertEqual(1, len(checks))
        self.assertEqual("deferred", checks[0].status)
        self.assertIn("Ollama起動後", checks[0].detail)

    def test_model_store_under_source_root_is_rejected_before_identity_verification(self):
        with tempfile.TemporaryDirectory() as temporary:
            source_root = Path(temporary)
            model_store = source_root / "models"
            model_store.mkdir()
            with mock.patch.object(preflight, "verify_model_store") as verify:
                checks = preflight.model_store_check(model_store, (source_root,), True)

        verify.assert_not_called()
        self.assertEqual("blocked", checks[0].status)
        self.assertEqual("model.store", checks[0].id)

    def test_model_store_root_symlink_is_rejected_before_identity_verification(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            actual_store = base / "actual-models"
            actual_store.mkdir()
            model_link = base / "models-link"
            try:
                model_link.symlink_to(actual_store, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("symlinkを作成できない環境です")

            with mock.patch.object(preflight, "verify_model_store") as verify:
                checks = preflight.model_store_check(model_link, (), True)

        verify.assert_not_called()
        self.assertEqual(1, len(checks))
        self.assertEqual("model.store.path", checks[0].id)
        self.assertEqual("blocked", checks[0].status)
        self.assertIn("rootにsymlink", checks[0].detail)

    def test_model_store_with_symlink_parent_is_rejected_before_identity_verification(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            actual_parent = base / "actual-parent"
            actual_parent.mkdir()
            actual_store = actual_parent / "models"
            actual_store.mkdir()
            link_parent = base / "model-parent-link"
            try:
                link_parent.symlink_to(actual_parent, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("symlinkを作成できない環境です")

            with mock.patch.object(preflight, "verify_model_store") as verify:
                checks = preflight.model_store_check(link_parent / "models", (), True)

        verify.assert_not_called()
        self.assertEqual(1, len(checks))
        self.assertEqual("model.store.path", checks[0].id)
        self.assertEqual("blocked", checks[0].status)
        self.assertIn("rootのparentにsymlink", checks[0].detail)


if __name__ == "__main__":
    unittest.main()
