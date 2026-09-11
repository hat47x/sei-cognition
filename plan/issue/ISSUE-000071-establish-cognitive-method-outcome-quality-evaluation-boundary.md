# ISSUE-000071: Cognitive Method成果品質の評価境界を確立する

Status: **Resolved**  
Priority: **1**  
Related ADRs: **ADR-0017, ADR-0018, ADR-0020, ADR-0021, ADR-0025**  
Product Milestone: **PMS-06**  
Updated: 2026-09-03

## Goal

actual Cognitive Methodが「実行できた」ことと、その出力が人間の探索やKJ法の実践にとって「よい成果だった」ことを分けて評価できる基線を作る。

E3b-M1bのactual model-backed executionと、ISSUE-000068のactual model artifact交換で得たEvidenceを入力として、少なくとも次の四つを同じPASS / FAILへ押し込めないようにする。

```text
execution conformance
  != structural safety / integrity
  != Cognitive Method outcome quality
  != Product Value / Adoption outcome
```

成果品質を単一スコアへ圧縮せず、生成AI自身の採点も正解として扱わない。機械的に確認できる事実、人間が判断すべき意味上の品質、製品価値として評価すべき結果を、それぞれ別の責務として残す。

## Background

ISSUE-000066では、固定revisionのKJ AtlasをOllama上のactual modelへ接続し、actual inferenceからSEI Cognitive Method ApplicationへのmappingまでをScoped Executable Evidenceとして確認した。

ISSUE-000067ではMethod RealizationとExact Bindingによるhistorical reconstruction境界を整理し、ISSUE-000068では同じKJ Atlas / Method input / Ollama runtimeの下でactual model artifactを交換しても、先行ApplicationのRealization、Provenance、outputを保持できることを実証した。

一方、同じprompt SHA-256、同じKJ Atlas revision、同じruntime / model identityを使ったM1bの複数runでも、生成されたgroup labelやrationaleは一致しなかった。

```text
same prompt digest
  != same generated wording
  != same cognitive quality
```

保存済みのactual runでは、どちらも在宅勤務に関する2枚を一つに束ね、held cardを除外している。ただし、Run `33596839607`の表札は`生活習慣`、Run `33609470323`の表札は`在宅勤務`だった。

この差は構造検査だけでは良否を決められない。表札が元cardの訴えを広げすぎていないか、単なる話題名に退いていないか、rationaleが入力にない分類や因果を持ち込んでいないかは、人間が元cardへ戻って確認する必要がある。

この観測自体をhuman reviewの代用にはしない。execution conformanceと成果品質を分ける必要性を示す比較材料として保持する。

## Questions and answers

### 1. 機械検査でどこまで確認するか

意味内容を採点せず、入力card identity、held / excluded、重複所属、空group / label、request / result digest等の構造不変条件だけを確認する。

### 2. 人間は何を確認するか

元cardの「訴え」、束ね方、無理な統合、見落とし、表札の具体性、入力にない断定、held・異論・残差、次の壁打ちへの有用性を、単一スコアへ潰さず記録する。

### 3. 同一条件で異なる生成結果をどう扱うか

勝敗やgolden answerへ変換せず、input identity、Method source、runtime / model identity、prompt digest、raw result、structure result、review contextを比較可能なhistorical observationとして残す。

### 4. Product Valueとの境界

structure checkや一件のhuman reviewを、Operational EvidenceやAdoption / Outcome Evidenceへ昇格させない。実利用で価値が届いたかどうかは別の評価段階で扱う。

## Constraints

- 生成AIや自動評価器の品質判定を、人間のKJ法レビューと同等の正解として扱わない。
- model名、runtime名、temperature、特定prompt等をUniversal Cognitive Method Contractの必須fieldへ先取りしない。
- structure checkのPASSを、groupingや表札の意味的品質のPASSへ昇格させない。
- human reviewの記録を、直ちにOperational EvidenceやAdoption / Outcome Evidenceへ昇格させない。
- 成果品質を単一の総合点だけで表現しない。数値化する場合も、元の観測、違和感、残差を失わない。
- held / excluded、入力card identity、生成group、Provenance等、後から判断過程へ戻るための情報を保持する。
- KJ法の成果物をRecommendationやDecisionへ自動昇格させない既存境界を維持する。
- case catalogへ`expectedGroups`、`expectedLabel`、`qualityScore`等の機械的な正解を持ち込まない。
- historical sampleへ`preferred`、`winner`、期待表札等を付けない。
- AI補助観測にもwinner、golden label、machine scoreを持ち込まず、human reviewと明確に分離する。
- 現時点では新しいStable Requirement / Scenarioを追加しない。
- GitHub Actions workflowやrunner availabilityを、この評価基盤の意味上の成立条件にしない。

## Established evaluation boundary

### EVAL-Q1 — 構造検査

