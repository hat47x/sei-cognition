# ISSUE-000071: Cognitive Method成果品質の評価境界を確立する

Status: **Open**  
Priority: **1**  
Related ADRs: **ADR-0017, ADR-0018, ADR-0020, ADR-0021, ADR-0025**  
Product Milestone: **PMS-06**  
Updated: 2026-09-03

## Goal

actual Cognitive Methodについて、「実行できた」という事実と、その出力が人間の探索やKJ法の実践にとって「よい成果だった」という判断を分けて扱える評価基盤を整える。

少なくとも、次の四つは同じPASS / FAILへまとめない。

```text
execution conformance
  != structural safety / integrity
  != Cognitive Method outcome quality
  != Product Value / Adoption outcome
```

機械検査で確かめられる構造上の事実と、人間が元cardへ戻って判断すべき意味上の品質を分離する。成果品質を単一スコアへ圧縮せず、生成AI自身による採点も人間のKJ法レビューの代わりにはしない。

## 背景

ISSUE-000066では、固定revisionのKJ AtlasをOllama上のactual modelへ接続し、actual inferenceからSOZA Cognitive Method Applicationへ戻すところまでをScoped Executable Evidenceとして確認した。

ISSUE-000067ではMethod RealizationとExact Bindingのhistorical reconstruction境界を整理し、ISSUE-000068では、同じKJ Atlas / Method input / Ollama runtimeのもとでactual model artifactを交換しても、先行ApplicationのRealization、Provenance、outputを保持できることを実証した。

一方、同じprompt SHA-256、同じKJ Atlas revision、同じruntime / model identityを使ったM1bの複数runでも、生成された表札とrationaleは一致しなかった。

```text
same prompt digest
  != same generated wording
  != same cognitive quality
```

保存済みの二つのrunでは、どちらも「在宅勤務で通勤時間を減らせる」「移動負担を減らせる」という二枚を同じgroupへ置き、held状態の人事評価制度cardを除外している。この構造は共通しているが、表札はRun `33596839607`で`生活習慣`、Run `33609470323`で`在宅勤務`となった。

どちらも構造検査だけなら成立し得る。しかし、表札が元cardの具体的な訴えを広げすぎていないか、単なる話題名に退いていないか、rationaleが入力にない分類・因果・評価を持ち込んでいないかは、構造検査だけでは決められない。

この差異は、execution failureにも品質上の勝敗にも変換せず、後から人間が読み直せる観測として残す。

## 評価で分けるもの

### 1. Execution conformance

Methodが定めた入力を受け取り、指定された実行境界を通り、追跡可能な出力を返したかを扱う。

ここでは「実行経路が成立したか」を見る。出力内容の良し悪しは判断しない。

### 2. Structural safety / integrity

入力cardのidentity、held / excluded、group所属、Provenance、digest等について、機械的に確認できる不変条件を扱う。

ここでPASSしても、束ね方や表札の意味的品質がよいとは限らない。

### 3. Cognitive Method outcome quality

cardの「訴え」が保たれているか、無理な束ねや話題語だけの分類になっていないか、表札が差異を消しすぎていないか、入力にない断定を持ち込んでいないか等を扱う。

この層は、人間が元cardと生成結果へ戻って判断する。生成AIによる補助観測を使う場合も、人間の判断欄とは分離する。

### 4. Product Value / Adoption outcome

その成果が実利用で役立ったか、継続利用する価値があったか、意思決定や探索にどのような変化をもたらしたかを扱う。

一件のstructure checkやhuman reviewから、この層まで成立したとは扱わない。

## Questions

