from __future__ import annotations

import copy
import unittest
from pathlib import Path

from inquiry_continuity_review_analysis import response_template
from inquiry_continuity_review_evidence import (
    InquiryEvidenceBundleError,
    build_evidence_bundle,
)
from inquiry_continuity_review_runner import (
    load_context,
    record_checked_response,
)
from matched_review_session import new_session

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = (
    ROOT
    / "evaluation/personal-inquiry-decision/"
    / "inquiry_continuity_counterfactual_matched_set_v1.json"
)


def completed_session() -> tuple[dict, dict, dict[str, dict]]:
    manifest, fixtures = load_context(MANIFEST, ROOT)
    session = new_session(
        manifest,
        fixtures,
        "R1",
        "evidence-bundle-unit-test",
        "2031-01-01T00:00:00+00:00",
    )
    for stage, minute in (("phase1", 0), ("post", 1), ("audit", 2)):
        fixture_ids = [item["fixture_id"] for item in session["assignments"]]
        for index, fixture_id in enumerate(fixture_ids):
            response = response_template(stage, fixtures[fixture_id])
            if "answers" in response:
                response["answers"] = [
                    f"unit-test-{stage}-{i + 1}"
                    for i in range(len(response["answers"]))
                ]
            session = record_checked_response(
                session,
                manifest,
                fixtures,
                fixture_id,
                stage,
                f"2031-01-01T00:{minute:02d}:{index + 1:02d}+00:00",
                response,
            )
    return session, manifest, fixtures


class InquiryContinuityReviewEvidenceTest(unittest.TestCase):
    def test_completed_session_is_split_into_distinct_layers(self):
        session, manifest, fixtures = completed_session()
        bundle = build_evidence_bundle(session, manifest, fixtures)

        self.assertEqual(
            bundle["schema"],
            "sei.inquiry-continuity-review-evidence-bundle/v0",
        )
        self.assertEqual(len(bundle["human_review_observations"]), 3)
        self.assertEqual(len(bundle["semantic_audits"]), 3)
        for item in bundle["human_review_observations"]:
            self.assertEqual(
                set(item),
                {"fixture_id", "condition", "phase1", "post"},
            )
            self.assertNotIn("audit", item)
        for item in bundle["semantic_audits"]:
            self.assertEqual(
                set(item),
                {"fixture_id", "condition", "audit"},
            )
            self.assertNotIn("phase1", item)
            self.assertNotIn("post", item)

    def test_bundle_does_not_mutate_completed_session(self):
        session, manifest, fixtures = completed_session()
        before = copy.deepcopy(session)
        bundle = build_evidence_bundle(session, manifest, fixtures)
        bundle["human_review_observations"][0]["phase1"]["response"]["answers"][0] = (
            "changed in projection"
        )
        self.assertEqual(session, before)

    def test_incomplete_session_is_rejected(self):
        manifest, fixtures = load_context(MANIFEST, ROOT)
        session = new_session(
            manifest,
            fixtures,
            "R1",
            "incomplete-evidence-bundle-unit-test",
            "2031-01-01T00:00:00+00:00",
        )
        with self.assertRaises(InquiryEvidenceBundleError):
            build_evidence_bundle(session, manifest, fixtures)

    def test_bundle_keeps_product_value_stopline(self):
        session, manifest, fixtures = completed_session()
        bundle = build_evidence_bundle(session, manifest, fixtures)
        self.assertEqual(
            bundle["evidence_boundaries"]["product_value"],
            "not-established-by-this-artifact",
        )
        serialized = repr(bundle).lower()
        self.assertNotIn("overall_score", serialized)
        self.assertNotIn("preferred_condition", serialized)


if __name__ == "__main__":
    unittest.main()
