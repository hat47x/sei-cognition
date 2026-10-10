import importlib.util
import json
import os
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "capture_reference_l0", HERE / "capture_reference_l0.py"
)
capture = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(capture)


class ReferenceManagedCaptureTest(unittest.TestCase):
    def test_child_environment_is_offline_and_drops_credentials(self):
        previous = {
            key: os.environ.get(key)
            for key in (
                "HF_TOKEN",
                "HUGGING_FACE_HUB_TOKEN",
                "LAYA_API_KEY",
                "PYTHONPATH",
            )
        }
        os.environ["HF_TOKEN"] = "secret"
        os.environ["HUGGING_FACE_HUB_TOKEN"] = "secret"
        os.environ["LAYA_API_KEY"] = "secret"
        os.environ["PYTHONPATH"] = "/wrong"
        try:
            env = capture.child_environment(3)
        finally:
            for key, value in previous.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value
        self.assertEqual(env["HF_HUB_OFFLINE"], "1")
        self.assertEqual(env["TRANSFORMERS_OFFLINE"], "1")
        self.assertEqual(env["PYTHONNOUSERSITE"], "1")
        self.assertEqual(env["LAYA_DEVICE"], "cpu")
        self.assertEqual(env["LAYA_THREADS"], "3")
        self.assertNotIn("HF_TOKEN", env)
        self.assertNotIn("LAYA_API_KEY", env)
        self.assertNotIn("PYTHONPATH", env)

    def test_source_manifest_changes_with_source_bytes(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "site" / "laya"
            root.mkdir(parents=True)
            (root / "__init__.py").write_text("x = 1\n", encoding="utf-8")
            first = capture.source_manifest(root)
            (root / "extra.py").write_text("y = 2\n", encoding="utf-8")
            second = capture.source_manifest(root)
        self.assertNotEqual(first, second)

    def test_extract_wheel_accepts_pinned_shape_and_rejects_traversal(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            good = root / "good.whl"
            with zipfile.ZipFile(good, "w") as archive:
                archive.writestr("laya/__init__.py", "__version__ = '0.3.20'\n")
                archive.writestr("laya/x.py", "x = 1\n")
                archive.writestr(
                    "laya-0.3.20.dist-info/METADATA",
                    "Metadata-Version: 2.1\nName: laya\nVersion: 0.3.20\n",
                )
            info = capture.extract_verified_wheel(good, root / "good-site")
            self.assertEqual(info["version"], "0.3.20")
            self.assertEqual(info["source_file_count"], 2)

            bad = root / "bad.whl"
            with zipfile.ZipFile(bad, "w") as archive:
                archive.writestr("../escape.py", "bad\n")
                archive.writestr(
                    "laya-0.3.20.dist-info/METADATA",
                    "Metadata-Version: 2.1\nName: laya\nVersion: 0.3.20\n",
                )
            with self.assertRaises(capture.ReferenceCaptureError):
                capture.extract_verified_wheel(bad, root / "bad-site")

    def test_runtime_dependency_gate_is_fail_closed(self):
        versions = {name: "1.0" for name in capture.REQUIRED_DEPENDENCIES}
        with mock.patch.object(
            capture,
            "package_version",
            side_effect=lambda name: versions.get(name),
        ):
            self.assertEqual(capture.require_runtime_dependencies(), versions)

        with mock.patch.object(
            capture,
            "package_version",
            side_effect=lambda name: None if name == "transformers" else "1.0",
        ):
            with self.assertRaises(capture.ReferenceCaptureError):
                capture.require_runtime_dependencies()

    def test_runtime_identity_requires_exact_managed_binding(self):
        dependencies = {
            name: "1.0" for name in capture.REQUIRED_DEPENDENCIES
        }
        identity = {
            "laya_version": "0.3.20",
            "imported_from_extracted_wheel": True,
            "source_manifest_sha256": "a" * 64,
            "source_file_count": 10,
            "loaded": ["typed-decisions"],
            "model_binding_local_directory": True,
            "device": "cpu",
            "torch_num_threads": 4,
            "offline": {
                "HF_HUB_OFFLINE": "1",
                "TRANSFORMERS_OFFLINE": "1",
            },
            "dependencies": dependencies,
        }
        capture.validate_runtime_identity(
            identity,
            expected_manifest_sha256="a" * 64,
            expected_source_file_count=10,
            expected_dependencies=dependencies,
            expected_threads=4,
        )

        for field, value in (
            ("laya_version", "0.3.19"),
            ("loaded", []),
            ("model_binding_local_directory", False),
            ("device", "cuda"),
            ("torch_num_threads", 8),
        ):
            broken = json.loads(json.dumps(identity))
            broken[field] = value
            with self.subTest(field=field), self.assertRaises(
                capture.ReferenceCaptureError
            ):
                capture.validate_runtime_identity(
                    broken,
                    expected_manifest_sha256="a" * 64,
                    expected_source_file_count=10,
                    expected_dependencies=dependencies,
                    expected_threads=4,
                )

    def test_live_token_counts_bind_to_retained_reference(self):
        records = [
            {
                "case_id": "a",
                "response_utf8": json.dumps(
                    {"usage": {"input_tokens": 7}}
                ),
            },
            {
                "case_id": "b",
                "response_utf8": json.dumps(
                    {"usage": {"input_tokens": 9}}
                ),
            },
        ]
        capture.bind_live_token_counts(records, {"a": 7, "b": 9})
        self.assertTrue(records[0]["live_token_count_matches_reference"])

        bad = [
            {
                "case_id": "a",
                "response_utf8": json.dumps(
                    {"usage": {"input_tokens": 8}}
                ),
            }
        ]
        with self.assertRaises(capture.ReferenceCaptureError):
            capture.bind_live_token_counts(bad, {"a": 7})

    def test_choice11_diagnostic_requires_exact_12_option_probe(self):
        class Protocol:
            @staticmethod
            def validate_fixture(_fixture):
                return None

        diagnostic = {
            "schema": "test",
            "cases": [
                {
                    "case_id": "choice11",
                    "request": {
                        "state": {"x": 1},
                        "questions": {
                            "q": {
                                "type": "choice",
                                "instructions": "pick",
                                "criteria": {
                                    f"o{i:02d}": f"Option {i}"
                                    for i in range(12)
                                },
                            }
                        },
                    },
                }
            ],
        }
        capture.validate_choice11_diagnostic(diagnostic, Protocol)
        del diagnostic["cases"][0]["request"]["questions"]["q"]["criteria"][
            "o11"
        ]
        with self.assertRaises(capture.ReferenceCaptureError):
            capture.validate_choice11_diagnostic(diagnostic, Protocol)

    def test_output_must_stay_outside_verified_source_tree(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "repo"
            outside = Path(td) / "evidence"
            root.mkdir()
            outside.mkdir()
            with self.assertRaises(capture.ReferenceCaptureError):
                capture.require_external_output_path(root / "run.json", root)
            self.assertEqual(
                capture.require_external_output_path(
                    outside / "run.json", root
                ),
                (outside / "run.json").resolve(),
            )


if __name__ == "__main__":
    unittest.main()
