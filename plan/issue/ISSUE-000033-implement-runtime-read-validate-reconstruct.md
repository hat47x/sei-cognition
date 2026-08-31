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

```text
runtime/go/
  go.mod
  semanticruntime/
    model.go
    loader.go
    loader_test.go
```

runtime packageはArchitecture concernの恒久identityではなく、current implementation配置として扱う。

### 2. current Contract identity / versionを読み分ける

Semantic Reference、Decision Memory、Capability Observation、Semantic Interchangeのcurrent v1alpha1を明示的に扱い、未知のnested Contractは既知Contractとして解釈せず`not_verified`相当としてopaque payloadを保持する。

### 3. Semantic Reference / Decision Memory / Capability Observation境界をruntimeで検査する

Logical Reference、Exact Binding metadata、Verification Outcome vocabulary、Semantic Lineage、Decision / Recommendation、context / basis / unresolved / responsibility、Capability Observation等をcurrent Contractに沿って読み込む。

```text
Recommendation != Decision
Decision != Authority
Decision creation != uncertainty resolution
unknown Contract != fully validated
```

### 4. F1〜F7とnegative / boundary fixtureをruntimeへ接続した

F1〜F7を同じContract fixture sourceから読み込み、Recommendation without Decision、Decision with unresolved、same-logical-id lineage violation、mismatched exact binding、unknown Contract、partial knowledge等も検査する。

F5 / F6は複数recordを持つSemantic Interchangeとして読み込む。

### 5. original interchange bytesをlosslessに再exportできる

read / validate成功を理由に受信Interchangeを自動normalize / rewriteせず、`Bundle.ExportOriginal()`で元bytesの独立copyを返す。

これはsemantic migration機構の完成ではなく、first sliceにおけるlossless handling Evidenceである。

### 6. Contract checkerとruntime testを同じfixture sourceへ接続した

`.github/workflows/runtime-conformance.yml`でContract checkerと`go test ./...`を同じCI jobから実行する。

初回にはchecker dependency導入漏れ、次のrunではF5/F6のfixture種別誤認をCIで検出し、原因を修正してからsuccessを確認した。

### 7. actual branch CIでPASSした

- workflow: `Semantic Runtime Conformance`
- Run ID: `33348972805`
- conclusion: **success**

Contract checkerでは17 fixtureすべてが期待結果と一致し、Go semantic runtime testsもPASSした。

## Acceptance

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
- [x] original Semantic Interchange bytesを再exportできる。
- [x] Runtime CIをactual branchで再現できる。
- [x] Contract checkerとruntime testを同じfixture sourceへ接続できる。

## Current evidence boundary

```text
runtime CI PASS
  != all SOZA runtime requirements complete
  != Provider production integration
  != Authorization / Action execution complete
  != release readiness
  != Operational Evidence
```

Representation Profile fixture-scoped EvidenceはADR-0023 / ISSUE-000009で別途成立している。current runtimeへProduction-grade Verifier Registry / Adapterを完全統合したことまでは本Issueから主張しない。

その後ISSUE-000036でsynthetic Provider Adapterを同じruntime conformanceへ追加し、Provider-specific state → Capability Observationの最小mapping sliceまでcurrent CIで確認した。この後続Evidenceもproduction Provider integrationとは区別する。

## Follow-up

- ISSUE-000022 — repository baseline（Resolved）
- ISSUE-000036 — synthetic Provider Adapter（Resolved）
- ISSUE-000034 — historical M47 digest Profile recovery（Blocked）
- Production Runtime verifier integrationは必要性をcurrent Scenario / Requirementから確認したうえで独立Issueへ切り出す。
- production Provider integrationも対象ProviderとAcceptanceを定めて独立Issueで扱う。

## CI handling rule applied

CI failureを検出した場合、その時点で原因を特定し、意味設計を安易に弱めずに修正し、successを確認してから次の作業へ進む。

本Issueでもdependency導入漏れとfixture loader種別誤りを順に解消し、run `33348972805`のsuccessを確認してから閉じた。

## Natural Japanese review

実装、fixture、CIログ、後続Provider Adapter Evidenceへ戻ってAcceptanceを照合した。その後、first runtimeのExecutable Evidenceと未検証のProduction / Release / Operational領域を分離し、意味、規範強度、Evidence境界を変えないよう自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。
