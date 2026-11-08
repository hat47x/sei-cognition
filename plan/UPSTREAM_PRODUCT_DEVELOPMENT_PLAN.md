# SEI 上流プロダクト開発計画

更新日: 2026-11-08（§9.1追補。旧Laneの個別状態は作成時点の履歴を含む）  
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

canonical-only resume、AI correction、AI unavailable、working-set rebuild、commit fault injection、stale draft、AI context egressについてはProduct-localなprobe / test sourceが一通り揃っています。E1〜E8 actual実行は、2026-10-09に事前配置のgo1.25.14でtested commit `694ec5805c00a8bae9034e15ee0d1589e40f6fd8`に対して**PASS**しました（必須18 testがすべてpass、verifier findings 0。Local Single-Node上のProduct-local probeに限定したScoped Executable Evidence）。一方、H1 / H2 human reviewは**Not Yet Observed**です。H2は073/078共通のprovenance-first review runnerへ統合し、known exposureをclean blinded reviewへ読み替えない境界を固定しています。

E1〜E8 PASSはDecision Continuityの人間にとっての価値を示しません。したがって次の高情報量Evidenceは、(1) real InquiryでのH1 actual resume、(2) provenance条件を満たすH2 human matched reviewです。加えて、bootstrap wrapperがpinned archiveからtoolchainを自力で準備する経路は未実行のため、外向き通信が可能な環境での実行確認も残ります。

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

### 横断的な探索候補 — 組織の暗黙の要求・価値観を文脈に合わせて明文化する（2026-11-01、Proposed）

