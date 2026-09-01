# SOZA Product Packaging / Deployment

更新日: 2026-09-01  
状態: **Current Product Packaging / Deployment Baseline**

## 1. この文書の役割

この文書は、SOZAを実際に起動し、保存し、終了後に再開できる最小製品単位を、Product Valueと既存のsemantic boundaryから定めます。

ここで決めるのは、特定cloud、Kubernetes、特定DB、Web framework等ではありません。最初に成立させるdeployment profileと、そこから将来別のStorageやSurfaceへ移行しても失ってはならない境界を定めます。

```text
Product Packaging
  = executable runtime + replaceable persistence + portable semantic data
  != semantic ontology
  != one mandatory deployment topology
```

## 2. 中心原則

### 2.1 実行物と耐久データを分ける

SOZAの実行物を削除・更新・再配布しても、判断記憶や来歴が失われない構成を基本とします。

```text
runtime executable
  != canonical semantic data
```

Goの単一バイナリ化は配布上の利点として利用できますが、バイナリ自体を意味上の正本にはしません。

### 2.2 deployment unitとsemantic boundaryを分ける

最初は一つのprocessへ複数の論理Surfaceを同居させても構いません。

```text
one process
  may contain
    Interaction Surface
    Canonical Semantic Access
    Persistence Adapter
    Integration Adapter
```

ただし、一つのprocessへ同居していることから、それらを一つのsemantic concernへ統合しません。将来service分割しても、canonical meaningを変えない構造を維持します。

### 2.3 Storageは交換可能なRealizationとする

filesystem、RDB、object store、event store等はPersistence Realizationです。

Logical Reference、Semantic Lineage、Exact Binding、Provenance等の意味を、file path、row ID、object key、event sequenceへ依存させません。

### 2.4 保存できたことと意味を理解できたことを分ける

未知versionや未知Contractを含むportable dataを保持できても、その意味を検証済みとは主張しません。

```text
bytes retained
  != semantics understood
  != validation succeeded
```

## 3. 最初のsupported Packaging Profile

最初に成立させる最小profileを、**Local Single-Node Package**とします。

構成は次です。

```text
┌─────────────────────────────────────┐
│ SOZA local runtime                  │
│                                     │
│  Interaction / machine surfaces    │
│  Canonical semantic runtime        │
│  Persistence boundary              │
│  Provider / Adapter boundary       │
└─────────────────┬───────────────────┘
                  │
                  ▼
        local durable data root
                  │
          portable semantic data
```

### 3.1 runtime

first-party runtimeはADR-0027に従いGoを標準とします。

最小profileでは、単一process・単一hostで起動できることを優先します。最初からservice meshや複数daemonを要求しません。

### 3.2 durable data root

runtime外に、耐久データを置く明示的なdata rootを持ちます。

最初のfilesystem Realizationでは、少なくとも次を分離します。

- portable semantic bundle
- 必要に応じてlocal payload bytes
- runtime-local metadataが必要な場合は、それがsemantic authorityではないことを明示した領域

正確なdirectory名やfile名は実装profileで定めます。file pathそのものをLogical Referenceにはしません。

### 3.3 Surface

PMS-04ではproduction Web / desktop / CLIの最終選定を要求しません。

最初のpackageは、Interaction Surfaceを同一processへ接続できる構造を持てばよく、PMS-03のreference probeや後続のsupported UIを交換可能に載せられることを優先します。

## 4. portable semantic data

### 4.1 Semantic Interchangeを移行境界として再利用する

current baselineでは、新しいpackage専用Universal Contractを追加せず、`soza.semantic-interchange/v1alpha1`をportable semantic export / importの中心として再利用します。

```text
Persistence internal form
  -> portable Semantic Interchange
  -> another Persistence Realization
```

Persistence Provider内部のindex、transaction log、DB schema等をexport formatへ漏らしません。

### 4.2 byte preservationとsemantic migrationを分ける

import / exportで未知recordを保持する場合、runtimeが意味を理解していないrecordを黙って再構成・正規化しません。

Contract versionを上げる必要がある場合も、Storage migrationをsemantic revisionへ自動変換しません。

### 4.3 external payload

