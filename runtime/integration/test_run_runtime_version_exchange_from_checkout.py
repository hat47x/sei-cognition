import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


INTEGRATION_DIR = Path(__file__).resolve().parent
ENTRYPOINT_PATH = INTEGRATION_DIR / "run_runtime_version_exchange_from_checkout.py"
SPEC = importlib.util.spec_from_file_location(
    "run_runtime_version_exchange_from_checkout",
    ENTRYPOINT_PATH,
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load checkout entrypoint: {ENTRYPOINT_PATH}")
ENTRYPOINT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ENTRYPOINT)


class RuntimeVersionExchangeFromCheckoutTest(unittest.TestCase):
    def test_rejects_forwarded_checkout_source_option(self):
        with self.assertRaisesRegex(ValueError, "source option"):
            ENTRYPOINT._reject_unsafe_forwarded_source_options(
                ["--kj-atlas-dir", "/tmp/other"]
            )

    def test_rejects_forwarded_bundle_source_option(self):
        with self.assertRaisesRegex(ValueError, "source option"):
            ENTRYPOINT._reject_unsafe_forwarded_source_options(
                ["--kj-atlas-backend-bundle=/tmp/other"]
            )

    def test_checkout_is_exported_before_harness_receives_source(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            checkout = root / "checkout"
            checkout.mkdir()
            bundle = root / "bundle"
            identity = root / "source-export.json"
            calls = []

            def fake_export(checkout_dir, output_dir):
                calls.append(("export", checkout_dir, output_dir))
                output_dir.mkdir()
                return {
                    "schema": "soza.kj-atlas-runtime-source-export/v1",
                    "sourceAcquisition": "git-archive-from-pinned-commit",
                    "sourceCommit": "f" * 40,
                    "verification": {
                        "verified": True,
                        "sourceMode": "verified-runtime-bundle",
                    },
                }

            class Completed:
                returncode = 0

            def fake_run(command, check):
                calls.append(("run", command, check))
                return Completed()

            with patch.object(ENTRYPOINT, "export_runtime_bundle", side_effect=fake_export), patch.object(
                ENTRYPOINT.subprocess,
                "run",
                side_effect=fake_run,
            ):
                result = ENTRYPOINT.run_from_checkout(
                    checkout,
                    ["--keep-work"],
                    source_bundle_dir=bundle,
                    source_export_identity=identity,
                )

            self.assertEqual(0, result)
            self.assertEqual("export", calls[0][0])
            self.assertEqual(checkout.resolve(), calls[0][1])
            self.assertEqual(bundle.resolve(), calls[0][2])
            self.assertEqual("run", calls[1][0])
            command = calls[1][1]
            self.assertEqual(str(ENTRYPOINT.HARNESS), command[0])
            self.assertEqual("--kj-atlas-backend-bundle", command[1])
            self.assertEqual(str(bundle.resolve()), command[2])
            self.assertNotIn("--kj-atlas-dir", command)
            self.assertIn("--keep-work", command)

            payload = json.loads(identity.read_text(encoding="utf-8"))
            self.assertEqual("git-archive-from-pinned-commit", payload["sourceAcquisition"])

    def test_existing_identity_path_is_rejected_before_export_or_harness(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            checkout = root / "checkout"
            checkout.mkdir()
            bundle = root / "bundle"
            identity = root / "source-export.json"
            identity.write_text("existing\n", encoding="utf-8")

            with patch.object(ENTRYPOINT, "export_runtime_bundle") as exporter, patch.object(
                ENTRYPOINT.subprocess,
                "run",
            ) as runner:
                with self.assertRaisesRegex(ValueError, "identity already exists"):
                    ENTRYPOINT.run_from_checkout(
                        checkout,
                        [],
                        source_bundle_dir=bundle,
                        source_export_identity=identity,
                    )
                exporter.assert_not_called()
                runner.assert_not_called()

    def test_identity_path_inside_checkout_is_rejected_before_export(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            checkout = root / "checkout"
            checkout.mkdir()
            bundle = root / "bundle"
            identity = checkout / "local" / "source-export.json"

            with patch.object(ENTRYPOINT, "export_runtime_bundle") as exporter:
                with self.assertRaisesRegex(ValueError, "must not be inside the KJ Atlas repository"):
                    ENTRYPOINT.run_from_checkout(
                        checkout,
                        [],
                        source_bundle_dir=bundle,
                        source_export_identity=identity,
                    )
                exporter.assert_not_called()

    def test_identity_path_inside_bundle_is_rejected_before_export(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            checkout = root / "checkout"
            checkout.mkdir()
            bundle = root / "bundle"
            identity = bundle / "source-export.json"

            with patch.object(ENTRYPOINT, "export_runtime_bundle") as exporter:
                with self.assertRaisesRegex(ValueError, "must not be inside the verified runtime bundle"):
                    ENTRYPOINT.run_from_checkout(
                        checkout,
                        [],
                        source_bundle_dir=bundle,
                        source_export_identity=identity,
                    )
                exporter.assert_not_called()


if __name__ == "__main__":
    unittest.main()
