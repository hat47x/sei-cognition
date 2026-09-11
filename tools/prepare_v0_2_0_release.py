#!/usr/bin/env python3
"""SEI v0.2.0のrelease publication bundleを検査・準備する。

このスクリプトはGitHub Releaseを作成しない。Release Candidate Gateが生成した
candidate reportとLocal Reference Packageを照合し、actual publicationへ渡せる
read-onlyのbundleを作る。releaseの存在そのものやRelease Evidenceは主張しない。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path
from typing import Any

EXPECTED_REQUEST_SCHEMA = "soza.release-request/v1"
EXPECTED_REPORT_SCHEMA = "soza.release-candidate-report/v1"
EXPECTED_VERSION = "0.2.0"
EXPECTED_TAG = "v0.2.0"
EXPECTED_REPOSITORY = "hat47x/soza"
EXPECTED_BRANCH = "develop/v0.2.0"
EXPECTED_SCOPE = "local-reference-product-baseline"
EXPECTED_TARGET = "linux-amd64"
HEX64 = re.compile(r"^[0-9a-f]{64}$")
HEX40 = re.compile(r"^[0-9a-f]{40}$")


def fail(message: str) -> None:
    raise ValueError(message)


def load_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"{label}が見つかりません: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"{label}がJSONとして不正です: {exc}") from exc
    if not isinstance(value, dict):
        fail(f"{label}のrootはobjectである必要があります")
    return value


def require_equal(obj: dict[str, Any], key: str, expected: Any, label: str) -> None:
    actual = obj.get(key)
    if actual != expected:
        fail(f"{label}.{key} = {actual!r}, expected {expected!r}")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_expected_checksum(path: Path) -> str:
    try:
        text = path.read_text(encoding="utf-8").strip()
    except FileNotFoundError as exc:
        raise ValueError(f"checksum fileが見つかりません: {path}") from exc
    if not text:
        fail("checksum fileが空です")
    digest = text.split()[0].lower()
    if not HEX64.fullmatch(digest):
        fail(f"checksum fileのSHA-256が不正です: {digest!r}")
    return digest


def validate_request(request: dict[str, Any]) -> None:
    require_equal(request, "schema", EXPECTED_REQUEST_SCHEMA, "release request")
    require_equal(request, "version", EXPECTED_VERSION, "release request")
    require_equal(request, "tag", EXPECTED_TAG, "release request")
    require_equal(request, "repository", EXPECTED_REPOSITORY, "release request")
    require_equal(request, "target_branch", EXPECTED_BRANCH, "release request")
    require_equal(request, "release_scope", EXPECTED_SCOPE, "release request")
    require_equal(request, "artifact_target", EXPECTED_TARGET, "release request")
    require_equal(request, "publish", True, "release request")
    release_name = request.get("release_name")
    if not isinstance(release_name, str) or not release_name.strip():
        fail("release request.release_nameは空でない文字列である必要があります")


def validate_report(report: dict[str, Any], expected_commit: str) -> None:
    require_equal(report, "schema", EXPECTED_REPORT_SCHEMA, "candidate report")
    require_equal(report, "version", EXPECTED_VERSION, "candidate report")
    require_equal(report, "repository", EXPECTED_REPOSITORY, "candidate report")
    require_equal(report, "release_scope", EXPECTED_SCOPE, "candidate report")
    require_equal(report, "source_commit_sha", expected_commit, "candidate report")
    require_equal(report, "candidate_gate_passed", True, "candidate report")
    require_equal(report, "release_evidence", False, "candidate report")
    require_equal(report, "operational_evidence", False, "candidate report")
    require_equal(report, "adoption_outcome_evidence", False, "candidate report")

    tree_sha = report.get("source_tree_sha")
    if not isinstance(tree_sha, str) or not HEX40.fullmatch(tree_sha):
        fail(f"candidate report.source_tree_shaが40桁SHAではありません: {tree_sha!r}")

    gates = report.get("executed_gates")
    if not isinstance(gates, list) or "release-candidate-policy" not in gates:
        fail("candidate reportにrelease-candidate-policy gateがありません")
    if "local-reference-package" not in gates:
        fail("candidate reportにlocal-reference-package gateがありません")

    non_claims = report.get("explicit_non_claims")
    if not isinstance(non_claims, dict):
        fail("candidate report.explicit_non_claimsがobjectではありません")
    for key in (
        "release_evidence",
        "operational_evidence",
        "adoption_outcome_evidence",
        "e3b_live_external_integration",
        "e4_operational_portability",
    ):
        if non_claims.get(key) is not False:
            fail(f"candidate report.explicit_non_claims.{key}はfalseである必要があります")


def validate_notes(path: Path) -> None:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValueError(f"Release Notesが見つかりません: {path}") from exc
    required_fragments = (
        "Local Reference Product Baseline",
        "このreleaseで主張しないこと",
        "E3b",
        "E4",
        "Operational Evidence",
        "Adoption / Outcome Evidence",
    )
    missing = [fragment for fragment in required_fragments if fragment not in text]
    if missing:
        fail(f"Release Notesに必要な境界記述がありません: {missing}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--request", type=Path, required=True)
    parser.add_argument("--candidate-report", type=Path, required=True)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--checksum", type=Path, required=True)
    parser.add_argument("--notes", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument("--candidate-run-id", required=True)
    args = parser.parse_args()

    try:
        if not HEX40.fullmatch(args.expected_commit):
            fail(f"expected commitが40桁SHAではありません: {args.expected_commit!r}")

        request = load_object(args.request, "release request")
        report = load_object(args.candidate_report, "candidate report")
        validate_request(request)
        validate_report(report, args.expected_commit)
        validate_notes(args.notes)

        if not args.package.is_file():
            fail(f"Local Reference Packageが見つかりません: {args.package}")
        expected_digest = read_expected_checksum(args.checksum)
        actual_digest = sha256_file(args.package)
        if actual_digest != expected_digest:
            fail(
                "Local Reference PackageのSHA-256がchecksumと一致しません: "
                f"actual={actual_digest}, expected={expected_digest}"
            )

        output = args.output_dir
        if output.exists():
            shutil.rmtree(output)
        output.mkdir(parents=True)

        package_name = "soza-local-reference-linux-amd64.tar.gz"
        checksum_name = package_name + ".sha256"
        report_name = "v0.2.0-candidate-report.json"
        metadata_name = "release-metadata.json"

        shutil.copyfile(args.package, output / package_name)
        shutil.copyfile(args.checksum, output / checksum_name)
        shutil.copyfile(args.candidate_report, output / report_name)

        metadata = {
            "schema": "soza.release-publication-bundle/v1",
            "version": EXPECTED_VERSION,
            "tag": EXPECTED_TAG,
            "repository": EXPECTED_REPOSITORY,
            "release_scope": EXPECTED_SCOPE,
            "source_commit_sha": report["source_commit_sha"],
            "source_tree_sha": report["source_tree_sha"],
            "candidate_run_id": str(args.candidate_run_id),
            "candidate_gate_passed": True,
            "artifact": {
                "filename": package_name,
                "target": EXPECTED_TARGET,
                "sha256": actual_digest,
                "checksum_filename": checksum_name,
            },
            "candidate_report_filename": report_name,
            "release_notes_source": args.notes.as_posix(),
            "release_evidence": False,
            "operational_evidence": False,
            "adoption_outcome_evidence": False,
            "note": (
                "This bundle is prepared from a successful Release Candidate Gate. "
                "Publication and Release Evidence are evaluated separately."
            ),
        }
        (output / metadata_name).write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        print(
            "PASS: v0.2.0 release publication bundle prepared; "
            f"commit={args.expected_commit} package_sha256={actual_digest}"
        )
        print("Release Evidence remains NOT VERIFIED until actual tag/release are observed.")
        return 0
    except ValueError as exc:
        print(f"FAIL: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
