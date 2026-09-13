import unittest
from unittest import mock

import prepare_tei_revision_b_source as subject


class _Response:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return b"{}"


class TEIRevisionBSourceRedirectBoundaryTest(unittest.TestCase):
    def test_redirect_handler_rejects_cross_origin_before_followup_request(self):
        request = subject.urllib.request.Request(
            subject._api("git/trees/" + "a" * 40),
            headers={"Authorization": "Bearer secret-token"},
        )
        handler = subject._RejectRedirectHandler()

        with self.assertRaisesRegex(ValueError, "redirect") as raised:
            handler.redirect_request(
                request,
                None,
                302,
                "Found",
                {},
                "https://example.invalid/token-target",
            )

        self.assertIn("api.github.com", str(raised.exception))
        self.assertIn("example.invalid", str(raised.exception))
        self.assertNotIn("secret-token", str(raised.exception))

    def test_non_fixed_repository_url_is_rejected_before_opener_creation(self):
        with mock.patch.object(subject.urllib.request, "build_opener") as build_opener:
            with self.assertRaisesRegex(ValueError, "未承認"):
                subject._github_json(
                    "https://api.github.com/repos/other/repo/git/trees/abc",
                    "secret-token",
                )
        build_opener.assert_not_called()

    def test_github_json_installs_redirect_rejecting_opener(self):
        opener = mock.Mock()
        opener.open.return_value = _Response()
        with mock.patch.object(
            subject.urllib.request,
            "build_opener",
            return_value=opener,
        ) as build_opener:
            result = subject._github_json(
                subject._api("git/trees/" + "a" * 40),
                "secret-token",
            )

        self.assertEqual({}, result)
        handler = build_opener.call_args.args[0]
        self.assertIsInstance(handler, subject._RejectRedirectHandler)
        request = opener.open.call_args.args[0]
        self.assertEqual("Bearer secret-token", request.get_header("Authorization"))
        self.assertEqual(60, opener.open.call_args.kwargs["timeout"])


if __name__ == "__main__":
    unittest.main()
