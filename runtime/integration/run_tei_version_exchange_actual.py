#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import tarfile
from pathlib import Path

import run_tei_bundle_adapter_compatibility as adapter_runner
import run_tei_revision_b_prepositioned as bundle_runner

SCHEMA = "soza.tei-version-exchange-actual/v1"
STOP_LINE = (
    "actual E2/E3 orchestration result recorded "
    "!= ISSUE-000072 Resolved != arbitrary TEI version compatibility "
    "!= Release Evidence != Operational Evidence"
)


def _write_new_json(path: Path, payload: dict[str, object]) -> None:
    path = path.expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    fd = os.open(path, flags, 0o600)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, sort_keys=True, indent=2)
            handle.write("\n")
    except Exception:
        try:
            path.unlink(missing_ok=True)
        finally:
            raise


def _failure_payload(
    phase: str,
    failure: dict[str, object],
    *,
    e2: dict[str, object] | None = None,
) -> dict[str, object]:
    value: dict[str, object] = {
        "schema": SCHEMA,
        "result": "failed",
        "phase": phase,
        "failure": failure,
        "qualityJudgement": "not_evaluated",
        "stopLine": STOP_LINE,
    }
    if e2 is not None:
        value["e2"] = e2
    return value


def run_actual(
    *,
    source_repo: Path,
    reference_source_repo: Path,
    output_archive: Path,
    soza_repo_root: Path,
    expected_soza_head: str | None,
    result_file: Path,
) -> tuple[int, dict[str, object]]:
    output_archive = output_archive.expanduser().resolve()
    result_file = result_file.expanduser().resolve()
    if output_archive == result_file:
        raise ValueError("Evidence bundleとresult JSONに同じpathを指定できません")
    if output_archive.exists():
        raise FileExistsError(
            f"既存Evidence bundleを上書きしません: {output_archive}"
        )
    if result_file.exists():
        raise FileExistsError(f"既存result JSONを上書きしません: {result_file}")

    try:
        e2 = bundle_runner.produce_bundle(
            source_repo,
            reference_source_repo,
            output_archive,
        )
    except bundle_runner.TEIEvidenceStageError as exc:
        payload = _failure_payload("E2", exc.as_dict())
        _write_new_json(result_file, payload)
        return 1, payload
    except (OSError, ValueError, tarfile.TarError) as exc:
        payload = _failure_payload(
            "E2",
            {"stage": "unclassified_e2", "message": str(exc)},
        )
        _write_new_json(result_file, payload)
        return 1, payload

    try:
        e3 = adapter_runner.run_compatibility(
            output_archive,
            soza_repo_root=soza_repo_root,
            expected_source_commit=bundle_runner.source_identity.REVISION_B,
            expected_soza_head=expected_soza_head,
        )
    except adapter_runner.TEIAdapterStageError as exc:
        payload = _failure_payload("E3", exc.as_dict(), e2=e2)
        _write_new_json(result_file, payload)
        return 1, payload
    except (OSError, ValueError, RuntimeError, tarfile.TarError) as exc:
        payload = _failure_payload(
            "E3",
            {"stage": "unclassified_e3", "message": str(exc)},
            e2=e2,
        )
        _write_new_json(result_file, payload)
        return 1, payload

    payload = {
        "schema": SCHEMA,
        "result": "ready_to_review",
        "phase": "complete",
        "e2": e2,
        "e3": e3,
        "qualityJudgement": "not_evaluated",
        "stopLine": STOP_LINE,
    }
    _write_new_json(result_file, payload)
    return 0, payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "ISSUE-000072のactual E2/E3をrepository-local runnerで順に実行し、"
            "成功・失敗のどちらでも新規JSONへ結果を保存します。"
        ),
        allow_abbrev=False,
    )
    parser.add_argument("--source-repo", required=True, type=Path)
    parser.add_argument("--reference-source-repo", required=True, type=Path)
    parser.add_argument("--output-archive", required=True, type=Path)
    parser.add_argument("--soza-repo-root", required=True, type=Path)
    parser.add_argument("--expected-soza-head")
    parser.add_argument("--result-file", required=True, type=Path)
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        code, payload = run_actual(
            source_repo=args.source_repo,
            reference_source_repo=args.reference_source_repo,
            output_archive=args.output_archive,
            soza_repo_root=args.soza_repo_root,
            expected_soza_head=args.expected_soza_head,
            result_file=args.result_file,
        )
    except (OSError, ValueError) as exc:
        print(f"TEI version exchange actual orchestration could not start: {exc}")
        return 2

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2))
    elif code == 0:
        print("TEI version exchange actual orchestration: ready to review")
        print(f"- result file: {args.result_file}")
        print(f"- Evidence bundle: {args.output_archive}")
        print(STOP_LINE)
    else:
        failure = payload["failure"]
        print(
            "TEI version exchange actual orchestration failed at "
            f"{payload['phase']}/{failure['stage']}: {failure['message']}"
        )
        print(f"- result file: {args.result_file}")
        print(STOP_LINE)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
