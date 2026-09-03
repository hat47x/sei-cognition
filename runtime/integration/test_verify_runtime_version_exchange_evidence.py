import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "verify_runtime_version_exchange_evidence",
    HERE / "verify_runtime_version_exchange_evidence.py",
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)

RUNTIME_A_SHA = "0fd1dece38a1c6242e8013ce20b597345c5de072ae6b320160edb0e729ef1de1"
RUNTIME_B_SHA = "c620917a71e146ab3a7f893084f066069c4c65d144ef8379a91c3cbe8b27de8f"
MODEL_SHA = "a8b0c51577010a279d933d14c2a8ab4b268079d44c5c8830c0a93900f1827c67"
PROMPT_SHA = "1" * 64


class EvidenceVerifierTest(unittest.TestCase):
    def make_evidence(self, root: Path) -> None:
        source = {
            "schema": "soza.kj-atlas-runtime-source-identity/v1",
            "verified": True,
            "sourceMode": "verified-runtime-bundle",
            "repository": "hat47x/kj-atlas",
            "sourceCommit": MODULE.EXPECTED_SOURCE_COMMIT,
            "pinnedBackendTree": MODULE.EXPECTED_PARENT_BACKEND_TREE,
            "runtimeSurfaceTree": MODULE.EXPECTED_RUNTIME_SURFACE_TREE,
            "verificationBasis": MODULE.EXPECTED_SOURCE_VERIFICATION_BASIS,
        }
        identity = {
            "schema": MODULE.EXPECTED_IDENTITY_SCHEMA,
            "executionId": "fixture",
            "executionSurface": "repository-local-harness",
            "repositoryCommit": "f" * 40,
            "methodSourceCommit": MODULE.EXPECTED_SOURCE_COMMIT,
            "methodSource": source,
            "executionHost": {"os": "linux", "arch": "amd64"},
            "runtimeA": {
                "name": "ollama",
                "version": "0.32.13",
                "archiveSha256": RUNTIME_A_SHA,
                "archiveAcquisition": "prepositioned",
            },
            "runtimeB": {
                "name": "ollama",
                "version": "0.32.14",
                "archiveSha256": RUNTIME_B_SHA,
                "archiveAcquisition": "prepositioned",
            },
            "model": {
                "name": "qwen2.5:0.5b",
                "expectedDigest": MODEL_SHA,
                "storageMode": "prepositioned",
            },
            "qualityJudgement": "not_evaluated",
        }
        request = {
            "cards": [
                {
                    "id": "c-remote-time",
                    "text": MODULE.EXPECTED_CARD_TEXT["c-remote-time"],
                    "textReviewed": True,
                },
                {
                    "id": "c-remote-load",
                    "text": MODULE.EXPECTED_CARD_TEXT["c-remote-load"],
                    "textReviewed": True,
                },
                {
                    "id": "c-held",
                    "text": MODULE.EXPECTED_CARD_TEXT["c-held"],
                    "textReviewed": True,
                },
            ],
            "doc": {
                "cards": [
                    {"id": "c-remote-time"},
                    {"id": "c-remote-load"},
                    {"id": "c-held", "holdState": "held"},
                ]
            },
        }
        runner_log = (
            b"fixture harness output\n"
            b"Runtime version exchange probe completed successfully.\n"
        )
        import hashlib

        runner = {
            "schema": MODULE.EXPECTED_RUNNER_SCHEMA,
            "completed": True,
            "exitCode": 0,
            "sourcePreparation": "verified-runtime-bundle",
            "combinedOutputSha256": hashlib.sha256(runner_log).hexdigest(),
            "combinedOutputBytes": len(runner_log),
            "qualityJudgement": "not_evaluated",
        }
        model_evidence = {
            "schema": MODULE.EXPECTED_ADAPTER_SCHEMA,
            "adapter_role": "integration-only",
            "task": MODULE.EXPECTED_TASK,
            "model": "qwen2.5:0.5b",
            "prompt_sha256": PROMPT_SHA,
            "ollama_done": True,
            "ollama_done_reason": "stop",
            "prompt_eval_count": 196,
            "eval_count": 79,
        }
        result = {
            "groups": [
                {
                    "label": "fixture",
                    "cardIds": ["c-remote-time", "c-remote-load"],
                }
            ],
            "excludedCardIds": ["c-held"],
            "truncated": False,
        }
        tags = {"models": [{"name": "qwen2.5:0.5b", "digest": MODEL_SHA}]}

        root.mkdir()
        for name, payload in {
            "runtime-exchange-identity.json": identity,
            "kj-atlas-source-identity.json": source,
            "kj-atlas-runtime-exchange-request.json": request,
            "runtime-exchange-runner-observation.json": runner,
            "runtime-exchange-a-tags.json": tags,
            "runtime-exchange-b-tags.json": tags,
            "runtime-exchange-a-evidence.json": model_evidence,
            "runtime-exchange-b-evidence.json": model_evidence,
            "runtime-exchange-a-result.json": result,
            "runtime-exchange-b-result.json": result,
        }.items():
            (root / name).write_text(json.dumps(payload), encoding="utf-8")
        (root / "runtime-exchange-runner.log").write_bytes(runner_log)
        for name, text in {
            "runtime-exchange-a-version.txt": "ollama version is 0.32.13\n",
            "runtime-exchange-b-version.txt": "ollama version is 0.32.14\n",
            "runtime-exchange-a-archive-sha256.txt": RUNTIME_A_SHA + "\n",
            "runtime-exchange-b-archive-sha256.txt": RUNTIME_B_SHA + "\n",
            "runtime-exchange-a-model-id.txt": MODEL_SHA + "\n",
            "runtime-exchange-b-model-id.txt": MODEL_SHA + "\n",
        }.items():
            (root / name).write_text(text, encoding="utf-8")

    def report(self, mutate=None):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "evidence"
            self.make_evidence(root)
            if mutate:
                mutate(root)
            return MODULE.verify_evidence_directory(
                root,
                manifest_path=HERE / "runtime_version_exchange_artifacts.json",
            )

    def test_complete_fixture_is_ready_to_review(self):
        report = self.report()
        self.assertEqual("ready-to-review", report["result"], report["blockers"])

    def test_missing_file_is_not_sufficient(self):
        report = self.report(lambda root: (root / "runtime-exchange-b-result.json").unlink())
        self.assertEqual("not-sufficient", report["result"])
        self.assertIn("file.runtime-exchange-b-result.json", report["blockers"])

    def test_non_strict_source_is_rejected(self):
        def mutate(root):
            path = root / "kj-atlas-source-identity.json"
            payload = json.loads(path.read_text())
            payload["sourceMode"] = "git-checkout"
            path.write_text(json.dumps(payload))

        report = self.report(mutate)
        self.assertIn("source.mode", report["blockers"])

    def test_non_string_runtime_archive_acquisition_is_rejected(self):
        def mutate(root):
            path = root / "runtime-exchange-identity.json"
            payload = json.loads(path.read_text())
            payload["runtimeA"]["archiveAcquisition"] = ["prepositioned"]
            path.write_text(json.dumps(payload))

        report = self.report(mutate)
        self.assertIn("identity.runtimeA", report["blockers"])

    def test_non_string_model_storage_mode_is_rejected(self):
        def mutate(root):
            path = root / "runtime-exchange-identity.json"
            payload = json.loads(path.read_text())
            payload["model"]["storageMode"] = ["prepositioned"]
            path.write_text(json.dumps(payload))

        report = self.report(mutate)
        self.assertIn("identity.model", report["blockers"])

    def test_completion_marker_missing_is_rejected(self):
        def mutate(root):
            import hashlib

            path = root / "runtime-exchange-runner.log"
            data = b"harness stopped before completion\n"
            path.write_bytes(data)
            observation_path = root / "runtime-exchange-runner-observation.json"
            observation = json.loads(observation_path.read_text())
            observation["combinedOutputSha256"] = hashlib.sha256(data).hexdigest()
            observation["combinedOutputBytes"] = len(data)
            observation_path.write_text(json.dumps(observation))

        report = self.report(mutate)
        self.assertIn("runner.completion-marker", report["blockers"])

    def test_runner_log_tamper_is_rejected(self):
        report = self.report(
            lambda root: (root / "runtime-exchange-runner.log").write_bytes(b"tampered\n")
        )
        self.assertIn("runner.log-sha256", report["blockers"])

    def test_runtime_digest_drift_is_rejected(self):
        report = self.report(
            lambda root: (root / "runtime-exchange-a-archive-sha256.txt").write_text(
                "0" * 64 + "\n"
            )
        )
        self.assertIn("runtime.a.archive-sha256", report["blockers"])

    def test_model_digest_drift_is_rejected(self):
        report = self.report(
            lambda root: (root / "runtime-exchange-b-model-id.txt").write_text(
                "0" * 64 + "\n"
            )
        )
        self.assertIn("model.b.id", report["blockers"])
        self.assertIn("model.same-artifact", report["blockers"])

    def test_prompt_drift_is_rejected(self):
        def mutate(root):
            path = root / "runtime-exchange-b-evidence.json"
            payload = json.loads(path.read_text())
            payload["prompt_sha256"] = "3" * 64
            path.write_text(json.dumps(payload))

        report = self.report(mutate)
        self.assertIn("inference.same-prompt", report["blockers"])

    def test_zero_eval_count_is_rejected(self):
        def mutate(root):
            path = root / "runtime-exchange-a-evidence.json"
            payload = json.loads(path.read_text())
            payload["eval_count"] = 0
            path.write_text(json.dumps(payload))

        report = self.report(mutate)
        self.assertIn("inference.a.eval_count", report["blockers"])

    def test_quality_promotion_is_rejected(self):
        def mutate(root):
            path = root / "runtime-exchange-identity.json"
            payload = json.loads(path.read_text())
            payload["qualityJudgement"] = "satisfied"
            path.write_text(json.dumps(payload))

        report = self.report(mutate)
        self.assertIn("identity.quality-boundary", report["blockers"])

    def test_runner_failure_is_rejected(self):
        def mutate(root):
            path = root / "runtime-exchange-runner-observation.json"
            payload = json.loads(path.read_text())
            payload["completed"] = False
            payload["exitCode"] = 1
            path.write_text(json.dumps(payload))

        report = self.report(mutate)
        self.assertIn("runner.exit-code", report["blockers"])

    def test_symlink_evidence_file_is_rejected(self):
        def mutate(root):
            target = root / "external.txt"
            target.write_text(MODEL_SHA + "\n")
            path = root / "runtime-exchange-a-model-id.txt"
            path.unlink()
            path.symlink_to(target)

        report = self.report(mutate)
        self.assertIn("file.runtime-exchange-a-model-id.txt", report["blockers"])


if __name__ == "__main__":
    unittest.main()
