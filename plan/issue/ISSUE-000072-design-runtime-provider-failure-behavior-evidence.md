# ISSUE-000072: Runtime / Provider failure behaviorのEvidence境界を設計する

Status: **Open**  
Priority: **2**  
Related ADRs: **ADR-0013, ADR-0019, ADR-0021, ADR-0024, ADR-0025**  
Product Milestone: **PMS-06**  
Updated: 2026-09-10

## Goal

外部Runtime、Provider、model / executable artifactの取得・実行で起きる失敗を、SOZAのsemantic identityやCognitive Methodの成果品質と混同せず、比較可能なEvidenceとして観測するための境界を設計する。

最初の対象は、少なくとも次の失敗である。

- network degradation、timeout、connection loss
- rate limitや一時的なProvider拒否
- credentialの欠落、失効、期限切れ、authorization rejection
- model / executable artifactの取得不能
- 取得したartifactのidentity / integrity不一致
- process開始後のruntime execution failure

本Issueでは、これらを一つの「外部エラー」へ丸めない。一方で、HTTP status code、Ollama、GitHub、TEI等のcurrent実装語彙をUniversal Contractへ先取りしない。

また、万能なretry policyをここで決めない。障害がどの段階で起き、何を安全に記録でき、再試行によって何が変わり得るかを先に分離し、Stable Requirementが必要かは後続Evidenceから判断する。

## Background

ISSUE-000057〜000068では、out-of-process Realization / Provider交換、fixed artifact、actual external Provider、actual TEI CLI、actual Cognitive Method、actual model-backed execution、historical reconstruction、model artifact交換までを段階的に実証した。

これらは主として「固定した入力・Realization・artifactを使って実行が成立したとき、何を観測し、どのsemantic identityへ戻すか」を確認している。

一方、current上流計画では次の未定領域が残っている。

```text
success-path portability
  != failure behavior
  != retry policy
  != Operational Evidence
```

特に、次の差を失うと、後から失敗原因とProduct上の意味を分離できなくなる。

```text
artifactを取得できない
  != artifactを取得したがidentityが一致しない
  != runtimeを開始できない
  != runtime開始後に処理が失敗する
  != Providerが一時的に受付を拒否する
  != credentialが利用できない
```

さらに、外部失敗はsemantic identityの変更を自動的には意味しない。

```text
temporary provider outage
  != new Method Realization

credential rotation
  != new Cognitive Method Definition

rate limit
  != Cognitive Method outcome quality

retry success
  != first failure did not occur
```

ISSUE-000070のruntime version交換は、固定model artifactの下でruntime versionだけを交換したhistorical reconstructionを検証する別のOpen Issueである。本Issueはその実証を横取りせず、成功経路・交換経路の次に必要となるfailure Evidenceの設計を扱う。

## Questions

1. どの失敗段階を意味上区別して観測する必要があるか。
2. Provider固有のerror codeと、Providerを越えて比較したいfailure classificationをどこで分けるか。
3. secretやcredential本文を保存せず、失敗を後から検証するために何をEvidenceとして残すか。
4. retry可能性はUniversal semantics、Realization contract、Provider Adapter、deployment policyのどこに属するか。
5. 一度失敗したattemptと、その後成功したretryを別のhistorical observationとしてどう保持するか。
6. artifact取得不能とExact Binding / integrity不一致を、同じacquisition failureへ潰さずに扱えるか。
7. fixtureによるfailure injectionで確認できる範囲と、actual Provider / actual deploymentでなければ確認できない範囲をどう分けるか。
8. どのEvidenceまで得られたとき、Stable Requirement追加・既存Requirement統合・No Changeを判断できるか。

## Candidate failure stages

以下は実験を設計するためのcandidate分類であり、現時点のUniversal Contract enumではない。

### FB-1 — Reachability / transport

対象例:

- name resolution failure
- connection refusal
- timeout
- mid-stream connection loss

Provider固有のnetwork stackやerror文字列をUniversal semanticsへ固定せず、「実行対象へ到達できなかった」「通信途中で継続不能になった」という観測を比較する。

### FB-2 — Provider admission / throttling

対象例:

- rate limit
- capacity不足による一時拒否
- provider-side temporary unavailable

