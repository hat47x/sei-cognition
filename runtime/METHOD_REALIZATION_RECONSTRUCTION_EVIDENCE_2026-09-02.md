# Method Realization Historical Reconstruction Evidence — 2026-09-02

状態: **Scoped Executable Evidence available for H1**  
対象: **ISSUE-000067 / Method Realization revision historical reconstruction probe**

## 1. この文書の役割

この文書は、E3b-M1a / M1bで実際に観測したRealization差を入力として、current Cognitive Method ContractとSemantic Reference / Exact Bindingだけで、**交換前後のMethod Realizationを過去のApplicationから取り違えずに辿れるか**を検査したH1 probeのEvidenceを記録します。

H1はactual modelをもう一度呼ぶ試験ではありません。M1a / M1bで既に成立した実行identityを用いて、portable historical reconstructionの表現力を検査するsemantic runtime probeです。

```text
actual M1a / M1b execution Evidence
  → H1 historical reconstruction probe
  != new actual model version exchange
  != E4 Operational portability
```

## 2. 出発点となった不足

current `runtime/go/livemethodintegration`では、KJ Atlasのsource commitを基準にRealization logical refを作っています。

M1aとM1bは次が共通です。

- KJ Atlas repository: `hat47x/kj-atlas`
- KJ Atlas commit: `4f28c13abe4176503c6fed863383a2d1db2299e9`
- Method surface: `POST /ai/suggest-card-groups`

一方、model executionは異なります。

### M1a

- KJ Atlas repository同梱deterministic model stub
- representative current-baseline Run: `33587455439`

### M1b

- Ollama `0.32.14`
- `qwen2.5:0.5b`
- observed model ID: `a8b0c5157701`
- representative post-merge Run: `33609470323`

実行時にはこの差を観測できていますが、current live integration helperがApplicationへ保持するRealization Referenceはlogical-onlyです。また、probe-local ProvenanceはKJ Atlas sourceとresult digestを中心に保持しており、model / runtime identityをportable Method Applicationの意味として直接表してはいません。

したがって、次を分けて検査する必要がありました。

```text
実行Evidenceに差がある
  != portable Application historyから差を再構成できる
```

## 3. H1の仮説

current Cognitive Method Contractはすでに、次の二つを許しています。

- `MethodRealization.implementation_refs`にExact Referenceを置く。
- `MethodApplication.realization_ref`にExact Referenceを置く。

そこでH1では、同じMethod Definitionと同じRealization logical identityの下に、二つのExact revisionを置きました。

```text
Method Definition
  M-KJ-ATLAS-GROUPING

Method Realization logical identity
  MR-KJ-ATLAS-GROUPING

Revision A
  KJ Atlas fixed source Exact Binding
  + deterministic model stub Artifact Exact Binding

Revision B
  KJ Atlas fixed source Exact Binding
  + Ollama / qwen execution Artifact Exact Binding
```

model / runtimeの具体情報は、probe-localなimplementation Artifact payloadに置きます。Cognitive Method Contractへ`model`や`runtime`のUniversal fieldを追加しません。

## 4. 実装したprobe

実装:

- `runtime/go/semanticruntime/method_realization_reconstruction_test.go`

H1では次を検査します。

1. 二つのMethod Realization revisionが同じLogical Referenceを共有できる。
2. Realization自身のExact Bindingはrevisionごとに異なる。
3. KJ Atlas source ArtifactのExact Bindingは両revisionで共有できる。
4. model execution ArtifactのExact Bindingだけをrevisionごとに変えられる。
5. M1a相当ApplicationはRevision A、M1b相当ApplicationはRevision BをExact Referenceで指せる。
6. bundle Exact Reference consistencyが成立する。
7. 後続Revision Bの存在によって、過去Application AのExact Bindingが書き換わらない。
8. logical-only Realization Referenceでは候補が二つになり、historical revisionを一意に選べない。

## 5. actual CI結果

PR #56のbehavior headでSemantic Runtime Conformanceを実行しました。

- Workflow: `Semantic Runtime Conformance`
- Run: `33629248978`
- Job: `100244317333`
- Result: **success**

同runではcurrent Contract fixturesを再検査した後、semantic runtimeとProvider adaptersを含むGo test群がsuccessしました。H1 probeもこのtest群に含まれています。

Plan integrity Run `33629248942`もsuccessし、ISSUE-000067とPlan Registryの整合が確認されています。

## 6. H1から言えること

H1の範囲では、**新しいUniversal model / runtime fieldを追加しなくても、current Method Realization + implementation refs + Exact Bindingでhistorical revisionを区別できる**ことが確認できました。

```text
Method identity
  != Realization logical identity
  != Realization exact revision
  != implementation Artifact identity
```

