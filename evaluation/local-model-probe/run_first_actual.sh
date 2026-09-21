#!/usr/bin/env bash
set -euo pipefail

RUNTIME_TAG="${RUNTIME_TAG:-b10964}"
RUNTIME_VERSION="${RUNTIME_VERSION:-${RUNTIME_TAG}}"
RUNTIME_ARCHIVE_NAME="${RUNTIME_ARCHIVE_NAME:-llama-b10964-bin-ubuntu-x64.tar.gz}"
RUNTIME_SHA256="${RUNTIME_SHA256:-9abf88aea48a55d0f80edb1ee20220b186848cca0b4e919d71518cfd7ca67443}"
RUNTIME_URL="${RUNTIME_URL:-https://github.com/ggml-org/llama.cpp/releases/download/${RUNTIME_TAG}/${RUNTIME_ARCHIVE_NAME}}"
RUNTIME_BINARY_PATH="${RUNTIME_BINARY_PATH:-}"
RUNTIME_BINARY_SHA256="${RUNTIME_BINARY_SHA256:-}"

MODEL_NAME="${MODEL_NAME:-Qwen3.5-0.8B-Q4_0.gguf}"
MODEL_SHA256="${MODEL_SHA256:-57d1997790d1744fba5b40a7317df71ea5e2acee28c47e78f0cce39c0703f8cf}"
MODEL_URL="${MODEL_URL:-https://huggingface.co/ggml-org/Qwen3.5-0.8B-GGUF/resolve/main/${MODEL_NAME}?download=true}"
MODEL_ALIAS="${MODEL_ALIAS:-qwen35-0.8b-q4_0}"
QUANTIZATION="${QUANTIZATION:-Q4_0}"
MODEL_FILE_PATH="${MODEL_FILE_PATH:-}"

PORT="${PORT:-8080}"
HOST="${HOST:-127.0.0.1}"
CONTEXT_SIZE="${CONTEXT_SIZE:-4096}"
THREADS="${THREADS:-8}"
MAX_TOKENS="${MAX_TOKENS:-800}"
HEALTH_WAIT_SECONDS="${HEALTH_WAIT_SECONDS:-120}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
PROBE_DIR="${REPO_ROOT}/evaluation/sparse-associative-cognition/prototype-go"
WORK_DIR="${WORK_DIR:-${REPO_ROOT}/.local-model-run/qwen35-08-q4-0}"

RUNTIME_ARCHIVE="${WORK_DIR}/${RUNTIME_ARCHIVE_NAME}"
RUNTIME_DIR="${WORK_DIR}/llama-runtime"
RUNTIME_MARKER="${RUNTIME_DIR}/.archive-sha256"
MODEL_FILE="${MODEL_FILE_PATH:-${WORK_DIR}/${MODEL_NAME}}"
SERVER_LOG="${SERVER_LOG:-${WORK_DIR}/llama-server.log}"

require_command() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "required command not found: $1" >&2
    exit 2
  }
}

download_if_missing() {
  local url="$1"
  local path="$2"
  if [[ -f "$path" ]]; then
    return
  fi
  echo "downloading $(basename "$path")"
  curl --fail --location --retry 3 --retry-delay 2 --output "${path}.partial" "$url"
  mv "${path}.partial" "$path"
}

verify_sha256() {
  local expected="$1"
  local path="$2"
  local actual
  actual="$(sha256sum "$path" | awk '{print $1}')"
  if [[ "$actual" != "$expected" ]]; then
    echo "SHA-256 mismatch for $path" >&2
    echo "expected: $expected" >&2
    echo "observed: $actual" >&2
    exit 3
  fi
}

