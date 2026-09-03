package livemethodintegration

import (
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"io"
	"os"
	"os/exec"
	"regexp"
	"strings"
	"testing"
)

const (
	runtimeExchangeKJAtlasDirEnv  = "SOZA_E3B_RUNTIME_EXCHANGE_KJ_ATLAS_DIR"
	runtimeExchangeAVersionLogEnv = "SOZA_E3B_RUNTIME_EXCHANGE_VERSION_LOG_A"
	runtimeExchangeBVersionLogEnv = "SOZA_E3B_RUNTIME_EXCHANGE_VERSION_LOG_B"
	runtimeExchangeAArchiveEnv    = "SOZA_E3B_RUNTIME_EXCHANGE_ARCHIVE_A"
	runtimeExchangeBArchiveEnv    = "SOZA_E3B_RUNTIME_EXCHANGE_ARCHIVE_B"
)

// TestMainは、runtime version交換のlive testを実行するときだけ、実際に使った
// KJ Atlas source、runtime version、runtime archiveをGo側でも再検証します。
// Exact Bindingへ固定するidentityと実行事実が一致しない状態では、historical
// revisionの検査を開始しません。
//
// current baselineでは実行場所を意味境界から分離するため、GitHub Actions固有の
// workspaceや固定/tmp配置へ暗黙に戻りません。repository-local harnessなどの
// 実行器が、検証対象のpathを明示的な環境変数として渡します。
func TestMain(m *testing.M) {
	if os.Getenv("SOZA_E3B_RUNTIME_EXCHANGE_LIVE") == "1" {
		if err := verifyRuntimeExchangeKJAtlasSource(); err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(1)
		}

		runtimes := []struct {
			label         string
			version       string
			versionLogEnv string
			archiveEnv    string
			artifactSHA   string
		}{
			{
				label:         "A",
				version:       runtimeExchangeVersionA,
				versionLogEnv: runtimeExchangeAVersionLogEnv,
				archiveEnv:    runtimeExchangeAArchiveEnv,
				artifactSHA:   runtimeExchangeArtifactA,
			},
			{
				label:         "B",
				version:       runtimeExchangeVersionB,
				versionLogEnv: runtimeExchangeBVersionLogEnv,
				archiveEnv:    runtimeExchangeBArchiveEnv,
				artifactSHA:   runtimeExchangeArtifactB,
			},
		}

		for _, runtime := range runtimes {
			versionLog, err := runtimeExchangeRequiredPath(runtime.versionLogEnv)
			if err != nil {
				fmt.Fprintln(os.Stderr, err)
				os.Exit(1)
			}
			archive, err := runtimeExchangeRequiredPath(runtime.archiveEnv)
			if err != nil {
				fmt.Fprintln(os.Stderr, err)
				os.Exit(1)
			}
			if err := verifyRuntimeExchangeVersion(runtime.label, versionLog, runtime.version); err != nil {
				fmt.Fprintln(os.Stderr, err)
				os.Exit(1)
			}
			if err := verifyRuntimeExchangeArtifact(runtime.label, archive, runtime.artifactSHA); err != nil {
				fmt.Fprintln(os.Stderr, err)
				os.Exit(1)
			}
		}
	}
	os.Exit(m.Run())
}

func runtimeExchangeRequiredPath(envName string) (string, error) {
	value := strings.TrimSpace(os.Getenv(envName))
	if value == "" {
		return "", fmt.Errorf("runtime exchange live testでは%sを明示してください", envName)
	}
	return value, nil
}

func verifyRuntimeExchangeKJAtlasSource() error {
	kjAtlasDir, err := runtimeExchangeRequiredPath(runtimeExchangeKJAtlasDirEnv)
	if err != nil {
		return err
	}
	command := exec.Command("git", "-C", kjAtlasDir, "rev-parse", "HEAD")
	output, err := command.Output()
	if err != nil {
		return fmt.Errorf("KJ Atlas checkoutのcommitを確認できません: dir=%s: %w", kjAtlasDir, err)
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
