#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

INTEGRATION_DIR = Path(__file__).resolve().parent
ARTIFACT_MANIFEST = INTEGRATION_DIR / "runtime_version_exchange_artifacts.json"

EXPECTED_SOURCE_COMMIT = "4f28c13abe4176503c6fed863383a2d1db2299e9"
EXPECTED_PARENT_BACKEND_TREE = "7d71ac2b4d32bef90f3a481ade1b4c92ddddd084"
EXPECTED_RUNTIME_SURFACE_TREE = "208bea71eef4afed3ddfd3fabb36b0969d167a90"
EXPECTED_SOURCE_MODE = "verified-runtime-bundle"
EXPECTED_SOURCE_VERIFICATION_BASIS = "pinned-git-object-identities"
EXPECTED_ADAPTER_SCHEMA = "sei.e3b-m1b-model-call/v1"
EXPECTED_IDENTITY_SCHEMA = "sei.runtime-version-exchange-evidence-identity/v1"
EXPECTED_RUNNER_SCHEMA = "sei.runtime-version-exchange-runner-observation/v1"
EXPECTED_TASK = "suggest_card_groups"
EXPECTED_HELD_CARD = "c-held"
EXPECTED_CARD_IDS = ("c-remote-time", "c-remote-load", EXPECTED_HELD_CARD)
EXPECTED_CARD_TEXT = {
    "c-remote-time": "在宅勤務では通勤に使う時間を減らせる",
    "c-remote-load": "在宅勤務では移動による負担を減らせる",
    "c-held": "人事評価制度の見直しはまだ着手していない",
}
EXPECTED_COMPLETION_MARKER = b"Runtime version exchange probe completed successfully."


@dataclass(frozen=True)
class Check:
    id: str
    status: str
    detail: str


class Verification:
    def __init__(self) -> None:
        self.checks: list[Check] = []

    def ok(self, check_id: str, detail: str) -> None:
        self.checks.append(Check(check_id, "ok", detail))

    def blocked(self, check_id: str, detail: str) -> None:
        self.checks.append(Check(check_id, "blocked", detail))

    def require(
        self,
        check_id: str,
        condition: bool,
        ok_detail: str,
        blocked_detail: str,
    ) -> bool:
        if condition:
            self.ok(check_id, ok_detail)
            return True
        self.blocked(check_id, blocked_detail)
        return False

    @property
    def ready(self) -> bool:
        return all(check.status == "ok" for check in self.checks)


def _load_manifest(path: Path = ARTIFACT_MANIFEST) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema") != "sei.runtime-version-exchange-artifact-manifest/v1":
        raise ValueError(f"artifact manifest schema mismatch: {payload.get('schema')!r}")
    return payload


def _required_file(root: Path, name: str, verification: Verification) -> Path | None:
    path = root / name
    if path.is_symlink():
        verification.blocked(
            f"file.{name}",
            f"Evidence fileはsymlinkを許可しません: {path}",
        )
        return None
    if not path.is_file():
        verification.blocked(f"file.{name}", f"Evidence fileがありません: {path}")
        return None
    verification.ok(f"file.{name}", f"Evidence fileを確認しました: {name}")
    return path


def _read_json(
    root: Path,
    name: str,
    verification: Verification,
) -> dict[str, Any] | None:
    path = _required_file(root, name, verification)
    if path is None:
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        verification.blocked(f"json.{name}", f"JSONを解釈できません: {name}: {exc}")
        return None
    if not isinstance(payload, dict):
        verification.blocked(f"json.{name}", f"JSON objectが必要です: {name}")
        return None
    verification.ok(f"json.{name}", f"JSON objectを確認しました: {name}")
    return payload


def _read_text(root: Path, name: str, verification: Verification) -> str | None:
    path = _required_file(root, name, verification)
    if path is None:
        return None
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        verification.blocked(
            f"text.{name}",
            f"UTF-8 textとして読めません: {name}: {exc}",
        )
        return None
    verification.ok(f"text.{name}", f"UTF-8 textを確認しました: {name}")
    return text


def _exact_version_token(text: str, version: str) -> bool:
    return re.search(rf"(^|[^0-9]){re.escape(version)}([^0-9]|$)", text) is not None


def _model_digest_from_tags(payload: dict[str, Any], model_name: str) -> str | None:
    models = payload.get("models")
    if not isinstance(models, list):
        return None
    for item in models:
        if isinstance(item, dict) and item.get("name") == model_name:
            digest = item.get("digest")
            if isinstance(digest, str):
                return digest
    return None


