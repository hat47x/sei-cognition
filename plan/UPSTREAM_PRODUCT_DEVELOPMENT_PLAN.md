# SEI 上流プロダクト開発計画

更新日: 2026-09-13  
状態: **Current Upstream Planning Baseline — Product Value discovery / resume-first Product Slice / TEI version exchangeを並行優先**

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

また、Product Valueの根に関わる探索は、直ちにRequirementや実装へ降ろす必要はありません。ブランド世界、実利用上の違和感、KJ的な統合、外部研究等が新しい価値仮説を照らす場合は、まず**Product Value discovery source**として扱い、既存Value ModelやScenarioへ逆照合します。

```text
rich source / metaphor / observation
  != Product Value authority
  != Requirement authority
```

象徴や比喩が豊かであること自体を規範上の根拠にはせず、そこから利用者benefit、failure、counterexample、既存coverageを取り出して初めてProduct文書へ反映します。

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

## 4. 現在の最優先探索 — 三本柱

### Priority A — ブランド世界をProduct Value discoveryへ接続する

**ISSUE-000077**を、SEI Cognitionの「井」を中心に形成されたブランド世界から、Product Valueの未発見部分や弱い部分を探索する上流laneとして扱います。

このIssueでは、井戸、水、深層、中央の空白、静けさ、四方向性、共有財産といった象徴をProduct Requirementへ直接変換しません。まず、それらが何を利用者・組織の価値として照らしているのかを、十分に豊かな文章として保存し、current Product Value / Value Model / Vision / Principlesへ逆照合します。

主要なProduct hypothesisは次です。

- **Cognitive Commons** — 認知成果を一個人・一AI session・一Providerの私有状態へ閉じず、適切なaccess / responsibility boundaryのもとで組織の共有資産として持続させる価値。
- **Surface / Depth Interface** — まだ十分に言語化・構造化されていない観察や違和感を、Truthへ早まって昇格させず、扱える認知対象へ持ち上げる価値。
- **Deliberate Non-closure** — Unknown / Conflict / Hypothesisを必要な期間保ち、未解決を消さずに責任あるDecisionへ進める価値。
- **Durable Cognitive Aperture** — 時間・人・AI・Surfaceが変わっても、問いを置き直し、認識へ戻り、新しいObservationを加えられる入口を持続させる価値。
- **Quiet Infrastructure** — 常時AI suggestionを押し付けるのではなく、必要時に深い認知へ到達でき、通常時のattention burdenを増やしすぎない基盤としての価値。
- **Shared but not Unbounded** — 共有可能性とSelective Disclosure / Responsibility / Access Controlを両立させる価値。

これらは新しいValue Axisとして確定していません。V1〜V8やDecision Continuityの別表現で十分なら統合し、新しいProduct Valueを増やさない結論を正当な成果とします。

探索では、ブランド世界をKJの外部分類枠として用いません。象徴は問いを増やすcueとして使い、最終的な価値構造はSEIのcurrent Product material、実利用Scenario、failure、counterexampleから立ち上げます。

最初の成果物は次を想定します。

- ブランド世界をProduct Value探索源として保存する非規範source文書。
- Product Value Discovery Review。
- 必要性が確認できたProduct Value / Value Model / Vision / Proposition / Principles等の改稿または新規起票。
- Product文書へ採用しなかった洞察についてのNo Change理由。
- actual human reviewやprototypeが必要な価値仮説のFollow-up Issue。

このlaneはProduct Valueの根を見直すため、実装laneより上流に置きます。ただし、検討中であることを理由にISSUE-000073やISSUE-000072の独立したEvidence取得を止めません。

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

ブランド世界から来た価値候補についても、最初に「井に対応するfieldは何か」と考えません。たとえば「静けさ」が重要に見えるなら、AI suggestionの過剰提示、attention burden、早すぎる収束等、利用者世界で何が壊れるのかを先に言葉にします。

### Step 2 — 既存REQ / SCNへ戻る

既存Requirementの組み合わせで表せるなら、新IDを増やさない。

ISSUE-000073では少なくともREQ-0001 / 0005 / 0006 / 0010 / 0011 / 0014 / 0015 / 0019、SCN-0003 / 0013 / 0016 / 0018を先に使う。

ISSUE-000077から生じる価値候補は、Requirement以前にProduct Value / Value Model / Principleの既存coverageへ戻る。象徴との対応が美しいことだけではRequirement化の理由になりません。

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

