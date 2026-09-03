#!/usr/bin/env bash
set -euo pipefail

# GitHub Actionsに依存せず、同一のKJ Atlas / model artifact / Method inputで
# Ollama runtimeだけを0.32.13から0.32.14へ交換し、SOZAの履歴再構成境界を検証します。
# 実験結果の意味はISSUE-000070を正とし、このscriptの成功を成果品質やE4へ昇格させません。

SOZA_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
KJ_ATLAS_COMMIT="4f28c13abe4176503c6fed863383a2d1db2299e9"
MODEL_NAME="qwen2.5:0.5b"
MODEL_SHA256="a8b0c51577010a279d933d14c2a8ab4b268079d44c5c8830c0a93900f1827c67"
RUNTIME_VERSION_A="0.32.13"
RUNTIME_VERSION_B="0.32.14"
RUNTIME_SHA256_A="0fd1dece38a1c6242e8013ce20b597345c5de072ae6b320160edb0e729ef1de1"
RUNTIME_SHA256_B="c620917a71e146ab3a7f893084f066069c4c65d144ef8379a91c3cbe8b27de8f"

KJ_ATLAS_DIR="${SOZA_RUNTIME_EXCHANGE_KJ_ATLAS_DIR:-${SOZA_ROOT}/_external/kj-atlas}"
WORK_DIR="${SOZA_RUNTIME_EXCHANGE_WORK_DIR:-}"
EVIDENCE_DIR="${SOZA_RUNTIME_EXCHANGE_EVIDENCE_DIR:-}"
KEEP_WORK="${SOZA_RUNTIME_EXCHANGE_KEEP_WORK:-0}"

usage() {
  cat <<'USAGE'
Usage: runtime/integration/run_runtime_version_exchange.sh [options]

Options:
  --kj-atlas-dir PATH   固定KJ Atlas checkoutの場所。既定は _external/kj-atlas。
  --work-dir PATH       一時作業ディレクトリ。未指定時はmktempで作成する。
  --evidence-dir PATH   Evidence保存先。未指定時は/tmp配下に作成する。
  --keep-work           一時作業ディレクトリを削除しない。
  -h, --help            この説明を表示する。

必要コマンド:
  git, python3, go, curl, zstd, tar, sha256sum

SOZAとKJ AtlasはcleanなGit checkoutである必要があります。
KJ Atlas checkoutのHEADは固定commitと一致している必要があります。
work / Evidence directoryをSOZAまたはKJ Atlas repository配下には置けません。
このscriptはGitHub Actions、runner ID、workflow run IDを実験成立条件にしません。
USAGE
}

while (($# > 0)); do
  case "$1" in
    --kj-atlas-dir)
      KJ_ATLAS_DIR="$2"
      shift 2
      ;;
    --work-dir)
      WORK_DIR="$2"
      shift 2
      ;;
    --evidence-dir)
      EVIDENCE_DIR="$2"
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

for command in git python3 go curl zstd tar sha256sum; do
  command -v "${command}" >/dev/null || {
    echo "Required command is missing: ${command}" >&2
    exit 1
  }
done

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

if [[ ! -d "${KJ_ATLAS_DIR}/.git" ]]; then
  echo "KJ Atlas checkout not found: ${KJ_ATLAS_DIR}" >&2
  echo "Clone hat47x/kj-atlas and checkout ${KJ_ATLAS_COMMIT}, or pass --kj-atlas-dir." >&2
  exit 1
fi
KJ_ATLAS_DIR="$(canonical_path "${KJ_ATLAS_DIR}")"

require_clean_repository "SOZA" "${SOZA_ROOT}"
require_clean_repository "KJ Atlas" "${KJ_ATLAS_DIR}"

ACTUAL_KJ_COMMIT="$(git -C "${KJ_ATLAS_DIR}" rev-parse HEAD)"
if [[ "${ACTUAL_KJ_COMMIT}" != "${KJ_ATLAS_COMMIT}" ]]; then
  echo "KJ Atlas commit mismatch: actual=${ACTUAL_KJ_COMMIT} expected=${KJ_ATLAS_COMMIT}" >&2
  exit 1
fi
SOZA_COMMIT="$(git -C "${SOZA_ROOT}" rev-parse HEAD)"

if [[ -z "${WORK_DIR}" ]]; then
  WORK_DIR="$(mktemp -d "${TMPDIR:-/tmp}/soza-runtime-version-exchange.XXXXXX")"
else
  mkdir -p "${WORK_DIR}"
  WORK_DIR="$(canonical_path "${WORK_DIR}")"
fi

EXECUTION_ID="${SOZA_RUNTIME_EXCHANGE_EXECUTION_ID:-local-$(date -u +%Y%m%dT%H%M%SZ)-$$}"
if [[ -z "${EVIDENCE_DIR}" ]]; then
  EVIDENCE_DIR="${TMPDIR:-/tmp}/soza-runtime-version-exchange-evidence-${EXECUTION_ID}"
fi
mkdir -p "${EVIDENCE_DIR}"
EVIDENCE_DIR="$(canonical_path "${EVIDENCE_DIR}")"

for output_dir in "${WORK_DIR}" "${EVIDENCE_DIR}"; do
  if is_within_path "${output_dir}" "${SOZA_ROOT}"; then
    echo "runtime exchange output directory must not be inside the SOZA repository: ${output_dir}" >&2
    exit 1
  fi
  if is_within_path "${output_dir}" "${KJ_ATLAS_DIR}"; then
    echo "runtime exchange output directory must not be inside the KJ Atlas repository: ${output_dir}" >&2
    exit 1
  fi
done

