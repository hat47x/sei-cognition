#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import verify_runtime_version_exchange_evidence as core


EXPECTED_PREFLIGHT_SCHEMA = "sei.runtime-version-exchange-preflight/v1"
EXPECTED_SOURCE_EXPORT_SCHEMA = "sei.kj-atlas-runtime-source-export/v1"
EXPECTED_SOURCE_EXPORT_ACQUISITION = "git-archive-from-pinned-commit"
SOURCE_PREPARATION_DIRECT = "verified-runtime-bundle"
SOURCE_PREPARATION_CHECKOUT = "checkout-to-verified-runtime-bundle"
ALLOWED_SOURCE_PREPARATIONS = {
    SOURCE_PREPARATION_DIRECT,
    SOURCE_PREPARATION_CHECKOUT,
}
EVIDENCE_DIRECTORY_CREATED_BY_STRICT = "strict-entrypoint"
EVIDENCE_DIRECTORY_CREATED_BY_FAILURE = "verified-runner-after-failure"
ALLOWED_EVIDENCE_DIRECTORY_CREATORS = {
    EVIDENCE_DIRECTORY_CREATED_BY_STRICT,
    EVIDENCE_DIRECTORY_CREATED_BY_FAILURE,
}


@dataclass(frozen=True)
class Check:
    id: str
    status: str
    detail: str


class Verification:
    def __init__(self) -> None:
        self.checks: list[Check] = []

    def require(
        self,
        check_id: str,
        condition: bool,
        ok_detail: str,
        blocked_detail: str,
    ) -> bool:
        if condition:
            self.checks.append(Check(check_id, "ok", ok_detail))
            return True
        self.checks.append(Check(check_id, "blocked", blocked_detail))
        return False

    def blocked(self, check_id: str, detail: str) -> None:
        self.checks.append(Check(check_id, "blocked", detail))

    @property
    def ready(self) -> bool:
        return all(check.status == "ok" for check in self.checks)


def _required_json(root: Path, name: str, verification: Verification) -> dict[str, Any] | None:
    path = root / name
    if path.is_symlink():
        verification.blocked(
            f"provenance.file.{name}",
            f"Provenance fileはsymlinkを許可しません: {path}",
        )
        return None
    if not path.is_file():
        verification.blocked(
            f"provenance.file.{name}",
            f"Provenance fileがありません: {path}",
        )
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        verification.blocked(
            f"provenance.json.{name}",
            f"JSONを解釈できません: {name}: {exc}",
        )
        return None
    if not isinstance(payload, dict):
        verification.blocked(
            f"provenance.json.{name}",
            f"JSON objectが必要です: {name}",
        )
        return None
    verification.require(
        f"provenance.json.{name}",
        True,
        f"JSON objectを確認しました: {name}",
        "",
    )
    return payload


def _optional_json(root: Path, name: str, verification: Verification) -> dict[str, Any] | None:
    path = root / name
    if not path.exists() and not path.is_symlink():
        return None
    return _required_json(root, name, verification)


def _expected_fixed_artifacts(manifest: dict[str, Any]) -> dict[str, Any]:
    runtime_a = manifest["runtimeArchives"]["a"]
    runtime_b = manifest["runtimeArchives"]["b"]
    model = manifest["model"]
    return {
        "runtimeA": {
            "version": runtime_a["version"],
            "sizeBytes": runtime_a["sizeBytes"],
            "sha256": runtime_a["sha256"],
        },
        "runtimeB": {
            "version": runtime_b["version"],
            "sizeBytes": runtime_b["sizeBytes"],
            "sha256": runtime_b["sha256"],
        },
        "totalCompressedRuntimeBytes": runtime_a["sizeBytes"] + runtime_b["sizeBytes"],
        "model": {
            "name": model["name"],
            "sha256": model["sha256"],
        },
    }


def _expected_source_identity() -> dict[str, Any]:
    return {
        "repository": "hat47x/kj-atlas",
        "sourceCommit": core.EXPECTED_SOURCE_COMMIT,
        "pinnedBackendTree": core.EXPECTED_PARENT_BACKEND_TREE,
        "runtimeSurfaceTree": core.EXPECTED_RUNTIME_SURFACE_TREE,
    }


