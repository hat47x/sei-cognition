package main

import (
	"context"
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"time"

	"github.com/hat47x/sei-cognition/evaluation/sparse-associative-cognition/prototype-go/cognitiveeval"
	"github.com/hat47x/sei-cognition/evaluation/sparse-associative-cognition/prototype-go/modelprobe"
)

func main() {
	modeFlag := flag.String("mode", "staged", "probe mode: raw, workspace, or staged")
	fixtureFlag := flag.String("fixture", "all", "fixture id or all")
	endpointFlag := flag.String("endpoint", "http://127.0.0.1:8080/v1/chat/completions", "OpenAI-compatible chat-completions endpoint")
	modelFlag := flag.String("model", "local-model", "model id sent to endpoint")
	dryRunFlag := flag.Bool("dry-run", false, "print probe plans without invoking a model")
	timeoutFlag := flag.Duration("timeout", 120*time.Second, "per-request timeout")
	maxTokensFlag := flag.Int("max-tokens", 800, "maximum completion tokens")
	runIDFlag := flag.String("run-id", "", "stable run identity shared with preflight")
	sourceGitSHAFlag := flag.String("source-git-sha", "", "exact lowercase 40-character source Git SHA")
	telemetryJSONFlag := flag.String("telemetry-json", "", "write run-level actual invocation telemetry to a new JSON file")
	runJSONFlag := flag.String("run-json", "", "write results plus telemetry as a new actual-run artifact JSON file")
	flag.Parse()

	mode := modelprobe.Mode(*modeFlag)
	if mode != modelprobe.ModeRaw && mode != modelprobe.ModeWorkspace && mode != modelprobe.ModeStaged {
		fatalf("unsupported --mode %q", *modeFlag)
	}

	fixtures := selectFixtures(*fixtureFlag)
	if len(fixtures) == 0 {
		fatalf("fixture not found: %s", *fixtureFlag)
	}

	artifactMode := *telemetryJSONFlag != "" || *runJSONFlag != ""
	if *dryRunFlag && artifactMode {
		fatalf("--telemetry-json/--run-json are for actual inference and cannot be combined with --dry-run")
	}
	if artifactMode {
		if err := modelprobe.ValidateRunIdentity(*runIDFlag, *sourceGitSHAFlag); err != nil {
			fatalf("%v", err)
		}
		if *telemetryJSONFlag != "" {
			ensureNewOutput(*telemetryJSONFlag, "telemetry")
		}
		if *runJSONFlag != "" {
			ensureNewOutput(*runJSONFlag, "run artifact")
		}
		if *telemetryJSONFlag != "" && *runJSONFlag != "" && *telemetryJSONFlag == *runJSONFlag {
			fatalf("--telemetry-json and --run-json must use different paths")
		}
	}

	encoder := json.NewEncoder(os.Stdout)
	encoder.SetIndent("", "  ")
	observations := make([]modelprobe.ActualRunObservation, 0, len(fixtures))
	results := make([]modelprobe.Result, 0, len(fixtures))
	hadRunError := false

	for _, fixture := range fixtures {
		plan, err := modelprobe.BuildPlan(fixture, mode)
		if err != nil {
			fatalf("%s: %v", fixture.ID, err)
		}
		if *dryRunFlag {
			if err := encoder.Encode(plan); err != nil {
				fatalf("encode plan: %v", err)
			}
			continue
		}

		ctx, cancel := context.WithTimeout(context.Background(), *timeoutFlag)
		result, runErr := modelprobe.Run(ctx, modelprobe.Config{
			Endpoint:  *endpointFlag,
			Model:     *modelFlag,
			MaxTokens: *maxTokensFlag,
		}, fixture, mode)
		cancel()

		if artifactMode {
			observations = append(
				observations,
				modelprobe.ObserveActualRun(plan, result, runErr),
			)
		}

		if runErr != nil {
			if !artifactMode {
				fatalf("%s: %v", fixture.ID, runErr)
			}
			fmt.Fprintf(os.Stderr, "%s: %v\n", fixture.ID, runErr)
			hadRunError = true
			continue
		}

		results = append(results, result)
		if err := encoder.Encode(result); err != nil {
			fatalf("encode result: %v", err)
		}
	}

	if !artifactMode {
		return
	}

	summary, err := modelprobe.SummarizeActualTelemetry(
		*runIDFlag,
		*sourceGitSHAFlag,
		*modelFlag,
		mode,
		fixtures,
		observations,
	)
	if err != nil {
		fatalf("summarize actual telemetry: %v", err)
	}
	if *telemetryJSONFlag != "" {
		if err := writeJSONExclusive(*telemetryJSONFlag, summary); err != nil {
			fatalf("write telemetry: %v", err)
		}
	}
	if *runJSONFlag != "" {
		artifact, err := modelprobe.BuildActualRunArtifact(summary, results)
		if err != nil {
			fatalf("build run artifact: %v", err)
		}
		if err := writeJSONExclusive(*runJSONFlag, artifact); err != nil {
			fatalf("write run artifact: %v", err)
		}
	}
	if hadRunError || !summary.CompleteWithoutInvocationError {
		os.Exit(1)
	}
}

func ensureNewOutput(path string, label string) {
	if _, err := os.Stat(path); err == nil {
		fatalf("%s output already exists: %s", label, path)
	} else if !os.IsNotExist(err) {
		fatalf("inspect %s output: %v", label, err)
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

func selectFixtures(id string) []cognitiveeval.Fixture {
	all := cognitiveeval.ReferenceFixtures()
	if id == "all" {
		return all
	}
	for _, fixture := range all {
		if fixture.ID == id {
			return []cognitiveeval.Fixture{fixture}
		}
	}
	return nil
}

func fatalf(format string, args ...any) {
	fmt.Fprintf(os.Stderr, format+"\n", args...)
	os.Exit(1)
}
