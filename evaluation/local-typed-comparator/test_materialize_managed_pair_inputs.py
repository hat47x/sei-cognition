import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "materialize_managed_pair_inputs",
    HERE / "materialize_managed_pair_inputs.py",
)
mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = mod
SPEC.loader.exec_module(mod)

SHA = "1" * 40


def reference_receipt(output: Path):
    return {
        "schema": mod.reference_materializer.SCHEMA,
        "status": "materialized-and-verified",
        "transport_id": mod.reference_materializer.HF_ID,
        "output_dir": str(output.resolve()),
        "files": [{"path": "model.safetensors", "bytes": 1, "sha256": "a" * 64}],
        "directory_verification": {"valid": True},
        "scope": {
            "model_bytes_materialized": True,
            "model_directory_verified": True,
            "model_weights_loaded": False,
            "live_inference": False,
            "numeric_parity": False,
            "shipping_decision": False,
        },
    }


def papaya_receipt(output: Path):
    return {
        "schema": mod.papaya_materializer.SCHEMA,
        "status": "materialized-and-verified",
        "transport_id": mod.papaya_materializer.TRANSPORT_ID,
        "output_dir": str(output.resolve()),
        "files": [{"path": "tokenizer.json", "bytes": 1, "sha256": "b" * 64}],
        "candidate_input_verification": {"valid": True},
        "scope": {
            "candidate_bytes_materialized": True,
            "candidate_inputs_verified": True,
            "compatibility_overlay_prepared": False,
            "model_weights_loaded": False,
            "live_inference": False,
            "numeric_parity": False,
            "shipping_decision": False,
        },
    }


