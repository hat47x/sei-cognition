#!/usr/bin/env bash
set -euo pipefail

if [[ "$#" -ne 1 ]]; then
  echo "usage: $0 <evidence.sha256>" >&2
  exit 2
fi

DIGEST_INPUT="$1"
if [[ ! -f "$DIGEST_INPUT" ]]; then
  echo "evidence digest sidecar not found: $DIGEST_INPUT" >&2
  exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
PROBE_DIR="${REPO_ROOT}/evaluation/sparse-associative-cognition/prototype-go"

EXPECTED_SOURCE_GIT_SHA="${EXPECTED_SOURCE_GIT_SHA:-}"
EXPECTED_MODEL_SHA256="${EXPECTED_MODEL_SHA256:-}"
EXPECTED_EVIDENCE_DIGESTS_SHA256="${EXPECTED_EVIDENCE_DIGESTS_SHA256:-}"
VERIFICATION_OUTPUT="${VERIFICATION_OUTPUT:-}"

require_command() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "required command not found: $1" >&2
    exit 2
  }
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

require_command sha256sum
require_command awk
require_command go

GO_VERSION="$(go env GOVERSION)"
GO_VERSION_NUM="${GO_VERSION#go}"
GO_MAJOR="${GO_VERSION_NUM%%.*}"
GO_MINOR_REST="${GO_VERSION_NUM#*.}"
GO_MINOR="${GO_MINOR_REST%%.*}"
if [[ ! "$GO_MAJOR" =~ ^[0-9]+$ || ! "$GO_MINOR" =~ ^[0-9]+$ ]] ||
   (( GO_MAJOR < 1 || (GO_MAJOR == 1 && GO_MINOR < 25) )); then
  echo "Go 1.25 or newer is required for the canonical verifier module; observed: $GO_VERSION" >&2
  exit 2
fi

if [[ -n "$EXPECTED_EVIDENCE_DIGESTS_SHA256" ]]; then
  verify_sha256 "$EXPECTED_EVIDENCE_DIGESTS_SHA256" "$DIGEST_INPUT"
fi

DIGEST_DIR="$(cd "$(dirname "$DIGEST_INPUT")" && pwd)"
DIGEST_BASENAME="$(basename "$DIGEST_INPUT")"

MATRIX_FILE=""
SERVER_LOG_FILE=""
MATRIX_EXIT_CODE=""
HASH_ENTRY_COUNT=0
HASH_FILES=()

while IFS= read -r line || [[ -n "$line" ]]; do
  line="${line%$'\r'}"
  case "$line" in
    "")
      continue
      ;;
    "# modelmatrix_exit_code="*)
      MATRIX_EXIT_CODE="${line#\# modelmatrix_exit_code=}"
      ;;
    "# matrix_file="*)
      MATRIX_FILE="${line#\# matrix_file=}"
      ;;
    "# server_log_file="*)
      SERVER_LOG_FILE="${line#\# server_log_file=}"
      ;;
    \#*)
      continue
      ;;
    *)
      if [[ ! "$line" =~ ^([0-9A-Fa-f]{64})[[:space:]][[:space:]](.+)$ ]]; then
        echo "invalid digest line: $line" >&2
        exit 4
      fi
      evidence_file="${BASH_REMATCH[2]}"
      if [[ "$evidence_file" == */* || "$evidence_file" == "." || "$evidence_file" == ".." ]]; then
        echo "digest sidecar must contain basename-only evidence files: $evidence_file" >&2
        exit 4
      fi
      HASH_FILES+=("$evidence_file")
      HASH_ENTRY_COUNT=$((HASH_ENTRY_COUNT + 1))
      ;;
  esac
done <"$DIGEST_INPUT"

if [[ "$MATRIX_EXIT_CODE" != "0" && "$MATRIX_EXIT_CODE" != "1" ]]; then
  echo "digest sidecar must contain modelmatrix_exit_code 0 or 1 when a matrix artifact is present" >&2
  exit 4
fi
if [[ -z "$MATRIX_FILE" || -z "$SERVER_LOG_FILE" ]]; then
  echo "digest sidecar must identify both matrix_file and server_log_file" >&2
  exit 4
fi
for evidence_file in "$MATRIX_FILE" "$SERVER_LOG_FILE"; do
  if [[ "$evidence_file" == */* || "$evidence_file" == "." || "$evidence_file" == ".." ]]; then
    echo "evidence filename must be a basename: $evidence_file" >&2
    exit 4
  fi
done
if [[ "$MATRIX_FILE" == "$SERVER_LOG_FILE" ]]; then
  echo "matrix and server log filenames must be distinct" >&2
  exit 4
fi
if (( HASH_ENTRY_COUNT != 2 )); then
  echo "digest sidecar must contain exactly two SHA-256 entries; observed: $HASH_ENTRY_COUNT" >&2
  exit 4
fi
if [[ "${HASH_FILES[0]}" == "${HASH_FILES[1]}" ]]; then
  echo "digest sidecar must hash two distinct evidence files" >&2
  exit 4
fi
matrix_hashed=false
server_log_hashed=false
for evidence_file in "${HASH_FILES[@]}"; do
  if [[ "$evidence_file" == "$MATRIX_FILE" ]]; then
    matrix_hashed=true
  fi
  if [[ "$evidence_file" == "$SERVER_LOG_FILE" ]]; then
    server_log_hashed=true
  fi
done
if [[ "$matrix_hashed" != true || "$server_log_hashed" != true ]]; then
  echo "matrix_file/server_log_file comments must match the two hashed evidence files" >&2
  exit 4
fi

(
  cd "$DIGEST_DIR"
  sha256sum -c "$DIGEST_BASENAME"
)

MATRIX_PATH="${DIGEST_DIR}/${MATRIX_FILE}"
SERVER_LOG_PATH="${DIGEST_DIR}/${SERVER_LOG_FILE}"
if [[ ! -f "$MATRIX_PATH" || ! -f "$SERVER_LOG_PATH" ]]; then
  echo "verified evidence files are missing after digest check" >&2
  exit 4
fi

VERIFY_ARGS=(
  go run ./cmd/modelmatrixverify
  --matrix "$MATRIX_PATH"
  --observed-modelmatrix-exit-code "$MATRIX_EXIT_CODE"
)
if [[ -n "$EXPECTED_SOURCE_GIT_SHA" ]]; then
  VERIFY_ARGS+=(--expected-source-git-sha "$EXPECTED_SOURCE_GIT_SHA")
fi
if [[ -n "$EXPECTED_MODEL_SHA256" ]]; then
  VERIFY_ARGS+=(--expected-model-sha256 "$EXPECTED_MODEL_SHA256")
fi
if [[ -n "$VERIFICATION_OUTPUT" ]]; then
  VERIFY_ARGS+=(--output "$VERIFICATION_OUTPUT")
fi

(
  cd "$PROBE_DIR"
  "${VERIFY_ARGS[@]}"
)
