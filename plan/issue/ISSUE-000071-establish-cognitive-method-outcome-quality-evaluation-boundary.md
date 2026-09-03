# ISSUE-000071: Cognitive Method成果品質の評価境界を確立する

Status: **Open**  
Priority: **1**  
Related ADRs: **ADR-0017, ADR-0018, ADR-0020, ADR-0021, ADR-0025**  
Product Milestone: **PMS-06**  
Updated: 2026-09-03

## Goal

actual Cognitive Methodを「実行できた」ことと、その出力が人間の探索やKJ法実践にとって「よい成果だった」ことを分離して評価できる基線を作る。

E3b-M1bで成立したactual model-backed executionと、ISSUE-000068で実証したactual model artifact交換を入力として、少なくとも次の四層を混同しない。

```text
execution conformance
  != structural safety / integrity
  != Cognitive Method outcome quality
  != Product Value / Adoption outcome
```

成果品質を単一スコアへ圧縮したり、生成AI自身の採点を正解として採用したりせず、機械検査で確認できる事実と、人間のレビューを必要とする判断を明確に分ける。

## Background

ISSUE-000066では、固定revisionのKJ AtlasをOllama上のactual modelへ接続し、actual inferenceからSOZA Cognitive Method ApplicationへのmappingまでをScoped Executable Evidenceとして確認した。

ISSUE-000067ではMethod RealizationとExact Bindingのhistorical reconstruction境界を整理し、ISSUE-000068では同じKJ Atlas / Method input / Ollama runtimeのもとでactual model artifactを交換しても、先行ApplicationのRealization、Provenance、outputを保持できることをScoped Executable Evidenceとして実証した。

一方、同じprompt SHA-256、同じKJ Atlas revision、同じruntime / model identityを使ったM1bの複数runでも、生成されたgroup labelやrationaleは一致しなかった。

```text
same prompt digest
  != same generated wording
  != same cognitive quality
```

既存runでは同じ二枚の在宅勤務cardを一つのgroupへ束ね、held cardを除外する構造は共通していたが、Run `33596839607`では表札が`生活習慣`、Run `33609470323`では`在宅勤務`となった。

両方とも構造検査の範囲では成立し得る。しかし、表札が元cardの訴えを広げすぎていないか、単なる話題名に退いていないか、rationaleが入力にない分類や因果を持ち込んでいないかは、構造検査だけでは判断できない。

この観測をhuman reviewの代用にはしない。execution conformanceと成果品質を同じPASS / FAILへ押し込めないことを示す比較材料として保持する。

## Questions

1. Cognitive Method outputについて、意味内容を採点せず機械的に確認できる構造上の不変条件は何か。
2. KJ法としてのgrouping、表札、残差の扱い等について、人間のレビューで何を確認すべきか。
3. 同じ入力から異なる生成結果が得られた場合、差異を「ばらつき」として捨てず、比較可能な記録としてどう保持するか。
4. model出力品質、KJ法としての成果品質、Product Valueへの寄与を、どのEvidence段階で別々に扱うか。
5. 評価方法の都合からOllama、Qwen、KJ Atlas固有fieldをSOZA Universal Contractへ持ち込まずに済むか。
6. 意味的近接、話題語による誤分類、緊張、橋、held・異論・残差、孤立を残す必要性をどう評価入力へ含めるか。
7. 評価ケースが機械的なgolden groupingや期待表札の固定へ変質しないよう、どこに停止線を置くか。
8. 既存actual outputを品質の正解へ昇格させず、将来の比較レビューへ再利用できるhistorical sampleとしてどう保存するか。

## Constraints

- 生成AIまたは自動評価器の品質判定を、人間のKJ法レビューと同等の正解として扱わない。
- model名、runtime名、temperature、特定prompt等をUniversal Cognitive Method Contractの必須fieldへ先取りしない。
- 構造検査のPASSを、groupingや表札の意味的品質のPASSへ昇格させない。
- human reviewの記録を、直ちにOperational EvidenceやAdoption / Outcome Evidenceへ昇格させない。
- 単一の総合点だけで品質を表現しない。少数の数値へ圧縮する場合も、元の観測・違和感・残差を失わない。
- held / excluded、入力card identity、生成group、Provenance等、後から判断過程を辿るための情報を保持する。
- KJ法の成果物をRecommendationやDecisionへ自動昇格させない既存境界を維持する。
- 評価case catalogへ`expectedGroups`、`expectedLabel`、`qualityScore`等の機械的な正解を持ち込まない。
- historical sampleへ`preferred`、`winner`、期待表札等を付けず、observed outputとsource identityだけを保存する。
- 現時点では新しいStable Requirement / Scenarioを追加しない。必要性は評価実証の後で再監査する。
- GitHub Actions workflowの存在やrunner availabilityを、本Issueの評価境界成立条件にしない。検査はrepository同梱toolとして再現可能であることを優先する。

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

少なくとも次を単一スコアへ潰さず記録できるreview templateを維持する。

- cardの「訴え」が保たれているか。
- 分類語の近さだけで束ねていないか。
- 無理に一つの島へ押し込めていないか。
- 明らかに響き合うcardを見落としていないか。
- 表札が元cardの具体性や差異を消しすぎていないか。
- 入力にない断定・因果・評価を持ち込んでいないか。
- held、異論、違和感、未整理部分を処理済みに見せていないか。
- その出力を次の壁打ち・配置・統合・文章化のproposalとして使えるか。

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

