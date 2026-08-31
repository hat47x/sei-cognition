# ISSUE-000015: 既存の開発文書を自然な日本語で再監査する

Status: **In Progress**  
Priority: **1**  
Related ADRs: **—**  
Updated: 2026-08-31

## 目的

SOZAの既存開発文書を、技術的な意味・仕様・留保・Evidence強度を変えず、**自然な日本語となることを最重要視して全文をドラフトし直す工程**へ通す。

この作業は一度限りの文章校正ではありません。新規・更新文書でも同じ工程を必須とし、継続的な品質ゲートとして扱います。

## 必須工程

1. 文書の目的と決定範囲を確認する。
2. 最新のProduct Value、Requirement、ADR、Architecture、Contract、actual Evidenceとの整合を確認する。
3. 古い議論、破棄済み前提、古いEvidence記述が残っていないか確認する。
4. 技術的な矛盾、重複、不足を修正する。
5. 意味、仕様、留保、Evidence強度をいったん固定する。
6. **自然な日本語となることを最重要視して全文をドラフトし直す。**
7. 再ドラフトで要求強度、条件、例外、Evidenceの高さが変わっていないか最終監査する。

詳細は`plan/DOCUMENT_AUTHORING_STANDARD.md`を正とします。

## Evidenceの現在基準

