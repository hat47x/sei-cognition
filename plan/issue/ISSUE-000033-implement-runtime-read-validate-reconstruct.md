# ISSUE-000033: read / validate / reconstruct runtime sliceを実装する

Status: **Resolved**  
Priority: **1**  
Related ADRs: **ADR-0021, ADR-0022, ADR-0023**  
Updated: 2026-08-31

## Goal

ADR-0022で確定したfirst runtime sliceをGoでactual repositoryへ実装し、current Contract fixtureをruntimeへ読み込むend-to-end conformanceを構築する。

外部Action実行を先行せず、Semantic Interchange、Decision Memory、Capability Observation、Semantic Referenceの読み込み・意味検査・historical reconstructionを、SOZA current baselineで最初のExecutable runtime Evidenceとする。

## Resolution

### 1. Go semantic runtimeをactual treeへ実体化した

主な実装は次に置いた。

```text
runtime/go/
  go.mod
  semanticruntime/
    model.go
    loader.go
    loader_test.go
```

runtime packageはArchitecture concernの恒久identityではない。現在の実装配置としてのみ扱う。

### 2. current Contract identity / versionを読み分ける

runtimeは少なくとも次のcurrent Contractを明示的に扱う。

- `soza.semantic-reference/v1alpha1`
- `soza.decision-memory/v1alpha1`
- `soza.capability-observation/v1alpha1`
- `soza.semantic-interchange/v1alpha1`

未知のnested Contractを既知Contractとして解釈せず、`not_verified`相当としてopaque payloadを保持する。

```text
unknown Contract != invalid known Contract
unknown Contract != fully validated
```

### 3. Semantic Reference境界をruntimeで検査する

次を実装した。

- Logical Reference
- Exact Binding metadata
- Representation Profile identity / version
- Verification Outcome vocabulary
- Semantic Lineage
- same-logical-id lineageのexact endpoint要求

`verified / failed / not_verified`を別状態として扱い、未知Verifierや未検証状態を`failed`へ潰さない。

### 4. Decision Memory境界をruntimeで検査する

DecisionとRecommendationを分け、次を保持する。

- context refs
- basis refs
- recommendation refs
- unresolved refs
- responsibility refs
- rationale
- lineage

Decision recordへ`authority`を直接持ち込むfixtureは拒否する。

```text
Recommendation != Decision
Decision != Authority
Decision creation != uncertainty resolution
```

### 5. Capability Observation境界をruntimeで検査する

F1〜F7 fixtureをcurrent runtimeへ接続した。

- F1 TEI partial degradation
- F2 proposed state != actual state
- F3 release without environment binding
- F4 observation gap
- F5 cross-provider comparison
- F6 historical reconstruction
- F7 selective disclosure

F5/F6は複数recordを持つSemantic Interchangeであるため、単一Capability Observationとしてではなくbundleとして読み込む。

Provider-specific contextをCapability meaningそのものへ昇格させず、`observed_at`、condition、provenance、mapping provenance等を保持する。

### 6. bundle内のhistorical exact reference整合を検査する

Decision basisがbundle内のexact-bound Artifactを参照する場合、同じlogical identityで異なるexact contentへ黙って向け直されないことを検査する。

mismatched exact binding fixtureは期待どおり拒否される。

### 7. partial knowledgeを保持する

`unknown`と`withheld`を保持したCapability Observationと、未解決参照を残したDecisionを同じInterchangeから読み込める。

```text
unknown != false
withheld != unknown
Decision != uncertainty resolved
```

### 8. original interchange bytesをlosslessに再exportできる

read / validateの成功を理由に、受信したSemantic Interchangeを自動normalize / rewriteしない。

`Bundle.ExportOriginal()`は元bytesの独立copyを返し、runtime read model化によって元交換representationを失わない。

これはsemantic migration機構の完成を意味しない。最初のread / validate / reconstruct sliceにおけるlossless handling Evidenceである。

### 9. Contract checkerとruntime testを同じfixture sourceへ接続した

`.github/workflows/runtime-conformance.yml`を追加し、次を一つのCI jobで実行する。

1. Contract checker dependencyを導入する。
2. `tools/check_contract_conformance.py`でcurrent fixtureを再検査する。
3. `runtime/go`で`go test ./...`を実行する。

初回CIではchecker dependency導入漏れを検出し修正した。

2回目CIではF5/F6がSemantic Interchangeであるにもかかわらず、runtime testが全F1〜F7を`LoadStandalone`で読んでいた問題を検出した。fixtureのtop-level Contractを確認し、Capability ObservationとSemantic Interchangeでloaderを分けるよう修正した。

### 10. actual branch CIでPASSした

最終確認:

- branch: `develop/v0.1.0`
- commit: `834c3f2a8bd911829743c1582ef09f098c776a54`
- workflow: `Semantic Runtime Conformance`
- run: `#3` / `33348972805`
- conclusion: **success**

CI上で次の両方が成功した。

- current Contract fixture checker: **PASS**
- Go semantic runtime tests: **PASS**

Contract checkerでは17 fixtureすべてが期待結果と一致した。F1〜F7のpositive fixture、Schema fail、semantic fail、unknown Contractの`not_verified`、Verification Outcome境界を含む。

## Acceptance

### Executable Acceptance

- [x] `runtime/go`がactual treeに存在する。
- [x] Go moduleがcompile / testできる。
- [x] Semantic Interchange v1alpha1を読み込める。
- [x] F1〜F7をruntime read modelへ読み込める。
- [x] Recommendation without Decisionを正常に扱える。
- [x] Decision with unresolved stateを正常に扱える。
- [x] partial-knowledge interchangeを正常に扱える。
- [x] same-logical-id lineage without exact endpointを拒否できる。
- [x] mismatched exact bindingを拒否できる。
- [x] unknown nested Contractを`not_verified`相当として扱える。
- [x] original semantic interchange bytesを意味を変えず再exportできる。
- [x] Runtime CIをactual branchで再現できる。
- [x] Contract checkerとruntime testを同じfixture sourceへ接続できる。

## Evidence boundary at closure

本Issueで得られたEvidenceは、**current Contract fixtureを入力とするfirst semantic runtime sliceのExecutable Evidence**である。

```text
runtime CI PASS
  != all SOZA runtime requirements complete
  != Provider production integration
  != Authorization / Action execution complete
  != release readiness
  != operational evidence
```

Representation Profileのfixture-scoped Executable EvidenceはADR-0023 / ISSUE-000009で別途成立している。current runtimeへProduction-grade Verifier Registry / Adapterを完全統合したことまでは本Issueから主張しない。

## Follow-up

- ISSUE-000022 — repository baseline全体のclosure監査
- ISSUE-000034 — historical M47 digest profile recovery
- Production Runtime verifier integrationは、必要性をcurrent Scenario / Requirementから確認したうえで独立Issueへ切り出す。
- Provider / TEI integrationはCapability Observation Contractとruntime境界を壊さず、後続vertical sliceで扱う。

## CI handling rule applied

開発中にCI failureを検出した場合、その時点で原因を特定し、意味設計を安易に弱めずに修正し、成功を確認してから次の作業へ進む。

今回もdependency導入漏れとfixture loader種別誤りを順に解消し、run #3のsuccessを確認してから本Issueを閉じた。

## Natural Japanese review

実装、fixture、CIログ、Acceptanceを実際の到達状態へ戻して照合した後、過大な達成主張を避けつつ、意味、規範強度、Evidence境界を変えないように全文を再構成した。そのうえで、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
