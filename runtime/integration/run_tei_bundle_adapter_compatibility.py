#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import tarfile
import tempfile
from pathlib import Path, PurePosixPath
from typing import Mapping

import verify_tei_evidence_bundle as bundle_verifier
import verify_tei_execution_source_identity as source_identity

REVISION_A = source_identity.REVISION_A
REVISION_B = source_identity.REVISION_B
FIXED_RUN = "reference/order_rollout.durable-run.m0.21.start.json"
FIXED_WORKSPACE = "reference/workspace"
FIXED_PLUGIN_LOCK = "reference/workspace/.tei/plugin-lock.json"
LIVE_TEST = "^TestLiveTEIProviderPlan$"
SOZA_EVIDENCE_PATHS = [
    "runtime/go",
    "runtime/integration/run_tei_bundle_adapter_compatibility.py",
    "runtime/integration/verify_tei_evidence_bundle.py",
    "runtime/integration/verify_tei_execution_source_identity.py",
]
REFERENCE_OBJECTS = source_identity.REVISION_A_REFERENCE_OBJECTS
STOP_LINE = (
    "current SOZA Adapter compatibility verified for exact-B executable + exact-A fixed input bundle "
    "!= arbitrary TEI version compatibility != Release Evidence "
    "!= Operational Evidence != ISSUE-000072 Resolved"
)


def _member_name(member: tarfile.TarInfo) -> str:
    name = member.name
    while name.startswith("./"):
        name = name[2:]
    path = PurePosixPath(name)
    if not name or path.is_absolute() or ".." in path.parts:
        raise ValueError(f"bundle member pathが不正です: {member.name!r}")
    return path.as_posix()


def _ensure_linux_amd64() -> None:
    system = platform.system().lower()
    machine = platform.machine().lower()
    if system != "linux" or machine not in {"x86_64", "amd64"}:
        raise ValueError(
            "Linux/amd64 Evidence bundleをlive実行できない環境です: "
            f"system={system} machine={machine}"
        )


def _stage_bundle(archive: Path, target: Path) -> dict[str, Path]:
    target.mkdir(parents=True, exist_ok=True)
    required = {"bin/tei", FIXED_RUN, FIXED_PLUGIN_LOCK}

    with tarfile.open(archive, mode="r:gz") as tar:
        members: dict[str, tarfile.TarInfo] = {}
        for member in tar.getmembers():
            name = _member_name(member)
            if member.issym() or member.islnk() or member.isdev():
                raise ValueError(f"bundleにlink/device memberを含められません: {name}")
            if name in members:
                raise ValueError(f"bundle memberが重複しています: {name}")
            members[name] = member

        missing = required - members.keys()
        if missing:
            raise ValueError(
                f"live Adapter検査に必要なbundle memberがありません: {sorted(missing)}"
            )

        for name, member in members.items():
            if not (
                name == "bin/tei"
                or name == FIXED_RUN
                or name == FIXED_WORKSPACE
                or name.startswith(FIXED_WORKSPACE + "/")
            ):
                continue
            destination = target / PurePosixPath(name)
            if member.isdir():
                destination.mkdir(parents=True, exist_ok=True)
                continue
            if not member.isfile():
                raise ValueError(
                    f"live Adapter検査対象にregular file以外があります: {name}"
                )
            handle = tar.extractfile(member)
            if handle is None:
                raise ValueError(f"bundle memberを読み込めません: {name}")
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(handle.read())
            destination.chmod(member.mode & 0o777)

    binary = target / "bin/tei"
    workspace = target / FIXED_WORKSPACE
    run = target / FIXED_RUN
    plugin_lock = target / FIXED_PLUGIN_LOCK
    if not binary.is_file() or not os.access(binary, os.X_OK):
        raise ValueError("staged bin/teiがexecutable fileではありません")
    if not workspace.is_dir():
        raise ValueError("staged reference workspaceがdirectoryではありません")
    for path in (run, plugin_lock):
        if not path.is_file():
            raise ValueError(f"staged fixed reference inputがfileではありません: {path}")
    return {
        "executable": binary,
        "workspace": workspace,
        "run": run,
        "plugin_lock": plugin_lock,
    }


def _git_blob_sha1(path: Path) -> str:
    payload = path.read_bytes()
    header = f"blob {len(payload)}\0".encode("ascii")
    return hashlib.sha1(header + payload).hexdigest()


