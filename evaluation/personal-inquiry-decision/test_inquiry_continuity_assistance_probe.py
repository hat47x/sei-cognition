from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from inquiry_continuity_assistance_probe import (
    AssistanceProbeError,
    RESPONSE_SCHEMA,
    build_audit_packets,
    build_initial_packets,
    build_reveal_packets,
    git_blob_sha1,
    load_sources,
    probe_content_sha256,
    response_template,
    validate_probe,
    validate_response,
)


def fixture(fid: str) -> dict:
    return {
        "schema": "sei.inquiry-continuity-comparison-fixture/v0",
        "status": "evaluation-only",
        "fixture_id": fid,
        "title": fid,
        "scenario": {
            "decision_present": False,
            "post_interruption_evidence": [],
        },
        "conditions": {
            "A_raw_chat": {"surface_text": ["raw"]},
            "B_chronological_note": {"surface_text": ["note"]},
            "C_sei_resume": {
                "surface_text": {
                    "orientation": {
                        "original_concern": fid,
                        "current_question": "q",
                        "material_observations": ["o"],
                        "open_unknowns": ["u"],
                        "hypotheses": ["h"],
                        "decision": None,
                        "next_useful_investigation": "n",
                    }
                }
            },
        },
        "reference_state": {"must_not_infer": ["certainty"]},
        "human_review_template": {
            "before_post_interruption_evidence": [],
            "after_post_interruption_evidence": [],
        },
        "review_key": {"hard_failures": ["rewrite"]},
    }


def write_fixture(
    root: Path,
    fid: str,
) -> tuple[str, str]:
    path = root / f"{fid}.json"
    raw = (
        json.dumps(
            fixture(fid),
            ensure_ascii=False,
            separators=(",", ":"),
        )
        + "\n"
    ).encode()
    path.write_bytes(raw)
    return str(path.relative_to(root)), git_blob_sha1(raw)


def make_probe(root: Path) -> dict:
    cases = []
    for fid in ("f1", "f2", "f3"):
        path, sha = write_fixture(root, fid)
        cases.append(
            {
                "fixture_id": fid,
                "path": path,
                "blob_sha1": sha,
                "suggestions": [
                    {
                        "id": "s1",
                        "priority": "primary",
                        "text": "primary",
                    },
                    {
                        "id": "s2",
                        "priority": "secondary",
                        "text": "two",
                    },
                    {
                        "id": "s3",
                        "priority": "secondary",
                        "text": "three",
                    },
                    {
                        "id": "s4",
                        "priority": "secondary",
                        "text": "four",
                    },
                    {
                        "id": "s5",
                        "priority": "secondary",
                        "text": "five",
                    },
                ],
            }
        )
    return {
        "schema": "sei.inquiry-continuity-assistance-probe/v1",
        "status": "evaluation-only",
        "issue": "ISSUE-000078",
        "probe_id": "p1",
        "semantic_stopline": {
            "suggestions_are_canonical": False,
            "quiet_may_hide_canonical_orientation": False,
            "surface_choice_is_stable_requirement": False,
            "overall_winner_allowed": False,
        },
        "presentation_rules": {
            "condition_labels_hidden_until_audit": True,
            "response_stages": ["initial", "reveal"],
            "audit_reveals_condition_mapping": True,
            "same_fixture_multiple_conditions_before_fixed_response": False,
        },
        "cases": cases,
        "conditions": {
            "A_proactive_first": {"initial_visibility": "all"},
            "B_quiet_first": {"initial_visibility": "none"},
            "C_adaptive_progressive": {
                "initial_visibility": "primary-only"
            },
        },
        "assignment_rotations": {
            "R1": [
                {
                    "fixture": "f1",
                    "condition": "A_proactive_first",
                },
                {
                    "fixture": "f2",
                    "condition": "B_quiet_first",
                },
                {
                    "fixture": "f3",
                    "condition": "C_adaptive_progressive",
                },
            ],
            "R2": [
                {
                    "fixture": "f1",
                    "condition": "B_quiet_first",
                },
                {
                    "fixture": "f2",
                    "condition": "C_adaptive_progressive",
                },
                {
                    "fixture": "f3",
                    "condition": "A_proactive_first",
                },
            ],
            "R3": [
                {
                    "fixture": "f1",
                    "condition": "C_adaptive_progressive",
                },
                {
                    "fixture": "f2",
                    "condition": "A_proactive_first",
                },
                {
                    "fixture": "f3",
                    "condition": "B_quiet_first",
                },
            ],
        },
        "review_questions": {
            "initial": [
                {"id": "Q1", "prompt": "initial one"},
                {"id": "Q2", "prompt": "initial two"},
            ],
            "reveal": [
                {"id": "Q3", "prompt": "reveal one"}
            ],
        },
        "audit_key": {
            "semantic_hard_failures": ["fail"]
        },
        "evidence_boundary": {
            "current": "executable-scaffold-only",
            "human_review": "not-yet-observed",
            "stable_requirement_change": "not-authorized",
        },
    }


class AssistanceProbeTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.probe = make_probe(self.root)
        self.fixtures = load_sources(
            self.probe,
            self.root,
        )

    def tearDown(self):
        self.tmp.cleanup()

    def _response(
        self,
        name: str,
        stage: str,
    ) -> Path:
        value = response_template(
            self.probe,
            "R1",
            stage,
        )
        for entry in value["entries"]:
            for question_id in entry["answers"]:
                entry["answers"][question_id] = "fixed"
        path = self.root / name
        path.write_text(
            json.dumps(value, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        return path

    def test_rotation_and_semantic_stoplines_validate(self):
        validate_probe(self.probe)
        self.assertEqual(
            set(self.fixtures),
            {"f1", "f2", "f3"},
        )

    def test_response_template_is_probe_bound_and_condition_blind(self):
        value = response_template(
            self.probe,
            "R1",
            "initial",
        )
        self.assertEqual(
            value["schema"],
            RESPONSE_SCHEMA,
        )
        self.assertEqual(
            value["probe_sha256"],
            probe_content_sha256(self.probe),
        )
        rendered = json.dumps(value)
        self.assertNotIn("A_proactive_first", rendered)
        self.assertNotIn("B_quiet_first", rendered)
        self.assertNotIn("C_adaptive_progressive", rendered)

    def test_initial_visibility_differs_without_exposing_condition_label(self):
        packets = build_initial_packets(
            self.probe,
            self.fixtures,
            "R1",
        )
        self.assertEqual(
            [
                len(packet["visible_ai_suggestions"])
                for packet in packets
            ],
            [5, 0, 1],
        )
        for packet in packets:
            self.assertIn("canonical_orientation", packet)
            self.assertIn("presentation_id", packet)
            self.assertNotIn("condition", packet)
            self.assertNotIn("reference_state", packet)
            self.assertNotIn("audit_key", packet)

    def test_reveal_requires_structured_fixed_initial_response(self):
        response = self._response(
            "initial.json",
            "initial",
        )
        packets = build_reveal_packets(
            self.probe,
            self.fixtures,
            "R1",
            response,
        )
        self.assertEqual(len(packets), 3)
        self.assertEqual(
            {
                len(packet["all_ai_suggestions"])
                for packet in packets
            },
            {5},
        )
        self.assertTrue(
            all(
                packet["fixed_initial_response_sha256"]
                for packet in packets
            )
        )
        self.assertTrue(
            all("condition" not in packet for packet in packets)
        )

    def test_unstructured_response_is_rejected_before_reveal(self):
        response = self.root / "bad.json"
        response.write_text(
            '{"answers":["fixed"]}\n',
            encoding="utf-8",
        )
        with self.assertRaises(AssistanceProbeError):
            build_reveal_packets(
                self.probe,
                self.fixtures,
                "R1",
                response,
            )

    def test_response_fixture_and_presentation_order_are_fixed(self):
        value = response_template(
            self.probe,
            "R1",
            "initial",
        )
        for entry in value["entries"]:
            for question_id in entry["answers"]:
                entry["answers"][question_id] = "fixed"

        changed = copy.deepcopy(value)
        changed["entries"][0]["fixture_id"] = "f2"
        with self.assertRaises(AssistanceProbeError):
            validate_response(
                changed,
                self.probe,
                "R1",
                "initial",
            )

        changed = copy.deepcopy(value)
        changed["entries"][0][
            "presentation_id"
        ] = "R1-P9"
        with self.assertRaises(AssistanceProbeError):
            validate_response(
                changed,
                self.probe,
                "R1",
                "initial",
            )

    def test_audit_reveals_condition_only_after_both_responses_fixed(self):
        initial = self._response(
            "initial.json",
            "initial",
        )
        reveal = self._response(
            "reveal.json",
            "reveal",
        )
        packets = build_audit_packets(
            self.probe,
            self.fixtures,
            "R1",
            initial,
            reveal,
        )
        self.assertEqual(
            [packet["condition"] for packet in packets],
            [
                "A_proactive_first",
                "B_quiet_first",
                "C_adaptive_progressive",
            ],
        )
        self.assertTrue(
            all("reference_state" in packet for packet in packets)
        )
        self.assertTrue(
            all("audit_key" in packet for packet in packets)
        )
        self.assertTrue(
            all(
                packet["fixed_initial_response_sha256"]
                for packet in packets
            )
        )
        self.assertTrue(
            all(
                packet["fixed_reveal_response_sha256"]
                for packet in packets
            )
        )

    def test_source_freeze_rejects_changed_fixture(self):
        (self.root / "f1.json").write_text(
            json.dumps(fixture("f1")) + " changed\n",
            encoding="utf-8",
        )
        with self.assertRaises(AssistanceProbeError):
            load_sources(
                self.probe,
                self.root,
            )

    def test_quiet_cannot_hide_canonical_orientation(self):
        changed = copy.deepcopy(self.probe)
        changed["semantic_stopline"][
            "quiet_may_hide_canonical_orientation"
        ] = True
        with self.assertRaises(AssistanceProbeError):
            validate_probe(changed)

    def test_condition_labels_cannot_be_unblinded_before_audit(self):
        changed = copy.deepcopy(self.probe)
        changed["presentation_rules"][
            "condition_labels_hidden_until_audit"
        ] = False
        with self.assertRaises(AssistanceProbeError):
            validate_probe(changed)

    def test_each_case_requires_one_primary_suggestion(self):
        changed = copy.deepcopy(self.probe)
        changed["cases"][0]["suggestions"][1][
            "priority"
        ] = "primary"
        with self.assertRaises(AssistanceProbeError):
            validate_probe(changed)


if __name__ == "__main__":
    unittest.main()
