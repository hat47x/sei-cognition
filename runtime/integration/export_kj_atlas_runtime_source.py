#!/usr/bin/env python3

from __future__ import annotations

import argparse
import io
import json
import shutil
import subprocess
import tarfile
import tempfile
from pathlib import Path, PurePosixPath

from verify_kj_atlas_runtime_source import (
    PINNED_IDENTITY,
    RuntimeSourceIdentity,
    verify_runtime_bundle,
)

BACKEND_PREFIX = "03_Implement/backend"
ARCHIVE_PARENT_DIRECTORIES = {"03_Implement", BACKEND_PREFIX}
RUNTIME_PATHS = (
    f"{BACKEND_PREFIX}/pyproject.toml",
    f"{BACKEND_PREFIX}/alembic.ini",
    f"{BACKEND_PREFIX}/alembic",
    f"{BACKEND_PREFIX}/src",
)


def _run_git(checkout_dir: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", "-C", str(checkout_dir), *args],
        check=False,
        capture_output=True,
    )


def _require_git_repository(checkout_dir: Path, identity: RuntimeSourceIdentity) -> None:
    inside = _run_git(checkout_dir, "rev-parse", "--is-inside-work-tree")
    if inside.returncode != 0 or inside.stdout.strip() != b"true":
        raise ValueError(f"KJ Atlas Git repositoryを確認できません: {checkout_dir}")

    commit = _run_git(checkout_dir, "cat-file", "-e", f"{identity.source_commit}^{{commit}}")
    if commit.returncode != 0:
        raise ValueError(
            "KJ Atlas repositoryに固定commit objectがありません: "
            f"commit={identity.source_commit}"
        )


def _validate_archive_members(members: list[tarfile.TarInfo]) -> None:
    prefix = BACKEND_PREFIX + "/"
    allowed_roots = set(RUNTIME_PATHS)

    for member in members:
        raw_name = member.name.rstrip("/")
        path = PurePosixPath(raw_name)
        if path.is_absolute() or ".." in path.parts:
            raise ValueError(f"unsafe runtime source archive path: {member.name}")

        name = path.as_posix()
        if name in ARCHIVE_PARENT_DIRECTORIES:
            if not member.isdir():
                raise ValueError(f"runtime source archive parent must be a directory: {member.name}")
            continue
        if not name.startswith(prefix):
            raise ValueError(f"archive member escaped backend prefix: {member.name}")
        if member.issym() or member.islnk():
            raise ValueError(f"symlink is not allowed in runtime source archive: {member.name}")
        if not (member.isdir() or member.isfile()):
            raise ValueError(f"unsupported archive member: {member.name}")

        relative = name[len(prefix) :]
        root = relative.split("/", 1)[0]
        root_path = f"{BACKEND_PREFIX}/{root}"
        if root_path not in allowed_roots:
            raise ValueError(f"unexpected runtime source archive member: {member.name}")


def _paths_overlap(left: Path, right: Path) -> bool:
    left = left.expanduser().resolve(strict=False)
    right = right.expanduser().resolve(strict=False)
    return left == right or left in right.parents or right in left.parents


def _prepare_identity_output_path(
    path: Path,
    *,
    checkout_dir: Path,
    output_dir: Path,
) -> Path:
    checkout = checkout_dir.expanduser().resolve(strict=True)
    bundle = output_dir.expanduser().resolve(strict=False)
    if path.is_symlink():
        raise ValueError(f"identity output must not be a symlink: {path}")
    output = path.expanduser().resolve(strict=False)
    if output.exists():
        raise ValueError(f"identity output already exists: {output}")
    for label, protected in (
        ("KJ Atlas repository", checkout),
        ("runtime source bundle", bundle),
    ):
        if _paths_overlap(output, protected):
            raise ValueError(
                "identity output must be separated from source inputs and exported bundle: "
                f"output={output} overlaps={label}:{protected}"
            )
    return output


def export_runtime_bundle(
    checkout_dir: Path,
    output_dir: Path,
    identity: RuntimeSourceIdentity = PINNED_IDENTITY,
) -> dict[str, object]:
    checkout_dir = checkout_dir.resolve(strict=True)
    output_dir = output_dir.expanduser().resolve(strict=False)

    if output_dir.exists():
        raise ValueError(f"output directory already exists: {output_dir}")
    if output_dir == checkout_dir or checkout_dir in output_dir.parents:
        raise ValueError(f"output directory must not be inside the KJ Atlas repository: {output_dir}")

    _require_git_repository(checkout_dir, identity)

    archive = _run_git(
        checkout_dir,
        "archive",
        "--format=tar",
        identity.source_commit,
        "--",
        *RUNTIME_PATHS,
    )
    if archive.returncode != 0:
        detail = archive.stderr.decode("utf-8", errors="replace").strip()
        raise ValueError(f"固定commitからruntime sourceをexportできません: {detail}")

    # 一時展開先も最終bundleと同じ側へ置き、親processのTMPDIRへsource bytesを流さない。
    extraction_parent = output_dir.parent
    extraction_parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix="soza-kj-atlas-source-export-",
        dir=extraction_parent,
    ) as temporary:
        extraction_root = Path(temporary)
        with tarfile.open(fileobj=io.BytesIO(archive.stdout), mode="r:") as handle:
            members = handle.getmembers()
            _validate_archive_members(members)
            # archiveはGit自身が固定commitから生成し、上でpathとentry typeを全件検査している。
            # Python 3.10でも動作させるため、3.12以降のextraction filterには依存しない。
            handle.extractall(extraction_root, members=members)

        backend_dir = extraction_root / BACKEND_PREFIX
        if not backend_dir.is_dir():
            raise ValueError("runtime source archiveにbackend rootがありません")

        shutil.copytree(backend_dir, output_dir)

    try:
        verification = verify_runtime_bundle(output_dir, identity)
    except Exception:
        shutil.rmtree(output_dir, ignore_errors=True)
        raise

    return {
        "schema": "soza.kj-atlas-runtime-source-export/v1",
        "sourceAcquisition": "git-archive-from-pinned-commit",
        "checkoutRepository": str(checkout_dir),
        "sourceCommit": identity.source_commit,
        "outputDirectory": str(output_dir),
        "verification": verification,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "KJ Atlasの固定commit objectから、ISSUE-000070用の最小runtime source bundleをexportします。"
        )
    )
    parser.add_argument("--checkout-dir", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--identity-output", type=Path)
    args = parser.parse_args()

    try:
        identity_output = (
            _prepare_identity_output_path(
                args.identity_output,
                checkout_dir=args.checkout_dir,
                output_dir=args.output_dir,
            )
            if args.identity_output is not None
            else None
        )
        payload = export_runtime_bundle(args.checkout_dir, args.output_dir)
    except (OSError, ValueError, subprocess.SubprocessError, tarfile.TarError) as exc:
        parser.exit(1, f"KJ Atlas runtime source export failed: {exc}\n")

    rendered = json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    if identity_output is not None:
        identity_output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