[組織の暗黙の期待の明文化とフィッティング研究](../evaluation/organization-tacit-needs/RESEARCH_AND_REQUIREMENTS_CANDIDATE_2026-11-01.md)を、既存[SEI #677](https://github.com/hat47x/sei-cognition/issues/677)のIR-01〜06と[SEI #660](https://github.com/hat47x/sei-cognition/issues/660)の組織文脈適用を具体化する**評価候補**として追加する。現在の三本柱の達成や優先順位を置き換えるものではなく、Stable Requirement / Core Contract の追加を決定しない。

**価値の問い**：組織の種類、法域、時流、業態、MVV、経営者の表明、部門・役割、現在の事業状況が異なるとき、同じ職種の担当者がどんな前提で判断するかを、安易な類型化を避けて説明・再評価できるか。組織の実慣行と宣言価値、文化の推測と正式な規則、現在の権限と過去の判断を区別できるか。

**先に試す手順**：
1. SaaS型、SI受託型、両事業を持つ複合企業の**合成**資料で、プリセットを「決定済みの規則」ではなく「最初の確認質問」として使う。国・人種・民族等から個人の性格・価値観を推測する方式は採用候補にしない。
2. 公式MVV、許可された規程・決定・観測、部門別の異論、事業状況を参照し、暗黙の期待を**Hypothesis / Question / Conflict / Unknown / Clause Candidate**として文脈・出典・版に束縛する。要求の正式採否は当該Ownerに委ねる。
3. SUIの既存違和感メモと履歴、SEIの時点付き認知・再開、TEIの組織/業務意味モデル、SHOの原典、EKIの限定委任を接続する。現在の責務を重複して新しい共通Coreに移さない。
4. 同一質問・同一入力で「外部Harnessのみ」「Harness＋組織Contextメモ」「Harness＋SEIの根拠・相反・再評価」を比較する。組織変更・プリセット版更新・役割失効・情報未取得・違和感の反例を加え、選択の質と確認負荷を測る。
5. 価値が確かめられた差だけを既存REQ/Scenario/Profile/Issueへ昇格候補として戻し、不要ならSkill/通常ファイル/既存UIのまま成立させる。人事・採用等の高影響判断や実組織データ収集は別の安全・権限確認を要する。

**Evidenceの状態**：外部研究と設計比較はDesign Evidence。上記の合成テスト、実利用、組織内情報へのアクセス、本人の評価、正式なOwner受理は**NOT RUN**。既存の課題・実証を重複させず、次に有効なEvidenceが取れる時点で優先順位を見直す。

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
| Product Interaction | ISSUE-000073 | Open / prototype + Requirement audit progressed / E1〜E8 actual PASS (2026-10-09) / H1・H2 pending | H1 actual resume、H2 provenance-first human review |
| Application implementation strategy | ISSUE-000079 | Open / source freeze PASS + TEI Stage 0 Reference checker Scoped Executable Evidence available / TEI PR #686 merged | Change 1のnative / TEI change-amplification比較、次いでExisting / extension / Native / gap再分類 |
| TEI Provider portability | ISSUE-000072 | Open / execution blocked externally | exact-B actual E2 when execution surface is available |
| TEI actual Evidence protocol | ISSUE-000074 | Open / teiprobe + CLI + protocol source implemented / tests + actual run Not Yet Verified | current Go環境でfixture-scoped tests、次いでactual TEI binary report |
| Family integration apex（提案） | ADR-0035 Proposed / ISSUE-000085〜000088 Open | 提案のみ。所有者のレビュー待ち。Design Evidenceに限る | 所有者による再基線化項目のレビュー（ISSUE-000085）、次いで実在の記録からの求心プロファイル（ISSUE-000087）と4つの空白の組合せ試験（ISSUE-000086） |
| Method outcome quality | ISSUE-000071 follow-up | evaluation boundary established | actual human outcome review |
| Cognitive Methodの問い相対的十分性（TEI連携） | SEI #767 / #769、#820（関連） | 公開合成の反証・TEI実CLIの限定観測まで。実SEI Method接続と独立比較は未実施 | 同一Q・同一Source/Grant/予算でD0/D1/M1の限定実Read比較 |
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

### 9.1 TEIハーネス#3：問い相対の根拠十分性を実Productへ接続する（2026-11-08・計画）

**位置づけ**：SEI [#767](https://github.com/hat47x/sei-cognition/issues/767) のMethod Inquiry・Residual・次Probe選択を、TEI [#3262](https://github.com/hat47x/tei-platform/issues/3262) の実CLI Readと独立Required、[TEI #2516](https://github.com/hat47x/tei-platform/issues/2516) のConstruction Context、[TAI #168](https://github.com/hat47x/tai-pleroma/issues/168) の実Harness受渡しへつなぐ。SEIはQuery/Parser/Index・Oracle・実Provider・Host認可の第二実装を持たず、意味受理はTEI/業務Ownerへ残す。Method/Skillの追加は効果が確認された場合に限り必須条件を検討する。

**確認済みの出発点（資格を限定）**：TEI [merged #3354](https://github.com/hat47x/tei-platform/pull/3354) のexact-head専用CIでは、固定公開Workspaceの実CLI **11 Reply**、独立Required Rule **3件**、合成Consumer負例 **32件**、6 pinned Step＋既知RuleのT1-A **1件**が限定PASS。これはFunction/Business/Ruleの全閉包や外部Tool Replyの完全配送、AIによる未知Obligation発見、Owner意味受理を証明しない。TEI [Draft #3176](https://github.com/hat47x/tei-platform/pull/3176) CC-12〜18のGo Profile/Read cohort/Path Open/Test Event/隠れたDependencyも狭い反例であり、実SEI Methodの能力ではない。外部DSH→TEI実Tool起動とH3のSkill本文Readには観測があるが、OS隔離・Tool Result欠落・独立Expected採点の問題が残り、**TAIのH2/H3比較資格は0/4**。これらを同じ「PASS」として合算しない。

**限定実証 M1R（計画・NOT RUN）**：問いを二つに固定する。 `Q_rule`＝「指定Functionの必要Rule/RelationとSourceが現在読めているか」、`Q_test`＝「依存Source変更後も指定TestのPASSを現在の根拠として使えるか」。Required Source/Rule/Relation/非出力Predicateと独立Expectedは、Method候補を出す側とは別に事前固定する。Product実Readのbyte・mode・scope・revision・観測時点・Resultの欠落と、Consumerが受領したbyte/part/endを区別する（連続するCLI応答の同一Fingerprintだけでは同一Snapshotの証明にならない）。

| 対照 | 認知作業 | 比較の受入 |
|---|---|---|
| D0 | 現在の実観測と独立Requiredを決定的に照合し、不足を明示。追加Readなし | 不足・wrong-mode・unsupported・unknownの適切な区別 |
| D1 | D0に事前固定した一回の追加read-only Probeを加える | 必要根拠への到達、余分なRead、誤った不存在判断 |
| M1 | 同じ初期観測・許可Tool/Mode・開示・Read予算1/2からSEI Methodが次Probeを選ぶ | D1比での必要根拠到達、残余保持、誤断定・漏洩・費用。D1と同じProbeを提案しただけなら固有の改善と数えない |

**次の受入を順序付きで実行する**（既存のTool、独立Oracle、Harness Runbookを再利用）。

1. **M1R-0 Product前提**：現mainのTEI CLIで実SubjectとRequired Ruleをread-only再取得し、11 Replyの各status/Source Indexのsubject・index mode、Loader Read/Source role、未読込と真正不存在を区別する。正常JSONでの欠落・正常な空集合・誤modeを「存在しない」「全部読んだ」へ短絡させない。#3354の結果は歴史的baselineであり、現在の実同版観測を代用しない。
2. **M1R-1 SEIとの接合資格**：まず実在するSEI CLIのRecommendation/Decision/ResumeとCognitive Methodの研究用Referenceを**別々に棚卸し**する。現在のCLIにObservation/Question/Method Applicationの正式なwrite APIが存在すると仮定しない。`Q_rule`または`Q_test`の実受領ReplyとMethod候補・不足根拠を、最初は独立評価票へ保持し、既存Recommendationへ記録する場合も出典と「Method未受理」を明示する。ネイティブMethod Application保存・再開は実契約が確認された後の別Exitとする。架空のCLI/MCP、独自Method正本、新Claim Storeは作らない。
3. **M1R-2 盲検比較**：D0/D1/M1を同じSource/Toolchain/Tool allowlist/Grant/開示・初期観測・予算で行い、独立ExpectedをMethodへ漏らさず、`required reached`、実Reply完全受領、false absence、誤った旧PASS再利用、余分Read、確認負担とコストを別軸で採点する。未受理の業務意味・非開示情報に由来する結論は`unknown`を維持する。
4. **M1R-3 外部利用・再開**：上のProduct-only結果を、TAI [#168の既存Runbook](https://github.com/hat47x/tai-pleroma/issues/168) の隔離・Task固定・H2/H3実提供と独立採点が成立した後に、SEI [#769](https://github.com/hat47x/sei-cognition/issues/769) のProduct Skill候補へ薄く渡す。Tool発見/実Call/実Reply/Skill実Load/Consumer受領/現Grantは別資格。H2/H3の失敗Trialを後付けで選別せず、方法の有益性を断定しない。
5. **M1R-4 再資格化**：Rule/Relation/非出力Predicate、Go Profile/依存Source、Source occurrence、Provider/Policy/現Grant、Consumer投影のうち一軸を変え、歴史的Observationは保持しつつ必要なQだけを再Probe。個別SHA一致やA→B→A、旧PASS、OKFの`verified`/`stable`、SHO/SUIの表示・コピーを現在の意味/公開適格・独立根拠へ昇格させない。OKF適合/知識交換は[SEI #820](https://github.com/hat47x/sei-cognition/issues/820)が担当。

**停止線と引渡し**：独立Requiredがない、実Readのmode/Scope/cohortが不明、Tool結果が途中切断、Consumerの許可投影から主張を識別不能なら、強い不存在・全件性・現在の実行資格のClaimを出さない。ただし許された限定read-only探索まで一律に止めない。ProductのQuery/Source/Plugin/Trait/BOM/Targetの実資格はTEI、独立ExpectedとT1-B未知ObligationはTEI #2514/#3262、外部Harness/OS・送出はTAI #168/#232、Methodの問い・残余・Probe選択はSEI #767、Skillの入口は#769へそれぞれ返す。探索完了／設計受理／Plugin Binding／実Target起動／Effect Receipt／Owner Acceptanceは別段階であり、この計画追加によって自動昇格しない。

**反証可能な成果指標**：同じ前提でD0/D1からM1への改善が無い、誤断定や情報露出が増える、追加確認負担が増える場合はSEI Methodの必須化を見送る。改善が確認できたScopeだけを採用候補にし、一般的な「AIで完全保証」へ拡張しない。本節は実証計画への取り込みであり、M1R-0〜4の新規実行、SEI実Tool接続、Ownerレビューは**NOT RUN**。

### 9.2 横断実証の対象を「正常だが不足」まで広げる（2026-11-08・既存M1Rへ追加）

**今回確定できる設計差分**：単なる失敗・エラーだけでなく、**正常に返ったが問いQに必要な情報を含まない応答**を、SEIが「真正不存在」「未取得」「別のScope」「別の型」「未検証」「非開示」に分けて説明できる必要がある。SEIは個別CLIのReaderやSchemaを複製しない。各Productの実Consumerが確認済みのResponseとその条件を受け、問い相対の不足・次のProbe候補を選ぶ。M1R-0〜4の順序と責務分担を維持し、横断事例を新しい共通Gateにはしない。

#### 9.2.1 同じ「成功」を五つの資格に分解する

| 資格 | 必要な独立観測 | SEIがしてはいけない昇格 |
|---|---|---|
| **S：Source / Design取得** | 必要なID・Role・Rule・Relation・Source occurrence、実Loader/Parser Read、Scope・Revision・mode、Requiredとの比較 | 出力に見えない項目や未探索領域を「不存在」とする |
| **B：Binding / Capability** | Plugin能力の宣言、環境への選択、実Provider identity、Build/Load、実Invocationを個別に照合 | Capabilityがselectedなら当該Providerが実際に使用されたと推測する |
| **T：Transport / Consumer受領** | Tool Request/Responseの対応、raw byte/分割順序/終端、stdout/stderr/exit、Consumerによる実Read | Product側でJSONが成立しただけで外部Harnessへの完全受領とする |
| **G：Generation / Evaluation** | 独立Required・Expected、実実行Step Receipt、判別したMutant・未知Obligation、局所Coverageと全体Coverageの別分母 | 既知のStepがPASSしただけで未知Ruleも検証済みとする |
| **A：Authority / Effect** | Ownerの意味受理、現時点のHost/Provider Grant、Effect Receipt、Consumerへの許可投影、必要に応じたOutcome | Method候補・旧Decision・OKF/SHO文書・生成Artifactを実行資格へ昇格する |

この五分解は**試験票の見方**であり、新しいProduct共通Schemaや正本ではない。SEIのInquiryは用途に必要な欄だけを要求し、観測不能な欄はunknownとして残す。さらに「個別Sourceが同じSHA」「各ReplyのFingerprintが一致」「Readerが成功」は、複数Readの共同成立や現在のGrantを自動保証しない。

#### 9.2.2 既存実装から導く最小の判別事例

| ケース | 公開の根拠／担当Owner | 次Probeでの正しい区別・停止線 |
|---|---|---|
| **H3-X01 正常Arrayと応答欠落** | TEI [#3347](https://github.com/hat47x/tei-platform/issues/3347)・[#3370](https://github.com/hat47x/tei-platform/pull/3370)。`requirements.result`は配列、未宣言の他Command shapeはunknown | `result:[]`を正常な空配列として受けることと「Requiredに当たるものが存在しない」は別。実版と`resultShape`の実宣言を照合し、全Commandをobjectへ統一しない |
| **H3-X02 Source Indexの取得mode** | TEI [merged #3354](https://github.com/hat47x/tei-platform/pull/3354)、[#3262](https://github.com/hat47x/tei-platform/issues/3262)。subject/indexは異なる取得範囲 | subject-modeで見えないRuleを「削除された」と断定しない。必要Rule3件など独立Requiredに対し実index-mode/Loader/Definition/Canonicalを照合する |
| **H3-X03 表示とLoaderによる実意味読取** | TEI [#3356](https://github.com/hat47x/tei-platform/pull/3356)。`view.semanticFingerprint`の範囲と管理Markdownの`readByLoader:false` | Viewの局所指紋をWorld全体の指紋に転用せず、管理文書が存在することをParser/Meaning消費と扱わない。必要なら実Loaderへ戻る |
| **H3-X04 局所PASSと全体未観測** | TEI [Draft #3365](https://github.com/hat47x/tei-platform/pull/3365) のTT-105/106（限定exact-head CIの履歴） | 受信済みStepの局所正証人を保持し、途中欠落・部分目録から別Stepの`untested`を確定しない。全Product Coverageはunknownのまま。T1-Aと盲検T1-Bを別採点 |
| **H3-X05 Plugin選択と実呼出し** | TEI [#3363](https://github.com/hat47x/tei-platform/pull/3363) 参照Workspaceの24 Binding＝22 selected、2 missing／[Draft #3371](https://github.com/hat47x/tei-platform/pull/3371) | `missing`2件は検証器の検査範囲外を含み、直ちに欠陥ではない。selected≠Provider実装≠Build/Load≠実Invocation。CLIとStudioで選択Provider B・実呼出Aの食い違いをTEI Ownerが実試験する |
| **H3-X06 Queryの非表示依存** | TEI [#2586](https://github.com/hat47x/tei-platform/issues/2586)／[#2634](https://github.com/hat47x/tei-platform/issues/2634) | `Function→Query→選択SQL/Bind→Provider実Read→Rowset→Context→Claim`のうち未観測Edgeを列挙。空Result/表示列一致を`NOT EXISTS`、全母集団、同一Read cohortへ昇格しない |
| **H3-X07 Harness実受領の欠落** | TAI [#168](https://github.com/hat47x/tai-pleroma/issues/168)／TEI [#2509](https://github.com/hat47x/tei-platform/issues/2509)。実Tool起動とH3 Skill本文Readerの観測はあるが、比較資格は0/4 | Request対Reply欠落、8,192-byte切断、Skill未露出・実Loader Read、隔離と独立Expectedを別評価。正常終了や最終回答をDelivery完備としない |
| **H3-X08 二次表現と独立根拠** | SEI [#820](https://github.com/hat47x/sei-cognition/issues/820)／SUI [#3397](https://github.com/hat47x/sui-sensemaking/pull/3397)／SHO [#21](https://github.com/hat47x/sho-composer/pull/21) | コピーMarkdown354 byte、Parser成功、link数0、OKF `verified/stable`を原典独立数・Meaning完全性・Owner受理に変換しない。同一一次Sourceの派生を独立投票へ加算せず、原資料の到達条件を残す |

各ケースは既存Productが所有する**限定Evidenceまたは提案済み負例**をM1Rの判別材料として参照するものであり、表の全件がSEI Methodで実行済みという意味ではない。対象Productの版・実Response・実受領条件を再取得したうえで、必要な一件のみをまず実連結する。

#### 9.2.3 最小比較の観測票と非対称な停止

M1R-2で最初に扱うのは **H3-X02（Rule/Source Index mode）** の一件とし、独立Requiredを変更しない。D0・D1・M1が同じ初期Tool Replyと同一の許可されたTool一覧・Read予算を受け取り、D1が事前固定の追加Read、M1がMethod選択の追加Readを提案する。各Trialは**同じ条件で実際に呼び出されたToolの結果**を収集し、次を別々に評価する。

1. 正しい`mode`へ達したか、Required Rule/Sourceを実際に確認できたか、取得できない場合に`wrong-mode / not-loaded / unknown / unsupported / withheld`を取り違えなかったか。
2. Tool呼出し・実Response・Consumer完全受領の三段階が揃ったか。独立Expectedに対して局所結論が正しいか。未観測を虚偽の不存在や未テスト確定へ変換しなかったか。
3. 機密なSource path・件数・隠れたAction名・内部Probe選択理由を、許可された外部Viewへ漏らさなかったか。二つの内部世界が同じ公開Viewなら、許可されない差分が外部の質問候補・Tool Traceへ現れないか。
4. 余分なRead、実際に受領したtoken/byte、時間、人の確認負担を別計測する。M1がD1と同じProbeを提案し性能差を示さなければ、追加のMethod必須化を正当化しない。

**局所的な正の証人は保持し、強い否定/完了の主張だけを止める。** たとえば既知Ruleを実Readした事実は維持し、残るFunction全件・未探索のRule・別Consumerへの公開資格はunknownとする。Probe候補を提案できることは、実Tool利用・Productの現在Grant・最終Decision採用とは違う。

#### 9.2.4 Ontology／SUI／REA／KONへの拡張は現在のBlocking条件にしない

[TEI #3475](https://github.com/hat47x/tei-platform/issues/3475) のOntology DSL／型付きSDK／Decision Twin／SEIへの判断移譲は**長期構想**として参照する。現段階の設計上の境界として、SUIは観測・素材・探索候補、TEIは意味構造/型/Rule/Provider契約、SEIは問い・根拠照合・判断候補/保留、SHOは文書・説明、Host/Provider/EKIは現実の権限・Effect/配送（各製品の責務内）を分離する。

将来のInquiryであっても `Observation→Structural Candidate→Accepted Meaning→Decision→Grant→Effect→Outcome` を黙って昇格させない。REAからの逆解析やSUI探索の情報は、TEIの正式意味を直接確定しない。OntologyにおけるEntity/Relation/Stateの`same ID`・`same Projection`・`same revision`から、実世界の同一対象/意味同一性を推定しない。KON Dataspaceは任意の将来データ交換候補であり、SEI Method・TEI CLI・現在のread-only試験の必須依存にしない。OKFは知識交換契約であって第二のDecision Storeや実行資格ではない。

**優先順位**：今実行可能なのは既存Data/Role/Sourceのread-only Fit/GapとH3-X02最小実連結まで。TEIの全体セルフビルドとSUI基本機能完成前にDigital Twin/Simulationの実装・外部DecisionメッセージングをM1RのBlocking Exitへ追加しない。対象の新しいDSL構文・共通Host/Registry・SEIが自動承認するAuthorityをここで採用しない。外部計算・予測・神経応答的な局所即応は、将来各Productの独立適格性とOwner判断を要する別段階とする。

**今回の変更範囲**：`§9.1`にある実Read→Method→D0/D1/M1→Harness・再資格化の順序は維持。上記は既存Evidenceの比較受入と長期構想との境界を追加した計画のみ。H3-X01〜08のSEI本体での新試験、M1R-0〜4、実Plugin Invoke/物理DB、実H2/H3完全受領、正式Ontology SDK/Decision Handoff、人間の判断評価・Owner受理は**NOT RUN**。

### 9.3 実在するSEI CLIを起点にした最小の接合と、認知Methodの対照試験（2026-11-08・計画の収束）

**実装可能性についての訂正**：[SEI #711](https://github.com/hat47x/sei-cognition/issues/711)と現mainの[`sei` Quickstart](https://github.com/hat47x/sei-cognition/blob/main/runtime/go/cmd/sei/QUICKSTART.md)を照合すると、現在の`sei add`/MCPが正式に書けるのは**RecommendationとDecision**である。Observation / Interpretation / Questionをネイティブ記録として書く経路はなく、Method Applicationを正式に保存・再開するCLIの実在証拠もない。 `sei resume --json`の`basis_references`や`snapshot_digest`は**保存束内の参照表現・読取り指紋**であり、TEIのSourceの現在性・実物到達や業務Meaningを確認したことにはならない。SEI #711で当該記録責務はOwner未決であり、製品側に架空のMethod Storeを作ってはならない。

**したがってM1Rは次の二つを別資格で進める。**

- **M1R-A：今ある製品を使う限定Read/Resume試験**。TEI [#3354](https://github.com/hat47x/tei-platform/pull/3354) で使われた既存CLI（`tei source-index -workspace reference/workspace -subject-kind semantic-data -subject-id sales.order` と、`tei source-index -workspace reference/workspace`）による**subject/index両mode**の実Replyを、Source/CLI Revision・raw byte・mode・Independent Requiredとともに取得。既存TEI Context Gateの確認済みResultを参照し、新たなParser/Index Readerは作らない。SEIの実`sei add recommendation`を利用するとしても、それは**Methodの調査提案を表すRecommendation**に限る。原TEI Replyのbytesと固定の根拠比較票はSourceを保持する側に残し、SEIの`sei resume --json`で推薦/未決の表示範囲と原記録への戻り先を検証する。RecommendationをObservation・正式Decision・Method Applicationに読み替えない。
- **M1R-B：認知Methodの追加価値試験**。[SEI #767](https://github.com/hat47x/sei-cognition/issues/767) の既存研究Referenceを、最初はProduct外の**候補選択/残余説明**として利用し、D0（決定論的不足表示）／D1（あらかじめ決めた追加Read）／M1（Methodが選ぶ追加Read）で比較する。M1R-Aのactual Raw Replyを同じ初期観測とし、Tool allowlist・同一Scope/版/権限/調査予算・独立Expectedを固定する。Methodが提案しただけのProbeと、現に実行したTool・結果をConsumerが受領した事実を分ける。**ProductへのネイティブMethod接続は、実在するContract/CLIを確認するまで達成と呼ばない**。

**H3-X02の評価上の位置づけを修正する**：既存index modeへの切替でRequired Ruleが確認できる合成/公開ケースは、決定論的D1が解ける**陰性対照（Method不要が妥当な例）**とする。M1が同じProbeを提案しても独自価値を加点しない。H3-X06のような非表示依存や、曖昧なProvider/Source選択の実観測へ進むには、TEI [#2586](https://github.com/hat47x/tei-platform/issues/2586) の`Function→Query→DB Binding→実Provider Read`が実接続した証拠が必要であり、未接続の間は仮説として保持する。失敗例を増やすこと自体をKPIにしない。

**最初の一件の受入票（同一Attemptで記録、件数ではなく到達を検収）**：

| 欄 | 必要な観測 | 未確認なら |
|---|---|---|
| TEI実物 | pinned Source/CLI版・実Workspace Root、subject-modeとindex-modeの実stdout原byte/SHA、exit、schema、mode、Source Index/Loader Scope | `source-bound=unknown`。旧CIを今のRunへ転用しない |
| 対象の必要性 | 独立Required Rule/Relation/Sourceと実取得した定義・Source occurrenceを区別 | 不足原因を`wrong-mode / not-loaded / unobserved`へ分け、`not exists`を主張しない |
| SEI入口 | 実`sei`版、使った`add recommendation`・`resume --json`のraw Reply、元Storeのsnapshot digest、対象の論理/Exact basis | `recommendation-only`または`not-run`。保存束内の参照はTEI原証拠の実到達を保証しない |
| Method追加価値 | D0/D1/M1の割付、同一Input/Toolと必要Probe、実Read・Reply受領・Independent Expected、余分なRead/コスト | Method固有改善は`not-established`。false absence/開示リスクを別判定 |

**開始順序と停止線**：まず一件のM1R-Aを実行し、`SEIの実Recommendation/Resumeで「実TEI観測から提案を保存・再開できる範囲」と「Question／未決として正式には保存されない範囲」をどこまで正確に区別できるか`を限定検証する。そこでSEI CLIの記録種別やbasis解決に不足があれば、既存#711/#678へ事実を返し、仮のObservation/Question保存APIを新設しない。そのうえで同じ実TEI根拠をM1R-Bへ再利用する。外部H2/H3・SUI→SHO実受渡し・正式Decision handoff・Plugin実Provider/Host・Ontology SDKは、ここでの最初のBlocking条件に加えない。**この§9.3は要件・実行順序の精密化であり、新しいCLI/SEI Product Method/二製品E2E/Owner受理の実証ではない。**

### 9.4 M1R-Aの実装監査：Recommendation保存はInquiry/Unknownの永続化ではない（2026-11-08）

§9.3の「既存CLIで提案・未決を保存する」は、現行コードに対して**提案の保存と未決の保存を分けて読む必要がある**。以下は現在の[`runtime/go/seicli/seicli.go`](https://github.com/hat47x/sei-cognition/blob/main/runtime/go/seicli/seicli.go) の`runAdd`／`BuildResume`／`runResume`と[`runtime/go/cmd/sei/QUICKSTART.md`](https://github.com/hat47x/sei-cognition/blob/main/runtime/go/cmd/sei/QUICKSTART.md)から直接確かめた実装境界であり、**新しい実バイナリ実験のPASSではない**。

**コード監査による具体的な境界**

1. `sei add recommendation`の現行フラグは`--id`/`--statement`/`--rationale`/`--source`/`--basis`/`--responsible`。**`--unresolved`はDecisionでのみ定義**され、Recommendationには存在しない。観測結果が曖昧なことをRecommendationの`rationale`へ記述できても、型付きQuestion/Unknownを保存したとは言えない。
2. `BuildResume`の`Unresolved`は認識済み**Decision**の`UnresolvedRefs`だけから構成される。`recommendations_not_yet_relied_on`（出力名は既存JSONの実版に従う）は**未採用の推薦**であって、**未解決の質問一覧ではない**。RecommendationだけのStoreで`unresolved`が0でも対象案件に未決が無いとは言えない。`coverage.case_completeness=not_assessed`の停止線を維持する（[#678](https://github.com/hat47x/sei-cognition/issues/678)）。
3. CLIの`--basis`は`kind:id`の参照を受け取るが、実TEI Sourceのbyteや現行Meaning/Scope/Providerを自動取得・検証しない。`--source`はCLI呼出者が指定した**出所ラベル**であり、署名済みの実Tool ReceiptやOwnerの身元保証ではない。`basis_references`の保存・表示を元資料の独立根拠として計数しない（[#710](https://github.com/hat47x/sei-cognition/issues/710)、[#711](https://github.com/hat47x/sei-cognition/issues/711)、[#820](https://github.com/hat47x/sei-cognition/issues/820)）。
4. `sei resume --json`の`snapshot_digest`はSEI **Store bundleの実Read bytes**の指紋であり、TEI Workspace/CLI binary/Read-setのDigestとは別。原記録へ戻る`sei resume --json --record-id <ID> --snapshot-digest <DIGEST>`は同じ保存束なら原記録を取得するが、外部TEI Sourceの再取得やGrantの確認はしない。Store変更後の古いDigestは読み直しが必要。人間表示ではRecommendationの`rationale`は原則省略され、JSON側に残る。
5. `sei mcp --read-only`が公開するのは`resume`だけであり、`add_recommendation`は使えない。通常MCP起動はRecommendation追加に加えて`check_decision`を公開し、後者は監査ログを書き込むためread-onlyとは言えない。**TEIのread-only Probeと、隔離されたSEI Storeへの記録Write、AIへ公開するTool集合を分離**する。外部H2/H3では既存TAI #168/#232の実物理隔離・送出計測を先に満たす。

**M1R-Aの実行可能な最小手順候補（コマンドの存在をコードで確認、Trial自体はNOT RUN）**

```text
1. TEI実CLIの同一Pinned workspace/root/subject/revisionで
   source-index subject-mode と index-mode を取得する。
   実argv、stdout raw bytes、exit、Tool結果・SourceのDigestを製品側で保持。

2. 実行対象と切り離した一時Working Directoryで sei init。
   sei add recommendation --id R-h3-index-mode
     --statement "<許可された事実と次の確認提案>"
     --rationale "<観測された根拠不足と確認条件>"
     --basis semantic-data:sales.order --source tei-cli
   ※basis/sourceは未検証の文字列参照。実TEIのRead証拠と突合したとは扱わない。

3. sei resume --json の実Responseを保存・再読取。
   推薦のstatement/rationale/basis/record出所が保持された範囲を確認。
   未解決一覧が空でもInquiryの完了とは判定しない。

4. snapshot_digestを固定して同じrecord_idの原記録を取得。
   別Revision/Store更新後は旧digestの失効を確認。
   SEIのStore bundle DigestとTEIのSource/Binary Digestsを混同しない。

5. External Harnessへ引き渡す場合は、Toolの実ロード/許可/実Reply
   完全受領、実隔離、公開可能な説明を別に検収する。
```

**有限の受入対照（独立Expectedは実Runtimeの`resume`から生成しない）**

| ID | 入力／操作 | 独立Expectedと止めるClaim |
|---|---|---|
| A-01 | TEI subject-modeには必要Ruleが不足、index-modeには独立Requiredがある | 正しい取得modeを診断。欠落≠Rule不存在。既存TEI #3354のReadと比較する |
| A-02 | Recommendationのみを保存して`resume --json` | 推薦の存在は肯定できるが、型付きQuestion/Unresolved保存とは判定しない。未決0件≠未決なし |
| A-03 | `--rationale`に不足根拠、`--basis semantic-data:sales.order`を記録 | JSONには説明と参照ラベルが残り得るが、TEI Sourceの実Read/SHA/現在資格は未検証。人向け表示のrationale欠落を別評価 |
| A-04 | `--source tei-cli`と異なる自己申告Sourceラベルを比較 | 出所名は識別子の記録であって実Tool/人の身元認証ではない |
| A-05 | Storeへ追加記録した後、旧`snapshot_digest`による原記録読出し | 旧Digestの適用を拒否し、履歴指紋一致≠Source/Grant現在有効とする |
| A-06 | `sei mcp --read-only`と標準起動のTool exposureを比較 | read-onlyでは`add_recommendation`を実行不可。通常起動の`check_decision`効果も独立評価。外部情報送出と実OS隔離は別試験 |
| A-07 | Methodが同じindex-mode Probeを提案、D1も同じProbeを固定選択 | D1/M1の同じ結果にMethod固有改善を加点しない。追加価値が無いならMethod必須化を見送る |

**優先順位とOwner引渡し**：まずA-02〜04の**実SEIバイナリ・一時Store**で保存・Resume表示を独立Expectedに対して確認し、次にA-01の実TEI Sourceへ結び、A-05〜07へ進む。TEIのSource/必要Rule/意味と実バイナリはTEI #3262/#2516、SEIの記録種別・参照の意味はSEI #711/#678、Method選択の効果はSEI #767/#450、外部Toolと送出はTAI #168/#232がOwner。A-02で未決の意味保存が不成立なら、**適格なRecommendation保存までを肯定し、Inquiry持続性・Method ApplicationのProduct実結合は未成立として止める**。失敗を隠すために偽のDecisionを新設したり、既存Decisionの`unresolved`を書き換えたりしない。

**未実施**：A-01〜07の新規Trial・GitHub Actionsによるexact-head CI・独立SEIビルドとTEI同一Attempt二製品受領・外部OS/Network隔離・Method Application正式保存・人のOwner受理は**NOT RUN**。本節は現行の実コードの監査結果と反証可能な受入計画に限る。第二Store/Parser/Index/Hostを追加しない（隔離したSEI試験用Storeは既存Product機能として用いる）。

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

2026-10-02には、ADR-0035（Proposed）とISSUE-000085〜000088による家族の統合の頂点の提案を、work laneの表へ一行加えました。これは所有者のレビュー待ちの提案であり、他のlaneのEvidenceを代用しません。

各laneは互いのEvidenceを代用せず、上流価値、Inquiry Continuity、Decision-centered Product Interaction、Application implementation strategy、Provider portabilityという異なる未知を減らします。

今回の更新では、ISSUE-000077のResolutionとactiveなfollow-up探索の分離を現在地へ合わせました。ブランド世界の詩的な豊かさと、SEIのProduct governanceが要求するauthority / Evidenceの厳密さをどちらも削らず、背景から価値仮説、Discovery Reviewの結論、follow-up実証、下位設計へ降ろさない停止線、現在のwork laneまでが自然につながるように再読し、**自然な日本語となることを最重要視したうえで、意味、規範強度、current Evidence、未検証範囲が変わっていないことを最終監査しました。**