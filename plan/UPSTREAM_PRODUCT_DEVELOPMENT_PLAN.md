# SEI 上流プロダクト開発計画

更新日: 2026-09-11  
状態: **Current Upstream Planning Baseline — resume-first Product Slice / TEI version exchangeを並行優先**

## 1. この文書の役割

この文書は、SEIのProduct Valueから、Open Question、Requirement、ADR、Architecture、Implementation、Evidenceへ降りる順序と、**現在どの未知を優先して減らすか**を定めます。

ここは実証履歴の詳細台帳ではありません。run ID、artifact digest、revisionごとの詳細な停止点は各Issue / Evidence文書を正とし、本書では現在のProduct判断に必要な粒度へ要約します。

目的は、実装を増やすことではなく、次の循環を保つことです。

```text
Product Value
  ↓
Product hypothesis / Open Question
  ↓
Research / Design / Experiment / Human Review
  ↓
Evidence
  ↓
Candidate Requirement
  ↓
Requirement audit
  ↓
Stable Requirement / existing integration / No Change
  ↓
ADR / Architecture / Contract
  ↓
Implementation / Test / Probe
  ↓
必要なら上位へ戻る
```

実装しやすさ、current Provider、UI framework、AI model、CI環境等を上位概念の根拠として逆輸入しません。一方、actual実装・利用で得た反証はProduct仮説を見直す正当なEvidenceです。

## 2. 優先順位を決める原則

calendar deadlineではなく、次の順で優先度を判断します。

1. Product Valueへの影響が大きいか。
2. 未決のままだと後続設計を広く拘束するか。
3. 次の高情報量Evidenceを得られるか。
4. 外部環境待ちではなく、現在進められるか。
5. 既存の意味境界を深める仕事か、単なる実装量の追加か。

一つの探索が外部条件で止まっても、SEI全体を同じ待ち状態へしません。意味上独立した高優先課題は並行して進めます。

## 3. Current Product baseline

現在までに、少なくとも次がDesign baselineとして成立しています。

- Product Value / Value Proposition / V1〜V8。
- Decision Memory、Unknown / Conflict、Revision / Exact Binding等のDurable Semantic boundary。
- Human / AIが異なるSurfaceから同じcanonical meaningへ戻るProduct Interaction boundary。
- Local Single-Node Package。
- Product Accessとsemantic Responsibility / Authorityの分離。
- Cognitive Method / Capability ProviderをUniversal semanticsへ同化させない交換境界。

Scoped Executable Evidenceも、Semantic Runtime、Interaction probe、Packaging、Product Access、external Provider / Method、historical reconstruction等で蓄積しています。

v0.2.0 Local Reference Product BaselineにはRelease Evidenceがあります。ただし、post-releaseのExecutable Evidenceを理由に、公開済みv0.2.0のsupported scopeを遡及的に拡張しません。

```text
Design
  != Executable
  != Release
  != Operational
  != Adoption / Outcome
```

この5段階を今後も混同しません。

## 4. 現在の最優先探索 — 二本柱

### Priority B1 — first usable resume-first Product Slice

**ISSUE-000073**を、PMS-03を「意味境界のprobe」から「利用者が継続利用できる製品体験」へ進める最優先探索とします。

Product仮説は次です。

> SEIの最初の強い利用者価値は、recordを多く作れることではなく、時間・AI session・画面stateをまたいで文脈を失った後でも、何を考え、何を決め、何が未解決で、何がその後変わったかへ戻れることにある。

この仮説を**resume-first decision work**として検証します。

最初のsliceはLocal Single-Node上のsingle-userを基本条件とします。これはteam / hosted利用を否定するものではなく、人間側のProduct Valueを最小条件でactualに評価するためのscopeです。

設計上は次を中心にします。

- canonical stateだけから有用なResume Briefを再構成する。
- working set / recent / chat / form stateをProjection-local convenienceへ留める。
- AI outputをprovisional suggestionとして受け、明示的なsemantic change previewを経てcommitする。
- Decision当時のbasisと、Decision後に増えた情報を分けて見せる。
- AI unavailable時もopen / read / manual write / Decision / review / reopenを継続する。
- partial commitとstale writeを「成功した意味変更」として黙って見せない。
- external AIへ出すcontextを選択・確認できる方向を保つ。

この段階では新しいStable Requirementを追加しません。ISSUE-000073のCR-73.1〜10をCandidate Requirementとして、prototypeとhuman reviewから独立したProduct failureが確認された場合だけ昇格を検討します。

最初のDesign正本は次です。

- `product/interaction/SEI_FIRST_USABLE_PRODUCT_SLICE.md`
- `architecture/SEI_INTERACTION_WORKING_SET_ARCHITECTURE.md`
- `plan/issue/ISSUE-000073-define-first-usable-resume-first-product-slice.md`

