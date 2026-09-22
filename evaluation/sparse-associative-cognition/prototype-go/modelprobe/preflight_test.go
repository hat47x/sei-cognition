package modelprobe

import (
	"context"
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestPreflightRecordsReachableEndpoint(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
	}))
	defer server.Close()

	m := Preflight(context.Background(), server.URL, server.Client())
	if !m.Endpoint.Reachable || m.Endpoint.HTTPStatus != http.StatusOK {
		t.Fatalf("endpoint=%+v", m.Endpoint)
	}
	if m.Schema != runManifestSchema || m.ExecutionKind != "preflight" {
		t.Fatalf("manifest=%+v", m)
	}
	if m.Host.OS == "" || m.Host.Arch == "" || m.Host.LogicalCPU < 1 {
		t.Fatalf("host=%+v", m.Host)
	}
	if m.RuntimeProcess.Status != "not-requested" {
		t.Fatalf("runtime process status=%q want=not-requested", m.RuntimeProcess.Status)
	}
}

func TestPreflightWithoutEndpointIsExplicit(t *testing.T) {
	m := Preflight(context.Background(), "", nil)
	if m.Endpoint.Reachable {
		t.Fatal("empty endpoint must not be reachable")
	}
	if m.Endpoint.Error == "" {
		t.Fatal("missing endpoint should be explicit")
	}
}
