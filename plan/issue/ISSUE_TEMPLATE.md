# ISSUE-XXXXXX: タイトル

Status: **Open**  
Priority: **N**  
Related ADRs: **—**  
Updated: YYYY-MM-DD

## Goal

このIssueで何を決定可能・検証可能な状態にするかを書く。

「調査する」「実装する」だけで終わらせず、何が揃えば次のDecision、ADR、Requirement更新、Architecture / Contract、実装、Evidenceへ進めるのかを明示する。

## Background

なぜ今この課題が必要かを書く。

事実、推論、historical / local candidate、actual repositoryの状態、未確認事項を必要に応じて分ける。存在しない成果物や過去PASSをcurrent Evidenceとして扱わない。

## Product Value trace

重要Issueでは、可能な範囲で次を記す。

- 関連するProduct Value / Value Model（V1〜V8）
- 関連するREQ / SCN、または同等の具体Scenario
- 解消したい価値上・設計上のgap
- 現在のEvidenceの高さと、次に必要なEvidenceの高さ

すべてのIssueへ機械的に同じ追跡を要求しない。ただし、Core境界、Product Boundary、Evidence claim、重要なAcceptanceを扱うIssueでは省略しない。

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

文書、ADR、Schema、Fixture、Runtime、CI、Operational Evidence等を区別し、未実装・未検証のものを完了扱いしない。

## Evidence boundary

必要に応じて、現在確認したEvidenceと今回の非対象を明示する。

```text
Design Evidence
  != Executable Evidence
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

一つの層のPASSを次の層へ自動継承しない。`Not Yet Verified`はFAILと同じではないが、PASSでもない。

## Dependencies / blocked by

依存がある場合は、何が揃うまで何を進められないかを書く。

Statusを`Blocked — 理由`のような独自文字列へ拡張せず、Statusは規定値を使い、blocked reasonやdependencyを本文へ分ける。

## Resolution / reopen conditions

Open中は完了条件を書く。Resolved時は実際の結論、Decisionを受けるADR、後続Issue、必要なら再開条件へ書き換える。

「ADRがAcceptedになった」「Schema / Fixtureが実体化した」「CIがPASSした」「Releaseした」「実運用で成立した」「利用者価値が確認された」を同一の完了状態として扱わない。

## Natural Japanese review

内容・構造を作成し、Product Value、Requirement、Accepted ADR、Architecture / Contract、actual Evidenceとの技術的一貫性を確認する。意味・仕様・留保・Evidence強度をいったん固定した後、**自然な日本語となることを最重要視して全文をドラフトし直す。** 最後に、再ドラフトによって要求強度、条件、例外、Evidenceの高さが変わっていないか最終意味監査を行う。
