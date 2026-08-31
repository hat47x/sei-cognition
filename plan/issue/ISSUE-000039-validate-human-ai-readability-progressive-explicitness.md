# ISSUE-000039: Human / AI ReadabilityとProgressive Explicitnessを再現可能に評価する

Status: **Open**  
Priority: **1**  
Related ADRs: **ADR-0005, ADR-0018, ADR-0020, ADR-0021**  
Updated: 2026-09-01

## Goal

SOZAのV6 Human / AI ReadabilityとV7 Progressive Explicitnessについて、特定のUI技術や製品画面へ早期固定せず、**同じcanonical meaningを人間向けProjectionとmachine-readable representationの双方から回収できること**、および**案件の影響度に応じて明示量を変えても必要な意味を失わないこと**を、再現可能な評価系で検証する。

このIssueの目的は「UIを完成させること」ではない。

```text
Projection evaluation
  != Product UI completion
  != Universal UI ontology
  != Release readiness
```

## Background

current Product Value Traceabilityでは、V1〜V5とV8にはContract、fixture、Representation Profile、first semantic runtime、synthetic Provider Adapter等の限定Executable Evidenceが存在する。

一方、V6 / V7には次のgapが残っている。

### V6 Human / AI Readability

- human-readable Contract Definitionとmachine-readable Schemaは存在する。
- REQ-0019は、人間とAIの双方が同じ意味へ戻れることを要求している。
- SCN-0006ではProjectionを作り直してもcanonical meaningを失わないことを要求している。
- SCN-0013ではsimple viewとmachine-readable representationの意味整合を要求している。
- しかし、具体的なProjectionを使ってbasis、未解決点、Responsibility等を人間が回収できるExecutable Evidenceはまだない。

### V7 Progressive Explicitness

- ADR-0005とREQ-0010で、案件の影響・不確実性・不可逆性等に応じて必要な明示量を段階的に変える境界は定義済みである。
- SCN-0004では低影響案件と高影響案件で必要な明示性が異なることを要求している。
- SCN-0013では簡略表示のためにcanonical meaningを削除しないことを要求している。
- しかし、軽量Projectionと監査・高影響Projectionを同じcanonical sourceから生成・比較する再現可能なEvidenceはまだない。

この状態のままRelease準備やUI実装を先行すると、「意味は厳密だが人間には追いにくい」「簡単に使うためにはcanonical meaningを削る」といった逆転が起こり得る。

## Product Value trace

### Value Axis

- **V6 Human / AI Readability**
- **V7 Progressive Explicitness**

### Requirements

- **REQ-0010** — Progressive Semantic Explicitness
- **REQ-0011** — Projectionを意味上の正本にしない
- **REQ-0019** — 人間とAIの双方が意味を読める
- **REQ-0020** — Evidenceを超える達成主張をしない

### Acceptance Scenarios

- **SCN-0004** — 軽量案件と高影響案件
- **SCN-0006** — Projectionを作り直す
- **SCN-0013** — 簡略UIとcanonical meaningを両立する
- **SCN-0017** — Evidenceが低い段階で達成主張を監査する

### Current Evidence

- Design: V6 / V7ともに境界は定義済み。ただしProjection具体化は一部`Partially Satisfied`。
- Executable: representative Projection / detail-level切替については**Not Yet Verified**。
- Release: **Not Yet Verified**。
- Operational: **Not Yet Verified**。
- Adoption / Outcome: **Not Yet Verified**。

## Questions

