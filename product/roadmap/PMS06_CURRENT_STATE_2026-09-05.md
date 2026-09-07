# PMS-06 — Current State Snapshot

更新日: 2026-09-07  
対象: PMS-06 Realization / Provider Exchange

## この文書の役割

この文書は、PMS-06の現在地を短く確認するためのsnapshotです。`SOZA_PRODUCT_MILESTONES.md`、`SOZA_REALIZATION_PROVIDER_EXCHANGE.md`、`SOZA_VALUE_TRACEABILITY.md`等のProduct基線を置き換えず、2026-09-05以降に進展したversion-exchange EvidenceとIssue状態を補完します。

Product Value、Milestone Outcome、Requirement、Acceptance Scenario、Universal Contractを新しく定義しません。意味上の正本は既存Product / Requirement / Issue本文であり、このsnapshotは現在のEvidence位置を読み違えないための補助資料です。

## 現在のEvidence ladder

```text
E1 Contract / in-process synthetic
  → E2 out-of-process reference exchange
  → E3a version-pinned external artifact integration
  → E3b live external process / service integration
  → E4 Operational portability
```

現在までに、少なくとも次のScoped Executable Evidenceがあります。

- E2 out-of-process reference exchange
- E3a version-pinned external artifact integration
- E3b-P1 public live Provider integration
- E3b-P2 revision A fixed-artifact actual TEI CLI execution
- E3b-M1a fixed KJ Atlas + deterministic model stub
- E3b-M1b fixed KJ Atlas + actual inference model
- Method Realization historical revision / portable reconstruction
- actual model artifact交換後のhistorical Application保持
- fixed model artifact下のOllama `0.32.13` / `0.32.14` runtime version交換後のhistorical Application保持

これらはv0.2.0 supported release scopeを遡及的に広げません。v0.2.0のsupported scopeはE3aまでです。

## Current exploration status

2026-09-07時点で、PMS-06のruntime / Provider version-exchange探索は次の状態です。

```text
ISSUE-000070
  = Resolved
  = fixed-scope Ollama runtime version exchangeのScoped Executable Evidence available

ISSUE-000072
  = Open
  = TEI executable / Provider Plan revision B actual execution pending
  = snapshot transport / E2 partial / failure audit path repository-side ready
```

片方のEvidenceをもう片方へ流用しません。

## ISSUE-000070 — Ollama runtime version exchange

交換軸は次へ固定しました。

```text
same KJ Atlas source
same Method input
same model artifact
same prompt

Ollama 0.32.13
  ↕ runtime version only
Ollama 0.32.14
```

execution `local-20260904T193531Z-7855` のactual Evidenceを2026-09-05にcurrent developへ回収し、ISSUE-000070のResolution Criteriaへ再照合しました。

確認済み:

- fixed KJ Atlas runtime surface identity
- Ollama `0.32.13` / `0.32.14` actual archive bytes / SHA-256
- A / B actual binary version
- fixed `qwen2.5:0.5b` model full digest
- A / B actual `/api/tags` model identity
- same fixed Method input / same prompt digest
- A / B actual inference
- same logical Realization / different Exact Binding
- historical Application AのExact Reference / Provenance / output不変性
- portable historical reconstruction
- unknown revision / identity変更のnegative control
- Recommendation / Decisionへの自動昇格なし
- canonical Evidence + Provenance verification: `ready-to-review`
- verifier checks: `107 ok / 0 blocked`
- Requirement / Contract再照合: No Change

actual run commitとcurrent developのGit object identityも再監査し、ISSUE-000070 Resolution Criteria、core Evidence verifier、Provenance verifier、fixed artifact manifest、Product Requirements、Acceptance Scenarios、関連Semantic Contract baselineが同一objectであることを確認しました。

したがってISSUE-000070は**Resolved**です。

```text
ISSUE-000070 Resolved
  = fixed KJ Atlas + fixed model artifact下のOllama 0.32.13 / 0.32.14 version exchangeについてScoped Executable Evidence available
  != arbitrary runtime version portability
  != other runtime implementation portability
  != model output quality satisfied
  != KJ-method outcome quality satisfied
  != E4 Operational portability
```

成果品質は引き続き`qualityJudgement=not_evaluated`です。

## ISSUE-000072 — TEI executable version exchange

