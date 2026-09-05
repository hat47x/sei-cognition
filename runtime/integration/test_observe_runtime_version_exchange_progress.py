import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import observe_runtime_version_exchange_progress as subject


PROMPT_SHA = "a" * 64


class RuntimeVersionExchangeProgressObserverTest(unittest.TestCase):
    def write_json(self, root: Path, name: str, payload: dict) -> None:
        (root / name).write_text(
            json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    def write_ready_preflight(self, root: Path) -> None:
        self.write_json(
            root,
            "runtime-exchange-preflight.json",
            {
                "schema": subject.PREFLIGHT_SCHEMA,
                "result": "ready",
                "blockers": [],
            },
        )

    def write_identity(self, root: Path) -> None:
        manifest = subject.core._load_manifest()
        runtime_a = manifest["runtimeArchives"]["a"]
        runtime_b = manifest["runtimeArchives"]["b"]
        model = manifest["model"]
        self.write_json(
            root,
            "runtime-exchange-identity.json",
            {
                "schema": subject.IDENTITY_SCHEMA,
                "runtimeA": {
                    "version": runtime_a["version"],
                    "archiveSha256": runtime_a["sha256"],
                },
                "runtimeB": {
                    "version": runtime_b["version"],
                    "archiveSha256": runtime_b["sha256"],
                },
                "model": {
                    "name": model["name"],
                    "expectedDigest": model["sha256"],
                },
                "qualityJudgement": "not_evaluated",
            },
        )

    def write_archive_digest(self, root: Path, label: str, *, valid: bool = True) -> None:
        manifest = subject.core._load_manifest()
        digest = manifest["runtimeArchives"][label]["sha256"] if valid else "0" * 64
        (root / f"runtime-exchange-{label}-archive-sha256.txt").write_text(
            digest + "\n", encoding="utf-8"
        )

    def write_version(self, root: Path, label: str) -> None:
        manifest = subject.core._load_manifest()
        version = manifest["runtimeArchives"][label]["version"]
        (root / f"runtime-exchange-{label}-version.txt").write_text(
            f"ollama version is {version}\n", encoding="utf-8"
        )

    def write_tags(self, root: Path, label: str) -> None:
        manifest = subject.core._load_manifest()
        model = manifest["model"]
        self.write_json(
            root,
            f"runtime-exchange-{label}-tags.json",
            {"models": [{"name": model["name"], "digest": model["sha256"]}]},
        )

    def write_inference(self, root: Path, label: str, *, prompt_sha: str = PROMPT_SHA) -> None:
        model = subject.core._load_manifest()["model"]
        self.write_json(
            root,
            f"runtime-exchange-{label}-evidence.json",
            {
                "schema": subject.core.EXPECTED_ADAPTER_SCHEMA,
                "model": model["name"],
                "task": subject.core.EXPECTED_TASK,
                "ollama_done": True,
                "prompt_eval_count": 5,
                "eval_count": 3,
                "prompt_sha256": prompt_sha,
            },
        )
        self.write_json(
            root,
            f"runtime-exchange-{label}-result.json",
            {
                "groups": [{"title": "remote work", "cardIds": ["c-remote-time"]}],
                "excludedCardIds": [subject.core.EXPECTED_HELD_CARD],
                "truncated": False,
            },
        )

    def write_runner(self, root: Path, *, completed: bool, exit_code: int) -> None:
        self.write_json(
            root,
            "runtime-exchange-runner-observation.json",
            {
                "schema": subject.RUNNER_SCHEMA,
                "completed": completed,
                "exitCode": exit_code,
            },
        )

    def write_through_a_inference(self, root: Path) -> None:
        self.write_ready_preflight(root)
        self.write_identity(root)
        self.write_archive_digest(root, "a")
        self.write_archive_digest(root, "b")
        self.write_version(root, "a")
        self.write_tags(root, "a")
        self.write_inference(root, "a")

    def write_complete(self, root: Path) -> None:
        self.write_through_a_inference(root)
        self.write_version(root, "b")
        self.write_tags(root, "b")
        self.write_inference(root, "b")

    def test_blocked_preflight_is_not_promoted_to_strict_progress(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_json(
                root,
                "runtime-exchange-preflight.json",
                {
                    "schema": subject.PREFLIGHT_SCHEMA,
                    "result": "blocked",
                    "blockers": ["runtime.a.archive"],
                },
            )
            self.write_json(
                root,
                "runtime-exchange-preflight-observation.json",
                {
                    "schema": subject.PREFLIGHT_OBSERVATION_SCHEMA,
                    "strictStarted": False,
                },
            )
            report = subject.observe_progress(root)

        self.assertEqual("preflight_blocked", report["state"])
        self.assertIsNone(report["lastObservedMilestone"])
        self.assertEqual("preflight_ready", report["nextUnobservedMilestone"])
        self.assertIn("開始されていません", report["boundary"])

    def test_strict_failure_after_a_inference_reports_only_observed_boundary(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_through_a_inference(root)
            self.write_runner(root, completed=False, exit_code=1)
            report = subject.observe_progress(root)

        self.assertEqual("partial_after_strict_failure", report["state"])
        self.assertEqual("runtime_a_inference_observed", report["lastObservedMilestone"])
        self.assertEqual("runtime_b_version_observed", report["nextUnobservedMilestone"])
        self.assertTrue(report["monotonicEvidenceOrder"])
        self.assertIn("細かいfailure原因", report["boundary"])

    def test_complete_actual_milestones_require_real_harness_file_names(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_complete(root)
            self.write_runner(root, completed=True, exit_code=0)
            report = subject.observe_progress(root)

        self.assertEqual("all_observed_milestones_completed", report["state"])
        self.assertEqual("cross_runtime_prompt_identity_observed", report["lastObservedMilestone"])
        self.assertIsNone(report["nextUnobservedMilestone"])
        self.assertTrue(report["monotonicEvidenceOrder"])
        self.assertTrue(all(item["observed"] for item in report["milestones"]))

    def test_later_evidence_without_required_prefix_is_inconsistent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_ready_preflight(root)
            self.write_identity(root)
            # A archive digestを欠落させたまま、後段のB archive digestを置く。
            self.write_archive_digest(root, "b")
            self.write_runner(root, completed=False, exit_code=1)
            report = subject.observe_progress(root)

        self.assertEqual("inconsistent_evidence_order", report["state"])
        self.assertEqual("fixed_identity_recorded", report["lastObservedMilestone"])
        self.assertEqual("runtime_a_archive_digest_observed", report["nextUnobservedMilestone"])
        self.assertIn(
            "runtime_b_archive_digest_observed",
            report["unexpectedLaterObservedMilestones"],
        )

    def test_wrong_actual_digest_is_not_observed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_ready_preflight(root)
            self.write_identity(root)
            self.write_archive_digest(root, "a", valid=False)
            self.write_runner(root, completed=False, exit_code=1)
            report = subject.observe_progress(root)

        self.assertEqual("partial_after_strict_failure", report["state"])
        self.assertEqual("fixed_identity_recorded", report["lastObservedMilestone"])
        self.assertEqual("runtime_a_archive_digest_observed", report["nextUnobservedMilestone"])

    def test_corrupt_inference_json_is_not_promoted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_ready_preflight(root)
            self.write_identity(root)
            self.write_archive_digest(root, "a")
            self.write_archive_digest(root, "b")
            self.write_version(root, "a")
            self.write_tags(root, "a")
            (root / "runtime-exchange-a-evidence.json").write_text("{broken", encoding="utf-8")
            self.write_json(
                root,
                "runtime-exchange-a-result.json",
                {
                    "groups": [{"title": "x", "cardIds": ["c-remote-time"]}],
                    "excludedCardIds": [subject.core.EXPECTED_HELD_CARD],
                    "truncated": False,
                },
            )
            self.write_runner(root, completed=False, exit_code=1)
            report = subject.observe_progress(root)

        self.assertEqual("runtime_a_model_identity_observed", report["lastObservedMilestone"])
        self.assertEqual("runtime_a_inference_observed", report["nextUnobservedMilestone"])

    def test_cli_rejects_progress_output_inside_evidence_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "evidence"
            root.mkdir()
            output = root / "progress.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(Path(subject.__file__)),
                    "--evidence-dir",
                    str(root),
                    "--output",
                    str(output),
                ],
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(2, completed.returncode)
        self.assertIn("must not be inside the Evidence directory", completed.stderr)


if __name__ == "__main__":
    unittest.main()
