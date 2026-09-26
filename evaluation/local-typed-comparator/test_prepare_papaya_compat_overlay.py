import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "prepare_papaya_compat_overlay", HERE / "prepare_papaya_compat_overlay.py"
)
overlay = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = overlay
SPEC.loader.exec_module(overlay)

RAW_CONFIG = """{
  "encoder": "answerdotai/ModernBERT-large",
  "head_layers": 2,
  "max_len": 1024,
  "head_max_len": 256,
  "max_prefixes": 6,
  "act_costs": {
    "escalate": 0.5
  },
  "cost_wrong_act": 3.0,
  "amp_dtype": "bf16",
  "model_name": "laya-typed-decisions",
  "temperature": [
    1.0148024559020996,
    1.0374259948730469,
    1.0575125217437744
  ],
  "temperature_by_options": {
    "choice:3-5": 1.7601518630981445,
    "choice:6-10": 1.0000158548355103,
    "score:3-5": 1.2514300346374512,
    "noul:2": 1.983399510383606,
    "choice:11+": 0.10058280825614929,
    "choice:2": 1.9063563346862793
  },
  "training": {
    "updates": 7313,
    "epochs_completed": 1,
    "hours": 1.96,
    "world_size": 1,
    "fine_tuned_from_checkpoint": true
  },
  "gradient_checkpointing": true,
  "max_tokens_per_batch": 4096,
  "fine_tuned": true
}"""

TOKENIZER_CONFIG = """{
  "clean_up_tokenization_spaces": true,
  "cls_token": "[CLS]",
  "local_files_only": false,
  "mask_token": "[MASK]",
  "model_input_names": [
    "input_ids",
    "attention_mask"
  ],
  "model_max_length": 8192,
  "pad_token": "[PAD]",
  "sep_token": "[SEP]",
  "tokenizer_class": "PreTrainedTokenizerFast",
  "unk_token": "[UNK]"
}"""


def spec(path, data, role):
    return overlay.ArtifactSpec(
        path, len(data), hashlib.sha256(data).hexdigest(), role
    )


