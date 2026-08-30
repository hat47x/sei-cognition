# ISSUE-000015: 既存の開発文書を自然な日本語で再監査する

Status: **In Progress**  
Priority: **1**  
Related ADRs: **—**  
Updated: 2026-08-31

## Goal

SOZAの既存開発文書を、技術的意味・仕様・留保を変えず、**自然な日本語となることを最重要視して全文をドラフトし直す工程**へ通す。

この工程を一度限りの文章校正ではなく、今後の文書作成に必須の品質ゲートとして定着させる。

## Required workflow

1. 文書の目的と決定範囲を確認する。
2. 最新のProduct Value、Requirement、ADR、Architectureとの整合を確認する。
3. 古い議論や破棄済み前提が残っていないかを確認する。
4. 技術的な矛盾・重複・不足を修正する。
5. 意味・仕様・留保を固定する。
6. **自然な日本語となることを最重要視して全文をドラフトし直す。**
7. 再ドラフトによって意味の強度、条件、例外が変わっていないか最終監査する。

第6工程は省略しない。

## Audit priorities

1. `product/value`, `product/vision`, `product/principles`
2. `plan/adr`, `plan/issue`, `plan/registry.yaml`
3. `requirements`
4. `architecture`, `contracts`
5. `plan/rebaseline`等の報告・計画文書
6. repository README、補助文書

## Progress — 2026-08-31

### Product Value / Vision / Principles

今回の優先監査で次を完了した。

- `product/README.md`
- `product/value/SOZA_PRODUCT_VALUE.md`
- `product/value/SOZA_VALUE_MODEL.md`
- `product/value/SOZA_VALUE_SCENARIOS.md`
- `product/value/SOZA_VALUE_TRACEABILITY.md`
- `product/vision/SOZA_PRODUCT_VISION.md`
- `product/principles/SOZA_PRODUCT_PRINCIPLES.md`

Product Valueについて、価値階層、価値衝突時の優先規則、Core昇格基準、V1〜V9のvalidation axis、Evidence level、Value Scenario、価値定義と価値実証の非同一性まで再整理した。

`product/README.md`では、Product Value / Value Model / Vision / Principles / Value Scenario / Traceabilityの役割、権威関係、変更規則を一つの索引へ整理した。

### ADR

ADR-0001〜ADR-0019を全文で最新Product Valueへ戻して監査した。

- ADR-0001〜ADR-0018: 既存DecisionにProduct Valueとの明白な矛盾なし。
- ADR-0018: Value ScenarioとEvidence Calibrationを含むProduct Value governanceへ精緻化。
- ADR-0019: Provider-neutral Capability Observation境界を新規Accepted。
- `SOZA_VALUE_TRACEABILITY.md`で各ADRとV1〜V9 / Value Scenarioの関係を明示した。

### Issue

ISSUE-000001〜ISSUE-000025を本文まで再監査した。

今回の主な変更:

- ISSUE-000019: ADR-0017のAccepted Decisionに基づきResolved。
- ISSUE-000020: ADR-0019に基づきDecision boundaryをResolvedとし、actual contract / fixtureをISSUE-000025へ分離。
- ISSUE-000024: Value ScenarioからRequirement / NFR / Acceptanceへ追跡する最優先Issueを追加。
- ISSUE-000025: Provider-neutral Capability Observationのactual contract / fixture実体化Issueを追加。ISSUE-000022完了までBlocked。
- ISSUE-000009: 独自の長いStatus表記を`Blocked`へ正規化し、historical / local candidate Evidenceとactual repository Evidenceを分離。
- ISSUE-000008 / 000010 / 000011 / 000013: `Resolved — 補足`形式の独自Statusを`Resolved`へ正規化し、補足をResolution / Evidence stateへ移した。
- ISSUE-000023: Value Scenario、V1〜V9、Value Traceability、Evidence levelを含む現在のProduct Value governanceへ追随させた。
- ISSUE-000022: actual repository materializationが進行中である実態に合わせて`In Progress`へ更新した。

### Planning convention / registry / management scripts