revision Aについては、ISSUE-000065でfixed-artifact actual TEI CLI executionのScoped Executable Evidenceがあります。

revision Bは次へ固定しています。

`1a7028d444fcae60a1c4f2f2d247456f4c7c35be`

version交換の比較軸は、reference input driftを避けるため次へ固定しています。

```text
build / executable source
  = exact revision B

fixed reference input
  = exact revision A
```

repository側では次まで整っています。

- revision A historical Evidence再検証
- historical A artifact内workspace / durable run / plugin lock bytesの固定Git object identity再検証
- acquisition-independent TEI Evidence bundle verifier
- historical A Evidence bundleをexternal fixed identityへ照合しreference inputだけをmaterializeするhelper
- revision B execution-source Git identity verifier
- revision B signed commit objectをGitHub verified payload / PGP signatureから独立再構成し、固定commit SHA-1へ一致することを確認したacquisition Evidence
- revision A fixed reference input identity verifier
- tracked変更 / untracked / gitignored entryをactual source / checkout fixed input境界から排除するworking-tree purity guard
- A/B Provider Plan source surface static comparison
- exact-B + exact-A fixed-input prepositioned E2 runner
- A fixed input acquisitionをexact A checkout / verified historical A Evidence bundleから選べるE2 / combined runner
- E3未準備環境でもactual E2だけを先行回収できるGitHub acquisition E2 partial runner
- E2 partial bundleをexact revision B source commit + exact revision A fixed reference identityへbindingするstrict verifier
- verified bundle → current SOZA Adapter E3 runner
- 保存済みE2 partialからrevision B source取得 / E2 build / Provider Planを再実行せずcurrent E3だけを後日実行するresume runner
- resume後のcanonical report publishまでは成功しGitHub wrapper report publishだけが中断した場合にE2 / E3を再実行せずreport pairを復旧するreconcile runner
- E2 / E3 separate Go toolchains
- canonical combined runner: `runtime/integration/run_tei_version_exchange_evidence.py`
- E2 / E3 stage-aware failure Evidence
- E3 Go requirement判定のstandalone runner側への集約
- combined runnerのGo path setup failureに対するmachine-readable toolchain stage
- Evidence出力pathをrevision B / SOZA checkoutから分離し、checkout取得時はrevision A checkoutとも分離し、historical bundle取得時は入力bundleをEvidence directory内へ包含しない実行前guard
- Requirement / Scenario pre-audit
- GitHub / local post-run Resolution audit
- E2 partial actual → strict re-verification → later E3 resume → 必要時reconcile → Resolution auditを一続きにしたoperator runbook
- GitHub credentialを持つonline環境でGit Data responseをcredential-free snapshotへ固定するsnapshot capture producer
- snapshotをoffline Linux/amd64環境でexact-B sourceへ再構成しcanonical verifierへ戻すsnapshot materializer
- snapshotから既存E2 partial contractへ接続するsnapshot → E2 one-shot runner
- actual E2 partialがstage-aware failureで停止した場合にResolution Criteriaへ戻し、false successやE3到達扱いを作らないE2 failure専用audit
- snapshot transport success / failure双方を分岐として固定した2026-09-07 operator runbook

E2 historical TEI buildとE3 current SOZA live testは別toolchainを使います。Go versionや配置方法はexecution EvidenceでありStable Requirement / Universal Contractではありません。

Git object identityが一致するだけではactual source / checkout fixed inputのpurity成立とは扱いません。execution boundary内にtracked変更、untracked entry、gitignored entryがあればE2開始前に拒否します。historical bundle経路ではworking treeの代わりに、bundle metadataのA source commit、historical binary / Provider Plan digest、およびactual reference bytesから再計算したGit object identityを固定値へ照合します。

revision Bについては、GitHub Git Commit APIのverified payload / PGP signatureからsigned commit raw objectを独立再構成し、Git object SHA-1が固定revision B `1a7028d444fcae60a1c4f2f2d247456f4c7c35be`へ一致することを確認済みです。ただし、これはfull source checkoutをmaterializeしたEvidenceではありません。canonical source verifierが要求するworking tree cleanlinessやactual build source bytesの配置は、実行環境上で別途成立させる必要があります。

