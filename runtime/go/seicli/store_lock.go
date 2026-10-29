package seicli

import (
	"errors"
	"fmt"
	"io/fs"
	"os"
	"path/filepath"
	"runtime"
	"strconv"
	"time"
)

// storeLockFile is held while a command reads and then rewrites the bundle.
// The bundle is rewritten whole, so two commands that interleave their read and
// their write would silently drop one record. The lock serializes them.
const storeLockFile = "store.lock"

// storeLockTimeout bounds how long a command waits for another sei process.
// A lock that is still held after this is reported, not broken: removing it
// while a live process holds it would reintroduce the lost-write race.
var storeLockTimeout = 10 * time.Second

const storeLockPoll = 20 * time.Millisecond

// withStoreLock runs fn while holding the store lock for dataRoot.
func withStoreLock(dataRoot string, fn func() error) error {
	if err := os.MkdirAll(dataRoot, 0o755); err != nil {
		return err
	}
	path := filepath.Join(dataRoot, storeLockFile)
	deadline := time.Now().Add(storeLockTimeout)
	for {
		f, err := os.OpenFile(path, os.O_CREATE|os.O_EXCL|os.O_WRONLY, 0o644)
		if err == nil {
			_, _ = f.WriteString(strconv.Itoa(os.Getpid()) + "\n")
			_ = f.Close()
			defer func() { _ = os.Remove(path) }()
			return fn()
		}
		if !errors.Is(err, fs.ErrExist) && !lockMayBeBeingReleased(err) {
			return err
		}
		if time.Now().After(deadline) {
			if !errors.Is(err, fs.ErrExist) {
				return err
			}
			return fmt.Errorf("the store is locked by another sei process (%s); if no sei process is running, remove that file and retry", path)
		}
		time.Sleep(storeLockPoll)
	}
}

// lockMayBeBeingReleased reports whether err can be a lock that another
// process is deleting right now. On Windows, creating a file that is
// pending deletion fails with "Access is denied" (a permission error) instead
// of "file exists". That is contention to wait out, not a failure. A real
// permission problem keeps failing until the timeout and is then returned
// unchanged.
func lockMayBeBeingReleased(err error) bool {
	return runtime.GOOS == "windows" && errors.Is(err, fs.ErrPermission)
}
