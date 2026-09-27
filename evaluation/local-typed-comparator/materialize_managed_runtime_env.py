#!/usr/bin/env python3
"""Materialize a host-assisted managed runtime from the retained exact wheels.

The environment uses a venv with system site packages enabled so host-provided
torch/huggingface-hub/numpy/fastapi/uvicorn remain explicitly host-assisted.
Only the four retained wheels (Laya, Transformers, tokenizers, safetensors) are
installed with no-index/no-deps and receive installation-origin attestation.

This is an evaluation runtime helper, not a product/runtime lock.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import urllib.parse
import venv
from pathlib import Path
from typing import Any, Callable, Sequence

import verify_runtime_dependency_wheelhouse as wheelhouse_verifier

SCHEMA = "sei.local-typed-comparator-managed-runtime-environment/v1"
RECEIPT_FILE = "sei_managed_runtime_environment.json"
TRANSPORTED_DISTRIBUTIONS = (
    "laya",
    "transformers",
    "tokenizers",
    "safetensors",
)
IMPORT_MODULES = {
    "laya": "laya",
    "transformers": "transformers",
    "tokenizers": "tokenizers",
    "safetensors": "safetensors",
}


class ManagedRuntimeEnvironmentError(ValueError):
    pass


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _load_json_bytes(path: Path, label: str) -> tuple[dict[str, Any], bytes]:
    try:
        raw = path.read_bytes()
        value = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ManagedRuntimeEnvironmentError(
            f"cannot read {label}: {path}"
        ) from exc
    if not isinstance(value, dict):
        raise ManagedRuntimeEnvironmentError(
            f"{label} root must be an object"
        )
    return value, raw


def _require_raw_binding(
    value: dict[str, Any], raw: bytes, label: str
) -> None:
    try:
        decoded = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ManagedRuntimeEnvironmentError(
            f"{label} raw bytes must be UTF-8 JSON"
        ) from exc
    if decoded != value:
        raise ManagedRuntimeEnvironmentError(
            f"{label} object/raw-byte binding drift"
        )


def _require_platform(manifest: dict[str, Any]) -> dict[str, str]:
    expected = manifest.get("platform")
    if not isinstance(expected, dict):
        raise ManagedRuntimeEnvironmentError(
            "wheelhouse manifest platform must be an object"
        )
    observed = {
        "os": (
            "linux"
            if sys.platform.startswith("linux")
            else sys.platform.lower()
        ),
        "arch": platform.machine().lower(),
        "python": platform.python_version(),
    }
    if observed != expected:
        raise ManagedRuntimeEnvironmentError(
            f"host platform drift: expected {expected!r}, got {observed!r}"
        )
    return observed


def _venv_python(root: Path) -> Path:
    return root / "bin" / "python"


def _absolute_without_resolving_symlinks(path: Path) -> Path:
    return Path(os.path.abspath(str(path.expanduser())))


def _write_receipt(path: Path, value: dict[str, Any]) -> None:
    temp = path.with_name(path.name + ".tmp")
    temp.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temp.replace(path)


def _run(
    command: Sequence[str],
    *,
    env: dict[str, str] | None = None,
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> subprocess.CompletedProcess[str]:
    try:
        return runner(
            list(command),
            text=True,
            capture_output=True,
            check=False,
            env=env,
        )
    except OSError as exc:
        raise ManagedRuntimeEnvironmentError(
            f"cannot execute {Path(command[0]).name}: {exc}"
        ) from exc


def _probe_script() -> str:
    return r'''
import importlib
import importlib.metadata as metadata
import json
import pathlib
import sys

transported = {
    "laya": "laya",
    "transformers": "transformers",
    "tokenizers": "tokenizers",
    "safetensors": "safetensors",
}
host = [
    "torch",
    "huggingface-hub",
    "numpy",
    "fastapi",
    "uvicorn",
]
result = {
    "prefix": str(pathlib.Path(sys.prefix).resolve()),
    "base_prefix": str(pathlib.Path(sys.base_prefix).resolve()),
    "transported": {},
    "host_dependencies": {},
    "modernbert_import": False,
}
for distribution, module_name in transported.items():
    dist = metadata.distribution(distribution)
    module = importlib.import_module(module_name)
    direct = None
    for item in dist.files or []:
        if pathlib.PurePosixPath(str(item)).name == "direct_url.json":
            path = pathlib.Path(dist.locate_file(item)).resolve()
            direct = json.loads(path.read_text(encoding="utf-8"))
            break
    result["transported"][distribution] = {
        "version": dist.version,
        "module_file": str(pathlib.Path(module.__file__).resolve()),
        "direct_url": direct,
    }
for distribution in host:
    result["host_dependencies"][distribution] = metadata.version(distribution)

from transformers.models.modernbert import ModernBertConfig
result["modernbert_import"] = ModernBertConfig is not None
print(json.dumps(result, separators=(",", ":")))
'''


def _parse_direct_url(
    value: Any,
    *,
    wheel_path: Path,
    wheel_sha256: str,
    distribution: str,
) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ManagedRuntimeEnvironmentError(
            f"{distribution}: direct_url.json missing"
        )
    url = value.get("url")
    archive_info = value.get("archive_info")
    if not isinstance(url, str) or not isinstance(archive_info, dict):
        raise ManagedRuntimeEnvironmentError(
            f"{distribution}: direct_url.json shape drift"
        )
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "file":
        raise ManagedRuntimeEnvironmentError(
            f"{distribution}: install origin must be a local file URL"
        )
    observed_path = Path(
        urllib.parse.unquote(parsed.path)
    ).resolve()
    if observed_path != wheel_path.resolve():
        raise ManagedRuntimeEnvironmentError(
            f"{distribution}: direct_url wheel path drift"
        )

    observed_hash = None
    hashes = archive_info.get("hashes")
    if isinstance(hashes, dict):
        observed_hash = hashes.get("sha256")
    if observed_hash is None:
        raw_hash = archive_info.get("hash")
        if (
            isinstance(raw_hash, str)
            and raw_hash.startswith("sha256=")
        ):
            observed_hash = raw_hash.split("=", 1)[1]
    if observed_hash != wheel_sha256:
        raise ManagedRuntimeEnvironmentError(
            f"{distribution}: direct_url wheel SHA-256 drift"
        )
    return {
        "scheme": "file",
        "wheel_filename": wheel_path.name,
        "archive_sha256": observed_hash,
        "source_path_retained": False,
    }


def _expected_wheels(
    verification: dict[str, Any],
    wheelhouse: Path,
) -> dict[str, dict[str, Any]]:
    wheels = verification.get("wheels")
    if not isinstance(wheels, list):
        raise ManagedRuntimeEnvironmentError(
            "wheelhouse verification wheels missing"
        )
    by_name: dict[str, dict[str, Any]] = {}
    for item in wheels:
        if not isinstance(item, dict):
            raise ManagedRuntimeEnvironmentError(
                "wheelhouse verification entry must be an object"
            )
        distribution = item.get("distribution")
        if (
            not isinstance(distribution, str)
            or distribution in by_name
        ):
            raise ManagedRuntimeEnvironmentError(
                "wheelhouse distribution drift or duplicate"
            )
        by_name[distribution] = dict(item)
    if set(by_name) != set(TRANSPORTED_DISTRIBUTIONS):
        raise ManagedRuntimeEnvironmentError(
            "wheelhouse transported distribution set drift"
        )
    for distribution, item in by_name.items():
        filename = item.get("filename")
        if not isinstance(filename, str):
            raise ManagedRuntimeEnvironmentError(
                f"{distribution}: wheel filename missing"
            )
        item["path"] = wheelhouse / filename
    return by_name


def _probe_environment(
    env_root: Path,
    *,
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> dict[str, Any]:
    python = _venv_python(env_root)
    if not python.is_file():
        raise ManagedRuntimeEnvironmentError(
            f"environment Python missing: {python}"
        )
    probe_env = dict(os.environ)
    probe_env["HF_HUB_OFFLINE"] = "1"
    probe_env["TRANSFORMERS_OFFLINE"] = "1"
    completed = _run(
        [str(python), "-c", _probe_script()],
        env=probe_env,
        runner=runner,
    )
    if completed.returncode != 0:
        raise ManagedRuntimeEnvironmentError(
            "runtime environment import probe failed"
        )
    try:
        value = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise ManagedRuntimeEnvironmentError(
            "runtime environment probe did not emit JSON"
        ) from exc
    if not isinstance(value, dict):
        raise ManagedRuntimeEnvironmentError(
            "runtime environment probe root must be an object"
        )
    return value


def verify_environment(
    manifest: dict[str, Any],
    wheelhouse: Path,
    env_root: Path,
    *,
    expected_python_executable: Path | None = None,
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> dict[str, Any]:
    verification = wheelhouse_verifier.verify_wheelhouse(
        manifest,
        wheelhouse,
    )
    if verification.get("valid") is not True:
        raise ManagedRuntimeEnvironmentError(
            "wheelhouse verification did not return valid=true"
        )
    _require_platform(manifest)
    root = env_root.expanduser().resolve()
    if not root.is_dir():
        raise ManagedRuntimeEnvironmentError(
            f"runtime environment not found: {root}"
        )

    pyvenv = root / "pyvenv.cfg"
    try:
        cfg = pyvenv.read_text(encoding="utf-8").lower()
    except (OSError, UnicodeDecodeError) as exc:
        raise ManagedRuntimeEnvironmentError(
            f"cannot read runtime pyvenv.cfg: {pyvenv}"
        ) from exc
    if "include-system-site-packages = true" not in cfg:
        raise ManagedRuntimeEnvironmentError(
            "runtime environment must keep system-site-packages enabled"
        )

    python = _absolute_without_resolving_symlinks(
        _venv_python(root)
    )
    if (
        expected_python_executable is not None
        and python
        != _absolute_without_resolving_symlinks(
            expected_python_executable
        )
    ):
        raise ManagedRuntimeEnvironmentError(
            "current interpreter is not the verified managed runtime"
        )

    wheels = _expected_wheels(verification, wheelhouse)
    probe = _probe_environment(root, runner=runner)
    if Path(probe.get("prefix", "")).resolve() != root:
        raise ManagedRuntimeEnvironmentError(
            "runtime probe sys.prefix drift"
        )
    if probe.get("prefix") == probe.get("base_prefix"):
        raise ManagedRuntimeEnvironmentError(
            "runtime probe is not executing inside a virtual environment"
        )
    if probe.get("modernbert_import") is not True:
        raise ManagedRuntimeEnvironmentError(
            "ModernBERT import probe did not pass"
        )

    transported = probe.get("transported")
    if not isinstance(transported, dict):
        raise ManagedRuntimeEnvironmentError(
            "runtime transported package probe missing"
        )
    installed: dict[str, dict[str, Any]] = {}
    for distribution in TRANSPORTED_DISTRIBUTIONS:
        observed = transported.get(distribution)
        expected = wheels[distribution]
        if not isinstance(observed, dict):
            raise ManagedRuntimeEnvironmentError(
                f"{distribution}: runtime probe missing"
            )
        if observed.get("version") != expected.get("version"):
            raise ManagedRuntimeEnvironmentError(
                f"{distribution}: installed version drift"
            )
        module_file = observed.get("module_file")
        if not isinstance(module_file, str):
            raise ManagedRuntimeEnvironmentError(
                f"{distribution}: module file missing"
            )
        try:
            Path(module_file).resolve().relative_to(root)
        except ValueError as exc:
            raise ManagedRuntimeEnvironmentError(
                f"{distribution}: module imported outside managed runtime"
            ) from exc
        origin = _parse_direct_url(
            observed.get("direct_url"),
            wheel_path=expected["path"],
            wheel_sha256=expected["sha256"],
            distribution=distribution,
        )
        installed[distribution] = {
            "version": expected["version"],
            "wheel": origin,
            "module_within_runtime": True,
        }

    host_dependencies = probe.get("host_dependencies")
    if not isinstance(host_dependencies, dict):
        raise ManagedRuntimeEnvironmentError(
            "runtime host dependency probe missing"
        )
    for distribution in wheelhouse_verifier.HOST_REQUIRED_NOT_SUPPLIED:
        version = host_dependencies.get(distribution)
        if not isinstance(version, str) or not version:
            raise ManagedRuntimeEnvironmentError(
                f"host dependency missing in managed runtime: {distribution}"
            )

    return {
        "schema": SCHEMA,
        "valid": True,
        "python": {
            "relative_path": "bin/python",
            "version": platform.python_version(),
            "system_site_packages": True,
            "current_interpreter_matches": (
                expected_python_executable is not None
            ),
        },
        "transported": installed,
        "host_dependencies": {
            distribution: host_dependencies[distribution]
            for distribution in wheelhouse_verifier.HOST_REQUIRED_NOT_SUPPLIED
        },
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


def materialize_environment(
    manifest: dict[str, Any],
    manifest_raw: bytes,
    wheelhouse: Path,
    output_dir: Path,
    *,
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
    builder_factory: Callable[..., venv.EnvBuilder] = venv.EnvBuilder,
) -> dict[str, Any]:
    _require_raw_binding(
        manifest,
        manifest_raw,
        "runtime dependency wheelhouse manifest",
    )
    verification = wheelhouse_verifier.verify_wheelhouse(
        manifest,
        wheelhouse,
    )
    if verification.get("valid") is not True:
        raise ManagedRuntimeEnvironmentError(
            "wheelhouse verification did not return valid=true"
        )
    _require_platform(manifest)
    root = output_dir.expanduser().resolve()
    if root.exists():
        raise ManagedRuntimeEnvironmentError(
            f"runtime environment already exists: {root}"
        )
    root.parent.mkdir(parents=True, exist_ok=True)

    wheels = _expected_wheels(verification, wheelhouse)
    try:
        builder = builder_factory(
            system_site_packages=True,
            clear=False,
            symlinks=True,
            with_pip=True,
        )
        builder.create(str(root))
        python = _venv_python(root)
        install_env = dict(os.environ)
        install_env["PIP_NO_INDEX"] = "1"
        install_env["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"
        install_env["HF_HUB_OFFLINE"] = "1"
        install_env["TRANSFORMERS_OFFLINE"] = "1"
        command = [
            str(python),
            "-m",
            "pip",
            "install",
            "--no-index",
            "--no-deps",
            "--disable-pip-version-check",
            "--force-reinstall",
            *[
                str(wheels[name]["path"])
                for name in TRANSPORTED_DISTRIBUTIONS
            ],
        ]
        completed = _run(command, env=install_env, runner=runner)
        if completed.returncode != 0:
            raise ManagedRuntimeEnvironmentError(
                "offline exact-wheel installation failed"
            )

        runtime_verification = verify_environment(
            manifest,
            wheelhouse,
            root,
            runner=runner,
        )
        receipt = {
            "schema": SCHEMA,
            "status": "materialized-and-verified",
            "wheelhouse_manifest_sha256": _sha256_bytes(manifest_raw),
            "wheelhouse": verification,
            "install": {
                "mode": "pip-no-index-no-deps-force-reinstall",
                "wheel_filenames": [
                    wheels[name]["filename"]
                    for name in TRANSPORTED_DISTRIBUTIONS
                ],
                "returncode": 0,
            },
            "environment_verification": runtime_verification,
            "scope": runtime_verification["scope"],
        }
        _write_receipt(root / RECEIPT_FILE, receipt)
        return receipt
    except BaseException:
        shutil.rmtree(root, ignore_errors=True)
        raise


def main(argv: list[str] | None = None) -> int:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "manifest",
        type=Path,
        nargs="?",
        default=here / "runtime_dependency_wheelhouse.v1.json",
    )
    parser.add_argument("wheelhouse", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)

    try:
        manifest, raw = _load_json_bytes(
            args.manifest,
            "runtime dependency wheelhouse manifest",
        )
        receipt = materialize_environment(
            manifest,
            raw,
            args.wheelhouse.resolve(),
            args.output_dir,
        )
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(
        json.dumps(
            {
                "status": receipt["status"],
                "output_dir": str(args.output_dir.expanduser().resolve()),
                "receipt": RECEIPT_FILE,
                "transported_wheel_installation_origin_attested": True,
                "runtime_installation_origin_attested": False,
                "model_weights_loaded": False,
                "live_inference": False,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
