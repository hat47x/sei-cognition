# ISSUE-000073: resume-firstな最初の実用Product Sliceを定義・実証する

Status: **Open**  
Priority: **1**  
Related ADRs: **ADR-0005, ADR-0010, ADR-0028, ADR-0029**  
Updated: 2026-09-11

## Goal

PMS-03の「first usable Product Interaction」を、意味境界のreference probeから一段進め、**一人の利用者が時間・AI session・画面stateをまたいでも、一つの判断仕事へ戻り、過去を捏造せず続きを始められる最初の実用Product Slice**として定義・実証する。

このIssueはUIを作ること自体をGoalにしない。Product Value側で定義したcross-axis Product Outcomeである**Decision Continuity（判断継続性）**を、actual prototypeとhuman reviewで反証可能にすることをGoalとする。

利用者が再開時に少なくとも次へ戻れることを中心に置く。

- いま何を問い、何を目指しているか。
- すでに何をDecisionしたか。
- そのDecisionは何をbasisとしていたか。
- 何がUnknown / Conflict / residualとして残っているか。
- Decision後に何が変わったか。
- どの条件でreview / reopenすべきか。
- 次に確認する価値が高いものは何か。

Design baselineを整えただけではResolvedにしない。canonical-only resume、AI suggestionのprovisional境界、意味変更preview、AI unavailable時のgraceful degradation、stale write / partial commitのfailure behaviorをprototypeで検査する。さらにhuman reviewでは、SOZAだけを評価するのではなく、raw chat / chronological note等の単純な代替手段との比較を行い、**SOZAの追加構造が本当に再構成負担・誤帰属・AI correction負担を減らし、その価値がcapture / review overheadを上回るか**を確認する。

## Background

SOZAはV1 Historical Reconstruction、V2 Semantic Separation、V3 Revision Integrity、V5 Uncertainty Preservation、V6 Human / AI Readability、V7 Progressive Explicitnessを持ち、V4 Provider IndependenceとV8 Execution Independenceによって、技術・Providerが変わっても意味を継続できる方向を定めている。

REQ-0001 / 0005 / 0006 / 0010 / 0011 / 0014 / 0019、SCN-0003 / 0013 / 0016 / 0018は、判断の再構成、Projection非権威性、残差からの再開、人間とAIの同一canonical meaning利用を既に要求している。

ADR-0028ではProduct Interactionをcanonical meaning上の論理操作境界として定義し、`Case` / `Session` / `Workspace` / `Thread`をInteraction都合だけでUniversal Coreへ追加しないDecisionもAcceptedしている。ISSUE-000053のreference probeでは、人間向け・machine向けSurfaceが同じcanonical sourceを扱うこと、Unknown / Conflict、Recommendation / Decision、light / audit等の意味差を限定範囲で実証した。

一方、current Executable Evidenceは「意味を失わず複数Surfaceから操作できる」ことが中心であり、**利用者が数日後・別AI session・別画面stateから実際に仕事を再開するときの認知負荷や誤再構成**までは検証していない。

### Product Value上の追加整理

resume-firstを単なるUI方針として扱うと、SOZAの価値を狭める。Product Value側では、次をDecision Continuityとして整理した。

```text
Decision Continuity
  = 時間が空いても
  + SurfaceやAIが変わっても
  + 新しい情報が増えても
  + 不確実性が残っていても
  過去を捏造せず、判断仕事の続きを始められること
```

Decision ContinuityはV9ではない。V1〜V8が利用者の一つの仕事で同時に成立した結果として扱う。

### Research Evidenceから得る仮説

中断・task resumption研究では、再開時にtask goalやcontext cueを再活性化すること、長い中断ではworking memoryだけでなくcontext reconstructionが重要になることが報告されている。またcognitive offloading研究では、外部記憶が認知負荷を下げる一方、offload先を失うと性能低下が起こり得ることが整理されている。Human-AI Interaction研究では、AIの誤りを容易にdismiss / correctできること、uncertain時にgracefully degradeすることが重要とされる。

これらをSOZA Requirementへ直接輸入しない。SOZAでは次のProduct hypothesisを選ぶためのResearch Evidenceとして扱い、actual prototype / human reviewで再検証する。

