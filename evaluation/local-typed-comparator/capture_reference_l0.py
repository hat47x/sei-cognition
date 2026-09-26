#!/usr/bin/env python3
"""Managed first-live capture for the exact Python-Laya typed-decisions reference.

This runner closes the local execution chain from a pinned Laya wheel and an
attested standalone model directory to one loopback-only /v1/systemone capture.
It intentionally does not compare against Papaya or make task-quality claims.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import importlib.util
import json
import os
import platform
import signal
import socket
import stat
import subprocess
import sys
import tempfile
import time
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any

RUN_SCHEMA = "sei.local-typed-comparator-reference-managed-run/v1"
PINNED_LAYA_VERSION = "0.3.20"
PINNED_LAYA_SOURCE_REVISION = "23a17522aa4942da6cce53a995a275760320b691"
PINNED_LAYA_WHEEL_SHA256 = "6039e802fa5effb8dd492061cd7ad39a43087beadc4a4fa4a649614e77eb83d4"
PINNED_LAYA_WHEEL_SIZE = 118_520
PINNED_MODEL_REPOSITORY = "convaiinnovations/laya-typed-decisions"
PINNED_MODEL_REVISION = "f9ab0b228f0fc0f14d873dbc99038f135c2da1b2"
REQUIRED_DEPENDENCIES = (
    "torch",
    "transformers",
    "safetensors",
    "huggingface-hub",
    "numpy",
    "fastapi",
    "uvicorn",
)
MAX_LOG_PREFIX_BYTES = 64 * 1024

BOOTSTRAP_CODE = r"""
import hashlib
import importlib.metadata
import json
import os
import sys
from pathlib import Path

site = Path(sys.argv[1]).resolve()
model_dir = Path(sys.argv[2]).resolve()
identity_path = Path(sys.argv[3]).resolve()
port = int(sys.argv[4])
threads = int(sys.argv[5])
expected_manifest = sys.argv[6]

sys.path.insert(0, str(site))

import laya
from laya.router import Router
from laya.serve import create_app
import torch
import uvicorn

laya_file = Path(laya.__file__).resolve()
if site != laya_file and site not in laya_file.parents:
    raise RuntimeError("laya import did not resolve from the extracted pinned wheel")

def sha256_file(path):
    h = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
            size += len(block)
    return h.hexdigest(), size

