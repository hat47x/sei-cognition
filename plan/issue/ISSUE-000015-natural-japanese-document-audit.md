# ISSUE-000015: 既存の開発文書を自然な日本語で再監査する

Status: **Resolved**  
Priority: **1**  
Related ADRs: **—**  
Updated: 2026-09-01

## 目的

SOZAの既存開発文書を、技術的な意味、仕様、留保、Evidence強度を変えず、**自然な日本語となることを最重要視して全文をドラフトし直す工程**へ通す。

このIssueは一度限りの校正作業ではなく、今後の新規・更新文書にも同じ工程を組み込むための品質基線を確立することを目的とした。

## 確立した標準工程

1. 文書の目的と決定範囲を確認する。
2. 最新のProduct Value、Requirement、ADR、Architecture、Contract、actual Evidenceとの整合を確認する。
3. 古い議論、破棄済み前提、古いEvidence記述が残っていないか確認する。
4. 技術的な矛盾、重複、不足を修正する。
5. 意味、仕様、留保、Evidence強度を固定する。
6. **自然な日本語となることを最重要視して全文をドラフトし直す。**
7. 再ドラフトで要求強度、条件、例外、Evidenceの高さが変わっていないか最終監査する。

詳細な通常運用は`plan/DOCUMENT_AUTHORING_STANDARD.md`、`plan/DEVELOPMENT_WORKFLOW.md`、ADR / Issue Templateへ反映済みである。

## Evidenceの現在基準

```text
Design Evidence
  != Executable Evidence
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

確認済みの下位Evidenceを、上位Evidenceの未確認を理由に弱めない。同時に、CI PASSやfixture PASSをRelease / Operational / Adoption / Outcomeへ自動昇格しない。

## 完了した監査範囲

`plan/document_review_registry.yaml`をcurrent Markdown開発文書の監査台帳として使用し、2026-09-01時点で`pending: []`へ到達した。

監査済みの主な層は次のとおりである。

- Product Value / Value Model / Value Acceptance / Value Traceability / Vision / Principles
- ADR-0001〜ADR-0024
- ISSUE-000001〜ISSUE-000037
- Requirements / Acceptance Scenarios / historical mapping
- Reference Architecture / Traceability / historical mapping
- 4 Contract family / Contract Catalog / Contract Evidence
- JCS / raw-bytes Representation Profile / Profile Evidence
- first Semantic Runtime / synthetic Provider Adapter Evidence
- Contract fixture / synthetic Provider fixture README
- Planning品質文書
- ADR / Issue Template
- KJ working documents

## 主な是正

### currentとhistoricalの分離

historical Milestone、旧X-TEA / TEI設計候補、過去のlocal PASSをcurrentの成立事実として読める箇所を整理した。

historical M47 digest Profile recoveryは`ISSUE-000034`の独立Blocked事項として残し、本Issueの完了条件へ混ぜていない。

### Product Valueからの逆向き監査

Product Valueを上位authorityとし、Requirements、ADR、Architecture、Contract、Runtimeへ逆向きに照合した。

Recommendation / Decision / Authority / Execution、Capability / Provider、Unknown / negative fact、Design / Executable等の非同一性が文書間で崩れていないことを確認した。

### Evidenceの5段階化

旧4段階表現や、CI PASSを実装完了・Release readinessへ広げて読める記述をcurrent 5段階Evidenceへ同期した。

### Representation Profile

`soza.jcs+sha256/v1alpha1`と`soza.raw-bytes+sha256/v1alpha1`がADR-0023でAccepted済みであることへ文書を揃えた。

Profile Evidenceに残っていたhistorical M47追跡先`ISSUE-000032`の誤記を、正しい`ISSUE-000034`へ訂正した。

### KJ working documents

KJの生カード、束ね、核融合法、残差、当時のDecision preparationは、現在の結論へ合わせて後知恵で書き換えない。

`plan/kj/README.md`を新設し、原記録とcurrent authorityの関係を別層で明示した。

- Requirement Inquiry → ADR-0015
- Authorization Evidence → ADR-0016
- Reference Model / Cognitive Method → ADR-0017
- Provider-neutral Capability Observation → ADR-0019
- Provider Adapter observation mapping → ADR-0024

## CI / verification

監査中にCI failureを検出した場合は、原因を解消してsuccessを確認してから後続作業へ進めた。

主要な回帰確認には次を含む。

- Requirements Registry Conformance: success
- Plan integrity: success
- Contract Conformance: success
- Representation Profile Conformance: success
- Semantic Runtime Conformance: success

これらは各workflowが検査する範囲のExecutable Evidenceであり、Release / Operational / Adoption / Outcomeを意味しない。

## Resolution

次の条件を満たしたため、本IssueをResolvedとする。

- [x] 固定100倍基準をcurrent Product正本から除去し、10〜50×のmoving horizonへ統一した。
- [x] X-TEAをcurrent Product名として扱わない。
- [x] TEIをSOZA内部Runtimeと誤読させないProduct / Architecture境界を整備した。
- [x] 5段階Evidenceをcurrent上位文書とPlanning規約へ反映した。
- [x] REQ / SCNのcurrent正本とhistorical mappingを分離した。
- [x] ADR-0001〜ADR-0024をcurrent baselineから全件再監査した。
- [x] ISSUE-000001〜ISSUE-000037をcurrent baselineから全件再監査した。
- [x] current Markdown開発文書の監査台帳を実体化した。
- [x] Product、Requirements、Architecture、Contracts / Profiles、Runtime Evidence、fixture README、KJ文書、Templateを監査した。
- [x] `plan/document_review_registry.yaml`から`pending`をなくした。
- [x] 自然な日本語全文再ドラフトを通常の文書作成・更新工程へ組み込んだ。

## 今後の運用

本Issueを閉じても文書品質監査は終了しない。

新規・更新文書では、今回確立した工程を通常のDefinition of Doneとして適用する。将来、文書監査標準自体に構造的な欠陥が見つかった場合は、本Issueを形式的に再開するより、影響範囲を明示した新しいIssueを作ることを基本とする。

## Reopen conditions

本Issueそのものを再開するのは、次のように「今回の全件監査が未完了だった」と判断すべき事実が見つかった場合に限る。

- 2026-09-01時点で存在していたcurrent Markdown開発文書が監査台帳から漏れていた。
- `reviewed-no-change`または`excluded-historical`の判断が、原文保全という目的では説明できない誤分類だった。
- 監査によって仕様・Evidence強度を意図せず変更していたことが判明した。

## Natural Japanese review

全対象文書、監査台帳、current Product Value、REQ-0001〜0022、SCN-0001〜0017、ADR-0001〜0024、4 Contract family、2 Representation Profile、first Semantic Runtime、synthetic Provider Adapter、actual CI結果へ戻って最終監査した。その後、完了条件、未検証範囲、KJ原記録の扱いを固定し、意味・仕様・留保・Evidence強度を変えない範囲で自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。