class PapayaCompatOverlayTest(unittest.TestCase):
    def test_clamp_matches_reference_policy(self):
        self.assertEqual(overlay.clamp_temperature(0.1), 0.5)
        self.assertEqual(overlay.clamp_temperature(0.5), 0.5)
        self.assertEqual(overlay.clamp_temperature(3.0), 3.0)
        self.assertEqual(overlay.clamp_temperature(8.0), 5.0)
        self.assertEqual(overlay.clamp_temperature(float("nan")), 1.0)
        self.assertEqual(overlay.clamp_temperature(float("inf")), 1.0)
        self.assertEqual(overlay.clamp_temperature("bad"), 1.0)

    def test_current_config_only_clamps_choice_11plus(self):
        derived, changes = overlay.derive_compat_config(json.loads(RAW_CONFIG))
        self.assertEqual(changes, [overlay.EXPECTED_CURRENT_CHANGE])
        self.assertEqual(
            derived["temperature_by_options"]["choice:11+"], 0.5
        )
        self.assertEqual(
            derived["temperature_by_options"]["choice:3-5"],
            1.7601518630981445,
        )

    def _fixture(self, root):
        candidate = root / "candidate"
        candidate.mkdir()
        q8 = b"q8-bytes"
        head = b"head-bytes"
        raw = RAW_CONFIG.encode()
        tokcfg = TOKENIZER_CONFIG.encode()
        reference = root / "reference-tokenizer.json"
        reference.write_bytes(b"reference-tokenizer-bytes")

        files = {
            "q8.gguf": q8,
            "head.safetensors": head,
            "rl_agent_config.json": raw,
            "tokenizer_config.json": tokcfg,
        }
        for name, data in files.items():
            (candidate / name).write_bytes(data)

        specs = (
            spec("q8.gguf", q8, "q8_backbone"),
            spec("head.safetensors", head, "decision_head"),
            spec("rl_agent_config.json", raw, "raw_config"),
            spec("tokenizer_config.json", tokcfg, "tokenizer_config"),
        )
        ref_spec = spec(
            "tokenizer.json", reference.read_bytes(), "reference_tokenizer"
        )
        return candidate, reference, specs, ref_spec

    def test_stage_uses_reference_tokenizer_and_not_candidate_copy(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            candidate, reference, specs, ref_spec = self._fixture(root)
            # A deliberately wrong candidate tokenizer must not be consumed.
            (candidate / "tokenizer.json").write_text("wrong", encoding="utf-8")
            output = root / "overlay"

            receipt = overlay.prepare_overlay(
                candidate,
                reference,
                output,
                artifact_specs=specs,
                attested_tokenizer_spec=ref_spec,
            )

            self.assertTrue((output / "q8.gguf").is_symlink())
            self.assertTrue((output / "head.safetensors").is_symlink())
            self.assertEqual(
                (output / "tokenizer" / "tokenizer.json").read_bytes(),
                reference.read_bytes(),
            )
            derived = json.loads((output / "rl_agent_config.json").read_text())
            self.assertEqual(
                derived["temperature_by_options"]["choice:11+"], 0.5
            )
            self.assertTrue(
                receipt["tokenizer_identity"]["candidate_byte_identity_attested"]
            )
            self.assertTrue(
                receipt["tokenizer_identity"]["staged_bytes_verified"]
            )
            self.assertTrue(
                receipt["scope"]["tokenizer_byte_identity_preserved"]
            )
            self.assertTrue(
                receipt["scope"]["frozen_token_marker_parity_precondition"]
            )
            self.assertFalse(receipt["scope"]["full_numeric_parity"])
            self.assertFalse(receipt["scope"]["live_inference"])
            self.assertEqual(
                receipt["temperature_policy"]["compat_config_sha256"],
                overlay.EXPECTED_COMPAT_CONFIG_SHA256,
            )
            self.assertEqual(
                receipt["temperature_policy"]["compat_config_bytes"],
                overlay.EXPECTED_COMPAT_CONFIG_BYTES,
            )
            for artifact in receipt["candidate_bundle"]["artifacts"].values():
                self.assertNotIn("path", artifact)

    def test_wrong_attested_tokenizer_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            candidate, tokenizer, specs, ref_spec = self._fixture(root)
            tokenizer.write_bytes(b"tampered-tokenizer")
            with self.assertRaises(overlay.OverlayError):
                overlay.inspect_overlay_inputs(
                    candidate,
                    tokenizer,
                    artifact_specs=specs,
                    attested_tokenizer_spec=ref_spec,
                )

    def test_wrong_candidate_artifact_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            candidate, reference, specs, ref_spec = self._fixture(root)
            (candidate / "q8.gguf").write_bytes(b"tampered")
            with self.assertRaises(overlay.OverlayError):
                overlay.inspect_overlay_inputs(
                    candidate,
                    reference,
                    artifact_specs=specs,
                    attested_tokenizer_spec=ref_spec,
                )

    def test_unexpected_temperature_delta_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            candidate, reference, specs, ref_spec = self._fixture(root)
            changed = json.loads(RAW_CONFIG)
            changed["temperature_by_options"]["choice:3-5"] = 0.1
            raw = json.dumps(changed, indent=2).encode()
            (candidate / "rl_agent_config.json").write_bytes(raw)
            specs = tuple(
                spec(s.relative_path, raw, s.role)
                if s.role == "raw_config"
                else s
                for s in specs
            )
            with self.assertRaises(overlay.OverlayError):
                overlay.inspect_overlay_inputs(
                    candidate,
                    reference,
                    artifact_specs=specs,
                    attested_tokenizer_spec=ref_spec,
                )


if __name__ == "__main__":
    unittest.main()
