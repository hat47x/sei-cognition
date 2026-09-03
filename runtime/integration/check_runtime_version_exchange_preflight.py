#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import socket
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

KJ_ATLAS_COMMIT = "4f28c13abe4176503c6fed863383a2d1db2299e9"
RUNTIME_VERSION_A = "0.32.13"
RUNTIME_VERSION_B = "0.32.14"
RUNTIME_SHA256_A = "0fd1dece38a1c6242e8013ce20b597345c5de072ae6b320160edb0e729ef1de1"
RUNTIME_SHA256_B = "c620917a71e146ab3a7f893084f066069c4c65d144ef8379a91c3cbe8b27de8f"
RUNTIME_SIZE_A = 1421793186
RUNTIME_SIZE_B = 1421191399
TOTAL_COMPRESSED_RUNTIME_BYTES = RUNTIME_SIZE_A + RUNTIME_SIZE_B
MODEL_NAME = "qwen2.5:0.5b"
MODEL_SHA256 = "a8b0c51577010a279d933d14c2a8ab4b268079d44c5c8830c0a93900f1827c67"
REQUIRED_COMMANDS = ("git", "python3", "go", "curl", "zstd", "tar", "sha256sum", "uname", "mktemp")
REQUIRED_PORTS = (("ollama", 11434), ("soza-model-adapter", 8001), ("kj-atlas", 8101))


@dataclass(frozen=True)
class Check:
    id: str
    status: str
    detail: str


def canonical_path(path: Path) -> Path:
    return path.expanduser().resolve(strict=False)