1. 意味内容を採点せず、機械的に確認できる構造上の不変条件は何か。
2. grouping、表札、残差の扱いについて、人間は何を確認すべきか。
3. 同じ入力から異なる生成結果が得られた場合、その差を捨てずにどう保存するか。
4. model出力品質、KJ法としての成果品質、Product Valueへの寄与を、どのEvidence段階で分けるか。
5. 評価方法の都合からOllama、Qwen、KJ Atlas固有fieldをSOZA Universal Contractへ持ち込まずに済むか。
6. 意味的近接、話題語による誤分類、緊張、橋、held・異論・残差、孤立といった難所を、評価入力へどう残すか。
7. case catalogが機械的なgolden groupingや期待表札へ変質しないよう、どこに停止線を置くか。
8. actual outputを品質の正解へ昇格させず、将来の比較レビューへ再利用できるhistorical sampleとしてどう保存するか。

## Constraints

- 生成AIまたは自動評価器の品質判定を、人間のKJ法レビューと同等の正解として扱わない。
- model名、runtime名、temperature、特定prompt等をUniversal Cognitive Method Contractの必須fieldへ先取りしない。
- 構造検査のPASSを、groupingや表札の意味的品質のPASSへ昇格させない。
- human reviewの記録を、直ちにOperational EvidenceやAdoption / Outcome Evidenceへ昇格させない。
- 単一の総合点だけで品質を表現しない。数値へ要約する場合も、元の観測・違和感・残差を失わない。
- held / excluded、入力card identity、生成group、Provenance等、後から判断過程へ戻るための情報を保持する。
- Cognitive Methodの出力をRecommendationやDecisionへ自動昇格させない既存境界を維持する。
- case catalogへ`expectedGroups`、`expectedLabel`、`qualityScore`等の機械的な正解を持ち込まない。
- historical sampleへ`preferred`、`winner`、期待表札等を付けない。observed outputとsource identityを保存する。
- 現時点では新しいStable Requirement / Scenarioを追加しない。必要性は評価実証の後で再監査する。
- GitHub Actions workflowやrunner availabilityを、本Issueの評価境界が成立する条件にしない。評価toolは実行場所から独立したrepository同梱資産として保つ。

## Required scenarios / experiments

### EVAL-Q1 — 機械的な構造検査

actualまたはfixtureのgrouping resultに対して、少なくとも次を検査する。

- group内のcard IDが入力候補に存在する。
- held cardがgroupへ再混入していない。
- held cardと`excludedCardIds`の対応を確認できる。
- 同じcardが複数groupへ重複所属していない。
- 同じcardがgroupと`excludedCardIds`の双方へ同時に現れない。
- group labelが空でない。
- 検査対象のinput / result digestを記録できる。

これは構造安全性の検査であり、groupingの意味的品質は採点しない。

### EVAL-Q2 — 人間によるstructured review

人間レビューでは、次の観点を単一スコアへ潰さずに記録できるようにする。

- cardの「訴え」が束ねた後にも残っているか。
- 表面的な分類語の近さだけで束ねていないか。
- 本来は離しておくべきcardを無理に同じ島へ押し込めていないか。
- 明らかに響き合うcardを見落としていないか。
- 表札が元cardの具体性や差異を消しすぎていないか。
- 表札やrationaleが、入力にない断定・因果・評価を持ち込んでいないか。
- held、異論、違和感、未整理部分を処理済みに見せていないか。
- 次の壁打ち・配置・統合・文章化を考えるproposalとして役立つか。

### EVAL-Q3 — 同一条件で異なる生成結果を保持する

同じprompt digestから異なるlabel / rationaleが出た既存M1b Evidenceを、execution failureでも品質上の勝敗でもなく、比較可能なhistorical observationとして扱う。

少なくとも次を別々に保持する。

- input identity
- repository / Method source revision
- runtime / model identity
- prompt digest
- raw generated result
- structure check result
- human review record

### EVAL-Q4 — actual M1bへの評価基盤接続

M1bのactual model-backed実行で得たKJ Atlas resultへEVAL-Q1の構造検査を適用できるようにする。

actual request、result、model call Evidence、structure report、runtime / model identityをreview bundleとして保持し、manifestでrun / repository commit / Method source commit / file digestを対応付ける。

```text
structure check PASS
  + review bundle preserved
  != grouping quality satisfied
  != KJ-method outcome quality satisfied
  != Product Value satisfied
```

