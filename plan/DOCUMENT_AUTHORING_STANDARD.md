# SOZA 開発文書作成標準

更新日: 2026-08-31  
状態: **Accepted Documentation Standard**

## 1. 基本方針

SOZAの開発文書では、内容と構造を整えた後に、**自然な日本語となることを最重要視して全文をドラフトし直す工程**を必ず設けます。

この工程は、意味を平易化して削るためのものではありません。技術的な意味、条件、例外、留保、Evidenceの強さを保ったまま、人間が無理なく読み進められる日本語へ整えるためのものです。

## 2. 必須工程

新規作成・更新のいずれでも、原則として次の工程を通します。

### 2.1 目的と境界を定める

文書が何を定義・判断・報告するのかを明確にします。同時に、その文書では決めないことも必要に応じて示します。

### 2.2 事実・前提・Evidenceを確認する

未確認事項を確定事項として書きません。historical candidate、actual repositoryのExecutable Evidence、Release、Operational、Adoption / Outcomeを区別します。

### 2.3 構造を作る

読み手が背景、論点、選択肢、判断、影響、未決事項を追える順序へ整理します。

### 2.4 技術的一貫性を確認する

Product Value、Requirements、ADR、Architecture、Contract、Representation Profile、Runtime、Evidenceの間に矛盾がないか確認します。

### 2.5 自然な日本語へ全文をドラフトし直す

意味や仕様を変えず、日本語として自然な語順、接続、段落構成へ整えます。

特に次を確認します。

- 英単語や識別子を名詞として過剰に連結していないか。
- 「〜側」「〜系」「〜化」だけで関係を曖昧にしていないか。
- `actual`、`candidate`、`planning`等の作業メモ語を、説明なしに日本語文へ混在させていないか。
- 主語・目的語・述語の対応が読み取りやすいか。
- 箇条書きの断片だけで重要な判断理由を済ませていないか。
- 同じ概念を不用意に別名で呼んでいないか。
- 技術用語を無理に和訳して意味を曖昧にしていないか。

### 2.6 意味を再監査する

日本語を整えた結果、条件や留保が弱まったり、未決事項が確定事項へ変わったり、Evidenceが実際より高い状態へ見えたりしていないか確認します。

## 3. Evidence表現

達成状態を書く場合は、必要に応じて次の5段階を区別します。

```text
Design Evidence
  != Executable Evidence
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

たとえば`CI success`だけから`release ready`や`利用者価値を実証済み`とは書きません。

未検証はFAILと同じではありませんが、PASSでもありません。`Not Yet Verified`等、上位文書で定めた状態語彙を文脈に応じて用います。

## 4. 技術用語

`Decision`、`Capability`、`Provider`、`Exact Binding`等、SOZAで識別子として意味を持つ語は無理に日本語へ置換しません。

一方、本文では必要に応じて自然な説明を添えます。

```text
悪い例:
Capability Choice production implementation start condition

改善例:
Capability Choiceのproduction実装を開始する条件
```

境界を端的に表す式は使用できます。

```text
Recommendation != Decision != Authority != Execution
```

ただし、重要な式には本文でも自然な日本語の説明を添えます。

## 5. current文書と原文保存資料

current開発文書は本標準の対象です。

一方、次のように原文自体がEvidenceとなる資料は、自然な日本語へ直すために本文を改変しません。

- historical implementation reportの参照コピー
- legacy Contractの比較用原文
- 外部由来の原資料
- 固定入力・negative caseとして意味を持つfixture

これらは`plan/document_review_registry.yaml`で`excluded-historical`として除外理由を残します。

source code、JSON Schema、workflow定義等は本台帳が対象とする「自然言語の開発文書本文」には含めません。ただし、説明READMEやcode commentの品質を無視してよいという意味ではありません。

## 6. 監査状態

既存文書の監査状態は`plan/document_review_registry.yaml`で管理します。

- `revised` — 内容・構造を確認した後、自然な日本語へ全文を再ドラフトし、最終意味監査まで完了した。
- `reviewed-no-change` — 全文を確認し、意味・可読性とも現状のままでよいと判断した。
- `excluded-historical` — 原文保存や固定Evidenceとしての性質から改稿対象外とした。
- `pending` — current文書だが全件移行監査がまだ完了していない。

`pending`は移行中にのみ使用し、ISSUE-000015を完了するときには残しません。

## 7. 新規文書の扱い

ISSUE-000015の移行監査中であっても、新しく作成する文書をいったん`pending`へ積む必要はありません。

作成した作業単位の中で本標準を最後まで通した文書は、直接`revised`または`reviewed-no-change`として台帳へ登録できます。

これにより「新規文書が増えるため監査が永遠に終わらない」状態を避けます。

## 8. Natural Japanese review

5段階Evidence、actual document review registry、current Contract / Runtime / Provider Adapterへ戻って本標準の適用範囲を再確認した。その後、文書品質の要求強度と原文保存例外を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。
