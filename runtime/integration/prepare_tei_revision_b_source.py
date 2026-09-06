#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import json
import os
import shutil
import subprocess
import tempfile
import urllib.error
import urllib.request
from pathlib import Path
from typing import Callable, Mapping

from runtime_path_safety import reject_symlink_path_or_ancestors
from verify_tei_execution_source_identity import (
    EXPECTED_OBJECTS,
    REVISION_B,
    verify_repository,
)

GITHUB_REPOSITORY = "hat47x/tei-platform"
REVISION_B_ROOT_TREE = "630d3e9e2acaea70312bee19cf8a0f7235655cd6"
SOZA_ROOT = Path(__file__).resolve().parents[2]
API_BASE = "https://api.github.com"
API_REPOSITORY_BASE = f"{API_BASE}/repos/{GITHUB_REPOSITORY}/"
STOP_LINE = (
    "exact revision B source materialized and canonical identity verified "
    "!= revision B build PASS != Provider Plan execution PASS "
    "!= SOZA Adapter compatibility PASS != ISSUE-000072 Resolved"
)
JsonRequester = Callable[[str, str], dict[str, object]]


class _RejectRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError(
            "GitHub API redirectをcredential付きrequestでは許可しません: "
            f"status={code} from={req.full_url} to={newurl}"
        )


def _run_git(
    repo: Path,
    *args: str,
    input_bytes: bytes | None = None,
) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        input=input_bytes,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def _require_git_success(
    result: subprocess.CompletedProcess[bytes],
    label: str,
) -> bytes:
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise ValueError(f"{label}に失敗しました: {detail}")
    return result.stdout


def _paths_overlap(left: Path, right: Path) -> bool:
    left = left.expanduser().resolve(strict=False)
    right = right.expanduser().resolve(strict=False)
    return left == right or left in right.parents or right in left.parents


def _prepare_output_path(output_dir: Path) -> Path:
    requested = output_dir.expanduser()
    reject_symlink_path_or_ancestors(requested, "TEI revision B source出力")
    output = requested.resolve(strict=False)
    if output.exists():
        raise ValueError(
            f"TEI revision B source出力は新規pathを指定してください: {output}"
        )
    if output == SOZA_ROOT or SOZA_ROOT in output.parents:
        raise ValueError(
            f"TEI revision B source出力をSOZA repository配下には置けません: {output}"
        )
    return output


def _prepare_report_path(path: Path, output_dir: Path) -> Path:
    requested = path.expanduser()
    reject_symlink_path_or_ancestors(requested, "TEI source acquisition report")
    report = requested.resolve(strict=False)
    if report.exists():
        raise ValueError(
            f"TEI source acquisition reportは新規pathを指定してください: {report}"
        )
    if _paths_overlap(report, output_dir):
        raise ValueError(
            "TEI source acquisition reportはmaterialized sourceから分離してください: "
            f"report={report} source={output_dir}"
        )
    if report == SOZA_ROOT or SOZA_ROOT in report.parents:
        raise ValueError(
            f"TEI source acquisition reportをSOZA repository配下には置けません: {report}"
        )
    return report


def _github_json(url: str, token: str) -> dict[str, object]:
    if not url.startswith(API_REPOSITORY_BASE):
        raise ValueError(f"許可されていないGitHub repository API URLです: {url}")
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "soza-tei-revision-b-source-acquisition",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    opener = urllib.request.build_opener(_RejectRedirectHandler())
    try:
        with opener.open(request, timeout=60) as response:
            raw = response.read()
    except urllib.error.HTTPError as exc:
        raise ValueError(
            f"GitHub API request failed: status={exc.code} url={url}"
        ) from exc
    except urllib.error.URLError as exc:
        raise ValueError(
            f"GitHub API request failed: url={url} reason={exc.reason}"
        ) from exc
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(
            f"GitHub API responseをJSONとして解釈できません: {url}"
        ) from exc
    if not isinstance(payload, dict):
        raise ValueError(f"GitHub API responseがobjectではありません: {url}")
    return payload


def _api(path: str) -> str:
    return f"{API_BASE}/repos/{GITHUB_REPOSITORY}/{path.lstrip('/')}"


