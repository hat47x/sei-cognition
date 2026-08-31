# ADR-XXXX: タイトル

Status: **Proposed**  
Related Issue: **ISSUE-XXXXXX**  
Updated: YYYY-MM-DD

## Context

何を判断する必要があるのかを書く。

少なくとも、必要な範囲で次を分けて示す。

- Product Value / Value Modelとの関係
- Requirement / Acceptance Scenarioとの関係
- 既存ADRとの関係
- 現在確認できているEvidence
- 未確認事項、Unknown、Conflict
- 今回のDecisionで固定しない範囲

背景説明だけで結論を先取りしない。

## Decision

採用する判断を、読み手がこのADRだけでも意味境界を理解できる自然な日本語で書く。

重要な非同一性は必要に応じて短い式でも示すが、式だけに頼らず本文でも説明する。

```text
A != B
```

Product Valueより下位の実装都合だけを理由に、上位の意味・不確実性・Responsibility・Provenanceを失わせない。

## Alternatives considered

採用しなかった主要案と、その理由を書く。

単に「複雑だから」「将来不要そうだから」で終えず、Product Value、相互運用、historical reconstruction、実装負荷等のどの観点で差が生じるかを示す。

## Consequences

### Positive

- 

### Costs / Risks

- 

新しい抽象・Contract・Core要素を増やす場合は、その維持コストと将来の削除条件も確認する。

## Revisit conditions

何が起きれば判断を再検討するかを書く。「将来必要なら」だけで終わらせない。

例:

- 前提としていたProduct Value / Requirementが変わった。
- 異なるProviderや実装で同じ境界が成立しないEvidenceが得られた。
- current Designでは保持できないhistorical reconstruction要求が確認された。
- 実装・運用EvidenceがDecision時の仮定と継続的に矛盾した。

## Evidence

このADRを支えるEvidenceと、その高さを明示する。

```text
Design Evidence
  != Executable Evidence
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

候補:

- Product Requirement / Acceptance Scenario / NFR
- KJ working record
- Architecture / Contract / Representation Profile
- fixture / validator / test / CI result
- runtime / Provider Adapter Evidence
- 外部資料

CI successやfixture PASSを、Release / Operational / Adoption / Outcomeへ自動昇格しない。

## Follow-up

必要な場合だけ、後続Issue、Contract変更、fixture、Runtime slice、移行作業等を書く。

ADRをAcceptedにすることと、後続実装・Releaseが完了することを同一視しない。

## Natural Japanese review

内容・構造を作成して技術的一貫性を確認した後、意味、要求強度、仕様、留保、Evidence強度を固定する。そのうえで、**自然な日本語となることを最重要視して全文をドラフトし直す。** 最後に再ドラフト前後を照合し、Decision、例外、非同一性、Revisit条件、Evidenceの高さが変わっていないことを再監査する。
