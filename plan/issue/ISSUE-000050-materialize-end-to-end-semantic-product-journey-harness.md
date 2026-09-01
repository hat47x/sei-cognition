# ISSUE-000050: end-to-end Semantic Product Journey harnessを実体化する

Status: **Open**  
Priority: **1**  
Related ADRs: **ADR-0005, ADR-0008, ADR-0009, ADR-0018, ADR-0020, ADR-0021, ADR-0022, ADR-0025**  
Updated: 2026-09-01

## Goal

SCN-0018「Inquiryから実行後の再検討までを一続きに扱う」について、個別Contract / runtime / Provider AdapterのPASSを足し合わせるのではなく、**一つのsemantic Product Journeyとして実際に接続して検査できるExecutable harness**をactual repositoryへ実体化する。

最初のharnessではproduction UIやproduction execution engineを必須にしない。Canonical Semantic Access Surfaceに相当するfixture / adapter / CLI / test harness等から、耐久的な意味が一続きに再構成できることを検査する。

## Why now

Product ShapeとREQ-0001〜REQ-0022のcomposition analysisにより、新しいUniversal Requirementを増やすより、既存の意味要求をend-to-endで同時に検査することが不足していると分かった。

SCN-0018では、とくに次の境界を統合している。

```text
Inquiry
  → Observation / Evidence / Unknown / Conflict
  → Cognitive Method Application
  → Recommendation
  → Decision / Responsibility
  → external Capability / Execution
  → resulting Observation
  → historical review / reopen
```

current repositoryには各段階の一部を支えるscoped Executable Evidenceがあるが、この連鎖全体を一つの検査経路として確認したEvidenceはまだない。

## Dependency

ISSUE-000043のCognitive Method Contract / runtime sliceと強く関係する。

ただし、ISSUE-000050をISSUE-000043の全面完了へ機械的にblockしない。SCN-0018のharnessに必要なCognitive Method read / validate / reconstruct能力がactual branchに成立した時点で統合を進められる。

## Scope

### 1. canonical journey fixture

少なくとも一つの代表的なjourneyについて、次をstable Referenceで接続する。

- Inquiryまたは等価なQuestion / context Artifact
- Observation / Evidence
- Unknown / Conflict / residual
- Cognitive Method Definition / Realization / Application
- Recommendation
- Decision
- Responsibility / Authorityに必要なcontextual reference
- Capability / Provider selectionに必要なObservation
- external executionを表すreference / receipt相当のArtifact
- execution後に得た新しいObservation
- historical review / reopenへ必要なReference

既存Contractで表現できない部分を見つけた場合、harness都合だけでUniversal fieldを追加しない。既存Artifact Reference / Extension / external Artifact等で表せるかを先に確認し、本当に意味上の不足がある場合だけIssue / ADRへ戻る。

### 2. required variants

#### normal

必要なEvidenceが集まり、Decision後に外部実行まで進む。

#### uncertain

Unknown / Conflictを残したままDecisionし、後日得たObservationからreview / Inquiryを再開する。

#### collaborative

AIがCognitive Method Application / Recommendationを担い、人間または明示的に委任された主体がDecisionする。actor種別だけからAuthorityを推定しない。

#### provider replacement

後続実行では別Providerを利用するが、以前のDecision identityとbasisはProvider固有run IDに依存せず再構成できる。

#### no execution

Decisionまでで終了し、external executionがなくてもDecision recordとhistorical valueが成立する。

### 3. temporal integrity

execution後に得たObservationを、過去Decision作成時のbasisへ混入させない。

```text
observation acquired after D1
  != evidence known when D1 was made
```

D1をhistoricalに再構成したときは当時のbasisを読み、新Observationは後続review / D2等へ接続する。

### 4. provider / projection independence

- Provider固有run IDをDecisionのcanonical identityにしない。
- Provider交換後もhistorical Decisionを読める。
- Projectionをcanonical authorityにしない。
- current UIやProjectionがなくてもcanonical recordから必要な意味を再構成できる。

### 5. unknown version handling

Journey内にunsupported Contract versionが含まれる場合は、known current versionとして誤解釈しない。

Semantic Interchange等のcurrent boundaryに従い、可能な範囲でopaque + `not_verified`として保持する。

## Minimal executable checks

少なくとも次をactual testで検査する。

