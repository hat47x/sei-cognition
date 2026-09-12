package main

import (
	"bytes"
	"encoding/json"
	"strings"
	"testing"

	"github.com/hat47x/soza/evaluation/sparse-associative-cognition/prototype-go/suiassocprovider"
)

func validRequestJSON(t *testing.T) []byte {
	t.Helper()
	value := map[string]any{
		"schema":     suiassocprovider.RequestSchema,
		"requestId":  "transport-1",
		"networkId":  "network-1",
		"intent":     "neighborhood",
		"anchorRefs": []string{"c1"},
		"items": []any{
			map[string]any{
				"ref":  "c1",
				"kind": "card",
				"channels": map[string]any{
					"text": "現場観察では確認作業が増えた",
				},
			},
			map[string]any{
				"ref":  "c2",
				"kind": "card",
				"channels": map[string]any{
					"text": "確認作業の増加は引継ぎ時間にも影響している",
				},
			},
		},
		"policy": map[string]any{"candidateLimit": 1},
	}
	data, err := json.Marshal(value)
	if err != nil {
		t.Fatal(err)
	}
	return data
}

func TestRunWritesOneFormalResponseToStdout(t *testing.T) {
	var stdout, stderr bytes.Buffer
	code := run(bytes.NewReader(validRequestJSON(t)), &stdout, &stderr)
	if code != 0 {
		t.Fatalf("exit=%d stderr=%q", code, stderr.String())
	}
	if stderr.Len() != 0 {
		t.Fatalf("unexpected stderr: %q", stderr.String())
	}

	var resp suiassocprovider.Response
	dec := json.NewDecoder(&stdout)
	dec.DisallowUnknownFields()
	if err := dec.Decode(&resp); err != nil {
		t.Fatal(err)
	}
	if resp.Schema != suiassocprovider.ResponseSchema || resp.RequestID != "transport-1" {
		t.Fatalf("unexpected response: %#v", resp)
	}
	if resp.Provider.ProviderID != "sei-sacs-go-eval" || resp.Provider.ImplementationVersion != implementationVersion {
		t.Fatalf("unexpected provider trace: %#v", resp.Provider)
	}

	encoded := stdout.String()
	for _, forbidden := range []string{
		`"similarity"`, `"activation"`, `"confidence"`, `"importance"`,
		`"rank"`, `"score"`, `"novelty_signal"`,
	} {
		if strings.Contains(encoded, forbidden) {
			t.Fatalf("transport leaked %s: %s", forbidden, encoded)
		}
	}
}

func TestRunKeepsDiagnosticsOffStdout(t *testing.T) {
	var stdout, stderr bytes.Buffer
	code := run(strings.NewReader(`{"schema":"broken"}`), &stdout, &stderr)
	if code == 0 {
		t.Fatal("expected non-zero exit")
	}
	if stdout.Len() != 0 {
		t.Fatalf("stdout must stay empty on invalid request: %q", stdout.String())
	}
	if !strings.Contains(stderr.String(), "invalid request") {
		t.Fatalf("missing stderr diagnostic: %q", stderr.String())
	}
}

func TestRunRejectsTrailingSecondJSONValue(t *testing.T) {
	payload := append(validRequestJSON(t), []byte(` {}`)...)
	var stdout, stderr bytes.Buffer
	code := run(bytes.NewReader(payload), &stdout, &stderr)
	if code == 0 {
		t.Fatal("expected non-zero exit")
	}
	if stdout.Len() != 0 {
		t.Fatalf("unexpected stdout: %q", stdout.String())
	}
}

func TestRunRejectsOversizedTransportPayload(t *testing.T) {
	var stdout, stderr bytes.Buffer
	payload := strings.Repeat("x", 4<<20)
	code := run(strings.NewReader(payload), &stdout, &stderr)
	if code == 0 {
		t.Fatal("expected non-zero exit")
	}
	if stdout.Len() != 0 {
		t.Fatalf("unexpected stdout: %q", stdout.String())
	}
	if !strings.Contains(stderr.String(), "4 MiB") {
		t.Fatalf("missing size diagnostic: %q", stderr.String())
	}
}
