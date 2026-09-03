#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO, Callable

MANIFEST_PATH = Path(__file__).with_name("runtime_version_exchange_artifacts.json")
MANIFEST_SCHEMA = "soza.runtime-version-exchange-artifact-manifest/v1"


@dataclass(frozen=True)
class Verification:
    path: Path
    size_bytes: int
    sha256: str


def load_manifest(path: Path = MANIFEST_PATH) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema") != MANIFEST_SCHEMA:
        raise ValueError(f"manifest schemaが未対応です: {payload.get('schema')!r}")
    archives = payload.get("runtimeArchives")
    if not isinstance(archives, dict) or set(archives) != {"a", "b"}:
        raise ValueError("manifestにはruntimeArchives.a / runtimeArchives.bが必要です")
    local_names: set[str] = set()
    for label in ("a", "b"):
        archive = archives[label]
        if not isinstance(archive, dict):
            raise ValueError(f"runtimeArchives.{label}がobjectではありません")
        for name in (
            "runtime",
            "version",
            "assetName",
            "localFileName",
            "sizeBytes",
            "sha256",
            "downloadUrl",
        ):
            if name not in archive:
                raise ValueError(f"runtimeArchives.{label}.{name}がありません")
        local_name = archive["localFileName"]
        if not isinstance(local_name, str) or not local_name or Path(local_name).name != local_name:
            raise ValueError(f"runtimeArchives.{label}.localFileNameが不正です")
        if local_name in local_names:
            raise ValueError("runtime A / BのlocalFileNameが衝突しています")
        local_names.add(local_name)
        sha256 = archive["sha256"]
        if not isinstance(sha256, str) or len(sha256) != 64:
            raise ValueError(f"runtimeArchives.{label}.sha256が不正です")
        size = archive["sizeBytes"]
        if not isinstance(size, int) or size <= 0:
            raise ValueError(f"runtimeArchives.{label}.sizeBytesが不正です")
    return payload


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_archive(path: Path, expected_size: int, expected_sha256: str) -> Verification:
    if not path.is_file():
        raise ValueError(f"archive fileが存在しません: {path}")
    actual_size = path.stat().st_size
    if actual_size != expected_size:
        raise ValueError(
            f"archive sizeが固定値と一致しません: path={path} "
            f"actual={actual_size} expected={expected_size}"
        )
    actual_sha256 = sha256_file(path)
    if actual_sha256 != expected_sha256:
        raise ValueError(
            f"archive SHA-256が固定値と一致しません: path={path} "
            f"actual={actual_sha256} expected={expected_sha256}"
        )
    return Verification(path=path, size_bytes=actual_size, sha256=actual_sha256)


def download_archive(
    url: str,
    target: Path,
    expected_size: int,
    expected_sha256: str,
    opener: Callable[..., BinaryIO] | None = None,
) -> Verification:
    target = target.expanduser().resolve(strict=False)
    target.parent.mkdir(parents=True, exist_ok=True)

    if target.exists():
        return verify_archive(target, expected_size, expected_sha256)

    partial = target.with_name(target.name + ".part")
    if partial.exists():
        raise ValueError(
            f"途中downloadと思われるfileが既にあります: {partial}。"
            "内容を確認してから削除または退避してください"
        )

    open_url = opener or urllib.request.urlopen
    digest = hashlib.sha256()
    size = 0
    try:
        with open_url(url) as response, partial.open("xb") as output:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                output.write(chunk)
                digest.update(chunk)
                size += len(chunk)

        actual_sha256 = digest.hexdigest()
        if size != expected_size:
            raise ValueError(
                "downloadしたarchive sizeが固定値と一致しません: "
                f"actual={size} expected={expected_size}"
            )
        if actual_sha256 != expected_sha256:
            raise ValueError(
                "downloadしたarchive SHA-256が固定値と一致しません: "
                f"actual={actual_sha256} expected={expected_sha256}"
            )
        os.replace(partial, target)
        return Verification(path=target, size_bytes=size, sha256=actual_sha256)
    except Exception:
        # 途中fileは診断材料として残し、次回実行時に暗黙再利用しません。
        raise


def selected_archives(
    manifest: dict[str, object], selection: str
) -> list[tuple[str, dict[str, object]]]:
    archives = manifest["runtimeArchives"]
    assert isinstance(archives, dict)
    labels = ("a", "b") if selection == "all" else (selection,)
    return [(label, archives[label]) for label in labels]


