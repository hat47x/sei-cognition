#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

import git_object_environment
import preflight_tei_version_exchange_from_github as common
import prepare_tei_revision_b_checkout as checkout_prepare
import run_tei_version_exchange_evidence as version_exchange
import verify_tei_execution_source_identity as source_identity
from runtime_path_safety import reject_symlink_path_or_ancestors

SCHEMA = "soza.tei-version-exchange-local-preflight/v1"
STOP_LINE = (
    "local preflight ready != revision B checkout prepared "
    "!= revision B build PASS != Provider Plan execution PASS "
    "!= SEI Adapter compatibility PASS != ISSUE-000072 Resolved"
)


def _is_within(candidate: Path, root: Path) -> bool:
    return candidate == root or root in candidate.parents


def _git(
    repo: Path,
    *args: str,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=git_object_environment.controlled_git_environment(),
    )
    if check and result.returncode != 0:
        raise ValueError(
            f"Git command failed: {' '.join(args)}: {result.stderr.strip()}"
        )
    return result


def _check_source_clone(source_repo: Path) -> dict[str, object]:
    repo = source_repo.expanduser().resolve(strict=True)
    checkout_prepare._ensure_git_worktree(repo)
    checkout_prepare._ensure_self_contained_object_database(repo, "source clone")
    checkout_prepare._ensure_revision_available(repo)

    observed: dict[str, str] = {}
    for path, expected in source_identity.EXPECTED_OBJECTS.items():
        result = _git(repo, "rev-parse", f"{source_identity.REVISION_B}:{path}")
        actual = result.stdout.strip()
        observed[path] = actual
        if actual != expected:
            raise ValueError(
                "source clone内revision B object identityが期待値と一致しません: "
                f"path={path} expected={expected} actual={actual}"
            )

    state = checkout_prepare._source_state(repo)
    return {
        "repositoryRoot": str(repo),
        "revisionAvailable": source_identity.REVISION_B,
        "revisionBExecutionSourceObjects": observed,
        "sourceObjectDatabaseSelfContained": True,
        "sourceState": state,
        "gitObjectEnvironmentControlled": True,
        "replaceObjectsDisabled": True,
        "networkAccessPerformed": False,
        "filesystemMutationPerformed": False,
    }


def _normalized_new_path(path: Path, label: str) -> Path:
    requested = path.expanduser()
    reject_symlink_path_or_ancestors(requested, label)
    resolved = requested.resolve(strict=False)
    if resolved.exists():
        raise ValueError(f"{label}は新規pathである必要があります: {resolved}")
    if not resolved.parent.is_dir():
        raise ValueError(f"{label}のparent directoryがありません: {resolved.parent}")
    return resolved


def _reject_overlap(candidate: Path, label: str, roots: list[tuple[str, Path]]) -> None:
    for root_label, root in roots:
        if _is_within(candidate, root):
            raise ValueError(
                f"{label}を{root_label}配下には置けません: candidate={candidate} root={root}"
            )
        if _is_within(root, candidate):
            raise ValueError(
                f"{label}で{root_label}を包含できません: candidate={candidate} root={root}"
            )


def _check_checkout_output_path(
    checkout_output: Path,
    *,
    source_repo: Path,
    soza_repo_root: Path,
    reference_source_repo: Path | None,
    reference_evidence_bundle: Path | None,
    evidence_output_dir: Path,
) -> dict[str, object]:
    output = _normalized_new_path(
        checkout_output,
        "revision B checkout output",
    )
    source = source_repo.expanduser().resolve(strict=True)
    soza = soza_repo_root.expanduser().resolve(strict=True)
    evidence = evidence_output_dir.expanduser().resolve(strict=False)
    roots: list[tuple[str, Path]] = [
        ("source clone", source),
        ("SEI repository", soza),
        ("Evidence directory", evidence),
    ]
    if reference_source_repo is not None:
        roots.append(
            (
                "revision A reference checkout",
                reference_source_repo.expanduser().resolve(strict=True),
            )
        )
    _reject_overlap(output, "revision B checkout output", roots)

    if reference_evidence_bundle is not None:
        bundle = reference_evidence_bundle.expanduser().resolve(strict=True)
        if _is_within(bundle, output):
            raise ValueError(
                "revision B checkout outputでhistorical reference bundleを包含できません: "
                f"output={output} bundle={bundle}"
            )

    return {
        "checkoutOutput": str(output),
        "newPathRequired": True,
        "sourceCheckoutSeparated": True,
        "evidenceOutputSeparated": True,
        "filesystemMutationPerformed": False,
    }


