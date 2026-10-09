# Cognitive Workspace Comparison — Raw Context vs Bounded Cognition

更新日: 2026-10-02  
状態: **Evaluation-only Comparison Harness（§2.1は ADR-0035 Proposed による提案）**  
関連: Issue #383 / #381 / #375 / #371

## 1. 根幹の趣旨

SEI Cognitionの価値仮説は、汎用LLMを使わないことではない。

重要なのは、**何でもそのまま汎用LLMへ渡す前に、認知状態を壊さず、必要な問題と材料へ絞り、安価な認知系で処理できるものを処理し、必要な場合だけ高価な認知へ上げること**である。

この評価では、同じ問題・同じunderlying evidence universeから、次の3条件を作り分ける。

```text
A. Raw Context
   raw / flattened context
      ↓
   general-purpose reasoner

B. Cognitive Workspace
   selected evidence
   + Unknown / Conflict
   + constraints
   + historical boundary
      ↓
   same reasoner class

C. Staged Cognition
   deterministic / SACS / route decision
      ↓
   bounded Cognitive Workspace
      ↓
   local SLM / evidence expansion / stronger reasoner when needed
```

比較したいのは、単にtoken数が減るかではない。

```text
less context
  + lost Unknown / historical boundary
  = failure
```

**意味境界を守ったまま認知負荷を下げられるか**を見る。

## 2. 何を反証したいか

SEI Cognition側に都合のよい比較にしない。

次が成立するなら、Cognitive Workspaceやstaged routingは縮小・再設計すべきである。

- Raw ContextでもUnknown / Conflict / Decision basisが同程度に保持される
- Workspace圧縮によって重要Evidenceが頻繁に落ちる
- staged routeが誤って軽量処理へ閉じる
- routeの追加costがmodel-call削減を上回る
- general-purpose modelがraw contextで一貫して安全かつ十分安価に解ける

逆に、次が観測されれば仮説は強まる。

- Workspaceでcontextを大きく削減してもsemantic integrityが維持される
- routine / symbolic caseでgeneral-purpose model callを避けられる
- novelty / fresh-data caseで推測せずEvidence expansionへ戻せる
- late-arriving evidenceをhistorical Decision basisへ混ぜにくくなる
- small/local reasonerでもbounded problemなら十分なcaseが増える

### 2.1 脱皮台帳への一般化と、Workspaceの再正当化（提案 — ISSUE-000088 / ADR-0035）

上の反証の条件は、Cognitive Workspaceとstaged routingだけに当てはまるものではありません。SEIの各仕組みについて、**なぜ必要なのか（正当化の札）**と**何が観測されたら縮小するか（縮小の条件、tripwire）**を先に書く台帳へ広げることを提案します。札は次の三つです。

- **制度** — 権限、責任、時間、複数の主体に由来する。モデルが強くなっても残るか、強まる。
- **容量** — モデルの弱さを補うために必要。薄くなる。
- **経済・物理** — コスト、電力、通信、privacyに由来する。一部は残る。

台帳の初期内容は`plan/issue/ISSUE-000088-maintain-model-progress-robustness-register.md`にあります。新しい世代の基盤モデルが出たときは、この比較をA / B / Cで再実行し、`historical PASS != current PASS`として記録します。

Cognitive Workspaceについては、正当化を「容量」から「**開示範囲**」へ移すことを提案します。文脈長が伸び、生の履歴を読み直すコストが下がれば、「小さい文脈に絞らないと扱えない」という容量の理由は弱まります。一方、「この主体に、何を見せてよいか」という権限と開示範囲の理由は残ります。したがって、上の反証条件のうち「Raw Contextでも同程度に保持される」が成立しても、開示範囲を制御する必要が残る限り、Workspaceを全面的には縮小しません。容量のための部分だけを縮小します。

この再正当化は評価仮説であり、Stable RequirementやUniversal Contractではありません。

## 3. 比較条件

### A — Raw Context Baseline

source materialをflatなtext sequenceとして渡す。

