import os
import unittest
from unittest import mock

import run_tei_version_exchange_from_github as subject


class TEIGitHubOneShotPreflightCredentialTest(unittest.TestCase):
    def test_gh_token_source_is_preserved_without_reporting_value(self):
        token = "placeholder-gh-token"
        with mock.patch.dict(
            os.environ,
            {"GITHUB_TOKEN": "", "GH_TOKEN": token},
            clear=False,
        ):
            environment = subject._credential_environment_for_preflight(token)

        self.assertEqual({"GH_TOKEN": token}, environment)

    def test_programmatic_token_is_presented_without_process_env_mutation(self):
        token = "placeholder-programmatic-token"
        with mock.patch.dict(
            os.environ,
            {"GITHUB_TOKEN": "", "GH_TOKEN": ""},
            clear=False,
        ):
            environment = subject._credential_environment_for_preflight(token)
            # mock.patch.dict restores the original mapping on exit, which removes
            # keys that were absent before the patch. The no-mutation check must
            # therefore run while the patched values are still in effect.
            self.assertEqual("", os.environ["GITHUB_TOKEN"])
            self.assertEqual("", os.environ["GH_TOKEN"])

        self.assertEqual({"GITHUB_TOKEN": token}, environment)


if __name__ == "__main__":
    unittest.main()
