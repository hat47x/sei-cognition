# SEI Product Interaction

更新日: 2026-09-11  
状態: **Current Product Interaction Baseline / Resume-first first usable slice defined / Scoped prior Executable Evidence available**

## 1. この文書の役割

この文書は、SEIを人間とAIが製品として扱うとき、**どの仕事を、どの意味境界を保ったまま行える必要があるか**を定めます。

ここで定めるのはWeb画面、desktop framework、CLI構文、HTTP endpoint、MCP tool名ではありません。UIやprotocolより先に、利用者が何をできる必要があるかと、その操作がどのcanonical meaningへ接続するかを定めます。

```text
Product Interaction
  = usable work operations over canonical meaning
  != UI layout
  != chat transcript
  != workflow state machine
  != agent orchestration
```

SEIのProduct Interactionは、`SEI_PRODUCT_SHAPE.md`のWork / Interaction Surfaceを具体化するProduct-level baselineです。portable semantic agreementが必要になった場合だけContractへ、重要なArchitecture判断はADRへ、実装方式はRuntime / Adapterへ落とします。

詳細な最初のProduct Sliceは`SEI_FIRST_USABLE_PRODUCT_SLICE.md`、そのArchitectureは`../../architecture/SEI_INTERACTION_WORKING_SET_ARCHITECTURE.md`を正とします。

## 2. Interactionで守る中心

人間とAIに同じ見た目を与えることは要求しません。入口や表現が異なっても、**同じcanonicalな判断文脈へ戻れること**を要求します。

```text
human view != AI view
human view -> canonical meaning
AI view    -> canonical meaning
```

画面、会話、prompt、worklist、canvas、CLI出力等はProjectionになり得ますが、意味上の唯一の正本にはしません。

特に次を守ります。

- 人間向けUIだけにDecisionやUnknownの意味を閉じ込めない。
- AI向けpromptやconversation historyだけにObservationやRecommendationの意味を閉じ込めない。
- Projectionを作り直してもcanonical artifactを失わない。
- AIのprivate chain-of-thoughtをInteraction成立条件にしない。
- actorが人間かAIかだけからAuthority / Responsibilityを推定しない。
- 低影響な仕事へ最大詳細を強制せず、必要なときだけ詳細へ降りる。
- AI suggestionを明示的なsemantic commitなしにDecision / canonical factへ昇格させない。
- current informationをhistorical Decision basisへ遡及混入させない。

## 3. 新しいUniversalな「作業単位」は追加しない

最初のInteractionを実装するためだけに、`Case`、`Session`、`Workspace`、`Thread`等をUniversal Coreへ追加しません。

利用者が画面上で一件の「案件」や「作業」を開くことはありますが、そのまとまりはProduct / Projection上のworking setとして扱えます。耐久的意味は既存のInquiry、Observation、Unknown / Conflict、Cognitive Method Application、Recommendation、Decision、Responsibility、Reference、Lineage等へ置きます。

```text
workspace / session / thread / working set
  = interaction convenience
  != automatically a Universal semantic entity
```

複数domainで独立したsemantic necessityが実証された場合だけ、Requirement / ADRを通して再検討します。

## 4. 利用者が行う最小の仕事

first usable interactionでは、少なくとも次を自然につなげられる必要があります。これは固定workflowではなく利用可能な操作分類です。

### 4.1 始める・開く

問い、目的、短い文脈など、現在分かっている最小限からInquiryを始めます。

既存の判断仕事を開き直し、当時basis、Unknown / Conflict、残差、reopen condition等から続きを始められます。

最初から最大field setを要求しません。

### 4.2 情報を加える

人間、AI、外部Provider等から得たObservationやEvidenceを追加できます。

Source、discovery route、Interpretation、EvidenceUse等を区別する必要がある場合は後から詳細化できます。

### 4.3 分からないこと・食い違いを残す

Unknown、Conflict、保留事項を「入力不足」として消しません。

Decisionが作成されても、未解決事項を自動的にresolvedへしません。

### 4.4 方法を適用する

必要な場合、調査、比較、統合、検査等に用いたCognitive Method Applicationを記録できます。

Prompt、人間手順、外部tool等のRealizationが変わっても、必要なinput / output / residualをcanonical meaningへ戻せることを優先します。

### 4.5 提案する

人間またはAIはRecommendationを追加できます。

Recommendationの存在だけでDecision、Authority、Executionが成立したことにはしません。

### 4.6 決める

必要な主体はDecisionを記録できます。

案件に応じてbasis、主要Constraint、未解決事項、Responsibility等を必要な粒度で残します。高影響な判断で必要な意味をlight viewの都合だけで削りません。

### 4.7 実行後の結果を戻す

外部Capability / Providerで実行した結果を、新しいObservationとして判断文脈へ戻せます。

実行成功をDecisionの正しさへ自動変換せず、実行後のObservationを過去Decisionのbasisへ混ぜません。

