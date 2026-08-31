# ISSUE-000015: 既存の開発文書を自然な日本語で再監査する

Status: **Resolved**  
Priority: **1**  
Related ADRs: **—**  
Updated: 2026-09-01

## 目的

SOZAの既存開発文書を、技術的な意味・仕様・留保・Evidence強度を変えず、**自然な日本語となることを最重要視して全文をドラフトし直す工程**へ通す。

この作業は一度限りの文章校正ではない。新規・更新文書でも同じ工程を必須とし、継続的な品質ゲートとして扱う。

## 必須工程

1. 文書の目的と決定範囲を確認する。
2. 最新のProduct Value、Requirement、ADR、Architecture、Contract、actual Evidenceとの整合を確認する。
3. 古い議論、破棄済み前提、古いEvidence記述が残っていないか確認する。
4. 技術的な矛盾、重複、不足を修正する。
5. 意味、仕様、留保、Evidence強度をいったん固定する。
6. **自然な日本語となることを最重要視して全文をドラフトし直す。**
7. 再ドラフトで要求強度、条件、例外、Evidenceの高さが変わっていないか最終監査する。

詳細は`plan/DOCUMENT_AUTHORING_STANDARD.md`を正とする。

## Evidenceの現在基準

```text
Design Evidence
  != Executable Evidence
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

旧文書が4段階を前提としていた場合はcurrent 5段階へ同期した。ただし、上位Evidenceが未確認であることを理由に確認済みの下位Evidenceまで弱めたり、逆に自動昇格させたりしていない。

## 監査管理

`plan/document_review_registry.yaml`をcurrent Markdown開発文書の監査台帳とする。

状態:

- `revised`
- `reviewed-no-change`
- `excluded-historical`
- `pending`

2026-09-01時点で、今回のcurrent監査対象に`pending`は残っていない。

## 完了した監査範囲

### Product

Product Value、Value Model、Value Acceptance、Value Traceability、Vision、Principles、Product README、root READMEをcurrent上位baselineへ整合した。

### ADR / Issue / Planning

ADR-0001〜ADR-0024、ISSUE-000001〜ISSUE-000037をcurrent Product Value / Requirements / Architecture / Contract / Runtimeから逆向きに全件監査した。

planning規約、Development Workflow、Document Authoring Standard、planning scripts READMEもcurrent 5段階Evidenceへ同期した。

ADR / Issue Templateについては、Product Value trace、historical / local / actualの分離、5段階Evidence、Decision boundaryとimplementation statusの分離を反映した。

### Requirements

次のcurrent Requirements文書を全件監査した。

- `requirements/README.md`
- `requirements/PRODUCT_REQUIREMENTS.md`
- `requirements/ACCEPTANCE_SCENARIOS.md`
- `requirements/history/HISTORICAL_REQUIREMENT_MAPPING.md`

ISSUE-000037でREQ-0001〜REQ-0022のEvidence表示を5段階へ統一し、synthetic Provider Adapterの限定Executable Evidenceを該当Requirementへ反映した。Release / Operational / Adoption / Outcomeへは昇格させていない。

### Architecture

次を全件監査した。

- `architecture/README.md`
- `architecture/SOZA_REFERENCE_ARCHITECTURE.md`
- `architecture/TRACEABILITY.md`
- `architecture/history/HISTORICAL_ARCHITECTURE_MAPPING.md`

current 4 Contract family、2 Representation Profile、first semantic runtime、synthetic Provider Adapterと、未検証のproduction / Release / Operational / Adoption・Outcomeを分離した。

### Contracts / Representation Profiles

4 Contract Definition、Contract Catalog / README / Traceability / Evidence、2 Representation Profile、Profile Evidence、historical mappingを全件監査した。

規範意味や技術条件を変えず、actual Schema / 17 fixture / first runtime / synthetic Adapterの限定Executable Evidenceへ再基線化した。

### Runtime / Fixtures

次を全文監査し、既に自然な日本語再ドラフトと最終意味監査が完了していることを再確認した。

- `runtime/CONFORMANCE_EVIDENCE_2026-08-31.md`
- `fixtures/contracts/v1alpha1/README.md`
- `fixtures/providers/synthetic/README.md`

### KJ統合文書

次の3文書を全文監査した。

- `plan/kj/2026-08-31_ReferenceModel_CapabilityObservation_ラウンドKJ.md`
- `plan/kj/2026-08-31_RequirementInquiry_AuthorizationEvidence_ラウンドKJ.md`
- `plan/kj/2026-08-31_TEI設計系列_ラウンドKJ統合.md`

これらは生カード、束ね、核融合、Decision preparationを含む**思考過程のsource snapshot**である。後続ADRで採らなかった当時の候補語も含め、現在の結論へ書き換えると設計史を損なうため、`reviewed-no-change`とした。

current Decisionの正本は対応するProduct Value、Requirement、ADR、Architecture / Contractであり、KJ文書自体をcurrent仕様として扱わない。

## 対象外

自然な日本語への改稿を理由に、次のような固定Evidence・machine-readable資産・source codeを変更していない。

- JSON fixture
- JSON Schema
- Go source
- checker / tool source
- GitHub Actions workflow
- 原文自体がEvidenceとなるhistorical資料

これらは通常のcode / schema reviewまたはhistorical provenance管理で扱う。

## Resolution

`plan/document_review_registry.yaml`のcurrent対象から`pending`がなくなり、対象文書は`revised`、`reviewed-no-change`、または理由付き`excluded-historical`のいずれかへ到達した。

したがって、本Issueで予定した**既存current開発文書の全件自然日本語監査は完了**とする。

このclosureは文書品質工程を終了する意味ではない。今後の新規・更新文書では、通常の作成フローとして同じ工程を継続する。

```text
ISSUE-000015 Resolved
  != future document review no longer required
