# ISSUE-000073: resume-firstな最初の実用Product Sliceを定義・実証する

Status: **Open**  
Priority: **1**  
Related ADRs: **ADR-0005, ADR-0010, ADR-0028, ADR-0029**  
Updated: 2026-10-09

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

## Current implementation / Evidence status — 2026-09-18

現在はDesign baselineだけの段階から、E1〜E8を再現するGo interaction probeと、runner・verifier・one-command captureを持つ段階へ進んでいる。ただし、sourceや受入れtoolingの存在とactual E1〜E8実行結果は分ける。

- Decision Continuity synthesis、first usable Product Slice、Interaction Working-Set Architecture: **Design Evidence available**
- CR-73.8 / CR-73.9: **REQ-0023 / SCN-0019へformalize済み**
- `runtime/go/interactionprobe`: E1〜E8に対応するprobe / test sourceあり
- `tools/run_issue_000073_resume_first_evidence.py`: E1〜E8をmachine-readable recordへ束ねるrunnerあり
- `tools/verify_issue_000073_resume_first_evidence.py`: recorded tested commit、source blob / SHA-256、Go version、E1〜E8個別test結果を再検証するverifierあり
- `tools/capture_issue_000073_resume_first_evidence.py`: runner → verifier → Evidence保存を一命令でfail-closedに連結する標準入口あり
- `tools/bootstrap_issue_000073_resume_first_evidence.sh`: Go 1.25.xがhostにない場合、事前配置済みGo 1.25.xまたはSHA-256固定済みGo 1.25.14 Linux / amd64 archiveからtoolchainをcheckout外へ準備し、既存captureへ渡す入口あり。**bootstrap追加はE1〜E8 PASSを意味しない**
- bootstrap mechanics: exact committed script blobに対する`bash -n`、事前配置Go 1.25.xのcapture受け渡し、dirty-tree拒否、`--go`迂回拒否をsynthetic Git repositoryで**PASS**。Evidenceは`evaluation/personal-inquiry-decision/evidence/issue-000073/go125-bootstrap-mechanics-2026-10-07.json`。archive materializationとE1〜E8 actual実行は未検証
- runner preflight self-test: **PASS on canonical-HEAD-bound current source (2026-09-18); machine-readable delta Evidence recorded**
- verifier self-test: **PASS on canonical-HEAD-bound current source (2026-09-18); machine-readable delta Evidence recorded**
- capture workflow: **historical full self-test PASS retained; canonical-HEAD deltaは8 case actual + same-output focused preflight actualで確認 (2026-09-18)**
- E1〜E8 actual Go 1.25.x execution: **PASS (2026-10-09, tested commit `694ec5805c00a8bae9034e15ee0d1589e40f6fd8`, go1.25.14 linux/amd64)**。`go test -count=1 -json ./interactionprobe`の必須18 testがすべてpass、`go test`全体も31 pass / 0 fail。verifierもfindings 0でPASS。Evidenceは`evaluation/personal-inquiry-decision/evidence/issue-000073/e1-e8.json`と`e1-e8-verification.json`。**事前配置のGo 1.25.14によるScoped Executable Evidenceであり、bootstrap wrapperのpinned archive materialization経路は実行していない**
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

SEI側で明確な価値差が観測されなくてもFAILを隠さない。raw chat / simple noteで十分である、またはcapture overheadが利益を上回る場合は、Decision Continuity Product hypothesisを弱める・scopeを狭めるEvidenceとして記録する。

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

### Current resolution status — 2026-10-09

- 条件1、2、9、10: **Design / Requirement auditの範囲では成立**。
- 条件3〜5: **Local Single-Node上のProduct-local probeの範囲で成立 (2026-10-09)**。go1.25.14でE1〜E8の必須18 testがすべてpassし、verifierもfindings 0でPASSした（tested commit `694ec5805c00a8bae9034e15ee0d1589e40f6fd8`、`evaluation/personal-inquiry-decision/evidence/issue-000073/e1-e8.json`）。条件3はE1〜E5、条件4はE6 / E7のpartial commit・stale writeを黙って受理しない挙動、条件5はE8のexternal AI context / provisional response境界に対応する。ただし**事前配置のGo 1.25.14によるScoped Executable Evidence**であり、bootstrap wrapperのpinned archive materialization経路、他OS / 他Storage profile、Production永続層は対象外。E1〜E8 PASSは条件6〜8のhuman observationもProduct Valueも成立させない。
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
python3 tools/capture_issue_000073_resume_first_evidence.py --expected-head <canonical-commit-sha>
bash tools/bootstrap_issue_000073_resume_first_evidence.sh --expected-head <canonical-commit-sha>
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

runner / captureはcheckout外で独立に取得したcanonical expected HEADとの完全一致、clean committed HEAD、required sourceとHEAD blobの一致、Go 1.25.xをpreconditionとする。verifierもEvidence record内の`expected_head == head`と`head_matches_expected=true`を必須にする。preconditionを満たせずblockedとなった場合はrepository test failureともPASSとも扱わない。2026-09-18の実行環境ではhost Go 1.23.2であり、Go自身のtoolchain自動取得はnetwork / DNS制限でblockedだった。2026-10-07にGo 1.25.x bootstrap入口を追加してrepository tooling上の取得経路を具体化したが、この入口によるactual E1〜E8 runはまだ記録していないため、Evidence状態はNot Yet Verifiedのまま保持する。

runner preflight / verifier / capture workflowについては、current sourceに対する2026-09-18 actual self-test PASSをmachine-readable Evidenceへ固定済みである。ただしこれはEvidence受入れ経路の検証であり、Go 1.25.xで`interactionprobe`を実行したEvidenceへは昇格させない。

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

2026-09-17には、E1〜E8の実行入口をrunner単体からrunner / verifier / one-command captureのcurrent implementationへ同期した。2026-09-18にはEvidence受入れ経路のcurrent sourceをactualに再実行し、runner preflight、verifier、capture workflowのself-testをいずれもPASSとしてmachine-readable Evidenceへ固定した。同日Go 1.25.x取得経路も再確認したが、current execution environmentではhost Go 1.23.2かつ外向きDNS / network制限が継続しているためactual E1〜E8 runは未取得である。

H2についても同日、073専用の別runnerを増やさず、既存Inquiry Continuity review runnerをDecision manifestへ対応させた。reviewer provenance、stage gate、Decision固有validation、Evidence exportを一つの経路へ収束させ、provenance固定前に提示されたR1 materialは回答未固定のprotocol exposureとしてのみ扱う。H1 / H2ともactual human observationがないためNot Yet Observedのまま保持する。

同日の後続監査ではcurrent manifest / fixtureのstatic整合とactual-repository integration test sourceまで確認し、そのfocused Python testをclean HEAD / source binding付きでEvidence化するcapture入口も追加した。capture workflow self-testのPASSは受入れ経路だけのExecutable Evidenceであり、Decision regression actual PASSやH2 human observationへは昇格させない。

SEIのsemantic integrityが高いだけではProduct Valueとせず、historical誤帰属、Recommendation / Decision混同、再構成負担を実際に減らし、その利益がcapture / review overheadを上回るかまでを見る。価値差がない結果もProduct hypothesisを修正する正当なEvidenceとして扱う。意味、要求強度、留保、Evidenceの高さを固定したうえで自然な日本語として読み直し、最終意味監査を実施した。