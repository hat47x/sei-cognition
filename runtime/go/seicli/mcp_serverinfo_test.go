package seicli

import (
	"reflect"
	"testing"

	"github.com/hat47x/sei-cognition/runtime/go/semanticruntime"
)

// serverInfo carries the same build identity and Contract list as `sei version`
// and `sei doctor`, so a client can tell which Contract versions the server
// reads without a second call.
func TestMCPServerInfoCarriesCommitAndContracts(t *testing.T) {
	fixClock(t)
	responses := session(t, []string{"--data-root", t.TempDir()}, initialize)
	result, _ := responses[0]["result"].(map[string]any)
	info, _ := result["serverInfo"].(map[string]any)
	if info == nil {
		t.Fatalf("no serverInfo in %v", responses[0])
	}
	if info["name"] != "sei" || info["version"] != currentCLI().Version || info["commit"] != currentCLI().Commit {
		t.Errorf("serverInfo name/version/commit = %v/%v/%v", info["name"], info["version"], info["commit"])
	}
	var got []string
	list, _ := info["contracts"].([]any)
	for _, c := range list {
		got = append(got, c.(string))
	}
	if want := semanticruntime.KnownContracts(); len(want) == 0 || !reflect.DeepEqual(got, want) {
		t.Errorf("serverInfo contracts = %v, want %v", got, want)
	}
}
