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

### 1. 文書品質基盤 / Product層

`plan/DEVELOPMENT_WORKFLOW.md`、`plan/DOCUMENT_AUTHORING_STANDARD.md`、`plan/README.md`へ、内容・構造を確定した後に自然な日本語で全文再ドラフトし、さらに意味監査を行う工程を組み込んだ。

Product Value / Value Model / Value Acceptance / Vision / Principlesも主要baselineを一巡し、Value hierarchy、V1〜V8、Evidence階層、Core昇格基準等をcurrent正本として整備済みである。

### 2. ADR全件逆向き監査

ADR-0001〜ADR-0024について、current Product Value / Requirements / Architecture / Contract / Runtime Evidenceから逆向きに再監査した。

主な是正:

- historical M48 / M49 / M50をcurrent Architectureの正本として読める参照をcurrent Contract / Architectureへ置換した。
- Representation Profile確定前の記述をADR-0023 / ISSUE-000009のcurrent基線へ同期した。
- Decision Memory / Capability Observation / Runtime実体化前のEvidence記述をcurrent到達点へ同期した。
- TEIやProvider Adapterの後続実装によっても、SOZA / TEI Product BoundaryやProvider-neutralityが変わっていないことを確認した。

ADRのDecision自体を後続実装都合で変更した箇所はない。

**ADR-0001〜ADR-0024の既存本文を含む全件逆向き監査は完了した。**

### 3. ISSUE全件逆向き監査

ISSUE-000001〜ISSUE-000036についてcurrent Evidenceへ戻って再監査した。

ISSUE-000001〜000007、000016〜000019、000021〜000023、000027〜000028、000034、000036は、主要な意味・Evidence境界がcurrent状態と整合していることを確認した。

古い時系列前提が残っていたIssueでは次を更新した。

- ISSUE-000005 — historical M49表現をcurrent Decision Memoryへ接続。
- ISSUE-000008 — repository baseline未実体化前提を削除し、ISSUE-000022 closureへ同期。
- ISSUE-000009 — first runtime存在とRuntime verifier未統合を分離。
- ISSUE-000010〜000012 — historical M49 labelとcurrent Decision Memory Contract / Runtime Evidenceを分離。
- ISSUE-000013〜000014 — historical M50 planningとcurrent Capability Observation / synthetic Adapter Evidenceを分離。
- ISSUE-000020 — ISSUE-000024 / 000036のcurrent Evidenceへ同期。
- ISSUE-000024 — Representation Profile / Runtime / Adapterの後続Evidenceへ同期。
- ISSUE-000026 — Requirements Registry checker完了へ同期。
- ISSUE-000029〜000031 — Contract / Profile / Runtimeが未実体化だったEvidence欄をcurrent状態へ更新。
- ISSUE-000032〜000033 — runtime implementationとProvider Adapter後続完了へ同期。
- ISSUE-000035 — Design closureとISSUE-000036のExecutable Evidenceを分離。

**ISSUE-000001〜ISSUE-000036の既存本文を含む全件逆向き監査は完了した。**

### 4. Requirements / Architecture / Contracts / Runtime

RequirementsはREQ-0001〜REQ-0022、SCN-0001〜SCN-0017をcurrent baselineとし、Registry checker / negative self-test / GitHub Actionsまで成立している。

ArchitectureはMilestone順ではなくarchitecture concernへ再構成済みで、Contract 4 family、Representation Profile、Schema / Fixture conformance、first semantic runtime、synthetic Provider Adapterへ追跡できる。

root READMEと`requirements/PRODUCT_REQUIREMENTS.md`もcurrent actual Evidenceへ再基線化済みである。

## CIと文書更新

CI failureを検出した場合は、その時点で原因を解消し、successを確認してから次の作業へ進む。

Plan文書とregistryを同時に変更する場合は可能な範囲でatomic commitを用い、中間不整合を避ける。

文書だけの更新でもPlan integrityを確認し、自然な日本語への再ドラフトによってID、Status、関連参照等が壊れていないことを検査する。

## 次の監査対象

ADR / Issue全件監査が完了したため、次はcurrent branchに残る**その他の開発説明文書**を対象一覧化し、優先順に監査する。

主な対象:

1. `plan/rebaseline`等のhistorical / reporting文書
2. `plan/kj`等の設計統合・思考記録
3. `runtime/`配下のREADME / Evidence文書 / code comment
4. `fixtures/`配下のREADME / fixture説明
5. `tools/`配下のREADME / checker説明
6. root以外の補助README / traceability補助文書

historical一次資料や固定fixtureの内容そのものは、自然な日本語化を理由に改変しない。current説明文とhistorical evidenceを区別する。

ISSUE-000034はhistorical一次sourceの回収待ちであり、本Issueとは独立したBlocked事項として扱う。

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
- [x] ADR-0001〜ADR-0024の既存本文をcurrent baselineから全件再監査した。
- [x] ISSUE-000001〜ISSUE-000036の既存本文をcurrent baselineから全件再監査した。
- [ ] その他current branchに残る開発説明文書の対象一覧を確定し、監査漏れがないことを確認する。

current branchに存在する対象開発文書を確認し終えるまで、本IssueをResolvedにしない。

## 対象外

技術用語をすべて日本語へ翻訳することは目的としない。

読みやすくするために未決事項を勝手に確定したり、Evidenceより強い状態へ書き換えたりしない。

自然な日本語と技術的精度を両立する。

## Natural Japanese review

ADR-0001〜0024、ISSUE-000001〜000036、Product / Requirements / Architecture / Contract / Representation Profile / Runtime / Provider Adapterのcurrent到達点へ戻って全件逆向き監査を行った。歴史的Milestone、各Issue自身のclosure、後続Issueで増えたExecutable Evidence、未検証のProduction / Release / Operational領域を分離した後、監査範囲とEvidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。
