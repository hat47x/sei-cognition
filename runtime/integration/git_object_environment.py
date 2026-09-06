from __future__ import annotations

import os
from collections.abc import Mapping

# These variables can redirect a Git command away from the repository selected by
# `git -C <repo>`, redirect object lookup/writes, substitute a different index, or
# change replace/graft semantics.  ISSUE-000072 source identity checks must observe
# the repository's own object database and literal object graph instead.
UNTRUSTED_GIT_ENVIRONMENT = {
    "GIT_DIR",
    "GIT_WORK_TREE",
    "GIT_COMMON_DIR",
    "GIT_OBJECT_DIRECTORY",
    "GIT_ALTERNATE_OBJECT_DIRECTORIES",
    "GIT_INDEX_FILE",
    "GIT_NAMESPACE",
    "GIT_REPLACE_REF_BASE",
    "GIT_GRAFT_FILE",
}


def controlled_git_environment(
    base: Mapping[str, str] | None = None,
) -> dict[str, str]:
    """Return an environment for literal repository/object identity operations.

    This is intentionally narrower than a fully hermetic Git configuration.  It
    removes only process-level overrides that can change which repository/object
    graph/index is observed and disables replace-object resolution.  Repository
    configuration remains available; callers still select the repository explicitly
    with `git -C` or an explicit path.
    """

    env = dict(os.environ if base is None else base)
    for key in UNTRUSTED_GIT_ENVIRONMENT:
        env.pop(key, None)

    # Git's replace refs can make the same commit object name resolve to a different
    # tree.  Exact Evidence identity needs the literal object named by the SHA.
    env["GIT_NO_REPLACE_OBJECTS"] = "1"

    # New temporary repositories used by the acquisition helpers are expected to use
    # the SHA-1 object format because all fixed ISSUE-000072 Git object identities are
    # SHA-1.  An ambient GIT_DEFAULT_HASH must not silently change that format.
    env["GIT_DEFAULT_HASH"] = "sha1"
    return env
