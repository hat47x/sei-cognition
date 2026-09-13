package main

import (
	"context"
	"flag"
	"fmt"
	"os"

	"github.com/hat47x/soza/evaluation/sparse-associative-cognition/prototype-go/modelprobe"
)

func main() {
	endpoint := flag.String("endpoint", "http://127.0.0.1:8080/health", "runtime health endpoint")
	runtimeName := flag.String("runtime", "", "runtime name")
	runtimeVersion := flag.String("runtime-version", "", "runtime version")
	model := flag.String("model", "", "model identifier")
	quant := flag.String("quantization", "", "quantization label")
	ctxSize := flag.Int("context-size", 0, "context size")
	threads := flag.Int("threads", 0, "runtime thread count")
	fixture := flag.String("fixture", "", "probe fixture id")
	mode := flag.String("mode", "", "probe mode: raw|workspace|staged")
	flag.Parse()

	m := modelprobe.Preflight(context.Background(), *endpoint, nil)
	m.RuntimeName = *runtimeName
	m.RuntimeVersion = *runtimeVersion
	m.Model = *model
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
