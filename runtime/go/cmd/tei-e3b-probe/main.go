package main

import (
	"context"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"os"
	"time"

	"github.com/hat47x/sei-cognition/runtime/go/provideradapter"
	"github.com/hat47x/sei-cognition/runtime/go/semanticruntime"
	"github.com/hat47x/sei-cognition/runtime/go/teiintegration"
	"github.com/hat47x/sei-cognition/runtime/go/teiprobe"
)

func main() {
	if err := run(os.Args[1:]); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}

func run(args []string) error {
	flags := flag.NewFlagSet("tei-e3b-probe", flag.ContinueOnError)
	flags.SetOutput(os.Stderr)

	binary := flags.String("binary", "", "direct TEI executable file")
	sourceRepository := flags.String("source-repository", "", "declared TEI source repository")
	sourceCommit := flags.String("source-commit", "", "declared TEI source commit")
	manifest := flags.String("manifest", "", "optional TEI build manifest JSON")

	workspace := flags.String("workspace", "", "TEI workspace path")
	runPath := flags.String("run", "", "TEI durable run path")
	solution := flags.String("solution", "", "TEI solution ID")
	version := flags.String("version", "", "TEI solution version")
	pluginLock := flags.String("plugin-lock", "", "TEI plugin lock path")
	expectedRevision := flags.Int("expected-revision", -1, "optional expected durable-run revision")

	observationID := flags.String("observation-id", "", "Capability Observation ID")
	capabilityKind := flags.String("capability-kind", "capability", "Capability reference kind")
	capabilityID := flags.String("capability-id", "", "Capability reference ID")
	observedAt := flags.String("observed-at", "", "observation timestamp")
	sourceStateRef := flags.String("source-state-ref", "", "non-secret source state reference")
	timeout := flags.Duration("timeout", 30*time.Second, "TEI process timeout")

	if err := flags.Parse(args); err != nil {
		return err
	}
	if flags.NArg() != 0 {
		return errors.New("positional arguments are not supported")
	}
	if *timeout <= 0 {
		return errors.New("--timeout must be greater than zero")
	}

	var expectedRevisionPtr *int
	if *expectedRevision >= 0 {
		value := *expectedRevision
		expectedRevisionPtr = &value
	}

	request := teiprobe.Request{
		BinaryPath:         *binary,
		DeclaredRepository: *sourceRepository,
		DeclaredCommit:     *sourceCommit,
		ManifestPath:       *manifest,
		ProviderPlan: teiintegration.ProviderPlanRequest{
			Workspace:        *workspace,
			Run:              *runPath,
			Solution:         *solution,
			Version:          *version,
			PluginLock:       *pluginLock,
			ExpectedRevision: expectedRevisionPtr,
		},
		ObservationContext: provideradapter.ObservationContext{
			ObservationID: *observationID,
			CapabilityRef: semanticruntime.LogicalReference{
				Kind: *capabilityKind,
				ID:   *capabilityID,
			},
			ObservedAt:     *observedAt,
			SourceStateRef: *sourceStateRef,
		},
	}

	ctx, cancel := context.WithTimeout(context.Background(), *timeout)
	defer cancel()

	report, err := teiprobe.Probe(ctx, request)
	if err != nil {
		return err
	}

	encoder := json.NewEncoder(os.Stdout)
	encoder.SetEscapeHTML(false)
	encoder.SetIndent("", "  ")
	if err := encoder.Encode(report); err != nil {
		return fmt.Errorf("write TEI Evidence report: %w", err)
	}
	return nil
}
