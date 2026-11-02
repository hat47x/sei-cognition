# ISSUE-000073: resume-firstな最初の実用Product Sliceを定義・実証する

Status: **Open**  
Priority: **1**  
Related ADRs: **ADR-0005, ADR-0010, ADR-0028, ADR-0029**  
Updated: 2026-11-02

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

Design baselineを整えただけではResolvedにしない。canonical-only resume、AI suggestionのprovisional境界、意味変更preview、AI unavailable時のgraceful degradation、stale write / partial commitのfailure behaviorをprototypeで検査する。さらにhuman reviewでは、SEIだけを評価するのではなく、raw chat / chronological note等の単純な代替手段との比較を行い、**SEIの追加構造が本当に再構成負担・誤帰属・AI correction負担を減らし、その価値がcapture / review overheadを上回るか**を確認する。

## Background

SEIはV1 Historical Reconstruction、V2 Semantic Separation、V3 Revision Integrity、V5 Uncertainty Preservation、V6 Human / AI Readability、V7 Progressive Explicitnessを持ち、V4 Provider IndependenceとV8 Execution Independenceによって、技術・Providerが変わっても意味を継続できる方向を定めている。

REQ-0001 / 0005 / 0006 / 0010 / 0011 / 0014 / 0019、SCN-0003 / 0013 / 0016 / 0018は、判断の再構成、Projection非権威性、残差からの再開、人間とAIの同一canonical meaning利用を既に要求している。

ADR-0028ではProduct Interactionをcanonical meaning上の論理操作境界として定義し、`Case` / `Session` / `Workspace` / `Thread`をInteraction都合だけでUniversal Coreへ追加しないDecisionもAcceptedしている。ISSUE-000053のreference probeでは、人間向け・machine向けSurfaceが同じcanonical sourceを扱うこと、Unknown / Conflict、Recommendation / Decision、light / audit等の意味差を限定範囲で実証した。

一方、current Executable Evidenceは「意味を失わず複数Surfaceから操作できる」ことが中心であり、**利用者が数日後・別AI session・別画面stateから実際に仕事を再開するときの認知負荷や誤再構成**までは検証していない。

### Product Value上の追加整理

resume-firstを単なるUI方針として扱うと、SEIの価値を狭める。Product Value側では、次をDecision Continuityとして整理した。

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

これらをSEI Requirementへ直接輸入しない。SEIでは次のProduct hypothesisを選ぶためのResearch Evidenceとして扱い、actual prototype / human reviewで再検証する。

```text
Research Evidence
  != SEI Product Evidence
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

9と10もProduct failure候補として扱う。SEIのsemantic structure自体をProduct Valueの証明にしない。

## Product hypothesis

SEIの最初の強いProduct Experienceは「たくさんの構造化recordを作れること」ではなく、**文脈を失った後でも、判断仕事の現在地と変化を正しく再構成し、必要な次の一手へ戻れること**に置く。

```text
SEI first useful value
  = Decision Continuity
  = resume a decision context with meaning intact
  != semantic schema editor
  != chat transcript archive
  != autonomous agent shell
