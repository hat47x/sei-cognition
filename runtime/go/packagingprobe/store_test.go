package packagingprobe

import (
	"bytes"
	"context"
	"errors"
	"os"
	"path/filepath"
	"testing"

	"github.com/hat47x/soza/runtime/go/semanticruntime"
)

func fixture(t *testing.T, name string) []byte {
	t.Helper()
	path := filepath.Join("..", "..", "..", "fixtures", "contracts", "v1alpha1", "boundary", name)
	data, err := os.ReadFile(path)
	if err != nil {
		t.Fatalf("read fixture %s: %v", name, err)
	}
	return data
}

func TestFilesystemSaveDiscardAndReloadPreservesPortableBytes(t *testing.T) {
	ctx := context.Background()
	original := fixture(t, "partial-knowledge-interchange.json")
	bundle, err := semanticruntime.LoadInterchange(original)
	if err != nil {
		t.Fatalf("LoadInterchange() error = %v", err)
	}

	root := t.TempDir()
	storeA := FilePersistence{DataRoot: root}
	if err := SaveBundle(ctx, storeA, bundle); err != nil {
		t.Fatalf("SaveBundle() error = %v", err)
	}

	// The original runtime object is intentionally discarded. A new store and
	// a new Bundle must reconstruct the package only from durable bytes.
	bundle = nil
	storeB := FilePersistence{DataRoot: root}
	reloaded, err := LoadBundle(ctx, storeB)
	if err != nil {
		t.Fatalf("LoadBundle() error = %v", err)
	}
	if reloaded.Envelope.BundleID != "partial-knowledge-interchange" {
		t.Fatalf("bundle_id = %q", reloaded.Envelope.BundleID)
	}
	if !bytes.Equal(reloaded.ExportOriginal(), original) {
		t.Fatal("reload changed portable Semantic Interchange bytes")
	}
	if len(reloaded.Records) != 2 {
		t.Fatalf("records = %d, want 2", len(reloaded.Records))
	}
	if reloaded.Records[0].Capability == nil || reloaded.Records[1].Decision == nil {
		t.Fatal("typed semantic records were not reconstructed after restart")
	}
}

func TestUnknownContractRemainsOpaqueAcrossFilesystemRestart(t *testing.T) {
	ctx := context.Background()
	original := fixture(t, "unknown-contract-version.json")
	bundle, err := semanticruntime.LoadInterchange(original)
	if err != nil {
		t.Fatalf("LoadInterchange() error = %v", err)
	}
	store := FilePersistence{DataRoot: t.TempDir()}
	if err := SaveBundle(ctx, store, bundle); err != nil {
		t.Fatalf("SaveBundle() error = %v", err)
	}

	reloaded, err := LoadBundle(ctx, FilePersistence{DataRoot: store.DataRoot})
	if err != nil {
		t.Fatalf("LoadBundle() error = %v", err)
	}
	if len(reloaded.Records) != 1 || reloaded.Records[0].Status != semanticruntime.RecordNotVerified {
		t.Fatalf("unknown record status = %#v, want not_verified", reloaded.Records)
	}
	if !bytes.Equal(reloaded.ExportOriginal(), original) {
		t.Fatal("opaque record bytes changed during save/reload")
	}
}

func TestFilesystemExportImportsIntoMemoryPersistenceWithoutSemanticRewrite(t *testing.T) {
	ctx := context.Background()
	original := fixture(t, "partial-knowledge-interchange.json")
	bundle, err := semanticruntime.LoadInterchange(original)
	if err != nil {
		t.Fatalf("LoadInterchange() error = %v", err)
	}
	fileStore := FilePersistence{DataRoot: t.TempDir()}
	if err := SaveBundle(ctx, fileStore, bundle); err != nil {
		t.Fatalf("SaveBundle() error = %v", err)
	}

	exported, err := Export(ctx, fileStore)
	if err != nil {
		t.Fatalf("Export() error = %v", err)
	}
	memoryStore := &MemoryPersistence{}
	if err := Import(ctx, memoryStore, exported); err != nil {
		t.Fatalf("Import() error = %v", err)
	}
	reloaded, err := LoadBundle(ctx, memoryStore)
	if err != nil {
		t.Fatalf("LoadBundle(memory) error = %v", err)
	}
	if !bytes.Equal(reloaded.ExportOriginal(), original) {
		t.Fatal("storage migration rewrote portable semantic bytes")
	}
	if reloaded.Envelope.BundleID != bundle.Envelope.BundleID {
		t.Fatalf("bundle identity changed: %q -> %q", bundle.Envelope.BundleID, reloaded.Envelope.BundleID)
	}
}