この接続はGitHub Actionsを必須としない。手動実行、ローカル実行、将来の外部runner等、実行場所を評価意味から分離する。

### EVAL-Q5 — non-golden case catalog

一つの簡単なM1b入力だけでは捉えにくい難所を複数の評価ケースとして保持する。

current catalogでは少なくとも次を含める。

- 語彙が異なるが訴えが近いcard。
- 同じ話題語を含むが訴えが異なるcard。
- 利点と懸念が緊張したまま残るcard。
- 二つのまとまりをまたぐ橋になり得るcard。
- held、異論、未整理の残差を含むcase。
- 一部だけが近く、残りは孤立させた方が自然なcase。

case catalogは「何を観測したいか」だけを持ち、期待groupや期待表札を正解として固定しない。

### EVAL-Q6 — 評価toolの再現可能な検査

actual model取得を必要としない範囲で、少なくとも次を一括して再実行できる状態を保つ。

- grouping structure checker test
- review bundle manifest test
- case catalog validator test
- historical actual sample test
- current `case_catalog.json` validation

GitHub Actionsへの配置は任意とし、評価toolの意味上の責務とは分離する。

### EVAL-Q7 — historical actual sampleの保存

既存runのrequest / result / source identityを`historical_actual_samples.json`へ保存する。

current baselineでは少なくともRun `33596839607`とRun `33609470323`を保持する。両者は同じrequest、Method source、Ollama `0.32.14`、`qwen2.5:0.5b`、prompt SHA-256を共有する一方、生成されたlabel / rationaleが異なる。

sample testでは次を確認する。

- 各sampleがstructure checkerを通過する。
- `qualityJudgement`は`not_evaluated`のままである。
- 同じexecution identityから異なるgenerated wordingが保存されている。
- run / job / commit identityを区別して追跡できる。
- `expectedGroups`、`expectedLabel`、`qualityScore`、`preferred`、`winner`等のgolden / ranking fieldを持たない。

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
- actual M1b結果へ構造検査とreview bundle生成を適用できる実行境界
- `plan/registry.yaml`
- `plan/document_review_registry.yaml`

## Current verification state

旧作業branchでは、評価toolのローカル検査として既存19ケース、case catalog validator 10ケース、historical actual sample 4ケースを合わせて33ケース相当まで確認済みである。

同branchではGitHub Actions workflowも試作されたが、現在の統合基線ではworkflowを採用しない。runner割当やworkflow生成の成否を、この評価基盤の意味的な成立証拠として扱わない。

```text
evaluation tools reproducible
  != runner assigned
  != GitHub Actions required
  != outcome quality satisfied
```

## Resolution

次を満たした時点でResolvedにできる。

1. execution conformance、structural safety、human outcome review、Product Value / Adoption outcomeの境界が文書化されている。
2. grouping resultの構造検査がpositive / negative testで動作する。
3. review bundle manifestがidentity / digestの整合を検査し、structure PASSをquality PASSへ昇格させない。
4. non-golden case catalogとvalidatorが、意味的な正解を固定せず複数の評価難所を保持できる。
5. historical actual sampleがactual outputの変動を品質順位へ変換せず保存できる。
6. actual E3b-M1b outputにも同じ構造検査を適用し、review bundleを生成できる。
7. 人間レビュー用templateが、単一スコアやAI採点を正解としない形式で用意されている。
8. 評価toolの再現可能な検査とactual M1b実証の責務が分離されている。
9. 上流計画と文書レビュー台帳がcurrent stateへ同期している。

このIssueのResolvedは、成果品質そのものがSatisfiedになったことを意味しない。実際のhuman review、複数caseでのactual比較、実利用時の価値評価は後続Evidenceとして残す。

## Reopen conditions

- 構造検査が意味的品質を暗黙に採点してしまうことが判明した。
- case catalogやhistorical sampleが、実質的なgolden answer / ranking datasetへ変質した。
- KJ法の実践者レビューで、現在の質問群では重要な残差を記録できないことが分かった。
- 別Cognitive Methodで現在の四層分離が成立しない事例が見つかった。
- model / runtime交換時に、品質比較へ必要なProvenanceを保持できないことが判明した。
- Product Value / Requirementの変更により、成果品質の評価責任を見直す必要が生じた。

## Verification

repository同梱の評価toolを、外部model取得なしで再現可能に実行する。actual M1b評価は、固定したinput / source / runtime / model identityとともに別途実行し、structure reportとreview bundleを保存する。

workflowやrunnerの有無は検証手段の選択肢であり、本Issueの意味上の完了条件には含めない。

## Natural Japanese review

M1bのactual Evidence、ISSUE-000067で整理したRealization / Provenance境界、ISSUE-000068のactual model artifact交換、既存V6 / V7 human structured reviewへ戻り、評価責任を過不足なく分離した。

さらに、単一の簡単な入力だけへ評価を閉じないようnon-golden case catalogを設け、期待groupや期待表札を機械的な正解として固定しない停止線を維持した。既存actual runについても、表札やrationaleの差を勝敗へ変換せずhistorical sampleとして保持し、後から同じ入力・実行identity・生成結果へ戻れるようにした。

最後に、現在のCI停止方針へ合わせ、GitHub Actionsのworkflow生成やrunner availabilityを評価基盤そのものの成立条件から外した。意味、要求強度、未検証範囲、Evidence強度を固定したうえで、自然な日本語として一続きに読めることを最重要視して全文を再ドラフトした。
