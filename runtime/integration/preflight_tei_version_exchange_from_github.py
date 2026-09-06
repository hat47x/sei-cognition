#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import tarfile
from pathlib import Path
from typing import Callable

import prepare_tei_fixed_reference_input as fixed_reference
import run_tei_bundle_adapter_compatibility as adapter_runner
import run_tei_revision_b_prepositioned as build_runner
import run_tei_version_exchange_evidence as version_exchange
import run_tei_version_exchange_from_github as github_runner
import verify_tei_execution_source_identity as source_identity
from runtime_path_safety import reject_symlink_path_or_ancestors

SCHEMA = "soza.tei-version-exchange-github-preflight/v1"
STOP_LINE = (
    "preflight ready != revision B source acquired != revision B build PASS "
    "!= Provider Plan execution PASS != SOZA Adapter compatibility PASS "
    "!= ISSUE-000072 Resolved"
)
EXPECTED_ERRORS = (
    OSError,
    ValueError,
    RuntimeError,
    subprocess.SubprocessError,
    tarfile.TarError,
)


def _is_within(candidate: Path, root: Path) -> bool:
    return candidate == root or root in candidate.parents


def _capture(name: str, action: Callable[[], dict[str, object]]) -> dict[str, object]:
    try:
        observation = action()
    except EXPECTED_ERRORS as exc:
        return {
            "name": name,
            "status": "blocked",
            "error": {
                "type": type(exc).__name__,
                "message": str(exc),
            },
        }
    return {
        "name": name,
        "status": "ready",
        "observation": observation,
    }


def _check_platform() -> dict[str, object]:
    system = platform.system().lower()
    machine = platform.machine().lower()
    if system != "linux" or machine not in {"x86_64", "amd64"}:
        raise ValueError(
            "TEI version exchange actual EvidenceはLinux/amd64を要求します: "
            f"system={system} machine={machine}"
        )
    return {
        "system": system,
        "machine": machine,
        "linuxAmd64": True,
    }


def _check_github_credential(env: dict[str, str] | None = None) -> dict[str, object]:
    values = os.environ if env is None else env
    if values.get("GITHUB_TOKEN"):
        source = "GITHUB_TOKEN"
    elif values.get("GH_TOKEN"):
        source = "GH_TOKEN"
    else:
        raise ValueError("GITHUB_TOKEN/GH_TOKENがありません")
    return {
        "present": True,
        "source": source,
        "valueReported": False,
        "networkAccessPerformed": False,
    }


def _resolve_go(executable: Path) -> Path:
    requested = executable.expanduser()
    if requested.name != "go":
        raise ValueError(
            "Linux actual EvidenceではGo executableのbasenameを'go'に固定します: "
            f"{requested}"
        )
    resolved = requested.resolve(strict=True)
    if not resolved.is_file() or not os.access(resolved, os.X_OK):
        raise ValueError(f"Go executableではありません: {resolved}")
    return resolved


def _go_env_for_executable(executable: Path, base: dict[str, str]) -> tuple[Path, dict[str, str]]:
    resolved = _resolve_go(executable)
    env = dict(base)
    env["PATH"] = str(resolved.parent) + os.pathsep + env.get("PATH", "")
    discovered = shutil.which("go", path=env["PATH"])
    if discovered is None or Path(discovered).resolve() != resolved:
        raise ValueError(
            "指定Go executableをpreflight PATH先頭へ固定できません: "
            f"expected={resolved} actual={discovered}"
        )
    return resolved, env


def _check_tei_go(executable: Path) -> dict[str, object]:
    resolved, env = _go_env_for_executable(executable, build_runner._controlled_go_env())
    env["GOTOOLCHAIN"] = "local"
    process = subprocess.run(
        ["go", "version"],
        cwd=resolved.parent,
        env=env,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=30,
    )
    if process.returncode != 0:
        raise ValueError(
            "E2 Go version確認に失敗しました: "
            + process.stderr.strip()
        )
    observed = process.stdout.strip()
    if not observed.startswith(f"go version {build_runner.EXPECTED_GO_VERSION} "):
        raise ValueError(
            "historical E2 Go toolchain versionが一致しません: "
            f"expected={build_runner.EXPECTED_GO_VERSION} actual={observed}"
        )
    return {
        "executable": str(resolved),
        "required": build_runner.EXPECTED_GO_VERSION,
        "observed": observed,
        "exactMatch": True,
        "implicitToolchainDownloadAllowed": False,
    }