この接続はGitHub Actionsを必須としない。手動実行、ローカル実行、将来の外部runner等、実行場所を評価の意味から切り離す。

### EVAL-Q5 — non-golden case catalog

一つの簡単なM1b入力だけでは捉えにくい難所を、複数の評価ケースとして保持する。

current catalogでは少なくとも次を扱う。

- 語彙が異なるが訴えが近いcard。
- 同じ話題語を含むが訴えが異なるcard。
- 利点と懸念が緊張したまま残るcard。
- 二つのまとまりをまたぐ橋になり得るcard。
- held、異論、未整理の残差を含むcase。
- 一部だけが近く、残りは孤立させた方が自然なcase。

case catalogは「何を観測したいか」だけを持ち、期待groupや期待表札を正解として固定しない。

### EVAL-Q6 — 評価toolの再現可能な検査

actual modelを取得しなくても、少なくとも次を再実行できる状態を保つ。

- grouping structure checker test
- review bundle manifest test
- case catalog validator test
- historical actual sample test
- current `case_catalog.json` validation

GitHub Actionsへの配置は任意とし、評価toolの意味上の責務とは分離する。

### EVAL-Q7 — historical actual sampleの保存

既存runのrequest / result / source identityを`historical_actual_samples.json`へ保存する。

current baselineではRun `33596839607`とRun `33609470323`を保持している。両者は同じrequest、Method source、Ollama `0.32.14`、`qwen2.5:0.5b`、prompt SHA-256を共有する一方、生成されたlabel / rationaleが異なる。

sample testでは次を確認する。

- 各sampleがstructure checkerを通過する。
- `qualityJudgement`は`not_evaluated`のままである。
- 同じexecution identityから異なるgenerated wordingが保存されている。
- run / job / commit identityを区別して追跡できる。
- `expectedGroups`、`expectedLabel`、`qualityScore`、`preferred`、`winner`等のgolden / ranking fieldを持たない。

## AI補助観測の扱い

PR #73では、二つのhistorical sampleの差異を`evaluation/method-quality/historical/ai-supplemental-comparison.json`へ保存した。

この記録は、Human Review Template第8節に沿う**非権威的なAI補助観測**であり、human reviewそのものではない。次の停止線を機械的に保持する。

```text
reviewAuthority = non_authoritative_ai_supplement
humanReviewCompleted = false
qualityJudgement = not_evaluated
winnerSelection = false
goldenLabel = false
machineScore = false
```

補助観測では、`生活習慣`が元cardより広い分類語へずれている可能性、`在宅勤務`が二枚の共通核より一般的な話題名に留まっている可能性などを、人間が確認すべき問いとして残している。どちらを優れた出力とも決めず、期待表札も固定していない。

人間がレビューする際は、このAI補助観測を判断欄へ転記するのではなく、元cardとactual resultを読み直したうえでQ1〜Q8を判断する。

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
- `evaluation/method-quality/historical/ai-supplemental-comparison.json`
- `evaluation/method-quality/test_ai_supplemental_comparison.py`
- actual M1b結果へ構造検査とreview bundle生成を適用できる実行境界
- `plan/registry.yaml`
- `plan/document_review_registry.yaml`

## Current verification state

評価toolについては、統合前の作業branchで、既存19ケース、case catalog validator 10ケース、historical actual sample 4ケースを合わせて33ケース相当のローカル検査が成功した記録を保持している。

PR #73では、保存済みactual M1b 2 runに対するAI補助観測と、その記録がhuman judgement・winner・golden label・machine scoreへ変質していないことを検査するtestを追加した。これにより、人間レビュー前の補助観測をhuman reviewから分離して保存できる形になった。

ただし、現在の`develop/v0.2.0`で評価tool一式を再実行した記録は、このIssue上ではまだ確定していない。また、actual成果の意味品質について人間がQ1〜Q8を記録した事実もまだない。