def _git_tree_sha1(root: Path) -> str:
    entries: list[tuple[bytes, str, str, str]] = []
    for path in root.iterdir():
        if path.is_symlink():
            raise ValueError(f"fixed reference workspaceにsymlinkがあります: {path}")
        if path.is_dir():
            mode = "40000"
            digest = _git_tree_sha1(path)
            sort_key = path.name.encode("utf-8") + b"/"
        elif path.is_file():
            mode = "100755" if path.stat().st_mode & 0o111 else "100644"
            digest = _git_blob_sha1(path)
            sort_key = path.name.encode("utf-8")
        else:
            raise ValueError(f"fixed reference workspaceに未対応entryがあります: {path}")
        entries.append((sort_key, mode, path.name, digest))

    body = bytearray()
    for _, mode, name, digest in sorted(entries, key=lambda entry: entry[0]):
        body.extend(mode.encode("ascii"))
        body.extend(b" ")
        body.extend(name.encode("utf-8"))
        body.extend(b"\0")
        body.extend(bytes.fromhex(digest))
    header = f"tree {len(body)}\0".encode("ascii")
    return hashlib.sha1(header + body).hexdigest()


def _verify_reference_input_identity(
    paths: dict[str, Path],
    metadata: Mapping[str, object],
    *,
    expected_objects: Mapping[str, str] = REFERENCE_OBJECTS,
) -> dict[str, object]:
    expected_metadata = {
        "reference_input_source_commit": REVISION_A,
        "reference_workspace_tree": expected_objects[FIXED_WORKSPACE],
        "reference_run_blob": expected_objects[FIXED_RUN],
        "reference_plugin_lock_blob": expected_objects[FIXED_PLUGIN_LOCK],
    }
    for key, expected in expected_metadata.items():
        actual = metadata.get(key)
        if actual != expected:
            raise ValueError(
                "bundle metadataのfixed reference identityが期待値と一致しません: "
                f"field={key} expected={expected} actual={actual!r}"
            )

    observed = {
        FIXED_WORKSPACE: _git_tree_sha1(paths["workspace"]),
        FIXED_RUN: _git_blob_sha1(paths["run"]),
        FIXED_PLUGIN_LOCK: _git_blob_sha1(paths["plugin_lock"]),
    }
    for path, expected in expected_objects.items():
        actual = observed[path]
        if actual != expected:
            raise ValueError(
                "staged fixed revision A reference inputのGit object identityが一致しません: "
                f"path={path} expected={expected} actual={actual}"
            )
    return {
        "sourceCommit": REVISION_A,
        "objects": observed,
    }


def _git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=check,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def _verify_soza_source_identity(
    repo: Path,
    *,
    paths: list[str] = SOZA_EVIDENCE_PATHS,
    expected_head: str | None = None,
) -> dict[str, object]:
    inside = _git(repo, "rev-parse", "--is-inside-work-tree", check=False)
    if inside.returncode != 0 or inside.stdout.strip() != "true":
        raise ValueError(f"SOZA Git repositoryではありません: {repo}")
    dirty = _git(
        repo,
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
        "--",
        *paths,
    ).stdout.splitlines()
    dirty = [line for line in dirty if line.strip()]
    if dirty:
        raise ValueError(
            "SOZA Adapter / Evidence runner境界に未commit変更またはuntracked fileがあります: "
            + " | ".join(dirty)
        )
    head = _git(repo, "rev-parse", "HEAD").stdout.strip()
    if expected_head is not None and head != expected_head:
        raise ValueError(
            f"SOZA HEADが期待値と一致しません: expected={expected_head} actual={head}"
        )
    objects: dict[str, str] = {}
    for path in paths:
        result = _git(repo, "rev-parse", f"HEAD:{path}", check=False)
        if result.returncode != 0:
            raise ValueError(f"SOZA Git objectを取得できません: {path}")
        objects[path] = result.stdout.strip()
    return {
        "head": head,
        "expectedHead": expected_head,
        "expectedHeadMatched": expected_head is None or head == expected_head,
        "objects": objects,
        "worktreeCleanWithinBoundary": True,
    }


def _controlled_env(paths: dict[str, Path], source_state_ref: str) -> dict[str, str]:
    env = os.environ.copy()
    env["GOWORK"] = "off"
    env["GOENV"] = "off"
    env["GOTOOLCHAIN"] = "local"
    env.pop("GOFLAGS", None)
    env.pop("GOOS", None)
    env.pop("GOARCH", None)
    env.update(
        {
            "SOZA_E3B_TEI_LIVE": "1",
            "SOZA_TEI_EXECUTABLE": str(paths["executable"]),
            "SOZA_TEI_WORKSPACE": str(paths["workspace"]),
            "SOZA_TEI_RUN": str(paths["run"]),
            "SOZA_TEI_PLUGIN_LOCK": str(paths["plugin_lock"]),
            "SOZA_TEI_SOURCE_STATE_REF": source_state_ref,
        }
    )
    return env


