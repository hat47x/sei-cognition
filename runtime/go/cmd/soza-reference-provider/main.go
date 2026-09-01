package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"
)

type request struct {
	State string `json:"state"`
}

type providerAState struct {
	Health     string `json:"health"`
	DelayMS    int64  `json:"delay_ms"`
	ServiceRef string `json:"service_ref"`
}

type providerBState struct {
	Ready           bool    `json:"ready"`
	ResponseSeconds float64 `json:"response_seconds"`
	Endpoint        string  `json:"endpoint"`
}

func main() {
	profile := flag.String("profile", "", "reference provider profile: a or b")
	flag.Parse()

	var input request
	if err := json.NewDecoder(os.Stdin).Decode(&input); err != nil {
		fail("入力JSONを読めません: %v", err)
	}
	if input.State == "" {
		fail("stateは必須です")
	}

	encoder := json.NewEncoder(os.Stdout)
	switch *profile {
	case "a":
		state := providerAState{ServiceRef: "reference://provider-a/service"}
		switch input.State {
		case "healthy":
			state.Health = "green"
			state.DelayMS = 120
		case "degraded":
			state.Health = "amber"
			state.DelayMS = 260
		default:
			fail("profile aでは未対応のstateです: %s", input.State)
		}
		if err := encoder.Encode(state); err != nil {
			fail("出力JSONを書けません: %v", err)
		}
	case "b":
		state := providerBState{Endpoint: "reference://provider-b/endpoint"}
		switch input.State {
		case "healthy":
			state.Ready = true
			state.ResponseSeconds = 0.09
		case "degraded":
			state.Ready = false
			state.ResponseSeconds = 0.31
		default:
			fail("profile bでは未対応のstateです: %s", input.State)
		}
		if err := encoder.Encode(state); err != nil {
			fail("出力JSONを書けません: %v", err)
		}
	default:
		fail("profileはaまたはbを指定してください")
	}
}

func fail(format string, args ...any) {
	fmt.Fprintf(os.Stderr, format+"\n", args...)
	os.Exit(2)
}
