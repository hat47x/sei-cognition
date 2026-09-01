package realizationprobe

import (
	"bytes"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"os/exec"
)

// RunJSON はreference probeで外部Realizationを別OS processとして起動し、
// JSON入出力を受け渡します。このJSON形式はprobe-localであり、SOZAの
// Universal Semantic Contractや正式なProvider protocolではありません。
func RunJSON(binary string, args []string, input any, output any) error {
	payload, err := json.Marshal(input)
	if err != nil {
		return fmt.Errorf("reference process inputをJSON化できません: %w", err)
	}

	cmd := exec.Command(binary, args...)
	cmd.Stdin = bytes.NewReader(payload)
	var stdout bytes.Buffer
	var stderr bytes.Buffer
	cmd.Stdout = &stdout
	cmd.Stderr = &stderr
	if err := cmd.Run(); err != nil {
		if stderr.Len() > 0 {
			return fmt.Errorf("reference processが失敗しました: %w: %s", err, stderr.String())
		}
		return fmt.Errorf("reference processが失敗しました: %w", err)
	}

	decoder := json.NewDecoder(bytes.NewReader(stdout.Bytes()))
	decoder.DisallowUnknownFields()
	if err := decoder.Decode(output); err != nil {
		return fmt.Errorf("reference process outputを読めません: %w", err)
	}
	var extra any
	if err := decoder.Decode(&extra); !errors.Is(err, io.EOF) {
		if err == nil {
			return errors.New("reference process outputに複数のJSON値があります")
		}
		return fmt.Errorf("reference process outputの末尾を検査できません: %w", err)
	}
	return nil
}

// RunRawJSON はProvider固有stateのように、Adapterへそのまま渡すJSON bytesを返します。
func RunRawJSON(binary string, args []string, input any) ([]byte, error) {
	payload, err := json.Marshal(input)
	if err != nil {
		return nil, fmt.Errorf("reference process inputをJSON化できません: %w", err)
	}
	cmd := exec.Command(binary, args...)
	cmd.Stdin = bytes.NewReader(payload)
	var stdout bytes.Buffer
	var stderr bytes.Buffer
	cmd.Stdout = &stdout
	cmd.Stderr = &stderr
	if err := cmd.Run(); err != nil {
		if stderr.Len() > 0 {
			return nil, fmt.Errorf("reference processが失敗しました: %w: %s", err, stderr.String())
		}
		return nil, fmt.Errorf("reference processが失敗しました: %w", err)
	}
	if !json.Valid(stdout.Bytes()) {
		return nil, errors.New("reference process outputが有効なJSONではありません")
	}
	return append([]byte(nil), stdout.Bytes()...), nil
}
