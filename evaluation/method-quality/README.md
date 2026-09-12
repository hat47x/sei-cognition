# Cognitive Method成果品質の評価基線

更新日: 2026-09-03  
状態: **Evaluation boundary established — quality itself is Not Yet Verified**

## 1. この評価系の役割

このディレクトリは、Cognitive Methodを「実行できた」ことと、その出力が人間の探索やKJ法の実践にとって「よい成果だった」ことを分けて扱うための評価基線です。

E3b-M1bでは、actual model inferenceを含むKJ Atlasの実行結果をSEI Cognitive Method Applicationへ戻せることまで確認しました。しかし、実行経路が成立しただけでは、groupingや表札の意味的品質は分かりません。

そこで、評価を少なくとも次の四層に分けます。

```text
1. execution conformance
   実process / model / Methodが所定の境界で実行できたか

2. structural safety / integrity
   入出力identityやheld状態など、機械的に確認できる不変条件を壊していないか

3. Cognitive Method outcome quality
   cardの訴え、束ね方、表札、残差が、人間の探索にとって妥当・有用か

4. Product Value / Adoption outcome
   実利用で判断記憶の継続や意思決定支援に価値が生じたか
```

これらは互いに代用できません。

```text
actual inference PASS
  + structural check PASS
  != KJ-method outcome quality satisfied
  != Product Value satisfied
```

ISSUE-000071は、この四層を分けて評価できる基線が整ったためResolvedです。これは成果品質そのものがSatisfiedになったという意味ではありません。

## 2. 機械検査が扱う範囲

`check_grouping_structure.py`は、KJ Atlasのgrouping resultについて次だけを検査します。

- group内のcard IDが入力に存在する。
- held cardがgroupへ再混入していない。
- held cardが`excludedCardIds`へ保持されている。
- `excludedCardIds`に入力に存在しないIDが紛れ込んでいない。
- 同じcardが複数groupへ重複所属していない。
- 同じcardがgroupと`excludedCardIds`の双方へ現れない。
- groupが空ではない。
- group labelが空ではない。
- 検査したrequest / resultのSHA-256を記録する。

非held cardがgroupへ入らず残ることは構造違反にしません。KJ法では、無理に束ねないこと自体が意味を持ち得るためです。

次は機械検査の対象外です。

- labelがよい言葉か。
- rationaleが深いか。
- groupingがcardの「訴え」を捉えているか。
- 分類語の近さだけで束ねていないか。
- 人間がそのproposalを採用すべきか。

これらをcheckerへ埋め込むと、人間の判断を実装上の正解へ先取りしてしまうため、行いません。

## 3. 人間レビューが扱う範囲

`HUMAN_REVIEW_TEMPLATE.md`は、Cognitive Method outputを人間が読み、意味的な成果品質と残差を記録するための様式です。

単一の総合点は設けません。特に、次の問いを一つの数値へ潰さないことを重視します。

- cardの訴えが保たれたか。
- 無理な束ねが起きていないか。
- 明らかに響き合うcardを見落としていないか。
- 表札が具体性や差異を消しすぎていないか。
- 入力にない断定・因果・評価を持ち込んでいないか。
- 違和感、異論、保留、残差を次の探索へ持ち越せるか。
- proposalとして人間の壁打ちに使えるか。

レビュー結果は、評価者の役割や経験、対象input / output identityと一緒に残します。

## 4. AI補助観測の扱い

current baselineでは、生成AIや別LLMを品質graderとして採用しません。

AIによる比較や指摘は、人間が見るべき論点を見つける補助として利用できます。しかし、その出力を人間のKJ法レビューと同等の正解にはしません。

PR #73では、保存済みactual M1b 2 runの差を`historical/ai-supplemental-comparison.json`へ保存しました。

この記録は次を明示しています。

```text
reviewAuthority = non_authoritative_ai_supplement
humanReviewCompleted = false
qualityJudgement = not_evaluated
winnerSelection = false
goldenLabel = false
machineScore = false
```

AIの観測はHuman Review TemplateのQ1〜Q8へそのまま転記せず、人間が元cardとactual resultを読み直すための補助材料として使います。

## 5. 生成結果の変動をどう扱うか