GitHub Actions workflowは現在の統合基線では採用していない。runner割当やworkflow生成の成否を、この評価基盤の成立証拠として扱わない。

```text
evaluation tools prepared
  + historical actual outputs preserved
  + non-authoritative AI observation separated
  != current-branch execution record completed
  != human outcome review completed
  != outcome quality satisfied
```

## Resolution

次を確認できた時点で、本IssueはResolvedにできる。

1. execution conformance、structural safety、human outcome review、Product Value / Adoption outcomeの境界が文書化されている。
2. grouping resultの構造検査がpositive / negative testで動作する。
3. review bundle manifestがidentity / digestの整合を検査し、structure PASSをquality PASSへ昇格させない。
4. non-golden case catalogとvalidatorが、意味的な正解を固定せず複数の評価難所を保持できる。
5. historical actual sampleがactual outputの変動を品質順位へ変換せず保存できる。
6. actual E3b-M1b outputにも同じ構造検査を適用し、review bundleを生成できる。
7. 人間レビュー用templateが、単一スコアやAI採点を正解としない形式で用意されている。
8. AI補助観測をhuman reviewから明確に分離できる。
9. 評価toolの再現可能な検査とactual M1b実証の責務が分離されている。
10. 上流計画と文書レビュー台帳がcurrent stateへ同期している。
11. 現在の統合基線で、repository同梱の評価toolが再現可能に実行できることを記録する。

本IssueのResolvedは、Cognitive Methodの成果品質そのものがSatisfiedになったことを意味しない。実際のhuman review、複数caseでのactual比較、実利用時の価値評価は、評価基盤の成立後に積み上げる別のEvidenceである。

## Reopen conditions

- 構造検査が意味的品質を暗黙に採点してしまうことが判明した。
- case catalogやhistorical sampleが、実質的なgolden answer / ranking datasetへ変質した。
- AI補助観測がhuman judgementへ自動転記されるなど、両者の境界が崩れた。
- KJ法の実践者レビューで、現在の質問群では重要な残差を記録できないことが分かった。
- 別Cognitive Methodで現在の四層分離が成立しない事例が見つかった。
- model / runtime交換時に、品質比較へ必要なProvenanceを保持できないことが判明した。
- Product Value / Requirementの変更により、成果品質の評価責任を見直す必要が生じた。

## Verification

repository同梱の評価toolを、外部model取得なしで再現可能に実行する。actual M1bを評価する場合は、固定したinput / source / runtime / model identityとともに別途扱い、structure reportとreview bundleを保存する。

AI補助観測を利用する場合も、その記録はhuman reviewとは別に保持する。human reviewでは元cardとactual resultへ戻り、補助観測へ同意するかどうかを含めて人間が判断する。

workflowやrunnerの有無は検証手段の選択肢にすぎず、本Issueの意味上の完了条件には含めない。

## Natural Japanese review

M1bのactual Evidence、ISSUE-000067で整理したRealization / Provenance境界、ISSUE-000068のactual model artifact交換、既存V6 / V7 human structured reviewへ戻り、評価責任を過不足なく分離した。

単一の簡単な入力だけへ評価を閉じないようnon-golden case catalogを設け、期待groupや期待表札を機械的な正解として固定しない停止線を維持した。既存actual runについても、表札やrationaleの差を勝敗へ変換せずhistorical sampleとして保持し、後から同じ入力・実行identity・生成結果へ戻れるようにしている。

PR #73で追加したAI補助観測についても、「人間レビューの代行」ではなく、人間が元cardへ戻るための論点整理として位置づけた。`生活習慣`と`在宅勤務`のどちらを良い表札とも決めず、違和感や確認点だけを残している。

最後に、現在のCI停止方針に合わせ、GitHub Actionsのworkflowやrunner availabilityを評価基盤そのものの成立条件から外した。意味、要求強度、未検証範囲、Evidence強度を変えず、技術語を必要以上に連ねない自然な日本語として読み通せることを最重要視して全文を再ドラフトした。