特定model名やruntime名はimplementation Artifactの内容として外在化でき、Method Applicationはその内容を直接理解しなくても、Realization revisionのExact Bindingを通して当時の実現条件へ辿れます。

したがって、H1だけを根拠にCognitive Method Contractへmodel / runtime固有fieldを追加する必要はありません。

## 7. negative controlが示したこと

logical-only referenceでは、同じRealization logical identityに二つのrevisionが存在すると候補が二つになります。

```text
logical Realization ref
  → current identityは分かる
  → historical revisionは一意に決まらない
```

一方、ApplicationがExact Realization Referenceを保持していれば、当時のrevisionを一意に選べます。

これは「すべてのApplicationにExact Bindingが必要」という意味ではありません。historical reconstructionでrevision差が重要なApplicationにだけ、必要な明示性を適用するというcurrent Contractの方針と整合します。

## 8. H1ではまだ解決していないこと

H1はCore Contract / Bundle表現力を確認したprobeです。current live integration mappingがこの表現力を実際に使えていることまでは確認していません。

特に次が残ります。

- `runtime/go/livemethodintegration`はcurrent Applicationへlogical-only Realization Referenceを渡している。
- `interactionprobe.CanonicalStore`はlogical identity単位でrecordを一意に扱い、同一logical identityの複数Exact revisionを同一storeへ保持する用途には設計されていない。
- M1a / M1bを「別Realization identity」として表す方が自然か、「同一Realizationのrevision」として表す方が自然かは、live mappingの責務と利用Scenarioを踏まえて決める必要がある。
- actual model / runtimeをさらに交換した場合のportable historyは未検証である。

したがって、ISSUE-000067はH1 successだけではResolvedにしません。

## 9. 次のH2

H2では、current live integration mappingで実行条件の差をportable Application historyへ残す最小方式を比較します。

候補は少なくとも次です。

### A. 異なるMethod Realization logical identityとして扱う

M1aとM1bを別Realizationとして記録し、両方を同じMethod Definitionへ結びます。

これは「model execution方式が異なるなら別Realizationである」という単純な表現です。

### B. 同じRealization logical identityのExact revisionとして扱う

H1と同様にRealization logical identityを共有し、implementation Artifactの違いをExact revisionとして表します。

これは同じRealization configurationのversion更新等に適する可能性があります。

H2では、どちらをUniversal ruleにするかを先に決めません。実際の履歴再構成で必要な意味差を比較し、live integration helperが情報を落とさない最小境界を選びます。

## 10. Requirement / Contract監査

H1ではcurrent Contractだけで必要な表現が成立しました。そのため、現時点では新しいStable RequirementもContract fieldも追加しません。

既存の次で引き続き扱います。

- REQ-0001 — 耐久的な意味の連続性
- REQ-0004 — Methodと一つのRealizationを同一視しない
- REQ-0021 — Realization / Executionを交換可能にする
- SCN-0005 — Cognitive Methodの交換・再構成
- SCN-0015 — Method Applicationのportable reconstruction

H2でlive mappingへ落としたときにcurrent Contractでは表せないProduct failureが現れた場合にだけ、Candidate Requirementを検討します。

## 11. Evidence state

- M1a deterministic model stub execution: **Scoped Executable Evidence available**
- M1b actual model-backed execution: **Scoped Executable Evidence available**
- H1 Core / Bundle historical reconstruction: **Scoped Executable Evidence available in Run 33629248978**
- live integration preservation of Realization execution identity: **Not Yet Verified**
- arbitrary model / runtime version portability: **Not Yet Verified**
- E4 Operational portability: **Not Yet Verified**
- Operational Evidence: **Not Yet Verified**

## 12. v0.2.0との関係

H1はrelease後のScoped Executable Evidenceです。

```text
H1 historical reconstruction PASS
  != v0.2.0 supported scope expanded
  != v0.2.0 Release Evidence expanded
```

公開済みv0.2.0でsupportを主張するRealization / Provider exchange範囲はE3aまでのままです。

## 13. 自然な日本語レビュー

ISSUE-000067、current Cognitive Method Contract、ADR-0008 / 0009 / 0017 / 0021 / 0025 / 0026、Semantic RuntimeのExact Reference consistency、E3b-M1a / M1b Evidence、current live integration helper、H1 probe、Run `33629248978`を照合しました。

H1が確認したのはCore Contract / Bundleの表現力であり、current live integrationやOperational portabilityまで成立したとは扱っていません。また、model / runtime固有fieldをUniversal Contractへ追加せず、implementation ArtifactのExact Bindingとして保持できることと、すべてのApplicationへExact Bindingを強制しないことを両立させています。

意味、規範強度、未検証範囲、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施しました。