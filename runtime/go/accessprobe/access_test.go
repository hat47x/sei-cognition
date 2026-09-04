package accessprobe

import (
	"errors"
	"testing"

	"github.com/hat47x/soza/runtime/go/interactionprobe"
	"github.com/hat47x/soza/runtime/go/semanticruntime"
)

func logical(kind, id, scope string) semanticruntime.LogicalReference {
	return semanticruntime.LogicalReference{Kind: kind, ID: id, Scope: scope}
}

func seedDecision(t *testing.T, store *interactionprobe.CanonicalStore) semanticruntime.LogicalReference {
	t.Helper()
	human := interactionprobe.NewHumanSurface(store)
	inquiry, err := human.StartInquiry("I-ACCESS", "製品アクセス権と意味上の責任を分離して確認する")
	if err != nil {
		t.Fatalf("StartInquiry() error = %v", err)
	}
	decision := logical("decision", "D-ACCESS", "case-a")
	responsibility := logical("subject", "alice", "org-a")
	if err := human.RecordDecision(interactionprobe.DecisionInput{
		Ref:                decision,
		Statement:          "この判断の意味上の責任主体はAliceとして記録する",
		ContextRefs:        []semanticruntime.LogicalReference{inquiry},
		ResponsibilityRefs: []semanticruntime.LogicalReference{responsibility},
	}); err != nil {
		t.Fatalf("RecordDecision() error = %v", err)
	}
	return decision
}

func TestIdPReplacementPreservesBoundedSubjectAndHistoricalResponsibility(t *testing.T) {
	store := interactionprobe.NewCanonicalStore()
	decisionRef := seedDecision(t, store)

	directory := NewIdentityDirectory()
	alice := BoundedSubjectRef{ScopeRef: "org-a", SubjectID: "alice"}
	oldIdentity := AuthenticationIdentity{Provider: "idp-old", SubjectID: "alice-001", ActorKind: "human"}
	newIdentity := AuthenticationIdentity{Provider: "idp-new", SubjectID: "00u-new-alice", ActorKind: "human"}
	if err := directory.Bind(oldIdentity, alice); err != nil {
		t.Fatalf("Bind(old) error = %v", err)
	}
	if err := directory.Bind(newIdentity, alice); err != nil {
		t.Fatalf("Bind(new) error = %v", err)
	}

	policy := NewPolicy()
	if err := policy.Grant("scope-team-a", alice, PermissionRead); err != nil {
		t.Fatalf("Grant() error = %v", err)
	}
	guarded := GuardedStore{Store: store, Directory: directory, Policy: policy, ScopeID: "scope-team-a"}

	for _, identity := range []AuthenticationIdentity{oldIdentity, newIdentity} {
		record, found, err := guarded.Read(identity, decisionRef)
		if err != nil {
			t.Fatalf("Read(%s) error = %v", identity.Provider, err)
		}
		if !found || record.Decision == nil || record.Decision.Decision == nil {
			t.Fatalf("Read(%s) did not reconstruct decision: %#v", identity.Provider, record)
		}
		refs := record.Decision.Decision.ResponsibilityRefs
		if len(refs) != 1 {
			t.Fatalf("responsibility refs = %#v, want one", refs)
		}
		logicalRef, ok := refs[0].LogicalIdentity()
		if !ok || logicalRef != logical("subject", "alice", "org-a") {
			t.Fatalf("historical responsibility changed after identity replacement: %#v", refs[0])
		}
	}
}

func TestSemanticResponsibilityDoesNotGrantProductAccess(t *testing.T) {
	store := interactionprobe.NewCanonicalStore()
	decisionRef := seedDecision(t, store)

	directory := NewIdentityDirectory()
	alice := BoundedSubjectRef{ScopeRef: "org-a", SubjectID: "alice"}
	identity := AuthenticationIdentity{Provider: "idp", SubjectID: "alice-login", ActorKind: "human"}
	if err := directory.Bind(identity, alice); err != nil {
		t.Fatalf("Bind() error = %v", err)
	}

	guarded := GuardedStore{Store: store, Directory: directory, Policy: NewPolicy(), ScopeID: "scope-team-a"}
	_, _, err := guarded.Read(identity, decisionRef)
	var enforcement EnforcementError
	if !errors.As(err, &enforcement) {
		t.Fatalf("Read() error = %v, want EnforcementError", err)
	}
	if enforcement.Evaluation.Status != AccessDenied {
		t.Fatalf("Read() status = %s, want denied", enforcement.Evaluation.Status)
	}
}

