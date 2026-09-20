package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"

	"github.com/hat47x/sei-cognition/evaluation/sparse-associative-cognition/prototype-go/modelprobe"
)

func main() {
	matrixPath := flag.String("matrix", "", "complete local-model matrix artifact JSON")
	reviewPath := flag.String("review", "", "filled human adjudication JSON; omit to generate a template")
	reviewerLabel := flag.String("reviewer-label", "", "non-empty reviewer label used when generating a template")
	outputPath := flag.String("output", "", "new output JSON path")
	flag.Parse()

	if *matrixPath == "" {
		fatalf("--matrix is required")
	}
	if *outputPath == "" {
		fatalf("--output is required")
	}
	if _, err := os.Stat(*outputPath); err == nil {
		fatalf("output already exists: %s", *outputPath)
	} else if !os.IsNotExist(err) {
		fatalf("inspect output: %v", err)
	}

	var matrix modelprobe.ActualMatrixArtifact
	readStrictJSON(*matrixPath, &matrix)

	if *reviewPath == "" {
		template, err := modelprobe.BuildHumanAdjudicationTemplate(matrix, *reviewerLabel)
		if err != nil {
			fatalf("build review template: %v", err)
		}
		if err := writeJSONExclusive(*outputPath, template); err != nil {
			fatalf("write review template: %v", err)
		}
		return
	}

	if *reviewerLabel != "" {
		fatalf("--reviewer-label is only valid when generating a template")
	}
	var review modelprobe.HumanAdjudication
	readStrictJSON(*reviewPath, &review)
	report, err := modelprobe.ValidateHumanAdjudication(matrix, review)
	if err != nil {
		fatalf("validate human adjudication: %v", err)
	}
	if err := writeJSONExclusive(*outputPath, report); err != nil {
		fatalf("write adjudication report: %v", err)
	}
}

func readStrictJSON(path string, value any) {
	file, err := os.Open(path)
	if err != nil {
		fatalf("open %s: %v", path, err)
	}
	defer file.Close()

	decoder := json.NewDecoder(file)
	decoder.DisallowUnknownFields()
	if err := decoder.Decode(value); err != nil {
		fatalf("decode %s: %v", path, err)
	}
}

func writeJSONExclusive(path string, value any) error {
	file, err := os.OpenFile(path, os.O_WRONLY|os.O_CREATE|os.O_EXCL, 0o600)
	if err != nil {
		return err
	}
	encoder := json.NewEncoder(file)
	encoder.SetIndent("", "  ")
	if err := encoder.Encode(value); err != nil {
		_ = file.Close()
		return err
	}
	return file.Close()
}

func fatalf(format string, args ...any) {
	fmt.Fprintf(os.Stderr, format+"\n", args...)
	os.Exit(1)
}
