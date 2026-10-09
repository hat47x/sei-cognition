#!/usr/bin/env python3
"""Evaluation-only SEI consumer for TEI context-scoped epistemic projections.

This module intentionally does not reimplement TEI epistemic state transitions.
It consumes TEI's projection and applies SEI-side fail-closed routing before
information can enter a cognition/context-assembly premise lane.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

INPUT_CONTRACT = "tei.epistemic-projection/v0"
INPUT_SCHEMA = "tei.reference.epistemic-assessment/v0"
OUTPUT_SCHEMA = "sei.epistemic-routing-evaluation/v0"
EGRESS_PLAN_SCHEMA = "sei.context-egress-plan-evaluation/v0"

ALLOWED_USE_STATES = {"premise", "candidate-only", "review-required", "blocked"}
ALLOWED_METADATA_STATES = {"complete", "partial", "absent"}
ALLOWED_TARGET_BINDINGS = {
    "not-required",
    "exact",
    "reanchored",
    "ambiguous",
    "detached",
}
ALLOWED_CONTEXT_COMPATIBILITY = {"compatible", "incompatible", "unknown"}
ALLOWED_FRESHNESS = {"current", "stale", "not-yet-valid", "unknown"}
ALLOWED_CONFLICT = {"none", "inactive", "present"}
ALLOWED_RESOLUTION_COVERAGE_STATES = {
    "not-configured",
    "unknown",
    "insufficient-sample",
    "healthy",
    "attention",
}

REQUIRED_AUTHORITY_LIMITS = {
    "assessment-does-not-assert-objective-truth",
    "assessment-does-not-grant-canonical-acceptance",
    "reviewer-candidate-is-not-review-authority",
    "content-fingerprint-does-not-restore-review-history",
    "meaning-fingerprint-is-input-not-semantic-proof",
    "assessment-does-not-grant-write-or-runtime-authority",
    "target-anchor-resolution-does-not-prove-semantic-identity",
    "coverage-mapping-is-input-not-semantic-completeness-proof",
    "resolution-coverage-is-operational-readiness-not-truth-ratio",
    "partial-transport-health-is-not-project-wide-health",
    "review-history-is-bounded-by-context-as-of",
    "review-binding-includes-context-kind-and-target-identity",
    "review-binding-includes-validity-window",
    "checked-at-is-bound-to-current-subject",
}


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def _require_object(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be an object")
    return value


def _require_list(value: Any, name: str) -> list[Any]:
    if not isinstance(value, list):
        raise ValueError(f"{name} must be a list")
    return value


def _require_string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{name} must be a non-empty string")
    return value


def validate_projection(projection: dict[str, Any]) -> None:
    if projection.get("contract") != INPUT_CONTRACT:
        raise ValueError(f"contract must be {INPUT_CONTRACT}")
    if projection.get("schema") != INPUT_SCHEMA:
        raise ValueError(f"schema must be {INPUT_SCHEMA}")

    authority_limits = _require_list(
        projection.get("authorityLimits"), "authorityLimits"
    )
    if not all(isinstance(item, str) for item in authority_limits):
        raise ValueError("authorityLimits must contain strings")
    missing_limits = REQUIRED_AUTHORITY_LIMITS - set(authority_limits)
    if missing_limits:
        raise ValueError(
            "projection is missing required authority limits: "
            + ", ".join(sorted(missing_limits))
        )

    assessments = _require_list(projection.get("assessments"), "assessments")
    if not assessments:
        raise ValueError("assessments must not be empty")

    seen_ids: set[str] = set()
    for index, raw in enumerate(assessments):
        assessment = _require_object(raw, f"assessments[{index}]")
        assertion_id = _require_string(
            assessment.get("assertionId"), f"assessments[{index}].assertionId"
        )
        if assertion_id in seen_ids:
            raise ValueError(f"duplicate assertionId: {assertion_id}")
        seen_ids.add(assertion_id)

        meaning_fingerprint = _require_string(
            assessment.get("meaningFingerprint"),
            f"assessments[{index}].meaningFingerprint",
        )
        if (
            not meaning_fingerprint.startswith("sha256:")
            or len(meaning_fingerprint) != 71
            or any(ch not in "0123456789abcdef" for ch in meaning_fingerprint[7:])
        ):
            raise ValueError(
                f"assessments[{index}].meaningFingerprint must be exact sha256"
            )
        review_subject_fingerprint = _require_string(
            assessment.get("reviewSubjectFingerprint"),
            f"assessments[{index}].reviewSubjectFingerprint",
        )
        if (
            not review_subject_fingerprint.startswith("sha256:")
            or len(review_subject_fingerprint) != 71
            or any(ch not in "0123456789abcdef" for ch in review_subject_fingerprint[7:])
        ):
            raise ValueError(
                f"assessments[{index}].reviewSubjectFingerprint must be exact sha256"
            )

        review_log_sequence = assessment.get("reviewLogSequence")
        if (
            not isinstance(review_log_sequence, int)
            or isinstance(review_log_sequence, bool)
            or review_log_sequence < 0
        ):
            raise ValueError(
                f"assessments[{index}].reviewLogSequence must be a non-negative integer"
            )

        _require_string(
            assessment.get("contentOrigin"),
            f"assessments[{index}].contentOrigin",
        )
        _require_string(
            assessment.get("ingestedBy"),
            f"assessments[{index}].ingestedBy",
        )
        _require_string(
            assessment.get("statementKind"),
            f"assessments[{index}].statementKind",
        )
        _require_string(
            assessment.get("confirmationState"),
            f"assessments[{index}].confirmationState",
        )
        _require_string(
            assessment.get("reviewBinding"),
            f"assessments[{index}].reviewBinding",
        )
        _require_string(
            assessment.get("lifecycleState"),
            f"assessments[{index}].lifecycleState",
        )

        checks = (
            ("useState", ALLOWED_USE_STATES),
            ("metadataState", ALLOWED_METADATA_STATES),
            ("targetBinding", ALLOWED_TARGET_BINDINGS),
            ("contextCompatibility", ALLOWED_CONTEXT_COMPATIBILITY),
            ("freshness", ALLOWED_FRESHNESS),
            ("conflict", ALLOWED_CONFLICT),
        )
        for field, allowed in checks:
            value = assessment.get(field)
            if value not in allowed:
                raise ValueError(
                    f"assessments[{index}].{field} must be one of "
                    f"{sorted(allowed)}, got {value!r}"
                )

        reasons = assessment.get("reasons", [])
        if not isinstance(reasons, list) or not all(
            isinstance(item, str) for item in reasons
        ):
            raise ValueError(f"assessments[{index}].reasons must be a string list")

    health = _require_object(projection.get("health"), "health")
    if health.get("viewMetadataState") not in ALLOWED_METADATA_STATES:
        raise ValueError(
            "health.viewMetadataState must be complete, partial, or absent"
        )
    coverage = _require_object(health.get("coverage"), "health.coverage")
    areas = coverage.get("areas", [])
    if not isinstance(areas, list):
        raise ValueError("health.coverage.areas must be a list")
    for index, raw in enumerate(areas):
        area = _require_object(raw, f"health.coverage.areas[{index}]")
        _require_string(area.get("areaId"), f"health.coverage.areas[{index}].areaId")
        if area.get("state") not in {"mapped", "gap"}:
            raise ValueError(
                f"health.coverage.areas[{index}].state must be mapped or gap"
            )

    resolution_coverage = health.get("resolutionCoverage")
    if resolution_coverage is not None:
        resolution_coverage = _require_object(
            resolution_coverage, "health.resolutionCoverage"
        )
        for field in (
            "eligible",
            "resolved",
            "confirmed",
            "nativePremise",
            "rejected",
            "unresolved",
        ):
            value = resolution_coverage.get(field)
            if (
                not isinstance(value, int)
                or isinstance(value, bool)
                or value < 0
            ):
                raise ValueError(
                    f"health.resolutionCoverage.{field} must be a non-negative integer"
                )
        ratio = resolution_coverage.get("ratio")
        if (
            not isinstance(ratio, (int, float))
            or isinstance(ratio, bool)
            or ratio < 0
            or ratio > 1
        ):
            raise ValueError(
                "health.resolutionCoverage.ratio must be between 0 and 1"
            )
        if (
            resolution_coverage["resolved"] > resolution_coverage["eligible"]
            or resolution_coverage["unresolved"] > resolution_coverage["eligible"]
            or resolution_coverage["resolved"] + resolution_coverage["unresolved"]
            != resolution_coverage["eligible"]
        ):
            raise ValueError("health.resolutionCoverage counts are inconsistent")
        if resolution_coverage.get("state") not in ALLOWED_RESOLUTION_COVERAGE_STATES:
            raise ValueError("health.resolutionCoverage.state is unsupported")

    issues = health.get("issues", [])
    if not isinstance(issues, list):
        raise ValueError("health.issues must be a list")
    for index, raw in enumerate(issues):
        item = _require_object(raw, f"health.issues[{index}]")
        _require_string(item.get("assertionId"), f"health.issues[{index}].assertionId")
        _require_string(item.get("consumer"), f"health.issues[{index}].consumer")


def route_assessment(assessment: dict[str, Any]) -> dict[str, Any]:
    source_use_state = assessment["useState"]
    reasons = list(assessment.get("reasons", []))
    sei_reasons: list[str] = []

    route = source_use_state
    if route == "candidate-only":
        route = "candidate"
    elif route == "review-required":
        route = "review"

    # Defense in depth: malformed or future TEI producers must not smuggle an
    # unsafe "premise" past the consumer boundary. A source-side blocked state
    # remains blocked even if another signal would otherwise route to review.
    if source_use_state == "blocked":
        route = "blocked"
        sei_reasons.append("SEI_SOURCE_BLOCKED")
    elif assessment["lifecycleState"] != "active":
        route = "blocked"
        sei_reasons.append("SEI_LIFECYCLE_NOT_ACTIVE")
    elif assessment["confirmationState"] == "rejected":
        route = "blocked"
        sei_reasons.append("SEI_CONFIRMATION_REJECTED")
    elif assessment["contextCompatibility"] == "incompatible":
        route = "blocked"
        sei_reasons.append("SEI_CONTEXT_INCOMPATIBLE")
    elif assessment["freshness"] in {"stale", "not-yet-valid"}:
        route = "blocked"
        sei_reasons.append("SEI_ASSERTION_FRESHNESS_BLOCKED")
    elif assessment["metadataState"] != "complete":
        # Missing metadata must never pass as a premise. However, a source-side
        # candidate does not automatically become a human-review task merely
        # because metadata is incomplete; higher-stakes dependencies can still
        # escalate it through Health / reviewRequests.
        if source_use_state == "premise":
            route = "review"
        sei_reasons.append("SEI_METADATA_NOT_COMPLETE")
    elif assessment["targetBinding"] in {"ambiguous", "detached"}:
        route = "review"
        sei_reasons.append("SEI_TARGET_NOT_STABLY_BOUND")
    elif assessment["contextCompatibility"] == "unknown":
        route = "review"
        sei_reasons.append("SEI_CONTEXT_COMPATIBILITY_UNKNOWN")
    elif assessment["conflict"] == "present":
        route = "review"
        sei_reasons.append("SEI_CONFLICT_PRESENT")

    return {
        "assertionId": assessment["assertionId"],
        "meaningFingerprint": assessment["meaningFingerprint"],
        "reviewSubjectFingerprint": assessment["reviewSubjectFingerprint"],
        "reviewLogSequence": assessment["reviewLogSequence"],
        "route": route,
        "sourceUseState": source_use_state,
        "contentOrigin": assessment["contentOrigin"],
        "ingestedBy": assessment["ingestedBy"],
        "statementKind": assessment["statementKind"],
        "confirmationState": assessment["confirmationState"],
        "reviewBinding": assessment["reviewBinding"],
        "metadataState": assessment["metadataState"],
        "targetBinding": assessment["targetBinding"],
        "contextCompatibility": assessment["contextCompatibility"],
        "freshness": assessment["freshness"],
        "lifecycleState": assessment["lifecycleState"],
        "conflict": assessment["conflict"],
        "targetReanchored": assessment["targetBinding"] == "reanchored",
        "inferredContextUsed": bool(assessment.get("inferredContextUsed", False)),
        "sourceReasons": sorted(set(reasons)),
        "seiReasons": sorted(set(sei_reasons)),
    }


def _egress_reference(route: dict[str, Any]) -> dict[str, Any]:
    """Return an access-neutral reference plan, never assertion content."""
    return {
        "assertionId": route["assertionId"],
        "meaningFingerprint": route["meaningFingerprint"],
        "reviewSubjectFingerprint": route["reviewSubjectFingerprint"],
        "reviewLogSequence": route["reviewLogSequence"],
        "contentOrigin": route["contentOrigin"],
        "statementKind": route["statementKind"],
        "confirmationState": route["confirmationState"],
        "reviewBinding": route["reviewBinding"],
        "metadataState": route["metadataState"],
        "targetBinding": route["targetBinding"],
        "contextCompatibility": route["contextCompatibility"],
        "freshness": route["freshness"],
        "lifecycleState": route["lifecycleState"],
        "conflict": route["conflict"],
    }


def build_context_egress_plan(
    routes: list[dict[str, Any]],
    unknowns: list[dict[str, Any]],
    escalations: list[dict[str, Any]],
) -> dict[str, Any]:
    """Build a reference-only context plan from already fail-closed routes.

    The TEI projection does not carry assertion text, source content, or the
    complete access-controlled Evidence surface. Therefore this function
    selects references only. A later resolver must re-check access and the
    binding receipts before loading content.
    """
    lanes: dict[str, list[dict[str, Any]]] = {
        "premiseReferences": [],
        "candidateReferences": [],
        "reviewReferences": [],
        "blockedReferences": [],
    }
    lane_by_route = {
        "premise": "premiseReferences",
        "candidate": "candidateReferences",
        "review": "reviewReferences",
        "blocked": "blockedReferences",
    }
    for item in routes:
        lane = lane_by_route.get(item["route"])
        if lane is None:
            raise ValueError(f"unsupported routed lane: {item['route']!r}")
        lanes[lane].append(_egress_reference(item))

    for values in lanes.values():
        values.sort(key=lambda item: item["assertionId"])

    return {
        "schema": EGRESS_PLAN_SCHEMA,
        **lanes,
        "projectUnknowns": [dict(item) for item in unknowns],
        "escalations": [dict(item) for item in escalations],
        "contentResolution": {
            "required": True,
            "reason": "routing projection contains references and epistemic signals, not assertion content",
        },
        "authorityLimits": [
            "egress-plan-selects-references-not-content",
            "candidate-reference-is-not-premise",
            "review-and-blocked-references-are-not-context-premises",
            "content-resolution-must-recheck-access-and-binding",
        ],
    }


def route_projection(projection: dict[str, Any]) -> dict[str, Any]:
    validate_projection(projection)

    routes = [route_assessment(item) for item in projection["assessments"]]
    routes.sort(key=lambda item: item["assertionId"])

    health = projection["health"]
    view_state = health["viewMetadataState"]
    project_health_scope = "complete" if view_state == "complete" else "partial"

    unknowns: list[dict[str, Any]] = []
    escalations: list[dict[str, Any]] = []

    if project_health_scope == "partial":
        unknowns.append(
            {
                "kind": "partial-health-view",
                "reason": "visible health is not project-wide health",
            }
        )

    for area in health.get("coverage", {}).get("areas", []):
        if area.get("state") != "gap":
            continue
        unknown = {
            "kind": "coverage-gap",
            "areaId": area["areaId"],
            "criticality": area.get("criticality", "normal"),
            "reasons": sorted(set(area.get("reasons", []))),
        }
        unknowns.append(unknown)
        if area.get("criticality") in {"high", "critical"}:
            escalations.append(
                {
                    "kind": "coverage-gap",
                    "areaId": area["areaId"],
                    "criticality": area.get("criticality"),
                    "reasons": unknown["reasons"],
                }
            )

    for issue in health.get("issues", []):
        criticality = issue.get("criticality", "normal")
        if criticality not in {"high", "critical"}:
            continue
        escalations.append(
            {
                "kind": "health-issue",
                "assertionId": issue["assertionId"],
                "consumer": issue["consumer"],
                "criticality": criticality,
                "consumerFreshness": issue.get("consumerFreshness"),
                "reasons": sorted(set(issue.get("reasons", []))),
            }
        )

    for request in projection.get("reviewRequests", []):
        if not isinstance(request, dict):
            raise ValueError("reviewRequests must contain objects")
        escalations.append(
            {
                "kind": "review-request",
                "assertionId": _require_string(
                    request.get("assertionId"), "reviewRequests[].assertionId"
                ),
                "targetBinding": request.get("targetBinding"),
                "reasons": sorted(set(request.get("reasons", []))),
                "downstreamImpact": sorted(
                    set(request.get("downstreamImpact", []))
                ),
            }
        )

    unknowns.sort(key=lambda item: (item["kind"], item.get("areaId", "")))
    escalations.sort(
        key=lambda item: (
            item["kind"],
            item.get("assertionId", ""),
            item.get("areaId", ""),
            item.get("consumer", ""),
        )
    )

    context_egress_plan = build_context_egress_plan(routes, unknowns, escalations)

    return {
        "schema": OUTPUT_SCHEMA,
        "sourceContract": projection["contract"],
        "sourceSchema": projection["schema"],
        "projectHealth": {
            "sourceLevel": health.get("level", "unknown"),
            "scope": project_health_scope,
            "viewMetadataState": view_state,
            "resolutionCoverage": health.get("resolutionCoverage"),
        },
        "routes": routes,
        "unknowns": unknowns,
        "escalations": escalations,
        "contextEgressPlan": context_egress_plan,
        "authorityLimits": [
            "sei-routing-does-not-assert-objective-truth",
            "sei-routing-does-not-grant-decision-or-write-authority",
            "semantic-similarity-does-not-upgrade-confirmation",
            "reanchored-target-is-not-semantic-identity-proof",
            "partial-health-view-is-not-project-wide-health",
            "resolution-coverage-does-not-upgrade-routing",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("projection", type=Path)
    args = parser.parse_args(argv)

    try:
        document = load_json(args.projection)
        projection = document.get("projection", document)
        if not isinstance(projection, dict):
            raise ValueError("projection must be an object")
        routed = route_projection(projection)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    json.dump(routed, sys.stdout, ensure_ascii=False, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
