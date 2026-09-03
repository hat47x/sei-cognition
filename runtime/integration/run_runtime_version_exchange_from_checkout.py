#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from export_kj_atlas_runtime_source import export_runtime_bundle


INTEGRATION_DIR = Path(__file__).resolve().parent
HARNESS = INTEGRATION_DIR / "run_runtime_version_exchange.sh"


def _reject_unsafe_forwarded_source_options(arguments: list[str]) -> None:
    forbidden = {"--kj-atlas-dir", "--kj-atlas-backend-bundle"}
    for argument in arguments:
        if argument in forbidden or any(argument.startswith(name + "=") for name in forbidden):
            raise ValueError(
                "source optionはこのentrypoint側で確定します。"
                f"harnessへ直接渡せません: {argument}"
            )


def _prepare_identity_path(
    path: Path | None,
    *,
    checkout_dir: Path,
    bundle_dir: Path,
) -> Path | None:
    if path is None:
        return None

    identity_path = path.expanduser().resolve(strict=False)
    if identity_path.exists():
        raise ValueError(f"source export identity already exists: {identity_path}")
    if identity_path == checkout_dir or checkout_dir in identity_path.parents:
        raise ValueError(
            "source export identity must not be inside the KJ Atlas repository: "
            f"{identity_path}"
        )
    if identity_path == bundle_dir or bundle_dir in identity_path.parents:
        raise ValueError(
            "source export identity must not be inside the verified runtime bundle: "
            f"{identity_path}"
        )
    return identity_path


def run_from_checkout(
    checkout_dir: Path,
    harness_arguments: list[str],
    *,
    source_bundle_dir: Path | None = None,
    source_export_identity: Path | None = None,
) -> int:
    _reject_unsafe_forwarded_source_options(harness_arguments)

    checkout_dir = checkout_dir.expanduser().resolve(strict=True)
    temporary: tempfile.TemporaryDirectory[str] | None = None
    if source_bundle_dir is None:
        temporary = tempfile.TemporaryDirectory(prefix="soza-kj-atlas-runtime-source-")
        bundle_dir = Path(temporary.name) / "backend"
    else:
        bundle_dir = source_bundle_dir.expanduser().resolve(strict=False)

    identity_path = _prepare_identity_path(
        source_export_identity,
        checkout_dir=checkout_dir,
        bundle_dir=bundle_dir,
    )

    try:
        payload = export_runtime_bundle(checkout_dir, bundle_dir)
        rendered = json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
        if identity_path is not None:
            identity_path.parent.mkdir(parents=True, exist_ok=True)
            identity_path.write_text(rendered, encoding="utf-8")
        else:
            print(rendered, end="", file=sys.stderr)

        completed = subprocess.run(
            [
                str(HARNESS),
                "--kj-atlas-backend-bundle",
                str(bundle_dir),
                *harness_arguments,
            ],
            check=False,
        )
        return completed.returncode
    finally:
        if temporary is not None:
            temporary.cleanup()
        elif source_bundle_dir is not None and bundle_dir.exists():
            # 明示したbundle directoryは後続の検証・監査に使うため残す。
            pass


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "KJ Atlas checkoutのworking treeを実行せず、固定commit objectからverified runtime "
            "bundleを生成してISSUE-000070 harnessを起動します。"
        ),
        allow_abbrev=False,
    )
    parser.add_argument("--kj-atlas-dir", required=True, type=Path)
    parser.add_argument(
        "--source-bundle-dir",
        type=Path,
        help="生成したverified runtime bundleを残す新規directory。省略時は一時directoryを使います。",
    )
    parser.add_argument(
        "--source-export-identity",
        type=Path,
        help="checkoutからbundleを生成したProvenanceを保存する新規JSON path。",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args, harness_arguments = parser.parse_known_args()
    if harness_arguments and harness_arguments[0] == "--":
        harness_arguments = harness_arguments[1:]

    try:
        return run_from_checkout(
            args.kj_atlas_dir,
            harness_arguments,
            source_bundle_dir=args.source_bundle_dir,
            source_export_identity=args.source_export_identity,
        )
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        parser.exit(1, f"runtime version exchange checkout entrypoint failed: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