このbaselineは意図的に弱いsummaryを作らない。

```text
same underlying material
  -> flattened baseline context
```

semantic roleをSEI Cognition側で補強せず、通常のcontext consumptionに近い条件を作る。

### B — Cognitive Workspace

同じmaterialから次を明示する。

- objective
- selected evidence
- Unknown
- Conflict
- constraints
- Decision / historical basis boundary
- later evidence
- expected output role

Workspaceはcanonical stateではなく、一時的なbounded projectionである。

### C — Staged Route

既存`hybridreasoning.RouteReasoning`を利用し、まずrouteを決める。

候補は次のとおりです。

- symbolic
- non-LLM recall
- local SLM
- expand evidence
- external evidence required
- human / stronger review
- abstain

```text
route choice
  != Truth
  != semantic confidence
```

## 4. Model-independent evaluator

actual modelをまだ接続しなくても、出力JSONを次の観点で評価できるようにする。

### Historical integrity

- Decision basisにpost-decision / late-captured evidenceが入っていないか
- later evidenceを「当時知っていた」ように扱っていないか

### Uncertainty preservation

- expected Unknown refが残っているか
- expected Conflict refが残っているか
- `need_more_evidence`を適切に使えるか

### Responsibility boundary

- RecommendationとDecisionを同一視していないか
- generated proposalをcanonical Decisionとして扱っていないか

### Evidence discipline

- material claimにsupporting refがあるか
- refがfixture universeに存在するか
- unsupported claim数はいくつか

### Routing

- expected routeと一致するか
- routine / symbolicを不用意にLLMへ上げていないか
- novelty / current external factをmodel memoryで埋めようとしていないか

## 5. Context reductionは独立指標にする

単一scoreへ潰さない。

記録する候補は次のとおりです。

- raw context characters
- Workspace characters
- selected record count / total record count
- unresolved count preserved
- general-model call required
- local-model call allowed
- route

actual model接続後は別途:

- first-token latency
- total latency
- peak RSS
- prompt tokens
- output tokens
- provider cost

を追加する。

## 6. Fixture class

最初の7ケースは次を含む。

1. DecisionなしのInquiry
2. Decision + unresolved Unknown
3. RecommendationとDecisionが異なる
4. Decision後にlate-arriving evidenceがある
5. current external factが必要
6. high noveltyでEvidence expansionが必要
7. deterministic / symbolicだけで解ける

これにより、単純なsummary benchmarkではなくSEI Cognition固有の境界を試す。

## 7. 出力の権威

比較対象modelから返るものはすべてproposalである。

```text
model output
  != canonical semantic state
  != Recommendation
  != Decision
  != Authority
```

このharnessはhidden chain-of-thoughtを要求・保存しない。

必要なのは、最終的なproposal、supporting refs、remaining Unknown / Conflict、need-more-evidence等の外部評価可能な出力だけである。

## 8. 実装配置

- 設計: `evaluation/cognitive-workspace-comparison/`
- executable mechanics: `evaluation/sparse-associative-cognition/prototype-go/cognitiveeval/`
- routing: existing `prototype-go/hybridreasoning/`

Go package側では:

- fixture -> A/B/C bundle生成
- bounded Workspace生成
- route decision
- context stats
- model-independent output evaluation

を行う。

## 9. Evidenceの強度

この段階で得られるのはExecutable Mechanics Evidenceである。

```text
bundle generation passes
  != local SLM is good enough
  != general LLM calls are reduced in practice
  != user Outcome improved
```

actual model比較はIssue #375と接続し、その後real Personal Inquiry / organization caseへ進む。

## 10. 次段

1. focused fixture test
2. sub-1B / 2–4B / general modelへ同じbundleを投入
3. A/Bでcontext shaping効果を比較
4. B/Cでrouting効果を比較
5. false continuity / unsupported claimを比較
6. real Inquiryで再検証

Stable Requirement / Universal Contractへの昇格は、その後に判断する。
