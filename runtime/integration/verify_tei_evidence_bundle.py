#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import tarfile
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import Mapping

SCHEMA = "tei.soza-e3b-p2-evidence/v1"
REPOSITORY = "hat47x/tei-platform"
ENTRY_POINT = "cmd/tei deployment-provider-plan"
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
ALLOWED_PROVIDER_PLAN_FIELDS = {"executors", "observations", "evidence", "pluginRuntime"}
REQUIRED_MEMBERS = {"metadata.json", "provider-plan.json", "bin/tei"}
REFERENCE_WORKSPACE = "reference/workspace"
REFERENCE_RUN = "reference/order_rollout.durable-run.m0.21.start.json"
REFERENCE_PLUGIN_LOCK = "reference/workspace/.tei/plugin-lock.json"
REFERENCE_METADATA_FIELDS = (
    "reference_input_source_commit",
    "reference_workspace_tree",
    "reference_run_blob",
    "reference_plugin_lock_blob",
)
REFERENCE_OBSERVATION_FIELDS = (
    "source_commit",
    "workspace_tree",
    "run_blob",
    "plugin_lock_blob",
)


@dataclass(frozen=True)
class BundleObservation:
    source_commit: str
    binary_sha256: str
    provider_plan_sha256: str
    archive_sha256: str
    provider_surface_recognized: bool
    binary_executable: bool


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _member_name(member: tarfile.TarInfo) -> str:
    name = member.name
    while name.startswith("./"):
        name = name[2:]
    path = PurePosixPath(name)
    if not name or path.is_absolute() or ".." in path.parts:
        raise ValueError(f"bundle member pathが不正です: {member.name!r}")
    return path.as_posix()


def _read_member(
    tar: tarfile.TarFile,
    members: dict[str, tarfile.TarInfo],
    name: str,
) -> bytes:
    member = members.get(name)
    if member is None or not member.isfile():
        raise ValueError(f"bundleにrequired fileがありません: {name}")
    handle = tar.extractfile(member)
    if handle is None:
        raise ValueError(f"bundle memberを読み込めません: {name}")
    return handle.read()


def _parse_metadata(raw: bytes) -> dict[str, object]:
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(
            f"metadata.jsonが有効なUTF-8 JSONではありません: {exc}"
        ) from exc
    if not isinstance(value, dict):
        raise ValueError("metadata.jsonはobjectである必要があります")
    if value.get("schema") != SCHEMA:
        raise ValueError(f"metadata schemaが未対応です: {value.get('schema')!r}")
    if value.get("repository") != REPOSITORY:
        raise ValueError(f"metadata repositoryが不正です: {value.get('repository')!r}")
    if value.get("entry_point") != ENTRY_POINT:
        raise ValueError(f"metadata entry_pointが不正です: {value.get('entry_point')!r}")
    source_commit = value.get("source_commit")
    if not isinstance(source_commit, str) or HEX40.fullmatch(source_commit) is None:
        raise ValueError("metadata source_commitは40桁lowercase hexである必要があります")
    for key in ("binary_sha256", "provider_plan_sha256"):
        digest = value.get(key)
        if not isinstance(digest, str) or HEX64.fullmatch(digest) is None:
            raise ValueError(f"metadata {key}は64桁lowercase hexである必要があります")

    present_reference_fields = [
        key for key in REFERENCE_METADATA_FIELDS if key in value
    ]
    if present_reference_fields and len(present_reference_fields) != len(
        REFERENCE_METADATA_FIELDS
    ):
        missing = sorted(set(REFERENCE_METADATA_FIELDS) - set(present_reference_fields))
        raise ValueError(
            "fixed reference identity metadataが部分的です: "
            f"missing={missing}"
        )
    if present_reference_fields:
        for key in REFERENCE_METADATA_FIELDS:
            digest = value.get(key)
            if not isinstance(digest, str) or HEX40.fullmatch(digest) is None:
                raise ValueError(
                    f"metadata {key}は40桁lowercase Git object hexである必要があります"
                )
    return value


def _parse_provider_plan(raw: bytes) -> dict[str, object]:
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(
            f"provider-plan.jsonが有効なUTF-8 JSONではありません: {exc}"
        ) from exc
    if not isinstance(value, dict):
        raise ValueError("provider-plan.jsonはobjectである必要があります")
    unknown = set(value) - ALLOWED_PROVIDER_PLAN_FIELDS
    if unknown:
        raise ValueError(
            f"Provider Planにunknown top-level fieldがあります: {sorted(unknown)}"
        )
    if not any(value.get(key) for key in ALLOWED_PROVIDER_PLAN_FIELDS):
        raise ValueError("Provider Planに認識可能な情報がありません")
    return value


def _git_blob_sha1(raw: bytes) -> str:
    header = f"blob {len(raw)}\0".encode("ascii")
    return hashlib.sha1(header + raw).hexdigest()


