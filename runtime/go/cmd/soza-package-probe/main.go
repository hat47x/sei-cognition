package main

import (
	"context"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"os"

	"github.com/hat47x/soza/runtime/go/packagingprobe"
	"github.com/hat47x/soza/runtime/go/semanticruntime"
)

type inspectResult struct {
	BundleID         string `json:"bundle_id"`
	RecordCount      int    `json:"record_count"`
	ValidatedCount   int    `json:"validated_count"`
	NotVerifiedCount int    `json:"not_verified_count"`
}

func main() {
	if err := run(context.Background(), os.Args[1:]); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}

func run(ctx context.Context, args []string) error {
	if len(args) == 0 {
		return errors.New("subcommand is required: save or inspect")
	}

	switch args[0] {
	case "save":
		return runSave(ctx, args[1:])
	case "inspect":
		return runInspect(ctx, args[1:])
	default:
		return fmt.Errorf("unknown subcommand %q: expected save or inspect", args[0])
	}
}

func runSave(ctx context.Context, args []string) error {
	flags := flag.NewFlagSet("save", flag.ContinueOnError)
	flags.SetOutput(os.Stderr)
	dataRoot := flags.String("data-root", "", "filesystem data root")
	input := flags.String("input", "", "Semantic Interchange JSON file")
	if err := flags.Parse(args); err != nil {
		return err
	}
	if *dataRoot == "" {
		return errors.New("save requires --data-root")
	}
	if *input == "" {
		return errors.New("save requires --input")
	}

	data, err := os.ReadFile(*input)
	if err != nil {
		return fmt.Errorf("read input: %w", err)
	}
	persistence := packagingprobe.FilePersistence{DataRoot: *dataRoot}
	if err := packagingprobe.Import(ctx, persistence, data); err != nil {
		return fmt.Errorf("save package: %w", err)
	}
	return nil
}

func runInspect(ctx context.Context, args []string) error {
	flags := flag.NewFlagSet("inspect", flag.ContinueOnError)
	flags.SetOutput(os.Stderr)
	dataRoot := flags.String("data-root", "", "filesystem data root")
	if err := flags.Parse(args); err != nil {
		return err
	}
	if *dataRoot == "" {
		return errors.New("inspect requires --data-root")
	}

	bundle, err := packagingprobe.LoadBundle(ctx, packagingprobe.FilePersistence{DataRoot: *dataRoot})
	if err != nil {
		return fmt.Errorf("load package: %w", err)
	}

	result := inspectResult{
		BundleID:    bundle.Envelope.BundleID,
		RecordCount: len(bundle.Records),
	}
	for _, record := range bundle.Records {
		switch record.Status {
		case semanticruntime.RecordValidated:
			result.ValidatedCount++
		case semanticruntime.RecordNotVerified:
			result.NotVerifiedCount++
		}
	}

	encoder := json.NewEncoder(os.Stdout)
	encoder.SetEscapeHTML(false)
	if err := encoder.Encode(result); err != nil {
		return fmt.Errorf("write inspection result: %w", err)
	}
	return nil
}
