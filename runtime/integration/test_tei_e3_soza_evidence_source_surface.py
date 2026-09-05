import subprocess
import tempfile
import unittest
from pathlib import Path

import run_tei_bundle_adapter_compatibility as subject


EXPECTED_EXECUTION_PATHS = {
    "runtime/go",
    "runtime/integration/run_tei_version_exchange_evidence.py",
    "runtime/integration/run_tei_revision_b_prepositioned.py",
    "runtime/integration/run_tei_bundle_adapter_compatibility.py",
    "runtime/integration/prepare_tei_fixed_reference_input.py",
    "runtime/integration/runtime_path_safety.py",
    "runtime/integration/verify_tei_evidence_bundle.py",
    "runtime/integration/verify_tei_execution_source_identity.py",
}


class TEIE3SOZAEvidenceSourceSurfaceTest(unittest.TestCase):
    def make_repo(self, root: Path) -> Path:
        repo = root / "soza"
        for relative in EXPECTED_EXECUTION_PATHS:
            path = repo / relative
            if relative == "runtime/go":
                path.mkdir(parents=True)
                (path / "go.mod").write_text(
                    "module example.invalid/soza\n\ngo 1.25\n", encoding="utf-8"
                )
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("# fixture\n", encoding="utf-8")

        subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True)
        subprocess.run(
            ["git", "-C", str(repo), "config", "user.email", "test@example.invalid"],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(repo), "config", "user.name", "test"],
            check=True,
        )
        subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-qm", "fixture"], check=True)
        return repo

    def test_actual_handoff_paths_are_in_source_identity_boundary(self):
        self.assertTrue(EXPECTED_EXECUTION_PATHS.issubset(set(subject.SOZA_EVIDENCE_PATHS)))

    def test_clean_full_execution_surface_is_verified(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self.make_repo(Path(tmp))
            result = subject._verify_soza_source_identity(repo)
        self.assertTrue(result["worktreeCleanWithinBoundary"])
        self.assertEqual(EXPECTED_EXECUTION_PATHS, set(result["objects"]))

    def assert_ignored_helper_is_rejected(self, relative: str):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self.make_repo(Path(tmp))
            helper = repo / relative
            subprocess.run(["git", "-C", str(repo), "rm", "-q", str(helper)], check=True)
            subprocess.run(
                ["git", "-C", str(repo), "commit", "-qm", "remove helper"], check=True
            )
            exclude = repo / ".git/info/exclude"
            exclude.write_text(relative + "\n", encoding="utf-8")
            helper.write_text("# ignored replacement\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "ignored"):
                subject._verify_soza_source_identity(repo)

    def test_ignored_path_safety_helper_is_rejected(self):
        self.assert_ignored_helper_is_rejected(
            "runtime/integration/runtime_path_safety.py"
        )

    def test_ignored_fixed_reference_helper_is_rejected(self):
        self.assert_ignored_helper_is_rejected(
            "runtime/integration/prepare_tei_fixed_reference_input.py"
        )


if __name__ == "__main__":
    unittest.main()
