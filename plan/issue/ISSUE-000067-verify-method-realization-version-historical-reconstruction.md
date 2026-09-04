# ISSUE-000067: Method Realization交換時のhistorical reconstructionを検証する

Status: **Resolved**  
Priority: **1**  
Related ADRs: **ADR-0008, ADR-0009, ADR-0017, ADR-0021, ADR-0025, ADR-0026**  
Updated: 2026-09-02

## Goal

E3b-M1a / M1bで得られた実行Evidenceを入力として、**同じCognitive Method Definitionを異なるMethod Realizationで実行した履歴を、後から取り違えずに再構成できるか**を検証する。

中心となる問いは、model名やruntime名をSOZA Universal Contractへ追加すべきかではない。

```text
実行時にRealizationの違いを観測できること
  != その違いがhistorical Applicationへ残ること
  != model / runtime固有fieldをUniversal Contractへ追加する必要があること
```

current Cognitive Method ContractとSemantic Reference / Exact Bindingで必要な再構成が成立するかを先に確かめ、不足が確認された場合にだけContract / Requirementを増やす方針で検証した。

## 背景

E3b-M1aでは、固定revisionのKJ Atlasと同repositoryのdeterministic model stubを実行した。E3b-M1bでは、KJ Atlasのsource revisionとMethod surfaceを変えず、model processだけをOllama `0.32.14`上の`qwen2.5:0.5b`へ交換した。

この二つは実行条件が異なる。一方、従来の`runtime/go/livemethodintegration`はKJ Atlas source commitを手掛かりに同じlogical Realization Referenceへ戻していた。また、probe-local ProvenanceはKJ Atlas sourceとresult digestを中心に保持し、model / runtime identityをportable Application historyへ残していなかった。

そのため、実行時には差を観測できても、後からApplicationを読み直したときに実現条件の差が失われる可能性があった。

## H1 — current Contractの表現力

H1では、同じMethod Definitionと同じRealization logical identityの下に二つのExact revisionを置いた。

```text
Method Definition
  M-KJ-ATLAS-GROUPING

Method Realization logical identity
  MR-KJ-ATLAS-GROUPING

Revision A
  KJ Atlas fixed source
  + deterministic model stub Artifact

Revision B
  KJ Atlas fixed source
  + Ollama / qwen execution Artifact
```

`runtime/go/semanticruntime/method_realization_reconstruction_test.go`で、次を確認した。

1. 同じRealization logical identityに複数のExact revisionを保持できる。
2. KJ Atlas source ArtifactのExact Bindingは共有し、model execution Artifactだけを別Bindingにできる。
3. 各Applicationは、実際に使用したRealization revisionをExact Referenceで指せる。
4. 後続revisionが追加されても、過去Applicationのhistorical bindingは書き換わらない。
5. bundle Exact Reference consistencyが成立する。
6. logical-only Realization Referenceでは、複数revisionからhistorical revisionを一意に選べない。

### H1 CI

- Semantic Runtime Conformance Run `33629248978`: **success**
- Job `100244317333`: **success**
- Plan integrity Run `33629248942`: **success**

H1により、**current Method Realization + implementation refs + Exact Bindingにはhistorical revisionを区別する表現力がある**ことを確認した。

したがって、H1を理由として次は追加しない。

- model / runtime固有のUniversal Contract field
- 新しいStable Requirement / Scenario
- 全Method ApplicationへExact Bindingを要求する一律規則

## H2 — live integrationで情報を落とさない

H1でCore Contractの能力は確認できたが、M1a / M1bのlive mapping自体は同じlogical Realizationへ畳み込んでいた。H2では、実際のmappingでこの情報欠落をなくした。

### H2で採った表現

M1aとM1bは、同じRealizationの単なるartifact revisionではなく、実現機構そのものが異なる。

```text
M1a
  deterministic model stub

M1b
  Ollama runtime + actual model
```

そのため、この二つは**同じMethod Definitionを実現する別のMethod Realization**として扱う。

```text
M-KJ-ATLAS-GROUPING
  ├─ MR-KJ-ATLAS-M1A
  └─ MR-KJ-ATLAS-M1B
```

これはUniversalな命名規則ではない。current integration probeで、実現機構の違いを取り違えないためのlogical identityである。

一方、同じRealizationの内部でsource Artifactやmodel Artifactのrevisionだけが変わる場合には、H1で確認したExact Bindingを利用できる。

```text
Method Definitionの違い
  != Realizationの違い
  != 同一Realization内のhistorical revision
```

この三層を混同しない。

### H2実装