```

最初のsliceはLocal Single-Node Package上のsingle-user利用を想定する。これは将来のteam / hosted利用を否定するものではなく、PMS-03の体験品質を最小deployment条件で切り出すためのProduct Sliceである。

Product Valueとして成立するには、SEI内でresumeできるだけでは不十分である。妥当な単純代替に対して、少なくとも重要な誤り・負担の一つを実質的に減らし、その効果がcapture / review overheadを相殺する必要がある。

## Candidate requirementsと監査結果

以下10件は、本Issueで検証を開始したCandidate Requirementである。2026-09-16のRequirement auditでは、これらを機械的にStable Requirementへ昇格させず、current REQ / SCNへ一件ずつ再照合した。

この節には検討時の意味核を残す。currentの規範上の正本は`requirements/PRODUCT_REQUIREMENTS.md`と`requirements/ACCEPTANCE_SCENARIOS.md`であり、Candidateの記述がStable Requirementより優先することはない。

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

### Requirement audit result — 2026-09-16

CR-73.1〜73.10を既存REQ / SCN、Product / Projection境界、human Outcome評価へ再照合した結果は次のとおりである。

- **CR-73.1〜73.7、CR-73.10** — 既存Requirement / Scenario、Product / Projection-localな設計境界、またはH1 / H2で観測すべきProduct Outcomeへ戻せるため、このIssueから新しいStable REQを追加しない。
- **CR-73.8 + CR-73.9** — partial commitとstale writeはmechanismこそ異なるが、どちらも「successful canonical commitが実際のcanonical meaningと食い違う」という同一の独立failureを生む。既存REQではこのfailureを直接禁止できなかったため、**REQ-0023 — Canonical commitの整合性**へ一件として統合し、**SCN-0019**でfault / stale variantをAcceptance化した。
- transaction、atomic replace、snapshot token、ETag、generation、digest等はProduct / Persistence-localな実現手段のままとし、Universal semantic entityやSemantic Revisionへ昇格させない。

このformalizationはDesign Evidenceである。REQ-0023 / SCN-0019がAcceptedであることやprobe sourceが存在することを、actual Executable PASSへ読み替えない。

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
10. raw chat / chronological note等の単純な外部記憶と比較したとき、SEI固有の価値差はどこにあり、その差はcapture / review負担を上回るか。

### 2026-09-16時点の問いの整理

Question 5、6、9については、Requirement auditとREQ-0023 / SCN-0019のformalizationにより、current design-levelの回答を得た。atomicityやconcurrency controlの具体方式はPersistence / Product realizationへ委ね、semantic revisionとは分離する。

一方、Question 1〜4、7、8、10は、source codeやRequirement文書だけでは閉じない。E1〜E8のactual実行、H1 / H2 human review、capture / review burdenの観測を通して検証する。

### 2026-10-10時点の問いの整理

E1〜E8 actual PASSにより、Question 1〜4、7について「必要な意味をcanonical stateから再構成できるか」「AI unavailableやprovisional境界を技術的に保てるか」というmechanism側の反証は、Local Single-Nodeのprobe範囲で通った。tested commitからcurrent source closureも39 / 39 blob一致である。

ただし、どの表示が人間の認知負荷を本当に下げるか、semantic diffが人間に誤りを見つけさせるか、first human-facing interactionが過剰な負担を生まないか、単純baselineより価値があるかはExecutable Evidenceだけでは閉じない。したがってQuestion 1〜4、8、10のhuman / Product Value側はH1 / H2へ残す。E1〜E8はsource closureが変わらない限り再実行を優先しない。

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
- Research EvidenceをSEI Product Evidenceへ読み替えない。
- ISSUE-000072のTEI version-exchange Evidenceとは独立して扱う。

## Current implementation / Evidence status — 2026-10-10

現在はDesign baselineだけの段階から、E1〜E8を再現するGo interaction probeと、runner・verifier・one-command captureを持つ段階へ進んでいる。ただし、sourceや受入れtoolingの存在とactual E1〜E8実行結果は分ける。

- Decision Continuity synthesis、first usable Product Slice、Interaction Working-Set Architecture: **Design Evidence available**
- CR-73.8 / CR-73.9: **REQ-0023 / SCN-0019へformalize済み**
- `runtime/go/interactionprobe`: E1〜E8に対応するprobe / test sourceあり
- `tools/run_issue_000073_resume_first_evidence.py`: E1〜E8をmachine-readable recordへ束ねるrunnerあり
- `tools/verify_issue_000073_resume_first_evidence.py`: recorded tested commit、source blob / SHA-256、Go version、E1〜E8個別test結果を再検証するverifierあり
- `tools/capture_issue_000073_resume_first_evidence.py`: runner → verifier → Evidence保存を一命令でfail-closedに連結する標準入口あり
- `tools/bootstrap_issue_000073_resume_first_evidence.sh`: Go 1.25.xがhostにない場合、事前配置済みGo 1.25.xまたはSHA-256固定済みGo 1.25.14 Linux / amd64 archiveからtoolchainをcheckout外へ準備し、既存captureへ渡す入口あり。**bootstrap追加はE1〜E8 PASSを意味しない**
- bootstrap mechanics: exact committed script blobに対する`bash -n`、事前配置Go 1.25.xのcapture受け渡し、dirty-tree拒否、`--go`迂回拒否をsynthetic Git repositoryで**PASS**。Evidenceは`evaluation/personal-inquiry-decision/evidence/issue-000073/go125-bootstrap-mechanics-2026-10-07.json`。archive materializationとE1〜E8 actual実行は未検証
- `tools/prepare_issue_000073_external_execution_bundle.py`: private GitHubへ接続できない外部実行環境へ、canonical commit identityを保ったclean sourceを渡すGit bundle handoff入口あり。clean HEAD、独立に与えるexpected HEAD、repository外outputを要求し、bundleを`git bundle verify`とSHA-256 manifestで検査する
- external handoff mechanics: preparer / self-testの**exact committed Git blob**をmaterializeし、exact HEAD clone、expected HEAD不一致拒否、dirty source拒否、repository内output拒否、明示`--replace`制御を**5/5 PASS**。Evidenceは`evaluation/personal-inquiry-decision/evidence/issue-000073/external-execution-bundle-mechanics-2026-10-09.json`。actual SEI repository bundle作成、外部node clone、E1〜E8 actual実行は未検証
- `tools/run_issue_000073_external_execution_bundle.py`: handoff artifactのSHA-256 / manifest / source identityを検証し、exact clone後にbundleを再検証して既存bootstrap / captureへ接続し、`pass / blocked / fail`を外部run recordへ保存する受け側入口あり
- external runner mechanics: preparer / receiver / self-testのexact committed blobを使い、成功経路、bundle digest改ざん拒否、manifest source identity改ざん拒否、bootstrap blocked非昇格を**4/4 PASS**。Evidenceは`evaluation/personal-inquiry-decision/evidence/issue-000073/external-execution-runner-mechanics-2026-10-09.json`。synthetic bootstrapを用いたmechanics testでありactual E1〜E8ではない
- runner preflight self-test: **PASS on canonical-HEAD-bound current source (2026-09-18); machine-readable delta Evidence recorded**
- verifier self-test: **PASS on canonical-HEAD-bound current source (2026-09-18); machine-readable delta Evidence recorded**
- capture workflow: **historical full self-test PASS retained; canonical-HEAD deltaは8 case actual + same-output focused preflight actualで確認 (2026-09-18)**
- E1〜E8 actual Go 1.25.x execution: **PASS (2026-10-09, tested commit `694ec5805c00a8bae9034e15ee0d1589e40f6fd8`, go1.25.14 linux/amd64)**。`go test -count=1 -json ./interactionprobe`の必須18 testがすべてpass、`go test`全体も31 pass / 0 fail。verifierもfindings 0でPASS。Evidenceは`evaluation/personal-inquiry-decision/evidence/issue-000073/e1-e8.json`と`e1-e8-verification.json`。**事前配置のGo 1.25.14によるScoped Executable Evidenceであり、bootstrap wrapperのpinned archive materialization経路は実行していない**
- E1〜E8 current-source applicability: **39 / 39 source-closure blob一致 (2026-10-10)**。tested commitから`develop/v0.2.0`の観測HEAD `3ecb15848e3f07760a868f9e266183383eda0a40`まで、`runtime/go/interactionprobe` 22 file、`runtime/go/semanticruntime` 13 file、`go.mod` / `go.sum`、runner / verifierの全blobが同一だった。既存のactual PASSはこの未変更source closureへ適用可能と判断する。これは新しいtest実行ではない。Evidenceは`evaluation/personal-inquiry-decision/evidence/issue-000073/e1-e8-current-source-closure-2026-10-10.json`
- REQ-0023 / SCN-0019 Executable Evidence: **E6 / E7のprobeレベルでPASS (2026-10-09)**。E6（`TestCommitCoordinator*` 3 test）とE7（`TestStaleDraftCommitRequiresFreshProposal`、`TestReclassifiedObservationKeepsOriginalSnapshotPrecondition`）がpartial commitとstale writeを黙って受理しないことを確認した。ただしこれはLocal Single-Node上のProduct-local probeに対する結果であり、他のStorage profileやProductionの永続層へは一般化しない
- H1 resume usability review: **Not Yet Observed**
- H2 counterfactual Decision Continuity review: **Not Yet Observed**。073/078共通runnerでreviewer provenanceをstimulus提示前に固定し、Decision固有validationとEvidence exportまで同じ経路へ統合済み。current Decision manifest / 3 fixture / R1〜R3のstatic source auditは整合し、actual repository integration test sourceも追加済み。tested commit `42872959a13746eb5fd87f1fe10233ccd55caac0` の対象12 sourceをGit blob SHA一致でmaterializeしたactual executionでは、Python focused regressionが**8 tests / 8 PASS**。ただしnative clean-HEAD captureは**Not Yet Verified**
- `tools/capture_issue_000073_h2_runner_selftest.py`: H2 shared runner Decision regression testをclean HEAD / source binding付きでEvidence化するcapture入口あり
- H2 runner capture workflow self-test: **PASS on canonical-HEAD / fixture-bound current source (2026-09-18); machine-readable Evidence recorded**
- H2 shared runner Decision regression actual capture: **Not Yet Verified**
- Decision Continuity Product Value: **Not Established**
- Operational Evidence: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

runner / captureはclean committed HEAD、required sourceとHEAD blobの一致、Go 1.25.xを要求する。2026-09-18にcurrent execution environmentを再確認したが、host Goは引き続き1.23.2で、`GOTOOLCHAIN=go1.25.0+auto go version`によるtoolchain取得は`proxy.golang.org`へのDNS / 外向き通信制限でblockedとなった。さらに別経路としてGo公式配布先 `go.dev` / `dl.google.com` へのdirect probeもactualに実行し、いずれもDNS resolution failure（curl exit 6）だった。filesystem scanでもGo executable candidateは`/usr/local/go/bin/go`のみで、Go 1.25.xは見つからなかった。これはinteractionprobe FAILではなくenvironment blockerであり、低いGoで代替PASSを作らない。

Evidence受入れ経路のactual self-test結果は、次のmachine-readable Evidenceへ固定している。

```text
evaluation/personal-inquiry-decision/evidence/issue-000073/runner-verifier-selftests-2026-09-18.json
evaluation/personal-inquiry-decision/evidence/issue-000073/capture-workflow-selftest-2026-09-18.json
evaluation/personal-inquiry-decision/evidence/issue-000073/h2-runner-capture-selftest-2026-09-18.json
evaluation/personal-inquiry-decision/evidence/issue-000073/h2-runner-capture-head-bound-selftest-2026-09-18.json
evaluation/personal-inquiry-decision/evidence/issue-000073/go-toolchain-acquisition-blocker-2026-09-18.json
evaluation/personal-inquiry-decision/evidence/issue-000073/e1-e8-canonical-head-binding-selftests-2026-09-18.json
evaluation/personal-inquiry-decision/evidence/issue-000073/go125-bootstrap-mechanics-2026-10-07.json
evaluation/personal-inquiry-decision/evidence/issue-000073/external-execution-bundle-mechanics-2026-10-09.json
evaluation/personal-inquiry-decision/evidence/issue-000073/external-execution-runner-mechanics-2026-10-09.json
evaluation/personal-inquiry-decision/evidence/issue-000073/e1-e8-current-source-closure-2026-10-10.json
```

これらはrunner / verifier / captureの受入れ系に限定したExecutable Evidenceであり、E1〜E8 actual Go Evidenceではない。currentの実行手順とblocker詳細は`evaluation/personal-inquiry-decision/DECISION_CONTINUITY_EXECUTION_READINESS_2026-09-16.md`をcurrent-state正本として参照する。


### Go 1.25.x実行入口の更新 — 2026-10-07

2026-09-18の実行環境ではhost Go 1.23.2しか利用できず、Go自身のtoolchain取得とGo公式配布先へのdirect probeもDNS / 外向き通信制限で停止した。この観測は当時のEnvironment Evidenceとして保持する。

その後、repository内の別評価経路でexact Go 1.25.14 Linux / amd64 archive identityが固定されたため、ISSUE-000073でも同じarchive identityを用いて既存captureへ到達する専用入口を追加した。

```text
tools/bootstrap_issue_000073_resume_first_evidence.sh
```

入口は次の順序でGo executableを選ぶ。

1. `GO_BINARY_PATH`で明示されたGo 1.25.xを検証して利用する。
2. hostの`go`がGo 1.25.xならそのまま利用する。
3. それ以外のLinux / amd64では、Go 1.25.14 archiveを事前配置または取得し、SHA-256照合後にcheckout外のcacheへ展開する。
4. 既存の`capture_issue_000073_resume_first_evidence.py`へ`--go`として渡し、runner → verifier → Evidence保存の既存境界を変更しない。

自動取得で固定するidentityは次のとおり。

```text
go1.25.14.linux-amd64.tar.gz
sha256:a21ae5633a269bcd7e90cf767e48225633795e99d831742cbf3397064fee7712
```

通常の入口:

```bash
bash tools/bootstrap_issue_000073_resume_first_evidence.sh \
  --expected-head <canonical-commit-sha>
```

外部で準備済みのGo 1.25.xを使う場合:

```bash
GO_BINARY_PATH=/path/to/go \
bash tools/bootstrap_issue_000073_resume_first_evidence.sh \
  --expected-head <canonical-commit-sha>
```

固定archiveを事前配置する場合:

```bash
GO_TOOLCHAIN_ARCHIVE_PATH=/path/to/go1.25.14.linux-amd64.tar.gz \
bash tools/bootstrap_issue_000073_resume_first_evidence.sh \
  --expected-head <canonical-commit-sha>
