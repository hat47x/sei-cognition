# ISSUE-000072: TEI executableの取得・version交換後もProvider Observation境界を保てるか検証する

Status: **Open**  
Priority: **1**  
Related ADRs: **ADR-0013, ADR-0019, ADR-0021, ADR-0024**  
Product Milestone: **PMS-06**  
Updated: 2026-09-07

## Goal

ISSUE-000065で成立したfixed-artifact actual TEI CLI executionを一つのrevisionへ固定された成功例にとどめず、**TEI executableのsource revisionや取得経路を交換した後も、SEIがProvider固有の実行面とcurrent Capability Observationの意味境界を混同せず扱えるか**を検証する。

少なくとも次を判別できる状態にする。

```text
artifact acquisition path
  != artifact identity
  != TEI Provider surface compatibility
  != SEI Capability Observation identity
```

version交換後のbinaryやProvider Plan bytesが旧revisionと一致することは要求しない。一方、historical revision Aのsource / binary / output identityを保持したままrevision Bを別の外部実現として観測し、current Adapterで意味を壊さず解釈できるかを確認する。

## Background

ISSUE-000061では、private repositoryの取得・credentialと、TEI executableのprocess invocation、Provider固有JSONの解釈、SEI Capability Observationへのmappingを分離した。

ISSUE-000065では、次の固定revisionについてactual CLI build / executionとSEI Adapter接続までScoped Executable Evidenceが成立した。

- Repository: `hat47x/tei-platform`
- Source commit: `48a7ca1fe8a9538e9e9be3e1ee08ef14804c8f67`
- CLI: `cmd/tei`
- Command: `deployment-provider-plan`
- actual binary SHA-256: `31f0298b47f9caaa93cd4b2da538cda72e23e5b518f2d0ddad2cf98c46882154`
- actual Provider Plan SHA-256: `39eafb26cf189681e0bd2ff46fcaf000cbe2f860cf698765bbadac6dfbd2a950`

ただしISSUE-000065は、arbitrary / future TEI versionとの互換性、binaryの正式配布、credential lifecycle、Operational portabilityを未検証として残している。

2026-09-05の追加実証では、旧revision AのGitHub Actions Evidence artifactをGitHub connector経由で再取得し、actual bundle内のsource commit、binary SHA-256、Provider Plan SHA-256を再計算して既存Evidenceと一致することを確認した。さらに、artifact内に保存されたworkspace / durable run / plugin lock bytesからGit object identityを独立再計算し、historical Aの固定値へ一致することも確認した。

同時に、2026-09-05時点のTEI current mainをrevision B候補として固定した。

- source commit: `1a7028d444fcae60a1c4f2f2d247456f4c7c35be`
- evidence branch: `evidence/sei-e3b-p2-version-exchange-2026-09-05`
- workflow commit: `5e87cd18967b6d86001cc4d5229bd4886b94e30d`

revision Bを旧revisionと同じ`deployment-provider-plan`条件で実行するEvidence workflow Run `33913500170`を起動したが、attempt 1 / 2ともjob stepが一つも開始される前にfailureとなった。

```text
GitHub-hosted job start failure
  != TEI build failure
  != Provider surface incompatibility
  != SEI Adapter incompatibility
```

このため、revision B actual executionは現時点ではNot Yet Verifiedである。

2026-09-07には、exact revision BのGit objectへ束縛したsource-level監査で、`cmd/tei`に決定論的なcompile矛盾候補が観測された。`cmd/tei/main.go`と`cmd/tei/validation_output.go`が同一`package main`で`validateWorkspace`を二重定義し、後者が参照する`workspace.DiagnosticFromLoadError`もfixed-B側の`SourceDiagnosticFromError`と一致しない。既知のbuild-fix commit `3b928502...`はfixed-Bのancestorではなくdivergedである。

これはexact-B source内容に対するStatic Evidenceであり、canonical actual checkoutをGo 1.23.2 / Linux amd64でbuildした結果ではない。

```text
deterministic source-level compile contradiction
  != canonical actual revision B build FAIL
  != Provider Plan failure
  != SEI Adapter incompatibility
```

したがって比較軸は変更せず、actual E2でfixed-Bをそのまま検証する。

その後、GitHub-hosted executionとは独立してactual Bを検証できるよう、repository-local経路を段階的に整備した。2026-09-06時点では、少なくとも次が実装済みである。

