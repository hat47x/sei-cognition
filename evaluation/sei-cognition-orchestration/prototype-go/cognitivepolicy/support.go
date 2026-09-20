package cognitivepolicy

import "sort"

// RouteObservationSupport describes observational evidence available for one
// allowed route. It is descriptive only and does not estimate propensities,
// causal effects, or statistical confidence.
type RouteObservationSupport struct {
	Assessed               int
	NotAssessed            int
	ObservedPolicyVersions []string
}

// ObservationalSupport externalizes which allowed routes and policy versions
// are represented in OutcomeRecord observations. Full route coverage does not
// imply that route assignment was unbiased or randomized.
type ObservationalSupport struct {
	ProblemClass              string
	Routes                    map[string]RouteObservationSupport
	TotalAssessed             int
	TotalNotAssessed          int
	RoutesWithAssessed        []string
	RoutesWithoutAssessed     []string
	ObservedPolicyVersions    []string
	AllAllowedRoutesAssessed  bool
	SelectionBiasCorrected    bool
}

// DiagnoseObservationalSupport reuses OutcomeRecord validation and aggregation
// without changing candidate snapshots or the active policy.
//
// The diagnostic intentionally does not perform propensity estimation,
// inverse-propensity weighting, causal correction, confidence estimation, or
// automatic policy gating.
func (s *Store) DiagnoseObservationalSupport(
	records []OutcomeRecord,
) (map[string]ObservationalSupport, error) {
	stats, err := s.aggregate(records)
	if err != nil {
		return nil, err
	}

	out := make(map[string]ObservationalSupport, len(s.definitions))
	for problemClass, definition := range s.definitions {
		support := ObservationalSupport{
			ProblemClass:           problemClass,
			Routes:                 make(map[string]RouteObservationSupport, len(definition.AllowedRoutes)),
			SelectionBiasCorrected: false,
		}
		policyVersions := make(map[string]struct{})

		for _, option := range definition.AllowedRoutes {
			routeStats := stats[problemClass][option.ID]
			versions := sortedPolicyVersions(routeStats.ObservedPolicyVersions)
			support.Routes[option.ID] = RouteObservationSupport{
				Assessed:               routeStats.Assessed,
				NotAssessed:            routeStats.NotAssessed,
				ObservedPolicyVersions: versions,
			}
			support.TotalAssessed += routeStats.Assessed
			support.TotalNotAssessed += routeStats.NotAssessed
			if routeStats.Assessed > 0 {
				support.RoutesWithAssessed = append(support.RoutesWithAssessed, option.ID)
			} else {
				support.RoutesWithoutAssessed = append(support.RoutesWithoutAssessed, option.ID)
			}
			for _, version := range versions {
				policyVersions[version] = struct{}{}
			}
		}

		sort.Strings(support.RoutesWithAssessed)
		sort.Strings(support.RoutesWithoutAssessed)
		support.ObservedPolicyVersions = sortedStringSet(policyVersions)
		support.AllAllowedRoutesAssessed = len(support.RoutesWithoutAssessed) == 0
		out[problemClass] = support
	}
	return out, nil
}

func sortedPolicyVersions(in map[string]int) []string {
	out := make([]string, 0, len(in))
	for version := range in {
		out = append(out, version)
	}
	sort.Strings(out)
	return out
}

func sortedStringSet(in map[string]struct{}) []string {
	out := make([]string, 0, len(in))
	for value := range in {
		out = append(out, value)
	}
	sort.Strings(out)
	return out
}