「requestを送れなかった」ことと「送ったが一時的に受理されなかった」ことを分ける。429等の特定status codeをUniversal fieldへ固定しない。

### FB-3 — Authentication / authorization / credential

対象例:

- credential未設定
- credential失効・期限切れ
- scope不足
- authorization rejection

credential本文、token、secret path等を通常Evidenceへ保存しない。記録するのは、どのboundaryで利用不能と判定されたか、実行開始前後のどちらか、後続semantic stateへ何を反映しなかったかである。

### FB-4 — Artifact acquisition

対象例:

- requested revision / artifactが存在しない
- registry / repositoryへ到達できない
- downloadが完了しない

「取得できなかった」事実と、取得したartifactが誤っていた事実を分ける。

### FB-5 — Artifact identity / integrity verification

対象例:

- expected digest不一致
- requested revisionとobserved revisionの不一致
- Exact Binding verification failure

これは単なる一時的network failureとしてretry成功へ丸めない。既存のExact Binding fail-closed原則を維持し、誤ったartifactを実行へ進めない。

### FB-6 — Runtime execution

対象例:

- process start failure
- process開始後のnon-zero exit
- malformed / incomplete response
- provider-specific resultをcurrent observationへmappingできない

「runtimeを開始できなかった」「開始したが実行に失敗した」「実行結果は返ったがsemantic mappingを受理できなかった」を必要に応じて分ける。

## Candidate observation boundary

後続実験では、各failure caseについて少なくとも次を比較できるようにする。

- failureが起きたstage
- input / Application / Realizationの固定identity
- Provider Adapterが観測した、secretを含まない最小限の事実
- execution開始前か、開始後か
- retryを行ったかどうか
- retryした場合、元attemptとretry attemptを別記録として辿れるか
- semantic identityを変更したか、変更していないか
- historical Application / Decision Memory等の既存保存物を変更していないか
- fixture、actual executable、actual ProviderのどのEvidence高さで確認したか

これらは実験記録の観測項目であり、現時点でUniversal Contract fieldを追加する提案ではない。

## Retry boundary

retryは失敗分類と分けて扱う。

```text
failure classification
  != retry eligibility
  != retry schedule
  != retry outcome
```

たとえば、rate limitは一定条件で再試行可能かもしれないが、その条件や待機時間はProvider / deployment policyへ属する可能性がある。一方、digest mismatchを「もう一度試せばよい」一時障害へ自動分類すると、Exact Bindingの意味を壊す。

したがって、本Issueでは次を要求する。

- retry前のfailure Evidenceを消さない。
- retry attemptは元attemptと区別する。
- retry成功を元failureの不存在として扱わない。
- retry policyのcurrent実装都合をStable Requirementへ先取りしない。
- identity / integrity failureをtransport retryへ自動的に読み替えない。

## Secret-safe Evidence boundary

通常のEvidenceへ次を保存しない。

- access token
- password
- API key
- credential file本文
- secretを含むDSN / URL
- secretそのものを推測可能にする不要なraw header

必要な場合は、credentialを読み込めたか、Providerからauthorization rejectionを受けたか等の結果だけを保存する。

secretをredactした結果、診断に必要な区別まで失う場合は、Universal Evidenceへsecretを追加するのではなく、実行環境内の限定diagnosticとrepositoryへ保存するEvidenceを分離する。

## Evidence ladder

### Design Evidence

本Issueで次を固定する。

- failure stageを一つの外部エラーへ潰さない。
- secret-safe Evidenceを要求する。
- failure classificationとretry policyを分ける。
- success-path Evidenceや成果品質とfailure Evidenceを分ける。
- Provider固有error vocabularyをUniversal Contractへ先取りしない。

### Executable Evidence — current state

#### 1. deterministic / fixture-scoped

PR #336〜#338で、`case_catalog.json`、validator、9 caseのdeterministic probe、既存`provideradapter`境界へ接続したfailure test fixtureを追加した。

current fixtureでは、transport timeout、Provider admission rejection、credential rejection、artifact unavailable、digest mismatch、process start failure、process開始後failure、semantic mapping rejection、retry successを分けて発火できる。catalogは`evaluation-only` / `non-universal`であり、Provider固有error code、retry schedule、credential / token / secret等を固定する変更はvalidatorで拒否する。