def _check_soza_go(executable: Path, soza_repo_root: Path) -> dict[str, object]:
    resolved, env = _go_env_for_executable(
        executable,
        adapter_runner._go_toolchain_env(),
    )
    observation = adapter_runner._verify_soza_go_requirement(
        soza_repo_root,
        env=env,
    )
    return {
        "executable": str(resolved),
        "required": observation["required"],
        "observed": observation["observed"],
        "requirementSatisfied": True,
        "implicitToolchainDownloadAllowed": False,
    }


def _check_reference_input(
    reference_source_repo: Path | None,
    reference_evidence_bundle: Path | None,
) -> dict[str, object]:
    if (reference_source_repo is None) == (reference_evidence_bundle is None):
        raise ValueError(
            "exact revision A fixed inputはreference source repoまたは"
            "historical Evidence bundleのどちらか一方が必要です"
        )
    if reference_source_repo is not None:
        repo = reference_source_repo.expanduser().resolve(strict=True)
        verification = source_identity.verify_repository(
            repo,
            expected_objects=source_identity.REVISION_A_REFERENCE_OBJECTS,
            expected_head=source_identity.REVISION_A,
        )
        return {
            "mode": "git_checkout",
            "sourceCommit": source_identity.REVISION_A,
            "path": str(repo),
            "head": verification["head"],
            "worktreeCleanWithinBoundary": verification["worktreeCleanWithinBoundary"],
        }

    assert reference_evidence_bundle is not None
    verification = fixed_reference.verify_fixed_reference_input_bundle(
        reference_evidence_bundle
    )
    return {
        "mode": "historical_evidence_bundle",
        "sourceCommit": verification["sourceCommit"],
        "path": verification["archive"],
        "archiveSha256": verification["archiveSha256"],
    }


def _check_soza_source(
    soza_repo_root: Path,
    expected_soza_head: str | None,
) -> dict[str, object]:
    root = soza_repo_root.expanduser().resolve(strict=True)
    if not (root / "runtime/go/go.mod").is_file():
        raise ValueError(f"SOZA runtime/go moduleを確認できません: {root / 'runtime/go'}")
    verification = adapter_runner._verify_soza_source_identity(
        root,
        expected_head=expected_soza_head,
    )
    return {
        "repositoryRoot": str(root),
        "head": verification["head"],
        "expectedHead": expected_soza_head,
        "expectedHeadMatched": verification["expectedHeadMatched"],
        "worktreeCleanWithinBoundary": verification["worktreeCleanWithinBoundary"],
    }


def _check_output_path(
    output_dir: Path,
    *,
    soza_repo_root: Path,
    reference_source_repo: Path | None,
    reference_evidence_bundle: Path | None,
    overwrite: bool,
) -> dict[str, object]:
    requested = output_dir.expanduser()
    reject_symlink_path_or_ancestors(
        requested,
        "TEI version exchange preflight Evidence directory",
    )
    resolved = requested.resolve(strict=False)
    if resolved.exists() and not resolved.is_dir():
        raise ValueError(
            f"TEI version exchange Evidence出力先がdirectoryではありません: {resolved}"
        )

    soza_root = soza_repo_root.expanduser().resolve(strict=True)
    roots: list[tuple[str, Path]] = [("SOZA repository", soza_root)]
    if reference_source_repo is not None:
        reference_root = reference_source_repo.expanduser().resolve(strict=True)
        roots.append(("revision A reference checkout", reference_root))
    for label, root in roots:
        if _is_within(resolved, root):
            raise ValueError(
                f"Evidence directoryを{label}配下には置けません: output={resolved} root={root}"
            )
        if _is_within(root, resolved):
            raise ValueError(
                f"Evidence directoryで{label}を包含できません: output={resolved} root={root}"
            )

    bundle = None
    if reference_evidence_bundle is not None:
        bundle = reference_evidence_bundle.expanduser().resolve(strict=True)
        if _is_within(bundle, resolved):
            raise ValueError(
                "Evidence directoryでhistorical reference bundleを包含できません: "
                f"output={resolved} bundle={bundle}"
            )

    wrapper_report = resolved / github_runner.REPORT_NAME
    reject_symlink_path_or_ancestors(
        wrapper_report,
        "TEI GitHub-acquired version exchange report",
    )
    canonical_paths = [
        resolved / version_exchange.BUNDLE_NAME,
        resolved / version_exchange.REPORT_NAME,
        wrapper_report,
    ]
    existing = [path for path in canonical_paths if path.exists()]
    if existing and not overwrite:
        raise ValueError(
            "既存Evidenceを無言で上書きしません。--overwriteを明示してください: "
            + ", ".join(str(path) for path in existing)
        )
    if overwrite:
        for path in existing:
            if path == wrapper_report:
                if not path.is_file():
                    raise ValueError(f"wrapper report出力先がfileではありません: {path}")
            elif not path.is_file() and not path.is_symlink():
                raise ValueError(f"Evidence出力先がfileではありません: {path}")

    return {
        "outputDirectory": str(resolved),
        "overwrite": overwrite,
        "existingCanonicalOutputs": [str(path) for path in existing],
        "staticPathSafetyVerified": True,
        "revisionBTemporarySourceRelationship": "deferred_until_materialization",
        "filesystemMutationPerformed": False,
    }


