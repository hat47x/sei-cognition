# ISSUE-000076: Runtime / Provider failure behaviorのEvidence境界を設計する

Status: **Open**  
Priority: **2**  
Related ADRs: **ADR-0013, ADR-0019, ADR-0021, ADR-0024, ADR-0025**  
Product Milestone: **PMS-06**  
Updated: 2026-09-18

## Goal

外部Runtime、Provider、model / executable artifactの取得・実行で起きる失敗を、SEIのsemantic identityやCognitive Methodの成果品質と混同せず、比較可能なEvidenceとして観測するための境界を設計する。

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

PR #336では、`evaluation/failure-behavior/case_catalog.json`とvalidatorを追加した。catalogは`evaluation-only` / `non-universal`として、transport、Provider admission、credential、artifact acquisition、artifact identity / integrity、runtime execution、semantic mapping、retryを比較可能なcaseへ分けている。Provider固有error code、retry schedule、credential / token / secret等をcatalogへ固定する変更はvalidatorで拒否する。

PR #337では、同catalogの9 caseを外部serviceなしで発火させるdeterministic probeを追加した。socket timeout、synthetic admission rejection、credential rejection、artifact unavailable、digest mismatch、process start failure、process開始後failure、semantic mapping rejection、retry successを同じreport shapeで観測し、reportの決定性、secret非保存、semantic state非変更、identity / integrity failureのfail closed、retry前failureの保持をfixture-scopedに検査する。PR記録上、catalog validatorを含む16 testはlocalでPASSしている。

PR #338では、既存`runtime/go/provideradapter`の`Adapter.Observe(...)`と`ValidateObservation(...)`を直接使うfailure test fixtureを追加した。Provider固有payloadのdecode後にmappingが失敗した場合にpartial Capability Observationを返さないこと、mapping成功後のsemantic runtime validation failureを別段階として扱えること、retry成功時も初回mapping failureを別attemptとして保持できることをtestとして固定した。

PR #343では、GitHub Actionsを成立条件にしないrepository-local入口として`evaluation/failure-behavior/run_local_checks.py`を追加した。2026-09-18の再監査で、runner先頭docstringとCLI descriptionだけが誤って`ISSUE-000072`を名乗っていたことを確認し、実行意味を変えず`ISSUE-000076`へ訂正した。catalog validator、deterministic probe、runner自身のtest、Provider Adapter Go testを一つの実行境界へまとめ、timeout、起動不能、途中停止、未実行checkをPASSへ読み替えない。子processには`SEI_*`、`KJ_ATLAS_*`、model runtimeや各種API key等のlive入力を暗黙継承しない。runner unit logicは6 test PASSを確認したが、`go test ./provideradapter`自体はこの作業環境では未実行である。

PR #344では、既存`runtime/go/liveintegration`へfailure probe testを追加した。deterministic `httptest`ではProvider rejection時にCapability Observationを生成しないこととAuthorization tokenをerrorへ漏らさないことを検査し、明示的opt-inのactual GitHub negative probeとして、存在しないrevisionと固定invalid credentialの2 caseを定義した。通常のrepository-local checkではlive flagが環境浄化で除去されるため、actual通信を自動実行しない。

PR #345では、actual negative probe専用の`run_live_provider_failure_probe.py`を追加した。`--allow-live`がなければ外部通信前に終了し、親環境のreal credentialを除去したうえで`SEI_E3B_FAILURE_LIVE=1`だけを設定する。`go test -json`のprocess exit codeだけではなく、missing revision / invalid credentialのexact 2 testが双方`pass`したことを要求し、missing / skip / fail / malformed JSON / non-zero / timeout / launch errorをfail closedとする。2026-09-18の再監査では、runnerのIssue表記を`ISSUE-000076`へ揃え、child processへ旧名`SOZA_*`の秘匿値も継承しないよう境界を補強した。current probe blob `613b75824fe88595749d8667d06d8bbaa5822313`とcurrent test blob `cd0e91ad436321a61fd7ed0d000acf80a1c937f2`を一時領域へ再構成したfocused executionでは11 testすべてPASSした。ただし、これは完全なrepository checkout上の実行ではなく、`go test ./liveintegration`やactual GitHub negative probeを実行済みとするEvidenceではない。

