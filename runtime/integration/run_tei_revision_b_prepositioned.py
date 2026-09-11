#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import tarfile
import tempfile
from pathlib import Path

import prepare_tei_fixed_reference_input as fixed_reference
import verify_tei_evidence_bundle as bundle_verifier
import verify_tei_execution_source_identity as source_identity
from runtime_path_safety import reject_symlink_path_or_ancestors

FIXED_RUN = "reference/order_rollout.durable-run.m0.21.start.json"
FIXED_WORKSPACE = "reference/workspace"
FIXED_PLUGIN_LOCK = "reference/workspace/.tei/plugin-lock.json"
FIXED_SOLUTION = "order_rollout"
FIXED_VERSION = "2026.8.27"
EXPECTED_GO_VERSION = "go1.23.2"
EXPECTED_GOOS = "linux"
EXPECTED_GOARCH = "amd64"
EXPECTED_GO_TARGET = f"{EXPECTED_GOOS}/{EXPECTED_GOARCH}"
MAX_STAGE_OUTPUT = 16 * 1024
SOZA_ROOT = Path(__file__).resolve().parents[2]
STOP_LINE = (
    "prepositioned exact-B bundle produced with exact-A reference input "
    "!= SEI Adapter compatibility verified != TEI version exchange PASS "
    "!= Operational Evidence"
)


class TEIEvidenceStageError(RuntimeError):
    def __init__(
        self,
        stage: str,
        message: str,
        *,
        command: list[str] | None = None,
        returncode: int | None = None,
        stdout: str = "",
        stderr: str = "",
    ) -> None:
        super().__init__(f"{stage}: {message}")
        self.stage = stage
        self.message = message
        self.command = command
        self.returncode = returncode
        self.stdout = stdout[-MAX_STAGE_OUTPUT:]
        self.stderr = stderr[-MAX_STAGE_OUTPUT:]

    def as_dict(self) -> dict[str, object]:
        value: dict[str, object] = {
            "stage": self.stage,
            "message": self.message,
        }
        if self.command is not None:
            value["command"] = self.command
        if self.returncode is not None:
            value["returnCode"] = self.returncode
        if self.stdout:
            value["stdoutTail"] = self.stdout
        if self.stderr:
            value["stderrTail"] = self.stderr
        return value


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _controlled_go_env() -> dict[str, str]:
    env = os.environ.copy()
    env["GOWORK"] = "off"
    env["GOENV"] = "off"
    env["GOTOOLCHAIN"] = "local"
    for key in (
        "GOFLAGS",
        "GOOS",
        "GOARCH",
        "GOAMD64",
        "GOEXPERIMENT",
        "CGO_ENABLED",
    ):
        env.pop(key, None)
    return env


def _ensure_linux_amd64() -> None:
    system = platform.system().lower()
    machine = platform.machine().lower()
    if system != "linux" or machine not in {"x86_64", "amd64"}:
        raise ValueError(
            "historical Linux/amd64 Evidence条件と異なる実行環境です: "
            f"system={system} machine={machine}"
        )