def _git_tree_sha1_from_bundle(
    tar: tarfile.TarFile,
    members: dict[str, tarfile.TarInfo],
    root: str,
) -> str:
    root_member = members.get(root)
    if root_member is None or not root_member.isdir():
        raise ValueError(f"bundleにfixed reference workspace directoryがありません: {root}")

    tree: dict[str, object] = {}
    prefix = root + "/"
    for name, member in members.items():
        if not name.startswith(prefix) or not member.isfile():
            continue
        relative = PurePosixPath(name[len(prefix) :])
        if not relative.parts:
            continue
        node = tree
        for part in relative.parts[:-1]:
            existing = node.get(part)
            if existing is None:
                child: dict[str, object] = {}
                node[part] = child
                node = child
            elif isinstance(existing, dict):
                node = existing
            else:
                raise ValueError(
                    "fixed reference workspaceのfile/directory構造が競合しています: "
                    f"{name}"
                )
        leaf = relative.parts[-1]
        if leaf in node:
            raise ValueError(
                f"fixed reference workspaceのentryが競合しています: {name}"
            )
        raw = _read_member(tar, members, name)
        mode = "100755" if member.mode & 0o111 else "100644"
        node[leaf] = (mode, _git_blob_sha1(raw))

    def hash_tree(node: dict[str, object]) -> str:
        entries: list[tuple[bytes, str, str, str]] = []
        for name, value in node.items():
            if isinstance(value, dict):
                digest = hash_tree(value)
                mode = "40000"
                sort_key = name.encode("utf-8") + b"/"
            else:
                mode, digest = value
                sort_key = name.encode("utf-8")
            entries.append((sort_key, mode, name, digest))

        body = bytearray()
        for _, mode, name, digest in sorted(entries, key=lambda entry: entry[0]):
            body.extend(mode.encode("ascii"))
            body.extend(b" ")
            body.extend(name.encode("utf-8"))
            body.extend(b"\0")
            body.extend(bytes.fromhex(digest))
        header = f"tree {len(body)}\0".encode("ascii")
        return hashlib.sha1(header + body).hexdigest()

    return hash_tree(tree)


def _observe_reference_identity(
    tar: tarfile.TarFile,
    members: dict[str, tarfile.TarInfo],
    *,
    source_commit: str,
) -> dict[str, str]:
    return {
        "source_commit": source_commit,
        "workspace_tree": _git_tree_sha1_from_bundle(
            tar, members, REFERENCE_WORKSPACE
        ),
        "run_blob": _git_blob_sha1(_read_member(tar, members, REFERENCE_RUN)),
        "plugin_lock_blob": _git_blob_sha1(
            _read_member(tar, members, REFERENCE_PLUGIN_LOCK)
        ),
    }


def _verify_reference_identity(
    tar: tarfile.TarFile,
    members: dict[str, tarfile.TarInfo],
    metadata: dict[str, object],
) -> dict[str, str] | None:
    if not all(key in metadata for key in REFERENCE_METADATA_FIELDS):
        return None

    observed = _observe_reference_identity(
        tar,
        members,
        source_commit=str(metadata["reference_input_source_commit"]),
    )
    expected = {
        "workspace_tree": str(metadata["reference_workspace_tree"]),
        "run_blob": str(metadata["reference_run_blob"]),
        "plugin_lock_blob": str(metadata["reference_plugin_lock_blob"]),
    }
    for key, expected_value in expected.items():
        actual = observed[key]
        if actual != expected_value:
            raise ValueError(
                "actual fixed reference input Git object identityがmetadataと一致しません: "
                f"field={key} actual={actual} metadata={expected_value}"
            )
    return observed


def _verify_expected_reference_identity(
    tar: tarfile.TarFile,
    members: dict[str, tarfile.TarInfo],
    expected: Mapping[str, str],
    declared: dict[str, str] | None,
) -> dict[str, str]:
    missing = [key for key in REFERENCE_OBSERVATION_FIELDS if key not in expected]
    if missing:
        raise ValueError(
            "expected fixed reference identityが不足しています: "
            f"missing={missing}"
        )
    for key in REFERENCE_OBSERVATION_FIELDS:
        value = expected[key]
        if not isinstance(value, str) or HEX40.fullmatch(value) is None:
            raise ValueError(
                f"expected fixed reference identity {key}は40桁lowercase Git object hexである必要があります"
            )

    observed = _observe_reference_identity(
        tar,
        members,
        source_commit=expected["source_commit"],
    )
    for key in REFERENCE_OBSERVATION_FIELDS:
        if observed[key] != expected[key]:
            raise ValueError(
                "actual fixed reference input Git object identityが期待値と一致しません: "
                f"field={key} actual={observed[key]} expected={expected[key]}"
            )
    if declared is not None:
        for key in REFERENCE_OBSERVATION_FIELDS:
            if declared[key] != expected[key]:
                raise ValueError(
                    "bundle metadataのfixed reference identityが外部期待値と一致しません: "
                    f"field={key} metadata={declared[key]} expected={expected[key]}"
                )
    return observed