`runtime/go/livemethodintegration`へprobe-localな`ExecutionIdentity`を追加した。

保持できるのは次の情報である。

- execution profile
- runtime
- runtime version
- model
- model ID

これらはopaque Provenanceに保存し、Cognitive Method ContractのUniversal fieldへ昇格させない。

M1a workflowでは次を明示した。

- Realization: `MR-KJ-ATLAS-M1A`
- execution profile: `kj-atlas-deterministic-model-stub`
- model: `mock`

M1b workflowでは次を明示した。

- Realization: `MR-KJ-ATLAS-M1B`
- execution profile: `ollama-model-backed`
- runtime: `ollama`
- runtime version: `0.32.14`
- model: `qwen2.5:0.5b`
- model ID: `a8b0c5157701`

Applicationは対応するRealization logical referenceを保持し、Provenanceから具体的な実行条件を読み直せるようにした。

また、不完全なExecution Identityをcanonical state変更前に拒否するnegative testを追加した。実行条件を記録しようとしているのに最低限の意味が欠けた状態を、曖昧なProvenanceとして残さない。

### H2 CI

behavior-complete head `711b31cccdcd4644ab47554322455e4219f910b6`では、次を確認した。

- External Method Integration E3b Run `33630741545`: **success**
  - M1a actual KJ Atlas grouping: success
  - mapping boundary tests: success
  - `MR-KJ-ATLAS-M1A` + deterministic stub execution identityでのSOZA mapping: success
- External Model-backed Method E3b M1b Run `33630741559`: **success**
  - digest-pinned Ollama runtime install: success
  - model identity `a8b0c5157701`確認: success
  - actual inference: success
  - mapping boundary tests: success
  - `MR-KJ-ATLAS-M1B` + Ollama / qwen execution identityでのSOZA mapping: success
- Semantic Runtime Conformance Run `33630741581`: **success**
- Plan integrity Run `33630741593`: **success**
- Release Candidate Gate Run `33630741555`: **success**
  - Gate 1〜9: success
  - 公開済みv0.2.0のprepare / publish: skip

PR #56の最終head `9bb1861f7df0c2e6750895863883c12fe1a63ab6`でも9系統のworkflowがすべてsuccessし、PR #56はmerge commit `7ab1fce89879da64b2b41c34e3d4306dcc2a7e94`として`develop/v0.2.0`へ統合した。

## H1とH2の関係

H2でM1a / M1bを別Realizationとして扱うことは、H1を否定しない。

H1は、**一つのRealizationについてhistorical revisionを固定する必要が生じた場合にExact Bindingで表現できる**ことを示した。

H2は、**実現機構が異なるM1a / M1bを同じRealizationへ誤って畳み込まない**ことを示した。

```text
H2: 実現機構が違う
  → logical Realizationを分ける

H1: 同じRealizationのhistorical revisionを区別したい
  → Exact Bindingを使う
```

この二段構えで今回必要な意味を表現できたため、Universal Contract拡張は不要と判断した。

## Requirement / Scenario監査

H1 / H2の結果から、新しいStable Requirement / Scenarioは追加しない。

既存の次で今回のProduct failureと解決境界を表現できる。

- REQ-0001 — 耐久的な意味の連続性
- REQ-0004 — Methodと一つのRealizationを同一視しない
- REQ-0021 — Realization / Executionを交換可能にする
- SCN-0005 — Cognitive Methodの交換・再構成
- SCN-0015 — Method Applicationのportable reconstruction

今回の実証では、Contract fieldやRequirementを増やすより、既存Contractをintegration mappingで正しく使うことが必要だった。

## 上流計画への反映

`plan/UPSTREAM_PRODUCT_DEVELOPMENT_PLAN.md`へH1 / H2の結果を反映した。

計画上のcurrent boundaryは次のように整理した。

```text
実現機構が異なる
  → logical Realizationを分ける

同じRealizationのhistorical revisionを固定する必要がある
  → Exact Bindingを使う

model / runtime等の具体的な実行条件
  → 必要な範囲でProvenanceへ残す
```

これにより、次の探索点をhistorical reconstructionの最小境界そのものから、任意version交換、model / KJ法としての成果品質評価、E4 Operational portabilityへ移した。

## Non-goals / 停止線

- model出力品質を評価すること
- KJ法としての成果品質を評価すること
- 同じpromptから同じ生成文を再現すること
- Ollama、qwen、Git commitをUniversal identityへ固定すること
- model / runtime固有fieldをCognitive Method Contractへ追加すること
- 全ApplicationへExact Bindingを必須化すること
- production credential / distribution policyを決めること
- arbitrary model / runtime portabilityを成立させること
- E4 Operational portabilityを成立させること
- v0.2.0 supported scopeを遡及的に拡張すること