def _verify_request(payload: dict[str, Any], verification: Verification) -> None:
    cards = payload.get("cards")
    actual_ids = (
        tuple(card.get("id") for card in cards if isinstance(card, dict))
        if isinstance(cards, list)
        else ()
    )
    verification.require(
        "request.cards",
        actual_ids == EXPECTED_CARD_IDS,
        "固定3-card Method inputを確認しました",
        f"Method inputのcard IDが固定値と一致しません: actual={actual_ids}",
    )
    actual_text = (
        {
            card.get("id"): card.get("text")
            for card in cards
            if isinstance(card, dict) and isinstance(card.get("id"), str)
        }
        if isinstance(cards, list)
        else {}
    )
    verification.require(
        "request.card-text",
        actual_text == EXPECTED_CARD_TEXT,
        "固定3-card Method inputの本文を確認しました",
        f"Method input本文が固定値と一致しません: actual={actual_text!r}",
    )

    doc = payload.get("doc")
    doc_cards = doc.get("cards") if isinstance(doc, dict) else None
    held = None
    if isinstance(doc_cards, list):
        held = next(
            (
                item
                for item in doc_cards
                if isinstance(item, dict) and item.get("id") == EXPECTED_HELD_CARD
            ),
            None,
        )
    verification.require(
        "request.held-card",
        isinstance(held, dict) and held.get("holdState") == "held",
        "固定held cardを確認しました",
        "c-heldがheld状態として固定されていません",
    )


def _verify_model_evidence(
    label: str,
    payload: dict[str, Any],
    model_name: str,
    verification: Verification,
) -> str | None:
    prefix = f"inference.{label}"
    verification.require(
        f"{prefix}.schema",
        payload.get("schema") == EXPECTED_ADAPTER_SCHEMA,
        f"runtime {label} model Evidence schemaを確認しました",
        f"runtime {label} model Evidence schemaが一致しません: {payload.get('schema')!r}",
    )
    verification.require(
        f"{prefix}.model",
        payload.get("model") == model_name,
        f"runtime {label} model名を確認しました: {model_name}",
        f"runtime {label} model名が固定値と一致しません: {payload.get('model')!r}",
    )
    verification.require(
        f"{prefix}.task",
        payload.get("task") == EXPECTED_TASK,
        f"runtime {label} taskを確認しました",
        f"runtime {label} taskが一致しません: {payload.get('task')!r}",
    )
    verification.require(
        f"{prefix}.done",
        payload.get("ollama_done") is True,
        f"runtime {label} actual inference完了を確認しました",
        f"runtime {label} ollama_done=trueを確認できません",
    )
    for key in ("prompt_eval_count", "eval_count"):
        value = payload.get(key)
        verification.require(
            f"{prefix}.{key}",
            isinstance(value, int) and not isinstance(value, bool) and value > 0,
            f"runtime {label} {key}>0を確認しました: {value}",
            f"runtime {label} {key}>0を確認できません: {value!r}",
        )
    prompt_sha = payload.get("prompt_sha256")
    verification.require(
        f"{prefix}.prompt-sha256",
        isinstance(prompt_sha, str)
        and re.fullmatch(r"[0-9a-f]{64}", prompt_sha) is not None,
        f"runtime {label} prompt SHA-256を確認しました",
        f"runtime {label} prompt SHA-256が不正です: {prompt_sha!r}",
    )
    return prompt_sha if isinstance(prompt_sha, str) else None


def _verify_result(
    label: str,
    payload: dict[str, Any],
    verification: Verification,
) -> None:
    groups = payload.get("groups")
    verification.require(
        f"result.{label}.groups",
        isinstance(groups, list) and bool(groups),
        f"runtime {label} KJ Atlas groupsを確認しました",
        f"runtime {label} KJ Atlas groupsが空または不正です",
    )
    verification.require(
        f"result.{label}.excluded",
        payload.get("excludedCardIds") == [EXPECTED_HELD_CARD],
        f"runtime {label} held card除外を確認しました",
        f"runtime {label} excludedCardIdsが固定値と一致しません: {payload.get('excludedCardIds')!r}",
    )
    verification.require(
        f"result.{label}.truncated",
        payload.get("truncated") is False,
        f"runtime {label} resultがtruncatedではないことを確認しました",
        f"runtime {label} truncated=falseを確認できません",
    )


