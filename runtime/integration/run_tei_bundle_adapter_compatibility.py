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

import git_object_environment
import verify_tei_evidence_bundle as bundle_verifier
import verify_tei_execution_source_identity as source_identity

REVISION_A = source_identity.REVISION_A
REVISION_B = source_identity.REVISION_B
FIXED_RUN = "reference/order_rollout.durable-run.m0.21.start.json"
FIXED_WORKSPACE = "reference/workspace"
FIXED_PLUGIN_LOCK = "reference/workspace/.tei/plugin-lock.json"
LIVE_TEST = "^TestLiveTEIProviderPlan$"
MAX_STAGE_OUTPUT = 32 * 1024
SOZA_EVIDENCE_PATHS = [
    "runtime/go",
    "runtime/integration/run_tei_version_exchange_evidence.py",
    "runtime/integration/run_tei_revision_b_prepositioned.py",
    "runtime/integration/run_tei_bundle_adapter_compatibility.py",
    "runtime/integration/prepare_tei_fixed_reference_input.py",
    "runtime/integration/runtime_path_safety.py",
    "runtime/integration/git_object_environment.py",
    "runtime/integration/verify_tei_evidence_bundle.py",
    "runtime/integration/verify_tei_execution_source_identity.py",
]
REFERENCE_OBJECTS = source_identity.REVISION_A_REFERENCE_OBJECTS
STOP_LINE = (
    "current SOZA Adapter compatibility verified for exact-B executable + exact-A fixed input bundle "
    "!= arbitrary TEI version compatibility != Release Evidence "
    "!= Operational Evidence != ISSUE-000072 Resolved"
)


class TEIAdapterStageError(RuntimeError):
    def __init__(
        self,
        stage: str,
        message: str,
        *,
        command: list[str] | None = None,
        returncode: int | None = None,
        stdout: str = "",
        stderr: str = "",
    ) -> None:
        super().__init__(f"{stage}: {message}")
        self.stage = stage
        self.message = message
        self.command = command
        self.returncode = returncode
        self.stdout = stdout[-MAX_STAGE_OUTPUT:]
        self.stderr = stderr[-MAX_STAGE_OUTPUT:]

    def as_dict(self) -> dict[str, object]:
        value: dict[str, object] = {
            "stage": self.stage,
            "message": self.message,
        }
        if self.command is not None:
            value["command"] = self.command
        if self.returncode is not None:
            value["returnCode"] = self.returncode
        if self.stdout:
            value["stdoutTail"] = self.stdout
        if self.stderr:
            value["stderrTail"] = self.stderr
        return value


def _wrap_stage(stage: str, exc: Exception) -> TEIAdapterStageError:
    if isinstance(exc, TEIAdapterStageError):
        return exc
    return TEIAdapterStageError(stage, str(exc))


def _run_stage(
    stage: str,
    argv: list[str],
    *,
    cwd: Path,
    env: dict[str, str],
    timeout: int,
) -> subprocess.CompletedProcess[str]:
    try:
        result = subprocess.run(
            argv,
            cwd=cwd,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise TEIAdapterStageError(stage, str(exc), command=argv) from exc
    if result.returncode != 0:
        raise TEIAdapterStageError(
            stage,
            "external process returned non-zero status",
            command=argv,
            returncode=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
        )
    return result


def _parse_go_version(value: str) -> tuple[int, int, int]:
    token = value.strip()
    if token.startswith("go"):
        token = token[2:]
    parts = token.split(".")
    if len(parts) not in {2, 3} or not all(part.isdigit() for part in parts):
        raise ValueError(f"Go versionを解釈できません: {value!r}")
    numbers = [int(part) for part in parts]
    if len(numbers) == 2:
        numbers.append(0)
    return numbers[0], numbers[1], numbers[2]


def _read_go_directive(go_mod: Path) -> str:
    try:
        lines = go_mod.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise TEIAdapterStageError(
            "soza_go_toolchain",
            f"current SOZA go.modを読めません: {exc}",
        ) from exc
    for line in lines:
        fields = line.strip().split()
        if len(fields) == 2 and fields[0] == "go":
            try:
                _parse_go_version(fields[1])
            except ValueError as exc:
                raise TEIAdapterStageError(
                    "soza_go_toolchain",
                    f"current SOZA go.modのGo directiveを解釈できません: {fields[1]!r}",
                ) from exc
            return fields[1]
    raise TEIAdapterStageError(
        "soza_go_toolchain",
        "current SOZA go.modにGo directiveがありません",
    )


def _go_toolchain_env() -> dict[str, str]:
    env = os.environ.copy()
    env["GOWORK"] = "off"
    env["GOENV"] = "off"
    env["GOTOOLCHAIN"] = "local"
    for key in (
        "GOFLAGS",
        "GOOS",
        "GOARCH",
        "GOAMD64",
        "GOEXPERIMENT",
        "CGO_ENABLED",
    ):
        env.pop(key, None)
    return env


def _verify_soza_go_requirement(
    soza_repo_root: Path,
    *,
    env: dict[str, str] | None = None,
) -> dict[str, str]:
    go_root = soza_repo_root / "runtime/go"
    requirement = _read_go_directive(go_root / "go.mod")
    process = _run_stage(
        "soza_go_toolchain",
        ["go", "version"],
        cwd=go_root,
        env=_go_toolchain_env() if env is None else env,
        timeout=30,
    )
    observed = process.stdout.strip()
    fields = observed.split()
    if len(fields) < 3 or fields[0:2] != ["go", "version"]:
        raise TEIAdapterStageError(
            "soza_go_toolchain",
            f"go version出力を解釈できません: {observed!r}",
            command=["go", "version"],
            stdout=process.stdout,
            stderr=process.stderr,
        )
    try:
        actual = _parse_go_version(fields[2])
        required = _parse_go_version(requirement)
    except ValueError as exc:
        raise TEIAdapterStageError(
            "soza_go_toolchain",
            str(exc),
            command=["go", "version"],
            stdout=process.stdout,
            stderr=process.stderr,
        ) from exc
    if actual < required:
        raise TEIAdapterStageError(
            "soza_go_toolchain",
            "current SOZA go.modのGo要件を満たしません: "
            f"required>={requirement} actual={fields[2]}",
            command=["go", "version"],
            stdout=process.stdout,
            stderr=process.stderr,
        )
    return {
        "required": requirement,
        "observed": observed,
    }


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
        env=git_object_environment.controlled_git_environment(),
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
        "--ignored=matching",
        "--",
        *paths,
    ).stdout.splitlines()
    dirty = [line for line in dirty if line.strip()]
    if dirty:
        raise ValueError(
            "SOZA Adapter / Evidence runner境界に未commit変更、untracked file、またはignored entryがあります: "
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
        "gitObjectEnvironmentControlled": True,
        "replaceObjectsDisabled": True,
    }