2026-09-18には、既存の`scoped_go_failure_execution_20260910.json`が固定したGo 1.23.2 scoped PASSとcurrent sourceの間を再監査し、`scoped_go_failure_source_delta_audit_20260918.json`へsource-delta auditを保存した。対象7fileは、byte-identical、ADR-0031のidentity rename、evaluation-only probe literal rename、または説明コメント追加へ限定され、正規化後のexecutable contentに追加差分は確認されなかった。一方、exact blobは変わっているため、これをcurrent Go PASSへ昇格していない。auditはcurrent fileのGit blob SHA-1に加えて、historical/currentへ同じ正規化を適用したcontent SHA-1も固定する。初回の補助JavaScript SHA-1実装には64-bit message-length trailerの生成誤りがあり、test相当の再照合で7件すべてのdigest不一致として検出したため、current-source PASSを主張する前に値を訂正し、その理由を`digestCorrection`へ保存した。訂正後はhistorical/currentの正規化digestが7/7一致し、current blob SHAも7/7一致することを機械的に再確認した。`test_scoped_go_failure_source_delta_audit.py`はcurrent fileから正規化digestを再計算し、source driftまたは正規化境界の不整合時に古いauditをfail closedにする。この検査もrepository-local runnerへ接続した。

PR #346では、Product Requirements / Acceptance Scenariosを再監査し、`evaluation/failure-behavior/requirement_audit.json`へ`completed-no-change-at-current-evidence-height`を記録した。REQ-0002、REQ-0006、REQ-0007、REQ-0020、REQ-0021、REQ-0022と、SCN-0010、SCN-0011、SCN-0017、SCN-0018を対象に、現Evidence高さでは新Stable Requirement、既存Stable Requirement変更、Acceptance Scenario追加・変更、Universal Contract field追加のいずれも行わない判断を固定した。audit testは5 test PASSを確認した。

したがってcurrent Evidenceは次の高さに留まる。

```text
Design Evidence
  + deterministic fixture-scoped Executable Evidence
  + current Provider Adapter / liveintegration pathに接続したfailure test定義
  + repository-local regression runner
  + explicit opt-in actual failure runner
  + Requirement audit = No Change at current evidence height
  != Provider Adapter Go testの実行済みEvidence
  != complete two-case actual Provider integration failure Evidence
  != actual deployment failure Evidence
  != Operational Evidence
```

### Requirement audit

current auditの結論は次である。

```text
new Stable Requirement = no
modify existing Stable Requirement = no
new / modified Acceptance Scenario = no
new Universal Contract field = no
```

既存のREQ-0002はUnknown / unobserved等の認識状態を平坦化しないこと、REQ-0006はRecommendation / Decision / Authority / Provider Execution等を分離すること、REQ-0007 / REQ-0021 / REQ-0022はProvider中立性・交換可能性・Provider-neutral Observationを要求している。REQ-0020はfixture / Executable EvidenceをOperational / Adoption / Outcomeへ昇格させない境界を既に持つ。SCN-0011もdegraded / 未観測Providerを単純なavailable / unavailableへ潰さない。

このため、failure stage enumやretry eligibility / schedule等を現時点でStable semanticsへ昇格させる根拠はない。actual Providerまたは第二Provider、あるいはOperational Evidenceから既存境界で表現できない持続的な意味差が現れた場合に再監査する。

### Next executable steps

次の優先順位は次とする。

1. 完全なrepository checkoutとGo実行環境で`python evaluation/failure-behavior/run_local_checks.py`を実行し、`provideradapter`と`liveintegration`を含むcurrent local regressionを確定する。
2. その結果が成立した後、`python evaluation/failure-behavior/run_live_provider_failure_probe.py --allow-live`を明示的に実行し、missing revision / invalid credentialのactual GitHub negative probeを確認する。
3. actual probe結果をfixture Evidenceと分離して記録し、Provider固有HTTP statusやerror vocabularyをUniversal semanticsへ昇格させない。
4. 必要性が残る場合のみ、Provider admission / throttlingやartifact acquisition failureを別のactual Provider / actual executableへ広げる。

actual probe runnerはreal credentialを親環境から継承しない。missing revisionは匿名GitHub API、credential rejectionはtest内の固定invalid tokenだけを利用する。

### Operational Evidence — not yet

実環境での障害頻度、復旧時間、Provider側運用、credential rotation運用等はOperational Evidenceである。synthetic failure injectionや一回のactual failureをOperational Evidenceへ昇格させない。

### Adoption / Outcome Evidence — out of scope

障害時の利用者体験や組織的価値まで評価する場合は、別のOperational / Adoption系列で扱う。本IssueのDesign / Executable Evidenceだけから推定しない。

## Required scenarios / experiments

少なくとも次のcaseを同じ観測形式で比較する。

1. transport timeout
2. temporary provider rejection / throttling
3. invalidまたはexpired credential
4. requested artifact unavailable
5. acquired artifact digest mismatch
6. child process start failure
7. child process started but execution failed
8. provider response received but semantic mapping rejected
9. retry後に成功したcaseで、初回failureとretry successの双方が保持されること

