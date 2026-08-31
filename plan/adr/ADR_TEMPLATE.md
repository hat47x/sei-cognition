# ADR-XXXX: タイトル

Status: **Proposed**  
Related Issue: **ISSUE-XXXXXX**  
Updated: YYYY-MM-DD

## Context

何を判断する必要があるのかを書く。

Product Value、Requirement、既存ADR、Architecture、Contractとの関係を必要な範囲で示し、現在確認できるEvidenceと未確認事項を分ける。

historical / local candidateとactual repositoryの状態が異なる場合は、その差を明示する。過去の候補やPASSを、現在の実体やcurrent PASSとして扱わない。

## Product Value trace

Core境界、Product Boundary、高影響なDecision、重要なEvidence claimを扱うADRでは、少なくとも次を確認する。

- 関連するProduct Value / Value Model（V1〜V8）
- 関連するREQ / SCN、または同等の具体Scenario
- 守る意味境界
- 現在確認できるEvidenceの高さ

局所的で上位追跡を追加しても意味が増えない判断では、形式的に欄を埋めることを目的にしない。その場合も、上位追跡が不要であることを判断したうえで進める。

## Decision

採用する判断を、読み手が独立して理解できる自然な日本語で書く。

重要な非同一性は必要に応じて短い式でも示すが、式だけに頼らず本文でも説明する。

```text
A != B
```

Decision boundaryとimplementation statusを分ける。意味上の判断がAcceptedでも、Schema、Fixture、Runtime、Release、Production operation等が未実装・未検証なら、その状態を別に記す。

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

actual use、複数Provider、複数domain、新しい反証Evidence、将来の技術変化等、判断を覆し得る条件を可能な範囲で具体化する。

## Evidence

必要なものだけを記載する。

- Product Value / REQ / SCN
- KJ / Architecture / Contract
- Fixture / Test / CI
- historical / local candidate evidence
- actual repository evidence
- Release evidence
- Operational evidence
- Adoption / Outcome evidence
- 外部資料等

Evidenceの高さは次を混同しない。

```text
Design Evidence
  != Executable Evidence
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

存在しないEvidenceを形式的に埋めない。未確認は未確認のまま残し、`Not Yet Verified`をFAILやPASSへ読み替えない。

## Natural Japanese review

内容・構造を作成し、Product Value、Requirement、既存ADR、Architecture / Contract、actual Evidenceとの技術的一貫性を確認する。意味・仕様・留保・Evidence強度をいったん固定した後、**自然な日本語となることを最重要視して全文をドラフトし直す。** 最後に、再ドラフトによって要求強度、条件、例外、Evidenceの高さが変わっていないか最終意味監査を行う。