M1bでは、同じprompt digestと同じ実行identityでも、runによってgroup labelやrationaleが変化しました。この差を消したり、execution failureとして扱ったりしません。

比較時には少なくとも次を別々に保持します。

- input identity / digest
- Method Definition / Realization / source revision
- model / runtime等の必要なProvenance
- raw Method output / result digest
- structural check result
- human review record

```text
same input identity
  + same execution identity
  != same generated wording
  != same human judgement
```

複数出力を比較するときも、自動的な勝者を決めることを目的にしません。差異そのものを、Method Realizationの性質を理解するための観測として残します。

## 6. actual出力をreview-ready bundleへする

actual outputを人間レビューへ渡すときは、少なくとも次を対応付けられるようにします。

- Method request
- actual grouping result
- model call Evidence
- structure report
- runtime / model identity
- repository commit
- Method source commit
- 各ファイルのdigest

`build_review_bundle_manifest.py`は、このidentity / digest対応をmanifestへまとめます。structure reportが記録したrequest / result digestと実ファイルが一致しない場合は、manifest生成を拒否します。

manifest自身は成果品質を採点しません。

```text
review bundle preserved
  = output / provenance / structureを後から再確認できる
  != human review completed
  != Cognitive Method outcome quality satisfied
```

### historical actual runからの再構成

PR #72では、成功済みRun `33596839607` / Job `100141890796`について、repositoryに保存していたhistorical sampleとGitHubに残る当該job logからreview-ready bundleを再構成しました。

保存先:

`historical/M1B-RUN-33596839607/`

保存物:

- `request.json`
- `result.json`
- `model-evidence.json`
- `runtime-version.txt`
- `model-list.txt`
- `structure-report.json`
- `review-manifest.json`
- `reconstruction-provenance.json`

structure checkは`passed`、`violations = []`で、`qualityJudgement = not_evaluated`を維持しています。

元workflowはartifactを保存していませんでした。そのため、このbundleを当時のworkflow artifactとは扱いません。`reconstruction-provenance.json`で`originalWorkflowArtifactAvailable = false`を明示し、historical sampleと保存job logからの再構成物として扱います。

## 7. 正解を固定しない評価ケース

`case_catalog.json`には、簡単な一ケースだけでは捉えにくい複数の難所を保持します。ただし、「正しいgrouping」や「正しい表札」をgolden answerとして置きません。

現在は次の観測点を含みます。

- 語彙が違っていても訴えが近いcardを見いだせるか。
- 同じ話題語でも訴えが異なるcardを安易に一括しないか。
- 利点と懸念の緊張関係を勝手に解消しないか。
- 二つのまとまりをまたぐ橋cardの可能性を排他的な分類で消さないか。
- held、異論、未整理の残差を処理済みに見せないか。
- 全cardを束ね切ること自体を成果にせず、孤立cardを残せるか。

`validate_case_catalog.py`は、ケース集の形式と停止線だけを検査します。`expectedGroups`、`expectedLabel`、`qualityScore`等を追加すると失敗させます。

```text
review focus
  = 人間が見るべき問い
  != machine-authoritative answer
```

## 8. historical actual sample

`historical_actual_samples.json`には、将来の比較レビューから参照できるようactual M1b出力を保存しています。

current baselineでは次の2 runを保持します。

- Run `33596839607` / Job `100141890796`
  - label: `生活習慣`
- Run `33609470323` / Job `100180968648`
  - label: `在宅勤務`

両runは、同じrequest、KJ Atlas source revision、Ollama `0.32.14`、`qwen2.5:0.5b`、observed model ID prefix、prompt SHA-256を共有しています。一方、生成されたlabel / rationaleは一致しません。

これらを「正解例」「優良例」「失敗例」にはしません。actualに観測された出力とsource identityを、後から同じ条件へ戻るためのhistorical sampleとして保存します。

## 9. 再現可能な検査

評価toolの意味上の責務をGitHub Actionsへ依存させません。

current baselineでは、repository同梱のPython test / validatorを直接実行できます。

主な検査は次です。

- structure checker test
- review bundle manifest test
- case catalog validator test
- historical actual sample test
- historical review bundle reconstruction test
- AI supplemental observation boundary test
- current `case_catalog.json` validation

確認済みの検査資産は累積39ケース相当です。