class ManagedPairInputMaterializationTest(unittest.TestCase):
    def _patches(self):
        source = mock.patch.object(
            mod.papaya_capture,
            "require_git_checkout",
            return_value={"git_sha": SHA, "clean": True},
        )
        ref_validate = mock.patch.object(
            mod.reference_materializer,
            "validate_manifest",
            return_value={mod.reference_materializer.HF_ID: []},
        )
        pap_validate = mock.patch.object(
            mod.papaya_materializer,
            "validate_manifest",
            return_value=[
                {
                    "role": "attested_tokenizer",
                    "path": "tokenizer.json",
                }
            ],
        )

        def ref_materialize(_manifest, _transport, output, *, timeout):
            output.mkdir()
            return reference_receipt(output)

        def pap_materialize(_manifest, output, *, timeout):
            output.mkdir()
            (output / "tokenizer.json").write_bytes(b"tokenizer")
            return papaya_receipt(output)

        ref_mat = mock.patch.object(
            mod.reference_materializer,
            "materialize_reference_model",
            side_effect=ref_materialize,
        )
        pap_mat = mock.patch.object(
            mod.papaya_materializer,
            "materialize_papaya_candidate",
            side_effect=pap_materialize,
        )

        def prepare_overlay(candidate, tokenizer, output):
            self.assertTrue(candidate.is_dir())
            self.assertEqual(tokenizer, candidate / "tokenizer.json")
            output.mkdir()
            return {"schema": mod.overlay.SCHEMA, "scope": {}}

        overlay_prepare = mock.patch.object(
            mod.overlay,
            "prepare_overlay",
            side_effect=prepare_overlay,
        )
        overlay_verify = mock.patch.object(
            mod.overlay,
            "verify_prepared_overlay",
            return_value={"valid": True, "schema": mod.overlay.SCHEMA},
        )
        return (
            source,
            ref_validate,
            pap_validate,
            ref_mat,
            pap_mat,
            overlay_prepare,
            overlay_verify,
        )

    def _run(self, root: Path, **kwargs):
        source = root / "sei"
        source.mkdir()
        output = root / "workspace"
        with self._patches()[0] as _src,              self._patches()[1] as _rv,              self._patches()[2] as _pv,              self._patches()[3] as _rm,              self._patches()[4] as _pm,              self._patches()[5] as _op,              self._patches()[6] as _ov:
            return mod.prepare_workspace(
                source_sha=SHA,
                sei_source_dir=source,
                reference_manifest={"schema": "reference"},
                reference_manifest_raw=b'{"schema":"reference"}',
                reference_transport=mod.reference_materializer.HF_ID,
                papaya_manifest={"schema": "papaya"},
                papaya_manifest_raw=b'{"schema":"papaya"}',
                output_dir=output,
                timeout=30.0,
                **kwargs,
            )

    def test_success_writes_portable_receipt(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "sei"
            source.mkdir()
            output = root / "workspace"

            patches = self._patches()
            with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5], patches[6]:
                receipt = mod.prepare_workspace(
                    source_sha=SHA,
                    sei_source_dir=source,
                    reference_manifest={"schema": "reference"},
                    reference_manifest_raw=b'{"schema":"reference"}',
                    reference_transport=mod.reference_materializer.HF_ID,
                    papaya_manifest={"schema": "papaya"},
                    papaya_manifest_raw=b'{"schema":"papaya"}',
                    output_dir=output,
                    timeout=30.0,
                )

            self.assertEqual(
                receipt["status"], "ready-for-managed-pair-preflight"
            )
            self.assertTrue((output / mod.REFERENCE_DIR).is_dir())
            self.assertTrue((output / mod.PAPAYA_CANDIDATE_DIR).is_dir())
            self.assertTrue((output / mod.PAPAYA_OVERLAY_DIR).is_dir())
            retained = json.loads(
                (output / mod.RECEIPT_FILE).read_text(encoding="utf-8")
            )
            self.assertEqual(retained, receipt)
            rendered = json.dumps(receipt)
            self.assertNotIn(str(output.resolve()), rendered)
            self.assertNotIn("output_dir", receipt["reference"])
            self.assertNotIn("output_dir", receipt["papaya_candidate"])
            self.assertFalse(
                receipt["scope"]["runtime_installation_origin_attested"]
            )
            self.assertFalse(receipt["scope"]["model_weights_loaded"])
            self.assertFalse(receipt["scope"]["live_reference_inference"])
            self.assertFalse(receipt["scope"]["live_papaya_inference"])

    def test_papaya_failure_removes_entire_workspace(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "sei"
            source.mkdir()
            output = root / "workspace"
            patches = self._patches()
            with patches[0], patches[1], patches[2], patches[3],                  mock.patch.object(
                     mod.papaya_materializer,
                     "materialize_papaya_candidate",
                     side_effect=RuntimeError("synthetic Papaya failure"),
                 ), patches[5], patches[6]:
                with self.assertRaises(RuntimeError):
                    mod.prepare_workspace(
                        source_sha=SHA,
                        sei_source_dir=source,
                        reference_manifest={},
                        reference_manifest_raw=b"{}",
                        reference_transport=mod.reference_materializer.HF_ID,
                        papaya_manifest={},
                        papaya_manifest_raw=b"{}",
                        output_dir=output,
                        timeout=30.0,
                    )
            self.assertFalse(output.exists())

    def test_overlay_failure_removes_materialized_model_dirs(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "sei"
            source.mkdir()
            output = root / "workspace"
            patches = self._patches()
            with patches[0], patches[1], patches[2], patches[3], patches[4],                  mock.patch.object(
                     mod.overlay,
                     "prepare_overlay",
                     side_effect=RuntimeError("synthetic overlay failure"),
                 ), patches[6]:
                with self.assertRaises(RuntimeError):
                    mod.prepare_workspace(
                        source_sha=SHA,
                        sei_source_dir=source,
                        reference_manifest={},
                        reference_manifest_raw=b"{}",
                        reference_transport=mod.reference_materializer.HF_ID,
                        papaya_manifest={},
                        papaya_manifest_raw=b"{}",
                        output_dir=output,
                        timeout=30.0,
                    )
            self.assertFalse(output.exists())

    def test_optional_wheelhouse_is_verified_before_workspace_creation(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "sei"
            source.mkdir()
            wheelhouse = root / "wheelhouse"
            wheelhouse.mkdir()
            output = root / "workspace"
            patches = self._patches()

            with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5], patches[6],                  mock.patch.object(
                     mod.wheelhouse_verifier,
                     "verify_wheelhouse",
                     return_value={"valid": True, "scope": {"transport_candidate_only": True}},
                 ):
                receipt = mod.prepare_workspace(
                    source_sha=SHA,
                    sei_source_dir=source,
                    reference_manifest={},
                    reference_manifest_raw=b"{}",
                    reference_transport=mod.reference_materializer.HF_ID,
                    papaya_manifest={},
                    papaya_manifest_raw=b"{}",
                    output_dir=output,
                    timeout=30.0,
                    runtime_wheelhouse_dir=wheelhouse,
                    runtime_wheelhouse_manifest={"schema": "wheelhouse"},
                    runtime_wheelhouse_manifest_raw=b'{"schema":"wheelhouse"}',
                )
            self.assertTrue(receipt["runtime_wheelhouse"]["provided"])
            self.assertFalse(
                receipt["runtime_wheelhouse"]["external_path_retained"]
            )
            self.assertTrue(receipt["scope"]["runtime_wheelhouse_verified"])

    def test_invalid_wheelhouse_fails_before_workspace_creation(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "sei"
            source.mkdir()
            wheelhouse = root / "wheelhouse"
            wheelhouse.mkdir()
            output = root / "workspace"
            patches = self._patches()
            with patches[0], patches[1], patches[2],                  mock.patch.object(
                     mod.wheelhouse_verifier,
                     "verify_wheelhouse",
                     return_value={"valid": False},
                 ):
                with self.assertRaises(mod.ManagedPairMaterializationError):
                    mod.prepare_workspace(
                        source_sha=SHA,
                        sei_source_dir=source,
                        reference_manifest={},
                        reference_manifest_raw=b"{}",
                        reference_transport=mod.reference_materializer.HF_ID,
                        papaya_manifest={},
                        papaya_manifest_raw=b"{}",
                        output_dir=output,
                        timeout=30.0,
                        runtime_wheelhouse_dir=wheelhouse,
                        runtime_wheelhouse_manifest={"schema": "wheelhouse"},
                        runtime_wheelhouse_manifest_raw=b"{}",
                    )
            self.assertFalse(output.exists())

    def test_existing_or_source_internal_workspace_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "sei"
            source.mkdir()
            existing = root / "existing"
            existing.mkdir()
            with self.assertRaises(mod.ManagedPairMaterializationError):
                mod._new_external_workspace(existing, source)
            with self.assertRaises(mod.ManagedPairMaterializationError):
                mod._new_external_workspace(source / "models", source)

    def test_source_checkout_drift_is_rejected_before_workspace(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "sei"
            source.mkdir()
            output = root / "workspace"
            with mock.patch.object(
                mod.papaya_capture,
                "require_git_checkout",
                return_value={"git_sha": "2" * 40, "clean": True},
            ):
                with self.assertRaises(mod.ManagedPairMaterializationError):
                    mod.prepare_workspace(
                        source_sha=SHA,
                        sei_source_dir=source,
                        reference_manifest={},
                        reference_manifest_raw=b"{}",
                        reference_transport=mod.reference_materializer.HF_ID,
                        papaya_manifest={},
                        papaya_manifest_raw=b"{}",
                        output_dir=output,
                        timeout=30.0,
                    )
            self.assertFalse(output.exists())

    def test_papaya_transport_must_have_one_attested_tokenizer(self):
        with self.assertRaises(mod.ManagedPairMaterializationError):
            mod._attested_tokenizer_relative_path([])
        with self.assertRaises(mod.ManagedPairMaterializationError):
            mod._attested_tokenizer_relative_path(
                [
                    {"role": "attested_tokenizer", "path": "a.json"},
                    {"role": "attested_tokenizer", "path": "b.json"},
                ]
            )


if __name__ == "__main__":
    unittest.main()
