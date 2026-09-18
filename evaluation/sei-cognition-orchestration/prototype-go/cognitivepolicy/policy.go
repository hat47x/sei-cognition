// Package cognitivepolicy provides an evaluation-only outcome-informed
// routing policy prototype for SEI Cognition.
//
// It learns route efficacy, not semantic truth. Policy candidates are immutable
// snapshots and never become active without an explicit activation step.
package cognitivepolicy

import (
	"errors"
	"fmt"
	"math"
	"sort"
	"strings"
)

const BaselineVersion = "v0"

type CognitiveOutcome string

const (
	CognitiveSufficient  CognitiveOutcome = "sufficient"
	CognitiveInsufficient CognitiveOutcome = "insufficient"
	CognitiveNotAssessed CognitiveOutcome = "not-assessed"
)

type ExecutionOutcome string

const (
	ExecutionCompleted   ExecutionOutcome = "completed"
	ExecutionFailed      ExecutionOutcome = "failed"
	ExecutionNotRecorded ExecutionOutcome = "not-recorded"
)

type OutcomeRecord struct {
	ProblemClass          string
	Route                 string
	CognitiveOutcome      CognitiveOutcome
	ExecutionOutcome      ExecutionOutcome
	ProvenanceRef         string
	ObservedPolicyVersion string
}

type RouteOption struct {
	ID              string
	EscalationLevel int
}

type ProblemPolicy struct {
	ProblemClass            string
	StaticRoute             string
	AllowedRoutes           []RouteOption
	RequiredSuccessRate     float64
	MinAssessedObservations int
}

type RouteStats struct {
	Assessed        int
	Sufficient      int
	Insufficient    int
	NotAssessed     int
	ExecutionFailed int
	SuccessRate     float64
}

type Selection struct {
	Route  string
	Reason string
	Stats  RouteStats
}

type Snapshot struct {
	Version       string
	ParentVersion string
	Selections    map[string]Selection
	Efficacy      map[string]map[string]RouteStats
}

type Store struct {
	definitions map[string]ProblemPolicy
	snapshots   map[string]Snapshot
	active      string
	nextVersion int
}

func NewStore(definitions []ProblemPolicy) (*Store, error) {
	if len(definitions) == 0 {
		return nil, errors.New("at least one problem policy is required")
	}
	defs := make(map[string]ProblemPolicy, len(definitions))
	baselineSelections := make(map[string]Selection, len(definitions))
	for _, definition := range definitions {
		if err := validateProblemPolicy(definition); err != nil {
			return nil, err
		}
		if _, exists := defs[definition.ProblemClass]; exists {
			return nil, fmt.Errorf("duplicate problem class: %s", definition.ProblemClass)
		}
		cloned := cloneProblemPolicy(definition)
		defs[definition.ProblemClass] = cloned
		baselineSelections[definition.ProblemClass] = Selection{
			Route:  definition.StaticRoute,
			Reason: "static baseline",
		}
	}
	baseline := Snapshot{
		Version:    BaselineVersion,
		Selections: baselineSelections,
		Efficacy:   make(map[string]map[string]RouteStats),
	}
	return &Store{
		definitions: defs,
		snapshots:   map[string]Snapshot{BaselineVersion: cloneSnapshot(baseline)},
		active:      BaselineVersion,
		nextVersion: 1,
	}, nil
}

func (s *Store) ActiveVersion() string {
	return s.active
}

func (s *Store) Route(problemClass string) (string, error) {
	definition, ok := s.definitions[problemClass]
	if !ok {
		return "", fmt.Errorf("unknown problem class: %s", problemClass)
	}
	snapshot := s.snapshots[s.active]
	selection, ok := snapshot.Selections[definition.ProblemClass]
	if !ok {
		return "", fmt.Errorf("active snapshot %s has no route for %s", s.active, problemClass)
	}
	return selection.Route, nil
}

func (s *Store) Snapshot(version string) (Snapshot, bool) {
	snapshot, ok := s.snapshots[version]
	if !ok {
		return Snapshot{}, false
	}
	return cloneSnapshot(snapshot), true
}

