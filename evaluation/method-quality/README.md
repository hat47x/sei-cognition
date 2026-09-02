# Cognitive Method成果品質の評価基線

更新日: 2026-09-02  
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
- 表札が具体性や差異を消しすぎていないか。
- 入力にない断定を持ち込んでいないか。
- 違和感、異論、保留、残差を次の探索へ持ち越せるか。
- proposalとして人間の壁打ちに使えるか。

レビュー結果は、評価者の役割や経験、対象input / output identityと一緒に残します。

## 4. AIによる品質採点の扱い

current baselineでは、生成AIや別のLLMを品質graderとして採用しません。

AIを使った比較や指摘が将来補助材料として役立つ可能性はありますが、その出力を人間のKJ法レビューと同等の正解にはしません。AI graderを導入する場合は、grader自身の再現性、偏り、根拠、human reviewとの関係を別の評価protocolで検証してから扱います。

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

## 6. Evidenceの読み方

この評価系のcheckerやtemplateが存在すること自体は、成果品質のEvidenceではありません。

- checker testのPASS: 評価コードが想定した構造違反を検出できる限定Executable Evidence
- actual M1b outputへのchecker PASS: その出力が定義済み構造不変条件を満たした限定Executable Evidence
- human review record: 人間による評価観測。条件・評価者・対象を伴って読む
- repeated actual use: Operational / Adoption / Outcomeを検討するための別Evidence

人間レビューが一件成立しても、それだけでproduction品質や一般的なKJ法能力を主張しません。

## 7. ファイル

- `check_grouping_structure.py` — grouping resultの構造不変条件を検査する。
- `test_check_grouping_structure.py` — positive / negative controlを検査する。
- `HUMAN_REVIEW_TEMPLATE.md` — 人間が成果品質と残差を記録する。

## 8. Natural Japanese review

ISSUE-000066のactual model-backed Evidence、ISSUE-000067のRealization / Provenance境界、ISSUE-000068のactual model artifact交換、既存V6 / V7 structured reviewへ戻り、機械検査と人間判断が互いを代替しない構成として整理しました。その後、意味とEvidence強度を固定し、自然な日本語として読み進められることを最重要視して全文を再ドラフトしています。
