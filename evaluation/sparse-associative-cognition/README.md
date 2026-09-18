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
生成・高度なreasoningが必要な場合だけbounded local SLM
  ↓
high novelty / high stakes / broader synthesisだけstronger model / human review
```

「非LLMで置き換えること」自体を目的にせず、軽い方式で十分な認知機能は軽い方式へ移し、LLMを本当に必要な処理へ限定する。

## 2. SEI CognitionとSUI Sensemakingの役割を分ける

再利用可能な疎連想・新奇性・近傍想起の基質は、**SEI Cognition方向の共通認知基盤（現在のSEI repository）で所有する**。

SEIは認知場と簡易記憶を持ち、現在の目的に応じて注意、想起、仮説、再探索を制御する。

SUI SensemakingはSEIの「呼び出し側」ではない。**人間、生成AI、SEI、外部collaboratorが同じ情報ネットワークへ参加し、それぞれ異なる関心・役割・interfaceを持ちながら、共有可能な認知状態を形成する外在化されたsensemaking環境**として扱う。

SUIは特に次を所有する。

- 長期的・共有可能な情報ネットワーク
- card / relation / layout / history / provenance
- neighborhood / contrast / bridge / residual / temporal / provenance等のQuery
- subgraph / spatial / table / card stack / narrative等へのProjection
- 人間、生成AI、SEI、外部主体ごとのContext Projection
- proposal / review / patch / approvalの協働境界
- singleton / hold / critique / residualの保護
- 親和図法固有のbenchmarkと受入条件

SEIはSUIから必要な情報を都度queryして認知場へ取り込み、SUIはSEIの内部思考状態そのものを永続正本として所有しない。

```text
SEI inquiry / current interest
          │
          ▼
SUI information network
  selection / qualitative analysis /
  actor-aware context projection
          │
          ▼
SEI cognitive field
  recall / local reasoning / hypothesis
          │
          ▼
proposal / question / review request
          │
          ▼
SUI collaboration / consensus space
          │
          ├─ human response
          ├─ generative AI response
          ├─ external collaborator response
          └─ approved shared state
```

ここでいうconsensusは全面一致を意味しない。異論、保留、少数意見、未解決を残したまま、どこまで共有・承認できたかを扱う。

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
- **bounded local SLM**: 少数候補を使ったcompare / synthesize / interpret / contradiction analysis / hypothesis / plan
- **stronger model / human review**: high novelty、high stakes、current external evidence、local SLM capacity超過時のみ

static semantic表現を採用する場合も、coreはmodelを直接知る必要がない。adapterがdense vectorから上位dimension等を`Feature`へ変換するか、独立channelとして候補統合する。

### 4.1 lightweight local SLMとの組み合わせ

local SLMをSACSの代替memoryにはしない。

```text
SEI current inquiry
  -> SUI query / context projection
  -> sparse associative candidate narrowing
  -> bounded Working Set
  -> lightweight local SLM
  -> proposal / hypothesis / explanation
  -> deterministic validation / SUI collaboration / human action
```

Working Setには、Inquiry、少数candidate meaning、Unknown / Conflict、Constraint、historical boundaryを含める。local SLMのoutputはcanonical write authorityを持たない。

特に、Evidenceが少ないほどmodelを呼ぶ構成にはしない。noveltyが高くbounded Working Setを作れない場合は、推測ではなくSUIへのevidence expansion query / abstentionへ戻す。

詳細は`HYBRID_LOCAL_REASONING.md`、実行境界は`prototype-go/hybridreasoning/`を参照する。

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
local SLM output != canonical truth
local SLM output != user Decision
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
- local-SLM routing / bounded Working Set boundary

ANN indexはまだ導入しない。数千〜数万件では、compact signatureのlinear scanが単純で低memoryであり、まず実測してから追加indexの必要性を判断する。

actual local model runtimeもまだcore dependencyへ入れない。model比較はprocess boundaryで行い、SACS substrateとorchestrationを分離して評価する。

## 7. Evidenceの読み方

prototypeのunit testやsynthetic benchmarkは、アルゴリズム実装が動くことと、局所的なlatency / allocation特性を示すだけである。

これだけでは次を証明しない。

- SUI Sensemakingの親和図法で深層意味近接が十分であること
- Fly-inspired方式がstatic semantic encoderより優れること
- lightweight local SLMとのhybridが大型modelに近いreasoning qualityへ届くこと
- SUIの多主体query / consensus形成が実利用で認知増分を生むこと
- production runtimeとして採用できること
- Product Value / Operational / Adoption / Outcome Evidence

SUI側の事前登録benchmarkはhuman adjudication完了までsemantic resultを生成しない。そのgateを、この共通基質の実装都合で開かない。


## 8. Cross-stage human-adjudicated benchmark gate

B1/B2/B3/B4/B6/B6b/B6c/SEI-B7にはlimited synthetic executable evidenceがあるが、これをそのまま実SUI/SEI意味品質へ一般化しない。

human-adjudicated評価へ進む前に、比較variant、split、B3 prior、B4 fingerprint、B7 training / holdout、metrics、停止線を事前登録する。

- machine-readable preregistration: `cross_stage_benchmark_preregistration.json`
- 説明文書: `CROSS_STAGE_BENCHMARK_PREREGISTRATION.md`
- preregistration validator: `validate_cross_stage_preregistration.py`
- freeze kit: `cross-stage-freeze/`
- freeze kit validator: `cross-stage-freeze/freeze_manifests.py`
- explicit evaluation run: `cross-stage-run/`
- result artifact contract: `cross-stage-result/`
- interpretation artifact contract: `cross-stage-interpretation/`

現在は **Evaluation Locked** である。

```text
synthetic executable evidence
  ↓
cross-stage preregistration
  ↓
human adjudication freeze
  ↓
explicit evaluation-run artifact
  ↓
human-adjudicated evaluation
  ↓
immutable result artifact
  ↓
non-decisional interpretation artifact
  ↓
future decision
```

preregistration artifact自身はsemantic benchmark resultを生成しない。

特に次を維持する。

- evaluation labelを使ってB3 salience priorを作らない
- evaluation labelを使ってB4 fingerprintを作らない
- B7 training Outcomeとholdout replayを混ぜない
- B6b/B6c diagnosticをsemantic scoreへ変換しない
- quality / robustness / resource / safetyを単一scoreへ圧縮しない
- cross-stage preregistrationだけではB5 learned sparse projectionのentry gateを開かない
