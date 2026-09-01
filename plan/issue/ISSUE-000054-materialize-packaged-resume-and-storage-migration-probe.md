# ISSUE-000054: packaged resume / Storage migration reference probeを実体化する

Status: **Resolved**  
Priority: **1**  
Related ADRs: **ADR-0007, ADR-0021, ADR-0022, ADR-0029**  
Updated: 2026-09-01

## Goal

PMS-04と`product/packaging/SOZA_PRODUCT_PACKAGING.md`で定めたLocal Single-Node Packageについて、**portable semantic dataを保存し、元のin-memory runtime stateを破棄した後に別runtime objectで再構成できること**をreference probeで検証する。

あわせて、filesystem Persistenceと別Persistence Realization相当のmemory storeの間でportable Semantic Interchangeを移し、Storage implementationがsemantic identityになっていないことを限定的に確認する。

このIssueでいう「再開」はliteralなOS process再起動を実証した意味ではない。actual testでは同一test process内で元のBundle objectを破棄し、新しいPersistence / runtime objectからdurable bytesを再読する。

## Resolution

`runtime/go/packagingprobe`に、runtime-levelのPersistence境界とfilesystem / memoryの二つのprobe Realizationを実装した。

```text
runtime object A
  -> filesystem persistence
  -> original in-memory state discarded
  -> runtime object B
  -> reload

filesystem persistence
  -> portable export
  -> memory persistence
  -> reload
```

Semantic Interchangeのparse / validationを別実装せず、既存`semanticruntime.LoadInterchange`と`Bundle.ExportOriginal`を再利用している。

probe-local `Persistence` interfaceはUniversal Contractではない。

## filesystem Persistence

最初のfilesystem Realizationでは、data root配下の`semantic.bundle.json`をcanonical bundle fileとして扱う。

保存では、temporary fileへcomplete bytesを書き、file sync、closeの後にcanonical fileへrenameする。

この方式はfirst filesystem probeの実装であり、UniversalなPersistence要件ではない。また、directory fsyncやOS / filesystem固有のcrash guaranteeまでは検証していない。

## memory Persistence

Storage交換probeの第二Realizationとしてmemory Persistenceを実装した。

これはproduction in-memory StorageをsupportedとするDecisionではない。filesystem固有mechanicsを外してもportable Semantic Interchangeから同じsemantic bundleを再読できることを検査するためのRealizationである。

## 必須検査の結果

### 1. valid Semantic Interchange bytesをfilesystemへ保存できる

**Satisfied in scoped Executable Evidence.**

`partial-knowledge-interchange.json`をcurrent semantic runtimeで読み、original bytesをfilesystem Persistenceへ保存した。

### 2. 元のruntime stateを破棄した後、新しいruntime objectから再読できる

**Satisfied in scoped Executable Evidence.**

元の`Bundle` objectを破棄し、新しい`FilePersistence`と`LoadBundle`呼び出しから再構成できることを確認した。

ただし、OS processの終了・再起動そのものは行っていない。

### 3. reload後もoriginal Semantic Interchange bytesを保持する

**Satisfied in scoped Executable Evidence.**

保存・再読前後で`Bundle.ExportOriginal()`のbytesがfixture原文と一致することを確認した。

### 4. typed semantic recordを再構成する

**Satisfied in scoped Executable Evidence.**

保存前に存在したCapability ObservationとDecisionが、reload後にもcurrent runtimeのtyped recordとして再構成されることを確認した。

### 5. unknown Contract recordをopaque `not_verified`のまま保持する

**Satisfied in scoped Executable Evidence.**

`unknown-contract-version.json`を保存・再読し、unknown nested Contractが`RecordNotVerified`のままであることと、original bytesが変化しないことを確認した。

### 6. filesystem pathをLogical Referenceへ混入させない

**Satisfied in scoped Executable Evidence.**

異なる二つのdata root間でportable bytesを移し、physical pathが変わってもSemantic Interchange bytesが変化しないことを確認した。probeはfile pathをLogical Referenceへ変換しない。

### 7. Surface-local stateを保存しなくてもcanonical bundleを再読できる

**Satisfied structurally and in scoped Executable Evidence.**

Persistence境界が保存するのはportable Semantic Interchange bytesであり、PMS-03 probeのSurface-local state等を入力として要求しない。保存済みbytesだけからbundleを再構成するtestが通っている。

### 8. data rootを別directoryへcopyしてrestoreできる

**Satisfied in scoped Executable Evidence for canonical bundle file.**

保存済みcanonical fileを別directoryへ複製し、そのdirectoryを新しいdata rootとして同じbytesを再読できることを確認した。

将来のexternal payload等を含む完全なproduction backupではない。

### 9. incomplete / invalid canonical stateを正常packageとして受理しない

**Satisfied in scoped Executable Evidence.**

- invalid canonical fileを`LoadInterchange`で拒否する。
- temporary fileだけが存在しcanonical fileがない状態は`ErrPackageNotFound`とする。
- invalid importが失敗しても、直前のvalid memory stateを置き換えない。

### 10. filesystemからexportしたportable bytesをmemory Persistenceへimportできる

**Satisfied in scoped Executable Evidence.**

filesystemからexportしたbytesをmemory Persistenceへimportし、再読後もoriginal bytesと`bundle_id`が保持されることを確認した。

### 11. Persistence交換前後でsemantic identity / referencesを保持する

**Satisfied in scoped Executable Evidence within tested fixture.**

byte preservationとcurrent runtimeによるtyped再構成によって、tested bundleのsemantic recordをPersistence交換後も保持できることを確認した。

production規模のlong-running migrationや別DB schemaでは未検証である。