`evaluation/method-quality/check_grouping_structure.py`は、actualまたはfixtureのgrouping resultについて次を確認する。

- group内のcard IDが入力候補に存在する。
- held cardがgroupへ再混入していない。
- held cardと`excludedCardIds`の対応を確認できる。
- 同じcardが複数groupへ重複所属していない。
- 同じcardがgroupと`excludedCardIds`の双方へ現れない。
- groupとlabelが空でない。
- request / resultのSHA-256を記録できる。

出力には`qualityJudgement = not_evaluated`を保持する。これは構造安全性の検査であり、意味的品質の採点ではない。

### EVAL-Q2 — structured human review

`evaluation/method-quality/HUMAN_REVIEW_TEMPLATE.md`では、少なくとも次を個別に記録できる。

- cardの訴えが保たれているか。
- 表面的な分類語だけで束ねていないか。
- 離しておくべきcardを無理に押し込めていないか。
- 明らかに響き合うcardを見落としていないか。
- 表札が元cardの具体性や差異を消しすぎていないか。
- 入力にない断定・因果・評価を持ち込んでいないか。
- held、異論、違和感、未整理部分を処理済みに見せていないか。
- 次の壁打ち、配置、統合、文章化のproposalとして役立つか。

### EVAL-Q3 — historical observation

`historical_actual_samples.json`へ、Run `33596839607`とRun `33609470323`を保存している。

両者は同じrequest、Method source、Ollama `0.32.14`、`qwen2.5:0.5b`、prompt SHA-256を共有する一方、生成されたlabel / rationaleが異なる。この差をexecution failureや品質上の順位へ変換せず、actual outputの変動として保持する。

### EVAL-Q4 — actual M1bへの接続

PR #72で、成功済みactual M1b Run `33596839607` / Job `100141890796`について、repositoryに保存したhistorical sampleとGitHubに残る当該job logからreview bundleを再構成した。

保存先:

`evaluation/method-quality/historical/M1B-RUN-33596839607/`

保存しているもの:

- `request.json`
- `result.json`
- `model-evidence.json`
- `runtime-version.txt`
- `model-list.txt`
- `structure-report.json`
- `review-manifest.json`
- `reconstruction-provenance.json`

structure checkの結果は次だった。

```text
status = passed
violations = []
inputCardCount = 3
heldCardCount = 1
groupedCardCount = 2
excludedCardCount = 1
qualityJudgement = not_evaluated
```

request SHA-256:
`f07684c39c9bbb1f1ffcc223da33506c94c91393bf09abc45f550f0baac83cc0`

result SHA-256:
`3b52f421e3a8240ae6e3ae3c625becdc380ff08cf5235f65df8896d9562c9355`

元workflowはartifactを保存していなかったため、このbundleを「当時のworkflow artifact」とは扱わない。`reconstruction-provenance.json`で`originalWorkflowArtifactAvailable = false`を明示し、historical sampleと保存job logからの再構成物として扱う。

`test_historical_review_bundle.py`では、保存request / resultからstructure reportを再生成できること、manifestを再生成できること、原artifactが存在したかのような主張をしていないことを検査する。3件はローカルでPASSしている。

```text
actual historical output
  + log-derived execution provenance
  + structural check PASS
  + reproducible review manifest
  = review-ready reconstructed bundle

review-ready bundle
  != original workflow artifact
  != human review completed
  != grouping quality satisfied
```

### EVAL-Q5 — non-golden case catalog

`case_catalog.json`では、期待groupや期待表札を正解として固定せず、少なくとも次の難所を保持する。

- 語彙が異なるが訴えが近いcard。
- 同じ話題語を含むが訴えが異なるcard。
- 利点と懸念が緊張したまま残るcard。
- 二つのまとまりをまたぐ橋になり得るcard。
- held、異論、未整理の残差を含むcase。
- 一部だけが近く、残りは孤立させた方が自然なcase。

validatorはgolden-answer化につながるfieldを拒否する。

### EVAL-Q6 — 再現可能な評価tool

actual model取得を必要としない範囲で、次をrepository同梱toolとして再実行できる。

- grouping structure checker test
- review bundle manifest test
- case catalog validator test
- historical actual sample test
- historical review bundle reconstruction test
- AI supplemental observation boundary test
- current `case_catalog.json` validation

旧作業branchで、structure checker / manifestの19ケース、case catalog validatorの10ケース、historical actual sampleの4ケース、合計33ケースを確認済みである。

PR #72でhistorical review bundleの3ケースを追加し、ローカルでPASSを確認した。PR #73で追加したAI補助観測の境界3ケースについても、2026-09-03にローカルでPASSを再確認した。

これらは累積39ケースの検査資産に相当する。ただし、各時点の検査結果を一つのCI runが39件まとめて実行したという意味ではない。

### EVAL-Q7 — AI補助観測とhuman reviewの分離

