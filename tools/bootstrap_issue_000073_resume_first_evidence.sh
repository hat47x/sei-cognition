#!/usr/bin/env bash
set -euo pipefail

if [[ "$#" -eq 0 ]]; then
  echo "usage: $0 --expected-head <commit-sha> [capture options]" >&2
  exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
CAPTURE="${REPO_ROOT}/tools/capture_issue_000073_resume_first_evidence.py"

PINNED_GO_VERSION="go1.25.14"
PINNED_GO_OS="linux"
PINNED_GO_ARCH="amd64"
PINNED_ARCHIVE="go1.25.14.linux-amd64.tar.gz"
PINNED_ARCHIVE_SHA256="a21ae5633a269bcd7e90cf767e48225633795e99d831742cbf3397064fee7712"
GO_TOOLCHAIN_URL="${GO_TOOLCHAIN_URL:-https://go.dev/dl/${PINNED_ARCHIVE}}"
GO_BINARY_PATH="${GO_BINARY_PATH:-}"
GO_TOOLCHAIN_ARCHIVE_PATH="${GO_TOOLCHAIN_ARCHIVE_PATH:-}"

CACHE_BASE="${XDG_CACHE_HOME:-${HOME:-/tmp}/.cache}"
TOOLCHAIN_BASE="${GO_TOOLCHAIN_WORK_DIR:-${CACHE_BASE}/sei-cognition/go-toolchains}"
DOWNLOAD_DIR="${TOOLCHAIN_BASE}/downloads"
INSTALL_DIR="${TOOLCHAIN_BASE}/${PINNED_GO_VERSION}-${PINNED_GO_OS}-${PINNED_GO_ARCH}"
MARKER="${INSTALL_DIR}/.archive-sha256"

require_command() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "required command not found: $1" >&2
    exit 2
  }
}

sha256_file() {
  sha256sum "$1" | awk '{print $1}'
}

verify_archive() {
  local path="$1"
  local observed
  observed="$(sha256_file "$path")"
  if [[ "$observed" != "$PINNED_ARCHIVE_SHA256" ]]; then
    echo "Go archive SHA-256 mismatch: $path" >&2
    echo "expected: $PINNED_ARCHIVE_SHA256" >&2
    echo "observed: $observed" >&2
    return 1
  fi
}

is_go125() {
  local go_binary="$1"
  [[ -f "$go_binary" && -x "$go_binary" ]] || return 1

  local version
  version="$(GOTOOLCHAIN=local "$go_binary" version 2>/dev/null || true)"
  [[ "$version" =~ ^go[[:space:]]version[[:space:]]go1\.25([.][0-9]+)?[[:space:]] ]]
}

verify_pinned_go() {
  local go_binary="$1"
  [[ -f "$go_binary" && -x "$go_binary" ]] || return 1

  local goversion gohostos gohostarch
  goversion="$(GOTOOLCHAIN=local "$go_binary" env GOVERSION 2>/dev/null || true)"
  gohostos="$(GOTOOLCHAIN=local "$go_binary" env GOHOSTOS 2>/dev/null || true)"
  gohostarch="$(GOTOOLCHAIN=local "$go_binary" env GOHOSTARCH 2>/dev/null || true)"

  [[ "$goversion" == "$PINNED_GO_VERSION" &&
     "$gohostos" == "$PINNED_GO_OS" &&
     "$gohostarch" == "$PINNED_GO_ARCH" ]]
}

require_command git
require_command sha256sum
require_command awk
require_command python3

if [[ ! -f "$CAPTURE" ]]; then
  echo "ISSUE-000073 capture tool not found: $CAPTURE" >&2
  exit 2
fi

has_expected_head=false
has_go_argument=false
for arg in "$@"; do
  case "$arg" in
    --expected-head|--expected-head=*)
      has_expected_head=true
      ;;
    --go|--go=*)
      has_go_argument=true
      ;;
  esac
done

if [[ "$has_expected_head" != true ]]; then
  echo "--expected-head is required and must come from an independent canonical source" >&2
  exit 2
fi
if [[ "$has_go_argument" == true ]]; then
  echo "do not pass --go to this bootstrap wrapper; use GO_BINARY_PATH for a pre-provisioned Go 1.25.x binary" >&2
  exit 2
fi

SOURCE_STATUS="$(git -C "$REPO_ROOT" status --porcelain=v1 --untracked-files=all)"
if [[ -n "$SOURCE_STATUS" ]]; then
  echo "working tree is not clean; refusing ISSUE-000073 executable Evidence capture" >&2
  printf '%s\n' "$SOURCE_STATUS" | head -n 20 >&2
  exit 2
