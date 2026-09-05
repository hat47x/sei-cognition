# ISSUE-000072: TEI executableの取得・version交換後もProvider Observation境界を保てるか検証する

Status: **Open**  
Priority: **1**  
Related ADRs: **ADR-0013, ADR-0019, ADR-0021, ADR-0024**  
Product Milestone: **PMS-06**  
Updated: 2026-09-05

## Goal

ISSUE-000065で成立したfixed-artifact actual TEI CLI executionを一つのrevisionへ固定された成功例にとどめず、**TEI executableのsource revisionや取得経路を交換した後も、SOZAがProvider固有の実行面とcurrent Capability Observationの意味境界を混同せず扱えるか**を検証する。

少なくとも次を判別できる状態にする。

```text
artifact acquisition path
  != artifact identity
  != TEI Provider surface compatibility
  != SOZA Capability Observation identity
```

version交換後のbinaryやProvider Plan bytesが旧revisionと一致することは要求しない。一方、historical revision Aのsource / binary / output identityを保持したままrevision Bを別の外部実現として観測し、current Adapterで意味を壊さず解釈できるかを確認する。

## Background

ISSUE-000061では、private repositoryの取得・credentialと、TEI executableのprocess invocation、Provider固有JSONの解釈、SOZA Capability Observationへのmappingを分離した。

ISSUE-000065では、次の固定revisionについてactual CLI build / executionとSOZA Adapter接続までScoped Executable Evidenceが成立した。

- Repository: `hat47x/tei-platform`
- Source commit: `48a7ca1fe8a9538e9e9be3e1ee08ef14804c8f67`
- CLI: `cmd/tei`
- Command: `deployment-provider-plan`
- actual binary SHA-256: `31f0298b47f9caaa93cd4b2da538cda72e23e5b518f2d0ddad2cf98c46882154`
- actual Provider Plan SHA-256: `39eafb26cf189681e0bd2ff46fcaf000cbe2f860cf698765bbadac6dfbd2a950`

ただしISSUE-000065は、arbitrary / future TEI versionとの互換性、binaryの正式配布、credential lifecycle、Operational portabilityを未検証として残している。

2026-09-05の追加実証では、旧revision AのGitHub Actions Evidence artifactをGitHub connector経由で再取得し、actual bundle内のsource commit、binary SHA-256、Provider Plan SHA-256を再計算して既存Evidenceと一致することを確認した。

同時に、2026-09-05時点のTEI current mainをrevision B候補として固定した。

- source commit: `1a7028d444fcae60a1c4f2f2d247456f4c7c35be`
- evidence branch: `evidence/soza-e3b-p2-version-exchange-2026-09-05`
- workflow commit: `5e87cd18967b6d86001cc4d5229bd4886b94e30d`

revision Bを旧revisionと同じ`deployment-provider-plan`条件で実行するEvidence workflow Run `33913500170`を起動したが、attempt 1 / 2ともjob stepが一つも開始される前にfailureとなった。

```text
GitHub-hosted job start failure
  != TEI build failure
  != Provider surface incompatibility
  != SOZA Adapter incompatibility
```

このため、revision B actual executionは現時点ではNot Yet Verifiedである。

その後、GitHub-hosted executionとは独立してactual Bを検証できるよう、次のrepository-local経路を整備した。

- revision B execution-source Git identity verifier
- revision A fixed reference input identity verifier
- tracked変更 / untracked / gitignored entryをexecution source / fixed input境界から排除するworking-tree purity guard
- A / B Provider Plan source surfaceの静的比較
- exact-B build source + exact-A fixed reference inputによるprepositioned Evidence runner
- verified Evidence bundleからcurrent SOZA `teiintegration` live testへ接続するAdapter compatibility runner
- E2用Go 1.23.2とE3用current SOZA Goを分離して連続実行するorchestrator
- E2 / E3 failureを外部観測可能なstageへ分けて記録するstage-aware diagnostics
- revision A / B / SOZA checkoutとEvidence outputを副作用前に分離し、symlinkや暗黙上書きを拒否するpath-safety guard

