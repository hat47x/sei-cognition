import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BASE_TEST = load_module(
    "runtime_exchange_base_evidence_test_fixture",
    HERE / "test_verify_runtime_version_exchange_evidence.py",
)
PROVENANCE = load_module(
    "verify_runtime_version_exchange_provenance",
    HERE / "verify_runtime_version_exchange_provenance.py",
)


class RuntimeVersionExchangeProvenanceVerifierTest(unittest.TestCase):
    def make_evidence(self, root: Path) -> None:
        fixture = BASE_TEST.EvidenceVerifierTest()
        fixture.make_evidence(root)

        manifest = PROVENANCE.core._load_manifest(
            HERE / "runtime_version_exchange_artifacts.json"
        )
        preflight = {
            "schema": PROVENANCE.EXPECTED_PREFLIGHT_SCHEMA,
            "result": "ready",
            "blockers": [],
            "fixedArtifacts": PROVENANCE._expected_fixed_artifacts(manifest),
            "pinnedSourceIdentity": PROVENANCE._expected_source_identity(),
            "checks": [],
            "stopLine": (
                "preflight ready != actual runtime A/B inference PASS "
                "!= runtime-version-exchange Scoped Executable Evidence"
            ),
        }
        (root / "runtime-exchange-preflight.json").write_text(
            json.dumps(preflight),
            encoding="utf-8",
        )

        runner_path = root / "runtime-exchange-runner-observation.json"
        runner = json.loads(runner_path.read_text(encoding="utf-8"))
        runner["preflightResult"] = "ready"
        runner["evidenceDirectoryCreatedBy"] = (
            PROVENANCE.EVIDENCE_DIRECTORY_CREATED_BY_STRICT
        )
        runner_path.write_text(json.dumps(runner), encoding="utf-8")

    def report(self, mutate=None):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "evidence"
            self.make_evidence(root)
            if mutate is not None:
                mutate(root)
            return PROVENANCE.verify_run_provenance(
                root,
                manifest_path=HERE / "runtime_version_exchange_artifacts.json",
            )

    def test_complete_direct_bundle_fixture_is_ready_to_review(self):
        report = self.report()
        self.assertEqual("ready-to-review", report["result"], report["blockers"])
        self.assertEqual("ready-to-review", report["coreEvidenceResult"])

    def test_missing_preflight_report_is_rejected(self):
        report = self.report(
            lambda root: (root / "runtime-exchange-preflight.json").unlink()
        )
        self.assertIn(
            "provenance.file.runtime-exchange-preflight.json",
            report["blockers"],
        )

    def test_preflight_blocked_state_is_rejected(self):
        def mutate(root: Path) -> None:
            path = root / "runtime-exchange-preflight.json"
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["result"] = "blocked"
            payload["blockers"] = ["port.ollama"]
            path.write_text(json.dumps(payload), encoding="utf-8")

        report = self.report(mutate)
        self.assertIn("provenance.preflight.result", report["blockers"])
        self.assertIn("provenance.runner.preflight-result", report["blockers"])

    def test_preflight_fixed_artifact_drift_is_rejected(self):
        def mutate(root: Path) -> None:
            path = root / "runtime-exchange-preflight.json"
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["fixedArtifacts"]["runtimeA"]["sha256"] = "0" * 64
            path.write_text(json.dumps(payload), encoding="utf-8")

        report = self.report(mutate)
        self.assertIn("provenance.preflight.fixed-artifacts", report["blockers"])

    def test_preflight_source_identity_drift_is_rejected(self):
        def mutate(root: Path) -> None:
            path = root / "runtime-exchange-preflight.json"
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["pinnedSourceIdentity"]["runtimeSurfaceTree"] = "0" * 40
            path.write_text(json.dumps(payload), encoding="utf-8")

        report = self.report(mutate)
        self.assertIn("provenance.preflight.source-identity", report["blockers"])

    def test_runner_preflight_result_mismatch_is_rejected(self):
        def mutate(root: Path) -> None:
            path = root / "runtime-exchange-runner-observation.json"
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["preflightResult"] = "blocked"
            path.write_text(json.dumps(payload), encoding="utf-8")

        report = self.report(mutate)
        self.assertIn("provenance.runner.preflight-result", report["blockers"])

    def test_missing_evidence_directory_creator_is_rejected(self):
        def mutate(root: Path) -> None:
            path = root / "runtime-exchange-runner-observation.json"
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload.pop("evidenceDirectoryCreatedBy")
            path.write_text(json.dumps(payload), encoding="utf-8")

        report = self.report(mutate)
        self.assertIn(
            "provenance.runner.evidence-directory-created-by",
            report["blockers"],
        )

    def test_unknown_evidence_directory_creator_is_rejected(self):
        def mutate(root: Path) -> None:
            path = root / "runtime-exchange-runner-observation.json"
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["evidenceDirectoryCreatedBy"] = "unknown-writer"
            path.write_text(json.dumps(payload), encoding="utf-8")

        report = self.report(mutate)
        self.assertIn(
            "provenance.runner.evidence-directory-created-by",
            report["blockers"],
        )

    def test_non_string_evidence_directory_creator_is_rejected(self):
        def mutate(root: Path) -> None:
            path = root / "runtime-exchange-runner-observation.json"
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["evidenceDirectoryCreatedBy"] = ["strict-entrypoint"]
            path.write_text(json.dumps(payload), encoding="utf-8")

        report = self.report(mutate)
        self.assertIn(
            "provenance.runner.evidence-directory-created-by",
            report["blockers"],
        )

    def test_complete_run_cannot_claim_failure_directory_creator(self):
        def mutate(root: Path) -> None:
            path = root / "runtime-exchange-runner-observation.json"
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["evidenceDirectoryCreatedBy"] = (
                PROVENANCE.EVIDENCE_DIRECTORY_CREATED_BY_FAILURE
            )
            path.write_text(json.dumps(payload), encoding="utf-8")

        report = self.report(mutate)
        self.assertIn(
            "provenance.runner.complete-run-directory-creator",
            report["blockers"],
        )

    def test_unknown_source_preparation_is_rejected(self):
        def mutate(root: Path) -> None:
            path = root / "runtime-exchange-runner-observation.json"
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["sourcePreparation"] = "working-tree-direct"
            path.write_text(json.dumps(payload), encoding="utf-8")

        report = self.report(mutate)
        self.assertIn("provenance.runner.source-preparation", report["blockers"])

    def test_non_string_source_preparation_is_rejected(self):
        def mutate(root: Path) -> None:
            path = root / "runtime-exchange-runner-observation.json"
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["sourcePreparation"] = [PROVENANCE.SOURCE_PREPARATION_DIRECT]
            path.write_text(json.dumps(payload), encoding="utf-8")

        report = self.report(mutate)
        self.assertIn("provenance.runner.source-preparation", report["blockers"])

    def test_checkout_preparation_requires_source_export(self):
        def mutate(root: Path) -> None:
            path = root / "runtime-exchange-runner-observation.json"
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["sourcePreparation"] = PROVENANCE.SOURCE_PREPARATION_CHECKOUT
            path.write_text(json.dumps(payload), encoding="utf-8")

        report = self.report(mutate)
        self.assertIn(
            "provenance.file.runtime-exchange-source-export.json",
            report["blockers"],
        )

    def test_checkout_preparation_accepts_matching_source_export(self):
        def mutate(root: Path) -> None:
            runner_path = root / "runtime-exchange-runner-observation.json"
            runner = json.loads(runner_path.read_text(encoding="utf-8"))
            runner["sourcePreparation"] = PROVENANCE.SOURCE_PREPARATION_CHECKOUT
            runner_path.write_text(json.dumps(runner), encoding="utf-8")

            source = json.loads(
                (root / "kj-atlas-source-identity.json").read_text(encoding="utf-8")
            )
            export = {
                "schema": PROVENANCE.EXPECTED_SOURCE_EXPORT_SCHEMA,
                "sourceAcquisition": PROVENANCE.EXPECTED_SOURCE_EXPORT_ACQUISITION,
                "checkoutRepository": "/tmp/kj-atlas",
                "sourceCommit": PROVENANCE.core.EXPECTED_SOURCE_COMMIT,
                "outputDirectory": "/tmp/exported-backend",
                "verification": source,
            }
            (root / "runtime-exchange-source-export.json").write_text(
                json.dumps(export),
                encoding="utf-8",
            )

        report = self.report(mutate)
        self.assertEqual("ready-to-review", report["result"], report["blockers"])

    def test_checkout_source_export_verification_drift_is_rejected(self):
        def mutate(root: Path) -> None:
            runner_path = root / "runtime-exchange-runner-observation.json"
            runner = json.loads(runner_path.read_text(encoding="utf-8"))
            runner["sourcePreparation"] = PROVENANCE.SOURCE_PREPARATION_CHECKOUT
            runner_path.write_text(json.dumps(runner), encoding="utf-8")

            source = json.loads(
                (root / "kj-atlas-source-identity.json").read_text(encoding="utf-8")
            )
            source["runtimeSurfaceTree"] = "0" * 40
            export = {
                "schema": PROVENANCE.EXPECTED_SOURCE_EXPORT_SCHEMA,
                "sourceAcquisition": PROVENANCE.EXPECTED_SOURCE_EXPORT_ACQUISITION,
                "sourceCommit": PROVENANCE.core.EXPECTED_SOURCE_COMMIT,
                "verification": source,
            }
            (root / "runtime-exchange-source-export.json").write_text(
                json.dumps(export),
                encoding="utf-8",
            )

        report = self.report(mutate)
        self.assertIn(
            "provenance.source-export.verification-copy",
            report["blockers"],
        )

    def test_direct_bundle_rejects_checkout_source_export_file(self):
        def mutate(root: Path) -> None:
            (root / "runtime-exchange-source-export.json").write_text(
                json.dumps({"schema": PROVENANCE.EXPECTED_SOURCE_EXPORT_SCHEMA}),
                encoding="utf-8",
            )

        report = self.report(mutate)
        self.assertIn(
            "provenance.source-export.direct-mode-absence",
            report["blockers"],
        )


if __name__ == "__main__":
    unittest.main()