- revision B execution-source Git identity verifier
- revision A fixed reference input identity verifier
- historical A Evidence bundle内fixed reference bytesを外部固定Git object identityへ照合し、安全にmaterializeするhelper
- tracked変更 / untracked / gitignored entryをexecution source / checkout fixed input境界から排除するworking-tree purity guard
- A / B Provider Plan source surfaceの静的比較
- self-contained local Git object databaseから独立exact-B checkoutを作るhelper
- GitHub Git Data APIからexact-B sourceをcontent-addressedに再構成するacquisition helper
- exact-B build source + exact-A fixed reference inputによるprepositioned Evidence runner
- verified Evidence bundleからcurrent SEI `teiintegration` live testへ接続するAdapter compatibility runner
- E2用GoとE3用current SEI Goを別executableとして連続実行するcanonical orchestrator
- GitHub acquisitionからcanonical E2 → E3へ接続するone-shot wrapper
- GitHub / localのactual開始前preflight
- GitHub one-shot自身によるsource acquisition前のautomatic preflight
- source temporary parentの副作用なしpreflightとactual直前再検査
- Git object / process-level Git config injectionをexecution source identityから分離するcontrolled Git environment
- E2 / E3のprocess-level Go build/test overrideをambient environmentから分離するcontrolled Go environment
- E2 exact Go `1.23.2` / Linux amd64、E3 current `runtime/go/go.mod` minimum / Linux amd64を、`go version`とcontrolled `go env GOOS GOARCH`の両方で確認するtoolchain identity guard
- E2 / E3 failureを外部観測可能なstageへ分けて記録するstage-aware diagnostics
- revision B / SEI / revision A inputとEvidence outputを分離し、symlinkや暗黙上書きを拒否するpath-safety guard
- GitHub / local取得経路別のpost-run Resolution audit
- E3 Goをまだ用意できない環境でもGitHub acquisitionからactual E2だけを先行回収できるE2 partial runner
- E2 bundleをexact revision B source commitとexact revision A fixed reference identityへbindingして再検証するstrict verifier
- 保存済みE2 partial Evidenceからrevision B source取得 / E2 build / Provider Planを再実行せずcurrent E3だけを後日実行するresume runner
- resume後のcanonical report publishまでは成功しGitHub wrapper report publishだけが中断した場合に、E3を再実行せずreport pairを復旧するreconcile runner
- E2 partial actual → strict re-verification → later E3 resume → 必要時reconcile → Resolution auditを一続きにしたoperator runbook

version交換の比較軸については、revision AとBの`reference/workspace` treeが異なることを確認したため、**B checkout内のreference inputを使わず、historical revision Aのfixed reference inputをexact A checkoutまたは検証済みhistorical A Evidence bundleから与える**形へ補正した。

```text
executable/build source
  = exact revision B

fixed reference input
  = exact revision A

fixed input acquisition
  = exact A checkout
  or verified historical A Evidence bundle
```

historical bundle経路はA source checkoutを復元したものとは扱わない。bundle metadataのA source commit、historical binary / Provider Plan SHA-256、およびactual reference bytesから再計算したworkspace / durable run / plugin lock Git object identityを固定値へ照合したうえでfixed inputだけをmaterializeする。

これにより、runtime revision、reference input identity、reference input acquisition pathを混同しない。

また、E2 historical buildはexact `go1.23.2 linux/amd64`、E3 current SEI live testはcurrent `runtime/go/go.mod`を満たすLinux / amd64 Go executableを使う。両者とも`GOTOOLCHAIN=local`とし、ambient `GOOS` / `GOARCH`等を除外したcontrolled environmentで`go env GOOS GOARCH = linux / amd64`を再確認する。同じ`go` command名を同一toolchain identityとは扱わず、combined runnerでは2つのGo executableを別々に明示する。

actual E2 → E3は特定hostや特定のRemote Desktop接続を成立条件にしない。exact revision B / exact revision A fixed input / current SEI、必要toolchain、入力から分離したEvidence出力を配置できる適切なLinux / amd64実行環境で実行する。

また、2026-09-05時点で`hat47x/tei-platform`のGitHub Releasesは0件であり、正式なTEI executable distribution surfaceはまだ確認できない。

## Questions

1. TEI source revision / binary identity / Provider Plan output identityを、Capability identityへ昇格させずにどこまでProvenanceとして保持すればよいか。
2. revision A / BでbinaryやProvider Plan bytesが異なっても、current Adapter-local DTOとCapability Observationへのmappingを維持できるか。
3. executable取得経路がsource build、GitHub Actions artifact、将来のRelease asset等へ変わっても、同じartifact identity検証へ戻せるか。
4. Provider Plan surfaceがversion間で変化した場合、Adapter-local compatibility changeとして扱えるか、それとも既存Requirement / Contractでは表現できないProduct failureがあるか。
5. historical revision Aを後から再取得・再検証できなくなった場合、どのEvidenceをdurableに保存する必要があるか。
6. 正式な配布・署名・更新channelをSEI側で標準化する必要が本当にあるか。それともTEI側またはdeployment policyへ残すべきか。
7. executable revisionだけを交換したい検証で、workspace / durable run / plugin lock等のreference input identityをどこまで固定すべきか。