def _verify_preflight(
    payload: dict[str, Any],
    manifest: dict[str, Any],
    verification: Verification,
) -> None:
    verification.require(
        "provenance.preflight.schema",
        payload.get("schema") == EXPECTED_PREFLIGHT_SCHEMA,
        "preflight schemaを確認しました",
        f"preflight schemaが一致しません: {payload.get('schema')!r}",
    )
    verification.require(
        "provenance.preflight.result",
        payload.get("result") == "ready" and payload.get("blockers") == [],
        "保存済みpreflightがready / blockers=[]であることを確認しました",
        "保存済みpreflightがreadyではありません: "
        f"result={payload.get('result')!r} blockers={payload.get('blockers')!r}",
    )
    verification.require(
        "provenance.preflight.fixed-artifacts",
        payload.get("fixedArtifacts") == _expected_fixed_artifacts(manifest),
        "preflightの固定runtime / model artifact条件をcurrent manifestへ一致させました",
        "preflightのfixedArtifactsがcurrent artifact manifestと一致しません",
    )
    verification.require(
        "provenance.preflight.source-identity",
        payload.get("pinnedSourceIdentity") == _expected_source_identity(),
        "preflightの固定KJ Atlas source identityを確認しました",
        "preflightのpinnedSourceIdentityがcurrent固定値と一致しません",
    )


def _verify_runner_evidence_directory_provenance(
    runner: dict[str, Any],
    verification: Verification,
) -> None:
    created_by = runner.get("evidenceDirectoryCreatedBy")
    verification.require(
        "provenance.runner.evidence-directory-created-by",
        isinstance(created_by, str) and created_by in ALLOWED_EVIDENCE_DIRECTORY_CREATORS,
        f"Evidence directory作成主体を確認しました: {created_by}",
        f"Evidence directory作成主体を認識できません: {created_by!r}",
    )

    completed_successfully = runner.get("completed") is True and runner.get("exitCode") == 0
    verification.require(
        "provenance.runner.complete-run-directory-creator",
        not completed_successfully or created_by == EVIDENCE_DIRECTORY_CREATED_BY_STRICT,
        "complete runのEvidence directoryがstrict entrypoint由来であることを確認しました",
        "complete runのEvidence directory作成主体がstrict entrypointではありません: "
        f"{created_by!r}",
    )


def _verify_source_preparation(
    root: Path,
    *,
    runner: dict[str, Any],
    source: dict[str, Any] | None,
    verification: Verification,
) -> None:
    preparation = runner.get("sourcePreparation")
    verification.require(
        "provenance.runner.source-preparation",
        isinstance(preparation, str) and preparation in ALLOWED_SOURCE_PREPARATIONS,
        f"runner source preparationを確認しました: {preparation}",
        f"runner source preparationを認識できません: {preparation!r}",
    )

    export_path = root / "runtime-exchange-source-export.json"
    if preparation == SOURCE_PREPARATION_CHECKOUT:
        export_payload = _required_json(
            root,
            "runtime-exchange-source-export.json",
            verification,
        )
        if export_payload is None:
            return
        verification.require(
            "provenance.source-export.schema",
            export_payload.get("schema") == EXPECTED_SOURCE_EXPORT_SCHEMA,
            "checkout source export schemaを確認しました",
            f"checkout source export schemaが一致しません: {export_payload.get('schema')!r}",
        )
        verification.require(
            "provenance.source-export.acquisition",
            export_payload.get("sourceAcquisition") == EXPECTED_SOURCE_EXPORT_ACQUISITION,
            "固定commit objectからgit archiveでsourceを取得したことを確認しました",
            "checkout source acquisitionが固定commit object exportではありません: "
            f"{export_payload.get('sourceAcquisition')!r}",
        )
        verification.require(
            "provenance.source-export.commit",
            export_payload.get("sourceCommit") == core.EXPECTED_SOURCE_COMMIT,
            "checkout source exportの固定commitを確認しました",
            "checkout source exportのsourceCommitが固定値と一致しません: "
            f"{export_payload.get('sourceCommit')!r}",
        )
        verification.require(
            "provenance.source-export.verification-copy",
            source is not None and export_payload.get("verification") == source,
            "checkout source exportのverificationがactual source identity fileと一致します",
            "checkout source exportのverificationがactual source identity fileと一致しません",
        )
        return

    if preparation == SOURCE_PREPARATION_DIRECT:
        verification.require(
            "provenance.source-export.direct-mode-absence",
            not export_path.exists() and not export_path.is_symlink(),
            "verified bundle直入力ではcheckout source exportを生成していません",
            "verified bundle直入力なのにcheckout source export fileが存在します",
        )


