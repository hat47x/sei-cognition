# SEI 上流プロダクト開発計画

更新日: 2026-09-18  
状態: **Current Upstream Planning Baseline — Brand-world Product Value discovery完了 / Inquiry Continuity actual dogfood / resume-first Product Slice / TEI version exchange + actual-binary Evidence protocolを並行優先**

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
- Work / Interaction、Projection / Review、Evidence / Governance等のApplication PlaneではTEIを第一候補としつつ、SEI Product / Semantic authorityとTEI implementation authorityを分離するTEI-first方針。Semantic Core、Cognitive Method、provider-specific low-level integration、headless pathはTEIへ強制しない。

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

### Priority A foundation — ブランド世界をProduct Value discoveryへ接続する（ISSUE-000077 Resolved）

**ISSUE-000077**では、SEI Cognitionの「井」を中心に形成されたブランド世界を、Product Valueの未発見部分や弱い部分を探索する上流sourceとして整備し、2026-09-16にResolution条件を満たしたと判断しました。

このIssueでは、井戸、水、深層、中央の空白、静けさ、四方向性、共有財産といった象徴をProduct Requirementへ直接変換せず、それらが何を利用者・組織の価値として照らしているのかを十分に豊かな文章として保存し、current Product Value / Value Model / Vision / Principlesへ逆照合しました。

完了した探索単位は次です。

- `product/value/SEI_BRAND_WORLD_DISCOVERY_SOURCE.md`に、井、中央の空白、水、静けさ、四方向性、Cognitive Commons、SEI / SUI / TEIの象徴関係を**非規範のProduct Value discovery source**として保存した。
- `product/value/SEI_BRAND_WORLD_PRODUCT_VALUE_REVIEW.md`で、Cognitive Commons、Surface / Depth Interface、Deliberate Non-closure、Durable Cognitive Aperture、Quiet Infrastructure、Shared but not Unboundedをcurrent V1〜V8 / Decision Continuityへ逆照合した。
- `product/vision/SEI_PRODUCT_VISION.md`へ、判断前のInquiryを失わないこと、boundedな共有認知基盤、人間・AI・Methodが利用するInfrastructure、過剰なattentionを要求しない将来像を反映した。
- 新しいValue Axisを追加しないと判断した。
- Reviewで最も独立性が高く残った**Decision成立前のInquiry Continuity**を、ISSUE-000078としてactual comparisonへ切り出した。

Discovery Reviewのcurrent判断は次です。

```text
Cognitive Commons           → Product Visionへ統合 / 新Value Axisなし
Surface / Depth Interface   → Brand / Vision説明へ限定
Deliberate Non-closure      → current V2 / V5で十分
Quiet Infrastructure        → Product Interaction quality hypothesis
Shared but not Unbounded    → Cognitive Commons成立条件
Inquiry Continuity          → follow-up Product hypothesis
```

したがって、ISSUE-000077の完了後にブランド文書を増やし続けることはPriority Aの目的ではありません。activeな高情報量探索は**ISSUE-000078**へ引き継ぎ、Decisionがまだ存在しない長期Inquiryについて、raw chat / chronological note / SEI canonical meaningを比較し、SEI固有の継続価値が本当に存在するかを反証可能にします。

この比較では、resume speedだけでなく、historical attribution error、Observation / Hypothesis混同、unresolved omission、original concern drift、capture burden、AI summary correction burden等を観測します。

2026-09-14にはfirst actual caseをseedし、2026-09-16にはcase作成からの暦上のmulti-day gapへ一度到達しました。ただし、同日の上流計画・branch整理でcurrent Inquiry stateへmaterialな事前露出が生じたため、cleanな認知的gapはそこで再設定しています。現在の境界は次です。

```text
actual Inquiry seeded
+ calendar multi-day gap reached once
+ resumption procedure prepared
+ pre-orientation material exposure observed
+ clean context gap reset
!= human resumption observed
!= Inquiry Continuity value established
```

