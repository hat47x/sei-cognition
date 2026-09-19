from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SACS_DIR = HERE.parent
INTERPRETATION_DIR = SACS_DIR / "cross-stage-interpretation"
RESULT_DIR = SACS_DIR / "cross-stage-result"
RUN_DIR = SACS_DIR / "cross-stage-run"
FREEZE_DIR = SACS_DIR / "cross-stage-freeze"

for path in (
    HERE,
    SACS_DIR,
    INTERPRETATION_DIR,
    RESULT_DIR,
    RUN_DIR,
    FREEZE_DIR,
):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from freeze_manifests import freeze_documents, load_directory  # noqa: E402
from test_validate_evaluation_run import (  # noqa: E402
    authorized_run,
    frozen_prereg,
    synthetic_freeze_draft,
)
from test_validate_interpretation import interpreted  # noqa: E402
from test_validate_result import completed_result  # noqa: E402
from validate_decision import (  # noqa: E402
    canonical_decision_digest,
    validate_decided_artifact,
    validate_decision_structure,
)

DECISION_PATH = HERE / "decision.json"
INTERPRETATION_PATH = INTERPRETATION_DIR / "interpretation.json"
RESULT_PATH = RESULT_DIR / "result.json"
RUN_PATH = RUN_DIR / "evaluation_run.json"
PREREG_PATH = SACS_DIR / "cross_stage_benchmark_preregistration.json"


def decided(
    interpretation: dict,
    *,
    disposition: str = "retain-current-stage",
) -> dict:
    document = json.loads(DECISION_PATH.read_text(encoding="utf-8"))
    document.update({
        "state": "decided",
        "decision_id": "decision:fixture:001",
        "decided_at": "2026-09-18T11:50:00Z",
        "disposition": disposition,
        "scope": copy.deepcopy(interpretation["scope"]),
        "rationale_refs": ["analysis:decision:fixture:001"],
        "limitations_acknowledged": copy.deepcopy(
            interpretation["limitations"]
        ),
        "b5_entry_condition_assessed": True,
        "b5_review_requested": disposition == "request-b5-review",
    })
    document["interpretation_binding"]["digest"] = interpretation[
        "interpretation_digest"
    ]
    document["decision_authority"] = {
        "ref": "decision-authority:fixture:001",
        "commit": "d" * 40,
    }
    document["decision_digest"] = canonical_decision_digest(document)
    return document


def refresh_digest(document: dict) -> None:
    document["decision_digest"] = canonical_decision_digest(document)


class CrossStageDecisionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.current_decision = json.loads(
            DECISION_PATH.read_text(encoding="utf-8")
        )
        self.current_interpretation = json.loads(
            INTERPRETATION_PATH.read_text(encoding="utf-8")
        )
        self.current_result = json.loads(
            RESULT_PATH.read_text(encoding="utf-8")
        )
        self.current_run = json.loads(
            RUN_PATH.read_text(encoding="utf-8")
        )
        self.current_prereg = json.loads(
            PREREG_PATH.read_text(encoding="utf-8")
        )
        self.current_freeze = load_directory(FREEZE_DIR)

        self.frozen = freeze_documents(
            synthetic_freeze_draft(),
            "2026-09-18T11:20:00Z",
        )
        self.prereg = frozen_prereg(self.frozen)
        self.prereg["evaluation_run"].update({
            "state": "authorized",
            "current_run_authorized": True,
        })
        self.run = authorized_run(
            self.frozen,
            metrics=["recall_at_k", "observed_winner_share"],
        )
        self.result = completed_result(self.run)
        self.interpretation = interpreted(self.result)

    def validate(
        self,
        document: dict,
        *,
        interpretation: dict | None = None,
    ) -> list[str]:
        return validate_decided_artifact(
            document,
            interpretation or self.interpretation,
            self.result,
            self.run,
            self.prereg,
            self.frozen,
        )

    def assert_error(self, errors: list[str], fragment: str) -> None:
        self.assertTrue(
            any(fragment in error for error in errors),
            f"expected {fragment!r}; got {errors!r}",
        )

    def test_current_draft_decision_is_structurally_valid(self) -> None:
        self.assertEqual(
            validate_decision_structure(self.current_decision),
            [],
        )

    def test_current_draft_upstream_cannot_support_decided_artifact(self) -> None:
        document = decided(self.interpretation)
        errors = validate_decided_artifact(
            document,
            self.interpretation,
            self.current_result,
            self.current_run,
            self.current_prereg,
            self.current_freeze,
        )
        self.assert_error(errors, "interpreted artifact:")

    def test_synthetic_retain_current_stage_decision_is_valid(self) -> None:
        self.assertEqual(self.validate(decided(self.interpretation)), [])

    def test_synthetic_defer_for_evidence_decision_is_valid(self) -> None:
        document = decided(
            self.interpretation,
            disposition="defer-for-evidence",
        )
        self.assertEqual(self.validate(document), [])
        self.assertFalse(document["b5_review_requested"])

    def test_synthetic_request_b5_review_is_valid_without_opening_gate(self) -> None:
        document = decided(
            self.interpretation,
            disposition="request-b5-review",
        )
        self.assertEqual(self.validate(document), [])
        self.assertTrue(document["b5_review_requested"])
        self.assertFalse(document["b5_gate_opened"])

    def test_interpretation_digest_binding_is_exact(self) -> None:
        document = decided(self.interpretation)
        document["interpretation_binding"]["digest"] = "0" * 64
        refresh_digest(document)
        self.assert_error(
            self.validate(document),
            "does not match interpreted artifact digest",
        )

    def test_scope_track_must_match_interpretation(self) -> None:
        document = decided(self.interpretation)
        document["scope"]["track"] = "routing"
        refresh_digest(document)
        self.assert_error(self.validate(document), "scope.track must match")

    def test_scope_variant_must_match_interpretation(self) -> None:
        document = decided(self.interpretation)
        document["scope"]["variant"] = "B0"
        refresh_digest(document)
        self.assert_error(self.validate(document), "scope.variant must match")

    def test_scope_capacity_must_match_interpretation(self) -> None:
        document = decided(self.interpretation)
        document["scope"]["capacity_profile"] = "large"
        refresh_digest(document)
        self.assert_error(
            self.validate(document),
            "scope.capacity_profile must match",
        )

    def test_scope_stress_policy_must_match_interpretation(self) -> None:
        run = authorized_run(
            self.frozen,
            capacity_profile="oversized-stress",
            stress_policy="cap128",
            metrics=["oversized_residual_policy_stress"],
        )
        result = completed_result(run)
        interpretation = interpreted(result)
        document = decided(interpretation)
        document["scope"]["stress_policy"] = "cap64"
        refresh_digest(document)
        errors = validate_decided_artifact(
            document,
            interpretation,
            result,
            run,
            self.prereg,
            self.frozen,
        )
        self.assert_error(errors, "scope.stress_policy must match")

    def test_decision_authority_ref_is_required(self) -> None:
        document = decided(self.interpretation)
        document["decision_authority"]["ref"] = ""
        refresh_digest(document)
        self.assert_error(
            self.validate(document),
            "canonical decision_authority.ref",
        )

    def test_decision_authority_commit_is_required(self) -> None:
        document = decided(self.interpretation)
        document["decision_authority"]["commit"] = "main"
        refresh_digest(document)
        self.assert_error(
            self.validate(document),
            "40-char lowercase git SHA",
        )

    def test_rationale_ref_is_required(self) -> None:
        document = decided(self.interpretation)
        document["rationale_refs"] = []
        refresh_digest(document)
        self.assert_error(
            self.validate(document),
            "at least one rationale_ref",
        )

    def test_rationale_refs_must_be_unique(self) -> None:
        document = decided(self.interpretation)
        document["rationale_refs"].append(
            document["rationale_refs"][0]
        )
        refresh_digest(document)
        self.assert_error(
            self.validate(document),
            "rationale_refs must not contain duplicates",
        )

    def test_interpretation_limitations_must_be_preserved_exactly(self) -> None:
        document = decided(self.interpretation)
        document["limitations_acknowledged"] = []
        refresh_digest(document)
        self.assert_error(
            self.validate(document),
            "must exactly preserve interpreted artifact limitations",
        )

    def test_decision_cannot_precede_interpretation(self) -> None:
        document = decided(self.interpretation)
        document["decided_at"] = "2026-09-18T11:44:00Z"
        refresh_digest(document)
        self.assert_error(
            self.validate(document),
            "must not precede interpretation.generated_at",
        )

    def test_post_decision_mutation_is_detected(self) -> None:
        document = decided(self.interpretation)
        document["rationale_refs"][0] = "analysis:mutated"
        self.assert_error(
            self.validate(document),
            "decision_digest does not match canonical content",
        )

    def test_b5_entry_condition_must_be_explicitly_assessed(self) -> None:
        document = decided(self.interpretation)
        document["b5_entry_condition_assessed"] = False
        refresh_digest(document)
        self.assert_error(
            self.validate(document),
            "requires b5_entry_condition_assessed=true",
        )

    def test_b5_review_request_must_match_disposition(self) -> None:
        document = decided(
            self.interpretation,
            disposition="request-b5-review",
        )
        document["b5_review_requested"] = False
        refresh_digest(document)
        self.assert_error(
            self.validate(document),
            "must match request-b5-review disposition",
        )

    def test_semantic_truth_claim_must_remain_false(self) -> None:
        document = decided(self.interpretation)
        document["semantic_truth_claimed"] = True
        refresh_digest(document)
        self.assert_error(
            self.validate(document),
            "semantic_truth_claimed must remain false",
        )

    def test_variant_winner_selection_must_remain_false(self) -> None:
        document = decided(self.interpretation)
        document["variant_winner_selected"] = True
        refresh_digest(document)
        self.assert_error(
            self.validate(document),
            "variant_winner_selected must remain false",
        )

    def test_b5_gate_open_must_remain_false(self) -> None:
        document = decided(
            self.interpretation,
            disposition="request-b5-review",
        )
        document["b5_gate_opened"] = True
        refresh_digest(document)
        self.assert_error(
            self.validate(document),
            "b5_gate_opened must remain false",
        )

    def test_production_default_change_must_remain_false(self) -> None:
        document = decided(self.interpretation)
        document["production_default_changed"] = True
        refresh_digest(document)
        self.assert_error(
            self.validate(document),
            "production_default_changed must remain false",
        )

    def test_winner_field_is_rejected_by_strict_schema(self) -> None:
        document = copy.deepcopy(self.current_decision)
        document["winner"] = "B1-B2"
        self.assert_error(
            validate_decision_structure(document),
            "top-level keys mismatch",
        )

    def test_unknown_disposition_is_rejected(self) -> None:
        document = decided(self.interpretation)
        document["disposition"] = "open-b5"
        refresh_digest(document)
        self.assert_error(
            self.validate(document),
            "disposition is not registered",
        )

    def test_familiarity_decision_preserves_source_identity(self) -> None:
        run = authorized_run(
            self.frozen,
            track="familiarity",
            variant="SAC-B4",
            capacity_profile=None,
            metrics=["missed_change_rate"],
        )
        result = completed_result(run)
        interpretation = interpreted(result)
        document = decided(interpretation)
        self.assertEqual(
            validate_decided_artifact(
                document,
                interpretation,
                result,
                run,
                self.prereg,
                self.frozen,
            ),
            [],
        )

    def test_routing_decision_preserves_source_identity(self) -> None:
        run = authorized_run(
            self.frozen,
            track="routing",
            variant="SEI-B7",
            capacity_profile=None,
            metrics=["regret_against_static_policy"],
        )
        result = completed_result(run)
        interpretation = interpreted(result)
        document = decided(interpretation)
        self.assertEqual(
            validate_decided_artifact(
                document,
                interpretation,
                result,
                run,
                self.prereg,
                self.frozen,
            ),
            [],
        )


if __name__ == "__main__":
    unittest.main()
