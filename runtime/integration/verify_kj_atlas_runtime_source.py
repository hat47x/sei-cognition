#!/usr/bin/env python3

import argparse
import hashlib
import json
import os
import stat
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RuntimeSourceIdentity:
    repository: str
    source_commit: str
    backend_tree: str
    runtime_surface_tree: str
    pyproject_blob: str
    alembic_ini_blob: str
    alembic_tree: str
    src_tree: str


PINNED_IDENTITY = RuntimeSourceIdentity(
    repository="hat47x/kj-atlas",
    source_commit="4f28c13abe4176503c6fed863383a2d1db2299e9",
    backend_tree="7d71ac2b4d32bef90f3a481ade1b4c92ddddd084",
    runtime_surface_tree="208bea71eef4afed3ddfd3fabb36b0969d167a90",
    pyproject_blob="29d9427889a29cb8efcef10c59da5228c82147af",
    alembic_ini_blob="05ace092c712dfda73634ef70e7bcb52eb74c712",
    alembic_tree="fbecd06d167e162609ae8b844dda3c7585479960",
    src_tree="4c0b786a81bded22eab5d308289dc55a91cf8324",
)

ALLOWED_TOP_LEVEL = {"pyproject.toml", "alembic.ini", "alembic", "src"}


def _git_object_oid(kind: str, payload: bytes) -> str:
    header = f"{kind} {len(payload)}\0".encode("ascii")
    return hashlib.sha1(header + payload).hexdigest()


def _git_tree_oid(entries: list[tuple[bytes, bool, bytes, str]]) -> str:
    # Git treeの並び順は、directory名を末尾`/`付きとして比較する。
    entries.sort(key=lambda item: item[0] + (b"/" if item[1] else b""))

    body = bytearray()
    for name, _is_tree, mode, oid in entries:
        body.extend(mode)
        body.extend(b" ")
        body.extend(name)
        body.extend(b"\x00")
        body.extend(bytes.fromhex(oid))

    return _git_object_oid("tree", bytes(body))


def git_blob_oid(path: Path) -> str:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"regular file required: {path}")

    mode = path.stat().st_mode
    if mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH):
        raise ValueError(f"runtime source file must not be executable: {path}")

    return _git_object_oid("blob", path.read_bytes())


def git_tree_oid(directory: Path) -> str:
    if directory.is_symlink() or not directory.is_dir():
        raise ValueError(f"directory required: {directory}")

    entries: list[tuple[bytes, bool, bytes, str]] = []
    for child in directory.iterdir():
        name = os.fsencode(child.name)
        if b"\x00" in name or b"/" in name:
            raise ValueError(f"unsupported source path name: {child}")

        if child.is_symlink():
            raise ValueError(f"symlink is not allowed in runtime source bundle: {child}")

        if child.is_file():
            entries.append((name, False, b"100644", git_blob_oid(child)))
            continue

        if child.is_dir():
            try:
                next(child.iterdir())
            except StopIteration as exc:
                raise ValueError(
                    f"empty directory is not allowed in runtime source bundle: {child}"
                ) from exc
            entries.append((name, True, b"40000", git_tree_oid(child)))
            continue

        raise ValueError(f"unsupported source filesystem entry: {child}")

    return _git_tree_oid(entries)


def verify_runtime_bundle(
    backend_dir: Path,
    identity: RuntimeSourceIdentity = PINNED_IDENTITY,
) -> dict[str, object]:
    backend_dir = backend_dir.resolve(strict=True)
    if not backend_dir.is_dir():
        raise ValueError(f"KJ Atlas runtime source bundle is not a directory: {backend_dir}")

    actual_top_level = {entry.name for entry in backend_dir.iterdir()}
    if actual_top_level != ALLOWED_TOP_LEVEL:
        missing = sorted(ALLOWED_TOP_LEVEL - actual_top_level)
        extra = sorted(actual_top_level - ALLOWED_TOP_LEVEL)
        raise ValueError(
            f"runtime source bundle top-level mismatch: missing={missing} extra={extra}"
        )

    actual = {
        "pyprojectBlob": git_blob_oid(backend_dir / "pyproject.toml"),
        "alembicIniBlob": git_blob_oid(backend_dir / "alembic.ini"),
        "alembicTree": git_tree_oid(backend_dir / "alembic"),
        "srcTree": git_tree_oid(backend_dir / "src"),
        "runtimeSurfaceTree": git_tree_oid(backend_dir),
    }
    expected = {
        "pyprojectBlob": identity.pyproject_blob,
        "alembicIniBlob": identity.alembic_ini_blob,
        "alembicTree": identity.alembic_tree,
        "srcTree": identity.src_tree,
        "runtimeSurfaceTree": identity.runtime_surface_tree,
    }

    if actual != expected:
        mismatches = {
            key: {"actual": actual[key], "expected": expected[key]}
            for key in expected
            if actual[key] != expected[key]
        }
        raise ValueError(
            "runtime source bundle identity mismatch: "
            + json.dumps(mismatches, sort_keys=True)
        )

    return {
        "schema": "soza.kj-atlas-runtime-source-identity/v1",
        "verified": True,
        "sourceMode": "verified-runtime-bundle",
        "repository": identity.repository,
        "sourceCommit": identity.source_commit,
        "pinnedBackendTree": identity.backend_tree,
        "runtimeSurfaceTree": actual["runtimeSurfaceTree"],
        "verificationBasis": "pinned-git-object-identities",
        "runtimeSurface": actual,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify the pinned KJ Atlas runtime source bundle."
    )
    parser.add_argument("--backend-dir", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    try:
        payload = verify_runtime_bundle(args.backend_dir)
    except (OSError, ValueError) as exc:
        parser.exit(1, f"KJ Atlas runtime source verification failed: {exc}\n")

    rendered = json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    if args.output is not None:
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