したがって、現在もっとも高情報量なのは、最後のmaterial exposureから十分なgapを置き、元chat / sourceを先に開かず、SEI Orientationだけから実際に再開し、historical correctness、unresolved preservation、source reopen、attention burden、first useful actionを観測することです。

ISSUE-000078の結果は、次のいずれでも正当です。

```text
existing V1〜V8 / Decision Continuityで十分
or Decision Continuityの適用範囲拡張
or Cognitive Continuityへの再整理
or Inquiry Continuityの独立cross-axis outcome
or SEIに実質的な価値差なし
```

探索では、ブランド世界をKJの外部分類枠として用いません。象徴は問いを増やすcueとして使い、最終的な価値構造はSEIのcurrent Product material、実利用Scenario、failure、counterexampleから立ち上げます。

ISSUE-000077はProduct Value discovery sourceの確立として完了しましたが、その成果は引き続き上流へ戻るためのsourceとして維持します。ISSUE-000078、ISSUE-000073、ISSUE-000072はそれぞれ異なる未知を扱う独立laneであり、相互のEvidenceを代用しません。

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

ISSUE-000073のCandidate Requirement監査では、CR-73.8 / CR-73.9を一つのfailure boundaryとして統合し、**REQ-0023 / SCN-0019 Canonical commit integrity**へformalizeしました。これはpartial commitとstale writeが利用者へ誤ったcanonical成功状態を見せる独立failureとして残ったためです。

一方、CR-73.1〜73.7 / 73.10は既存Requirement、Product-local設計、またはH1 / H2 human Outcome評価へ戻し、新しいStable Requirementへは昇格していません。prototype sourceやrunnerの存在だけをRequirement成立理由にはしません。

最初のDesign正本は次です。

- `product/interaction/SEI_FIRST_USABLE_PRODUCT_SLICE.md`
- `architecture/SEI_INTERACTION_WORKING_SET_ARCHITECTURE.md`
- `plan/issue/ISSUE-000073-define-first-usable-resume-first-product-slice.md`

canonical-only resume、AI correction、AI unavailable、working-set rebuild、commit fault injection、stale draft、AI context egressについてはProduct-localなprobe / test sourceが一通り揃っています。E1〜E8 actual実行はGo 1.25.x環境待ちで**Not Yet Verified**、H1 / H2 human reviewは**Not Yet Observed**です。H2は073/078共通のprovenance-first review runnerへ統合し、known exposureをclean blinded reviewへ読み替えない境界を固定しています。

したがって次の高情報量Evidenceは、(1) clean Go 1.25.x環境でのE1〜E8 actual実行、(2) real InquiryでのH1 actual resume、(3) provenance条件を満たすH2 human matched reviewです。

### Priority B1 companion — TEI-first Application Plane Reference Adoption

Product Shapeで定めたTEI-first方針を、実装上の既成事実ではなく反証可能な探索へ戻すため、**ISSUE-000079**をPriority 1で起票しました。

ISSUE-000079が問うのは、SEIをTEIへ多く移せるかではありません。ISSUE-000073のresume-first Product Valueを保ったまま、Application PlaneをTEIで実装することで、二重管理を増やさずchange amplificationを実際に減らせるかを検証します。

最初のReferenceはWeb UI完成ではなく、SEI側をauthorityとして保ったread-only Resume / Review Projectionです。次にEvidence / Governance SurfaceをPressureします。

```text
SEI canonical state
  = authority

TEI Reference mapping / Projection
  = derived / read-only

TEI can render/read SEI meaning
  != TEI owns SEI meaning
```

SUI Reference Adoptionで採用された`encapsulation before translation`、およびExisting TEI → reusable extension → Native application asset → cross-application Evidenceを伴うCore candidateという分類を再利用します。ただし、SUIのEvidenceをSEIのEvidenceへ流用しません。

SUI側で候補となっているReview / Diff Visualizationは、SEIを第二Applicationとして再利用性をPressureできるため、Plugin / extension discovery上の高情報量な比較対象です。SEI一件またはSUI一件だけを根拠にTEI Coreを増やしません。