PR #73では、2つのactual M1b resultの意味上の差を、`non_authoritative_ai_supplement`として別保存した。

AI補助観測では、`生活習慣`が元cardより広い分類へずれている可能性、`在宅勤務`が共通核より一般的な話題名に退いている可能性などを、人間が確認するための論点として記録した。

一方、次を明示的に保持している。

```text
humanReviewCompleted = false
qualityJudgement = not_evaluated
winnerSelection = false
goldenLabel = false
machineScore = false
```

したがって、AIの観測をHuman Review TemplateのQ1〜Q8へそのまま転記せず、人間が元cardとactual resultを読み直す。

## Deliverables

- `evaluation/method-quality/README.md`
- `evaluation/method-quality/HUMAN_REVIEW_TEMPLATE.md`
- `evaluation/method-quality/check_grouping_structure.py`
- `evaluation/method-quality/test_check_grouping_structure.py`
- `evaluation/method-quality/build_review_bundle_manifest.py`
- `evaluation/method-quality/test_build_review_bundle_manifest.py`
- `evaluation/method-quality/case_catalog.json`
- `evaluation/method-quality/validate_case_catalog.py`
- `evaluation/method-quality/test_validate_case_catalog.py`
- `evaluation/method-quality/historical_actual_samples.json`
- `evaluation/method-quality/test_historical_actual_samples.py`
- `evaluation/method-quality/historical/M1B-RUN-33596839607/*`
- `evaluation/method-quality/test_historical_review_bundle.py`
- `evaluation/method-quality/historical/ai-supplemental-comparison.json`
- `evaluation/method-quality/test_ai_supplemental_comparison.py`
- `plan/registry.yaml`
- `plan/document_review_registry.yaml`

## Resolution

次の9条件を確認し、本IssueをResolvedとする。

1. execution conformance、structural safety、human outcome review、Product Value / Adoption outcomeの境界を文書化した。**完了**
2. grouping resultの構造検査についてpositive / negative testを用意した。**完了**
3. review bundle manifestがidentity / digestの整合を検査し、structure PASSをquality PASSへ昇格させない。**完了**
4. non-golden case catalogとvalidatorが、意味的な正解を固定せず複数の評価難所を保持する。**完了**
5. historical actual sampleがactual outputの変動を品質順位へ変換せず保存する。**完了**
6. actual E3b-M1b outputへ同じ構造検査を適用し、review bundleを再構成できることをPR #72で確認した。**完了**
7. 人間レビュー用templateが、単一スコアやAI採点を正解としない形式で用意されている。**完了**
8. 評価toolの再現可能な検査とactual M1b実証の責務を分離した。**完了**
9. 上流計画と文書レビュー台帳をcurrent stateへ同期する。**本Issueを閉じるPlan整合変更で完了**

このResolvedは、Cognitive Methodの成果品質がSatisfiedになったことを意味しない。

```text
evaluation boundary established
  != human review completed
  != model quality proven
  != KJ-method outcome quality proven
  != Product Value satisfied
```

実際のhuman review、複数caseでのactual比較、実利用時の価値評価は後続Evidenceとして扱う。

## Reopen conditions

- 構造検査が意味的品質を暗黙に採点していることが分かった。
- case catalogやhistorical sampleが実質的なgolden answer / ranking datasetへ変質した。
- KJ法の実践者レビューで、現在の質問群では重要な残差を記録できないことが分かった。
- 別Cognitive Methodで現在の四層分離が成立しない事例が見つかった。
- model / runtime交換時に、品質比較へ必要なProvenanceを保持できないことが分かった。
- Product Value / Requirementの変更により、成果品質の評価責任を見直す必要が生じた。

## Verification

repository同梱の評価toolは、外部model取得やGitHub Actionsを必須とせず再実行できるようにする。actual model-backed executionが必要な評価は、固定したinput / source / runtime / model identityとともに別途実行し、後から同じ対象へ戻れるEvidenceを保存する。

workflowやrunnerは実行手段の一つであり、評価意味の正本ではない。

## Natural Japanese review

M1bのactual Evidence、ISSUE-000067のRealization / Provenance境界、ISSUE-000068のactual model artifact交換、既存V6 / V7 human structured reviewへ戻り、評価責任を再確認した。

文章は「何が検査できるか」「何を人間へ残すか」「何をまだ主張しないか」が自然に読み分けられるように組み直した。case catalogやhistorical sampleは正解集にせず、actual resultの揺れや違和感へ戻るための材料として位置づけた。

PR #72でhistorical actual outputからreview-ready bundleを再構成できることを確認したが、元workflow artifactが存在しなかった事実はそのまま残した。PR #73のAI補助観測についても、人間の判断を代行したように読めないよう、非権威的な補助記録として分離した。

意味、要求強度、未検証範囲、Evidence強度を変えず、自然な日本語として一続きに読めることを最重要視して全文を再ドラフトした。