```text
Design Evidence
  != Executable Evidence
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

旧文書が4段階を前提としている場合はcurrent 5段階へ同期します。ただし、上位Evidenceが未確認であることを理由に、確認済みの下位Evidenceまで弱めたり、逆に自動昇格させたりしません。

## 監査管理

`plan/document_review_registry.yaml`をcurrent Markdown開発文書の監査台帳とします。

状態:

- `revised`
- `reviewed-no-change`
- `excluded-historical`
- `pending`

新規文書は作業単位の中で本標準を完了できる場合、直接`revised`または`reviewed-no-change`へ登録します。

## 完了済み範囲

### Product層

Product Value、Value Model、Value Acceptance、Value Traceability、Vision、Principles、Product READMEをcurrent上位baselineへ整合済みです。

### ADR / Issue

ADR-0001〜ADR-0024、ISSUE-000001〜ISSUE-000037をcurrent Product Value / Requirements / Architecture / Contract / Runtimeから逆向きに全件監査済みです。

historical Milestone、Issue自身のclosure、後続Executable Evidence、未検証のProduction / Release / Operational / Adoption / Outcomeを分け直しました。

ISSUE-000037では、REQ-0001〜REQ-0022のEvidence表示をcurrent 5段階へ全文再整合しています。

### Planning品質文書

`plan/README.md`、Development Workflow、Document Authoring Standard、Review Report、planning scripts READMEをcurrent 5段階Evidenceと文書監査台帳へ同期済みです。

### Requirements層

次のcurrent Requirements文書をすべて監査しました。

- `requirements/README.md`
- `requirements/PRODUCT_REQUIREMENTS.md`
- `requirements/ACCEPTANCE_SCENARIOS.md`
- `requirements/history/HISTORICAL_REQUIREMENT_MAPPING.md`

`PRODUCT_REQUIREMENTS.md`はISSUE-000037でREQ-0001〜REQ-0022を5段階Evidenceへ再整合しました。

SCN-0001〜0017はcurrent Contract / Runtime / Provider Adapterへ一件ずつ照合し、実際に確認できたScenarioだけExecutable Evidenceを限定的に更新しました。Release / Operational / Adoption / Outcomeへは引き上げていません。

historical mappingも、旧local PASSとcurrent Executable Evidenceを分離したまま5段階Evidenceへ同期しています。

**Requirements層のcurrent Markdown文書監査は完了しました。**

### Architecture層

次のcurrent Architecture文書をすべて監査しました。

- `architecture/README.md`
- `architecture/SOZA_REFERENCE_ARCHITECTURE.md`
- `architecture/TRACEABILITY.md`
- `architecture/history/HISTORICAL_ARCHITECTURE_MAPPING.md`

Reference Architectureでは、historical時点の「Contract候補」「Representation未固定」という表現と、currentで既にAccepted・実体化されている4 Contract family、2 Representation Profile、first semantic runtime、synthetic Provider Adapterの現在地を分離しました。

Evidenceは5段階へ統一し、Contract / Profile / runtime / AdapterのCI成功を限定されたExecutable Evidenceとして反映しています。一方、Architecture全体の実装完了、production Provider / TEI integration、Release、Operational、Adoption / Outcomeへは昇格させていません。

historical mappingでは、過去のJCS / SHA-256 / Go等の選択をcurrentへ自動継承せず、current ADRで改めて採用したProfile・実装と区別しています。historical M47 digest mappingは引き続きISSUE-000034の独立Blocked事項です。

**Architecture層のcurrent Markdown文書監査は完了しました。**

### Contracts / Representation Profiles層

次のcurrent Contract / Profile文書を監査しました。

- `contracts/README.md`
- `contracts/CONTRACT_CATALOG.md`
- `contracts/CONFORMANCE_EVIDENCE_2026-08-31.md`
- `contracts/semantic-reference/SOZA_SEMANTIC_REFERENCE_v1alpha1.md`
- `contracts/decision-memory/SOZA_DECISION_MEMORY_v1alpha1.md`
- `contracts/capability/SOZA_CAPABILITY_OBSERVATION_v1alpha1.md`
- `contracts/interchange/SOZA_SEMANTIC_INTERCHANGE_v1alpha1.md`
- `contracts/TRACEABILITY.md`
- `contracts/profiles/README.md`
- `contracts/profiles/SOZA_JCS_SHA256_PROFILE_v1alpha1.md`
- `contracts/profiles/SOZA_RAW_BYTES_SHA256_PROFILE_v1alpha1.md`
- `contracts/profiles/CONFORMANCE_EVIDENCE_2026-08-31.md`
- `contracts/history/HISTORICAL_CONTRACT_MAPPING.md`

4 Contract Definitionでは規範意味を変更せず、実体化前のEvidence記述をcurrent JSON Schema / 17 fixture / first semantic runtime / synthetic Provider Adapterへ再基線化しました。

Representation Profileでは、ADR-0023で`soza.jcs+sha256/v1alpha1`と`soza.raw-bytes+sha256/v1alpha1`がAccepted済みであることをcurrent正本へ揃え、Profile Definitionとverifier implementationを引き続き分離しています。RFC 8785、SHA-256、数値精度、Unicode非正規化、raw-bytesの入力規則等の技術条件は維持しました。

Profile Evidence文書に残っていたhistorical M47 digest recoveryの追跡先`ISSUE-000032`という誤記は、current正本に合わせて`ISSUE-000034`へ訂正しました。

監査後の回帰確認:

- Contract Conformance — Run `33389973776`: **success**
- Representation Profile Conformance — Run `33389973772`: **success**
- Semantic Runtime Conformance — Run `33389973787`: **success**

これらはそれぞれのtested scopeに限定したExecutable Evidenceです。Release / Operational / Adoption / Outcomeへは昇格させていません。

**Contracts / Representation Profiles層のcurrent Markdown文書監査は完了しました。**

## 未完了範囲

`plan/document_review_registry.yaml`で`pending`となっているcurrent文書を上位から順に監査します。

次の優先順:

1. Runtime Evidence
2. fixture README
3. KJ統合文書
4. ADR / Issue Template

historical M47 digest Profile recoveryはISSUE-000034の独立Blocked事項であり、この文書監査の完了条件へ混ぜません。

## CI運用

CI failureを検出した場合は、その時点で原因を特定・修正し、successを確認してから次の作業へ進みます。

Requirements文書を変更した場合はRequirements Registry Conformanceを確認し、Plan文書変更後はPlan integrityも確認します。Contract / Representation Profile文書を変更した場合は、変更内容に応じてContract Conformance、Representation Profile Conformance、Semantic Runtime Conformanceへの影響も確認します。

## Acceptance criteria

- [x] 固定100倍基準をcurrent Product正本から除去し、10〜50×のmoving horizonへ統一した。
- [x] X-TEAをcurrent Product名として扱わない。
- [x] TEIをSOZA内部Runtimeと誤読させないProduct / Architecture境界を整備した。
- [x] 5段階Evidenceをcurrent上位文書とPlanning規約へ反映した。
- [x] REQ / SCNのcurrent正本とhistorical mappingを分離した。
- [x] ADR-0001〜ADR-0024をcurrent baselineから全件再監査した。
- [x] ISSUE-000001〜ISSUE-000037をcurrent baselineから全件再監査した。
- [x] current文書の監査対象一覧を`plan/document_review_registry.yaml`へ実体化した。
- [x] Requirements層のcurrent Markdown文書を全件再監査した。
- [x] Architecture層のcurrent Markdown文書を全件再監査した。
- [x] Contracts / Representation Profiles層のcurrent Markdown文書を全件再監査した。
- [ ] `document_review_registry.yaml`のcurrent対象から`pending`をなくす。

`pending`が残る間は本IssueをResolvedにしません。

## 対象外

技術用語をすべて日本語へ翻訳することは目的としません。

原文自体がEvidenceとなる資料、machine-readable Schema、固定fixture、source code等を、日本語化のためだけに改変しません。

読みやすくするために未決事項を勝手に確定したり、Evidenceより強い状態へ書き換えたりしません。

## Natural Japanese review

Product、Planning、Requirements、Architectureに続いて、4 Contract family、2 Representation Profile、Contract / Profile Evidence、historical mappingをcurrent Product Value、REQ-0001〜0022、SCN-0001〜0017、ADR-0001〜0024、actual Schema / fixture / first runtime / synthetic Provider Adapterへ戻って再監査しました。規範意味や技術条件を変えず、historical候補とcurrentでAccepted・実体化・限定検証済みの境界を分け、Evidenceを5段階へ統一しています。その後、意味、監査条件、Evidence強度を変えない範囲で自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
