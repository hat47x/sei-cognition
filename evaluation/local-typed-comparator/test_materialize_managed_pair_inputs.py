import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from contextlib import ExitStack
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
REFERENCE_MANIFEST = {"schema": "reference"}
REFERENCE_RAW = b'{"schema":"reference"}'
PAPAYA_MANIFEST = {"schema": "papaya"}
PAPAYA_RAW = b'{"schema":"papaya"}'
REFERENCE_BYTES = 10
PAPAYA_BYTES = 5


def reference_receipt(output: Path):
    return {
        "schema": mod.reference_materializer.SCHEMA,
        "status": "materialized-and-verified",
        "transport_id": mod.reference_materializer.HF_ID,
        "output_dir": str(output.resolve()),
        "files": [
            {
                "path": "model.safetensors",
                "bytes": 1,
                "sha256": "a" * 64,
            }
        ],
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


def runtime_receipt(output: Path, manifest_raw: bytes):
    return {
        "schema": mod.runtime_materializer.SCHEMA,
        "status": "materialized-and-verified",
        "wheelhouse_manifest_sha256": hashlib.sha256(manifest_raw).hexdigest(),
        "wheelhouse": {"valid": True},
        "install": {"returncode": 0},
        "environment_verification": {"valid": True},
        "scope": {
            "host_assisted_environment": True,
            "transported_wheel_installation_origin_attested": True,
            "runtime_installation_origin_attested": False,
            "host_dependency_versions_pinned": False,
            "self_contained_runtime": False,
            "environment_relocatable": False,
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
        "files": [
            {
                "path": "tokenizer.json",
                "bytes": 1,
                "sha256": "b" * 64,
            }
        ],
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
    def _install_common_patches(
        self,
        stack: ExitStack,
        events: list[str] | None = None,
        attempts_seen: list[tuple[str, int]] | None = None,
    ):
        stack.enter_context(
            mock.patch.object(
                mod.papaya_capture,
                "require_git_checkout",
                return_value={"git_sha": SHA, "clean": True},
            )
        )
        stack.enter_context(
            mock.patch.object(
                mod.reference_materializer,
                "validate_manifest",
                return_value={
                    mod.reference_materializer.HF_ID: [
                        {"path": "model.safetensors", "bytes": REFERENCE_BYTES}
                    ]
                },
            )
        )
        stack.enter_context(
            mock.patch.object(
                mod.papaya_materializer,
                "validate_manifest",
                return_value=[
                    {
                        "role": "attested_tokenizer",
                        "path": "tokenizer.json",
                        "bytes": PAPAYA_BYTES,
                    }
                ],
            )
        )

        def ref_materialize(
            _manifest, _transport, output, *, timeout, attempts
        ):
            if events is not None:
                events.append("reference")
            if attempts_seen is not None:
                attempts_seen.append(("reference", attempts))
            output.mkdir()
            return reference_receipt(output)

        def pap_materialize(_manifest, output, *, timeout, attempts):
            if events is not None:
                events.append("papaya")
            if attempts_seen is not None:
                attempts_seen.append(("papaya", attempts))
            output.mkdir()
            (output / "tokenizer.json").write_bytes(b"tokenizer")
            for spec in mod.overlay.DEFAULT_ARTIFACTS:
                if spec.role in ("q8_backbone", "decision_head"):
                    path = output / spec.relative_path
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(spec.role.encode("ascii"))
            return papaya_receipt(output)

        stack.enter_context(
            mock.patch.object(
                mod.reference_materializer,
                "materialize_reference_model",
                side_effect=ref_materialize,
            )
        )
        stack.enter_context(
            mock.patch.object(
                mod.papaya_materializer,
                "materialize_papaya_candidate",
                side_effect=pap_materialize,
            )
        )

        def materialize_runtime(
            _manifest, _raw, _wheelhouse, output, **kwargs
        ):
            if events is not None:
                events.append("runtime")
            output.mkdir()
            (output / "bin").mkdir()
            (output / "bin" / "python").write_bytes(b"python")
            return runtime_receipt(output, _raw)

        stack.enter_context(
            mock.patch.object(
                mod.runtime_materializer,
                "materialize_environment",
                side_effect=materialize_runtime,
            )
        )

        def prepare_overlay(candidate, tokenizer, output):
            self.assertTrue(candidate.is_dir())
            self.assertEqual(tokenizer, candidate / "tokenizer.json")
            output.mkdir()
            for spec in mod.overlay.DEFAULT_ARTIFACTS:
                if spec.role in ("q8_backbone", "decision_head"):
                    staged = output / spec.relative_path
                    staged.parent.mkdir(parents=True, exist_ok=True)
                    staged.symlink_to(
                        (candidate / spec.relative_path).resolve()
                    )
            return {"schema": mod.overlay.SCHEMA, "scope": {}}

        stack.enter_context(
            mock.patch.object(
                mod.overlay,
                "prepare_overlay",
                side_effect=prepare_overlay,
            )
        )
        stack.enter_context(
            mock.patch.object(
                mod.overlay,
                "verify_prepared_overlay",
                return_value={
                    "valid": True,
                    "schema": mod.overlay.SCHEMA,
                },
            )
        )

    def _prepare(
        self,
        root: Path,
        *,
        runtime_wheelhouse_dir=None,
        runtime_wheelhouse_manifest=None,
        runtime_wheelhouse_manifest_raw=None,
        materialize_runtime_environment=False,
        events=None,
        attempts=mod.DEFAULT_DOWNLOAD_ATTEMPTS,
        attempts_seen=None,
        disk_reserve_bytes=mod.DEFAULT_DISK_RESERVE_BYTES,
    ):
        source = root / "sei"
        source.mkdir()
        output = root / "workspace"
        with ExitStack() as stack:
            self._install_common_patches(
                stack,
                events=events,
                attempts_seen=attempts_seen,
            )
            receipt = mod.prepare_workspace(
                source_sha=SHA,
                sei_source_dir=source,
                reference_manifest=REFERENCE_MANIFEST,
                reference_manifest_raw=REFERENCE_RAW,
                reference_transport=mod.reference_materializer.HF_ID,
                papaya_manifest=PAPAYA_MANIFEST,
                papaya_manifest_raw=PAPAYA_RAW,
                output_dir=output,
                timeout=30.0,
                attempts=attempts,
                disk_reserve_bytes=disk_reserve_bytes,
                runtime_wheelhouse_dir=runtime_wheelhouse_dir,
                runtime_wheelhouse_manifest=runtime_wheelhouse_manifest,
                runtime_wheelhouse_manifest_raw=runtime_wheelhouse_manifest_raw,
                materialize_runtime_environment=(
                    materialize_runtime_environment
                ),
            )
        return source, output, receipt

    def test_success_writes_portable_receipt(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _source, output, receipt = self._prepare(root)

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
            self.assertTrue(
                receipt["papaya_overlay"]["workspace_binding"]["valid"]
            )
            self.assertTrue(
                receipt["papaya_overlay"]["workspace_binding"][
                    "absolute_symlink_targets"
                ]
            )
            self.assertFalse(
                receipt["papaya_overlay"]["workspace_binding"][
                    "workspace_relocatable"
                ]
            )
            self.assertFalse(receipt["scope"]["workspace_relocatable"])
            self.assertFalse(
                receipt["scope"]["runtime_environment_materialized"]
            )
            self.assertFalse(
                receipt["scope"][
                    "transported_wheel_installation_origin_attested"
                ]
            )
            self.assertFalse(
                receipt["scope"]["runtime_installation_origin_attested"]
            )
            self.assertFalse(receipt["scope"]["model_weights_loaded"])
            self.assertFalse(receipt["scope"]["live_reference_inference"])
            self.assertFalse(receipt["scope"]["live_papaya_inference"])
            self.assertEqual(
                receipt["disk_capacity"]["required_model_input_bytes"],
                REFERENCE_BYTES + PAPAYA_BYTES,
            )
            self.assertEqual(
                receipt["disk_capacity"]["reserve_bytes"],
                mod.DEFAULT_DISK_RESERVE_BYTES,
            )
            self.assertEqual(
                receipt["disk_capacity"]["required_free_bytes"],
                REFERENCE_BYTES
                + PAPAYA_BYTES
                + mod.DEFAULT_DISK_RESERVE_BYTES,
            )
            self.assertGreaterEqual(
                receipt["disk_capacity"][
                    "observed_free_bytes_before_model_transfer"
                ],
                receipt["disk_capacity"]["required_free_bytes"],
            )
            self.assertTrue(receipt["disk_capacity"]["sufficient"])

    def test_download_attempt_policy_is_shared_and_retained(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            attempts_seen: list[tuple[str, int]] = []
            _source, _output, receipt = self._prepare(
                root,
                attempts=5,
                attempts_seen=attempts_seen,
            )
            self.assertEqual(
                attempts_seen,
                [("reference", 5), ("papaya", 5)],
            )
            self.assertEqual(
                receipt["download_policy"],
                {
                    "attempts_per_file": 5,
                    "restart_from_zero": True,
                    "retryable_failures": "transport/read only",
                    "integrity_failures_retried": False,
                },
            )

    def test_invalid_attempt_policy_fails_before_workspace_creation(self):
        for attempts in (0, -1, True):
            with tempfile.TemporaryDirectory() as td:
                root = Path(td)
                source = root / "sei"
                source.mkdir()
                output = root / "workspace"
                with self.subTest(attempts=attempts), self.assertRaisesRegex(
                    mod.ManagedPairMaterializationError,
                    "attempts must be an integer >= 1",
                ):
                    mod.prepare_workspace(
                        source_sha=SHA,
                        sei_source_dir=source,
                        reference_manifest=REFERENCE_MANIFEST,
                        reference_manifest_raw=REFERENCE_RAW,
                        reference_transport=mod.reference_materializer.HF_ID,
                        papaya_manifest=PAPAYA_MANIFEST,
                        papaya_manifest_raw=PAPAYA_RAW,
                        output_dir=output,
                        timeout=30.0,
                        attempts=attempts,
                    )
                self.assertFalse(output.exists())

    def test_materializer_default_attempt_policy_must_match(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "sei"
            source.mkdir()
            output = root / "workspace"
            with mock.patch.object(
                mod.papaya_materializer,
                "DEFAULT_ATTEMPTS",
                mod.reference_materializer.DEFAULT_ATTEMPTS + 1,
            ):
                with self.assertRaisesRegex(
                    mod.ManagedPairMaterializationError,
                    "default download-attempt policy drift",
                ):
                    mod.prepare_workspace(
                        source_sha=SHA,
                        sei_source_dir=source,
                        reference_manifest=REFERENCE_MANIFEST,
                        reference_manifest_raw=REFERENCE_RAW,
                        reference_transport=mod.reference_materializer.HF_ID,
                        papaya_manifest=PAPAYA_MANIFEST,
                        papaya_manifest_raw=PAPAYA_RAW,
                        output_dir=output,
                        timeout=30.0,
                    )
            self.assertFalse(output.exists())

    def test_insufficient_disk_stops_before_model_transfer(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            attempts_seen: list[tuple[str, int]] = []
            with mock.patch.object(
                mod.shutil,
                "disk_usage",
                return_value=mock.Mock(
                    free=REFERENCE_BYTES + PAPAYA_BYTES - 1
                ),
            ):
                with self.assertRaisesRegex(
                    mod.ManagedPairMaterializationError,
                    "insufficient free disk before model transfer",
                ):
                    self._prepare(
                        root,
                        disk_reserve_bytes=0,
                        attempts_seen=attempts_seen,
                    )
            self.assertEqual(attempts_seen, [])
            self.assertFalse((root / "workspace").exists())

    def test_disk_gate_runs_after_optional_runtime_environment(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            wheelhouse = root / "wheelhouse"
            wheelhouse.mkdir()
            events: list[str] = []
            with mock.patch.object(
                mod.wheelhouse_verifier,
                "verify_wheelhouse",
                return_value={"valid": True},
            ), mock.patch.object(
                mod.shutil,
                "disk_usage",
                return_value=mock.Mock(free=0),
            ):
                with self.assertRaisesRegex(
                    mod.ManagedPairMaterializationError,
                    "insufficient free disk before model transfer",
                ):
                    self._prepare(
                        root,
                        runtime_wheelhouse_dir=wheelhouse,
                        runtime_wheelhouse_manifest={"schema": "wheelhouse"},
                        runtime_wheelhouse_manifest_raw=b'{"schema":"wheelhouse"}',
                        materialize_runtime_environment=True,
                        events=events,
                        disk_reserve_bytes=0,
                    )
            self.assertEqual(events, ["runtime"])
            self.assertFalse((root / "workspace").exists())

    def test_invalid_disk_reserve_fails_before_workspace_creation(self):
        for reserve in (-1, True):
            with tempfile.TemporaryDirectory() as td:
                root = Path(td)
                source = root / "sei"
                source.mkdir()
                output = root / "workspace"
                with self.subTest(reserve=reserve), self.assertRaisesRegex(
                    mod.ManagedPairMaterializationError,
                    "disk-reserve-bytes must be an integer >= 0",
                ):
                    mod.prepare_workspace(
                        source_sha=SHA,
                        sei_source_dir=source,
                        reference_manifest=REFERENCE_MANIFEST,
                        reference_manifest_raw=REFERENCE_RAW,
                        reference_transport=mod.reference_materializer.HF_ID,
                        papaya_manifest=PAPAYA_MANIFEST,
                        papaya_manifest_raw=PAPAYA_RAW,
                        output_dir=output,
                        timeout=30.0,
                        disk_reserve_bytes=reserve,
                    )
                self.assertFalse(output.exists())

    def test_papaya_failure_removes_entire_workspace(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "sei"
            source.mkdir()
            output = root / "workspace"
            with ExitStack() as stack:
                self._install_common_patches(stack)
                stack.enter_context(
                    mock.patch.object(
                        mod.papaya_materializer,
                        "materialize_papaya_candidate",
                        side_effect=RuntimeError(
                            "synthetic Papaya failure"
                        ),
                    )
                )
                with self.assertRaises(RuntimeError):
                    mod.prepare_workspace(
                        source_sha=SHA,
                        sei_source_dir=source,
                        reference_manifest=REFERENCE_MANIFEST,
                        reference_manifest_raw=REFERENCE_RAW,
                        reference_transport=mod.reference_materializer.HF_ID,
                        papaya_manifest=PAPAYA_MANIFEST,
                        papaya_manifest_raw=PAPAYA_RAW,
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
            with ExitStack() as stack:
                self._install_common_patches(stack)
                stack.enter_context(
                    mock.patch.object(
                        mod.overlay,
                        "prepare_overlay",
                        side_effect=RuntimeError(
                            "synthetic overlay failure"
                        ),
                    )
                )
                with self.assertRaises(RuntimeError):
                    mod.prepare_workspace(
                        source_sha=SHA,
                        sei_source_dir=source,
                        reference_manifest=REFERENCE_MANIFEST,
                        reference_manifest_raw=REFERENCE_RAW,
                        reference_transport=mod.reference_materializer.HF_ID,
                        papaya_manifest=PAPAYA_MANIFEST,
                        papaya_manifest_raw=PAPAYA_RAW,
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
            wheel_manifest = {"schema": "wheelhouse"}
            wheel_raw = b'{"schema":"wheelhouse"}'

            with ExitStack() as stack:
                self._install_common_patches(stack)
                stack.enter_context(
                    mock.patch.object(
                        mod.wheelhouse_verifier,
                        "verify_wheelhouse",
                        return_value={
                            "valid": True,
                            "scope": {
                                "transport_candidate_only": True
                            },
                        },
                    )
                )
                receipt = mod.prepare_workspace(
                    source_sha=SHA,
                    sei_source_dir=source,
                    reference_manifest=REFERENCE_MANIFEST,
                    reference_manifest_raw=REFERENCE_RAW,
                    reference_transport=mod.reference_materializer.HF_ID,
                    papaya_manifest=PAPAYA_MANIFEST,
                    papaya_manifest_raw=PAPAYA_RAW,
                    output_dir=output,
                    timeout=30.0,
                    runtime_wheelhouse_dir=wheelhouse,
                    runtime_wheelhouse_manifest=wheel_manifest,
                    runtime_wheelhouse_manifest_raw=wheel_raw,
                )

            self.assertTrue(receipt["runtime_wheelhouse"]["provided"])
            self.assertFalse(
                receipt["runtime_wheelhouse"]["external_path_retained"]
            )
            self.assertTrue(receipt["scope"]["runtime_wheelhouse_verified"])

    def test_runtime_environment_is_materialized_before_models(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            wheelhouse = root / "wheelhouse"
            wheelhouse.mkdir()
            wheel_manifest = {"schema": "wheelhouse"}
            wheel_raw = b'{"schema":"wheelhouse"}'
            events: list[str] = []

            with mock.patch.object(
                mod.wheelhouse_verifier,
                "verify_wheelhouse",
                return_value={"valid": True},
            ):
                _source, output, receipt = self._prepare(
                    root,
                    runtime_wheelhouse_dir=wheelhouse,
                    runtime_wheelhouse_manifest=wheel_manifest,
                    runtime_wheelhouse_manifest_raw=wheel_raw,
                    materialize_runtime_environment=True,
                    events=events,
                )

            self.assertEqual(
                events[:3], ["runtime", "reference", "papaya"]
            )
            self.assertTrue((output / mod.RUNTIME_ENV_DIR).is_dir())
            self.assertEqual(
                receipt["layout"]["runtime_environment_dir"],
                mod.RUNTIME_ENV_DIR,
            )
            self.assertTrue(
                receipt["runtime_environment"]["provided"]
            )
            self.assertTrue(
                receipt["scope"]["runtime_environment_materialized"]
            )
            self.assertTrue(
                receipt["scope"][
                    "transported_wheel_installation_origin_attested"
                ]
            )
            self.assertFalse(
                receipt["scope"]["runtime_installation_origin_attested"]
            )

    def test_runtime_receipt_binding_drift_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            wheelhouse = root / "wheelhouse"
            wheelhouse.mkdir()
            wheel_manifest = {"schema": "wheelhouse"}
            wheel_raw = b'{"schema":"wheelhouse"}'

            cases = []

            bad = runtime_receipt(root / "unused", wheel_raw)
            bad["wheelhouse_manifest_sha256"] = "0" * 64
            cases.append(bad)

            bad = runtime_receipt(root / "unused", wheel_raw)
            bad["wheelhouse"]["valid"] = False
            cases.append(bad)

            bad = runtime_receipt(root / "unused", wheel_raw)
            bad["install"]["returncode"] = 1
            cases.append(bad)

            bad = runtime_receipt(root / "unused", wheel_raw)
            bad["environment_verification"]["valid"] = False
            cases.append(bad)

            for index, bad_receipt in enumerate(cases):
                with self.subTest(index=index):
                    output = root / f"workspace-{index}"
                    source = root / f"sei-{index}"
                    source.mkdir()
                    with ExitStack() as stack:
                        self._install_common_patches(stack)
                        stack.enter_context(
                            mock.patch.object(
                                mod.wheelhouse_verifier,
                                "verify_wheelhouse",
                                return_value={"valid": True},
                            )
                        )
                        stack.enter_context(
                            mock.patch.object(
                                mod.runtime_materializer,
                                "materialize_environment",
                                return_value=bad_receipt,
                            )
                        )
                        with self.assertRaises(
                            mod.ManagedPairMaterializationError
                        ):
                            mod.prepare_workspace(
                                source_sha=SHA,
                                sei_source_dir=source,
                                reference_manifest=REFERENCE_MANIFEST,
                                reference_manifest_raw=REFERENCE_RAW,
                                reference_transport=(
                                    mod.reference_materializer.HF_ID
                                ),
                                papaya_manifest=PAPAYA_MANIFEST,
                                papaya_manifest_raw=PAPAYA_RAW,
                                output_dir=output,
                                timeout=30.0,
                                runtime_wheelhouse_dir=wheelhouse,
                                runtime_wheelhouse_manifest=wheel_manifest,
                                runtime_wheelhouse_manifest_raw=wheel_raw,
                                materialize_runtime_environment=True,
                            )
                    self.assertFalse(output.exists())

    def test_runtime_environment_requires_wheelhouse_before_workspace(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "sei"
            source.mkdir()
            output = root / "workspace"
            with self.assertRaisesRegex(
                mod.ManagedPairMaterializationError,
                "requires runtime wheelhouse",
            ):
                mod.prepare_workspace(
                    source_sha=SHA,
                    sei_source_dir=source,
                    reference_manifest=REFERENCE_MANIFEST,
                    reference_manifest_raw=REFERENCE_RAW,
                    reference_transport=mod.reference_materializer.HF_ID,
                    papaya_manifest=PAPAYA_MANIFEST,
                    papaya_manifest_raw=PAPAYA_RAW,
                    output_dir=output,
                    timeout=30.0,
                    materialize_runtime_environment=True,
                )
            self.assertFalse(output.exists())

    def test_runtime_environment_failure_stops_before_model_transfer(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "sei"
            source.mkdir()
            wheelhouse = root / "wheelhouse"
            wheelhouse.mkdir()
            output = root / "workspace"
            wheel_manifest = {"schema": "wheelhouse"}
            wheel_raw = b'{"schema":"wheelhouse"}'
            events: list[str] = []

            with ExitStack() as stack:
                self._install_common_patches(stack, events=events)
                stack.enter_context(
                    mock.patch.object(
                        mod.wheelhouse_verifier,
                        "verify_wheelhouse",
                        return_value={"valid": True},
                    )
                )
                stack.enter_context(
                    mock.patch.object(
                        mod.runtime_materializer,
                        "materialize_environment",
                        side_effect=RuntimeError(
                            "synthetic runtime failure"
                        ),
                    )
                )
                with self.assertRaises(RuntimeError):
                    mod.prepare_workspace(
                        source_sha=SHA,
                        sei_source_dir=source,
                        reference_manifest=REFERENCE_MANIFEST,
                        reference_manifest_raw=REFERENCE_RAW,
                        reference_transport=mod.reference_materializer.HF_ID,
                        papaya_manifest=PAPAYA_MANIFEST,
                        papaya_manifest_raw=PAPAYA_RAW,
                        output_dir=output,
                        timeout=30.0,
                        runtime_wheelhouse_dir=wheelhouse,
                        runtime_wheelhouse_manifest=wheel_manifest,
                        runtime_wheelhouse_manifest_raw=wheel_raw,
                        materialize_runtime_environment=True,
                    )

            self.assertEqual(events, [])
            self.assertFalse(output.exists())

    def test_invalid_wheelhouse_fails_before_workspace_creation(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "sei"
            source.mkdir()
            wheelhouse = root / "wheelhouse"
            wheelhouse.mkdir()
            output = root / "workspace"
            with ExitStack() as stack:
                self._install_common_patches(stack)
                stack.enter_context(
                    mock.patch.object(
                        mod.wheelhouse_verifier,
                        "verify_wheelhouse",
                        return_value={"valid": False},
                    )
                )
                with self.assertRaises(
                    mod.ManagedPairMaterializationError
                ):
                    mod.prepare_workspace(
                        source_sha=SHA,
                        sei_source_dir=source,
                        reference_manifest=REFERENCE_MANIFEST,
                        reference_manifest_raw=REFERENCE_RAW,
                        reference_transport=mod.reference_materializer.HF_ID,
                        papaya_manifest=PAPAYA_MANIFEST,
                        papaya_manifest_raw=PAPAYA_RAW,
                        output_dir=output,
                        timeout=30.0,
                        runtime_wheelhouse_dir=wheelhouse,
                        runtime_wheelhouse_manifest={"schema": "wheelhouse"},
                        runtime_wheelhouse_manifest_raw=b'{"schema":"wheelhouse"}',
                    )
            self.assertFalse(output.exists())

    def test_manifest_object_raw_binding_is_required(self):
        with self.assertRaises(mod.ManagedPairMaterializationError):
            mod._require_raw_binding(
                {"schema": "expected"},
                b'{"schema":"different"}',
                "test manifest",
            )

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
                with self.assertRaises(
                    mod.ManagedPairMaterializationError
                ):
                    mod.prepare_workspace(
                        source_sha=SHA,
                        sei_source_dir=source,
                        reference_manifest=REFERENCE_MANIFEST,
                        reference_manifest_raw=REFERENCE_RAW,
                        reference_transport=mod.reference_materializer.HF_ID,
                        papaya_manifest=PAPAYA_MANIFEST,
                        papaya_manifest_raw=PAPAYA_RAW,
                        output_dir=output,
                        timeout=30.0,
                    )
            self.assertFalse(output.exists())

    def test_overlay_workspace_binding_rejects_non_symlink(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            candidate = root / "candidate"
            staged = root / "overlay"
            candidate.mkdir()
            staged.mkdir()
            for spec in mod.overlay.DEFAULT_ARTIFACTS:
                if spec.role in ("q8_backbone", "decision_head"):
                    source = candidate / spec.relative_path
                    source.parent.mkdir(parents=True, exist_ok=True)
                    source.write_bytes(b"source")
                    target = staged / spec.relative_path
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(b"copy")
            with self.assertRaises(
                mod.ManagedPairMaterializationError
            ):
                mod._verify_overlay_workspace_binding(candidate, staged)

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
