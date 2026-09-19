# SACS + Lightweight Local SLM — Hybrid Reasoning Design

更新日: 2026-09-12  
状態: **Evaluation-only Hybrid Cognitive Design / Not Product Requirement**  
関連: Issue #371 / `README.md` / `prototype-go/`

## 1. Root Intent

目的はLLM利用率をゼロへ近づけることではない。

SEIが保持する耐久的意味と責任境界を壊さず、**単純な想起・近接・選別は非LLMで極小costに処理し、高度な推論が必要な局面だけ小型local language modelへ狭いWorking Setを渡す**ことで、local / offlineでも実用的なreasoning capabilityを得られるかを評価する。

```text
maximize useful reasoning per memory / latency
while preserving SEI semantic boundaries
```

狙う構造は、

```text
SEI durable meaning
  -> exact / symbolic
  -> sparse associative recall / narrowing
  -> bounded working set
  -> lightweight local reasoner
  -> proposal / hypothesis / explanation
```

であり、small modelにknowledge store・retrieval・semantic authorityのすべてを背負わせない。

## 2. なぜ組み合わせる余地があるか

小型language modelは大型modelよりknowledge capacityとgeneral reasoning robustnessが弱い。

一方、SEIでは推論前に次を構造化できる。

- Inquiry / current question
- Observation / source claim
- Unknown / Conflict
- Recommendation / Decision
- historical basis
- candidate Artifact / Method
- Constraint / premise
- provenance / time boundary

つまりlocal modelへ渡す問題を、raw history全体から「何が重要か探す」問題にしなくてよい。

小型modelが主に行うのは、**選ばれた少数のmeaningful recordsを組み合わせるreasoning**である。

この分業により、parameter countが小さいことによるknowledge capacity不足を、SEIのexternalized memory / retrieval / semantic structureで補える可能性がある。

## 3. Cognitive Cascade

### Tier 0 — Deterministic / Symbolic

- exact ref
- schema / grammar
- historical basis validation
- constraint evaluation
- fixed rule

ここで解けるものはLLMへ送らない。

### Tier 1 — Sparse Associative Cognition

- sparse signature recall
- novelty / abstention
- top-k candidate narrowing
- lexical / static-semantic feature adapter where useful

出力はcandidateでありTruthではない。

### Tier 2 — Optional compositional non-LLM cognition

必要になった場合のみ、HDC/VSAや軽量なstatic semantic representation等でrelation / distributional cueを補う。

### Tier 3 — Lightweight local SLM reasoner

次のようなtaskだけを担当する候補とする。

- compare
- synthesize
- interpret
- contradiction analysis
- bounded hypothesis generation
- plan
- human-facing explanation

local SLMはcanonical memoryではない。

### Tier 4 — Stronger external model / human review

次のような場合だけ上位へ送る。

- high-stakes
- working set外のcurrent external evidenceが必要
- high novelty / insufficient evidence
- local SLMのreasoning capacityを越えるmulti-domain synthesis
- formal assuranceが必要

Tier番号はauthority hierarchyではない。cost / capability routingである。

## 4. Working Set Compression

local modelへfull Inquiry historyを渡さない。

SACS / symbolic layerが候補を絞り、次のpacketを作る。

```text
Local Reasoning Working Set
  Inquiry / task
  top candidate meanings
  unresolved Unknown / Conflict
  hard Constraints
  historical boundaries
  requested output contract
```

first sliceでは最大候補数と各text長をboundedにする。

目的:

- context lengthを小さく保つ
- KV cacheを小さくする
- irrelevant contextによるreasoning degradationを減らす
- modelに検索責任を背負わせない
- evidence refsを明示し、あとから検査しやすくする

## 5. local SLMへ渡すsemantic boundary

Working Setにはmodelへの責任境界をmachine-readableに含める。

最低限:

```text
output_is_proposal_only = true
may_not_rewrite_historical_basis = true
recommendation_is_not_decision = true
must_preserve_unknown_and_conflict = true
must_cite_candidate_keys_for_material_claims = true
canonical_write_requires_separate_validation_or_human_action = true
```

local modelのoutputは、最大でも次のcandidateである。

- Interpretation candidate
- Hypothesis candidate
- Recommendation candidate
- explanation / plan candidate

```text
model output
  != Observation truth
  != user Decision
  != Authority
  != Assurance
```

## 6. いつlocal SLMを呼ばないか

### 6.1 symbolicで解ける

validation、exact lookup、historical basis判定等は呼ばない。

### 6.2 retrievalだけが目的

関連Inquiryを探すだけならSACSで止める。

### 6.3 Evidenceが足りない

high noveltyでworking setが形成できないなら、modelに推測させずabstain / evidence expansionする。

### 6.4 current external factが必要

local model内部知識で補わず、Source PlaneからEvidenceを取得する。

### 6.5 high-stakes

first personal prototypeではautonomous local reasoning routeへ送らない。

## 7. 高度な推論を狙う方法

小型model単体で大型model相当を期待しない。

SEI側で推論問題を変形する。

### 7.1 Retrieval compression

関係する少数recordへ絞る。

### 7.2 Semantic role preservation

plain textへflattenせず、Observation / Unknown / Decision等のroleを残す。

### 7.3 Problem decomposition

一度に「最終結論」を求めず、必要に応じて、

1. premise確認
2. contradiction抽出
3. option比較
4. unresolved列挙
5. provisional recommendation

へ分ける。

### 7.4 Short reasoning budget

小型modelへ長い自由CoTを要求するより、task-specificでboundedなreasoningを優先する。

### 7.5 Deterministic verification