retry caseでは初回failureと後続successを別attemptとして保持し、identity / integrity failureではfail closedを要求する。

#### 2. repository-local regression / explicit live runner

PR #343〜#345で、GitHub Actionsを成立条件にしない`run_local_checks.py`と、明示的opt-inの`run_live_provider_failure_probe.py`を追加した。

通常のlocal checksはlive入力やcredentialを子processへ暗黙継承せず、timeout、起動不能、途中停止、未実行checkをPASSへ読み替えない。actual negative probeは`--allow-live`なしでは外部通信前に終了し、`go test -json`のprocess exit codeだけでなく、missing revision / invalid credentialのexact 2 testの個別PASSを要求する。

PR #350とPR #353で、後述するscoped Go Evidenceとactual Provider service観測の保存済みEvidenceも通常local checksの回帰対象へ追加した。current runnerは9 checkを構成するが、Go 1.25 full checkout環境で9 checkすべてを通したEvidenceはまだない。

#### 3. scoped main-source Go execution

PR #349では、private repositoryのfull checkoutとGo 1.25 toolchainを利用できない実行環境で、main commit `fc9c7b41d8c6cae60ff1549ebb679a9888efc2a1`の正確なsource blobからfailure pathに必要なsliceを再構成し、Go 1.23.2で限定実行した。

確認した範囲は次である。

- `provideradapter` failure behavior 3 test: PASS
  - mapping failureでpartial Capability Observationを返さない。
  - semantic validation failureをmapping failureとは別に扱う。
  - retry後も初回mapping failureを別attemptとして保持する。
- `liveintegration` secret-safe deterministic rejection: PASS
  - Provider rejection時にCapability Observationを生成しない。
  - Authorization tokenをerrorへ漏らさない。
- actual live 2 test: Not Executed

このEvidenceは`scoped-main-source-slice`であり、full repository regressionでもGo 1.25 baseline verificationでもない。PR #351でRequirement auditにもこの高さを反映した。

#### 4. actual Provider service observation

PR #352では、接続済みGitHub API境界から`hat47x/cultural-substrate-weaving`のcommit-by-revision endpointを実際に観測した。

- known revision `aa3651f3460a6db7dc70bd848f93b600f149ffe8`: success
- nonexistent revision `0000000000000000000000000000000000000000`: Provider rejection
- GitHub固有status: `422`

同じendpoint familyで既知revisionが成功し、不存在revisionがProviderから拒否されたことまではactual Provider serviceの事実として確認できた。一方、status `422`やProvider messageはGitHub固有の観測値であり、Universal failure codeではない。

この観測はconnected GitHub API経由であり、SOZAの`GitHubCommitService`や`run_live_provider_failure_probe.py`を実行したEvidenceではない。credential rejectionも未実行である。credential本文やAuthorization headerはEvidenceへ保存していない。

PR #354では、この差をRequirement auditへ反映し、`actualProviderServiceObservation=true`と`actualProviderIntegrationFailureEvidence=false`を別軸として固定した。

### Current Evidence height

```text
Design Evidence
  + deterministic fixture-scoped Executable Evidence
  + scoped main-source Go failure execution (Go 1.23.2)
  + actual GitHub Provider service missing-revision observation
  + repository-local regression / explicit live runner definitions
  + Requirement audit = No Change at current evidence height
  != full repository Go 1.25 regression
  != SOZA GitHubCommitService actual negative probe execution
  != credential rejection Evidence
  != actual deployment failure Evidence
  != Operational Evidence
```

## Requirement audit

PR #346でProduct Requirements / Acceptance Scenariosを再監査し、その後PR #351、#354でEvidence高さだけを更新した。current結論は引き続き次である。

```text
new Stable Requirement = no
modify existing Stable Requirement = no
new / modified Acceptance Scenario = no
new Universal Contract field = no
```

REQ-0002はUnknown / unobserved等の認識状態を平坦化しないこと、REQ-0006はRecommendation / Decision / Authority / Provider Execution等を分離すること、REQ-0007 / REQ-0021 / REQ-0022はProvider中立性・交換可能性・Provider-neutral Observationを要求している。REQ-0020はfixture / Executable EvidenceをOperational / Adoption / Outcomeへ昇格させない境界を既に持つ。SCN-0011もdegraded / 未観測Providerを単純なavailable / unavailableへ潰さない。

