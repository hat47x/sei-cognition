# Cognitive Method成果品質 Human Review Template

更新日: 2026-09-03  
位置づけ: **Structured human review record template — この様式自体はEvidenceではない**

## 1. 使い方

このテンプレートは、Cognitive Methodが生成したgrouping、表札、rationale等を人間が読み、その成果品質を単一スコアへ潰さず記録するためのものです。

機械的なstructure checkがPASSしていても、KJ法としてよい成果だとは判断しません。また、一件のhuman reviewだけから一般的なmodel品質、Operational Evidence、Adoption / Outcome Evidenceを導きません。

レビューでは、生成結果を「正解か不正解か」だけで閉じず、どこに納得があり、どこに違和感や残差が残るかを記録します。

## 2. Review context

- Review date:
- Case ID:
- Reviewer role / context:
- KJ法に関する経験・前提:
- Workflow run / review bundle artifact:
- Input identity / digest:
- Method Definition / Realization:
- Method source revision:
- Output identity / digest:
- Structure report identity / digest:
- Model / runtime等のProvenance（必要な場合）:
- レビュー前にmodel / runtime identityを知っていたか: yes / no / partial

workflow artifactを使う場合は、request、result、model call Evidence、structure reportが同じrunに属することを確認し、そのrunまたはartifactを上欄へ記録します。artifactの存在自体を品質判定の根拠にはしません。

model名やruntime名は評価結果の意味を再構成するために必要な範囲で記録します。特定modelをSOZAの標準として扱うための欄ではありません。

## 3. 元データの確認

レビュー前に、可能な限り生成結果だけでなく元cardとheld / unresolved状態を確認します。

- 対象card一覧:
- held / excluded card:
- 既存island / contextがある場合の概要:
- その他、評価時に見えていた文脈:

## 4. 成果品質の問い

各項目について、次のいずれかを記録します。

- `よく保たれている`
- `概ね保たれているが手直しが必要`
- `重要な問題がある`
- `判断保留`
- `このケースでは該当しない`

結果だけでなく、そう感じた具体的なcard、表札、言葉、引っかかりを残します。

| ID | 問い | 結果 | 根拠・違和感・残差 |
|---|---|---|---|
| Q1 | 各cardが訴えていることは、束ねた後にも失われず残っているか |  |  |
| Q2 | 表面的な分類語の近さだけでなく、cardが訴えていることの近さで束ねられているか |  |  |
| Q3 | 本来は離しておくべきcardを、無理に同じ島へ押し込めていないか |  |  |
| Q4 | 明らかに響き合っているcardを見落としていないか。ただし、孤立cardを無理に束ねる必要はない |  |  |
| Q5 | 表札は元cardの具体性や差異を消しすぎず、束の核を言葉にできているか |  |  |
| Q6 | 表札やrationaleが、元cardにはない断定・因果・評価を勝手に持ち込んでいないか |  |  |
| Q7 | held、異論、違和感、未整理部分など、残すべきものを処理済みのように見せていないか |  |  |
| Q8 | この出力は、次の壁打ち・配置・統合・文章化を考えるためのproposalとして役立つか |  |  |

## 5. とくに残したい観測

- 一見もっともらしいが、cardを読み返すとずれている箇所:
- 言葉は粗いが、束ね方そのものには意味を感じる箇所:
- 表札を変えれば使えそうな箇所:
- grouping自体を組み替えたい箇所:
- あえて孤立・保留のまま残したいcard:
- 生成結果を見たことで新たに気づいた問い:
- その他の違和感・残差:

「違和感があるがまだ言葉にできない」ことも、有効な記録として残します。理由を無理に確定させません。

## 6. Proposalとしての扱い

最終的な扱いは、次のいずれかから選びます。これはmodelの能力を一般評価する判定ではなく、**このケースのこの出力をどう扱うか**の記録です。

- `そのまま壁打ちに使える`
- `手直しすれば使える`
- `採用しない`
- `判断保留`

扱い:

手直しする場合の内容:

理由:

## 7. 比較レビューを行う場合

複数の生成結果を比較する場合も、総合順位を必須にしません。それぞれについて同じ質問群を記録し、次を比較します。

- どのcardの訴えを拾ったか。
- どこで差異を消したか。
- どこに新しい断定を持ち込んだか。
- どの出力がどの種類の壁打ちに使いやすいか。
- 両方に残る共通の問題は何か。
- 一方だけを見ていたら気づかなかった残差は何か。

同じinput / prompt digestでも生成内容が異なり得ます。差異そのものを失敗や優劣へ即座に変換せず、観測として残します。

## 8. AIによる補助評価を併用した場合

current baselineではAI graderを正解として使用しません。別AIによる指摘を補助的に参照した場合は、human reviewと混ざらないよう次へ分離して記録します。

- 使用したAI / method:
- AIが指摘した内容:
- 人間が同意した点:
- 人間が同意しなかった点:
- 判断保留とした点:

AIの評価結果を、そのままQ1〜Q8のhuman judgementへ転記しません。

## 9. Evidence boundary

このreview recordは、対象ケースについて人間が何を観測・判断したかを残すものです。

```text
one human review
  != general model quality proven
  != KJ-method certification
  != Operational Evidence
  != Adoption / Outcome Evidence
```

反復評価、複数case、複数reviewer、実利用文脈等を扱う場合は、目的に応じて別protocolを設計します。

## 10. Natural Japanese review

KJ法の成果を単一尺度で裁定するのではなく、元cardへ戻りながら「訴え」「束ね」「表札」「残差」「次の壁打ち」を具体的に記録できる形へ整理しました。actual workflowのreview bundleを使う場合も、artifactの存在と品質判断を混同せず、同じrunのrequest / result / structure / Provenanceへ戻れるようにしました。技術的な実行identityは必要な範囲に留め、レビュー本文では人間が自然に読み書きできる日本語を最優先して全文を再ドラフトしています。