large binaryや外部Sourceをすべてinline化することは要求しません。

Exact Bindingが参照するpayloadをlocal package内に保持する場合でも、payload locatorはruntime / Persistence Providerの実装詳細です。Logical ReferenceやExact Bindingへfilesystem pathを埋め込むことは要求しません。

payloadを移行できなかった場合は、「存在しなかった」やdigest mismatchへ変換せず、取得不能・`not_verified`等の適切な状態を保ちます。

## 5. 保存と再開

Local Single-Node Packageは、少なくとも次を満たす必要があります。

1. portable semantic dataをdurable data rootへ保存できる。
2. processを終了した後、同じdata rootから別processを起動して再読できる。
3. 再読後もlogical identity、Decision basis、Unknown / Conflict、Responsibility、Provenance等の意味差が保たれる。
4. 保存途中の不完全な状態を、正常に確定したpackageとして見せない。
5. runtime executableを入れ替えても、supported Contract範囲では同じsemantic dataを読める。
6. Surface-local stateが失われてもcanonical semantic dataは失われない。

保存のatomicityを実現する具体手段はPersistence Realizationへ委ねます。最初のfilesystem probeではtemporary fileへの完全書き込み、file sync、close、renameを用いましたが、これをUniversal要件にはしません。

現時点のExecutable Evidenceは、同一test process内で元のin-memory runtime stateを破棄し、新しいruntime objectからdurable bytesを再構成できる範囲です。literalなOS process終了・再起動と、executable version交換後のresumeはまだ検証していません。

## 6. backup / restore

最小profileでは、backupを「running processの内部状態を複製すること」と定義しません。

backup対象は、別processで意味を再構成するために必要なdurable dataです。

filesystem Realizationでは、停止中または整合したsnapshotとしてdata rootを複製し、別の場所へrestoreした後に同じsemantic dataを再読できることを最小条件とします。

reference probeではcanonical semantic bundle fileを別directoryへ複製し、restore先から同じportable bytesを再読できることを確認しました。外部payload等を含む将来のdata root全体を対象とするproduction backupは未検証です。

online backup、incremental backup、point-in-time recovery等は現時点では必須にしません。

## 7. import / export / migration

### 7.1 export

Persistence内部形式からportable Semantic Interchangeを作成できることを求めます。

### 7.2 import

portable Semantic Interchangeを、新しいPersistence Realizationへ取り込める境界を持ちます。

### 7.3 migration

最小のStorage migrationは、次の形で検査します。

```text
Persistence A
  -> portable export
  -> Persistence B
  -> reload
  -> semantic comparison
```

比較ではphysical locatorや内部indexの一致ではなく、logical identity、record kind、meaningful references、historical binding等の保持を確認します。

reference probeではfilesystemからmemory Persistenceへoriginal Semantic Interchange bytesを移し、同じbundleを再読できることを確認しました。これはStorage交換境界の限定Executable Evidenceであり、production RDB / object store migrationを証明するものではありません。

## 8. 最初に固定しないこと

次はOpen Questionのまま残します。

- productionで最初に採用する主要human-facing UI
- HTTP API / MCP / SDKの正式なsupported combination
- RDBを最初のserver-side Storageとするか
- team / multi-user deployment topology
- online migration
- HA / replication
- container imageを正式配布単位とするか
- cloud-managed deployment
- background daemonを必須にするか

これらはPackaging Designやreference probeのPASSだけを理由にRequirementへ昇格させません。

## 9. Requirement / Acceptance監査

current Packaging境界とprobe結果は、主に既存Requirementで表現できます。

- REQ-0001 — 実装やStorageが変わっても意味を引き継ぐ。
- REQ-0005 — 保存後もDecisionを歴史的に再構成できる。
- REQ-0009 — physical versionとsemantic revisionを混同しない。
- REQ-0011 — Surfaceを意味上の正本にしない。
- REQ-0018 — Storage実装から意味を独立させる。
- REQ-0020 — package testをRelease / Operational Evidenceへ昇格させない。
- REQ-0021 — StorageやProjection等のRealizationを交換可能にする。

AcceptanceではSCN-0008「Storageを交換する」とSCN-0010「可変Artifact更新後に過去Decisionを再構成する」を中心に再利用します。