def build_plan(
    manifest: dict[str, object], output_dir: Path, selection: str
) -> dict[str, object]:
    items = []
    total = 0
    for label, archive in selected_archives(manifest, selection):
        size = int(archive["sizeBytes"])
        total += size
        items.append(
            {
                "label": label,
                "runtime": archive["runtime"],
                "version": archive["version"],
                "officialAssetName": archive["assetName"],
                "target": str(
                    (output_dir / str(archive["localFileName"])).resolve(strict=False)
                ),
                "sizeBytes": size,
                "sha256": archive["sha256"],
                "downloadUrl": archive["downloadUrl"],
            }
        )
    return {
        "schema": "soza.runtime-version-exchange-artifact-preparation-plan/v1",
        "selection": selection,
        "outputDir": str(output_dir.resolve(strict=False)),
        "compressedBytesTotal": total,
        "archives": items,
        "stopLine": (
            "archive preparation success != actual runtime A/B inference PASS "
            "!= runtime-version-exchange Scoped Executable Evidence"
        ),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "ISSUE-000070で固定しているOllama Linux/amd64 archiveを、"
            "公式URLから安全に準備または再検証します。"
        )
    )
    parser.add_argument(
        "--output-dir", type=Path, required=True, help="archiveを置くdirectory。"
    )
    parser.add_argument(
        "--runtime",
        choices=("a", "b", "all"),
        default="all",
        help="準備するruntime。既定はa/bの両方です。",
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="network取得を行わず、既存archiveのsize / SHA-256だけを検証します。",
    )
    parser.add_argument(
        "--plan",
        action="store_true",
        help="取得計画だけを表示し、file作成やnetworkアクセスを行いません。",
    )
    parser.add_argument("--json", action="store_true", help="結果をJSONで出力します。")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    manifest = load_manifest()
    output_dir = args.output_dir.expanduser().resolve(strict=False)
    plan = build_plan(manifest, output_dir, args.runtime)

    if args.plan:
        if args.json:
            print(json.dumps(plan, ensure_ascii=False, sort_keys=True, indent=2))
        else:
            print("runtime version exchange artifact preparation plan")
            for item in plan["archives"]:
                print(
                    f"- runtime {item['label']}: Ollama {item['version']} "
                    f"{item['sizeBytes']} bytes -> {item['target']}"
                )
                print(f"  SHA-256: {item['sha256']}")
                print(f"  URL: {item['downloadUrl']}")
            print(f"- compressed total: {plan['compressedBytesTotal']} bytes")
            print(plan["stopLine"])
        return 0

    results = []
    for label, archive in selected_archives(manifest, args.runtime):
        target = output_dir / str(archive["localFileName"])
        try:
            if args.verify_only:
                verification = verify_archive(
                    target, int(archive["sizeBytes"]), str(archive["sha256"])
                )
                acquisition = "verified-existing"
            else:
                existed = target.exists()
                verification = download_archive(
                    str(archive["downloadUrl"]),
                    target,
                    int(archive["sizeBytes"]),
                    str(archive["sha256"]),
                )
                acquisition = "verified-existing" if existed else "downloaded"
            results.append(
                {
                    "label": label,
                    "version": archive["version"],
                    "path": str(verification.path),
                    "sizeBytes": verification.size_bytes,
                    "sha256": verification.sha256,
                    "acquisition": acquisition,
                    "status": "ok",
                }
            )
        except Exception as exc:
            results.append(
                {
                    "label": label,
                    "version": archive["version"],
                    "path": str(target.resolve(strict=False)),
                    "status": "blocked",
                    "error": str(exc),
                }
            )
            break

    payload = {
        "schema": "soza.runtime-version-exchange-artifact-preparation-result/v1",
        "result": (
            "ok"
            if results and all(item["status"] == "ok" for item in results)
            else "blocked"
        ),
        "archives": results,
        "stopLine": plan["stopLine"],
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2))
    else:
        print(f"runtime archive preparation: {payload['result']}")
        for item in results:
            if item["status"] == "ok":
                print(
                    f"- [ok] {item['label']} Ollama {item['version']}: "
                    f"{item['path']} ({item['sizeBytes']} bytes)"
                )
            else:
                print(
                    f"- [blocked] {item['label']} Ollama {item['version']}: "
                    f"{item['error']}",
                    file=sys.stderr,
                )
        print(payload["stopLine"])
    return 0 if payload["result"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