```

toolchain cacheは既定でrepository外へ置く。既存の不完全なcacheやdigest不一致を暗黙に上書きせずfail-closedにする。これによりcaptureのclean-tree preconditionをtoolchain materialization自身が壊さない。

この追加でrepository tooling上のGo 1.25.x取得経路は具体化したが、2026-10-07時点でこの新入口によるE1〜E8 actual executionはまだ記録していない。したがってEvidence状態は変えない。

2026-10-09には、事前配置のGo 1.25.14（`GO_BINARY_PATH`）をこの入口へ渡してE1〜E8 actual executionを取得した。取得経路は`pre-provisioned-binary`であり、`GO_TOOLCHAIN_ARCHIVE_PATH`やpinned archiveのdownload / SHA-256照合 / 展開というwrapper自身のmaterialization経路は通っていない。そのためwrapperのarchive materializationは引き続き**Not Yet Verified**とする。

```text
bootstrap path available
  != E1-E8 actual PASS
  != H1 / H2 human review
  != Decision Continuity Product Value established
```


### External exact-source handoff — 2026-10-09

実行nodeがprivate GitHubへ接続できない場合でも、canonical commitを別のsource snapshotへ置き換えずにE1〜E8へ進めるため、Git bundleによるhandoffを追加した。

```text
tools/prepare_issue_000073_external_execution_bundle.py
```

clean checkoutで、checkout外から取得したcanonical expected HEADを指定して実行する。

```bash
python3 tools/prepare_issue_000073_external_execution_bundle.py \
  --expected-head <canonical-commit-sha> \
  --output-dir <outside-repository-directory>
```

preparerは、source HEADとexpected HEADの一致、clean working tree、repository外outputを確認し、次を一組として作る。

```text
*.gitbundle
*.manifest.json
*.SHA256SUMS
```

外部nodeでは`.gitbundle`からcloneし、HEAD一致を確認してから既存bootstrap / captureを実行する。これにより、private GitHub credentialやnetwork接続をProduct semanticsやEvidence成立条件へ持ち込まず、Git commit identityはそのまま維持できる。

```text
canonical clean checkout
  → exact Git bundle
  → transport
  → external clone
  → exact HEAD verification
  → Go 1.25.x bootstrap / capture
  → e1-e8.json + e1-e8-verification.json
```

2026-10-09にはpreparerとself-testのexact committed Git blobをmaterializeし、synthetic Git repositoryで5件をactual実行して5/5 PASSした。ただしactual SEI repositoryのclean checkoutからbundleを生成したわけではなく、外部nodeでreal bundleをcloneしてE1〜E8を実行したEvidenceでもない。

```text
handoff mechanics PASS
  != actual SEI bundle prepared
  != external clone executed
  != E1-E8 actual PASS
```


受け側では次を一命令で行える。

```bash
python3 tools/run_issue_000073_external_execution_bundle.py \
  --bundle <bundle.gitbundle> \
  --manifest <bundle.manifest.json> \
  --sha256sums <bundle.SHA256SUMS> \
  --work-dir <new-clean-work-directory> \
  --result-dir <outside-work-directory-result>
