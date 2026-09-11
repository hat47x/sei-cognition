import base64
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

import prepare_tei_revision_b_source as prepare


def git_hash(object_type: str, content: bytes) -> str:
    result = subprocess.run(
        ["git", "hash-object", "-t", object_type, "--stdin"],
        input=content,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return result.stdout.decode().strip()


def git_tree(entries: list[tuple[str, str, str, str]]) -> str:
    with tempfile.TemporaryDirectory() as temporary:
        subprocess.run(["git", "-C", temporary, "init", "-q"], check=True)
        payload = b"".join(
            f"{mode} {object_type} {sha}\t".encode("ascii")
            + name.encode("utf-8")
            + b"\0"
            for mode, object_type, sha, name in entries
        )
        result = subprocess.run(
            ["git", "-C", temporary, "mktree", "-z", "--missing"],
            input=payload,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        return result.stdout.decode().strip()


class FakeGitHub:
    def __init__(self, responses: dict[str, dict[str, object]]):
        self.responses = responses
        self.calls: list[str] = []
        self.tokens: list[str] = []

    def __call__(self, url: str, token: str) -> dict[str, object]:
        self.calls.append(url)
        self.tokens.append(token)
        prefix = f"{prepare.API_BASE}/repos/{prepare.GITHUB_REPOSITORY}/"
        if not url.startswith(prefix):
            raise AssertionError(f"unexpected URL: {url}")
        key = url[len(prefix) :]
        if key not in self.responses:
            raise AssertionError(f"unexpected API path: {key}")
        return self.responses[key]


class RevisionBSourceAcquisitionTest(unittest.TestCase):
    def fixture(self):
        go_mod = b"module synthetic\n\ngo 1.23.2\n"
        main_go = b"package main\n\nfunc main() {}\n"
        go_sha = git_hash("blob", go_mod)
        main_sha = git_hash("blob", main_go)
        cmd_tree = git_tree([("100644", "blob", main_sha, "main.go")])
        root_tree = git_tree(
            [
                ("040000", "tree", cmd_tree, "cmd"),
                ("100644", "blob", go_sha, "go.mod"),
            ]
        )

        payload = (
            f"tree {root_tree}\n"
            "author Test <test@example.com> 0 +0000\n"
            "committer Test <test@example.com> 0 +0000\n"
            "\n"
            "synthetic\n"
        )
        signature = (
            "-----BEGIN PGP SIGNATURE-----\n"
            "\n"
            "fake\n"
            "=abcd\n"
            "-----END PGP SIGNATURE-----\n"
        )
        raw_commit = (
            f"tree {root_tree}\n"
            "author Test <test@example.com> 0 +0000\n"
            "committer Test <test@example.com> 0 +0000\n"
            "gpgsig -----BEGIN PGP SIGNATURE-----\n"
            " \n"
            " fake\n"
            " =abcd\n"
            " -----END PGP SIGNATURE-----\n"
            "\n"
            "synthetic\n"
        ).encode("utf-8")
        commit_sha = git_hash("commit", raw_commit)

        responses = {
            f"git/trees/{root_tree}": {
                "sha": root_tree,
                "truncated": False,
                "tree": [
                    {
                        "path": "cmd",
                        "mode": "040000",
                        "type": "tree",
                        "sha": cmd_tree,
                    },
                    {
                        "path": "go.mod",
                        "mode": "100644",
                        "type": "blob",
                        "sha": go_sha,
                    },
                ],
            },
            f"git/trees/{cmd_tree}": {
                "sha": cmd_tree,
                "truncated": False,
                "tree": [
                    {
                        "path": "main.go",
                        "mode": "100644",
                        "type": "blob",
                        "sha": main_sha,
                    }
                ],
            },
            f"git/blobs/{go_sha}": {
                "sha": go_sha,
                "encoding": "base64",
                "content": base64.b64encode(go_mod).decode("ascii"),
                "size": len(go_mod),
            },
            f"git/blobs/{main_sha}": {
                "sha": main_sha,
                "encoding": "base64",
                "content": base64.b64encode(main_go).decode("ascii"),
                "size": len(main_go),
            },
            f"git/commits/{commit_sha}": {
                "sha": commit_sha,
                "tree": {"sha": root_tree},
                "verification": {
                    "verified": True,
                    "payload": payload,
                    "signature": signature,
                },
            },
        }
        expected = {
            "commit": commit_sha,
            "rootTree": root_tree,
            "objects": {"cmd": cmd_tree, "go.mod": go_sha},
            "goMod": go_mod,
            "mainGo": main_go,
            "mainSha": main_sha,
            "payload": payload,
            "signature": signature,
            "rawCommit": raw_commit,
        }
        return expected, responses

    def materialize(self, target: Path, expected, responses, *, request=None):
        fake = request or FakeGitHub(responses)
        result = prepare.materialize_revision_b_source(
            target,
            token="secret-token",
            expected_commit=expected["commit"],
            expected_root_tree=expected["rootTree"],
            expected_objects=expected["objects"],
            request_json=fake,
        )
        return result, fake

    def test_synthetic_git_graph_is_materialized_and_verified(self):
        expected, responses = self.fixture()
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "tei-b"
            result, fake = self.materialize(target, expected, responses)

            self.assertEqual("verified", result["result"])
            self.assertEqual(
                "github-git-data-api-content-addressed",
                result["sourceAcquisition"],
            )
            self.assertEqual(expected["commit"], result["sourceCommit"])
            self.assertEqual(expected["rootTree"], result["rootTree"])
            self.assertEqual(expected["goMod"], (target / "go.mod").read_bytes())
            self.assertEqual(
                expected["mainGo"],
                (target / "cmd" / "main.go").read_bytes(),
            )

            head = subprocess.check_output(
                ["git", "-C", str(target), "rev-parse", "HEAD"],
                text=True,
            ).strip()
            self.assertEqual(expected["commit"], head)
            status = subprocess.check_output(
                [
                    "git",
                    "-C",
                    str(target),
                    "status",
                    "--porcelain=v1",
                    "--untracked-files=all",
                    "--ignored=matching",
                    "--",
                    "cmd",
                    "go.mod",
                ],
                text=True,
            )
            self.assertEqual("", status)
            self.assertEqual(5, result["objectAcquisition"]["apiRequests"])
            self.assertEqual(2, result["objectAcquisition"]["treesMaterialized"])
            self.assertEqual(
                2,
                result["objectAcquisition"]["uniqueBlobsMaterialized"],
            )
            self.assertTrue(all(token == "secret-token" for token in fake.tokens))
            self.assertNotIn("secret-token", json.dumps(result, ensure_ascii=False))
            self.assertFalse(result["revisionBBuildPass"])
            self.assertFalse(result["providerPlanExecutionPass"])
            self.assertFalse(result["seiAdapterCompatibilityPass"])
            self.assertFalse(result["issue000072Resolved"])

    def test_signed_commit_reconstruction_preserves_multiline_gpgsig(self):
        expected, _responses = self.fixture()
        actual = prepare._reconstruct_signed_commit(
            expected["payload"],
            expected["signature"],
        )
        self.assertEqual(expected["rawCommit"], actual)
        self.assertEqual(expected["commit"], git_hash("commit", actual))

    def test_signature_without_trailing_newline_is_rejected(self):
        expected, _responses = self.fixture()
        with self.assertRaisesRegex(ValueError, "末尾改行"):
            prepare._reconstruct_signed_commit(
                expected["payload"],
                expected["signature"].rstrip("\n"),
            )

    def test_blob_byte_drift_never_publishes_target(self):
        expected, responses = self.fixture()
        responses = dict(responses)
        key = f"git/blobs/{expected['mainSha']}"
        corrupted = dict(responses[key])
        drift = b"package main\n\nfunc main() {x}\n"
        corrupted["content"] = base64.b64encode(drift).decode("ascii")
        corrupted["size"] = len(drift)
        responses[key] = corrupted

        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            target = parent / "tei-b"
            with self.assertRaisesRegex(ValueError, "取得blob bytes"):
                self.materialize(target, expected, responses)
            self.assertFalse(target.exists())
            self.assertEqual([], list(parent.glob(".tei-b.staging-*")))

    def test_tree_entry_drift_never_publishes_target(self):
        expected, responses = self.fixture()
        responses = dict(responses)
        key = f"git/trees/{expected['rootTree']}"
        changed = dict(responses[key])
        changed["tree"] = list(changed["tree"][:-1])
        responses[key] = changed

        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            target = parent / "tei-b"
            with self.assertRaisesRegex(ValueError, "Git tree identity"):
                self.materialize(target, expected, responses)
            self.assertFalse(target.exists())
            self.assertEqual([], list(parent.glob(".tei-b.staging-*")))

    def test_symlink_entry_is_rejected_before_blob_fetch(self):
        expected, responses = self.fixture()
        responses = dict(responses)
        link_sha = git_hash("blob", b"outside")
        key = f"git/trees/{expected['rootTree']}"
        changed = dict(responses[key])
        changed["tree"] = list(changed["tree"]) + [
            {
                "path": "linked",
                "mode": "120000",
                "type": "blob",
                "sha": link_sha,
            }
        ]
        responses[key] = changed
        fake = FakeGitHub(responses)

        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "tei-b"
            with self.assertRaisesRegex(ValueError, "通常file/executable以外"):
                self.materialize(target, expected, responses, request=fake)
            self.assertFalse(target.exists())
        self.assertFalse(any(url.endswith(link_sha) for url in fake.calls))

    def test_existing_output_is_rejected_before_api_access(self):
        expected, responses = self.fixture()
        fake = FakeGitHub(responses)
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "tei-b"
            target.mkdir()
            with self.assertRaisesRegex(ValueError, "新規path"):
                self.materialize(target, expected, responses, request=fake)
        self.assertEqual([], fake.calls)

    def test_symlink_output_parent_is_rejected_before_api_access(self):
        expected, responses = self.fixture()
        fake = FakeGitHub(responses)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            actual = root / "actual"
            actual.mkdir()
            linked = root / "linked"
            try:
                linked.symlink_to(actual, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("symlinkを作成できない環境です")
            target = linked / "tei-b"
            with self.assertRaisesRegex(ValueError, "symlink"):
                self.materialize(target, expected, responses, request=fake)
            self.assertFalse((actual / "tei-b").exists())
        self.assertEqual([], fake.calls)

    def test_output_created_during_acquisition_is_not_overwritten(self):
        expected, responses = self.fixture()
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            target = parent / "tei-b"
            fake = FakeGitHub(responses)

            def racing_request(url: str, token: str):
                payload = fake(url, token)
                if url.endswith(f"git/commits/{expected['commit']}"):
                    target.mkdir()
                    (target / "marker").write_text("keep", encoding="utf-8")
                return payload

            with self.assertRaisesRegex(ValueError, "暗黙上書き"):
                self.materialize(
                    target,
                    expected,
                    responses,
                    request=racing_request,
                )
            self.assertEqual(
                "keep",
                (target / "marker").read_text(encoding="utf-8"),
            )
            self.assertEqual([], list(parent.glob(".tei-b.staging-*")))

    def test_truncated_tree_is_rejected(self):
        expected, responses = self.fixture()
        responses = dict(responses)
        key = f"git/trees/{expected['rootTree']}"
        changed = dict(responses[key])
        changed["truncated"] = True
        responses[key] = changed

        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "tei-b"
            with self.assertRaisesRegex(ValueError, "truncated=false"):
                self.materialize(target, expected, responses)
            self.assertFalse(target.exists())


if __name__ == "__main__":
    unittest.main()
