import tempfile
import unittest
from pathlib import Path
from unittest import mock

import preflight_tei_version_exchange_from_github as subject


class TEIGitHubVersionExchangePreflightTest(unittest.TestCase):
    def make_go(
        self,
        root: Path,
        version: str,
        *,
        goos: str = "linux",
        goarch: str = "amd64",
    ) -> Path:
        executable = root / "go"
        executable.write_text(
            "#!/bin/sh\n"
            "case \"$1\" in\n"
            f"  version) echo 'go version {version} linux/amd64' ;;\n"
            "  env)\n"
            "    if [ \"$2\" = GOOS ] && [ \"$3\" = GOARCH ]; then\n"
            f"      printf '{goos}\\n{goarch}\\n'\n"
            "    else\n"
            "      exit 2\n"
            "    fi\n"
            "    ;;\n"
            "  *) exit 2 ;;\n"
            "esac\n",
            encoding="utf-8",
        )
        executable.chmod(0o755)
        return executable

    def make_soza_go_mod(self, root: Path, requirement: str = "1.25") -> Path:
        repo = root / "soza"
        go_root = repo / "runtime/go"
        go_root.mkdir(parents=True)
        (go_root / "go.mod").write_text(
            f"module example.invalid/soza\n\ngo {requirement}\n",
            encoding="utf-8",
        )
        return repo

    def test_credential_reports_source_without_value(self):
        secret = "not-a-real-token-value"
        observation = subject._check_github_credential(
            {"GITHUB_TOKEN": secret, "GH_TOKEN": "unused"}
        )

        self.assertEqual("GITHUB_TOKEN", observation["source"])
        self.assertFalse(observation["valueReported"])
        self.assertFalse(observation["networkAccessPerformed"])
        self.assertNotIn(secret, repr(observation))

    def test_gh_token_is_accepted_when_github_token_is_absent(self):
        observation = subject._check_github_credential(
            {"GH_TOKEN": "not-a-real-token-value"}
        )
        self.assertEqual("GH_TOKEN", observation["source"])

    def test_e2_go_requires_exact_historical_version_and_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            good_dir = root / "good"
            good_dir.mkdir()
            good = self.make_go(good_dir, subject.build_runner.EXPECTED_GO_VERSION)
            observation = subject._check_tei_go(good)
            self.assertTrue(observation["exactMatch"])
            self.assertTrue(observation["targetMatch"])
            self.assertEqual(
                subject.build_runner.EXPECTED_GO_VERSION,
                observation["required"],
            )
            self.assertEqual("linux/amd64", observation["requiredTarget"])
            self.assertEqual("linux/amd64", observation["observedTarget"])

            bad_dir = root / "bad"
            bad_dir.mkdir()
            bad = self.make_go(bad_dir, "go1.23.3")
            with self.assertRaisesRegex(Exception, "go1.23.3"):
                subject._check_tei_go(bad)

            wrong_target_dir = root / "wrong-target"
            wrong_target_dir.mkdir()
            wrong_target = self.make_go(
                wrong_target_dir,
                subject.build_runner.EXPECTED_GO_VERSION,
                goarch="arm64",
            )
            with self.assertRaisesRegex(Exception, "linux/arm64"):
                subject._check_tei_go(wrong_target)

    def test_e3_go_uses_current_soza_go_directive_and_linux_amd64_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            soza = self.make_soza_go_mod(root, "1.25")

            good_dir = root / "good"
            good_dir.mkdir()
            good = self.make_go(good_dir, "go1.25.1")
            observation = subject._check_soza_go(good, soza)
            self.assertEqual("1.25", observation["required"])
            self.assertTrue(observation["requirementSatisfied"])
            self.assertTrue(observation["targetMatch"])
            self.assertEqual("linux/amd64", observation["observedTarget"])

            bad_dir = root / "bad"
            bad_dir.mkdir()
            bad = self.make_go(bad_dir, "go1.24.9")
            with self.assertRaisesRegex(Exception, "required"):
                subject._check_soza_go(bad, soza)

            wrong_target_dir = root / "wrong-target"
            wrong_target_dir.mkdir()
            wrong_target = self.make_go(
                wrong_target_dir,
                "go1.25.1",
                goarch="arm64",
            )
            with self.assertRaisesRegex(Exception, "linux/arm64"):
                subject._check_soza_go(wrong_target, soza)

    def test_reference_checkout_reuses_canonical_git_identity_verifier(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "reference-a"
            repo.mkdir()
            expected = {
                "head": subject.source_identity.REVISION_A,
                "worktreeCleanWithinBoundary": True,
            }
            with mock.patch.object(
                subject.source_identity,
                "verify_repository",
                return_value=expected,
            ) as verifier:
                observation = subject._check_reference_input(repo, None)

            verifier.assert_called_once_with(
                repo.resolve(),
                expected_objects=subject.source_identity.REVISION_A_REFERENCE_OBJECTS,
                expected_head=subject.source_identity.REVISION_A,
            )
            self.assertEqual("git_checkout", observation["mode"])
            self.assertTrue(observation["worktreeCleanWithinBoundary"])

    def test_historical_reference_bundle_reuses_existing_bundle_verifier(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp) / "historical-a.tar.gz"
            archive.write_bytes(b"fixture")
            verified = {
                "sourceCommit": subject.source_identity.REVISION_A,
                "archive": str(archive.resolve()),
                "archiveSha256": "abc123",
            }
            with mock.patch.object(
                subject.fixed_reference,
                "verify_fixed_reference_input_bundle",
                return_value=verified,
            ) as verifier:
                observation = subject._check_reference_input(None, archive)

            verifier.assert_called_once_with(archive)
            self.assertEqual("historical_evidence_bundle", observation["mode"])
            self.assertEqual("abc123", observation["archiveSha256"])

    def test_multiple_missing_prerequisites_are_aggregated(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            soza = self.make_soza_go_mod(root)
            reference = root / "reference-a"
            reference.mkdir()
            output = root / "evidence"
            missing_go = root / "missing" / "go"

            with mock.patch.object(
                subject,
                "_check_platform",
                side_effect=ValueError("platform mismatch"),
            ), mock.patch.object(
                subject,
                "_check_reference_input",
                return_value={"mode": "git_checkout"},
            ), mock.patch.object(
                subject,
                "_check_soza_source",
                return_value={"head": "fixture"},
            ), mock.patch.object(
                subject,
                "_check_output_path",
                return_value={"staticPathSafetyVerified": True},
            ):
                result = subject.run_preflight(
                    reference,
                    soza,
                    output,
                    tei_go_executable=missing_go,
                    soza_go_executable=missing_go,
                    env={},
                )

            self.assertFalse(result["ready"])
            self.assertEqual("blocked", result["result"])
            self.assertIn("execution_platform", result["blockedChecks"])
            self.assertIn("github_credential", result["blockedChecks"])
            self.assertIn("tei_go_toolchain", result["blockedChecks"])
            self.assertIn("soza_go_toolchain", result["blockedChecks"])
            self.assertFalse(result["networkAccessPerformed"])
            self.assertFalse(result["revisionBSourceMaterialized"])
            self.assertFalse(result["evidenceOutputCreated"])

    def test_output_inside_soza_repository_is_rejected_without_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            soza = self.make_soza_go_mod(root)
            output = soza / "runtime/evidence/new-run"

            with self.assertRaisesRegex(ValueError, "SEI repository"):
                subject._check_output_path(
                    output,
                    soza_repo_root=soza,
                    reference_source_repo=None,
                    reference_evidence_bundle=None,
                    overwrite=False,
                )

            self.assertFalse(output.exists())

    def test_existing_outputs_are_reported_without_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            soza = self.make_soza_go_mod(root)
            output = root / "evidence"
            output.mkdir()
            canonical = output / subject.version_exchange.REPORT_NAME
            canonical.write_text("existing\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "--overwrite"):
                subject._check_output_path(
                    output,
                    soza_repo_root=soza,
                    reference_source_repo=None,
                    reference_evidence_bundle=None,
                    overwrite=False,
                )

            self.assertEqual("existing\n", canonical.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
