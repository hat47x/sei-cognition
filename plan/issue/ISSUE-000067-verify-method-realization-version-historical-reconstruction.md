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

これはUniversal Contractの不足とはまだ断定しない。current Contractはすでに次を許しているためである。

- `MethodRealization.implementation_refs`にExact Referenceを置く。
- `MethodApplication.realization_ref`にExact Referenceを置く。
- 同じLogical Referenceに複数のExact Binding revisionを持たせる。

## 最初の実証仮説

最初のH1 probeでは、M1a / M1bを次の二つのRealization revisionとして扱う。

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

Revision A / Bは同じMethod Definitionを実現し、同じRealization logical identityの履歴に属するが、実装ArtifactのExact BindingとRealization自身のExact Bindingは異なるものとして記録する。

各Method Applicationは、その時点で用いたRealization revisionをExact Referenceで指す。

この表現で次が成立するなら、model / runtime固有fieldをMethod Applicationへ追加する必要はない。

## H1 probeで確認すること

1. M1a / M1bに相当する二つのRealization revisionが、同じLogical Referenceの下で共存できる。
2. 両Realizationは同じKJ Atlas source Artifactを参照できる。
3. model execution Artifactだけを別のExact Bindingとして保持できる。
4. Application AはRevision A、Application BはRevision BをExact Referenceで指せる。
5. 後からRevision Bが追加されても、Application Aのhistorical bindingがRevision Bへ置き換わらない。
6. bundle内のExact Reference consistencyが成立する。
7. logical-onlyなRealization Referenceでは、複数revisionが存在するとhistorical revisionを一意に選べないことをnegative controlとして確認する。
8. model / runtime identityはprobe-localなimplementation Artifactの内容として保持し、Universal Cognitive Method fieldへ昇格させない。

## 実証に用いる既存Evidence

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

このH1 probeではactual modelを再度呼ぶこと自体を目的にしない。既に成立したM1a / M1bの実行identityを入力として、portable historical reconstructionの意味境界を検査する。

## Requirement / Scenario監査

現時点では新しいStable Requirement / Scenarioを追加しない。

まず既存の次で表現できるかを検査する。

- REQ-0001 — 耐久的な意味の連続性
- REQ-0004 — Methodと一つのRealizationを同一視しない
- REQ-0021 — Realization / Executionを交換可能にする
- SCN-0005 — Cognitive Methodの交換・再構成
- SCN-0015 — Method Applicationのportable reconstruction

H1 probeでcurrent Contract / Exact Bindingだけでは守れない独立したProduct failureが確認された場合にだけ、Candidate Requirementを検討する。

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
historical reconstruction probe PASS
  != arbitrary model/runtime portability
  != model quality
  != Operational Evidence
```

## 完了条件

- [x] M1a / M1bの差とcurrent live integration記録の差を整理する。
- [x] current Cognitive Method Contract / Exact Bindingで表現可能な仮説を定義する。
- [ ] 同一Realization logical identityに二つのExact Binding revisionを置くH1 probeを実装する。
- [ ] 各Applicationが対応するRealization revisionをExact Referenceで保持できることを確認する。
- [ ] logical-only referenceが複数revisionを一意に復元できないnegative controlを確認する。
- [ ] bundle Exact Reference consistencyを確認する。
- [ ] actual CIでH1 probeを成功させる。
- [ ] 実証結果から、Universal Contract / Requirement変更が必要かを監査する。
- [ ] Evidence文書、上流計画、Plan台帳を同期する。
- [ ] 自然な日本語を最重要視して全文を再ドラフトし、最終意味監査を行う。

## Evidence state

- M1a deterministic model stub execution: **Scoped Executable Evidence available**
- M1b actual model-backed execution: **Scoped Executable Evidence available**
- Realization revision historical reconstruction H1: **Not Yet Verified**
- arbitrary model / runtime version portability: **Not Yet Verified**
- E4 Operational portability: **Not Yet Verified**

## Reopen / escalation条件

本IssueをResolvedした後も、次の場合は再検討する。

- Exact-bound Realizationを保持しても過去Applicationを一意に復元できない。
- implementation ArtifactのExact Bindingだけでは、複数の実行条件を区別できない重要Scenarioが見つかる。
- Realization revisionとmodel / runtime revisionの関係をUniversalに表さないと複数domainで同じ意味欠落が起きる。
- live integration helperがlogical-only referenceへ退化し、historical bindingを失う。
- version交換によって過去Decisionのbasis reconstructionが書き換わる。

## 自然な日本語レビュー

current Upstream Product Development Plan、Cognitive Method Contract、ADR-0008 / 0009 / 0017 / 0021 / 0025 / 0026、E3b-M1a / M1b Evidence、`runtime/go/livemethodintegration`のcurrent mappingを照合した。

M1aとM1bではKJ Atlasのsource revisionが同じままmodel executionだけが変わるため、source commitだけをRealization identityの手掛かりにするとhistorical reconstructionが不足し得ることを明示した。一方、これを直ちにUniversal model fieldの不足とは扱わず、既存のMethod Realization、implementation refs、Exact Bindingで解けるかを先に実証する構成とした。

意味、規範強度、未検証範囲、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施した。