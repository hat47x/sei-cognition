package main

import (
	"bytes"
	"crypto/sha256"
	"encoding/json"
	"fmt"
	"io"
	"math/big"
	"os"
	"strings"

	"github.com/gowebpki/jcs"
)

const safeIntegerMax = "9007199254740991"

type fixture struct {
	ProfileID string `json:"profile_id"`
	Cases     []struct {
		ID                string `json:"id"`
		Expect            string `json:"expect"`
		Input             string `json:"input"`
		ExpectedCanonical string `json:"expected_canonical"`
		ExpectedDigest    string `json:"expected_digest"`
	} `json:"cases"`
}

func validateSafeIntegers(raw []byte) error {
	decoder := json.NewDecoder(bytes.NewReader(raw))
	decoder.UseNumber()
	var value any
	if err := decoder.Decode(&value); err != nil {
		return err
	}
	var extra any
	if err := decoder.Decode(&extra); err != io.EOF {
		if err == nil {
			return fmt.Errorf("multiple JSON values")
		}
		return err
	}
	limit := new(big.Int)
	limit.SetString(safeIntegerMax, 10)
	return walkNumbers(value, limit)
}

func walkNumbers(value any, limit *big.Int) error {
	switch v := value.(type) {
	case json.Number:
		text := v.String()
		if strings.ContainsAny(text, ".eE") {
			return nil
		}
		n := new(big.Int)
		if _, ok := n.SetString(text, 10); !ok {
			return fmt.Errorf("invalid integer literal: %s", text)
		}
		abs := new(big.Int).Abs(n)
		if abs.Cmp(limit) > 0 {
			return fmt.Errorf("unsafe integer outside IEEE-754 safe range: %s", text)
		}
	case []any:
		for _, item := range v {
			if err := walkNumbers(item, limit); err != nil {
				return err
			}
		}
	case map[string]any:
		for _, item := range v {
			if err := walkNumbers(item, limit); err != nil {
				return err
			}
		}
	}
	return nil
}

func digest(data []byte) string {
	sum := sha256.Sum256(data)
	return fmt.Sprintf("sha256:%x", sum)
}

func main() {
	if len(os.Args) != 2 {
		fmt.Fprintln(os.Stderr, "usage: jcs_probe <fixture.json>")
		os.Exit(2)
	}

	raw, err := os.ReadFile(os.Args[1])
	if err != nil {
		panic(err)
	}
	var f fixture
	if err := json.Unmarshal(raw, &f); err != nil {
		panic(err)
	}
	if f.ProfileID != "soza.jcs+sha256/v1alpha1" {
		panic("unexpected profile_id: " + f.ProfileID)
	}

	verified := 0
	negative := 0
	results := map[string]string{}
	for _, tc := range f.Cases {
		input := []byte(tc.Input)
		preflightErr := validateSafeIntegers(input)

		switch tc.Expect {
		case "invalid_semantic_number":
			if preflightErr == nil {
				panic(tc.ID + ": unsafe semantic number was not rejected")
			}
			if !strings.Contains(preflightErr.Error(), "unsafe integer") {
				panic(tc.ID + ": unexpected preflight error: " + preflightErr.Error())
			}
			negative++
			fmt.Printf("PASS %s: rejected before JCS (%v)\n", tc.ID, preflightErr)
			continue
		case "invalid_representation":
			canonical, transformErr := jcs.Transform(input)
			if transformErr == nil {
				panic(fmt.Sprintf("%s: invalid representation was accepted: %s", tc.ID, canonical))
			}
			negative++
			fmt.Printf("PASS %s: JCS rejected representation (%v)\n", tc.ID, transformErr)
			continue
		case "verified":
			if preflightErr != nil {
				panic(tc.ID + ": preflight rejected verified case: " + preflightErr.Error())
			}
		default:
			panic(tc.ID + ": unknown expectation: " + tc.Expect)
		}

		canonical, err := jcs.Transform(input)
		if err != nil {
			panic(tc.ID + ": JCS transform failed: " + err.Error())
		}
		if string(canonical) != tc.ExpectedCanonical {
			panic(fmt.Sprintf("%s: canonical mismatch\nwant: %s\n got: %s", tc.ID, tc.ExpectedCanonical, string(canonical)))
		}
		actualDigest := digest(canonical)
		if actualDigest != tc.ExpectedDigest {
			panic(fmt.Sprintf("%s: digest mismatch: want %s got %s", tc.ID, tc.ExpectedDigest, actualDigest))
		}
		results[tc.ID] = actualDigest
		verified++
		fmt.Printf("PASS %s: %s\n", tc.ID, actualDigest)
	}

	if results["JCS-005-unicode-nfc"] == results["JCS-006-unicode-nfd"] {
		panic("Unicode normalization boundary lost: NFC and NFD digests are identical")
	}

	fmt.Printf("JCS probe PASS: verified=%d negative=%d\n", verified, negative)
}
