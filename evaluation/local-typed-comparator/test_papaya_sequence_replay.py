import copy
import importlib.util
import json
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "papaya_sequence_replay", HERE / "papaya_sequence_replay.py"
)
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)

FIXTURE = json.loads((HERE / "fixture.v1.json").read_text(encoding="utf-8"))
REFERENCE = json.loads(
    (HERE / "reference_token_fixture.v1.json").read_text(encoding="utf-8")
)
ATTESTATION = json.loads(
    (HERE / "papaya_candidate_tokenizer_attestation.v1.json").read_text(
        encoding="utf-8"
    )
)
REPLAY = json.loads(
    (HERE / "papaya_sequence_replay.v1.json").read_text(encoding="utf-8")
)


class PapayaSequenceReplayTest(unittest.TestCase):
    def test_retained_replay_is_valid(self):
        mod.validate_papaya_sequence_replay(
            copy.deepcopy(FIXTURE),
            copy.deepcopy(REFERENCE),
            copy.deepcopy(ATTESTATION),
            copy.deepcopy(REPLAY),
        )

    def test_candidate_attestation_must_remain_true(self):
        attestation = copy.deepcopy(ATTESTATION)
        attestation["scope"]["candidate_side_tokenizer_attested"] = False
        with self.assertRaises(mod.PapayaSequenceReplayError):
            mod.validate_papaya_sequence_replay(
                copy.deepcopy(FIXTURE),
                copy.deepcopy(REFERENCE),
                attestation,
                copy.deepcopy(REPLAY),
            )

    def test_candidate_binding_drift_is_rejected(self):
        mutations = (
            ("candidate_revision", "0" * 40),
            ("tokenizer_bytes", 1),
            ("tokenizer_git_blob", "0" * 40),
            ("tokenizer_sha256", "0" * 64),
        )
        for field, value in mutations:
            replay = copy.deepcopy(REPLAY)
            replay["candidate_tokenizer_attestation"][field] = value
            with self.subTest(field=field), self.assertRaises(
                mod.PapayaSequenceReplayError
            ):
                mod.validate_papaya_sequence_replay(
                    copy.deepcopy(FIXTURE),
                    copy.deepcopy(REFERENCE),
                    copy.deepcopy(ATTESTATION),
                    replay,
                )

    def test_parity_scope_drift_is_rejected(self):
        replay = copy.deepcopy(REPLAY)
        replay["scope"]["parity_scope"] = "broader than frozen replay"
        with self.assertRaises(mod.PapayaSequenceReplayError):
            mod.validate_papaya_sequence_replay(
                copy.deepcopy(FIXTURE),
                copy.deepcopy(REFERENCE),
                copy.deepcopy(ATTESTATION),
                replay,
            )

    def test_papaya_source_drift_is_rejected(self):
        replay = copy.deepcopy(REPLAY)
        replay["papaya_source"]["sequences_git_blob"] = "0" * 40
        with self.assertRaises(mod.PapayaSequenceReplayError):
            mod.validate_papaya_sequence_replay(
                copy.deepcopy(FIXTURE),
                copy.deepcopy(REFERENCE),
                copy.deepcopy(ATTESTATION),
                replay,
            )

    def test_request_drift_is_rejected(self):
        fixture = copy.deepcopy(FIXTURE)
        fixture["cases"][0]["request"]["state"]["retry_count"] = 5
        with self.assertRaises(mod.PapayaSequenceReplayError):
            mod.validate_papaya_sequence_replay(
                fixture,
                copy.deepcopy(REFERENCE),
                copy.deepcopy(ATTESTATION),
                copy.deepcopy(REPLAY),
            )

    def test_input_id_or_marker_drift_is_rejected(self):
        for field in ("input_ids", "marker_positions"):
            replay = copy.deepcopy(REPLAY)
            replay["cases"][0][field][0] += 1
            with self.subTest(field=field), self.assertRaises(
                mod.PapayaSequenceReplayError
            ):
                mod.validate_papaya_sequence_replay(
                    copy.deepcopy(FIXTURE),
                    copy.deepcopy(REFERENCE),
                    copy.deepcopy(ATTESTATION),
                    replay,
                )

    def test_replay_method_overclaim_is_rejected(self):
        for field in (
            "upstream_python_executed",
            "transformers_auto_tokenizer_executed",
            "model_weights_loaded",
        ):
            replay = copy.deepcopy(REPLAY)
            replay["replay_basis"][field] = True
            with self.subTest(field=field), self.assertRaises(
                mod.PapayaSequenceReplayError
            ):
                mod.validate_papaya_sequence_replay(
                    copy.deepcopy(FIXTURE),
                    copy.deepcopy(REFERENCE),
                    copy.deepcopy(ATTESTATION),
                    replay,
                )

    def test_downstream_overclaim_is_rejected(self):
        for field in (
            "numeric_model_parity",
            "temperature_semantics_parity",
            "live_l0_inference",
            "provider_identity_equivalence",
            "reference_provider_promotion",
        ):
            replay = copy.deepcopy(REPLAY)
            replay["scope"][field] = True
            with self.subTest(field=field), self.assertRaises(
                mod.PapayaSequenceReplayError
            ):
                mod.validate_papaya_sequence_replay(
                    copy.deepcopy(FIXTURE),
                    copy.deepcopy(REFERENCE),
                    copy.deepcopy(ATTESTATION),
                    replay,
                )


if __name__ == "__main__":
    unittest.main()
