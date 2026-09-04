#!/usr/bin/env bash
set -euo pipefail

# GitHub Actionsに依存せず、同一のKJ Atlas / model artifact / Method inputで
# Ollama runtimeだけを0.32.13から0.32.14へ交換し、SOZAの履歴再構成境界を検証します。
# Linuxで直接実行するため、このfileはrepository上でもLFを維持します。
# 実験結果の意味はISSUE-000070を正とし、このscriptの成功を成果品質やE4へ昇格させません。
# strict Evidenceのsourceはverified runtime bundleだけを受け付けます。KJ Atlas checkoutを
# 起点にする場合はrun_runtime_version_exchange_strict.pyで固定commit objectからexportします。

SOZA_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd -P)"
KJ_ATLAS_COMMIT="4f28c13abe4176503c6fed863383a2d1db2299e9"
MODEL_NAME="qwen2.5:0.5b"
MODEL_SHA256="a8b0c51577010a279d933d14c2a8ab4b268079d44c5c8830c0a93900f1827c67"
RUNTIME_VERSION_A="0.32.13"
RUNTIME_VERSION_B="0.32.14"
RUNTIME_SHA256_A="0fd1dece38a1c6242e8013ce20b597345c5de072ae6b320160edb0e729ef1de1"
RUNTIME_SHA256_B="c620917a71e146ab3a7f893084f066069c4c65d144ef8379a91c3cbe8b27de8f"

KJ_ATLAS_BACKEND_BUNDLE="${SOZA_RUNTIME_EXCHANGE_KJ_ATLAS_BACKEND_BUNDLE:-}"
KJ_ATLAS_SOURCE_VERIFIER="${SOZA_ROOT}/runtime/integration/verify_kj_atlas_runtime_source.py"
RUNTIME_ARCHIVE_PREPARER="${SOZA_ROOT}/runtime/integration/prepare_runtime_version_exchange_archives.py"
MODEL_STORE_PREPARER="${SOZA_ROOT}/runtime/integration/prepare_runtime_version_exchange_model_store.py"
WORK_DIR="${SOZA_RUNTIME_EXCHANGE_WORK_DIR:-}"
EVIDENCE_DIR="${SOZA_RUNTIME_EXCHANGE_EVIDENCE_DIR:-}"
PREPOSITIONED_RUNTIME_ARCHIVE_A="${SOZA_RUNTIME_EXCHANGE_PREPOSITIONED_ARCHIVE_A:-}"
PREPOSITIONED_RUNTIME_ARCHIVE_B="${SOZA_RUNTIME_EXCHANGE_PREPOSITIONED_ARCHIVE_B:-}"
EXTERNAL_MODEL_STORE="${SOZA_RUNTIME_EXCHANGE_MODEL_DIR:-}"
KEEP_WORK="${SOZA_RUNTIME_EXCHANGE_KEEP_WORK:-0}"

usage() {
  cat <<'USAGE'
Usage: runtime/integration/run_runtime_version_exchange.sh [options]

Options:
  --kj-atlas-backend-bundle PATH   固定commit由来のverified backend source bundle。必須。
  --work-dir PATH                  新規に作成する一時作業ディレクトリ。既存pathは拒否する。
  --evidence-dir PATH              新規に作成するEvidence保存先。既存pathは拒否する。
  --runtime-a-archive PATH         事前配置したOllama 0.32.13 archiveを利用する。
  --runtime-b-archive PATH         事前配置したOllama 0.32.14 archiveを利用する。
  --model-dir PATH                 固定model artifactを保持済みのOllama model storageを利用する。
  --keep-work                      一時作業ディレクトリを削除しない。
  -h, --help                       この説明を表示する。

必要コマンド:
  git, python3, go, curl, zstd, tar, sha256sum, uname, mktemp, cp

現在の固定runtime artifactはLinux / amd64用です。
SOZAはcleanなGit checkoutである必要があります。
このlow-level harnessはverified KJ Atlas backend bundleだけを実行sourceとして受け付けます。
KJ Atlas checkoutを起点にする場合は、run_runtime_version_exchange_strict.pyを利用し、
固定commit objectからverified runtime bundleへ変換してから本harnessへ委譲してください。
work / Evidence / external model directoryをSOZAまたはKJ Atlas source配下には置けません。

runtime archiveを指定しない場合だけ、repository-localのarchive preparation helperを通して
Ollama公式GitHub Releaseから取得します。事前配置したarchiveも同じ固定SHA-256を必ず
検証します。--model-dirを指定しない場合は、runtime A/Bを起動する前にrepository-localの
model preparation helperで固定manifest / blobを検証したwork-local storeを一度だけ準備し、
両runtimeで同じstoreを利用します。runtime実行中の暗黙なmodel pullは行いません。

このscriptはGitHub Actions、runner ID、workflow run IDを実験成立条件にしません。
USAGE
}