// BuildCandidate aggregates only explicit cognitive assessments. Execution
// outcome is tracked separately and never converted into cognitive success or
// failure by this package.
func (s *Store) BuildCandidate(records []OutcomeRecord) (Snapshot, error) {
	stats, err := s.aggregate(records)
	if err != nil {
		return Snapshot{}, err
	}

	version := fmt.Sprintf("v%d", s.nextVersion)
	selections := make(map[string]Selection, len(s.definitions))
	for problemClass, definition := range s.definitions {
		selected := Selection{
			Route:  definition.StaticRoute,
			Reason: "static fallback: no allowed route met evidence floor",
		}
		type eligibleRoute struct {
			option RouteOption
			stats  RouteStats
		}
		var eligible []eligibleRoute
		for _, option := range definition.AllowedRoutes {
			routeStats := stats[problemClass][option.ID]
			if routeStats.Assessed < definition.MinAssessedObservations {
				continue
			}
			if routeStats.SuccessRate < definition.RequiredSuccessRate {
				continue
			}
			eligible = append(eligible, eligibleRoute{option: option, stats: routeStats})
		}
		sort.Slice(eligible, func(i, j int) bool {
			if eligible[i].option.EscalationLevel != eligible[j].option.EscalationLevel {
				return eligible[i].option.EscalationLevel < eligible[j].option.EscalationLevel
			}
			if eligible[i].stats.SuccessRate != eligible[j].stats.SuccessRate {
				return eligible[i].stats.SuccessRate > eligible[j].stats.SuccessRate
			}
			if eligible[i].stats.Assessed != eligible[j].stats.Assessed {
				return eligible[i].stats.Assessed > eligible[j].stats.Assessed
			}
			return eligible[i].option.ID < eligible[j].option.ID
		})
		if len(eligible) > 0 {
			selected = Selection{
				Route:  eligible[0].option.ID,
				Reason: "lowest escalation route meeting assessed evidence floor",
				Stats:  eligible[0].stats,
			}
		}
		selections[problemClass] = selected
	}

	candidate := Snapshot{
		Version:       version,
		ParentVersion: s.active,
		Selections:    selections,
		Efficacy:      cloneEfficacy(stats),
	}
	s.snapshots[version] = cloneSnapshot(candidate)
	s.nextVersion++
	return cloneSnapshot(candidate), nil
}

// Activate changes only the active policy pointer. Snapshots remain immutable,
// so activating an older version is also the rollback mechanism.
func (s *Store) Activate(version string) error {
	if _, ok := s.snapshots[version]; !ok {
		return fmt.Errorf("unknown policy version: %s", version)
	}
	s.active = version
	return nil
}

func (s *Store) aggregate(records []OutcomeRecord) (map[string]map[string]RouteStats, error) {
	stats := make(map[string]map[string]RouteStats, len(s.definitions))
	for problemClass := range s.definitions {
		stats[problemClass] = make(map[string]RouteStats)
	}

	for i, record := range records {
		if err := s.validateOutcomeRecord(record); err != nil {
			return nil, fmt.Errorf("outcome record %d: %w", i, err)
		}
		routeStats := stats[record.ProblemClass][record.Route]
		if record.ExecutionOutcome == ExecutionFailed {
			routeStats.ExecutionFailed++
		}
		switch record.CognitiveOutcome {
		case CognitiveSufficient:
			routeStats.Assessed++
			routeStats.Sufficient++
		case CognitiveInsufficient:
			routeStats.Assessed++
			routeStats.Insufficient++
		case CognitiveNotAssessed:
			routeStats.NotAssessed++
		}
		if routeStats.Assessed > 0 {
			routeStats.SuccessRate = float64(routeStats.Sufficient) / float64(routeStats.Assessed)
		}
		stats[record.ProblemClass][record.Route] = routeStats
	}
	return stats, nil
}