def _hash_blob(repo: Path, content: bytes) -> str:
    result = _run_git(repo, "hash-object", "-w", "--stdin", input_bytes=content)
    return _require_git_success(result, "Git blob object作成").decode().strip()


def _hash_tree(
    repo: Path,
    entries: list[tuple[str, str, str, str]],
) -> str:
    # `-z`によりpath名をquote変換せず、そのままGit treeへ渡す。
    data = b"".join(
        f"{mode} {object_type} {sha}\t".encode("ascii")
        + name.encode("utf-8")
        + b"\0"
        for mode, object_type, sha, name in entries
    )
    result = _run_git(repo, "mktree", "-z", input_bytes=data)
    return _require_git_success(result, "Git tree object作成").decode().strip()


def _format_gpgsig(signature: str) -> bytes:
    if not signature:
        raise ValueError("GitHub commit verification signatureが空です")
    encoded = signature.encode("utf-8")
    lines = encoded.splitlines(keepends=True)
    if not lines:
        raise ValueError("GitHub commit verification signatureをlineへ分解できません")
    if not lines[-1].endswith(b"\n"):
        raise ValueError("GitHub commit verification signatureの末尾改行がありません")
    return b"gpgsig " + lines[0] + b"".join(b" " + line for line in lines[1:])


def _reconstruct_signed_commit(payload: str, signature: str) -> bytes:
    raw_payload = payload.encode("utf-8")
    marker = raw_payload.find(b"\n\n")
    if marker < 0:
        raise ValueError(
            "GitHub commit verification payloadにheader/message境界がありません"
        )
    header = raw_payload[:marker]
    message = raw_payload[marker + 2 :]
    return header + b"\n" + _format_gpgsig(signature) + b"\n" + message


def _write_commit_object(repo: Path, raw_commit: bytes) -> str:
    result = _run_git(
        repo,
        "hash-object",
        "-t",
        "commit",
        "-w",
        "--stdin",
        input_bytes=raw_commit,
    )
    return _require_git_success(result, "Git commit object作成").decode().strip()


