#!/bin/sh
# Build the `sei` single binary for several platforms.
#
# usage: tools/build_sei.sh <output-dir> [os/arch ...]
# default targets: linux/amd64 linux/arm64 darwin/arm64 darwin/amd64 windows/amd64
#
# Requires Go 1.25 or later (see runtime/go/go.mod). The build does not use cgo,
# so every target is produced from one machine and has no runtime dependency.
set -eu

if [ "$#" -lt 1 ]; then
    echo "usage: $0 <output-dir> [os/arch ...]" >&2
    exit 2
fi

out=$1
mkdir -p "$out"
out=$(cd "$out" && pwd)
shift
if [ "$#" -eq 0 ]; then
    set -- linux/amd64 linux/arm64 darwin/arm64 darwin/amd64 windows/amd64
fi

root=$(cd "$(dirname "$0")/.." && pwd)
mkdir -p "$out"
version=${SEI_VERSION:-dev}
# Full-length revision, with "+dirty" when the tree has uncommitted changes
# (including untracked files), the same form `go build` records from VCS info.
commit=$(sh "$root/tools/sei_build_commit.sh" "$root")
case "$commit" in
*+dirty) echo "warning: working tree has uncommitted changes; commit is $commit and the artifacts in $out are not reproducible from that commit" >&2 ;;
esac
pkg=github.com/hat47x/sei-cognition/runtime/go/seicli

for target in "$@"; do
    goos=${target%/*}
    goarch=${target#*/}
    ext=""
    if [ "$goos" = "windows" ]; then
        ext=".exe"
    fi
    file="$out/sei-$goos-$goarch$ext"
    (cd "$root/runtime/go" && CGO_ENABLED=0 GOOS=$goos GOARCH=$goarch \
        go build -trimpath \
        -ldflags "-s -w -X $pkg.BuildVersion=$version -X $pkg.BuildCommit=$commit -X $pkg.BuildTarget=$target" \
        -o "$file" ./cmd/sei)
    echo "built $file"
done

# sha256sum is GNU coreutils; stock macOS has shasum instead.
if command -v sha256sum >/dev/null 2>&1; then
    (cd "$out" && sha256sum sei-* > SHA256SUMS)
else
    (cd "$out" && shasum -a 256 sei-* > SHA256SUMS)
fi
echo "wrote $out/SHA256SUMS"
