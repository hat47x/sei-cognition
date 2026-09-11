# ISSUE-000024: Capability Observation境界をschemaとfixtureで実体化する

Status: **Resolved**  
Priority: **2**  
Related ADRs: **ADR-0006, ADR-0008, ADR-0012, ADR-0013, ADR-0014, ADR-0019**  
Updated: 2026-08-31

## Goal

ADR-0019で確定したProvider-neutralなCapability Observation境界を、actual repositoryで検証できるContract、schema、fixture、semantic validatorへ落とす。

意味境界を先に固定した状態を保ち、TEI固有Schemaや一時的な実装都合からUniversal Coreを逆算しない。

## Resolution

### 1. Capability Observation Contractを実体化した

次をcurrent Contractとして実体化した。

- `contracts/capability/SEI_CAPABILITY_OBSERVATION_v1alpha1.md`
- `contracts/schemas/v1alpha1/capability-observation.schema.json`

Contractでは次を分離している。

```text
Capability Definition
  != Capability Observation
  != Matching
  != Choice Decision
  != Provider Selection
  != Authority
  != Execution
```

Provider internal stateをSEI Universal Coreへ直接コピーせず、Provider-specific target referenceとmapping / adapter provenanceを保持できる。

### 2. F1〜F7をactual fixtureとして実体化した

`fixtures/contracts/v1alpha1/capability/`へ、TEI partial degradation、proposed state / actual state、Environment binding、Observation gap、cross-provider comparison、historical reconstruction、selective disclosureを扱うF1〜F7を追加した。

Value Axisとの対応はfixture READMEへ明示している。

### 3. Provider-neutralityを維持した

F5ではTEIとSaaSを同じCapabilityに対する異質なProviderとして同一Semantic Interchangeへ入れた。

一方、TEIのrelease情報やSaaSのservice plan等はProvider固有contextとして保持し、Universal Capability Observation fieldへ無理に平坦化していない。

Universal suitability scoreやProvider kindによる優先順位も要求していない。

### 4. Unknown / Conflict / Withheld境界を保持した

```text
not observed != unavailable
Unknown != incompatible
withheld != false
```

F7では、内部topologyの存在は示されているが内容が非開示という状態を`withheld`として保持した。

### 5. mapping provenanceとhistorical reconstructionを実体化した

F6では、Decisionが利用したCapability Observationとadapter mappingをExact Bindingで特定した。

current releaseやcurrent mappingへ黙って追随せず、Decision時点のObservation / mappingを復元する構造になっている。

### 6. actual repository上でExecutable Evidenceを取得した

GitHub Actions `Contract Conformance` Run ID `33346472419`で17 fixtureが期待結果どおりに分類され、Capability F1〜F7もexpected PASSとなった。

詳細は`contracts/CONFORMANCE_EVIDENCE_2026-08-31.md`を正とする。

その後、ISSUE-000033で同じF1〜F7をfirst semantic runtimeへ接続し、ISSUE-000036では異なるsynthetic Provider inputをCapability Observationへ変換するAdapter sliceまで実装した。

```text
Contract fixture PASS
  → first runtime read / validate / reconstruct
  → synthetic Provider Adapter mapping
```

ただし、これらをproduction Provider interoperabilityへ昇格させない。

## Acceptance criteria

- [x] ADR-0019の意味境界をContract / schemaで表現できる。
- [x] TEI固有型がSEI Universal Coreへ漏れていない。
- [x] F1〜F7のfixtureが存在する。
- [x] fixtureごとにV1〜V8との関係を説明できる。
- [x] normalized / interpreted conditionからprovenanceまたはProvider-specific referenceへ戻れる。
- [x] historical reconstructionが現在版への追随ではなく当時版の復元になっている。
- [x] actual repository上で再現可能なContract conformanceを得た。
- [x] first runtimeでもF1〜F7を読み込める。
- [x] synthetic Provider Adapterをcurrent Capability Observation validationへ接続した。
- [x] 文書・fixture説明を自然な日本語で再ドラフトし、最終意味監査を行った。

## Current evidence state

- Capability Observation Design: **Satisfied**
- Capability Observation fixture-scoped Executable Evidence: **Satisfied**
- current Representation Profile baseline: **Satisfied — ADR-0023 / ISSUE-000009**
- first runtime conformance: **Satisfied within ISSUE-000033 scope**
- synthetic Provider Adapter: **Satisfied within ISSUE-000036 scope**
- actual multi-Provider production adapter interoperability: **Not Yet Verified**
- Release / Operational Evidence: **Not Yet Verified**

本IssueのResolvedはCapability Observation境界とF1〜F7のcurrent conformanceを意味する。production Provider接続やSEI全体のrelease readinessを意味しない。

## Follow-up

- ISSUE-000009 — current Representation Profile（Resolved）
- ISSUE-000031 — Contract conformance（Resolved）
- ISSUE-000033 — first semantic runtime（Resolved）
- ISSUE-000036 — synthetic Provider Adapter（Resolved）
- ISSUE-000034 — historical M47 digest Profile recovery（Blocked）
- production Provider adapterは具体的なProvider / Acceptanceが定まった時点で独立Issueとして扱う。

## Natural Japanese review

F1〜F7、Capability Observation Contract / Schema、Contract CI、first runtime、synthetic Provider Adapterのcurrent Evidenceへ戻って再照合した。fixture-scoped / runtime-scoped Executable Evidenceと未検証のproduction / Release / Operational領域を分離した後、意味、条件、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。