func TestFilesystemDataRootCopyRestoresSamePackage(t *testing.T) {
	ctx := context.Background()
	original := fixture(t, "partial-knowledge-interchange.json")
	bundle, err := semanticruntime.LoadInterchange(original)
	if err != nil {
		t.Fatalf("LoadInterchange() error = %v", err)
	}
	sourceRoot := t.TempDir()
	source := FilePersistence{DataRoot: sourceRoot}
	if err := SaveBundle(ctx, source, bundle); err != nil {
		t.Fatalf("SaveBundle() error = %v", err)
	}

	backup, err := os.ReadFile(filepath.Join(sourceRoot, DefaultBundleFile))
	if err != nil {
		t.Fatalf("read backup source: %v", err)
	}
	restoreRoot := t.TempDir()
	if err := os.WriteFile(filepath.Join(restoreRoot, DefaultBundleFile), backup, 0o600); err != nil {
		t.Fatalf("write restored package: %v", err)
	}

	restored, err := LoadBundle(ctx, FilePersistence{DataRoot: restoreRoot})
	if err != nil {
		t.Fatalf("LoadBundle(restored) error = %v", err)
	}
	if !bytes.Equal(restored.ExportOriginal(), original) {
		t.Fatal("restored data root changed canonical bundle bytes")
	}
}

func TestInvalidCanonicalFileIsRejected(t *testing.T) {
	root := t.TempDir()
	if err := os.WriteFile(filepath.Join(root, DefaultBundleFile), []byte(`{"not":"semantic-interchange"}`), 0o600); err != nil {
		t.Fatalf("write invalid package: %v", err)
	}
	if _, err := LoadBundle(context.Background(), FilePersistence{DataRoot: root}); err == nil {
		t.Fatal("LoadBundle() accepted invalid canonical file")
	}
}

func TestTemporaryFileAloneIsNotACompletedPackage(t *testing.T) {
	root := t.TempDir()
	if err := os.WriteFile(filepath.Join(root, ".sei-package-interrupted.tmp"), []byte(`partial`), 0o600); err != nil {
		t.Fatalf("write temporary file: %v", err)
	}
	_, err := LoadBundle(context.Background(), FilePersistence{DataRoot: root})
	if !errors.Is(err, ErrPackageNotFound) {
		t.Fatalf("LoadBundle() error = %v, want ErrPackageNotFound", err)
	}
}

func TestImportRejectsInvalidBytesWithoutReplacingExistingPackage(t *testing.T) {
	ctx := context.Background()
	valid := fixture(t, "partial-knowledge-interchange.json")
	store := &MemoryPersistence{}
	if err := Import(ctx, store, valid); err != nil {
		t.Fatalf("Import(valid) error = %v", err)
	}
	if err := Import(ctx, store, []byte(`{"invalid":true}`)); err == nil {
		t.Fatal("Import(invalid) succeeded")
	}
	after, err := Export(ctx, store)
	if err != nil {
		t.Fatalf("Export() error = %v", err)
	}
	if !bytes.Equal(after, valid) {
		t.Fatal("failed import replaced the last valid package")
	}
}

func TestFilesystemLocatorNeverBecomesSemanticIdentity(t *testing.T) {
	ctx := context.Background()
	original := fixture(t, "partial-knowledge-interchange.json")
	bundle, err := semanticruntime.LoadInterchange(original)
	if err != nil {
		t.Fatalf("LoadInterchange() error = %v", err)
	}
	rootA := filepath.Join(t.TempDir(), "physical-a")
	rootB := filepath.Join(t.TempDir(), "physical-b")
	storeA := FilePersistence{DataRoot: rootA}
	storeB := FilePersistence{DataRoot: rootB}
	if err := SaveBundle(ctx, storeA, bundle); err != nil {
		t.Fatalf("SaveBundle(A) error = %v", err)
	}
	exported, err := Export(ctx, storeA)
	if err != nil {
		t.Fatalf("Export(A) error = %v", err)
	}
	if err := Import(ctx, storeB, exported); err != nil {
		t.Fatalf("Import(B) error = %v", err)
	}
	reloaded, err := LoadBundle(ctx, storeB)
	if err != nil {
		t.Fatalf("LoadBundle(B) error = %v", err)
	}
	if !bytes.Equal(reloaded.ExportOriginal(), original) {
		t.Fatal("physical locator change affected semantic package")
	}
}