ISSUE-000079はISSUE-000073のH1 / H2 human reviewをブロックしません。073は人間にとってのProduct Value、079はApplication implementation strategyを扱う別laneです。

2026-09-18にはStage 0としてTEI側ISSUE-000054 / PR #686を実装し、SEI fixtureをread-only sourceとするReference checkerについてGo 1.23.2のtargeted `go test` / `go vet` PASSを取得しました。TEI Coreや新Application Pattern Kindは追加していません。

このEvidenceが示すのは、Recommendation / Decision、historical basis、unresolved、post-decision changeの意味差をReference-localに保持できることまでです。TEI Application / Projectionを使うことで実際に開発負荷が下がるかは未検証なので、次はChange 1（Decision後Observationの追加）のnative / TEI change-amplification比較を優先します。

```text
073 human usability / Decision Continuity Evidence
  != 079 TEI adoption Evidence

079 change-amplification improvement
  != 073 Product Value established
```

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

隣接する**ISSUE-000074**では、actual TEI binaryを実行した際のEvidence採取を再利用可能にするため、`runtime/go/teiprobe`、`runtime/go/cmd/tei-e3b-probe`、`runtime/ACTUAL_TEI_EVIDENCE_PROTOCOL.md`を2026-09-18に実体化しました。direct executableのSHA-256、declared source、optional manifest match、Provider Plan実行、current Capability Observationをderived reportへ束ねます。

このprotocol sourceの実装は、ISSUE-000072のrevision B actual executionを代替しません。fixture-scoped test sourceもactual TEI Evidenceではなく、current Go 1.25環境でのtest実行とactual binary report生成は**Not Yet Verified**です。

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

### 5.2 Inquiry Continuityのcounterfactual comparison

ISSUE-000078では、Decision成立前のInquiryを対象に、raw chat、chronological note、SEI canonical meaning + derived Projectionを比較します。

ここでは「SEIを使うと詳しく記録できる」ことを価値としません。

次を分けて観測します。

- original concernを正しく再構成できるか。
- Observation / Hypothesis / AI suggestionを取り違えないか。
- unresolvedを発見できるか。
- later informationをhistorical contextへ誤帰属しないか。
- next useful stepへ戻る負担が減るか。
- capture / review overheadが価値を相殺しないか。

first actual caseでは、最後のmaterial exposureから十分なgapを置いた後、まずSEI Orientation単独のcleanなresumptionを観測します。Generic Summary / chronological noteとのcounterfactual比較は、その観測後に行い、比較自体が最初の再開時working memoryへ干渉しないようにします。

Quiet-first / Proactive-firstの比較も、同じfirst caseで同時提示して結論を出しません。別caseまたは条件順序を入れ替えた比較を用い、順序効果を分離します。

この探索はISSUE-000073のDecision-centered resumeと近接しますが、Decisionが存在しない条件を意図的に分離して検証します。

### 5.3 broader portability

fixed-scope runtime version、model artifact、TEI revision等の実証から、arbitrary portabilityを推定しません。

別model family、別Provider、別runtime implementation等へ広げる場合は、一変数比較とhistorical reconstructionを維持しながら別Evidenceとして進めます。

### 5.4 Operational / Adoption / Outcome

Release済みであることと、実際の利用者が価値を得たことを分けます。

resume-first sliceやInquiry Continuity比較は、PMS-08へ向けたAdoption / Outcome観測にもつながり得ます。ただしprototype usability reviewを直ちにAdoption Evidenceへ昇格させません。

## 6. Requirementを深める手順

### Step 1 — Product failureを言葉にする

最初に「どのfieldが必要か」ではなく、利用者または意味上何が壊れるかを書く。

例:

- chat historyを失うと判断へ戻れない。
- AI suggestionがDecisionへ黙って昇格する。
- Decision後の情報でhistorical basisが書き換わる。
- staleな画面が新しいcanonical changeを上書きする。
- Decision前のInquiryで、数日後に元のconcernや未解決点へ戻れない。