def verify_bundle(
    archive: Path,
    *,
    expected_source_commit: str | None = None,
    expected_binary_sha256: str | None = None,
    expected_provider_plan_sha256: str | None = None,
    expected_reference_input: Mapping[str, str] | None = None,
) -> dict[str, object]:
    archive = archive.expanduser().resolve(strict=True)
    if not archive.is_file():
        raise ValueError(f"bundle archiveがfileではありません: {archive}")

    archive_sha256 = sha256_file(archive)
    with tarfile.open(archive, mode="r:gz") as tar:
        members: dict[str, tarfile.TarInfo] = {}
        for member in tar.getmembers():
            name = _member_name(member)
            if member.issym() or member.islnk() or member.isdev():
                raise ValueError(f"bundleにlink/device memberを含められません: {name}")
            if name in members:
                raise ValueError(f"bundle memberが重複しています: {name}")
            members[name] = member

        missing = REQUIRED_MEMBERS - members.keys()
        if missing:
            raise ValueError(f"bundleにrequired memberがありません: {sorted(missing)}")

        metadata = _parse_metadata(_read_member(tar, members, "metadata.json"))
        provider_plan_raw = _read_member(tar, members, "provider-plan.json")
        _parse_provider_plan(provider_plan_raw)
        binary_raw = _read_member(tar, members, "bin/tei")
        binary_member = members["bin/tei"]
        reference_identity = _verify_reference_identity(tar, members, metadata)
        if expected_reference_input is not None:
            reference_identity = _verify_expected_reference_identity(
                tar,
                members,
                expected_reference_input,
                reference_identity,
            )

    binary_sha256 = hashlib.sha256(binary_raw).hexdigest()
    provider_plan_sha256 = hashlib.sha256(provider_plan_raw).hexdigest()
    if binary_sha256 != metadata["binary_sha256"]:
        raise ValueError(
            "actual binary SHA-256がmetadataと一致しません: "
            f"actual={binary_sha256} metadata={metadata['binary_sha256']}"
        )
    if provider_plan_sha256 != metadata["provider_plan_sha256"]:
        raise ValueError(
            "actual Provider Plan SHA-256がmetadataと一致しません: "
            f"actual={provider_plan_sha256} metadata={metadata['provider_plan_sha256']}"
        )

    source_commit = str(metadata["source_commit"])
    expected_pairs = (
        ("source commit", source_commit, expected_source_commit),
        ("binary SHA-256", binary_sha256, expected_binary_sha256),
        (
            "Provider Plan SHA-256",
            provider_plan_sha256,
            expected_provider_plan_sha256,
        ),
    )
    for label, actual, expected in expected_pairs:
        if expected is not None and actual != expected:
            raise ValueError(
                f"{label}が期待値と一致しません: actual={actual} expected={expected}"
            )

    observation = BundleObservation(
        source_commit=source_commit,
        binary_sha256=binary_sha256,
        provider_plan_sha256=provider_plan_sha256,
        archive_sha256=archive_sha256,
        provider_surface_recognized=True,
        binary_executable=bool(binary_member.mode & 0o111),
    )
    if not observation.binary_executable:
        raise ValueError("bin/teiにexecutable bitがありません")

    result: dict[str, object] = {
        "schema": "soza.tei-evidence-bundle-verification/v1",
        "result": "verified",
        "archive": str(archive),
        "observation": asdict(observation),
        "metadata": metadata,
        "qualityJudgement": "not_evaluated",
        "stopLine": (
            "TEI Evidence bundle identity verified != SOZA Adapter compatibility verified "
            "!= TEI version exchange PASS != Operational Evidence"
        ),
    }
    if reference_identity is not None:
        result["referenceInput"] = reference_identity
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "TEI E3b-P2 Evidence bundleのsource / binary / Provider Plan identityと"
            "archive構造を、取得方法やGitHub Actionsから独立して再検証します。"
        ),
        allow_abbrev=False,
    )
    parser.add_argument("archive", type=Path)
    parser.add_argument("--expected-source-commit")
    parser.add_argument("--expected-binary-sha256")
    parser.add_argument("--expected-provider-plan-sha256")
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = verify_bundle(
            args.archive,
            expected_source_commit=args.expected_source_commit,
            expected_binary_sha256=args.expected_binary_sha256,
            expected_provider_plan_sha256=args.expected_provider_plan_sha256,
        )
    except (OSError, ValueError, tarfile.TarError) as exc:
        print(f"TEI Evidence bundle verification failed: {exc}")
        return 1
    if args.json:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    else:
        observation = result["observation"]
        print("TEI Evidence bundle verification: verified")
        print(f"- source commit: {observation['source_commit']}")
        print(f"- binary SHA-256: {observation['binary_sha256']}")
        print(f"- Provider Plan SHA-256: {observation['provider_plan_sha256']}")
        if "referenceInput" in result:
            reference = result["referenceInput"]
            print(f"- reference input source commit: {reference['source_commit']}")
            print(f"- reference workspace tree: {reference['workspace_tree']}")
        print(result["stopLine"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
