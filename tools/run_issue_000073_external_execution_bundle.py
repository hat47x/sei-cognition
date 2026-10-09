#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import Any

HANDOFF_SCHEMA = "issue-000073-external-execution-bundle/v1"
RUN_SCHEMA = "issue-000073-external-execution-run/v1"
ISSUE = "ISSUE-000073"
HEX40_RE = re.compile(r"^[0-9a-f]{40}$")
HEX64_RE = re.compile(r"^[0-9a-f]{64}$")
STOP_LINE = (
    "External handoff execution PASS != H1/H2 human review "
    "!= Decision Continuity Product Value established."
)


def run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def read_sums(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) != 2:
            raise ValueError("SHA256SUMS line must contain exactly digest and basename")
        digest, name = parts
        if not HEX64_RE.fullmatch(digest):
            raise ValueError(f"invalid SHA-256 digest in SHA256SUMS: {digest!r}")
        if name in {".", ".."} or "/" in name or "\\" in name:
            raise ValueError(f"SHA256SUMS entry must be a basename: {name!r}")
        if name in result:
            raise ValueError(f"duplicate SHA256SUMS entry: {name}")
        result[name] = digest
    return result


def fail(message: str, code: int = 2) -> int:
    print(message, file=sys.stderr)
    return code


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify, clone, and execute an ISSUE-000073 exact-source external handoff bundle."
    )
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--sha256sums", type=Path, required=True)
    parser.add_argument("--work-dir", type=Path, required=True)
    parser.add_argument("--result-dir", type=Path, required=True)
    parser.add_argument("--replace-results", action="store_true")
    args = parser.parse_args()

    if shutil.which("git") is None:
        return fail("git executable not found")
    if shutil.which("bash") is None:
        return fail("bash executable not found")

    bundle = args.bundle.expanduser().resolve()
    manifest_path = args.manifest.expanduser().resolve()
    sums_path = args.sha256sums.expanduser().resolve()
    work_dir = args.work_dir.expanduser().resolve()
    result_dir = args.result_dir.expanduser().resolve()

    for label, path in (("bundle", bundle), ("manifest", manifest_path), ("SHA256SUMS", sums_path)):
        if not path.is_file():
            return fail(f"{label} file not found: {path}")

    if work_dir.exists():
        return fail(f"work directory must not already exist: {work_dir}")
    if is_within(result_dir, work_dir) or is_within(work_dir, result_dir):
        return fail("work directory and result directory must not contain one another")

    try:
        manifest = read_json(manifest_path)
        sums = read_sums(sums_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return fail(f"handoff metadata is invalid: {exc}")

    if manifest.get("schema") != HANDOFF_SCHEMA or manifest.get("issue") != ISSUE:
        return fail("handoff manifest schema or issue is unsupported")

    source = manifest.get("source")
    bundle_meta = manifest.get("bundle")
    if not isinstance(source, dict) or not isinstance(bundle_meta, dict):
        return fail("handoff manifest source/bundle metadata is missing")

    head = source.get("head")
    expected_head = source.get("expected_head")
    if (
        not isinstance(head, str)
        or not HEX40_RE.fullmatch(head)
        or expected_head != head
        or source.get("head_matches_expected") is not True
        or source.get("clean") is not True
    ):
        return fail("handoff source identity is not an exact clean expected HEAD")

    if bundle_meta.get("file") != bundle.name:
        return fail("handoff manifest bundle filename does not match supplied bundle")
    if not isinstance(bundle_meta.get("sha256"), str) or not HEX64_RE.fullmatch(bundle_meta["sha256"]):
        return fail("handoff manifest bundle SHA-256 is invalid")
    if bundle_meta.get("size_bytes") != bundle.stat().st_size:
        return fail("handoff bundle size does not match manifest")

    expected_sum_names = {bundle.name, manifest_path.name}
    if set(sums) != expected_sum_names:
        return fail("SHA256SUMS must contain exactly the supplied bundle and manifest basenames")

    observed_bundle_sha = sha256_file(bundle)
    observed_manifest_sha = sha256_file(manifest_path)
    if sums[bundle.name] != observed_bundle_sha or bundle_meta["sha256"] != observed_bundle_sha:
        return fail("handoff bundle SHA-256 mismatch")
    if sums[manifest_path.name] != observed_manifest_sha:
        return fail("handoff manifest SHA-256 mismatch")

    heads = run(["git", "bundle", "list-heads", str(bundle)], bundle.parent)
    if heads.returncode != 0:
        return fail(heads.stderr.strip() or "git bundle list-heads failed")
    if f"{head} HEAD" not in heads.stdout.splitlines():
        return fail("git bundle does not advertise manifest source HEAD as HEAD")

    result_dir.mkdir(parents=True, exist_ok=True)
    evidence = result_dir / "e1-e8.json"
    verification = result_dir / "e1-e8-verification.json"
    stdout_log = result_dir / "bootstrap.stdout.log"
    stderr_log = result_dir / "bootstrap.stderr.log"
    run_record = result_dir / "external-run.json"
    outputs = (evidence, verification, stdout_log, stderr_log, run_record)
    existing = [p for p in outputs if p.exists()]
    if existing and not args.replace_results:
        return fail(
            "result output already exists; use --replace-results only for an intentional rerun: "
            + ", ".join(str(p) for p in existing)
        )
    if args.replace_results:
        for path in outputs:
            path.unlink(missing_ok=True)

    clone = run(["git", "clone", "--quiet", str(bundle), str(work_dir)], bundle.parent)
    if clone.returncode != 0:
        return fail(clone.stderr.strip() or "git clone from handoff bundle failed", 1)

    cloned_head = run(["git", "rev-parse", "HEAD"], work_dir)
    cloned_status = run(["git", "status", "--porcelain=v1", "--untracked-files=all"], work_dir)
    if cloned_head.returncode != 0 or cloned_head.stdout.strip() != head:
        return fail("cloned repository HEAD does not match handoff source HEAD", 1)
    if cloned_status.returncode != 0 or cloned_status.stdout != "":
        return fail("cloned repository is not clean before execution", 1)
    verify = run(["git", "bundle", "verify", str(bundle)], work_dir)
    if verify.returncode != 0:
        return fail(verify.stderr.strip() or "git bundle verify failed after clone", 1)

    bootstrap = work_dir / "tools" / "bootstrap_issue_000073_resume_first_evidence.sh"
    if not bootstrap.is_file():
        return fail(f"bootstrap entry point not found in cloned source: {bootstrap}", 1)

    command = [
        "bash",
        str(bootstrap),
        "--expected-head",
        head,
        "--evidence",
        str(evidence),
        "--verification",
        str(verification),
    ]
    proc = run(command, work_dir)
    stdout_log.write_text(proc.stdout, encoding="utf-8")
    stderr_log.write_text(proc.stderr, encoding="utf-8")

    status = "fail"
    detail = "bootstrap/capture did not establish verified E1-E8 PASS"
    evidence_status = None
    verification_passed = None
    tested_head = None

    if evidence.is_file():
        try:
            e = read_json(evidence)
            evidence_status = e.get("status")
            repo_meta = e.get("repository")
            if isinstance(repo_meta, dict):
                tested_head = repo_meta.get("head")
        except (OSError, ValueError, json.JSONDecodeError):
            pass
    if verification.is_file():
        try:
            v = read_json(verification)
            verification_passed = v.get("passed")
            if tested_head is None:
                tested_head = v.get("tested_head")
        except (OSError, ValueError, json.JSONDecodeError):
            pass

    if (
        proc.returncode == 0
        and evidence_status == "pass"
        and verification_passed is True
        and tested_head == head
    ):
        status = "pass"
        detail = "external exact-source clone completed and existing capture/verifier established E1-E8 PASS"
    elif proc.returncode == 2 and evidence_status == "blocked":
        status = "blocked"
        detail = "external exact-source clone completed but bootstrap/capture reported a blocked execution precondition"

    record = {
        "schema": RUN_SCHEMA,
        "issue": ISSUE,
        "status": status,
        "detail": detail,
        "source_head": head,
        "bundle": {
            "file": bundle.name,
            "sha256": observed_bundle_sha,
            "manifest_file": manifest_path.name,
            "manifest_sha256": observed_manifest_sha,
        },
        "execution": {
            "work_dir": str(work_dir),
            "result_dir": str(result_dir),
            "command": command,
            "exit_code": proc.returncode,
            "stdout_sha256": sha256_file(stdout_log),
            "stderr_sha256": sha256_file(stderr_log),
            "evidence_status": evidence_status,
            "verification_passed": verification_passed,
            "tested_head": tested_head,
        },
        "stop_line": STOP_LINE,
    }
    run_record.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record, ensure_ascii=False, indent=2))
    return 0 if status == "pass" else 2 if status == "blocked" else 1


if __name__ == "__main__":
    raise SystemExit(main())
