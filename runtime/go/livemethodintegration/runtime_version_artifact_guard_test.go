package livemethodintegration

import (
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"io"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"strings"
	"testing"
)

// TestMainは、runtime version交換のlive testを実行するときだけ、実際に使った
// KJ Atlas source、runtime version、runtime archiveをGo側でも再検証します。
// Exact Bindingへ固定するidentityと実行事実が一致しない状態では、historical
// revisionの検査を開始しません。
func TestMain(m *testing.M) {
	if os.Getenv("SOZA_E3B_RUNTIME_EXCHANGE_LIVE") == "1" {
		if err := verifyRuntimeExchangeKJAtlasSource(); err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(1)
		}
		for _, runtime := range []struct {
			label        string
			version      string
			versionLog   string
			archive      string
			artifactSHA  string
		}{
			{label: "A", version: runtimeExchangeVersionA, versionLog: "/tmp/runtime-exchange-a-version.txt", archive: "/tmp/ollama-a.tar.zst", artifactSHA: runtimeExchangeArtifactA},
			{label: "B", version: runtimeExchangeVersionB, versionLog: "/tmp/runtime-exchange-b-version.txt", archive: "/tmp/ollama-b.tar.zst", artifactSHA: runtimeExchangeArtifactB},
		} {
			if err := verifyRuntimeExchangeVersion(runtime.label, runtime.versionLog, runtime.version); err != nil {
				fmt.Fprintln(os.Stderr, err)
				os.Exit(1)
			}
			if err := verifyRuntimeExchangeArtifact(runtime.label, runtime.archive, runtime.artifactSHA); err != nil {
				fmt.Fprintln(os.Stderr, err)
				os.Exit(1)
			}
		}
	}
	os.Exit(m.Run())
}

func verifyRuntimeExchangeKJAtlasSource() error {
	workspace := strings.TrimSpace(os.Getenv("GITHUB_WORKSPACE"))
	if workspace == "" {
		return fmt.Errorf("runtime exchange live testではGITHUB_WORKSPACEが必要です")
	}
	command := exec.Command("git", "-C", filepath.Join(workspace, "_external", "kj-atlas"), "rev-parse", "HEAD")
	output, err := command.Output()
	if err != nil {
		return fmt.Errorf("KJ Atlas checkoutのcommitを確認できません: %w", err)
	}
	actual := strings.TrimSpace(string(output))
	if actual != pinnedKJAtlasCommit {
		return fmt.Errorf("KJ Atlas checkoutがExact Binding用の固定commitと一致しません: actual=%s expected=%s", actual, pinnedKJAtlasCommit)
	}
	return nil
}

func verifyRuntimeExchangeVersion(label, path, expected string) error {
	data, err := os.ReadFile(path)
	if err != nil {
		return fmt.Errorf("runtime %s version logを読めません: %w", label, err)
	}
	pattern := regexp.MustCompile(`(^|[^0-9])` + regexp.QuoteMeta(expected) + `([^0-9]|$)`)
	if !pattern.Match(data) {
		return fmt.Errorf("runtime %s versionがExact Binding用の固定値と一致しません: expected=%s log=%q", label, expected, strings.TrimSpace(string(data)))
	}
	return nil
}

func verifyRuntimeExchangeArtifact(label, path, expected string) error {
	file, err := os.Open(path)
	if err != nil {
		return fmt.Errorf("runtime %s artifactを開けません: %w", label, err)
	}
	defer file.Close()

	hash := sha256.New()
	if _, err := io.Copy(hash, file); err != nil {
		return fmt.Errorf("runtime %s artifactのSHA-256を計算できません: %w", label, err)
	}
	actual := hex.EncodeToString(hash.Sum(nil))
	if actual != expected {
		return fmt.Errorf("runtime %s artifact digestがExact Binding用の固定値と一致しません: actual=%s expected=%s", label, actual, expected)
	}
	return nil
}
