import json
import tempfile
import unittest
from pathlib import Path

import run_runtime_version_exchange_with_verification as subject


class RuntimeExchangeWriteJsonOnceTest(unittest.TestCase):
    def test_success_creates_json_once(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "observation.json"

            subject._write_json_once(path, {"result": "ok"})

            self.assertEqual(
                {"result": "ok"},
                json.loads(path.read_text(encoding="utf-8")),
            )
            with self.assertRaises(ValueError):
                subject._write_json_once(path, {"result": "changed"})
            self.assertEqual(
                {"result": "ok"},
                json.loads(path.read_text(encoding="utf-8")),
            )

    def test_existing_symlink_is_rejected_without_touching_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "target.json"
            target.write_text('{"sentinel": true}\n', encoding="utf-8")
            path = root / "observation.json"
            path.symlink_to(target)

            with self.assertRaises(ValueError):
                subject._write_json_once(path, {"result": "changed"})

            self.assertEqual(
                '{"sentinel": true}\n',
                target.read_text(encoding="utf-8"),
            )
            self.assertTrue(path.is_symlink())

    def test_dangling_symlink_is_rejected_without_creating_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "missing-target.json"
            path = root / "observation.json"
            path.symlink_to(target)
            self.assertFalse(path.exists())
            self.assertTrue(path.is_symlink())
            self.assertFalse(target.exists())

            with self.assertRaises(ValueError):
                subject._write_json_once(path, {"result": "changed"})

            self.assertTrue(path.is_symlink())
            self.assertFalse(target.exists())


if __name__ == "__main__":
    unittest.main()
