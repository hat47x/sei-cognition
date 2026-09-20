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

type ProcessMemorySample struct {
	ObservedAt      string `json:"observed_at"`
	Stage           string `json:"stage"`
	Mode            Mode   `json:"mode,omitempty"`
	CurrentRSSBytes uint64 `json:"current_rss_bytes"`
	PeakRSSBytes    uint64 `json:"peak_rss_bytes"`
}

type RuntimeMemoryEvidence struct {
	Status              string                `json:"status"`
	PID                 int                   `json:"pid,omitempty"`
	ProcessName         string                `json:"process_name,omitempty"`
	Source              string                `json:"source,omitempty"`
	MaxObservedRSSBytes uint64                `json:"max_observed_rss_bytes,omitempty"`
	PeakRSSBytes        uint64                `json:"peak_rss_bytes,omitempty"`
	Samples             []ProcessMemorySample `json:"samples,omitempty"`
	Errors              []string              `json:"errors,omitempty"`
}

func newRuntimeMemoryEvidence(pid int) RuntimeMemoryEvidence {
	if pid <= 0 {
		return RuntimeMemoryEvidence{Status: "not-requested"}
	}
	if runtime.GOOS != "linux" {
		return RuntimeMemoryEvidence{
			Status: "unsupported",
			PID:    pid,
			Errors: []string{"runtime process RSS sampling currently requires Linux /proc"},
		}
	}
	return RuntimeMemoryEvidence{
		Status: "pending",
		PID:    pid,
		Source: fmt.Sprintf("/proc/%d/status", pid),
	}
}

func (e *RuntimeMemoryEvidence) Observe(stage string, mode Mode) {
	if e == nil || e.PID <= 0 || e.Status == "not-requested" || e.Status == "unsupported" {
		return
	}

	current, peak, processName, err := readLinuxProcessMemory(e.PID)
	if err != nil {
		e.Errors = append(e.Errors, fmt.Sprintf("%s: %v", stage, err))
		if len(e.Samples) == 0 {
			e.Status = "unavailable"
		} else {
			e.Status = "partial"
		}
		return
	}

	if e.ProcessName == "" {
		e.ProcessName = processName
	}
	sample := ProcessMemorySample{
		ObservedAt:      time.Now().UTC().Format(time.RFC3339),
		Stage:           stage,
		Mode:            mode,
		CurrentRSSBytes: current,
		PeakRSSBytes:    peak,
	}
	e.Samples = append(e.Samples, sample)
	if current > e.MaxObservedRSSBytes {
		e.MaxObservedRSSBytes = current
	}
	if peak > e.PeakRSSBytes {
		e.PeakRSSBytes = peak
	}
	if len(e.Errors) == 0 {
		e.Status = "observed"
	} else {
		e.Status = "partial"
	}
}

func readLinuxProcessMemory(pid int) (currentRSSBytes uint64, peakRSSBytes uint64, processName string, err error) {
	if runtime.GOOS != "linux" {
		return 0, 0, "", fmt.Errorf("Linux /proc is required")
	}
	if pid <= 0 {
		return 0, 0, "", fmt.Errorf("pid must be positive")
	}

	path := filepath.Join("/proc", strconv.Itoa(pid), "status")
	file, err := os.Open(path)
	if err != nil {
		return 0, 0, "", err
	}
	defer file.Close()

	var currentSeen bool
	var peakSeen bool
	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		line := scanner.Text()
		switch {
		case strings.HasPrefix(line, "Name:"):
			processName = strings.TrimSpace(strings.TrimPrefix(line, "Name:"))
		case strings.HasPrefix(line, "VmRSS:"):
			value, parseErr := parseProcStatusBytes(line, "VmRSS:")
			if parseErr != nil {
				return 0, 0, "", parseErr
			}
			currentRSSBytes = value
			currentSeen = true
		case strings.HasPrefix(line, "VmHWM:"):
			value, parseErr := parseProcStatusBytes(line, "VmHWM:")
			if parseErr != nil {
				return 0, 0, "", parseErr
			}
			peakRSSBytes = value
			peakSeen = true
		}
	}
	if err := scanner.Err(); err != nil {
		return 0, 0, "", err
	}
	if !currentSeen {
		return 0, 0, "", fmt.Errorf("VmRSS is missing from %s", path)
	}
	if !peakSeen {
		return 0, 0, "", fmt.Errorf("VmHWM is missing from %s", path)
	}
	return currentRSSBytes, peakRSSBytes, processName, nil
}

func parseProcStatusBytes(line string, prefix string) (uint64, error) {
	fields := strings.Fields(strings.TrimSpace(strings.TrimPrefix(line, prefix)))
	if len(fields) != 2 || fields[1] != "kB" {
		return 0, fmt.Errorf("unexpected %s format %q", strings.TrimSuffix(prefix, ":"), line)
	}
	kib, err := strconv.ParseUint(fields[0], 10, 64)
	if err != nil {
		return 0, fmt.Errorf("parse %s: %w", strings.TrimSuffix(prefix, ":"), err)
	}
	return kib * 1024, nil
}