- structure checker + review manifest: 19ケース
- case catalog validator: 10ケース
- historical actual sample: 4ケース
- historical review bundle: 3ケース
- AI supplemental observation boundary: 3ケース

historical review bundle 3ケースとAI supplemental observation boundary 3ケースは、2026-09-03にローカルでPASSを確認しています。39件すべてを同一CI runで一括実行したという意味ではありません。

GitHub Actions、外部runner、将来のCIを利用する場合も、これらは検証手段です。workflowの存在やrunner availabilityを、成果品質評価の意味上の成立条件にはしません。

## 10. Evidenceの読み方

この評価系のcheckerやtemplateが存在すること自体は、成果品質のEvidenceではありません。

- checker testのPASS: 想定した構造違反を検出できる限定Executable Evidence
- manifest generator testのPASS: review bundleのidentity / digest対応を検査できる限定Executable Evidence
- case catalog validator testのPASS: ケース定義とnon-golden境界を検査できる限定Executable Evidence
- historical sample testのPASS: actual出力のvariationを構造・identityとともに保持できる限定Executable Evidence
- actual outputへのchecker PASS: その出力が定義済み構造不変条件を満たした限定Executable Evidence
- review-ready bundle: 対象runのinput / output / execution / structureを人間が再確認できる記録
- AI supplemental observation: 人間レビュー前の非権威的な補助観測
- human review record: 人間による評価観測。条件・評価者・対象と一緒に読む
- repeated actual use: Operational / Adoption / Outcomeを検討するための別Evidence

人間レビューが一件成立しても、それだけでproduction品質や一般的なKJ法能力を主張しません。

## 11. ファイル

- `check_grouping_structure.py` — grouping resultの構造不変条件だけを検査する。
- `test_check_grouping_structure.py` — checkerのpositive / negative control。
- `build_review_bundle_manifest.py` — review bundleのrun identity、source commit、file digestを対応付ける。
- `test_build_review_bundle_manifest.py` — manifest生成器のidentity / digest検査とquality非昇格境界を検査する。
- `case_catalog.json` — golden groupingを持たず、意味上の難所とhuman review focusを保持する評価ケース集。
- `validate_case_catalog.py` — case catalogの形式とnon-golden境界だけを検査する。
- `test_validate_case_catalog.py` — golden fieldやmachine scoring等を拒否する制御ケース。
- `historical_actual_samples.json` — actual M1b runのinput / output / source identityを品質順位なしで保存する。
- `test_historical_actual_samples.py` — historical sampleの構造、identity、variation、non-golden境界を検査する。
- `historical/M1B-RUN-33596839607/` — actual historical outputから再構成したreview-ready bundle。
- `test_historical_review_bundle.py` — 再構成bundleをrepository toolから再生成できることを検査する。
- `historical/ai-supplemental-comparison.json` — human judgementを代替しないAI補助観測。
- `test_ai_supplemental_comparison.py` — AI補助観測がwinner / golden label / quality judgementへ変質しないことを検査する。
- `HUMAN_REVIEW_TEMPLATE.md` — 人間が成果品質と残差を記録する。

## 12. Natural Japanese review

ISSUE-000066のactual model-backed Evidence、ISSUE-000067のRealization / Provenance境界、ISSUE-000068のactual model artifact交換、ISSUE-000071、既存V6 / V7 structured reviewへ戻り、機械検査と人間判断が互いを代替しない構成として整理しました。

以前のREADMEには、actual outputをActions artifactとして保存することや、軽量評価toolをGitHub Actionsで回すことをcurrent前提とする記述が残っていました。PR #70でActionsをcurrent baselineから外したため、「何を保存・検査するか」と「どの実行基盤を使うか」を分けて書き直しました。

PR #72でhistorical actual runからreview-ready bundleを再構成できることを確認しましたが、元workflow artifactが存在しなかった事実は隠していません。PR #73のAI補助観測もhuman reviewとは別の記録として明示しています。

評価ケースやhistorical sampleは正解集にせず、意味的近接、話題語と訴えの違い、緊張、橋、held・異論・残差、孤立、生成結果の揺れへ後から戻るための材料として維持します。

意味とEvidence強度を変えず、自然な日本語として読み進められることを最重要視して全文を再ドラフトしました。