def source_manifest(package_root):
    entries = []
    for path in sorted(package_root.rglob("*.py")):
        if not path.is_file():
            continue
        digest, size = sha256_file(path)
        entries.append({
            "path": path.relative_to(package_root.parent).as_posix(),
            "bytes": size,
            "sha256": digest,
        })
    payload = json.dumps(entries, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return hashlib.sha256(payload).hexdigest(), len(entries)

manifest_sha256, source_file_count = source_manifest(laya_file.parent)
if manifest_sha256 != expected_manifest:
    raise RuntimeError("extracted Laya source manifest drift before model load")

torch.set_num_threads(threads)
router = Router(
    models={"typed-decisions": str(model_dir)},
    device="cpu",
    max_loaded=1,
    default="typed-decisions",
    preload=False,
)
router.preload(["typed-decisions"])
agent = router.load("typed-decisions")
model_binding_local_directory = Path(str(agent.model_id)).resolve() == model_dir
if not model_binding_local_directory:
    raise RuntimeError("typed-decisions agent did not bind to the verified local model directory")

dependencies = {}
for distribution in ("torch", "transformers", "safetensors", "huggingface-hub", "numpy", "fastapi", "uvicorn"):
    dependencies[distribution] = importlib.metadata.version(distribution)

identity = {
    "laya_version": importlib.metadata.version("laya"),
    "imported_from_extracted_wheel": True,
    "source_manifest_sha256": manifest_sha256,
    "source_file_count": source_file_count,
    "loaded": list(router.loaded),
    "model_binding_local_directory": model_binding_local_directory,
    "device": "cpu",
    "torch_num_threads": int(torch.get_num_threads()),
    "offline": {
        "HF_HUB_OFFLINE": os.environ.get("HF_HUB_OFFLINE"),
        "TRANSFORMERS_OFFLINE": os.environ.get("TRANSFORMERS_OFFLINE"),
    },
    "dependencies": dependencies,
}
identity_path.write_text(json.dumps(identity, separators=(",", ":")) + "\n", encoding="utf-8")

uvicorn.run(
    create_app(router),
    host="127.0.0.1",
    port=port,
    log_level="warning",
)
"""


class ReferenceCaptureError(ValueError):
    pass


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(block)
            size += len(block)
    return digest.hexdigest(), size


def require_pinned_file(
    path: Path,
    *,
    expected_sha256: str,
    expected_size: int,
    label: str,
) -> dict[str, Any]:
    if not path.is_file():
        raise ReferenceCaptureError(f"{label} not found: {path}")
    digest, size = sha256_file(path)
    if size != expected_size:
        raise ReferenceCaptureError(
            f"{label} byte-size mismatch: expected {expected_size}, got {size}"
        )
    if digest != expected_sha256:
        raise ReferenceCaptureError(f"{label} SHA-256 mismatch: {digest}")
    return {"name": path.name, "bytes": size, "sha256": digest}


def package_version(distribution: str) -> str | None:
    try:
        return importlib.metadata.version(distribution)
    except importlib.metadata.PackageNotFoundError:
        return None


def require_runtime_dependencies() -> dict[str, str]:
    versions: dict[str, str] = {}
    missing: list[str] = []
    for distribution in REQUIRED_DEPENDENCIES:
        version = package_version(distribution)
        if version is None:
            missing.append(distribution)
        else:
            versions[distribution] = version
    if missing:
        raise ReferenceCaptureError(
            "managed reference runtime dependencies are missing: "
            + ", ".join(sorted(missing))
        )
    return versions


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ReferenceCaptureError(f"cannot import module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def require_clean_source(expected_sha: str) -> dict[str, str]:
    if len(expected_sha) != 40 or any(
        c not in "0123456789abcdef" for c in expected_sha.lower()
    ):
        raise ReferenceCaptureError(
            "source_git_sha must be a full 40-character hexadecimal SHA"
        )
    try:
        root = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"], text=True
        ).strip()
        actual = subprocess.check_output(
            ["git", "-C", root, "rev-parse", "HEAD"], text=True
        ).strip()
        dirty = subprocess.check_output(
            [
                "git",
                "-C",
                root,
                "status",
                "--porcelain=v1",
                "--untracked-files=all",
            ],
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ReferenceCaptureError(
            "capture must run from a Git working tree"
        ) from exc
    if actual != expected_sha:
        raise ReferenceCaptureError(
            f"source HEAD mismatch: expected {expected_sha}, observed {actual}"
        )
    if dirty:
        raise ReferenceCaptureError(
            "source working tree must be clean before capture"
        )
    return {"git_sha": actual, "root": str(Path(root).resolve())}


def require_external_output_path(output: Path, source_root: Path) -> Path:
    resolved = output.resolve()
    source_root = source_root.resolve()
    try:
        resolved.relative_to(source_root)
    except ValueError:
        return resolved
    raise ReferenceCaptureError(
        "output must stay outside the verified SEI source checkout"
    )


def _wheel_member_is_symlink(info: zipfile.ZipInfo) -> bool:
    mode = (info.external_attr >> 16) & 0xFFFF
    return stat.S_ISLNK(mode)


def extract_verified_wheel(wheel: Path, target: Path) -> dict[str, Any]:
    target.mkdir(parents=True, exist_ok=False)
    try:
        with zipfile.ZipFile(wheel) as archive:
            members = archive.infolist()
            if not members:
                raise ReferenceCaptureError("runtime wheel is empty")
            for info in members:
                pure = PurePosixPath(info.filename)
                if (
                    not info.filename
                    or pure.is_absolute()
                    or ".." in pure.parts
                    or "\x00" in info.filename
                ):
                    raise ReferenceCaptureError(
                        f"unsafe runtime wheel member: {info.filename!r}"
                    )
                if _wheel_member_is_symlink(info):
                    raise ReferenceCaptureError(
                        f"runtime wheel symlink is not admitted: {info.filename!r}"
                    )
            archive.extractall(target)
    except (OSError, zipfile.BadZipFile) as exc:
        raise ReferenceCaptureError("cannot extract runtime wheel") from exc

    metadata = list(target.glob("laya-*.dist-info/METADATA"))
    if len(metadata) != 1:
        raise ReferenceCaptureError(
            "runtime wheel must contain exactly one laya dist-info METADATA"
        )
    fields: dict[str, str] = {}
    for line in metadata[0].read_text(encoding="utf-8").splitlines():
        if ": " in line:
            key, value = line.split(": ", 1)
            fields.setdefault(key, value)
    if fields.get("Name", "").lower() != "laya":
        raise ReferenceCaptureError("runtime wheel metadata name drift")
    if fields.get("Version") != PINNED_LAYA_VERSION:
        raise ReferenceCaptureError("runtime wheel metadata version drift")

    package_root = target / "laya"
    if not package_root.is_dir():
        raise ReferenceCaptureError("runtime wheel does not contain the laya package")
    manifest_sha256, source_file_count = source_manifest(package_root)
    return {
        "version": fields["Version"],
        "source_manifest_sha256": manifest_sha256,
        "source_file_count": source_file_count,
    }


def source_manifest(package_root: Path) -> tuple[str, int]:
    entries: list[dict[str, Any]] = []
    for path in sorted(package_root.rglob("*.py")):
        if not path.is_file():
            continue
        digest, size = sha256_file(path)
        entries.append(
            {
                "path": path.relative_to(package_root.parent).as_posix(),
                "bytes": size,
                "sha256": digest,
            }
        )
    if not entries:
        raise ReferenceCaptureError("runtime package source manifest is empty")
    payload = json.dumps(
        entries,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return sha256_bytes(payload), len(entries)


def child_environment(threads: int) -> dict[str, str]:
    env = dict(os.environ)
    for key in (
        "HF_TOKEN",
        "HUGGING_FACE_HUB_TOKEN",
        "LAYA_API_KEY",
        "PYTHONPATH",
    ):
        env.pop(key, None)
    env["HF_HUB_OFFLINE"] = "1"
    env["TRANSFORMERS_OFFLINE"] = "1"
    env["HF_DATASETS_OFFLINE"] = "1"
    env["PYTHONNOUSERSITE"] = "1"
    env["TOKENIZERS_PARALLELISM"] = "false"
    env["LAYA_DEVICE"] = "cpu"
    env["LAYA_THREADS"] = str(threads)
    return env


def find_free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def wait_for_health(
    capture_module: Any,
    endpoint: str,
    process: subprocess.Popen,
    *,
    timeout: float,
) -> dict[str, Any]:
    deadline = time.monotonic() + timeout
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        code = process.poll()
        if code is not None:
            raise ReferenceCaptureError(
                f"managed Laya process exited before health with code {code}"
            )
        try:
            return capture_module.capture_health(endpoint)
        except Exception as exc:
            last_error = exc
            time.sleep(0.25)
    raise ReferenceCaptureError(
        f"managed Laya endpoint did not become healthy within {timeout}s"
        + (f": {last_error}" if last_error is not None else "")
    )


def stop_process(process: subprocess.Popen | None) -> dict[str, Any]:
    if process is None:
        return {"started": False, "return_code_after_stop": None}
    method = "already-exited"
    if process.poll() is None:
        method = "SIGINT"
        process.send_signal(signal.SIGINT)
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            method = "terminate"
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                method = "kill"
                process.kill()
                process.wait(timeout=5)
    return {
        "started": True,
        "stop_method": method,
        "return_code_after_stop": process.poll(),
    }


def capture_log(path: Path, replacements: dict[str, str]) -> dict[str, Any]:
    if not path.is_file():
        return {"present": False}
    digest, size = sha256_file(path)
    raw = path.read_bytes()[:MAX_LOG_PREFIX_BYTES]
    text = raw.decode("utf-8", errors="replace")
    for source, replacement in sorted(
        replacements.items(), key=lambda item: len(item[0]), reverse=True
    ):
        text = text.replace(source, replacement)
    return {
        "present": True,
        "sha256": digest,
        "size_bytes": size,
        "utf8_prefix_sanitized": text,
        "prefix_truncated": size > len(raw),
    }


def load_json_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ReferenceCaptureError(f"cannot read {label}: {path}") from exc
    if not isinstance(value, dict):
        raise ReferenceCaptureError(f"{label} must be a JSON object")
    return value


def expected_token_counts(
    reference_token_fixture: dict[str, Any],
) -> dict[str, int]:
    counts: dict[str, int] = {}
    for case in reference_token_fixture.get("cases", []):
        case_id = case.get("case_id")
        token_count = case.get("token_count")
        if (
            not isinstance(case_id, str)
            or isinstance(token_count, bool)
            or not isinstance(token_count, int)
            or token_count <= 0
        ):
            raise ReferenceCaptureError(
                "reference token fixture contains an invalid token count"
            )
        counts[case_id] = token_count
    if not counts:
        raise ReferenceCaptureError("reference token fixture contains no cases")
    return counts


def bind_live_token_counts(
    records: list[dict[str, Any]], expected: dict[str, int]
) -> None:
    seen: set[str] = set()
    for record in records:
        case_id = record.get("case_id")
        if case_id not in expected:
            raise ReferenceCaptureError(
                f"unexpected live case for reference token binding: {case_id!r}"
            )
        try:
            response = json.loads(record["response_utf8"])
            observed = response["usage"]["input_tokens"]
        except (KeyError, TypeError, json.JSONDecodeError) as exc:
            raise ReferenceCaptureError(
                f"{case_id}: response does not retain input_tokens"
            ) from exc
        if (
            isinstance(observed, bool)
            or not isinstance(observed, int)
            or observed != expected[case_id]
        ):
            raise ReferenceCaptureError(
                f"{case_id}: live input_tokens {observed!r} != "
                f"retained reference {expected[case_id]}"
            )
        record["input_tokens"] = observed
        record["expected_reference_input_tokens"] = expected[case_id]
        record["live_token_count_matches_reference"] = True
        seen.add(case_id)
    if seen != set(expected):
        raise ReferenceCaptureError(
            "live frozen-case set does not exactly match the reference token fixture"
        )


def validate_choice11_diagnostic(
    diagnostic: dict[str, Any], protocol_module: Any
) -> None:
    protocol_module.validate_fixture(diagnostic)
    cases = diagnostic.get("cases")
    if not isinstance(cases, list) or len(cases) != 1:
        raise ReferenceCaptureError("choice:11+ diagnostic must contain one case")
    request = cases[0].get("request")
    questions = request.get("questions") if isinstance(request, dict) else None
    if not isinstance(questions, dict) or len(questions) != 1:
        raise ReferenceCaptureError(
            "choice:11+ diagnostic must contain one question"
        )
    question = next(iter(questions.values()))
    criteria = question.get("criteria") if isinstance(question, dict) else None
    if question.get("type") != "choice" or not isinstance(criteria, dict):
        raise ReferenceCaptureError(
            "choice:11+ diagnostic must be a Choice question"
        )
    if len(criteria) != 12:
        raise ReferenceCaptureError(
            "choice:11+ diagnostic must contain exactly 12 options"
        )


def validate_runtime_identity(
    identity: dict[str, Any],
    *,
    expected_manifest_sha256: str,
    expected_source_file_count: int,
    expected_dependencies: dict[str, str],
    expected_threads: int,
) -> None:
    if identity.get("laya_version") != PINNED_LAYA_VERSION:
        raise ReferenceCaptureError("child Laya version drift")
    if identity.get("imported_from_extracted_wheel") is not True:
        raise ReferenceCaptureError(
            "child did not attest import from extracted pinned wheel"
        )
    if identity.get("source_manifest_sha256") != expected_manifest_sha256:
        raise ReferenceCaptureError("child Laya source manifest drift")
    if identity.get("source_file_count") != expected_source_file_count:
        raise ReferenceCaptureError("child Laya source-file count drift")
    if identity.get("loaded") != ["typed-decisions"]:
        raise ReferenceCaptureError(
            "child did not preload only the typed-decisions checkpoint"
        )
    if identity.get("model_binding_local_directory") is not True:
        raise ReferenceCaptureError(
            "child did not bind typed-decisions to the verified local directory"
        )
    if identity.get("device") != "cpu":
        raise ReferenceCaptureError("child device must remain cpu")
    if identity.get("torch_num_threads") != expected_threads:
        raise ReferenceCaptureError("child torch thread count drift")
    offline = identity.get("offline")
    if not isinstance(offline, dict) or offline != {
        "HF_HUB_OFFLINE": "1",
        "TRANSFORMERS_OFFLINE": "1",
    }:
        raise ReferenceCaptureError("child offline-mode attestation drift")
    if identity.get("dependencies") != expected_dependencies:
        raise ReferenceCaptureError("child dependency-version receipt drift")


def ensure_same_verification(
    before: dict[str, Any], after: dict[str, Any], label: str
) -> None:
    if before != after:
        raise ReferenceCaptureError(f"{label} changed during managed capture")


def write_artifact(path: Path, artifact: dict[str, Any]) -> None:
    text = json.dumps(artifact, indent=2, ensure_ascii=False) + "\n"
    try:
        with path.open("x", encoding="utf-8") as stream:
            stream.write(text)
    except FileExistsError as exc:
        raise ReferenceCaptureError(f"output already exists: {path}") from exc


def main(argv: list[str] | None = None) -> int:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-git-sha", required=True)
    parser.add_argument("--model-dir", type=Path, required=True)
    parser.add_argument("--runtime-wheel", type=Path, required=True)
    parser.add_argument("--fixture", type=Path, default=here / "fixture.v1.json")
    parser.add_argument(
        "--reference-token-fixture",
        type=Path,
        default=here / "reference_token_fixture.v1.json",
    )
    parser.add_argument(
        "--model-attestation",
        type=Path,
        default=here / "reference_model_directory_attestation.v1.json",
    )
    parser.add_argument(
        "--diagnostic",
        type=Path,
        default=here / "papaya_choice11_diagnostic.v1.json",
    )
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--startup-timeout", type=float, default=300.0)
    args = parser.parse_args(argv)

    process: subprocess.Popen | None = None
    artifact: dict[str, Any] | None = None
    failure: Exception | None = None
    output: Path | None = None

    try:
        if args.threads <= 0:
            raise ReferenceCaptureError("threads must be positive")
        if args.startup_timeout <= 0:
            raise ReferenceCaptureError("startup-timeout must be positive")

        source = require_clean_source(args.source_git_sha.lower())
        source_root = Path(source.pop("root"))
        output = require_external_output_path(args.output, source_root)
        if output.exists():
            raise ReferenceCaptureError(f"output already exists: {output}")
        output.parent.mkdir(parents=True, exist_ok=True)

        capture_module = load_module(here / "capture_l0.py", "capture_l0_managed")
        protocol = load_module(
            here / "protocol_contract.py", "protocol_contract_managed"
        )
        model_verifier = load_module(
            here / "verify_reference_model_directory.py",
            "reference_model_directory_managed",
        )
        token_verifier = load_module(
            here / "reference_token_fixture.py",
            "reference_token_fixture_managed",
        )

        wheel = require_pinned_file(
            args.runtime_wheel,
            expected_sha256=PINNED_LAYA_WHEEL_SHA256,
            expected_size=PINNED_LAYA_WHEEL_SIZE,
            label="Laya runtime wheel",
        )
        dependencies = require_runtime_dependencies()

        attestation = load_json_object(args.model_attestation, "model attestation")
        model_verifier.validate_attestation(attestation)
        model_before = model_verifier.verify_model_directory(args.model_dir)

        fixture_raw = args.fixture.read_bytes()
        fixture = json.loads(fixture_raw.decode("utf-8"))
        protocol.validate_fixture(fixture)

        token_packet = load_json_object(
            args.reference_token_fixture, "reference token fixture"
        )
        token_verifier.validate_reference_token_fixture(fixture, token_packet)
        token_counts = expected_token_counts(token_packet)
        if set(token_counts) != {
            case.get("case_id") for case in fixture.get("cases", [])
        }:
            raise ReferenceCaptureError(
                "reference token fixture case set does not match frozen fixture"
            )

        diagnostic_raw = args.diagnostic.read_bytes()
        diagnostic = json.loads(diagnostic_raw.decode("utf-8"))
        validate_choice11_diagnostic(diagnostic, protocol)

        port = find_free_port()
        endpoint = f"http://127.0.0.1:{port}/v1/systemone"

        artifact = {
            "schema": RUN_SCHEMA,
            "status": "incomplete",
            "run_id": args.run_id,
            "source": source,
            "provider": {
                "name": "laya",
                "managed_endpoint": True,
                "endpoint": "http://127.0.0.1:<ephemeral>/v1/systemone",
                "runtime_source_revision": PINNED_LAYA_SOURCE_REVISION,
                "runtime_wheel": wheel,
                "runtime_dependencies": dependencies,
            },
            "checkpoint": {
                "repository": PINNED_MODEL_REPOSITORY,
                "revision": PINNED_MODEL_REVISION,
                "attestation_schema": attestation.get("schema"),
                "verification_before_preparation": model_before,
                "verification_immediately_before_launch": None,
                "verification_after_health_before_inference": None,
                "verification_after_inference": None,
            },
            "fixture": {
                "file": args.fixture.name,
                "schema": fixture.get("schema"),
                "sha256": sha256_bytes(fixture_raw),
                "case_count": len(fixture.get("cases", [])),
                "reference_token_fixture_schema": token_packet.get("schema"),
            },
            "choice11_diagnostic": {
                "file": args.diagnostic.name,
                "schema": diagnostic.get("schema"),
                "sha256": sha256_bytes(diagnostic_raw),
                "case_count": 1,
                "option_count": 12,
                "expected_answer": None,
                "quality_claim": False,
            },
            "host": {
                "python": platform.python_version(),
                "python_executable_name": Path(sys.executable).name,
                "platform": platform.platform(),
                "threads_requested": args.threads,
            },
            "runtime_extraction": None,
            "runtime_identity": None,
            "health": None,
            "frozen_cases": [],
            "diagnostic_cases": [],
            "process": None,
            "logs": {},
            "scope": {
                "reference_runtime_wheel_bytes_verified": True,
                "reference_runtime_imported_from_verified_wheel": False,
                "reference_model_directory_verified": True,
                "endpoint_loaded_exact_directory_attested": False,
                "endpoint_exact_runtime_wheel_attested": False,
                "reference_live_inference": False,
                "frozen_protocol_contract": False,
                "frozen_live_token_count_matches_reference": False,
                "choice11_reference_path_exercised": False,
                "numeric_parity_with_papaya": False,
                "task_quality": False,
                "calibration_validity": False,
                "jev_provider_identity": False,
            },
        }

        with tempfile.TemporaryDirectory(
            prefix=".laya-reference-live-", dir=output.parent
        ) as temp_dir:
            temp_root = Path(temp_dir)
            runtime_site = temp_root / "runtime-site"
            identity_path = temp_root / "runtime-identity.json"
            stdout_path = temp_root / "laya.stdout.log"
            stderr_path = temp_root / "laya.stderr.log"

            extraction = extract_verified_wheel(args.runtime_wheel, runtime_site)
            artifact["runtime_extraction"] = extraction

            launch_verification = model_verifier.verify_model_directory(
                args.model_dir
            )
            ensure_same_verification(
                model_before,
                launch_verification,
                "reference model directory before launch",
            )
            artifact["checkpoint"][
                "verification_immediately_before_launch"
            ] = launch_verification

            env = child_environment(args.threads)
            command = [
                sys.executable,
                "-c",
                BOOTSTRAP_CODE,
                str(runtime_site.resolve()),
                str(args.model_dir.resolve()),
                str(identity_path.resolve()),
                str(port),
                str(args.threads),
                extraction["source_manifest_sha256"],
            ]
            artifact["process"] = {
                "command_shape": [
                    "<capture-python>",
                    "-c",
                    "<managed-reference-bootstrap>",
                    "<extracted-pinned-wheel-site>",
                    "<verified-reference-model-dir>",
                    "<runtime-identity-receipt>",
                    "<ephemeral-loopback-port>",
                    str(args.threads),
                    extraction["source_manifest_sha256"],
                ],
                "network_mode": {
                    "HF_HUB_OFFLINE": "1",
                    "TRANSFORMERS_OFFLINE": "1",
                },
                "model_binding": "Router(models={'typed-decisions': <verified-local-dir>})",
                "started": False,
            }

            with stdout_path.open("wb") as stdout_file, stderr_path.open(
                "wb"
            ) as stderr_file:
                process = subprocess.Popen(
                    command,
                    cwd=temp_root,
                    env=env,
                    stdout=stdout_file,
                    stderr=stderr_file,
                )
                artifact["process"]["started"] = True
                try:
                    artifact["health"] = wait_for_health(
                        capture_module,
                        endpoint,
                        process,
                        timeout=args.startup_timeout,
                    )

                    identity = load_json_object(
                        identity_path, "child runtime identity receipt"
                    )
                    validate_runtime_identity(
                        identity,
                        expected_manifest_sha256=extraction[
                            "source_manifest_sha256"
                        ],
                        expected_source_file_count=extraction[
                            "source_file_count"
                        ],
                        expected_dependencies=dependencies,
                        expected_threads=args.threads,
                    )
                    artifact["runtime_identity"] = identity
                    artifact["scope"][
                        "reference_runtime_imported_from_verified_wheel"
                    ] = True
                    artifact["scope"][
                        "endpoint_exact_runtime_wheel_attested"
                    ] = True

                    post_health = model_verifier.verify_model_directory(
                        args.model_dir
                    )
                    ensure_same_verification(
                        launch_verification,
                        post_health,
                        "reference model directory after health",
                    )
                    artifact["checkpoint"][
                        "verification_after_health_before_inference"
                    ] = post_health
                    artifact["scope"][
                        "endpoint_loaded_exact_directory_attested"
                    ] = True

                    artifact["frozen_cases"] = capture_module.capture_cases(
                        fixture,
                        endpoint,
                        capture_module.PINNED_REQUEST_MODEL,
                        protocol.validate_response,
                    )
                    bind_live_token_counts(
                        artifact["frozen_cases"], token_counts
                    )
                    artifact["scope"]["reference_live_inference"] = True
                    artifact["scope"]["frozen_protocol_contract"] = True
                    artifact["scope"][
                        "frozen_live_token_count_matches_reference"
                    ] = True

                    artifact["diagnostic_cases"] = capture_module.capture_cases(
                        diagnostic,
                        endpoint,
                        capture_module.PINNED_REQUEST_MODEL,
                        protocol.validate_response,
                    )
                    artifact["diagnostic_cases"][0]["diagnostic_contract"] = {
                        "option_count": 12,
                        "temperature_bucket": "choice:11+",
                        "reference_applied_temperature": 0.5,
                        "expected_answer": None,
                        "quality_claim": False,
                    }
                    artifact["scope"][
                        "choice11_reference_path_exercised"
                    ] = True

                    post_inference = model_verifier.verify_model_directory(
                        args.model_dir
                    )
                    ensure_same_verification(
                        post_health,
                        post_inference,
                        "reference model directory after inference",
                    )
                    artifact["checkpoint"][
                        "verification_after_inference"
                    ] = post_inference

                    observed_manifest, observed_count = source_manifest(
                        runtime_site / "laya"
                    )
                    if (
                        observed_manifest
                        != extraction["source_manifest_sha256"]
                        or observed_count != extraction["source_file_count"]
                    ):
                        raise ReferenceCaptureError(
                            "extracted Laya source changed during managed capture"
                        )
                    artifact["status"] = "complete"
                except Exception as exc:
                    failure = exc
                    artifact["error"] = f"{type(exc).__name__}: {exc}"
                finally:
                    artifact["process"]["termination"] = stop_process(process)
                    process = None

            replacements = {
                str(source_root): "<sei-source>",
                str(args.model_dir.resolve()): "<reference-model-dir>",
                str(args.runtime_wheel.resolve()): "<laya-wheel>",
                str(runtime_site.resolve()): "<runtime-site>",
                str(temp_root.resolve()): "<capture-temp>",
            }
            artifact["logs"] = {
                "stdout": capture_log(stdout_path, replacements),
                "stderr": capture_log(stderr_path, replacements),
            }

        write_artifact(output, artifact)
        if failure is not None:
            raise failure

        print(
            json.dumps(
                {
                    "status": "complete",
                    "run_id": args.run_id,
                    "output": str(output),
                    "frozen_cases": len(artifact["frozen_cases"]),
                    "diagnostic_cases": len(artifact["diagnostic_cases"]),
                    "numeric_parity_with_papaya": False,
                },
                indent=2,
            )
        )
        return 0
    except Exception as exc:
        if process is not None:
            stop_process(process)
        if artifact is not None and output is not None and not output.exists():
            artifact["error"] = f"{type(exc).__name__}: {exc}"
            try:
                write_artifact(output, artifact)
            except Exception:
                pass
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
