import importlib.util
import tempfile
import unittest
from pathlib import Path


INTEGRATION_DIR = Path(__file__).resolve().parent
ENTRYPOINT_PATH = INTEGRATION_DIR / "run_runtime_version_exchange_strict.py"
SPEC = importlib.util.spec_from_file_location("run_runtime_version_exchange_strict", ENTRYPOINT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load strict entrypoint: {ENTRYPOINT_PATH}")
ENTRYPOINT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ENTRYPOINT)


class StrictRuntimeExchangeWriteJsonOnceTest(unittest.TestCase):
    def test_success_then_existing_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "observation.json"
            ENTRYPOINT._write_json(path, {"result": "ok"})
            with self.assertRaises(ValueError):
                ENTRYPOINT._write_json(path, {"result": "changed"})
            self.assertIn('"ok"', path.read_text(encoding="utf-8"))

    def test_existing_symlink_is_rejected_without_touching_target(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "target.json"
            target.write_text('{"sentinel": true}\n', encoding="utf-8")
            path = root / "observation.json"
            path.symlink_to(target)

            with self.assertRaises(ValueError):
                ENTRYPOINT._write_json(path, {"result": "changed"})

            self.assertEqual('{"sentinel": true}\n', target.read_text(encoding="utf-8"))
            self.assertTrue(path.is_symlink())

    def test_dangling_symlink_is_rejected_without_creating_target(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "missing-target.json"
            path = root / "observation.json"
            path.symlink_to(target)
            self.assertTrue(path.is_symlink())
            self.assertFalse(path.exists())
            self.assertFalse(target.exists())

            with self.assertRaises(ValueError):
                ENTRYPOINT._write_json(path, {"result": "changed"})

            self.assertTrue(path.is_symlink())
            self.assertFalse(target.exists())


if __name__ == "__main__":
    unittest.main()