1. journey内の各Artifact / recordをstable Referenceで辿れる。
2. Decisionから当時のbasisへ戻れる。
3. DecisionからCognitive Method Application、Responsibility、residualへ戻れる。
4. execution resultを新しいObservationとして接続できる。
5. execution後Observationが過去Decision basisへ時間逆行して混入しない。
6. new Observationからreview / reopenの次のcontextへ接続できる。
7. Provider交換後もhistorical Decisionを再構成できる。
8. no-execution variantでもDecisionが成立する。
9. RecommendationをDecisionへ自動昇格しない。
10. Execution successをDecision correctness / Business Outcome successへ自動昇格しない。
11. unsupported versionをknown versionとして扱わない。
12. Projectionだけをcanonical sourceとして利用しない。

## Negative cases

少なくとも次を明示的にFAILさせるか、semantic violationとして検出する。

- AI RecommendationをDecisionとして同一record / roleへ潰す。
- Decision作成と同時にUnknown / Conflictを自動resolvedへ変える。
- Provider run IDをDecision identityとしてのみ保存する。
- execution successからDecisionを`verified`へ昇格する。
- 後から得たObservationでD1のhistorical basisを上書きする。
- Provider交換時に以前のDecision referenceが解決不能になる。
- no-execution pathを不正な未完了Decisionとして拒否する。
- unsupported Contract versionをcurrent versionへ黙ってcoerceする。

## Non-goals

- production UI完成
- production workflow / agent execution engine
- external Providerの本番接続
- Product Identity / Authorization / Collaboration全体の実装
- Storage migrationの全面実証
- operational SLAの検証
- human usabilityの実証
- Adoption / Outcomeの実証

これらはISSUE-000045〜000047や後続Release / Operational / Outcome課題へ分離する。

## Acceptance criteria

### Design

- [x] SCN-0018がcurrent Acceptance Scenarioとして定義されている。
- [x] Requirement composition上、新しいUniversal Requirementが現時点では不要と整理されている。
- [ ] harnessのArtifact graph / fixture structureを定義する。
- [ ] current Contractで表現できない箇所を洗い出し、Extension / Reference等で扱えるか監査する。

### Executable

- [ ] normal variantがactual testでPASSする。
- [ ] uncertain variantがactual testでPASSする。
- [ ] collaborative variantがactual testでPASSする。
- [ ] provider replacement variantがactual testでPASSする。
- [ ] no-execution variantがactual testでPASSする。
- [ ] temporal integrity negative caseがFAILする。
- [ ] Recommendation / Decisionの自動昇格negative caseがFAILする。
- [ ] Provider identity依存negative caseがFAILする。
- [ ] unsupported version boundaryを検査できる。
- [ ] `go test ./...`および関連Contract / Requirements / Plan CIがsuccessする。

### Evidence update

- [ ] SCN-0018のExecutable Evidenceをactual harnessで確認できた範囲だけ更新する。
- [ ] 関連REQのExecutable Evidenceを過大主張せず再評価する。
- [ ] Product Value Traceabilityへend-to-end harnessのscopeを反映する。
- [ ] component-level PASSとProduct Journey PASSの差をEvidence文書へ残す。

### Higher evidence

- Release Evidence: **Not Yet Verified**
- Operational Evidence: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

本IssueをResolvedにしても、これらを自動的にSatisfiedへ上げない。

## Implementation order

1. current Contract / runtime / Cognitive Method sliceのactual状態を再確認する。
2. Product JourneyのArtifact graphとfixture identityを定める。
3. normal / uncertain / no-executionを先に作る。
4. collaborative / provider replacementを追加する。
5. temporal integrityとsemantic promotionのnegative caseを追加する。
6. harnessをCIへ接続する。
7. Requirement / Scenario / Value TraceabilityのEvidenceを更新する。
8. 追加・更新文書を自然な日本語へ全文再ドラフトし、最終意味監査する。
9. 対象CIがすべてsuccessすることを確認する。

CI failureを検出した場合は、その原因を解消してsuccessを確認してから後続作業へ進む。

## Evidence state

- Design Evidence: **Partially Satisfied** — SCN-0018と最小検査条件は定義済み。harness構造は未確定。
- Executable Evidence: **Not Yet Verified for SCN-0018 end-to-end**
- Release Evidence: **Not Yet Verified**
- Operational Evidence: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

## Natural Japanese review

Product Shape、`PRODUCT_JOURNEY_COMPOSITION.md`、SCN-0018、REQ-0001〜REQ-0022、current Semantic Reference / Decision Memory / Capability Observation / Semantic Interchange / Cognitive Method Contract、first runtime、synthetic Provider Adapterへ戻り、component-level Evidenceとend-to-end Evidenceを混同しない実装課題として整理した。Product JourneyのためだけにUniversal fieldを増やさず、まず既存Reference / Extension / external Artifactで表現できるかを確認する境界を置いた。その後、実装順序、negative case、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。
