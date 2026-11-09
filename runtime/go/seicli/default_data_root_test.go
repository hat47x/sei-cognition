package seicli

import (
	"regexp"
	"testing"
)

// Without --data-root and SEI_DATA_ROOT the data root is ".sei" relative to the
// current directory, so the same command run from two directories reads two
// different stores. The output names no store location, only bundle_id.
func TestDefaultDataRootFollowsTheCurrentDirectory(t *testing.T) {
	fixClock(t)
	t.Setenv("SEI_DATA_ROOT", "")
	idOf := func(dir string) string {
		t.Chdir(dir)
		mustRun(t, "init")
		out := mustRun(t, "resume", "--json")
		m := regexp.MustCompile(`"bundle_id":\s*"([^"]+)"`).FindStringSubmatch(out)
		if m == nil {
			t.Fatalf("no bundle_id in resume output: %s", out)
		}
		return m[1]
	}
	a, b := idOf(t.TempDir()), idOf(t.TempDir())
	if a == b {
		t.Errorf("two directories read the same store: %s", a)
	}
}
