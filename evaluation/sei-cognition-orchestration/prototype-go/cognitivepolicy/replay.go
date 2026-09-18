package cognitivepolicy

import (
	"fmt"
)

type ReplayCase struct {
	ID            string
	ProblemClass  string
	RouteOutcomes map[string]bool
}

type ReplayMetrics struct {
	TotalCases                  int
	PolicySuccesses             int
	StaticSuccesses             int
	UnnecessaryEscalations      int
	RegretAgainstStatic         int
	PolicySuccessRate           float64
	StaticSuccessRate           float64
	UnnecessaryEscalationRate   float64
	RegretAgainstStaticRate     float64
}

// Replay evaluates a fixed immutable policy snapshot against synthetic or
// otherwise counterfactually complete route outcomes. Production observations
// usually do not contain outcomes for routes that were not executed, so this
// helper must not be treated as an online estimator.
func (s *Store) Replay(version string, cases []ReplayCase) (ReplayMetrics, error) {
	snapshot, ok := s.snapshots[version]
	if !ok {
		return ReplayMetrics{}, fmt.Errorf("unknown policy version: %s", version)
	}
	if len(cases) == 0 {
		return ReplayMetrics{}, fmt.Errorf("at least one replay case is required")
	}

	var metrics ReplayMetrics
	for i, replayCase := range cases {
		definition, ok := s.definitions[replayCase.ProblemClass]
		if !ok {
			return ReplayMetrics{}, fmt.Errorf("replay case %d has unknown problem class: %s", i, replayCase.ProblemClass)
		}
		selection, ok := snapshot.Selections[replayCase.ProblemClass]
		if !ok {
			return ReplayMetrics{}, fmt.Errorf("snapshot %s has no route for %s", version, replayCase.ProblemClass)
		}
		if replayCase.ID == "" {
			return ReplayMetrics{}, fmt.Errorf("replay case %d id must not be empty", i)
		}
		if len(replayCase.RouteOutcomes) != len(definition.AllowedRoutes) {
			return ReplayMetrics{}, fmt.Errorf("replay case %s must provide outcomes for every allowed route", replayCase.ID)
		}
		for _, option := range definition.AllowedRoutes {
			if _, ok := replayCase.RouteOutcomes[option.ID]; !ok {
				return ReplayMetrics{}, fmt.Errorf("replay case %s missing route outcome for %s", replayCase.ID, option.ID)
			}
		}

		policySuccess := replayCase.RouteOutcomes[selection.Route]
		staticSuccess := replayCase.RouteOutcomes[definition.StaticRoute]
		metrics.TotalCases++
		if policySuccess {
			metrics.PolicySuccesses++
		}
		if staticSuccess {
			metrics.StaticSuccesses++
		}
		if !policySuccess && staticSuccess {
			metrics.RegretAgainstStatic++
		}
		if policySuccess {
			selectedLevel, _ := escalationLevel(definition, selection.Route)
			for _, option := range definition.AllowedRoutes {
				if option.EscalationLevel < definition.MinimumEscalationLevel ||
					option.EscalationLevel >= selectedLevel {
					continue
				}
				if replayCase.RouteOutcomes[option.ID] {
					metrics.UnnecessaryEscalations++
					break
				}
			}
		}
	}

	metrics.PolicySuccessRate = float64(metrics.PolicySuccesses) / float64(metrics.TotalCases)
	metrics.StaticSuccessRate = float64(metrics.StaticSuccesses) / float64(metrics.TotalCases)
	metrics.RegretAgainstStaticRate = float64(metrics.RegretAgainstStatic) / float64(metrics.TotalCases)
	if metrics.PolicySuccesses > 0 {
		metrics.UnnecessaryEscalationRate = float64(metrics.UnnecessaryEscalations) / float64(metrics.PolicySuccesses)
	}
	return metrics, nil
}

func escalationLevel(definition ProblemPolicy, route string) (int, bool) {
	for _, option := range definition.AllowedRoutes {
		if option.ID == route {
			return option.EscalationLevel, true
		}
	}
	return 0, false
}
