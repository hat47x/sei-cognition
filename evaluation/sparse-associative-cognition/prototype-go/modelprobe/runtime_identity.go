package modelprobe

import (
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"runtime"
	"strconv"
	"strings"
)

type RuntimeProcessIdentity struct {
	Status         string `json:"status"`
	PID            int    `json:"pid,omitempty"`
	ExecutableName string `json:"executable_name,omitempty"`
	Source         string `json:"source,omitempty"`
	SizeBytes      int64  `json:"size_bytes,omitempty"`
	SHA256         string `json:"sha256,omitempty"`
	Error          string `json:"error,omitempty"`
}

func ObserveRuntimeProcessIdentity(pid int) RuntimeProcessIdentity {
	if pid <= 0 {
		return RuntimeProcessIdentity{Status: "not-requested"}
	}
	if runtime.GOOS != "linux" {
		return RuntimeProcessIdentity{
			Status: "unsupported",
			PID:    pid,
			Error:  "runtime executable identity currently requires Linux /proc",
		}
	}

	source := filepath.Join("/proc", strconv.Itoa(pid), "exe")
	identity := RuntimeProcessIdentity{
		Status: "unavailable",
		PID:    pid,
		Source: source,
	}

	target, err := os.Readlink(source)
	if err != nil {
		identity.Error = err.Error()
		return identity
	}
	target = strings.TrimSuffix(target, " (deleted)")
	identity.ExecutableName = filepath.Base(target)

	file, err := os.Open(source)
	if err != nil {
		identity.Error = err.Error()
		return identity
	}
	defer file.Close()

	info, err := file.Stat()
	if err != nil {
		identity.Error = err.Error()
		return identity
	}
	if !info.Mode().IsRegular() {
		identity.Error = fmt.Sprintf("runtime executable is not a regular file: %s", info.Mode())
		return identity
	}

	hasher := sha256.New()
	if _, err := io.Copy(hasher, file); err != nil {
		identity.Error = err.Error()
		return identity
	}

	identity.Status = "observed"
	identity.SizeBytes = info.Size()
	identity.SHA256 = hex.EncodeToString(hasher.Sum(nil))
	identity.Error = ""
	return identity
}
