# ADR-XXXX: タイトル

Status: **Proposed**  
Related Issue: **ISSUE-XXXXXX**  
Updated: YYYY-MM-DD

## Context

何を判断する必要があるのかを書く。

Product Value / Value Model / Requirement / 既存ADRとの関係、現在確認できるEvidence、未確認事項を分ける。historical / local candidateとactual repositoryのEvidenceが異なる場合も明示する。

## Product Value trace

Core境界、Product Boundary、高影響なDecision、Evidence claim等の重要ADRでは、少なくとも次を確認する。

- 関連するProduct Value / Value Model validation axis
- 関連するValue Scenarioまたは同等の具体Scenario
- 守る意味境界
- 現時点のEvidence level

軽微な局所判断では、意味のある追跡がない場合に無理に欄を埋めない。その場合も「なぜ上位追跡が不要か」を判断する。

## Decision

採用する判断を、読み手が独立して理解できる自然な日本語で書く。

重要な非同一性は必要に応じて短い式でも示すが、式だけに頼らず本文でも説明する。

```text
A != B
```

Decision boundaryとimplementation statusを分ける。意味上の判断がAcceptedでも、schema、runtime、fixture、production operation等が未実装なら、その状態を明示する。

## Alternatives considered

採用しなかった主要案と、その理由を書く。

単に「複雑」「好みではない」で終わらせず、Product Value、意味境界、Evidence、将来耐性等のどこで差が生じるかを示す。

## Consequences

### Positive

- 

### Costs / Risks

- 

## Revisit conditions

何が起きれば判断を再検討するかを書く。「将来必要なら」だけで終わらせない。

actual use、複数Provider、複数domain、新しいEvidence等、判断を覆し得る条件を可能な範囲で具体化する。

## Evidence

- Product Value / Value Scenario
- Product Requirement / NFR
- KJ / Architecture / Fixture / Test
- historical / local candidate evidence
- actual repository evidence
- operational / adoption / outcome evidence
- 外部資料等

存在しないEvidence levelを埋める必要はない。確認できていないものは未確認のまま残す。

## Natural Japanese review

内容・構造を作成し技術的一貫性を確認した後、意味・仕様・留保・Evidence強度を変えず、自然な日本語となることを最重要視して全文をドラフトし直す。最後に意味差分を再監査する。