actual GitHub serviceでmissing revision rejectionを観測しても、GitHub固有statusやmessageを一般化すべき根拠にはならない。また、SOZA integration経路とcredential rejectionはまだ未実行である。このため、failure stage enumやretry eligibility / scheduleをStable semanticsへ昇格させる判断は行わない。

## Next executable steps

次の優先順位は次とする。

1. 完全なrepository checkoutとGo 1.25実行環境で`python evaluation/failure-behavior/run_local_checks.py`を実行し、`provideradapter`と`liveintegration`を含むcurrent 9 checkを確定する。
2. その後、`python evaluation/failure-behavior/run_live_provider_failure_probe.py --allow-live`を明示的に実行し、SOZA `GitHubCommitService`経由のmissing revisionと固定invalid credentialの2 negative probeを確認する。
3. actual integration結果をProvider service observationと別Evidenceとして記録し、GitHub固有HTTP statusやerror vocabularyをUniversal semanticsへ昇格させない。
4. その結果からなお必要性が残る場合だけ、Provider admission / throttlingや別Provider、artifact acquisition failureのactual実証へ広げる。

actual live runnerはreal credentialを親環境から継承しない。credential rejectionはtest内の固定invalid tokenだけを利用する。

## Operational Evidence — not yet

実環境での障害頻度、復旧時間、Provider側運用、credential rotation運用等はOperational Evidenceである。synthetic failure injection、scoped Go execution、一回のactual Provider service rejectionのいずれもOperational Evidenceへ昇格させない。

## Adoption / Outcome Evidence — out of scope

障害時の利用者体験や組織的価値まで評価する場合は、別のOperational / Adoption系列で扱う。本IssueのDesign / Executable / Provider service Evidenceだけから推定しない。

## Required scenarios / experiments

少なくとも次のcaseを同じ観測形式で比較する。

1. transport timeout
2. temporary provider rejection / throttling
3. invalidまたはexpired credential
4. requested artifact / revision unavailable
5. acquired artifact digest mismatch
6. child process start failure
7. child process started but execution failed
8. provider response received but semantic mapping rejected
9. retry後に成功したcaseで、初回failureとretry successの双方が保持されること

current deterministic probeでは1〜9をfixture-scopedに発火させている。8と9は既存Provider Adapter経路へ接続したtest fixtureを持ち、scoped main-source Go executionでも対応するProvider Adapter failure sliceを実行済みである。

4に相当するmissing revisionはactual GitHub Provider serviceでも拒否を観測した。ただしSOZA integration経路では未実行であり、3のactual credential rejectionも未実行である。actual service固有の再現方法は各Realization / Provider Adapter側で選び、caseそのものをHTTPやGitHub等へ固定しない。

## Constraints

- current Product Value、Requirement、ADRを、failure fixtureを実装しやすくするためだけに変更しない。
- Provider固有error code、HTTP status、CLI exit codeを直ちにUniversal enumへ昇格しない。
- credential本文やsecret pathを通常Evidenceへ保存しない。
- credential失効をsemantic identity変更として扱わない。
- temporary outageやrate limitをCognitive Method outcome qualityへ混入させない。
- retry成功で最初のfailure observationを上書きしない。
- identity / integrity不一致を一時的transport failureへ読み替えない。
- fixture / scoped executionのPASSをactual Provider integrationやOperational Evidenceへ昇格させない。
- actual Provider service observationをSOZA integration executionへ読み替えない。
- GitHub Actionsや特定runnerを意味上の成立条件にしない。
- actual live probeを通常のlocal regressionから暗黙に起動しない。
- 現時点では新しいStable Requirement / Acceptance Scenario / Universal Contract fieldを追加しない。

## Deliverables

本Issueで管理する成果物は次とする。

- failure classificationとretry boundaryを記録した本Issue
- deterministic failure fixture / helperまたは同等のfault-injection手段
- secret-safe failure Evidenceの検査
- failure stageを跨ぐ比較可能なfixture / case catalog
- repository-local failure regression runner
- explicit opt-in actual Provider failure runner
- scoped main-source Go execution Evidence
- actual Provider service observation Evidence
- 必要に応じたactual SOZA integration / actual executable failure Evidence
- Requirement audit結果
- `plan/registry.yaml`
- `plan/document_review_registry.yaml`

