package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"

	"github.com/hat47x/sei-cognition/evaluation/sparse-associative-cognition/prototype-go/modelprobe"
)

func main() {
	rawPath := flag.String("raw", "", "raw-mode actual run artifact JSON")
	workspacePath := flag.String("workspace", "", "workspace-mode actual run artifact JSON")
	stagedPath := flag.String("staged", "", "staged-mode actual run artifact JSON")
	outputPath := flag.String("output", "", "optional new output JSON path; stdout when omitted")
	flag.Parse()

	if *rawPath == "" || *workspacePath == "" || *stagedPath == "" {
		fatalf("--raw, --workspace, and --staged are required")
	}

	raw := readArtifact(*rawPath)
	workspace := readArtifact(*workspacePath)
	staged := readArtifact(*stagedPath)

	comparison, err := modelprobe.CompareActualRuns(raw, workspace, staged)
	if err != nil {
		fatalf("compare runs: %v", err)
	}

	if *outputPath == "" {
		encoder := json.NewEncoder(os.Stdout)
		encoder.SetIndent("", "  ")
		if err := encoder.Encode(comparison); err != nil {
			fatalf("encode comparison: %v", err)
		}
		return
	}

	file, err := os.OpenFile(*outputPath, os.O_WRONLY|os.O_CREATE|os.O_EXCL, 0o600)
	if err != nil {
		fatalf("open output: %v", err)
	}
	encoder := json.NewEncoder(file)
	encoder.SetIndent("", "  ")
	if err := encoder.Encode(comparison); err != nil {
		_ = file.Close()
		fatalf("encode comparison: %v", err)
	}
	if err := file.Close(); err != nil {
		fatalf("close output: %v", err)
	}
}

func readArtifact(path string) modelprobe.ActualRunArtifact {
	file, err := os.Open(path)
	if err != nil {
		fatalf("open %s: %v", path, err)
	}
	defer file.Close()

	var artifact modelprobe.ActualRunArtifact
	decoder := json.NewDecoder(file)
	decoder.DisallowUnknownFields()
	if err := decoder.Decode(&artifact); err != nil {
		fatalf("decode %s: %v", path, err)
	}
	return artifact
}

func fatalf(format string, args ...any) {
	fmt.Fprintf(os.Stderr, format+"\n", args...)
	os.Exit(1)
}