ブランド世界から来た価値候補についても、最初に「井に対応するfieldは何か」と考えません。たとえば「静けさ」が重要に見えるなら、AI suggestionの過剰提示、attention burden、早すぎる収束等、利用者世界で何が壊れるのかを先に言葉にします。

### Step 2 — 既存REQ / SCNへ戻る

既存Requirementの組み合わせで表せるなら、新IDを増やさない。

ISSUE-000073では少なくともREQ-0001 / 0005 / 0006 / 0010 / 0011 / 0014 / 0015 / 0019、SCN-0003 / 0013 / 0016 / 0018を先に使う。

ISSUE-000077から生じる価値候補は、Requirement以前にProduct Value / Value Model / Principleの既存coverageへ戻る。象徴との対応が美しいことだけではRequirement化の理由にならない。

ISSUE-000077 / 000078から生じる価値候補は、Requirement以前にProduct Value / Value Model / Principleの既存coverageへ戻る。象徴との対応が美しいことや、比較実験で一度差が出たことだけではRequirement化の理由になりません。

### Step 3 — Candidate Requirementとして仮置きする

意味上重要に見えても、current implementation固有の問題である可能性がある間はCandidateに留める。

prototype、fault injection、human reviewで再現性を確認する。

ISSUE-000078では、Inquiry、Workspace、Session等を先にCandidate Requirementへ置かず、まずexisting canonical meaningだけでProduct failureを改善できるか確認します。

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

ISSUE-000078の`Inquiry Continuity`も、現時点ではevaluation上のProduct hypothesisです。`Inquiry`を新しいUniversal entityへ昇格させる理由にはしません。

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

ISSUE-000078では、resume speedだけでなくhistorical correctnessを同時に見ます。早く再開できても、later knowledgeでinitial concernを書き換えていればProduct Value上の成功にはしません。

### 8.2 Fault injection

Product confidenceを高めるため、happy pathだけでなくpartial commit、stale write、AI unavailable、Projection cache loss等をactualに壊します。

「失敗したとき何を守るか」を先に設計します。

## 9. Current work lanes

現在の主要laneを次のように扱います。

| Lane | Issue / area | State | Next high-information step |
|---|---|---|---|
| Product Value discovery | ISSUE-000077 | Resolved / source + review + Vision integration complete | ISSUE-000078等のactual Evidenceでreopen conditionが生じた場合のみ再監査 |
| Inquiry Continuity validation | ISSUE-000078 | Open / actual Inquiry seeded / clean context gap reset after material exposure | last material exposureから十分なgap後のSEI Orientation actual human resumption、次いでraw chat / note counterfactual |
| Product Interaction | ISSUE-000073 | Open / prototype + Requirement audit progressed / E1〜E8 actual・H1/H2 pending | Go 1.25 actual E1〜E8、H1 actual resume、H2 provenance-first human review |
| Application implementation strategy | ISSUE-000079 | Open / source freeze PASS + TEI Stage 0 Reference checker Scoped Executable Evidence available / PR #686 merged | Change 1のnative / TEI change-amplification比較、次いでExisting / extension / Native / gap再分類 |
| TEI Provider portability | ISSUE-000072 | Open / execution blocked externally | exact-B actual E2 when execution surface is available |
| TEI actual Evidence protocol | ISSUE-000074 | Open / teiprobe + CLI + protocol source implemented / tests + actual run Not Yet Verified | current Go環境でfixture-scoped tests、次いでactual TEI binary report |
| Method outcome quality | ISSUE-000071 follow-up | evaluation boundary established | actual human outcome review |
| Operational / Adoption | PMS-08 | Not Yet Verified | first real use after usable slice exists |

lane間でEvidenceを流用しません。