cleanup() {
  if [[ -n "${RUNTIME_PID:-}" ]] && kill -0 "$RUNTIME_PID" 2>/dev/null; then
    kill "$RUNTIME_PID" 2>/dev/null || true
    wait "$RUNTIME_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT INT TERM

require_command curl
require_command sha256sum
require_command awk
require_command git
require_command go

GO_VERSION="$(go env GOVERSION)"
GO_VERSION_NUM="${GO_VERSION#go}"
GO_MAJOR="${GO_VERSION_NUM%%.*}"
GO_MINOR_REST="${GO_VERSION_NUM#*.}"
GO_MINOR="${GO_MINOR_REST%%.*}"
if [[ ! "$GO_MAJOR" =~ ^[0-9]+$ || ! "$GO_MINOR" =~ ^[0-9]+$ ]] ||
   (( GO_MAJOR < 1 || (GO_MAJOR == 1 && GO_MINOR < 25) )); then
  echo "Go 1.25 or newer is required for the canonical probe module; observed: $GO_VERSION" >&2
  exit 2
fi

mkdir -p "$WORK_DIR"

if [[ -n "$RUNTIME_BINARY_PATH" ]]; then
  if [[ ! -f "$RUNTIME_BINARY_PATH" || ! -x "$RUNTIME_BINARY_PATH" ]]; then
    echo "pre-provisioned runtime binary must be an executable file: $RUNTIME_BINARY_PATH" >&2
    exit 4
  fi
  LLAMA_SERVER="$RUNTIME_BINARY_PATH"
  if [[ -n "$RUNTIME_BINARY_SHA256" ]]; then
    verify_sha256 "$RUNTIME_BINARY_SHA256" "$LLAMA_SERVER"
  fi
  RUNTIME_SOURCE="pre-provisioned-binary"
else
  require_command tar
  require_command find

  if [[ "$(uname -s)" != "Linux" ]]; then
    echo "pinned runtime archive path currently supports Linux only" >&2
    exit 2
  fi
  case "$(uname -m)" in
    x86_64|amd64) ;;
    *)
      echo "pinned runtime archive is x86_64; observed architecture: $(uname -m)" >&2
      exit 2
      ;;
  esac

  download_if_missing "$RUNTIME_URL" "$RUNTIME_ARCHIVE"
  verify_sha256 "$RUNTIME_SHA256" "$RUNTIME_ARCHIVE"

  EXTRACTED_RUNTIME_SHA=""
  if [[ -f "$RUNTIME_MARKER" ]]; then
    IFS= read -r EXTRACTED_RUNTIME_SHA <"$RUNTIME_MARKER" || true
  fi
  if [[ "$EXTRACTED_RUNTIME_SHA" != "$RUNTIME_SHA256" ]]; then
    rm -rf "$RUNTIME_DIR"
    mkdir -p "$RUNTIME_DIR"
    tar -xzf "$RUNTIME_ARCHIVE" -C "$RUNTIME_DIR"
    printf '%s\n' "$RUNTIME_SHA256" >"$RUNTIME_MARKER"
  fi

  LLAMA_SERVER="$(find "$RUNTIME_DIR" -type f -name llama-server -print -quit)"
  if [[ -z "$LLAMA_SERVER" ]]; then
    echo "llama-server not found under $RUNTIME_DIR" >&2
    exit 4
  fi
  RUNTIME_SOURCE="pinned-archive"
fi

if [[ -n "$MODEL_FILE_PATH" ]]; then
  if [[ ! -f "$MODEL_FILE" ]]; then
    echo "pre-provisioned model file not found: $MODEL_FILE" >&2
    exit 4
  fi
  MODEL_SOURCE="pre-provisioned-file"
else
  download_if_missing "$MODEL_URL" "$MODEL_FILE"
  MODEL_SOURCE="pinned-download"
fi
verify_sha256 "$MODEL_SHA256" "$MODEL_FILE"

RUNTIME_BINARY_OBSERVED_SHA256="$(sha256sum "$LLAMA_SERVER" | awk '{print $1}')"

