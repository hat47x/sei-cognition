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
    "materialize_reference_model",
    HERE / "materialize_reference_model.py",
)
mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = mod
SPEC.loader.exec_module(mod)

MANIFEST = json.loads(
    (HERE / "reference_model_transport.v1.json").read_text(
        encoding="utf-8"
    )
)


class ReferenceModelTransportTest(unittest.TestCase):
    def test_retained_manifest_is_exact(self):
        transports = mod.validate_manifest(copy.deepcopy(MANIFEST))
        self.assertEqual(
            set(transports),
            {mod.HF_ID, mod.MIRROR_ID, mod.HF_MIRROR_ID},
        )
        for entries in transports.values():
            self.assertEqual(len(entries), 5)

    def test_manifest_scope_overclaim_is_rejected(self):
        for field in (
            "current_chat_transport_succeeded",
            "model_bytes_materialized",
            "model_weights_loaded",
            "live_inference",
            "numeric_parity",
            "shipping_decision",
        ):
            packet = copy.deepcopy(MANIFEST)
            packet["scope"][field] = True
            with self.subTest(field=field), self.assertRaises(
                mod.ReferenceModelTransportError
            ):
                mod.validate_manifest(packet)

    def test_transport_contract_or_provenance_drift_is_rejected(self):
        packet = copy.deepcopy(MANIFEST)
        packet["transports"][1]["provenance"]["git_blob"] = "0" * 40
        with self.assertRaises(mod.ReferenceModelTransportError):
            mod.validate_manifest(packet)

        packet = copy.deepcopy(MANIFEST)
        packet["transports"][0]["files"][0]["sha256"] = "0" * 64
        with self.assertRaises(mod.ReferenceModelTransportError):
            mod.validate_manifest(packet)

        packet = copy.deepcopy(MANIFEST)
        packet["transports"][1]["files"][0]["url"] += "?changed=1"
        with self.assertRaises(mod.ReferenceModelTransportError):
            mod.validate_manifest(packet)

        packet = copy.deepcopy(MANIFEST)
        packet["transports"][2]["provenance"][
            "independent_exact_reference_observation"
        ]["report_git_blob"] = "0" * 40
        with self.assertRaises(mod.ReferenceModelTransportError):
            mod.validate_manifest(packet)

        packet = copy.deepcopy(MANIFEST)
        packet["transports"][2]["files"][0]["url"] += "?changed=1"
        with self.assertRaises(mod.ReferenceModelTransportError):
            mod.validate_manifest(packet)

        packet = copy.deepcopy(MANIFEST)
        packet["transports"][2]["content_addressed_url"] = True
        with self.assertRaises(mod.ReferenceModelTransportError):
            mod.validate_manifest(packet)

    def test_atomic_materialization_succeeds_for_verified_streams(self):
        blobs = {
            "https://example.invalid/a": b"alpha",
            "https://example.invalid/nested/b": b"beta",
        }
        entries = [
            {
                "path": "a",
                "url": "https://example.invalid/a",
                "bytes": len(blobs["https://example.invalid/a"]),
                "sha256": hashlib.sha256(
                    blobs["https://example.invalid/a"]
                ).hexdigest(),
            },
            {
                "path": "nested/b",
                "url": "https://example.invalid/nested/b",
                "bytes": len(
                    blobs["https://example.invalid/nested/b"]
                ),
                "sha256": hashlib.sha256(
                    blobs["https://example.invalid/nested/b"]
                ).hexdigest(),
            },
        ]

        def stream(url, _timeout):
            return closing(io.BytesIO(blobs[url]))

        def verify(root):
            self.assertEqual(
                (root / "a").read_bytes(),
                b"alpha",
            )
            self.assertEqual(
                (root / "nested/b").read_bytes(),
                b"beta",
            )
            return {"valid": True}

        with tempfile.TemporaryDirectory() as td:
            output = Path(td) / "model"
            receipt = mod.materialize_entries(
                entries,
                output,
                transport_id="synthetic",
                stream_factory=stream,
                directory_verifier=verify,
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
                receipt["scope"]["model_bytes_materialized"]
            )
            self.assertFalse(
                receipt["scope"]["model_weights_loaded"]
            )

    def test_transient_download_failure_retries_from_zero(self):
        blob = b"reference"
        entry = {
            "path": "model.safetensors",
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
            output = Path(td) / "model"
            receipt = mod.materialize_entries(
                [entry],
                output,
                transport_id="synthetic",
                attempts=3,
                stream_factory=stream,
                directory_verifier=lambda _root: {"valid": True},
            )
            self.assertEqual(calls, 2)
            self.assertEqual(
                receipt["files"][0]["download_attempts"], 2
            )
            self.assertEqual(
                (output / "model.safetensors").read_bytes(), blob
            )

    def test_source_read_failure_is_retryable(self):
        blob = b"reference-read"
        entry = {
            "path": "model.safetensors",
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
            output = Path(td) / "model"
            receipt = mod.materialize_entries(
                [entry],
                output,
                transport_id="synthetic",
                attempts=3,
                stream_factory=stream,
                directory_verifier=lambda _root: {"valid": True},
            )
            self.assertEqual(calls, 2)
            self.assertEqual(
                receipt["files"][0]["download_attempts"], 2
            )

    def test_local_staging_write_failure_is_not_retried(self):
        blob = b"reference-write"
        entry = {
            "path": "model.safetensors",
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
            output = root / "model"
            with mock.patch.object(
                mod.Path,
                "open",
                return_value=WriteFails(),
            ) as open_mock:
                with self.assertRaisesRegex(
                    mod.ReferenceModelTransportError,
                    "staged write failed",
                ):
                    mod.materialize_entries(
                        [entry],
                        output,
                        transport_id="synthetic",
                        attempts=3,
                        stream_factory=stream,
                        directory_verifier=lambda _root: {"valid": True},
                    )
            self.assertEqual(open_mock.call_count, 1)
            self.assertEqual(stream_calls, 1)
            self.assertEqual(write_calls, 1)
            self.assertFalse(output.exists())
            self.assertEqual(list(root.iterdir()), [])

    def test_download_attempt_limit_and_exhaustion_are_fail_closed(self):
        blob = b"right"
        entry = {
            "path": "model.safetensors",
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
            output = root / "model"
            with self.assertRaisesRegex(
                mod.ReferenceModelDownloadError,
                "failed after 2 download attempts",
            ):
                mod.materialize_entries(
                    [entry],
                    output,
                    transport_id="synthetic",
                    attempts=2,
                    stream_factory=always_fails,
                    directory_verifier=lambda _root: {"valid": True},
                )
            self.assertEqual(calls, 2)
            self.assertFalse(output.exists())
            self.assertEqual(list(root.iterdir()), [])

        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(
                mod.ReferenceModelTransportError,
                "attempts must be an integer >= 1",
            ):
                mod.materialize_entries(
                    [],
                    Path(td) / "model",
                    transport_id="synthetic",
                    attempts=0,
                )

    def test_hash_or_size_failure_never_publishes_output(self):
        entry = {
            "path": "model.safetensors",
            "url": "https://example.invalid/model",
            "bytes": 5,
            "sha256": hashlib.sha256(b"right").hexdigest(),
        }

        def stream(_url, _timeout):
            return closing(io.BytesIO(b"wrong"))

        with tempfile.TemporaryDirectory() as td:
            output = Path(td) / "model"
            with self.assertRaises(
                mod.ReferenceModelTransportError
            ):
                mod.materialize_entries(
                    [entry],
                    output,
                    transport_id="synthetic",
                    stream_factory=stream,
                    directory_verifier=lambda _root: {"valid": True},
                )
            self.assertFalse(output.exists())
            self.assertEqual(list(Path(td).iterdir()), [])

    def test_oversized_stream_stops_at_attested_boundary_without_retry(self):
        entry = {
            "path": "model.safetensors",
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
            output = root / "model"
            with self.assertRaisesRegex(
                mod.ReferenceModelTransportError,
                "exceeded expected",
            ):
                mod.materialize_entries(
                    [entry],
                    output,
                    transport_id="synthetic",
                    attempts=3,
                    stream_factory=stream,
                    directory_verifier=lambda _root: {"valid": True},
                )
            self.assertEqual(stream_calls, 1)
            self.assertEqual(read_calls, 2)
            self.assertFalse(output.exists())
            self.assertEqual(list(root.iterdir()), [])

    def test_integrity_failure_is_not_retried(self):
        entry = {
            "path": "a",
            "url": "https://example.invalid/a",
            "bytes": len(b"right"),
            "sha256": hashlib.sha256(b"right").hexdigest(),
        }
        calls = 0

        def stream(_url, _timeout):
            nonlocal calls
            calls += 1
            return closing(io.BytesIO(b"wrong"))

        with tempfile.TemporaryDirectory() as td:
            output = Path(td) / "model"
            with self.assertRaises(mod.ReferenceModelTransportError):
                mod.materialize_entries(
                    [entry],
                    output,
                    transport_id="synthetic",
                    attempts=3,
                    stream_factory=stream,
                    directory_verifier=lambda _root: {"valid": True},
                )
            self.assertEqual(calls, 1)
            self.assertFalse(output.exists())
            self.assertEqual(list(Path(td).iterdir()), [])

    def test_attempt_count_must_be_positive_integer(self):
        entry = {
            "path": "a",
            "url": "https://example.invalid/a",
            "bytes": 1,
            "sha256": hashlib.sha256(b"a").hexdigest(),
        }
        for attempts in (0, -1, True):
            with tempfile.TemporaryDirectory() as td:
                with self.subTest(attempts=attempts), self.assertRaises(
                    mod.ReferenceModelTransportError
                ):
                    mod.materialize_entries(
                        [entry],
                        Path(td) / "model",
                        transport_id="synthetic",
                        attempts=attempts,
                        stream_factory=lambda _url, _timeout: closing(
                            io.BytesIO(b"a")
                        ),
                        directory_verifier=lambda _root: {"valid": True},
                    )

    def test_output_collision_and_unsafe_paths_are_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            output = root / "model"
            output.mkdir()
            with self.assertRaises(
                mod.ReferenceModelTransportError
            ):
                mod.materialize_entries(
                    [],
                    output,
                    transport_id="synthetic",
                )

        with self.assertRaises(mod.ReferenceModelTransportError):
            mod._safe_relative_path("../escape", "path")
        with self.assertRaises(mod.ReferenceModelTransportError):
            mod._safe_relative_path("/absolute", "path")


if __name__ == "__main__":
    unittest.main()
