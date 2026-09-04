#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path

import check_runtime_version_exchange_preflight as preflight
from prepare_runtime_version_exchange_archives import load_manifest
from prepare_runtime_version_exchange_model_store import _validate_model_acquisition
from verify_kj_atlas_runtime_source import PINNED_IDENTITY
from verify_runtime_version_exchange_model_store import _load_fixed_model_identity


INTEGRATION_DIR = Path(__file__).resolve().parent
ARTIFACT_MANIFEST = INTEGRATION_DIR / "runtime_version_exchange_artifacts.json"
OFFICIAL_RELEASE_SNAPSHOT = (
    INTEGRATION_DIR / "runtime_version_exchange_official_release_snapshot.json"
)
RELEASE_SNAPSHOT_SCHEMA = "soza.runtime-version-exchange-official-release-snapshot/v1"


@dataclass(frozen=True)
class Check:
    id: str
    status: str
    detail: str


def _equal(checks: list[Check], check_id: str, actual: object, expected: object) -> None:
    if actual == expected:
        checks.append(Check(check_id, "ok", f"一致します: {actual!r}"))
    else:
        checks.append(
            Check(
                check_id,
                "blocked",
                f"固定値が一致しません: actual={actual!r} expected={expected!r}",
            )
        )


def _load_release_snapshot(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema") != RELEASE_SNAPSHOT_SCHEMA:
        raise ValueError(f"official release snapshot schemaが未対応です: {payload.get('schema')!r}")
    if payload.get("sourceRepository") != "ollama/ollama":
        raise ValueError("official release snapshotのsourceRepositoryがollama/ollamaではありません")
    if payload.get("sourceType") != "github-release-api":
        raise ValueError("official release snapshotのsourceTypeがgithub-release-apiではありません")
    archives = payload.get("archives")
    if not isinstance(archives, dict) or set(archives) != {"a", "b"}:
        raise ValueError("official release snapshotにはarchives.a / archives.bが必要です")
    return payload


def _release_snapshot_checks(
    checks: list[Check],
    archives: dict[str, object],
    snapshot_path: Path,
) -> None:
    try:
        snapshot = _load_release_snapshot(snapshot_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        checks.append(Check("release-snapshot.schema", "blocked", str(exc)))
        return

    checks.append(
        Check(
            "release-snapshot.schema",
            "ok",
            "Ollama公式GitHub Release APIの観測snapshotを読み込みました",
        )
    )
    snapshot_archives = snapshot["archives"]
    assert isinstance(snapshot_archives, dict)

    for label in ("a", "b"):
        archive = archives[label]
        observed = snapshot_archives[label]
        if not isinstance(archive, dict) or not isinstance(observed, dict):
            checks.append(
                Check(
                    f"release-snapshot.{label}",
                    "blocked",
                    "manifestまたはofficial release snapshotのarchiveがobjectではありません",
                )
            )
            continue

        _equal(checks, f"release-snapshot.{label}.version", archive.get("version"), observed.get("version"))
        _equal(checks, f"release-snapshot.{label}.assetName", archive.get("assetName"), observed.get("assetName"))
        _equal(checks, f"release-snapshot.{label}.sizeBytes", archive.get("sizeBytes"), observed.get("sizeBytes"))
        observed_digest = observed.get("digest")
        expected_digest = (
            f"sha256:{archive.get('sha256')}"
            if isinstance(archive.get("sha256"), str)
            else None
        )
        _equal(checks, f"release-snapshot.{label}.digest", expected_digest, observed_digest)
        _equal(
            checks,
            f"release-snapshot.{label}.browserDownloadUrl",
            archive.get("downloadUrl"),
            observed.get("browserDownloadUrl"),
        )
        _equal(
            checks,
            f"release-snapshot.{label}.releaseTag",
            f"v{archive.get('version')}",
            observed.get("releaseTag"),
        )
        _equal(checks, f"release-snapshot.{label}.assetState", observed.get("assetState"), "uploaded")
        _equal(
            checks,
            f"release-snapshot.{label}.contentType",
            observed.get("contentType"),
            "application/zstd",
        )


def collect_checks(
    manifest_path: Path = ARTIFACT_MANIFEST,
    release_snapshot_path: Path = OFFICIAL_RELEASE_SNAPSHOT,
) -> list[Check]:
    checks: list[Check] = []
    try:
        payload = load_manifest(manifest_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return [Check("manifest.runtime-archive-schema", "blocked", str(exc))]

    checks.append(
        Check(
            "manifest.runtime-archive-schema",
            "ok",
            "runtime archive取得条件をmanifest loaderで検証しました",
        )
    )

    source = payload.get("methodSource")
    if not isinstance(source, dict):
        checks.append(Check("manifest.method-source", "blocked", "methodSourceがobjectではありません"))
    else:
        source_pairs = (
            ("repository", PINNED_IDENTITY.repository),
            ("commit", PINNED_IDENTITY.source_commit),
            ("backendTree", PINNED_IDENTITY.backend_tree),
            ("runtimeSurfaceTree", PINNED_IDENTITY.runtime_surface_tree),
            ("pyprojectBlob", PINNED_IDENTITY.pyproject_blob),
            ("alembicIniBlob", PINNED_IDENTITY.alembic_ini_blob),
            ("alembicTree", PINNED_IDENTITY.alembic_tree),
            ("srcTree", PINNED_IDENTITY.src_tree),
        )
        for key, expected in source_pairs:
            _equal(checks, f"method-source.{key}", source.get(key), expected)

    archives = payload["runtimeArchives"]
    assert isinstance(archives, dict)
    runtime_pairs = (
        ("a", "version", preflight.RUNTIME_VERSION_A),
        ("a", "sizeBytes", preflight.RUNTIME_SIZE_A),
        ("a", "sha256", preflight.RUNTIME_SHA256_A),
        ("b", "version", preflight.RUNTIME_VERSION_B),
        ("b", "sizeBytes", preflight.RUNTIME_SIZE_B),
        ("b", "sha256", preflight.RUNTIME_SHA256_B),
    )
    for label, key, expected in runtime_pairs:
        archive = archives[label]
        assert isinstance(archive, dict)
        _equal(checks, f"runtime-{label}.{key}", archive.get(key), expected)

    _release_snapshot_checks(checks, archives, release_snapshot_path)

    model = payload.get("model")
    if not isinstance(model, dict):
        checks.append(Check("manifest.model", "blocked", "modelがobjectではありません"))
    else:
        try:
            acquisition = _validate_model_acquisition(model)
        except (OSError, ValueError) as exc:
            checks.append(Check("model.acquisition", "blocked", str(exc)))
        else:
            checks.append(
                Check(
                    "model.acquisition",
                    "ok",
                    "model取得条件をmodel preparation境界で検証しました",
                )
            )
            _equal(checks, "model.name", acquisition["name"], preflight.MODEL_NAME)
            _equal(checks, "model.sha256", acquisition["sha256"], preflight.MODEL_SHA256)

            fixed_model = _load_fixed_model_identity()
            for key in ("name", "sha256", "storeManifestPath", "digestBasis"):
                _equal(
                    checks,
                    f"model-verifier.{key}",
                    acquisition[key],
                    fixed_model[key],
                )

    return checks


def report(
    manifest_path: Path = ARTIFACT_MANIFEST,
    release_snapshot_path: Path = OFFICIAL_RELEASE_SNAPSHOT,
) -> dict[str, object]:
    checks = collect_checks(manifest_path, release_snapshot_path)
    blockers = [check.id for check in checks if check.status == "blocked"]
    return {
        "schema": "soza.runtime-version-exchange-manifest-consistency/v1",
        "result": "blocked" if blockers else "consistent",
        "manifest": str(manifest_path.expanduser().resolve(strict=False)),
        "officialReleaseSnapshot": str(
            release_snapshot_path.expanduser().resolve(strict=False)
        ),
        "blockers": blockers,
        "checks": [asdict(check) for check in checks],
        "stopLine": (
            "manifest consistency + official release metadata snapshot agreement "
            "!= artifact bytes verified != actual runtime A/B inference PASS "
            "!= ISSUE-000070 Resolved"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "ISSUE-000070の固定artifact manifestとsource / preflight / model consumer、"
            "Ollama公式GitHub Release APIの観測snapshotが相互に一致するかを、"
            "副作用なく確認します。"
        )
    )
    parser.add_argument("--manifest", type=Path, default=ARTIFACT_MANIFEST)
    parser.add_argument(
        "--official-release-snapshot", type=Path, default=OFFICIAL_RELEASE_SNAPSHOT
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = report(args.manifest, args.official_release_snapshot)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    else:
        print(f"runtime version exchange manifest consistency: {result['result']}")
        for check in result["checks"]:
            print(f"- [{check['status']}] {check['id']}: {check['detail']}")
        print(result["stopLine"])
    return 0 if result["result"] == "consistent" else 1


if __name__ == "__main__":
    raise SystemExit(main())
