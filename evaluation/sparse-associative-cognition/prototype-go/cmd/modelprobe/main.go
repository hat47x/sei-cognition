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
	flag.Parse()

	mode := modelprobe.Mode(*modeFlag)
	if mode != modelprobe.ModeRaw && mode != modelprobe.ModeWorkspace && mode != modelprobe.ModeStaged {
		fatalf("unsupported --mode %q", *modeFlag)
	}

	fixtures := selectFixtures(*fixtureFlag)
	if len(fixtures) == 0 {
		fatalf("fixture not found: %s", *fixtureFlag)
	}

	encoder := json.NewEncoder(os.Stdout)
	encoder.SetIndent("", "  ")

	for _, fixture := range fixtures {
		if *dryRunFlag {
			plan, err := modelprobe.BuildPlan(fixture, mode)
			if err != nil {
				fatalf("%s: %v", fixture.ID, err)
			}
			if err := encoder.Encode(plan); err != nil {
				fatalf("encode plan: %v", err)
			}
			continue
		}

		ctx, cancel := context.WithTimeout(context.Background(), *timeoutFlag)
		result, err := modelprobe.Run(ctx, modelprobe.Config{
			Endpoint:  *endpointFlag,
			Model:     *modelFlag,
			MaxTokens: *maxTokensFlag,
		}, fixture, mode)
		cancel()
		if err != nil {
			fatalf("%s: %v", fixture.ID, err)
		}
		if err := encoder.Encode(result); err != nil {
			fatalf("encode result: %v", err)
		}
	}
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
