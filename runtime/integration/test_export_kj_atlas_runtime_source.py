import importlib.util
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


INTEGRATION_DIR = Path(__file__).resolve().parent
VERIFIER_PATH = INTEGRATION_DIR / "verify_kj_atlas_runtime_source.py"
EXPORTER_PATH = INTEGRATION_DIR / "export_kj_atlas_runtime_source.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VERIFIER = load_module("verify_kj_atlas_runtime_source", VERIFIER_PATH)
EXPORTER = load_module("export_kj_atlas_runtime_source", EXPORTER_PATH)


class KJAtlasRuntimeSourceExporterTest(unittest.TestCase):
    def make_backend(self, root: Path) -> Path:
        backend = root / "03_Implement" / "backend"
        (backend / "alembic" / "versions").mkdir(parents=True)
        (backend / "src" / "kj_atlas_api").mkdir(parents=True)
        (backend / "pyproject.toml").write_text(
            "[build-system]\nrequires=['setuptools>=61']\nbuild-backend='setuptools.build_meta'\n"
            "[project]\nname='fixture'\nversion='0.1.0'\n"
            "[tool.setuptools.packages.find]\nwhere=['src']\n",
            encoding="utf-8",
        )
        (backend / "alembic.ini").write_text("[alembic]\nscript_location = alembic\n", encoding="utf-8")
        (backend / "alembic" / "env.py").write_text("x = 1\n", encoding="utf-8")
        (backend / "alembic" / "versions" / "0001.py").write_text("revision='1'\n", encoding="utf-8")
        (backend / "src" / "kj_atlas_api" / "__init__.py").write_text("", encoding="utf-8")
        (backend / "src" / "kj_atlas_api" / "main.py").write_text("APP='fixture'\n", encoding="utf-8")
        return backend

    def init_repository(self, root: Path) -> tuple[Path, object]:
        backend = self.make_backend(root)
        (root / ".gitignore").write_text(".env\n*.so\n__pycache__/\n", encoding="utf-8")
        subprocess.run(["git", "init", str(root)], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(root), "config", "user.email", "fixture@example.invalid"], check=True)
        subprocess.run(["git", "-C", str(root), "config", "user.name", "Fixture"], check=True)
        subprocess.run(["git", "-C", str(root), "add", "."], check=True)
        subprocess.run(["git", "-C", str(root), "commit", "-m", "fixture"], check=True, capture_output=True)
        commit = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        identity = VERIFIER.RuntimeSourceIdentity(
            repository="fixture/kj-atlas",
            source_commit=commit,
            backend_tree="e" * 40,
            runtime_surface_tree=VERIFIER.git_tree_oid(backend),
            pyproject_blob=VERIFIER.git_blob_oid(backend / "pyproject.toml"),
            alembic_ini_blob=VERIFIER.git_blob_oid(backend / "alembic.ini"),
            alembic_tree=VERIFIER.git_tree_oid(backend / "alembic"),
            src_tree=VERIFIER.git_tree_oid(backend / "src"),
        )
        return backend, identity

    def test_export_uses_commit_object_not_ignored_worktree_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "repo"
            root.mkdir()
            backend, identity = self.init_repository(root)

            (backend / ".env").write_text("KJ_ATLAS_LLM_PROVIDER=unexpected\n", encoding="utf-8")
            (backend / "src" / "kj_atlas_api" / "shadow.so").write_bytes(b"ignored-binary")
            pycache = backend / "src" / "kj_atlas_api" / "__pycache__"
            pycache.mkdir()
            (pycache / "main.cpython-310.pyc").write_bytes(b"ignored-bytecode")

            output = Path(temporary) / "bundle"
            payload = EXPORTER.export_runtime_bundle(root, output, identity)

            self.assertEqual("git-archive-from-pinned-commit", payload["sourceAcquisition"])
            self.assertTrue(payload["verification"]["verified"])
            self.assertFalse((output / ".env").exists())
            self.assertFalse((output / "src" / "kj_atlas_api" / "shadow.so").exists())
            self.assertFalse((output / "src" / "kj_atlas_api" / "__pycache__").exists())
            self.assertEqual(identity.runtime_surface_tree, VERIFIER.git_tree_oid(output))

    def test_export_does_not_require_head_to_equal_source_commit(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "repo"
            root.mkdir()
            _backend, identity = self.init_repository(root)
            (root / "later.txt").write_text("later\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "later.txt"], check=True)
            subprocess.run(["git", "-C", str(root), "commit", "-m", "later"], check=True, capture_output=True)

            output = Path(temporary) / "bundle"
            payload = EXPORTER.export_runtime_bundle(root, output, identity)

            self.assertEqual(identity.source_commit, payload["sourceCommit"])
            self.assertTrue(payload["verification"]["verified"])

    def test_export_temporary_extraction_uses_output_parent_not_parent_tmpdir(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            root = base / "repo"
            root.mkdir()
            _backend, identity = self.init_repository(root)
            output = base / "safe" / "bundle"
            unsafe_tmp = root / "unsafe-tmp"
            unsafe_tmp.mkdir()
            original_temporary_directory = tempfile.TemporaryDirectory
            observed_dirs: list[Path] = []

            def tracked_temporary_directory(*args, **kwargs):
                observed_dirs.append(Path(kwargs["dir"]).resolve())
                return original_temporary_directory(*args, **kwargs)

            with patch.dict(os.environ, {"TMPDIR": str(unsafe_tmp)}, clear=False), patch.object(
                EXPORTER.tempfile,
                "TemporaryDirectory",
                side_effect=tracked_temporary_directory,
            ):
                payload = EXPORTER.export_runtime_bundle(root, output, identity)

            self.assertTrue(payload["verification"]["verified"])
            self.assertEqual([output.parent.resolve()], observed_dirs)
            self.assertFalse(any(unsafe_tmp in path.parents or path == unsafe_tmp for path in observed_dirs))

    def test_existing_output_directory_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "repo"
            root.mkdir()
            _backend, identity = self.init_repository(root)
            output = Path(temporary) / "bundle"
            output.mkdir()

            with self.assertRaisesRegex(ValueError, "already exists"):
                EXPORTER.export_runtime_bundle(root, output, identity)

    def test_output_inside_repository_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "repo"
            root.mkdir()
            _backend, identity = self.init_repository(root)

            with self.assertRaisesRegex(ValueError, "must not be inside"):
                EXPORTER.export_runtime_bundle(root, root / "bundle", identity)

    def test_identity_output_inside_repository_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            checkout = base / "repo"
            checkout.mkdir()
            bundle = base / "bundle"

            with self.assertRaisesRegex(ValueError, "separated from source inputs"):
                EXPORTER._prepare_identity_output_path(
                    checkout / "identity.json",
                    checkout_dir=checkout,
                    output_dir=bundle,
                )

    def test_identity_output_inside_exported_bundle_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            checkout = base / "repo"
            checkout.mkdir()
            bundle = base / "bundle"

            with self.assertRaisesRegex(ValueError, "separated from source inputs"):
                EXPORTER._prepare_identity_output_path(
                    bundle / "identity.json",
                    checkout_dir=checkout,
                    output_dir=bundle,
                )

    def test_existing_identity_output_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            checkout = base / "repo"
            checkout.mkdir()
            bundle = base / "bundle"
            identity_output = base / "identity.json"
            identity_output.write_text("existing\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "already exists"):
                EXPORTER._prepare_identity_output_path(
                    identity_output,
                    checkout_dir=checkout,
                    output_dir=bundle,
                )

    def test_external_new_identity_output_is_accepted(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            checkout = base / "repo"
            checkout.mkdir()
            bundle = base / "bundle"
            identity_output = base / "identity.json"

            prepared = EXPORTER._prepare_identity_output_path(
                identity_output,
                checkout_dir=checkout,
                output_dir=bundle,
            )

            self.assertEqual(identity_output.resolve(strict=False), prepared)
            self.assertFalse(identity_output.exists())


if __name__ == "__main__":
    unittest.main()