fi

GO_BINARY=""
GO_SOURCE=""

if [[ -n "$GO_BINARY_PATH" ]]; then
  if ! is_go125 "$GO_BINARY_PATH"; then
    echo "GO_BINARY_PATH must point to a Go 1.25.x executable" >&2
    exit 4
  fi
  GO_BINARY="$GO_BINARY_PATH"
  GO_SOURCE="pre-provisioned-binary"
elif command -v go >/dev/null 2>&1 && is_go125 "$(command -v go)"; then
  GO_BINARY="$(command -v go)"
  GO_SOURCE="system-go1.25"
else
  if [[ "$(uname -s)" != "Linux" ]]; then
    echo "automatic pinned Go bootstrap currently supports Linux only; provide GO_BINARY_PATH for another supported host" >&2
    exit 2
  fi
  case "$(uname -m)" in
    x86_64|amd64) ;;
    *)
      echo "automatic pinned Go bootstrap uses the linux-amd64 archive; observed: $(uname -m)" >&2
      exit 2
      ;;
  esac

  require_command tar
  mkdir -p "$DOWNLOAD_DIR" "$TOOLCHAIN_BASE"

  if [[ -n "$GO_TOOLCHAIN_ARCHIVE_PATH" ]]; then
    ARCHIVE_PATH="$GO_TOOLCHAIN_ARCHIVE_PATH"
    [[ -f "$ARCHIVE_PATH" ]] || {
      echo "pre-provisioned Go archive not found: $ARCHIVE_PATH" >&2
      exit 4
    }
    GO_SOURCE="pre-provisioned-archive"
  else
    require_command curl
    ARCHIVE_PATH="${DOWNLOAD_DIR}/${PINNED_ARCHIVE}"
    if [[ ! -f "$ARCHIVE_PATH" ]]; then
      partial="${ARCHIVE_PATH}.partial.$$"
      trap 'rm -f "$partial"' EXIT
      curl --fail --location --retry 3 --retry-delay 2 --output "$partial" "$GO_TOOLCHAIN_URL"
      verify_archive "$partial" || exit 4
      mv "$partial" "$ARCHIVE_PATH"
      trap - EXIT
    fi
    GO_SOURCE="pinned-archive"
  fi

  verify_archive "$ARCHIVE_PATH" || exit 4

  if [[ -x "${INSTALL_DIR}/go/bin/go" && -f "$MARKER" ]]; then
    installed_digest="$(cat "$MARKER")"
    if [[ "$installed_digest" == "$PINNED_ARCHIVE_SHA256" ]] && verify_pinned_go "${INSTALL_DIR}/go/bin/go"; then
      GO_BINARY="${INSTALL_DIR}/go/bin/go"
    else
      echo "existing cached Go toolchain does not match the pinned identity; remove it explicitly before retrying: $INSTALL_DIR" >&2
      exit 4
    fi
  else
    if [[ -e "$INSTALL_DIR" ]]; then
      echo "cached Go toolchain path already exists but is incomplete; remove it explicitly before retrying: $INSTALL_DIR" >&2
      exit 4
    fi

    staging="${INSTALL_DIR}.partial.$$"
    rm -rf "$staging"
    mkdir -p "$staging"
    trap 'rm -rf "$staging"' EXIT
    tar -xzf "$ARCHIVE_PATH" -C "$staging"

    if ! verify_pinned_go "${staging}/go/bin/go"; then
      echo "materialized Go toolchain does not match pinned ${PINNED_GO_VERSION} ${PINNED_GO_OS}/${PINNED_GO_ARCH}" >&2
      exit 4
    fi

    printf '%s\n' "$PINNED_ARCHIVE_SHA256" > "${staging}/.archive-sha256"
    mv "$staging" "$INSTALL_DIR"
    trap - EXIT
    GO_BINARY="${INSTALL_DIR}/go/bin/go"
  fi
fi

GO_BINARY="$(cd "$(dirname "$GO_BINARY")" && pwd)/$(basename "$GO_BINARY")"
GO_BINARY_SHA256="$(sha256_file "$GO_BINARY")"
GO_VERSION_OUTPUT="$(GOTOOLCHAIN=local "$GO_BINARY" version)"

echo "issue=ISSUE-000073"
echo "go_source=$GO_SOURCE"
echo "go_version=$GO_VERSION_OUTPUT"
echo "go_binary=$GO_BINARY"
echo "go_binary_sha256=$GO_BINARY_SHA256"

exec python3 "$CAPTURE" --go "$GO_BINARY" "$@"
