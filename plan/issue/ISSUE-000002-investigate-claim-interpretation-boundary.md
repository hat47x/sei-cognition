# ISSUE-000002: Claim / Interpretationの境界を調査する

Status: **Resolved**  
Priority: **3**  
Related ADRs: **ADR-0002**  
Updated: 2026-08-31

## Goal

資料に書かれている内容、そこからの解釈、仮説、Method固有の統合物を区別するために、Universal `Claim` / `Interpretation`型が必要かを検討する。

## Investigation

原資料→SNS紹介→紹介者の推論、複数Observation→KJ統合、文化体系→research question、同一Sourceへの複数Interpretation等を比較した。

その結果、現時点ではObservation、Hypothesis、Method固有Artifact、Derivation、EpistemicSeam、Provenance、EvidenceUseの組み合わせで必要な意味差を保持できることを確認した。

## Resolution

Universal `Claim` / `Interpretation`をv1 Coreへ追加しない。Source assertionを世界のTruthへ自動昇格させず、解釈は外在化して由来を辿れるようにする。

再検討条件はADR-0002へ移したため、本IssueはResolvedとする。

## Natural Japanese review

Architecture baselineへ戻して内容を照合した後、自然な日本語となることを最重要視して全文を再ドラフトし、意味監査を実施済み。
