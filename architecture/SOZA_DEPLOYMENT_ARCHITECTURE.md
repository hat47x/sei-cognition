# SOZA Deployment Architecture

更新日: 2026-09-01  
状態: **Current Local Single-Node Deployment Baseline**

## 1. この文書の役割

この文書は、Product Packaging baselineとADR-0029で採用したLocal Single-Node Packageを、current Reference Architectureのsemantic concernを壊さずに配置するためのDeployment Architectureです。

ここでいうcomponentはdeployment上の実現単位であり、Universal semantic entityではありません。

```text
deployment component
  != semantic concern
  != Universal Contract
```

## 2. 最小構成

最初のdeployment profileは、単一host・単一processを基本とします。

```text
Human / Machine Surface
          │
          ▼
┌──────────────────────────────────────┐
│           SOZA Go process            │
│                                      │
│ Interaction Adapter                  │
│ Canonical Semantic Runtime           │
│ Persistence Port                     │
│ Provider / Integration Adapters      │
└──────────────────┬───────────────────┘
                   │
                   ▼
           Persistence Adapter
                   │
                   ▼
             durable data root
```

一つのprocessへ同居させるのは初期配布を単純にするためであり、Interaction、Semantic Runtime、Persistence、Provider Integrationを同じ意味へ統合するためではありません。

## 3. Component責務

### 3.1 Interaction Adapter

人間向け・機械向けSurfaceからの操作をcanonical semantic operationへ接続します。UI state、chat transcript、cursor、tab等をcanonical persistenceの必須要素にしません。

### 3.2 Canonical Semantic Runtime

current Semantic Contractを読み、既知recordを検証し、unknown recordをEvidence強度を上げずに保持します。deployment固有のfile path、process ID、port番号等をLogical Referenceへ持ち込みません。

### 3.3 Persistence Port

保存・再読のruntime境界です。probeでは小さな`Save` / `Load`相当interfaceを使いますが、このGo interface自体はUniversal Contractではありません。

### 3.4 Persistence Adapter

最初のRealizationはfilesystemです。directory、file name、temporary file、rename、permission等のphysical mechanicsを所有し、それらをSemantic Contractへ漏らしません。

後続のRDB / object store Adapterも、同じsemantic boundaryを満たせる限り交換可能です。

### 3.5 Provider / Integration Adapter

TEI、SaaS、AI、外部System等との接続を担います。Packagingのためにworkflow / agent runtimeを内蔵必須にはしません。

## 4. durable data root

durable data rootは、process終了後にも残るphysical storage locationです。

最初のfilesystem profileでは、canonical semantic bundleを次のような明示的fileとして保持します。

```text
data root/
  semantic.bundle.json
  [optional runtime-local / payload area]
```

このlayoutはfilesystem Realizationのprofileであり、SOZA Universal ontologyではありません。

## 5. 保存境界

正常なsaveは、成功を返す前に完全なportable semantic bytesをPersistence Adapterへ渡し切る必要があります。

filesystem probeでは次を用います。

```text
complete bytes
  -> temporary file
  -> file sync / close
  -> rename to canonical file
```

重要なのは、不完全なwriteを正常なcanonical packageとして公開しないことです。この具体mechanicsをDB等へ一般化しません。

reference probeではinvalid canonical fileやtemporary fileだけの状態を正常packageとして扱わないことを確認しています。一方、この結果をpower loss時のcrash durabilityや全platformでのatomicity保証へは広げません。

## 6. 再開境界

resumeはprocess heapの復元ではありません。

```text
resume
  = load durable portable semantic data
    + reconstruct supported semantic records
  != restore previous process heap
  != restore UI session state
```

ISSUE-000054では、二段階でこの境界を検査しました。

1. 元の`Bundle` objectを破棄し、新しいruntime objectからdurable bytesを再構成する。
2. `go build`で生成したGo executableを独立したprocess Aとして起動して保存し、process A終了後に別process Bを起動して同じdata rootから再読する。

process Bはprocess Aのin-memory stateを共有しません。これにより、same-versionのbuild済みexecutableによるliteral process restartにはscoped Executable Evidenceがあります。

```text
same-version process restart: verified in scoped probe
version-upgrade resume: not yet verified
```

未知Contract / versionはprocessを跨いでもopaque `not_verified`のまま保持します。

## 7. package lifecycle controlとProduct Interaction

process probe executableには`save` / `inspect`だけを置いています。これはDeployment / Packaging acceptanceを検査するための管理入口です。

```text
package lifecycle control
  != Product Interaction Surface
```

