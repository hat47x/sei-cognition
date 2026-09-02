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

まずcurrent Cognitive Method ContractとSemantic Reference / Exact Bindingだけで必要な再構成が成立するかを実証し、不足が確認された場合にだけContract / Requirementの追加を検討する。

## 背景

E3b-M1aでは、固定revisionのKJ Atlasと同repositoryのdeterministic model stubを実行した。E3b-M1bでは、KJ Atlasのsource revisionとMethod surfaceを変えず、model processだけをOllama `0.32.14`上の`qwen2.5:0.5b`へ交換した。

この二つは実行条件が異なる。一方、current `runtime/go/livemethodintegration`のreference helperはKJ Atlas source commitを基準に、どちらも同じlogical Realization Referenceへ戻す。

```text
MR-KJ-ATLAS-4F28C13
```

また、現在のprobe-local Provenance payloadが保持するのは主として次である。

- KJ Atlas repository
- KJ Atlas commit
- entry point
- result SHA-256

M1b workflowではmodel / runtime identityをintegration Evidenceとして別途記録できるが、その情報をそのままhistorical Method Applicationのportable記録へ移してはいない。

したがって、同じsource revisionの下でmodel / runtimeだけを交換した場合、**実行時の観測Evidenceには差があるのに、portable Application historyでは実現条件の差を十分に辿れない可能性**がある。

これはUniversal Contractの不足とは断定しない。current Contractはすでに次を許しているためである。

- `MethodRealization.implementation_refs`にExact Referenceを置く。
- `MethodApplication.realization_ref`にExact Referenceを置く。
- 同じLogical Referenceに複数のExact Binding revisionを持たせる。

## H1 — current Contractだけでhistorical revisionを区別できるか

H1では、M1a / M1bを次の二つのRealization revisionとして表現した。

```text
Method Definition
  M-KJ-ATLAS-GROUPING

Method Realization logical identity
  MR-KJ-ATLAS-GROUPING

Revision A
  KJ Atlas fixed source
  + deterministic model stub artifact

Revision B
  KJ Atlas fixed source
  + Ollama 0.32.14 / qwen2.5:0.5b execution artifact
```

Revision A / Bは同じMethod Definitionを実現し、同じRealization logical identityの履歴に属する。一方、実装ArtifactのExact BindingとRealization自身のExact Bindingはrevisionごとに分ける。

各Method Applicationは、その時点で用いたRealization revisionをExact Referenceで指す。

model / runtimeの具体情報はprobe-localなimplementation Artifact payloadに置き、Cognitive Method Contractへ`model`や`runtime`のUniversal fieldを追加しない。

## H1で確認したこと

`runtime/go/semanticruntime/method_realization_reconstruction_test.go`で、次を検査した。

1. M1a / M1b相当の二つのRealization revisionが、同じLogical Referenceの下で共存できる。
2. 両Realizationは同じKJ Atlas source ArtifactのExact Bindingを共有できる。
3. model execution Artifactだけを異なるExact Bindingとして保持できる。
4. Application AはRevision A、Application BはRevision BをExact Referenceで指せる。
5. 後からRevision Bが存在しても、Application Aが保持するhistorical bindingはRevision Bへ置き換わらない。
6. bundle内のExact Reference consistencyが成立する。
7. logical-onlyなRealization Referenceでは候補が二つとなり、historical revisionを一意に選べない。
8. model / runtime identityをUniversal Cognitive Method fieldへ昇格させなくても、implementation Artifactを経由して当時の実現条件へ辿れる。

### H1 CI

- `Semantic Runtime Conformance` Run `33629248978`: **success**
- Job `100244317333`: **success**
- 同Runの`go test ./...`にH1 probeを含む。
- Plan integrity Run `33629248942`: **success**

後続headでもSemantic Runtime Conformance Run `33629465281`はsuccessしている。

H1の正本Evidenceは`runtime/METHOD_REALIZATION_RECONSTRUCTION_EVIDENCE_2026-09-02.md`とする。

## H1から得た判断

H1の範囲では、**current Method Realization + implementation refs + Exact Bindingでhistorical revisionを区別できる**。

したがって、現時点では次を追加しない。

- model / runtime固有のUniversal Contract field
- 新しいStable Requirement / Scenario
- すべてのMethod ApplicationへExact Bindingを要求する一律規則

```text
H1 Core / Bundle reconstruction PASS
  != current live integration preservation PASS
  != arbitrary model/runtime portability
  != E4 Operational portability
```

H1はCore Contract / Bundleの表現力を確認したものであり、current live integration helperがその表現力を実際に使えていることまでは確認していない。

## H2 — live integrationへ落としたときの最小表現を比較する

ISSUE-000067はH1 successだけでは閉じない。

current `livemethodintegration`はApplicationへlogical-only Realization Referenceを渡している。また、`interactionprobe.CanonicalStore`はlogical identityを中心にrecordを扱っており、同一logical identityの複数Exact revisionを同一storeへ保持する用途はまだ実証していない。

H2では、少なくとも次の二案を比較する。

### A. 実行条件が異なるものを別Realization logical identityとして扱う

M1aとM1bを別のMethod Realizationとして記録し、両方を同じMethod Definitionへ結び付ける。

### B. 同じRealization logical identityのExact revisionとして扱う

H1と同様にlogical identityを共有し、implementation Artifactの違いをExact revisionとして表す。

どちらかをUniversal ruleとして先に固定しない。実際のApplication history、CanonicalStore、bundle交換、historical reviewで失われる意味を比較し、情報を落とさない最小境界を選ぶ。