```text
Research Evidence
  != SOZA Product Evidence
```

### 現状のまま実装した場合の主要failure

1. canonical recordは正しいが、利用者がどこから再開すべきか分からない。
2. AI chatが事実上のworking memoryとなり、chatを失うと判断文脈も失う。
3. AIが生成したObservation / Recommendation候補が、利用者に意味差を見せないままcanonicalへ書き込まれる。
4. Decision後に得たObservationが、現在表示を簡単にするため過去Decisionのbasisへ混入する。
5. AI serviceが利用不能になると、open / read / manual add / Decision / reopenまで利用不能になる。
6. UI working setやrecent stateをsemantic identityとして扱い、Projection convenienceがCoreへ侵入する。
7. 複数semantic changeを伴う一操作の途中失敗で、意味上誤解を招く半端な状態が利用者へ見える。
8. staleな画面・AI draftが、後から入ったcanonical changeを黙って上書きする。
9. semantic integrityは高いが入力・review負担が大きく、利用者が継続利用しない。
10. raw chat / simple noteと比べても再開品質に実質的な差がなく、追加構造だけが増える。

9と10もProduct failure候補として扱う。SOZAのsemantic structure自体をProduct Valueの証明にしない。

## Product hypothesis

SOZAの最初の強いProduct Experienceは「たくさんの構造化recordを作れること」ではなく、**文脈を失った後でも、判断仕事の現在地と変化を正しく再構成し、必要な次の一手へ戻れること**に置く。

```text
SOZA first useful value
  = Decision Continuity
  = resume a decision context with meaning intact
  != semantic schema editor
  != chat transcript archive
  != autonomous agent shell
```

最初のsliceはLocal Single-Node Package上のsingle-user利用を想定する。これは将来のteam / hosted利用を否定するものではなく、PMS-03の体験品質を最小deployment条件で切り出すためのProduct Sliceである。

Product Valueとして成立するには、SOZA内でresumeできるだけでは不十分である。妥当な単純代替に対して、少なくとも重要な誤り・負担の一つを実質的に減らし、その効果がcapture / review overheadを相殺する必要がある。

## Candidate requirements

以下は本Issueで検証するCandidate Requirementであり、現時点ではStable REQ IDを付けない。

### CR-73.1 — Canonical-only resume

transient UI state、chat history、AI context、projection cacheを破棄しても、canonical stateだけから有用なresume Projectionを再構成できること。

resume Projectionは固定Contract field listではないが、少なくとも問い / goal、current Decision、主要basis、未解決事項、Decision後の変化、reopen conditionへ到達できることを目標とする。

### CR-73.2 — Provisional AI boundary

AIが生成したObservation候補、Recommendation候補、Method output等は、Product Surface上でprovisionalであることを保ち、明示的なsemantic commitなしにcanonical fact / Decisionへ昇格させないこと。

### CR-73.3 — Efficient correction / dismissal

利用者はAI suggestionをschema / JSONの直接編集なしに修正、意味種別の変更、却下できること。却下されたdraftをcanonical historyへ「発生したDecision」等として残さないこと。

AI suggestion自体の監査が必要なdomainでは、別の明示的policyにより保存し得るが、first sliceのInteraction convenienceからUniversal保存義務を導かない。

### CR-73.4 — Change-oriented review

Decision後に追加されたObservation / Conflict / Recommendation等を、当時のbasisと混ぜずに「何が変わったか」として再開時に確認できること。

```text
post-decision observation
  != historical decision basis
```

### CR-73.5 — Progressive explicitness

利用者は短い問い / goal / contextから始められること。basis、Responsibility、Exact Binding等は、その意味が必要になった操作や影響度で段階的に要求・提示し、最初の保存に最大詳細を強制しないこと。

### CR-73.6 — Graceful AI degradation

AI / model / external Cognitive Methodが利用不能または不確実でも、canonicalなopen / read / manual add / Decision / review / reopenを継続できること。AI failureをnegative business factや`No`へ読み替えないこと。

### CR-73.7 — Working-set non-authority

recent、pin、filter、chat state、form draft、working-set membership等をProduct-local / Projection-local convenienceとし、破棄・再構成してもcanonical meaningを失わないこと。

