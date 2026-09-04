package packagingprobe

import (
	"context"
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"sync"

	"github.com/hat47x/soza/runtime/go/semanticruntime"
)

const DefaultBundleFile = "semantic.bundle.json"

var ErrPackageNotFound = errors.New("package data not found")

// Persistence is a runtime-level boundary used by the packaging probe.
// It is not a Universal Semantic Contract.
type Persistence interface {
	Save(ctx context.Context, data []byte) error
	Load(ctx context.Context) ([]byte, error)
}

// SaveBundle persists the original Semantic Interchange bytes. The probe does
// not rewrite the bundle merely because the current runtime can parse it.
func SaveBundle(ctx context.Context, persistence Persistence, bundle *semanticruntime.Bundle) error {
	if persistence == nil {
		return errors.New("persistence is required")
	}
	if bundle == nil {
		return errors.New("bundle is required")
	}
	return persistence.Save(ctx, bundle.ExportOriginal())
}

// LoadBundle loads persisted bytes and delegates semantic parsing and
// validation to the existing semantic runtime.
func LoadBundle(ctx context.Context, persistence Persistence) (*semanticruntime.Bundle, error) {
	if persistence == nil {
		return nil, errors.New("persistence is required")
	}
	data, err := persistence.Load(ctx)
	if err != nil {
		return nil, err
	}
	return semanticruntime.LoadInterchange(data)
}

// Export returns a defensive copy of the portable Semantic Interchange bytes.
func Export(ctx context.Context, persistence Persistence) ([]byte, error) {
	if persistence == nil {
		return nil, errors.New("persistence is required")
	}
	data, err := persistence.Load(ctx)
	if err != nil {
		return nil, err
	}
	return append([]byte(nil), data...), nil
}

// Import validates portable Semantic Interchange bytes before persisting them.
// Validation prevents an invalid canonical file from being accepted as a
// normal package state, while unknown nested Contracts remain not_verified in
// accordance with semanticruntime.LoadInterchange.
func Import(ctx context.Context, persistence Persistence, data []byte) error {
	if persistence == nil {
		return errors.New("persistence is required")
	}
	if _, err := semanticruntime.LoadInterchange(data); err != nil {
		return fmt.Errorf("invalid semantic interchange: %w", err)
	}
	return persistence.Save(ctx, append([]byte(nil), data...))
}

// FilePersistence is the first filesystem realization for the packaging probe.
// DataRoot and file paths are physical locators only; they never become
// LogicalReference values.
type FilePersistence struct {
	DataRoot   string
	BundleFile string
}

func (p FilePersistence) bundlePath() (string, error) {
	if p.DataRoot == "" {
		return "", errors.New("data root is required")
	}
	name := p.BundleFile
	if name == "" {
		name = DefaultBundleFile
	}
	if filepath.Base(name) != name || name == "." || name == ".." {
		return "", errors.New("bundle file must be a simple file name")
	}
	return filepath.Join(p.DataRoot, name), nil
}

func (p FilePersistence) Save(ctx context.Context, data []byte) error {
	if err := ctx.Err(); err != nil {
		return err
	}
	path, err := p.bundlePath()
	if err != nil {
		return err
	}
	if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
		return err
	}

	tmp, err := os.CreateTemp(filepath.Dir(path), ".soza-package-*.tmp")
	if err != nil {
		return err
	}
	tmpName := tmp.Name()
	keepTemp := false
	defer func() {
		if !keepTemp {
			_ = os.Remove(tmpName)
		}
	}()

	if _, err := tmp.Write(data); err != nil {
		_ = tmp.Close()
		return err
	}
	if err := tmp.Sync(); err != nil {
		_ = tmp.Close()
		return err
	}
	if err := tmp.Close(); err != nil {
		return err
	}
	if err := ctx.Err(); err != nil {
		return err
	}
	if err := os.Rename(tmpName, path); err != nil {
		return err
	}
	keepTemp = true
	return nil
}

func (p FilePersistence) Load(ctx context.Context) ([]byte, error) {
	if err := ctx.Err(); err != nil {
		return nil, err
	}
	path, err := p.bundlePath()
	if err != nil {
		return nil, err
	}
	data, err := os.ReadFile(path)
	if errors.Is(err, os.ErrNotExist) {
		return nil, ErrPackageNotFound
	}
	if err != nil {
		return nil, err
	}
	return data, nil
}

// MemoryPersistence is a second replaceable realization used only to prove
// that portable semantic bytes are not tied to filesystem mechanics.
type MemoryPersistence struct {
	mu   sync.RWMutex
	data []byte
	set  bool
}

func (p *MemoryPersistence) Save(ctx context.Context, data []byte) error {
	if err := ctx.Err(); err != nil {
		return err
	}
	if p == nil {
		return errors.New("memory persistence is required")
	}
	p.mu.Lock()
	defer p.mu.Unlock()
	p.data = append([]byte(nil), data...)
	p.set = true
	return nil
}

func (p *MemoryPersistence) Load(ctx context.Context) ([]byte, error) {
	if err := ctx.Err(); err != nil {
		return nil, err
	}
	if p == nil {
		return nil, errors.New("memory persistence is required")
	}
	p.mu.RLock()
	defer p.mu.RUnlock()
	if !p.set {
		return nil, ErrPackageNotFound
	}
	return append([]byte(nil), p.data...), nil
}
