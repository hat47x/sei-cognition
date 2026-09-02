# ISSUE-000067: Method Realization交換時のhistorical reconstructionを検証する

Status: **Open**  
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

まずcurrent Cognitive Method ContractとSemantic Reference / Exact Bindingで必要な再構成が成立するかを確かめ、不足が確認された場合にだけContract / Requirementの追加を検討する。

## 背景

E3b-M1aでは、固定revisionのKJ Atlasと同repositoryのdeterministic model stubを実行した。E3b-M1bでは、KJ Atlasのsource revisionとMethod surfaceを変えず、model processだけをOllama `0.32.14`上の`qwen2.5:0.5b`へ交換した。

この二つは実行条件が異なる。一方、従来の`runtime/go/livemethodintegration`はKJ Atlas source commitを手掛かりに同じlogical Realization Referenceへ戻していた。また、probe-local ProvenanceはKJ Atlas sourceとresult digestを中心に保持し、model / runtime identityをportable Application historyへ残していなかった。

そのため、実行時には差を観測できても、後からApplicationだけを読むと実現条件の差が失われる可能性があった。

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

`runtime/go/semanticruntime/method_realization_reconstruction_test.go`で次を確認した。

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

H1から、**current Method Realization + implementation refs + Exact Bindingにはhistorical revisionを区別する表現力がある**ことが確認できた。

したがって、H1を理由として次は追加しない。

- model / runtime固有のUniversal Contract field
- 新しいStable Requirement / Scenario
- 全Method ApplicationへExact Bindingを要求する一律規則

## H2 — live integrationで情報を落とさない

H1でCore Contractの能力は確認できたが、M1a / M1bのlive mapping自体は同じlogical Realizationへ畳み込んでいた。H2では、実際のmappingでこの情報欠落をなくす。

### H2で採る表現

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

M1a workflowでは次を明示する。

- Realization: `MR-KJ-ATLAS-M1A`
- execution profile: `kj-atlas-deterministic-model-stub`
- model: `mock`

M1b workflowでは次を明示する。

- Realization: `MR-KJ-ATLAS-M1B`
- execution profile: `ollama-model-backed`
- runtime: `ollama`
- runtime version: `0.32.14`
- model: `qwen2.5:0.5b`
- model ID: `a8b0c5157701`

Applicationは対応するRealization logical referenceを保持し、Provenanceから具体的な実行条件を読み直せるようにする。

### H2で検査すること

- M1a / M1bが同じRealizationへ畳み込まれない。
- live Applicationの`realization_ref`がworkflowから明示したidentityと一致する。
- model / runtime等の実行条件がopaque Provenanceへ保持される。
- 実行条件を追加してもKJ Atlas固有responseをUniversal Contractへ昇格させない。
- grouping結果をRecommendation / Decisionへ自動昇格させない。
- 不完全なExecution Identityはcanonical stateを書き換える前に拒否する。
- 既存のlogical-only利用を壊さない。

## H1とH2の関係

H2でM1a / M1bを別Realizationとして扱うことは、H1を否定しない。

H1は、**一つのRealizationについてhistorical revisionを固定する必要が生じた場合にExact Bindingで表現できる**ことを示した。

H2は、**実現機構が異なるM1a / M1bを同じRealizationへ誤って畳み込まない**ことを示す。

```text
H2: 実現機構が違う
  → logical Realizationを分ける

H1: 同じRealizationのhistorical revisionを区別したい
  → Exact Bindingを使う
```

現時点では、この二段構えで必要な意味を表現できるため、Universal Contract拡張は不要と判断している。

## Requirement / Scenario監査

新しいStable Requirement / Scenarioは追加しない。

既存の次で扱える。

- REQ-0001 — 耐久的な意味の連続性
- REQ-0004 — Methodと一つのRealizationを同一視しない
- REQ-0021 — Realization / Executionを交換可能にする
- SCN-0005 — Cognitive Methodの交換・再構成
- SCN-0015 — Method Applicationのportable reconstruction

H2のactual CIでcurrent Contractでは守れない独立したProduct failureが現れた場合にだけ、Candidate Requirementを検討する。

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

### H2 / Issue closure

- [x] M1a / M1bを別Realizationとして扱うcurrent mapping方針を定める。
- [x] live mappingへ明示的なRealization identityを渡す。
- [x] model / runtime等の実行条件をopaque Provenanceへ保持する。
- [x] 不完全なExecution Identityをcanonical state変更前に拒否するtestを追加する。
- [ ] M1a actual workflowで新しいmappingを成功させる。
- [ ] M1b actual workflowで新しいmappingを成功させる。
- [ ] Plan integrity / Semantic Runtime / Release Candidate Gateを含む対象CIをsuccessさせる。
- [ ] H2結果からRequirement / Contract変更の要否を最終監査する。
- [ ] 上流計画へH1 / H2結果を同期する。
- [ ] 自然な日本語を最重要視して全文を再確認し、最終意味監査を行う。

## Evidence state

- M1a deterministic model stub execution: **Scoped Executable Evidence available**
- M1b actual model-backed execution: **Scoped Executable Evidence available**
- H1 Core / Bundle historical reconstruction: **Scoped Executable Evidence available — Run `33629248978`**
- H2 live integration preservation: **Awaiting current PR CI**
- arbitrary model / runtime version portability: **Not Yet Verified**
- E4 Operational portability: **Not Yet Verified**
- Operational Evidence: **Not Yet Verified**

## Reopen / escalation条件

本IssueをResolvedした後も、次の場合は再検討する。

- Realizationを分けても過去Applicationの実行条件を十分に再構成できない。
- 同一Realization内のrevisionをExact Bindingしてもhistorical revisionを一意に復元できない。
- implementation Artifact / opaque Provenanceだけでは複数domainで重要な意味が失われる。
- live integration helperが再び異なる実現機構を同じRealizationへ畳み込む。
- version交換によって過去Decisionのbasis reconstructionが書き換わる。

## 自然な日本語レビュー

current Upstream Product Development Plan、Cognitive Method Contract、ADR-0008 / 0009 / 0017 / 0021 / 0025 / 0026、E3b-M1a / M1b Evidence、`runtime/go/livemethodintegration`、H1 probeと実行結果を照合した。

H1で確認した「同一Realization内のhistorical revision」と、H2で扱う「実現機構そのものが異なるRealization」を分けて整理した。M1a / M1bの違いをmodel / runtime固有のUniversal fieldへ持ち込まず、logical Realizationとopaque Provenanceで保持する。一方、同じRealization内のrevisionを固定する必要がある場合にはExact Bindingを利用できる。

意味、規範強度、未検証範囲、Evidence強度を変えず、自然な日本語として一続きに読めることを最重要視して全文を再ドラフトし、H2 CI前の意味監査を実施した。
