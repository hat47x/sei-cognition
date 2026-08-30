# ADR-0021: current Architecture / Contract基線の責務と正本構成を定める

Status: **Accepted**  
Related Issue: **ISSUE-000028**  
Updated: 2026-08-31

## Context

SOZAの`develop/v0.1.0`では、Product Value、Requirements、ADR / Issueまでがcurrent Design baselineとして実体化された。

次は`architecture/`と`contracts/`をactual repositoryへ実体化する必要がある。しかし、過去candidateの設計文書をそのままコピーすると、次の問題が起こり得る。

- M48 / M49 / M50等のMilestone構造をcurrent ontologyへ誤って持ち込む。
- 当時のGo型やfeasibility designを現在のRequirementより強い正本として扱う。
- Architecture、Contract、Schema、Implementationの責務が混ざる。
- historical local PASSをcurrent Executable Evidenceへ誤継承する。
- SOZA / TEI境界やProvider-neutral Capability Observation等、後から確定したADRを反映できない。

そのため、current Architecture / Contractsを実体化する前に、責務と正本構成を固定する。

## Decision

### 1. Product / Requirement / ADRをArchitectureより上位の入力とする

current Architectureは、Product Value、Requirements、Accepted ADRを具体的な構造へ落とす。

```text
Product Value / Value Model / Value Acceptance
  ↓
Requirements
  ↓
ADR
  ↓
Architecture
  ↓
Contract
  ↓
Implementation / Test / Evidence
```

既存Implementationを温存するためだけにArchitectureから上位文書を書き換えない。

### 2. Architectureは「責務と関係」を定める

Architectureは、主に次を定める。

- どの意味をどの層が所有するか。
- Core、Profile、Provider、Adapter、Projection等の責務をどう分けるか。
- Artifactや主体がどの境界を越えるか。
- どの意味をcurrent SOZAが所有し、何を外部へ委譲するか。
- どのContractが必要になるか。

Architectureへ、特定Go structのfield名、特定DB table、特定SDK呼出し等を必要以上に固定しない。

### 3. Contractは「境界を越えて守る不変条件」を定める

Contractは、Architectureで定めた境界について、実装・言語・Providerが変わっても検査したい意味条件を定める。

たとえば次を扱える。

- Artifact reference / Exact Bindingの不変条件
- Epistemic Artifactの必須意味
- Decision / Capability / Responsibility間の参照条件
- Portable interchangeの意味条件
- Profile固有のcrossing contract

Contractは単なる説明文でも、単なるwire schemaでもない。**何を満たせばその境界を実現したと言えるか**を記述する。

### 4. SchemaはContractの一つのRepresentationであり、Contractそのものではない

JSON Schema、Go struct、Protocol定義等は、Contractを機械的に表現・検査するための一つのRealizationである。

```text
Architecture != Contract != Schema != Implementation
```

Schemaに表現されていない意味がContract本文に存在する場合、Schemaだけを読んで意味を縮小しない。

逆に、Schemaへfieldが存在することだけを理由にUniversal Coreの意味へ昇格させない。

### 5. current Architectureの最小正本入口を定める

初期baselineでは、次をcurrent Architectureの入口とする。

```text
architecture/
  README.md
  SOZA_ARCHITECTURE.md
  REQUIREMENT_TRACEABILITY.md
```

- `README.md` — Architecture文書の読み方、状態、正本関係を説明する。
- `SOZA_ARCHITECTURE.md` — current SOZA全体の責務と主要境界を定める。
- `REQUIREMENT_TRACEABILITY.md` — V1〜V8 / REQ / ADR / Architecture / Contractの主要な追跡を示す。

個別の境界文書は、必要性が確認されたものから追加する。

### 6. current Contractsの最小正本入口を定める

初期baselineでは次を入口とする。

```text
contracts/
  README.md
```

その後、current Architectureから必要と判断されたContractを意味境界ごとに追加する。

Machine-readable schemaが必要になった場合は`contracts/schemas/`等へ配置できる。ただし、ディレクトリ構造自体をontologyとはみなさない。

### 7. Core / Profile / Provider / Adapter / Projection / Referenceを分ける

current Architectureは、少なくとも次を区別する。

#### Durable Semantic Core

実行手段が変わってもSOZAが保持する意味を扱う。

主な責務領域:

- world — Goal / Intent / Constraint等の文脈
- epistemics — Observation / Unknown / Conflict / Evidence / Provenance等
- cognition — Cognitive Method / Method Application等
- decision — Recommendation / Decision / Rationale等
- capability — Capability Definition / Observation / Matching等
- memory — exact historical binding / revision / supersession等

この列挙は、現在の全型を固定するものではない。

#### Method Pack

KJ法等のCognitive Method固有の知識・手続を置く。Method固有のArtifactをUniversal Coreへ無条件に昇格させない。

#### Optional Profile

federation、safe-action、coordination等、一定の利用条件で意味境界を追加する層とする。

#### Provider

workflow、agent runtime、SaaS、TEI、人間作業等、実現や実行を担う交換可能な手段とする。

#### Adapter