## Constraints

- TEIをUniversal Provider ontologyへ昇格させない。
- TEI CLIのfield setをSEI Universal Contractへ複製しない。
- repository URL、GitHub Actions、credential名、artifact store、Release方式をsemantic identityへ含めない。
- acquisition pathとactual artifact identityを分離する。
- historical revision Aのsource / binary / Provider Plan identityをrevision B追加で書き換えない。
- binary SHA-256やProvider Plan SHA-256が異なることだけをcompatibility failureにしない。
- Provider Planの意味的差分を、byte比較だけで良否判定しない。
- GitHub-hosted runner failureをTEI Product failureへ昇格させない。
- artifact bundle検証PASSをSEI Adapter互換、Operational Evidence、Release Evidenceへ昇格させない。
- 静的なProvider Plan source continuityをactual revision B execution PASSへ昇格させない。
- source-level compile矛盾を、canonical actual revision B build failureやSEI Adapter incompatibilityへ昇格させない。
- fixed revision Bを、build-fixを含む後続revisionへ無言で差し替えない。後継revisionを検証対象へ加える場合は、Bのexact bindingとEvidenceを保持したまま別revisionとして明示的に固定する。
- B executableの検証で、B checkout内の変化したreference workspaceをhistorical fixed inputへ無言で置き換えない。
- Git object identityが一致していても、execution boundary内のtracked変更、untracked entry、gitignored entryをactual source / checkout fixed inputへ混入させない。
- historical bundle取得時は、bundle metadataだけをfixed input identityとして信頼せず、actual reference bytesからGit object identityを再計算して固定値へ照合する。
- historical bundleからfixed inputを取得しても、A source checkoutを再構成したEvidenceへ昇格させない。
- Evidence outputをrevision B / SEI checkout配下へ置かず、checkout取得時はrevision A checkout配下にも置かない。Evidence directoryがそれらcheckoutを包含する配置もしない。
- historical bundle取得時は入力bundleをEvidence directory配下に置かない。
- Evidence output path / ancestor symlinkやstandalone E2 archiveの暗黙上書きを許可しない。
- Evidence path configuration rejectionをE2 build failure、Provider Plan failure、SEI Adapter failureへ昇格させない。
- stderr / stdoutの文言だけからTEI内部のworkspace load / validation / plugin lock等のsubstageを推定しない。
- Go live testの文言だけからstrict decode / Capability Observation validator等のsubstageを推定しない。
- 特定host / runner / Remote Desktop接続をProduct semantics上の成立条件にしない。
- 新しいStable Requirement / Universal Contract fieldは、actual B Evidenceまたは独立したProduct failureが確認される前に追加しない。
- 現時点でTEI GitHub Releaseの新設や特定配布方式を完了条件にしない。

## Required scenarios / experiments

### E0 — revision A historical artifact再検証

- historical Evidence artifactを取得できる。
- bundle内source commitが固定A revisionへ一致する。
- actual binary SHA-256がmetadataと固定Evidenceへ一致する。
- actual Provider Plan SHA-256がmetadataと固定Evidenceへ一致する。
- archive path traversal、symlink / hardlink / device等を受理しない。
- historical bundle内fixed workspace / durable run / plugin lock bytesを固定Git object identityへ再照合できる。

### E1 — acquisition-independent bundle verification

- source build、workflow artifact、将来の別取得経路のいずれでも、取得済みbundleを同じrepository-local verifierへ渡せる。
- verifierは取得credentialやGitHub run IDをartifact identityの必須条件にしない。
- optional expected source / binary / Provider Plan identityへ照合できる。
- legacy bundleでも、外部から固定したreference identityへactual workspace / durable run / plugin lock bytesを照合できる。

### E2 — revision B actual executable

