#!/usr/bin/env python3
from __future__ import annotations

import json
import unittest
from pathlib import Path

import check_release_candidate as candidate


ROOT = Path(__file__).resolve().parents[1]


class ReleaseCandidateLocalExecutionTest(unittest.TestCase):
    def test_current_candidate_policies_do_not_require_github_actions_workflows(self):
        for version in ("0.1.0", "0.2.0"):
            with self.subTest(version=version):
                config = json.loads(
                    (ROOT / "release" / f"v{version}" / "release-candidate.json").read_text(encoding="utf-8")
                )
                workflow_paths = [
                    path
                    for path in config["required_paths"]
                    if path == ".github" or path.startswith(".github/")
                ]
                self.assertEqual([], workflow_paths)

    def test_version_policy_anchors_do_not_require_automation_provider_files(self):
        for version, policy in candidate.VERSION_POLICIES.items():
            with self.subTest(version=version):
                automation_paths = [
                    path
                    for path in policy.required_path_anchors
                    if path == ".github" or path.startswith(".github/")
                ]
                self.assertEqual([], automation_paths)

    def test_v020_keeps_repository_local_candidate_checker_as_required_path(self):
        config = json.loads(
            (ROOT / "release" / "v0.2.0" / "release-candidate.json").read_text(encoding="utf-8")
        )
        self.assertIn("tools/check_release_candidate.py", config["required_paths"])

    def test_required_gate_semantics_are_unchanged(self):
        for version, policy in candidate.VERSION_POLICIES.items():
            with self.subTest(version=version):
                config = json.loads(
                    (ROOT / "release" / f"v{version}" / "release-candidate.json").read_text(encoding="utf-8")
                )
                self.assertEqual(policy.required_gates, frozenset(config["required_gates"]))


if __name__ == "__main__":
    unittest.main()