同様に、ISSUE-000077の`well`、`depth`、`aperture`、`commons`、`quiet`等はProduct Value探索の語彙であり、Contract fieldやruntime entityの候補ではありません。独立した規範上の必要性が別途確認されない限り、象徴語彙を下位設計へ持ち込みません。

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
- 最初の有用saveまでの入力負担が大きすぎないか。
- audit detailが必要な場面で到達できるか。

ISSUE-000077由来の価値仮説をhuman reviewへ進める場合は、ブランド語に共感するかではなく、実務上のbenefit / burden / failureを観測します。「静かな感じがする」「井の比喩が分かりやすい」ことだけをProduct Value Evidenceにしません。

### 8.2 Fault injection

Product confidenceを高めるため、happy pathだけでなくpartial commit、stale write、AI unavailable、Projection cache loss等をactualに壊します。

「失敗したとき何を守るか」を先に設計します。

## 9. Current work lanes

現在の主要laneを次のように扱います。

| Lane | Issue / area | State | Next high-information step |
|---|---|---|---|
| Product Value discovery | ISSUE-000077 | Open / upstream hypothesis | brand-world source + Value Discovery Review + document placement audit |
| Product Interaction | ISSUE-000073 | Open / Design baseline | prototype E1〜E8 + human review |
| TEI Provider portability | ISSUE-000072 | Open / execution blocked externally | exact-B actual E2 when execution surface is available |
| Method outcome quality | ISSUE-000071 follow-up | evaluation boundary established | actual human outcome review |
| Operational / Adoption | PMS-08 | Not Yet Verified | first real use after usable slice exists |

lane間でEvidenceを流用しません。

```text
brand-world coherence
  != Product Value validated

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
- ブランド象徴や比喩からfield、Universal型、workflowを直接演繹しようとしている。
- 「井」「水」「深層」「静けさ」等の美しい整合だけをProduct Value成立のEvidenceにしようとしている。
- `cognitive commons`を全情報の無制限共有やAccess Control不要という意味へ読み替えようとしている。
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
- Product Value / Value Model / Vision / Proposition / Principles
- Issue / ADR
- Requirement / Acceptance Scenario
- Architecture / Contract
- Evidence文書
- `plan/registry.yaml`
- `plan/document_review_registry.yaml`

「全部を毎回更新する」ことは目的にしません。正本関係に矛盾が生じる箇所だけを更新します。

新しいMarkdownを追加した場合はDocument Review Registryのscopeを確認し、自然な日本語として再ドラフトした後、意味・要求強度・留保・Evidence強度が変わっていないか最終監査します。

特にProduct Value discoveryでは、短い標語や箇条書きだけを追加して完了としません。価値が生まれる背景、利用者世界での意味、反対側のtrade-off、既存Valueとの関係まで十分な文脈として書き、別の人間や将来のAIがその判断を再構成できる状態を目指します。

## 12. Natural Japanese review

2026-09-13時点で、従来の二本柱に加え、ISSUE-000077のBrand-world-informed Product Value discoveryを上流laneとして追加した。

SEI Cognitionへの改名とブランド設計を深める過程で、「井」は単なる名称・ロゴモチーフではなく、地表とまだ十分に形を得ていない認知領域の間にあるgateway、中央の空白を問いと可能性のために保つ構造、共有されながら無制限公開ではないCognitive Commons、早すぎる収束を強制しないQuiet InfrastructureといったProduct上の問いを照らしている。

ただし、この豊かなブランド世界をそのままProduct Valueの正本にはしない。ISSUE-000077では、象徴を探索sourceに留め、利用者benefit、failure、counterexample、既存V1〜V8 / Decision Continuityとの重複を通して、必要な上位文書へだけ反映する停止線を置いた。新しいValue AxisやRequirementを増やさない結論も正当な成果とする。

Provider / Method portabilityのEvidenceは引き続き重要であり、人間が「使い続けられること」のactual Evidenceを深めるISSUE-000073も並行して進める。ISSUE-000072のTEI executable version exchangeもPriority 1のまま維持する。三つのlaneは互いのEvidenceを代用せず、上流価値、Product Interaction、Provider portabilityという異なる未知を減らす。

今回の更新では、ブランド世界の詩的な豊かさと、SEIのProduct governanceが要求するauthority / Evidenceの厳密さをどちらも削らないことを重視した。背景から価値仮説、下位設計へ降ろさない停止線、現在のwork laneまでが自然につながるように全文を再構成し、**自然な日本語となることを最重要視して再ドラフトしたうえで、意味、規範強度、current Evidence、未検証範囲が変わっていないことを最終監査した。**