"""fixtures/contracts/v1alpha1/loader-schema-gap/cases.json の全行を検査する(#744)。

基準の文書はschemaに適合し、各caseの文書はschemaに違反する。Go loaderの挙動
(loader_accepts)は runtime/go/semanticruntime/schema_gap_test.go が固定する。
jsonschema と referencing が無い環境では skip する。
"""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    import check_contract_conformance as ccc
    HAVE_DEPS = True
except SystemExit:
    HAVE_DEPS = False
except ImportError:
    HAVE_DEPS = False

CASES = Path(__file__).resolve().parent.parent / "fixtures" / "contracts" / "v1alpha1" / "loader-schema-gap" / "cases.json"


@unittest.skipUnless(HAVE_DEPS, "jsonschema and referencing are required")
class LoaderSchemaGapTable(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.table = json.loads(CASES.read_text(encoding="utf-8"))
        cls.schemas, cls.registry = ccc.load_schemas()

    def schema_name(self, name):
        self.assertIn(name, self.schemas)
        return name

    def test_bases_satisfy_the_schema(self):
        for key, base in self.table["bases"].items():
            errors = ccc.schema_errors(self.schema_name(base["schema"]), base["document"], self.schemas, self.registry)
            self.assertEqual(errors, [], key)

    def test_every_case_violates_the_schema(self):
        for case in self.table["cases"]:
            errors = ccc.schema_errors(self.schema_name(case["schema"]), case["document"], self.schemas, self.registry)
            self.assertTrue(errors, case["name"] + " must violate the schema")


if __name__ == "__main__":
    unittest.main()
