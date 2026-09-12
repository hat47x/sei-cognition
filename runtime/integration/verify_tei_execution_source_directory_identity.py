#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
from pathlib import Path, PurePosixPath
from typing import Mapping

import verify_tei_execution_source_identity as source_identity
from runtime_path_safety import reject_symlink_path_or_ancestors

EXPECTED_OBJECTS = source_identity.EXPECTED_OBJECTS
STOP_LINE = (
    "TEI execution-source directory bytes matched fixed revision-B Git object set "
    "!= exact revision B Git checkout HEAD/purity verified != revision B build PASS "
    "!= Provider Plan execution PASS != SEI Adapter compatibility PASS "
    "!= ISSUE-000072 Resolved"
)


def _git_blob_sha1(raw: bytes) -> str:
    header = f"blob {len(raw)}\0".encode("ascii")
    return hashlib.sha1(header + raw).hexdigest()


def _safe_relative_path(value: str) -> PurePosixPath:
    path = PurePosixPath(value)
    if not value or path.is_absolute() or ".." in path.parts:
        raise ValueError(f"execution-source pathが不正です: {value!r}")
    return path


def _reject_symlink_components(root: Path, relative: PurePosixPath) -> Path:
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError(f"execution-source境界にsymlinkを含められません: {current}")
    return current


def _read_regular_file(path: Path) -> tuple[bytes, str]:
    try:
        before = path.stat(follow_symlinks=False)
    except FileNotFoundError as exc:
        raise ValueError(f"execution-source fileがありません: {path}") from exc
    if not stat.S_ISREG(before.st_mode):
        raise ValueError(f"execution-source entryがregular fileではありません: {path}")

    raw = path.read_bytes()
    after = path.stat(follow_symlinks=False)
    stable_fields = (
        before.st_dev,
        before.st_ino,
        before.st_size,
        before.st_mtime_ns,
        before.st_mode,
    )
    observed_fields = (
        after.st_dev,
        after.st_ino,
        after.st_size,
        after.st_mtime_ns,
        after.st_mode,
    )
    if stable_fields != observed_fields:
        raise ValueError(f"execution-source fileがhash計算中に変化しました: {path}")

    mode = "100755" if before.st_mode & 0o111 else "100644"
    return raw, mode


def _git_tree_sha1_from_directory(root: Path) -> str:
    try:
        root_stat = root.stat(follow_symlinks=False)
    except FileNotFoundError as exc:
        raise ValueError(f"execution-source directoryがありません: {root}") from exc
    if not stat.S_ISDIR(root_stat.st_mode):
        raise ValueError(f"execution-source entryがdirectoryではありません: {root}")

    entries: list[tuple[bytes, str, str, str]] = []
    try:
        children = list(os.scandir(root))
    except OSError as exc:
        raise ValueError(f"execution-source directoryを走査できません: {root}: {exc}") from exc

    for child in children:
        name = child.name
        if "/" in name or name in {"", ".", ".."}:
            raise ValueError(f"execution-source entry名が不正です: {name!r}")
        child_path = root / name
        if child.is_symlink():
            raise ValueError(f"execution-source境界にsymlinkを含められません: {child_path}")
        child_stat = child.stat(follow_symlinks=False)
        if stat.S_ISDIR(child_stat.st_mode):
            digest = _git_tree_sha1_from_directory(child_path)
            mode = "40000"
            sort_key = name.encode("utf-8") + b"/"
        elif stat.S_ISREG(child_stat.st_mode):
            raw, mode = _read_regular_file(child_path)
            digest = _git_blob_sha1(raw)
            sort_key = name.encode("utf-8")
        else:
            raise ValueError(
                "execution-source境界にregular file/directory以外を含められません: "
                f"{child_path}"
            )
        entries.append((sort_key, mode, name, digest))

    body = bytearray()
    for _, mode, name, digest in sorted(entries, key=lambda item: item[0]):
        body.extend(mode.encode("ascii"))
        body.extend(b" ")
        body.extend(name.encode("utf-8"))
        body.extend(b"\0")
        body.extend(bytes.fromhex(digest))
    header = f"tree {len(body)}\0".encode("ascii")
    return hashlib.sha1(header + body).hexdigest()


def _observe_object(root: Path, relative_text: str) -> tuple[str, str]:
    relative = _safe_relative_path(relative_text)
    path = _reject_symlink_components(root, relative)
    try:
        entry_stat = path.stat(follow_symlinks=False)
    except FileNotFoundError as exc:
        raise ValueError(f"execution-source entryがありません: {relative_text}") from exc

    if stat.S_ISDIR(entry_stat.st_mode):
        return "tree", _git_tree_sha1_from_directory(path)
    if stat.S_ISREG(entry_stat.st_mode):
        raw, _ = _read_regular_file(path)
        return "blob", _git_blob_sha1(raw)
    raise ValueError(
        "execution-source entryがregular file/directoryではありません: "
        f"{relative_text}"
    )


def verify_directory(
    root: Path,
    *,
    expected_objects: Mapping[str, str] = EXPECTED_OBJECTS,
) -> dict[str, object]:
    requested = root.expanduser()
    reject_symlink_path_or_ancestors(requested, "TEI execution-source content directory")
    resolved = requested.resolve(strict=True)
    if not resolved.is_dir():
        raise ValueError(f"execution-source content rootがdirectoryではありません: {resolved}")

    observed: dict[str, str] = {}
    object_types: dict[str, str] = {}
    for relative, expected_sha in expected_objects.items():
        object_type, actual_sha = _observe_object(resolved, relative)
        object_types[relative] = object_type
        observed[relative] = actual_sha
        if actual_sha != expected_sha:
            raise ValueError(
                "Git object identityが期待値と一致しません: "
                f"path={relative} expected={expected_sha} actual={actual_sha}"
            )

    fixed_revision_b_set = dict(expected_objects) == dict(EXPECTED_OBJECTS)
    return {
        "schema": "sei.tei-execution-source-directory-identity/v1",
        "result": "verified",
        "sourceRoot": str(resolved),
        "acquisitionMode": "content_directory",
        "expectedRevision": source_identity.REVISION_B if fixed_revision_b_set else None,
        "revisionBExecutionSourceObjectSetMatched": fixed_revision_b_set,
        "executionSourceObjects": observed,
        "executionSourceObjectTypes": object_types,
        "gitCheckoutHeadVerified": False,
        "gitCheckoutWorkingTreePurityVerified": False,
        "qualityJudgement": "not_evaluated",
        "stopLine": STOP_LINE,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Git checkoutでない取得済みdirectoryについて、actual bytes / executable modeから"
            "TEI execution-source Git object identityを再構成し、fixed revision B object setへ"
            "一致するか検証します。Git HEAD / working-tree purityの代替にはしません。"
        ),
        allow_abbrev=False,
    )
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = verify_directory(args.source_root)
    except (OSError, ValueError) as exc:
        print(f"TEI execution-source content directory verification failed: {exc}")
        return 1

    if args.json:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    else:
        print("TEI execution-source content directory: verified")
        print(f"- expected revision: {result['expectedRevision']}")
        for path, digest in result["executionSourceObjects"].items():
            print(f"- {path}: {digest}")
        print(result["stopLine"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