### CR-73.8 — Meaning-preserving commit

一つの利用者操作が複数canonical changeを計画する場合、途中失敗によって意味上誤解を招くpartial semantic stateを正常完了として露出させないこと。

これはUniversal transaction ontologyを要求しない。Product / Persistence-local atomicity、commit protocol、compensation等のどこに置くべきかはprototypeで比較する。

### CR-73.9 — Stale-write protection

canonical snapshot Sを前提に作られたhuman / AI draftについて、その後canonical stateが変更された場合、古いdraftが新しい意味を黙って上書きしないこと。

snapshot token / revision token等はProduct / Persistence-local mechanism候補であり、Logical ReferenceやSemantic Revisionそのものへ昇格させない。

### CR-73.10 — AI egress visibility

external AIへ渡すcanonical contextは、Interaction側が選択した必要範囲に限定し、何を外へ渡すか利用者またはpolicyから確認可能な方向を保つこと。外部AIを呼び出せることからcanonical write権やDecision Authorityを推定しない。

## Questions

1. resume時に最初に見せる情報は何であれば、semantic completenessを失わず認知負荷を最も下げられるか。
2. current stateとhistorical stateをどのように分ければ、最新情報で過去Decisionを読み替える誤りを避けられるか。
3. AI suggestionからcanonical commitまでに、どのsemantic diff / previewがあれば意味種別の誤りを利用者が発見できるか。
4. working setをProjection-localのまま、複数Inquiry / Decision / residualを自然な一件の仕事として見せるには何が必要か。
5. multi-record semantic changeのatomicityはProduct requirementとして独立に必要か、それともPersistence realizationのAcceptanceで十分か。
6. stale writeを防ぐために、semantic revisionとは別のconcurrency controlをどこへ置くべきか。
7. AIが使えない状態でも成立すべき最低限のProduct Interactionはどこまでか。
8. first human-facing prototypeをlocal browser UI等で実装する場合、その選択をProduct Requirementへ焼き付けずにhuman reviewを行えるか。
9. existing REQ / SCNの組み合わせでCandidate Requirementを十分表現できるか。独立したProduct failureが見つかるのはどこか。
10. raw chat / chronological note等の単純な外部記憶と比較したとき、SOZA固有の価値差はどこにあり、その差はcapture / review負担を上回るか。

## Constraints

- `Workspace` / `Case` / `Session` / `Thread`をInteraction convenienceだけでUniversal Coreへ追加しない。
- Decision ContinuityをV9やUniversal semantic entityへ昇格させない。
- chat transcript、UI state、projection cache、recent listをcanonical authorityにしない。
- AI suggestionをObservation / Recommendation / Decisionへ黙って昇格させない。
- Recommendation != Decision != Authority != Executionを維持する。
- Decision後の新しいObservationをhistorical basisへ遡及混入させない。
- Unknown / Conflict / not_verified / external failureをfalse / Noへ平坦化しない。
- private chain-of-thoughtを保存・提示の成立条件にしない。
- external AI / Providerへ渡すcontextとcanonical semantic stateを同一視しない。
- stale-write対策のruntime revisionをSemantic Revisionへ流用しない。
- local browser、HTTP、MCP、特定AI model等のprototype方式をStable Requirementへ昇格させない。
- prototype PASSをproduction UX、Operational Evidence、Adoption / Outcome Evidenceへ昇格させない。
- Research EvidenceをSOZA Product Evidenceへ読み替えない。
- ISSUE-000072のTEI version-exchange Evidenceとは独立して扱う。

## Required scenarios / experiments

### E1 — canonical-only resume

一つのInquiryへObservation / Conflict / Recommendation / Decisionを作成し、Decision後に新しいObservationを追加する。transient working-set state、chat state、projection cacheを破棄した後、canonical stateだけからresume Projectionを再構成する。

PASS条件:

- current question / goalへ到達できる。
- Decisionと当時basisを読める。
- Unknown / Conflict / residualへ到達できる。
- Decision後の新情報が「変化」として区別される。
- historical basis bytes / refsを変更しない。

### E2 — AI correction / dismissal

