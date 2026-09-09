#!/usr/bin/env python3
"""Self-tests for check_representation_profiles.py using only the Python stdlib."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

CHECKER_PATH = Path(__file__).with_name("check_representation_profiles.py")
SPEC = importlib.util.spec_from_file_location("check_representation_profiles", CHECKER_PATH)
assert SPEC is not None and SPEC.loader is not None
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)

JCS_PROFILE = "soza.jcs+sha256/v1alpha1"
RAW_PROFILE = "soza.raw-bytes+sha256/v1alpha1"
UNKNOWN_PROFILE = "example.unknown/v1"


class RepresentationProfileCheckerTest(unittest.TestCase):
    def make_temp_dir(self) -> Path:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        return Path(temp_dir.name)

    def write_json(self, root: Path, name: str, value: dict) -> Path:
        path = root / name
        path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
        return path

    def minimal_jcs_fixture(self) -> dict:
        canonical = '{"a":1}'
        nfc = '{"s":"é"}'
        nfd = '{"s":"é"}'
        return {
            "profile_id": JCS_PROFILE,
            "digest_algorithm": "sha256",
            "cases": [
                {
                    "id": "JCS-001-basic",
                    "expect": "verified",
                    "expected_canonical": canonical,
                    "expected_digest": checker.digest(canonical.encode("utf-8")),
                },
                {
                    "id": "JCS-003-duplicate-key",
                    "expect": "invalid_representation",
                    "input": '{"a":1,"a":2}',
                },
                {
                    "id": "JCS-004-unsafe-large-integer",
                    "expect": "invalid_semantic_number",
                    "input": '{"n":9007199254740993}',
                },
                {
                    "id": "JCS-005-unicode-nfc",
                    "expect": "verified",
                    "expected_canonical": nfc,
                    "expected_digest": checker.digest(nfc.encode("utf-8")),
                },
                {
                    "id": "JCS-006-unicode-nfd",
                    "expect": "verified",
                    "expected_canonical": nfd,
                    "expected_digest": checker.digest(nfd.encode("utf-8")),
                },
            ],
        }

    def test_digest_has_stable_sha256_shape_and_value(self) -> None:
        self.assertEqual(
            "sha256:ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
            checker.digest(b"abc"),
        )

    def test_profile_docs_require_id_and_natural_japanese_review(self) -> None:
        root = self.make_temp_dir()
        good = root / "jcs.md"
        good.write_text(f"{JCS_PROFILE}\nNatural Japanese review\n", encoding="utf-8")
        broken = root / "raw.md"
        broken.write_text("raw profile draft\n", encoding="utf-8")

        errors: list[str] = []
        with (
            mock.patch.object(checker, "ROOT", root),
            mock.patch.object(checker, "PROFILE_DOCS", {JCS_PROFILE: good, RAW_PROFILE: broken}),
        ):
            checker.check_profile_docs(errors)

        self.assertNotIn(f"Profile IDがDefinition本文にありません: {JCS_PROFILE}", errors)
        self.assertIn(f"Profile IDがDefinition本文にありません: {RAW_PROFILE}", errors)
        self.assertIn("自然な日本語レビュー節がありません: raw.md", errors)

    def test_jcs_minimal_required_boundaries_pass(self) -> None:
        root = self.make_temp_dir()
        fixture = self.write_json(root, "jcs.json", self.minimal_jcs_fixture())
        errors: list[str] = []
        with mock.patch.object(checker, "JCS_FIXTURE", fixture):
            verified = checker.check_jcs(errors)

        self.assertEqual(3, verified)
        self.assertEqual([], errors)

    def test_jcs_detects_duplicate_id_and_digest_mismatch(self) -> None:
        root = self.make_temp_dir()
        data = self.minimal_jcs_fixture()
        data["cases"][0]["expected_digest"] = "sha256:" + "0" * 64
        data["cases"].append({"id": "JCS-001-basic", "expect": "invalid_representation"})
        fixture = self.write_json(root, "jcs-broken.json", data)
        errors: list[str] = []
        with mock.patch.object(checker, "JCS_FIXTURE", fixture):
            checker.check_jcs(errors)

        self.assertIn("JCS fixture IDが重複しています。", errors)
        self.assertIn("JCS-001-basic: canonical bytesとexpected_digestが一致しません。", errors)

    def test_raw_fixture_accepts_exact_bytes_digest(self) -> None:
        root = self.make_temp_dir()
        fixture = self.write_json(
            root,
            "raw.json",
            {
                "profile_id": RAW_PROFILE,
                "digest_algorithm": "sha256",
                "cases": [
                    {
                        "id": "RAW-001",
                        "bytes_base64": "YWJj",
                        "expected_digest": checker.digest(b"abc"),
                    }
                ],
            },
        )
        errors: list[str] = []
        with mock.patch.object(checker, "RAW_FIXTURE", fixture):
            checked = checker.check_raw(errors)

        self.assertEqual(1, checked)
        self.assertEqual([], errors)

    def test_raw_fixture_detects_invalid_base64_and_duplicate_id(self) -> None:
        root = self.make_temp_dir()
        fixture = self.write_json(
            root,
            "raw-broken.json",
            {
                "profile_id": RAW_PROFILE,
                "digest_algorithm": "sha256",
                "cases": [
                    {
                        "id": "RAW-001",
                        "bytes_base64": "YWJj",
                        "expected_digest": checker.digest(b"abc"),
                    },
                    {
                        "id": "RAW-001",
                        "bytes_base64": "***not-base64***",
                        "expected_digest": checker.digest(b"ignored"),
                    },
                ],
            },
        )
        errors: list[str] = []
        with mock.patch.object(checker, "RAW_FIXTURE", fixture):
            checked = checker.check_raw(errors)

        self.assertEqual(1, checked)
        self.assertIn("raw-bytes fixture IDが重複しています。", errors)
        self.assertTrue(any(error.startswith("RAW-001: bytes_base64をdecodeできません:") for error in errors))

    def test_resolve_raw_outcome_keeps_three_state_boundary(self) -> None:
        payload = b"abc"
        exact = checker.digest(payload)
        wrong = "sha256:" + "0" * 64
        profiles = {RAW_PROFILE: Path("raw.md"), JCS_PROFILE: Path("jcs.md")}
        with mock.patch.object(checker, "PROFILE_DOCS", profiles):
            self.assertEqual("verified", checker.resolve_raw_outcome(RAW_PROFILE, payload, exact))
            self.assertEqual("failed", checker.resolve_raw_outcome(RAW_PROFILE, payload, wrong))
            self.assertEqual("not_verified", checker.resolve_raw_outcome(UNKNOWN_PROFILE, payload, exact))
            self.assertEqual("not_verified", checker.resolve_raw_outcome(JCS_PROFILE, payload, exact))

    def test_outcome_fixture_covers_verified_failed_and_not_verified(self) -> None:
        root = self.make_temp_dir()
        payload_digest = checker.digest(b"abc")
        fixture = self.write_json(
            root,
            "outcomes.json",
            {
                "cases": [
                    {
                        "id": "OUT-001",
                        "bytes_base64": "YWJj",
                        "profile_id": RAW_PROFILE,
                        "content_digest": payload_digest,
                        "expect_outcome": "verified",
                    },
                    {
                        "id": "OUT-002",
                        "bytes_base64": "YWJj",
                        "profile_id": RAW_PROFILE,
                        "content_digest": "sha256:" + "0" * 64,
                        "expect_outcome": "failed",
                    },
                    {
                        "id": "OUT-003",
                        "bytes_base64": "YWJj",
                        "profile_id": UNKNOWN_PROFILE,
                        "content_digest": payload_digest,
                        "expect_outcome": "not_verified",
                    },
                ]
            },
        )
        errors: list[str] = []
        with (
            mock.patch.object(checker, "OUTCOME_FIXTURE", fixture),
            mock.patch.object(checker, "PROFILE_DOCS", {RAW_PROFILE: Path("raw.md")}),
        ):
            checked = checker.check_outcomes(errors)

        self.assertEqual(3, checked)
        self.assertEqual([], errors)

    def test_outcome_fixture_rejects_missing_state_coverage(self) -> None:
        root = self.make_temp_dir()
        fixture = self.write_json(
            root,
            "outcomes-incomplete.json",
            {
                "cases": [
                    {
                        "id": "OUT-001",
                        "bytes_base64": "YWJj",
                        "profile_id": RAW_PROFILE,
                        "content_digest": checker.digest(b"abc"),
                        "expect_outcome": "verified",
                    }
                ]
            },
        )
        errors: list[str] = []
        with (
            mock.patch.object(checker, "OUTCOME_FIXTURE", fixture),
            mock.patch.object(checker, "PROFILE_DOCS", {RAW_PROFILE: Path("raw.md")}),
        ):
            checker.check_outcomes(errors)

        self.assertIn(
            "verified / failed / not_verifiedの三状態をfixtureで網羅していません。",
            errors,
        )


if __name__ == "__main__":
    unittest.main()
