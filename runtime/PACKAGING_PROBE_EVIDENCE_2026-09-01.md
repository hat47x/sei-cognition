# Packaging / Persistence Reference Probe Evidence

更新日: 2026-09-01  
状態: **Scoped Executable Evidence**

## 1. この文書の役割

この文書は、PMS-04、Product Packaging baseline、ADR-0029に対して、current Packaging / Persistence probeで実際に確認できた範囲を記録します。

今回、新たに**build済みGo executableを別々のOS processとして起動し、保存processの終了後にdurable dataだけから再開できること**まで確認しました。

```text
probe PASS
  != supported distributable artifact proven
  != executable version upgrade proven
  != crash durability proven
  != actual production Storage migration proven
  != Release / Operational / Adoption Evidence
```

## 2. 実装した境界

`runtime/go/packagingprobe`には、probe-localな`Persistence`境界とfilesystem / memoryの二つのRealizationがあります。Semantic Interchangeの意味解釈は新しく実装せず、既存の`semanticruntime.LoadInterchange`と`Bundle.ExportOriginal`を再利用します。

`runtime/go/cmd/soza-package-probe`には、process境界を検査するための`save` / `inspect`だけを持つGo executableを追加しました。このcommandは正式なProduct Interaction CLIではありません。

filesystem Realizationでは`semantic.bundle.json`をcanonical bundle fileとして扱い、temporary fileへの書き込み、file sync、close、renameを使います。このmechanics自体はUniversal仕様ではなく、power lossや全OS / filesystemでのcrash durabilityも今回のEvidenceには含めません。

## 3. literal process restart

`process_test.go`では、まず`go build`でprobe executableを実際に生成し、その後に独立したprocessを順に起動します。

```text
process A: save
  -> durable data root
  -> exit

process B: inspect
  -> durable data root only
  -> semantic reconstruction
```

`partial-knowledge-interchange.json`について、次を確認しました。

- process A終了後、process Bが同じdata rootから再読できる。
- 保存されたSemantic Interchange bytesが入力fixtureと一致する。
- `bundle_id`が保持される。
- 2件のknown recordを`validated`として再構成できる。

process Bはprocess AのheapやGo objectを共有しません。このため、**same-versionのbuild済みGo executableによるsave → exit → independent reload**にはscoped Executable Evidenceがあります。

## 4. unknown Contractの保持

`unknown-contract-version.json`でもsave processとinspect processを分けています。再開後もunknown recordは`not_verified`のままであり、保存・再開できたことを「意味を理解しvalidatedした」と読み替えません。

```text
retained across process boundary
  != semantics understood
  != validated
```

## 5. その他のPersistence Evidence

unit-level probeでは、元の`Bundle` objectを破棄し、新しい`FilePersistence` / `LoadBundle`から同じbytesとtyped recordを再構成できます。

filesystemからportable bytesをexportし、memory Persistenceへimportした後にも同じbundleを再読できます。この交換でSemantic Revisionは生成しません。ただしmemory Persistenceは評価用Realizationであり、このPASSをfilesystemからproduction RDB / object storeへのactual Storage migrationと同一視しません。

canonical bundle fileを別directoryへcopyし、restore先から同じportable bytesを再読できることも確認しています。これはcanonical semantic bundle fileに限ったrestore probeであり、external payloadやcredential等を含むproduction backup全体のEvidenceではありません。

## 6. negative case

次をactual testで確認しています。

- invalid JSON / invalid Semantic Interchangeを正常packageとして受理しない。
- temporary fileだけが存在しcanonical fileがない状態をcompleted saveと扱わない。
- invalid importで直前のvalid memory stateを壊さない。
- physical data-root変更でsemantic bytesを書き換えない。
- unknown Contractをvalidatedへ昇格させない。

## 7. SCN-0008との関係

filesystem / memory probeは、Storage-neutralなPersistence境界が実装可能であることを補助的に示します。

```text
Persistence exchange probe PASS
  supports SCN-0008 design
  != SCN-0008 actual Storage migration verified
```

production classのRDB / object store migrationを行っていないため、SCN-0008自体のExecutable Evidenceは引き続き**Not Yet Verified**です。

## 8. Requirement / Acceptance再監査

literal process restartまで実施した結果、新しいstable Product RequirementやAcceptance Scenarioを追加する独立した必要性は確認されませんでした。

引き続きREQ-0001 / 0005 / 0009 / 0011 / 0018 / 0020 / 0021、SCN-0008 / 0010を主な検査軸とします。literal process restartは、PMS-04と既存Requirementを検査する実証手段として扱います。

## 9. PMS-04への反映

現在のEvidenceは次の高さです。

```text
Packaging / Deployment Design: established
filesystem persistence: scoped Executable Evidence available
runtime-state-independent reconstruction: scoped Executable Evidence available
same-version literal process restart: scoped Executable Evidence available
filesystem -> memory Persistence exchange: scoped Executable Evidence available
canonical bundle copy / restore: scoped Executable Evidence available
supported distributable artifact: not yet verified
version upgrade resume: not yet verified
actual production Storage migration: not yet verified
Release / Operational / Adoption: not yet verified
```

PMS-04のOutcome全体に含まれる「利用者へ渡せる最小package」はまだ成立扱いにしません。残差はISSUE-000055で扱います。

## 10. CI Evidence

literal process probeを含むhead `9d28d2f04d5e31a7ca766a1a6d05eedc6c00d4d8`で、次が**success**しました。

- Semantic Runtime Conformance Run `33508376230`
  - current Contract fixture再検査
  - `runtime/go`全体の`go test ./...`
  - probe executableの`go build`
  - independent save / inspect process test
- Plan integrity Run `33508376256`

このCI successは記載したscopeに限ったEvidenceです。

## 11. 未検証範囲

- supported distribution artifact
- executable version upgrade後のresume
- production Product Interaction CLI / Web / desktop Surface
- process crash / power loss durability
- cross-platform filesystem guarantee
- concurrent writer / locking / transaction isolation
- production RDB / object storeとactual SCN-0008 migration
- external payloadを含む完全backup / restore
- encryption / credential storage / login / authorization / collaboration
- HA / replication / production security
- Release / Operational / Adoption / Outcome Evidence

## 12. Natural Japanese review

Product Packaging baseline、Deployment Architecture、ADR-0029、ISSUE-000046 / 000054 / 000055、REQ-0018 / 0021、SCN-0008 / 0010、current Semantic Interchange runtime、`runtime/go/packagingprobe`、build可能なprocess probe executable、Semantic Runtime Conformance Run `33508376230`、Plan integrity Run `33508376256`を照合しました。runtime object再生成とliteralな別OS processからの再開、Persistence交換probeとactual production Storage migration、build可能なtest executableとsupported distribution artifactを明確に分けています。process restartの成功をversion upgrade、crash durability、Release / Operational Evidenceへ広げず、probe commandやPersistence interfaceもUniversal semantic modelや正式Product Interactionへ昇格させていません。そのうえで、意味、Evidence強度、未検証範囲を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。