```text
H1 / H2 historical reconstruction PASS
  != arbitrary model/runtime portability
  != model quality
  != Operational Evidence
```

## 完了条件

### H1

- [x] M1a / M1bの差と従来のlive integration記録の差を整理する。
- [x] current Cognitive Method Contract / Exact Bindingで表現可能な仮説を定義する。
- [x] 同一Realization logical identityに二つのExact Binding revisionを置くprobeを実装する。
- [x] 各Applicationが対応するRealization revisionをExact Referenceで保持できることを確認する。
- [x] logical-only referenceの曖昧性をnegative controlで確認する。
- [x] bundle Exact Reference consistencyを確認する。
- [x] actual CIでH1 probeを成功させる。
- [x] H1時点ではUniversal Contract / Requirement変更をNo Changeとする。

### H2 / closure

- [x] M1a / M1bを別Realizationとして扱うcurrent mapping方針を定める。
- [x] live mappingへ明示的なRealization identityを渡す。
- [x] model / runtime等の実行条件をopaque Provenanceへ保持する。
- [x] 不完全なExecution Identityをcanonical state変更前に拒否するtestを追加する。
- [x] M1a actual workflowで新しいmappingを成功させる。
- [x] M1b actual workflowで新しいmappingを成功させる。
- [x] Plan integrity / Semantic Runtime / Release Candidate Gateを含む対象CIをsuccessさせる。
- [x] H2結果からRequirement / Contract変更の要否を再監査し、No Changeとする。
- [x] H1 / H2結果を上流計画へ同期する。
- [x] 自然な日本語を最重要視して全文を再確認し、最終意味監査を行う。

## Resolution

ISSUE-000067の問いに対して、今回の実証範囲では次の結論を得た。

1. 実現機構が異なるMethod実行は、同じMethod Definitionに属する別Realizationとして保持できる。
2. 同一Realization内でhistorical revisionを区別する必要がある場合は、既存Exact Bindingで当時のrevisionを固定できる。
3. model / runtime等の具体条件は、必要な範囲でProvenanceへ保持できる。
4. このためにUniversal Cognitive Method Contractへmodel / runtime固有fieldを追加する必要は確認されなかった。
5. 新しいStable Requirement / Scenarioも不要で、既存REQ / SCNで意味境界を保てる。

以上をactual CIで検査し、上流計画へ反映したため、本Issueを**Resolved**とする。

## Evidence state

- M1a deterministic model stub execution: **Scoped Executable Evidence available**
- M1b actual model-backed execution: **Scoped Executable Evidence available**
- H1 Core / Bundle historical reconstruction: **Scoped Executable Evidence available — Run `33629248978`**
- H2 live integration preservation: **Scoped Executable Evidence available — Runs `33630741545` / `33630741559`**
- arbitrary model / runtime version portability: **Not Yet Verified**
- E4 Operational portability: **Not Yet Verified**
- Operational Evidence: **Not Yet Verified**

## Reopen / escalation条件

次の場合は再検討する。

- Realizationを分けても過去Applicationの実行条件を十分に再構成できない。
- 同一Realization内のrevisionをExact Bindingしてもhistorical revisionを一意に復元できない。
- implementation Artifact / opaque Provenanceだけでは複数domainで重要な意味が失われる。
- live integration helperが再び異なる実現機構を同じRealizationへ畳み込む。
- version交換によって過去Decisionのbasis reconstructionが書き換わる。

## 自然な日本語レビュー

current Upstream Product Development Plan、Cognitive Method Contract、ADR-0008 / 0009 / 0017 / 0021 / 0025 / 0026、E3b-M1a / M1b Evidence、`runtime/go/livemethodintegration`、H1 probe、H2 actual workflow結果、PR #56の最終CIを照合した。

H1で確認した「同一Realization内のhistorical revision」と、H2で扱った「実現機構そのものが異なるRealization」を分けて整理した。M1a / M1bの違いをmodel / runtime固有のUniversal fieldへ持ち込まず、logical Realizationとopaque Provenanceで保持する。一方、同じRealization内のrevisionを固定する必要がある場合にはExact Bindingを利用できる。

上流計画へ成立範囲と未検証範囲を同期し、次の探索点を任意version交換、品質評価、E4へ移した。意味、規範強度、Evidence強度を引き上げず、自然な日本語として一続きに読めることを最重要視して全文を再ドラフトし、最終意味監査を実施した。
