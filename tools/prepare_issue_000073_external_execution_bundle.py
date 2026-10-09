#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
from typing import Any

SCHEMA = "issue-000073-external-execution-bundle/v1"
ISSUE = "ISSUE-000073"
STOP_LINE = (
    "Prepared Git bundle != external clone executed != E1-E8 actual PASS "
    "!= H1/H2 human review != Decision Continuity Product Value established."
)


def run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def git_text(repo: Path, *args: str) -> str | None:
    proc = run(["git", *args], repo)
    return proc.stdout.strip() if proc.returncode == 0 else None


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Prepare an exact-source Git bundle for ISSUE-000073 external E1-E8 execution."
    )
    parser.add_argument(
        "--expected-head",
        required=True,
        help="Canonical commit SHA obtained independently of this checkout.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directory outside the repository where bundle artifacts will be written.",
    )
    parser.add_argument("--prefix", help="Output filename prefix. Defaults to issue-000073-<short-sha>.")
    parser.add_argument("--replace", action="store_true", help="Replace an existing bundle pair intentionally.")
    parser.add_argument("--repo", type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()

    repo = (args.repo or Path(__file__).resolve().parents[1]).resolve()
    output_dir = args.output_dir.expanduser().resolve()

    if shutil.which("git") is None:
        print("git executable not found", file=sys.stderr)
        return 2

    head = git_text(repo, "rev-parse", "HEAD")
    tree = git_text(repo, "rev-parse", "HEAD^{tree}")
    status = git_text(repo, "status", "--porcelain=v1", "--untracked-files=all")
    git_version = git_text(repo, "--version")

    if head is None or tree is None or status is None:
        print("repository must be a readable Git checkout", file=sys.stderr)
        return 2
    if head != args.expected_head:
        print(
            f"checkout HEAD does not match expected canonical HEAD: actual={head} expected={args.expected_head}",
            file=sys.stderr,
        )
        return 2
    if status:
        print("working tree is not clean; refusing exact-source bundle preparation", file=sys.stderr)
        for line in status.splitlines()[:20]:
            print(line, file=sys.stderr)
        return 2
    if is_within(output_dir, repo):
        print("output directory must be outside the source repository", file=sys.stderr)
        return 2

    prefix = args.prefix or f"issue-000073-{head[:12]}"
    if not prefix or prefix in {".", ".."} or "/" in prefix or "\\" in prefix:
        print("prefix must be a single safe filename component", file=sys.stderr)
        return 2

    output_dir.mkdir(parents=True, exist_ok=True)
    final_bundle = output_dir / f"{prefix}.gitbundle"
    final_manifest = output_dir / f"{prefix}.manifest.json"
    final_sums = output_dir / f"{prefix}.SHA256SUMS"
    finals = (final_bundle, final_manifest, final_sums)
    existing = [p for p in finals if p.exists()]
    if existing and not args.replace:
        print(
            "output already exists; use --replace only for an intentional rerun: "
            + ", ".join(str(p) for p in existing),
            file=sys.stderr,
        )
        return 2

    with tempfile.TemporaryDirectory(prefix="issue-000073-bundle-", dir=output_dir) as temp_name:
        temp_dir = Path(temp_name)
        temp_bundle = temp_dir / final_bundle.name
        temp_manifest = temp_dir / final_manifest.name
        temp_sums = temp_dir / final_sums.name

        create_proc = run(["git", "bundle", "create", str(temp_bundle), "HEAD"], repo)
        if create_proc.returncode != 0:
            print(create_proc.stderr.strip() or "git bundle create failed", file=sys.stderr)
            return 1

        verify_proc = run(["git", "bundle", "verify", str(temp_bundle)], repo)
        if verify_proc.returncode != 0:
            print(verify_proc.stderr.strip() or "git bundle verify failed", file=sys.stderr)
            return 1

        heads_proc = run(["git", "bundle", "list-heads", str(temp_bundle)], repo)
        if heads_proc.returncode != 0:
            print(heads_proc.stderr.strip() or "git bundle list-heads failed", file=sys.stderr)
            return 1
        heads = []
        head_bound = False
        for line in heads_proc.stdout.splitlines():
            parts = line.split(maxsplit=1)
            if len(parts) != 2:
                continue
            sha, ref = parts
            heads.append({"sha": sha, "ref": ref})
            if sha == head and ref == "HEAD":
                head_bound = True
        if not head_bound:
            print("bundle does not advertise the exact tested HEAD as HEAD", file=sys.stderr)
            return 1

        bundle_sha256 = sha256_file(temp_bundle)
        bundle_size = temp_bundle.stat().st_size
        verification_text = (verify_proc.stdout + verify_proc.stderr).strip()
        verification_sha256 = hashlib.sha256(verification_text.encode("utf-8")).hexdigest()

        manifest: dict[str, Any] = {
            "schema": SCHEMA,
            "issue": ISSUE,
            "created_at": now_utc(),
            "source": {
                "head": head,
                "expected_head": args.expected_head,
                "head_matches_expected": True,
                "tree": tree,
                "clean": True,
            },
            "bundle": {
                "file": final_bundle.name,
                "sha256": bundle_sha256,
                "size_bytes": bundle_size,
                "heads": heads,
                "verify_output_sha256": verification_sha256,
            },
            "preparation_environment": {
                "git_version": git_version,
                "python_version": platform.python_version(),
                "platform": platform.platform(),
            },
            "external_execution": {
                "clone": ["git", "clone", final_bundle.name, "sei-cognition-e73"],
                "verify_head": ["git", "-C", "sei-cognition-e73", "rev-parse", "HEAD"],
                "bootstrap": [
                    "bash",
                    "tools/bootstrap_issue_000073_resume_first_evidence.sh",
                    "--expected-head",
                    head,
                ],
                "preprovisioned_go_example": (
                    "GO_BINARY_PATH=/path/to/go1.25.x bash "
                    "tools/bootstrap_issue_000073_resume_first_evidence.sh "
                    f"--expected-head {head}"
                ),
                "preprovisioned_archive_example": (
                    "GO_TOOLCHAIN_ARCHIVE_PATH=/path/to/go1.25.14.linux-amd64.tar.gz bash "
                    "tools/bootstrap_issue_000073_resume_first_evidence.sh "
                    f"--expected-head {head}"
                ),
                "return_files": [
                    "evaluation/personal-inquiry-decision/evidence/issue-000073/e1-e8.json",
                    "evaluation/personal-inquiry-decision/evidence/issue-000073/e1-e8-verification.json",
                ],
            },
            "scope": "Exact-source transport and handoff only. No E1-E8 test is executed by this preparation step.",
            "stop_line": STOP_LINE,
        }
        write_json(temp_manifest, manifest)
        manifest_sha256 = sha256_file(temp_manifest)
        temp_sums.write_text(
            f"{bundle_sha256}  {final_bundle.name}\n{manifest_sha256}  {final_manifest.name}\n",
            encoding="utf-8",
        )

        status_after = git_text(repo, "status", "--porcelain=v1", "--untracked-files=all")
        head_after = git_text(repo, "rev-parse", "HEAD")
        if status_after != "" or head_after != head:
            print("source repository changed while preparing the external bundle", file=sys.stderr)
            return 1

        for temp, final in zip((temp_bundle, temp_manifest, temp_sums), finals):
            if args.replace:
                os.replace(temp, final)
            else:
                os.link(temp, final)

    if sha256_file(final_bundle) != bundle_sha256:
        print("published bundle digest differs from prepared bundle", file=sys.stderr)
        return 1
    final_verify = run(["git", "bundle", "verify", str(final_bundle)], repo)
    if final_verify.returncode != 0:
        print(final_verify.stderr.strip() or "published git bundle verification failed", file=sys.stderr)
        return 1

    print(
        json.dumps(
            {
                "schema": SCHEMA,
                "status": "pass",
                "head": head,
                "bundle": str(final_bundle),
                "manifest": str(final_manifest),
                "sha256sums": str(final_sums),
                "bundle_sha256": bundle_sha256,
                "stop_line": STOP_LINE,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