while (($# > 0)); do
  case "$1" in
    --kj-atlas-backend-bundle)
      [[ $# -ge 2 ]] || { echo "--kj-atlas-backend-bundle requires PATH" >&2; exit 2; }
      KJ_ATLAS_BACKEND_BUNDLE="$2"
      shift 2
      ;;
    --work-dir)
      [[ $# -ge 2 ]] || { echo "--work-dir requires PATH" >&2; exit 2; }
      WORK_DIR="$2"
      shift 2
      ;;
    --evidence-dir)
      [[ $# -ge 2 ]] || { echo "--evidence-dir requires PATH" >&2; exit 2; }
      EVIDENCE_DIR="$2"
      shift 2
      ;;
    --runtime-a-archive)
      [[ $# -ge 2 ]] || { echo "--runtime-a-archive requires PATH" >&2; exit 2; }
      PREPOSITIONED_RUNTIME_ARCHIVE_A="$2"
      shift 2
      ;;
    --runtime-b-archive)
      [[ $# -ge 2 ]] || { echo "--runtime-b-archive requires PATH" >&2; exit 2; }
      PREPOSITIONED_RUNTIME_ARCHIVE_B="$2"
      shift 2
      ;;
    --model-dir)
      [[ $# -ge 2 ]] || { echo "--model-dir requires PATH" >&2; exit 2; }
      EXTERNAL_MODEL_STORE="$2"
      shift 2
      ;;
    --keep-work)
      KEEP_WORK=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

for command in git python3 go curl zstd tar sha256sum uname mktemp cp; do
  command -v "${command}" >/dev/null || {
    echo "Required command is missing: ${command}" >&2
    exit 1
  }
done

HOST_OS="$(uname -s)"
HOST_ARCH_RAW="$(uname -m)"
if [[ "${HOST_OS}" != "Linux" ]]; then
  echo "runtime version exchange harness currently requires Linux: actual=${HOST_OS}" >&2
  exit 1
fi
case "${HOST_ARCH_RAW}" in
  x86_64|amd64)
    HOST_ARCH="amd64"
    ;;
  *)
    echo "runtime version exchange harness currently requires amd64: actual=${HOST_ARCH_RAW}" >&2
    exit 1
    ;;
esac

canonical_path() {
  python3 - "$1" <<'PY'
import os
import sys
print(os.path.realpath(sys.argv[1]))
PY
}

is_within_path() {
  local candidate="$1"
  local parent="$2"
  [[ "${candidate}" == "${parent}" || "${candidate}" == "${parent}/"* ]]
}

require_clean_repository() {
  local label="$1"
  local path="$2"
  if ! git -C "${path}" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "${label} is not a Git working tree: ${path}" >&2
    exit 1
  fi
  local status
  status="$(git -C "${path}" status --porcelain --untracked-files=all)"
  if [[ -n "${status}" ]]; then
    echo "${label} working tree is not clean: ${path}" >&2
    printf '%s\n' "${status}" >&2
    exit 1
  fi
}

require_safe_output_path() {
  local label="$1"
  local candidate="$2"
  if is_within_path "${candidate}" "${SOZA_ROOT}"; then
    echo "${label} must not be inside the SOZA repository: ${candidate}" >&2
    exit 1
  fi
  if is_within_path "${candidate}" "${KJ_ATLAS_SOURCE_ROOT}"; then
    echo "${label} must not be inside the KJ Atlas source: ${candidate}" >&2
    exit 1
  fi
}

ensure_tcp_port_available() {
  local label="$1"
  local port="$2"
  LABEL="${label}" PORT="${port}" python3 - <<'PY'
import os
import socket

label = os.environ["LABEL"]
port = int(os.environ["PORT"])
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind(("127.0.0.1", port))
    except OSError as exc:
        raise SystemExit(f"{label} port {port} is not available: {exc}")
PY
}

require_clean_repository "SOZA" "${SOZA_ROOT}"
SOZA_COMMIT="$(git -C "${SOZA_ROOT}" rev-parse HEAD)"

if [[ -z "${KJ_ATLAS_BACKEND_BUNDLE}" ]]; then
  echo "verified KJ Atlas backend bundle is required; use --kj-atlas-backend-bundle PATH." >&2
  echo "When starting from a checkout, use run_runtime_version_exchange_strict.py so the pinned commit object is exported first." >&2
  exit 2
fi

KJ_ATLAS_BACKEND_BUNDLE="$(canonical_path "${KJ_ATLAS_BACKEND_BUNDLE}")"
if is_within_path "${KJ_ATLAS_BACKEND_BUNDLE}" "${SOZA_ROOT}"; then
  echo "KJ Atlas backend bundle must not be inside the SOZA repository: ${KJ_ATLAS_BACKEND_BUNDLE}" >&2
  exit 1
fi
[[ -d "${KJ_ATLAS_BACKEND_BUNDLE}" ]] || {
  echo "KJ Atlas backend bundle not found: ${KJ_ATLAS_BACKEND_BUNDLE}" >&2
  exit 1
}
python3 "${KJ_ATLAS_SOURCE_VERIFIER}" --backend-dir "${KJ_ATLAS_BACKEND_BUNDLE}" >/dev/null
KJ_ATLAS_SOURCE_MODE="verified-runtime-bundle"
KJ_ATLAS_SOURCE_ROOT="${KJ_ATLAS_BACKEND_BUNDLE}"
KJ_ATLAS_BACKEND_DIR=""
KJ_ATLAS_INSTALL_DIR=""
ACTUAL_KJ_COMMIT="${KJ_ATLAS_COMMIT}"

EXECUTION_ID="${SOZA_RUNTIME_EXCHANGE_EXECUTION_ID:-local-$(date -u +%Y%m%dT%H%M%SZ)-$$}"
if [[ ! "${EXECUTION_ID}" =~ ^[A-Za-z0-9._-]+$ ]]; then
  echo "SOZA_RUNTIME_EXCHANGE_EXECUTION_ID contains unsupported characters: ${EXECUTION_ID}" >&2
  exit 1
fi

TMP_ROOT="$(canonical_path "${TMPDIR:-/tmp}")"
require_safe_output_path "temporary root" "${TMP_ROOT}"

if [[ -z "${WORK_DIR}" ]]; then
  WORK_DIR="$(mktemp -d "${TMP_ROOT}/soza-runtime-version-exchange.XXXXXX")"
else
  WORK_DIR="$(canonical_path "${WORK_DIR}")"
  require_safe_output_path "work directory" "${WORK_DIR}"
  if [[ -e "${WORK_DIR}" ]]; then
    echo "work directory already exists; specify a new path: ${WORK_DIR}" >&2
    exit 1
  fi
  mkdir -p "${WORK_DIR}"
fi
WORK_DIR="$(canonical_path "${WORK_DIR}")"
require_safe_output_path "work directory" "${WORK_DIR}"

if [[ -z "${EVIDENCE_DIR}" ]]; then
  EVIDENCE_DIR="${TMP_ROOT}/soza-runtime-version-exchange-evidence-${EXECUTION_ID}"
fi
EVIDENCE_DIR="$(canonical_path "${EVIDENCE_DIR}")"
require_safe_output_path "Evidence directory" "${EVIDENCE_DIR}"
if [[ -e "${EVIDENCE_DIR}" ]]; then
  echo "Evidence directory already exists; specify a new path: ${EVIDENCE_DIR}" >&2
  exit 1
fi
mkdir -p "${EVIDENCE_DIR}"

KJ_ATLAS_SOURCE_IDENTITY_FILE="${WORK_DIR}/kj-atlas-source-identity.json"
KJ_ATLAS_BACKEND_DIR="${WORK_DIR}/kj-atlas-backend-execution"
KJ_ATLAS_INSTALL_DIR="${WORK_DIR}/kj-atlas-backend-install"
mkdir -p "${KJ_ATLAS_BACKEND_DIR}" "${KJ_ATLAS_INSTALL_DIR}"
cp -a "${KJ_ATLAS_SOURCE_ROOT}/." "${KJ_ATLAS_BACKEND_DIR}/"
cp -a "${KJ_ATLAS_SOURCE_ROOT}/." "${KJ_ATLAS_INSTALL_DIR}/"
python3 "${KJ_ATLAS_SOURCE_VERIFIER}" \
  --backend-dir "${KJ_ATLAS_BACKEND_DIR}" \
  --output "${KJ_ATLAS_SOURCE_IDENTITY_FILE}" >/dev/null
python3 "${KJ_ATLAS_SOURCE_VERIFIER}" --backend-dir "${KJ_ATLAS_INSTALL_DIR}" >/dev/null

if [[ -n "${PREPOSITIONED_RUNTIME_ARCHIVE_A}" ]]; then
  PREPOSITIONED_RUNTIME_ARCHIVE_A="$(canonical_path "${PREPOSITIONED_RUNTIME_ARCHIVE_A}")"
  [[ -f "${PREPOSITIONED_RUNTIME_ARCHIVE_A}" ]] || {
    echo "prepositioned runtime A archive is not a file: ${PREPOSITIONED_RUNTIME_ARCHIVE_A}" >&2
    exit 1
  }
fi
if [[ -n "${PREPOSITIONED_RUNTIME_ARCHIVE_B}" ]]; then
  PREPOSITIONED_RUNTIME_ARCHIVE_B="$(canonical_path "${PREPOSITIONED_RUNTIME_ARCHIVE_B}")"
  [[ -f "${PREPOSITIONED_RUNTIME_ARCHIVE_B}" ]] || {
    echo "prepositioned runtime B archive is not a file: ${PREPOSITIONED_RUNTIME_ARCHIVE_B}" >&2
    exit 1
  }
fi

VENV_DIR="${WORK_DIR}/venv"
MODEL_STORE_PREPARATION_FILE="${WORK_DIR}/runtime-exchange-model-store-preparation.json"
MODEL_STORE_NEEDS_PREPARATION=0
if [[ -n "${EXTERNAL_MODEL_STORE}" ]]; then
  EXTERNAL_MODEL_STORE="$(canonical_path "${EXTERNAL_MODEL_STORE}")"
  require_safe_output_path "external model directory" "${EXTERNAL_MODEL_STORE}"
  [[ -d "${EXTERNAL_MODEL_STORE}" ]] || {
    echo "external model directory does not exist: ${EXTERNAL_MODEL_STORE}" >&2
    exit 1
  }
  MODEL_STORE="${EXTERNAL_MODEL_STORE}"
  MODEL_STORE_MODE="prepositioned"
else
  MODEL_STORE="${WORK_DIR}/ollama-models"
  MODEL_STORE_MODE="work-local"
  MODEL_STORE_NEEDS_PREPARATION=1
fi

REQUEST_FILE="${WORK_DIR}/kj-atlas-runtime-exchange-request.json"
IDENTITY_FILE="${WORK_DIR}/runtime-exchange-identity.json"
RUNTIME_ROOT_A="${WORK_DIR}/ollama-runtime-a"
RUNTIME_ROOT_B="${WORK_DIR}/ollama-runtime-b"
RUNTIME_ARCHIVE_PREPARATION_DIR="${WORK_DIR}/runtime-archives"
RUNTIME_ARCHIVE_A="${PREPOSITIONED_RUNTIME_ARCHIVE_A:-}"
RUNTIME_ARCHIVE_B="${PREPOSITIONED_RUNTIME_ARCHIVE_B:-}"
RUNTIME_ACQUISITION_A="downloaded"
RUNTIME_ACQUISITION_B="downloaded"
[[ -n "${PREPOSITIONED_RUNTIME_ARCHIVE_A}" ]] && RUNTIME_ACQUISITION_A="prepositioned"
[[ -n "${PREPOSITIONED_RUNTIME_ARCHIVE_B}" ]] && RUNTIME_ACQUISITION_B="prepositioned"

OLLAMA_PID=""
ADAPTER_PID=""
KJ_PID=""

cleanup_processes() {
  local pid
  for pid in "${KJ_PID}" "${ADAPTER_PID}" "${OLLAMA_PID}"; do
    if [[ -n "${pid}" ]]; then
      kill "${pid}" 2>/dev/null || true
      wait "${pid}" 2>/dev/null || true
    fi
  done
  KJ_PID=""
  ADAPTER_PID=""
  OLLAMA_PID=""
}

prepare_downloaded_runtime_archive() {
  local label="$1"
  local result_file="${WORK_DIR}/runtime-exchange-${label}-archive-preparation.json"

  python3 "${RUNTIME_ARCHIVE_PREPARER}" \
    --output-dir "${RUNTIME_ARCHIVE_PREPARATION_DIR}" \
    --runtime "${label}" \
    --json >"${result_file}"

  RESULT_FILE="${result_file}" LABEL="${label}" python3 - <<'PY'
import json
import os
from pathlib import Path

payload = json.loads(Path(os.environ["RESULT_FILE"]).read_text(encoding="utf-8"))
archives = payload.get("archives")
if payload.get("result") != "ok" or not isinstance(archives, list) or len(archives) != 1:
    raise SystemExit(f"runtime archive preparation did not return one successful artifact: {payload!r}")
archive = archives[0]
if archive.get("label") != os.environ["LABEL"] or archive.get("status") != "ok":
    raise SystemExit(f"runtime archive preparation result is inconsistent: {archive!r}")
path = archive.get("path")
if not isinstance(path, str) or not path:
    raise SystemExit(f"runtime archive preparation did not return a path: {archive!r}")
print(path)
PY
}

preserve_evidence() {
  local preserve_status=0
  mkdir -p "${EVIDENCE_DIR}" || return 1
  local path
  for path in \
    "${IDENTITY_FILE}" \
    "${KJ_ATLAS_SOURCE_IDENTITY_FILE}" \
    "${REQUEST_FILE}" \
    "${WORK_DIR}/runtime-exchange-a-archive-preparation.json" \
    "${WORK_DIR}/runtime-exchange-b-archive-preparation.json" \
    "${MODEL_STORE_PREPARATION_FILE}" \
    "${WORK_DIR}/runtime-exchange-a-version.txt" \
    "${WORK_DIR}/runtime-exchange-b-version.txt" \
    "${WORK_DIR}/runtime-exchange-a-archive-sha256.txt" \
    "${WORK_DIR}/runtime-exchange-b-archive-sha256.txt" \
    "${WORK_DIR}/runtime-exchange-a-model-id.txt" \
    "${WORK_DIR}/runtime-exchange-b-model-id.txt" \
    "${WORK_DIR}/runtime-exchange-a-tags.json" \
    "${WORK_DIR}/runtime-exchange-b-tags.json" \
    "${WORK_DIR}/runtime-exchange-a-evidence.json" \
    "${WORK_DIR}/runtime-exchange-b-evidence.json" \
    "${WORK_DIR}/runtime-exchange-a-result.json" \
    "${WORK_DIR}/runtime-exchange-b-result.json" \
    "${WORK_DIR}/runtime-exchange-a-adapter.log" \
    "${WORK_DIR}/runtime-exchange-b-adapter.log" \
    "${WORK_DIR}/runtime-exchange-a-kj.log" \
    "${WORK_DIR}/runtime-exchange-b-kj.log" \
    "${WORK_DIR}/runtime-exchange-a-ollama.log" \
    "${WORK_DIR}/runtime-exchange-b-ollama.log"; do
    if [[ -f "${path}" && "$(dirname "${path}")" != "${EVIDENCE_DIR}" ]]; then
      cp -f "${path}" "${EVIDENCE_DIR}/" || preserve_status=1
    fi
  done
  return "${preserve_status}"
}

finish() {
  local status=$?
  set +e
  cleanup_processes
  preserve_evidence
  local preserve_status=$?

  if [[ "${KEEP_WORK}" != "1" ]]; then
    if is_within_path "${EVIDENCE_DIR}" "${WORK_DIR}"; then
      echo "Evidence directory is inside the work directory; retaining work directory: ${WORK_DIR}" >&2
    else
      rm -rf -- "${WORK_DIR}"
    fi
  fi

  if [[ "${status}" == "0" && "${preserve_status}" != "0" ]]; then
    status="${preserve_status}"
  fi

  echo "Evidence directory: ${EVIDENCE_DIR}"
  if [[ "${KEEP_WORK}" == "1" ]]; then
    echo "Work directory: ${WORK_DIR}"
  fi

  trap - EXIT
  exit "${status}"
}
trap finish EXIT

if [[ "${RUNTIME_ACQUISITION_A}" == "downloaded" ]]; then
  RUNTIME_ARCHIVE_A="$(prepare_downloaded_runtime_archive a)"
fi
if [[ "${RUNTIME_ACQUISITION_B}" == "downloaded" ]]; then
  RUNTIME_ARCHIVE_B="$(prepare_downloaded_runtime_archive b)"
fi
if [[ "${MODEL_STORE_NEEDS_PREPARATION}" == "1" ]]; then
  MODEL_STORE_PREPARATION_JSON="$(
    python3 "${MODEL_STORE_PREPARER}" --target-dir "${MODEL_STORE}"
  )"
  printf '%s\n' "${MODEL_STORE_PREPARATION_JSON}" >"${MODEL_STORE_PREPARATION_FILE}"
fi

SOZA_COMMIT="${SOZA_COMMIT}" \
KJ_ATLAS_COMMIT="${ACTUAL_KJ_COMMIT}" \
KJ_ATLAS_SOURCE_IDENTITY_FILE="${KJ_ATLAS_SOURCE_IDENTITY_FILE}" \
EXECUTION_ID="${EXECUTION_ID}" \
IDENTITY_FILE="${IDENTITY_FILE}" \
RUNTIME_VERSION_A="${RUNTIME_VERSION_A}" \
RUNTIME_VERSION_B="${RUNTIME_VERSION_B}" \
RUNTIME_SHA256_A="${RUNTIME_SHA256_A}" \
RUNTIME_SHA256_B="${RUNTIME_SHA256_B}" \
RUNTIME_ACQUISITION_A="${RUNTIME_ACQUISITION_A}" \
RUNTIME_ACQUISITION_B="${RUNTIME_ACQUISITION_B}" \
MODEL_NAME="${MODEL_NAME}" \
MODEL_SHA256="${MODEL_SHA256}" \
MODEL_STORE_MODE="${MODEL_STORE_MODE}" \
HOST_OS="${HOST_OS}" \
HOST_ARCH="${HOST_ARCH}" \
python3 - <<'PY'
import json
import os
from pathlib import Path

method_source = json.loads(
    Path(os.environ["KJ_ATLAS_SOURCE_IDENTITY_FILE"]).read_text(encoding="utf-8")
)
payload = {
    "schema": "soza.runtime-version-exchange-evidence-identity/v1",
    "executionId": os.environ["EXECUTION_ID"],
    "executionSurface": "repository-local-harness",
    "repositoryCommit": os.environ["SOZA_COMMIT"],
    "methodSourceCommit": os.environ["KJ_ATLAS_COMMIT"],
    "methodSource": method_source,
    "executionHost": {
        "os": os.environ["HOST_OS"].lower(),
        "arch": os.environ["HOST_ARCH"],
    },
    "runtimeA": {
        "name": "ollama",
        "version": os.environ["RUNTIME_VERSION_A"],
        "archiveSha256": os.environ["RUNTIME_SHA256_A"],
        "archiveAcquisition": os.environ["RUNTIME_ACQUISITION_A"],
    },
    "runtimeB": {
        "name": "ollama",
        "version": os.environ["RUNTIME_VERSION_B"],
        "archiveSha256": os.environ["RUNTIME_SHA256_B"],
        "archiveAcquisition": os.environ["RUNTIME_ACQUISITION_B"],
    },
    "model": {
        "name": os.environ["MODEL_NAME"],
        "expectedDigest": os.environ["MODEL_SHA256"],
        "storageMode": os.environ["MODEL_STORE_MODE"],
    },
    "qualityJudgement": "not_evaluated",
}
Path(os.environ["IDENTITY_FILE"]).write_text(
    json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
    encoding="utf-8",
)
PY

python3 -m venv "${VENV_DIR}"
"${VENV_DIR}/bin/python" -m pip install --disable-pip-version-check "${KJ_ATLAS_INSTALL_DIR}"

acquire_runtime() {
  local label="$1"
  local expected_sha="$2"
  local archive="$3"
  local root="$4"
  local digest_file="${WORK_DIR}/runtime-exchange-${label}-archive-sha256.txt"

  mkdir -p "${root}"
  [[ -n "${archive}" ]] || {
    echo "runtime ${label} archive path is empty after preparation" >&2
    return 1
  }

  local actual_sha remainder
  read -r actual_sha remainder < <(sha256sum "${archive}")
  printf '%s\n' "${actual_sha}" >"${digest_file}"
  if [[ "${actual_sha}" != "${expected_sha}" ]]; then
    echo "runtime ${label} archive digest mismatch: actual=${actual_sha} expected=${expected_sha}" >&2
    return 1
  fi

  zstd -dc "${archive}" | tar -xf - -C "${root}"
  test -x "${root}/bin/ollama"
}

acquire_runtime a "${RUNTIME_SHA256_A}" "${RUNTIME_ARCHIVE_A}" "${RUNTIME_ROOT_A}"
acquire_runtime b "${RUNTIME_SHA256_B}" "${RUNTIME_ARCHIVE_B}" "${RUNTIME_ROOT_B}"

cat >"${REQUEST_FILE}" <<'JSON'
{
  "cards": [
    {"id":"c-remote-time","text":"在宅勤務では通勤に使う時間を減らせる","textReviewed":true},
    {"id":"c-remote-load","text":"在宅勤務では移動による負担を減らせる","textReviewed":true},
    {"id":"c-held","text":"人事評価制度の見直しはまだ着手していない","textReviewed":true}
  ],
  "doc": {
    "version": 1,
    "id": "soza-e3b-runtime-exchange",
    "createdAt": "2026-09-02T00:00:00Z",
    "updatedAt": "2026-09-02T00:00:00Z",
    "transform": {"panX":0,"panY":0,"zoom":1},
    "cards": [
      {"id":"c-remote-time","text":"在宅勤務では通勤に使う時間を減らせる","x":0,"y":0,"textReviewed":true},
      {"id":"c-remote-load","text":"在宅勤務では移動による負担を減らせる","x":40,"y":0,"textReviewed":true},
      {"id":"c-held","text":"人事評価制度の見直しはまだ着手していない","x":80,"y":0,"textReviewed":true,"holdState":"held"}
    ],
    "edges": [],
    "islands": [],
    "evidenceLinks": []
  }
}
JSON

export OLLAMA_HOST="127.0.0.1:11434"
export OLLAMA_MODELS="${MODEL_STORE}"
export SOZA_E3B_RUNTIME_EXCHANGE_MODEL_SHA256="${MODEL_SHA256}"

model_store_has_pinned_artifact() {
  local tags="$1"
  TAGS="${tags}" MODEL_NAME="${MODEL_NAME}" MODEL_SHA256="${MODEL_SHA256}" \
    "${VENV_DIR}/bin/python" - <<'PY'
import json
import os
from pathlib import Path

payload = json.loads(Path(os.environ["TAGS"]).read_text(encoding="utf-8"))
model = next((item for item in payload.get("models", []) if item.get("name") == os.environ["MODEL_NAME"]), None)
raise SystemExit(0 if model and model.get("digest") == os.environ["MODEL_SHA256"] else 1)
PY
}

run_probe() {
  local label="$1"
  local version="$2"
  local runtime_root="$3"
  local ollama="${runtime_root}/bin/ollama"
  local database="${WORK_DIR}/kj-atlas-runtime-exchange-${label}.db"
  local result="${WORK_DIR}/runtime-exchange-${label}-result.json"
  local evidence="${WORK_DIR}/runtime-exchange-${label}-evidence.json"
  local tags="${WORK_DIR}/runtime-exchange-${label}-tags.json"
  local version_log="${WORK_DIR}/runtime-exchange-${label}-version.txt"
  local ollama_log="${WORK_DIR}/runtime-exchange-${label}-ollama.log"
  local adapter_log="${WORK_DIR}/runtime-exchange-${label}-adapter.log"
  local kj_log="${WORK_DIR}/runtime-exchange-${label}-kj.log"

  cleanup_processes
  ensure_tcp_port_available "Ollama" 11434
  ensure_tcp_port_available "SOZA model adapter" 8001
  ensure_tcp_port_available "KJ Atlas" 8101

  echo "=== Ollama ${version}: verify pinned runtime artifact ==="
  "${ollama}" --version 2>&1 | tee "${version_log}"
  local escaped_version="${version//./\.}"
  grep -Eq "(^|[^0-9])${escaped_version}([^0-9]|$)" "${version_log}"

  "${ollama}" serve >"${ollama_log}" 2>&1 &
  OLLAMA_PID=$!
  for attempt in $(seq 1 60); do
    if ! kill -0 "${OLLAMA_PID}" 2>/dev/null; then
      echo "Ollama ${version} exited before becoming ready" >&2
      cat "${ollama_log}" >&2 || true
      return 1
    fi
    if curl --fail --silent http://127.0.0.1:11434/api/tags >/dev/null; then
      if kill -0 "${OLLAMA_PID}" 2>/dev/null; then
        break
      fi
    fi
    if [[ "${attempt}" == "60" ]]; then
      echo "Ollama ${version} did not become ready" >&2
      cat "${ollama_log}" >&2 || true
      return 1
    fi
    sleep 0.5
  done

  curl --fail --silent http://127.0.0.1:11434/api/tags >"${tags}"
  if ! model_store_has_pinned_artifact "${tags}"; then
    echo "${MODEL_STORE_MODE} model directory does not contain the pinned artifact: ${MODEL_SHA256}" >&2
    return 1
  fi

  LABEL="${label}" TAGS="${tags}" MODEL_NAME="${MODEL_NAME}" MODEL_SHA256="${MODEL_SHA256}" WORK_DIR="${WORK_DIR}" \
    "${VENV_DIR}/bin/python" - <<'PY'
import json
import os
from pathlib import Path

payload = json.loads(Path(os.environ["TAGS"]).read_text(encoding="utf-8"))
model_name = os.environ["MODEL_NAME"]
model = next((item for item in payload.get("models", []) if item.get("name") == model_name), None)
assert model is not None, payload
digest = model.get("digest")
assert isinstance(digest, str) and len(digest) == 64, model
expected = os.environ["MODEL_SHA256"]
if digest != expected:
    raise SystemExit(f"pinned model artifact changed: actual={digest}, expected={expected}")
Path(os.environ["WORK_DIR"], f"runtime-exchange-{os.environ['LABEL']}-model-id.txt").write_text(
    digest + "\n", encoding="utf-8"
)
print(json.dumps({"model": model_name, "digest": digest}, sort_keys=True))
PY

  (
    cd "${KJ_ATLAS_BACKEND_DIR}"
    KJ_ATLAS_DATABASE_URL="sqlite:///${database}" \
    PYTHONPATH="${KJ_ATLAS_BACKEND_DIR}/src" \
      "${VENV_DIR}/bin/alembic" upgrade head
  )

  SOZA_M1B_MODEL="${MODEL_NAME}" \
  SOZA_M1B_MODEL_EVIDENCE="${evidence}" \
    "${VENV_DIR}/bin/python" "${SOZA_ROOT}/runtime/integration/e3b_m1b_ollama_adapter.py" \
      --host 127.0.0.1 --port 8001 >"${adapter_log}" 2>&1 &
  ADAPTER_PID=$!

  KJ_ATLAS_DATABASE_URL="sqlite:///${database}" \
  KJ_ATLAS_RUNTIME_PROFILE=local-dev \
  KJ_ATLAS_LLM_PROVIDER=local \
  KJ_ATLAS_LOCAL_LLM_BASE_URL=http://127.0.0.1:8001 \
  KJ_ATLAS_LOCAL_LLM_MODEL="${MODEL_NAME}" \
  KJ_ATLAS_LLM_FALLBACK_TO_NONE=false \
  PYTHONPATH="${KJ_ATLAS_BACKEND_DIR}/src" \
    "${VENV_DIR}/bin/python" -m uvicorn kj_atlas_api.main:app --host 127.0.0.1 --port 8101 \
      >"${kj_log}" 2>&1 &
  KJ_PID=$!

  for attempt in $(seq 1 100); do
    if ! kill -0 "${ADAPTER_PID}" 2>/dev/null; then
      echo "runtime ${label} model adapter exited before becoming ready" >&2
      cat "${adapter_log}" >&2 || true
      return 1
    fi
    if ! kill -0 "${KJ_PID}" 2>/dev/null; then
      echo "runtime ${label} KJ Atlas exited before becoming ready" >&2
      cat "${kj_log}" >&2 || true
      return 1
    fi
    if curl --fail --silent http://127.0.0.1:8001/ >/dev/null \
      && curl --fail --silent http://127.0.0.1:8101/healthz >/dev/null; then
      if kill -0 "${ADAPTER_PID}" 2>/dev/null && kill -0 "${KJ_PID}" 2>/dev/null; then
        break
      fi
    fi
    if [[ "${attempt}" == "100" ]]; then
      echo "runtime ${label} Method processes did not become ready" >&2
      cat "${adapter_log}" >&2 || true
      cat "${kj_log}" >&2 || true
      return 1
    fi
    sleep 0.25
  done

  curl --fail-with-body --silent --show-error \
    -H 'Content-Type: application/json' \
    --data @"${REQUEST_FILE}" \
    http://127.0.0.1:8101/ai/suggest-card-groups \
    >"${result}"

  RESULT="${result}" EVIDENCE="${evidence}" MODEL_NAME="${MODEL_NAME}" \
    "${VENV_DIR}/bin/python" - <<'PY'
import json
import os
from pathlib import Path

result = json.loads(Path(os.environ["RESULT"]).read_text(encoding="utf-8"))
evidence = json.loads(Path(os.environ["EVIDENCE"]).read_text(encoding="utf-8"))
assert isinstance(result.get("groups"), list) and result["groups"], result
assert result.get("excludedCardIds") == ["c-held"], result
assert result.get("truncated") is False, result
assert evidence.get("model") == os.environ["MODEL_NAME"], evidence
assert evidence.get("task") == "suggest_card_groups", evidence
assert evidence.get("ollama_done") is True, evidence
assert isinstance(evidence.get("prompt_eval_count"), int) and evidence["prompt_eval_count"] > 0, evidence
assert isinstance(evidence.get("eval_count"), int) and evidence["eval_count"] > 0, evidence
print(json.dumps({"result": result, "evidence": evidence}, ensure_ascii=False, sort_keys=True))
PY

  cleanup_processes
  sleep 1
}

run_probe a "${RUNTIME_VERSION_A}" "${RUNTIME_ROOT_A}"
run_probe b "${RUNTIME_VERSION_B}" "${RUNTIME_ROOT_B}"

MODEL_ID_A="$(tr -d '\r\n' <"${WORK_DIR}/runtime-exchange-a-model-id.txt")"
MODEL_ID_B="$(tr -d '\r\n' <"${WORK_DIR}/runtime-exchange-b-model-id.txt")"
if [[ "${MODEL_ID_A}" != "${MODEL_SHA256}" || "${MODEL_ID_B}" != "${MODEL_SHA256}" ]]; then
  echo "pinned model artifact changed: A=${MODEL_ID_A} B=${MODEL_ID_B} expected=${MODEL_SHA256}" >&2
  exit 1
fi
if [[ "${MODEL_ID_A}" != "${MODEL_ID_B}" ]]; then
  echo "model artifact changed across runtimes: A=${MODEL_ID_A} B=${MODEL_ID_B}" >&2
  exit 1
fi

WORK_DIR="${WORK_DIR}" "${VENV_DIR}/bin/python" - <<'PY'
import json
import os
from pathlib import Path

work = Path(os.environ["WORK_DIR"])
a = json.loads((work / "runtime-exchange-a-evidence.json").read_text(encoding="utf-8"))
b = json.loads((work / "runtime-exchange-b-evidence.json").read_text(encoding="utf-8"))
if a.get("prompt_sha256") != b.get("prompt_sha256"):
    raise SystemExit(
        f"model prompt changed across runtimes: A={a.get('prompt_sha256')} B={b.get('prompt_sha256')}"
    )
print(json.dumps({"promptSHA256": a.get("prompt_sha256")}, sort_keys=True))
PY

(
  cd "${SOZA_ROOT}/runtime/go"
  env -u SOZA_E3B_RUNTIME_EXCHANGE_LIVE go test ./livemethodintegration -count=1
)

export SOZA_E3B_RUNTIME_EXCHANGE_LIVE=1
export SOZA_E3B_RUNTIME_EXCHANGE_KJ_ATLAS_SOURCE_MODE="${KJ_ATLAS_SOURCE_MODE}"
export SOZA_E3B_RUNTIME_EXCHANGE_KJ_ATLAS_BACKEND_DIR="${KJ_ATLAS_BACKEND_DIR}"
export SOZA_E3B_RUNTIME_EXCHANGE_KJ_ATLAS_SOURCE_VERIFIER="${KJ_ATLAS_SOURCE_VERIFIER}"
export SOZA_E3B_RUNTIME_EXCHANGE_RUNTIME_VERSION_A="${RUNTIME_VERSION_A}"
export SOZA_E3B_RUNTIME_EXCHANGE_RUNTIME_VERSION_B="${RUNTIME_VERSION_B}"
export SOZA_E3B_RUNTIME_EXCHANGE_MODEL_ID_A="${MODEL_ID_A}"
export SOZA_E3B_RUNTIME_EXCHANGE_MODEL_ID_B="${MODEL_ID_B}"
export SOZA_E3B_RUNTIME_EXCHANGE_RESULT_A="${WORK_DIR}/runtime-exchange-a-result.json"
export SOZA_E3B_RUNTIME_EXCHANGE_RESULT_B="${WORK_DIR}/runtime-exchange-b-result.json"
export SOZA_E3B_RUNTIME_EXCHANGE_EVIDENCE_A="${WORK_DIR}/runtime-exchange-a-evidence.json"
export SOZA_E3B_RUNTIME_EXCHANGE_EVIDENCE_B="${WORK_DIR}/runtime-exchange-b-evidence.json"
export SOZA_E3B_RUNTIME_EXCHANGE_ARCHIVE_A="${RUNTIME_ARCHIVE_A}"
export SOZA_E3B_RUNTIME_EXCHANGE_ARCHIVE_B="${RUNTIME_ARCHIVE_B}"
export SOZA_E3B_RUNTIME_EXCHANGE_VERSION_LOG_A="${WORK_DIR}/runtime-exchange-a-version.txt"
export SOZA_E3B_RUNTIME_EXCHANGE_VERSION_LOG_B="${WORK_DIR}/runtime-exchange-b-version.txt"

(
  cd "${SOZA_ROOT}/runtime/go"
  go test ./livemethodintegration \
    -run '^TestLiveKJAtlasRuntimeVersionExchangePreservesHistoricalApplication$' \
    -count=1 -v
)

echo "Runtime version exchange probe completed successfully."
