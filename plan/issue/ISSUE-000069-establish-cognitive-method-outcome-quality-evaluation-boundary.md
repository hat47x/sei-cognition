# ISSUE-000069: Cognitive Method成果品質の評価境界を確立する

Status: **Open**  
Priority: **1**  
Related ADRs: **ADR-0017, ADR-0018, ADR-0020, ADR-0021, ADR-0025**  
Product Milestone: **PMS-06**  
Updated: 2026-09-03

## Goal

actual Cognitive Methodを「実行できた」ことと、その出力が人間の探索やKJ法実践にとって「よい成果だった」ことを分離して評価できる基線を作る。

このIssueでは、E3b-M1bで成立したactual model-backed executionと、ISSUE-000068で実証したactual model artifact交換を入力として、次の四層を混同しない評価境界を設ける。

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

一方、同じprompt SHA-256、同じKJ Atlas revision、同じruntime / model identityを使ったM1bの複数runでも、生成されたgroup labelやrationaleは一致しなかった。既存Evidenceはこの差を隠さず、次の境界を明示している。

```text
same prompt digest
  != same generated wording
  != same cognitive quality
```

この変動はexecution conformanceを否定するものではない。一方、KJ AtlasがJSONとして受理できたことやmodel artifactを交換できたことだけを根拠に、groupingや表札がKJ法として妥当・有用だったと扱うこともできない。

実際、既存actual M1b runでは、同じ二枚を同じgroupへ束ねながら、一方は表札を`生活習慣`、別runは`在宅勤務`とした。構造上は受理できても、前者は元cardの訴えに対して広すぎ、後者も共有する核そのものではなく話題名に近い。rationaleにも入力にない分類や因果風の言い換えが入り得る。この観測はhuman reviewの代用ではないが、structure checkerだけでは成果品質を判定できないことを具体的に示している。

したがって次の段階では、実行成立と成果品質を同じPASS / FAILへ押し込まず、評価対象ごとに責任とEvidenceの高さを分ける必要がある。

## Questions

1. Cognitive Method outputについて、意味内容を採点せず機械的に確認できる構造上の不変条件は何か。
2. KJ法としてのgrouping、表札、残差の扱い等について、人間のレビューで何を確認すべきか。
3. 同じ入力から異なる生成結果が得られた場合、差異を「ばらつき」として捨てず、比較可能な記録としてどう保持するか。
4. model出力品質、KJ法としての成果品質、Product Valueへの寄与を、どのEvidence段階で別々に扱うか。
5. 評価方法の都合からOllama、Qwen、KJ Atlas固有fieldをSOZA Universal Contractへ持ち込まずに済むか。
6. 一つの簡単な入力だけに依存せず、意味的近接、話題語による誤分類、緊張、橋、held・異論・残差、孤立を残す必要性をどう評価入力へ含めるか。
7. 評価ケースを作ることが、機械的なgolden groupingや期待表札の固定へ変質しないよう、どこに停止線を置くか。

## Constraints

- 生成AIまたは自動評価器の品質判定を、人間のKJ法レビューと同等の正解として扱わない。
- model名、runtime名、temperature、特定prompt等をUniversal Cognitive Method Contractの必須fieldへ先取りしない。
- 構造検査のPASSを、groupingや表札の意味的品質のPASSへ昇格させない。
- 人間レビューの記録を、直ちにOperational EvidenceやAdoption / Outcome Evidenceへ昇格させない。
- 単一の総合点だけで品質を表現しない。少数の数値へ圧縮する場合も、元の観測・違和感・残差を失わない。
- held / excluded、入力card identity、生成group、Provenance等、後から判断過程を辿るための情報を保持する。
- KJ法の成果物をRecommendationやDecisionへ自動昇格させない既存境界を維持する。
- 評価case catalogへ`expectedGroups`、`expectedLabel`、`qualityScore`等の機械的な正解を持ち込まない。
- case catalogの妥当性検査は、形式とnon-golden境界に限定し、ケースの意味的な正解を採点しない。
- 現時点では新しいStable Requirement / Scenarioを追加しない。必要性は評価実証の後で再監査する。

## Required scenarios / experiments

### EVAL-Q1 — 機械的な構造検査

actualまたはfixtureのgrouping resultに対して、少なくとも次を検査できるようにする。

- group内のcard IDが入力候補に存在する。
- held cardがgroupへ再混入していない。
- held cardと`excludedCardIds`の対応を確認できる。
- 同じcardが複数groupへ重複所属していない。
- 同じcardがgroupと`excludedCardIds`の双方へ同時に現れない。
- group labelが空でない。
- 検査対象のinput / result digestを記録できる。

これらは**構造安全性の検査**であり、groupingの意味的品質を採点しない。

### EVAL-Q2 — 人間によるstructured review

少なくとも次を単一スコアへ潰さず記録できるreview templateを作る。

- cardの「訴え」が保たれているか。
- 分類語の近さだけで束ねていないか。
- 無理に一つの島へ押し込めていないか。
- 表札が元cardの具体性や差異を消しすぎていないか。
- 入力にない断定・因果・評価を持ち込んでいないか。
- 残すべき違和感、異論、未整理部分が何か。
- その出力を人間がproposalとして使えるか、手直しが必要か、採用しないか。

### EVAL-Q3 — 同一条件で異なる生成結果を保持する

同じprompt digestから異なるlabel / rationaleが出た既存M1b Evidenceを、execution failureではなく品質評価の入力例として扱う。

比較時には、どちらが優れているかを自動推定せず、入力identity、実行identity、生成結果、review結果を別々に保持する。

### EVAL-Q4 — actual M1bへの評価基盤接続

