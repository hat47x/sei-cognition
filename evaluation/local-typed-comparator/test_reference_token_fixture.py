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