AIが誤った意味種別または誤内容のsuggestionを返す。利用者が修正・再分類・却下し、semantic change previewを確認する。

PASS条件:

- uncommitted suggestionはcanonicalへ現れない。
- corrected commitだけが指定した意味種別で保存される。
- dismissalをDecisionやnegative factとして捏造しない。

### E3 — AI unavailable

AI adapter / modelを意図的に利用不能にする。

PASS条件:

- open / read / manual Observation追加 / Decision / review / reopenが継続できる。
- unavailableをNo / failed Decisionへ変換しない。

### E4 — progressive explicitness

low-impactな判断を短いcontextから開始し、後からbasis / residualを追加する。別のrich caseではaudit detailへ降りる。

PASS条件:

- minimal startで最大field setを要求しない。
- detail追加後も同じcanonical identity / lineageへ戻れる。
- UI-localなimpact levelをUniversal ontologyにしない。

### E5 — working-set rebuild

pin、recent、filter、draft等のProjection-local metadataを削除する。

PASS条件:

- canonical semantic dataは不変。
- 同じ意味からworking setを再構成できる。

### E6 — semantic commit fault injection

複数canonical changeを含む一操作の途中へfaultを入れる。

PASS条件:

- 利用者が正常状態として読むcanonical viewは、操作前のvalid stateまたは操作後のvalid stateのどちらかである。
- 意味上半端なstateをsuccessful commitとして露出させない。

### E7 — stale draft

snapshot Sからdraftを作った後、別操作でcanonical stateを更新し、その後S由来draftをcommitする。

PASS条件:

- newer canonical changeを黙ってoverwriteしない。
- reject / rebase / explicit conflictのいずれかとして観測できる。

### E8 — external AI context boundary

選択したcanonical contextだけをexternal AIへ渡し、responseをprovisional suggestionとして受け取る。

PASS条件:

- outbound context setを検査できる。
- 非選択canonical dataが暗黙に送出されない。
- response受信だけでcanonical write / Decision Authorityが成立しない。

### H1 — resume usability review

prototypeを用いて、人間がchat historyや内部schemaの知識なしに、次へ答えられるかを観測する。

- 何を考えていたか。
- 何を決めたか。
- なぜそう決めたか。
- 何がまだ分からないか。
- 何がその後変わったか。
- 次に何を見直すべきか。

初回から固定thresholdをStable Requirementにはしない。time-to-orientation、必須入力量、AI誤りの修正負担、audit detailへ降りる回数等を観測する。

### H2 — counterfactual Decision Continuity review

同じ判断素材について、少なくとも次の二つの条件を比較する。

```text
A: raw chat / chronological note等の単純baselineだけから再開
B: SOZA canonical state + Resume Projectionから再開
```

厳密な被験者実験や統計有意差をfirst iterationの必須条件にはしない。まずpilot比較として、同一または同等の判断素材を使い、どのfailureが実際に減るかを観測する。

観測項目:

- current questionを正しく説明できるか。
- current DecisionをRecommendationと混同しないか。
- unresolvedを発見できるか。
- post-decision情報をhistorical basisへ誤帰属しないか。
- resumeまでの時間、操作、主観的mental effort。
- AI suggestionの修正・却下負担。
- first useful saveまでのcapture burden。
- 継続利用したいか。その理由は何か。

解釈規則:

```text
faster resume
  + worse historical accuracy
  = Product Value improvementではない
```

SOZA側で明確な価値差が観測されなくてもFAILを隠さない。raw chat / simple noteで十分である、またはcapture overheadが利益を上回る場合は、Decision Continuity Product hypothesisを弱める・scopeを狭めるEvidenceとして記録する。

## Deliverables

- `product/value/SOZA_DECISION_CONTINUITY.md` — V1〜V8をDecision Continuityへ接続するProduct Value synthesis。
- `product/interaction/SOZA_FIRST_USABLE_PRODUCT_SLICE.md` — first sliceのProduct Design baseline。
- `architecture/SOZA_INTERACTION_WORKING_SET_ARCHITECTURE.md` — state authority、resume Projection、semantic commit、AI境界のReference Architecture。
- prototype / probe — Local Single-Node上でE1〜E8を再現できる最小実装。
- human review record — H1のresume usability観測結果。
- comparative Product Value review — H2のbaseline比較、capture tax、誤帰属、correction負担の観測結果。
- Requirement audit — CR-73.1〜10をexisting REQ / SCNへ統合するか、新Stable Requirementへ昇格するか、No Changeとするかを記録する。

