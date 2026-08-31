# ISSUE-XXXXXX: タイトル

Status: **Open**  
Priority: **N**  
Related ADRs: **—**  
Updated: YYYY-MM-DD

## Goal

このIssueで、何を**決定可能・検証可能な状態**にするかを書く。

「検討する」「整理する」だけで終えず、完了時に何が判別でき、どの成果物へ着地するかを明示する。

## Background

なぜ今この課題が必要かを書く。

必要に応じて次を分ける。

- 確認済みの事実
- 現時点の推論・仮説
- Unknown / Conflict
- historicalな前提とcurrent baselineの差
- Product Value / Requirement / Accepted ADRとの関係

古いMilestoneや旧設計をcurrentの成立事実として扱わない。

## Questions

1. 
2. 
3. 

質問は、IssueのGoalへ答えが返る粒度にする。単なる実装TODOと意味上の未決事項を混在させる場合は、その違いを明示する。

## Constraints

- Product ValueやAccepted ADRから外してはならない条件
- 保持すべき意味・不確実性・Responsibility・Provenance
- Provider / Runtime / UI等へ残すべき境界
- 今回のNon-goal

関連製品との親和性、実装の容易さ、現在のtool都合だけを理由にUniversal Coreへ昇格させない。

## Required scenarios / experiments

1. 
2. 

実験を要求する場合は、何をPASS / FAIL / NOT_VERIFIEDとして読むかをできる限り先に定める。

```text
Design Evidence
  != Executable Evidence
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

下位Evidenceの成立から上位Evidenceを自動推定しない。

## Deliverables

- 

必要に応じて、ADR、Architecture、Contract、Profile、fixture、Runtime、Evidence report等への着地点を書く。

## Resolution

Open中は、どの条件を満たせばResolvedにできるかを書く。

Resolvedへ変更するときは、少なくとも次を現在形で記録する。

- 実際に成立した結論
- 生成・更新した成果物
- 確認できたEvidenceの高さ
- 意図的に残した未完了事項

IssueがResolvedであることと、Release / Operational / Adoption / Outcomeが成立したことを同一視しない。

## Reopen conditions

Resolved後に再開すべき具体条件を書く。

例:

- Accepted ADRの前提を覆すEvidenceが得られた。
- 別Provider / 別実装で現在の境界が成立しない。
- historical reconstructionに必要な情報が失われる事例が見つかった。
- Product Value / Requirementが変更された。

## CI / verification

このIssueで変更する対象に応じ、必要なchecker / workflowを明示する。

CI failureを検出した場合は、原因を特定・解消してsuccessを確認してから後続作業へ進む。

CI successそのものをProduct Value達成やRelease readinessの証明にはしない。

## Natural Japanese review

内容・構造を作成して技術的一貫性を確認した後、意味、要求強度、仕様、留保、Evidence強度を固定する。そのうえで、**自然な日本語となることを最重要視して全文をドラフトし直す。** 最後に再ドラフト前後を照合し、Goal、Questions、Constraints、完了条件、Reopen条件、Evidenceの高さが変わっていないことを再監査する。