1. 同一のcanonical Artifactから、軽量表示と監査向け詳細表示を作っても、意味上必要な情報を失わずに済むか。
2. 人間向けProjectionとmachine-readable representationから、同じbasis、未解決点、Responsibility、重要なEvidence / Authority境界を回収できるか。
3. 低影響案件では不要な詳細を前面へ出さず、高影響案件では必要な詳細を省略しない切替を、固定UIではなくProfile / Policyまたは評価入力として表せるか。
4. Projection固有stateがcanonical semantic stateへ逆流していないことを、どのnegative caseで検査するか。
5. 再現可能なExecutable Evidenceを作るために必要な最小Projection harnessは何か。新しいUniversal ContractやCore概念を追加せずに成立するか。
6. 人間とAIの「同じ意味を読める」を、単一の数値スコアへ還元せず、Scenario単位でどのように判定するか。

## Constraints

- Web、CLI、desktop、dashboard等の特定UI技術をUniversal Coreへ固定しない。
- Projectionをcanonical semantic authorityへ昇格させない。
- UIを簡略化するためにUnknown、Conflict、Responsibility、basis、revision、Authority / Evidence境界等をcanonical recordから削除しない。
- 高影響案件で必要な明示性を、入力負担削減だけを理由に省略しない。
- 低影響案件へ最大詳細の入力・表示を一律に強制しない。
- machine-readable側だけに重要なbasisを残し、人間向けProjectionから辿れない状態を合格にしない。
- 人間向け説明だけに意味を追加し、machine-readable canonical dataと矛盾する状態を合格にしない。
- private chain-of-thoughtの保存・復元を評価成立条件にしない。
- 読了時間、クリック数、文字数等の単一UX指標をProduct Valueの普遍的KPIにしない。
- synthetic / static harnessのPASSをRelease / Operational / Adoption / Outcomeへ昇格させない。

## Required scenarios / experiments

### E1 — 同一Decisionのlight / audit Projection

一つのrepresentative Decision Memory / Semantic Interchangeをcanonical sourceとし、少なくとも次の二つのProjectionを作る。

- **light** — 日常的な判断確認に必要な要約、Decision状態、主要な未解決点等を前景化する。
- **audit** — basis、provenance、revision、Responsibility、必要なEvidence / Authority境界等へ降りられる。

両者は別のcanonical recordを持たない。

### E2 — machine-readable representationとの意味照合

同じcanonical sourceについて、人間向けProjectionとmachine-readable representationの双方から、事前に定めたsemantic questionsへ回答できることを確認する。

例:

- 何がDecisionされたか。
- 何がbasisとして使われたか。
- 何が未解決のまま残ったか。
- 誰／何がどの文脈でResponsibilityを持つか。
- Authority / Authorizationが未確認なら、その未確認性を識別できるか。
- どのArtifact / Observationの版が重要なbasisだったか。

「同じ回答文になること」ではなく、意味上の矛盾や欠落がないことを評価する。

### E3 — 低影響 / 高影響のProgressive Explicitness

SCN-0004に対応する二つの評価入力を用意する。

- low-impact / reversible case
- high-impact / irreversible or externally consequential case

低影響では不要な詳細を前景化しなくてもよい一方、高影響では必要なbasis、Authority / Evidence、未解決点等を見えないまま進めないことを確認する。

### E4 — Projection交換

同じcanonical sourceから別形式のProjectionを作り、最初のProjectionを削除してもsemantic Artifactを失わないことを確認する。

実装形式は固定しない。最低限、二つの異なるProjection表現で再現できればよい。

### E5 — Negative cases

少なくとも次を失敗として検出する。

1. light ProjectionがUnknown / unresolvedを「問題なし」のように見せる。
2. Responsibilityがcanonical dataにはあるが人間向けProjectionから辿れない。
3. machine-readable側だけがbasisを保持し、人間向け表示では根拠不明になる。
4. human summaryがcanonical dataに存在しないAuthorityや確定事実を追加する。
5. Projectionの編集によりcanonical Artifactが暗黙に書き換わる。
6. high-impact caseで必要な明示性がlight profileのまま欠落する。
7. low-impact caseへ不要な最大詳細入力を必須化し、Progressive Explicitnessが実質的に機能しない。

## Evaluation approach

