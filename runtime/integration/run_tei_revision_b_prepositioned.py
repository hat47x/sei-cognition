#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import tarfile
import tempfile
from pathlib import Path

import verify_tei_evidence_bundle as bundle_verifier
import verify_tei_execution_source_identity as source_identity

FIXED_RUN = "reference/order_rollout.durable-run.m0.21.start.json"
FIXED_WORKSPACE = "reference/workspace"
FIXED_PLUGIN_LOCK = "reference/workspace/.tei/plugin-lock.json"
FIXED_SOLUTION = "order_rollout"
FIXED_VERSION = "2026.8.27"
EXPECTED_GO_VERSION = "go1.23.2"
STOP_LINE = (
    "prepositioned exact-B bundle produced != SOZA Adapter compatibility verified "
    "!= TEI version exchange PASS != Operational Evidence"
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _controlled_go_env() -> dict[str, str]:
    env = os.environ.copy()
    env["GOWORK"] = "off"
    env["GOENV"] = "off"
    env.pop("GOFLAGS", None)
    env.pop("GOOS", None)
    env.pop("GOARCH", None)
    return env


def _ensure_linux_amd64() -> None:
    system = platform.system().lower()
    machine = platform.machine().lower()
    if system != "linux" or machine not in {"x86_64", "amd64"}:
        raise ValueError(
            "historical Linux/amd64 Evidence条件と異なる実行環境です: "
            f"system={system} machine={machine}"
        )


def _run(
    argv: list[str],
    *,
    cwd: Path,
    env: dict[str, str],
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        argv,
        cwd=cwd,
        env=env,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def _copy_reference_inputs(source_repo: Path, bundle_root: Path) -> None:
    workspace = source_repo / FIXED_WORKSPACE
    run_file = source_repo / FIXED_RUN
    plugin_lock = source_repo / FIXED_PLUGIN_LOCK
    for path in (workspace, run_file, plugin_lock):
        if not path.exists():
            raise ValueError(f"fixed reference inputがありません: {path}")

    reference_root = bundle_root / "reference"
    shutil.copytree(workspace, reference_root / "workspace")
    shutil.copy2(run_file, reference_root / run_file.name)


def produce_bundle(source_repo: Path, output_archive: Path) -> dict[str, object]:
    source_repo = source_repo.expanduser().resolve(strict=True)
    output_archive = output_archive.expanduser().resolve()
    output_archive.parent.mkdir(parents=True, exist_ok=True)

    source_observation = source_identity.verify_repository(
        source_repo,
        expected_head=source_identity.REVISION_B,
    )

    _ensure_linux_amd64()
    env = _controlled_go_env()
    go_version = _run(["go", "version"], cwd=source_repo, env=env).stdout.strip()
    if not go_version.startswith(f"go version {EXPECTED_GO_VERSION} "):
        raise ValueError(
            "historical EvidenceとGo toolchain versionが一致しません: "
            f"expected={EXPECTED_GO_VERSION} actual={go_version}"
        )

    with tempfile.TemporaryDirectory(prefix="soza-tei-b-") as tmp:
        bundle_root = Path(tmp) / "tei-e3b-p2"
        binary = bundle_root / "bin" / "tei"
        binary.parent.mkdir(parents=True)

        _run(
            [
                "go",
                "build",
                "-trimpath",
                "-ldflags=-s -w",
                "-o",
                str(binary),
                "./cmd/tei",
            ],
            cwd=source_repo,
            env=env,
        )
        if not binary.is_file() or not os.access(binary, os.X_OK):
            raise ValueError("build後のbin/teiがexecutable fileではありません")

        provider = _run(
            [
                str(binary),
                "deployment-provider-plan",
                "-workspace",
                str(source_repo / FIXED_WORKSPACE),
                "-run",
                str(source_repo / FIXED_RUN),
                "-solution",
                FIXED_SOLUTION,
                "-version",
                FIXED_VERSION,
                "-plugin-lock",
                str(source_repo / FIXED_PLUGIN_LOCK),
            ],
            cwd=source_repo,
            env=env,
        )
        provider_plan = bundle_root / "provider-plan.json"
        provider_plan.write_text(provider.stdout, encoding="utf-8")

        bundle_verifier._parse_provider_plan(provider.stdout.encode("utf-8"))

        _copy_reference_inputs(source_repo, bundle_root)
        metadata = {
            "schema": bundle_verifier.SCHEMA,
            "repository": bundle_verifier.REPOSITORY,
            "source_commit": source_identity.REVISION_B,
            "entry_point": bundle_verifier.ENTRY_POINT,
            "binary_sha256": _sha256(binary),
            "provider_plan_sha256": _sha256(provider_plan),
            "go_version": go_version,
        }
        (bundle_root / "metadata.json").write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        candidate = Path(tmp) / "tei-e3b-p2-linux-amd64.tar.gz"
        with tarfile.open(candidate, "w:gz") as tar:
            for path in sorted(bundle_root.rglob("*")):
                arcname = path.relative_to(bundle_root).as_posix()
                tar.add(path, arcname=arcname, recursive=False)

        verification = bundle_verifier.verify_bundle(
            candidate,
            expected_source_commit=source_identity.REVISION_B,
        )
        shutil.copy2(candidate, output_archive)

    return {
        "schema": "soza.tei-revision-b-prepositioned-run/v1",
        "result": "bundle_produced",
        "source": source_observation,
        "bundle": verification,
        "outputArchive": str(output_archive),
        "qualityJudgement": "not_evaluated",
        "stopLine": STOP_LINE,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "prepositionedされたexact revision BのTEI checkoutを検証し、"
            "historical E3b-P2と同じbuild / deployment-provider-plan条件でEvidence bundleを生成します。"
        ),
        allow_abbrev=False,
    )
    parser.add_argument("--source-repo", required=True, type=Path)
    parser.add_argument("--output-archive", required=True, type=Path)
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = produce_bundle(args.source_repo, args.output_archive)
    except (OSError, ValueError, subprocess.SubprocessError, tarfile.TarError) as exc:
        print(f"TEI revision B prepositioned run failed: {exc}")
        return 1

    if args.json:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    else:
        observation = result["bundle"]["observation"]
        print("TEI revision B prepositioned run: bundle produced")
        print(f"- source commit: {observation['source_commit']}")
        print(f"- binary SHA-256: {observation['binary_sha256']}")
        print(f"- Provider Plan SHA-256: {observation['provider_plan_sha256']}")
        print(result["stopLine"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
