import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "materialize_managed_runtime_env",
    HERE / "materialize_managed_runtime_env.py",
)
mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = mod
SPEC.loader.exec_module(mod)

MANIFEST = {
    "schema": "sei.local-typed-comparator-runtime-wheelhouse/v1",
    "platform": {
        "os": "linux",
        "arch": "x86_64",
        "python": "3.13.5",
    },
}
MANIFEST_RAW = json.dumps(MANIFEST, separators=(",", ":")).encode()
HOST_DEPS = {
    "torch": "2.10.0+cpu",
    "huggingface-hub": "1.16.1",
    "numpy": "2.3.5",
    "fastapi": "0.128.2",
    "uvicorn": "0.48.0",
}


def wheel_verification(root: Path):
    wheels = []
    for index, distribution in enumerate(
        mod.TRANSPORTED_DISTRIBUTIONS
    ):
        filename = f"{distribution}-synthetic.whl"
        path = root / filename
        path.write_bytes(f"wheel-{distribution}".encode())
        wheels.append(
            {
                "distribution": distribution,
                "version": f"1.0.{index}",
                "filename": filename,
                "bytes": path.stat().st_size,
                "sha256": f"{index + 1:064x}",
                "tags": ["py3-none-any"],
            }
        )
    return {
        "valid": True,
        "wheels": wheels,
        "scope": {
            "transport_candidate_only": True,
            "host_assisted_transport": True,
            "self_contained_wheelhouse": False,
        },
    }


def probe_for(env_root: Path, verification: dict):
    transported = {}
    for item in verification["wheels"]:
        dist = item["distribution"]
        wheel = env_root.parent / "wheelhouse" / item["filename"]
        module_path = (
            env_root
            / "lib"
            / "python3.13"
            / "site-packages"
            / dist.replace("-", "_")
            / "__init__.py"
        )
        transported[dist] = {
            "version": item["version"],
            "module_file": str(module_path),
            "direct_url": {
                "url": wheel.resolve().as_uri(),
                "archive_info": {
                    "hashes": {"sha256": item["sha256"]}
                },
            },
        }
    return {
        "prefix": str(env_root.resolve()),
        "base_prefix": "/synthetic/base",
        "transported": transported,
        "host_dependencies": dict(HOST_DEPS),
        "modernbert_import": True,
    }


def create_env_skeleton(root: Path):
    (root / "bin").mkdir(parents=True)
    (root / "bin" / "python").write_bytes(b"synthetic-python")
    (root / "pyvenv.cfg").write_text(
        "include-system-site-packages = true\n",
        encoding="utf-8",
    )


