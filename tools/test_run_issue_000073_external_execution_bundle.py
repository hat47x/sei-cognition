#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

PREPARER = Path(__file__).with_name("prepare_issue_000073_external_execution_bundle.py")
RUNNER = Path(__file__).with_name("run_issue_000073_external_execution_bundle.py")


def run(cmd: list[str], cwd: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def make_repo(root: Path) -> tuple[Path, str]:
    repo = root / "repo"
    (repo / "tools").mkdir(parents=True)
    run(["git", "init", "-q"], repo).check_returncode()
    run(["git", "config", "user.name", "Test User"], repo).check_returncode()
    run(["git", "config", "user.email", "test@example.com"], repo).check_returncode()
    bootstrap = repo / "tools" / "bootstrap_issue_000073_resume_first_evidence.sh"
    bootstrap.write_text(
        """#!/usr/bin/env bash
set -euo pipefail
expected=""
evidence=""
verification=""
while [[ "$#" -gt 0 ]]; do
  case "$1" in
    --expected-head) expected="$2"; shift 2 ;;
    --evidence) evidence="$2"; shift 2 ;;
    --verification) verification="$2"; shift 2 ;;
    *) shift ;;
  esac
done
head="$(git rev-parse HEAD)"
if [[ "${FAKE_BOOTSTRAP_BLOCKED:-0}" == "1" ]]; then
  printf '{"status":"blocked","repository":{"head":"%s","expected_head":"%s"}}\n' "$head" "$expected" > "$evidence"
  exit 2
fi
printf '{"status":"pass","repository":{"head":"%s","expected_head":"%s"}}\n' "$head" "$expected" > "$evidence"
printf '{"passed":true,"tested_head":"%s"}\n' "$head" > "$verification"
""",
        encoding="utf-8",
    )
    (repo / "README.md").write_text("hello\n", encoding="utf-8")
    run(["git", "add", "."], repo).check_returncode()
    run(["git", "commit", "-q", "-m", "initial"], repo).check_returncode()
    head = run(["git", "rev-parse", "HEAD"], repo).stdout.strip()
    return repo, head


def prepare(repo: Path, head: str, out: Path) -> tuple[Path, Path, Path]:
    proc = run(
        [
            sys.executable,
            str(PREPARER),
            "--repo",
            str(repo),
            "--expected-head",
            head,
            "--output-dir",
            str(out),
        ],
        repo,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr)
    summary = json.loads(proc.stdout)
    return Path(summary["bundle"]), Path(summary["manifest"]), Path(summary["sha256sums"])


@unittest.skipUnless(shutil.which("git") and shutil.which("bash"), "git and bash required")
class ExternalBundleRunTests(unittest.TestCase):
    def invoke(
        self,
        root: Path,
        bundle: Path,
        manifest: Path,
        sums: Path,
        *,
        env: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        return run(
            [
                sys.executable,
                str(RUNNER),
                "--bundle",
                str(bundle),
                "--manifest",
                str(manifest),
                "--sha256sums",
                str(sums),
                "--work-dir",
                str(root / "work"),
                "--result-dir",
                str(root / "result"),
            ],
            root,
            env=env,
        )

    def test_runs_exact_bundle_and_collects_verified_results(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            repo, head = make_repo(root)
            bundle, manifest, sums = prepare(repo, head, root / "handoff")
            proc = self.invoke(root, bundle, manifest, sums)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            record = json.loads(proc.stdout)
            self.assertEqual(record["status"], "pass")
            self.assertEqual(record["source_head"], head)
            self.assertEqual(record["execution"]["tested_head"], head)
            self.assertTrue((root / "result" / "e1-e8.json").is_file())
            self.assertTrue((root / "result" / "e1-e8-verification.json").is_file())

    def test_rejects_bundle_digest_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            repo, head = make_repo(root)
            bundle, manifest, sums = prepare(repo, head, root / "handoff")
            raw = bytearray(bundle.read_bytes())
            raw[-1] ^= 1
            bundle.write_bytes(raw)
            proc = self.invoke(root, bundle, manifest, sums)
            self.assertEqual(proc.returncode, 2)
            self.assertIn("SHA-256 mismatch", proc.stderr)

    def test_rejects_semantically_changed_manifest_even_with_updated_sum(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            repo, head = make_repo(root)
            bundle, manifest, sums = prepare(repo, head, root / "handoff")
            data = json.loads(manifest.read_text(encoding="utf-8"))
            data["source"]["expected_head"] = "0" * 40
            manifest.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
            sums.write_text(
                f"{sha256_file(bundle)}  {bundle.name}\n{sha256_file(manifest)}  {manifest.name}\n",
                encoding="utf-8",
            )
            proc = self.invoke(root, bundle, manifest, sums)
            self.assertEqual(proc.returncode, 2)
            self.assertIn("source identity", proc.stderr)

    def test_records_blocked_bootstrap_without_promoting_pass(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            repo, head = make_repo(root)
            bundle, manifest, sums = prepare(repo, head, root / "handoff")
            env = os.environ.copy()
            env["FAKE_BOOTSTRAP_BLOCKED"] = "1"
            proc = self.invoke(root, bundle, manifest, sums, env=env)
            self.assertEqual(proc.returncode, 2)
            record = json.loads(proc.stdout)
            self.assertEqual(record["status"], "blocked")
            self.assertFalse((root / "result" / "e1-e8-verification.json").exists())
            run_record = json.loads((root / "result" / "external-run.json").read_text(encoding="utf-8"))
            self.assertEqual(run_record["status"], "blocked")


if __name__ == "__main__":
    unittest.main()
