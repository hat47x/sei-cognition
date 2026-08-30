# ISSUE-000022: SOZA repositoryの基線ファイルを実体化し、Evidence claimを再整合する

Status: **In Progress**  
Priority: **2**  
Related ADRs: **ADR-0007, ADR-0008, ADR-0009, ADR-0014**  
Updated: 2026-08-31

## Goal

GitHub上の`hat47x/soza`に、Product Value、Requirements、Architecture、Contracts、Fixtures、Runtime、Tools等のactiveな基線を、現在のProduct BoundaryとAccepted ADRへ合わせて段階的に実体化する。

同時に、「historical / local candidateに候補実装やPASSがあること」と「actual GitHub repositoryに実装・検査資産が存在し、再実行できること」を区別し、Evidence claimを現在の実体へ合わせる。

## Background

`soza` repositoryは実体化されたが、現在のactual treeはProduct / plan文書が中心である。READMEには旧Phase 1 candidateで存在したRequirements、Architecture、Contracts、Runtime、Tools等への参照が残る一方、それらの多くはactual treeにまだ存在しない。

historical / local candidateには有用な設計・runtime・fixture・generated summaryが残っているが、それらを無検査でactual repositoryへ移し、過去PASSを現在PASSとして扱うことはできない。

最新Product Value、ADR-0014のSOZA / TEI Product Boundary、ADR-0018のEvidence Calibrationを基準に、上位文書から順に再基線化する。

## Current progress

### Completed in actual repository

- Product Value / Value Modelを最新基線へ精緻化。
- Value Scenarios / Value Traceabilityを追加。
- Product Vision / PrinciplesをValue Modelへ再整合。
- ADR-0001〜ADR-0019をProduct Valueへ戻して監査。
- plan Issue / registryをISSUE-000025まで正規化。
- 自然な日本語ドラフト工程をplanning conventionへ組み込み。

### Not yet materialized

- active Requirements / Acceptance Scenarios
- current Architecture baseline
- current Contracts / schemas
- actual fixtures
- Go module / runtime implementation
- conformance / test tools
- actual repository gate

これらについて、historical / local candidateの存在をactual treeの存在へ読み替えない。

## Required work

### 1. Requirements / Acceptanceを最新Product Valueから再基線化する

ISSUE-000024で、Value ScenarioからProduct Requirement / NFR / Acceptanceへの追跡基線を作る。

historical candidateを利用する場合も、最新Value Modelへ戻してretain / revise / split / merge / historical only等を判断する。

### 2. Architecture / ContractsをAccepted ADRへ戻す

旧candidateを一括コピーせず、少なくとも次へ照合する。

- ADR-0001〜ADR-0019
- `SOZA_VALUE_TRACEABILITY.md`
- SOZA / TEI Product Boundary
- Provider-neutral Capability Observation boundary
- Evidence Calibration

### 3. Runtime / Fixtures / Toolsをactual treeへ実体化する

Library等の候補資産を利用する場合、現在のProduct Boundaryと衝突しないことを確認する。

Go module、package、schema、fixtures、test toolがactual repositoryへ入った後にのみ、actual-repo gateを実行する。

### 4. historical M47を正直に扱う

歴史的M47 sourceがactual repositoryに存在しない場合、存在しない回帰試験をPASS扱いしない。

M47 contract / reportをhistorical referenceとして利用する場合は、そのEvidence levelを明示する。

### 5. Evidence namespaceを分ける

少なくとも次を区別する。

```text
historical evidence
local candidate evidence
actual repository design coverage
actual repository executable conformance
operational evidence
adoption / outcome evidence
```

一つのlevelのPASSを次へ自動継承しない。

### 6. READMEをactual treeへ合わせる

READMEの現在地、読む順序、gate、実装状態、Issue状態を、actual treeに存在するものだけで説明できるようにする。

historical candidateへの参照が必要な場合は、actual componentと区別して記述する。

## Constraints

- historical / local candidateのPASSをactual repository PASSへ自動継承しない。
- 存在しないM47 regressionをPASS扱いしない。
- READMEの記述を実装存在のEvidenceとしない。
- 旧bundleを無検査で一括コピーしない。
- TEI実装をSOZA実装の代替Evidenceにしない。
- 文書・コードとも、最新Product ValueとAccepted ADRを優先する。
- implementation orderをProduct ontologyへ変換しない。
- actual treeへ存在しないgateを「実行可能」として列挙しない。

## Dependencies and unlocked work

このIssueの進行と並行して、planningは先行できる。

- ISSUE-000024: Value → Requirement / Acceptance追跡は進行可能。
- ISSUE-000009: actual verifier実装・PASSは本Issueのruntime/tool基線待ち。
- ISSUE-000025: actual Capability Observation contract / fixtureは本Issueのcontract/fixture基線待ち。

したがって本Issueは単一の巨大copy作業ではなく、上位意味を確定しながらactual treeを段階的に増やす統合Issueとして扱う。

## Completion criteria

- Product ValueからRequirements / Acceptanceへ追跡できるactive文書がactual treeにある。
- READMEで参照するactiveな必須ファイルがactual treeに存在する。
- actual repository上で再実行可能なgateだけを列挙できる。
- actual repository evidenceとhistorical / local candidate evidenceが明確に分離される。
- ISSUE-000009の残件をactual treeで検証できる入口ができる。
- ISSUE-000025のcontract / fixtureを実体化できる入口ができる。
- M49 / M50等のproduction implementationを開始できるかを、最新Product Valueから改めて判断できる。
- READMEがactual treeとIssue状態を正しく反映する。

## Reopen conditions

Resolved後、READMEとactual treeが再び大きく乖離する、historical Evidenceがactual PASSとして扱われる、または新しいbaseline migrationで同種の混同が再発した場合は再開する。

## Natural Japanese review

actual tree、Product Value、ADR-0014 / 0018、ISSUE-000024 / 000025へ戻して現在地と依存関係を整理した後、意味、Evidence強度、未実装範囲を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済み。
