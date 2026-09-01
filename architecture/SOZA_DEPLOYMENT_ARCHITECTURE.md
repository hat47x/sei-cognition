# SOZA Deployment Architecture

更新日: 2026-09-01  
状態: **Current Local Single-Node Deployment Baseline**

## 1. この文書の役割

この文書は、`product/packaging/SOZA_PRODUCT_PACKAGING.md`とADR-0029で採用したLocal Single-Node Packageを、current Reference Architectureのsemantic concernを壊さずに配置するためのDeployment Architectureです。

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

人間向け・機械向けSurfaceからの操作を、canonical semantic operationへ接続します。

UI state、chat transcript、cursor、tab等をcanonical persistenceの必須要素にしません。

### 3.2 Canonical Semantic Runtime

current Semantic Contractを読み、既知recordを検証し、unknown recordをEvidence強度を上げずに保持します。

Deployment固有のfile path、process ID、port番号等をLogical Referenceへ持ち込みません。

### 3.3 Persistence Port

保存・再読のruntime境界です。

最初のprobeでは`Save` / `Load`相当の小さなinterfaceを使いますが、このGo interface自体はUniversal Contractではありません。

Persistence Portの責務は、portable semantic bytesをStorage Realizationへ渡し、後から同じportable representationとして取り出せることです。

### 3.4 Persistence Adapter

最初のRealizationはfilesystemです。

filesystem Adapterは、directory、file name、temporary file、rename、permission等の物理mechanicsを所有します。これらをSemantic Contractへ漏らしません。

後続のRDB / object store Adapterも、同じsemantic boundaryを満たせる限り交換可能です。

### 3.5 Provider / Integration Adapter

TEI、SaaS、AI、外部System等との接続を担います。

Packagingのためにworkflow / agent runtimeを内蔵必須にはしません。

## 4. durable data root

durable data rootは、process終了後にも残るphysical storage locationです。

最初のfilesystem profileでは、canonical semantic bundleを明示的なfileとして保持します。

```text
data root/
  semantic.bundle.json
  [optional runtime-local / payload area]
```

このlayoutはfilesystem Realizationのprofileであり、SOZA Universal ontologyではありません。

`semantic.bundle.json`の内容にはcurrent Semantic Interchangeを利用します。

## 5. 保存境界

正常なsaveは、呼び出し元へ成功を返す前に、少なくとも完全なportable semantic bytesをPersistence Adapterへ渡し切る必要があります。

filesystem probeでは、次の手順を使います。

```text
complete bytes
  -> temporary file
  -> flush / close
  -> rename to canonical file
```

この手順はfirst filesystem Realizationの実装です。将来のDB transaction等を同じ方法へ揃えることは要求しません。

重要なのは、不完全なwriteを正常なcanonical packageとして公開しないことです。

## 6. 再開境界

resumeはprocess memoryの復元ではありません。

```text
resume
  = load durable portable semantic data
    + reconstruct supported semantic records
  != restore previous process heap
  != restore UI session state
```

新しいruntime instanceがdata rootからbundleを読み、既知Contractをcurrent validatorで再構成します。

未知Contract / versionはopaque `not_verified`のまま保持でき、runtimeが理解できないことを理由に削除しません。

## 7. export / import

Persistence Adapterの内部形式が将来変わっても、portable Semantic InterchangeをStorage交換境界として利用します。

```text
filesystem adapter
      │ export
      ▼
Semantic Interchange bytes
      │ import
      ▼
RDB / object-store / other adapter
```

export / importでphysical locatorをsemantic identityへ変換しません。

## 8. backup / restore

最初のfilesystem profileでは、整合したcanonical fileを含むdata rootを別locationへ複製し、そこから新しいruntime instanceが同じbundleを再読できることを最小restore条件とします。

running processのheap、Surface-local state、temporary fileは最小backupのcanonical対象ではありません。

online snapshot、incremental backup、PITRは後続Profileで扱います。

## 9. failure boundary

次を正常なpackage stateとして扱いません。

- canonical fileが存在しない。
- canonical fileがinvalid JSONである。
- Semantic Interchangeとして検証できない。
- save途中のtemporary fileしか存在しない。

一方、Semantic Interchange内にruntime未知のnested Contractが含まれることは、それだけでpackage全体の破損とはみなしません。unknown recordは`not_verified`として保持します。

## 10. 将来のservice分割

将来、Interaction、Persistence、Provider Adapter等を別process / serviceへ分割できます。

その際も次を守ります。

- Logical Referenceをservice-local IDへ置換しない。
- service境界をsemantic authority境界と同一視しない。
- transport retryやqueue stateをDecision stateへ昇格させない。
- Persistence内部transactionをSemantic Revisionへ昇格させない。

Local Single-Node Profileは、将来の分割を禁止するものではありません。

## 11. Security / Identityとの境界

filesystem permission、process user、credential等は重要ですが、本baselineではProduct Identity / Authorizationの意味境界を確定しません。

```text
OS file permission
  != semantic Authority
  != contextual Responsibility
```

PMS-05 / ISSUE-000047で、product access permissionとsemantic Authority / Responsibilityを分離して扱います。

## 12. Evidence状態

- Deployment Architecture Design Evidence: **Established**
- filesystem packaged resume Executable Evidence: **Not Yet Verified at document creation time**
- Storage migration Executable Evidence: **Not Yet Verified at document creation time**
- Release Evidence: **Not Yet Verified**
- Operational Evidence: **Not Yet Verified**

Executable EvidenceはISSUE-000054のreference probeで取得します。

## 13. 関連文書

- `SOZA_REFERENCE_ARCHITECTURE.md`
- `IMPLEMENTATION_LANGUAGE_POLICY.md`
- `../product/packaging/SOZA_PRODUCT_PACKAGING.md`
- `../plan/adr/ADR-0007-canonical-persistence-boundary.md`
- `../plan/adr/ADR-0029-local-single-node-packaging-profile.md`
- `../plan/issue/ISSUE-000054-materialize-packaged-resume-and-storage-migration-probe.md`

## 14. Natural Japanese review

Reference Architecture、Product Packaging baseline、ADR-0007 / 0029、Semantic Interchange runtime、Payload Source、Product Interaction boundaryを照合し、Local Single-Node Packageをdeployment componentの配置として整理しました。単一processやfilesystem layoutをsemantic concernへ昇格させず、保存、再開、export / import、backup / restore、failureの境界を分けています。そのうえで、意味、Architecture上の責務、未検証範囲、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。