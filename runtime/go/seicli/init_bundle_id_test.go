package seicli

import (
	"os"
	"path/filepath"
	"regexp"
	"strings"
	"testing"
)

func TestInitRejectsMalformedBundleIdWithoutCreatingTheStore(t *testing.T) {
	fixClock(t)
	cases := []struct {
		name string
		id   string
		want string
	}{
		{"whitespace only", "  ", "must not be empty or only whitespace"},
		{"newline", "x\ny", "control character"},
		{"tab", "x\ty", "control character"},
		{"leading space", " store", "must not start or end with whitespace"},
		{"trailing space", "store ", "must not start or end with whitespace"},
		{"too long", strings.Repeat("a", maxBundleIDRunes+1), "the limit is"},
	}
	for _, c := range cases {
		t.Run(c.name, func(t *testing.T) {
			root := filepath.Join(t.TempDir(), "store")
			_, err := run(t, "init", "--data-root", root, "--bundle-id", c.id)
			if err == nil || !strings.Contains(err.Error(), c.want) {
				t.Fatalf("want error containing %q, got %v", c.want, err)
			}
			if _, statErr := os.Stat(filepath.Join(root, "semantic.bundle.json")); !os.IsNotExist(statErr) {
				t.Fatalf("a store was created for a rejected bundle id: %v", statErr)
			}
		})
	}
}

func TestInitAcceptsBundleIdAtTheLimit(t *testing.T) {
	fixClock(t)
	root := filepath.Join(t.TempDir(), "store")
	id := strings.Repeat("あ", maxBundleIDRunes)
	if _, err := run(t, "init", "--data-root", root, "--bundle-id", id); err != nil {
		t.Fatalf("a %d-character bundle id should be accepted: %v", maxBundleIDRunes, err)
	}
}

func TestInitDefaultBundleIdDiffersBetweenStoresMadeOnTheSameDay(t *testing.T) {
	fixClock(t)
	pattern := regexp.MustCompile(`^sei-store-\d{4}-\d{2}-\d{2}-[0-9a-f]{8}$`)
	seen := map[string]bool{}
	for i := 0; i < 5; i++ {
		root := filepath.Join(t.TempDir(), "store")
		out := mustRun(t, "init", "--data-root", root)
		m := regexp.MustCompile(`"bundle_id":\s*"([^"]+)"`).FindStringSubmatch(out)
		if m == nil || !pattern.MatchString(m[1]) {
			t.Fatalf("unexpected default bundle id in %q", out)
		}
		if seen[m[1]] {
			t.Fatalf("default bundle id %q repeated", m[1])
		}
		seen[m[1]] = true
	}
}

func TestInitDoesNotReapplyBundleIdRulesToAnExistingStore(t *testing.T) {
	fixClock(t)
	root := filepath.Join(t.TempDir(), "store")
	mustRun(t, "init", "--data-root", root)
	bundle := filepath.Join(root, "semantic.bundle.json")
	data, err := os.ReadFile(bundle)
	if err != nil {
		t.Fatal(err)
	}
	long := strings.Repeat("a", maxBundleIDRunes+50)
	edited := regexp.MustCompile(`"bundle_id": "[^"]*"`).ReplaceAllString(string(data), `"bundle_id": "`+long+`"`)
	if err := os.WriteFile(bundle, []byte(edited), 0o600); err != nil {
		t.Fatal(err)
	}
	if _, err := run(t, "resume", "--data-root", root); err != nil {
		t.Fatalf("an existing store with a long bundle id must still load: %v", err)
	}
}
