#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tarfile
from pathlib import Path

import prepare_tei_fixed_reference_input as fixed_reference
import verify_tei_evidence_bundle as bundle_verifier
import verify_tei_execution_source_identity as source_identity

SCHEMA = "soza.tei-version-exchange-e2-bundle-verification/v1"
STOP_LINE = (
    "exact-B + exact-A E2 bundle identity verified "
    "!= E3 SEI Adapter compatibility verified "
    "!= arbitrary TEI version compatibility != ISSUE-000072 Resolved"
)


def verify_version_exchange_e2_bundle(archive: Path) -> dict[str, object]:
    verification = bundle_verifier.verify_bundle(
        archive,
        expected_source_commit=source_identity.REVISION_B,
        expected_reference_input=fixed_reference.EXPECTED_REFERENCE,
    )
    return {
        "schema": SCHEMA,
        "result": "verified",
        "archive": verification["archive"],
        "observation": verification["observation"],
        "referenceInput": verification["referenceInput"],
        "qualityJudgement": "not_evaluated",
        "stopLine": STOP_LINE,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "ISSUE-000072 revision B E2 Evidence bundleを、actual binary / Provider Planの"
            "事前SHAを要求せず、fixed revision B source commitとfixed revision A reference "
            "input identityへacquisition-independentに再検証します。"
        ),
        allow_abbrev=False,
    )
    parser.add_argument("archive", type=Path)
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = verify_version_exchange_e2_bundle(args.archive)
    except (OSError, ValueError, tarfile.TarError) as exc:
        print(f"TEI version-exchange E2 bundle verification failed: {exc}")
        return 1

    if args.json:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    else:
        observation = result["observation"]
        reference = result["referenceInput"]
        print("TEI version-exchange E2 bundle verification: verified")
        print(f"- source commit: {observation['source_commit']}")
        print(f"- binary SHA-256: {observation['binary_sha256']}")
        print(f"- Provider Plan SHA-256: {observation['provider_plan_sha256']}")
        print(f"- archive SHA-256: {observation['archive_sha256']}")
        print(f"- reference source commit: {reference['source_commit']}")
        print(result["stopLine"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
