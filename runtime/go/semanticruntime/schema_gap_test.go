package semanticruntime

import (
	"encoding/json"
	"testing"
)

// schemaGapFile は、同梱のJSON Schemaが拒否する入力と、Go loaderの現在の挙動を
// 固定した表である(#744)。表は fixtures/contracts/v1alpha1/loader-schema-gap/cases.json
// にあり、tools/test_loader_schema_gap.py が全行をschemaで検査する。
// loader_accepts が true の行は、loaderがschemaより緩い現状の差である。loaderを
// 厳しくする、またはschemaを緩めると、この表の行が変わる。
type schemaGapFile struct {
	Bases map[string]struct {
		Schema   string          `json:"schema"`
		Document json.RawMessage `json:"document"`
	} `json:"bases"`
	Cases []struct {
		Name          string          `json:"name"`
		Schema        string          `json:"schema"`
		Document      json.RawMessage `json:"document"`
		LoaderAccepts bool            `json:"loader_accepts"`
	} `json:"cases"`
}

func loadForSchema(schema string, document []byte) error {
	if schema == "semantic-interchange" {
		_, err := LoadInterchange(document)
		return err
	}
	_, err := LoadStandalone(document)
	return err
}

func readSchemaGapFile(t *testing.T) schemaGapFile {
	t.Helper()
	var file schemaGapFile
	if err := json.Unmarshal(readFixture(t, "loader-schema-gap", "cases.json"), &file); err != nil {
		t.Fatal(err)
	}
	if len(file.Cases) == 0 || len(file.Bases) == 0 {
		t.Fatal("schema gap table is empty")
	}
	return file
}

func TestLoaderAgainstSchemaViolations(t *testing.T) {
	for _, tc := range readSchemaGapFile(t).Cases {
		t.Run(tc.Name, func(t *testing.T) {
			err := loadForSchema(tc.Schema, tc.Document)
			if accepted := err == nil; accepted != tc.LoaderAccepts {
				t.Fatalf("loader accepted=%v, pinned %v (err: %v)", accepted, tc.LoaderAccepts, err)
			}
		})
	}
}

// 基準の入力は、loaderとschemaの双方で有効である(schema側はPythonの試験が見る)。
func TestSchemaGapBasesAreAcceptedByLoader(t *testing.T) {
	for name, base := range readSchemaGapFile(t).Bases {
		if err := loadForSchema(base.Schema, base.Document); err != nil {
			t.Errorf("base %s rejected: %v", name, err)
		}
	}
}