### 4.8 読み直す・再開する

lightなResume Projectionから現在地を把握し、必要なときだけaudit detailへ降ります。

後日、新しいEvidenceや環境変化が生じた場合は過去Decisionを削除せず、残差や新しいObservationからreview / Inquiryを再開します。

## 5. Resume-first first usable slice

2026-09-11時点では、PMS-03を次へ進める最初のProduct Sliceとして**resume-first decision work**を採用します。

中心価値は「semantic recordを作れること」ではなく、時間・AI session・画面stateをまたいだ後でも次へ戻れることです。

- 何を考えていたか。
- 何をDecisionしたか。
- なぜそうDecisionしたか。
- 何がまだUnknown / Conflictとして残るか。
- 何がDecision後に変わったか。
- どの条件でreview / reopenすべきか。

再開時のResume BriefはProjectionであり、新しいcanonical summary Contractではありません。

AIを利用する場合、responseはまずprovisional suggestionとして扱い、意味変更previewを経てcanonicalへcommitします。AIが停止してもopen / read / manual add / Decision / review / reopenは継続できることを目標とします。

詳細なCandidate Requirement、prototype scenario、human reviewはISSUE-000073と`SEI_FIRST_USABLE_PRODUCT_SLICE.md`で扱います。

## 6. light viewとaudit detail

日常利用ではcanonical recordの全fieldを常時表示しません。

light / resume viewでは、案件に応じて次を優先します。

- 現在の問い / goal。
- current Decision。
- 主要なbasis。
- Unknown / Conflict / residual。
- Decision後に変わったこと。
- review / reopen候補。

これは固定Contract field listではありません。

必要な場合、audit detailから次へ降りられる余地を持たせます。

- Decision basis
- Provenance / discovery / derivation
- Responsibility / Authorityに関わる文脈
- Revision / Semantic Lineage
- Exact Bindingが必要な可変Artifact
- Unknown / Conflict / withheld等の認識状態
- Cognitive Method Applicationの主要input / output / residual

```text
light / resume view
  != incomplete canonical storage

audit detail
  != separate source of truth
```

## 7. 人間向け入口

人間向けSurfaceではsemantic modelの型名を覚えなければ使えない製品にしません。

「問いを始める」「情報を加える」「分からない点を残す」「提案を見る」「決める」「後で読み直す」といった自然な仕事を前面に出し、裏側でcanonical artifactへ接続します。

分かりやすさのためにRecommendationとDecisionを一つの「回答」へ潰したり、Unknownを空欄として捨てたりしません。

## 8. AI向け入口とprovisional boundary

AI向けSurfaceは、人間向け画面を画面操作させることを必須にしません。必要なcanonical contextを構造化して読み、許可された操作を通してObservation候補、Method Application、Recommendation候補等を作れます。

AI向けSurfaceは次を守ります。

- Projectionからcanonical referenceへ戻れる。
- 何をObservation / Recommendation / Decision等として記録するか明示する。
- private chain-of-thoughtを要求しない。
- AIであることだけからAuthorityを付与しない。
- human UIだけにある隠れた意味へ依存しない。
- AI response受信だけではcanonical writeを完了しない。

first sliceではAI responseをprovisional suggestionとして受け、Semantic Change Plan相当のpreviewを通してcommitする方向を検証します。

protocolはHTTP API、MCP、local process、SDK等を候補としますが、本baselineでは固定しません。

## 9. Human / AI parity

Human / AI parityは同一UIではなく、次を意味します。

1. 同じcanonical artifactを参照できる。
2. 同じ意味上の区別を失わない。
3. 一方がcommitした耐久的意味を他方が再読できる。
4. 一方にしか存在しないconversation / screen stateをhistorical reconstructionの必須条件にしない。
5. actor kindからAuthority / Responsibilityを自動推定しない。

入力支援や表示形式が異なることは許容します。

## 10. 論理操作境界

protocol名やfunction名を固定せず、実装が少なくとも次の仕事を表現できることを求めます。

```text
start / open
read resume / light projection
read audit / structured projection
add observation / evidence
record unknown / conflict
record method application
record recommendation
record decision
return resulting observation
review history / reopen
```

これらはUniversal workflow stateではありません。

first sliceではさらに、AI suggestionの`review / edit / dismiss / commit`と、stale draft / commit failureの明示的なfailure behaviorをProduct Operationとして検証します。

## 11. protocolとUI

Web UI、desktop UI、CLI、HTTP API、MCPのいずれも恒久的Product標準として確定していません。

ISSUE-000053ではGoのreference probeとしてhuman-oriented入口とmachine-oriented入口を同じevaluation-only CanonicalStoreへ接続し、Surface間の意味共有をScoped Executable Evidenceとして確認しました。

```text
reference probe surface
  != supported production surface decision
```

