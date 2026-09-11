#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import tarfile
import tempfile
from pathlib import Path

import verify_tei_evidence_bundle as bundle_verifier
import verify_tei_execution_source_identity as source_identity
from runtime_path_safety import reject_symlink_path_or_ancestors

FIXED_WORKSPACE = "reference/workspace"
FIXED_RUN = "reference/order_rollout.durable-run.m0.21.start.json"
FIXED_PLUGIN_LOCK = "reference/workspace/.tei/plugin-lock.json"
REVISION_A_BINARY_SHA256 = "31f0298b47f9caaa93cd4b2da538cda72e23e5b518f2d0ddad2cf98c46882154"
REVISION_A_PROVIDER_PLAN_SHA256 = "39eafb26cf189681e0bd2ff46fcaf000cbe2f860cf698765bbadac6dfbd2a950"
EXPECTED_REFERENCE = {
    "source_commit": source_identity.REVISION_A,
    "workspace_tree": source_identity.REVISION_A_REFERENCE_OBJECTS[FIXED_WORKSPACE],
    "run_blob": source_identity.REVISION_A_REFERENCE_OBJECTS[FIXED_RUN],
    "plugin_lock_blob": source_identity.REVISION_A_REFERENCE_OBJECTS[FIXED_PLUGIN_LOCK],
}
STOP_LINE = (
    "revision A fixed reference input verified from historical Evidence bundle "
    "!= revision A source checkout reconstructed != revision B build PASS "
    "!= SEI Adapter compatibility verified != ISSUE-000072 Resolved"
)


def verify_fixed_reference_input_bundle(archive: Path) -> dict[str, object]:
    requested = archive.expanduser()
    reject_symlink_path_or_ancestors(
        requested,
        "TEI historical revision A Evidence bundle",
    )
    resolved = requested.resolve(strict=True)
    if not resolved.is_file():
        raise ValueError(
            f"TEI historical revision A Evidence bundleがfileではありません: {resolved}"
        )
    verification = bundle_verifier.verify_bundle(
        resolved,
        expected_source_commit=source_identity.REVISION_A,
        expected_binary_sha256=REVISION_A_BINARY_SHA256,
        expected_provider_plan_sha256=REVISION_A_PROVIDER_PLAN_SHA256,
        expected_reference_input=EXPECTED_REFERENCE,
    )
    return {
        "schema": "sei.tei-fixed-reference-input-bundle/v1",
        "result": "verified",
        "acquisitionMode": "historical_evidence_bundle",
        "sourceCommit": source_identity.REVISION_A,
        "head": source_identity.REVISION_A,
        "executionSourceObjects": dict(source_identity.REVISION_A_REFERENCE_OBJECTS),
        "archive": str(resolved),
        "archiveSha256": verification["observation"]["archive_sha256"],
        "referenceInput": verification["referenceInput"],
        "historicalBundle": verification["observation"],
        "qualityJudgement": "not_evaluated",
        "stopLine": STOP_LINE,
    }


def _validated_members(tar: tarfile.TarFile) -> dict[str, tarfile.TarInfo]:
    members: dict[str, tarfile.TarInfo] = {}
    for member in tar.getmembers():
        name = bundle_verifier._member_name(member)
        if member.issym() or member.islnk() or member.isdev():
            raise ValueError(f"bundleにlink/device memberを含められません: {name}")
        if name in members:
            raise ValueError(f"bundle memberが重複しています: {name}")
        members[name] = member
    return members


def _materialize_member(
    tar: tarfile.TarFile,
    member: tarfile.TarInfo,
    destination: Path,
) -> None:
    if member.isdir():
        destination.mkdir(parents=True, exist_ok=True)
        return
    if not member.isfile():
        raise ValueError(
            f"fixed reference inputにregular file/directory以外があります: {member.name}"
        )
    handle = tar.extractfile(member)
    if handle is None:
        raise ValueError(f"bundle memberを読み込めません: {member.name}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(handle.read())
    destination.chmod(0o755 if member.mode & 0o111 else 0o644)


def materialize_fixed_reference_input_bundle(
    archive: Path,
    output_root: Path,
) -> dict[str, object]:
    verification = verify_fixed_reference_input_bundle(archive)
    archive = Path(verification["archive"])

    requested = output_root.expanduser()
    reject_symlink_path_or_ancestors(requested, "TEI fixed reference input output")
    resolved = requested.resolve(strict=False)
    if resolved.exists():
        raise ValueError(
            f"fixed reference input出力先は新規pathである必要があります: {resolved}"
        )
    resolved.parent.mkdir(parents=True, exist_ok=True)

    stage = Path(tempfile.mkdtemp(prefix=resolved.name + ".partial-", dir=resolved.parent))
    try:
        with tarfile.open(archive, mode="r:gz") as tar:
            members = _validated_members(tar)
            workspace_member = members.get(FIXED_WORKSPACE)
            if workspace_member is None or not workspace_member.isdir():
                raise ValueError(
                    f"bundleにfixed reference workspace directoryがありません: {FIXED_WORKSPACE}"
                )
            for required in (FIXED_RUN, FIXED_PLUGIN_LOCK):
                member = members.get(required)
                if member is None or not member.isfile():
                    raise ValueError(f"fixed reference input fileがありません: {required}")

            selected = [
                (name, member)
                for name, member in members.items()
                if name == FIXED_WORKSPACE
                or name.startswith(FIXED_WORKSPACE + "/")
                or name == FIXED_RUN
            ]
            for name, member in selected:
                _materialize_member(tar, member, stage / name)

        if not (stage / FIXED_WORKSPACE).is_dir():
            raise ValueError("materialized fixed reference workspaceがdirectoryではありません")
        for required in (FIXED_RUN, FIXED_PLUGIN_LOCK):
            if not (stage / required).is_file():
                raise ValueError(
                    f"materialized fixed reference inputがfileではありません: {required}"
                )
        os.replace(stage, resolved)
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise

    return {
        **verification,
        "materializedRoot": str(resolved),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "historical revision A TEI Evidence bundleに保存されたfixed reference inputを、"
            "既知のGit object identityへ照合し、必要なら新規directoryへmaterializeします。"
        ),
        allow_abbrev=False,
    )
    parser.add_argument("archive", type=Path)
    parser.add_argument("--materialize-dir", type=Path)
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.materialize_dir is None:
            result = verify_fixed_reference_input_bundle(args.archive)
        else:
            result = materialize_fixed_reference_input_bundle(
                args.archive,
                args.materialize_dir,
            )
    except (OSError, ValueError, tarfile.TarError) as exc:
        print(f"TEI fixed reference input verification failed: {exc}")
        return 1

    if args.json:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    else:
        print("TEI fixed reference input: verified")
        print(f"- acquisition: {result['acquisitionMode']}")
        print(f"- source commit: {result['sourceCommit']}")
        print(f"- workspace tree: {result['referenceInput']['workspace_tree']}")
        if "materializedRoot" in result:
            print(f"- materialized root: {result['materializedRoot']}")
        print(result["stopLine"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
