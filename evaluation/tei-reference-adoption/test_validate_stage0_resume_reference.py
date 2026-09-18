#!/usr/bin/env python3
"""Self-tests for ISSUE-000079 Stage 0 source freeze validator."""

from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("validate_stage0_resume_reference.py")
SPEC = importlib.util.spec_from_file_location("validate_stage0_resume_reference", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Stage0ResumeReferenceValidatorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.repo_root = Path(__file__).resolve().parents[2]
        cls.manifest_path = Path(__file__).with_name(
            "stage0_resume_review_source_freeze_v1.json"
        )
        cls.manifest = MODULE.load_json(cls.manifest_path)

    def test_current_repository_manifest_validates(self) -> None:
        result = MODULE.validate_manifest(self.manifest, self.repo_root)
        self.assertTrue(result["valid"], result["errors"])
        self.assertEqual([], result["errors"])

    def test_oracle_cannot_become_reference_input(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["input_json_pointers"].append(
            "/conditions/C_sei_resume/surface_text"
        )
        result = MODULE.validate_manifest(manifest, self.repo_root)
        self.assertFalse(result["valid"])
        self.assertTrue(
            any("input_json_pointers" in error or "overlap" in error for error in result["errors"])
        )

    def test_fixture_byte_change_breaks_source_freeze(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = self.repo_root / self.manifest["source_authority"]["fixture_path"]
            target = root / self.manifest["source_authority"]["fixture_path"]
            target.parent.mkdir(parents=True)
            target.write_bytes(source.read_bytes() + b"\n")
            result = MODULE.validate_manifest(self.manifest, root)
            self.assertFalse(result["valid"])
            self.assertTrue(any("SHA-1" in error for error in result["errors"]))
            self.assertTrue(any("SHA-256" in error for error in result["errors"]))

    def test_missing_decision_basis_reference_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = self.repo_root / self.manifest["source_authority"]["fixture_path"]
            fixture = json.loads(source.read_text(encoding="utf-8"))
            decision = next(
                item for item in fixture["scenario"]["phase_1"]
                if item["role"] == "decision"
            )
            decision["basis_refs"] = ["missing-observation"]
            payload = (json.dumps(fixture, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")
            target = root / self.manifest["source_authority"]["fixture_path"]
            target.parent.mkdir(parents=True)
            target.write_bytes(payload)

            manifest = copy.deepcopy(self.manifest)
            manifest["source_authority"]["git_blob_sha1"] = MODULE.git_blob_sha1(payload)
            manifest["source_authority"]["content_sha256"] = MODULE.sha256(payload)
            manifest["source_authority"]["byte_length"] = len(payload)
            result = MODULE.validate_manifest(manifest, root)
            self.assertFalse(result["valid"])
            self.assertTrue(any("missing phase_1 ref" in error for error in result["errors"]))

    def test_recommendation_reference_must_stay_recommendation(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = self.repo_root / self.manifest["source_authority"]["fixture_path"]
            fixture = json.loads(source.read_text(encoding="utf-8"))
            decision = next(
                item for item in fixture["scenario"]["phase_1"]
                if item["role"] == "decision"
            )
            decision["recommendation_refs"] = ["obs-a-timeout"]
            payload = (json.dumps(fixture, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")
            target = root / self.manifest["source_authority"]["fixture_path"]
            target.parent.mkdir(parents=True)
            target.write_bytes(payload)

            manifest = copy.deepcopy(self.manifest)
            manifest["source_authority"]["git_blob_sha1"] = MODULE.git_blob_sha1(payload)
            manifest["source_authority"]["content_sha256"] = MODULE.sha256(payload)
            manifest["source_authority"]["byte_length"] = len(payload)
            result = MODULE.validate_manifest(manifest, root)
            self.assertFalse(result["valid"])
            self.assertTrue(any("recommendation_refs" in error for error in result["errors"]))

    def test_new_application_pattern_kind_is_not_authorized(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["tei_reference_context"]["new_pattern_kind_added_for_stage0"] = True
        result = MODULE.validate_manifest(manifest, self.repo_root)
        self.assertFalse(result["valid"])
        self.assertTrue(any("new TEI Application Pattern kind" in error for error in result["errors"]))


if __name__ == "__main__":
    unittest.main()