- revision B source identityを固定する。
- revision B build sourceと、checkout取得時のrevision A fixed reference inputの対象境界にtracked変更、untracked entry、gitignored entryがないことを確認する。
- actual `cmd/tei`をbuildまたは同等の固定artifactとして取得する。
- executable/build sourceはexact revision Bへ固定する。
- historical fixed reference inputは取得経路にかかわらずexact revision Aへ固定する。
- A fixed input acquisitionはexact A checkoutまたは検証済みhistorical A Evidence bundleのどちらか一方とし、acquisition modeをProvenanceとして記録する。
- Evidence出力を入力checkoutから分離したnon-symlink pathへ置き、historical bundle取得時は入力bundleをEvidence directory配下へ置かず、既存standalone archiveを暗黙上書きしない。
- path configuration rejectionはactual E2 process開始前の入力拒否として扱う。
- actual execution hostはLinux / amd64とする。
- E2 Go executable identityはexact `go1.23.2 linux/amd64`とし、controlled environmentで`go env GOOS GOARCH = linux / amd64`を確認する。
- actual `deployment-provider-plan`を実行する。
- Bのactual binary / Provider Plan SHA-256を記録する。
- job割当や取得failureをCLI互換性failureと区別する。
- source identity / fixed input identity / platform / Go toolchain / build / Provider Plan process / output validation / Evidence packagingのどの外部stageまで成立したかを区別できる。
- `deployment-provider-plan` process内部のworkspace load / validation / durable run / plugin lock等は、machine-readable Evidenceが得られた場合だけ追加で細分化する。

### E3 — current SEI Adapter compatibility

- revision B actual binaryをcurrent `runtime/go/teiintegration`から別OS processとして起動する。
- Provider Planをcurrent Adapter-local DTOでstrictにdecodeする。
- current Capability Observation validatorを通る。
- `availability = true`と`provider_plan_resolved = true`を観測できる。
- TEI固有fieldをUniversal Capability Observationへ漏らさない。
- B source、A fixed reference input、bundle identityをMapping Provenanceから追跡できる。
- どのSEI source / local Go toolchainでlive検査したかを記録する。
- E3 Go executableはcurrent `runtime/go/go.mod`のdirective以上かつLinux / amd64とし、controlled environmentで`go env GOOS GOARCH = linux / amd64`を確認する。
- SEI source identity / bundle verification / staging / fixed input identity / Go toolchain / existing `teiintegration` live-test processのどの外部stageまで成立したかを区別できる。
- live-test内部のstrict decode / mapping / validator等は、machine-readable Evidenceが得られた場合だけ追加で細分化する。

### E4 — A/B historical separation

- revision B追加後もrevision Aのsource / binary / output Evidenceを変更しない。
- A/Bの取得経路、source identity、binary identity、Provider Plan identityを別々に追跡できる。
- Provider Planの差がある場合、その差をbyte drift、Adapter compatibility、semantic changeへ分けて評価できる。
- build sourceとfixed reference inputのProvenanceを別々に追跡できる。
- fixed reference inputのidentityとacquisition pathを別々に追跡できる。

### E5 — distribution / credential boundary assessment

- current TEIの実際の配布面を確認する。
- artifact retention、private repository credential、Release asset等をProduct semanticsと分離する。
- 正式なdistribution contractが必要かを、actual A/B Evidenceの後で再評価する。

```text
Design Evidence
  != Executable Evidence
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

## Current Evidence

2026-09-07時点のcurrent snapshotは次である。過去のsynthetic test件数は、その時点の実装検査記録として各PR / readiness文書へ残し、このIssueでは現在のactual-ready境界を正とする。

```text
revision A fixed-artifact actual TEI execution
  = Scoped Executable Evidence available from ISSUE-000065

revision A artifact re-acquisition / bundle identity re-verification
  = observed / verified

revision A fixed reference input artifact bytes
  = workspace tree / durable run blob / plugin-lock blob independently revalidated against fixed Git object identities

revision B source identity
  = fixed to 1a7028d444fcae60a1c4f2f2d247456f4c7c35be

version-exchange comparison axis
  = exact-B build source + exact-A fixed reference input

local exact-B checkout preparation
  = implemented

GitHub content-addressed exact-B source acquisition
  = implemented

GitHub / local actual-run preflight
  = implemented

GitHub one-shot automatic preflight before acquisition
  = implemented

GitHub source temporary parent preflight / actual recheck
  = implemented; side-effect-free resolution uses TMPDIR -> TEMP -> TMP -> /tmp

source / fixed-input Git object identity and working-tree purity
  = implemented; tracked / untracked / ignored entries are rejected in execution boundary

controlled Git environment
  = implemented for canonical source verifier, local preparation/preflight, GitHub acquisition, and E3 SEI source identity

A fixed-input acquisition modes
  = exact A checkout or verified historical A Evidence bundle

E2 / E3 separate toolchains
  = implemented and explicit in canonical combined runner

E2 Go identity
  = exact go1.23.2 linux/amd64 + controlled target linux/amd64