```

runnerはSHA-256、manifest schema / Issue / exact source HEAD、bundle advertised HEADを検査してからcloneする。clone後にもexact HEAD、clean working tree、`git bundle verify`を確認し、その後でbootstrap / captureを起動する。結果は`e1-e8.json`、`e1-e8-verification.json`、stdout / stderr digest、`external-run.json`へ分離して保存する。bootstrapが実行前提不足で`blocked`を返した場合は、verificationを捏造せず`blocked`のまま保持する。

exact committed sourceを使ったself-testでは、成功経路、bundle改ざん、manifestのexpected HEAD改変、bootstrap blockedの4件を4/4 PASSした。これは受け側mechanicsのEvidenceであり、actual SEI bundleを使ったexternal runではない。

H2については2026-09-18に実行経路を再監査し、`inquiry_continuity_review_runner.py`を073/078共通のprovenance-first入口としてDecision Continuityにも対応させた。reviewer provenanceを固定しないsessionからreviewer bundleを開かず、condition labelをreviewerへ出さず、Decision固有response validationを通したcomplete sessionだけをEvidence exportへ進める。

同じ日にcurrent Decision manifestと3 fixtureを正本bytesから再照合し、Decision参照、historical basis、unresolved、post-decision id、condition割当、R1〜R3 rotationの構造整合をstatic source auditとして確認した。さらにcurrent repositoryのmanifest / fixtureを共有runnerから直接開くintegration test sourceを追加した。その後、tested commit `42872959a13746eb5fd87f1fe10233ccd55caac0` の対象12 sourceをGit blob SHA一致でmaterializeし、focused Python regressionをactual実行して8 tests / 8 PASSを確認した。これはnative clean-HEAD captureではなく、H2 human observationでもない。

同じDecision regression testをactual checkoutで再現可能なEvidenceへ落とすため、`capture_issue_000073_h2_runner_selftest.py`を追加した。captureはclean committed HEAD、required sourceのHEAD blob一致、正確なtest commandを固定し、test failureをPASSへ昇格させない。capture workflow自体のsynthetic self-testはactualにPASSしmachine-readable Evidenceへ固定済みである。Decision regression test本体もexact blob-validated materializationでは8 tests / 8 PASSをactual確認したが、**native clean-HEAD actual captureはNot Yet Verified**のままとする。

同日の作業過程では、R1相当のphase1 materialがこの境界を追加する前に一度提示されたが、human responseは固定されなかった。この提示をH2 observationへは数えず、同じreaderが後続reviewを行う場合は`known-material-exposure`として扱う。clean blinded pilotが必要なら、当該materialへ未露出のreaderを用いる。

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
B: SEI canonical state + Resume Projectionから再開
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

**【提案・ADR-0035 / 2026-10-02】主な指標と副次の指標の重みづけ。** 一人で再開する速さは、各ベンダーの記憶機能が伸びるほど代替されやすい価値です。したがってH1 / H2の人手レビューでは、次を**主な指標**に置きます。

1. historical basisへの誤帰属（Decision後の情報を、当時から知っていたように読む誤り）
2. AI suggestionの誤った昇格（RecommendationをDecisionと読む、provisionalなものをcanonicalと読む誤り）
3. プロバイダ（AIモデルや記憶の提供元）を交換した後の継続

time-to-orientation（再開までの時間）、操作数、mental effortは**副次の指標**とします。副次の指標が良くても、主な指標が悪ければ成功とは扱いません。

この変更はResolution条件を強めたり弱めたりしません。H2の観測項目のうち「post-decision情報をhistorical basisへ誤帰属しないか」は主な指標1に、「current DecisionをRecommendationと混同しないか」は主な指標2の前半に、「AI suggestionの修正・却下負担」は主な指標2の後半の観測に対応します。プロバイダ交換後の継続（主な指標3）は、E1〜E8とH1 / H2の観測項目には明示されていないため、観測項目へ加えるかどうかは別途判断します。ここでは観測の重みづけを明示するだけです。プロバイダ交換後の継続は、`SEI_VALUE_ACCEPTANCE.md`のV4のプロバイダ離脱訓練（ISSUE-000088）とも対応します。

SEI側で明確な価値差が観測されなくてもFAILを隠さない。raw chat / simple noteで十分である、またはcapture overheadが利益を上回る場合は、Decision Continuity Product hypothesisを弱める・scopeを狭めるEvidenceとして記録する。


### 2026-11-02 横断受入追補：履歴の再現、現在の利用、行為の資格

**位置付け：既存H1/H2とCR-73.1〜10の評価を精緻化する計画追補。新たなStable Requirement、共通Runtime／Host、Owner受理の追加ではない。** 2026-11-02照合基準はSEI `main` `234c3f91ce86b59b0f202295f454bad74dc6758c`。以下のIssue番号はGitHub Issueを指し、本ファイルの`ISSUE-000073`や過去のGitHub #73とは別の識別子である。

**三つの継続性を別々に説明する。** (A) *Historical reconstruction*：当時のDecision／Recommendation／basis／Unknown／判断後に生じた情報の区別。(B) *Current applicability*：現在のSource・Rule・用途・外部条件と過去の判断の適合。確認できない箇所は、用途に応じた再確認先を持つ未判定として保持する。(C) *Action eligibility/effect*：現在の主体・対象・権限・Commit／Receipt／Business Outcome。Cは既存Host・Capability・Provider等の責務とし、SEIの`resume`や`check_decision`の成功を実行許可・業務完了へ昇格させない。

**判断の根拠の解像度と取得範囲を保存する。** 論理IDと同一内容digestだけで参照対象を同一視せず、scope・Exact Binding・Representation Profile・資料の版／位置を必要な用途で辿れるようにする。独立recordが見つからなくても文書本文に候補が残る場合、`record未発見`と`内容不存在`を区別する。検索結果0件／未決一覧0件／Impact候補が正数であることだけで、対象全件性や業務上の無影響を断定しない。TEIの評価Ruleが変われば元Graph／Source byteが同じでも評価結果は変わり得る。SEI [#767](https://github.com/hat47x/sei-cognition/issues/767)が扱う外延の網羅、問いに必要な意味区別、開示可能な範囲、現在の適用可能性の4軸を、H1・横断受入での解釈票に利用する。新しい共通Claim型やTruth Storeへは移さない。

**機密と外部Harnessの境界。** 内部Productが知るSourceと、外部AI／Harnessへ開示できるProjectionは一致しない場合がある。開示Projectionが同じ二入力でも内部の正解が異なり得るため、外部AIによる「不存在」「全件確認済み」の断定を許さない。必要な確認は権限を持つProductへ委ね、外部へ返す理由・件数も開示許可に従って選択する。本文や外部ツール結果はdataとして扱い、そこに記された命令を操作権限に変換しない（SEI #660/#767、TAI #232、TEI #2515/#2516の責務を参照）。

**既存実装との一致と残余。** [PR #679](https://github.com/hat47x/sei-cognition/pull/679) は2026-10-29に統合済みで、集計範囲と照合付き原record読出しを追加した（外部原資料の真正性や人間の理解は別）。GitHub [#699](https://github.com/hat47x/sei-cognition/issues/699) はClosedであり、Gate結果の版束縛を未着手とする古い記述を現状へ持ち込まない。残る課題は、Exact basis表示 [#697](https://github.com/hat47x/sei-cognition/issues/697)、記録側のExact Binding [#686](https://github.com/hat47x/sei-cognition/issues/686)、根拠解決と未検証範囲 [#710](https://github.com/hat47x/sei-cognition/issues/710)、同一論理参照の曖昧さ [#724](https://github.com/hat47x/sei-cognition/issues/724)、後続Lineageの意味 [#687](https://github.com/hat47x/sei-cognition/issues/687)、現在文脈の経路 [#660](https://github.com/hat47x/sei-cognition/issues/660) 等の既存Issueで追う。`allow`／`verify`の終了コードや、記録されたDecisionの存在だけを強い意味受理へ変換しない。

**H2の二重の妥当性。** (1) *Semantic parity*：A raw chat／B chronological note／C SEI Resumeの全条件で、Decision、Recommendation、歴史的basis、Unknown、後発情報を同じ意味で伝える。(2) *Product fidelity*：Cの固定`surface_text`は人が整理した評価素材であり、現行`BuildResume()`を直接取得した製品出力ではない。既存fixtureと未露出条件を維持してpilotを行い、別のoperator-side照合票でC素材と現行CLI/MCP出力の取得可能範囲・原recordへの操作・補足編集量を比較する。H2のC優位をそのまま現行製品の優位へ昇格させない。

**Human Evidenceの適格性。** 3 fixture×3 condition=9組のcounterbalance coverageは構造上の網羅であり、異なるreader、事前素材への非露出、human authorship、独立した正誤監査を証明しない。既存`review_provenance`・session snapshot・stage gateを再利用し、評価者の重複／事前露出／合成回答／回答監査の根拠をoperator票で分ける。回答本文の文字列型・質問数・`findings=pass`だけで正解を主張しない。暦上のgapと認知的gapを分けたH1を、H2の技術的capture修正と並行して実施できる。新しいhuman session schemaは設けない。

**証拠取得のP0修正候補（未実装・NOT RUN）。** H2はpreflight 7／shared-runner 8／analysis 5、合計20 testを期待する。現行`capture_issue_000073_h2_runner_selftest.py`は`unittest discover`の終了コードだけでPASSとし、一部未発見でも誤PASSになり得る。完全PASSには期待したtest ID集合の実行、skip／error／failureなし、expected HEAD・required sourceの照合を要求する。3件だけのsynthetic self-test fixtureも7/8/5へ合わせる。さらに`--replace`付きのHEAD／source preflight失敗で既存Evidenceを削除し得るため、preflight失敗時は旧byteを保持し、新Evidenceを正常に確定できた場合にだけ原子的に置換する。合成負例を先に作り、修正前の挙動と修正後の結果を分けて保存する。**20/20 actual runと修正後capture self-testは未取得**。

**RC-06の実装候補を別Draft PRへ切り出した（2026-11-02）。** [PR #772](https://github.com/hat47x/sei-cognition/pull/772)はH2の実テスト20件の完全ID照合・skip拒否・旧Evidence保全を`tools/capture_issue_000073_h2_runner_selftest.py`および合成自己試験に実装する。GitHub上のソースID一致・変更範囲は静的確認済みだが、**対象Python self-test、現行fixtureの20件actual run、capture actual runは未実行**。#772はDraftのまま資格確認を行い、main実装済み・合格済みとは扱わない。#768の文書計画は実装・humanの証拠と独立に維持する。

**次の受入シナリオ（既存H1/H2と [#677](https://github.com/hat47x/sei-cognition/issues/677) のCT-01〜06への追補、実行未了）。**

| ケース | 入力・変化 | 観測すること | 主な追跡先 |
| --- | --- | --- | --- |
| RC-01 歴史と現在 | D1のbasis E0→E1、同一論理ID・異なるscope／digest、後続D2のLineage | D1の過去を保持し、今の用途への適合と未確認条件を区別 | #697/#687/#660 |
| RC-02 取得・解釈の欠落 | record 2件だけ直接解決、別の5文脈はPolicy本文内の対応候補、Unknown Q1は残存 | record未発見を内容不存在へ変換せず、候補位置と意味未確認を保つ | #677/#660/#767 |
| RC-03 比較と開示 | 同じ可視Projectionで非開示原本だけ異なる／Rule基準だけ変更 | 全件保証・秘密の推知・旧Ruleでの現在性保証を避け、適切な追加確認先を示す | #767／TEI #2516 |
| RC-04 Gateと行為 | 過去のallowを持つD1、Store／Authority変更、外部操作は未実行 | 当時の検査と現在のAction資格、Receipt・Effect・Outcomeを区別 | #691/#710、TEI #1174 |
| RC-05 Product Value | H1のreal Inquiry、H2の固定3条件、actual C製品出力の別票 | 正確性・first useful action・原record再閲覧・correction・capture/review taxを分離。単純baselineへの優位が無い結果も残す | ISSUE-000073 |
| RC-06 Evidence保全 | H2のテスト欠落・skip・同数別ID・`--replace`前提失敗 | 偽PASSを拒否、失敗診断を残し、既存Evidenceを保護 | ISSUE-000073 |

**責任と判断待ち。** SEIは問いと根拠・認識上の残余、H1/H2の判断再開を扱う。Cross-Consumerの比較可能性はTEI #2516、どの追加証拠・専門性が必要かを選ぶ認知MethodはSEI #767、記録・解釈をどの製品が保有するかはSEI #711、組織固有の意志や引継ぎはSEI #677が扱う。Lineageの向き・撤回端点と受理への効果、basisが参考資料か成立必須根拠か、実行・公開の資格は各Ownerの判断に残す。外部Harness・複数AIの同意を独立した根拠や人間の承認として加算しない。

**進め方。** 最初にRC-06のcapture再現・修正を実施し、H1の実再開と既存H2 pilotは可能な範囲で並行して観測する。続いてRC-01/02のread-only再開票、RC-03/04の現在利用・開示・実行境界を既存ConsumerのEvidenceで補強する。証拠は`source-static / synthetic executable / source-bound executable / actual human / actual provider`を分け、設計追加だけでISSUE-000073のResolution条件6〜8を成立させない。


### 2026-11-02 後続追補：問い相対の十分性と、再開後に意味のある観測を選ぶ方法

**成熟した設計上の区別（検証計画の追加）。** [SEI #767 P5/P6](https://github.com/hat47x/sei-cognition/issues/767)と[Draft PR #770](https://github.com/hat47x/sei-cognition/pull/770)は、証拠の十分性を「資料が何件見つかったか」から、**現在の問いQを、その観測Oで判定できるか**へ具体化した。これはISSUE-000073の認識の継続性へ接続できる。ただし、既存H1/H2の設計・Human Evidenceと、#767/#770の純粋合成Method研究を分離する。

**問いの種類ごとに、再開の成功条件を変える。** 例えば、`Q1=過去のD1で何を判断したか`は当時の固定Decisionと根拠で答えられる場合がある。`Q2=現在もD1の前提が成立するか`は現在のSource・Rule・用途・権限の追加照合を要する場合がある。`Q3=前回確認後に関連変更が一度もなかったか`は最終Snapshotが同じでも、区間中の追加・離脱・遅着訂正を覆う履歴を要する。Q1の復元成功をQ2/Q3への回答済みと扱わない。

**合成世界での識別性と十分性。** 固定した世界集合Wと問いQ、観測関数Oについて、すべてのA,B∈Wで`O(A)=O(B) ⇒ Q(A)=Q(B)`なら、**そのW内では**OはQを識別するのに十分な情報を持つ。一組の世界を区別するProbeの存在はW全体の十分性を示さない。また、Wへの新世界追加、実Providerの対象集合・Revision・アクセス範囲変更後の適用も別検証である。#770のW1〜W4では`count+has_C+has_E`がQを区別できるが、公開追加世界W5でW3/W5の観測が一致しQが異なり、固定Corpusでの成立が崩れる。#770の**最初の6/6 PASS（その後、追加7件を含め13/13 PASSと報告）は公開合成反例に限定**し、実SEI Productや現実の全世界の十分性を証明しない。

**有用な次の確認を選ぶ。** H1で再開に迷ったとき、認知Methodの候補は(1)現在の問いと必要な範囲を定める、(2)観測が同じなのに答えの異なる仮説を明示する、(3)区別し得る追加Source/履歴/独立Oracleを探す、(4)実際に利用できるToolと開示許可を確認する、(5)実行された確認と結果を観測し、残るQuestionへ戻す、の順で検討する。これは説明用の分析手順でありSEIの新しい公式状態機械ではない。明示された`Method Definition / Realization / Application`とApplicationの`input/output/residual/provenance`参照を再利用し、Method候補→実Tool発見→許可→実行→観測→用途適合の各段階を別Evidenceとする。

**認知の独立性。** 同じBrief/Oracle/Promptを複数AIに配信して得た一致は、元の独立根拠が増えたことを意味しない。モデルの人数ではなくSourceの系譜と実際に利用したOracleを確認する。外部へ開示したVが二つの内部世界で同じで、Qだけが異なる場合、外部Harnessは識別を完了できない。その際は内部の権限あるProductへ限定確認を委ね、秘密の要素・個数・存在を低権限側へ説明しない。提案の生成自体を禁止するのではなく、当該Claimの成立範囲と公開可能な説明を調整する。

**異なるConsumerと世代を揃える。** TEI [#2516](https://github.com/hat47x/tei-platform/issues/2516)の用途相対Projectionでは、二つのConsumerが同じ数値を示してもScope/Grain/Rule/Join・有効時点の違いを検査してから比較する。また、一つの作業で複数Sourceを読む場合、個別digestの一致と**共同で同じClaimを支持する版の組合せ**は別である。SHOの資料位置・Occurrence/Revision、MMIのSource identity、TEIのSource/Correspondence/Meaning/Generation/Publicationの区別を利用して、H1の次の調査候補へ接続する。外部HarnessのSkill候補`yi-sei-inquiry`は[SEI #769](https://github.com/hat47x/sei-cognition/issues/769)が所有し、Tool discoveryやSkill文書の存在を実行可能なProduct能力へ昇格させない。

**既存受入票への追加（RC-01〜06と独立の後続ケース）。**

| ケース | 公開合成入力と対照 | 証明する範囲と観測 |
| --- | --- | --- |
| **RC-07 問い相対のProbe** | Q=全対象が正値か。W1〜W4で一致したProbeを、同じ観測でQが異なるW5へ適用 | 二世界の識別、固定Corpus全体のQ十分性、未知世界を含む実Product資格を三段階で説明する。次の識別的なSource取得候補と未確認を示す（#767/#770の合成証拠を参照し、ここでの実行・H1成果は未成立） |
| **RC-08 同じ現在値・異なる履歴** | t0/t2のDecision対象・集計が同じで、別世界だけt1にRelation加入→離脱。さらにSource/Rule改版または遅着訂正を投入 | `いま同じ`と`前回から変更なし`のClaimを分け、後者に必要な区間履歴の取得範囲と不足を明示。H1の現在利用／再確認へ接続（TEI #1125/#2505/#2516） |
| **RC-09 Tool/Skill・情報開示** | 同一の開示Projection、異なる非開示原本、ToolありSkillなし／Skillありの二条件、同Source由来の複数Agent同意 | Skill候補・実Tool/版・許可・実観測・公開可能な結果を別証拠とし、独立根拠の誤加算・秘密の存在推知・不要な追加質問を別々に記録（SEI #769/#767、TAI Draft #270） |

**順序とProduct Value。** RC-07は#770の既存合成Referenceを再利用して別の実装を起こさず、RC-08はread-onlyのSource/履歴照合案から始める。RC-09は権限付き実接続のOwner・提供Toolが確定してから実施する。H1本番観測の最初の6問とH2の3 fixture×3 conditionをそのまま保持し、追加研究は回答固定後のoperator評価、または独立した合成横断票で扱う。成功条件は「答えを速く言えたか」だけではなく「問うているClaimに十分な根拠があるか、まだ何を調べる必要があるかを利用者が正しく理解したか」とし、余分な確認・取得費用・capture/review負担をともに測定する。

**実施資格。** #770の最初の6/6 PASSと、追加7件を含めた13/13 PASSはPython 3.13.5による公開合成Referenceの局所実行であり、別GitHub Draft PRの限定Evidenceである。SEI #769のSkill、本PRのRC-07〜09、現行SEI CLI/Goの認知Method実行、実Source Provider、H1/H2人間評価は**NOT RUN**。Product Value・Owner意味受理・現在の業務実行資格のEvidenceは変更しない。


### 2026-11-02 追補：観測同値類・複数Readの共同資格・限定継続

**設計上の成熟点。** [SEI #767 P6追補](https://github.com/hat47x/sei-cognition/issues/767)と[Draft #770](https://github.com/hat47x/sei-cognition/pull/770)では、従来の「固定Corpus W全体で問いQを識別できるか」に加え、**現在得た一つの観測oと整合する世界だけならQを限定的に判断できるか**を検討した。2026-11-02時点で既存6件＋追加7件の**公開合成Python 13/13 PASSが別Draft PRで報告**され、両ファイルのGit blobも記録されている。これは#770の局所合成試験のEvidenceであり、本IssueのH1/H2、実Provider、現行CLIの実行証拠へ加算しない。

**判断の単位を問いと観測の組に保つ。** 説明用の固定世界集合Wにおいて`C_W(o)={w∈W | O(w)=o}`とすると、`C_W(o)`が非空かつQが全要素で同じ場合に限り、その観測セルではQを限定的に説明できる。Wの全セルが同じ性質を持つ場合はW全体で十分性が成立する。セルが空なら`unmodeled-observation`、同じセルにQが異なる世界があれば`unknown-in-fixture`とし、否定結果を捏造しない。値が一致するセルも`true-in-fixture`／`false-in-fixture`の**合成範囲付き結果**に留める。

| RC-07の追加判別 | 合成入力 | 必要な観測と反証 |
| --- | --- | --- |
| **RC-07a 局所的な利用可能性** | W1〜W4、Probe=`count+has_C` | Corpus全体は不十分だがW1の観測セルはtrue、W2はfalse、W3/W4はunknown。**局所で答えられる問いを全件未回答へ一律縮退しない** |
| **RC-07b 追加世界での訂正** | W1〜W4では`count+has_C+has_E`でW3セルがtrue、新たにW5（D=0）を追加 | 同じ観測でQが異なるため`unknown-in-fixture`へ更新。旧Application・当時のWと判断理由を歴史として保存し、現在の適用だけ再評価 |
| **RC-07c 想定外観測** | 既存Wに対応しない新しいobserved signature | `unmodeled-observation`を`false`や対象不存在へ昇格させず、対象モデル・Sourceへ戻る次のInquiryを示す |

**追加取得と観測モデル拡張の関係。** 固定Wについて識別的なProbeを追加すれば観測セルは細分化され、旧unknownを限定的に解消できる場合がある。一方、同じProbeでもWに新たな可能性が加われば、旧限定結論がunknownへ戻り得る。これはApplicationの履歴が失われることではなく、**現在の問いに対する知識範囲が更新されたこと**である。実対象がWで覆われること、Source/Ruleの正本、各Observationの真正性はProduct/Ownerが別に確認する。

**複数Readを一つのClaimへ結合する資格。** 各Readの`result=pass`、単体digest、正しいTool応答だけでは、複数Readが**同じ対象世界・同じ問いに共同で適用できる**と証明したことにはならない。最小反例は`t0:A=1,B=0`、`t1:A=0,B=1`で、A@t0=1とB@t1=1を結合すると、どちらの実Snapshotでも偽の`A,Bとも正値`を作る。現行の公開合成Referenceの`joint_read_candidate`は必要フィールド、重複、epochとSource revisionのラベル混合を検出する**事前検査**であり、ラベル一致は実ReadのSource/Scope/Provider正当性を証明しない。異版でも有効な橋渡し（bridge）や用途限定の局所Claimが成立するかはTEI [#2516 W9/W10](https://github.com/hat47x/tei-platform/issues/2516)、#2605等のOwnerへ戻す。

| RC-08の追加判別 | 合成入力 | 期待する判断 |
| --- | --- | --- |
| **RC-08a 混合epoch** | A@t0 と B@t1、どちらも単独では正しく観測 | 合成の`mixed-epoch-unknown`へ戻す。実際の共同Snapshotや有効なbridgeがあれば既存ProductのEvidenceで別途確認 |
| **RC-08b 同epoch・異版** | epochは同じ、Source revisionだけ異なる | 合成の`mixed-source-unknown`。同じ文字列epochだけを共同資格とみなさない |
| **RC-08c 部分Claim** | D1側Sourceは必要集合が完全、D2は取得途中。問うClaimがD1単独／D1×D2 JOINの2種類 | D1単独に必要な情報が成立する場合はその問いを先に進め、JOINのClaimは必要依存の不足とともに保留する |

**開示の資格は結果の後にも必要。** 同じ外部可視Projection Vを与える二つの内部世界でQが異なる場合、外部Consumerの観測だけではそのQを判断できない。内部ProductにQの限定結論が得られても、結果やProbe名・失敗理由・隠れた対象の件数の公開は別の資格を要する。Draft #770は`result_release_authorized`を**信頼済み引数として与えた合成試験**に過ぎず、Tool名、Timing、Trace、反復照会、実OS／Networkの情報流出を防いだ実証ではない。実開示のOwnerはTEI #2515・TAI #232等に保持し、SEIの再開票では開示可能な説明にとどめる。

**Product Valueへの転換。** 再開後の認知支援は、「すべてを取得してから進む／不足があれば全部停止する」という二択を解消し、**根拠の足りている限定Claimについて調査や判断を前進させ、足りないClaimだけ必要な追加観測を提案する**ことを価値候補とする。H1では元の回答を固定した後、(1)限定結論の範囲、(2)保留の理由、(3)実際に取った次の一手、(4)誤った混合Read・誤保証の有無、(5)不要な再取得・人の確認負担をoperator側で観測する。H2の固定素材・盲検割当・評価指標は変更せず、合成研究の結果をHuman Evidenceへ転用しない。

**依存と状態。** 局所認知方法と次Probeの選択は#767、Question/Observation保存契約は#711、Method有効性の学習と独立holdoutは#450、外部Skillは#769／TAI Draft #270、Consumerの共同ReadはTEI #2516のまま。新しいContract enum、第二のClaim Store／Universal State Machine／Host、別の中央承認Gateを導入しない。**本PRは上記の計画・評価文書を更新するもので、RC-07a〜c/RC-08a〜cの実SEI・実Human検証はNOT RUN**。


### 2026-11-02 追補：調査計画自体の開示境界と、必要根拠・実取得・公開結果の分離

**成熟した横断反例。** SEI [#767 P6](https://github.com/hat47x/sei-cognition/issues/767)と[Draft #770](https://github.com/hat47x/sei-cognition/pull/770)は、最終回答が両世界で同じ`not-confirmable-from-released-information`でも、**非公開Actionの存在に応じて外部に提示するProbe候補名、Tool一覧、呼出し順、診断、件数が変化すると、その違い自体が秘密になる**ことを公開合成例として示した。TEI [#2516 W10 J-08〜11](https://github.com/hat47x/tei-platform/issues/2516)は、Claimの必要根拠、実Providerが取得した範囲、Consumer/Agentへ見せた範囲をそれぞれ別の観測対象とした。SEIのDecision Continuityでも、過去の判断や現在の次の一手を外部Harnessへ送る際に同じ区別が必要である。

**三つのFootprintを混ぜない。**
1. **Proof Dependency**：ある問いQを判断するために必要な対象、Source/Role、Rule・Relation/Field、Scope/対象全件性、時点、独立Oracle。画面に表示されないValidation Ruleなどが必要な場合もあり、未列挙依存は「不要」ではなく未確認。
2. **Actual Acquisition**：Product/Providerが実際に読んだRelation/Field、Snapshot・Source版、Cache/Overfetch、実Readの観測可能な証拠。宣言Mappingの狭さや返却JSONの狭さだけでは、実際のDBアクセスが最小だったとは言えない。
3. **Consumer-visible / Planner-visible**：外部に公開した回答・Source・Tool JSONだけでなく、提案する次の問い、Tool候補数・名称・Args、Error、Trace、Status、実呼出し順等の外部観測可能な事実。認知結果を秘匿してもPlanが秘密を漏らし得る。

**公開上の観測同値条件（合成研究上の不変条件候補）。** 同じ公開View、公開済みTool/Capability一覧、同じ用途Q、同じ公開許可条件を持つ二つの内部世界S0/S1で、秘密のActionだけが異なる場合、外部に許可された可視Planと公開診断が秘密の有無だけで変化しないことを比較する。公開が正式に許可された差は、何も違ってはならないという扱いにしない。これは情報流を評価するための**合成基準**であり、実OS/Network、Timing、Log、反復照会、Product内部の非干渉保証ではない。未知Toolは`unsupported`、未観測結果は`unknown`として扱い、Tool Discoveryの表示を実Tool/権限の実在とみなさない。

**RC-09への具体的追補（重複ケースを新設しない）。**

| ケース | 一致する公開入力と異なる内部条件 | 期待する証拠 |
| --- | --- | --- |
| **RC-09a Plan候補の漏出** | 同じ公開View・同じ公開Tool一覧。片方だけに秘密Actionがある | 最終回答だけでなく公開Probe候補と説明・件数・呼出し計画の差を確認。非公開依存で分岐する悪いPlannerを識別 |
| **RC-09b 必要根拠と実取得の差** | 表示Resultは同じ。片方のProviderは公開必要Fieldのみ、もう片方は秘匿列までOverfetch | 表示が同じことを実Read最小性の証拠にしない。実Providerの取得Witness未観測なら`physical-read-unverified` |
| **RC-09c 表示値と暗黙Rule依存** | 公開画面値は同じ。内部のRule必須入力が異なり、評価結果が変わる | 表示FieldだけでProof Dependencyを閉じない。Rule実評価と外部結果開示を別に記録 |

**人間の再開とMethodの価値。** 既存H1/H2の回答・盲検条件を維持し、H1回答固定後のoperator票では、(a)利用者が追加調査先を選べたか、(b)実際に使えるToolか、(c)必要根拠と取得情報が対応したか、(d)公開された計画や診断が過剰な情報を漏らしていないか、(e)余分なSource再取得・修正負担を分ける。安全な限定Planが問いを解けなかった場合も、機密性PASSだけをProduct Valueの達成へ昇格させない。

**別研究の証拠資格。** Draft #770の先行2 Moduleは**13/13 PASS**、追加の`test_probe_planning_visibility.py`は**単独7/7 PASS**が報告された。追加後の3 Module一括回帰、実Tool/OS/Provider/Network/Timing、SEI本体、H1/H2人間試験は**NOT RUN**。合計20件を一括PASSと記録しない。実Disclosure/Tool ActionはTEI #2507/#2515/#2516、TAI #232、実ReadはTEI #2628等の既存Ownerが担当する。SEIはInquiry/Methodにおける公開可能な次の問い・Probe提案の認知的妥当性を評価する。


### 2026-11-02 追加統合：調査計画の開示、必要根拠と実取得、Evidence取得修正の分離

**新たな失敗形：回答本文が同一でも調査計画が秘密を露出する。** [SEI #767](https://github.com/hat47x/sei-cognition/issues/767)のP6、[Draft #770](https://github.com/hat47x/sei-cognition/pull/770)、[TEI #2516 J-08〜11](https://github.com/hat47x/tei-platform/issues/2516)、[TAI Draft #270](https://github.com/hat47x/tai-pleroma/pull/270)を照合した。外部Consumerから見えるView・許可されたTool集合が同一の二つの内部世界S0/S1で、非公開Actionの有無だけが異なるとする。最終回答を双方同じ`not-confirmable`へ揃えても、候補Probe、Tool名、順序、エラー、詳細理由、件数が秘密に応じ変化すれば、**調査計画そのものが存在情報を伝える**。認知Methodの「どの調査が有益か」と、Consumerへ「どの調査候補を見せてよいか」を別条件とする。ツールの許可・実開示・Network/OS強制は既存Product/TAI/TEIの責務であり、SEIに第二Policy Engineを作らない。

**認知的な必要情報と実Readを同一視しない。** [TEI #2516 W10](https://github.com/hat47x/tei-platform/issues/2516)の三つの観測範囲を既存のMethod Applicationのinput/output/residualと受入票に対応させる。

| 対象 | 問いと証拠 | SEI側の扱い |
| --- | --- | --- |
| Claim Proof Dependency | Qを答えるために必要なSource/Role/Rule/Relation/Scope/Time/Oracle。画面に出ないRule入力も必要な場合がある | 取得未列挙を「不要」とせず、根拠上の残余を保持 |
| Actual Acquisition Footprint | 実際のQuery/Provider/Cache/Toolが読んだ対象と版・scope・完全性。返却JSONが狭くても秘密列をOverfetchした可能性 | 実Readが確認できなければ`physical-read-unverified`、宣言だけで取得最小性や全件性を保証しない |
| Consumer/Planner-visible Footprint | 画面・SHO・外部AI・Tool JSON/Traceへ実際に露出した本文、候補Action、Probe名、引数、診断、順序 | 開示許可に沿って説明を限定し、実OS／Networkや反復照会での非干渉は別受入 |

**既存RC-09の追加反例（新しい製品Schemaは要求しない）。**

| Case | 固定公開合成対照 | 期待する判別と追跡先 |
| --- | --- | --- |
| **RC-09a Planner-visible leakage** | 外部可視V・許可Tool集合・最終回答は同じ。内部に秘密Actionがある世界だけ提案候補が増える | 公開候補／説明・Tool discovery・Traceを比較し、秘密の存在を示す計画が露出しないかを問う。SEI #767/#770は候補の評価、TAI #232/TEI #2515/#2507は実機密・Action適合を担当 |
| **RC-09b Declared/actual gap** | 同じ表示入力と返却JSONだが、別世界では非表示Rule依存やProviderの秘密列Overfetchがある | 依存集合・実物理Read・開示の差を示し、確認できない項目はUnknownへ。実Provider取得はTEI #2628、Rule依存はTEI #2624/#1129 |
| **RC-09c Consistent joint evidence** | 各Sourceは個別にdigest/取得成功でも、Manifest/Source改版やRead epochが混在 | Qに必要なSourceが**共同で**一つのClaimを支持する証拠を確認。全部の再取得を必須とせず、局所依存だけの再確認と正式bridgeをTEI #2516/#2604で評価 |

**検証・費用の分離。** 方法候補やToolの発見、実Call、実取得・実開示、外部AIの応答、Ownerの受理は異なる観測である。誤保証、不要なSource再取得、確認時間/Token、秘密漏洩、許された部分作業を別の評価欄で比較し、単一スコアへ合算しない。H1の初回6問とH2の固定比較素材・盲検手順は維持し、新反例は回答固定後のoperator票または別合成研究へ収容する。CSWの自由な探索自体へ外部承認Gateを挿入しない。

**Evidence更新（2026-11-02）。** [SEI Draft #770](https://github.com/hat47x/sei-cognition/pull/770)は公開合成の先行13件にPlanner-visible leakの新規7件を追加し、新規7/7 PASSを報告した。ただし**追加後の3 Module全20件一括回帰は未実行**で、実OS/Tool/Skillの機密非干渉を実証したものではない。別途、H2 captureの修正候補を[Draft #771](https://github.com/hat47x/sei-cognition/pull/771)として2ファイルに記録し、期待ID完全性・skip・同数別ID・`--replace`失敗時の旧Evidence保全を実装案と合成セルフテストに落とした。**#771のPython actual self-testと現行H2 actual 20件実行は未取得**。Draft PRの作成や静的照合をEvidence PASSへ昇格させない。

## Deliverables

- `product/value/SEI_DECISION_CONTINUITY.md` — V1〜V8をDecision Continuityへ接続するProduct Value synthesis。**Design Evidence available**。
- `product/interaction/SEI_FIRST_USABLE_PRODUCT_SLICE.md` — first sliceのProduct Design baseline。**Design Evidence available**。
- `architecture/SEI_INTERACTION_WORKING_SET_ARCHITECTURE.md` — state authority、resume Projection、semantic commit、AI境界のReference Architecture。**Design Evidence available**。
- prototype / probe — Local Single-Node上でE1〜E8を再現する`runtime/go/interactionprobe`とrunner / verifier / captureを実体化済み。**actual E1〜E8 executionはgo1.25.14で2026-10-09にPASS（Scoped Executable Evidence）**。
- human review record — H1のresume usability観測結果。**Not Yet Observed**。
- comparative Product Value review — H2のbaseline比較、capture tax、誤帰属、correction負担の観測結果。**Not Yet Observed**。
- Requirement audit — CR-73.1〜10を再照合済み。CR-73.8 / CR-73.9だけを一つのfailure boundaryとしてREQ-0023 / SCN-0019へformalizeし、それ以外はexisting REQ / Product-local設計 / human Outcome評価へ戻した。

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

### Current resolution status — 2026-10-10

- 条件1、2、9、10: **Design / Requirement auditの範囲では成立**。
- 条件3〜5: **Local Single-Node上のProduct-local probeの範囲で成立 (2026-10-09、current source closureは2026-10-10に39 / 39 blob一致を確認)**。go1.25.14でE1〜E8の必須18 testがすべてpassし、verifierもfindings 0でPASSした（tested commit `694ec5805c00a8bae9034e15ee0d1589e40f6fd8`、`evaluation/personal-inquiry-decision/evidence/issue-000073/e1-e8.json`）。条件3はE1〜E5、条件4はE6 / E7のpartial commit・stale writeを黙って受理しない挙動、条件5はE8のexternal AI context / provisional response境界に対応する。ただし**事前配置のGo 1.25.14によるScoped Executable Evidence**であり、bootstrap wrapperのpinned archive materialization経路、他OS / 他Storage profile、Production永続層は対象外。E1〜E8 PASSは条件6〜8のhuman observationもProduct Valueも成立させない。
  - source closureが同一である限り、条件3〜5を維持するためだけのE1〜E8再実行は優先しない。`interactionprobe` / `semanticruntime` / Go依存定義 / runnerの意味が変わった場合に再実行する
  - 同じ2026-10-09には、別経路として**external exact-source handoff**のpreparer / 送受信mechanicsも実体化され、限定範囲でPASSしている（`external-execution-bundle-mechanics-2026-10-09.json`）。これはexact HEADのclone、expected HEAD不一致拒否、dirty source拒否等の**引き渡し経路のmechanics**であり、上記E1〜E8 actual PASSとは別のEvidenceである。handoff bundleを実際に外部nodeへ渡して実行した結果は未取得
- 条件6〜8: H1 / H2とProduct Valueのcounterfactual observationは**Not Yet Observed**であり、未成立。H2のprovenance-first共通runnerとDecision-specific validationは実装済みだが、reviewer response未取得のため条件7を満たしたとは扱わない。

したがってStatusは**Open**を維持する。条件3〜5がExecutable Evidenceとして成立しても、残る条件6〜8（H1 / H2 human observation、capture / review overheadの評価）が未観測である。Design文書が完成したこと、REQ-0023 / SCN-0019をformalizeしたこと、probe sourceやEvidence受入れtoolingを実装したことだけではResolvedにしない。prototypeが技術的にPASSした場合も、それだけでDecision ContinuityのAdoption / Outcome Evidenceが成立したことにはしない。

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

Plan / document整合は、変更範囲に応じて`plan/scripts/check_plan_registry.py`と`plan/scripts/check_document_review_registry.py`で確認する。E1〜E8のcurrent Executable Evidenceを取得するときの標準入口は、one-command captureとする。

```text
python3 tools/test_run_issue_000073_resume_first_evidence.py
python3 tools/test_verify_issue_000073_resume_first_evidence.py
python3 tools/test_capture_issue_000073_resume_first_evidence.py
python3 tools/test_prepare_issue_000073_external_execution_bundle.py
python3 tools/test_run_issue_000073_external_execution_bundle.py
python3 tools/capture_issue_000073_resume_first_evidence.py --expected-head <canonical-commit-sha>
bash tools/bootstrap_issue_000073_resume_first_evidence.sh --expected-head <canonical-commit-sha>
python3 tools/prepare_issue_000073_external_execution_bundle.py --expected-head <canonical-commit-sha> --output-dir <outside-repository-directory>
python3 tools/run_issue_000073_external_execution_bundle.py --bundle <bundle.gitbundle> --manifest <bundle.manifest.json> --sha256sums <bundle.SHA256SUMS> --work-dir <new-work-dir> --result-dir <result-dir>
python3 tools/test_capture_issue_000073_h2_runner_selftest.py
python3 tools/capture_issue_000073_h2_runner_selftest.py --expected-head <canonical-commit-sha>
python3 evaluation/personal-inquiry-decision/test_decision_continuity_review_runner.py
```

captureはrunner → verifier → Evidence保存をfail-closedに連結する。runnerがblocked / failならverifierへ進まずraw診断を保存し、verifier failureをPASSへ昇格させない。既存Evidenceの置換は明示的な`--replace`を要求し、一時artifactはcheckout外へ置いてclean-tree preconditionを自ら壊さない。

個別診断が必要な場合だけrunner / verifierを直接使う。

```text
python3 tools/run_issue_000073_resume_first_evidence.py --expected-head <canonical-commit-sha> --output <evidence-record.json>
python3 tools/verify_issue_000073_resume_first_evidence.py <evidence-record.json> --json-out <verification-record.json>
```

runner / captureはcheckout外で独立に取得したcanonical expected HEADとの完全一致、clean committed HEAD、required sourceとHEAD blobの一致、Go 1.25.xをpreconditionとする。verifierもEvidence record内の`expected_head == head`と`head_matches_expected=true`を必須にする。preconditionを満たせずblockedとなった場合はrepository test failureともPASSとも扱わない。2026-09-18の実行環境ではhost Go 1.23.2であり、Go自身のtoolchain自動取得はnetwork / DNS制限でblockedだった。2026-10-07にGo 1.25.x bootstrap入口を追加してrepository tooling上の取得経路を具体化したが、この入口によるactual E1〜E8 runは2026-10-07時点では記録しておらず、Evidence状態はNot Yet Verifiedだった。2026-10-09に事前配置のgo1.25.14で取得したE1〜E8 actual PASSにより、この状態は更新された（現況は上の一覧を正とする）。

runner preflight / verifier / capture workflowについては、current sourceに対する2026-09-18 actual self-test PASSをmachine-readable Evidenceへ固定済みである。ただしこれはEvidence受入れ経路の検証であり、Go 1.25.xで`interactionprobe`を実行したEvidenceへは昇格させない。

2026-10-09のexternal handoff self-testは、preparer / test sourceのGit blob SHA-1とSHA-256をGitHub上のcurrent sourceへ照合したうえで、exact blob materialization上で5件を実行し5/5 PASSした。これはGit bundle transport / fail-closed mechanicsのExecutable Evidenceであり、actual SEI checkoutからのbundle生成やGo 1.25.x interactionprobe実行には昇格させない。

H2 shared runnerのDecision経路には`test_decision_continuity_review_runner.py`があり、blinding、declared provenance、stage gate、Decision固有response validation、Evidence layer分離に加え、current repository manifest / fixtureを直接開くintegration caseも回帰test sourceとして固定している。

2026-09-18に`capture_issue_000073_h2_runner_selftest.py`と、そのfail-closed self-testを追加した。captureはclean committed HEAD、外部から独立に与えるcanonical expected HEADとの完全一致、required sourceのHEAD一致、matched-set manifest / 3 fixtureを含む13 source binding、正確なDecision regression test commandを固定し、test failureをPASSへ昇格させない。capture workflow self-testはactualにPASSしmachine-readable Evidenceへ固定した。Decision regression test本体もexact blob-validated materializationでは8 tests / 8 PASSをactual確認したが、**native clean-HEAD actual captureはNot Yet Verified**のままとする。

```text
runner / verifier / capture exists
  != E1-E8 actual PASS

