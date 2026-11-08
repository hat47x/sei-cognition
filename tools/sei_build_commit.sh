#!/bin/sh
# Print the commit label for a sei build of the repository at <root>.
#
# usage: tools/sei_build_commit.sh <root>
# Output: the full 40-character HEAD revision, with "+dirty" appended when
# `git status --porcelain` is not empty (modified, staged or untracked files;
# the same rule the Go toolchain uses for vcs.modified). "unknown" when git
# or the repository is unavailable.
set -u
root=${1:?usage: $0 <root>}
rev=$(git -C "$root" rev-parse HEAD 2>/dev/null) || { echo unknown; exit 0; }
if [ -n "$(git -C "$root" status --porcelain 2>/dev/null)" ]; then
    rev="$rev+dirty"
fi
echo "$rev"