必要性が残る場合には、閉じたPR #55で試した二つのactual modelによる交換probeの考え方をH2の実験入力として再利用できる。ただし、新しい`ExecutionIdentity`等の意味構造を先に正本へ追加しない。

## 実証に用いた既存Evidence

### Revision A相当 — M1a

- KJ Atlas repository: `hat47x/kj-atlas`
- KJ Atlas commit: `4f28c13abe4176503c6fed863383a2d1db2299e9`
- Method surface: `POST /ai/suggest-card-groups`
- model execution: KJ Atlas repository同梱deterministic model stub
- representative current-baseline Run: `33587455439`

### Revision B相当 — M1b

- KJ Atlas repository: `hat47x/kj-atlas`
- KJ Atlas commit: `4f28c13abe4176503c6fed863383a2d1db2299e9`
- Method surface: `POST /ai/suggest-card-groups`
- inference runtime: Ollama `0.32.14`
- model: `qwen2.5:0.5b`
- observed model ID: `a8b0c5157701`
- post-merge Run: `33609470323`

H1ではactual modelを再度呼ぶこと自体を目的としていない。既に成立したM1a / M1bの実行identityを入力として、portable historical reconstructionの意味境界を検査した。

## Requirement / Scenario監査

H1の結果を踏まえても、新しいStable Requirement / Scenarioは追加しない。

既存の次で引き続き扱う。

- REQ-0001 — 耐久的な意味の連続性
- REQ-0004 — Methodと一つのRealizationを同一視しない
- REQ-0021 — Realization / Executionを交換可能にする
- SCN-0005 — Cognitive Methodの交換・再構成
- SCN-0015 — Method Applicationのportable reconstruction

H2でcurrent Contract / Exact Bindingだけでは守れない独立したProduct failureが確認された場合にだけ、Candidate Requirementを検討する。

## Non-goals / 停止線

- model出力品質を評価すること
- KJ法としての成果品質を評価すること
- 同じpromptから同じ生成文を再現すること
- Ollama、qwen、Git commitをUniversal identityへ固定すること
- model / runtime固有fieldをCognitive Method Contractへ追加すること
- 全ApplicationへExact Bindingを必須化すること
- production credential / distribution policyを決めること
- E4 Operational portabilityを成立させること
- v0.2.0 supported scopeを遡及的に拡張すること

```text
historical reconstruction H1 PASS
  != arbitrary model/runtime portability
  != model quality
  != Operational Evidence
```

## 完了条件

### H1

- [x] M1a / M1bの差とcurrent live integration記録の差を整理する。
- [x] current Cognitive Method Contract / Exact Bindingで表現可能な仮説を定義する。
- [x] 同一Realization logical identityに二つのExact Binding revisionを置くH1 probeを実装する。
- [x] 各Applicationが対応するRealization revisionをExact Referenceで保持できることを確認する。
- [x] logical-only referenceが複数revisionを一意に復元できないnegative controlを確認する。
- [x] bundle Exact Reference consistencyを確認する。
- [x] actual CIでH1 probeを成功させる。
- [x] 実証結果からUniversal Contract / Requirement変更の要否を監査し、H1時点ではNo Changeとする。
- [x] H1 Evidence文書を作成する。

### H2 / Issue closure

- [ ] H1結果を上流計画、Product Milestone、文書監査台帳へ同期する。
- [ ] current live integrationでRealization execution identityを失わない最小表現を比較・実証する。
- [ ] H2結果からRequirement / Contract変更の要否を再監査する。
- [ ] 対象CIをすべてsuccessさせる。
- [ ] 自然な日本語を最重要視して更新文書を全文再確認し、最終意味監査を行う。

## Evidence state

- M1a deterministic model stub execution: **Scoped Executable Evidence available**
- M1b actual model-backed execution: **Scoped Executable Evidence available**
- H1 Core / Bundle historical reconstruction: **Scoped Executable Evidence available — Run `33629248978`**
- live integration preservation of Realization execution identity: **Not Yet Verified**
- arbitrary model / runtime version portability: **Not Yet Verified**
- E4 Operational portability: **Not Yet Verified**
- Operational Evidence: **Not Yet Verified**

## Reopen / escalation条件

本IssueをResolvedした後も、次の場合は再検討する。

- Exact-bound Realizationを保持しても過去Applicationを一意に復元できない。
- implementation ArtifactのExact Bindingだけでは、複数の実行条件を区別できない重要Scenarioが見つかる。
- Realization revisionとmodel / runtime revisionの関係をUniversalに表さないと複数domainで同じ意味欠落が起きる。
- live integration helperがlogical-only referenceへ退化し、historical bindingを失う。
- version交換によって過去Decisionのbasis reconstructionが書き換わる。

## 自然な日本語レビュー

current Upstream Product Development Plan、Cognitive Method Contract、ADR-0008 / 0009 / 0017 / 0021 / 0025 / 0026、E3b-M1a / M1b Evidence、`runtime/go/livemethodintegration`のcurrent mapping、H1 probe、Run `33629248978`を照合した。

M1aとM1bではKJ Atlasのsource revisionが同じままmodel executionだけが変わる。H1では、その差を直ちにUniversal model fieldの不足とは扱わず、既存のMethod Realization、implementation refs、Exact Bindingだけでhistorical revisionを一意に辿れることを確認した。一方、current live integrationはまだlogical-only Realization Referenceを使っているため、Core Contractの表現力と実際のmapping成立を混同せずH2へ残している。

意味、規範強度、未検証範囲、Evidence強度を変えず、自然な日本語として一続きに読めることを最重要視して全文を再ドラフトし、最終意味監査を実施した。
