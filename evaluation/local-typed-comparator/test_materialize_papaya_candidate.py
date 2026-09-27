import copy
import hashlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "materialize_papaya_candidate",
    HERE / "materialize_papaya_candidate.py",
)
mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = mod
SPEC.loader.exec_module(mod)

MANIFEST = json.loads(
    (HERE / "papaya_candidate_transport.v1.json").read_text(
        encoding="utf-8"
    )
)


class PapayaCandidateMaterializerTest(unittest.TestCase):
    def test_retained_manifest_validates(self):
        entries = mod.validate_manifest(copy.deepcopy(MANIFEST))
        self.assertEqual(
            [entry["role"] for entry in entries],
            list(mod.ROLE_ORDER),
        )
        self.assertEqual(
            entries[0]["revision"],
            mod.CANDIDATE_REVISION,
        )
        self.assertEqual(
            entries[-1]["revision"],
            mod.TOKENIZER_REVISION,
        )

    def test_manifest_revision_url_and_scope_drift_are_rejected(self):
        packet = copy.deepcopy(MANIFEST)
        packet["transport"]["files"][0]["revision"] = mod.TOKENIZER_REVISION
        with self.assertRaises(mod.PapayaCandidateTransportError):
            mod.validate_manifest(packet)

        packet = copy.deepcopy(MANIFEST)
        packet["transport"]["files"][-1]["revision"] = mod.CANDIDATE_REVISION
        with self.assertRaises(mod.PapayaCandidateTransportError):
            mod.validate_manifest(packet)

        packet = copy.deepcopy(MANIFEST)
        packet["transport"]["files"][0]["url"] += "?changed=1"
        with self.assertRaises(mod.PapayaCandidateTransportError):
            mod.validate_manifest(packet)

        packet = copy.deepcopy(MANIFEST)
        packet["scope"]["independent_exact_byte_mirror_available"] = True
        with self.assertRaises(mod.PapayaCandidateTransportError):
            mod.validate_manifest(packet)

        packet = copy.deepcopy(MANIFEST)
        packet["scope"]["candidate_bytes_materialized"] = True
        with self.assertRaises(mod.PapayaCandidateTransportError):
            mod.validate_manifest(packet)

    def test_manifest_file_order_and_hash_drift_are_rejected(self):
        packet = copy.deepcopy(MANIFEST)
        files = packet["transport"]["files"]
        files[0], files[1] = files[1], files[0]
        with self.assertRaises(mod.PapayaCandidateTransportError):
            mod.validate_manifest(packet)

        packet = copy.deepcopy(MANIFEST)
        packet["transport"]["files"][0]["sha256"] = "0" * 64
        with self.assertRaises(mod.PapayaCandidateTransportError):
            mod.validate_manifest(packet)

    def test_atomic_materialization_succeeds_for_verified_streams(self):
        blobs = {
            "https://example.invalid/q8": b"q8",
            "https://example.invalid/head": b"head",
        }
        entries = [
            {
                "path": "backbone.gguf",
                "role": "q8_backbone",
                "revision": "a" * 40,
                "url": "https://example.invalid/q8",
                "bytes": len(blobs["https://example.invalid/q8"]),
                "sha256": hashlib.sha256(
                    blobs["https://example.invalid/q8"]
                ).hexdigest(),
            },
            {
                "path": "head.safetensors",
                "role": "decision_head",
                "revision": "a" * 40,
                "url": "https://example.invalid/head",
                "bytes": len(blobs["https://example.invalid/head"]),
                "sha256": hashlib.sha256(
                    blobs["https://example.invalid/head"]
                ).hexdigest(),
            },
        ]

        def stream(url, _timeout):
            return closing(io.BytesIO(blobs[url]))

        def verify(root):
            self.assertEqual(
                (root / "backbone.gguf").read_bytes(),
                b"q8",
            )
            self.assertEqual(
                (root / "head.safetensors").read_bytes(),
                b"head",
            )
            return {
                "schema": "synthetic",
                "verified": True,
            }

        with tempfile.TemporaryDirectory() as td:
            output = Path(td) / "candidate"
            receipt = mod.materialize_entries(
                entries,
                output,
                stream_factory=stream,
                input_verifier=verify,
            )
            self.assertTrue(output.is_dir())
            self.assertEqual(
                receipt["status"],
                "materialized-and-verified",
            )
            self.assertTrue(
                receipt["scope"]["candidate_bytes_materialized"]
            )
            self.assertTrue(
                receipt["scope"]["candidate_inputs_verified"]
            )
            self.assertFalse(
                receipt["scope"]["compatibility_overlay_prepared"]
            )
            self.assertFalse(
                receipt["scope"]["model_weights_loaded"]
            )

    def test_hash_or_size_failure_never_publishes_output(self):
        entry = {
            "path": "model.gguf",
            "role": "q8_backbone",
            "revision": "a" * 40,
            "url": "https://example.invalid/model",
            "bytes": 5,
            "sha256": hashlib.sha256(b"right").hexdigest(),
        }

        def stream(_url, _timeout):
            return closing(io.BytesIO(b"wrong"))

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            output = root / "candidate"
            with self.assertRaises(
                mod.PapayaCandidateTransportError
            ):
                mod.materialize_entries(
                    [entry],
                    output,
                    stream_factory=stream,
                    input_verifier=lambda _root: {"verified": True},
                )
            self.assertFalse(output.exists())
            self.assertEqual(list(root.iterdir()), [])

    def test_verifier_failure_never_publishes_output(self):
        blob = b"q8"
        entry = {
            "path": "model.gguf",
            "role": "q8_backbone",
            "revision": "a" * 40,
            "url": "https://example.invalid/model",
            "bytes": len(blob),
            "sha256": hashlib.sha256(blob).hexdigest(),
        }

        def stream(_url, _timeout):
            return closing(io.BytesIO(blob))

        def reject(_root):
            raise mod.PapayaCandidateTransportError(
                "synthetic verification failure"
            )

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            output = root / "candidate"
            with self.assertRaises(
                mod.PapayaCandidateTransportError
            ):
                mod.materialize_entries(
                    [entry],
                    output,
                    stream_factory=stream,
                    input_verifier=reject,
                )
            self.assertFalse(output.exists())
            self.assertEqual(list(root.iterdir()), [])

    def test_output_collision_and_unsafe_paths_are_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            output = root / "candidate"
            output.mkdir()
            with self.assertRaises(
                mod.PapayaCandidateTransportError
            ):
                mod.materialize_entries([], output)

        for value in ("../escape", "/absolute", "a/../b"):
            with self.subTest(value=value), self.assertRaises(
                mod.PapayaCandidateTransportError
            ):
                mod._safe_relative_path(value, "path")


if __name__ == "__main__":
    unittest.main()
