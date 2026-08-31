# ISSUE-000015: 既存の開発文書を自然な日本語で再監査する

Status: **In Progress**  
Priority: **1**  
Related ADRs: **—**  
Updated: 2026-08-31

## 目的

SOZAの既存開発文書を、技術的な意味・仕様・留保・Evidence強度を変えず、**自然な日本語となることを最重要視して全文をドラフトし直す工程**へ通す。

この作業は一度限りの文章校正ではない。新規作成・更新する文書でも同じ工程を必須とし、SOZAの継続的な品質ゲートとして扱う。

## 必須工程

開発文書は原則として次の順序で確認する。

1. 文書の目的と決定範囲を確認する。
2. 最新のProduct Value、Requirement、ADR、Architecture、Contractとの整合を確認する。
3. 古い議論や破棄済みの前提が残っていないか確認する。
4. 技術的な矛盾、重複、不足、古いEvidence記述を修正する。
5. 技術的な意味、仕様、留保、Evidence強度をいったん固定する。
6. **自然な日本語となることを最重要視して全文をドラフトし直す。**
7. 再ドラフトによって要求強度、条件、例外、Evidenceの高さが変わっていないか最終監査する。

第6工程は省略しない。詳細な基準は`plan/DOCUMENT_AUTHORING_STANDARD.md`を正とする。

## 監査の優先順位

1. `product/value`、`product/vision`、`product/principles`
2. `plan/adr`、`plan/issue`、`plan/registry.yaml`
3. `requirements`
4. `architecture`、`contracts`
5. root README、runtime / fixture / toolの説明文書
6. `plan/rebaseline`等のhistorical / reporting文書

## 現在の進捗

### 1. 文書品質基盤

次を整備済み。

- `plan/DEVELOPMENT_WORKFLOW.md`
- `plan/DOCUMENT_AUTHORING_STANDARD.md`
- `plan/README.md`
- `product/principles/SOZA_PRODUCT_PRINCIPLES.md`

内容と構造を確定した後に全文を自然な日本語で再ドラフトし、さらに意味監査を行う工程を通常開発へ組み込んだ。

### 2. Product層

次のcurrent Product文書は主要baselineを一巡した。

- `product/value/SOZA_PRODUCT_VALUE.md`
- `product/value/SOZA_VALUE_MODEL.md`
- `product/value/SOZA_VALUE_ACCEPTANCE.md`
- `product/vision/SOZA_PRODUCT_VISION.md`
- `product/principles/SOZA_PRODUCT_PRINCIPLES.md`

Value Modelでは価値の三層、価値衝突時の優先規則、Core昇格基準、V1〜V8、失敗条件を明示した。

Value AcceptanceではDesign / Executable / Release / Operational Evidenceを分離した。

Vision / PrinciplesもValue Modelへ戻って再監査済みである。

### 3. Plan層

current registryはADR-0001〜ADR-0024、ISSUE-000001〜ISSUE-000036を管理する。

この期間に新規・大幅更新した主なDecision / Issue:

- ADR-0018 — Product Value authority / evaluation boundary
- ADR-0019 — Provider-neutral Capability Observation
- ADR-0020 — Requirements traceability / Evidence boundary
- ADR-0021 — Architecture / Contract authority / versioning
- ADR-0022 — first runtime read / validate / reconstruct slice
- ADR-0023 — current Representation Profile baseline
- ADR-0024 — Provider Adapter observation mapping boundary
- ISSUE-000022 — current repository baseline closure
- ISSUE-000024〜000033 — Requirements / Architecture / Contract / Runtime実体化
- ISSUE-000034 — historical M47 digest recovery
- ISSUE-000035 / 000036 — Provider Adapter設計・synthetic実装

新規・大幅更新文書は、自然な日本語全文再ドラフトと最終意味監査を通している。

ただし、ADR-0001〜ADR-0024、ISSUE-000001〜ISSUE-000036の**既存部分を含む全件逆向き監査が完了したとはまだ扱わない。**

### 4. Requirements層

current Requirements:

- REQ-0001〜REQ-0022
- SCN-0001〜SCN-0017
- historical mapping

Requirements Design baselineに加え、Registry checker / negative self-test / GitHub Actionsもcurrent actual repositoryで成立している。

`requirements/PRODUCT_REQUIREMENTS.md`は2026-08-31に再基線化し、Architecture / Contract / Runtimeが未実体化だった時期の古いEvidence記述を削除した。

現在は、各Requirementについてfixture / first runtime sliceで直接確認した範囲だけを`Partially Satisfied`等として記述し、Release / Operational Evidenceへ広げていない。

### 5. Architecture層

current Architecture baseline:

```text
architecture/
  README.md
  SOZA_REFERENCE_ARCHITECTURE.md
  TRACEABILITY.md
  history/
    HISTORICAL_ARCHITECTURE_MAPPING.md
```

M48 / M49 / M50等のMilestone順をcurrent ontologyへ持ち込まず、意味上のarchitecture concernへ再構成した。

REQ-0001〜REQ-0022を少なくとも一つのarchitecture concernへ追跡できる。

