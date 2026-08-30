# ISSUE-000028: current Architecture / Contracts基線の構成と移行規則を定める

Status: **In Progress**  
Priority: **1**  
Related ADRs: **ADR-0014, ADR-0018, ADR-0020**  
Updated: 2026-08-31

## 目的

current Requirements baselineを`architecture/`と`contracts/`へ落とす前に、正本となる文書構成、ArchitectureとContractの責務、Product / Requirement / ADRからの追跡方法、historical candidateの再利用規則を定めます。

過去candidateのArchitecture / Contract群をそのままGitHubへコピーしてから整理するのではなく、現在のProduct ValueとRequirementsを基準に、必要な設計だけをcurrent baselineとして再構成します。

## 背景

`develop/v0.1.0`では、次がcurrent Design baselineとして実体化されています。

- Product Value / Value Model / Value Acceptance
- Product Vision / Principles
- ADR / Issue / registry
- REQ-0001〜REQ-0022
- SCN-0001〜SCN-0017

一方、current `architecture/`と`contracts/`はまだ存在しません。

過去candidateには、Core Boundary、Epistemics、Exact Binding、Persistence、Decision Memory、Capability Choice、Federation等の設計文書とContractが存在します。これらには再利用価値がありますが、Milestone名や当時の実装候補、旧Evidence状態も含まれています。

## 決める必要があること

### 1. ArchitectureとContractの責務

- Architectureは何を正本とするか。
- Contractは何を正本とするか。
- Schemaやwire representationはContractとどのような関係に置くか。
- Architecture文書に実装fieldを過剰に固定しないための境界をどうするか。

### 2. 正本入口

最小のcurrent baselineとして、どの文書を入口にするか。

候補:

```text
architecture/
  README.md
  SOZA_ARCHITECTURE.md
  REQUIREMENT_TRACEABILITY.md

contracts/
  README.md
```

個別境界文書やschemaは、必要性が確認されたものから追加します。

### 3. レイヤ境界

少なくとも次を区別した設計として読める必要があります。

- Durable Semantic Core
- Method Pack
- Optional Profile
- Provider / Adapter
- Projection
- Reference / Historical Asset

Core内部では、world、epistemics、cognition、decision、capability、memoryの責務を現在のRequirementから再確認します。

### 4. Traceability

少なくとも次を追えるようにします。

```text
Product Value / V1〜V8
  → REQ
  → ADR
  → Architecture
  → Contract
  → Implementation / Test / Evidence
```

すべてを一対一対応にはしません。多対多の関係を許容しつつ、重要な設計境界の根拠を後から辿れることを優先します。

### 5. Historical candidateの扱い

過去candidate文書を、少なくとも次に分類できるようにします。

- `adopt` — current意味へ整合し、current文書として再構成する。
- `split` — 複数のcurrent責務へ分ける。
- `reference-only` — 設計履歴として残すがcurrent正本にはしない。
- `drop` — current Product Valueでは不要であり、現行設計へ持ち込まない。

historical filenameやMilestone名を、current Architectureのontologyへ自動継承しません。

## Acceptance criteria

### Semantic / Design Acceptance

- [ ] ArchitectureとContractの責務を区別できる。
- [ ] current正本入口を定めている。
- [ ] Core / Profile / Provider / Adapter / Projection / Referenceを区別している。
- [ ] REQ / ADRからArchitecture / Contractへ追跡できる規則を定めている。
- [ ] historical candidateを無条件にcurrent正本へコピーしない規則を定めている。
- [ ] SchemaをContractそのものと同一視しない。
- [ ] Milestone構造を利用者世界のontologyへ変換しない。
- [ ] 自然な日本語で全文を再ドラフトし、最終意味監査を行っている。

### Executable Acceptance

本Issueでは要求しません。Architecture / Contractsを実体化した後、具体的なschema、fixture、checkerを別Issueで検証します。

## Dependencies

- Product Value / Value Model / Value Acceptance
- ADR-0014 — SOZA / TEI Product Boundary
- ADR-0018 — Product Value authority / evaluation boundary
- ADR-0020 — Requirements traceability / evidence boundary
- ISSUE-000015 — 文書監査
- ISSUE-000022 — repository baseline実体化
- ISSUE-000026 — Requirements baseline

## 対象外

- historical runtimeの一括移植
- current Go package構成の確定
- wire field名の確定
- schema versionの確定
- Provider固有状態のUniversal Core化
- Design文書だけを根拠とするExecutable Evidenceの引き上げ

## 自然な日本語ドラフト

Requirements baselineとISSUE-000022へ戻って必要な判断を整理した後、Architecture / Contract / Schema / Implementationの責務を混同しないよう構造化しました。そのうえで、意味、強度、留保を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を行っています。