VENV_DIR="${WORK_DIR}/venv"
MODEL_STORE="${WORK_DIR}/ollama-models"
REQUEST_FILE="${WORK_DIR}/kj-atlas-runtime-exchange-request.json"
IDENTITY_FILE="${WORK_DIR}/runtime-exchange-identity.json"
RUNTIME_ROOT_A="${WORK_DIR}/ollama-runtime-a"
RUNTIME_ROOT_B="${WORK_DIR}/ollama-runtime-b"
RUNTIME_ARCHIVE_A="${WORK_DIR}/ollama-a.tar.zst"
RUNTIME_ARCHIVE_B="${WORK_DIR}/ollama-b.tar.zst"

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

preserve_evidence() {
  local preserve_status=0
  mkdir -p "${EVIDENCE_DIR}" || return 1
  local path
  for path in \
    "${IDENTITY_FILE}" \
    "${REQUEST_FILE}" \
    "${WORK_DIR}/runtime-exchange-a-version.txt" \
    "${WORK_DIR}/runtime-exchange-b-version.txt" \
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
      rm -rf "${WORK_DIR}"
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

SOZA_COMMIT="${SOZA_COMMIT}" \
KJ_ATLAS_COMMIT="${ACTUAL_KJ_COMMIT}" \
EXECUTION_ID="${EXECUTION_ID}" \
IDENTITY_FILE="${IDENTITY_FILE}" \
RUNTIME_VERSION_A="${RUNTIME_VERSION_A}" \
RUNTIME_VERSION_B="${RUNTIME_VERSION_B}" \
RUNTIME_SHA256_A="${RUNTIME_SHA256_A}" \
RUNTIME_SHA256_B="${RUNTIME_SHA256_B}" \
MODEL_NAME="${MODEL_NAME}" \
MODEL_SHA256="${MODEL_SHA256}" \
python3 - <<'PY'
import json
import os
from pathlib import Path

payload = {
    "schema": "soza.runtime-version-exchange-evidence-identity/v1",
    "executionId": os.environ["EXECUTION_ID"],
    "executionSurface": "repository-local-harness",
    "repositoryCommit": os.environ["SOZA_COMMIT"],
    "methodSourceCommit": os.environ["KJ_ATLAS_COMMIT"],
    "runtimeA": {
        "name": "ollama",
        "version": os.environ["RUNTIME_VERSION_A"],
        "archiveSha256": os.environ["RUNTIME_SHA256_A"],
    },
    "runtimeB": {
        "name": "ollama",
        "version": os.environ["RUNTIME_VERSION_B"],
        "archiveSha256": os.environ["RUNTIME_SHA256_B"],
    },
    "model": {
        "name": os.environ["MODEL_NAME"],
        "expectedDigest": os.environ["MODEL_SHA256"],
    },
    "qualityJudgement": "not_evaluated",
}
Path(os.environ["IDENTITY_FILE"]).write_text(
    json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
    encoding="utf-8",
)
PY

python3 -m venv "${VENV_DIR}"
"${VENV_DIR}/bin/python" -m pip install --disable-pip-version-check -e "${KJ_ATLAS_DIR}/03_Implement/backend"

acquire_runtime() {
  local label="$1"
  local version="$2"
  local expected_sha="$3"
  local archive="$4"
  local root="$5"

  mkdir -p "${root}"
  curl --fail --silent --show-error --location \
    "https://github.com/ollama/ollama/releases/download/v${version}/ollama-linux-amd64.tar.zst" \
    --output "${archive}"
  printf '%s  %s\n' "${expected_sha}" "${archive}" | sha256sum --check --strict
  zstd -dc "${archive}" | tar -xf - -C "${root}"
  test -x "${root}/bin/ollama"
}

acquire_runtime a "${RUNTIME_VERSION_A}" "${RUNTIME_SHA256_A}" "${RUNTIME_ARCHIVE_A}" "${RUNTIME_ROOT_A}"
acquire_runtime b "${RUNTIME_VERSION_B}" "${RUNTIME_SHA256_B}" "${RUNTIME_ARCHIVE_B}" "${RUNTIME_ROOT_B}"

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

  echo "=== Ollama ${version}: verify pinned runtime artifact ==="
  "${ollama}" --version 2>&1 | tee "${version_log}"
  local escaped_version="${version//./\.}"
  grep -Eq "(^|[^0-9])${escaped_version}([^0-9]|$)" "${version_log}"

  "${ollama}" serve >"${ollama_log}" 2>&1 &
  OLLAMA_PID=$!
  for attempt in $(seq 1 60); do
    if curl --fail --silent http://127.0.0.1:11434/api/tags >/dev/null; then
      break
    fi
    if [[ "${attempt}" == "60" ]]; then
      echo "Ollama ${version} did not become ready" >&2
      cat "${ollama_log}" >&2 || true
      return 1
    fi
    sleep 0.5
  done

  "${ollama}" pull "${MODEL_NAME}"
  curl --fail --silent http://127.0.0.1:11434/api/tags >"${tags}"

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
    cd "${KJ_ATLAS_DIR}/03_Implement/backend"
    KJ_ATLAS_DATABASE_URL="sqlite:///${database}" "${VENV_DIR}/bin/alembic" upgrade head
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
  PYTHONPATH="${KJ_ATLAS_DIR}/03_Implement/backend/src" \
    "${VENV_DIR}/bin/python" -m uvicorn kj_atlas_api.main:app --host 127.0.0.1 --port 8101 \
      >"${kj_log}" 2>&1 &
  KJ_PID=$!

  for attempt in $(seq 1 100); do
    if curl --fail --silent http://127.0.0.1:8001/ >/dev/null \
      && curl --fail --silent http://127.0.0.1:8101/healthz >/dev/null; then
      break
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
export SOZA_E3B_RUNTIME_EXCHANGE_KJ_ATLAS_DIR="${KJ_ATLAS_DIR}"
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