2026-09-07には、fixed revision Bのexact Git object identityへ束縛したsource-level監査で、`cmd/tei`に決定論的なcompile矛盾を観測しました。これはcanonical exact-B checkoutをexact Go 1.23.2 / Linux amd64でbuildしたactual E2結果ではありません。known build-fixはfixed-Bのancestorではなくdivergedしているため、fixed Bを後続repair revisionへ無言で置換しません。

```text
Git object identity matched
  + tracked / untracked / ignored execution boundary clean
  = source / checkout-fixed-input identity precondition satisfied
  != revision B build PASS

historical bundle fixed input identity verified
  != revision A source checkout reconstructed
  != fixed input acquisition path identity
  != revision B build PASS

exact revision B signed commit object reconstructed
  != exact revision B checkout materialized
  != revision B build PASS

deterministic fixed-B source-level compile contradiction observed
  != canonical actual revision B build FAIL
  != Provider Plan failure
  != SOZA Adapter incompatibility
```

GitHub-hosted actual workflowはattempt 7まで観測されていますが、latest attemptもrunner assignment / Product step / artifactを観測していません。したがってfailure分類はGitHub-hosted job-start層に留め、TEI build failureやProvider Plan failureへ昇格させません。

snapshot transport実装は成立していますが、credential-free **actual exact-B snapshot bytesはまだ取得していません**。historical `bootstrap/final-source`、`bootstrap/publish`、`bootstrap/materialize`等はfixed revision B sourceの代替にはせず、historical materialize staging commitをpatch baseにするshortcutもcanonical exact-B acquisitionを十分短縮しないため採用しません。

未検証:

```text
actual exact-B Git Data snapshot acquisition
revision B canonical actual CLI build / execution
revision B actual deployment-provider-plan
revision B current SOZA Adapter live compatibility
```

したがってISSUE-000072は**Open**です。

actual E2がbuild failureで停止した場合は、stage-aware failure reportを保存し、専用Resolution auditへ接続してE3へ進みません。`resolutionCandidate=false`を維持し、Bのexact binding / failure Evidenceを保持します。actual E2が成功した場合だけstrict bundle verificationを行い、current SOZA E3へ進みます。

## ISSUE-000071との関係

ISSUE-000071はResolvedですが、完了したのはCognitive Method成果品質の**評価境界の確立**です。

```text
evaluation boundary established
  != human review completed
  != KJ-method outcome quality satisfied
  != Product Value / Adoption outcome satisfied
```

ISSUE-000070のactual runtime exchange PASSも成果品質を満たしたことを意味しません。human outcome reviewは後続Evidenceです。

## Product-level interpretation

version exchangeでは、実現層のversionやartifact取得方法が変わっても、次を混同しないことを確認します。

```text
artifact acquisition path
  != artifact identity
  != logical Realization / Capability identity
  != historical Exact Binding / Provenance
  != canonical Decision / Observation meaning
```

ISSUE-000070とISSUE-000072は交換軸が異なります。

```text
ISSUE-000070
  = Cognitive Method側のinference runtime version exchange
  = fixed scopeでResolved

ISSUE-000072
  = Capability Provider側のTEI executable / Provider Plan version exchange
  = actual revision BがOpen
```

## Requirement boundary

ISSUE-000070ではREQ-0001、REQ-0004、REQ-0021、SCN-0005、SCN-0015へ再照合し、既存Requirement / Contractで表現可能と判断しました。新しいStable Requirement / Acceptance Scenario / Universal Contract fieldは追加していません。

ISSUE-000072ではactual B実行後にREQ-0001、REQ-0007、REQ-0021、SCN-0014、SCN-0018へ戻ります。Provider-neutral Observationの隣接境界としてREQ-0022も確認対象になり得ます。

```text
version exchange implementation exists
  != independent Product failure observed
  != new Stable Requirement needed
```

## Current execution prerequisite

ISSUE-000072のactual E2 / E3は、特定端末や特定のRemote Desktop接続を成立条件にしません。

actual実行に必要なのは、各stageが要求する固定identityとtoolchainを配置できる**適切なLinux / amd64実行環境**です。

E2を先行回収する最低条件は次です。

- exact revision B TEI sourceを取得できること、またはcredential-free exact-B Git Data snapshotをoffline E2環境へ渡せること
- exact revision A fixed reference input。取得元はexact A checkoutまたはverified historical A Evidence bundleのどちらか一方
- revision B execution boundaryがtracked / untracked / ignored entryを含まずcleanであること
- exact A checkoutを使う場合はfixed-input execution boundaryもtracked / untracked / ignored entryを含まずcleanであること
- historical A Evidence bundleを使う場合はA source commit、historical binary / Provider Plan digest、actual workspace / durable run / plugin lock Git object identityが固定値へ一致すること
- E2 historical TEI build用Go `1.23.2`
- inputから分離されたsafe Evidence出力directory