次の高情報量Evidenceは、canonical-only resume、AI correction、AI unavailable、working-set rebuild、commit fault injection、stale draft、AI context egress、human resume reviewです。

### Priority B2 — TEI executable version exchange

**ISSUE-000072**は引き続きPriority 1です。

historical revision Aを保持し、exact revision B executable sourceとexact revision A fixed reference inputを用いて、actual `deployment-provider-plan`とcurrent SEI Adapter compatibilityを検証します。

```text
build / executable source = exact revision B
fixed reference input     = exact revision A
```

repository-sideのidentity verifier、E2 / E3 runner、別toolchain、stage-aware diagnostics等は整っていますが、revision B actual CLI / Provider Plan / Adapter compatibilityはNot Yet Verifiedです。

外部runner等がactual stepを開始できない状態を、TEI Product failureやAdapter failureへ昇格させません。同時に、execution pathが復旧するまでSEI全体のProduct Interaction設計を止めません。

ISSUE-000072でactual Bが独立したProduct failureを示すまでは、新しいStable Requirement / Universal Contract fieldを追加しません。

## 5. 次順位の探索

### 5.1 actual human outcome review

ISSUE-000071でCognitive Method成果品質の評価境界は確立しましたが、actual human reviewとquality judgementは別です。

今後も次を分離します。

```text
execution conformance
  != structural safety
  != human outcome review
  != Product Value / Adoption outcome
```

resume-first sliceのhuman reviewと、KJ等のMethod成果品質reviewも同じ評価ではありません。前者はProduct Interaction / orientation / correction burden、後者はMethod output qualityを見ます。

### 5.2 broader portability

fixed-scope runtime version、model artifact、TEI revision等の実証から、arbitrary portabilityを推定しません。

別model family、別Provider、別runtime implementation等へ広げる場合は、一変数比較とhistorical reconstructionを維持しながら別Evidenceとして進めます。

### 5.3 Operational / Adoption / Outcome

Release済みであることと、実際の利用者が価値を得たことを分けます。

resume-first sliceは、PMS-08へ向けた最初のAdoption / Outcome観測にもつながります。ただしprototype usability reviewを直ちにAdoption Evidenceへ昇格させません。

## 6. Requirementを深める手順

### Step 1 — Product failureを言葉にする

最初に「どのfieldが必要か」ではなく、利用者または意味上何が壊れるかを書く。

例:

- chat historyを失うと判断へ戻れない。
- AI suggestionがDecisionへ黙って昇格する。
- Decision後の情報でhistorical basisが書き換わる。
- staleな画面が新しいcanonical changeを上書きする。

### Step 2 — 既存REQ / SCNへ戻る

既存Requirementの組み合わせで表せるなら、新IDを増やさない。

ISSUE-000073では少なくともREQ-0001 / 0005 / 0006 / 0010 / 0011 / 0014 / 0015 / 0019、SCN-0003 / 0013 / 0016 / 0018を先に使う。

### Step 3 — Candidate Requirementとして仮置きする

意味上重要に見えても、current implementation固有の問題である可能性がある間はCandidateに留める。

prototype、fault injection、human reviewで再現性を確認する。

### Step 4 — Requirement audit

Stable化前に次を確認する。

1. Product Valueのどれを守るのか。
2. 具体的なScenario / failureで必要性を説明できるか。
3. 既存REQ / SCNで十分ではないか。
4. UI / Provider / Storage / runtimeの実装詳細ではないか。
5. Profile / Adapter / Projection / Persistenceへ置く方が自然ではないか。
6. 10〜50倍先の技術環境でも意味が残るか。
7. Acceptanceをactualに観測できるか。

結果は次のどれでも正当です。

```text
Stable Requirement
or existing Requirement integration
or No Change / Deferred
```

新Requirementを作らない結論を失敗とみなしません。

## 7. Architecture / Contractへ降ろす基準

Architectureへ降ろすのは、意味境界やProduct responsibilityとして説明できるものです。

Contractへ降ろすのは、複数implementation / Provider / process間でportableかつverifiableな合意が必要なものです。

```text
Product requirement
  != Architecture component
  != portable Contract
  != runtime mechanism
```

たとえばISSUE-000073の`working set`や`Resume Brief`はProduct / Projection概念として重要ですが、現時点でUniversal Contractではありません。

`semantic change plan`、snapshot token、atomic commit mechanismも同様に、prototypeで必要性を確かめる前にContract化しません。

## 8. 実証設計の原則

実験では「動かすこと」より「何が判別できるか」を優先します。

少なくとも次を事前に分けます。

- PASS
- expected rejection / conflict
- NOT_VERIFIED
- environment failure
- Product failure