### 12. Storage migrationをSemantic Revisionとして自動生成しない

**Satisfied in scoped Executable Evidence.**

filesystemからmemory Persistenceへの移行経路はoriginal Semantic Interchange bytesをそのまま扱い、新しいSemantic Lineage / Revision recordを生成しない。

## Negative cases

actual testで次を確認した。

- invalid JSON / invalid Semantic Interchangeを正常packageとして受理しない。
- unknown Contractをvalidatedへ昇格させない。
- physical data-root変更によってsemantic bytesを書き換えない。
- temporary fileだけの状態をcompleted saveと扱わない。
- invalid importで最後のvalid stateを壊さない。
- Persistence交換時にportable bytesを不要に正規化しない。

## 既存runtimeとの重複監査

Packaging probeは第二のsemantic runtimeを作っていない。

- interchange parse / validation — `semanticruntime.LoadInterchange`を再利用。
- portable byte export — `Bundle.ExportOriginal`を再利用。
- unknown nested Contract — existing `RecordNotVerified`方針を再利用。
- semantic identity / exact binding — current Semantic Interchange / nested Contractに委ねる。

新たに実体化したのは、これらのportable bytesを保存・再読するruntime-level Persistence boundaryのみである。

## Requirement / Scenario再監査

probe結果から、新しいstable Product RequirementやAcceptance Scenarioを追加する独立した必要性は確認されなかった。

引き続き次を検査軸とする。

- REQ-0001 — 技術やStorageが変わっても意味を引き継ぐ。
- REQ-0005 — Decisionを歴史的に再構成する。
- REQ-0009 — physical migrationとSemantic Revisionを混同しない。
- REQ-0011 — Surfaceを意味上の正本にしない。
- REQ-0018 — Storage実装から意味を独立させる。
- REQ-0020 — Evidenceを超える達成主張をしない。
- REQ-0021 — Persistence等のRealizationを交換可能にする。
- SCN-0008 — Storageを交換する。
- SCN-0010 — 可変Artifact更新後に過去Decisionを再構成する。

SCN-0008にはfilesystem / memory間の限定Executable Evidenceが加わるが、production Storage migrationを全面的にSatisfiedとはしない。

literal OS-process restartや配布binary起動で、既存Scenarioでは表現できない独立したProduct failureが確認された場合に限り、Candidate Scenarioを再検討する。

## Non-goals / 未検証範囲

- actual Go binary build / distribution
- production CLI / Web / desktop Surface
- literal OS-process restart
- executable version upgrade後のresume
- process crash / power loss durability
- directory fsyncを含むfilesystem crash guarantee
- cross-platform filesystem behavior
- concurrent writer / locking / transaction isolation
- production RDB / object store
- online migration
- external payloadを含む完全backup / restore
- encryption at rest / credential storage
- login / authorization / collaboration
- HA / replication
- production security
- Release / Operational / Adoption / Outcome Evidence

## 完了条件

- [x] filesystem Persistence probeを実体化する。
- [x] memory Persistence probeを実体化する。
- [x] save → original runtime state破棄 → reloadをactual testへ落とす。
- [x] canonical bundle fileのbackup / restore相当のdirectory copy testを行う。
- [x] filesystem → portable export → memory importをtestする。
- [x] incomplete / invalid stateのnegative testを行う。
- [x] existing semanticruntimeとの重複監査を行う。
- [x] CIで再現可能なExecutable Evidenceを得る。
- [x] PMS-04 / Product Packaging / Evidence文書へ結果を同期する。
- [x] Requirement / SCN追加の要否を再監査する。今回は追加しない。
- [x] 自然な日本語全文再ドラフトと最終意味監査を行う。
- [ ] 最終headの対象CIをsuccessさせる。

初回実装head `5097636cdca40c4ec8cd8ab68bbb7066fb291db2`では、Semantic Runtime Conformance Run `33506712038`のruntime-conformance jobとPlan integrity Run `33506712033`がともに**success**した。

Evidence同期後の最終headでも対象CIを再確認し、そのRunを本IssueとEvidence文書へ同期する。

## Evidence state

- Design Evidence: **Satisfied**
- Executable Evidence: **Scoped Evidence available** — `runtime/go/packagingprobe`とSemantic Runtime Conformance Run `33506712038`。
- Release Evidence: **Not Yet Verified**
- Operational Evidence: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

詳細は`runtime/PACKAGING_PROBE_EVIDENCE_2026-09-01.md`を正とする。

## Reopen / escalation条件

- literal process restartでdurable bytesから再構成できない。
- executable version upgradeでsupported Contractの意味を保持できない。
- filesystemからproduction Storageへの移行でportable Semantic Interchangeでは意味を保持できない独立した失敗が確認された。
- Local Single-Node Profileがactual usabilityやsecurity requirementと両立しない。
- Persistence boundaryへphysical locatorやtransaction mechanicsをsemantic identityとして持ち込まないと成立しないことが確認された。

## Natural Japanese review

PMS-04、Product Packaging baseline、Deployment Architecture、ADR-0029、REQ-0018 / 0021、SCN-0008 / 0010、current Semantic Interchange runtime、`runtime/go/packagingprobe`のactual test、Semantic Runtime Conformance Run `33506712038`、Plan integrity Run `33506712033`を照合した。in-memory runtime stateを捨てた後の再構成とliteral OS-process restartを分離し、filesystem probeの成功をcrash durability、production DB migration、Release / Operational Evidenceへ広げていない。また、probe-local Persistence interfaceやfilesystem mechanicsをUniversal Contractへ昇格させず、既存Requirement / Scenarioを先に再利用する境界を維持した。そのうえで、意味、要求強度、留保、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。