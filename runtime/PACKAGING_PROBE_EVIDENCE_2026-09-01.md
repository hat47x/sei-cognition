# Packaging / Persistence Reference Probe Evidence

更新日: 2026-09-01  
状態: **Scoped Executable Evidence**

## 1. この文書の役割

この文書は、PMS-04、`product/packaging/SOZA_PRODUCT_PACKAGING.md`、ADR-0029で定めたLocal Single-Node Packageについて、`runtime/go/packagingprobe`で確認できた範囲を記録します。

今回のprobeで確認したのは、**portable Semantic Interchangeをfilesystemへ保存し、元のin-memory runtime stateを破棄した後に別のruntime objectから再構成できること、およびPersistence Realizationを変更してもportable semantic bytesを保持できること**です。

実際のOS process再起動、配布バイナリ、production database、crash durability、同時書き込み、production backup運用を実証するものではありません。

```text
packaging probe PASS
  != distributable package proven
  != literal OS-process restart proven
  != crash durability proven
  != production Storage migration proven
  != Release Evidence
  != Operational / Adoption Evidence
```

## 2. 実装したprobe

`runtime/go/packagingprobe`に、runtime-levelの小さなPersistence境界を実装しました。

```text
Semantic Interchange bytes
          │
          ▼
      Persistence
       /        \
filesystem     memory
```

このPersistence interfaceはprobe / runtimeの実装境界であり、Universal Semantic Contractではありません。

semantic parse / validationは別実装せず、既存の次を再利用します。

- `semanticruntime.LoadInterchange`
- `semanticruntime.Bundle.ExportOriginal`

したがって、Packaging probeがSemantic Interchangeの第二の意味解釈系になることを避けています。

## 3. filesystem Persistence

最初のfilesystem Realizationでは、data root配下の`semantic.bundle.json`をcanonical bundle fileとして扱います。

file pathはphysical locatorであり、Logical Referenceではありません。

保存では、probeの範囲で次の手順を用います。

```text
complete bytes
  -> temporary file
  -> file sync
  -> close
  -> rename to canonical file
```

これはfirst filesystem Realizationの実装であり、すべてのPersistence Providerへ同じmechanicsを要求するものではありません。

また、この手順だけでOS crash時のdurabilityを保証したとは主張しません。directory fsync、filesystem固有のrename保証、Windows等の異なるplatform behaviorは今回の検証範囲外です。

## 4. memory Persistence

Storage交換の境界を確認するため、第二Realizationとしてmemory Persistenceを実装しました。

これはproduction in-memory StorageをsupportするDecisionではありません。filesystemからexportしたportable bytesを別のPersistence Realizationへimportできることを小さく確認するためのprobeです。

## 5. 確認したExecutable Evidence

Semantic Runtime Conformance Run `33506712038`のruntime-conformance jobで、current Contract fixtureの再検査と`runtime/go`全体の`go test ./...`がsuccessしました。

### 5.1 保存後の再構成

`partial-knowledge-interchange.json`を既存`semanticruntime.LoadInterchange`で読み、filesystem Persistenceへ`Bundle.ExportOriginal()`のbytesを保存しました。

その後、元の`Bundle` objectを破棄し、新しい`FilePersistence`と`LoadBundle`呼び出しから再読しています。

確認した内容は次です。

- `bundle_id`が保持される。
- original Semantic Interchange bytesが変化しない。
- Capability ObservationとDecisionのtyped recordが再構成される。

これは同一test process内でruntime objectを作り直したEvidenceです。OS processを実際に終了・再起動したEvidenceではありません。

### 5.2 unknown Contractの保持

`unknown-contract-version.json`を保存・再読し、未知のnested Contractが`RecordNotVerified`のまま保持されることを確認しました。

original bytesも変化しません。

```text
retained across persistence
  != semantics understood
  != validated
```

### 5.3 filesystemからmemory Persistenceへの移行

filesystem Persistenceからportable bytesをexportし、memory Persistenceへimportした後、再び`LoadInterchange`経由で読み直せることを確認しました。

移行前後で次を保持しています。

- original Semantic Interchange bytes
- `bundle_id`
- current runtimeが再構成できるtyped semantic record

Storage migrationに伴うSemantic Revisionは生成していません。

### 5.4 data rootのcopy / restore

保存済みcanonical bundle fileを別directoryへ複製し、そのrestore先を新しいdata rootとして読み直せることを確認しました。

restore先のphysical pathが変わってもportable semantic bytesは変化しません。

このtestが確認するのはcanonical semantic bundleのcopy / restoreです。将来data rootへ追加される外部payload、index、credential等を含む完全なproduction backupを証明するものではありません。

### 5.5 invalid / incomplete stateの拒否

次をnegative caseとして確認しました。