E3 Go identity
  = current runtime/go/go.mod minimum + Linux/amd64 executable/controlled target

E2 / E3 process-level Go build/test environment isolation
  = implemented

E2 / E3 stage-aware diagnostics
  = implemented; outer stage and machine-readable substage boundary separated

Evidence output / input separation and symlink guards
  = implemented

E2 Evidence bundle no-overwrite publish
  = implemented

canonical / wrapper report publish guards
  = implemented

GitHub / local post-run Resolution audit
  = implemented

E2 partial GitHub acquisition path
  = implemented; actual E2 Not Yet Verified

E2 exact-B / exact-A strict bundle verification
  = implemented; actual E2 bundle not yet available

E2 partial -> later E3 resume
  = implemented; actual E3 Not Yet Verified

interrupted resume report-pair reconciliation
  = implemented; recovery path only, not Evidence promotion

E2 partial actual operator runbook
  = implemented through strict verification / resume / optional reconcile / Resolution audit

Provider Plan output surface A/B
  = strong static continuity observed

fixed-B source-level CLI compile contradiction
  = observed against exact Git object identity; actual E2 build failureではない

known fixed-B build-fix lineage
  = commit 3b928502... is diverged, not an ancestor of fixed B

workspace / validation / IR input interpretation
  = changed; actual fixed-input execution required

specific execution host
  = not selected; any suitable Linux / amd64 environment may be used

revision B workflow attempt 1 / 2
  = failure before any job step; not counted as Product failure

revision B actual CLI build / execution
  = Not Yet Verified

revision B Provider Plan
  = Not Yet Observed

revision B current SEI Adapter live compatibility
  = Not Yet Verified
```

repository-sideで、actual開始前のacquisition / identity / purity / preflight / orchestrationと、actual後のResolution auditまでは実装済みである。E2とE3を同じ機会に実行できない場合も、E2 partialを保存し、strict再検証後にE3だけを後日resumeして同じcanonical report / Resolution auditへ戻せる。したがって次にEvidenceの高さを本質的に上げる作業は、synthetic hardeningの追加ではなくactual revision B E2である。

#316のStatic Evidenceにより、fixed-BはE2 build stageで停止する可能性が具体化した。しかしactual E2前に結論を先取りしない。

```text
repository-side actual path
  = implemented through E2 partial / strict verification / E3 resume / optional reconcile / post-run audit

next substantive Evidence
  = actual revision B E2

actual B E2 PASS
  -> current SEI E3へ進む

actual B E2 confirms build failure
  -> Bのexact binding / failure Evidenceを保持する
  -> Bを後続revisionへ無言で差し替えない
  -> BについてE3 Adapter incompatibilityを主張しない
  -> ISSUE-000072はOpenを維持する
  -> version交換後のAdapter互換性を引き続き問う場合だけ、後続revisionを別候補として明示的に固定する
