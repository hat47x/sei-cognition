# ADR-0016: AuthorizationをProviderへ残し、SOZAは評価Evidenceを参照する

Status: **Accepted**  
Related Issue: **ISSUE-000018**  
Updated: 2026-08-31

## Context

SOZAはDecision、Responsibility、Capability Choiceを扱うが、実行時のAuthorizationは、対象Providerのcredential、policy、resource state等に依存する。

Authorization方式には、IAM、RBAC、ABAC、legacy auth、外部IdP、Provider固有policy等、多様な形があり得る。SOZAがAuthorization engineを所有すると、これらの固有モデルがCoreへ流入しやすい。

一方で、認可評価の来歴をまったく残さなければ、DecisionからExecutionまでの監査線を後から辿れない。

## Decision

### 1. Authorization engine / policy ontologyをSOZA Coreへ追加しない

Authorizationは、実行対象を所有するProviderまたはauthoritative Authorization Providerが評価する。

```text
Decision != Responsibility != Authorization != Execution
```

SOZAにDecisionが存在しても、それだけでAuthorityは成立しない。逆に、Providerが実行を許可できる状態であることも、SOZA Decisionが存在したことを意味しない。

### 2. Authorization評価は必要に応じてEvidenceとして参照する

後からDecision / Executionを監査する必要がある場合、Providerが行ったAuthorization evaluationを、Observation、Assurance、EvidenceUse、Provider-specific reference等から辿れるようにする。

SOZAは認可方式そのものを一つに共通化するのではなく、**どの評価を、どの文脈で利用したか**を保持する。

### 3. Universal `AuthorizationResult` Artifactを現時点では追加しない

Providerごとの認可方式は大きく異なるため、`allowed / denied`等をUniversal型へ固定しない。

まず既存のEpistemics / Assurance境界とProvider-specific evaluation referenceで表現し、複数Providerで共通の意味不足が繰り返し確認された場合に再検討する。

### 4. Entry / Resourceの評価を一つのbooleanへ潰さない

External Entry AuthorizationとResource / Subject Authorizationは、対象、scope、時点、policyが異なり得る。

監査に必要な場合は、別々のevaluationとして参照できるようにする。

```text
Entry Authorization != Resource Authorization
```

### 5. 過去のAuthorizationと現在のAuthorizationを分離する

後からpolicyやcredentialが変わっても、過去Execution時点でどの評価が使われたかを書き換えない。

歴史再構成が必要な場合は、Provider evaluation reference、policy binding、対象resource等を、必要に応じてExactArtifactBindingまたは同等の検証可能な参照へ結べる設計を許す。

```text
past authorization != current authorization
```

### 6. 未評価を拒否へ変換しない

Authorization Providerを利用できない、必要なcontextが不足している等の理由で評価できなかった場合、それを認識上の状態として自動的に`denied`へ変換しない。

```text
not evaluated != denied
```

実行を安全側に停止するPolicyは別途成立し得るが、「評価できなかった」と「拒否された」は区別する。

### 7. Provider acknowledgementを十分なAuthorization Evidenceとみなさない

command acceptedやsuccess acknowledgementだけでは、どのscope / resourceについて何が認可されたかを示すとは限らない。

必要なAssurance水準はProfile / Policy側から要求する。

## Current realization

current first semantic runtimeとsynthetic Provider Adapterは、AuthorizationやExecutionを意図的に所有していない。

Provider AdapterのExecutable Evidenceでも、Observation mappingからRecommendation、Decision、Authority、Executionを生成しないことを確認している。

これは本ADRの分離を支持するが、Production Authorization Providerとの統合やAuthorization Evidenceの実運用を検証したものではない。

## Consequences

### Positive

- SOZAがIAM / RBAC / legacy auth engineへ肥大化しにくい。
- TEI、SaaS、外部組織等の異なる認可方式を、同じDecision Memoryから参照できる余地を保てる。
- 過去Decisionと過去Authorizationを別々に再構成できる。
- ResponsibilityからAuthorityを推定する誤りを避けやすい。
- 未評価と拒否の意味差を保持できる。

### Costs

- Provider adapterや統合境界では、監査に必要なevaluation referenceやAssurance情報を外在化する必要がある。
- 単一のbooleanへ統一するよりProjection / queryが複雑になる。
- ProviderごとのEvidence品質をProfile / Policyで評価する設計が必要になる。

## Revisit conditions

次のような不足が、複数Provider / domainで繰り返し確認された場合にUniversal Authorization Artifactを再検討する。

- Authorization evaluation自体にSOZA共通のstable logical identityが必要になる。
- Provider-specific referenceではDecision / Execution監査に必要な意味を保持できない。
- 共通のrevision / Responsibility / Assurance relationが、独立Artifactなしでは表現できない。

## Natural Japanese review

current Decision / Responsibility / Provider boundary、first semantic runtime、Provider Adapter Evidenceへ戻ってDecisionを照合した。その後、特定製品の認可実装を根拠の中心に置かず、AuthorizationをProviderへ残す理由とSOZAが保持するEvidence境界へ焦点を戻した。意味、未評価と拒否の差、Production未検証の留保を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。
