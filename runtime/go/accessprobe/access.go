package accessprobe

import (
	"errors"
	"fmt"

	"github.com/hat47x/soza/runtime/go/interactionprobe"
	"github.com/hat47x/soza/runtime/go/semanticruntime"
)

// BoundedSubjectRef はADR-0004の主体境界をreference probeで扱うための最小表現です。
// Product Access Scopeや認証Provider固有IDとは別のものとして保持します。
type BoundedSubjectRef struct {
	ScopeRef  string
	SubjectID string
}

func (s BoundedSubjectRef) key() string {
	return s.ScopeRef + "\x00" + s.SubjectID
}

// AuthenticationIdentity は認証Providerが現在のrequest主体を識別した結果を表します。
// ActorKindは観測情報として保持しますが、permission推定には使いません。
type AuthenticationIdentity struct {
	Provider  string
	SubjectID string
	ActorKind string
}

func (i AuthenticationIdentity) key() string {
	return i.Provider + "\x00" + i.SubjectID
}

// IdentityDirectory は外部authentication identityとBounded Subjectの対応を保持する
// reference probe用のProduct security componentです。Universal Identity ontologyではありません。
type IdentityDirectory struct {
	bindings map[string]BoundedSubjectRef
}

func NewIdentityDirectory() *IdentityDirectory {
	return &IdentityDirectory{bindings: map[string]BoundedSubjectRef{}}
}

func (d *IdentityDirectory) Bind(identity AuthenticationIdentity, subject BoundedSubjectRef) error {
	if d == nil {
		return errors.New("identity directory is required")
	}
	if identity.Provider == "" || identity.SubjectID == "" {
		return errors.New("authentication identity requires provider and subject id")
	}
	if subject.ScopeRef == "" || subject.SubjectID == "" {
		return errors.New("bounded subject requires scope ref and subject id")
	}
	key := identity.key()
	if current, exists := d.bindings[key]; exists && current != subject {
		return errors.New("authentication identity is already bound to another bounded subject")
	}
	d.bindings[key] = subject
	return nil
}

func (d *IdentityDirectory) Resolve(identity AuthenticationIdentity) (BoundedSubjectRef, bool) {
	if d == nil {
		return BoundedSubjectRef{}, false
	}
	subject, ok := d.bindings[identity.key()]
	return subject, ok
}

type Permission string

const (
	PermissionRead       Permission = "read"
	PermissionAppend     Permission = "append"
	PermissionReview     Permission = "review"
	PermissionShare      Permission = "share"
	PermissionAdminister Permission = "administer"
)

type AccessStatus string

const (
	AccessAllowed      AccessStatus = "allowed"
	AccessDenied       AccessStatus = "denied"
	AccessNotEvaluated AccessStatus = "not_evaluated"
)

type AccessEvaluation struct {
	Status     AccessStatus
	Subject    BoundedSubjectRef
	ScopeID    string
	Permission Permission
	Reason     string
}

// Policy はProduct Access Scopeごとのpermissionを評価するprobe用Policyです。
// semantic Responsibility / AuthorityやActorKindを入力にしません。
type Policy struct {
	grants map[string]map[string]map[Permission]bool
}

func NewPolicy() *Policy {
	return &Policy{grants: map[string]map[string]map[Permission]bool{}}
}

func (p *Policy) Grant(scopeID string, subject BoundedSubjectRef, permissions ...Permission) error {
	if p == nil {
		return errors.New("policy is required")
	}
	if scopeID == "" {
		return errors.New("product access scope is required")
	}
	if subject.ScopeRef == "" || subject.SubjectID == "" {
		return errors.New("bounded subject is required")
	}
	if p.grants[scopeID] == nil {
		p.grants[scopeID] = map[string]map[Permission]bool{}
	}
	key := subject.key()
	if p.grants[scopeID][key] == nil {
		p.grants[scopeID][key] = map[Permission]bool{}
	}
	for _, permission := range permissions {
		p.grants[scopeID][key][permission] = true
	}
	return nil
}

func (p *Policy) Evaluate(directory *IdentityDirectory, identity AuthenticationIdentity, scopeID string, permission Permission) AccessEvaluation {
	if directory == nil || p == nil || scopeID == "" || permission == "" {
		return AccessEvaluation{Status: AccessNotEvaluated, ScopeID: scopeID, Permission: permission, Reason: "access context is incomplete"}
	}
	subject, ok := directory.Resolve(identity)
	if !ok {
		return AccessEvaluation{Status: AccessNotEvaluated, ScopeID: scopeID, Permission: permission, Reason: "authentication identity is not bound to a bounded subject"}
	}
	evaluation := AccessEvaluation{Subject: subject, ScopeID: scopeID, Permission: permission}
	if p.grants[scopeID] != nil && p.grants[scopeID][subject.key()] != nil && p.grants[scopeID][subject.key()][permission] {
		evaluation.Status = AccessAllowed
		evaluation.Reason = "permission is granted by product access policy"
		return evaluation
	}
	evaluation.Status = AccessDenied
	evaluation.Reason = "permission is not granted by product access policy"
	return evaluation
}

