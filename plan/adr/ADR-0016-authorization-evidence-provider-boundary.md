# ADR-0016: AuthorizationをProviderへ残し、SOZAは評価Evidenceを参照する

Status: **Accepted**  
Related Issue: **ISSUE-000018**  
Updated: 2026-08-31

## Context

SOZAはDecision、Responsibility、Capability Choiceを扱うが、実行時のAuthorizationは、対象Providerのcredential、policy、resource state等に依存する。

TEI設計系列でも、認証・認可を固定のUser / Role tableへ押し込まず、標準Capability入口と差し替え可能Providerへ分ける方向が採られている。また認可は、External EntryとResource / Subjectのように複数段階で評価され得る。

SOZAがAuthorization engineを所有すると、IAM、RBAC、ABAC、legacy auth等の固有モデルがCoreへ流入する。一方、認可結果を全く残さなければ、DecisionからExecutionまでの監査線を後から追えない。

## Decision

### 1. Authorization engine / policy ontologyをSOZA Coreへ追加しない

Authorizationは、実行対象を所有するProviderまたはauthoritative Authorization Providerが評価する。

```text
Decision != Responsibility != Authorization != Execution
```

SOZA DecisionがあってもAuthorityは成立しない。Providerが実行を許可できる状態でも、それだけでSOZA Decisionが存在したことにはならない。

### 2. Authorization評価は必要に応じてEvidenceとして参照する

後からDecision / Executionを監査する必要がある場合、Providerが行ったAuthorization evaluationを、Observation、AssuranceRecord、EvidenceUse、Provider-specific reference等から辿れるようにする。

SOZAは認可方式そのものを共通化するのではなく、**どの評価を、どの文脈で利用したか**を保持する。

### 3. Universal `AuthorizationResult` Artifactを現時点では追加しない

Providerごとの認可方式は大きく異なるため、`allowed / denied`等をUniversal型へ固定しない。

まず既存Epistemics / AssuranceとProvider-specific evaluation referenceで表現し、複数Providerで意味不足が反復した場合に再検討する。

### 4. Entry / Resourceの評価を一つのbooleanへ潰さない

External Entry AuthorizationとResource / Subject Authorizationは、対象、scope、時点、policyが異なり得る。

監査に必要な場合は別々のevaluationとして参照可能にする。

```text
Entry Authorization != Resource Authorization
```

### 5. 過去のAuthorizationと現在のAuthorizationを分離する

後日policyやcredentialが変わっても、過去Execution時点でどの評価が使われたかを書き換えない。

歴史再構成が必要な場合は、Provider evaluation reference、policy binding、対象resource等を必要に応じてExactArtifactBindingまたは同等の検証可能な参照へ結べる設計を許す。

```text
past authorization != current authorization
```

### 6. 未評価を拒否へ変換しない

Authorization Providerが利用不能、必要context不足等で評価できなかった場合、それを自動的に`denied`へ変換しない。

```text
not evaluated != denied
```

実行を安全側に止めるPolicyは別途成立し得るが、認識上の状態は区別する。

### 7. Provider acknowledgementを十分なAuthorization Evidenceとみなさない

command acceptedやsuccess acknowledgementだけでは、どのscope / resourceについて何が認可されたかを示すとは限らない。

必要なAssurance水準はProfile / Policyから要求する。

## Consequences

### Positive

- SOZAがIAM / RBAC / legacy auth engineへ肥大化しない。
- TEI、SaaS、外部組織等の異なる認可方式を同じDecision Memoryから利用できる。
- 過去Decisionと過去Authorizationを別々に再構成できる。
- ResponsibilityからAuthorityを推定する誤りを避けやすい。
- 未評価と拒否の意味差を保持できる。

### Costs

- Provider adapterは監査に必要なevaluation referenceやAssurance情報を外在化する必要がある。
- 統一booleanよりProjection / queryが複雑になる。
- ProviderごとのEvidence品質をProfile / Policyで評価する設計が必要になる。

## Revisit conditions

次が複数Provider / domainで反復した場合にUniversal Authorization Artifactを再検討する。

- Authorization evaluation自体にSOZA共通のstable logical identityが必要になる。
- Provider-specific referenceではDecision / Execution監査に必要な意味を保持できない。
- 共通のrevision / Responsibility / Assurance relationが独立Artifactなしでは表現できない。

## Evidence

- `plan/kj/2026-08-31_RequirementInquiry_AuthorizationEvidence_ラウンドKJ.md`
- ADR-0004 / ADR-0010 / ADR-0011 / ADR-0014
- TEI設計系列のEntry Authorization / Resource Authorization分離、差し替え可能Auth Provider方針

## Natural Japanese review

KJ統合と既存Decision / Responsibility / Provider境界を確定した後、意味を変えず自然な日本語となることを最優先に全文を再ドラフトし、最終意味監査を実施済み。
