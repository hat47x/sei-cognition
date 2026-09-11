# ISSUE-000054: packaged resume / Persistence交換reference probeを実体化する

Status: **Resolved**  
Priority: **1**  
Related ADRs: **ADR-0007, ADR-0021, ADR-0022, ADR-0029**  
Updated: 2026-09-01

## Goal

PMS-04と`product/packaging/SEI_PRODUCT_PACKAGING.md`で定めたLocal Single-Node Packageについて、**portable semantic dataを保存し、実行中の状態を失った後でもdurable dataだけから再開できること**をreference probeで検証する。

あわせて、filesystem Persistenceと別Realizationであるmemory Persistenceの間でportable Semantic Interchangeを移し、physical Storage implementationがsemantic identityになっていないことを限定的に確認する。

## Resolution

`runtime/go/packagingprobe`にruntime-levelのPersistence境界とfilesystem / memoryの二つのprobe Realizationを実装し、さらに`runtime/go/cmd/soza-package-probe`に検証専用のbuild可能なGo executableを追加した。

```text
process A
  -> portable Semantic Interchange
  -> filesystem Persistence
  -> process A exits

process B
  -> same durable data root
  -> load / validate / reconstruct
```

Persistence交換については次を検査する。

```text
filesystem Persistence
  -> portable export
  -> memory Persistence
  -> reload
```

Semantic Interchangeのparse / validationは新しく実装せず、既存の`semanticruntime.LoadInterchange`と`Bundle.ExportOriginal`を再利用する。

probe-local `Persistence` interfaceと検証用commandは、Universal Contractでもproduction Product Interaction Surfaceでもない。

## 実装した境界

### filesystem Persistence

最初のfilesystem Realizationでは、data root配下の`semantic.bundle.json`をcanonical bundle fileとして扱う。

保存は、complete bytesをtemporary fileへ書き、file sync、closeの後にcanonical fileへrenameする。

このmechanicsはfirst filesystem probeの実装であり、すべてのPersistence Providerへ要求するUniversal仕様ではない。また、directory fsync、power loss、OS / filesystem固有のrename保証までは今回のEvidenceに含めない。

### memory Persistence

Persistence交換境界を検査する第二Realizationとしてmemory Persistenceを実装した。

これはproduction in-memory StorageをsupportedとするDecisionではない。filesystem固有のphysical mechanicsを外しても、portable Semantic Interchangeから同じsemantic bundleを再読できることを確認するためのprobeである。

### process probe executable

`soza-package-probe`は、`save`と`inspect`の二つの検証用subcommandだけを持つ。

- `save` — Semantic Interchange fileを読み、current semantic runtimeで検証したうえでfilesystem Persistenceへ保存する。
- `inspect` — durable data rootからbundleを読み直し、bundle ID、record数、`validated` / `not_verified`数をJSONで出力する。

このcommandはProduct Interaction用の正式CLIではなく、Local Single-Node Packageのprocess境界を再現可能に検査するためのtest fixtureである。

## Executable Evidence

### 1. filesystemへの保存

`partial-knowledge-interchange.json`をcurrent semantic runtimeで検証し、original Semantic Interchange bytesをfilesystem Persistenceへ保存できることを確認した。

### 2. in-memory stateに依存しない再構成

元の`Bundle` objectを破棄し、新しい`FilePersistence` / `LoadBundle`から同じbytesとtyped recordを再構成できることを確認した。

### 3. literalな別OS processからの再開

process probe testでは、まず`go build`で`soza-package-probe` executableを実際に生成する。

その後、独立したprocess Aで`save`を実行して終了させ、process Bとして同じbinaryの`inspect`を新たに起動する。process Bはprocess Aのheapやin-memory objectへアクセスできず、durable data rootだけからbundleを再構成する。

`partial-knowledge-interchange.json`について、次を確認した。

- process Aが終了した後でもprocess Bがbundleを再読できる。
- `bundle_id`が`partial-knowledge-interchange`のままである。
- 2 recordを再構成し、双方を`validated`として扱う。
- 保存されたSemantic Interchange bytesが入力fixtureと一致する。

これにより、**同一versionのbuild済みGo executableを用いたliteral process boundaryでのsave → exit → reload**について、scoped Executable Evidenceが得られた。

ただし、version upgrade後のresumeやrelease artifactとしての配布は未検証である。

### 4. unknown Contractのprocess越し保持

`unknown-contract-version.json`についても、独立したsave processとinspect processを実行した。

再開後も1 recordは`not_verified`のままであり、理解していないContractを`validated`へ昇格させないことを確認した。

```text
persisted and reopened
  != semantics understood
  != validated
```

### 5. original bytesの保持

保存・再読前後でoriginal Semantic Interchange bytesがfixture原文と一致することを確認した。current runtimeが理解できるからという理由で、bundleを不要に正規化・再生成しない。

### 6. physical locatorとsemantic identityの分離

異なるdata root間で同じportable bytesを扱っても、physical pathをSemantic InterchangeやLogical Referenceへ取り込まないことを確認した。

### 7. canonical bundleのcopy / restore

保存済みcanonical fileを別directoryへ複製し、そのrestore先から同じportable bytesを再読できることを確認した。

これはcanonical semantic bundle fileに限ったrestore probeであり、将来追加されるexternal payload、index、credential等を含むproduction backup全体を証明するものではない。

### 8. Persistence Realizationの交換

filesystem Persistenceからportable bytesをexportし、memory Persistenceへimportした後、同じbundleを再読できることを確認した。

この交換でSemantic Revisionは生成しない。

これはPersistence境界の交換可能性に関する補助的なExecutable Evidenceであり、SCN-0008が想定するfilesystemからproduction RDB / object store等へのactual Storage migrationではない。

