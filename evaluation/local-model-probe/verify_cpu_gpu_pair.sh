#!/usr/bin/env bash
set -euo pipefail

if [[ "$#" -ne 2 ]]; then
  echo "usage: $0 <cpu-evidence.sha256> <gpu-evidence.sha256>" >&2
  exit 2
fi

CPU_DIGEST_INPUT="$1"
GPU_DIGEST_INPUT="$2"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
VERIFY_SINGLE="${SCRIPT_DIR}/verify_first_actual.sh"
PAIR_VERIFICATION_OUTPUT="${PAIR_VERIFICATION_OUTPUT:-}"
CPU_EXPECTED_EVIDENCE_DIGESTS_SHA256="${CPU_EXPECTED_EVIDENCE_DIGESTS_SHA256:-}"
GPU_EXPECTED_EVIDENCE_DIGESTS_SHA256="${GPU_EXPECTED_EVIDENCE_DIGESTS_SHA256:-}"

require_file() {
  local path="$1"
  if [[ ! -f "$path" ]]; then
    echo "evidence digest sidecar not found: $path" >&2
    exit 2
  fi
}

read_comment_value() {
  local path="$1"
  local key="$2"
  local prefix="# ${key}="
  local value=""
  while IFS= read -r line || [[ -n "$line" ]]; do
    line="${line%$'\r'}"
    if [[ "$line" == "${prefix}"* ]]; then
      if [[ -n "$value" ]]; then
        echo "duplicate ${key} metadata in $path" >&2
        exit 4
      fi
      value="${line#${prefix}}"
    fi
  done <"$path"
  printf '%s' "$value"
}

resolve_matrix_path() {
  local digest_input="$1"
  local matrix_file
  matrix_file="$(read_comment_value "$digest_input" matrix_file)"
  if [[ -z "$matrix_file" ]]; then
    echo "matrix_file metadata is missing from $digest_input" >&2
    exit 4
  fi
  if [[ "$matrix_file" == */* || "$matrix_file" == "." || "$matrix_file" == ".." ]]; then
    echo "matrix_file must be a basename: $matrix_file" >&2
    exit 4
  fi
  local digest_dir
  digest_dir="$(cd "$(dirname "$digest_input")" && pwd)"
  printf '%s/%s' "$digest_dir" "$matrix_file"
}

require_file "$CPU_DIGEST_INPUT"
require_file "$GPU_DIGEST_INPUT"
require_file "$VERIFY_SINGLE"
require_file "${SCRIPT_DIR}/verify_cpu_gpu_pair.py"

CPU_GPU_LAYERS="$(read_comment_value "$CPU_DIGEST_INPUT" gpu_layers_requested)"
GPU_GPU_LAYERS="$(read_comment_value "$GPU_DIGEST_INPUT" gpu_layers_requested)"
if [[ -z "$CPU_GPU_LAYERS" ]]; then
  CPU_GPU_LAYERS="0"
fi
if [[ ! "$CPU_GPU_LAYERS" =~ ^[0-9]+$ ]]; then
  echo "CPU gpu_layers_requested must be a non-negative integer when present; observed: $CPU_GPU_LAYERS" >&2
  exit 4
fi
if [[ -z "$GPU_GPU_LAYERS" || ! "$GPU_GPU_LAYERS" =~ ^[0-9]+$ || "$GPU_GPU_LAYERS" == "0" ]]; then
  echo "GPU evidence must record a positive gpu_layers_requested value; observed: ${GPU_GPU_LAYERS:-missing}" >&2
  exit 4
fi
if [[ "$CPU_GPU_LAYERS" != "0" ]]; then
  echo "CPU evidence must not request GPU offload; observed gpu_layers_requested=$CPU_GPU_LAYERS" >&2
  exit 4
fi

EXPECTED_EVIDENCE_DIGESTS_SHA256="$CPU_EXPECTED_EVIDENCE_DIGESTS_SHA256" \
VERIFICATION_OUTPUT="" \
bash "$VERIFY_SINGLE" "$CPU_DIGEST_INPUT"

EXPECTED_EVIDENCE_DIGESTS_SHA256="$GPU_EXPECTED_EVIDENCE_DIGESTS_SHA256" \
VERIFICATION_OUTPUT="" \
bash "$VERIFY_SINGLE" "$GPU_DIGEST_INPUT"

CPU_MATRIX_PATH="$(resolve_matrix_path "$CPU_DIGEST_INPUT")"
GPU_MATRIX_PATH="$(resolve_matrix_path "$GPU_DIGEST_INPUT")"

PAIR_ARGS=(
  python3 "${SCRIPT_DIR}/verify_cpu_gpu_pair.py"
  --cpu "$CPU_MATRIX_PATH"
  --gpu "$GPU_MATRIX_PATH"
  --cpu-gpu-layers-requested "$CPU_GPU_LAYERS"
  --gpu-gpu-layers-requested "$GPU_GPU_LAYERS"
)
if [[ -n "$PAIR_VERIFICATION_OUTPUT" ]]; then
  PAIR_ARGS+=(--output "$PAIR_VERIFICATION_OUTPUT")
fi

"${PAIR_ARGS[@]}"
