#!/usr/bin/env bash
set -euo pipefail

if [[ "$#" -ne 0 ]]; then
  echo "usage: $0" >&2
  exit 2
fi

GO_TOOLCHAIN_VERSION="${GO_TOOLCHAIN_VERSION:-go1.25.14}"
GO_TOOLCHAIN_OS="${GO_TOOLCHAIN_OS:-linux}"
GO_TOOLCHAIN_ARCH="${GO_TOOLCHAIN_ARCH:-amd64}"
GO_TOOLCHAIN_ARCHIVE_NAME="${GO_TOOLCHAIN_ARCHIVE_NAME:-go1.25.14.linux-amd64.tar.gz}"
GO_TOOLCHAIN_SHA256="${GO_TOOLCHAIN_SHA256:-a21ae5633a269bcd7e90cf767e48225633795e99d831742cbf3397064fee7712}"
GO_TOOLCHAIN_URL="${GO_TOOLCHAIN_URL:-https://go.dev/dl/${GO_TOOLCHAIN_ARCHIVE_NAME}}"
GO_BINARY_PATH="${GO_BINARY_PATH:-}"
GO_TOOLCHAIN_ARCHIVE_PATH="${GO_TOOLCHAIN_ARCHIVE_PATH:-}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
TOOLCHAIN_BASE="${GO_TOOLCHAIN_WORK_DIR:-${REPO_ROOT}/.local-model-run/toolchains}"
DOWNLOAD_DIR="${TOOLCHAIN_BASE}/downloads"
INSTALL_DIR="${TOOLCHAIN_BASE}/${GO_TOOLCHAIN_VERSION}-${GO_TOOLCHAIN_OS}-${GO_TOOLCHAIN_ARCH}"
INSTALL_MARKER="${INSTALL_DIR}/.archive-sha256"
DEFAULT_ARCHIVE_PATH="${DOWNLOAD_DIR}/${GO_TOOLCHAIN_ARCHIVE_NAME}"

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

verify_exact_go() {
  local go_binary="$1"
  if [[ ! -f "$go_binary" || ! -x "$go_binary" ]]; then
    echo "Go binary must be an executable file: $go_binary" >&2
    return 1
  fi

  local observed_version observed_os observed_arch
  observed_version="$(GOTOOLCHAIN=local "$go_binary" env GOVERSION)"
  observed_os="$(GOTOOLCHAIN=local "$go_binary" env GOHOSTOS)"
  observed_arch="$(GOTOOLCHAIN=local "$go_binary" env GOHOSTARCH)"

  if [[ "$observed_version" != "$GO_TOOLCHAIN_VERSION" ||
        "$observed_os" != "$GO_TOOLCHAIN_OS" ||
        "$observed_arch" != "$GO_TOOLCHAIN_ARCH" ]]; then
    echo "Go toolchain identity mismatch" >&2
    echo "expected: $GO_TOOLCHAIN_VERSION $GO_TOOLCHAIN_OS/$GO_TOOLCHAIN_ARCH" >&2
    echo "observed: $observed_version $observed_os/$observed_arch" >&2
    return 1
  fi
}

require_command git
require_command sha256sum
require_command awk

SOURCE_STATUS="$(git -C "$REPO_ROOT" status --porcelain=v1 --untracked-files=all)"
if [[ -n "$SOURCE_STATUS" ]]; then
  echo "working tree is not clean; refusing toolchain materialization for an ambiguous exact-source run" >&2
  dirty_line_count=0
  while IFS= read -r dirty_line; do
    printf '%s\n' "$dirty_line" >&2
    dirty_line_count=$((dirty_line_count + 1))
    if (( dirty_line_count >= 20 )); then
      break
    fi
  done <<<"$SOURCE_STATUS"
  exit 2
fi

TOOLCHAIN_SOURCE=""

if [[ -n "$GO_BINARY_PATH" ]]; then
  if ! verify_exact_go "$GO_BINARY_PATH"; then
    exit 4
  fi
  GO_BINARY="$GO_BINARY_PATH"
  TOOLCHAIN_SOURCE="pre-provisioned-binary"
elif command -v go >/dev/null 2>&1 && verify_exact_go "$(command -v go)" >/dev/null 2>&1; then
  GO_BINARY="$(command -v go)"
  TOOLCHAIN_SOURCE="system-exact"