このcommandを正式なSOZA CLI、human-facing UI、AI-facing protocolへ昇格させません。supported artifactの管理入口はISSUE-000055で検討します。

## 8. export / import

Persistence内部形式が変わっても、portable Semantic InterchangeをStorage交換境界として利用します。

```text
filesystem adapter
      │ export
      ▼
Semantic Interchange bytes
      │ import
      ▼
other Persistence adapter
```

reference probeではfilesystemからmemory Persistenceへoriginal bytesを移し、同じbundleを再読できることを確認しました。これはPersistence交換境界の補助的Evidenceであり、production DB / object store migrationではありません。

## 9. backup / restore

最初のfilesystem profileでは、整合したcanonical bundleを別locationへ複製し、そこから新しいruntimeが同じsemantic dataを再読できることを最小restore条件とします。

reference probeではcanonical bundle fileのcopy / restoreを確認しています。running processのheap、Surface-local state、temporary fileは最小backupのcanonical対象ではありません。

external payload等を含む完全なproduction backup、online snapshot、incremental backup、PITRは未検証です。

## 10. failure boundary

次を正常なpackage stateとして扱いません。

- canonical fileが存在しない。
- canonical fileがinvalid JSONである。
- Semantic Interchangeとして検証できない。
- save途中のtemporary fileしか存在しない。

一方、runtime未知のnested Contractが含まれることだけでpackage全体を破損扱いにはしません。unknown recordは`not_verified`として保持します。

## 11. 将来のservice分割

将来、Interaction、Persistence、Provider Adapter等を別process / serviceへ分割できます。その際も次を守ります。

- Logical Referenceをservice-local IDへ置換しない。
- service境界をsemantic authority境界と同一視しない。
- transport retryやqueue stateをDecision stateへ昇格させない。
- Persistence内部transactionをSemantic Revisionへ昇格させない。

Local Single-Node Profileは将来の分割を禁止するものではありません。

## 12. Security / Identityとの境界

filesystem permission、process user、credential等は重要ですが、本baselineではProduct Identity / Authorizationを確定しません。

```text
OS file permission
  != semantic Authority
  != contextual Responsibility
```

PMS-05 / ISSUE-000047で、product access permissionとsemantic Authority / Responsibilityを分離して扱います。

## 13. Evidence状態

```text
Deployment Architecture Design: established
filesystem persistence: scoped Executable Evidence available
runtime-state-independent reconstruction: scoped Executable Evidence available
same-version literal process restart: scoped Executable Evidence available
canonical bundle copy / restore: scoped Executable Evidence available
filesystem -> memory Persistence exchange: scoped Executable Evidence available
supported distributable artifact: not yet verified
version upgrade resume: not yet verified
crash durability / cross-platform guarantee: not yet verified
actual production Storage migration: not yet verified
Release / Operational: not yet verified
```

literal process probeを含むSemantic Runtime Conformance Run `33508376230`、Plan integrity Run `33508376256`はsuccessしています。

```text
process probe PASS
  != supported distribution artifact proven
  != version upgrade proven
  != crash durability proven
  != Release / Operational Evidence
```

詳細は`../runtime/PACKAGING_PROBE_EVIDENCE_2026-09-01.md`を参照します。

## 14. 関連文書

- `SOZA_REFERENCE_ARCHITECTURE.md`
- `IMPLEMENTATION_LANGUAGE_POLICY.md`
- `../product/packaging/SOZA_PRODUCT_PACKAGING.md`
- `../plan/adr/ADR-0007-canonical-persistence-boundary.md`
- `../plan/adr/ADR-0029-local-single-node-packaging-profile.md`
- `../plan/issue/ISSUE-000054-materialize-packaged-resume-and-storage-migration-probe.md`
- `../plan/issue/ISSUE-000055-materialize-first-supported-local-package-artifact.md`
- `../runtime/PACKAGING_PROBE_EVIDENCE_2026-09-01.md`

## 15. Natural Japanese review

Reference Architecture、Product Packaging baseline、ADR-0007 / 0029、Semantic Interchange runtime、Product Interaction boundary、`runtime/go/packagingprobe`、build済みGo executableによるliteral process restart、Semantic Runtime Conformance Run `33508376230`、Plan integrity Run `33508376256`を照合しました。Local Single-Node Packageをdeployment componentの配置として整理し、単一process、filesystem layout、probe commandをsemantic concernや正式Product Interactionへ昇格させていません。runtime object再生成とliteral process restart、same-version restartとversion upgrade、Persistence交換probeとactual production Storage migration、file sync / renameとcrash durability guaranteeを分けたうえで、意味、Architecture上の責務、未検証範囲、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。