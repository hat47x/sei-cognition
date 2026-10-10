import copy
import importlib.util
import json
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "papaya_candidate_tokenizer_attestation",
    HERE / "papaya_candidate_tokenizer_attestation.py",
)
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)

PACKET = json.loads(
    (HERE / "papaya_candidate_tokenizer_attestation.v1.json").read_text(encoding="utf-8")
)


class CandidateTokenizerAttestationTest(unittest.TestCase):
    def test_retained_packet_is_valid(self):
        mod.validate_candidate_tokenizer_attestation(copy.deepcopy(PACKET))

    def test_candidate_blob_drift_is_rejected(self):
        packet = copy.deepcopy(PACKET)
        packet["candidate"]["git_blob"] = "0" * 40
        with self.assertRaises(mod.CandidateTokenizerAttestationError):
            mod.validate_candidate_tokenizer_attestation(packet)

    def test_etag_drift_is_rejected(self):
        packet = copy.deepcopy(PACKET)
        packet["candidate"]["huggingface_resolve_etag"] = "0" * 40
        with self.assertRaises(mod.CandidateTokenizerAttestationError):
            mod.validate_candidate_tokenizer_attestation(packet)

    def test_candidate_byte_size_drift_is_rejected(self):
        packet = copy.deepcopy(PACKET)
        packet["candidate"]["bytes"] += 1
        with self.assertRaises(mod.CandidateTokenizerAttestationError):
            mod.validate_candidate_tokenizer_attestation(packet)

    def test_reference_sha256_drift_is_rejected(self):
        packet = copy.deepcopy(PACKET)
        packet["reference"]["sha256"] = "0" * 64
        with self.assertRaises(mod.CandidateTokenizerAttestationError):
            mod.validate_candidate_tokenizer_attestation(packet)

    def test_downstream_overclaim_is_rejected(self):
        for field in (
            "candidate_token_id_marker_parity",
            "numeric_model_parity",
            "live_l0_inference",
        ):
            packet = copy.deepcopy(PACKET)
            packet["scope"][field] = True
            with self.subTest(field=field), self.assertRaises(
                mod.CandidateTokenizerAttestationError
            ):
                mod.validate_candidate_tokenizer_attestation(packet)

    def test_independent_hash_overclaim_is_rejected(self):
        packet = copy.deepcopy(PACKET)
        packet["proof"]["candidate_sha256_independently_recomputed"] = True
        with self.assertRaises(mod.CandidateTokenizerAttestationError):
            mod.validate_candidate_tokenizer_attestation(packet)


if __name__ == "__main__":
    unittest.main()
