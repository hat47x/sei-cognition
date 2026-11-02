"""Synthetic negative-claim qualification; not a SQL/Provider/Policy engine.

The caller-supplied dependency set, revisions and completion signals are
assumptions of a *public fixture*, never proof that an actual scan was complete.
"""
from dataclasses import dataclass, replace
import unittest


@dataclass(frozen=True)
class Scan:
    observed_ids: tuple[str, ...]
    actual_read: bool
    source_bound: bool
    membership_bound: bool
    complete: bool
    # Dependency edges and revision values are synthetic trusted inputs.
    witnessed_dependencies: tuple[tuple[str, str], ...]


def qualify_not_exists(scan: Scan, required: dict[str, str]) -> str:
    """Return a limited fixture verdict, never a production NOT EXISTS proof."""
    if not scan.actual_read or not scan.source_bound:
        return "unknown-unobserved-read"
    # A positive witness is only for the same scoped Question and revision.
    if scan.observed_ids and not scan.membership_bound:
        return "unknown-unbound-member"
    if not required:
        return "unknown-dependency-closure"
    supplied = dict(scan.witnessed_dependencies)
    if len(supplied) != len(scan.witnessed_dependencies):
        return "unknown-ambiguous-dependency"
    if any(supplied.get(name) != revision for name, revision in required.items()):
        return "unknown-stale-or-missing-dependency"
    if scan.observed_ids:
        # Completeness is not required for a bound, current existential witness.
        return "exists-witness-in-fixture"
    if not scan.membership_bound:
        return "unknown-unbound-population"
    if not scan.complete:
        return "unknown-incomplete-scan"
    return "conditionally-absent-in-fixture"


REQUIRED = {
    "target-cohort": "c1",
    "query-predicate": "p1",
    "relation-occurrences": "r1",
    "provider-route": "v1",
    "snapshot-epoch": "e1",
}
VALID = Scan((), True, True, True, True, tuple(REQUIRED.items()))


class TestNegativeEvidenceClosure(unittest.TestCase):
    def test_same_empty_response_cannot_distinguish_partial_universe(self):
        # Both external reads [] can be produced by a true empty target and
        # a target with an unseen matching member; empty alone is insufficient.
        self.assertEqual(qualify_not_exists(replace(VALID, complete=False), REQUIRED),
                         "unknown-incomplete-scan")
        self.assertEqual(qualify_not_exists(VALID, REQUIRED),
                         "conditionally-absent-in-fixture")

    def test_unchanged_output_with_nonoutput_predicate_revision(self):
        self.assertEqual(qualify_not_exists(VALID, {**REQUIRED, "query-predicate": "p2"}),
                         "unknown-stale-or-missing-dependency")

    def test_dynamic_relation_occurrence_changed_without_output_change(self):
        self.assertEqual(qualify_not_exists(VALID, {**REQUIRED, "relation-occurrences": "r2"}),
                         "unknown-stale-or-missing-dependency")

    def test_required_dependency_added_after_a_prior_qualification(self):
        self.assertEqual(qualify_not_exists(VALID, {**REQUIRED, "hidden-rule": "h1"}),
                         "unknown-stale-or-missing-dependency")

    def test_proclaimed_completeness_without_actual_read_is_not_evidence(self):
        self.assertEqual(qualify_not_exists(replace(VALID, actual_read=False), REQUIRED),
                         "unknown-unobserved-read")
        self.assertEqual(qualify_not_exists(replace(VALID, source_bound=False), REQUIRED),
                         "unknown-unobserved-read")

    def test_one_bound_witness_refutes_nonexistence_despite_incomplete_read(self):
        scan = replace(VALID, observed_ids=("synthetic-C",), complete=False)
        self.assertEqual(qualify_not_exists(scan, REQUIRED), "exists-witness-in-fixture")
        self.assertEqual(qualify_not_exists(replace(scan, membership_bound=False), REQUIRED),
                         "unknown-unbound-member")

    def test_old_positive_witness_is_not_current_without_dependency_binding(self):
        scan = replace(VALID, observed_ids=("synthetic-C",), complete=False)
        self.assertEqual(
            qualify_not_exists(scan, {**REQUIRED, "query-predicate": "p2"}),
            "unknown-stale-or-missing-dependency")
        self.assertEqual(
            qualify_not_exists(scan, {**REQUIRED, "relation-occurrences": "r2"}),
            "unknown-stale-or-missing-dependency")

    def test_empty_but_population_not_bound(self):
        self.assertEqual(qualify_not_exists(replace(VALID, membership_bound=False), REQUIRED),
                         "unknown-unbound-population")

    def test_declared_unknown_closure_is_not_empty_set_proof(self):
        self.assertEqual(qualify_not_exists(VALID, {}), "unknown-dependency-closure")
        self.assertEqual(
            qualify_not_exists(replace(VALID, witnessed_dependencies=(
                ("target-cohort", "c1"), ("target-cohort", "c1")
            )), REQUIRED), "unknown-ambiguous-dependency")

    def test_changed_provider_epoch_and_cohort_are_independent_rechecks(self):
        for name, changed in (("provider-route", "v2"),
                              ("snapshot-epoch", "e2"),
                              ("target-cohort", "c2")):
            with self.subTest(dependency=name):
                self.assertEqual(qualify_not_exists(VALID, {**REQUIRED, name: changed}),
                                 "unknown-stale-or-missing-dependency")


if __name__ == "__main__":
    unittest.main()