SOURCE_GIT_SHA="$(git -C "$REPO_ROOT" rev-parse HEAD)"
RUN_ID_PREFIX="${RUN_ID_PREFIX:-qwen35-08-q4-0-$(date -u +%Y%m%dT%H%M%SZ)}"
OUTPUT="${OUTPUT:-${WORK_DIR}/${RUN_ID_PREFIX}-matrix.json}"

if [[ -e "$OUTPUT" ]]; then
  echo "matrix output already exists: $OUTPUT" >&2
  exit 5
fi

echo "source_git_sha=$SOURCE_GIT_SHA"
echo "runtime_source=$RUNTIME_SOURCE"
echo "runtime_version=$RUNTIME_VERSION"
echo "runtime_binary=$LLAMA_SERVER"
echo "runtime_binary_observed_sha256=$RUNTIME_BINARY_OBSERVED_SHA256"
if [[ "$RUNTIME_SOURCE" == "pinned-archive" ]]; then
  echo "runtime_archive_sha256=$RUNTIME_SHA256"
elif [[ -z "$RUNTIME_BINARY_SHA256" ]]; then
  echo "runtime_binary_expected_sha256=not-supplied"
fi
echo "model_source=$MODEL_SOURCE"
echo "model_alias=$MODEL_ALIAS"
echo "quantization=$QUANTIZATION"
echo "model_file=$MODEL_FILE"
echo "model_sha256=$MODEL_SHA256"
echo "work_dir=$WORK_DIR"
echo "output=$OUTPUT"

"$LLAMA_SERVER" \
  --model "$MODEL_FILE" \
  --alias "$MODEL_ALIAS" \
  --host "$HOST" \
  --port "$PORT" \
  --ctx-size "$CONTEXT_SIZE" \
  --threads "$THREADS" \
  --metrics \
  >"$SERVER_LOG" 2>&1 &
RUNTIME_PID=$!

HEALTH_URL="http://${HOST}:${PORT}/health"
METRICS_URL="http://${HOST}:${PORT}/metrics"
PROPS_URL="http://${HOST}:${PORT}/props"
CHAT_URL="http://${HOST}:${PORT}/v1/chat/completions"

deadline=$((SECONDS + HEALTH_WAIT_SECONDS))
while (( SECONDS < deadline )); do
  if ! kill -0 "$RUNTIME_PID" 2>/dev/null; then
    echo "llama-server exited before health became ready" >&2
    tail -n 80 "$SERVER_LOG" >&2 || true
    exit 6
  fi
  if curl --silent --show-error --fail "$HEALTH_URL" >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

if ! curl --silent --show-error --fail "$HEALTH_URL" >/dev/null 2>&1; then
  echo "health endpoint did not become ready within ${HEALTH_WAIT_SECONDS}s" >&2
  tail -n 80 "$SERVER_LOG" >&2 || true
  exit 7
fi

(
  cd "$PROBE_DIR"
  go run ./cmd/modelmatrix \
    --run-id-prefix "$RUN_ID_PREFIX" \
    --source-git-sha "$SOURCE_GIT_SHA" \
    --health-endpoint "$HEALTH_URL" \
    --endpoint "$CHAT_URL" \
    --runtime llama.cpp \
    --runtime-version "$RUNTIME_VERSION" \
    --runtime-pid "$RUNTIME_PID" \
    --runtime-metrics-endpoint "$METRICS_URL" \
    --runtime-props-endpoint "$PROPS_URL" \
    --model "$MODEL_ALIAS" \
    --model-file "$MODEL_FILE" \
    --expected-model-sha256 "$MODEL_SHA256" \
    --quantization "$QUANTIZATION" \
    --context-size "$CONTEXT_SIZE" \
    --threads "$THREADS" \
    --max-tokens "$MAX_TOKENS" \
    --stream \
    --output "$OUTPUT"
)

echo "matrix artifact: $OUTPUT"
echo "server log: $SERVER_LOG"
