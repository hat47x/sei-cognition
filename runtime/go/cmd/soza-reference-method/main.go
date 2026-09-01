package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"
)

type request struct {
	Inquiry        string   `json:"inquiry"`
	ObservationIDs []string `json:"observation_ids"`
	UnresolvedIDs  []string `json:"unresolved_ids"`
}

type response struct {
	Summary        string   `json:"summary"`
	Recommendation string   `json:"recommendation"`
	ResidualIDs    []string `json:"residual_ids"`
}

func main() {
	profile := flag.String("profile", "", "reference method profile: evidence-first or cautious")
	flag.Parse()

	var input request
	if err := json.NewDecoder(os.Stdin).Decode(&input); err != nil {
		fail("入力JSONを読めません: %v", err)
	}
	if input.Inquiry == "" {
		fail("inquiryは必須です")
	}

	result := response{ResidualIDs: append([]string(nil), input.UnresolvedIDs...)}
	switch *profile {
	case "evidence-first":
		result.Summary = "観測済みの情報と未解決事項を分け、観測済みの根拠を優先して候補を整理した"
		result.Recommendation = "観測済みの可用性を根拠に実行候補とし、未解決事項は後続確認へ残す"
	case "cautious":
		result.Summary = "未解決事項を残したまま、可逆性を優先して限定的な次の行動を整理した"
		result.Recommendation = "未解決事項を残したまま、取り消し可能な範囲で限定実行する"
	default:
		fail("profileはevidence-firstまたはcautiousを指定してください")
	}

	if err := json.NewEncoder(os.Stdout).Encode(result); err != nil {
		fail("出力JSONを書けません: %v", err)
	}
}

func fail(format string, args ...any) {
	fmt.Fprintf(os.Stderr, format+"\n", args...)
	os.Exit(2)
}
