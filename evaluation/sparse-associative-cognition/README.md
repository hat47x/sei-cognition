# Sparse Associative Cognitive Substrate

状態: **Evaluation / Experimental**  
更新日: 2026-09-12

## 1. 根幹の趣旨

この領域で実現したいのは、LLMを常時呼び出さなくても、入力の近接、既知パターンの想起、局所的な注意配分、新奇性の検出を、CPU上で高速・低メモリ・再現可能に行える認知実行基質である。

この基質は、自然言語理解そのもの、Cognitive Methodそのもの、判断、真偽、確信度を所有しない。複数の上位Methodや製品が利用できる**汎用の認知プリミティブ**を提供する。

そのため、実装方式は次の順で考える。

```text
決定論で解けるもの
  ↓
疎な表層・構造特徴
  ↓
疎連想・競合選択・新奇性
  ↓
必要な場合だけstatic semantic representation
  ↓
それでも不足する場合だけ、より重いlocal encoder
  ↓
生成・高度な言語化が本当に必要な場合だけLLM
```

「非LLMで置き換えること」自体を目的にせず、軽い方式で十分な認知機能は軽い方式へ移し、LLMを本当に必要な処理へ限定する。

## 2. 所有と配置を分ける

再利用可能な疎連想・新奇性・近傍想起の基質は、**SEI Cognition方向の共通認知基盤（現在のSOZA repository）で所有する**。

一方、呼び出し側のSUI Sensemakingは、親和図法に固有の次を所有する。

- どのcard / graph / layout / history情報を特徴として渡すか
- 「一緒に読んでみる価値がある」候補をどう解釈するか
- singleton / hold / critique / residualをどう保護するか
- 人間レビューとproposal-onlyの境界
- 親和図法のbenchmarkと受入条件

重要なのは、**ownership != deployment** である。

共通基質をSEI Cognition側で所有しても、実行時に必ずnetwork serviceを呼ぶ必要はない。遅延とmemoryを優先する場合、同一processへlibraryとして組み込む、local helperとして同一hostへ置く、またはSUI側へ同一実装をvendoringせずversioned packageとしてリンクする方式を比較できる。

最初のsliceでは、network hopを要求しない。

## 3. 第1段階の技術構成

最小構成は依存ゼロのGo prototypeとする。

```text
caller-owned features
  │
  ├─ lexical / token / n-gram
  ├─ graph / relation
  ├─ spatial / layout
  ├─ history / interaction
  └─ optional static-semantic dimensions
          │
          ▼
  deterministic feature hashing
          │
          ▼
 sparse random expansion
          │
          ▼
      k-WTA
          │
          ▼
 compact sparse signature
          │
    ┌─────┴─────────┐
    ▼               ▼
association       novelty
retrieval         signal
```

Coreは`Feature{Channel, Key, Weight}`だけを受け取る。これにより、自然言語tokenizerやstatic embedding modelをcore依存へ持ち込まない。

第1実装ではdimension IDを`uint16`で保持する。たとえばactive=64なら、signatureのactive payloadは128 byteで済む。検索indexはsignatureを連続sliceへ置き、Query時には全候補配列を作らずtop-kだけを保持する。

## 4. 補完する非LLM技術

疎ランダム展開だけで深層意味まで担えるとは仮定しない。役割を分ける。

- **exact / symbolic**: schema、grammar、constraint、exact binding等の正しさ
- **lexical sparse**: char n-gram、token、BM25系、feature hashing
- **sparse associative**: 近傍想起、競合選択、small-set bundle、新奇性
- **static semantic**: Model2Vec / StaticEmbedding / fastText等の非生成・attention-free表現を必要に応じてadapterとして追加
- **heavier local encoder**: static semanticで要求水準へ届かない場合だけ比較
- **LLM**: 新規文章生成、高度な意味説明、未構造入力の解釈等に限定

static semantic表現を採用する場合も、coreはmodelを直接知る必要がない。adapterがdense vectorから上位dimension等を`Feature`へ変換するか、独立channelとして候補統合する。

## 5. 意味上の停止線

この基質の出力は候補信号である。

```text
candidate activation != truth
candidate activation != confidence
novelty signal != Unknown
competition state != Conflict
candidate refs != Recommendation
candidate refs != Decision
candidate refs != Authority
candidate refs != Assurance
```

SUI Sensemakingで利用する場合も、近接候補から島・表札・relationを自動確定しない。

## 6. 現在のprototype

`prototype-go/`に、次だけを持つ依存ゼロの実験実装を置く。

- reusable scratchを持つsparse encoder
- fixed-seed feature hashing
- sparse random expansion
- k-WTA
- sorted compact signature
- binary cosine similarity
- small-set bundle
- novelty signal
- contiguous exact-scan top-k index

ANN indexはまだ導入しない。数千〜数万件では、compact signatureのlinear scanが単純で低memoryであり、まず実測してから追加indexの必要性を判断する。

## 7. Evidenceの読み方

prototypeのunit testやsynthetic benchmarkは、アルゴリズム実装が動くことと、局所的なlatency / allocation特性を示すだけである。

これだけでは次を証明しない。

- SUI Sensemakingの親和図法で深層意味近接が十分であること
- Fly-inspired方式がstatic semantic encoderより優れること
- production runtimeとして採用できること
- Product Value / Operational / Adoption / Outcome Evidence

SUI側の事前登録benchmarkはhuman adjudication完了までsemantic resultを生成しない。そのgateを、この共通基質の実装都合で開かない。