最初の評価は、actual production UIではなく**dependency-lightな再現可能harness**を優先する。

候補:

```text
canonical fixture
  → projection adapter / renderer
  → light representation
  → audit representation
  → semantic question checker / invariant checker
```

このharnessは評価用Projectionであり、SOZA Universal Coreの新しいContract familyとはみなさない。

人間向け評価については、完全自動化を無理に目指さない。機械的に検査できる意味欠落はcheckerへ置き、読みやすさ・理解可能性はScenarioに沿ったstructured reviewで記録してよい。

## Deliverables

1. V6 / V7評価プロトコル文書。
2. representative canonical fixtureの選定、または評価用fixtureの追加。
3. light / auditの少なくとも二つのProjection例。
4. machine-readable representationとのsemantic question対応表。
5. 自動検査可能なnegative caseとchecker / test。実装可能な範囲でdependency-lightにする。
6. 人間向けstructured reviewの記録様式。
7. actual Executable Evidenceが得られた場合のみ、SCN-0004 / 0006 / 0013およびV6 / V7 TraceabilityのEvidence状態を更新する。
8. 評価中に既存意味境界では表せない差が見つかった場合に限り、別Issue / ADR候補として切り出す。

## Dependencies / interaction with ISSUE-000038

ISSUE-000038はruntime Representation Verifier Registryを扱う別課題であり、本Issueとは独立である。

V6 / V7評価がExact Binding verificationを利用する場合でも、Verifier Registry完成を本Issue全体の前提にはしない。必要な検査だけをcurrent verified profile / fixtureで行い、依存が実際に発生した箇所だけ明示する。

## Completion criteria

### Semantic / Design Acceptance

- [ ] 評価protocolがV6 / V7、REQ-0010 / 0011 / 0019 / 0020、SCN-0004 / 0006 / 0013 / 0017へ追跡できる。
- [ ] light / auditの意味差を「表示量の差」として扱い、別canonical meaningにしていない。
- [ ] 人間向けProjectionとmachine-readable representationのsemantic question setを定義している。
- [ ] negative caseがcanonical meaning lossと過剰明示の双方を含む。

### Executable Acceptance

- [ ] representative canonical sourceから少なくとも二つのProjectionを再現できる。
- [ ] 自動検査可能なsemantic invariant / negative caseがactual repositoryでPASSする。
- [ ] Projection交換後もcanonical sourceが保持されることを再現できる。
- [ ] high-impact caseでは必要情報が欠落せず、low-impact caseでは不要な最大詳細を強制しないことを評価できる。

### Adoption / Outcomeへの留保

本Issueで得られるのは最大でもevaluation-harness scoped Executable Evidenceである。

```text
projection harness PASS
  != production UX validated
  != Operational Evidence
  != Adoption / Outcome Evidence
```

実利用者が実務上必要な時間・負担で意味を理解できるか、判断品質が改善するかは、後続のOperational / Adoption・Outcome評価で扱う。

## Resolution / reopen conditions

Executable Acceptanceまで満たした時点で、本IssueをResolvedにできる。

ただし、評価結果から新しいUniversal semantic conceptが必要に見えた場合は、本Issue内で即座にCore化しない。複数Scenarioで不可欠な意味差かを確認し、別ADR候補として扱う。

Resolved後も、production Projectionや実利用で「人間には必要な意味が見えない」「簡略化がcanonical意味を削る」「高影響案件で明示量が不足する」といった反例が得られた場合は再開または後続Issueを作成する。

## Natural Japanese review

Product Value Traceability、Value Acceptance、REQ-0010 / 0011 / 0019 / 0020、SCN-0004 / 0006 / 0013 / 0017、ADR-0005 / 0018 / 0020 / 0021、current Contract / Runtime Evidenceへ戻って論点を整理した。その後、UI実装とProduct Value評価、Executable EvidenceとOperational / Adoption・Outcomeを混同しないよう意味と留保を固定し、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。
