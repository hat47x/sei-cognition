package livemethodintegration

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io"
	"os"
	"os/exec"
	"regexp"
	"strings"
	"testing"
)

const (
	runtimeExchangeKJAtlasSourceModeEnv     = "SOZA_E3B_RUNTIME_EXCHANGE_KJ_ATLAS_SOURCE_MODE"
	runtimeExchangeKJAtlasBackendDirEnv     = "SOZA_E3B_RUNTIME_EXCHANGE_KJ_ATLAS_BACKEND_DIR"
	runtimeExchangeKJAtlasSourceVerifierEnv = "SOZA_E3B_RUNTIME_EXCHANGE_KJ_ATLAS_SOURCE_VERIFIER"
	runtimeExchangeAVersionLogEnv           = "SOZA_E3B_RUNTIME_EXCHANGE_VERSION_LOG_A"
	runtimeExchangeBVersionLogEnv           = "SOZA_E3B_RUNTIME_EXCHANGE_VERSION_LOG_B"
	runtimeExchangeAArchiveEnv              = "SOZA_E3B_RUNTIME_EXCHANGE_ARCHIVE_A"
	runtimeExchangeBArchiveEnv              = "SOZA_E3B_RUNTIME_EXCHANGE_ARCHIVE_B"

	runtimeExchangeKJAtlasSourceModeGitCheckout = "git-checkout"
	runtimeExchangeKJAtlasSourceModeBundle      = "verified-runtime-bundle"
	pinnedKJAtlasBackendTree                    = "7d71ac2b4d32bef90f3a481ade1b4c92ddddd084"
	pinnedKJAtlasRuntimeSurfaceTree             = "208bea71eef4afed3ddfd3fabb36b0969d167a90"
)

// TestMainは、runtime version交換のlive testを実行するときだけ、実際に使った
// KJ Atlas source、runtime version、runtime archiveをGo側でも再検証します。
// Exact Bindingへ固定するidentityと実行事実が一致しない状態では、historical
// revisionの検査を開始しません。
//
// KJ AtlasのGit checkoutはsource取得元として利用できますが、working treeを
// actual実行sourceにはしません。.env、__pycache__、*.soなどGitのignored fileが
// 実行条件へ混入し得るためです。live Evidenceでは、固定commit objectからexportした
// runtime surfaceか、同じGit object identityを持つ外部bundleを必ずverifierへ通します。
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
	sourceMode := strings.TrimSpace(os.Getenv(runtimeExchangeKJAtlasSourceModeEnv))
	if sourceMode == "" {
		return fmt.Errorf("runtime exchange live testでは%sを明示してください", runtimeExchangeKJAtlasSourceModeEnv)
	}

	switch sourceMode {
	case runtimeExchangeKJAtlasSourceModeGitCheckout:
		return fmt.Errorf(
			"runtime exchange live testではGit working treeを実行sourceにできません。" +
				"固定commit objectからverified runtime bundleをexportしてください",
		)
	case runtimeExchangeKJAtlasSourceModeBundle:
		return verifyRuntimeExchangeKJAtlasBundle()
	default:
		return fmt.Errorf("runtime exchange KJ Atlas source modeを認識できません: %s", sourceMode)
	}
}

func verifyRuntimeExchangeKJAtlasBundle() error {
	backendDir, err := runtimeExchangeRequiredPath(runtimeExchangeKJAtlasBackendDirEnv)
	if err != nil {
		return err
	}
	verifier, err := runtimeExchangeRequiredPath(runtimeExchangeKJAtlasSourceVerifierEnv)
	if err != nil {
		return err
	}

	command := exec.Command("python3", verifier, "--backend-dir", backendDir)
	output, err := command.CombinedOutput()
	if err != nil {
		return fmt.Errorf("KJ Atlas runtime source bundleを再検証できません: %s: %w", strings.TrimSpace(string(output)), err)
	}

	var payload struct {
		Verified           bool   `json:"verified"`
		SourceMode         string `json:"sourceMode"`
		SourceCommit       string `json:"sourceCommit"`
		PinnedBackendTree  string `json:"pinnedBackendTree"`
		RuntimeSurfaceTree string `json:"runtimeSurfaceTree"`
		VerificationBasis  string `json:"verificationBasis"`
	}
	if err := json.Unmarshal(output, &payload); err != nil {
		return fmt.Errorf("KJ Atlas runtime source verifierの出力を解釈できません: %w", err)
	}
	if !payload.Verified || payload.SourceMode != runtimeExchangeKJAtlasSourceModeBundle {
		return fmt.Errorf("KJ Atlas runtime source verifierがverified bundleを返しませんでした: %#v", payload)
	}
	if payload.SourceCommit != pinnedKJAtlasCommit {
		return fmt.Errorf(
			"KJ Atlas runtime source bundleのsource commitが固定値と一致しません: actual=%s expected=%s",
			payload.SourceCommit,
			pinnedKJAtlasCommit,
		)
	}
	if payload.PinnedBackendTree != pinnedKJAtlasBackendTree {
		return fmt.Errorf(
			"KJ Atlas runtime source bundleの親backend treeが固定値と一致しません: actual=%s expected=%s",
			payload.PinnedBackendTree,
			pinnedKJAtlasBackendTree,
		)
	}
	if payload.RuntimeSurfaceTree != pinnedKJAtlasRuntimeSurfaceTree {
		return fmt.Errorf(
			"KJ Atlas runtime source bundleの実行surface treeが固定値と一致しません: actual=%s expected=%s",
			payload.RuntimeSurfaceTree,
			pinnedKJAtlasRuntimeSurfaceTree,
		)
	}
	if payload.VerificationBasis != "pinned-git-object-identities" {
		return fmt.Errorf("KJ Atlas runtime source bundleの検証根拠を認識できません: %s", payload.VerificationBasis)
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
