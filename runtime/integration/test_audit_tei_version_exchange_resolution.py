import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import audit_tei_version_exchange_resolution as subject


class TEIVersionExchangeResolutionAuditTest(unittest.TestCase):
    def canonical(self, root: Path, result: str, *, staged=True) -> Path:
        bundle = root / "tei-b.tar.gz"
        bundle.write_bytes(b"bundle")
        report = {
            "schema": subject.CANONICAL_SCHEMA,
            "result": result,
            "comparisonAxis": {
                "buildSourceCommit": subject.source_identity.REVISION_B,
                "referenceInputSourceCommit": subject.source_identity.REVISION_A,
                "referenceInputAcquisition": "historical_evidence_bundle",
                "teiGoRequirement": "go1.23.2",
                "sozaGoRequirement": "1.25",
                "expectedSozaHead": "f" * 40,
            },
            "bundleArchive": str(bundle),
            "e2": None,
            "e3": None,
            "qualityJudgement": "not_evaluated",
        }
        if result in {
            "fixed_scope_e2_e3_verified",
            "e2_verified_e3_failed",
            "e2_bundle_verified_e3_not_run",
        }:
            report["e2"] = {
                "result": "bundle_produced",
                "completedStages": [
                    "tei_cli_build",
                    "deployment_provider_plan_execution",
                ],
            }
        if result == "fixed_scope_e2_e3_verified":
            report["e3"] = {
                "result": "adapter_compatible",
                "sozaSource": {"head": "f" * 40},
                "postLiveTestSozaSource": {"head": "f" * 40},
            }
        elif result == "e2_failed":
            report["failure"] = {"stage": "E2", "type": "StageError"}
            if staged:
                report["failure"]["substage"] = "tei_cli_build"
        elif result == "e2_verified_e3_failed":
            report["failure"] = {"stage": "E3", "type": "StageError"}
            if staged:
                report["failure"]["substage"] = "soza_teiintegration_live_test"
        path = root / "canonical.json"
        path.write_text(json.dumps(report), encoding="utf-8")
        return path

    def wrapper(
        self,
        root: Path,
        canonical_result: str,
        *,
        source_commit=None,
    ) -> Path:
        result = (
            canonical_result
            if canonical_result == "fixed_scope_e2_e3_verified"
            else "version_exchange_failed"
        )
        wrapper = {
            "schema": subject.WRAPPER_SCHEMA,
            "result": result,
            "sourceAcquisition": {
                "mode": "github_git_data_api",
                "repository": subject.github_source.GITHUB_REPOSITORY,
                "sourceCommit": source_commit or subject.source_identity.REVISION_B,
                "rootTree": subject.github_source.REVISION_B_ROOT_TREE,
                "credentialSource": "GITHUB_TOKEN",
                "canonicalSourceVerification": {
                    "revisionBExactHead": True,
                    "worktreeCleanWithinBoundary": True,
                },
            },
        }
        if canonical_result == "e2_failed":
            wrapper["failure"] = {"stage": "E2"}
        elif canonical_result == "e2_verified_e3_failed":
            wrapper["failure"] = {"stage": "E3"}
        path = root / "wrapper.json"
        path.write_text(json.dumps(wrapper), encoding="utf-8")
        return path

    def historical(self, root: Path) -> Path:
        path = root / "tei-a.tar.gz"
        path.write_bytes(b"historical")
        return path

    def baseline(self):
        return {
            "head": "f" * 40,
            "expectedHead": "f" * 40,
            "expectedHeadMatched": True,
            "objects": {path: "a" * 40 for path in subject.BASELINE_PATHS},
            "worktreeCleanWithinBoundary": True,
        }

    def historical_verification(self):
        return {
            "sourceCommit": subject.source_identity.REVISION_A,
            "archive": "/tmp/a.tar.gz",
            "archiveSha256": "1" * 64,
            "referenceInput": {"workspace_tree": "2" * 40},
        }

    def b_verification(self):
        return {
            "observation": {
                "source_commit": subject.source_identity.REVISION_B,
                "binary_sha256": "3" * 64,
                "provider_plan_sha256": "4" * 64,
                "archive_sha256": "5" * 64,
            },
            "referenceInput": {
                "source_commit": subject.source_identity.REVISION_A,
            },
        }

    def run_audit(
        self,
        root: Path,
        result: str,
        *,
        staged=True,
        wrapper=True,
        historical=True,
    ):
        canonical = self.canonical(root, result, staged=staged)
        wrapper_path = self.wrapper(root, result) if wrapper else None
        historical_path = self.historical(root) if historical else None
        with (
            mock.patch.object(
                subject,
                "_verify_soza_baseline",
                return_value=self.baseline(),
            ),
            mock.patch.object(
                subject.fixed_reference,
                "verify_fixed_reference_input_bundle",
                return_value=self.historical_verification(),
            ),
            mock.patch.object(
                subject.bundle_verifier,
                "verify_bundle",
                return_value=self.b_verification(),
            ),
        ):
            return subject.audit_resolution(
                canonical,
                soza_repo_root=root,
                historical_a_bundle=historical_path,
                github_wrapper_report=wrapper_path,
            )

    def test_full_success_becomes_manual_resolution_candidate_not_auto_resolved(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_audit(Path(tmp), "fixed_scope_e2_e3_verified")
        self.assertEqual("manual_review_required", result["result"])
        self.assertTrue(result["resolutionCandidate"])
        self.assertFalse(result["autoResolvePermitted"])
        self.assertEqual(
            [1, 2, 3, 4, 5, 6],
            result["automatedCriteria"]["satisfied"],
        )
        self.assertEqual(subject.MANUAL, result["criteria"]["7"]["status"])
        self.assertEqual(subject.MANUAL, result["criteria"]["8"]["status"])

    def test_e2_staged_failure_satisfies_stop_location_but_not_artifact_or_e3(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_audit(Path(tmp), "e2_failed")
        self.assertFalse(result["resolutionCandidate"])
        self.assertEqual(subject.BLOCKED, result["criteria"]["2"]["status"])
        self.assertEqual(subject.SATISFIED, result["criteria"]["3"]["status"])
        self.assertEqual(subject.BLOCKED, result["criteria"]["4"]["status"])
        self.assertEqual(subject.SATISFIED, result["criteria"]["6"]["status"])

    def test_e3_staged_failure_can_still_be_resolution_candidate(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_audit(Path(tmp), "e2_verified_e3_failed")
        self.assertTrue(result["resolutionCandidate"])
        self.assertEqual(subject.SATISFIED, result["criteria"]["2"]["status"])
        self.assertEqual(subject.SATISFIED, result["criteria"]["3"]["status"])
        self.assertEqual(subject.SATISFIED, result["criteria"]["4"]["status"])
        self.assertEqual(subject.SATISFIED, result["criteria"]["6"]["status"])
        self.assertEqual(
            "adapter_local_compatibility_review_first",
            result["criteria"]["7"]["detail"]["hint"]["classification"],
        )

    def test_unstaged_e3_failure_is_not_resolution_candidate(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_audit(
                Path(tmp),
                "e2_verified_e3_failed",
                staged=False,
            )
        self.assertFalse(result["resolutionCandidate"])
        self.assertEqual(subject.BLOCKED, result["criteria"]["4"]["status"])

    def test_wrapper_source_identity_mismatch_blocks_boundary_criterion(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            canonical = self.canonical(root, "fixed_scope_e2_e3_verified")
            wrapper = self.wrapper(
                root,
                "fixed_scope_e2_e3_verified",
                source_commit="0" * 40,
            )
            historical = self.historical(root)
            with (
                mock.patch.object(
                    subject,
                    "_verify_soza_baseline",
                    return_value=self.baseline(),
                ),
                mock.patch.object(
                    subject.fixed_reference,
                    "verify_fixed_reference_input_bundle",
                    return_value=self.historical_verification(),
                ),
                mock.patch.object(
                    subject.bundle_verifier,
                    "verify_bundle",
                    return_value=self.b_verification(),
                ),
            ):
                result = subject.audit_resolution(
                    canonical,
                    soza_repo_root=root,
                    historical_a_bundle=historical,
                    github_wrapper_report=wrapper,
                )
        self.assertEqual(subject.BLOCKED, result["criteria"]["6"]["status"])
        self.assertFalse(result["resolutionCandidate"])

    def test_missing_historical_bundle_keeps_criteria_1_and_5_manual(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_audit(
                Path(tmp),
                "fixed_scope_e2_e3_verified",
                historical=False,
            )
        self.assertEqual(subject.MANUAL, result["criteria"]["1"]["status"])
        self.assertEqual(subject.MANUAL, result["criteria"]["5"]["status"])
        self.assertFalse(result["resolutionCandidate"])

    def test_canonical_axis_drift_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = self.canonical(root, "e2_failed")
            value = json.loads(path.read_text(encoding="utf-8"))
            value["comparisonAxis"]["buildSourceCommit"] = "0" * 40
            path.write_text(json.dumps(value), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "comparison axis"):
                subject.audit_resolution(path, soza_repo_root=root)

    def test_soza_baseline_records_committed_requirement_objects(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "soza"
            repo.mkdir()
            for relative in subject.BASELINE_PATHS:
                path = repo / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(relative + "\n", encoding="utf-8")
            subprocess.run(
                ["git", "-C", str(repo), "init", "-q"],
                check=True,
            )
            subprocess.run(
                [
                    "git",
                    "-C",
                    str(repo),
                    "config",
                    "user.email",
                    "test@example.invalid",
                ],
                check=True,
            )
            subprocess.run(
                ["git", "-C", str(repo), "config", "user.name", "test"],
                check=True,
            )
            subprocess.run(
                ["git", "-C", str(repo), "add", "."],
                check=True,
            )
            subprocess.run(
                ["git", "-C", str(repo), "commit", "-qm", "baseline"],
                check=True,
            )
            head = subprocess.run(
                ["git", "-C", str(repo), "rev-parse", "HEAD"],
                text=True,
                stdout=subprocess.PIPE,
                check=True,
            ).stdout.strip()
            result = subject._verify_soza_baseline(repo, head)
        self.assertEqual(head, result["head"])
        self.assertEqual(set(subject.BASELINE_PATHS), set(result["objects"]))
        self.assertTrue(result["worktreeCleanWithinBoundary"])

    def test_output_inside_soza_repo_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            soza = root / "soza"
            soza.mkdir()
            with self.assertRaisesRegex(ValueError, "SEI repository配下"):
                subject._prepare_output(soza / "audit.json", soza)


if __name__ == "__main__":
    unittest.main()
