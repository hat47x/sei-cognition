package modelprobe

import (
	"bufio"
	"fmt"
	"os"
	"path/filepath"
	"runtime"
	"strconv"
	"strings"
	"time"
)

type RuntimeModelMappingEvidence struct {
	Status        string `json:"status"`
	ObservedAt    string `json:"observed_at,omitempty"`
	PID           int    `json:"pid,omitempty"`
	ModelFileName string `json:"model_file_name,omitempty"`
	Source        string `json:"source,omitempty"`
	MappingCount  int    `json:"mapping_count,omitempty"`
	Error         string `json:"error,omitempty"`
}

func ObserveRuntimeModelMapping(pid int, modelFilePath string) RuntimeModelMappingEvidence {
	modelFilePath = strings.TrimSpace(modelFilePath)
	if pid <= 0 || modelFilePath == "" {
		return RuntimeModelMappingEvidence{Status: "not-requested"}
	}

	evidence := RuntimeModelMappingEvidence{
		Status:        "unavailable",
		ObservedAt:    time.Now().UTC().Format(time.RFC3339),
		PID:           pid,
		ModelFileName: filepath.Base(filepath.Clean(modelFilePath)),
	}

	if runtime.GOOS != "linux" {
		evidence.Status = "unsupported"
		evidence.Error = "runtime model mapping observation currently requires Linux /proc"
		return evidence
	}

	targetInfo, err := os.Stat(modelFilePath)
	if err != nil {
		evidence.Error = fmt.Sprintf("stat model file: %v", err)
		return evidence
	}
	if !targetInfo.Mode().IsRegular() {
		evidence.Error = "model file must be a regular file"
		return evidence
	}

	source := filepath.Join("/proc", strconv.Itoa(pid), "maps")
	evidence.Source = source
	file, err := os.Open(source)
	if err != nil {
		evidence.Error = err.Error()
		return evidence
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		mappedPath := procMapsPath(scanner.Text())
		if mappedPath == "" {
			continue
		}
		mappedPath = strings.TrimSuffix(mappedPath, " (deleted)")
		mappedInfo, err := os.Stat(mappedPath)
		if err != nil {
			continue
		}
		if os.SameFile(targetInfo, mappedInfo) {
			evidence.MappingCount++
		}
	}
	if err := scanner.Err(); err != nil {
		evidence.Error = err.Error()
		return evidence
	}

	if evidence.MappingCount == 0 {
		evidence.Status = "not-observed"
		return evidence
	}
	evidence.Status = "observed"
	evidence.Error = ""
	return evidence
}

func procMapsPath(line string) string {
	fields := strings.Fields(line)
	if len(fields) < 6 {
		return ""
	}
	path := strings.Join(fields[5:], " ")
	if path == "" || strings.HasPrefix(path, "[") {
		return ""
	}
	return path
}