- invalid JSONまたはSemantic Interchangeとして不正なcanonical fileを正常packageとして受理しない。
- temporary fileだけが存在し、canonical bundle fileがない場合は保存済みpackageとして扱わない。
- memory Persistenceへinvalid bytesをimportしようとして失敗しても、直前のvalid stateを置き換えない。

### 5.6 physical locatorとsemantic identityの分離

異なる二つのfilesystem data root間でportable bytesを移動し、physical locatorの変更がSemantic Interchange bytesへ影響しないことを確認しました。

このprobeはfile pathやdirectory名をLogical Referenceへ変換しません。

## 6. SCN-0008への反映

SCN-0008「Storageを交換する」に対して、filesystem Persistenceとmemory Persistenceの二Realization間でportable Semantic Interchange bytesを移し、Storage-specific locatorに依存せず再読できる**限定されたExecutable Evidence**が得られました。

ただし、RDB、object store、schema migration、long-running production data等のactual migrationは未検証です。

そのためSCN-0008を全面的にSatisfiedとはしません。

## 7. process restart後のresumeの扱い

今回のtestでは、元のBundle objectを明示的に捨て、新しいruntime objectからdurable bytesを再読しています。

これは「前のin-memory stateに依存せず再構成できる」ことのEvidenceです。一方、次はまだ確認していません。

- 別OS processをspawnしてsaveする。
- processを終了する。
- 新しいprocessを起動してloadする。
- executable versionを交換して再開する。

したがって、literalなprocess restart acceptanceを新しいStable Scenarioとして追加する根拠にはまだしません。

## 8. Requirement / Acceptance再監査

probe結果から、新しいstable Product RequirementまたはAcceptance Scenarioを追加する独立した必要性は確認されませんでした。

今回の意味は、引き続き主に次で表現できます。

- REQ-0001 — 技術やStorageが変わっても意味を引き継ぐ。
- REQ-0005 — Decisionを歴史的に再構成する。
- REQ-0009 — physical migrationとSemantic Revisionを混同しない。
- REQ-0011 — Surfaceを意味上の正本にしない。
- REQ-0018 — Storage実装から意味を独立させる。
- REQ-0020 — Evidenceを超える達成主張をしない。
- REQ-0021 — Persistence等のRealizationを交換可能にする。
- SCN-0008 — Storageを交換する。
- SCN-0010 — 可変Artifact更新後に過去Decisionを再構成する。

literal OS-process restartや配布物起動で、これらでは表現できない独立したProduct failureが見つかった場合にのみ、Candidate Scenarioを再検討します。

## 9. 今回確認していないこと

- 実際のGo binary build / distribution
- CLI / Web / desktop Surfaceを含むend-user package
- literal OS-process restart
- executable version upgrade後のresume
- process crash / power loss durability
- directory fsyncを含むfilesystem crash guarantee
- Windows / macOSを含むcross-platform filesystem semantics
- concurrent writer
- transaction isolation
- locking
- production RDB / object store
- online migration
- payload areaを含む完全backup / restore
- encryption at rest
- credential storage
- login / authorization / collaboration
- HA / replication
- production security
- latency / throughput / resource usage
- Release / Operational / Adoption / Outcome Evidence

## 10. PMS-04への反映

PMS-04について、Packaging / Deployment Design Evidenceに加えて、**scoped persistence / resume / Storage migration Executable Evidence available**と判断できます。

ただし、PMS-04のOutcomeに含まれる「実際に起動・配布できる最小package」全体を満たしたとはまだ主張しません。

```text
Packaging Design: established
filesystem persistence probe: executable evidence available
runtime-state-independent reconstruction: executable evidence available
filesystem -> memory migration: executable evidence available
distributable product package: not yet verified
literal process restart: not yet verified
Release / Operational / Adoption: not yet verified
```

## 11. CI Evidence

- Workflow: `Semantic Runtime Conformance`
- Run: `33506712038`
- Job: `runtime-conformance`
- Result: **success**
- Scope:
  - current Contract fixture再検査
  - `runtime/go`で`go test ./...`
  - `runtime/go/packagingprobe`のcurrent test

同じheadではPlan integrity Run `33506712033`も**success**し、Packaging Design、ADR / Issue registry、Document Review Registryの整合を確認しています。

これらのCI successは、記載したscopeに限ったEvidenceとして扱います。

## 12. Natural Japanese review

Product Packaging baseline、Deployment Architecture、ADR-0029、ISSUE-000046 / 000054、REQ-0018 / 0021、SCN-0008 / 0010、current Semantic Interchange runtime、`runtime/go/packagingprobe`のactual test、Semantic Runtime Conformance Run `33506712038`、Plan integrity Run `33506712033`を照合しました。runtime object破棄後の再構成とliteral OS-process restartを区別し、filesystem probeの成功をcrash durability、production Storage migration、Release / Operational Evidenceへ広げていません。また、Persistence interface、file layout、temporary-file mechanicsをUniversal semantic modelへ昇格させていません。そのうえで、意味、Evidence強度、未検証範囲を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。