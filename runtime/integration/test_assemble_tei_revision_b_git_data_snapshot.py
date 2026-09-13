import json
import tempfile
import unittest
from pathlib import Path

import assemble_tei_revision_b_git_data_snapshot as assemble
import prepare_tei_revision_b_source as prepare
import prepare_tei_revision_b_source_from_snapshot as snapshot


class RevisionBSnapshotFragmentAssemblyTest(unittest.TestCase):
    def fragment(self, responses, **overrides):
        value = {
            "schema": snapshot.SNAPSHOT_SCHEMA,
            "repository": prepare.GITHUB_REPOSITORY,
            "sourceCommit": prepare.REVISION_B,
            "rootTree": prepare.REVISION_B_ROOT_TREE,
            "sourceAcquisition": snapshot.CANONICAL_SOURCE_ACQUISITION,
            "credentialSource": snapshot.CANONICAL_CREDENTIAL_SOURCE,
            "responses": responses,
        }
        value.update(overrides)
        return value

    def write_fragment(self, path: Path, responses, **overrides):
        path.write_text(
            json.dumps(
                self.fragment(responses, **overrides),
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            )
            + "\n",
            encoding="utf-8",
        )

    def test_disjoint_fragments_merge_into_existing_snapshot_schema(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first = root / "first.json"
            second = root / "second.json"
            output = root / "assembled.json"
            sha_a = "a" * 40
            sha_b = "b" * 40
            self.write_fragment(
                first,
                {f"git/blobs/{sha_a}": {"sha": sha_a, "content": "alpha"}},
            )
            self.write_fragment(
                second,
                {f"git/trees/{sha_b}": {"sha": sha_b, "tree": []}},
            )

            report = assemble.assemble_snapshot_fragments([first, second], output)
            loaded, loaded_sha256 = snapshot._load_snapshot(output)

            self.assertEqual(snapshot.SNAPSHOT_SCHEMA, loaded["schema"])
            self.assertEqual(prepare.REVISION_B, loaded["sourceCommit"])
            self.assertEqual(prepare.REVISION_B_ROOT_TREE, loaded["rootTree"])
            self.assertEqual(2, len(loaded["responses"]))
            self.assertEqual(2, report["snapshot"]["responses"])
            self.assertEqual(loaded_sha256, report["snapshot"]["sha256"])
            self.assertEqual(
                "not_evaluated_by_assembler",
                report["snapshot"]["completeness"],
            )
            self.assertTrue(report["snapshot"]["consumerValidationRequired"])
            self.assertFalse(report["snapshot"]["containsRuntimeCredential"])

    def test_identical_duplicate_response_is_deduplicated(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first = root / "first.json"
            second = root / "second.json"
            output = root / "assembled.json"
            sha = "c" * 40
            response = {"sha": sha, "content": "same"}
            self.write_fragment(first, {f"git/blobs/{sha}": response})
            self.write_fragment(second, {f"git/blobs/{sha}": response})

            report = assemble.assemble_snapshot_fragments([first, second], output)
            loaded, _ = snapshot._load_snapshot(output)

            self.assertEqual(1, len(loaded["responses"]))
            self.assertEqual(1, report["identicalDuplicateResponses"])

    def test_conflicting_duplicate_response_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first = root / "first.json"
            second = root / "second.json"
            output = root / "assembled.json"
            sha = "d" * 40
            self.write_fragment(
                first,
                {f"git/blobs/{sha}": {"sha": sha, "content": "first"}},
            )
            self.write_fragment(
                second,
                {f"git/blobs/{sha}": {"sha": sha, "content": "second"}},
            )

            with self.assertRaisesRegex(ValueError, "異なるpayload"):
                assemble.assemble_snapshot_fragments([first, second], output)
            self.assertFalse(output.exists())

    def test_fragment_metadata_drift_is_rejected_by_existing_loader(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fragment = root / "fragment.json"
            output = root / "assembled.json"
            sha = "e" * 40
            self.write_fragment(
                fragment,
                {f"git/blobs/{sha}": {"sha": sha}},
                sourceCommit="0" * 40,
            )

            with self.assertRaisesRegex(ValueError, "fixed revision B"):
                assemble.assemble_snapshot_fragments([fragment], output)
            self.assertFalse(output.exists())

    def test_output_bytes_do_not_depend_on_fragment_order(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first = root / "first.json"
            second = root / "second.json"
            output_ab = root / "ab.json"
            output_ba = root / "ba.json"
            sha_a = "1" * 40
            sha_b = "2" * 40
            self.write_fragment(
                first,
                {f"git/blobs/{sha_a}": {"sha": sha_a, "content": "a"}},
            )
            self.write_fragment(
                second,
                {f"git/blobs/{sha_b}": {"sha": sha_b, "content": "b"}},
            )

            assemble.assemble_snapshot_fragments([first, second], output_ab)
            assemble.assemble_snapshot_fragments([second, first], output_ba)

            self.assertEqual(output_ab.read_bytes(), output_ba.read_bytes())

    def test_existing_output_is_rejected_without_modification(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fragment = root / "fragment.json"
            output = root / "assembled.json"
            sha = "f" * 40
            self.write_fragment(
                fragment,
                {f"git/blobs/{sha}": {"sha": sha, "content": "value"}},
            )
            output.write_text("keep", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "新規path"):
                assemble.assemble_snapshot_fragments([fragment], output)
            self.assertEqual("keep", output.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
