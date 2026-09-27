import copy
import hashlib
import importlib.util
import tempfile
import unittest
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "verify_runtime_dependency_wheelhouse",
    HERE / "verify_runtime_dependency_wheelhouse.py",
)
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


def make_wheel(
    root: Path, name: str, version: str, tag: str
) -> tuple[Path, int, str]:
    filename = f"{name}-{version}-py3-none-any.whl"
    path = root / filename
    dist = f"{name}-{version}.dist-info"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(
            f"{dist}/METADATA",
            (
                "Metadata-Version: 2.1\n"
                f"Name: {name}\n"
                f"Version: {version}\n"
            ),
        )
        archive.writestr(
            f"{dist}/WHEEL",
            (
                "Wheel-Version: 1.0\n"
                "Root-Is-Purelib: true\n"
                f"Tag: {tag}\n"
            ),
        )
    raw = path.read_bytes()
    return path, len(raw), hashlib.sha256(raw).hexdigest()


def synthetic_manifest(root: Path):
    path, size, digest = make_wheel(
        root, "demo", "1.2.3", "py3-none-any"
    )
    return {
        "schema": mod.SCHEMA,
        "status": "transport-candidate",
        "entries": [
            {
                "distribution": "demo",
                "version": "1.2.3",
                "wheel_filename": path.name,
                "wheel_bytes": size,
                "wheel_sha256": digest,
                "wheel_tags": ["py3-none-any"],
                "source": {
                    "repository": "example/demo",
                    "revision": "a" * 40,
                    "workflow_run_id": 1,
                    "artifact_id": 2,
                    "artifact_name": "dist",
                    "artifact_zip_sha256": "b" * 64,
                },
            }
        ],
        "scope": {
            "transport_candidate_only": True,
            "product_runtime_pin": False,
            "model_bytes_materialized": False,
            "model_weights_loaded": False,
            "live_inference": False,
            "numeric_parity": False,
            "shipping_decision": False,
        },
    }


class WheelhouseTest(unittest.TestCase):
    def test_valid_synthetic_wheelhouse(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            manifest = synthetic_manifest(root)
            result = mod.verify_wheelhouse(manifest, root)
            self.assertTrue(result["valid"])
            self.assertEqual(result["wheel_count"], 1)

    def test_hash_or_metadata_drift_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            manifest = synthetic_manifest(root)

            bad = copy.deepcopy(manifest)
            bad["entries"][0]["wheel_sha256"] = "0" * 64
            with self.assertRaises(mod.WheelhouseError):
                mod.verify_wheelhouse(bad, root)

            bad = copy.deepcopy(manifest)
            bad["entries"][0]["version"] = "9.9.9"
            with self.assertRaises(mod.WheelhouseError):
                mod.verify_wheelhouse(bad, root)

    def test_missing_or_extra_wheel_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            manifest = synthetic_manifest(root)
            (root / "extra-1.0-py3-none-any.whl").write_bytes(b"x")
            with self.assertRaises(mod.WheelhouseError):
                mod.verify_wheelhouse(manifest, root)

    def test_scope_overclaim_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            manifest = synthetic_manifest(root)
            for field in (
                "product_runtime_pin",
                "model_bytes_materialized",
                "model_weights_loaded",
                "live_inference",
                "numeric_parity",
                "shipping_decision",
            ):
                bad = copy.deepcopy(manifest)
                bad["scope"][field] = True
                with self.subTest(field=field), self.assertRaises(
                    mod.WheelhouseError
                ):
                    mod.verify_wheelhouse(bad, root)

    def test_source_provenance_shape_is_required(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            manifest = synthetic_manifest(root)
            del manifest["entries"][0]["source"]["artifact_id"]
            with self.assertRaises(mod.WheelhouseError):
                mod.verify_wheelhouse(manifest, root)


if __name__ == "__main__":
    unittest.main()
