import unittest

import run_tei_revision_b_e2_from_github as partial
import run_tei_version_exchange_evidence as full


class TEIE2PartialArtifactNamesTest(unittest.TestCase):
    def test_partial_bundle_and_report_names_are_distinct_from_full_run(self):
        self.assertNotEqual(partial.BUNDLE_NAME, full.BUNDLE_NAME)
        self.assertNotEqual(partial.REPORT_NAME, full.REPORT_NAME)
        self.assertIn("e2-partial", partial.BUNDLE_NAME)


if __name__ == "__main__":
    unittest.main()
