#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path


INTEGRATION_DIR = Path(__file__).resolve().parent
ARTIFACT_MANIFEST = INTEGRATION_DIR / "runtime_version_exchange_artifacts.json"
RESULT_SCHEMA = "soza.runtime-version-exchange-model-store-verification/v1"
DIGEST_PATTERN = re.compile(r"^sha256:([0-9a-f]{64})$")


@dataclass(frozen=True)
class BlobVerification:
    digest: str
    path: str
    size_bytes: int
    sha256: str


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _require_regular_file_without_symlink(path: Path, root: Path, label: str) -> Path:
    root = root.resolve(strict=True)
    candidate = path.resolve(strict=True)
    if candidate == root or root not in candidate.parents:
        raise ValueError(f"{label}がmodel store外を指しています: {candidate}")

    current = path
    while current != root:
        if current.is_symlink():
            raise ValueError(f"{label}にsymlinkは利用できません: {current}")
        current = current.parent

    if not candidate.is_file():
        raise ValueError(f"{label}がregular fileではありません: {candidate}")
    return candidate


def _load_fixed_model_identity() -> dict[str, str]:
    payload = json.loads(ARTIFACT_MANIFEST.read_text(encoding="utf-8"))
    model = payload.get("model")
    if not isinstance(model, dict):
        raise ValueError("runtime artifact manifestにmodel identityがありません")

    required = ("name", "sha256", "storeManifestPath", "digestBasis")
    for key in required:
        value = model.get(key)
        if not isinstance(value, str) or not value:
            raise ValueError(f"runtime artifact manifestのmodel.{key}が不正です")

    if len(model["sha256"]) != 64 or any(ch not in "0123456789abcdef" for ch in model["sha256"]):
        raise ValueError("runtime artifact manifestのmodel.sha256が不正です")
    if model["digestBasis"] != "ollama-manifest-raw-bytes-sha256":
        raise ValueError(f"未対応のmodel digest basisです: {model['digestBasis']}")

    return {key: str(model[key]) for key in required}


def _layer_entries(manifest: dict[str, object]) -> list[dict[str, object]]:
    config = manifest.get("config")
    layers = manifest.get("layers")
    if not isinstance(config, dict):
        raise ValueError("Ollama model manifestのconfigがobjectではありません")
    if not isinstance(layers, list) or not all(isinstance(item, dict) for item in layers):
        raise ValueError("Ollama model manifestのlayersがarrayではありません")
    return [config, *layers]


def _validate_layer(layer: dict[str, object], label: str) -> tuple[str, int]:
    digest = layer.get("digest")
    size = layer.get("size")
    if not isinstance(digest, str):
        raise ValueError(f"{label}.digestが文字列ではありません")
    match = DIGEST_PATTERN.fullmatch(digest)
    if match is None:
        raise ValueError(f"{label}.digestがsha256形式ではありません: {digest!r}")
    if not isinstance(size, int) or isinstance(size, bool) or size < 0:
        raise ValueError(f"{label}.sizeが0以上の整数ではありません: {size!r}")
    return match.group(1), size


def verify_model_store(
    model_dir: Path,
    *,
    expected_model_name: str | None = None,
    expected_manifest_sha256: str | None = None,
    manifest_relative_path: str | None = None,
) -> dict[str, object]:
    fixed = _load_fixed_model_identity()
    model_name = expected_model_name or fixed["name"]
    manifest_sha256 = expected_manifest_sha256 or fixed["sha256"]
    relative_path = manifest_relative_path or fixed["storeManifestPath"]

    model_dir = model_dir.expanduser().resolve(strict=True)
    if not model_dir.is_dir():
        raise ValueError(f"Ollama model storeがdirectoryではありません: {model_dir}")

    relative = Path(relative_path)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"model manifest relative pathが不正です: {relative_path}")

    manifest_path_input = model_dir / relative
    manifest_path = _require_regular_file_without_symlink(
        manifest_path_input, model_dir, "model manifest"
    )
    raw_manifest = manifest_path.read_bytes()
    actual_manifest_sha256 = sha256_bytes(raw_manifest)
    if actual_manifest_sha256 != manifest_sha256:
        raise ValueError(
            "model manifestのraw SHA-256が固定値と一致しません: "
            f"actual={actual_manifest_sha256} expected={manifest_sha256}"
        )

    try:
        manifest = json.loads(raw_manifest)
    except json.JSONDecodeError as exc:
        raise ValueError(f"model manifestをJSONとして解釈できません: {exc}") from exc
    if not isinstance(manifest, dict):
        raise ValueError("model manifestのrootがobjectではありません")
    if manifest.get("schemaVersion") != 2:
        raise ValueError(
            f"model manifestのschemaVersionを認識できません: {manifest.get('schemaVersion')!r}"
        )

    referenced: dict[str, int] = {}
    ordered_layers = _layer_entries(manifest)
    for index, layer in enumerate(ordered_layers):
        digest_hex, declared_size = _validate_layer(layer, f"manifest entry {index}")
        previous = referenced.get(digest_hex)
        if previous is not None and previous != declared_size:
            raise ValueError(
                "同じblob digestに異なるsizeが宣言されています: "
                f"digest=sha256:{digest_hex} sizes={previous},{declared_size}"
            )
        referenced[digest_hex] = declared_size

    blobs: list[BlobVerification] = []
    for digest_hex, declared_size in referenced.items():
        blob_input = model_dir / "blobs" / f"sha256-{digest_hex}"
        blob = _require_regular_file_without_symlink(blob_input, model_dir, "model blob")
        actual_size = blob.stat().st_size
        if actual_size != declared_size:
            raise ValueError(
                "model blob sizeがmanifest宣言と一致しません: "
                f"path={blob} actual={actual_size} expected={declared_size}"
            )
        actual_sha256 = sha256_file(blob)
        if actual_sha256 != digest_hex:
            raise ValueError(
                "model blob SHA-256がmanifest宣言と一致しません: "
                f"path={blob} actual={actual_sha256} expected={digest_hex}"
            )
        blobs.append(
            BlobVerification(
                digest=f"sha256:{digest_hex}",
                path=str(blob),
                size_bytes=actual_size,
                sha256=actual_sha256,
            )
        )

    return {
        "schema": RESULT_SCHEMA,
        "verified": True,
        "model": model_name,
        "modelStore": str(model_dir),
        "manifestPath": str(manifest_path),
        "manifestRelativePath": relative_path,
        "manifestSha256": actual_manifest_sha256,
        "digestBasis": fixed["digestBasis"],
        "referencedBlobCount": len(blobs),
        "referencedBytesTotal": sum(item.size_bytes for item in blobs),
        "blobVerification": "declared-size+actual-sha256",
        "blobs": [asdict(item) for item in blobs],
        "stopLine": (
            "static model store verification PASS != actual Ollama /api/tags observation PASS "
            "!= actual runtime A/B inference PASS"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "ISSUE-000070で事前配置するOllama model storeを副作用なく検証します。"
            "固定manifestのraw SHA-256と、manifestが参照する全blobのsize / SHA-256を確認します。"
        )
    )
    parser.add_argument("--model-dir", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    try:
        payload = verify_model_store(args.model_dir)
    except (OSError, ValueError) as exc:
        parser.exit(1, f"runtime exchange model store verification failed: {exc}\n")

    rendered = json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    if args.output is not None:
        output = args.output.expanduser().resolve(strict=False)
        if output.exists():
            parser.exit(1, f"output file already exists: {output}\n")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
