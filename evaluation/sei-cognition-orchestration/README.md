# SEI Cognition — Continuous Cognitive Orchestration

更新日: 2026-09-12  
状態: **Evaluation-only Product / Architecture Hypothesis**  
関連: Issue #376 / Issue #371 / Issue #375

## 1. 根幹の趣旨

SEI Cognitionで実現したいのは、汎用LLMを一つの中心知能として常時呼び出すことではない。

個人・組織の日常的な小さな出来事から、例外系、未知事象、長期的な設計・調査までを対象に、**その時点で必要な認知処理を、必要な場所・計算資源・方式へ段階的に配る認知基盤**を目指す。

```text
always-on cognition
  != always-on LLM
```

常時動かす対象は、できるだけ軽量な観測・前処理・変化検出・候補想起・ルーティングである。

重い生成推論や汎用LLMは、軽い処理では不足する場合にだけ起動する。

## 2. なぜ必要か

SEI Cognitionが扱う問題は一種類ではない。

- 個人の日常行動や学習
- 個人プロジェクトや長期Inquiry
- 家庭内の環境変化や機器イベント
- 組織の定常業務
- システム運用の例外
- 文書・ログ・コード・会話の変化
- 未知の事故・障害・問い合わせ
- 複数部門をまたぐ判断
- 新しい設計や調査

これらすべてを一つの汎用LLMへ直接送ると、次の問題が生じる。

- trivialな処理まで高costになる
- latencyが不必要に増える
- privacy-sensitive raw dataを広く移動させやすい
- offline / degraded networkで機能しにくい
- battery / thermal / memoryへの負担が大きい
- deterministicに解ける問題まで生成モデルへ委ねる
- 問題に適した専用認知手法を使いにくい

したがって、認知処理を能力別に分解し、安価で局所的な処理から始める。

## 3. 基本ループ

```text
Sense / Observe
  ↓
Normalize / Filter / Feature Extraction
  ↓
Deterministic / Symbolic Processing
  ↓
Sparse Associative Recall / Novelty / Event Detection
  ↓
Bounded Context Assembly
  ↓
Cognitive Router
  ├─ deterministic method
  ├─ specialized cognitive method
  ├─ static semantic / local encoder
  ├─ local SLM
  ├─ organization cognitive fabric
  ├─ general-purpose LLM
  └─ fresh external retrieval / tool
  ↓
Validation / Human Authority / Action Boundary
```

この順序は固定workflowではなく、costと能力を考えるための基本形である。

## 4. 問題の種類でrouteを変える

### Routine

既知schema、既知pattern、定常的な入力。

原則:

```text
exact / symbolic
  -> SACS / lightweight classifier
  -> done
```

LLMを使わないことを第一候補にする。

### Mild exception

既知patternから少し外れるが、類似ケースや既知Methodがある。

```text
SACS / semantic retrieval
  -> relevant prior cases / Methods
  -> local SLM or specialized method
  -> validator
```

### Novel exception

noveltyが高く、既存caseでは十分説明できない。

```text
abstain
  -> collect more evidence
  -> broaden retrieval / external search
  -> general-purpose LLM or specialist method
```

noveltyが高いことを理由に、軽量modelへ推測させない。

### High-stakes

医療、法務、重大な金融、組織権限、production変更等。

```text
cognitive support
  -> evidence / alternatives / uncertainty
  -> explicit authority / human review
```

高性能modelを使っても、AuthorityやDecisionを自動生成しない。

## 5. 認知資源の階層

### Tier 0 — Sensor / MCU

目的:
- wake trigger
- threshold / anomaly
- simple feature extraction
- low-rate state summary

生成推論は原則行わない。

### Tier 1 — Wearable / Home Device

目的:
- sensor fusion
- privacy filtering
- lightweight event classification
- local pattern / routine detection
- simple recall

raw streamを上位へ送り続けるのではなく、必要なeventやfeatureへ圧縮する。

### Tier 2 — Phone / PC / Home Hub

目的:
- SACS
- local semantic index
- Personal Inquiry context
- local SLM
- richer Working Set construction

個人向けの主要local cognition node候補となる。

### Tier 3 — Local Server / Organization Edge

