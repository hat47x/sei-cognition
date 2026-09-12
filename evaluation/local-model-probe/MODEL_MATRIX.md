# Local Model Comparison Matrix

更新日: 2026-09-12  
状態: **Evaluation-only Candidate Matrix**  
関連: Issue #375 / `README.md`

## 1. 根幹の趣旨

目的は「最も強い小型modelを選ぶこと」ではない。

SEI Cognitionでは、Cognitive Workspaceとroutingにより問題を狭くした結果、**どのproblem classまでならどのmodel tierで十分か**を知りたい。

```text
problem
  -> bounded Workspace
  -> smallest sufficient reasoner
  -> stronger reasoner only when needed
```

したがってmodel比較は、model leaderboardではなく**認知routingの境界探索**として行う。

## 2. 第一比較候補

### A. Qwen3.5-0.8B — sub-1B baseline

位置づけ:
- 最小tierの第一候補
- extraction / classification / simple comparison / short explanation
- Workspaceによるproblem compressionの効果を見る

理由:
- 0.8B class
- Apache-2.0
- 2026-09時点のllama.cpp公式READMEがGGUFを直接quick-start例に使用
- `llama serve -hf ggml-org/Qwen3.5-0.8B-GGUF`でOpenAI-compatible serverを立てられる

期待しないこと:
- high-novelty reasoning
- broad factual recall
- long autonomous planning

公式参照:
- https://huggingface.co/Qwen/Qwen3.5-0.8B
- https://github.com/ggml-org/llama.cpp

### B. Gemma 3 4B IT — compact generalist comparator

位置づけ:
- 2–4B tierのgeneral-purpose comparator
- instruction following / summarization / comparison / ordinary reasoning
- reasoning-specialized modelとの対照

理由:
- Google公式4B instruction-tuned model
- official QAT Q4_0 GGUFが存在
- QAT版はmemoryを削減しつつBF16に近いqualityを狙う構成
- multilingual generalistとしてSEI Cognitionの日常・組織問題に近い

注意:
- Gemma TermsでありApache/MITではない
- model license条件とsoftware OSS条件を混同しない

公式参照:
- https://huggingface.co/google/gemma-3-4b-it-qat-q4_0-gguf
- https://huggingface.co/ggml-org/gemma-3-4b-it-GGUF

### C. Phi-4-mini-reasoning 3.8B — reasoning-specialized comparator

位置づけ:
- bounded multi-step reasoningの比較候補
- contradiction analysis / structured comparison / hypothesis candidate

理由:
- 3.8B parameter
- reasoning向けpost-training
- Microsoft model cardでは、同parameter帯の通常modelよりreasoning benchmarkを大幅に改善
- model card自身がsize由来のfactual knowledge制約とsearch/RAG補完の必要性を明示

これはSEI Cognitionの「知識は外部化し、modelはbounded reasoningへ集中させる」という仮説と相性がよい。

注意:
- llama.cppでのPhi系supportは進んでいるが、version/model variantによる互換性差が過去に存在する
- first runでruntime frictionが大きい場合、model自体のquality評価とruntime compatibilityを分離する

公式参照:
- https://huggingface.co/microsoft/Phi-4-mini-reasoning
- https://github.com/ggml-org/llama.cpp

### D. Llama 3.2 3B Instruct — optional mature baseline

位置づけ:
- 3B general instruct baseline
- 新しいmodel family固有の効果を切り分ける補助

理由:
- 3B
- conversational/instruction用途
- local runtime実績が広い

注意:
- Llama licenseでありstrict OSS modelではない
- first three candidatesで十分な場合は実行しない

公式参照:
- https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct

## 3. 最初に比較する順序

```text
Step 1  Qwen3.5-0.8B
        raw / workspace / staged

Step 2  failure analysis
        retrieval / Workspace / output contract / routeを改善

Step 3  Gemma 3 4B IT
        同一fixture・同一mode

Step 4  Phi-4-mini-reasoning 3.8B
        reasoning-specializationが効くcaseだけ比較

Step 5  必要時のみ3B/7–8B comparator
```

modelを大きくする前に、Step 2を必ず挟む。

## 4. 実験条件を固定する

model間で変更してよいのは、model/runtime固有に不可避な部分だけとする。