`plan/registry.yaml`では本Issueは引き続きOpen / Priority 2として登録済みであり、status、priority、related ADRに変更はない。`plan/document_review_registry.yaml`も`ISSUE-000001..ISSUE-000072`を監査対象として既に包含しているため、台帳を形式的に書き換えない。

## Current verification state

2026-09-10時点のcurrent stateは次のとおりである。

- Design Evidence: **Established**。failure stage、retry boundary、secret-safe Evidence、Evidence ladderを本Issueで固定した。
- case catalog / validator: **Verified fixture-scoped**。mainへ統合済み。
- deterministic probe: **Verified fixture-scoped**。9 caseを発火し、PR記録上catalog validatorを含む16 local tests PASS。
- Provider Adapter failure path: **Scoped Executable Evidence established**。main source由来sliceをGo 1.23.2で実行し、failure behavior 3 test PASS。ただしfull checkout / Go 1.25 baselineではない。
- liveintegration secret-safe deterministic path: **Scoped Executable Evidence established**。main source由来sliceでPASS。ただしactual live probeではない。
- repository-local failure runner: **Defined / regression boundary expanded**。scoped Go Evidenceとactual Provider service observationの保存済みEvidenceもcheck対象に含む9 check構成。Go 1.25 full-run Evidenceは未確認。
- actual Provider service missing revision: **Observed**。known revision successとnonexistent revision rejectionをconnected GitHub APIで対照確認。GitHub固有statusはProvider-localに保持。
- SOZA live Provider failure tests: **Defined explicit opt-in**。missing revision / invalid credentialを定義済みだが実行は未確認。
- explicit live failure runner: **Defined / unit-tested**。runner unit test 10 PASS。actual SOZA integration negative probeは未実行。
- Requirement audit: **Completed — No Change at current evidence height**。latest audit test 7 PASS。
- credential rejection Evidence: **Not Yet Verified**。
- actual deployment failure Evidence: **Not Yet Verified**。
- Operational Evidence: **Not Yet Verified**。

このためIssueはOpenを維持する。fixture → scoped Go → actual Provider serviceまではEvidenceが進んだが、Go 1.25 full regressionとSOZA integration negative probe、credential rejectionがまだ不足している。

## Resolution

次をすべて確認した時点で、本IssueをResolvedまたはClosed — No Changeとする。

1. 少なくともtransport、provider admission、credential、artifact acquisition、artifact identity / integrity、runtime executionを区別してpressure testした。
2. 同じ失敗をProvider固有語彙だけに依存せず比較できることを確認した。
3. failure classificationとretry policy / retry outcomeを分離した。
4. retry後も初回failure Evidenceを保持できることを確認した。
5. secret / credential本文をrepository保存Evidenceへ漏らさない検査を行った。
6. identity / integrity failureがfail closedであり、transport retryへ自動変換されないことを確認した。
7. fixture Evidence、actual executable / Provider Evidence、Operational Evidenceを別の高さとして記録した。
8. Product Valueと既存REQ / SCNを再監査し、新しいStable Requirementが必要か、既存Requirementへ統合できるか、No Changeかを明示した。
9. 新しいUniversal Contract fieldが必要な場合は、current Provider固有実装を一般化しただけではなく、複数caseから意味差の必要性を説明できるようにした。

項目8は完了している。1〜6についてfixture-scopedな比較境界は整い、Provider Adapter failure pathの限定Go実行とactual Provider serviceのmissing-revision観測まで進んだ。一方、Go 1.25 full regression、SOZA integration経路のactual negative probe、credential rejectionが未確認であるため、Resolution全体はまだ満たしていない。

## Reopen conditions

Resolved後でも、次の場合は再開を検討する。

- 別Provider / 別Realizationで既存分類では区別できないfailure stageが現れた。
- retryによってsemantic identityやhistorical stateが曖昧になるcaseが見つかった。
- secret-safe Evidenceだけでは原因の区別ができず、Evidence boundaryの再設計が必要になった。
- Operational Evidenceから、Design / Executable Evidenceで見落としていた重大なfailure modeが見つかった。