snapshot transportを使う場合、online T1 captureとoffline T2 E2を同一hostで行う必要はありません。T1ではruntime credentialをsnapshotへ保存せず、T2ではruntime GitHub credentialを要求しません。snapshotはsource acquisition identityではなくcross-environment transport Provenanceとして扱います。

E3まで同じ機会に実行する場合は、上記に加えてcurrent SOZA checkoutとcurrent SOZA E3 live-test要件を満たすGo toolchainを用意します。E3 toolchainを後から用意する場合は、保存済みE2 partial report / bundleをstrictに再検証したうえでresume runnerからE3だけを実行できます。

signed commit objectの独立再構成やhistorical bootstrap payloadは、上記exact revision B source materializationの代替にはしません。commit object identity、source checkout / snapshot materialization、working-tree purity、actual buildは別々のEvidence境界です。

どの端末・runner・外部実行基盤を使うかはexecution mechanismであり、Product Requirement / Capability identity / Universal Contractではありません。

```text
specific execution host not selected
  != TEI incompatibility
  != SOZA Adapter failure
  != ISSUE-000072 blocked by Product semantics
```

したがって、今後は特定端末の復帰待ちをPMS-06のcurrent blockerとして扱わず、GitHub private repository accessを持つonline capture surfaceが利用可能になればactual snapshotを生成し、Linux/amd64 E2環境へtransferしてactual E2を先行回収します。E2がfailureなら専用auditで停止し、E2が成功した場合だけstrict verification後にE3へ進みます。

## 次にEvidence強度が上がる条件

現在のPMS-06で次にEvidence強度が上がる主対象はISSUE-000072です。

snapshot transportを使う場合のoperator向け手順は`runtime/TEI_E2_SNAPSHOT_TRANSPORT_ACTUAL_RUNBOOK_2026-09-07.md`を正とし、次の順で進めます。

```text
T1 online exact-B Git Data snapshot capture
  ↓
credential-free snapshot transfer
  ↓
T2 offline exact-B reconstruction
  ↓
actual revision B E2 partial
  ↓
E2 resultで分岐
```

E2成功時:

```text
exact-B / exact-A strict bundle verification
  ↓
current SOZA E3 resume
  ↓
必要な場合だけ report-pair reconcile
  ↓
canonical Resolution audit
```

E2 failure時:

```text
stage-aware E2 failure report
  ↓
E2 partial failure Resolution audit
  ↓
E3へ進まない
  ↓
resolutionCandidate=false / ISSUE-000072 Openを維持
```

E3 toolchainとdirect exact-B source acquisitionを同時に用意できる場合はcanonical `run_tei_version_exchange_evidence.py`でE2 → E3を一度に実行する経路も有効です。snapshot / partial / resumeはfull one-shotの意味を弱める別基準ではなく、同じcomparison axisとcanonical reportへ戻る段階実行経路です。

途中停止した場合は、保存されたmachine-readable stageまでをEvidenceとし、自然言語logやStatic Evidenceからactual process結果を先取りしません。path configurationやworking-tree purity / historical bundle identityの事前拒否はE2 / E3 process failureへ読み替えません。fixed-Bのsource-level compile矛盾も、canonical actual buildを観測するまではactual build failureへ昇格させません。

ISSUE-000070について再実行が必要になるのは、Reopen conditionに該当するEvidenceやContract driftが観測された場合です。Resolvedであることを理由に任意runtime portabilityや成果品質へ主張を広げません。

## Stop line

```text
ISSUE-000070 fixed-scope runtime exchange Resolved
  != arbitrary runtime portability
  != outcome quality satisfied

ISSUE-000072 snapshot / E2 / failure-audit path ready
  != actual exact-B snapshot acquired
  != canonical revision B actual build result
  != Provider Plan PASS / FAIL observed
  != current SOZA E3 result observed
  != ISSUE-000072 Resolved
  != E4 Operational portability
  != v0.2.0 supported scope expanded
  != Adoption / Outcome Evidence
```