version交換の比較軸については、revision AとBの`reference/workspace` treeが異なることを確認したため、**B checkout内のreference inputを使わず、historical revision Aのfixed reference inputを別checkoutから与える**形へ補正した。

```text
executable/build source
  = exact revision B

fixed reference input
  = exact revision A
```

これにより、runtime revisionとreference inputの交換を混同しない。

また、E2 historical buildはGo `1.23.2`、E3 current SOZA live testはcurrent `runtime/go/go.mod`と`GOTOOLCHAIN=local`を使うため、同じ`go` command名を同一toolchain identityとは扱わない。combined runnerでは2つのGo executableを別々に明示する。

actual E2 → E3は特定hostや特定のRemote Desktop接続を成立条件にしない。exact revision B / exact revision A fixed input / current SOZA、必要toolchain、checkoutから分離したEvidence出力を配置できる適切なLinux / amd64実行環境で実行する。

また、2026-09-05時点で`hat47x/tei-platform`のGitHub Releasesは0件であり、正式なTEI executable distribution surfaceはまだ確認できない。

## Questions

1. TEI source revision / binary identity / Provider Plan output identityを、Capability identityへ昇格させずにどこまでProvenanceとして保持すればよいか。
2. revision A / BでbinaryやProvider Plan bytesが異なっても、current Adapter-local DTOとCapability Observationへのmappingを維持できるか。
3. executable取得経路がsource build、GitHub Actions artifact、将来のRelease asset等へ変わっても、同じartifact identity検証へ戻せるか。
4. Provider Plan surfaceがversion間で変化した場合、Adapter-local compatibility changeとして扱えるか、それとも既存Requirement / Contractでは表現できないProduct failureがあるか。
5. historical revision Aを後から再取得・再検証できなくなった場合、どのEvidenceをdurableに保存する必要があるか。
6. 正式な配布・署名・更新channelをSOZA側で標準化する必要が本当にあるか。それともTEI側またはdeployment policyへ残すべきか。
7. executable revisionだけを交換したい検証で、workspace / durable run / plugin lock等のreference input identityをどこまで固定すべきか。

## Constraints

- TEIをUniversal Provider ontologyへ昇格させない。
- TEI CLIのfield setをSOZA Universal Contractへ複製しない。
- repository URL、GitHub Actions、credential名、artifact store、Release方式をsemantic identityへ含めない。
- acquisition pathとactual artifact identityを分離する。
- historical revision Aのsource / binary / Provider Plan identityをrevision B追加で書き換えない。
- binary SHA-256やProvider Plan SHA-256が異なることだけをcompatibility failureにしない。
- Provider Planの意味的差分を、byte比較だけで良否判定しない。
- GitHub-hosted runner failureをTEI Product failureへ昇格させない。
- artifact bundle検証PASSをSOZA Adapter互換、Operational Evidence、Release Evidenceへ昇格させない。
- 静的なProvider Plan source continuityをactual revision B execution PASSへ昇格させない。
- B executableの検証で、B checkout内の変化したreference workspaceをhistorical fixed inputへ無言で置き換えない。
- Git object identityが一致していても、execution boundary内のtracked変更、untracked entry、gitignored entryをactual source / fixed inputへ混入させない。
- Evidence outputをrevision B / revision A / SOZA checkout配下へ置かず、Evidence directoryがそれらcheckoutを包含する配置もしない。
- Evidence output path / ancestor symlinkやstandalone E2 archiveの暗黙上書きを許可しない。
- Evidence path configuration rejectionをE2 build failure、Provider Plan failure、SOZA Adapter failureへ昇格させない。
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

### E1 — acquisition-independent bundle verification

- source build、workflow artifact、将来の別取得経路のいずれでも、取得済みbundleを同じrepository-local verifierへ渡せる。
- verifierは取得credentialやGitHub run IDをartifact identityの必須条件にしない。
- optional expected source / binary / Provider Plan identityへ照合できる。

