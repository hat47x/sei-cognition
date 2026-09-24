import copy
import importlib.util
import json
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "protocol_contract", HERE / "protocol_contract.py"
)
pc = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pc)

FIXTURE = json.loads((HERE / "fixture.v1.json").read_text(encoding="utf-8"))


def choice_request():
    return copy.deepcopy(FIXTURE["cases"][0]["request"])


class ProtocolContractTest(unittest.TestCase):
    def test_fixture_is_valid(self):
        pc.validate_fixture(copy.deepcopy(FIXTURE))

    def test_perturbation_group_must_preserve_state(self):
        fixture = copy.deepcopy(FIXTURE)
        fixture["cases"][1]["request"]["state"]["retry_count"] = 99
        with self.assertRaises(pc.ProtocolContractError):
            pc.validate_fixture(fixture)

    def test_missing_state_is_rejected_locally(self):
        fixture = copy.deepcopy(FIXTURE)
        del fixture["cases"][0]["request"]["state"]
        with self.assertRaises(pc.ProtocolContractError):
            pc.validate_fixture(fixture)

    def test_valid_choice_response(self):
        pc.validate_response(
            choice_request(),
            {
                "model": "laya-rl-agent",
                "answers": {
                    "route": {
                        "type": "choice",
                        "choice": "technical_review",
                        "probabilities": {
                            "observe": 0.1,
                            "technical_review": 0.8,
                            "manual_review": 0.1,
                        },
                        "confidence": 0.8,
                        "answer_confidence": 0.8,
                    }
                },
                "usage": {"input_tokens": 20, "output_tokens": 0},
                "routing": {"model": "typed-decisions"},
            },
        )

    def test_choice_probability_keys_must_match(self):
        with self.assertRaises(pc.ProtocolContractError):
            pc.validate_response(
                choice_request(),
                {
                    "model": "laya-rl-agent",
                    "answers": {
                        "route": {
                            "type": "choice",
                            "choice": "technical_review",
                            "probabilities": {"technical_review": 1.0},
                            "confidence": 1.0,
                        }
                    },
                    "usage": {"input_tokens": 1, "output_tokens": 0},
                },
            )

    def test_valid_score_response(self):
        request = copy.deepcopy(FIXTURE["cases"][2]["request"])
        pc.validate_response(
            request,
            {
                "model": "laya-rl-agent-onnx",
                "answers": {
                    "urgency": {
                        "type": "score",
                        "score": 2.3,
                        "legend": {
                            "0": "Low",
                            "1": "Moderate",
                            "2": "High",
                            "3": "Critical",
                        },
                        "probabilities": {
                            "0": 0.05,
                            "1": 0.1,
                            "2": 0.35,
                            "3": 0.5,
                        },
                        "confidence": 0.5,
                    }
                },
                "usage": {"input_tokens": 20, "output_tokens": 0},
            },
        )

    def test_score_legend_must_match_order(self):
        request = copy.deepcopy(FIXTURE["cases"][2]["request"])
        with self.assertRaises(pc.ProtocolContractError):
            pc.validate_response(
                request,
                {
                    "model": "laya-rl-agent",
                    "answers": {
                        "urgency": {
                            "type": "score",
                            "score": 2.0,
                            "legend": {
                                "0": "Critical",
                                "1": "High",
                                "2": "Moderate",
                                "3": "Low",
                            },
                            "probabilities": {
                                "0": 0.1,
                                "1": 0.1,
                                "2": 0.7,
                                "3": 0.1,
                            },
                            "confidence": 0.7,
                        }
                    },
                    "usage": {"input_tokens": 1, "output_tokens": 0},
                },
            )

    def test_valid_noul_response_allows_provider_extras(self):
        request = copy.deepcopy(FIXTURE["cases"][3]["request"])
        pc.validate_response(
            request,
            {
                "model": "laya-rl-agent",
                "answers": {
                    "needs_human_review": {
                        "type": "noul",
                        "noul": 0.91,
                        "confidence": 0.91,
                        "answer_confidence": 0.91,
                        "action": {"act_probability": 0.5},
                    }
                },
                "usage": {"input_tokens": 9, "output_tokens": 0},
            },
        )

    def test_extra_or_missing_answer_ids_are_rejected(self):
        with self.assertRaises(pc.ProtocolContractError):
            pc.validate_response(
                choice_request(),
                {
                    "model": "laya-rl-agent",
                    "answers": {},
                    "usage": {"input_tokens": 1, "output_tokens": 0},
                },
            )

    def test_boolean_probability_and_usage_are_rejected(self):
        with self.assertRaises(pc.ProtocolContractError):
            pc.validate_response(
                choice_request(),
                {
                    "model": "laya-rl-agent",
                    "answers": {
                        "route": {
                            "type": "choice",
                            "choice": "observe",
                            "probabilities": {
                                "observe": True,
                                "technical_review": 0.0,
                                "manual_review": 0.0,
                            },
                            "confidence": 1.0,
                        }
                    },
                    "usage": {"input_tokens": True, "output_tokens": 0},
                },
            )


if __name__ == "__main__":
    unittest.main()
