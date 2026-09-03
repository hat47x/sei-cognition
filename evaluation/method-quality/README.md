# Cognitive Method成果品質の評価基線

更新日: 2026-09-03  
状態: **Evaluation baseline — quality itself is Not Yet Verified**

## 1. この評価系の役割

このディレクトリは、Cognitive Methodを「実行できた」ことと、その出力が人間の探索やKJ法実践にとって「よい成果だった」ことを分けて扱うための評価基線です。

E3b-M1bでは、actual model inferenceを含むKJ Atlasの実行結果をSOZAのCognitive Method Applicationへ戻せることまで確認しました。一方、実行経路が成立しただけでは、groupingや表札の意味的品質は分かりません。

そこで、評価を少なくとも次の四層に分けます。

```text
1. execution conformance
   実process / model / Methodが所定の境界で実行できたか

2. structural safety / integrity
   入出力identityやheld状態など、機械的に確認できる不変条件を壊していないか

3. Cognitive Method outcome quality
   カードの訴え、束ね方、表札、残差が、人間の探索にとって妥当・有用か

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

## 2. 機械検査が扱う範囲

`check_grouping_structure.py`は、KJ Atlasのgrouping resultについて次だけを検査します。

- group内のcard IDが入力に存在する。
- held cardがgroupへ再混入していない。
- held cardが`excludedCardIds`へ保持されている。
- `excludedCardIds`に入力に存在しないIDが紛れ込んでいない。
- 同じcardが複数groupへ重複所属していない。
- 同じcardがgroupと`excludedCardIds`の双方へ同時に現れない。
- groupが空ではない。
- group labelが空ではない。
- 検査したrequest / resultのSHA-256を記録する。

非held cardがgroupへ入らず残ることは、構造違反にしません。KJ法では無理に束ねないこと自体が重要になり得るためです。

また、次は機械検査の対象外です。

- labelがよい言葉か。
- rationaleが深いか。
- groupingがカードの「訴え」を捉えているか。
- 分類語の近さだけで束ねていないか。
- 人間がそのproposalを採用すべきか。

これらをcheckerへ埋め込むと、評価者の判断を実装上の正解へ先取りするため、行いません。

## 3. 人間レビューが扱う範囲

`HUMAN_REVIEW_TEMPLATE.md`は、Cognitive Method outputを人間が読み、意味的な成果品質を記録するための様式です。

単一の総合点は設けません。特に、次のような異なる問いを一つの数値へ潰さないことを重視します。

- カードの訴えが保たれたか。
- 無理な束ねが起きていないか。
- 明らかに響き合うcardを見落としていないか。
- 表札が具体性や差異を消しすぎていないか。
- 入力にない断定・因果・評価を持ち込んでいないか。
- 違和感、異論、保留、残差を次の探索へ持ち越せるか。
- proposalとして人間の壁打ちに使えるか。

レビュー結果は、評価者の役割や経験、対象input / output identityと一緒に残します。

## 4. AIによる品質採点の扱い

current baselineでは、生成AIや別のLLMを品質graderとして採用しません。

AIを使った比較や指摘が補助材料として役立つ可能性はありますが、その出力を人間のKJ法レビューと同等の正解にはしません。AI graderを導入する場合は、grader自身の再現性、偏り、根拠、human reviewとの関係を別の評価protocolで検証してから扱います。

```text
AI critique
  = possible auxiliary observation
  != authoritative quality judgement
```

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

## 6. actual出力をレビューへ渡す

`External Model-backed Method E3b M1b`では、実行時の結果をログ表示だけで終わらせず、人間レビューへ引き渡せるActions artifactとして保持します。

review bundleには少なくとも次を含めます。

- KJ Atlasへ渡したrequest
- actual modelから得たgrouping result
- model callの実行Evidence
- grouping structure checkerのreport
- review bundle manifest
- 実行したOllama version
- 取得済みmodel identity一覧

manifestは、workflow run、repository commit、Method source commitと各ファイルのSHA-256 / byte sizeを対応付けます。さらに、structure reportが記録したrequest / result digestと実ファイルのdigestが一致しない場合はbundle生成を拒否します。manifest自身は成果品質を採点しません。

```text
review bundle preserved
  = output / provenance / structureを後から再確認できる
  != human review completed
  != Cognitive Method outcome quality satisfied
```

workflowが途中で失敗した場合にも、そこまでに生成されたファイルは可能な範囲でartifactへ残します。欠けたファイルがある場合は、その欠落自体を実行状況の一部として扱い、完全なreview bundleが成立したものとはみなしません。

## 7. 正解を固定しない評価ケース

簡単な一ケースだけで成果品質を語らないため、`case_catalog.json`に複数の評価入力を用意します。ただし、ここへ「正しいgrouping」や「正しい表札」をgolden answerとして置きません。

ケースが持つのは、入力cardと、人間がレビュー時に見落としたくない観測点です。現在は次の難所を含めています。

- 語彙が違っていても訴えが近いcardを見いだせるか。
- 同じ話題語を含んでいても、訴えが異なるcardを安易に一括しないか。
- 利点と懸念の緊張関係を、どちらか一方へ勝手に解消しないか。
- 二つのまとまりをまたぐ橋cardの可能性を、排他的な分類で消さないか。
- held、異論、未整理の残差を処理済みに見せないか。
- 全cardを束ね切ること自体を成果にせず、孤立cardを残せるか。

`validate_case_catalog.py`は、このケース集の形式と停止線だけを検査します。`expectedGroups`、`expectedLabel`、`qualityScore`等をケースへ追加すると失敗させます。

```text
review focus
  = 人間が見るべき問い
  != machine-authoritative answer