### E2 — revision B actual executable

- revision B source identityを固定する。
- revision B build sourceとrevision A fixed reference inputの対象境界にtracked変更、untracked entry、gitignored entryがないことを確認する。
- actual `cmd/tei`をbuildまたは同等の固定artifactとして取得する。
- executable/build sourceはexact revision Bへ固定する。
- historical fixed reference inputはexact revision Aへ固定する。
- Evidence出力を入力checkoutから分離したnon-symlink pathへ置き、既存standalone archiveを暗黙上書きしない。
- path configuration rejectionはactual E2 process開始前の入力拒否として扱う。
- actual `deployment-provider-plan`を実行する。
- Bのactual binary / Provider Plan SHA-256を記録する。
- job割当や取得failureをCLI互換性failureと区別する。
- source identity / fixed input identity / platform / Go toolchain / build / Provider Plan process / output validation / Evidence packagingのどの外部stageまで成立したかを区別できる。
- `deployment-provider-plan` process内部のworkspace load / validation / durable run / plugin lock等は、machine-readable Evidenceが得られた場合だけ追加で細分化する。

### E3 — current SOZA Adapter compatibility

- revision B actual binaryをcurrent `runtime/go/teiintegration`から別OS processとして起動する。
- Provider Planをcurrent Adapter-local DTOでstrictにdecodeする。
- current Capability Observation validatorを通る。
- `availability = true`と`provider_plan_resolved = true`を観測できる。
- TEI固有fieldをUniversal Capability Observationへ漏らさない。
- B source、A fixed reference input、bundle identityをMapping Provenanceから追跡できる。
- どのSOZA source / local Go toolchainでlive検査したかを記録する。
- SOZA source identity / bundle verification / staging / fixed input identity / Go toolchain / existing `teiintegration` live-test processのどの外部stageまで成立したかを区別できる。
- live-test内部のstrict decode / mapping / validator等は、machine-readable Evidenceが得られた場合だけ追加で細分化する。

### E4 — A/B historical separation

- revision B追加後もrevision Aのsource / binary / output Evidenceを変更しない。
- A/Bの取得経路、source identity、binary identity、Provider Plan identityを別々に追跡できる。
- Provider Planの差がある場合、その差をbyte drift、Adapter compatibility、semantic changeへ分けて評価できる。
- build sourceとfixed reference inputのProvenanceを別々に追跡できる。

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

2026-09-05時点では次まで確認済みである。

```text
revision A fixed-artifact actual TEI execution
  = Scoped Executable Evidence available from ISSUE-000065

revision A artifact re-acquisition
  = observed

revision A bundle identity re-verification
  = verified

acquisition-independent bundle verifier
  = implemented

bundle verifier synthetic tests
  = 7 passed

revision B source identity
  = fixed to 1a7028d444fcae60a1c4f2f2d247456f4c7c35be

revision B execution-source Git identity
  = fixed; repository-local verifier implemented

source / fixed-input working-tree purity
  = tracked changes / untracked / ignored entries rejected; PR #226 synthetic Git cases 5 passed

revision A fixed reference input identity
  = workspace tree / durable run blob / plugin-lock blob fixed

Provider Plan output surface A/B
  = strong static continuity observed

deployment / environment / releaseplan / plugin-runtime / core
  = exact source-tree continuity observed

workspace / validation / IR input interpretation
  = changed; actual fixed-input execution required

version-exchange comparison axis
  = exact-B build source + exact-A fixed reference input

prepositioned B Evidence runner baseline
  = implemented; earlier synthetic / fixed-input isolation checks passed

E2 stage-aware diagnostics
  = implemented; focused stage-model checks 4 passed; expanded branch tests added but full suite not re-run in current container

bundle → current Adapter live runner baseline
  = implemented; 8 synthetic tests passed before stage instrumentation

E3 stage-aware diagnostics
  = implemented; focused stage-model checks 4 passed; expanded branch tests added but full suite not re-run in current container

E2/E3 separate Go toolchains
  = identified and explicit in combined runner

toolchain-split combined runner baseline
  = implemented; 7 synthetic tests passed before stage-instrumentation additions

combined E2/E3 substage propagation
  = implemented; branch negative controls added; full suite not re-run in current container

Evidence output / checkout separation guard
  = implemented; PR #223 path-safety negative controls committed; full suite not re-run in current container

specific execution host
  = not selected; any suitable Linux / amd64 environment may be used

revision B workflow attempt 1
  = failure before any job step

revision B workflow attempt 2
  = failure before any job step

revision B actual CLI build / execution
  = Not Yet Verified

revision B Provider Plan
  = Not Yet Observed

revision B current SOZA Adapter live compatibility
  = Not Yet Verified
```