def verify_evidence_directory(
    evidence_dir: Path,
    *,
    manifest_path: Path = ARTIFACT_MANIFEST,
) -> dict[str, Any]:
    verification = Verification()
    if evidence_dir.is_symlink():
        verification.blocked(
            "evidence.directory",
            f"Evidence directoryはsymlinkを許可しません: {evidence_dir}",
        )
        return _report(evidence_dir, verification)
    try:
        root = evidence_dir.resolve(strict=True)
    except OSError as exc:
        verification.blocked(
            "evidence.directory",
            f"Evidence directoryを解決できません: {evidence_dir}: {exc}",
        )
        return _report(evidence_dir, verification)
    if not root.is_dir():
        verification.blocked(
            "evidence.directory",
            f"Evidence directoryではありません: {root}",
        )
        return _report(root, verification)
    verification.ok("evidence.directory", f"Evidence directoryを確認しました: {root}")

    try:
        manifest = _load_manifest(manifest_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        verification.blocked("artifact-manifest", f"固定artifact manifestを読めません: {exc}")
        return _report(root, verification)
    verification.ok("artifact-manifest", "固定artifact manifestを確認しました")

    runtime_a = manifest["runtimeArchives"]["a"]
    runtime_b = manifest["runtimeArchives"]["b"]
    model = manifest["model"]
    model_name = model["name"]
    model_sha = model["sha256"]

    identity = _read_json(root, "runtime-exchange-identity.json", verification)
    source = _read_json(root, "kj-atlas-source-identity.json", verification)
    request = _read_json(root, "kj-atlas-runtime-exchange-request.json", verification)
    runner = _read_json(root, "runtime-exchange-runner-observation.json", verification)

    if identity is not None:
        verification.require(
            "identity.schema",
            identity.get("schema") == EXPECTED_IDENTITY_SCHEMA,
            "runtime exchange identity schemaを確認しました",
            f"runtime exchange identity schemaが一致しません: {identity.get('schema')!r}",
        )
        repository_commit = identity.get("repositoryCommit")
        verification.require(
            "identity.repository-commit",
            isinstance(repository_commit, str)
            and re.fullmatch(r"[0-9a-f]{40}", repository_commit) is not None,
            "SEI repository commitをEvidenceへ保持しています",
            f"SEI repository commitが不正です: {repository_commit!r}",
        )
        host = identity.get("executionHost")
        verification.require(
            "identity.host",
            isinstance(host, dict)
            and host.get("os") == "linux"
            and host.get("arch") == "amd64",
            "固定runtime artifactに対応するLinux / amd64 hostを確認しました",
            f"execution hostが固定artifact条件と一致しません: {host!r}",
        )
        verification.require(
            "identity.quality-boundary",
            identity.get("qualityJudgement") == "not_evaluated",
            "qualityJudgement=not_evaluatedを保持しています",
            f"成果品質を実行Evidenceから昇格させています: {identity.get('qualityJudgement')!r}",
        )
        for label, expected in (("runtimeA", runtime_a), ("runtimeB", runtime_b)):
            actual = identity.get(label)
            archive_acquisition = actual.get("archiveAcquisition") if isinstance(actual, dict) else None
            verification.require(
                f"identity.{label}",
                isinstance(actual, dict)
                and actual.get("name") == "ollama"
                and actual.get("version") == expected["version"]
                and actual.get("archiveSha256") == expected["sha256"]
                and isinstance(archive_acquisition, str)
                and archive_acquisition in {"downloaded", "prepositioned"},
                f"{label}固定identityを確認しました",
                f"{label}固定identityがartifact manifestと一致しません: {actual!r}",
            )
        actual_model = identity.get("model")
        storage_mode = actual_model.get("storageMode") if isinstance(actual_model, dict) else None
        verification.require(
            "identity.model",
            isinstance(actual_model, dict)
            and actual_model.get("name") == model_name
            and actual_model.get("expectedDigest") == model_sha
            and isinstance(storage_mode, str)
            and storage_mode in {"work-local", "prepositioned"},
            "固定model identityを確認しました",
            f"固定model identityがartifact manifestと一致しません: {actual_model!r}",
        )

    if source is not None:
        verification.require(
            "source.schema",
            source.get("schema") == "sei.kj-atlas-runtime-source-identity/v1",
            "KJ Atlas source identity schemaを確認しました",
            f"KJ Atlas source identity schemaが一致しません: {source.get('schema')!r}",
        )
        verification.require(
            "source.verified",
            source.get("verified") is True and source.get("repository") == "hat47x/kj-atlas",
            "KJ Atlas verified source identityを確認しました",
            "KJ Atlas verified source identityを確認できません: "
            f"verified={source.get('verified')!r} repository={source.get('repository')!r}",
        )
        verification.require(
            "source.mode",
            source.get("sourceMode") == EXPECTED_SOURCE_MODE,
            "strict verified-runtime-bundle sourceを確認しました",
            f"strict Evidenceではverified-runtime-bundleが必要です: {source.get('sourceMode')!r}",
        )
        for key, expected in (
            ("sourceCommit", EXPECTED_SOURCE_COMMIT),
            ("pinnedBackendTree", EXPECTED_PARENT_BACKEND_TREE),
            ("runtimeSurfaceTree", EXPECTED_RUNTIME_SURFACE_TREE),
            ("verificationBasis", EXPECTED_SOURCE_VERIFICATION_BASIS),
        ):
            verification.require(
                f"source.{key}",
                source.get(key) == expected,
                f"source {key}を固定値へ一致させました",
                f"source {key}が固定値と一致しません: "
                f"actual={source.get(key)!r} expected={expected}",
            )
        if identity is not None:
            verification.require(
                "source.identity-copy",
                identity.get("methodSource") == source,
                "identity fileとsource identity fileが一致します",
                "runtime-exchange-identity.jsonのmethodSourceがsource identity fileと一致しません",
            )

    if request is not None:
        _verify_request(request, verification)

    if runner is not None:
        verification.require(
            "runner.schema",
            runner.get("schema") == EXPECTED_RUNNER_SCHEMA,
            "runner observation schemaを確認しました",
            f"runner observation schemaが一致しません: {runner.get('schema')!r}",
        )
        verification.require(
            "runner.quality-boundary",
            runner.get("qualityJudgement") == "not_evaluated",
            "runner observationでもqualityJudgement=not_evaluatedを保持しています",
            f"runner observationが成果品質を昇格させています: {runner.get('qualityJudgement')!r}",
        )
        verification.require(
            "runner.exit-code",
            runner.get("exitCode") == 0 and runner.get("completed") is True,
            "repository-local harnessのexit code 0を観測しています",
            f"repository-local harnessの完走を確認できません: exitCode={runner.get('exitCode')!r}",
        )
        output_sha = runner.get("combinedOutputSha256")
        verification.require(
            "runner.output-sha256",
            isinstance(output_sha, str)
            and re.fullmatch(r"[0-9a-f]{64}", output_sha) is not None,
            "harness combined output SHA-256を確認しました",
            f"harness combined output SHA-256が不正です: {output_sha!r}",
        )
        runner_log_path = _required_file(root, "runtime-exchange-runner.log", verification)
        if runner_log_path is not None:
            try:
                runner_log = runner_log_path.read_bytes()
            except OSError as exc:
                verification.blocked("runner.log-read", f"runner logを読めません: {exc}")
            else:
                actual_output_sha = hashlib.sha256(runner_log).hexdigest()
                verification.require(
                    "runner.log-sha256",
                    actual_output_sha == output_sha,
                    "runner observationとcombined output logのSHA-256が一致します",
                    "runner log SHA-256がobservationと一致しません: "
                    f"actual={actual_output_sha} expected={output_sha}",
                )
                output_bytes = runner.get("combinedOutputBytes")
                verification.require(
                    "runner.log-size",
                    output_bytes == len(runner_log),
                    f"runner combined output bytesを確認しました: {len(runner_log)}",
                    "runner combined output sizeが一致しません: "
                    f"actual={len(runner_log)} expected={output_bytes!r}",
                )
                verification.require(
                    "runner.completion-marker",
                    EXPECTED_COMPLETION_MARKER in runner_log,
                    "harness最終completion markerを確認しました",
                    "harness最終completion markerがrunner logにありません",
                )

    version_a = _read_text(root, "runtime-exchange-a-version.txt", verification)
    version_b = _read_text(root, "runtime-exchange-b-version.txt", verification)
    if version_a is not None:
        verification.require(
            "runtime.a.version",
            _exact_version_token(version_a, runtime_a["version"]),
            f"runtime A actual version {runtime_a['version']}を確認しました",
            f"runtime A version logに{runtime_a['version']}がありません",
        )
    if version_b is not None:
        verification.require(
            "runtime.b.version",
            _exact_version_token(version_b, runtime_b["version"]),
            f"runtime B actual version {runtime_b['version']}を確認しました",
            f"runtime B version logに{runtime_b['version']}がありません",
        )

    for label, expected in (("a", runtime_a), ("b", runtime_b)):
        digest = _read_text(
            root,
            f"runtime-exchange-{label}-archive-sha256.txt",
            verification,
        )
        if digest is not None:
            actual = digest.strip()
            verification.require(
                f"runtime.{label}.archive-sha256",
                actual == expected["sha256"],
                f"runtime {label.upper()} actual archive SHA-256を確認しました",
                f"runtime {label.upper()} archive SHA-256が固定値と一致しません: "
                f"actual={actual} expected={expected['sha256']}",
            )

    model_ids: dict[str, str | None] = {}
    tag_digests: dict[str, str | None] = {}
    model_evidence: dict[str, dict[str, Any] | None] = {}
    for label in ("a", "b"):
        model_id_text = _read_text(
            root,
            f"runtime-exchange-{label}-model-id.txt",
            verification,
        )
        model_id = model_id_text.strip() if model_id_text is not None else None
        model_ids[label] = model_id
        if model_id is not None:
            verification.require(
                f"model.{label}.id",
                model_id == model_sha,
                f"runtime {label.upper()} fixed model full digestを確認しました",
                f"runtime {label.upper()} model digestが固定値と一致しません: "
                f"actual={model_id} expected={model_sha}",
            )

        tags = _read_json(root, f"runtime-exchange-{label}-tags.json", verification)
        tag_digest = _model_digest_from_tags(tags, model_name) if tags is not None else None
        tag_digests[label] = tag_digest
        if tags is not None:
            verification.require(
                f"model.{label}.tags",
                tag_digest == model_sha,
                f"runtime {label.upper()} /api/tagsで固定model digestを確認しました",
                f"runtime {label.upper()} /api/tagsで固定model digestを確認できません: "
                f"{tag_digest!r}",
            )

        evidence = _read_json(
            root,
            f"runtime-exchange-{label}-evidence.json",
            verification,
        )
        model_evidence[label] = evidence
        if evidence is not None:
            _verify_model_evidence(label, evidence, model_name, verification)

        result = _read_json(
            root,
            f"runtime-exchange-{label}-result.json",
            verification,
        )
        if result is not None:
            _verify_result(label, result, verification)

    verification.require(
        "model.same-artifact",
        model_ids.get("a") == model_sha and model_ids.get("b") == model_sha,
        "A / Bが同じ固定model artifactを使ったことを確認しました",
        "A / Bのmodel artifactが固定条件を満たしません: "
        f"A={model_ids.get('a')!r} B={model_ids.get('b')!r}",
    )
    verification.require(
        "model.tags-same-artifact",
        tag_digests.get("a") == model_sha and tag_digests.get("b") == model_sha,
        "A / Bの/api/tags観測が同じ固定model artifactへ一致します",
        "A / Bの/api/tags観測が固定条件を満たしません: "
        f"A={tag_digests.get('a')!r} B={tag_digests.get('b')!r}",
    )

    prompt_a = (
        model_evidence.get("a", {}).get("prompt_sha256")
        if isinstance(model_evidence.get("a"), dict)
        else None
    )
    prompt_b = (
        model_evidence.get("b", {}).get("prompt_sha256")
        if isinstance(model_evidence.get("b"), dict)
        else None
    )
    verification.require(
        "inference.same-prompt",
        isinstance(prompt_a, str) and prompt_a == prompt_b,
        f"A / Bのprompt SHA-256が一致します: {prompt_a}",
        f"A / Bのprompt SHA-256が一致しません: A={prompt_a!r} B={prompt_b!r}",
    )

    return _report(root, verification)


def _report(evidence_dir: Path, verification: Verification) -> dict[str, Any]:
    blockers = [check.id for check in verification.checks if check.status != "ok"]
    return {
        "schema": "sei.runtime-version-exchange-evidence-verification/v1",
        "evidenceDirectory": str(evidence_dir),
        "result": "ready-to-review" if verification.ready else "not-sufficient",
        "blockers": blockers,
        "checks": [asdict(check) for check in verification.checks],
        "stopLine": (
            "mechanical Evidence verification PASS != Requirement / Contract assessment complete "
            "!= outcome quality satisfied != ISSUE-000070 Resolved"
        ),
    }


def _prepare_output_path(path: Path, evidence_dir: Path) -> Path:
    output = path.expanduser().resolve(strict=False)
    evidence = evidence_dir.expanduser().resolve(strict=False)
    if output.exists():
        raise ValueError(f"output path already exists: {output}")
    if output == evidence or evidence in output.parents:
        raise ValueError(
            f"verification output must not be inside the Evidence directory: {output}"
        )
    return output


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "ISSUE-000070のruntime version exchange Evidence directoryを"
            "副作用なく再検証します。"
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
        report = verify_evidence_directory(args.evidence_dir)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.exit(2, f"runtime version exchange Evidence verification failed: {exc}\n")

    rendered = json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    if args.json or output is None:
        print(rendered, end="")
    else:
        print(f"Evidence verification result: {report['result']}")
        if report["blockers"]:
            print("Blockers: " + ", ".join(report["blockers"]))
    return 0 if report["result"] == "ready-to-review" else 1


if __name__ == "__main__":
    raise SystemExit(main())