case catalog valid
  != Method output quality satisfied
```

ケース集を増やす場合も、機械採点のための隠れた正解表へ変えません。

## 8. historical actual sample

既存M1bのactual出力を、将来の比較レビューから参照できるよう`historical_actual_samples.json`へ保存します。

current baselineでは次の2 runを保持します。

- Run `33596839607` / Job `100141890796`
  - label: `生活習慣`
- Run `33609470323` / Job `100180968648`
  - label: `在宅勤務`

両runは、同じrequest、KJ Atlas source revision、Ollama `0.32.14`、`qwen2.5:0.5b`、observed model ID prefix、prompt SHA-256を共有しています。一方、生成されたlabel / rationaleは一致しません。

これらを「正解例」「優良例」「失敗例」にはしません。actualに観測された出力とsource identityを、後から同じ条件へ戻るためのhistorical sampleとして保存します。

`test_historical_actual_samples.py`では次だけを確認します。

- 各sampleが定義済みstructure checkerを通過する。
- `qualityJudgement`は`not_evaluated`のままである。
- 同じ実行identityから異なるgenerated wordingが保存されている。
- run / job / repository commitを区別して追跡できる。
- `expectedGroups`、`expectedLabel`、`qualityScore`、`preferred`、`winner`等を持たない。

```text
historical sample retained
  = actual variation can be revisited
  != preferred output selected
  != quality judgement completed
```

この4テストは手元で実行し、`Ran 4 tests` / `OK`を確認しています。既に確認済みのstructure checker 15件、manifest 4件、case catalog validator 10件と合わせ、current evaluation toolは33ケース相当です。

## 9. 軽量評価tool CI

case catalogや評価toolの変更は、actual modelを取得しない`Method Quality Evaluation` workflowでも検査します。

このworkflowは次を担当します。

- structure checker test
- review bundle manifest test
- case catalog validator test
- historical actual sample test
- current `case_catalog.json`のvalidation

actual M1b workflowはactual model-backed executionとreview bundle生成を担当します。軽量評価tool回帰とactual execution Evidenceを一つのworkflow責務へ混ぜません。

## 10. Evidenceの読み方

この評価系のcheckerやtemplateが存在すること自体は、成果品質のEvidenceではありません。

- checker testのPASS: 想定した構造違反を検出できる限定Executable Evidence
- manifest generator testのPASS: review bundleのidentity / digest対応と停止線を検査できる限定Executable Evidence
- case catalog validator testのPASS: ケース定義とnon-golden境界を検査できる限定Executable Evidence
- historical sample testのPASS: actual出力のvariationを構造・identityとともに保持できる限定Executable Evidence
- actual M1b outputへのchecker PASS: その出力が定義済み構造不変条件を満たした限定Executable Evidence
- actual M1b review bundle: 対象runのinput / output / execution / structureを後から人間が再確認できる記録
- human review record: 人間による評価観測。条件・評価者・対象を伴って読む
- repeated actual use: Operational / Adoption / Outcomeを検討するための別Evidence

人間レビューが一件成立しても、それだけでproduction品質や一般的なKJ法能力を主張しません。

## 11. ファイル

- `check_grouping_structure.py` — grouping resultの構造不変条件だけを検査する。
- `test_check_grouping_structure.py` — checkerのpositive / negative controlを検査する。
- `build_review_bundle_manifest.py` — review bundleのrun identity、source commit、file digestを対応付け、request / result digestの不一致を拒否する。
- `test_build_review_bundle_manifest.py` — manifest生成器のidentity / digest検査と、structure PASSをquality PASSへ昇格しない停止線を検査する。
- `case_catalog.json` — golden groupingを持たず、意味上の難所とhuman review focusを保持する評価ケース集。
- `validate_case_catalog.py` — case catalogの形式とnon-golden境界だけを検査する。
- `test_validate_case_catalog.py` — duplicate ID、golden field、machine scoring等を拒否するpositive / negative control。
- `historical_actual_samples.json` — actual M1b runのinput / output / source identityを品質順位なしで保存する。
- `test_historical_actual_samples.py` — historical sampleの構造、identity、variation、non-golden境界を検査する。
- `HUMAN_REVIEW_TEMPLATE.md` — 人間が成果品質と残差を記録する。

## 12. Natural Japanese review

ISSUE-000066のactual model-backed Evidence、ISSUE-000067のRealization / Provenance境界、ISSUE-000068のactual model artifact交換、既存V6 / V7 structured reviewへ戻り、機械検査と人間判断が互いを代替しない構成として整理しました。

actual outputは一時ログだけに閉じ込めず、request、result、実行Evidence、structure report、review bundle manifestを同じrunの材料として人間へ渡せるようにしました。manifestはidentityとdigestの整合だけを担い、成果品質の判断を機械へ先取りしません。

評価ケースは期待groupや期待表札を正解として埋め込まず、意味的近接、話題語と訴えの違い、緊張、橋、held・異論・残差、孤立を残す必要性という観測点だけを保持します。既存actual出力も優劣を付けずhistorical sampleとして保存し、同じ実行identityでも生成文が変わり得ることを後から再確認できるようにしました。

意味とEvidence強度を固定し、自然な日本語として読み進められることを最重要視して全文を再ドラフトしました。