def _controlled_env(paths: dict[str, Path], source_state_ref: str) -> dict[str, str]:
    env = _go_toolchain_env()
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

    try:
        if not (go_root / "go.mod").is_file():
            raise ValueError(f"SOZA runtime/go moduleを確認できません: {go_root}")
        if not (go_root / "teiintegration/tei_live_test.go").is_file():
            raise ValueError("current teiintegration live testを確認できません")
    except ValueError as exc:
        raise _wrap_stage("soza_runtime_layout", exc) from exc

    try:
        soza_source = _verify_soza_source_identity(
            soza_repo_root, expected_head=expected_soza_head
        )
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        raise _wrap_stage("soza_source_identity", exc) from exc

    try:
        verification = bundle_verifier.verify_bundle(
            archive,
            expected_source_commit=expected_source_commit,
        )
    except (OSError, ValueError, tarfile.TarError) as exc:
        raise _wrap_stage("bundle_identity_verification", exc) from exc

    observation = verification["observation"]
    metadata = verification["metadata"]
    source_commit = str(observation["source_commit"])
    archive_sha256 = str(observation["archive_sha256"])

    try:
        _ensure_linux_amd64()
    except ValueError as exc:
        raise _wrap_stage("execution_platform", exc) from exc

    with tempfile.TemporaryDirectory(prefix="soza-tei-adapter-") as tmp:
        try:
            paths = _stage_bundle(archive, Path(tmp))
        except (OSError, ValueError, tarfile.TarError) as exc:
            raise _wrap_stage("bundle_staging", exc) from exc

        try:
            reference_observation = _verify_reference_input_identity(paths, metadata)
        except (OSError, ValueError) as exc:
            raise _wrap_stage("reference_input_identity", exc) from exc

        source_state_ref = (
            f"tei-cli:{source_commit}:reference:{REVISION_A}:"
            f"bundle-sha256:{archive_sha256}"
        )
        env = _controlled_env(paths, source_state_ref)
        go_observation = _verify_soza_go_requirement(soza_repo_root, env=env)

        _run_stage(
            "soza_teiintegration_live_test",
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
            timeout=180,
        )

        try:
            post_live_soza_source = _verify_soza_source_identity(
                soza_repo_root,
                expected_head=expected_soza_head,
            )
        except (OSError, ValueError, subprocess.SubprocessError) as exc:
            detail = ValueError(
                "SOZA Adapter live test実行後のsource identity再検証に失敗しました: "
                f"{exc}"
            )
            raise _wrap_stage("soza_source_identity", detail) from exc

    return {
        "schema": "soza.tei-bundle-adapter-compatibility/v1",
        "result": "adapter_compatible",
        "sourceCommit": source_commit,
        "referenceInput": reference_observation,
        "sozaSource": soza_source,
        "postLiveTestSozaSource": post_live_soza_source,
        "sozaGoRequirement": go_observation["required"],
        "sozaGoVersion": go_observation["observed"],
        "binarySha256": observation["binary_sha256"],
        "providerPlanSha256": observation["provider_plan_sha256"],
        "archiveSha256": archive_sha256,
        "liveTest": "runtime/go/teiintegration.TestLiveTEIProviderPlan",
        "sourceStateRef": source_state_ref,
        "completedStages": [
            "soza_runtime_layout",
            "soza_source_identity",
            "bundle_identity_verification",
            "execution_platform",
            "bundle_staging",
            "reference_input_identity",
            "soza_go_toolchain",
            "soza_teiintegration_live_test",
        ],
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
    except TEIAdapterStageError as exc:
        print(
            "TEI bundle Adapter compatibility run failed at "
            f"{exc.stage}: {exc.message}"
        )
        return 1
    except (
        OSError,
        ValueError,
        RuntimeError,
        subprocess.SubprocessError,
        tarfile.TarError,
    ) as exc:
        print(f"TEI bundle Adapter compatibility run failed before staged execution: {exc}")
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
        print(f"- SOZA source commit: {result['sozaSource']['head']}")
        print(f"- SOZA Go requirement: {result['sozaGoRequirement']}")
        print(f"- SOZA Go: {result['sozaGoVersion']}")
        print(f"- binary SHA-256: {result['binarySha256']}")
        print(f"- Provider Plan SHA-256: {result['providerPlanSha256']}")
        print(result["stopLine"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())