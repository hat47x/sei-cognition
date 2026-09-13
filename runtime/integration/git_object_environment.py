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
    # These environment-level configuration injection mechanisms have higher
    # precedence than repository config.  They can silently override settings such
    # as core.autocrlf even after an acquisition helper fixed that setting locally.
    "GIT_CONFIG_COUNT",
    "GIT_CONFIG_PARAMETERS",
}


def _remove_environment_config_injection(env: dict[str, str]) -> None:
    # GIT_CONFIG_COUNT uses numbered KEY_n / VALUE_n variables.  Do not trust COUNT
    # to enumerate them because an inconsistent or malicious environment may leave
    # additional numbered entries behind.
    for key in list(env):
        if key.startswith("GIT_CONFIG_KEY_") or key.startswith("GIT_CONFIG_VALUE_"):
            env.pop(key, None)


def controlled_git_environment(
    base: Mapping[str, str] | None = None,
) -> dict[str, str]:
    """Return an environment for literal repository/object identity operations.

    This is intentionally narrower than a fully hermetic Git configuration.  It
    removes process-level overrides that can change which repository/object graph or
    index is observed, plus environment-level config injection that can override the
    repository settings used to materialize source bytes.  Repository, global, and
    system configuration remain available; callers still select the repository
    explicitly with `git -C` or an explicit path.
    """

    env = dict(os.environ if base is None else base)
    for key in UNTRUSTED_GIT_ENVIRONMENT:
        env.pop(key, None)
    _remove_environment_config_injection(env)

    # Git's replace refs can make the same commit object name resolve to a different
    # tree.  Exact Evidence identity needs the literal object named by the SHA.
    env["GIT_NO_REPLACE_OBJECTS"] = "1"

    # New temporary repositories used by the acquisition helpers are expected to use
    # the SHA-1 object format because all fixed ISSUE-000072 Git object identities are
    # SHA-1.  An ambient GIT_DEFAULT_HASH must not silently change that format.
    env["GIT_DEFAULT_HASH"] = "sha1"
    return env