- `plan/README.md`: 文書階層、Evidence level、Product Value trace、自然な日本語ドラフト工程を基線化済み。
- `plan/registry.yaml`: ADR-0019、ISSUE-000024 / 000025、ISSUE-000019 / 000020のResolved状態、ISSUE-000022のIn Progress状態を含めて正規化。
- registry上で見つかったADR-0010↔ISSUE-000011、ADR-0013↔ISSUE-000013の関連非対称を補正した。
- ADR / Issue template: Product Value trace、Evidence強度、自然な日本語レビューを含む現在の規約へ更新した。
- `plan/scripts/check_plan_registry.py`: ID桁数、本文ID、Status、registry全件収載、参照先、ADR↔Issue関連対称性を検査する管理スクリプトを追加した。
- `plan/scripts/next_plan_id.py`: actual treeから次のADR / Issue IDを算出する補助を追加した。
- `plan/scripts/README.md`: 管理スクリプトの責務・非責務を文書化した。
- `.github/workflows/plan-integrity.yml`: pull request / develop / mainでplanning metadataの整合を検査する最小CIを追加した。

管理スクリプトのPASSはplanning metadataの整合だけを示し、Product Valueの実証や実装完成を意味しない。

### Repository README

旧Phase 1 candidate bundleをactual treeのように列挙していたルートREADMEを、現在のProduct / Planning baselineへ再基線化した。

- actual treeに存在しない`requirements/`、`architecture/`、`contracts/`、`runtime/`、`tools/`を実体化済みとして扱わない。
- historical / local candidateとactual repository Evidenceを分離する。
- Product Value文書を最初に読む導線へ変更する。
- ADR / Issueの現在状態を最新registryへ合わせる。
- releaseを主張しない。

### KJ source

次のKJ文書をDecision sourceとして利用し、ADR / Issueへ反映した。

- `plan/kj/2026-08-31_RequirementInquiry_AuthorizationEvidence_ラウンドKJ.md`
- `plan/kj/2026-08-31_ReferenceModel_CapabilityObservation_ラウンドKJ.md`
- `plan/kj/2026-08-31_TEI設計系列_ラウンドKJ統合.md`

KJ法は最終文書の主題にせず、判断を立ち上げる思考・統合の源泉として利用する。

## Remaining scope

優先度順に次を継続する。

1. ISSUE-000024に基づくRequirements / Acceptance Scenariosの再基線化。
2. ISSUE-000022に基づくactual repository materializationとEvidence claim再整合。
3. actual treeへ移すArchitecture / Contractsについて、最新Product Value / ADRへ戻した自然な日本語監査。
4. historical / local candidateのreportや補助資料について、actual treeへ残すものとhistorical onlyにするものを整理する。
5. historical資料のうち原文保存が必要なものは改変せず、案内文・現行評価を別途整備する。

## Acceptance criteria

- 固定100倍基準が正本として残らない。
- X-TEAを現行Product名として扱わない。
- TEIをSOZA内部Runtimeと誤読させる記述を残さない。
- planning、design、historical/local candidate、actual repository、executable conformance、operational evidence、adoption / outcome evidenceを区別する。
- 重要な`!=`境界は、式だけでなく自然な日本語でも説明する。
- Product Valueとの関係を重要な文書から追跡できる。
- 再ドラフト後に技術的意味差分を監査する。
- 未決事項を読みやすさのために勝手に確定しない。

## Completion criteria

このIssueは、activeな日本語開発文書が一度すべて自然な日本語ドラフト工程を通り、以後は通常の文書作成手順だけで同じ品質ゲートを維持できる状態になった時点でResolvedとする。

新しい文書が追加されるたびにこのIssueを恒久的にOpenへ戻す必要はない。通常運用でレビュー工程を維持できることが完了条件である。

## Non-goals

技術用語をすべて日本語へ翻訳したり、読みやすさのために未決事項を勝手に確定したりしない。自然な日本語と技術的精度を両立させる。

## Natural Japanese review

今回のProduct Value / ADR / Issue / README / planning management audit結果を反映した後、進捗・残件・Evidence境界の意味を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済み。
