// Package capacityprofile provides evaluation-only helpers for scaling sparse
// associative configurations across bounded compute profiles.
//
// Profile labels do not imply device requirements. The helpers preserve and
// expose engineering invariants; they do not import biological ratios.
package capacityprofile

import (
	"errors"
	"fmt"
	"math"
	"strings"

	"github.com/hat47x/sei-cognition/evaluation/sparse-associative-cognition/prototype-go/sparseassoc"
)

type Profile struct {
	ID     string
	Sparse sparseassoc.Config
}

func Validate(profile Profile) error {
	if strings.TrimSpace(profile.ID) == "" {
		return errors.New("profile id must not be empty")
	}
	return sparseassoc.ValidateConfig(profile.Sparse)
}

func ActiveFraction(profile Profile) float64 {
	if profile.Sparse.Dimensions == 0 {
		return 0
	}
	return float64(profile.Sparse.Active) / float64(profile.Sparse.Dimensions)
}

// SignaturePayloadBytes reports only the uint16 active-dimension payload. It
// excludes slice headers and other Go runtime overhead.
func SignaturePayloadBytes(profile Profile) int {
	return int(profile.Sparse.Active) * 2
}

// EncoderScratchLowerBoundBytes reports the scores + marks arrays created by
// sparseassoc.Encoder: one float32 score and one uint32 mark per dimension.
// It excludes touched-slice capacity, headers, allocator overhead, and indexes.
func EncoderScratchLowerBoundBytes(profile Profile) int {
	return int(profile.Sparse.Dimensions) * 8
}

// ScaleDimensions derives a profile with the same fanout and seed while
// rounding Active to preserve the base active fraction as closely as integer
// sparse dimensions permit.
func ScaleDimensions(base Profile, id string, dimensions uint16) (Profile, error) {
	if err := Validate(base); err != nil {
		return Profile{}, fmt.Errorf("invalid base profile: %w", err)
	}
	if strings.TrimSpace(id) == "" {
		return Profile{}, errors.New("scaled profile id must not be empty")
	}
	if dimensions == 0 {
		return Profile{}, errors.New("scaled dimensions must be > 0")
	}

	ratio := float64(base.Sparse.Active) / float64(base.Sparse.Dimensions)
	active := int(math.Round(float64(dimensions) * ratio))
	if active < 1 {
		active = 1
	}
	if active > int(dimensions) {
		active = int(dimensions)
	}

	out := Profile{
		ID: id,
		Sparse: sparseassoc.Config{
			Dimensions: dimensions,
			Fanout:     base.Sparse.Fanout,
			Active:     uint16(active),
			Seed:       base.Sparse.Seed,
		},
	}
	if err := Validate(out); err != nil {
		return Profile{}, err
	}
	return out, nil
}

// EqualLocalHalfResidual divides half of the total winner budget equally across
// familyCount local groups and reserves the other half for global competition.
// It fails rather than silently distorting the requested ratio.
func EqualLocalHalfResidual(active uint16, familyCount uint16) (localEach uint16, globalResidual uint16, err error) {
	if active == 0 {
		return 0, 0, errors.New("active must be > 0")
	}
	if familyCount == 0 {
		return 0, 0, errors.New("family count must be > 0")
	}
	if active%2 != 0 {
		return 0, 0, errors.New("active must be even for half-local/half-global partition")
	}
	localTotal := active / 2
	if localTotal < familyCount {
		return 0, 0, fmt.Errorf("active %d is too small to reserve at least one slot for %d local families and half for global residual", active, familyCount)
	}
	if localTotal%familyCount != 0 {
		return 0, 0, fmt.Errorf("local half %d is not evenly divisible by %d families", localTotal, familyCount)
	}
	localEach = localTotal / familyCount
	globalResidual = active - localTotal
	return localEach, globalResidual, nil
}

// ProjectionUpperBound is a simple pre-collision upper bound on touched
// dimensions for positive keyed features. It is not an observed activation
// count and must not be treated as semantic quality.
func ProjectionUpperBound(positiveFeatureCount int, fanout uint16) int {
	if positiveFeatureCount <= 0 || fanout == 0 {
		return 0
	}
	return positiveFeatureCount * int(fanout)
}

// WinnerShareUpperBound estimates configured winners relative to the maximum
// pre-collision projections available from the caller-provided feature count.
// Values near or above 1 indicate weak or absent selection pressure.
func WinnerShareUpperBound(profile Profile, positiveFeatureCount int) float64 {
	upper := ProjectionUpperBound(positiveFeatureCount, profile.Sparse.Fanout)
	if upper == 0 {
		return 0
	}
	return float64(profile.Sparse.Active) / float64(upper)
}
