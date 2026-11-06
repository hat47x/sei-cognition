"""Focused synthetic tests for claim-relative *local* observability.

These tests use the public possible-world fixture. They do not model an actual
Provider, certified snapshot, authorization engine, or external disclosure.
Run together with the original six tests:
  python -m unittest -v probe_partition_reference test_probe_claim_qualifiers
"""

from __future__ import annotations

import unittest
from dataclasses import dataclass
from collections.abc import Mapping

from probe_partition_reference import (
    EXTRA_WORLD,
    WORLDS,
    World,
    corpus_sufficient,
    signature,
    target_claim,
)


def fixture_cell_verdict(
    worlds: Mapping[str, World],
    probes: tuple[str, ...],
    observed: tuple[object, ...],
) -> str:
    """Classify one observation *only* within an enumerated fixture corpus."""
    values = {
        target_claim(world)
        for world in worlds.values()
        if signature(world, probes) == observed
    }
    if not values:
        return "unmodeled-observation"
    if len(values) > 1:
        return "unknown-in-fixture"
    return "true-in-fixture" if True in values else "false-in-fixture"


@dataclass(frozen=True)
class Read:
    field: str
    value: int
    epoch: str
    source_revision: str


def joint_read_candidate(reads: tuple[Read, ...], required: tuple[str, ...]) -> str:
    """A synthetic consistency *precheck*, not proof of true Source binding.

    Even when the labels match, an actual Product must prove their authenticity,
    target completeness, scope and whether a causal bridge exists.
    """
    observed = [r.field for r in reads]
    if len(observed) != len(set(observed)):
        return "ambiguous-duplicates"
    if set(observed) != set(required):
        return "missing-or-extraneous-field"
    if len({r.epoch for r in reads}) != 1:
        return "mixed-epoch-unknown"
    if len({r.source_revision for r in reads}) != 1:
        return "mixed-source-unknown"
    return "same-labels-in-fixture"


def disclosure_limited_summary(
    internal_verdict: str, *, result_release_authorized: bool
) -> str:
    """A test with an assumed, trusted authorization input, not a Policy API."""
    if not result_release_authorized:
        return "not-confirmable-from-released-information"
    return internal_verdict


class TestClaimRelativeProbeQualification(unittest.TestCase):
    def test_some_cells_resolve_while_global_corpus_does_not(self) -> None:
        probes = ("count", "has_C")
        self.assertFalse(corpus_sufficient(WORLDS, probes))
        self.assertEqual(
            fixture_cell_verdict(WORLDS, probes, signature(WORLDS["W1"], probes)),
            "true-in-fixture",
        )
        self.assertEqual(
            fixture_cell_verdict(WORLDS, probes, signature(WORLDS["W2"], probes)),
            "false-in-fixture",
        )
        self.assertEqual(
            fixture_cell_verdict(WORLDS, probes, signature(WORLDS["W3"], probes)),
            "unknown-in-fixture",
        )

    def test_additional_world_revokes_apparent_local_certainty(self) -> None:
        probes = ("count", "has_C", "has_E")
        obs = signature(WORLDS["W3"], probes)
        self.assertEqual(fixture_cell_verdict(WORLDS, probes, obs), "true-in-fixture")
        extended = WORLDS | EXTRA_WORLD
        self.assertEqual(fixture_cell_verdict(extended, probes, obs), "unknown-in-fixture")

    def test_outside_the_fixture_is_not_a_negative_answer(self) -> None:
        probes = ("count",)
        unseen = ((("A", 2), ("B", 1)), 42)
        self.assertEqual(fixture_cell_verdict(WORLDS, probes, unseen), "unmodeled-observation")

    def test_mixed_epoch_reads_cannot_create_false_all_positive(self) -> None:
        # Both *real* snapshots fail Q, yet picking A from t0 and B from t1
        # makes the mixed read look all-positive.
        snapshots = {"t0": {"A": 1, "B": 0}, "t1": {"A": 0, "B": 1}}
        self.assertFalse(target_claim(snapshots["t0"]))
        self.assertFalse(target_claim(snapshots["t1"]))
        mixed = (Read("A", 1, "t0", "r1"), Read("B", 1, "t1", "r1"))
        self.assertTrue(all(read.value > 0 for read in mixed))
        self.assertEqual(joint_read_candidate(mixed, ("A", "B")), "mixed-epoch-unknown")

    def test_same_epoch_fixture_can_reveal_falsifying_witness(self) -> None:
        reads = (Read("A", 1, "t0", "r1"), Read("B", 0, "t0", "r1"))
        self.assertEqual(joint_read_candidate(reads, ("A", "B")), "same-labels-in-fixture")
        self.assertFalse(all(read.value > 0 for read in reads))
        # Still requires valid membership of B in the actual target set.

    def test_same_epoch_but_different_source_revisions(self) -> None:
        reads = (Read("A", 1, "t0", "r1"), Read("B", 1, "t0", "r2"))
        self.assertEqual(joint_read_candidate(reads, ("A", "B")), "mixed-source-unknown")

    def test_hidden_internal_answer_does_not_automatically_publish(self) -> None:
        # The same public baseline can cover opposing private conclusions.
        a, b = WORLDS["W1"], WORLDS["W2"]
        self.assertNotEqual(target_claim(a), target_claim(b))
        internal_a = "true-in-fixture" if target_claim(a) else "false-in-fixture"
        internal_b = "true-in-fixture" if target_claim(b) else "false-in-fixture"
        self.assertEqual(
            disclosure_limited_summary(internal_a, result_release_authorized=False),
            disclosure_limited_summary(internal_b, result_release_authorized=False),
        )
        # Does not test Tool names, status codes, timing, logs, repeat queries.


if __name__ == "__main__":
    unittest.main()