ISSUE-000073ではhuman usabilityをactualに観測するため、Local Single-Node Go runtimeにlocal browser UIを組み合わせる構成をfirst prototype候補とします。これはhuman reviewを速く回すためのRealization選択であり、Web UIをUniversal Requirementにしません。

## 12. Requirement / Acceptance監査

Interactionの主要境界はcurrent Requirementで表現できます。

- REQ-0001 — 技術やUIが変わっても意味を引き継ぐ。
- REQ-0005 — Decisionを後から再構成する。
- REQ-0006 — Recommendation / Decision / Authority / Executionを分ける。
- REQ-0010 — 低影響案件へ最大詳細を強制しない。
- REQ-0011 — Projectionを意味上の正本にしない。
- REQ-0014 — 残差と再開条件を保持する。
- REQ-0015 — private chain-of-thoughtへ依存しない。
- REQ-0019 — 人間とAIの双方が意味を読める。

SCN-0003、0013、0016、0018もresume-first sliceの主要Scenarioです。

ISSUE-000073では、canonical-only resume、meaning-preserving multi-record commit、stale-write protection、external AI context boundary等をCandidate Requirementとして検証します。prototype / human review前にStable REQ IDを追加しません。

## 13. 既存Executable Evidenceと新しいEvidence gap

`runtime/go/interactionprobe`では、HumanSurface / MachineSurfaceの同一canonical source利用、minimal start、Recommendation / Decision分離、Unknown / Conflict保持、light / audit Projection、post-decision Observationによるhistorical basis非改変、Surface-local state非権威性等をactual testとして確認済みです。

これは重要なScoped Executable Evidenceですが、次は未検証です。

- context loss後のactual human orientation。
- canonical-only resumeのProduct Experience。
- AI suggestion correction / dismissalの操作負担。
- AI unavailable時のgraceful degradation。
- multi-record commit fault injection。
- stale draft conflict。
- external AI context egressのinspection。

```text
interaction probe PASS
  != resume-first Product Slice proven
  != production UX proven
  != Adoption / Outcome proven
```

## 14. 現時点で決めないこと

- Web / desktop / CLIの正式human-facing surface。
- HTTP / MCP / SDKの正式machine-facing surface。
- team / tenant / workspaceのformal model。
- production Storage / concurrency mechanism。
- semantic change planのportable Contract化。
- production impact-level policy。
- autonomous agent orchestration / workflow engine。
- external AI vendor / model。

これらはISSUE-000073等のactual Evidenceから必要性を再評価します。

## 15. Evidence状態

- Product Interaction Design Evidence: **Established**
- Existing reference-probe Executable Evidence: **Scoped Evidence available**
- Resume-first Product Slice Design: **Established**
- Resume-first prototype Executable Evidence: **Not Yet Verified**
- Human usability Evidence: **Not Yet Verified**
- Operational Evidence: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

## 16. 関連文書

- `SEI_FIRST_USABLE_PRODUCT_SLICE.md`
- `../definition/SEI_PRODUCT_SHAPE.md`
- `../roadmap/SEI_PRODUCT_MILESTONES.md`
- `../../architecture/SEI_INTERACTION_WORKING_SET_ARCHITECTURE.md`
- `../../requirements/PRODUCT_REQUIREMENTS.md`
- `../../requirements/ACCEPTANCE_SCENARIOS.md`
- `../../runtime/INTERACTION_PROBE_EVIDENCE_2026-09-01.md`
- `../../plan/issue/ISSUE-000045-define-first-usable-product-interaction-boundary.md`
- `../../plan/adr/ADR-0028-product-interaction-canonical-operation-boundary.md`
- `../../plan/issue/ISSUE-000053-materialize-first-product-interaction-reference-probe.md`
- `../../plan/issue/ISSUE-000073-define-first-usable-resume-first-product-slice.md`

## 17. Natural Japanese review

Product Value、Product Shape、PMS-03、current Requirements / Scenarios、ADR-0028、Interaction reference probe、ISSUE-000073のProduct / Architecture Designを照合し、Interaction baselineを2026-09-11時点へ再構成した。

従来の「複数Surfaceから同じcanonical meaningへ戻れる」という基礎を維持しながら、次のProduct Valueとして「文脈を失った利用者が判断仕事へ戻れる」resume-first sliceを加えた。Resume Briefやworking setを重要なProduct構造として扱いつつ、新しいUniversal authorityにはしていない。

AIについてはprivate reasoningの保存や自動Decision化ではなく、provisional suggestion、修正可能性、meaning preview、graceful degradationを重視した。既存probeのPASSをhuman usabilityへ拡大解釈せず、partial / stale write等の新しい候補境界をStable Requirementへ先取りしない停止線も維持した。

意味、要求強度、Evidenceの高さ、未決事項を固定したうえで全文を自然な日本語として再ドラフトし、最終意味監査を実施した。