import copy
import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "verify_reference_model_directory",
    HERE / "verify_reference_model_directory.py",
)
verify = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = verify
SPEC.loader.exec_module(verify)

ATTESTATION = json.loads(
    (HERE / "reference_model_directory_attestation.v1.json").read_text(
        encoding="utf-8"
    )
)


def spec(path: str, value: bytes):
    return verify.FileSpec(path, len(value), hashlib.sha256(value).hexdigest())


class ReferenceModelDirectoryTest(unittest.TestCase):
    def test_retained_attestation_is_valid(self):
        verify.validate_attestation(copy.deepcopy(ATTESTATION))

    def _directory(self, root: Path):
        raw_config = json.dumps(
            {
                "temperature_by_options": {
                    "choice:11+": verify.RAW_CHOICE_11_PLUS
                }
            },
            separators=(",", ":"),
        ).encode()
        tokenizer_config = json.dumps(
            {
                "tokenizer_class": "PreTrainedTokenizerFast",
                "model_max_length": 8192,
            },
            separators=(",", ":"),
        ).encode()
        values = {
            "model.safetensors": b"synthetic-weights",
            "encoder/config.json": b'{"model_type":"modernbert"}',
            "rl_agent_config.json": raw_config,
            "tokenizer/tokenizer.json": b'{"model":{"type":"BPE"}}',
            "tokenizer/tokenizer_config.json": tokenizer_config,
        }
        for relative, value in values.items():
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(value)
        specs = tuple(spec(path, value) for path, value in values.items())
        return values, specs

    def test_synthetic_exact_directory_passes(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _values, specs = self._directory(root)
            result = verify.verify_model_directory(root, specs=specs)
        self.assertTrue(result["valid"])
        self.assertFalse(result["tokenizer_config_rewrite_required"])
        self.assertFalse(result["endpoint_loaded_exact_directory_attested"])
        self.assertFalse(result["live_reference_inference"])

    def test_file_byte_drift_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _values, specs = self._directory(root)
            (root / "model.safetensors").write_bytes(b"changed")
            with self.assertRaises(verify.ReferenceModelDirectoryError):
                verify.verify_model_directory(root, specs=specs)

    def test_tokenizer_rewrite_requirement_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            values, _specs = self._directory(root)
            changed = json.dumps(
                {"tokenizer_class": "TokenizersBackend"},
                separators=(",", ":"),
            ).encode()
            path = root / "tokenizer/tokenizer_config.json"
            path.write_bytes(changed)
            values["tokenizer/tokenizer_config.json"] = changed
            specs = tuple(spec(name, value) for name, value in values.items())
            with self.assertRaisesRegex(
                verify.ReferenceModelDirectoryError,
                "compatibility rewrite",
            ):
                verify.verify_model_directory(root, specs=specs)

    def test_raw_choice11_temperature_drift_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            values, _specs = self._directory(root)
            changed = json.dumps(
                {"temperature_by_options": {"choice:11+": 0.5}},
                separators=(",", ":"),
            ).encode()
            path = root / "rl_agent_config.json"
            path.write_bytes(changed)
            values["rl_agent_config.json"] = changed
            specs = tuple(spec(name, value) for name, value in values.items())
            with self.assertRaisesRegex(
                verify.ReferenceModelDirectoryError,
                "choice:11",
            ):
                verify.verify_model_directory(root, specs=specs)

    def test_scope_overclaim_is_rejected(self):
        for field in (
            "endpoint_loaded_exact_directory_attested",
            "endpoint_exact_runtime_wheel_attested",
            "live_reference_inference",
            "numeric_parity_with_papaya",
        ):
            packet = copy.deepcopy(ATTESTATION)
            packet["scope"][field] = True
            with self.subTest(field=field), self.assertRaises(
                verify.ReferenceModelDirectoryError
            ):
                verify.validate_attestation(packet)

    def test_independent_manifest_drift_is_rejected(self):
        packet = copy.deepcopy(ATTESTATION)
        packet["independent_manifest"]["git_blob"] = "0" * 40
        with self.assertRaises(verify.ReferenceModelDirectoryError):
            verify.validate_attestation(packet)


if __name__ == "__main__":
    unittest.main()
