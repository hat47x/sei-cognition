import importlib.util
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "preflight_managed_pair_tested", HERE / "preflight_managed_pair.py"
)
mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = mod
SPEC.loader.exec_module(mod)

SHA = "1" * 40


def write_json(path, value):
    path.write_text(
        json.dumps(value, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )


class FakeLoader:
    def __init__(self, *, replay_counts=None):
        self.replay_counts = replay_counts or {"a": 10}
        self.calls = []

    def __call__(self, path, name):
        self.calls.append(path.name)
        if path.name == "capture_reference_l0.py":
            return types.SimpleNamespace(
                PINNED_LAYA_WHEEL_SHA256="w" * 64,
                PINNED_LAYA_WHEEL_SIZE=123,
                require_pinned_file=lambda path, **kwargs: {
                    "name": path.name,
                    "bytes": 123,
                    "sha256": "w" * 64,
                },
                require_runtime_dependencies=lambda: {"torch": "1"},
                expected_token_counts=lambda packet: {"a": 10},
                validate_choice11_diagnostic=lambda diagnostic, protocol: None,
            )
        if path.name == "capture_papaya_l0.py":
            return types.SimpleNamespace(
                PAPAYA_SOURCE_REVISION="2" * 40,
                PAPAYA_SOURCE_BLOBS={"x.py": "3" * 40},
                require_git_checkout=lambda root, sha, *args, **kwargs: {
                    "git_sha": sha,
                    "clean": True,
                    "source_blobs": {},
                },
                require_runtime_dependencies=lambda: {"torch": "1"},
                require_papaya_import=lambda root: {
                    "source_checkout_imported": True
                },
                require_sei_evidence_blob=lambda root: {
                    "binding_verified": True
                },
                require_llama_server=lambda path: {
                    "sha256": "l" * 64,
                    "version_verified": True,
                },
                verify_overlay=lambda here, root: (
                    {"valid": True},
                    {"schema": "overlay/v1"},
                ),
                verify_replay_inputs=lambda here, fixture: (
                    dict(self.replay_counts),
                    {"schema": "replay/v1"},
                ),
                validate_choice11_diagnostic=lambda diagnostic, protocol: None,
            )
        if path.name == "verify_reference_model_directory.py":
            return types.SimpleNamespace(
                validate_attestation=lambda packet: None,
                verify_model_directory=lambda root: {"valid": True},
            )
        if path.name == "protocol_contract.py":
            return types.SimpleNamespace(validate_fixture=lambda value: None)
        if path.name == "reference_token_fixture.py":
            return types.SimpleNamespace(
                validate_reference_token_fixture=lambda fixture, packet: None
            )
        if path.name == "choice11_sequence_attestation.py":
            return types.SimpleNamespace(
                validate_choice11_sequence=lambda diagnostic, packet, fixture_raw: None
            )
        if path.name == "evaluate_papaya_numeric_parity.py":
            return types.SimpleNamespace(
                _validate_policy=lambda policy: ({}, {})
            )
        raise AssertionError(path)


class PairPreflightTest(unittest.TestCase):
    def _tree(self, root):
        here = root / "evaluation" / "local-typed-comparator"
        here.mkdir(parents=True)
        payloads = {
            "reference_model_directory_attestation.v1.json": {"schema": "att"},
            "fixture.v1.json": {"schema": "fixture", "cases": []},
            "reference_token_fixture.v1.json": {"schema": "tokens", "cases": []},
            "papaya_choice11_diagnostic.v1.json": {
                "schema": "fixture",
                "cases": [],
            },
            "choice11_sequence_attestation.v1.json": {"schema": "choice11"},
            "papaya_numeric_parity_policy.v1.json": {"schema": "policy"},
        }
        for name, value in payloads.items():
            write_json(here / name, value)
        return here

    def _run(self, *, replay_counts=None):
        td = tempfile.TemporaryDirectory()
        root = Path(td.name)
        here = self._tree(root)
        old_fixture = mod.FIXTURE_SHA256
        old_diag = mod.CHOICE11_DIAGNOSTIC_SHA256
        mod.FIXTURE_SHA256 = mod._sha256((here / "fixture.v1.json").read_bytes())
        mod.CHOICE11_DIAGNOSTIC_SHA256 = mod._sha256(
            (here / "papaya_choice11_diagnostic.v1.json").read_bytes()
        )
        loader = FakeLoader(replay_counts=replay_counts)
        try:
            receipt = mod.run_preflight(
                here=here,
                source_sha=SHA,
                sei_source_dir=root / "sei",
                reference_model_dir=root / "reference-model",
                laya_runtime_wheel=root / "laya.whl",
                papaya_source_dir=root / "papaya",
                papaya_overlay_dir=root / "overlay",
                llama_binary=root / "llama-server",
                loader=loader,
            )
        finally:
            mod.FIXTURE_SHA256 = old_fixture
            mod.CHOICE11_DIAGNOSTIC_SHA256 = old_diag
        return td, receipt, loader

    def test_ready_receipt_keeps_live_claims_false(self):
        td, receipt, loader = self._run()
        try:
            self.assertEqual(receipt["status"], "ready")
            self.assertEqual(receipt["source"]["git_sha"], SHA)
            self.assertTrue(receipt["scope"]["all_required_inputs_verified"])
            self.assertFalse(receipt["scope"]["model_weights_loaded"])
            self.assertFalse(receipt["scope"]["live_reference_inference"])
            self.assertFalse(receipt["scope"]["live_papaya_inference"])
            self.assertIn("capture_reference_l0.py", loader.calls)
            self.assertIn("capture_papaya_l0.py", loader.calls)
        finally:
            td.cleanup()

    def test_reference_and_papaya_token_counts_must_match(self):
        td = tempfile.TemporaryDirectory()
        try:
            root = Path(td.name)
            here = self._tree(root)
            old_fixture = mod.FIXTURE_SHA256
            old_diag = mod.CHOICE11_DIAGNOSTIC_SHA256
            mod.FIXTURE_SHA256 = mod._sha256(
                (here / "fixture.v1.json").read_bytes()
            )
            mod.CHOICE11_DIAGNOSTIC_SHA256 = mod._sha256(
                (here / "papaya_choice11_diagnostic.v1.json").read_bytes()
            )
            try:
                with self.assertRaises(mod.PairPreflightError):
                    mod.run_preflight(
                        here=here,
                        source_sha=SHA,
                        sei_source_dir=root / "sei",
                        reference_model_dir=root / "reference-model",
                        laya_runtime_wheel=root / "laya.whl",
                        papaya_source_dir=root / "papaya",
                        papaya_overlay_dir=root / "overlay",
                        llama_binary=root / "llama-server",
                        loader=FakeLoader(replay_counts={"a": 11}),
                    )
            finally:
                mod.FIXTURE_SHA256 = old_fixture
                mod.CHOICE11_DIAGNOSTIC_SHA256 = old_diag
        finally:
            td.cleanup()

    def test_full_source_sha_is_required(self):
        with self.assertRaises(mod.PairPreflightError):
            mod._full_sha("abc")

    def test_script_checkout_must_equal_sei_source_dir(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            here = root / "sei" / "evaluation" / "local-typed-comparator"
            here.mkdir(parents=True)
            self.assertEqual(
                mod._require_script_source_binding(here, root / "sei"),
                (root / "sei").resolve(),
            )
            with self.assertRaises(mod.PairPreflightError):
                mod._require_script_source_binding(here, root / "other-sei")

    def test_output_must_be_new_and_external(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            sei = root / "sei"
            papaya = root / "papaya"
            sei.mkdir()
            papaya.mkdir()
            with self.assertRaises(mod.PairPreflightError):
                mod._external_output(
                    sei / "out.json",
                    sei_source_dir=sei,
                    papaya_source_dir=papaya,
                )
            existing = root / "existing.json"
            existing.write_text("x")
            with self.assertRaises(mod.PairPreflightError):
                mod._external_output(
                    existing,
                    sei_source_dir=sei,
                    papaya_source_dir=papaya,
                )
            expected = (root / "ready.json").resolve()
            self.assertEqual(
                mod._external_output(
                    expected,
                    sei_source_dir=sei,
                    papaya_source_dir=papaya,
                ),
                expected,
            )

    def test_atomic_writer_round_trip(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "receipt.json"
            mod._write_atomic(path, {"status": "ready"})
            self.assertEqual(
                json.loads(path.read_text()),
                {"status": "ready"},
            )
            self.assertFalse(path.with_name(path.name + ".tmp").exists())


if __name__ == "__main__":
    unittest.main()
