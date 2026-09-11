#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import tempfile
import urllib.request
from pathlib import Path
from typing import BinaryIO, Callable, Mapping
from urllib.parse import urlparse

from runtime_path_safety import reject_symlink_path_or_ancestors
from verify_runtime_version_exchange_model_store import verify_model_store


INTEGRATION_DIR = Path(__file__).resolve().parent
SOZA_ROOT = INTEGRATION_DIR.parents[1]
ARTIFACT_MANIFEST = INTEGRATION_DIR / "runtime_version_exchange_artifacts.json"
CHUNK_SIZE = 1024 * 1024
REGISTRY_HOST = "registry.ollama.ai"
MODEL_ACQUISITION_FIELDS = (
    "name",
    "sha256",
    "storeManifestPath",
    "digestBasis",
    "registryManifestUrl",
    "registryBlobBaseUrl",
)


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _require_ollama_registry_url(url: str, label: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname != REGISTRY_HOST:
        raise ValueError(
            f"{label}はhttps://{REGISTRY_HOST}/ 配下である必要があります: {url}"
        )
    if parsed.username is not None or parsed.password is not None or parsed.port is not None:
        raise ValueError(f"{label}にuserinfoやportは指定できません: {url}")
    return url


def _expected_model_acquisition_locations(name: str) -> tuple[str, str, str]:
    repository, separator, tag = name.rpartition(":")
    if separator != ":" or not repository or not tag:
        raise ValueError(f"runtime artifact manifestのmodel.nameがrepository:tag形式ではありません: {name!r}")
    if ":" in repository or any(character in repository for character in "\\?#"):
        raise ValueError(f"runtime artifact manifestのmodel.name repository部が不正です: {name!r}")
    if any(character in tag for character in "/\\?#:"):
        raise ValueError(f"runtime artifact manifestのmodel.name tag部が不正です: {name!r}")

    repository_path = Path(repository)
    if repository_path.is_absolute() or ".." in repository_path.parts:
        raise ValueError(f"runtime artifact manifestのmodel.name repository部が不正です: {name!r}")

    registry_repository = f"library/{repository}"
    return (
        f"manifests/{REGISTRY_HOST}/{registry_repository}/{tag}",
        f"https://{REGISTRY_HOST}/v2/{registry_repository}/manifests/{tag}",
        f"https://{REGISTRY_HOST}/v2/{registry_repository}/blobs",
    )


def _validate_model_acquisition(model: Mapping[str, object]) -> dict[str, str]:
    result: dict[str, str] = {}
    for key in MODEL_ACQUISITION_FIELDS:
        value = model.get(key)
        if not isinstance(value, str) or not value:
            raise ValueError(f"runtime artifact manifestのmodel.{key}が不正です")
        result[key] = value

    if result["digestBasis"] != "ollama-manifest-raw-bytes-sha256":
        raise ValueError(f"未対応のmodel digest basisです: {result['digestBasis']}")
    if len(result["sha256"]) != 64 or any(
        ch not in "0123456789abcdef" for ch in result["sha256"]
    ):
        raise ValueError("runtime artifact manifestのmodel.sha256が不正です")

    relative = Path(result["storeManifestPath"])
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError("runtime artifact manifestのstoreManifestPathが不正です")

    _require_ollama_registry_url(result["registryManifestUrl"], "registryManifestUrl")
    _require_ollama_registry_url(result["registryBlobBaseUrl"], "registryBlobBaseUrl")

    expected_store_path, expected_manifest_url, expected_blob_base_url = (
        _expected_model_acquisition_locations(result["name"])
    )
    expected_values = (
        ("storeManifestPath", expected_store_path),
        ("registryManifestUrl", expected_manifest_url),
        ("registryBlobBaseUrl", expected_blob_base_url),
    )
    for key, expected in expected_values:
        if result[key] != expected:
            raise ValueError(
                f"runtime artifact manifestのmodel.{key}がmodel.nameと一致しません: "
                f"actual={result[key]!r} expected={expected!r}"
            )
    return result


def _load_model_acquisition() -> dict[str, str]:
    payload = json.loads(ARTIFACT_MANIFEST.read_text(encoding="utf-8"))
    model = payload.get("model")
    if not isinstance(model, dict):
        raise ValueError("runtime artifact manifestにmodel identityがありません")
    return _validate_model_acquisition(model)


def _is_within(candidate: Path, root: Path) -> bool:
    candidate = candidate.expanduser().resolve(strict=False)
    root = root.expanduser().resolve(strict=True)
    return candidate == root or root in candidate.parents


def _read_all(url: str, opener: Callable[..., BinaryIO]) -> bytes:
    with opener(url) as response:
        return response.read()


def _download_blob(
    url: str,
    target: Path,
    expected_size: int,
    expected_sha256: str,
    opener: Callable[..., BinaryIO],
) -> tuple[int, str]:
    digest = hashlib.sha256()
    size = 0
    target.parent.mkdir(parents=True, exist_ok=True)
    with opener(url) as response, target.open("xb") as output:
        while True:
            chunk = response.read(CHUNK_SIZE)
            if not chunk:
                break
            next_size = size + len(chunk)
            if next_size > expected_size:
                raise ValueError(
                    "model blob sizeが固定manifestを超えました: "
                    f"received={next_size} expected={expected_size} url={url}"
                )
            output.write(chunk)
            digest.update(chunk)
            size = next_size
    actual_sha256 = digest.hexdigest()
    if size != expected_size:
        raise ValueError(
            "model blob sizeが固定manifestと一致しません: "
            f"actual={size} expected={expected_size} url={url}"
        )
    if actual_sha256 != expected_sha256:
        raise ValueError(
            "model blob SHA-256が固定manifestと一致しません: "
            f"actual={actual_sha256} expected={expected_sha256} url={url}"
        )
    return size, actual_sha256


def _manifest_entries(manifest: dict[str, object]) -> list[dict[str, object]]:
    config = manifest.get("config")
    layers = manifest.get("layers")
    if not isinstance(config, dict):
        raise ValueError("Ollama model manifestのconfigがobjectではありません")
    if not isinstance(layers, list) or not all(isinstance(item, dict) for item in layers):
        raise ValueError("Ollama model manifestのlayersがarrayではありません")
    return [config, *layers]


def _entry_identity(entry: dict[str, object]) -> tuple[str, int]:
    digest = entry.get("digest")
    size = entry.get("size")
    if not isinstance(digest, str) or not digest.startswith("sha256:"):
        raise ValueError(f"model manifestのblob digestが不正です: {digest!r}")
    digest_hex = digest.removeprefix("sha256:")
    if len(digest_hex) != 64 or any(ch not in "0123456789abcdef" for ch in digest_hex):
        raise ValueError(f"model manifestのblob digestが不正です: {digest!r}")
    if not isinstance(size, int) or isinstance(size, bool) or size < 0:
        raise ValueError(f"model manifestのblob sizeが不正です: {size!r}")
    return digest_hex, size


def prepare_model_store(
    target_dir: Path,
    *,
    opener: Callable[..., BinaryIO] = urllib.request.urlopen,
    acquisition: Mapping[str, object] | None = None,
) -> dict[str, object]:
    fixed = _validate_model_acquisition(acquisition) if acquisition is not None else _load_model_acquisition()
    requested = target_dir.expanduser()
    reject_symlink_path_or_ancestors(requested, "model store target")
    target = requested.resolve(strict=False)
    if _is_within(target, SOZA_ROOT):
        raise ValueError(f"model storeをSEI repository配下には作成できません: {target}")
    if target.exists():
        raise ValueError(f"target model storeは新規pathである必要があります: {target}")

    target.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(
        tempfile.mkdtemp(prefix=f".{target.name}.partial-", dir=str(target.parent))
    ).resolve(strict=True)
    completed = False
    try:
        raw_manifest = _read_all(fixed["registryManifestUrl"], opener)
        actual_manifest_sha256 = _sha256_bytes(raw_manifest)
        if actual_manifest_sha256 != fixed["sha256"]:
            raise ValueError(
                "registry manifestのraw SHA-256が固定model identityと一致しません: "
                f"actual={actual_manifest_sha256} expected={fixed['sha256']}"
            )

        try:
            manifest = json.loads(raw_manifest)
        except json.JSONDecodeError as exc:
            raise ValueError(f"registry manifestをJSONとして解釈できません: {exc}") from exc
        if not isinstance(manifest, dict) or manifest.get("schemaVersion") != 2:
            raise ValueError("registry manifestのschemaVersionを認識できません")

        manifest_relative = Path(fixed["storeManifestPath"])
        manifest_target = staging / manifest_relative
        manifest_target.parent.mkdir(parents=True, exist_ok=True)
        manifest_target.write_bytes(raw_manifest)

        seen: dict[str, int] = {}
        downloaded_bytes = 0
        for entry in _manifest_entries(manifest):
            digest_hex, expected_size = _entry_identity(entry)
            previous_size = seen.get(digest_hex)
            if previous_size is not None:
                if previous_size != expected_size:
                    raise ValueError(
                        "同じblob digestに異なるsizeが宣言されています: "
                        f"sha256:{digest_hex} sizes={previous_size},{expected_size}"
                    )
                continue
            seen[digest_hex] = expected_size
            blob_target = staging / "blobs" / f"sha256-{digest_hex}"
            blob_url = f"{fixed['registryBlobBaseUrl'].rstrip('/')}/sha256:{digest_hex}"
            size, _sha256 = _download_blob(
                blob_url,
                blob_target,
                expected_size,
                digest_hex,
                opener,
            )
            downloaded_bytes += size

        verification = verify_model_store(
            staging,
            expected_model_name=fixed["name"],
            expected_manifest_sha256=fixed["sha256"],
            manifest_relative_path=fixed["storeManifestPath"],
        )
        os.replace(staging, target)
        completed = True
        return {
            "schema": "soza.runtime-version-exchange-model-store-preparation/v1",
            "prepared": True,
            "target": str(target),
            "model": fixed["name"],
            "manifestSha256": verification["manifestSha256"],
            "referencedBlobCount": verification["referencedBlobCount"],
            "referencedBytesTotal": verification["referencedBytesTotal"],
            "downloadedBytes": downloaded_bytes,
            "stopLine": (
                "prepared model store PASS != actual Ollama /api/tags observation PASS "
                "!= actual runtime A/B inference PASS"
            ),
        }
    finally:
        if not completed and staging.exists():
            shutil.rmtree(staging)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "ISSUE-000070で利用する固定Ollama model storeをregistryから準備します。"
            "固定manifest digestと全参照blobを検証し、成功時だけ完成directoryを公開します。"
        )
    )
    parser.add_argument("--target-dir", required=True, type=Path)
    args = parser.parse_args()

    try:
        result = prepare_model_store(args.target_dir)
    except (OSError, ValueError) as exc:
        parser.exit(1, f"runtime exchange model store preparation failed: {exc}\n")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