共通:
- 同じ7 fixture
- `raw` / `workspace` / `staged`
- temperature = 0
- one sample
- max completion tokens = 800を初期値
- hidden CoTを保存しない
- 同じ`cognitiveeval` evaluator
- current external fact / high novelty stop lineは固定

context windowはmodel最大値へ合わせない。

Cognitive Workspaceの価値を見るため、最初は小さな共通budgetに収まるfixtureだけを使う。

## 5. Quantizationの扱い

二つの問いを混ぜない。

### Deployment-realistic track

各modelで公式または代表的な4-bit量子化を使う。

目的:
- 実際のmemory / latency / quality trade-offを見る

例:
- Gemma 3: official QAT Q4_0
- Qwen: llama.cppで利用可能な4-bit GGUF

### Architecture-comparison track

可能なら近いquantization familyへ揃える。

目的:
- model差とquantization差をある程度切り分ける

first passではdeployment-realistic trackを優先する。

## 6. llama.cpp first runtime

first runtimeはllama.cppを候補とする。

理由:
- local CPU/GPU execution
- broad GGUF support
- OpenAI-compatible `/v1/chat/completions`
- 量子化modelを扱いやすい
- Qwen3.5-0.8Bの現行公式quick-startがある

ただし:

```text
probe contract
  != llama.cpp contract
```

vLLM / MLX / ONNX Runtime / ExecuTorch等へ後から差し替えられるよう、localhost API boundaryの外側へ意味論を置かない。

## 7. reasoning traceの扱い

reasoning modelが内部thoughtを生成しても、SEI Cognitionの評価正本にはしない。

取得対象:
- final proposal
- evidence refs
- preserved Unknown / Conflict
- need-more-evidence
- externally inspectable claims

取得不要:
- private chain-of-thought
- full hidden reasoning trace

llama.cpp側にreasoning field分離機能があっても、probe evaluatorはfinal externally inspectable resultだけを評価する。

## 8. 比較表

| Candidate | Tier | 主用途仮説 | Generalist / Reasoning | License注意 | First priority |
|---|---:|---|---|---|---|
| Qwen3.5-0.8B | <1B | extraction / simple compare | compact generalist | Apache-2.0 | 1 |
| Gemma 3 4B IT | 4B | daily/organization general reasoning | generalist | Gemma Terms | 2 |
| Phi-4-mini-reasoning | 3.8B | bounded multi-step reasoning | reasoning-specialized | model card確認 | 3 |
| Llama 3.2 3B Instruct | 3B | mature instruct baseline | generalist | Llama license | optional |

この表は採用順位ではなく実験順である。

## 9. 必ず記録する結果

model × fixture × modeごとに:

- request chars
- token usage（runtimeが返す場合）
- total latency
- response chars
- JSON contract success/failure
- Unknown preservation
- Conflict preservation
- Recommendation / Decision separation
- historical basis violation
- unsupported claim
- invalid evidence ref
- need-more-evidence appropriateness
- staged model call / skip

runtime側で別途:
- model load memory
- peak RSS / VRAM
- idle memory
- tokens/sec

を記録する。

## 10. 結果の読み方

### sub-1B + Workspaceが十分な場合

そのproblem classはTier Aへroute可能。

### rawでは失敗しWorkspaceでは成功する場合

model sizeではなくcontext shapingに価値がある。

### 0.8Bと4Bの両方が同じ失敗をする場合

大型化前に:
- selected evidence
- missing evidence
- problem decomposition
- task class
- output contract

を再検討する。

### reasoning-specializedだけ改善する場合

Method/model capability routingの根拠になる。

### generalist 4Bで十分な場合

reasoning-specialized modelを常駐させる必要はない。

## 11. 反証条件

次の場合、local SLM中心仮説を縮小する。

- Workspaceを使ってもsub-1B / 4Bがsemantic boundaryを頻繁に壊す
- rawとWorkspaceの差がほぼない
- JSON/output discipline維持のoverheadが大きすぎる
- general-purpose LLM escalation率がほぼ100%
- memory / latency差がProduct Valueへつながらない

逆に、小型modelの成功率だけを見て採用判断しない。

## 12. 次の実測単位

最初のactual runはQwen3.5-0.8Bのみで十分である。

```text
7 fixtures
× 3 modes
= 21 planned cases
```

ただし`staged`ではmodel非呼び出しcaseがあるため、actual inference回数は21より少なくなる。

この結果を見てから4B tierへ進む。
