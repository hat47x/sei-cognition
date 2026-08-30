# ISSUE-000020: TEIのApplication / Database情報をSOZAから読む境界を定める

Status: **Resolved**  
Priority: **5**  
Related ADRs: **ADR-0012, ADR-0013, ADR-0014, ADR-0019**  
Updated: 2026-08-31

## Goal

SOZAがCapability discovery / matching / choiceを行う際に、TEIのApplication、Database、Environment、Release、Observation等をどの粒度で参照すべきかを定める。

TEI固有SchemaをSOZA Coreへコピーせず、Capability判断に必要な情報だけをProvider-neutralに読める境界を設計する。

## Background

TEIでは、ApplicationとDatabaseを独立対象とし、一つのApplicationが複数Databaseを利用できる。

DatabaseにはDesired / Actual / Diff / Migration / Release / Contractがあり、DeploymentではcommandとObservation / Evidenceを分離する。

SOZA側では、Capability Definition、Capability Observation、Matching、Decisionを分ける。

SOZAがTEIをCapability Providerとして扱うためには、TEI内部の詳細をすべて知らなくても、次のような判断材料を読める必要がある。

- このCapabilityは何を提供できるか。
- 現在どの条件で利用できるか。
- どのConstraintを満たすか。
- 未確認点や競合するObservationは何か。
- どのEvidenceからその解釈に至ったか。
- 実行前に追加Decision / Authorizationが必要か。

## Resolution

ADR-0019で、Provider-neutralなCapability Observation境界をAcceptedとした。

### 1. SOZAはProvider内部SchemaではなくObservation envelopeを所有する

TEIのApplication、Database、Environment、Release、Plugin Lock、Migration、Deployment等はTEI側の正本として維持する。

SOZAは、Capability判断に必要な範囲で、Capability Definition、Provider、Provider-specific context、観測時点、condition、Evidence、provenance、Unknown / Conflict / Withheld等を参照できるObservation境界を持つ。

### 2. TEI状態からCapability解釈への写像はadapter / profile境界へ置く

```text
TEI internal state
  ↓ adapter / mapping
SOZA Capability Observation
  ↓ matching / inquiry / review
Recommendation / Decision
```

TEI内部状態とSOZA上のCapability解釈を同一視しない。

### 3. `not observed`を`unavailable`へ潰さない

観測不能、非開示、競合、制約付き状態を単純な利用不能へ変換しない。

### 4. 比較用の正規化値だけを正本にしない

複数Providerを比較するためのfacetは作成できるが、raw Observation、Evidence、mapping provenanceへ戻れることを必要条件とする。

### 5. 重要なDecision basisはhistoricalに再構成可能にする

特定release、binding、Plugin Lock、mapping version等がDecisionのbasisになった場合は、必要に応じてExactArtifactBinding等で当時の入力を固定する。

### 6. Selective Disclosureを許容する

TEI内部topologyを全量開示せず、Capability判断に必要なEvidenceだけを共有できる。非開示は単純なUnknownと区別する。

### 7. Observation accessとruntime authorityを分離する

```text
Observation access != Authorization != Action Intent != Provider Execution
```

SOZAがTEIの状態を読めても、TEIを操作するAuthorityを自動取得しない。

## Required scenariosへの回答

1. **Applicationは利用可能だが依存Databaseの一つがread-only**  
   Capability全体を自動的に`unavailable`とせず、対象operation / conditionに応じてadapterが制約付きObservationへ写像する。

2. **Database migration proposalはあるが未採用**  
   proposalをactual state changedと扱わない。Desired / proposed stateとObserved stateを分ける。

3. **Application Releaseは存在するがEnvironmentへ未Binding**  
   Release存在だけから対象Environmentでのavailabilityを推定しない。

4. **Pluginは解決済みだがObservation Providerが利用不能**  
   観測gapをUnknownとして残し、解決済みPluginだけからavailabilityを確定しない。

5. **同じCapabilityをTEIとSaaSが提供する**  
   Provider-neutral Observationと共通facetを用いて比較できる。Provider kindだけで優先しない。

6. **TEIの一部構成がunknown**  
   Unknownを保持したままChoiceを保留、条件付きDecision、追加Inquiryへ進める。

7. **過去Decision時のTEI release / bindingを再構成する**  
   重要なbasisにはexact historical bindingを適用する。

8. **内部topologyをSelective DisclosureしながらEvidenceだけ共有する**  
   raw内部構造を開示せず、必要なObservation / EvidenceとWithheld contextを共有できる。

## Acceptance

- [x] TEI→SOZA Capability Observation adapter boundaryを定義した。
- [x] Provider-neutralに必要な意味項目を定義した。
- [x] exact historical binding ruleを定義した。
- [x] selective disclosure ruleを定義した。
- [x] Observation / interpretation / Decision / Authorizationを分離した。
- [x] Product ValueのV1、V2、V3、V4、V5、V7、V8と整合することを確認した。
- [x] 自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施した。

## Follow-up

actual schema、provider-neutral fixture、TEI adapter fixture、cross-provider fixtureは`ISSUE-000024`で実体化する。

## Source

- `plan/adr/ADR-0019-provider-neutral-capability-observation-boundary.md`
- `plan/kj/2026-08-31_TEI設計系列_ラウンドKJ統合.md`
- `product/value/SOZA_VALUE_MODEL.md`

## Natural Japanese review

ADR-0019とValue Modelへ戻って結論を照合した後、意味、条件、留保を変えず、自然な日本語となることを最重要視して全文を再ドラフトした。最終意味監査も実施済み。