def _check_evidence_output_path(
    output_dir: Path,
    *,
    source_repo: Path,
    checkout_output: Path,
    soza_repo_root: Path,
    reference_source_repo: Path | None,
    reference_evidence_bundle: Path | None,
    overwrite: bool,
) -> dict[str, object]:
    requested = output_dir.expanduser()
    reject_symlink_path_or_ancestors(
        requested,
        "TEI local version exchange preflight Evidence directory",
    )
    resolved = requested.resolve(strict=False)
    if resolved.exists() and not resolved.is_dir():
        raise ValueError(f"Evidence出力先がdirectoryではありません: {resolved}")

    source = source_repo.expanduser().resolve(strict=True)
    checkout = checkout_output.expanduser().resolve(strict=False)
    soza = soza_repo_root.expanduser().resolve(strict=True)
    roots: list[tuple[str, Path]] = [
        ("source clone", source),
        ("revision B checkout output", checkout),
        ("SEI repository", soza),
    ]
    if reference_source_repo is not None:
        roots.append(
            (
                "revision A reference checkout",
                reference_source_repo.expanduser().resolve(strict=True),
            )
        )
    _reject_overlap(resolved, "Evidence directory", roots)

    if reference_evidence_bundle is not None:
        bundle = reference_evidence_bundle.expanduser().resolve(strict=True)
        if _is_within(bundle, resolved):
            raise ValueError(
                "Evidence directoryでhistorical reference bundleを包含できません: "
                f"output={resolved} bundle={bundle}"
            )

    canonical_paths = [
        resolved / version_exchange.BUNDLE_NAME,
        resolved / version_exchange.REPORT_NAME,
    ]
    for path in canonical_paths:
        reject_symlink_path_or_ancestors(path, "TEI local version exchange Evidence output")
    existing = [path for path in canonical_paths if path.exists()]
    if existing and not overwrite:
        raise ValueError(
            "既存Evidenceを無言で上書きしません。--overwriteを明示してください: "
            + ", ".join(str(path) for path in existing)
        )
    if overwrite:
        for path in existing:
            if not path.is_file() and not path.is_symlink():
                raise ValueError(f"Evidence出力先がfileではありません: {path}")

    return {
        "outputDirectory": str(resolved),
        "overwrite": overwrite,
        "existingCanonicalOutputs": [str(path) for path in existing],
        "staticPathSafetyVerified": True,
        "sourceCloneSeparated": True,
        "revisionBCheckoutSeparated": True,
        "filesystemMutationPerformed": False,
    }


def run_preflight(
    source_repo: Path,
    checkout_output: Path,
    reference_source_repo: Path | None,
    soza_repo_root: Path,
    output_dir: Path,
    *,
    reference_evidence_bundle: Path | None = None,
    tei_go_executable: Path,
    soza_go_executable: Path,
    expected_soza_head: str | None = None,
    overwrite: bool = False,
) -> dict[str, object]:
    checks = [
        common._capture("execution_platform", common._check_platform),
        common._capture(
            "revision_b_source_clone",
            lambda: _check_source_clone(source_repo),
        ),
        common._capture(
            "revision_a_fixed_reference_identity",
            lambda: common._check_reference_input(
                reference_source_repo,
                reference_evidence_bundle,
            ),
        ),
        common._capture(
            "soza_source_identity",
            lambda: common._check_soza_source(soza_repo_root, expected_soza_head),
        ),
        common._capture(
            "tei_go_toolchain",
            lambda: common._check_tei_go(tei_go_executable),
        ),
        common._capture(
            "soza_go_toolchain",
            lambda: common._check_soza_go(soza_go_executable, soza_repo_root),
        ),
        common._capture(
            "revision_b_checkout_output_path",
            lambda: _check_checkout_output_path(
                checkout_output,
                source_repo=source_repo,
                soza_repo_root=soza_repo_root,
                reference_source_repo=reference_source_repo,
                reference_evidence_bundle=reference_evidence_bundle,
                evidence_output_dir=output_dir,
            ),
        ),
        common._capture(
            "output_path",
            lambda: _check_evidence_output_path(
                output_dir,
                source_repo=source_repo,
                checkout_output=checkout_output,
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
        "credentialRequired": False,
        "revisionBCheckoutCreated": False,
        "evidenceOutputCreated": False,
        "qualityJudgement": "not_evaluated",
        "stopLine": STOP_LINE,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "local source cloneからexact revision B checkoutをprepareしてcanonical E2/E3へ進む前に、"
            "source object DB、fixed A input、SEI source、E2/E3 Go、checkout/evidence pathを"
            "副作用なしで一括検査します。credentialやnetwork accessは要求しません。"
        ),
        allow_abbrev=False,
    )
    parser.add_argument("--source-repo", required=True, type=Path)
    parser.add_argument("--checkout-output", required=True, type=Path)
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
        args.source_repo,
        args.checkout_output,
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
        print(f"TEI version exchange local preflight: {result['result']}")
        for check in result["checks"]:
            print(f"- {check['name']}: {check['status']}")
            if check["status"] != "ready":
                print(f"  {check['error']['message']}")
        print(result["stopLine"])
    return 0 if result["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
