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

<!-- local-cell-fractured-read-20261102 -->
## 追加評価：Corpus全体の十分性と「一つの観測への限定結論」を分離する

公開合成Referenceに`test_probe_claim_qualifiers.py`を追加しました。既存の`corpus_sufficient(W, probes)`は**Corpusにある全ての観測同値類についてQが一意か**を問います。一方、`fixture_cell_verdict(W, probes, observed)`は**一つの観測と整合するW内の世界だけ**を調べます。

- `count+has_C`はW1〜W4全体については不十分ですが、観測W1に対応する同値類では`true-in-fixture`、W2では`false-in-fixture`、W3/W4では`unknown-in-fixture`です。**全体の評価が不十分でも、個々のObservationに限定すれば成立する結論があり得る**という可能性を示します。
- W1〜W4において`count+has_C+has_E`でW3が`true-in-fixture`だったとしても、公開追加反例W5が入れば同じObservationが`unknown-in-fixture`になります。**Fixture内の局所判定は実世界の業務結論ではありません**。
- Corpusに適合する世界が0件の未観測Observationを、`false`や`not exists`へ変換せず`unmodeled-observation`とします。
- 別のSourceから得た一件の反例は、業務集合への対象帰属・時点が証明されて初めて元の全称Claimへの反証になります。別Claim間の一方向の証人/上下界・開示は[TEI #2516 W9](https://github.com/hat47x/tei-platform/issues/2516)、数学的なOracleは[TEI #2514](https://github.com/hat47x/tei-platform/issues/2514)がOwnerです。本テストは汎用含意Engineを実装しません。

## 追加評価：複数Readが「一つの世界」を指しているか

**反例**：時刻t0にA=1,B=0、t1にA=0,B=1とします。どちらの実Snapshotでも`∀(A,B)>0`はfalseです。しかしA@t0とB@t1を合わせれば両方1となり、誤ったtrueを作れます。

合成`Read(field,value,epoch,source_revision)`の`joint_read_candidate`は、既知の対象フィールド／重複／epoch／Source revisionラベルを単純照合し、**明らかな混合ならUnknownへ戻す**ための事前チェックです。`same-labels-in-fixture`は実Source/Scope一致、Grant、Snapshot真正性、Provider完全性の証明ではありません。異時点でも成立する**証明済みの橋渡し**があれば各Product Ownerが判断し、本合成Referenceがすべて拒否する正式ルールにはしません。

この検証は[TEI #2516 W10](https://github.com/hat47x/tei-platform/issues/2516)の異なるReadの共同資格、および[TEI #2605](https://github.com/hat47x/tei-platform/issues/2605)の実CLI/Skill read-bindingに接続します。「Skill説明が静的に一致」「実CLIを呼んだ」「同じClaimを支持する整合した実Readの組」「現在も結果を公開してよい」を別のEvidenceとして扱います。

`disclosure_limited_summary`は**信頼済みの結果開示可否を引数として与えるだけ**の無害なフィクスチャです。Policy/RLS/OS強制、非公開Action名/Probe名、Timing/Trace、反復クエリ、実Harnessの外部送信を安全にした実装・実験ではありません。判定そのものが秘密となる場合のProduct別開示は[TAI #232](https://github.com/hat47x/tai-pleroma/issues/232)とTEI #1178/#2515のOwnerに戻します。

### 同じ版に対する局所コマンド

```bash
cd evaluation/cognitive-method-sufficiency
python -m unittest -v probe_partition_reference test_probe_claim_qualifiers
```

**2026-11-02：上記二Moduleで13/13 PASS（元6、新7）**。ローカルで実行した二つのPythonファイルが、Draft PR branch上のGit blob SHA `7cfc1892362b48f03cd7a29f93bfdf524584debc`／`851c3e228895c28c6af68608be6ca92bb38892d7`と一致することを確認しました。これは公開合成Fixtureの評価であり、GitHub CI・SEI製品本体・TEI Tool実Read/DB・複数Harness・OS隔離・Owner受理の検証ではありません。公開例を未使用の独立holdoutとして扱わず、候補Methodの有効性は[SEI #450](https://github.com/hat47x/sei-cognition/issues/450)の別評価で比較します。

<!-- planning-visibility-20261102 -->
## 追加研究：外部へ返す答えだけでなく、調査の選び方も観測され得る

[SEI #767](https://github.com/hat47x/sei-cognition/issues/767) P6の「次のProbeを選ぶ」工程と、[TAI #232](https://github.com/hat47x/tai-pleroma/issues/232)のConsumer別機密境界、[TEI #2507のSA-21/22](https://github.com/hat47x/tei-platform/issues/2507)（Action名自体が非公開となる例）、[TAI Draft #270のSK-01 §M](https://github.com/hat47x/tai-pleroma/pull/270)を接続する。

**新しい反例**：内部世界S0とS1では非公開Actionの有無が異なるが、外部に許可されたViewと返答は同じとする。最終回答を共に`not-confirmable-from-released-information`へ揃えても、Plannerが内部のAction有無に応じて`private.reconcile`を候補一覧に追加すれば、**Tool候補名・実Call選択・ログなどの観測可能な経路から存在情報が漏れる**。これはTEI #2507の公開Action Candidate評価と相互補完の**認知MethodのProbe選択側**の反例であり、TEIに代わる開示エンジンをSEIに作るものではない。

`test_probe_planning_visibility.py`は、公開可能なPurpose/公開View/公開Tool一覧だけで次の公開Probe候補を決める単純な合成Plannerと、秘密状態を参照してしまう反例Plannerを比較する。内部Productは必要に応じて内部のQを検査できるが、**結果を外部へ公開する資格は独立の信頼済み入力**として与えられるという試験上の仮定を明示する。

試験の着目点：
- 非公開Actionの有無だけが違う二世界でも、結果開示が禁止なら**公開計画・公開応答の合成タプル**は同じになる。
- 最終文章が同じでも、危険なAction Discovery経路だけが世界差を表す負例を検出できる。
- 公開許可が**明示的にある**場合は、内部Qの異なる結果を区別した公開返答が成立し得る。これは機密保持違反の判定ではない。
- 対応する公開Toolが無い場合は`unsupported`とし、非公開Actionを暗黙の代替Toolへ昇格しない。
- 公開された**別の質問**なら、公開Probeを別に選んでもよい。同一View・同一Question・同一開示条件の比較と混同しない。
- 公開可視の`tools/list`、Tool名・順序、引数、回数、エラー、Trace、Network/Log/Timingなどの**実送出面**はProduct/Host/TAIが別に調べる。テストはPython内の小さい`tuple`しか比較していない。

```bash
cd evaluation/cognitive-method-sufficiency
python -m unittest -v test_probe_planning_visibility
```

**局所実測（2026-11-02）**：Python 3.13.5で**7/7 PASS**。GitHub上の`test_probe_planning_visibility.py`のGit blob SHA `19d231ed35ed83ef1b8ac566905483e450e225a8`と、ローカル実行したファイルのGit blobが一致。元2 Moduleの**13/13 PASSは前段の独立した実行結果**であり、新ファイルを含む3 Module一括のCI/実実行はこの追補時点で**NOT RUN**。公開合成例が増えてもsealed holdoutや実OS/Policyの非干渉証明とは扱わない。

**工程上の意味**：Cognitive Methodは、識別力の高い質問を生成するだけでなく、*その質問を外部Consumerへ提示してよいか／公開されたToolで実行できるか／実際にProduct内の検査へ委譲する必要があるか*を区別する。実ProductのAction適用性はTEI #2507、開示資格・実行強制はTAI #232/TEI #1178/#2515、外部Skillの導入・実使用はTAI Draft #270、Method EvaluationはSEI #767に維持する。通常の組織Dataへ一律の秘密分離要件を新設しない。

<!-- negative-evidence-dynamic-dependency-20261103 -->
## P6拡張：空の結果から「存在しない」を導かないための動的依存条件

2026-11-03時点、TEI側の[Construction Context #2516](https://github.com/hat47x/tei-platform/issues/2516) W0c・[統合済みPR #2626](https://github.com/hat47x/tei-platform/pull/2626)では、**公開Referenceを使った実Go CLI read-only観測**と、**合成の選択的再資格化**を別々に実証した。PR #2626は特定HEADのFocused CIで合成55件PASS、read-only実Go CLI観測成功を記録している。一方、実Provider SQL/閉じた対象母集団/動的依存の網羅/Host Grant/SHO文書・外部Agent/Owner意味受理には到達していない。SEI側の「空の応答をどう認知上評価するか」は、この成果を過大に利用せず次の実証課題として扱う。

公開合成`test_negative_evidence_closure.py`を追加した。`NOT EXISTS`など**否定的なClaim**は、単に`observed_ids=[]`だっただけでは成立しない。必要なのは、**問いQに対する対象集合・取得完了・現行述語・関係出現・Provider route・Snapshot epoch・Source/Read束縛が確認できているか**という用途相対の依存です。

- **NE-01／空応答と対象全件性**：同じ`[]`でも、部分Rで未取得の該当行を含む世界と完全な世界は区別できない。合成fixtureの`complete=False`なら`unknown-incomplete-scan`。
- **NE-02／非出力述語と関係依存**：返却行が変わらなくても`query-predicate p1→p2`、`relation-occurrences r1→r2`で否定Claimは再確認が必要。非出力PredicateがIRに保持されても、実SQLGlot Worker/実Queryの全依存被覆が保証されたわけではない（[TEI #2634](https://github.com/hat47x/tei-platform/issues/2634)）。
- **NE-03／依存の追加と未知Edge**：新規`hidden-rule`がRequiredに追加されたら、旧Resultは同じでも`unknown`。Required Dependency setの正しさ自体はこのテスト外の独立Product Evidenceが必要。原因そのものが非公開なら外部へ詳細を出さない。
- **NE-04／取得経路と現在性**：Provider route・cohort・epochの変更、実Read未観測、Source対象未束縛で`unknown`。同じDigestや過去の`full`表記を現在の資格に昇格しない（[TAI #271](https://github.com/hat47x/tai-pleroma/issues/271)）。
- **NE-05／片側Witness**：部分取得でも、対象所属と実Readの確認された１件のWitnessがあれば`NOT EXISTS`の反証にはなり得る。ただしWitnessが実対象へ属する証拠を欠くなら`unknown`。旧Predicate/Relation版のWitnessを現在の不存在反証として流用しない条件も合成テストで固定した。数学的なQuery/Scope/OracleはTEI #2586/#2514のOwner。
- **NE-06／同名Tool・申告値の限界**：`actual_read`、`complete`、Dependency revisionsは試験用の**信頼済み仮定入力**であり、実Toolのread/Provider snapshotを見て導出したものではない。`conditionally-absent-in-fixture`は業務不存在・外部開示の認可・Host/OS保証ではない。

```bash
cd evaluation/cognitive-method-sufficiency
python -m unittest -v test_negative_evidence_closure
# 全5moduleをローカルで一括実行する（GitHub Actionsは当面停止中のため、workflowは置かない）
python -m unittest discover -s . -p "*.py" -v
```

**実行証拠**：新テストはローカルPythonで**10/10 PASS**し、実行ファイルのGit blob `50e19dcd1b6b66c9c7338668865a7cc93ea0b4f4`とGitHub保存版が一致。前3 Moduleの6＋7＋7件は各々別の実行記録があり、**全4 Module 30/30の一括実行はこの追補時点ではNOT RUN**。

**一括実行（2026-11-06、統合前のローカル検証）**：origin/main（9e74fdf）を取り込んだ状態で、Python 3.12.10の`python -m unittest discover -s . -p "*.py" -v`が、discovery境界を含む全5 Moduleで**34件PASS**した。このリポジトリはGitHub Actionsを当面停止しているため（[開発ワークフロー](../../plan/DEVELOPMENT_WORKFLOW.md)の§8）、当初候補ブランチにあったFocused CI workflowは統合対象から外した。これも純粋合成Fixtureのローカル観測であり、実CI・SEI製品本体・TEI実Provider・Harness・Owner受理の検証ではない。

**次の実連結（Owner維持）**：SEIはProbe質問の選択と`Q/観測/不足依存/残余`の説明を行う。TEI #2586/#2387/#2634/#2637は実Query・Provider/Grantの必要依存と実時点を検証し、TAI #271が現在のActivity利用・引継ぎ資格を選択的に再確認する。SHO/外部Harnessへ渡すのはProductが許可した目的相対のProjectionに限る。空の結果を一律FAILへ倒すのではなく、**適用対象内の肯定・否定・限定的不明を区別**し、説明のために新Universal Proof Engine、共通Claim Store、Host、CSW探索中のGateを追加しない。