```

## Reopen conditions

次の場合は、本Issueを再開するか、対象が明確なら後続Issueを作成する。

- activeなcurrent文書群に、監査されないまま大量の既存文書が持ち込まれた。
- 自然な日本語工程が通常フローから外れ、継続的に省略される状態になった。
- Evidence強度やhistorical / current境界の誤読が広範囲に再発した。

個々の新規文書の通常reviewだけを理由に、本Issueを恒久的にOpenへ戻さない。

## Acceptance criteria

- [x] 固定100倍基準をcurrent Product正本から除去し、10〜50×のmoving horizonへ統一した。
- [x] X-TEAをcurrent Product名として扱わない。
- [x] TEIをSOZA内部Runtimeと誤読させないProduct / Architecture境界を整備した。
- [x] 5段階Evidenceをcurrent上位文書とPlanning規約へ反映した。
- [x] REQ / SCNのcurrent正本とhistorical mappingを分離した。
- [x] ADR-0001〜ADR-0024をcurrent baselineから全件再監査した。
- [x] ISSUE-000001〜ISSUE-000037をcurrent baselineから全件再監査した。
- [x] Requirements、Architecture、Contracts / Profiles、Runtime Evidence、fixture READMEを全件監査した。
- [x] KJ統合文書をsource snapshotとして全文監査し、改稿しない理由を明示した。
- [x] ADR / Issue Templateをcurrent文書品質・Evidence規約へ更新した。
- [x] `plan/document_review_registry.yaml`のcurrent対象から`pending`をなくした。

## Natural Japanese review

全current監査対象、Product Value、REQ-0001〜0022、SCN-0001〜0017、ADR-0001〜0024、actual Contract / Profile / Runtime / synthetic Provider Adapter Evidenceへ戻って最終照合した。KJ文書では生カードと当時のDecision preparationを保存し、current Decisionの正本と分離した。その後、意味、仕様、留保、Evidence強度、監査完了条件を変えず、自然な日本語となることを最重要視して本Issue全文を再ドラフトし、最終意味監査を実施済みである。
