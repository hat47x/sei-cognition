import copy
import hashlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from contextlib import closing
from unittest import mock
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
            self.assertEqual(
                [item["download_attempts"] for item in receipt["files"]],
                [1, 1],
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

    def test_transient_download_failure_retries_from_zero(self):
        blob = b"papaya"
        entry = {
            "path": "model.gguf",
            "role": "q8_backbone",
            "revision": "a" * 40,
            "url": "https://example.invalid/model",
            "bytes": len(blob),
            "sha256": hashlib.sha256(blob).hexdigest(),
        }
        calls = 0

        def stream(_url, _timeout):
            nonlocal calls
            calls += 1
            if calls == 1:
                raise OSError("synthetic transient failure")
            return closing(io.BytesIO(blob))

        with tempfile.TemporaryDirectory() as td:
            output = Path(td) / "candidate"
            receipt = mod.materialize_entries(
                [entry],
                output,
                attempts=3,
                stream_factory=stream,
                input_verifier=lambda _root: {"verified": True},
            )
            self.assertEqual(calls, 2)
            self.assertEqual(
                receipt["files"][0]["download_attempts"], 2
            )
            self.assertEqual(
                (output / "model.gguf").read_bytes(), blob
            )

    def test_source_read_failure_is_retryable(self):
        blob = b"papaya-read"
        entry = {
            "path": "model.gguf",
            "role": "q8_backbone",
            "revision": "a" * 40,
            "url": "https://example.invalid/model",
            "bytes": len(blob),
            "sha256": hashlib.sha256(blob).hexdigest(),
        }
        calls = 0

        class ReadFails(io.BytesIO):
            def read(self, _size=-1):
                raise OSError("synthetic source read failure")

        def stream(_url, _timeout):
            nonlocal calls
            calls += 1
            if calls == 1:
                return ReadFails(blob)
            return io.BytesIO(blob)

        with tempfile.TemporaryDirectory() as td:
            output = Path(td) / "candidate"
            receipt = mod.materialize_entries(
                [entry],
                output,
                attempts=3,
                stream_factory=stream,
                input_verifier=lambda _root: {"verified": True},
            )
            self.assertEqual(calls, 2)
            self.assertEqual(
                receipt["files"][0]["download_attempts"], 2
            )

    def test_local_staging_write_failure_is_not_retried(self):
        blob = b"papaya-write"
        entry = {
            "path": "model.gguf",
            "role": "q8_backbone",
            "revision": "a" * 40,
            "url": "https://example.invalid/model",
            "bytes": len(blob),
            "sha256": hashlib.sha256(blob).hexdigest(),
        }
        stream_calls = 0
        write_calls = 0

        class WriteFails:
            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def write(self, _block):
                nonlocal write_calls
                write_calls += 1
                raise OSError("synthetic local staging failure")

        def stream(_url, _timeout):
            nonlocal stream_calls
            stream_calls += 1
            return io.BytesIO(blob)

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            output = root / "candidate"
            with mock.patch.object(
                mod.Path,
                "open",
                return_value=WriteFails(),
            ) as open_mock:
                with self.assertRaisesRegex(
                    mod.PapayaCandidateTransportError,
                    "staged write failed",
                ):
                    mod.materialize_entries(
                        [entry],
                        output,
                        attempts=3,
                        stream_factory=stream,
                        input_verifier=lambda _root: {"verified": True},
                    )
            self.assertEqual(open_mock.call_count, 1)
            self.assertEqual(stream_calls, 1)
            self.assertEqual(write_calls, 1)
            self.assertFalse(output.exists())
            self.assertEqual(list(root.iterdir()), [])

    def test_download_attempt_limit_and_exhaustion_are_fail_closed(self):
        blob = b"right"
        entry = {
            "path": "model.gguf",
            "role": "q8_backbone",
            "revision": "a" * 40,
            "url": "https://example.invalid/model",
            "bytes": len(blob),
            "sha256": hashlib.sha256(blob).hexdigest(),
        }
        calls = 0

        def always_fails(_url, _timeout):
            nonlocal calls
            calls += 1
            raise OSError("synthetic transient failure")

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            output = root / "candidate"
            with self.assertRaisesRegex(
                mod.PapayaCandidateDownloadError,
                "failed after 2 download attempts",
            ):
                mod.materialize_entries(
                    [entry],
                    output,
                    attempts=2,
                    stream_factory=always_fails,
                    input_verifier=lambda _root: {"verified": True},
                )
            self.assertEqual(calls, 2)
            self.assertFalse(output.exists())
            self.assertEqual(list(root.iterdir()), [])

        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(
                mod.PapayaCandidateTransportError,
                "attempts must be an integer >= 1",
            ):
                mod.materialize_entries(
                    [],
                    Path(td) / "candidate",
                    attempts=0,
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

    def test_oversized_stream_stops_at_attested_boundary_without_retry(self):
        entry = {
            "path": "model.gguf",
            "role": "q8_backbone",
            "revision": "a" * 40,
            "url": "https://example.invalid/model",
            "bytes": 5,
            "sha256": hashlib.sha256(b"right").hexdigest(),
        }
        stream_calls = 0
        read_calls = 0

        class OversizedStream:
            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def read(self, _size=-1):
                nonlocal read_calls
                read_calls += 1
                if read_calls == 1:
                    return b"right"
                if read_calls == 2:
                    return b"extra"
                raise AssertionError("downloader read past oversized boundary")

        def stream(_url, _timeout):
            nonlocal stream_calls
            stream_calls += 1
            return OversizedStream()

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            output = root / "candidate"
            with self.assertRaisesRegex(
                mod.PapayaCandidateTransportError,
                "exceeded expected",
            ):
                mod.materialize_entries(
                    [entry],
                    output,
                    attempts=3,
                    stream_factory=stream,
                    input_verifier=lambda _root: {"verified": True},
                )
            self.assertEqual(stream_calls, 1)
            self.assertEqual(read_calls, 2)
            self.assertFalse(output.exists())
            self.assertEqual(list(root.iterdir()), [])

    def test_integrity_failure_is_not_retried(self):
        entry = {
            "path": "model.gguf",
            "role": "q8_backbone",
            "revision": "a" * 40,
            "url": "https://example.invalid/model",
            "bytes": len(b"right"),
            "sha256": hashlib.sha256(b"right").hexdigest(),
        }
        calls = 0

        def stream(_url, _timeout):
            nonlocal calls
            calls += 1
            return closing(io.BytesIO(b"wrong"))

        with tempfile.TemporaryDirectory() as td:
            output = Path(td) / "candidate"
            with self.assertRaises(mod.PapayaCandidateTransportError):
                mod.materialize_entries(
                    [entry],
                    output,
                    attempts=3,
                    stream_factory=stream,
                    input_verifier=lambda _root: {"verified": True},
                )
            self.assertEqual(calls, 1)
            self.assertFalse(output.exists())
            self.assertEqual(list(Path(td).iterdir()), [])

    def test_attempt_count_must_be_positive_integer(self):
        entry = {
            "path": "model.gguf",
            "role": "q8_backbone",
            "revision": "a" * 40,
            "url": "https://example.invalid/model",
            "bytes": 1,
            "sha256": hashlib.sha256(b"a").hexdigest(),
        }
        for attempts in (0, -1, True):
            with tempfile.TemporaryDirectory() as td:
                with self.subTest(attempts=attempts), self.assertRaises(
                    mod.PapayaCandidateTransportError
                ):
                    mod.materialize_entries(
                        [entry],
                        Path(td) / "candidate",
                        attempts=attempts,
                        stream_factory=lambda _url, _timeout: closing(
                            io.BytesIO(b"a")
                        ),
                        input_verifier=lambda _root: {"verified": True},
                    )

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
