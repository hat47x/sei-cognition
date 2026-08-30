# ISSUE-XXXXXX: タイトル

Status: **Open**  
Priority: **N**  
Related ADRs: **—**  
Updated: YYYY-MM-DD

## Goal

このIssueで何を決定可能・検証可能な状態にするかを書く。

「調査する」だけで終わらず、何が揃えば次のDecision、ADR、Requirement、実装へ進めるのかを明示する。

## Background

なぜ今この課題が必要かを書く。

事実、推論、historical / local candidate、actual repositoryの状態、未確認事項を必要に応じて分ける。存在しない成果物や過去PASSをactual Evidenceとして扱わない。

## Product Value trace

重要Issueでは、可能な範囲で次を記す。

- 関連するProduct Value / Value Model validation axis
- 関連するValue Scenarioまたは同等の具体Scenario
- 解消したい価値上のgap
- 現在のEvidence levelと、必要な次のEvidence level

すべてのIssueへ機械的に同じ追跡を要求しないが、Core境界、Product Boundary、Evidence claim、重要なAcceptanceを扱うIssueでは省略しない。

## Questions

1. 
2. 
3. 

## Constraints

- Product ValueやAccepted ADRから外してはならない条件
- Evidenceを超えて主張してはならないこと
- 今回のNon-goal

## Required scenarios / experiments

1. 
2. 

正常系だけでなく、意味喪失、誤昇格、Unknown / Conflict、negative case等が重要なら含める。

## Deliverables

- 

文書、ADR、schema、fixture、実装等を区別し、未実装のものを完了扱いしない。

## Dependencies / blocked by

依存がある場合は、何が揃うまで何を進められないかを書く。

Statusを`Blocked — 理由`のような独自文字列へ拡張せず、Statusは規定値を使い、理由を本文へ分ける。

## Resolution / reopen conditions

Open中は完了条件を書く。Resolved時は実際の結論、Decisionを受けるADR、後続Issue、必要なら再開条件へ書き換える。

「ADRがAcceptedになった」と「actual implementationが完成した」を混同しない。

## Natural Japanese review

内容・構造を作成し技術的一貫性を確認した後、意味・仕様・留保・Evidence強度を変えず、自然な日本語となることを最重要視して全文をドラフトし直す。最後に意味差分を再監査する。
