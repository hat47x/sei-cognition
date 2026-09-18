from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SACS_DIR = HERE.parent
RESULT_DIR = SACS_DIR / "cross-stage-result"
RUN_DIR = SACS_DIR / "cross-stage-run"
FREEZE_DIR = SACS_DIR / "cross-stage-freeze"

for path in (HERE, SACS_DIR, RESULT_DIR, RUN_DIR, FREEZE_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from freeze_manifests import freeze_documents, load_directory  # noqa: E402
from test_validate_evaluation_run import (  # noqa: E402
    authorized_run,
    frozen_prereg,
    synthetic_freeze_draft,
)
from test_validate_result import completed_result  # noqa: E402
from validate_interpretation import (  # noqa: E402
    canonical_interpretation_digest,
    validate_interpretation_structure,
    validate_interpreted_artifact,
)

INTERPRETATION_PATH = HERE / "interpretation.json"
RESULT_PATH = RESULT_DIR / "result.json"
RUN_PATH = RUN_DIR / "evaluation_run.json"
PREREG_PATH = SACS_DIR / "cross_stage_benchmark_preregistration.json"


def interpreted(result: dict) -> dict:
    document = json.loads(INTERPRETATION_PATH.read_text(encoding="utf-8"))
    document.update({
        "state": "interpreted",
        "interpretation_id": "interpretation:fixture:001",
        "generated_at": "2026-09-18T11:45:00Z",
        "scope": {
            "track": result["track"],
            "variant": result["variant"],
            "capacity_profile": result["capacity_profile"],
            "stress_policy": result["stress_policy"],
        },
        "findings": [
            {
                "id": "finding:001",
                "kind": "metric-observation",
                "claim_strength": "observation",
                "evidence_metrics": [result["metrics"][0]["name"]],
                "statement": "The referenced metric was observed in the synthetic fixture.",
            }
        ],
        "limitations": ["Synthetic fixture only; no human-adjudicated benchmark result."],
        "unresolved_questions": ["Generalization to the frozen human benchmark remains unresolved."],
    })
    document["result_binding"]["digest"] = result["result_digest"]
    document["analyst_provenance"] = {
        "ref": "analysis:fixture:001",
        "commit": "c" * 40,
    }
    document["interpretation_digest"] = canonical_interpretation_digest(document)
    return document


def refresh_digest(document: dict) -> None:
    document["interpretation_digest"] = canonical_interpretation_digest(document)


class CrossStageInterpretationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.current_interpretation = json.loads(
            INTERPRETATION_PATH.read_text(encoding="utf-8")
        )
        self.current_result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
        self.current_run = json.loads(RUN_PATH.read_text(encoding="utf-8"))
        self.current_prereg = json.loads(PREREG_PATH.read_text(encoding="utf-8"))
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

    def validate(
        self,
        document: dict,
        *,
        result: dict | None = None,
        run: dict | None = None,
    ) -> list[str]:
        return validate_interpreted_artifact(
            document,
            result or self.result,
            run or self.run,
            self.prereg,
            self.frozen,
        )

    def assert_error(self, errors: list[str], fragment: str) -> None:
        self.assertTrue(
            any(fragment in error for error in errors),
            f"expected {fragment!r}; got {errors!r}",
        )

    def test_current_draft_interpretation_is_structurally_valid(self) -> None:
        self.assertEqual(
            validate_interpretation_structure(self.current_interpretation),
            [],
        )

    def test_current_draft_upstream_cannot_support_interpreted_artifact(self) -> None:
        document = interpreted(self.result)
        errors = validate_interpreted_artifact(
            document,
            self.current_result,
            self.current_run,
            self.current_prereg,
            self.current_freeze,
        )
        self.assert_error(errors, "authorized run")
        self.assert_error(errors, "completed result")

    def test_synthetic_interpreted_artifact_is_valid(self) -> None:
        self.assertEqual(self.validate(interpreted(self.result)), [])

    def test_result_digest_binding_is_exact(self) -> None:
        document = interpreted(self.result)
        document["result_binding"]["digest"] = "0" * 64
        refresh_digest(document)
        self.assert_error(self.validate(document), "does not match completed result digest")

    def test_post_interpretation_mutation_is_detected(self) -> None:
        document = interpreted(self.result)
        document["limitations"].append("mutated")
        self.assert_error(
            self.validate(document),
            "interpretation_digest does not match canonical content",
        )

    def test_scope_track_must_match_result(self) -> None:
        document = interpreted(self.result)
        document["scope"]["track"] = "routing"
        refresh_digest(document)
        self.assert_error(self.validate(document), "scope.track must match")

    def test_scope_variant_must_match_result(self) -> None:
        document = interpreted(self.result)
        document["scope"]["variant"] = "B0"
        refresh_digest(document)
        self.assert_error(self.validate(document), "scope.variant must match")

    def test_scope_capacity_must_match_result(self) -> None:
        document = interpreted(self.result)
        document["scope"]["capacity_profile"] = "large"
        refresh_digest(document)
        self.assert_error(self.validate(document), "scope.capacity_profile must match")

    def test_scope_stress_policy_must_match_result(self) -> None:
        run = authorized_run(
            self.frozen,
            capacity_profile="oversized-stress",
            stress_policy="cap128",
            metrics=["oversized_residual_policy_stress"],
        )
        result = completed_result(run)
        document = interpreted(result)
        document["scope"]["stress_policy"] = "cap64"
        refresh_digest(document)
        errors = validate_interpreted_artifact(
            document,
            result,
            run,
            self.prereg,
            self.frozen,
        )
        self.assert_error(errors, "scope.stress_policy must match")

    def test_analyst_ref_is_required(self) -> None:
        document = interpreted(self.result)
        document["analyst_provenance"]["ref"] = ""
        refresh_digest(document)
        self.assert_error(self.validate(document), "canonical analyst_provenance.ref")

    def test_analyst_commit_is_required(self) -> None:
        document = interpreted(self.result)
        document["analyst_provenance"]["commit"] = "main"
        refresh_digest(document)
        self.assert_error(self.validate(document), "40-char lowercase git SHA")

    def test_finding_ids_must_be_unique(self) -> None:
        document = interpreted(self.result)
        document["findings"].append(copy.deepcopy(document["findings"][0]))
        refresh_digest(document)
        self.assert_error(self.validate(document), "finding id must be unique")

    def test_finding_evidence_metrics_are_required(self) -> None:
        document = interpreted(self.result)
        document["findings"][0]["evidence_metrics"] = []
        refresh_digest(document)
        self.assert_error(self.validate(document), "non-empty canonical string list")

    def test_unknown_result_metric_is_rejected(self) -> None:
        document = interpreted(self.result)
        document["findings"][0]["evidence_metrics"] = ["magic_score"]
        refresh_digest(document)
        self.assert_error(self.validate(document), "unknown result metrics")

    def test_finding_kind_is_restricted(self) -> None:
        document = interpreted(self.result)
        document["findings"][0]["kind"] = "winner-declaration"
        refresh_digest(document)
        self.assert_error(self.validate(document), "kind is not registered")

    def test_claim_strength_is_restricted(self) -> None:
        document = interpreted(self.result)
        document["findings"][0]["claim_strength"] = "truth"
        refresh_digest(document)
        self.assert_error(self.validate(document), "observation or hypothesis")

    def test_explicit_limitation_is_required(self) -> None:
        document = interpreted(self.result)
        document["limitations"] = []
        refresh_digest(document)
        self.assert_error(self.validate(document), "at least one explicit limitation")

    def test_interpretation_cannot_precede_result(self) -> None:
        document = interpreted(self.result)
        document["generated_at"] = "2026-09-18T11:39:00Z"
        refresh_digest(document)
        self.assert_error(self.validate(document), "must not precede result.generated_at")

    def test_winner_field_is_rejected_by_strict_schema(self) -> None:
        document = copy.deepcopy(self.current_interpretation)
        document["winner"] = "B1-B2"
        self.assert_error(
            validate_interpretation_structure(document),
            "top-level keys mismatch",
        )

    def test_semantic_truth_claim_must_remain_false(self) -> None:
        document = interpreted(self.result)
        document["semantic_truth_claimed"] = True
        refresh_digest(document)
        self.assert_error(self.validate(document), "semantic_truth_claimed must remain false")

    def test_variant_winner_must_remain_false(self) -> None:
        document = interpreted(self.result)
        document["variant_winner_declared"] = True
        refresh_digest(document)
        self.assert_error(self.validate(document), "variant_winner_declared must remain false")

    def test_recommendation_must_remain_false(self) -> None:
        document = interpreted(self.result)
        document["recommendation_generated"] = True
        refresh_digest(document)
        self.assert_error(self.validate(document), "recommendation_generated must remain false")

    def test_b5_decision_must_remain_false(self) -> None:
        document = interpreted(self.result)
        document["b5_decision_generated"] = True
        refresh_digest(document)
        self.assert_error(self.validate(document), "b5_decision_generated must remain false")

    def test_production_default_must_remain_false(self) -> None:
        document = interpreted(self.result)
        document["production_default_changed"] = True
        refresh_digest(document)
        self.assert_error(self.validate(document), "production_default_changed must remain false")

    def test_familiarity_interpretation_is_track_bound(self) -> None:
        run = authorized_run(
            self.frozen,
            track="familiarity",
            variant="SAC-B4",
            capacity_profile=None,
            metrics=["missed_change_rate"],
        )
        result = completed_result(run)
        document = interpreted(result)
        self.assertEqual(
            validate_interpreted_artifact(
                document,
                result,
                run,
                self.prereg,
                self.frozen,
            ),
            [],
        )

    def test_routing_interpretation_is_track_bound(self) -> None:
        run = authorized_run(
            self.frozen,
            track="routing",
            variant="SEI-B7",
            capacity_profile=None,
            metrics=["regret_against_static_policy"],
        )
        result = completed_result(run)
        document = interpreted(result)
        self.assertEqual(
            validate_interpreted_artifact(
                document,
                result,
                run,
                self.prereg,
                self.frozen,
            ),
            [],
        )

    def test_oversized_interpretation_preserves_stress_identity(self) -> None:
        run = authorized_run(
            self.frozen,
            capacity_profile="oversized-stress",
            stress_policy="cap128",
            metrics=["oversized_residual_policy_stress"],
        )
        result = completed_result(run)
        document = interpreted(result)
        self.assertEqual(
            validate_interpreted_artifact(
                document,
                result,
                run,
                self.prereg,
                self.frozen,
            ),
            [],
        )
        self.assertEqual(document["scope"]["stress_policy"], "cap128")


if __name__ == "__main__":
    unittest.main()