reference probeから、新しいstable Requirement / Scenarioを追加する独立した必要性は確認されませんでした。literal OS-process restartや配布binary起動で、既存Scenarioでは表現できない独立した失敗が確認された場合だけCandidate Scenarioを検討します。

## 10. Packaging reference probeの結果

ISSUE-000054で、`runtime/go/packagingprobe`を実体化しました。

確認できた範囲は次です。

1. Semantic Interchange bundleをfilesystemへ保存できる。
2. 元のin-memory Bundleを破棄し、新しいruntime objectからfilesystemのbundleを再読できる。
3. original Semantic Interchange bytesを保持できる。
4. current runtimeが理解するtyped recordを再構成できる。
5. unknown Contract recordを`not_verified`のまま保持できる。
6. Surface-local stateなしにcanonical bundleを再構成できる。
7. canonical bundle fileを別directoryへcopyし、restore先から同じbytesを再読できる。
8. filesystem locatorをsemantic bytesやLogical Referenceへ混入させない。
9. invalid canonical fileやtemporary fileだけの状態を正常packageとして受理しない。
10. filesystemからmemory Persistenceへportable bytesをimportし、同じbundleを再読できる。
11. failed importで直前のvalid stateを壊さない。
12. Storage交換をSemantic Revisionへ自動変換しない。

このprobeはproduction filesystem durability、literal OS process restart、DB migration、concurrent transaction、配布物起動を証明するものではありません。

詳細は`../../runtime/PACKAGING_PROBE_EVIDENCE_2026-09-01.md`を正とします。

## 11. Evidence状態

- Packaging / Deployment Design Evidence: **Established**
- Persistence / runtime-state-independent reconstruction Executable Evidence: **Scoped Evidence available**
- filesystem → memory Storage migration Executable Evidence: **Scoped Evidence available**
- literal OS-process restart: **Not Yet Verified**
- distributable product package: **Not Yet Verified**
- production Storage migration: **Not Yet Verified**
- Release Evidence: **Not Yet Verified**
- Operational Evidence: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

```text
packaging probe PASS
  != distributable package proven
  != literal process restart proven
  != crash durability proven
  != production Storage migration proven
  != Release / Operational / Adoption Evidence
```

## 12. 関連文書

- `../definition/SOZA_PRODUCT_SHAPE.md`
- `../roadmap/SOZA_PRODUCT_MILESTONES.md`
- `../interaction/SOZA_PRODUCT_INTERACTION.md`
- `../../architecture/SOZA_DEPLOYMENT_ARCHITECTURE.md`
- `../../requirements/PRODUCT_REQUIREMENTS.md`
- `../../requirements/ACCEPTANCE_SCENARIOS.md`
- `../../plan/adr/ADR-0007-canonical-persistence-boundary.md`
- `../../plan/adr/ADR-0027-go-as-standard-production-runtime-language.md`
- `../../plan/adr/ADR-0029-local-single-node-packaging-profile.md`
- `../../plan/issue/ISSUE-000046-define-v0-2-0-product-packaging-and-deployment-boundary.md`
- `../../plan/issue/ISSUE-000054-materialize-packaged-resume-and-storage-migration-probe.md`
- `../../runtime/PACKAGING_PROBE_EVIDENCE_2026-09-01.md`

## 13. Natural Japanese review

Product Value、Product Shape、PMS-04、Product Interaction、REQ-0001 / 0005 / 0009 / 0011 / 0018 / 0020 / 0021、SCN-0008 / 0010、ADR-0007 / 0014 / 0021 / 0022 / 0027 / 0029、current Semantic Interchange runtime、`runtime/go/packagingprobe`とcurrent CI Evidenceへ戻り、Packagingをsemantic ontologyではなく実行物・永続化・portable dataの組み合わせとして再監査しました。Goの単一バイナリやfilesystemの利点は利用しつつ、それらを意味上の正本や唯一のdeployment topologyへ昇格させていません。また、runtime object破棄後の再構成とliteral OS-process restart、filesystem→memory probeとproduction Storage migrationを明確に分けています。意味、要求強度、留保、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。