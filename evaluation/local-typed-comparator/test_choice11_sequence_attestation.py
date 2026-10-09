import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "choice11_sequence_attestation",
    HERE / "choice11_sequence_attestation.py",
)
mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = mod
SPEC.loader.exec_module(mod)

FIXTURE_PATH = HERE / "papaya_choice11_diagnostic.v1.json"
ATTESTATION_PATH = HERE / "choice11_sequence_attestation.v1.json"
FIXTURE_RAW = FIXTURE_PATH.read_bytes()
FIXTURE = json.loads(FIXTURE_RAW)
PACKET = json.loads(ATTESTATION_PATH.read_text(encoding="utf-8"))


class Choice11SequenceAttestationTest(unittest.TestCase):
    def test_retained_packet_validates(self):
        mod.validate_choice11_sequence(
            copy.deepcopy(FIXTURE),
            copy.deepcopy(PACKET),
            fixture_raw=FIXTURE_RAW,
        )

    def test_choice_order_drift_is_rejected(self):
        fixture = copy.deepcopy(FIXTURE)
        criteria = fixture["cases"][0]["request"]["questions"]["choice12"]["criteria"]
        fixture["cases"][0]["request"]["questions"]["choice12"]["criteria"] = {
            key: criteria[key] for key in reversed(list(criteria))
        }
        with self.assertRaises(mod.Choice11SequenceError):
            mod.validate_choice11_sequence(fixture, copy.deepcopy(PACKET))

    def test_marker_drift_is_rejected(self):
        packet = copy.deepcopy(PACKET)
        packet["case"]["marker_positions"][1] += 1
        with self.assertRaises(mod.Choice11SequenceError):
            mod.validate_choice11_sequence(
                copy.deepcopy(FIXTURE), packet, fixture_raw=FIXTURE_RAW
            )

    def test_marker_must_point_to_mask(self):
        packet = copy.deepcopy(PACKET)
        marker = packet["case"]["marker_positions"][0]
        packet["case"]["input_ids"][marker] = 0
        with self.assertRaises(mod.Choice11SequenceError):
            mod.validate_choice11_sequence(
                copy.deepcopy(FIXTURE), packet, fixture_raw=FIXTURE_RAW
            )

    def test_replay_sanity_must_remain_four_of_four(self):
        packet = copy.deepcopy(PACKET)
        packet["replay_validation"]["frozen_four_case_full_input_ids_exact"] = 3
        with self.assertRaises(mod.Choice11SequenceError):
            mod.validate_choice11_sequence(
                copy.deepcopy(FIXTURE), packet, fixture_raw=FIXTURE_RAW
            )

    def test_live_or_numeric_overclaim_is_rejected(self):
        for field in (
            "live_runtime_input_ids_observed",
            "live_runtime_marker_positions_observed",
            "live_inference",
            "numeric_model_parity",
            "calibration_validity",
            "task_quality",
            "reference_provider_promotion",
        ):
            packet = copy.deepcopy(PACKET)
            packet["scope"][field] = True
            with self.subTest(field=field), self.assertRaises(
                mod.Choice11SequenceError
            ):
                mod.validate_choice11_sequence(
                    copy.deepcopy(FIXTURE), packet, fixture_raw=FIXTURE_RAW
                )

    def test_fixture_blob_binding_is_checked_when_bytes_supplied(self):
        with self.assertRaises(mod.Choice11SequenceError):
            mod.validate_choice11_sequence(
                copy.deepcopy(FIXTURE),
                copy.deepcopy(PACKET),
                fixture_raw=FIXTURE_RAW + b"\n",
            )


if __name__ == "__main__":
    unittest.main()
