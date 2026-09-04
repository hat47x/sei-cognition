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


def collect_checks(manifest_path: Path = ARTIFACT_MANIFEST) -> list[Check]:
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


def report(manifest_path: Path = ARTIFACT_MANIFEST) -> dict[str, object]:
    checks = collect_checks(manifest_path)
    blockers = [check.id for check in checks if check.status == "blocked"]
    return {
        "schema": "soza.runtime-version-exchange-manifest-consistency/v1",
        "result": "blocked" if blockers else "consistent",
        "manifest": str(manifest_path.expanduser().resolve(strict=False)),
        "blockers": blockers,
        "checks": [asdict(check) for check in checks],
        "stopLine": (
            "manifest consistency != artifact bytes verified "
            "!= actual runtime A/B inference PASS != ISSUE-000070 Resolved"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "ISSUE-000070の固定artifact manifestとsource / preflight / model consumerの"
            "固定identityが相互に一致するかを、副作用なく確認します。"
        )
    )
    parser.add_argument("--manifest", type=Path, default=ARTIFACT_MANIFEST)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = report(args.manifest)
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