def verify_run_provenance(
    evidence_dir: Path,
    *,
    manifest_path: Path = core.ARTIFACT_MANIFEST,
) -> dict[str, Any]:
    core_report = core.verify_evidence_directory(
        evidence_dir,
        manifest_path=manifest_path,
    )
    verification = Verification()

    try:
        root = evidence_dir.expanduser().resolve(strict=True)
    except OSError as exc:
        verification.blocked(
            "provenance.evidence-directory",
            f"Evidence directoryを解決できません: {evidence_dir}: {exc}",
        )
        return _report(evidence_dir, core_report, verification)
    if evidence_dir.is_symlink() or not root.is_dir():
        verification.blocked(
            "provenance.evidence-directory",
            f"通常directoryのEvidenceが必要です: {evidence_dir}",
        )
        return _report(root, core_report, verification)

    try:
        manifest = core._load_manifest(manifest_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        verification.blocked(
            "provenance.artifact-manifest",
            f"固定artifact manifestを読めません: {exc}",
        )
        return _report(root, core_report, verification)

    preflight = _required_json(root, "runtime-exchange-preflight.json", verification)
    runner = _required_json(root, "runtime-exchange-runner-observation.json", verification)
    source = _optional_json(root, "kj-atlas-source-identity.json", verification)

    if preflight is not None:
        _verify_preflight(preflight, manifest, verification)

    if runner is not None:
        verification.require(
            "provenance.runner.preflight-result",
            preflight is not None
            and runner.get("preflightResult") == "ready"
            and runner.get("preflightResult") == preflight.get("result"),
            "runner observationと保存済みpreflight resultがreadyで一致します",
            "runner observationと保存済みpreflight resultが一致しません: "
            f"runner={runner.get('preflightResult')!r} "
            f"preflight={preflight.get('result') if preflight else None!r}",
        )
        _verify_runner_evidence_directory_provenance(runner, verification)
        _verify_source_preparation(
            root,
            runner=runner,
            source=source,
            verification=verification,
        )

    return _report(root, core_report, verification)


def _report(
    evidence_dir: Path,
    core_report: dict[str, Any],
    verification: Verification,
) -> dict[str, Any]:
    core_ready = core_report.get("result") == "ready-to-review"
    blockers = list(core_report.get("blockers", []))
    blockers.extend(check.id for check in verification.checks if check.status != "ok")
    checks = list(core_report.get("checks", []))
    checks.extend(asdict(check) for check in verification.checks)
    return {
        "schema": "sei.runtime-version-exchange-provenance-verification/v1",
        "evidenceDirectory": str(evidence_dir),
        "coreEvidenceResult": core_report.get("result"),
        "result": "ready-to-review" if core_ready and verification.ready else "not-sufficient",
        "blockers": blockers,
        "checks": checks,
        "stopLine": (
            "mechanical Evidence + Provenance verification PASS "
            "!= Requirement / Contract assessment complete "
            "!= outcome quality satisfied != ISSUE-000070 Resolved"
        ),
    }


def _prepare_output_path(path: Path, evidence_dir: Path) -> Path:
    return core._prepare_output_path(path, evidence_dir)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "ISSUE-000070のruntime version exchange Evidenceを、core execution条件に加えて"
            "保存済みpreflightとsource acquisition Provenanceまで再検証します。"
        )
    )
    parser.add_argument("--evidence-dir", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--json", action="store_true", help="構造化JSONだけを出力します。")
    args = parser.parse_args()

    try:
        output = (
            _prepare_output_path(args.output, args.evidence_dir)
            if args.output is not None
            else None
        )
        report = verify_run_provenance(args.evidence_dir)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.exit(2, f"runtime version exchange Provenance verification failed: {exc}\n")

    rendered = json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    if args.json or output is None:
        print(rendered, end="")
    else:
        print(f"Evidence + Provenance verification result: {report['result']}")
        if report["blockers"]:
            print("Blockers: " + ", ".join(report["blockers"]))
    return 0 if report["result"] == "ready-to-review" else 1


if __name__ == "__main__":
    raise SystemExit(main())