class _Acquirer:
    def __init__(self, repo: Path, token: str, request_json: JsonRequester):
        self.repo = repo
        self.token = token
        self.request_json = request_json
        self.tree_cache: set[str] = set()
        self.blob_cache: set[str] = set()
        self.tree_count = 0
        self.blob_count = 0
        self.blob_bytes = 0
        self.request_count = 0

    def _get(self, path: str) -> dict[str, object]:
        self.request_count += 1
        return self.request_json(_api(path), self.token)

    def materialize_blob(self, expected_sha: str) -> None:
        if expected_sha in self.blob_cache:
            return

        payload = self._get(f"git/blobs/{expected_sha}")
        if payload.get("sha") != expected_sha:
            raise ValueError(
                "GitHub blob responseのSHAが期待値と一致しません: "
                f"expected={expected_sha} actual={payload.get('sha')}"
            )
        if payload.get("encoding") != "base64" or not isinstance(
            payload.get("content"), str
        ):
            raise ValueError(
                f"GitHub blob responseのencoding/contentが不正です: {expected_sha}"
            )

        try:
            content = base64.b64decode(payload["content"], validate=False)
        except Exception as exc:
            raise ValueError(
                f"GitHub blob contentをBase64 decodeできません: {expected_sha}"
            ) from exc

        declared_size = payload.get("size")
        if isinstance(declared_size, int) and len(content) != declared_size:
            raise ValueError(
                f"GitHub blob sizeが一致しません: sha={expected_sha} "
                f"expected={declared_size} actual={len(content)}"
            )

        actual_sha = _hash_blob(self.repo, content)
        if actual_sha != expected_sha:
            raise ValueError(
                "取得blob bytesのGit object identityが期待値と一致しません: "
                f"expected={expected_sha} actual={actual_sha}"
            )

        self.blob_cache.add(expected_sha)
        self.blob_count += 1
        self.blob_bytes += len(content)

    def materialize_tree(self, expected_sha: str) -> None:
        if expected_sha in self.tree_cache:
            return

        payload = self._get(f"git/trees/{expected_sha}")
        if payload.get("sha") != expected_sha:
            raise ValueError(
                "GitHub tree responseのSHAが期待値と一致しません: "
                f"expected={expected_sha} actual={payload.get('sha')}"
            )
        if payload.get("truncated") is not False:
            raise ValueError(
                "GitHub tree responseのtruncated=falseを確認できません: "
                f"{expected_sha}"
            )

        raw_entries = payload.get("tree")
        if not isinstance(raw_entries, list):
            raise ValueError(
                f"GitHub tree responseにtree配列がありません: {expected_sha}"
            )

        entries: list[tuple[str, str, str, str]] = []
        for raw in raw_entries:
            if not isinstance(raw, dict):
                raise ValueError(
                    f"GitHub tree entryがobjectではありません: {expected_sha}"
                )
            name = raw.get("path")
            mode = raw.get("mode")
            object_type = raw.get("type")
            child_sha = raw.get("sha")
            if not all(
                isinstance(value, str) and value
                for value in (name, mode, object_type, child_sha)
            ):
                raise ValueError(
                    f"GitHub tree entryの必須fieldが不足しています: tree={expected_sha}"
                )
            if "/" in name or "\x00" in name:
                raise ValueError(
                    f"GitHub tree entry名が不正です: tree={expected_sha} path={name!r}"
                )

            if object_type == "tree":
                if mode != "040000":
                    raise ValueError(
                        f"tree entry modeが不正です: path={name} mode={mode}"
                    )
                self.materialize_tree(child_sha)
            elif object_type == "blob":
                if mode not in {"100644", "100755"}:
                    raise ValueError(
                        "通常file/executable以外のGit entryはsource acquisitionで受理しません: "
                        f"path={name} mode={mode}"
                    )
                self.materialize_blob(child_sha)
            else:
                raise ValueError(
                    "未対応Git object typeをsource acquisitionで受理しません: "
                    f"path={name} type={object_type} mode={mode}"
                )
            entries.append((mode, object_type, child_sha, name))

        actual_sha = _hash_tree(self.repo, entries)
        if actual_sha != expected_sha:
            raise ValueError(
                "取得tree entryから再構成したGit tree identityが期待値と一致しません: "
                f"expected={expected_sha} actual={actual_sha}"
            )

        self.tree_cache.add(expected_sha)
        self.tree_count += 1

    def materialize_commit(
        self,
        expected_commit: str,
        expected_root_tree: str,
    ) -> None:
        payload = self._get(f"git/commits/{expected_commit}")
        if payload.get("sha") != expected_commit:
            raise ValueError(
                "GitHub commit responseのSHAが期待値と一致しません: "
                f"expected={expected_commit} actual={payload.get('sha')}"
            )

        tree = payload.get("tree")
        if not isinstance(tree, dict) or tree.get("sha") != expected_root_tree:
            actual = tree.get("sha") if isinstance(tree, dict) else None
            raise ValueError(
                "GitHub commitのroot treeが期待値と一致しません: "
                f"expected={expected_root_tree} actual={actual}"
            )

        verification = payload.get("verification")
        if not isinstance(verification, dict) or verification.get("verified") is not True:
            raise ValueError("GitHub commit verificationがverified=trueではありません")
        raw_payload = verification.get("payload")
        signature = verification.get("signature")
        if not isinstance(raw_payload, str) or not isinstance(signature, str):
            raise ValueError("GitHub commit verification payload/signatureがありません")

        raw_commit = _reconstruct_signed_commit(raw_payload, signature)
        actual_commit = _write_commit_object(self.repo, raw_commit)
        if actual_commit != expected_commit:
            raise ValueError(
                "再構成したsigned commit identityが期待値と一致しません: "
                f"expected={expected_commit} actual={actual_commit}"
            )

    def observation(self) -> dict[str, int]:
        return {
            "apiRequests": self.request_count,
            "treesMaterialized": self.tree_count,
            "uniqueBlobsMaterialized": self.blob_count,
            "blobBytesMaterialized": self.blob_bytes,
        }


def _initialize_repository(path: Path) -> None:
    if not path.is_dir():
        raise ValueError(f"staging directoryがありません: {path}")
    _require_git_success(_run_git(path, "init", "-q"), "Git repository初期化")
    _require_git_success(
        _run_git(path, "config", "core.autocrlf", "false"),
        "core.autocrlf設定",
    )
    _require_git_success(
        _run_git(path, "config", "core.filemode", "true"),
        "core.filemode設定",
    )