func TestProductAdministratorDoesNotBecomeSemanticResponsible(t *testing.T) {
	store := interactionprobe.NewCanonicalStore()
	decisionRef := seedDecision(t, store)
	before, err := store.Digest()
	if err != nil {
		t.Fatalf("Digest() before error = %v", err)
	}

	directory := NewIdentityDirectory()
	bob := BoundedSubjectRef{ScopeRef: "org-a", SubjectID: "bob"}
	identity := AuthenticationIdentity{Provider: "idp", SubjectID: "bob-admin", ActorKind: "human"}
	_ = directory.Bind(identity, bob)
	policy := NewPolicy()
	_ = policy.Grant("scope-team-a", bob, PermissionAdminister)
	guarded := GuardedStore{Store: store, Directory: directory, Policy: policy, ScopeID: "scope-team-a"}

	if evaluation := guarded.Evaluate(identity, PermissionAdminister); evaluation.Status != AccessAllowed {
		t.Fatalf("administer status = %s, want allowed", evaluation.Status)
	}
	if evaluation := guarded.Evaluate(identity, PermissionRead); evaluation.Status != AccessDenied {
		t.Fatalf("read status = %s, want denied", evaluation.Status)
	}

	after, err := store.Digest()
	if err != nil {
		t.Fatalf("Digest() after error = %v", err)
	}
	if before != after {
		t.Fatalf("product admin permission changed canonical source: before=%s after=%s", before, after)
	}

	record, found, err := store.Find(decisionRef)
	if err != nil || !found {
		t.Fatalf("Find() = found:%v err:%v", found, err)
	}
	refs := record.Decision.Decision.ResponsibilityRefs
	if len(refs) != 1 {
		t.Fatalf("responsibility refs changed: %#v", refs)
	}
	logicalRef, _ := refs[0].LogicalIdentity()
	if logicalRef.ID != "alice" {
		t.Fatalf("product administrator became semantic responsible: %#v", logicalRef)
	}
}

func TestActorKindDoesNotInferPermissionAndNotEvaluatedDiffersFromDenied(t *testing.T) {
	directory := NewIdentityDirectory()
	policy := NewPolicy()
	ai := BoundedSubjectRef{ScopeRef: "org-a", SubjectID: "agent-1"}
	boundAI := AuthenticationIdentity{Provider: "idp", SubjectID: "agent-login", ActorKind: "ai"}
	if err := directory.Bind(boundAI, ai); err != nil {
		t.Fatalf("Bind() error = %v", err)
	}

	denied := policy.Evaluate(directory, boundAI, "scope-team-a", PermissionAppend)
	if denied.Status != AccessDenied {
		t.Fatalf("bound AI without grant = %s, want denied", denied.Status)
	}

	unboundHuman := AuthenticationIdentity{Provider: "idp", SubjectID: "unknown-human", ActorKind: "human"}
	notEvaluated := policy.Evaluate(directory, unboundHuman, "scope-team-a", PermissionAppend)
	if notEvaluated.Status != AccessNotEvaluated {
		t.Fatalf("unbound human = %s, want not_evaluated", notEvaluated.Status)
	}
	if denied.Status == notEvaluated.Status {
		t.Fatal("denied and not_evaluated were flattened")
	}
}

func TestSelectiveDisclosureProducesWithheldProjectionWithoutChangingCanonicalSource(t *testing.T) {
	store := interactionprobe.NewCanonicalStore()
	decisionRef := seedDecision(t, store)
	human := interactionprobe.NewHumanSurface(store)
	if _, err := human.RecordUnknown("U-INTERNAL", "内部資料の追加確認事項"); err != nil {
		t.Fatalf("RecordUnknown() error = %v", err)
	}
	before, err := store.Digest()
	if err != nil {
		t.Fatalf("Digest() before error = %v", err)
	}

	directory := NewIdentityDirectory()
	external := BoundedSubjectRef{ScopeRef: "partner-b", SubjectID: "reviewer"}
	identity := AuthenticationIdentity{Provider: "partner-idp", SubjectID: "reviewer-22", ActorKind: "human"}
	_ = directory.Bind(identity, external)
	policy := NewPolicy()
	_ = policy.Grant("scope-collab", external, PermissionRead)
	guarded := GuardedStore{Store: store, Directory: directory, Policy: policy, ScopeID: "scope-collab"}
	disclosure := NewDisclosurePolicy()
	if err := disclosure.Withhold("scope-collab", external, decisionRef); err != nil {
		t.Fatalf("Withhold() error = %v", err)
	}

	projection, err := Project(identity, guarded, disclosure)
	if err != nil {
		t.Fatalf("Project() error = %v", err)
	}
	if projection.WithheldCount != 1 {
		t.Fatalf("WithheldCount = %d, want 1", projection.WithheldCount)
	}
	for _, record := range projection.VisibleRecords {
		if record.Decision != nil && record.Decision.Decision != nil && record.Decision.Decision.Ref == decisionRef {
			t.Fatal("withheld decision leaked into visible projection")
		}
	}

	after, err := store.Digest()
	if err != nil {
		t.Fatalf("Digest() after error = %v", err)
	}
	if before != after {
		t.Fatalf("disclosure projection changed canonical source: before=%s after=%s", before, after)
	}
	record, found, err := store.Find(decisionRef)
	if err != nil || !found || record.Decision == nil {
		t.Fatalf("canonical withheld record was lost: found=%v err=%v record=%#v", found, err, record)
	}
}

func TestSelectiveDisclosureRequiresScopeReadPermission(t *testing.T) {
	store := interactionprobe.NewCanonicalStore()
	seedDecision(t, store)
	directory := NewIdentityDirectory()
	subject := BoundedSubjectRef{ScopeRef: "partner-b", SubjectID: "reviewer"}
	identity := AuthenticationIdentity{Provider: "partner-idp", SubjectID: "reviewer-22", ActorKind: "human"}
	_ = directory.Bind(identity, subject)
	guarded := GuardedStore{Store: store, Directory: directory, Policy: NewPolicy(), ScopeID: "scope-collab"}

	_, err := Project(identity, guarded, NewDisclosurePolicy())
	var enforcement EnforcementError
	if !errors.As(err, &enforcement) || enforcement.Evaluation.Status != AccessDenied {
		t.Fatalf("Project() error = %v, want denied EnforcementError", err)
	}
}