modelが生成した構造のうちdeterministicに検査できる部分は後段validatorへ戻す。

これにより、model sizeではなくsystem compositionで高度化する。

## 8. model sizeの考え方

model familyは固定Requirementにしない。

評価帯として概ね次を想定する。

### ultra-light: ~0.5–1B

用途候補:

- classification
- short explanation
- simple comparison
- rewrite / structured extraction

利点はmemoryが小さくCPU / mobile寄りであること。deep multi-step reasoningは限定的と仮定して評価する。

### balanced local reasoning: ~2–4B

用途候補:

- bounded multi-step comparison
- contradiction analysis
- hypothesis / planning
- code / structured reasoningの一部

SEI hybridで最初に狙う中心帯。

### stronger local: ~7–8B+

小型帯で不足する場合の比較対象。

ただしmodelを大きくする前に、Working Set / decomposition / retrieval qualityを改善する。

## 9. runtime boundary

first integration candidateはlocal OpenAI-compatible endpoint等のprocess boundaryとする。

```text
SEI process
  -> LocalReasoningRequest
  -> localhost model server
  -> structured proposal
  -> validator / human review
```

model runtimeをSEI Coreへ直接埋め込むことを初期Requirementにしない。

候補runtimeとしてGGUF quantizationとCPU / Metal / GPU等を扱える`llama.cpp`型のlocal serverを評価できる。

```text
local runtime choice
  != Universal semantics
```

## 10. Evaluation Matrix

非LLM単独とhybridを別軸で比較する。

| Mode | Recall | Synthesis | Memory | Latency | Hallucination surface |
|---|---|---|---|---|---|
| exact/symbolic | narrow/high precision | none | minimal | minimal | minimal |
| SACS only | approximate | minimal | low | very low | candidate false activation |
| SACS + 0.5–1B | approximate | light | low-medium | low-medium | generated proposal |
| SACS + 2–4B | approximate | medium | medium | medium | generated proposal |
| larger local/external | approximate | stronger | high | high | generated proposal |

測るもの:

- end-to-end task success
- evidence-role integrity
- unsupported claim rate
- Unknown / Conflict preservation
- correct citation of candidate refs
- reasoning latency
- peak RSS / model memory
- prompt / KV working memory
- model-call rate
- abstention quality
- larger model escalation rate

単一scoreへ潰さない。

### 10.1 Synthetic model-call avoidance snapshot

2026-09-19時点の7件の`ReferenceFixtures`について、current routing contractをsource inspectionし、model-call planを集計するevaluation-only helperを `prototype-go/modelprobe/call_avoidance.go` に追加した。

current fixture distribution:

- local SLM route: 4
- current external evidence required: 1
- high-novelty evidence expansion: 1
- deterministic symbolic: 1

raw / workspace comparison baselineは7件ともmodel invocationを計画する一方、staged routeは4件だけをlocal modelへ送る。このsynthetic fixture集合に限れば、raw baseline比で3/7、約42.9%のmodel invocationをrouting段階で回避する計画になる。

ただしこれは実model telemetryではない。aggregation logicのisolated testは5/5 PASSしているが、Issue #511でcurrent repository dependencyを使うactual Go integration runtimeを試行したところ、GitHub Actionsは `runner_id=0` / `steps=[]` のままrunner割当前に終了した。local実行環境はGo 1.23.2で、正本moduleの `go 1.25` requirementによりbuild前に拒否され、automatic toolchain取得もnetwork名前解決不可で開始できなかった。

したがって、current repository integration runtimeのPASS / FAILは引き続き**未観測**である。runner未開始やtoolchain取得不能をGo test failureへ読み替えない。

machine-readable Evidence:

- synthetic / isolated Evidence: `hybrid_model_call_avoidance_evidence_2026-09-19.json`
- repository-runtime blocker Evidence: `hybrid_model_call_avoidance_runtime_blocker_evidence_2026-09-19.json`

```text
synthetic routing call avoidance
  != production LLM call reduction
  != task success
  != semantic correctness
  != lower total system cost
```

## 11. Falsification

次ならhybrid Product Hypothesisを縮小する。

- small local modelがsemantic roleを頻繁に混同する
- SACS Working Setを与えてもunsupported claimが減らない
- 2–4Bでも実用reasoningへ届かず7–8B以上が常時必要
- inference latencyがresumption UXを壊す
- context preparationの方がmodel callより高costになる
- deterministic / non-LLM処理だけで十分なtaskが大半
- external strong modelとの差がProduct Value上許容不能

## 12. first executable step

actual modelを呼ぶ前に、次をdeterministicに実装する。

- task routing
- novelty / evidence adequacy gate
- bounded Working Set construction
- semantic stop lines
- no-canonical-write boundary

これにより次のmodel実験で、model性能とorchestration設計を分離して評価できる。

## 13. references / current implementation candidates

- Microsoft `Phi-4-mini-reasoning`, 3.8B reasoning-specialized model. Model card notes limited factual capacity and suggests retrieval augmentation for weaknesses.
- Qwen `Qwen3.5-0.8B`, current sub-1B local candidate family.
- `llama.cpp`, local GGUF inference and quantization runtime candidate.
- Srivastava et al. (2025), *Towards Reasoning Ability of Small Language Models*.
- Li et al. (2025), *Small Models Struggle to Learn from Strong Reasoners*.
- Yang et al. (2026), *FutureMind: Equipping Small Language Models with Strategic Thinking-Pattern Priors via Adaptive Knowledge Distillation*.

これらはProduct dependencyの決定ではなく、evaluation evidence / implementation referenceである。