def _checkout_exact_commit(repo: Path, commit: str, root_tree: str) -> None:
    _require_git_success(
        _run_git(repo, "update-ref", "--no-deref", "HEAD", commit),
        "detached HEAD設定",
    )
    _require_git_success(_run_git(repo, "read-tree", root_tree), "Git index作成")
    _require_git_success(
        _run_git(repo, "checkout-index", "-a"),
        "working tree展開",
    )


def materialize_revision_b_source(
    output_dir: Path,
    *,
    token: str,
    repository: str = GITHUB_REPOSITORY,
    expected_commit: str = REVISION_B,
    expected_root_tree: str = REVISION_B_ROOT_TREE,
    expected_objects: Mapping[str, str] = EXPECTED_OBJECTS,
    request_json: JsonRequester = _github_json,
) -> dict[str, object]:
    if repository != GITHUB_REPOSITORY:
        raise ValueError(f"未承認repositoryです: {repository}")
    if not token:
        raise ValueError("GitHub API tokenがありません")

    output = _prepare_output_path(output_dir)
    output.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(
        tempfile.mkdtemp(
            prefix=f".{output.name}.staging-",
            dir=output.parent,
        )
    )

    published = False
    try:
        _initialize_repository(staging)
        acquirer = _Acquirer(staging, token, request_json)
        acquirer.materialize_tree(expected_root_tree)
        acquirer.materialize_commit(expected_commit, expected_root_tree)
        _checkout_exact_commit(staging, expected_commit, expected_root_tree)

        verify_repository(
            staging,
            expected_objects=expected_objects,
            expected_head=expected_commit,
        )

        reject_symlink_path_or_ancestors(output, "TEI revision B source出力")
        if output.exists():
            raise ValueError(
                "TEI revision B source出力が取得中に作成されました。暗黙上書きしません: "
                f"{output}"
            )
        staging.rename(output)
        published = True

        verification = verify_repository(
            output,
            expected_objects=expected_objects,
            expected_head=expected_commit,
        )
        return {
            "schema": "soza.tei-revision-b-source-acquisition/v1",
            "result": "verified",
            "sourceAcquisition": "github-git-data-api-content-addressed",
            "repository": repository,
            "sourceCommit": expected_commit,
            "rootTree": expected_root_tree,
            "outputDirectory": str(output),
            "credentialSource": "environment",
            "objectAcquisition": acquirer.observation(),
            "canonicalSourceVerification": verification,
            "revisionBBuildPass": False,
            "providerPlanExecutionPass": False,
            "sozaAdapterCompatibilityPass": False,
            "issue000072Resolved": False,
            "qualityJudgement": "not_evaluated",
            "stopLine": STOP_LINE,
        }
    except Exception:
        if published:
            shutil.rmtree(output, ignore_errors=True)
        raise
    finally:
        if not published:
            shutil.rmtree(staging, ignore_errors=True)


def _token_from_environment() -> str:
    return os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "GitHub Git Data APIを取得経路としてexact TEI revision B sourceを新規directoryへ"
            "materializeし、取得bytesからGit object identityを再構成した後、canonical source verifierで"
            "HEAD/object/working-tree purityを確認します。"
        )
    )
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--report-output", type=Path)
    args = parser.parse_args()

    try:
        output = _prepare_output_path(args.output_dir)
        report = (
            _prepare_report_path(args.report_output, output)
            if args.report_output is not None
            else None
        )
        token = _token_from_environment()
        if not token:
            raise ValueError(
                "GITHUB_TOKENまたはGH_TOKENをenvironmentへ設定してください"
            )
        result = materialize_revision_b_source(output, token=token)
        rendered = json.dumps(
            result,
            ensure_ascii=False,
            sort_keys=True,
            indent=2,
        ) + "\n"
        if report is not None:
            report.parent.mkdir(parents=True, exist_ok=True)
            report.write_text(rendered, encoding="utf-8")
        print(rendered, end="")
        return 0
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        parser.exit(1, f"TEI revision B source acquisition failed: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
