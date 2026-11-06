"""Public synthetic reference for question-relative probe sufficiency.

This is a deliberately bounded possible-worlds example, not a Product API,
a real Provider query, a security policy, or a proof about unknown worlds.
Run with: python -m unittest -v probe_partition_reference.py
"""

from __future__ import annotations

import unittest
from collections import defaultdict
from collections.abc import Callable, Mapping

World = Mapping[str, int]
Probe = Callable[[World], object]

# The baseline read returns only A and B in every synthetic world.
BASE_KEYS = ("A", "B")
WORLDS: dict[str, dict[str, int]] = {
    "W1": {"A": 2, "B": 1},
    "W2": {"A": 2, "B": 1, "C": 0},
    "W3": {"A": 2, "B": 1, "D": 3},
    "W4": {"A": 2, "B": 1, "E": 0},
}
# Public extension counterexample: it was not in the four-world sample.
EXTRA_WORLD = {"W5": {"A": 2, "B": 1, "D": 0}}


def baseline(world: World) -> tuple[tuple[str, int], ...]:
    return tuple((key, world[key]) for key in BASE_KEYS)


def target_claim(world: World) -> bool:
    """Q: All rows in the *actual* synthetic target set have positive qty."""
    return all(qty > 0 for qty in world.values())


PROBES: dict[str, Probe] = {
    "count": lambda world: len(world),
    "has_C": lambda world: "C" in world,
    "has_E": lambda world: "E" in world,
    "has_nonpositive": lambda world: any(qty <= 0 for qty in world.values()),
}


def signature(world: World, names: tuple[str, ...]) -> tuple[object, ...]:
    """The observation available after the named probes, not a permission check."""
    return (baseline(world), *(PROBES[name](world) for name in names))


def ambiguous_pairs(
    worlds: Mapping[str, World], names: tuple[str, ...]
) -> list[tuple[str, str]]:
    """Find fixed-corpus pairs with equal observations but opposite Q."""
    groups: dict[tuple[object, ...], list[str]] = defaultdict(list)
    for key, world in worlds.items():
        groups[signature(world, names)].append(key)
    pairs: list[tuple[str, str]] = []
    for members in groups.values():
        for i, first in enumerate(members):
            for second in members[i + 1 :]:
                if target_claim(worlds[first]) != target_claim(worlds[second]):
                    pairs.append((first, second))
    return pairs


def corpus_sufficient(worlds: Mapping[str, World], names: tuple[str, ...]) -> bool:
    """Sufficient only relative to the explicitly enumerated test worlds."""
    return not ambiguous_pairs(worlds, names)


class TestQuestionRelativeProbeSufficiency(unittest.TestCase):
    def test_same_baseline_opposite_claim(self) -> None:
        self.assertEqual(len({baseline(w) for w in WORLDS.values()}), 1)
        self.assertEqual({target_claim(w) for w in WORLDS.values()}, {True, False})
        self.assertFalse(corpus_sufficient(WORLDS, ()))

    def test_one_separating_pair_does_not_prove_global_sufficiency(self) -> None:
        self.assertNotEqual(PROBES["count"](WORLDS["W1"]), PROBES["count"](WORLDS["W2"]))
        self.assertFalse(corpus_sufficient(WORLDS, ("count",)))
        self.assertIn(("W2", "W3"), ambiguous_pairs(WORLDS, ("count",)))

    def test_two_probes_still_leave_opposing_worlds(self) -> None:
        self.assertIn(("W3", "W4"), ambiguous_pairs(WORLDS, ("count", "has_C")))

    def test_bounded_corpus_can_be_separated(self) -> None:
        self.assertTrue(corpus_sufficient(WORLDS, ("count", "has_C", "has_E")))
        self.assertTrue(corpus_sufficient(WORLDS, ("has_nonpositive",)))

    def test_public_extension_breaks_apparent_sufficiency(self) -> None:
        extended = WORLDS | EXTRA_WORLD
        names = ("count", "has_C", "has_E")
        self.assertFalse(corpus_sufficient(extended, names))
        self.assertIn(("W3", "W5"), ambiguous_pairs(extended, names))
        # A direct full-world check remains sufficient for these *five* worlds.
        self.assertTrue(corpus_sufficient(extended, ("has_nonpositive",)))

    def test_internal_probe_does_not_imply_disclosure(self) -> None:
        # External observer gets baseline only; internal probe is intentionally
        # not included in the external signature (policy is outside this code).
        self.assertEqual(baseline(WORLDS["W1"]), baseline(WORLDS["W2"]))
        self.assertNotEqual(target_claim(WORLDS["W1"]), target_claim(WORLDS["W2"]))
        self.assertFalse(corpus_sufficient(WORLDS, ()))


if __name__ == "__main__":
    unittest.main()