environment cannot acquire Go 1.25.x
  != interactionprobe FAIL
  != E1-E8 PASS

E1-E8 actual PASS
  != H1 / H2 human review
  != Decision Continuity Product Value established
```

未実行の実験をPASSと扱わず、Design EvidenceをExecutable / Operational / Adoption Evidenceへ昇格させない。

## Natural Japanese review

Product Value、Decision Continuity synthesis、Value Model V1〜V8、Product Shape、PMS-03、Product Interaction、Packaging、REQ-0001 / 0005 / 0006 / 0010 / 0011 / 0014 / 0019 / 0023、SCN-0003 / 0013 / 0016 / 0018 / 0019、ADR-0005 / 0010 / 0028 / 0029、Interaction probe、ISSUE-000073 Evidence runner / verifier / captureを照合した。

従来のIssueは「再開できるUI / prototype」を中心に十分深く設計されていたが、そのままではSEI自身の仕組みだけを評価する自己完結的な検証になり得た。そこでDecision Continuityをcross-axis Product Outcomeとして上位価値へ接続し、raw chat / chronological note等の単純baselineとのcounterfactual reviewをResolution条件へ追加した。

2026-09-16の追加監査では、CR-73.1〜10を機械的にStable化せずcurrent REQ / SCNへ再照合した。resume、AI provisional boundary、Progressive Explicitness、working-set non-authority等は既存Requirement、Product-local設計またはhuman Outcome評価へ戻し、既存REQでは直接禁止できなかったpartial commitとstale writeだけを「successful canonical commitの整合性」という一つのREQ-0023へ統合し、SCN-0019でAcceptance化した。transaction、ETag、digest、snapshot token等の実現方式をUniversal semanticsへ昇格させていない。

2026-09-17には、E1〜E8の実行入口をrunner単体からrunner / verifier / one-command captureのcurrent implementationへ同期した。2026-09-18にはEvidence受入れ経路のcurrent sourceをactualに再実行し、runner preflight、verifier、capture workflowのself-testをいずれもPASSとしてmachine-readable Evidenceへ固定した。同日Go 1.25.x取得経路も再確認したが、当時のexecution environmentではhost Go 1.23.2かつ外向きDNS / network制限が継続していたためactual E1〜E8 runは未取得だった。その後2026-10-09に、事前配置のgo1.25.14を持つ別環境でactual E1〜E8 runを取得した。

H2についても同日、073専用の別runnerを増やさず、既存Inquiry Continuity review runnerをDecision manifestへ対応させた。reviewer provenance、stage gate、Decision固有validation、Evidence exportを一つの経路へ収束させ、provenance固定前に提示されたR1 materialは回答未固定のprotocol exposureとしてのみ扱う。H1 / H2ともactual human observationがないためNot Yet Observedのまま保持する。

同日の後続監査ではcurrent manifest / fixtureのstatic整合とactual-repository integration test sourceまで確認し、そのfocused Python testをclean HEAD / source binding付きでEvidence化するcapture入口も追加した。capture workflow self-testのPASSは受入れ経路だけのExecutable Evidenceであり、Decision regression actual PASSやH2 human observationへは昇格させない。

SEIのsemantic integrityが高いだけではProduct Valueとせず、historical誤帰属、Recommendation / Decision混同、再構成負担を実際に減らし、その利益がcapture / review overheadを上回るかまでを見る。価値差がない結果もProduct hypothesisを修正する正当なEvidenceとして扱う。意味、要求強度、留保、Evidenceの高さを固定したうえで自然な日本語として読み直し、最終意味監査を実施した。

2026-10-02には、ADR-0035（Proposed）に沿って、H2の解釈規則へ、主な指標（誤帰属、誤った昇格、プロバイダ交換後の継続）と副次の指標（再開の速さ等）の重みづけを提案として追記した。Resolution条件とEvidenceの高さは変えていない。

2026-10-09には、private GitHubへの接続可否とsource identityを分離するため、Git bundleによるexternal exact-source handoffを追加した。exact committed sourceで5件のmechanics testを実行し、同一HEADへのcloneと、expected HEAD不一致・dirty source・repository内output・暗黙上書きの拒否を確認した。実行環境のtransportを改善しただけであり、E1〜E8、H1 / H2、Decision Continuity Product ValueのEvidence強度は引き上げていない。自然な日本語として読み直し、既存の停止線と規範強度が変わっていないことを確認した。

同じ日に受け側runnerも追加し、handoffのSHA-256 / source identity検証、exact clone、post-clone bundle verification、既存bootstrap / capture実行、blocked非昇格までを一命令へ収束させた。exact committed sourceによる4件のmechanics testは4/4 PASSしたが、synthetic bootstrapを用いた受入れ試験であり、actual E1〜E8のEvidenceには数えていない。

2026-10-10には、actual E1〜E8のtested commitとcurrent developの実行対象closureをGit blobで再照合した。`interactionprobe` 22 file、`semanticruntime` 13 file、Go依存定義2 file、runner / verifier 2 fileの計39 fileが全て同一だった。これにより既存のScoped Executable PASSをcurrent source closureへ適用できることをmachine-readable Evidenceへ固定した。これは再実行ではなく、未変更sourceへの適用性確認である。以後の高情報量作業はH1 / H2 human observationへ移す。

2026-10-25には、H2 Decision Continuityの比較素材②・③についてRaw Chat／時系列ノート／SEI Resume間の既知の表現差を補正した。原典`scenario.phase_1`、`reference_state`とケース①のTEI Reference用固定素材は変更していない。差分再発を防ぐ2テストを既存preflightに追加し、対象をpreflight 7件・shared-runner 8件・analysis 5件の計20件とした。さらに既存`tools/capture_issue_000073_h2_runner_selftest.py`を3スイートの`unittest discover`実行へ拡張し、15 source binding、独立指定expected HEAD、clean checkout、不一致時のfail-closedを維持した。対応するsynthetic capture self-testも新しい3スイート検出に合わせて更新した。

本更新で確認したのはGitHub current sourceとfixture差分の静的整合である。**修正後20件のPython actual runおよびcapture self-test actual runは未取得**であり、2026-09-18の旧fixtureに対する8/8 PASSを新fixtureに転用しない。E1〜E8の既存Scoped Executable EvidenceとH1/H2 Human Evidenceは引き続き分離する。ISSUE-000073はOpenを維持し、次に必要なのはsource-bound実行結果とH1/H2の人間による観測・capture/review負荷の記録である。