def run_compatibility(
    archive: Path,
    *,
    soza_repo_root: Path,
    expected_source_commit: str = REVISION_B,
    expected_soza_head: str | None = None,
) -> dict[str, object]:
    archive = archive.expanduser().resolve(strict=True)
    soza_repo_root = soza_repo_root.expanduser().resolve(strict=True)
    go_root = soza_repo_root / "runtime/go"
    if not (go_root / "go.mod").is_file():
        raise ValueError(f"SOZA runtime/go moduleを確認できません: {go_root}")
    if not (go_root / "teiintegration/tei_live_test.go").is_file():
        raise ValueError("current teiintegration live testを確認できません")

    soza_source = _verify_soza_source_identity(
        soza_repo_root, expected_head=expected_soza_head
    )

    verification = bundle_verifier.verify_bundle(
        archive,
        expected_source_commit=expected_source_commit,
    )
    observation = verification["observation"]
    metadata = verification["metadata"]
    source_commit = str(observation["source_commit"])
    archive_sha256 = str(observation["archive_sha256"])

    _ensure_linux_amd64()
    with tempfile.TemporaryDirectory(prefix="soza-tei-adapter-") as tmp:
        paths = _stage_bundle(archive, Path(tmp))
        reference_observation = _verify_reference_input_identity(paths, metadata)
        source_state_ref = (
            f"tei-cli:{source_commit}:reference:{REVISION_A}:"
            f"bundle-sha256:{archive_sha256}"
        )
        env = _controlled_env(paths, source_state_ref)
        go_version_process = subprocess.run(
            ["go", "version"],
            cwd=go_root,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30,
            check=False,
        )
        if go_version_process.returncode != 0:
            detail = (
                go_version_process.stderr.strip()
                or go_version_process.stdout.strip()
            )[-8192:]
            raise RuntimeError("SOZA Go toolchainを確認できません: " + detail)
        go_version = go_version_process.stdout.strip()

        process = subprocess.run(
            [
                "go",
                "test",
                "./teiintegration",
                "-run",
                LIVE_TEST,
                "-count=1",
                "-v",
            ],
            cwd=go_root,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=180,
            check=False,
        )
        if process.returncode != 0:
            detail = (process.stderr.strip() or process.stdout.strip())[-32768:]
            raise RuntimeError(
                "current SOZA teiintegration live testが成立しませんでした: "
                + detail
            )

    return {
        "schema": "soza.tei-bundle-adapter-compatibility/v1",
        "result": "adapter_compatible",
        "sourceCommit": source_commit,
        "referenceInput": reference_observation,
        "sozaSource": soza_source,
        "sozaGoVersion": go_version,
        "binarySha256": observation["binary_sha256"],
        "providerPlanSha256": observation["provider_plan_sha256"],
        "archiveSha256": archive_sha256,
        "liveTest": "runtime/go/teiintegration.TestLiveTEIProviderPlan",
        "sourceStateRef": source_state_ref,
        "qualityJudgement": "not_evaluated",
        "stopLine": STOP_LINE,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "exact-B executable + exact-A fixed reference inputを含む検証済みTEI Evidence "
            "bundleを一時領域へ安全にstageし、current SOZA teiintegration live testで"
            "actual CLI process / strict decode / Capability Observation mappingを確認します。"
        ),
        allow_abbrev=False,
    )
    parser.add_argument("archive", type=Path)
    parser.add_argument(
        "--soza-repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
    )
    parser.add_argument("--expected-source-commit", default=REVISION_B)
    parser.add_argument("--expected-soza-head")
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = run_compatibility(
            args.archive,
            soza_repo_root=args.soza_repo_root,
            expected_source_commit=args.expected_source_commit,
            expected_soza_head=args.expected_soza_head,
        )
    except (
        OSError,
        ValueError,
        RuntimeError,
        subprocess.SubprocessError,
        tarfile.TarError,
    ) as exc:
        print(f"TEI bundle Adapter compatibility run failed: {exc}")
        return 1
    if args.json:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    else:
        print("TEI bundle Adapter compatibility: verified")
        print(f"- source commit: {result['sourceCommit']}")
        print(
            f"- reference input source commit: "
            f"{result['referenceInput']['sourceCommit']}"
        )
        print(f"- binary SHA-256: {result['binarySha256']}")
        print(f"- Provider Plan SHA-256: {result['providerPlanSha256']}")
        print(result["stopLine"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