### 9. invalid / incomplete stateの拒否

次をactual negative testで確認した。

- invalid JSON / invalid Semantic Interchangeを正常packageとして受理しない。
- temporary fileだけが存在しcanonical fileがない状態をcompleted saveと扱わない。
- invalid importで直前のvalid memory stateを壊さない。
- unknown Contractをvalidatedへ昇格させない。
- physical data-root変更でportable semantic bytesを書き換えない。

## Requirement / Scenario再監査

今回のprobeから、新しいstable Product RequirementやAcceptance Scenarioを追加する独立した必要性は確認されなかった。

引き続き主な検査軸は次とする。

- REQ-0001 — 技術やStorageが変わっても意味を引き継ぐ。
- REQ-0005 — Decisionを歴史的に再構成する。
- REQ-0009 — physical migrationとSemantic Revisionを混同しない。
- REQ-0011 — Surfaceを意味上の正本にしない。
- REQ-0018 — Storage実装から意味を独立させる。
- REQ-0020 — Evidenceを超える達成主張をしない。
- REQ-0021 — Persistence等のRealizationを交換可能にする。
- SCN-0008 — Storageを交換する。
- SCN-0010 — 可変Artifact更新後に過去Decisionを再構成する。

literal process restart自体は、現時点ではREQ-0001 / REQ-0018とPMS-04のProduct outcomeを実行可能に確認する方法として扱う。別processでの再開によって既存Requirement / Scenarioでは表現できない独立した失敗は確認されなかったため、新しいSCNは追加しない。

SCN-0008については、filesystem / memory間のprobeだけをactual production Storage migrationのEvidenceへ昇格させない。

## 完了条件

- [x] filesystem Persistence probeを実体化する。
- [x] memory Persistence probeを実体化する。
- [x] save → original runtime state破棄 → reloadをactual testへ落とす。
- [x] build済みGo executableによるsave process → exit → independent reload processをactual testへ落とす。
- [x] unknown Contractを別processでも`not_verified`のまま保持する。
- [x] canonical bundle fileのcopy / restore testを行う。
- [x] filesystem → portable export → memory importをtestする。
- [x] incomplete / invalid stateのnegative testを行う。
- [x] existing semanticruntimeとの重複監査を行う。
- [x] Requirement / SCN追加の要否を再監査する。今回は追加しない。
- [x] PMS-04 / Product Packaging / Deployment Architecture / Evidenceへ結果を同期する。
- [x] 自然な日本語全文再ドラフトと最終意味監査を行う。
- [x] 最終headの対象CIをsuccessさせる。

## CI Evidence

literal process probeを含むhead `9d28d2f04d5e31a7ca766a1a6d05eedc6c00d4d8`で、次が**success**した。

- Semantic Runtime Conformance Run `33508376230`
  - current Contract fixture再検査
  - `runtime/go`全体の`go test ./...`
  - `soza-package-probe` executable build
  - independent save / inspect process test
- Plan integrity Run `33508376256`

これらは記載したscopeに限ったExecutable / plan integrity Evidenceである。

## Evidence state

- Design Evidence: **Satisfied**
- Executable Evidence: **Scoped Evidence available**
  - filesystem persistence
  - runtime-state-independent reconstruction
  - same-version built executableによるliteral process restart
  - canonical bundle copy / restore
  - filesystem → memory Persistence exchange
- Release Evidence: **Not Yet Verified**
- Operational Evidence: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

## 未検証範囲

- supported distribution artifactとしてのpackage
- executable version upgrade後のresume
- production CLI / Web / desktop Product Interaction Surface
- process crash / power loss durability
- directory fsyncを含むfilesystem crash guarantee
- Windows / macOSを含むcross-platform filesystem semantics
- concurrent writer / locking / transaction isolation
- production RDB / object storeへのactual Storage migration
- online migration
- external payloadを含む完全backup / restore
- encryption at rest / credential storage
- login / authorization / collaboration
- HA / replication
- production security
- Release / Operational / Adoption / Outcome Evidence

## Follow-up

次の残差は、**buildできること**と**supported distributable artifactとして提供できること**の差である。

この差はISSUE-000055で扱う。そこではProduct Interactionの正式CLI選定と混同せず、package lifecycle用の最小管理入口、reproducible build、artifact identity、version表示、配布物からの起動・再開を検査する。

## Reopen条件

- same-versionのindependent processでは再開できるが、supported distribution artifactではportable dataを再読できない。
- executable version upgradeでsupported Contractの意味を保持できない。
- production Storageへの移行でportable Semantic Interchangeでは意味を保持できない独立した失敗が確認された。
- Local Single-Node Profileがactual usabilityやsecurity requirementと両立しない。
- Persistence boundaryへphysical locatorやtransaction mechanicsをsemantic identityとして持ち込まなければ成立しないことが確認された。

## Natural Japanese review

PMS-04、Product Packaging baseline、Deployment Architecture、ADR-0029、REQ-0001 / 0005 / 0009 / 0011 / 0018 / 0020 / 0021、SCN-0008 / 0010、current Semantic Interchange runtime、`runtime/go/packagingprobe`、build可能な`soza-package-probe`、Semantic Runtime Conformance Run `33508376230`、Plan integrity Run `33508376256`を照合した。runtime object破棄後の再構成とliteralな別OS processからの再開を分けたうえで、今回新たに確認できたsame-version process restartだけをExecutable Evidenceへ加えている。process restartの成功をversion upgrade、release artifact、crash durability、production Storage migration、Release / Operational Evidenceへ広げず、probe commandやPersistence interfaceもProduct InteractionやUniversal Contractへ昇格させていない。そのうえで、意味、要求強度、留保、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。