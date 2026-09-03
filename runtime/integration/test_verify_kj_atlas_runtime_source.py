import importlib.util
import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path


INTEGRATION_DIR = Path(__file__).resolve().parent
VERIFIER_PATH = INTEGRATION_DIR / "verify_kj_atlas_runtime_source.py"
SPEC = importlib.util.spec_from_file_location("verify_kj_atlas_runtime_source", VERIFIER_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load verifier: {VERIFIER_PATH}")
VERIFIER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFIER)


class KJAtlasRuntimeSourceVerifierTest(unittest.TestCase):
    def make_bundle(self, root: Path):
        (root / "alembic" / "versions").mkdir(parents=True)
        (root / "src" / "kj_atlas_api" / "routes").mkdir(parents=True)
        (root / "pyproject.toml").write_text("[project]\nname='fixture'\n", encoding="utf-8")
        (root / "alembic.ini").write_text("[alembic]\n", encoding="utf-8")
        (root / "alembic" / "env.py").write_text("x = 1\n", encoding="utf-8")
        (root / "alembic" / "versions" / "0001.py").write_text("revision='1'\n", encoding="utf-8")
        (root / "src" / "kj_atlas_api" / "__init__.py").write_text("", encoding="utf-8")
        (root / "src" / "kj_atlas_api" / "main.py").write_text("APP = 'fixture'\n", encoding="utf-8")
        (root / "src" / "kj_atlas_api" / "routes" / "ai.py").write_text("ROUTE = 'ai'\n", encoding="utf-8")

    def identity_for(self, root: Path):
        return VERIFIER.RuntimeSourceIdentity(
            repository="fixture/kj-atlas",
            source_commit="f" * 40,
            backend_tree="e" * 40,
            runtime_surface_tree=VERIFIER.git_tree_oid(root),
            pyproject_blob=VERIFIER.git_blob_oid(root / "pyproject.toml"),
            alembic_ini_blob=VERIFIER.git_blob_oid(root / "alembic.ini"),
            alembic_tree=VERIFIER.git_tree_oid(root / "alembic"),
            src_tree=VERIFIER.git_tree_oid(root / "src"),
        )

    def test_git_tree_oid_matches_git_write_tree(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            work_tree = base / "work"
            git_dir = base / "git"
            work_tree.mkdir()
            self.make_bundle(work_tree)

            subprocess.run(["git", "init", "--bare", str(git_dir)], check=True, capture_output=True)
            env = os.environ.copy()
            env["GIT_DIR"] = str(git_dir)
            env["GIT_WORK_TREE"] = str(work_tree)
            subprocess.run(["git", "add", "-A"], check=True, env=env, capture_output=True)
            expected = subprocess.run(
                ["git", "write-tree"],
                check=True,
                env=env,
                capture_output=True,
                text=True,
            ).stdout.strip()

            self.assertEqual(VERIFIER.git_tree_oid(work_tree), expected)

    def test_pinned_runtime_surface_tree_matches_pinned_components(self):
        identity = VERIFIER.PINNED_IDENTITY
        actual = VERIFIER._git_tree_oid(
            [
                (b"alembic.ini", False, b"100644", identity.alembic_ini_blob),
                (b"alembic", True, b"40000", identity.alembic_tree),
                (b"pyproject.toml", False, b"100644", identity.pyproject_blob),
                (b"src", True, b"40000", identity.src_tree),
            ]
        )

        self.assertEqual(actual, identity.runtime_surface_tree)
        self.assertNotEqual(identity.runtime_surface_tree, identity.backend_tree)

    def test_synthetic_runtime_bundle_is_accepted_for_matching_identity(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.make_bundle(root)
            identity = self.identity_for(root)

            payload = VERIFIER.verify_runtime_bundle(root, identity)

            self.assertTrue(payload["verified"])
            self.assertEqual(payload["sourceMode"], "verified-runtime-bundle")
            self.assertEqual(payload["sourceCommit"], identity.source_commit)
            self.assertEqual(payload["pinnedBackendTree"], identity.backend_tree)
            self.assertEqual(payload["runtimeSurfaceTree"], identity.runtime_surface_tree)
            self.assertEqual(payload["runtimeSurface"]["srcTree"], identity.src_tree)

    def test_tampered_runtime_source_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.make_bundle(root)
            identity = self.identity_for(root)
            (root / "src" / "kj_atlas_api" / "main.py").write_text(
                "APP = 'tampered'\n", encoding="utf-8"
            )

            with self.assertRaisesRegex(ValueError, "identity mismatch"):
                VERIFIER.verify_runtime_bundle(root, identity)

    def test_unexpected_top_level_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.make_bundle(root)
            identity = self.identity_for(root)
            (root / "setup.py").write_text("raise SystemExit\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "top-level mismatch"):
                VERIFIER.verify_runtime_bundle(root, identity)

    def test_executable_runtime_source_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.make_bundle(root)
            identity = self.identity_for(root)
            target = root / "src" / "kj_atlas_api" / "main.py"
            target.chmod(target.stat().st_mode | stat.S_IXUSR)

            with self.assertRaisesRegex(ValueError, "must not be executable"):
                VERIFIER.verify_runtime_bundle(root, identity)


if __name__ == "__main__":
    unittest.main()