def is_within(candidate: Path, parent: Path) -> bool:
    candidate = canonical_path(candidate)
    parent = canonical_path(parent)
    return candidate == parent or parent in candidate.parents


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_git(path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", "-C", str(path), *args], check=False, capture_output=True, text=True)


def repository_check(label: str, path: Path, expected_commit: str | None = None) -> list[Check]:
    checks: list[Check] = []
    inside = run_git(path, "rev-parse", "--is-inside-work-tree")
    if inside.returncode != 0 or inside.stdout.strip() != "true":
        return [Check(f"{label}.git", "blocked", f"Git working treeではありません: {path}")]
    checks.append(Check(f"{label}.git", "ok", f"Git working treeを確認しました: {path}"))

    status = run_git(path, "status", "--porcelain", "--untracked-files=all")
    if status.returncode != 0:
        checks.append(Check(f"{label}.clean", "blocked", "working tree状態を取得できませんでした"))
    elif status.stdout.strip():
        checks.append(Check(f"{label}.clean", "blocked", "未commit変更があります"))
    else:
        checks.append(Check(f"{label}.clean", "ok", "working treeはcleanです"))

    if expected_commit is not None:
        head = run_git(path, "rev-parse", "HEAD")
        actual = head.stdout.strip() if head.returncode == 0 else ""
        if actual == expected_commit:
            checks.append(Check(f"{label}.commit", "ok", f"固定commitと一致します: {actual}"))
        else:
            checks.append(Check(f"{label}.commit", "blocked", f"commitが固定値と一致しません: actual={actual or 'unavailable'} expected={expected_commit}"))
    return checks


def command_checks(commands: Iterable[str] = REQUIRED_COMMANDS) -> list[Check]:
    checks = []
    for command in commands:
        path = shutil.which(command)
        if path:
            checks.append(Check(f"command.{command}", "ok", f"{command}: {path}"))
        else:
            checks.append(Check(f"command.{command}", "blocked", f"必要コマンドが見つかりません: {command}"))
    return checks


def port_check(label: str, port: int) -> Check:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(("127.0.0.1", port))
        except OSError as exc:
            return Check(f"port.{label}", "blocked", f"127.0.0.1:{port} は使用できません: {exc}")
    return Check(f"port.{label}", "ok", f"127.0.0.1:{port} は使用可能です")


def output_path_check(label: str, path: Path | None, source_roots: Iterable[Path], must_be_new: bool) -> list[Check]:
    if path is None:
        return [Check(f"path.{label}", "deferred", "pathはharnessの既定値を使用します")]
    resolved = canonical_path(path)
    for root in source_roots:
        if is_within(resolved, root):
            return [Check(f"path.{label}", "blocked", f"source repository配下は使用できません: {resolved}")]
    if must_be_new and resolved.exists():
        return [Check(f"path.{label}", "blocked", f"既存pathは使用できません: {resolved}")]
    return [Check(f"path.{label}", "ok", f"path境界を確認しました: {resolved}")]


def archive_check(
    label: str,
    path: Path | None,
    expected_sha: str,
    expected_size: int,
    require_prepositioned: bool,
) -> list[Check]:
    if path is None:
        status = "blocked" if require_prepositioned else "deferred"
        detail = (
            "事前配置archiveが必要ですが指定されていません"
            if require_prepositioned
            else f"archiveは実行時download経路を利用します。公式固定size={expected_size} bytes。actual bytesのsize / digest検証は実行時に行います"
        )
        return [Check(f"archive.{label}", status, detail)]
    resolved = canonical_path(path)
    if not resolved.is_file():
        return [Check(f"archive.{label}", "blocked", f"archive fileが存在しません: {resolved}")]
    actual_size = resolved.stat().st_size
    if actual_size != expected_size:
        return [
            Check(
                f"archive.{label}",
                "blocked",
                f"archive sizeが公式固定値と一致しません: actual={actual_size} expected={expected_size}",
            )
        ]
    actual = sha256_file(resolved)
    if actual != expected_sha:
        return [Check(f"archive.{label}", "blocked", f"archive digestが固定値と一致しません: actual={actual} expected={expected_sha}")]
    return [Check(f"archive.{label}", "ok", f"固定size / digestと一致します: size={actual_size} sha256={actual}")]


def model_store_check(path: Path | None, source_roots: Iterable[Path], require_prepositioned: bool) -> list[Check]:
    if path is None:
        status = "blocked" if require_prepositioned else "deferred"
        detail = "事前配置model storageが必要ですが指定されていません" if require_prepositioned else "work-local model storageを利用します。固定model digestはOllama起動後にAPIで確認します"
        return [Check("model.store", status, detail)]
    resolved = canonical_path(path)
    for root in source_roots:
        if is_within(resolved, root):
            return [Check("model.store", "blocked", f"source repository配下は使用できません: {resolved}")]
    if not resolved.is_dir():
        return [Check("model.store", "blocked", f"model storage directoryが存在しません: {resolved}")]
    return [Check("model.store", "ok", f"model storage directoryを確認しました: {resolved}。固定model digestの一致はOllama起動後に確認します")]


def nearest_existing_path(path: Path) -> Path | None:
    current = canonical_path(path)
    while not current.exists():
        parent = current.parent
        if parent == current:
            return None
        current = parent
    return current


def disk_capacity_check(path: Path) -> Check:
    existing = nearest_existing_path(path)
    if existing is None:
        return Check("disk.work", "deferred", f"disk容量を確認できる既存parentがありません: {canonical_path(path)}")
    try:
        free = shutil.disk_usage(existing).free
    except OSError as exc:
        return Check("disk.work", "deferred", f"disk空き容量を確認できませんでした: path={existing} error={exc}")
    return Check(
        "disk.work",
        "ok",
        (
            f"work領域の既存parent={existing}; free={free} bytes; "
            f"固定runtime archive 2本の圧縮bytes合計={TOTAL_COMPRESSED_RUNTIME_BYTES}。"
            "展開後runtime、Python環境、work-local model storageには追加容量が必要です。"
            "この観測だけではdisk容量が十分とは判定しません"
        ),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ISSUE-000070のruntime交換実験を開始する前に、ローカル実行条件を副作用なく確認します。")
    parser.add_argument("--kj-atlas-dir", type=Path, default=None)
    parser.add_argument("--runtime-a-archive", type=Path, default=None)
    parser.add_argument("--runtime-b-archive", type=Path, default=None)
    parser.add_argument("--model-dir", type=Path, default=None)
    parser.add_argument("--work-dir", type=Path, default=None)
    parser.add_argument("--evidence-dir", type=Path, default=None)
    parser.add_argument("--require-prepositioned-artifacts", action="store_true", help="runtime archiveとmodel storageを事前配置済みであることを要求します。")
    parser.add_argument("--json", action="store_true", help="構造化JSONだけを出力します。")
    return parser


def collect_checks(args: argparse.Namespace, soza_root: Path) -> list[Check]:
    checks: list[Check] = []
    host_os = platform.system()
    host_arch = platform.machine()
    checks.append(Check("host.os", "ok" if host_os == "Linux" else "blocked", f"host OS: {host_os}; 固定runtime artifactはLinux用です"))
    checks.append(Check("host.arch", "ok" if host_arch in {"x86_64", "amd64"} else "blocked", f"host architecture: {host_arch}; 固定runtime artifactはamd64用です"))
    checks.extend(command_checks())

    kj_atlas_dir = canonical_path(args.kj_atlas_dir or (soza_root / "_external" / "kj-atlas"))
    checks.extend(repository_check("soza", soza_root))
    checks.extend(repository_check("kj-atlas", kj_atlas_dir, expected_commit=KJ_ATLAS_COMMIT))
    source_roots = (soza_root, kj_atlas_dir)
    checks.extend(output_path_check("work", args.work_dir, source_roots, must_be_new=True))
    checks.extend(output_path_check("evidence", args.evidence_dir, source_roots, must_be_new=True))
    work_target = canonical_path(args.work_dir or Path(os.environ.get("TMPDIR", "/tmp")))
    checks.append(disk_capacity_check(work_target))
    checks.extend(archive_check("runtime-a", args.runtime_a_archive, RUNTIME_SHA256_A, RUNTIME_SIZE_A, args.require_prepositioned_artifacts))
    checks.extend(archive_check("runtime-b", args.runtime_b_archive, RUNTIME_SHA256_B, RUNTIME_SIZE_B, args.require_prepositioned_artifacts))
    checks.extend(model_store_check(args.model_dir, source_roots, args.require_prepositioned_artifacts))
    for label, port in REQUIRED_PORTS:
        checks.append(port_check(label, port))
    return checks


def fixed_artifact_report() -> dict[str, object]:
    return {
        "runtimeA": {
            "version": RUNTIME_VERSION_A,
            "sizeBytes": RUNTIME_SIZE_A,
            "sha256": RUNTIME_SHA256_A,
        },
        "runtimeB": {
            "version": RUNTIME_VERSION_B,
            "sizeBytes": RUNTIME_SIZE_B,
            "sha256": RUNTIME_SHA256_B,
        },
        "totalCompressedRuntimeBytes": TOTAL_COMPRESSED_RUNTIME_BYTES,
        "model": {
            "name": MODEL_NAME,
            "sha256": MODEL_SHA256,
        },
    }


def report(checks: list[Check]) -> dict[str, object]:
    blockers = [check.id for check in checks if check.status == "blocked"]
    return {
        "schema": "soza.runtime-version-exchange-preflight/v1",
        "result": "blocked" if blockers else "ready",
        "blockers": blockers,
        "fixedArtifacts": fixed_artifact_report(),
        "checks": [asdict(check) for check in checks],
        "stopLine": "preflight ready != actual runtime A/B inference PASS != runtime-version-exchange Scoped Executable Evidence",
    }


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    soza_root = canonical_path(Path(__file__).resolve().parents[2])
    result = report(collect_checks(args, soza_root))
    if args.json:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    else:
        print(f"runtime version exchange preflight: {result['result']}")
        for check in result["checks"]:
            print(f"- [{check['status']}] {check['id']}: {check['detail']}")
        print()
        print(result["stopLine"])
    return 0 if result["result"] == "ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())