func (s *Store) validateOutcomeRecord(record OutcomeRecord) error {
	if strings.TrimSpace(record.ProblemClass) == "" {
		return errors.New("problem class must not be empty")
	}
	definition, ok := s.definitions[record.ProblemClass]
	if !ok {
		return fmt.Errorf("unknown problem class: %s", record.ProblemClass)
	}
	if !routeAllowed(definition, record.Route) {
		return fmt.Errorf("route %s is not allowed for problem class %s", record.Route, record.ProblemClass)
	}
	switch record.CognitiveOutcome {
	case CognitiveSufficient, CognitiveInsufficient, CognitiveNotAssessed:
	default:
		return fmt.Errorf("unsupported cognitive outcome: %s", record.CognitiveOutcome)
	}
	switch record.ExecutionOutcome {
	case ExecutionCompleted, ExecutionFailed, ExecutionNotRecorded:
	default:
		return fmt.Errorf("unsupported execution outcome: %s", record.ExecutionOutcome)
	}
	if strings.TrimSpace(record.ProvenanceRef) == "" {
		return errors.New("outcome provenance ref must not be empty")
	}
	if strings.TrimSpace(record.ObservedPolicyVersion) == "" {
		return errors.New("observed policy version must not be empty")
	}
	if _, ok := s.snapshots[record.ObservedPolicyVersion]; !ok {
		return fmt.Errorf("unknown observed policy version: %s", record.ObservedPolicyVersion)
	}
	return nil
}

func validateProblemPolicy(definition ProblemPolicy) error {
	if strings.TrimSpace(definition.ProblemClass) == "" {
		return errors.New("problem class must not be empty")
	}
	if definition.ProblemClass != strings.TrimSpace(definition.ProblemClass) {
		return errors.New("problem class must be canonical")
	}
	if strings.TrimSpace(definition.StaticRoute) == "" {
		return fmt.Errorf("problem class %s static route must not be empty", definition.ProblemClass)
	}
	if definition.StaticRoute != strings.TrimSpace(definition.StaticRoute) {
		return fmt.Errorf("problem class %s static route must be canonical", definition.ProblemClass)
	}
	if len(definition.AllowedRoutes) == 0 {
		return fmt.Errorf("problem class %s requires at least one allowed route", definition.ProblemClass)
	}
	if math.IsNaN(definition.RequiredSuccessRate) || math.IsInf(definition.RequiredSuccessRate, 0) ||
		definition.RequiredSuccessRate < 0 || definition.RequiredSuccessRate > 1 {
		return fmt.Errorf("problem class %s required success rate must be finite and in [0,1]", definition.ProblemClass)
	}
	if definition.MinAssessedObservations <= 0 {
		return fmt.Errorf("problem class %s minimum assessed observations must be > 0", definition.ProblemClass)
	}

	seen := make(map[string]struct{}, len(definition.AllowedRoutes))
	staticFound := false
	for _, option := range definition.AllowedRoutes {
		if strings.TrimSpace(option.ID) == "" {
			return fmt.Errorf("problem class %s contains empty route id", definition.ProblemClass)
		}
		if option.ID != strings.TrimSpace(option.ID) {
			return fmt.Errorf("problem class %s route id must be canonical: %q", definition.ProblemClass, option.ID)
		}
		if option.EscalationLevel < 0 {
			return fmt.Errorf("problem class %s route %s has negative escalation level", definition.ProblemClass, option.ID)
		}
		if _, exists := seen[option.ID]; exists {
			return fmt.Errorf("problem class %s has duplicate route %s", definition.ProblemClass, option.ID)
		}
		seen[option.ID] = struct{}{}
		if option.ID == definition.StaticRoute {
			staticFound = true
		}
	}
	if !staticFound {
		return fmt.Errorf("problem class %s static route %s is not in allowed routes", definition.ProblemClass, definition.StaticRoute)
	}
	return nil
}

func routeAllowed(definition ProblemPolicy, route string) bool {
	for _, option := range definition.AllowedRoutes {
		if option.ID == route {
			return true
		}
	}
	return false
}

func cloneProblemPolicy(in ProblemPolicy) ProblemPolicy {
	out := in
	out.AllowedRoutes = append([]RouteOption(nil), in.AllowedRoutes...)
	return out
}

func cloneSnapshot(in Snapshot) Snapshot {
	out := Snapshot{
		Version:       in.Version,
		ParentVersion: in.ParentVersion,
		Selections:    make(map[string]Selection, len(in.Selections)),
		Efficacy:      cloneEfficacy(in.Efficacy),
	}
	for problemClass, selection := range in.Selections {
		out.Selections[problemClass] = selection
	}
	return out
}

func cloneEfficacy(in map[string]map[string]RouteStats) map[string]map[string]RouteStats {
	out := make(map[string]map[string]RouteStats, len(in))
	for problemClass, routes := range in {
		routeCopy := make(map[string]RouteStats, len(routes))
		for route, stats := range routes {
			routeCopy[route] = stats
		}
		out[problemClass] = routeCopy
	}
	return out
}
