package main

import (
	"context"
	"flag"
	"fmt"
	"os"

	"github.com/hat47x/sei-cognition/evaluation/sparse-associative-cognition/prototype-go/modelprobe"
)

func main() {
	runID := flag.String("run-id", "", "stable run identity shared with actual telemetry")
	sourceGitSHA := flag.String("source-git-sha", "", "exact lowercase 40-character source Git SHA")
	endpoint := flag.String("endpoint", "http://127.0.0.1:8080/health", "runtime health endpoint")
	runtimeName := flag.String("runtime", "", "runtime name")
	runtimeVersion := flag.String("runtime-version", "", "runtime version")
	runtimePID := flag.Int("runtime-pid", 0, "optional local runtime server PID for Linux executable identity")
	model := flag.String("model", "", "model identifier")
	modelFile := flag.String("model-file", "", "optional local model artifact file to hash for provenance")
	expectedModelSHA256 := flag.String("expected-model-sha256", "", "optional expected SHA-256 for --model-file")
	quant := flag.String("quantization", "", "quantization label")
	ctxSize := flag.Int("context-size", 0, "context size")
	threads := flag.Int("threads", 0, "runtime thread count")
	fixture := flag.String("fixture", "", "probe fixture id")
	mode := flag.String("mode", "", "probe mode: raw|workspace|staged")
	flag.Parse()

	if (*runID == "") != (*sourceGitSHA == "") {
		fmt.Fprintln(os.Stderr, "--run-id and --source-git-sha must be supplied together")
		os.Exit(2)
	}
	resolvedSourceGitSHA := ""
	if *runID != "" {
		if err := modelprobe.ValidateRunIdentity(*runID, *sourceGitSHA); err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(2)
		}
		var err error
		resolvedSourceGitSHA, err = modelprobe.ResolveExactSourceGitSHA(*sourceGitSHA)
		if err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(2)
		}
	}

	modelArtifact, err := modelprobe.ObserveModelArtifact(*modelFile, *expectedModelSHA256)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(2)
	}

	m := modelprobe.Preflight(context.Background(), *endpoint, nil)
	m.RunID = *runID
	m.SourceGitSHA = resolvedSourceGitSHA
	m.RuntimeName = *runtimeName
	m.RuntimeVersion = *runtimeVersion
	m.RuntimeProcess = modelprobe.ObserveRuntimeProcessIdentity(*runtimePID)
	m.Model = *model
	m.ModelArtifact = modelArtifact
	m.Quantization = *quant
	m.ContextSize = *ctxSize
	m.Threads = *threads
	m.Fixture = *fixture
	m.Mode = modelprobe.Mode(*mode)

	b, err := m.JSON()
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	fmt.Println(string(b))
}