Provider固有状態をSOZAのObservation / Evidence / Capability境界へ写像する解釈・接続境界とする。

#### Projection

Workspace、UI、dashboard等の表示・操作面とする。Projectionをcanonical semantic authorityにしない。

#### Reference / Historical Asset

過去candidate、legacy runtime、historical contract等を、比較・再利用・回帰検討のために保存する。current normative Architectureとは分ける。

### 8. SOZA / TEIのProduct Boundaryを維持する

TEI固有のApplication、Database、Release、Deployment等をSOZA Architectureへ複製しない。

SOZAがTEIを利用する場合は、Capability、Provider-neutral Observation、Evidence、Adapter、Authorization等のcurrent境界から扱う。

TEIは関連製品であってもSOZAの内部Runtimeではない。

### 9. Historical candidateは一件ずつ再評価する

過去candidateのArchitecture / Contract文書は、次のいずれかへ分類する。

- `adopt` — current Requirements / ADRへ整合する意味をcurrent文書として再構成する。
- `split` — 一つの旧文書が複数のcurrent責務を混在させているため分割する。
- `reference-only` — historical evidenceとして価値はあるがcurrent正本にはしない。
- `drop` — current Product Valueでは不要であり、現行設計へ持ち込まない。

`M48_*`、`M49_*`等のMilestone名をcurrent Architectureの必須命名へ自動継承しない。

### 10. Traceabilityは多対多を許容する

一つのREQが複数ADR / Architecture / Contractへ展開してよい。一つのArchitecture境界が複数REQを支えてもよい。

重要なのは一対一対応ではなく、**なぜその境界が必要なのかをProduct Valueまで辿れること**である。

current `REQUIREMENT_TRACEABILITY.md`では、少なくとも重要なV1〜V8 / REQ / ADR / Architecture / Contract関係を明示する。

### 11. Design EvidenceとExecutable Evidenceを分ける

Architecture / Contract文書をactual repositoryへ追加したことはDesign Evidenceである。

Schema、runtime、fixture、checkerが存在し、actual repository上で検査できるまではExecutable EvidenceをSatisfiedへ上げない。

```text
Architecture document exists != Executable Acceptance Satisfied
Contract document exists != Runtime conformance PASS
```

### 12. 自然な日本語をcurrent Architecture / Contractの品質条件とする

current Architecture / Contractは、技術用語を保持しつつ、文書本文から責務・条件・留保が自然な日本語で読めることを要求する。

内容と構造を確定した後、`plan/DOCUMENT_AUTHORING_STANDARD.md`に従って全文を再ドラフトし、最終意味監査を行う。

historical原文は、原文性がEvidenceになる場合は書き換えずReference側へ置く。

## Consequences

### Positive

- 過去candidateの実装順序をcurrent ontologyへ持ち込みにくくなる。
- Product Value / REQ / ADRとArchitectureの関係を明示しやすい。
- SchemaやGo型が意味上の正本へ逆転しにくい。
- historical資産を捨てずに、current設計と分離して再利用できる。
- SOZA / TEI境界とProvider-neutral設計を維持しやすい。
- Design EvidenceとExecutable Evidenceの混同を防ぎやすい。

### Costs

- historical candidateを一括コピーするより再構成に時間がかかる。
- current Architecture / ContractごとにRequirement / ADRとの追跡を確認する必要がある。
- 一部の旧文書はcurrent版へrename / split / reference化する必要がある。

## Revisit conditions

次の場合に再検討する。

- current Architecture文書が増え、3つの入口だけでは編集・検索が実務上困難になる。
- Contractの数が増え、semantic / profile / interchange等の明示的な分類が必要になる。
- machine-readable traceabilityを要求するactual use caseが現れる。
- federation等で、別repositoryとのContract identityを安定して参照する必要が生じる。

ディレクトリ数が増えたことだけを理由に、意味ontologyを追加しない。

## Evidence

- `product/value/SOZA_PRODUCT_VALUE.md`
- `product/value/SOZA_VALUE_MODEL.md`
- `product/value/SOZA_VALUE_ACCEPTANCE.md`
- `requirements/PRODUCT_REQUIREMENTS.md`
- ADR-0014
- ADR-0018
- ADR-0020
- ISSUE-000022
- ISSUE-000028
- historical M48〜M50 architecture / contract candidate群

## Follow-up

1. ISSUE-000028を本ADRのDesign Acceptance確認後にResolvedとする。
2. `architecture/README.md`、`SOZA_ARCHITECTURE.md`、`REQUIREMENT_TRACEABILITY.md`を実体化する。
3. `contracts/README.md`を実体化する。
4. historical candidateを一件ずつ`adopt / split / reference-only / drop`へ分類する。
5. current Contract候補をREQ / ADRから再導出する。
6. runtime / schema / fixtureの再導入は、その後に行う。

## Natural Japanese review

Architecture、Contract、Schema、Implementationの権威関係と、Core / Profile / Provider / Adapter / Projection / Referenceの責務を整理した後、Product ValueとRequirementsへ戻って意味境界を確認しました。そのうえで、意味、強度、留保を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施しています。