Architecture文書は内容確定後に自然な日本語へ全文再ドラフトし、意味境界とEvidence強度を再監査済みである。

### 6. Contracts / Representation Profiles

current Contract family:

- `soza.semantic-reference/v1alpha1`
- `soza.decision-memory/v1alpha1`
- `soza.capability-observation/v1alpha1`
- `soza.semantic-interchange/v1alpha1`

Contract Definition、Catalog、Traceability、historical mapping、Schema、fixture、conformance checkerをactual treeへ実体化した。

Representation ProfileはADR-0023で、

- `soza.jcs+sha256/v1alpha1`
- `soza.raw-bytes+sha256/v1alpha1`

をcurrent/future基線としてAcceptedした。

historical M47 digest規則だけはcurrent Profileと分離し、ISSUE-000034でBlockedとしている。

旧文書にあった「Representation Profile全体が未確定」という記述はcurrent正本から除去・更新する。

### 7. Runtime / Provider Adapter

first semantic runtime sliceをGoで実体化し、current Contract fixtureと同じ意味境界からread / validate / reconstructを検証した。

`Semantic Runtime Conformance` run #3でContract checkerとGo testsがsuccessした。

さらにADR-0024に従い、異なるinput shapeを持つsynthetic Provider A / BからCapability Observationを生成するAdapter sliceを追加した。

Provider Adapterは、

- mapping provenance
- source state ref
- Unknown preservation
- Provider-specific target
- no Decision / Authority / Execution escalation

を検査する。

`Semantic Runtime Conformance` run #4でもsuccessを確認済みである。

fixture説明文書も、Provider固有fieldをUniversal schemaと誤読しないよう自然な日本語へ再ドラフト済みである。

### 8. root README

root READMEは、Requirements / Architecture / Contract / Representation Profile / Runtimeが未実体化だった古い状態からcurrent actual treeへ同期した。

current Evidenceの範囲と、Provider production integration / Release / Operational Evidenceの未完了を分けて記載している。

## CIと文書更新

開発中にCI failureを検出した場合は、その時点で原因を解消し、successを確認してから次の作業へ進む。

2026-08-31には、

- runtime workflowのdependency導入漏れ
- F5/F6 Semantic Interchangeをstandalone recordとして扱ったtest誤り
- Issue本文とregistryを別commitで更新した際の一時的status不整合

を検出し、いずれも原因を確認して修正した。

以後、Plan文書とregistryを同時に変更する場合は、可能な範囲でatomic commitを用いて中間不整合を避ける。

## 進行中の作業

現時点の中心は、**既存文書全件の逆向き監査**である。

優先順:

1. ADR-0001〜ADR-0017の既存本文をcurrent Product Value / REQ / Architecture / Contractから逆向きに再監査する。
2. ISSUE-000001〜ISSUE-000021の既存本文に、古いMilestone前提やEvidence状態が残っていないか再監査する。
3. `plan/rebaseline`等のhistorical / active境界を確認する。
4. runtime code comment / fixture README / tool README等の説明文書を同じ品質工程へ通す。
5. README / Requirements / Architecture / Contractを、後続実装でEvidenceが変わるたびに再同期する。

ISSUE-000034はhistorical一次sourceの回収待ちであり、自然な日本語監査とは独立したBlocked事項として扱う。

## Acceptance criteria

- [x] 固定100倍基準をcurrent Product正本から除去し、10〜50×のmoving horizonへ統一した。
- [x] X-TEAをcurrent Product名として扱わない。
- [x] TEIをSOZA内部Runtimeと誤読させないProduct / Architecture境界を整備した。
- [x] Design / Executable / Release / Operational Evidenceの区別をcurrent上位文書へ反映した。
- [x] REQ / SCNのcurrent正本とhistorical mappingを分離した。
- [x] Architecture concernとruntime componentを分離した。
- [x] Semantic ContractとRepresentation Profileを分離した。
- [x] Contract DefinitionとSchema / implementationの権威関係を分離した。
- [x] runtime / Provider Adapterの新規説明文書へ自然な日本語再ドラフト工程を適用した。
- [ ] ADR-0001〜ADR-0024の既存本文をcurrent baselineから全件再監査する。
- [ ] ISSUE-000001〜ISSUE-000036の既存本文をcurrent baselineから全件再監査する。
- [ ] その他current branchに残る開発説明文書の対象一覧を確定し、監査漏れがないことを確認する。

current branchに存在する対象開発文書を確認し終えるまで、本IssueをResolvedにしない。

## 対象外

技術用語をすべて日本語へ翻訳することは目的としない。

また、読みやすくするために未決事項を勝手に確定したり、Evidenceより強い状態へ書き換えたりしない。

自然な日本語と技術的精度を両立する。

## Natural Japanese review

Product / Requirements / Architecture / Contract / Representation Profile / Runtime / Provider Adapterのcurrent到達点とCI実績へ戻って進捗を再構成した。完了済みの基線整備と、既存文書全件の逆向き監査という未完了作業を分けた後、監査範囲、Evidence強度、未完了条件を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
