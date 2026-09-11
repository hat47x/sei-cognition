#!/usr/bin/env python3
"""Validate the method-quality case catalog without scoring semantic quality.

The catalog deliberately contains review focuses rather than golden groupings.
This validator checks only catalog integrity and the boundary that prevents an
expected grouping from becoming a machine-authoritative answer.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


SCHEMA = "sei.method-quality-case-catalog/v1"
FORBIDDEN_GOLDEN_KEYS = {
    "expectedGroups",
    "expectedGrouping",
    "goldenGroups",
    "goldenGrouping",
    "expectedLabel",
    "expectedLabels",
    "qualityScore",
}


def _require_non_empty_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value


def validate_catalog(catalog: dict[str, Any]) -> None:
    if catalog.get("schema") != SCHEMA:
        raise ValueError(f"schema must be {SCHEMA!r}")

    rules = catalog.get("rules")
    if not isinstance(rules, dict):
        raise ValueError("rules must be an object")
    if rules.get("goldenGrouping") is not False:
        raise ValueError("rules.goldenGrouping must be false")
    if rules.get("machineScoring") is not False:
        raise ValueError("rules.machineScoring must be false")
    if rules.get("humanReviewRequiredForOutcomeQuality") is not True:
        raise ValueError("rules.humanReviewRequiredForOutcomeQuality must be true")

    cases = catalog.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("cases must be a non-empty array")

    case_ids: set[str] = set()
    for case_index, case in enumerate(cases):
        if not isinstance(case, dict):
            raise ValueError(f"cases[{case_index}] must be an object")

        forbidden = FORBIDDEN_GOLDEN_KEYS.intersection(case)
        if forbidden:
            raise ValueError(
                f"cases[{case_index}] must not define machine-authoritative golden fields: "
                + ", ".join(sorted(forbidden))
            )

        case_id = _require_non_empty_string(case.get("id"), f"cases[{case_index}].id")
        if case_id in case_ids:
            raise ValueError(f"duplicate case id: {case_id}")
        case_ids.add(case_id)
        _require_non_empty_string(case.get("title"), f"cases[{case_index}].title")

        cards = case.get("cards")
        if not isinstance(cards, list) or len(cards) < 2:
            raise ValueError(f"cases[{case_index}].cards must contain at least two cards")

        card_ids: set[str] = set()
        for card_index, card in enumerate(cards):
            if not isinstance(card, dict):
                raise ValueError(
                    f"cases[{case_index}].cards[{card_index}] must be an object"
                )
            card_id = _require_non_empty_string(
                card.get("id"), f"cases[{case_index}].cards[{card_index}].id"
            )
            if card_id in card_ids:
                raise ValueError(f"duplicate card id in {case_id}: {card_id}")
            card_ids.add(card_id)
            _require_non_empty_string(
                card.get("text"), f"cases[{case_index}].cards[{card_index}].text"
            )
            if "holdState" in card and card["holdState"] != "held":
                raise ValueError(
                    f"cases[{case_index}].cards[{card_index}].holdState must be 'held' when present"
                )

        review_focus = case.get("reviewFocus")
        if not isinstance(review_focus, list) or not review_focus:
            raise ValueError(f"cases[{case_index}].reviewFocus must be a non-empty array")
        for focus_index, focus in enumerate(review_focus):
            _require_non_empty_string(
                focus, f"cases[{case_index}].reviewFocus[{focus_index}]"
            )


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"usage: {argv[0]} CASE_CATALOG.json", file=sys.stderr)
        return 2

    path = Path(argv[1])
    catalog = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(catalog, dict):
        raise ValueError("catalog root must be an object")
    validate_catalog(catalog)
    print(
        json.dumps(
            {
                "schema": "sei.method-quality-case-catalog-validation/v1",
                "catalog": str(path),
                "caseCount": len(catalog["cases"]),
                "qualityJudgement": "not_evaluated",
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