M1bのactual model-backed workflowで得たKJ Atlas resultへEVAL-Q1の構造検査を通す。

actual request、result、model call Evidence、structure report、runtime / model identityをreview bundleとして保持し、manifestでrun / source commit / file digestを対応付ける。

このworkflowがsuccessしても、成立するのは「actual outputに対して評価基盤の機械検査を実行し、後から同じ対象へ戻れる」というScoped Executable Evidenceまでとする。

```text
structure check PASS
  + review bundle preserved
  != grouping quality satisfied
  != KJ-method outcome quality satisfied
  != Product Value satisfied
```

### EVAL-Q5 — non-golden case catalog

一つの簡単なM1b入力だけでは捉えにくい難所を、複数の評価ケースとして保持する。

current catalogでは少なくとも次を含める。

- 語彙が異なるが訴えが近いcard。
- 同じ話題語を含むが訴えが異なるcard。
- 利点と懸念が緊張したまま残るcard。
- 二つのまとまりをまたぐ橋になり得るcard。
- held、異論、未整理の残差を含むcase。
- 一部だけが近く、残りは孤立させた方が自然なcase。

case catalogは「何を観測したいか」だけを持ち、期待groupや期待表札を正解として固定しない。

validatorは次を確認する。

- schemaとIDが整合している。
- card IDがcase内で重複していない。
- review focusが空でない。
- held状態の表現が想定範囲にある。
- `expectedGroups`、`expectedLabel`、`qualityScore`等のgolden fieldが入っていない。
- machine scoringが無効であり、outcome qualityにはhuman reviewが必要というルールが維持されている。

```text
case catalog validation PASS
  = evaluation input boundary intact
  != Method output quality PASS
```

### EVAL-Q6 — 軽量評価tool CI

case catalogや評価toolの変更を、actual model取得を必要としない軽量workflowでも検査する。

対象は少なくとも次とする。

- grouping structure checker test
- review bundle manifest test
- case catalog validator test
- current `case_catalog.json`のvalidation

actual M1b実証と軽量評価tool回帰を別の責務として観測できるようにする。

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
- `.github/workflows/method-quality-evaluation.yml`
- E3b-M1b actual workflowへの構造検査・review bundle接続
- `plan/registry.yaml`
- `plan/document_review_registry.yaml`
- 必要な上流計画 / Product Milestoneの同期

## Resolution

次を満たした時点でResolvedにできる。

1. execution conformance、structural safety、human outcome review、Product Value / Adoption outcomeの境界が文書化されている。
2. grouping resultの構造検査がpositive / negative testで動作する。
3. review bundle manifestがidentity / digestの整合を検査し、structure PASSをquality PASSへ昇格させない。
4. non-golden case catalogとvalidatorが、意味的な正解を固定せず複数の評価難所を保持できる。
5. actual E3b-M1b outputにも同じ構造検査を適用し、review bundleを生成できる。
6. 人間レビュー用templateが、単一スコアやAI採点を正解としない形式で用意されている。
7. 軽量評価tool CIとactual M1b CIの責務が分離して観測できる。
8. 上流計画と文書レビュー台帳がcurrent stateへ同期している。
9. 対象CIがrunner上で実行され、必要な検査がsuccessしている。

このIssueのResolvedは、**成果品質そのものがSatisfiedになったことを意味しない**。実際のhuman review、複数caseでのactual比較、実利用時の価値評価は後続Evidenceとして残す。

CI failureは修正対象だが、pushを停止する条件にはしない。runner未割当を含む赤いrunが残っていても、評価系の改善や修正commitは通常どおりpushする。Resolved、merge、Evidence確定に必要なCI条件は、それぞれのgateとして通常pushから分離する。

## Reopen conditions

- 構造検査が意味的品質を暗黙に採点してしまうことが判明した。
- case catalogがgolden groupingや単一scoreによる機械採点へ変質する。
- KJ法の実践者レビューで、現在の質問群では重要な残差を記録できないことが分かった。
- 別Cognitive Methodで現在の四層分離が成立しない事例が見つかった。
- model / runtime交換時に、品質比較へ必要なProvenanceを保持できないことが判明した。
- Product Value / Requirementの変更により、成果品質の評価責任を見直す必要が生じた。

## CI / verification

- `Method Quality Evaluation`で評価tool testとcase catalog validationを実行する。
- E3b-M1b actual model-backed workflowで、actual KJ Atlas resultへ構造検査を適用しreview bundleを生成する。
- Plan Registry / Document Review Registryのintegrity checkを通す。
- 既存Semantic Runtime ConformanceとE3b integration回帰を壊さない。

CI successは評価基盤が実行可能であることのEvidenceであり、Cognitive Method成果品質やProduct Valueの成立証明ではない。

## Natural Japanese review

M1bのactual Evidence、ISSUE-000067で整理したRealization / Provenance境界、ISSUE-000068のactual model artifact交換、既存V6 / V7 human structured reviewの考え方へ戻り、評価責任を過不足なく分離した。

既存actual出力では、構造上は同じ二枚を妥当に束ねながらも、表札やrationaleの意味品質に検討余地が残ることを確認した。この観測をhuman reviewの代用にはせず、構造検査と意味レビューを分ける必要性の具体例として扱っている。

また、評価入力を増やす際も、期待groupや期待表札を正解として固定しない。意味的近接、同じ話題語の罠、緊張、橋、held・異論・残差、孤立を残す必要性をreview focusとして保持し、validatorはそのnon-golden境界だけを検査する。軽量な評価tool CIとactual model実証も分離した。

意味、要求強度、未検証範囲、Evidence強度を固定し、自然な日本語として一続きに読めることを最重要視して全文を再ドラフトした。