current deterministic probeでは1〜9をすべてfixture-scopedに発火させている。8と9は既存Provider Adapter経路へ接続したGo test fixtureもmainへ統合済みである。actual GitHub negative probeでは3のcredential rejectionと、4に相当するmissing revisionを明示的opt-in testとして定義したが、そのactual実行は未確認である。actual service固有の再現方法は各Realization / Provider Adapter側で選び、caseそのものをHTTPやGitHub等へ固定しない。

## Constraints

- current Product Value、Requirement、ADRを、failure fixtureを実装しやすくするためだけに変更しない。
- Provider固有error code、HTTP status、CLI exit codeを直ちにUniversal enumへ昇格しない。
- credential本文やsecret pathを通常Evidenceへ保存しない。
- credential失効をsemantic identity変更として扱わない。
- temporary outageやrate limitをCognitive Method outcome qualityへ混入させない。
- retry成功で最初のfailure observationを上書きしない。
- identity / integrity不一致を一時的transport failureへ読み替えない。
- fixtureのPASSをactual ProviderやOperational Evidenceへ昇格させない。
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
- 必要に応じたactual Provider / actual executable failure Evidence
- Requirement audit結果
- `plan/registry.yaml`
- `plan/document_review_registry.yaml`

`plan/registry.yaml`では本Issueは引き続きOpen / Priority 2として登録済みであり、今回status、priority、related ADRに変更はない。`plan/document_review_registry.yaml`も`ISSUE-000001..ISSUE-000076`を監査対象として既に包含しているため、台帳を形式的に書き換えることはしない。

## Current verification state

2026-09-18時点のcurrent stateは次のとおりである。

- Design Evidence: **Established**。failure stage、retry boundary、secret-safe Evidence、Evidence ladderを本Issueで固定した。
- case catalog / validator: **Verified fixture-scoped**。mainへ統合済み。
- deterministic probe: **Verified fixture-scoped**。9 caseを発火し、PR記録上catalog validatorを含む16 local tests PASS。
- Provider Adapter failure tests: **Defined on current runtime path**。mapping failure、semantic validation failure、retry attempt separationを既存Adapter境界へ接続済み。
- repository-local failure runner: **Defined / unit-tested**。runner unit logic 6 test PASS。2026-09-18にsource-delta guardを追加し、current Git blobと正規化digestの7/7再照合、およびrunner wiringを確認した。ただしcurrent完全checkout上でのrunner全体は未実行であり、Provider Adapter Go testのcurrent exact-blob PASSは未確認。
- live Provider failure tests: **Defined explicit opt-in**。missing revision / invalid credential、secret-safe deterministic rejectionを追加済み。
- explicit live failure runner: **Defined / focused current-blob unit execution verified**。2026-09-18にcurrent probe/test blobを一時領域へ再構成し11/11 test PASSを確認した。これは完全checkout Evidenceではない。actual GitHub negative probe全体は未実行。missing revision単独については`actual_provider_missing_revision_observation_20260910.json`のactual service observationが存在するが、invalid credentialとの2-case runner完走は未確認。
- Requirement audit: **Completed — No Change at current evidence height**。audit test 5 test PASS。
- actual Provider failure Evidence: **Partially observed / not sufficient for Resolution**。`actual_provider_missing_revision_observation_20260910.json`にmissing revisionのactual service observationが保存されている一方、invalid credentialを含むexplicit live negative probe全体は未実行であり、Provider admission / credential等を跨ぐactual比較Evidenceには達していない。
- actual deployment failure Evidence: **Not Yet Verified**。
- Operational Evidence: **Not Yet Verified**。

このためIssueはOpenを維持する。fixtureとrunnerの設計・回帰境界は整ったが、current Go pathとactual Provider negative probeの実行済みEvidenceがまだない。

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

項目8はPR #346のRequirement auditにより完了した。1〜6についてfixture-scopedな比較境界は整っているが、current Go pathとactual Providerの実行済みEvidenceが不足しているため、Resolution全体はまだ満たしていない。

## Reopen conditions

Resolved後でも、次の場合は再開を検討する。

- 別Provider / 別Realizationで既存分類では区別できないfailure stageが現れた。
- retryによってsemantic identityやhistorical stateが曖昧になるcaseが見つかった。
- secret-safe Evidenceだけでは原因の区別ができず、Evidence boundaryの再設計が必要になった。
- Operational Evidenceから、Design / Executable Evidenceで見落としていた重大なfailure modeが見つかった。