else
  if [[ "$(uname -s)" != "Linux" ]]; then
    echo "pinned Go toolchain bootstrap currently supports Linux only" >&2
    exit 2
  fi
  case "$(uname -m)" in
    x86_64|amd64) ;;
    *)
      echo "pinned Go toolchain archive is linux-amd64; observed architecture: $(uname -m)" >&2
      exit 2
      ;;
  esac

  require_command tar
  mkdir -p "$DOWNLOAD_DIR" "$TOOLCHAIN_BASE"

  if [[ -n "$GO_TOOLCHAIN_ARCHIVE_PATH" ]]; then
    ARCHIVE_PATH="$GO_TOOLCHAIN_ARCHIVE_PATH"
    if [[ ! -f "$ARCHIVE_PATH" ]]; then
      echo "pre-provisioned Go archive not found: $ARCHIVE_PATH" >&2
      exit 4
    fi
    TOOLCHAIN_SOURCE="pre-provisioned-archive"
  else
    require_command curl
    ARCHIVE_PATH="$DEFAULT_ARCHIVE_PATH"
    if [[ ! -f "$ARCHIVE_PATH" ]]; then
      echo "downloading $GO_TOOLCHAIN_ARCHIVE_NAME"
      curl --fail --location --retry 3 --retry-delay 2 \
        --output "${ARCHIVE_PATH}.partial" \
        "$GO_TOOLCHAIN_URL"
      mv "${ARCHIVE_PATH}.partial" "$ARCHIVE_PATH"
    fi
    TOOLCHAIN_SOURCE="pinned-archive"
  fi

  verify_sha256 "$GO_TOOLCHAIN_SHA256" "$ARCHIVE_PATH"

  INSTALLED_ARCHIVE_SHA=""
  if [[ -f "$INSTALL_MARKER" ]]; then
    IFS= read -r INSTALLED_ARCHIVE_SHA <"$INSTALL_MARKER" || true
  fi
  if [[ "$INSTALLED_ARCHIVE_SHA" != "$GO_TOOLCHAIN_SHA256" ]]; then
    rm -rf "$INSTALL_DIR"
    mkdir -p "$INSTALL_DIR"
    tar -xzf "$ARCHIVE_PATH" -C "$INSTALL_DIR"
    printf '%s\n' "$GO_TOOLCHAIN_SHA256" >"$INSTALL_MARKER"
  fi

  GO_BINARY="${INSTALL_DIR}/go/bin/go"
  if ! verify_exact_go "$GO_BINARY"; then
    echo "materialized Go toolchain did not match the pinned identity" >&2
    exit 4
  fi
fi

GO_BINARY_SHA256="$(sha256sum "$GO_BINARY" | awk '{print $1}')"

export PATH="$(dirname "$GO_BINARY"):$PATH"
export GOTOOLCHAIN=local
export SEI_GO_TOOLCHAIN_VERSION="$GO_TOOLCHAIN_VERSION"
export SEI_GO_TOOLCHAIN_OS="$GO_TOOLCHAIN_OS"
export SEI_GO_TOOLCHAIN_ARCH="$GO_TOOLCHAIN_ARCH"
export SEI_GO_TOOLCHAIN_SOURCE="$TOOLCHAIN_SOURCE"
export SEI_GO_TOOLCHAIN_BINARY_SHA256="$GO_BINARY_SHA256"
if [[ "$TOOLCHAIN_SOURCE" == "pinned-archive" ||
      "$TOOLCHAIN_SOURCE" == "pre-provisioned-archive" ]]; then
  export SEI_GO_TOOLCHAIN_ARCHIVE_SHA256="$GO_TOOLCHAIN_SHA256"
else
  export SEI_GO_TOOLCHAIN_ARCHIVE_SHA256=""
fi

echo "go_toolchain_source=$TOOLCHAIN_SOURCE"
echo "go_toolchain_version=$GO_TOOLCHAIN_VERSION"
echo "go_toolchain_platform=$GO_TOOLCHAIN_OS/$GO_TOOLCHAIN_ARCH"
echo "go_toolchain_binary=$GO_BINARY"
echo "go_toolchain_binary_sha256=$GO_BINARY_SHA256"
if [[ -n "$SEI_GO_TOOLCHAIN_ARCHIVE_SHA256" ]]; then
  echo "go_toolchain_archive_sha256=$SEI_GO_TOOLCHAIN_ARCHIVE_SHA256"
fi

exec bash "${SCRIPT_DIR}/run_first_actual.sh"
