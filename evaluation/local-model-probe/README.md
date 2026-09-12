# Local Model Probe — Cognitive Workspace vs Raw Context

更新日: 2026-09-12  
状態: **Evaluation-only Probe Harness**  
関連: Issue #375 / #385 / #383

## 1. 根幹の趣旨

SEI Cognitionが狙うのは、単に小さいmodelへ置き換えることではない。

```text
Durable Semantic State
  -> bounded Cognitive Workspace
  -> cognitive route
  -> smallest sufficient reasoner
```

によって、認知境界を壊さずにmodelへ渡す問題を狭くし、必要な場合だけ強いreasonerへ上げられるかを実測する。

このprobeは、そのためのtransportとmeasurement entry pointである。

実際に比較するmodel tierと実験順は[`MODEL_MATRIX.md`](./MODEL_MATRIX.md)で整理する。

## 2. 比較する3 mode

### raw

同一fixtureのflattened raw contextをmodelへ送る。

staged routerが本来modelを呼ばないcaseでも、比較baselineとして明示的に送る。

したがって結果には`boundary_bypassed_for_baseline=true`が付き得る。

### workspace

同じmodelへbounded Cognitive Workspaceを送る。

これによりmodel sizeを変えず、context shapingだけの効果を比較できる。

### staged

SEI Cognitionのroutingを尊重する。

- deterministic -> modelを呼ばない
- current external fact -> modelを呼ばずexternal evidenceへ戻す
- high novelty -> modelを呼ばずevidence expansionへ戻す
- bounded local reasoning -> local modelを呼ぶ

`staged`が実運用候補、`raw` / `workspace`は比較実験条件である。

## 3. output contract

modelへhidden chain-of-thoughtは要求しない。

返すのはexternally inspectableなJSONのみ。

```json
{
  "proposal": "...",
  "supporting_refs": ["obs-1"],
  "decision_basis_refs": [],
  "preserved_unknown_refs": ["unk-1"],
  "preserved_conflict_refs": [],
  "recommendation_ref": "",
  "decision_ref": "",
  "need_more_evidence": false,
  "claims": [
    {
      "text": "material claim",
      "supporting_refs": ["obs-1"]
    }
  ]
}
```

このJSONは`cognitiveeval.EvaluateOutput`へ渡される。

## 4. localhost runtime boundary

probeは特定runtimeをUniversal semanticsへ持ち込まない。

第一probe interfaceはOpenAI-compatible Chat Completionsとする。

デフォルト:

```text
http://127.0.0.1:8080/v1/chat/completions
```

llama.cppの現行`llama-server` / `llama serve`はこのendpointを提供するため、一Realizationとして利用できる。

参考:
- https://github.com/ggml-org/llama.cpp
- https://github.com/ggml-org/llama.cpp/tree/master/tools/server

## 5. dry-run

model未導入でもprobe planを確認できる。

```bash
cd evaluation/sparse-associative-cognition/prototype-go

go run ./cmd/modelprobe \
  --mode staged \
  --fixture all \
  --dry-run
```

見る点:
- route
- should_invoke_model
- baseline boundary bypass
- request chars
- actual prompt material

## 6. llama.cpp例

runtime/model installそのものはこのrepositoryの責任外とする。

例として現行llama.cppでは、GGUF modelをserveしてOpenAI-compatible endpointを立てられる。

```bash
llama serve -hf ggml-org/Qwen3.5-0.8B-GGUF
```

その後:

```bash
go run ./cmd/modelprobe \
  --mode workspace \
  --fixture decision-with-unknown \
  --model local-model
```

raw baseline:

```bash
go run ./cmd/modelprobe \
  --mode raw \
  --fixture decision-with-unknown \
  --model local-model
```

staged:

```bash
go run ./cmd/modelprobe \
  --mode staged \
  --fixture all \
  --model local-model
```

## 7. model帯の比較

Issue #375では少なくとも次を比較する。

### sub-1B

用途仮説:
- extraction
- classification
- simple comparison
- short explanation

### 2–4B

用途仮説:
- bounded multi-step comparison
- contradiction analysis
- hypothesis / short planning

### stronger comparator

7–8B級または外部general-purpose modelを必要時だけ比較する。

重要なのはmodel familyではなく、同じfixture / mode / evaluatorで比較することである。

具体的なfirst candidatesは[`MODEL_MATRIX.md`](./MODEL_MATRIX.md)を参照する。

## 8. 現在取得するmeasurement

- route
- model invocation / skip
- request chars
- response chars
- total latency
- HTTP status
- providerが返すtoken usage（存在する場合）
- Unknown preservation
- Conflict preservation
- Recommendation / Decision separation
- historical basis violation
- unsupported claim
- invalid evidence ref
- need-more-evidence appropriateness

まだ取得しないもの:
- streaming first-token latency
- process peak RSS
- model weight memory
- KV cache memory
- energy

これらはruntime-specific probeとして後続する。

## 9. 実験順

最初から多数modelを回さない。

```text
1. dry-run
2. one sub-1B model
   raw vs workspace vs staged
3. failure caseを確認
4. Working Set / decomposition改善
5. 2–4B model
6. sub-1Bとの差を見る
7. 必要ならstronger comparator
```

小型modelの失敗を見たとき、直ちにmodelを大型化しない。

まず:
- evidence selection
- task decomposition
- prompt/output contract
- missing evidence
- route

を確認する。

## 10. 成功条件

有望な結果は「小型modelが大モデルと同じ文章を書くこと」ではない。

例えば:

```text
Workspace
  -> Unknown / Conflict / historical boundaryを保つ
  -> rawよりunsupported claimが少ない
  -> sub-1Bまたは2–4Bで十分なcaseが増える
  -> stagedで不要なmodel callを避ける
```

であれば価値がある。

逆に、Workspaceがraw contextと同等以下であれば、SEI-specific context shapingを縮小または再設計する。

## 11. 停止線

```text
model output != Truth
model output != Decision
well-formed JSON != correct reasoning
shorter context != better cognition
fewer LLM calls != Product Value
larger model != first remedy
current external fact != model memory
high novelty != permission to guess
```

このprobeはactual model Evidenceを取得する入口であり、それ自体をOutcome Evidenceとはみなさない。
