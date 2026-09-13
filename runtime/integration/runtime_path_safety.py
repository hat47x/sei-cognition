from __future__ import annotations

from pathlib import Path


def lexical_absolute_path(path: Path) -> Path:
    """symlinkを解決せず、要求されたpathを絶対pathとして扱う。"""

    requested = path.expanduser()
    if requested.is_absolute():
        return requested
    return Path.cwd() / requested


def reject_symlink_path_or_ancestors(path: Path, label: str) -> None:
    """path自身または既存ancestorにsymlinkがあれば、副作用前に拒否する。

    `resolve()`より先に字面上のpath chainを確認することで、深いancestorにある
    symlinkを「解決済みの通常path」として見落とさない。存在しないsuffix componentは
    `Path.is_symlink()`がFalseを返すため、新規出力pathにも利用できる。
    """

    requested = lexical_absolute_path(path)
    immediate_parent = requested.parent
    current = requested

    while True:
        if current.is_symlink():
            if current == requested:
                raise ValueError(f"{label}にsymlinkは利用できません: {current}")
            if current == immediate_parent:
                raise ValueError(f"{label}のparentにsymlinkは利用できません: {current}")
            raise ValueError(
                f"{label}のancestorにsymlinkは利用できません: "
                f"ancestor={current} requested={requested}"
            )

        parent = current.parent
        if parent == current:
            break
        current = parent