現在の主な実装・観測記録は次へ置く。

- `runtime/integration/verify_tei_evidence_bundle.py`
- `runtime/integration/test_verify_tei_evidence_bundle.py`
- `runtime/integration/verify_tei_execution_source_identity.py`
- `runtime/integration/run_tei_revision_b_prepositioned.py`
- `runtime/integration/run_tei_bundle_adapter_compatibility.py`
- `runtime/integration/run_tei_version_exchange_evidence.py`
- `runtime/TEI_VERSION_EXCHANGE_EVIDENCE_2026-09-05.md`
- `runtime/TEI_PROVIDER_SURFACE_STATIC_COMPATIBILITY_2026-09-05.md`
- `runtime/TEI_VERSION_EXCHANGE_EXECUTION_READINESS_2026-09-05.md`
- `runtime/TEI_VERSION_EXCHANGE_TOOLCHAIN_READINESS_2026-09-05.md`
- `runtime/TEI_VERSION_EXCHANGE_FAILURE_STAGES_2026-09-05.md`

## Deliverables

- TEI Evidence bundle verifier
- bundle verifierのnegative control
- revision B / revision A fixed inputのGit identity verifier
- source / fixed input working-tree purity guard
- revision A / B identityと取得経路を分けたEvidence report
- Provider Plan source surface / input interpretation差分のStatic Evidence
- exact-B build source + exact-A fixed inputのprepositioned Evidence runner
- verified bundleからcurrent SOZA Adapter live testへ接続するrunner
- E2 / E3を別toolchainで連続実行し段階別reportを残すcombined runner
- Evidence output / input checkout separation guard
- E2 / E3 failure stage taxonomyとnegative control
- revision B actual artifactを取得できた場合のB verification report
- A/B Adapter compatibility Evidence
- Requirement / Contract再照合結果
- 必要な場合のみ、後続ADR / Profile / distribution policy proposal

## Resolution

次をすべて満たした時点でResolvedにできる。

1. revision A historical artifactを現在のverifierで再検証できる。
2. revision Bのactual executableまたは固定Evidence bundleを取得し、そのsource / binary / Provider Plan identityを記録できる。
3. revision B actual `deployment-provider-plan`がexact-A fixed reference inputで成立するか、不成立ならrepository-local E2 stageのどこで停止したかを判別できる。TEI内部substageはmachine-readable Evidenceがある場合だけ追加で特定する。
4. current SOZA Adapterでrevision Bを実行し、Capability Observationへのmapping成立可否を確認する。不成立ならrepository-local E3 stageのどこで停止したかを判別し、live-test内部原因はmachine-readable Evidenceがある場合だけ追加で特定する。
5. revision B追加後もrevision A Evidenceを不変に保持する。
6. acquisition / credential / artifact identity / fixed input identity / Provider compatibilityの境界をEvidenceで確認する。
7. REQ-0001、REQ-0007、REQ-0021、SCN-0014、SCN-0018へ再照合し、新しいStable Requirementが必要かを監査する。
8. 自然な日本語を最重要視した最終意味監査を行う。

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
- distribution / credential方式をsemantic identityへ取り込まないと履歴再構成できないことが判明する。
- Product Value / Requirementが変更される。