def _run(
    argv: list[str],
    *,
    cwd: Path,
    env: dict[str, str],
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        argv,
        cwd=cwd,
        env=env,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def _run_stage(
    stage: str,
    argv: list[str],
    *,
    cwd: Path,
    env: dict[str, str],
) -> subprocess.CompletedProcess[str]:
    try:
        result = _run(argv, cwd=cwd, env=env)
    except OSError as exc:
        raise TEIEvidenceStageError(stage, str(exc), command=argv) from exc
    if result.returncode != 0:
        raise TEIEvidenceStageError(
            stage,
            "external process returned non-zero status",
            command=argv,
            returncode=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
        )
    return result


def _verify_tei_go_toolchain(
    cwd: Path,
    *,
    env: dict[str, str] | None = None,
) -> dict[str, str]:
    controlled = _controlled_go_env() if env is None else env
    version_process = _run_stage(
        "tei_go_toolchain",
        ["go", "version"],
        cwd=cwd,
        env=controlled,
    )
    observed_version = version_process.stdout.strip()
    fields = observed_version.split()
    if (
        len(fields) < 4
        or fields[0:2] != ["go", "version"]
        or fields[2] != EXPECTED_GO_VERSION
        or fields[3] != EXPECTED_GO_TARGET
    ):
        raise TEIEvidenceStageError(
            "tei_go_toolchain",
            "historical EvidenceとGo toolchain identityが一致しません: "
            f"expected={EXPECTED_GO_VERSION} {EXPECTED_GO_TARGET} actual={observed_version}",
            command=["go", "version"],
            stdout=version_process.stdout,
            stderr=version_process.stderr,
        )

    target_process = _run_stage(
        "tei_go_toolchain",
        ["go", "env", "GOOS", "GOARCH"],
        cwd=cwd,
        env=controlled,
    )
    target_fields = [line.strip() for line in target_process.stdout.splitlines()]
    if target_fields != [EXPECTED_GOOS, EXPECTED_GOARCH]:
        observed_target = "/".join(target_fields) if target_fields else "<empty>"
        raise TEIEvidenceStageError(
            "tei_go_toolchain",
            "historical Evidenceとcontrolled Go build targetが一致しません: "
            f"expected={EXPECTED_GO_TARGET} actual={observed_target}",
            command=["go", "env", "GOOS", "GOARCH"],
            stdout=target_process.stdout,
            stderr=target_process.stderr,
        )

    return {
        "requiredVersion": EXPECTED_GO_VERSION,
        "observedVersion": observed_version,
        "requiredTarget": EXPECTED_GO_TARGET,
        "observedTarget": EXPECTED_GO_TARGET,
    }


def _copy_reference_inputs(reference_input_root: Path, bundle_root: Path) -> None:
    workspace = reference_input_root / FIXED_WORKSPACE
    run_file = reference_input_root / FIXED_RUN
    plugin_lock = reference_input_root / FIXED_PLUGIN_LOCK
    for path in (workspace, run_file, plugin_lock):
        if not path.exists():
            raise ValueError(f"fixed revision A reference inputがありません: {path}")

    reference_root = bundle_root / "reference"
    shutil.copytree(workspace, reference_root / "workspace")
    shutil.copy2(run_file, reference_root / run_file.name)


def _wrap_stage(stage: str, exc: Exception) -> TEIEvidenceStageError:
    if isinstance(exc, TEIEvidenceStageError):
        return exc
    return TEIEvidenceStageError(stage, str(exc))


def _is_within(candidate: Path, root: Path) -> bool:
    return candidate == root or root in candidate.parents


def _prepare_reference_inputs(
    reference_source_repo: Path | None,
    reference_evidence_bundle: Path | None,
) -> tuple[Path | None, Path | None]:
    if (reference_source_repo is None) == (reference_evidence_bundle is None):
        raise ValueError(
            "exact revision A fixed inputは--reference-source-repoまたは"
            "--reference-evidence-bundleのどちらか一方で指定してください"
        )
    if reference_source_repo is not None:
        return reference_source_repo.expanduser().resolve(strict=True), None

    assert reference_evidence_bundle is not None
    requested = reference_evidence_bundle.expanduser()
    reject_symlink_path_or_ancestors(
        requested,
        "TEI historical reference Evidence bundle",
    )
    resolved = requested.resolve(strict=True)
    if not resolved.is_file():
        raise ValueError(
            "TEI historical reference Evidence bundleがfileではありません: "
            f"{resolved}"
        )
    return None, resolved


def _prepare_output_archive(
    output_archive: Path,
    *,
    source_repo: Path,
    reference_source_repo: Path | None,
) -> Path:
    requested = output_archive.expanduser()
    reject_symlink_path_or_ancestors(requested, "TEI Evidence output archive")
    resolved = requested.resolve(strict=False)
    if resolved.exists():
        raise ValueError(
            "既存TEI Evidence archiveを無言で上書きしません: "
            f"{resolved}"
        )
    roots: list[tuple[str, Path]] = [
        ("revision B source checkout", source_repo),
        ("SEI repository", SOZA_ROOT),
    ]
    if reference_source_repo is not None:
        roots.insert(1, ("revision A reference checkout", reference_source_repo))
    for label, root in roots:
        if _is_within(resolved, root):
            raise ValueError(
                f"TEI Evidence output archiveを{label}配下には置けません: "
                f"output={resolved} root={root}"
            )
    return resolved


def _publish_bundle_no_overwrite(candidate: Path, output_archive: Path) -> None:
    reject_symlink_path_or_ancestors(output_archive, "TEI Evidence output archive")
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            dir=output_archive.parent,
            prefix=f".{output_archive.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temporary = Path(handle.name)
            with candidate.open("rb") as source:
                shutil.copyfileobj(source, handle)
            handle.flush()
            os.fsync(handle.fileno())

        reject_symlink_path_or_ancestors(output_archive, "TEI Evidence output archive")
        if os.path.lexists(output_archive):
            raise ValueError(
                "TEI Evidence output archiveがpublish前に作成されています。暗黙上書きしません: "
                f"{output_archive}"
            )
        try:
            os.link(temporary, output_archive)
        except FileExistsError as exc:
            raise ValueError(
                "TEI Evidence output archiveがpublish競合で作成されました。暗黙上書きしません: "
                f"{output_archive}"
            ) from exc
        temporary.unlink()
        temporary = None
    finally:
        if temporary is not None and temporary.exists() and not temporary.is_symlink():
            temporary.unlink()


def _reverify_execution_inputs_after_provider(
    source_repo: Path,
    reference_source_repo: Path | None,
) -> dict[str, object]:
    try:
        source_observation = source_identity.verify_repository(
            source_repo,
            expected_head=source_identity.REVISION_B,
        )
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        detail = ValueError(
            "Provider Plan実行後のrevision B source再検証に失敗しました: "
            f"{exc}"
        )
        raise _wrap_stage("revision_b_source_identity", detail) from exc

    reference_observation: dict[str, object] | None = None
    if reference_source_repo is not None:
        try:
            reference_observation = source_identity.verify_repository(
                reference_source_repo,
                expected_objects=source_identity.REVISION_A_REFERENCE_OBJECTS,
                expected_head=source_identity.REVISION_A,
            )
        except (OSError, ValueError, subprocess.SubprocessError) as exc:
            detail = ValueError(
                "Provider Plan実行後のrevision A fixed input再検証に失敗しました: "
                f"{exc}"
            )
            raise _wrap_stage("revision_a_fixed_reference_identity", detail) from exc

    return {
        "source": source_observation,
        "referenceInput": reference_observation,
    }


def produce_bundle(
    source_repo: Path,
    reference_source_repo: Path | None,
    output_archive: Path,
    *,
    reference_evidence_bundle: Path | None = None,
) -> dict[str, object]:
    source_repo = source_repo.expanduser().resolve(strict=True)
    reference_source_repo, reference_evidence_bundle = _prepare_reference_inputs(
        reference_source_repo,
        reference_evidence_bundle,
    )
    output_archive = _prepare_output_archive(
        output_archive,
        source_repo=source_repo,
        reference_source_repo=reference_source_repo,
    )
    output_archive.parent.mkdir(parents=True, exist_ok=True)

    try:
        source_observation = source_identity.verify_repository(
            source_repo,
            expected_head=source_identity.REVISION_B,
        )
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        raise _wrap_stage("revision_b_source_identity", exc) from exc

    with tempfile.TemporaryDirectory(prefix="soza-tei-b-") as tmp:
        temp_root = Path(tmp)
        if reference_source_repo is not None:
            try:
                verified_reference = source_identity.verify_repository(
                    reference_source_repo,
                    expected_objects=source_identity.REVISION_A_REFERENCE_OBJECTS,
                    expected_head=source_identity.REVISION_A,
                )
            except (OSError, ValueError, subprocess.SubprocessError) as exc:
                raise _wrap_stage("revision_a_fixed_reference_identity", exc) from exc
            reference_input_root = reference_source_repo
            reference_observation = {
                **verified_reference,
                "acquisitionMode": "git_checkout",
                "sourceCommit": source_identity.REVISION_A,
            }
        else:
            assert reference_evidence_bundle is not None
            try:
                materialized = fixed_reference.materialize_fixed_reference_input_bundle(
                    reference_evidence_bundle,
                    temp_root / "fixed-reference-input",
                )
            except (OSError, ValueError, tarfile.TarError) as exc:
                raise _wrap_stage("revision_a_fixed_reference_identity", exc) from exc
            reference_input_root = Path(str(materialized["materializedRoot"]))
            reference_observation = {
                key: value
                for key, value in materialized.items()
                if key != "materializedRoot"
            }

        try:
            _ensure_linux_amd64()
        except ValueError as exc:
            raise _wrap_stage("execution_platform", exc) from exc

        env = _controlled_go_env()
        go_toolchain = _verify_tei_go_toolchain(source_repo, env=env)
        go_version = go_toolchain["observedVersion"]

        bundle_root = temp_root / "tei-e3b-p2"
        binary = bundle_root / "bin" / "tei"
        binary.parent.mkdir(parents=True)

        _run_stage(
            "tei_cli_build",
            [
                "go",
                "build",
                "-trimpath",
                "-ldflags=-s -w",
                "-o",
                str(binary),
                "./cmd/tei",
            ],
            cwd=source_repo,
            env=env,
        )
        if not binary.is_file() or not os.access(binary, os.X_OK):
            raise TEIEvidenceStageError(
                "tei_cli_build",
                "build後のbin/teiがexecutable fileではありません",
            )

        provider = _run_stage(
            "deployment_provider_plan_execution",
            [
                str(binary),
                "deployment-provider-plan",
                "-workspace",
                str(reference_input_root / FIXED_WORKSPACE),
                "-run",
                str(reference_input_root / FIXED_RUN),
                "-solution",
                FIXED_SOLUTION,
                "-version",
                FIXED_VERSION,
                "-plugin-lock",
                str(reference_input_root / FIXED_PLUGIN_LOCK),
            ],
            cwd=source_repo,
            env=env,
        )
        provider_plan = bundle_root / "provider-plan.json"
        try:
            provider_plan.write_text(provider.stdout, encoding="utf-8")
        except OSError as exc:
            raise _wrap_stage("provider_plan_capture", exc) from exc

        try:
            bundle_verifier._parse_provider_plan(provider.stdout.encode("utf-8"))
        except ValueError as exc:
            raise _wrap_stage("provider_plan_validation", exc) from exc

        post_execution_identity = _reverify_execution_inputs_after_provider(
            source_repo,
            reference_source_repo,
        )

        try:
            _copy_reference_inputs(reference_input_root, bundle_root)
        except (OSError, ValueError) as exc:
            raise _wrap_stage("reference_input_packaging", exc) from exc

        metadata = {
            "schema": bundle_verifier.SCHEMA,
            "repository": bundle_verifier.REPOSITORY,
            "source_commit": source_identity.REVISION_B,
            "entry_point": bundle_verifier.ENTRY_POINT,
            "binary_sha256": _sha256(binary),
            "provider_plan_sha256": _sha256(provider_plan),
            "go_version": go_version,
            "reference_input_source_commit": source_identity.REVISION_A,
            "reference_input_acquisition_mode": reference_observation["acquisitionMode"],
            "reference_workspace_tree": source_identity.REVISION_A_REFERENCE_OBJECTS[FIXED_WORKSPACE],
            "reference_run_blob": source_identity.REVISION_A_REFERENCE_OBJECTS[FIXED_RUN],
            "reference_plugin_lock_blob": source_identity.REVISION_A_REFERENCE_OBJECTS[FIXED_PLUGIN_LOCK],
        }
        if reference_observation["acquisitionMode"] == "historical_evidence_bundle":
            metadata["reference_input_bundle_archive_sha256"] = reference_observation[
                "archiveSha256"
            ]
        try:
            (bundle_root / "metadata.json").write_text(
                json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        except OSError as exc:
            raise _wrap_stage("evidence_metadata_write", exc) from exc

        candidate = temp_root / "tei-e3b-p2-linux-amd64.tar.gz"
        try:
            with tarfile.open(candidate, "w:gz") as tar:
                for path in sorted(bundle_root.rglob("*")):
                    arcname = path.relative_to(bundle_root).as_posix()
                    tar.add(path, arcname=arcname, recursive=False)
        except (OSError, tarfile.TarError) as exc:
            raise _wrap_stage("evidence_bundle_packaging", exc) from exc

        try:
            verification = bundle_verifier.verify_bundle(
                candidate,
                expected_source_commit=source_identity.REVISION_B,
            )
        except (OSError, ValueError, tarfile.TarError) as exc:
            raise _wrap_stage("evidence_bundle_verification", exc) from exc

        try:
            _publish_bundle_no_overwrite(candidate, output_archive)
        except (OSError, ValueError) as exc:
            raise _wrap_stage("evidence_bundle_publish", exc) from exc

    return {
        "schema": "soza.tei-revision-b-prepositioned-run/v1",
        "result": "bundle_produced",
        "source": source_observation,
        "referenceInput": reference_observation,
        "postExecutionIdentity": post_execution_identity,
        "bundle": verification,
        "outputArchive": str(output_archive),
        "completedStages": [
            "revision_b_source_identity",
            "revision_a_fixed_reference_identity",
            "execution_platform",
            "tei_go_toolchain",
            "tei_cli_build",
            "deployment_provider_plan_execution",
            "provider_plan_capture",
            "provider_plan_validation",
            "reference_input_packaging",
            "evidence_metadata_write",
            "evidence_bundle_packaging",
            "evidence_bundle_verification",
            "evidence_bundle_publish",
        ],
        "qualityJudgement": "not_evaluated",
        "stopLine": STOP_LINE,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "prepositionedされたexact revision BのTEI checkoutをbuild sourceとして検証し、"
            "exact revision Aのfixed reference inputをGit checkoutまたは検証済みhistorical "
            "Evidence bundleから与えて、runtime revisionだけを交換した"
            "deployment-provider-plan Evidence bundleを生成します。"
        ),
        allow_abbrev=False,
    )
    parser.add_argument(
        "--source-repo",
        required=True,
        type=Path,
        help="exact revision BのTEI checkout。build sourceとしてのみ使用する。",
    )
    reference_group = parser.add_mutually_exclusive_group(required=True)
    reference_group.add_argument(
        "--reference-source-repo",
        type=Path,
        help="exact revision AのTEI checkout。historical fixed reference inputとしてのみ使用する。",
    )
    reference_group.add_argument(
        "--reference-evidence-bundle",
        type=Path,
        help=(
            "historical revision Aのverified TEI Evidence bundle。保存済みreference inputを"
            "Git object identityへ戻して検証した後にだけ使用する。"
        ),
    )
    parser.add_argument("--output-archive", required=True, type=Path)
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = produce_bundle(
            args.source_repo,
            args.reference_source_repo,
            args.output_archive,
            reference_evidence_bundle=args.reference_evidence_bundle,
        )
    except TEIEvidenceStageError as exc:
        print(
            "TEI revision B prepositioned run failed at "
            f"{exc.stage}: {exc.message}"
        )
        return 1
    except (OSError, ValueError, subprocess.SubprocessError, tarfile.TarError) as exc:
        print(f"TEI revision B prepositioned run failed before staged execution: {exc}")
        return 1

    if args.json:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    else:
        observation = result["bundle"]["observation"]
        reference = result["referenceInput"]
        reference_source = reference.get("sourceCommit", reference.get("head"))
        print("TEI revision B prepositioned run: bundle produced")
        print(f"- source commit: {observation['source_commit']}")
        print(f"- reference input source commit: {reference_source}")
        print(f"- reference input acquisition: {reference['acquisitionMode']}")
        print(f"- binary SHA-256: {observation['binary_sha256']}")
        print(f"- Provider Plan SHA-256: {observation['provider_plan_sha256']}")
        print(result["stopLine"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())