```text
brand-world coherence
  != Product Value validated

Inquiry Continuity design
  != Inquiry Continuity human outcome proven

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
- Inquiry Continuityという名前を根拠に`Inquiry` / `Workspace` / `Session`等をUniversal ontologyへ昇格させようとしている。
- Workspace / Session / Thread等をProduct navigationからUniversal ontologyへ昇格させようとしている。
- AI responseをcanonical fact / Decisionへ黙って保存しようとしている。
- private chain-of-thoughtを再構成条件にしようとしている。
- current informationをhistorical Decision basisやinitial Inquiry contextへ混ぜようとしている。
- Unknown / Conflict / unavailableをfalse / Noへ変換しようとしている。
- concurrency tokenをSemantic Revisionへ流用しようとしている。
- browser / HTTP / MCP / specific modelをprototype採用だけでStable Requirementへしようとしている。
- TEI-first方針を「TEIを使わなければならない」というStable Requirementへ読み替え、SEI Application Planeの実証前にTEI Core / Plugin種別を増やそうとしている。
- TEIで表示できることを、SEI semantic authorityがTEIへ移ったこととして扱おうとしている。
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

2026-09-16時点で、ISSUE-000077のBrand World Discovery SourceとProduct Value Reviewは`product/value`へ一本化され、Product Visionへ必要な範囲だけを反映しています。旧`product/vision/SEI_BRAND_WORLD_SOURCE.md`および旧`SEI_BRAND_WORLD_VALUE_DISCOVERY_REVIEW.md`という配置・名称はcurrent正本ではありません。H77.1〜H77.6の逆照合、No Change判断、上位文書への配置、後続Issue切り出しまで完了したため、ISSUE-000077はResolvedとしました。

Reviewの結果、Cognitive Commons、Surface / Depth Interface、Deliberate Non-closure、Quiet Infrastructure、Shared but not Unboundedは、新しいValue Axisを増やすより、既存V1〜V8、Decision Continuity、Product Vision、Product Interactionの説明を深める方が自然と判断しました。

一方、Durable Cognitive Apertureの検討から、Decisionが成立する前のInquiryについて、時間・AI session・担当者をまたいで元のconcern、Observation、Unknown、Hypothesisへ戻れるかがcurrent Product Valueで十分に反証されていないことを確認しました。そのためISSUE-000078を起票し、ブランド比喩ではなくraw chat / noteとのcounterfactual comparisonでProduct Valueの有無を確認します。

first actual caseは2026-09-14にseed済みで、2026-09-16にはcase作成からの暦上のmulti-day gapへ一度到達しました。ただし同日の上流整理でmaterialな事前露出が生じたため、clean context gapはその時点から再設定し、human observationはまだ記録していません。この差を維持し、次は最後のmaterial exposureから十分なgapを置いた後にOrientationからのactual resumptionを先に観測し、その後にGeneric Summary / chronological noteおよびQuiet / Proactive条件を比較します。

Provider / Method portabilityのEvidenceは引き続き重要であり、人間が「使い続けられること」のactual Evidenceを深めるISSUE-000073も並行して進めます。ISSUE-000072のTEI executable version exchangeもPriority 1のまま維持します。加えて2026-09-18のProduct ShapeでApplication PlaneをTEI-firstとする実装方針が明示されたため、これを暗黙の実装命令にはせずISSUE-000079へ切り出しました。079ではResume / ReviewとEvidence / Governanceをread-only ReferenceからPressureし、change amplification、二重管理、authority driftを比較してbroad / incremental / limited / deferredの判断へ進めます。

各laneは互いのEvidenceを代用せず、上流価値、Inquiry Continuity、Decision-centered Product Interaction、Application implementation strategy、Provider portabilityという異なる未知を減らします。

今回の更新では、ISSUE-000077のResolutionとactiveなfollow-up探索の分離を現在地へ合わせました。ブランド世界の詩的な豊かさと、SEIのProduct governanceが要求するauthority / Evidenceの厳密さをどちらも削らず、背景から価値仮説、Discovery Reviewの結論、follow-up実証、下位設計へ降ろさない停止線、現在のwork laneまでが自然につながるように再読し、**自然な日本語となることを最重要視したうえで、意味、規範強度、current Evidence、未検証範囲が変わっていないことを最終監査しました。**