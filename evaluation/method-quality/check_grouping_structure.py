#!/usr/bin/env python3
"""Cognitive Method grouping resultの構造不変条件だけを検査する。

このcheckerはgroupingの意味的品質、KJ法としての妥当性、labelやrationaleの
良し悪しを採点しない。人間が成果品質をレビューする前提となるidentityと
held状態などが壊れていないかだけを検査する。
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

REPORT_SCHEMA = "sei.method-quality-structure-report/v1"


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _duplicates(values: list[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return sorted(duplicates)


def inspect_grouping_structure(
    request_body: dict[str, Any],
    result_body: dict[str, Any],
    *,
    request_bytes: bytes = b"",
    result_bytes: bytes = b"",
) -> dict[str, Any]:
    """意味的品質を判定せず、grouping resultの構造だけを検査する。"""

    violations: list[dict[str, Any]] = []

    request_cards = request_body.get("cards")
    if not isinstance(request_cards, list):
        request_cards = []
        violations.append({"code": "request_cards_not_list"})

    input_ids: list[str] = []
    for index, card in enumerate(request_cards):
        if not isinstance(card, dict) or not isinstance(card.get("id"), str) or not card["id"]:
            violations.append({"code": "invalid_request_card_id", "index": index})
            continue
        input_ids.append(card["id"])

    for card_id in _duplicates(input_ids):
        violations.append({"code": "duplicate_request_card_id", "cardId": card_id})

    input_set = set(input_ids)

    doc = request_body.get("doc")
    doc_cards = doc.get("cards", []) if isinstance(doc, dict) else []
    held_ids: list[str] = []
    if isinstance(doc_cards, list):
        for card in doc_cards:
            if (
                isinstance(card, dict)
                and card.get("holdState") == "held"
                and isinstance(card.get("id"), str)
                and card["id"]
            ):
                held_ids.append(card["id"])
    else:
        violations.append({"code": "doc_cards_not_list"})

    held_set = set(held_ids)
    for held_id in sorted(held_set - input_set):
        violations.append({"code": "held_card_not_in_request", "cardId": held_id})

    groups = result_body.get("groups")
    if not isinstance(groups, list):
        groups = []
        violations.append({"code": "groups_not_list"})

    grouped_ids: list[str] = []
    for group_index, group in enumerate(groups):
        if not isinstance(group, dict):
            violations.append({"code": "group_not_object", "groupIndex": group_index})
            continue

        label = group.get("label")
        if not isinstance(label, str) or not label.strip():
            violations.append({"code": "empty_group_label", "groupIndex": group_index})

        card_ids = group.get("cardIds")
        if not isinstance(card_ids, list):
            violations.append({"code": "group_card_ids_not_list", "groupIndex": group_index})
            continue
        if not card_ids:
            violations.append({"code": "empty_group", "groupIndex": group_index})

        for card_id in card_ids:
            if not isinstance(card_id, str) or not card_id:
                violations.append(
                    {"code": "invalid_group_card_id", "groupIndex": group_index}
                )
                continue
            grouped_ids.append(card_id)
            if card_id not in input_set:
                violations.append(
                    {
                        "code": "group_card_not_in_request",
                        "groupIndex": group_index,
                        "cardId": card_id,
                    }
                )
            if card_id in held_set:
                violations.append(
                    {
                        "code": "held_card_reintroduced",
                        "groupIndex": group_index,
                        "cardId": card_id,
                    }
                )

    for card_id in _duplicates(grouped_ids):
        violations.append({"code": "duplicate_group_membership", "cardId": card_id})

    excluded = result_body.get("excludedCardIds")
    if not isinstance(excluded, list):
        excluded = []
        violations.append({"code": "excluded_card_ids_not_list"})

    excluded_ids: list[str] = []
    for index, card_id in enumerate(excluded):
        if not isinstance(card_id, str) or not card_id:
            violations.append({"code": "invalid_excluded_card_id", "index": index})
            continue
        excluded_ids.append(card_id)
        if card_id not in input_set:
            violations.append({"code": "excluded_card_not_in_request", "cardId": card_id})

    for card_id in _duplicates(excluded_ids):
        violations.append({"code": "duplicate_excluded_card_id", "cardId": card_id})

    grouped_set = set(grouped_ids)
    excluded_set = set(excluded_ids)
    for card_id in sorted(grouped_set & excluded_set):
        violations.append({"code": "card_both_grouped_and_excluded", "cardId": card_id})

    for held_id in sorted(held_set - excluded_set):
        violations.append({"code": "held_card_missing_from_excluded", "cardId": held_id})

    return {
        "schema": REPORT_SCHEMA,
        "status": "passed" if not violations else "failed",
        "requestSha256": _sha256(request_bytes),
        "resultSha256": _sha256(result_bytes),
        "inputCardCount": len(input_ids),
        "heldCardCount": len(held_set),
        "groupCount": len(groups),
        "groupedCardCount": len(grouped_set),
        "excludedCardCount": len(excluded_set),
        "violations": violations,
        "qualityJudgement": "not_evaluated",
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="KJ grouping resultの構造不変条件を検査します。意味的品質は採点しません。"
    )
    parser.add_argument("--request", required=True, type=Path)
    parser.add_argument("--result", required=True, type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    request_bytes = args.request.read_bytes()
    result_bytes = args.result.read_bytes()
    try:
        request_body = json.loads(request_bytes.decode("utf-8"))
        result_body = json.loads(result_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SystemExit(f"入力JSONを読み取れません: {exc}") from exc

    if not isinstance(request_body, dict) or not isinstance(result_body, dict):
        raise SystemExit("request / resultはJSON objectである必要があります")

    report = inspect_grouping_structure(
        request_body,
        result_body,
        request_bytes=request_bytes,
        result_bytes=result_bytes,
    )
    encoded = json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