## CI / verification

GitHub ActionsはこのIssueの意味上の成立条件にしない。

TEI側Evidence workflowを利用できる場合はactual artifact生成の一経路として使うが、jobが開始されなかったrunをTEI compatibility failureへ数えない。取得済みartifactはrepository-local `verify_tei_evidence_bundle.py`へ戻して再検証する。

actual Bのrepository-local経路では、exact revision B checkoutをbuild source、exact revision A checkoutをfixed reference inputとして`run_tei_revision_b_prepositioned.py`へ渡す。両checkoutはGit object identityだけでなく、対象境界のtracked / untracked / ignored entryがないことを確認する。

Evidence archive / directoryはrevision B、revision A、SOZA checkoutから分離したnon-symlink pathへ置く。path configurationが不正な場合はactual processを開始せず、E2 / E3 failure stageへ読み替えない。standalone E2は既存archiveを暗黙上書きしない。

B Evidence bundleを得た後は、cleanなSOZA checkoutで`run_tei_bundle_adapter_compatibility.py`を実行し、既存`runtime/go/teiintegration.TestLiveTEIProviderPlan`へ接続する。runnerのsynthetic testやStatic Evidenceはactual TEI process executionの代替ではない。

E2からE3までを一度に実行する場合は`run_tei_version_exchange_evidence.py`を使い、TEI historical build用Go 1.23.2とcurrent SOZA live-test用Goを別々のexecutableとして明示する。failure reportは上位`E2` / `E3`とstage-aware `substage`を分離し、通常の例外文言からsubstageを捏造しない。

特定hostやRemote Desktop接続の復帰を待つことは完了条件にしない。上記identity / purity / toolchain / path条件を満たせる適切なLinux / amd64実行環境を用意できた時点でactual E2 → E3へ進む。

## Natural Japanese review

PMS-06、ISSUE-000061 / 000065、ADR-0013 / 0019 / 0021 / 0024、Actual TEI CLI Evidence、current `teiintegration`、revision A Evidence artifact、revision B Evidence workflow attempt 1 / 2、revision B Git object identity、A / B Provider Plan static compatibility、exact-A fixed reference input、E2 prepositioned runner、E3 Adapter live runner、toolchain-split combined runner、E2 / E3 failure-stage instrumentation、Evidence output path safety、source / fixed-input working-tree purityを照合した。

取得方法、artifact identity、build source、fixed reference input、Provider固有surface、SOZAのCapability Observationを一つにまとめず、今回すでに観測できたことと、revision B actual executionが未検証であることを分離している。

特に、A / Bでworkspace treeが異なることから「B checkout内のsame pathを使えば同じinput」という早合点を修正し、version交換ではB executableへhistorical A inputを与える比較軸へ固定した。また、Static EvidenceでProvider Plan出力surfaceに連続性がある一方、workspace / validation / IRが変化しているためactual検証が必要であることも明記した。

さらに、Git object identityが一致していてもworking treeのignored entryがactual build / fixed inputへ混入し得るため、tracked / untracked / ignoredをすべてexecution boundaryのpurity対象へ含めた。Evidence出力についても、入力checkoutとのoverlap、symlink、暗黙上書きをactual process前に拒否し、そのconfiguration failureをProvider compatibilityの失敗へ昇格させない。

actual failureの切り分けでは、stderr / stdoutの自然言語からTEI内部stageやSOZA live-test内部stageを推定せず、repository-local runnerが直接観測できる外部境界だけをEvidence stageとして扱う。これにより、診断情報を保持しつつ、原因の高さをEvidence以上に引き上げない。

また、特定host / CI provider / Remote DesktopをProduct semanticsへ持ち込まず、必要な固定identityとtoolchainを配置できる実行環境をexecution mechanismとして分離した。

意味、要求強度、留保、Evidenceの高さを固定したうえで、自然な日本語となることを最重要視して全文を再監査した。