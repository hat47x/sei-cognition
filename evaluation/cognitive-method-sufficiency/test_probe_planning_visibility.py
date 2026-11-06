"""Finite public/private planning pressure cases for SEI Cognitive Method.

This is an illustrative pure test, NOT an authorization mechanism, OS sandbox,
MCP tool discovery, or proof of timing/trace/side-channel noninterference.
Run with: python -m unittest -v test_probe_planning_visibility
"""

import unittest
from collections.abc import Mapping

PUBLIC_VIEW = ("order-H", ("A", "B"))
PUBLIC_TOOLS = ("product.check-public-claim", "public.describe")
WORLD0 = {"private_action_exists": False, "hidden_qty": 0}
WORLD1 = {"private_action_exists": True, "hidden_qty": 1}


def unsafe_planning_trace(private_world: Mapping[str, object]) -> tuple[str, ...]:
    """Demonstrates a leak in action discovery, even if reply is withheld."""
    actions = ["public.describe"]
    if private_world["private_action_exists"]:
        actions.append("private.reconcile")
    return tuple(actions)


def public_planning_trace(
    view: tuple[str, tuple[str, ...]],
    tools: tuple[str, ...],
    question: str,
) -> tuple[str, ...]:
    """No private world is available to this synthetic external planner."""
    if question == "is-entire-order-valid" and "product.check-public-claim" in tools:
        return ("product.check-public-claim", view[0])
    if "public.describe" in tools:
        return ("public.describe", view[0])
    return ("unsupported",)


def product_only_evaluation(world: Mapping[str, object]) -> bool:
    """Simulated internal evaluation; not callable by the external planner."""
    return world["hidden_qty"] == 0


def present_result(private_verdict: bool, release_allowed: bool) -> str:
    """Assumed trusted release flag; NOT an implementation of Policy."""
    if not release_allowed:
        return "not-confirmable-from-released-information"
    return "qualified-true" if private_verdict else "qualified-false"


def public_observation(world: Mapping[str, object], release_allowed: bool) -> tuple:
    return (
        PUBLIC_VIEW,
        public_planning_trace(PUBLIC_VIEW, PUBLIC_TOOLS, "is-entire-order-valid"),
        present_result(product_only_evaluation(world), release_allowed),
    )


class TestProbePlanningVisibility(unittest.TestCase):
    def test_unsafe_action_discovery_reveals_hidden_difference(self) -> None:
        self.assertNotEqual(unsafe_planning_trace(WORLD0), unsafe_planning_trace(WORLD1))

    def test_hidden_world_cannot_change_public_planning_trace(self) -> None:
        self.assertEqual(public_observation(WORLD0, False), public_observation(WORLD1, False))

    def test_equal_final_text_does_not_guarantee_equal_action_discovery(self) -> None:
        self.assertEqual(present_result(False, False), present_result(True, False))
        self.assertNotEqual(unsafe_planning_trace(WORLD0), unsafe_planning_trace(WORLD1))

    def test_release_of_verdict_may_legitimately_distinguish_worlds(self) -> None:
        self.assertNotEqual(public_observation(WORLD0, True), public_observation(WORLD1, True))
        self.assertEqual(
            public_observation(WORLD0, True)[1], public_observation(WORLD1, True)[1]
        )

    def test_missing_public_tool_stays_unsupported_without_private_fallback(self) -> None:
        self.assertEqual(public_planning_trace(PUBLIC_VIEW, (), "is-entire-order-valid"), ("unsupported",))
        self.assertEqual(
            public_planning_trace(PUBLIC_VIEW, ("public.describe",), "is-entire-order-valid"),
            ("public.describe", "order-H"),
        )

    def test_public_question_may_change_plan_without_private_state(self) -> None:
        self.assertEqual(
            public_planning_trace(PUBLIC_VIEW, PUBLIC_TOOLS, "describe"),
            ("public.describe", "order-H"),
        )
        self.assertEqual(
            public_planning_trace(PUBLIC_VIEW, PUBLIC_TOOLS, "is-entire-order-valid"),
            ("product.check-public-claim", "order-H"),
        )

    def test_repeated_public_plan_does_not_implicitly_enumerate_private_actions(self) -> None:
        for _ in range(5):
            for world in (WORLD0, WORLD1):
                self.assertNotIn("private.reconcile", public_observation(world, False)[1])


if __name__ == "__main__":
    unittest.main()