目的:
- larger local models
- organization context
- shared indexes
- stable long-running cognitive services
- source integration

### Tier 4 — Organization Cognitive Fabric

社内の遊休CPU / GPU / workstation / serverを、policyの範囲内でopportunisticに利用する。

用途:
- hypothesis fan-out
- alternative / counterfactual exploration
- document / repository pre-analysis
- batch re-ranking
- multi-model cross-check
- overnight reasoning
- index / representation rebuild

同期必須処理の前提にはしない。

### Tier 5 — Cloud / General-purpose LLM

目的:
- broad cross-domain reasoning
- difficult natural-language interpretation
- large-context synthesis
- fresh external knowledgeと組み合わせた推論
- local capabilityを超えるproblem solving

汎用LLMは重要なresourceであり、排除対象ではない。

## 6. 認知の常時実行と重い推論を分ける

常時実行候補:

- signal / event detection
- state change detection
- feature extraction
- local privacy filtering
- exact rule evaluation
- SACS candidate recall
- novelty estimation
- known-case matching
- lightweight route selection

必要時だけ起動する候補:

- local SLM
- large local model
- distributed reasoning
- general-purpose LLM
- fresh Web / external tool access

```text
continuous awareness
  != continuous generation
```

## 7. SACSとの関係

SACSはSEI Cognition全体ではなく、軽量な認知primitiveの一つである。

向く役割:
- candidate recall
- related-case selection
- novelty signal
- lightweight competition
- fast local association

向かない役割:
- Truth
- confidence
- Recommendation
- Decision
- high-level language synthesis

SACSはrouterの前段やspecialized methodの候補生成として利用する。

## 8. Local SLMとの関係

local SLMは、SACSで絞ったbounded Working Setについて、次のような処理を担える。

- compare
- explain
- summarize bounded evidence
- identify contradiction candidates
- propose hypotheses
- generate alternative plans

local SLMへraw organizational universeをそのまま渡さない。

```text
local SLM
  = bounded reasoner
  != memory authority
  != semantic authority
```

## 9. General-purpose LLMとの関係

汎用LLMは、問題領域の多様性を考えると不可欠な可能性が高い。

ただし利用前に、SEI Cognition側で次をできるだけ行う。

- relevant source selection
- known facts / Unknown / Conflict separation
- historical boundary preservation
- fresh-data need detection
- method / capability selection
- privacy filtering
- problem decomposition
- Working Set construction

これにより、汎用LLMは「全履歴を理解して何とかする」よりも、狭く明示された高価値問題へ集中できる。

## 10. Personal Inquiry Continuityとの関係

Personal Inquiry ContinuityはSEI Cognitionの一利用形態である。

Meaning Planeで保持されたObservation / Unknown / Conflict / Recommendation / Decision等を、SACSやlocal SLMやgeneral LLMのWorking Setへ供給できる。

重要なのは、どの認知手段を使ってもdurable historical meaningを勝手に書き換えないことである。

## 11. 命名移行

planned product nameは `SEI Cognition` とする。

ただしcurrent repositoryにはSOZA名称のcanonical Requirement / Architecture / Contract / file pathが多数存在する。

このevaluationでは概念名だけ先行してSEI Cognitionを利用し、repository-wide renameは行わない。

renameは別Issue / ADRで、少なくとも次を一緒に扱う。

- Product Value
- Requirements
- ADR
- Architecture filenames
- Traceability
- package / module / repository naming
- historical references

## 12. 非目標

- 汎用LLMを排除すること
- すべての認知をSACSで行うこと
- wearableへ常時生成modelを載せること
- device topologyをUniversal Semantic Contractへすること
- scheduler implementationをProduct semanticsへすること
- cognitive outputを自動Decisionへすること

## 13. 次に検証すること

1. routine / exception / novelでroutingが正しく分かれるか
2. local SLMで十分なproblem割合はどの程度か
3. general-purpose LLMへ送る前にcontextをどこまで削減できるか
4. wearable / home nodeで常時動かせる処理のpower / memory上限
5. organization idle computeを使うjobのpreemption / privacy / benefit
6. distributed cognitionがsingle strong modelより有利なproblem class
7. cognitive routing自体の失敗をどう検出するか
