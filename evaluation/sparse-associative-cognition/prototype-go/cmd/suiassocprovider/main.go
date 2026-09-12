// Command suiassocprovider exposes the evaluation-only SACS provider through a
// one-request stdin/stdout transport. Transport is intentionally thinner than
// the cognitive contract: one JSON request enters on stdin and one JSON
// response leaves on stdout. Diagnostics go to stderr only.
package main

import (
	"encoding/json"
	"fmt"
	"io"
	"os"

	"github.com/hat47x/soza/evaluation/sparse-associative-cognition/prototype-go/sparseassoc"
	"github.com/hat47x/soza/evaluation/sparse-associative-cognition/prototype-go/suiassocprovider"
)

const implementationVersion = "sacs-go-eval-v1-d4096-f8-a64-s47-t0.10"

func newProvider() (*suiassocprovider.Provider, error) {
	return suiassocprovider.New(suiassocprovider.Config{
		Sparse: sparseassoc.Config{
			Dimensions: 4096,
			Fanout:     8,
			Active:     64,
			Seed:       47,
		},
		MinInternalSimilarity: 0.10,
		ProviderID:            "sei-sacs-go-eval",
		ImplementationVersion: implementationVersion,
	})
}

func run(in io.Reader, out io.Writer, errOut io.Writer) int {
	data, err := io.ReadAll(io.LimitReader(in, 4<<20))
	if err != nil {
		fmt.Fprintf(errOut, "read request: %v\n", err)
		return 2
	}
	if len(data) == 4<<20 {
		fmt.Fprintln(errOut, "request exceeds 4 MiB transport limit")
		return 2
	}

	req, err := suiassocprovider.DecodeRequest(data)
	if err != nil {
		fmt.Fprintf(errOut, "invalid request: %v\n", err)
		return 2
	}
	provider, err := newProvider()
	if err != nil {
		fmt.Fprintf(errOut, "provider configuration: %v\n", err)
		return 3
	}
	resp, err := provider.Handle(req)
	if err != nil {
		fmt.Fprintf(errOut, "provider execution: %v\n", err)
		return 3
	}

	enc := json.NewEncoder(out)
	enc.SetEscapeHTML(false)
	if err := enc.Encode(resp); err != nil {
		fmt.Fprintf(errOut, "encode response: %v\n", err)
		return 3
	}
	return 0
}

func main() {
	os.Exit(run(os.Stdin, os.Stdout, os.Stderr))
}