```

operator向けactual手順は次を正とする。

- `runtime/TEI_E2_PARTIAL_ACTUAL_RUNBOOK_2026-09-06.md`
- `runtime/TEI_VERSION_EXCHANGE_E2_PARTIAL_DELTA_2026-09-06.md`

現在の主な実装・観測記録は次へ置く。

- `runtime/integration/verify_tei_evidence_bundle.py`
- `runtime/integration/verify_tei_version_exchange_e2_bundle.py`
- `runtime/integration/verify_tei_execution_source_identity.py`
- `runtime/integration/prepare_tei_fixed_reference_input.py`
- `runtime/integration/prepare_tei_revision_b_checkout.py`
- `runtime/integration/prepare_tei_revision_b_source.py`
- `runtime/integration/preflight_tei_version_exchange_from_github.py`
- `runtime/integration/preflight_tei_version_exchange_local.py`
- `runtime/integration/run_tei_revision_b_prepositioned.py`
- `runtime/integration/run_tei_revision_b_e2_from_github.py`
- `runtime/integration/run_tei_bundle_adapter_compatibility.py`
- `runtime/integration/run_tei_version_exchange_evidence.py`
- `runtime/integration/run_tei_version_exchange_from_github.py`
- `runtime/integration/run_tei_version_exchange_resume_from_e2_partial.py`
- `runtime/integration/reconcile_tei_e2_partial_resume_reports.py`
- `runtime/integration/audit_tei_version_exchange_resolution.py`
- `runtime/integration/audit_tei_version_exchange_resolution_local.py`
- `runtime/TEI_VERSION_EXCHANGE_EVIDENCE_2026-09-05.md`
- `runtime/TEI_PROVIDER_SURFACE_STATIC_COMPATIBILITY_2026-09-05.md`
- `runtime/TEI_VERSION_EXCHANGE_EXECUTION_READINESS_2026-09-05.md`
- `runtime/TEI_VERSION_EXCHANGE_TOOLCHAIN_READINESS_2026-09-05.md`
- `runtime/TEI_VERSION_EXCHANGE_FAILURE_STAGES_2026-09-05.md`
- `runtime/TEI_VERSION_EXCHANGE_CURRENT_READINESS_2026-09-06.md`
- `runtime/TEI_VERSION_EXCHANGE_E2_PARTIAL_DELTA_2026-09-06.md`
- `runtime/TEI_E2_PARTIAL_ACTUAL_RUNBOOK_2026-09-06.md`
- `runtime/TEI_VERSION_EXCHANGE_POST_RUN_AUDIT_2026-09-06.md`
- `runtime/evidence/tei-revision-b-static-cli-compile-contradiction-20260907/evidence.json`
- `runtime/evidence/tei-revision-b-static-cli-compile-contradiction-20260907/README.md`

## Deliverables

- TEI Evidence bundle verifier
- bundle verifierのnegative control
- revision B / revision A fixed inputのGit identity verifier
- historical A Evidence bundleのexternal fixed-input binding / materialization helper
- source / checkout fixed input working-tree purity guard
- revision A / B identityと取得経路を分けたEvidence report
- Provider Plan source surface / input interpretation差分のStatic Evidence
- local / GitHubのexact-B source acquisition / materialization helper
- GitHub / local actual-run preflight
- exact-B build source + exact-A fixed inputのprepositioned Evidence runner
- E3未準備環境でactual E2だけを先行回収するE2 partial runner
- E2 bundleをexact-B / exact-Aへbindingするstrict verifier
- verified bundleからcurrent SEI Adapter live testへ接続するrunner
- E2 / E3を別toolchainで連続実行し段階別reportを残すcombined runner
- 保存済みE2 partialからE3だけを後日実行するresume runner
- interrupted wrapper publishをE3再実行なしで復旧するreconcile runner
- GitHub acquisitionからcanonical E2 / E3へ接続するone-shot wrapper
- Evidence output / input separation guard
- E2 / E3 failure stage taxonomyとnegative control
- GitHub / local post-run Resolution audit
- E2 partial actual operator runbook
- revision B actual artifactを取得できた場合のB verification report
- A/B Adapter compatibility Evidence
- Requirement / Contract再照合結果
- 必要な場合のみ、後続ADR / Profile / distribution policy proposal

## Resolution

次をすべて満たした時点でResolvedにできる。

1. revision A historical artifactを現在のverifierで再検証できる。
2. revision Bのactual executableまたは固定Evidence bundleを取得し、そのsource / binary / Provider Plan identityを記録できる。
3. revision B actual `deployment-provider-plan`がexact-A fixed reference inputで成立するか、不成立ならrepository-local E2 stageのどこで停止したかを判別できる。TEI内部substageはmachine-readable Evidenceがある場合だけ追加で特定する。
4. current SEI Adapterでrevision Bを実行し、Capability Observationへのmapping成立可否を確認する。不成立ならrepository-local E3 stageのどこで停止したかを判別し、live-test内部原因はmachine-readable Evidenceがある場合だけ追加で特定する。
5. revision B追加後もrevision A Evidenceを不変に保持する。
6. acquisition / credential / artifact identity / fixed input identity / Provider compatibilityの境界をEvidenceで確認する。
7. REQ-0001、REQ-0007、REQ-0021、SCN-0014、SCN-0018へ再照合し、新しいStable Requirementが必要かを監査する。
8. 自然な日本語を最重要視した最終意味監査を行う。

#316のStatic EvidenceだけではResolution条件2〜4を満たさない。actual E2でfixed-Bのbuild failureが確認された場合も、そのfailureはBのExecution Evidenceとして保存するが、BをSEI Adapter incompatibilityへ読み替えず、条件4を満たしたことにも数えない。ISSUE-000072はOpenを維持し、Adapter version-exchangeの問いを継続する場合はBのexact bindingを変更せず、後続revisionを別の検証対象として明示的に固定する。

working-tree purity、Evidence output分離、toolchain固定はactual E2 / E3 Evidenceを信頼するためのexecution preconditionであり、新しいProduct outcomeをResolution Criteriaへ追加するものではない。

formal Release asset、特定credential方式、特定CI provider、特定execution host、binary byte同一性、Provider Plan byte同一性はResolution条件にしない。

## Reopen conditions

Resolved後も次の場合は再開する。

- historical revisionのartifact identityを後から特定できない。
- acquisition path変更だけでCapability identityが変化する。
- TEI version交換でProvider固有fieldがUniversal Capability Observationへ漏れる。
- current Adapterがversion固有fieldをUniversal semanticsとして要求する。
- Provider Plan差分をbyte driftとsemantic incompatibilityへ分離できない。
- build sourceとfixed reference inputのProvenanceを分離できない。
- fixed reference input identityとacquisition pathを分離できない。
- distribution / credential方式をsemantic identityへ取り込まないと履歴再構成できないことが判明する。
- Product Value / Requirementが変更される。

## CI / verification

GitHub ActionsはこのIssueの意味上の成立条件にしない。

TEI側Evidence workflowを利用できる場合はactual artifact生成の一経路として使うが、jobが開始されなかったrunをTEI compatibility failureへ数えない。取得済みartifactはrepository-local `verify_tei_evidence_bundle.py`へ戻して再検証する。ISSUE-000072のE2として評価する場合は、さらに`verify_tei_version_exchange_e2_bundle.py`でexact revision B source commitとexact revision A fixed reference identityへstrictにbindingする。

actual Bのrepository-local経路では、exact revision B checkoutをbuild sourceとして`run_tei_revision_b_prepositioned.py`へ渡す。revision B sourceは、self-contained local cloneから独立exact-B checkoutを作るか、GitHub Git Data APIからcontent-addressedに再構成できる。GitHub acquisitionを使う場合は、one-shot runner自身がsource取得前に副作用なしpreflightを必須化する。

E3 Goを同時に用意できない場合は、`TEI_E2_PARTIAL_ACTUAL_RUNBOOK_2026-09-06.md`をoperator手順の正本として`run_tei_revision_b_e2_from_github.py`でE2だけを先行回収する。取得したpartial bundleは`verify_tei_version_exchange_e2_bundle.py`でexact-B / exact-Aへstrict再検証し、後日`run_tei_version_exchange_resume_from_e2_partial.py`でE3だけを実行してcanonical reportへ戻す。resumeでcanonical report publish後のGitHub wrapper report publishだけが中断した限定状態では、`reconcile_tei_e2_partial_resume_reports.py`でE2 / E3を再実行せずreport pairを復旧する。

exact revision A fixed inputは次のどちらか一方から取得する。

- `--reference-source-repo`: exact revision A checkout。Git object identity、exact HEAD、対象境界のtracked / untracked / ignored entry不存在を確認する。
- `--reference-evidence-bundle`: verified historical revision A Evidence bundle。bundle metadataのA source commit、historical binary / Provider Plan SHA-256、actual workspace / durable run / plugin lock bytesから再計算したGit object identityを固定値へ照合してから、一時領域へfixed inputだけをmaterializeする。

両経路はmutually exclusiveとし、fixed input identityはどちらもexact revision Aへ固定する。historical bundle経路をA source checkout reconstructionへ昇格させない。

Evidence archive / directoryはrevision B、SEI checkoutから分離したnon-symlink pathへ置き、checkout取得時はrevision A checkoutからも分離する。historical bundle取得時は入力bundleをEvidence directory配下に置かない。path configurationが不正な場合はactual processを開始せず、E2 / E3 failure stageへ読み替えない。standalone E2は既存archiveを暗黙上書きしない。GitHub source temporary parentもSEI / revision A / Evidence境界から分離し、preflightとactual取得直前の両方で再検査する。

B Evidence bundleを得た後は、cleanなSEI checkoutで`run_tei_bundle_adapter_compatibility.py`を実行し、既存`runtime/go/teiintegration.TestLiveTEIProviderPlan`へ接続する。Bがactual E2 build stageで停止して有効なEvidence bundle / executableを得られない場合、このE3経路はBについて未到達であり、Adapter incompatibilityとは扱わない。runnerのsynthetic testやStatic Evidenceはactual TEI process executionの代替ではない。

E2からE3までを一度に実行する場合は`run_tei_version_exchange_evidence.py`を使い、TEI historical build用にはexact `go1.23.2 linux/amd64`、current SEI live-test用にはcurrent `runtime/go/go.mod`を満たすLinux / amd64 Go executableを別々に明示する。両toolchainともambient `GOOS` / `GOARCH`等を除外したcontrolled environmentで`go env GOOS GOARCH = linux / amd64`を再確認し、`GOTOOLCHAIN=local`を使う。A fixed input acquisition modeはcomparison axisへ記録する。failure reportは上位`E2` / `E3`とstage-aware `substage`を分離し、通常の例外文言からsubstageを捏造しない。

actual後は取得経路に応じて`audit_tei_version_exchange_resolution.py`または`audit_tei_version_exchange_resolution_local.py`へ戻し、Resolution条件1〜6をmachine-readable Evidenceから再監査する。E2 partial → E3 resumeのGitHub acquisition経路も、reconcileが必要だった場合を含め、最終的に同じ`audit_tei_version_exchange_resolution.py`へ戻す。条件7〜8はmanual reviewとして残し、自動でIssueをResolvedへしない。

特定hostやRemote Desktop接続の復帰を待つことは完了条件にしない。上記identity / purity / toolchain / path条件を満たせる適切なLinux / amd64実行環境を用意できた時点でactual E2、その後E3へ進む。

## Natural Japanese review

PMS-06、ISSUE-000061 / 000065、ADR-0013 / 0019 / 0021 / 0024、Actual TEI CLI Evidence、current `teiintegration`、revision A Evidence artifact、revision B Evidence workflow attempt 1 / 2、revision B Git object identity、A / B Provider Plan static compatibility、exact-A fixed reference input、historical A Evidence bundle fixed-input binding、local / GitHub exact-B acquisition、E2 prepositioned runner、E2 partial runner、exact-B / exact-A strict bundle verifier、E3 Adapter live runner、toolchain-split combined runner、E2 partialからのlater E3 resume、interrupted report-pair reconciliation、GitHub one-shot / local preflight、E2 / E3 failure-stage instrumentation、Evidence output path safety、source temporary parent、source / checkout fixed-input working-tree purity、actual operator runbook、post-run Resolution audit、fixed-B source-level CLI compile contradictionを照合した。

取得方法、artifact identity、build source、fixed reference input、fixed input acquisition path、Provider固有surface、SEIのCapability Observationを一つにまとめず、今回すでに観測できたことと、revision B actual executionが未検証であることを分離している。

特に、A / Bでworkspace treeが異なることから「B checkout内のsame pathを使えば同じinput」という早合点を修正し、version交換ではB executableへhistorical A inputを与える比較軸へ固定した。さらに、historical A artifactに保存されたactual reference bytesを固定Git object identityへ再照合できることから、A checkoutの有無とA fixed input identityを分離し、checkoutまたはverified historical bundleの二経路へした。ただし後者をA source checkout復元とは扱わない。

また、Static EvidenceでProvider Plan出力surfaceに連続性がある一方、workspace / validation / IRが変化しているためactual検証が必要であることも明記した。

さらに、Git object identityが一致していてもworking treeのignored entryがactual build / checkout fixed inputへ混入し得るため、tracked / untracked / ignoredをexecution boundaryのpurity対象へ含めた。Evidence出力についても、入力checkoutとのoverlap、historical input bundleの包含、symlink、暗黙上書きをactual process前に拒否し、そのconfiguration failureをProvider compatibilityの失敗へ昇格させない。GitHub取得のtemporary parentも同じく入力 / Evidence境界から分離し、preflightを副作用なしに保つ。

Goについては、host platform、Go executable identity、controlled build/test target、Product semanticsを一つにまとめない。E2の`go1.23.2 linux/amd64`とE3のcurrent `go.mod` minimum / Linux amd64はactual Evidenceの再現条件であり、Capability identityではない。ambient `GOOS` / `GOARCH`等を除外したうえでcontrolled targetを再確認しても、それ自体をE2 / E3 PASSへ昇格させない。

actual failureの切り分けでは、stderr / stdoutの自然言語からTEI内部stageやSEI live-test内部stageを推定せず、repository-local runnerが直接観測できる外部境界だけをEvidence stageとして扱う。これにより、診断情報を保持しつつ、原因の高さをEvidence以上に引き上げない。

また、特定host / CI provider / Remote DesktopをProduct semanticsへ持ち込まず、必要な固定identityとtoolchainを配置できる実行環境をexecution mechanismとして分離した。

E2とE3を同時に実行できない場合も、E2 partialを保存してstrictに再検証し、後日E3だけをresumeして同じResolution auditへ戻せる。report publishだけが中断した場合のreconcileもactual E2 / E3の再実行やEvidence昇格とは扱わない。

repository-sideでactual前後の経路が整った現在、追加のsynthetic hardeningだけを進捗として目的化しない。次に意味の高さを上げるのはactual revision B E2である。Bがactual buildを通過した場合はcurrent SEI E3へ進み、buildで停止した場合はBのEvidenceを保持したうえで、必要なら後続revisionを別の検証対象として明示的に固定する。

意味、要求強度、留保、Evidenceの高さを固定したうえで、自然な日本語となることを最重要視して全文を再監査した。