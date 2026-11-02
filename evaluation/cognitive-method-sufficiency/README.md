# 問い相対の観測十分性：合成Probe分割の最小実験

**2026-11-02 / 研究用Reference・実Productへの適用未受理。**

このファイル群は、[SEI #767](https://github.com/hat47x/sei-cognition/issues/767) P6「次の調査で仮説を識別できるか」を、独立した単純な合成例で確かめるためのものです。[TEI #2514](https://github.com/hat47x/tei-platform/issues/2514)のOracle適用、[TEI #2516](https://github.com/hat47x/tei-platform/issues/2516)のCross-Consumer Claim比較、[TEI #2595](https://github.com/hat47x/tei-platform/issues/2595)の実Source束縛を置き換えません。

## 最小の理論上の修正

二つの仮説 `H1,H2` に対して、Probe `p` が異なる答えを返すことは**その二世界の区別**には役立つ。しかし、そのProbeだけで、未知の対象世界全体に関するClaim `Q` が定まるとは限りません。

固定した合成世界集合 `W` の範囲に限り、観測 `O` が `Q` を識別する十分条件は次です。

```text
for every A,B in W:
  O(A) = O(B)  =>  Q(A) = Q(B)
```

- **pair separation**：特定の二世界を分ける性質。
- **claim sufficiency within W**：観測が同じ世界の組について、Claimの値がすべて一致する性質。
- **real-world qualification**：世界集合・業務対象・Snapshot・Source・Observation・権限・独立Expectedの正当性について、Productごとに追加証拠が必要な実資格。

この三つは互いに自動昇格しません。負例が見つかることは当該候補を反証しますが、列挙した世界で合格したことだけでは未知の世界すべてを保証しません。

## 公開合成世界と問い

全世界で最初のProvider readは同じ`R={A:2,B:1}`です。対象Claim `Q` は「**実際の対象明細すべてが正値か**」。以下のWは説明用であり、正式なBusiness Meaningの採用ではありません。

| 世界 | 実際の明細L | Q |
| --- | --- | --- |
| W1 | A=2, B=1 | true |
| W2 | A=2, B=1, C=0 | false |
| W3 | A=2, B=1, D=3 | true |
| W4 | A=2, B=1, E=0 | false |
| W5 | A=2, B=1, D=0 | false |

W1〜W4が最初の公開Corpus、W5が**公開追加反例**です。W5は非公開holdoutや独立人間評価を装いません。

Probe候補は`count`（内部全件数）、`has_C`、`has_E`、`has_nonpositive`（内部全件の非正値Witness存在）です。これは**合成worldへ直接アクセスできる試験関数**であり、実Provider Query、許可されたTool、API、権限、情報開示を実装したものではありません。

## 期待される判別

1. 現在の`R`だけでは、W1〜W4のQが異なっても同じ観測になります。
2. `count`はW1とW2を区別する一方、W2とW3（どちらも3件、Qは異なる）を区別できません。**一組を区別できても、Corpus全体への十分性ではありません。**
3. `count + has_C`でも、W3とW4（3件、Cなし、Qは異なる）が残ります。
4. `count + has_C + has_E`はW1〜W4ではQを識別できます。ただしW5を追加するとW3とW5が同じ観測になり、Qが異なります。**固定Corpusに対する成功と一般化を区別**できます。
5. `has_nonpositive`なら列挙したW1〜W5上ではQを識別できます。ただし、これを**権限あるProduct内部が実際に検査し、結果公開を許可した**事実はこの試験から得られません。外部Harnessへ非公開差を説明してよいわけでもありません。

## 実行・評価

```bash
python -m unittest -v probe_partition_reference.py
```

**局所観測（2026-11-02）**：このファイルとGitHub上のblobが一致することを確認したソースに対し、ローカルPython 3.13.5で**6件PASS**。これはこの公開合成集合に対する純粋関数試験です。GitHub Actions、SEI CLI/MCP、TEI Provider/DB、Harness/Skill実読み込み、OS隔離、独立Oracle/人の受理は検証していません。

## 次の成熟判定

- SEIは`Q/根拠の有効な世界集合（仮説・反例）/利用した観測/残余/次の識別候補`を**既存Method Applicationや評価票へのReference**として扱う。別のWorld Registry・正式Probe API・状態Engineを先行設置しません。
- 実Productの取得全件性・Source/Claim比較可能性はTEIの既存Ownerへ戻します。識別的なProbe候補の選択と、効果をどう検証するかをSEIが扱います。
- Consumerへの公開には、内部検証の実施許可だけでなく**結果開示の資格**が別に必要です。公開できない場合、外部AIの推測で秘密の有無を埋めません。
- Probe選択の有効性を学習する場合は[SEI #450](https://github.com/hat47x/sei-cognition/issues/450)の静的Baseline/候補とActiveの分離、独立holdoutを再利用。探索を途中で停止させる仕組みをCSWコアへ追加しません。
- Harness向け手順は[TAI Draft #270](https://github.com/hat47x/tai-pleroma/pull/270)で候補となっている`yi-sei-inquiry`の領域です。Skillロード成功・Agent完了はMethodの実資格ではありません。

**Scope**：実装は純粋なテスト関数のみ。新しいRuntime、Product CLI、Tool、Conformance Gate、Owner Meaning Contract、Agent Hostは追加しません。