external runner、network、credential、model availability等の失敗を、semantic failureへ昇格させません。

一方で、UIが正常表示されたことだけからcanonical integrityやhuman usabilityを推定しません。

### 8.1 Human review

human reviewでは最初から恣意的なscore thresholdをStable Requirementにしません。

まず次を観測します。

- context loss後に現在地へ戻れるか。
- DecisionとRecommendationを誤読しないか。
- historical basisとpost-decision changeを区別できるか。
- AI誤りを修正・却下できるか。
-最初の有用saveまでの入力負担が大きすぎないか。
- audit detailが必要な場面で到達できるか。

### 8.2 Fault injection

Product confidenceを高めるため、happy pathだけでなくpartial commit、stale write、AI unavailable、Projection cache loss等をactualに壊します。

「失敗したとき何を守るか」を先に設計します。

## 9. Current work lanes

現在の主要laneを次のように扱います。

| Lane | Issue / area | State | Next high-information step |
|---|---|---|---|
| Product Interaction | ISSUE-000073 | Open / Design baseline | prototype E1〜E8 + human review |
| TEI Provider portability | ISSUE-000072 | Open / execution blocked externally | exact-B actual E2 when execution surface is available |
| Method outcome quality | ISSUE-000071 follow-up | evaluation boundary established | actual human outcome review |
| Operational / Adoption | PMS-08 | Not Yet Verified | first real use after usable slice exists |

lane間でEvidenceを流用しません。

```text
interaction prototype PASS
  != TEI compatibility PASS

TEI compatibility PASS
  != human usability PASS

human usability review
  != Adoption / Outcome Satisfied
```

## 10. 作業の停止線

次の場合は実装へ急がず上流へ戻ります。

- 何のProduct Valueを改善するか説明できない。
- 新しい型を作る理由がUI convenienceだけである。
- Workspace / Session / Thread等をProduct navigationからUniversal ontologyへ昇格させようとしている。
- AI responseをcanonical fact / Decisionへ黙って保存しようとしている。
- private chain-of-thoughtを再構成条件にしようとしている。
- current informationをhistorical Decision basisへ混ぜようとしている。
- Unknown / Conflict / unavailableをfalse / Noへ変換しようとしている。
- concurrency tokenをSemantic Revisionへ流用しようとしている。
- browser / HTTP / MCP / specific modelをprototype採用だけでStable Requirementへしようとしている。
- partial commitやstale writeを「実装詳細」として放置し、利用者へ誤ったcanonical成功状態を見せる可能性がある。
- Design Evidenceだけでproduction usabilityを主張しようとしている。
- ISSUE-000070の固定scope PASSをISSUE-000072やarbitrary portabilityへ流用しようとしている。
- runner未割当等のenvironment failureをProduct failureへ昇格させようとしている。
- post-release Evidenceをv0.2.0 supported scopeへ遡及追加しようとしている。

## 11. 計画文書の更新単位

上流判断が変わった場合、必要な範囲で次を同じ作業単位に同期します。

- Product Interaction / Product Shape / Milestone文書
- Issue / ADR
- Requirement / Acceptance Scenario
- Architecture / Contract
- Evidence文書
- `plan/registry.yaml`
- `plan/document_review_registry.yaml`

「全部を毎回更新する」ことは目的にしません。正本関係に矛盾が生じる箇所だけを更新します。

新しいMarkdownを追加した場合はDocument Review Registryのscopeを確認し、自然な日本語として再ドラフトした後、意味・要求強度・留保・Evidence強度が変わっていないか最終監査します。

## 12. Natural Japanese review

2026-09-11時点で、上流計画を実証履歴の長い時系列説明から、Product Valueから現在の行動へ降りる計画書として再構成した。

Provider / Method portabilityのEvidenceは重要だが、意味境界の実証が進んだ一方で、人間が「使い続けられること」のactual Evidenceが相対的に弱い。このためPMS-03を再び主探索へ上げ、ISSUE-000073のresume-first Product SliceをPriority B1とした。

同時にISSUE-000072のTEI executable version exchangeはPriority 1のまま維持する。これは重要度を下げたのではなく、外部execution surface待ちの探索と、repository内で進められるProduct Interaction探索を独立laneとして扱うためである。

Candidate RequirementをStable化せず、working set、Resume Brief、semantic change plan、snapshot token等をProduct / Architecture上の設計語彙に留めた。今後はprototype、fault injection、human reviewから、既存REQ / SCNで不足する独立したProduct failureだけをRequirement化する。

意味、規範強度、current Evidence、未検証範囲を維持しながら、根幹の趣旨から個別作業へ自然に読める構造へ全文を再ドラフトし、最終意味監査を実施した。