class ManagedRuntimeEnvironmentTest(unittest.TestCase):
    def test_direct_url_requires_exact_local_wheel_and_hash(self):
        with tempfile.TemporaryDirectory() as td:
            wheel = Path(td) / "x.whl"
            wheel.write_bytes(b"x")
            value = {
                "url": wheel.resolve().as_uri(),
                "archive_info": {
                    "hash": "sha256=" + "a" * 64,
                },
            }
            result = mod._parse_direct_url(
                value,
                wheel_path=wheel,
                wheel_sha256="a" * 64,
                distribution="x",
            )
            self.assertEqual(result["wheel_filename"], "x.whl")
            self.assertFalse(result["source_path_retained"])

            bad = json.loads(json.dumps(value))
            bad["archive_info"]["hash"] = "sha256=" + "b" * 64
            with self.assertRaises(mod.ManagedRuntimeEnvironmentError):
                mod._parse_direct_url(
                    bad,
                    wheel_path=wheel,
                    wheel_sha256="a" * 64,
                    distribution="x",
                )

    def test_verify_environment_attests_only_transported_wheels(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            wheelhouse = root / "wheelhouse"
            wheelhouse.mkdir()
            verification = wheel_verification(wheelhouse)
            env_root = root / "runtime"
            create_env_skeleton(env_root)
            probe = probe_for(env_root, verification)

            with mock.patch.object(
                mod.wheelhouse_verifier,
                "verify_wheelhouse",
                return_value=verification,
            ), mock.patch.object(
                mod,
                "_require_platform",
                return_value=MANIFEST["platform"],
            ), mock.patch.object(
                mod,
                "_probe_environment",
                return_value=probe,
            ):
                result = mod.verify_environment(
                    MANIFEST,
                    wheelhouse,
                    env_root,
                    expected_python_executable=env_root / "bin" / "python",
                )

            self.assertTrue(result["valid"])
            self.assertTrue(
                result["scope"][
                    "transported_wheel_installation_origin_attested"
                ]
            )
            self.assertFalse(
                result["scope"]["runtime_installation_origin_attested"]
            )
            self.assertFalse(
                result["scope"]["host_dependency_versions_pinned"]
            )
            self.assertFalse(result["scope"]["self_contained_runtime"])
            self.assertFalse(result["scope"]["environment_relocatable"])
            self.assertEqual(result["host_dependencies"], HOST_DEPS)

    def test_module_import_outside_runtime_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            wheelhouse = root / "wheelhouse"
            wheelhouse.mkdir()
            verification = wheel_verification(wheelhouse)
            env_root = root / "runtime"
            create_env_skeleton(env_root)
            probe = probe_for(env_root, verification)
            probe["transported"]["transformers"][
                "module_file"
            ] = "/outside/transformers/__init__.py"

            with mock.patch.object(
                mod.wheelhouse_verifier,
                "verify_wheelhouse",
                return_value=verification,
            ), mock.patch.object(
                mod,
                "_require_platform",
                return_value=MANIFEST["platform"],
            ), mock.patch.object(
                mod,
                "_probe_environment",
                return_value=probe,
            ):
                with self.assertRaises(
                    mod.ManagedRuntimeEnvironmentError
                ):
                    mod.verify_environment(
                        MANIFEST,
                        wheelhouse,
                        env_root,
                    )

    def test_exact_venv_path_not_only_resolved_base_python_is_required(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            wheelhouse = root / "wheelhouse"
            wheelhouse.mkdir()
            verification = wheel_verification(wheelhouse)

            env_a = root / "env-a"
            env_b = root / "env-b"
            for env_root in (env_a, env_b):
                (env_root / "bin").mkdir(parents=True)
                (env_root / "bin" / "python").symlink_to(sys.executable)
                (env_root / "pyvenv.cfg").write_text(
                    "include-system-site-packages = true\n",
                    encoding="utf-8",
                )
            probe = probe_for(env_a, verification)

            with mock.patch.object(
                mod.wheelhouse_verifier,
                "verify_wheelhouse",
                return_value=verification,
            ), mock.patch.object(
                mod,
                "_require_platform",
                return_value=MANIFEST["platform"],
            ), mock.patch.object(
                mod,
                "_probe_environment",
                return_value=probe,
            ):
                with self.assertRaisesRegex(
                    mod.ManagedRuntimeEnvironmentError,
                    "current interpreter",
                ):
                    mod.verify_environment(
                        MANIFEST,
                        wheelhouse,
                        env_a,
                        expected_python_executable=env_b / "bin" / "python",
                    )

    def test_system_site_packages_must_remain_enabled(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            wheelhouse = root / "wheelhouse"
            wheelhouse.mkdir()
            verification = wheel_verification(wheelhouse)
            env_root = root / "runtime"
            create_env_skeleton(env_root)
            (env_root / "pyvenv.cfg").write_text(
                "include-system-site-packages = false\n",
                encoding="utf-8",
            )

            with mock.patch.object(
                mod.wheelhouse_verifier,
                "verify_wheelhouse",
                return_value=verification,
            ), mock.patch.object(
                mod,
                "_require_platform",
                return_value=MANIFEST["platform"],
            ):
                with self.assertRaisesRegex(
                    mod.ManagedRuntimeEnvironmentError,
                    "system-site-packages",
                ):
                    mod.verify_environment(
                        MANIFEST,
                        wheelhouse,
                        env_root,
                    )

    def test_materialize_success_retains_origin_boundary(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            wheelhouse = root / "wheelhouse"
            wheelhouse.mkdir()
            verification = wheel_verification(wheelhouse)
            env_root = root / "runtime"

            class Builder:
                def __init__(self, **kwargs):
                    self.kwargs = kwargs

                def create(self, path):
                    create_env_skeleton(Path(path))

            calls = []

            def runner(command, **kwargs):
                calls.append(command)
                return subprocess.CompletedProcess(
                    command, 0, stdout="", stderr=""
                )

            runtime_result = {
                "schema": mod.SCHEMA,
                "valid": True,
                "python": {
                    "relative_path": "bin/python",
                    "version": "3.13.5",
                    "system_site_packages": True,
                    "current_interpreter_matches": False,
                },
                "transported": {},
                "host_dependencies": HOST_DEPS,
                "scope": {
                    "host_assisted_environment": True,
                    "transported_wheel_installation_origin_attested": True,
                    "runtime_installation_origin_attested": False,
                    "host_dependency_versions_pinned": False,
                    "self_contained_runtime": False,
                    "environment_relocatable": False,
                    "model_weights_loaded": False,
                    "live_inference": False,
                    "numeric_parity": False,
                    "shipping_decision": False,
                },
            }

            with mock.patch.object(
                mod.wheelhouse_verifier,
                "verify_wheelhouse",
                return_value=verification,
            ), mock.patch.object(
                mod,
                "_require_platform",
                return_value=MANIFEST["platform"],
            ), mock.patch.object(
                mod,
                "verify_environment",
                return_value=runtime_result,
            ):
                receipt = mod.materialize_environment(
                    MANIFEST,
                    MANIFEST_RAW,
                    wheelhouse,
                    env_root,
                    runner=runner,
                    builder_factory=Builder,
                )

            self.assertEqual(
                receipt["status"], "materialized-and-verified"
            )
            self.assertTrue((env_root / mod.RECEIPT_FILE).is_file())
            install = calls[0]
            self.assertIn("--no-index", install)
            self.assertIn("--no-deps", install)
            self.assertIn("--force-reinstall", install)
            self.assertEqual(
                receipt["scope"][
                    "transported_wheel_installation_origin_attested"
                ],
                True,
            )
            self.assertFalse(
                receipt["scope"]["runtime_installation_origin_attested"]
            )

    def test_install_failure_removes_environment(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            wheelhouse = root / "wheelhouse"
            wheelhouse.mkdir()
            verification = wheel_verification(wheelhouse)
            env_root = root / "runtime"

            class Builder:
                def __init__(self, **kwargs):
                    pass

                def create(self, path):
                    create_env_skeleton(Path(path))

            def runner(command, **kwargs):
                return subprocess.CompletedProcess(
                    command, 2, stdout="", stderr="synthetic failure"
                )

            with mock.patch.object(
                mod.wheelhouse_verifier,
                "verify_wheelhouse",
                return_value=verification,
            ), mock.patch.object(
                mod,
                "_require_platform",
                return_value=MANIFEST["platform"],
            ):
                with self.assertRaises(
                    mod.ManagedRuntimeEnvironmentError
                ):
                    mod.materialize_environment(
                        MANIFEST,
                        MANIFEST_RAW,
                        wheelhouse,
                        env_root,
                        runner=runner,
                        builder_factory=Builder,
                    )
            self.assertFalse(env_root.exists())

    def test_manifest_raw_binding_and_existing_output_fail_closed(self):
        with self.assertRaises(mod.ManagedRuntimeEnvironmentError):
            mod._require_raw_binding(
                MANIFEST,
                b'{"schema":"different"}',
                "manifest",
            )

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            wheelhouse = root / "wheelhouse"
            wheelhouse.mkdir()
            verification = wheel_verification(wheelhouse)
            env_root = root / "runtime"
            env_root.mkdir()
            with mock.patch.object(
                mod.wheelhouse_verifier,
                "verify_wheelhouse",
                return_value=verification,
            ), mock.patch.object(
                mod,
                "_require_platform",
                return_value=MANIFEST["platform"],
            ):
                with self.assertRaises(
                    mod.ManagedRuntimeEnvironmentError
                ):
                    mod.materialize_environment(
                        MANIFEST,
                        MANIFEST_RAW,
                        wheelhouse,
                        env_root,
                    )


if __name__ == "__main__":
    unittest.main()
