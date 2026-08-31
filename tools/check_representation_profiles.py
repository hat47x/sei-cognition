#!/usr/bin/env python3
"""SOZA Representation ProfileのDefinitionと固定fixtureを検査する。"""

from __future__ import annotations

import base64
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE_DOCS = {
    "soza.jcs+sha256/v1alpha1": ROOT / "contracts/profiles/SOZA_JCS_SHA256_PROFILE_v1alpha1.md",
    "soza.raw-bytes+sha256/v1alpha1": ROOT / "contracts/profiles/SOZA_RAW_BYTES_SHA256_PROFILE_v1alpha1.md",
}
JCS_FIXTURE = ROOT / "fixtures/representation-profiles/jcs-v1alpha1.json"
RAW_FIXTURE = ROOT / "fixtures/representation-profiles/raw-bytes-v1alpha1.json"
DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


def digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def check_profile_docs(errors: list[str]) -> None:
    for profile_id, path in PROFILE_DOCS.items():
        require(path.is_file(), f"Profile Definitionがありません: {path.relative_to(ROOT)}", errors)
        if path.is_file():
            text = path.read_text(encoding="utf-8")
            require(profile_id in text, f"Profile IDがDefinition本文にありません: {profile_id}", errors)
            require("Natural Japanese review" in text, f"自然な日本語レビュー節がありません: {path.name}", errors)


def check_jcs(errors: list[str]) -> int:
    data = load(JCS_FIXTURE)
    require(data.get("profile_id") == "soza.jcs+sha256/v1alpha1", "JCS fixtureのprofile_idが不正です。", errors)
    require(data.get("digest_algorithm") == "sha256", "JCS fixtureのdigest_algorithmが不正です。", errors)

    cases = data.get("cases") or []
    ids = [case.get("id") for case in cases]
    require(len(ids) == len(set(ids)), "JCS fixture IDが重複しています。", errors)

    by_id = {case.get("id"): case for case in cases}
    verified = 0
    for case in cases:
        case_id = case.get("id", "<unknown>")
        expect = case.get("expect")
        if expect == "verified":
            verified += 1
            canonical = case.get("expected_canonical")
            expected_digest = case.get("expected_digest")
            require(isinstance(canonical, str), f"{case_id}: expected_canonicalがありません。", errors)
            require(isinstance(expected_digest, str) and bool(DIGEST_RE.fullmatch(expected_digest)), f"{case_id}: expected_digest形式が不正です。", errors)
            if isinstance(canonical, str):
                try:
                    json.loads(canonical)
                except json.JSONDecodeError as exc:
                    errors.append(f"{case_id}: expected_canonicalがJSONとして不正です: {exc}")
                else:
                    if isinstance(expected_digest, str):
                        require(digest(canonical.encode("utf-8")) == expected_digest, f"{case_id}: canonical bytesとexpected_digestが一致しません。", errors)

    duplicate = by_id.get("JCS-003-duplicate-key")
    require(duplicate is not None and duplicate.get("expect") == "invalid_representation", "duplicate key negative fixtureがありません。", errors)

    unsafe = by_id.get("JCS-004-unsafe-large-integer")
    require(unsafe is not None and unsafe.get("expect") == "invalid_semantic_number", "unsafe integer negative fixtureがありません。", errors)
    if unsafe:
        require("9007199254740993" in str(unsafe.get("input", "")), "unsafe integer fixtureがsafe-integer境界を越えていません。", errors)

    nfc = by_id.get("JCS-005-unicode-nfc")
    nfd = by_id.get("JCS-006-unicode-nfd")
    require(nfc is not None and nfd is not None, "NFC / NFD fixtureが不足しています。", errors)
    if nfc and nfd:
        nfc_canonical = nfc.get("expected_canonical", "")
        nfd_canonical = nfd.get("expected_canonical", "")
        require(nfc_canonical != nfd_canonical, "NFC / NFD fixtureが同じcanonical textになっています。", errors)
        require(unicodedata.normalize("NFC", nfc_canonical) == unicodedata.normalize("NFC", nfd_canonical), "NFC / NFD fixtureが同じ文字列の正規化差を表していません。", errors)
        require(nfc.get("expected_digest") != nfd.get("expected_digest"), "Unicode normalizationを行わない境界をdigest差で確認できません。", errors)

    return verified


def check_raw(errors: list[str]) -> int:
    data = load(RAW_FIXTURE)
    require(data.get("profile_id") == "soza.raw-bytes+sha256/v1alpha1", "raw-bytes fixtureのprofile_idが不正です。", errors)
    require(data.get("digest_algorithm") == "sha256", "raw-bytes fixtureのdigest_algorithmが不正です。", errors)

    cases = data.get("cases") or []
    ids = [case.get("id") for case in cases]
    require(len(ids) == len(set(ids)), "raw-bytes fixture IDが重複しています。", errors)

    checked = 0
    for case in cases:
        case_id = case.get("id", "<unknown>")
        try:
            payload = base64.b64decode(case.get("bytes_base64", ""), validate=True)
        except Exception as exc:
            errors.append(f"{case_id}: bytes_base64をdecodeできません: {exc}")
            continue
        expected_digest = case.get("expected_digest")
        require(isinstance(expected_digest, str) and bool(DIGEST_RE.fullmatch(expected_digest)), f"{case_id}: expected_digest形式が不正です。", errors)
        if isinstance(expected_digest, str):
            require(digest(payload) == expected_digest, f"{case_id}: raw bytes digestが一致しません。", errors)
        checked += 1
    return checked


def main() -> int:
    errors: list[str] = []
    check_profile_docs(errors)
    jcs_verified = check_jcs(errors)
    raw_checked = check_raw(errors)

    if errors:
        print("representation profile fixture check: FAILED", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"representation profile fixture check: PASS (JCS verified vectors={jcs_verified}, raw vectors={raw_checked})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
