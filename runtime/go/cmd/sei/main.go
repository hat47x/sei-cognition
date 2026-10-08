package main

import (
	"context"
	"errors"
	"fmt"
	"os"

	"github.com/hat47x/sei-cognition/runtime/go/seicli"
)

func main() {
	if err := seicli.Run(context.Background(), os.Args[1:], os.Stdout, os.Stderr); err != nil {
		fmt.Fprintln(os.Stderr, "sei:", err)
		var exit *seicli.ExitError
		if errors.As(err, &exit) {
			os.Exit(exit.Code)
		}
		os.Exit(1)
	}
}
