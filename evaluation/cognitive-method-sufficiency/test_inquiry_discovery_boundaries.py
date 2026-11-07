"""Public synthetic examples for missing discovery coverage and mixed snapshots."""

import hashlib
import unittest

LIMIT = 12


def ranked_candidates(tests, docs):
    selected = tests[:LIMIT]
    return selected + docs[:max(0, LIMIT - len(selected))]


class TestInquiryEvidenceLimits(unittest.TestCase):
    def test_full_candidate_list_may_hide_document(self):
        tests = [f"pkg/case_{i:02d}_test.go" for i in range(LIMIT)]
        self.assertEqual(ranked_candidates(tests, []),
                         ranked_candidates(tests, ["docs/related.md"]))

    def test_more_slots_and_unsearched_names_are_separate(self):
        tests = [f"pkg/case_{i:02d}_test.go" for i in range(LIMIT)]
        self.assertNotIn("docs/related.md",
                         ranked_candidates(tests, ["docs/related.md"]))
        self.assertNotIn("pkg/revision_test.go", tests)

    def test_valid_individual_digests_do_not_prove_joint_snapshot(self):
        first = {"A": b"1", "B": b"0"}
        second = {"A": b"0", "B": b"1"}
        mixed = (first["A"], second["B"])
        self.assertEqual(hashlib.sha256(mixed[0]).hexdigest(),
                         hashlib.sha256(first["A"]).hexdigest())
        self.assertEqual(hashlib.sha256(mixed[1]).hexdigest(),
                         hashlib.sha256(second["B"]).hexdigest())
        self.assertFalse(any(all(v == b"1" for v in state.values())
                             for state in (first, second)))

    def test_equal_endpoint_bytes_do_not_prove_interval_stability(self):
        start, middle, end = b"one", b"two", b"one"
        self.assertEqual(start, end)
        self.assertNotEqual(start, middle)


if __name__ == "__main__":
    unittest.main()
