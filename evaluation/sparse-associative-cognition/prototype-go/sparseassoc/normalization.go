package sparseassoc

import "errors"

// NormalizationMode selects an explicit evaluation-only preprocessing policy.
// The Encoder does not apply normalization implicitly.
type NormalizationMode uint8

const (
	NormalizationNone NormalizationMode = iota
	NormalizationGlobal
	NormalizationPerChannel
)

// NormalizationConfig controls bounded divisive normalization. DenominatorFloor
// prevents weak feature groups from being amplified merely because they are sparse.
type NormalizationConfig struct {
	Mode             NormalizationMode
	DenominatorFloor float32
}

// NormalizeFeatures returns a copy of features with positive, keyed feature
// weights divided according to cfg. Zero/negative weights and empty keys are
// preserved because Encoder already ignores them. No semantic feature is added.
func NormalizeFeatures(features []Feature, cfg NormalizationConfig) ([]Feature, error) {
	if cfg.DenominatorFloor <= 0 {
		return nil, errors.New("denominator floor must be > 0")
	}
	out := append([]Feature(nil), features...)
	switch cfg.Mode {
	case NormalizationNone:
		return out, nil
	case NormalizationGlobal:
		var total float32
		for _, f := range features {
			if f.Weight > 0 && f.Key != "" {
				total += f.Weight
			}
		}
		denominator := maxFloat32(total, cfg.DenominatorFloor)
		for i := range out {
			if out[i].Weight > 0 && out[i].Key != "" {
				out[i].Weight /= denominator
			}
		}
		return out, nil
	case NormalizationPerChannel:
		totals := make(map[string]float32)
		for _, f := range features {
			if f.Weight > 0 && f.Key != "" {
				totals[f.Channel] += f.Weight
			}
		}
		for i := range out {
			if out[i].Weight <= 0 || out[i].Key == "" {
				continue
			}
			out[i].Weight /= maxFloat32(totals[out[i].Channel], cfg.DenominatorFloor)
		}
		return out, nil
	default:
		return nil, errors.New("unknown normalization mode")
	}
}

func maxFloat32(a, b float32) float32 {
	if a > b {
		return a
	}
	return b
}
