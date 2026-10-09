import copy
import importlib.util
import json
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "reference_token_fixture", HERE / "reference_token_fixture.py"
)
rtf = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(rtf)

FIXTURE = json.loads((HERE / "fixture.v1.json").read_text(encoding="utf-8"))
TOKENS = json.loads(
    (HERE / "reference_token_fixture.v1.json").read_text(encoding="utf-8")
)


class ReferenceTokenFixtureTest(unittest.TestCase):
    def test_retained_fixture_is_valid(self):
        rtf.validate_reference_token_fixture(
            copy.deepcopy(FIXTURE), copy.deepcopy(TOKENS)
        )

    def test_marker_corruption_is_rejected(self):
        tokens = copy.deepcopy(TOKENS)
        tokens["cases"][0]["marker_positions"][0] += 1
        with self.assertRaises(rtf.ReferenceTokenFixtureError):
            rtf.validate_reference_token_fixture(copy.deepcopy(FIXTURE), tokens)

    def test_fixture_option_drift_is_rejected(self):
        fixture = copy.deepcopy(FIXTURE)
        del fixture["cases"][0]["request"]["questions"]["route"]["criteria"][
            "manual_review"
        ]
        with self.assertRaises(rtf.ReferenceTokenFixtureError):
            rtf.validate_reference_token_fixture(fixture, copy.deepcopy(TOKENS))

    def test_state_or_instruction_drift_is_rejected(self):
        for mutate in ("state", "instructions"):
            fixture = copy.deepcopy(FIXTURE)
            if mutate == "state":
                fixture["cases"][0]["request"]["state"]["retry_count"] = 5
            else:
                fixture["cases"][0]["request"]["questions"]["route"][
                    "instructions"
                ] += " changed"
            with self.assertRaises(rtf.ReferenceTokenFixtureError):
                rtf.validate_reference_token_fixture(
                    fixture, copy.deepcopy(TOKENS)
                )

    def test_request_hash_corruption_is_rejected(self):
        tokens = copy.deepcopy(TOKENS)
        tokens["cases"][0]["request_sha256"] = "0" * 64
        with self.assertRaises(rtf.ReferenceTokenFixtureError):
            rtf.validate_reference_token_fixture(copy.deepcopy(FIXTURE), tokens)

    def test_pinned_provenance_drift_is_rejected(self):
        mutations = (
            ("source_git_sha", "0" * 40),
            ("fixture.git_blob", "0" * 40),
            ("reference_runtime.git_sha", "0" * 40),
            ("reference_runtime.sequence_builder_git_blob", "0" * 40),
            ("tokenizer.git_blob", "0" * 40),
            ("tokenizer.sha256", "0" * 64),
            ("tokenizer_implementation.git_blob", "0" * 40),
            ("tokenizer_implementation.fuzz_fixture_git_blob", "0" * 40),
        )
        for path, value in mutations:
            tokens = copy.deepcopy(TOKENS)
            target = tokens
            parts = path.split(".")
            for part in parts[:-1]:
                target = target[part]
            target[parts[-1]] = value
            with self.subTest(path=path), self.assertRaises(
                rtf.ReferenceTokenFixtureError
            ):
                rtf.validate_reference_token_fixture(
                    copy.deepcopy(FIXTURE), tokens
                )

    def test_token_count_corruption_is_rejected(self):
        tokens = copy.deepcopy(TOKENS)
        tokens["cases"][2]["token_count"] += 1
        with self.assertRaises(rtf.ReferenceTokenFixtureError):
            rtf.validate_reference_token_fixture(copy.deepcopy(FIXTURE), tokens)

    def test_candidate_or_numeric_overclaim_is_rejected(self):
        for field in ("candidate_side_tokenizer_attested", "numeric_model_parity"):
            tokens = copy.deepcopy(TOKENS)
            tokens["scope"][field] = True
            with self.assertRaises(rtf.ReferenceTokenFixtureError):
                rtf.validate_reference_token_fixture(copy.deepcopy(FIXTURE), tokens)


if __name__ == "__main__":
    unittest.main()