// EnforcementError は監査上の評価状態を失わずにsafe failureさせるためのprobe用errorです。
type EnforcementError struct {
	Evaluation AccessEvaluation
}

func (e EnforcementError) Error() string {
	return fmt.Sprintf("product access %s: %s", e.Evaluation.Status, e.Evaluation.Reason)
}

// GuardedStore は既存interactionprobe.CanonicalStoreの手前でProduct Access Policyを評価します。
// Product permissionをsemantic Responsibility / Authorityへ変換しません。
type GuardedStore struct {
	Store     *interactionprobe.CanonicalStore
	Directory *IdentityDirectory
	Policy    *Policy
	ScopeID   string
}

func (g GuardedStore) Read(identity AuthenticationIdentity, ref semanticruntime.LogicalReference) (semanticruntime.RuntimeRecord, bool, error) {
	evaluation := g.Policy.Evaluate(g.Directory, identity, g.ScopeID, PermissionRead)
	if evaluation.Status != AccessAllowed {
		return semanticruntime.RuntimeRecord{}, false, EnforcementError{Evaluation: evaluation}
	}
	return g.Store.Find(ref)
}

func (g GuardedStore) Append(identity AuthenticationIdentity, record semanticruntime.RuntimeRecord) error {
	evaluation := g.Policy.Evaluate(g.Directory, identity, g.ScopeID, PermissionAppend)
	if evaluation.Status != AccessAllowed {
		return EnforcementError{Evaluation: evaluation}
	}
	return g.Store.Add(record)
}

func (g GuardedStore) Evaluate(identity AuthenticationIdentity, permission Permission) AccessEvaluation {
	return g.Policy.Evaluate(g.Directory, identity, g.ScopeID, permission)
}

// DisclosurePolicy はProduct Access Scopeへread可能な主体に対し、さらにrecord単位の
// Selective Disclosureを適用するprobe用Policyです。
type DisclosurePolicy struct {
	withheld map[string]map[string]map[string]bool
}

func NewDisclosurePolicy() *DisclosurePolicy {
	return &DisclosurePolicy{withheld: map[string]map[string]map[string]bool{}}
}

func logicalKey(ref semanticruntime.LogicalReference) string {
	return ref.Scope + "\x00" + ref.Kind + "\x00" + ref.ID
}

func (p *DisclosurePolicy) Withhold(scopeID string, subject BoundedSubjectRef, ref semanticruntime.LogicalReference) error {
	if p == nil {
		return errors.New("disclosure policy is required")
	}
	if scopeID == "" || subject.ScopeRef == "" || subject.SubjectID == "" || ref.Kind == "" || ref.ID == "" {
		return errors.New("scope, subject and logical reference are required")
	}
	if p.withheld[scopeID] == nil {
		p.withheld[scopeID] = map[string]map[string]bool{}
	}
	if p.withheld[scopeID][subject.key()] == nil {
		p.withheld[scopeID][subject.key()] = map[string]bool{}
	}
	p.withheld[scopeID][subject.key()][logicalKey(ref)] = true
	return nil
}

type DisclosureProjection struct {
	VisibleRecords []semanticruntime.RuntimeRecord
	WithheldCount  int
}

// Project はread permission確認後にSelective Disclosure Projectionを生成します。
// withheld recordをfake Unknown recordへ変換せず、canonical sourceも変更しません。
func Project(identity AuthenticationIdentity, guarded GuardedStore, disclosure *DisclosurePolicy) (DisclosureProjection, error) {
	evaluation := guarded.Evaluate(identity, PermissionRead)
	if evaluation.Status != AccessAllowed {
		return DisclosureProjection{}, EnforcementError{Evaluation: evaluation}
	}
	if guarded.Store == nil {
		return DisclosureProjection{}, errors.New("canonical store is required")
	}
	records, err := guarded.Store.Records()
	if err != nil {
		return DisclosureProjection{}, err
	}
	projection := DisclosureProjection{}
	for _, record := range records {
		ref, ok := runtimeRecordRef(record)
		if ok && disclosure != nil && disclosure.withheld[guarded.ScopeID] != nil && disclosure.withheld[guarded.ScopeID][evaluation.Subject.key()] != nil && disclosure.withheld[guarded.ScopeID][evaluation.Subject.key()][logicalKey(ref)] {
			projection.WithheldCount++
			continue
		}
		projection.VisibleRecords = append(projection.VisibleRecords, record)
	}
	return projection, nil
}

func runtimeRecordRef(record semanticruntime.RuntimeRecord) (semanticruntime.LogicalReference, bool) {
	if record.EnvelopeRecord.LogicalRef != nil {
		return *record.EnvelopeRecord.LogicalRef, true
	}
	if record.Decision != nil {
		if record.Decision.Decision != nil {
			return record.Decision.Decision.Ref, true
		}
		if record.Decision.Recommendation != nil {
			return record.Decision.Recommendation.Ref, true
		}
	}
	if record.Capability != nil {
		return record.Capability.Observation.Ref, true
	}
	return semanticruntime.LogicalReference{}, false
}
