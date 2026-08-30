# ISSUE-000001: 「移動する将来基準」をArchitecture Reviewへ落とし込む

Status: **Resolved**  
Priority: **4**  
Related ADRs: **ADR-0001**  
Updated: 2026-08-31

## Goal

ADR-0001の将来基準を、固定倍率のperformance testや主観的な未来予想へ変質させず、Core候補を見直すための実用的なArchitecture Reviewへ落とし込む。

## Questions considered

- 評価時点の「現在地」を何から確認するか。
- 10〜50倍程度先という距離を、偽精度なしにどう使うか。
- 現在の制約への過適合をどう見つけるか。
- 将来性だけを理由に現在必要な意味を削らないために何を確認するか。
- いつ再評価するか。
- 過去判断が新しい現在地から覆った場合に、ADRやRequirementをどう更新するか。

## Resolution

Architecture Reviewでは、耐久的な概念と現在依存のmechanismを意図的に混ぜて比較する。

Core候補については、現在の実務上の意味、技術進歩後にも残る意味差、Provider / Method / Profile / Projectionへの配置可能性、具体Scenarioでの必要性を確認する。

10〜50という目安をscoreへ変換しない。主要releaseやArchitecture Rebaseline、技術環境の大きな変化を再評価契機とする。

この結果をADR-0001へ反映し、本IssueはResolvedとする。

## Natural Japanese review

最新ADRへ照合した後、自然な日本語となることを最重要視して全文を再ドラフトし、意味監査を実施済み。