## Resolution

次をすべて満たしたときResolved候補とする。

1. first sliceのProduct DesignとArchitecture boundaryがcurrent Product Value / ADRと整合している。
2. Decision ContinuityをV9やUniversal型へ増やさず、cross-axis Product OutcomeとしてProduct Valueへ接続している。
3. E1〜E5を少なくともprototypeで実行し、canonical / Projection / transient境界が成立する。
4. E6 / E7について、partial commitとstale writeを黙って受理しないfailure behaviorをactualに確認する。
5. E8でexternal AI context / provisional response境界をactualに確認するか、first sliceでexternal AIを含めない合理的理由を記録する。
6. H1 human reviewを少なくとも一度実施し、再開時の認知負荷と修正可能性を観測する。
7. H2 counterfactual reviewを少なくともpilotとして実施し、単純baselineに対する価値差または価値差がないEvidenceを記録する。
8. capture / review overheadが観測されたProduct Valueを相殺していないか評価する。
9. Candidate Requirementをexisting REQ / SCNへ再照合し、Stable Requirement追加の要否を決定する。
10. 実装方式固有のlocal browser / protocol / AI model等をUniversal semanticsへ持ち込んでいない。

Design文書が完成しただけではResolvedにしない。prototypeが技術的にPASSしただけでも、Decision ContinuityのAdoption / Outcome Evidenceが成立したことにはしない。

## Reopen conditions

Resolved後でも、次の場合は再開する。

- 実利用でcanonical-only resumeでは必要な現在地を再構成できない事例が見つかった。
- AI suggestionのprovisional境界では誤commitを十分防げないEvidenceが得られた。
- single-userからteam利用へ進む際、working setにProjection convenienceでは説明できない耐久的semantic necessityが確認された。
- stale-write / atomic commitをPersistence-localに置く設計ではDecision integrityを守れない事例が確認された。
- raw chat / simple note等のより単純な手段に対する価値差が継続的に確認できない。
- capture / review overheadが利用者価値を上回る。
- Product Value / REQ / ADR-0028 / ADR-0029が変更された。

## CI / verification

GitHub Actionsを成立条件にしない。repository同梱test、local probe、fault injection、保存Evidence、human reviewを使う。

設計文書段階では`plan/scripts/check_plan_registry.py`と`plan/scripts/check_document_review_registry.py`の対象整合を確認する。prototype実装後は責務に応じたGo test / probeを追加する。

未実行の実験をPASSと扱わず、Design EvidenceをExecutable / Operational / Adoption Evidenceへ昇格させない。

## Natural Japanese review

Product Value、Decision Continuity synthesis、Value Model V1〜V8、Product Shape、PMS-03、Product Interaction、Packaging、REQ-0001 / 0005 / 0006 / 0010 / 0011 / 0014 / 0019、SCN-0003 / 0013 / 0016 / 0018、ADR-0005 / 0010 / 0028 / 0029を照合した。

従来のIssueは「再開できるUI / prototype」を中心に十分深く設計されていたが、そのままではSOZA自身の仕組みだけを評価する自己完結的な検証になり得た。そこでDecision Continuityをcross-axis Product Outcomeとして上位価値へ接続し、raw chat / chronological note等の単純baselineとのcounterfactual reviewをResolution条件へ追加した。

SOZAのsemantic integrityが高いだけではProduct Valueとせず、historical誤帰属、Recommendation / Decision混同、再構成負担を実際に減らし、その利益がcapture / review overheadを上回るかまでを見る。価値差がない結果もProduct hypothesisを修正する正当なEvidenceとして扱う。

Candidate Requirementはprototype / human review前にStable化せず、Research EvidenceもProduct Evidenceへ読み替えない。意味、要求強度、留保、Evidenceの高さを固定したうえで自然な日本語として読み直し、最終意味監査を実施した。