def run_preflight(
    reference_source_repo: Path | None,
    soza_repo_root: Path,
    output_dir: Path,
    *,
    reference_evidence_bundle: Path | None = None,
    tei_go_executable: Path,
    soza_go_executable: Path,
    expected_soza_head: str | None = None,
    overwrite: bool = False,
    env: dict[str, str] | None = None,
) -> dict[str, object]:
    checks = [
        _capture("execution_platform", _check_platform),
        _capture("github_credential", lambda: _check_github_credential(env)),
        _capture(
            "revision_a_fixed_reference_identity",
            lambda: _check_reference_input(
                reference_source_repo,
                reference_evidence_bundle,
            ),
        ),
        _capture(
            "soza_source_identity",
            lambda: _check_soza_source(soza_repo_root, expected_soza_head),
        ),
        _capture("tei_go_toolchain", lambda: _check_tei_go(tei_go_executable)),
        _capture(
            "soza_go_toolchain",
            lambda: _check_soza_go(soza_go_executable, soza_repo_root),
        ),
        _capture(
            "output_path",
            lambda: _check_output_path(
                output_dir,
                soza_repo_root=soza_repo_root,
                reference_source_repo=reference_source_repo,
                reference_evidence_bundle=reference_evidence_bundle,
                overwrite=overwrite,
            ),
        ),
    ]
    blocked = [str(check["name"]) for check in checks if check["status"] != "ready"]
    ready = not blocked
    return {
        "schema": SCHEMA,
        "result": "ready" if ready else "blocked",
        "ready": ready,
        "blockedChecks": blocked,
        "checks": checks,
        "networkAccessPerformed": False,
        "revisionBSourceMaterialized": False,
        "evidenceOutputCreated": False,
        "qualityJudgement": "not_evaluated",
        "stopLine": STOP_LINE,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "GitHub acquisition→canonical E2/E3を開始する前に、credential、platform、"
            "revision A fixed input、SOZA source、E2/E3 Go、output pathを副作用なしで一括検査します。"
        ),
        allow_abbrev=False,
    )
    reference_group = parser.add_mutually_exclusive_group(required=True)
    reference_group.add_argument("--reference-source-repo", type=Path)
    reference_group.add_argument("--reference-evidence-bundle", type=Path)
    parser.add_argument(
        "--soza-repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
    )
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--tei-go-executable", required=True, type=Path)
    parser.add_argument("--soza-go-executable", required=True, type=Path)
    parser.add_argument("--expected-soza-head")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = run_preflight(
        args.reference_source_repo,
        args.soza_repo_root,
        args.output_dir,
        reference_evidence_bundle=args.reference_evidence_bundle,
        tei_go_executable=args.tei_go_executable,
        soza_go_executable=args.soza_go_executable,
        expected_soza_head=args.expected_soza_head,
        overwrite=args.overwrite,
    )
    if args.json:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    else:
        print(f"TEI version exchange GitHub preflight: {result['result']}")
        for check in result["checks"]:
            print(f"- {check['name']}: {check['status']}")
            if check["status"] != "ready":
                print(f"  {check['error']['message']}")
        print(result["stopLine"])
    return 0 if result["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
