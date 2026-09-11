# SEI Product Packaging / Deployment

更新日: 2026-09-01  
状態: **Current Product Packaging / Deployment Baseline**

## 1. この文書の役割

この文書は、SEIを実際に起動し、保存し、終了後に再開できる最小製品単位を、Product Valueと既存のsemantic boundaryから定めます。

ここで定めるのは、最初に成立させるdeployment profileと、将来StorageやSurfaceが変わっても失ってはならない境界です。特定cloud、Kubernetes、特定DB、Web framework等をProduct ontologyへ固定しません。

```text
Product Packaging
  = executable runtime
  + replaceable persistence
  + explicit durable data root
  + portable semantic data
  != semantic ontology
  != one mandatory deployment topology
```

## 2. 中心原則

### 2.1 実行物と耐久データを分ける

SEIの実行物を削除・更新・再配布しても、判断記憶や来歴が失われない構成を基本とします。

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
    Interaction Adapter
    Canonical Semantic Runtime
    Persistence Adapter
    Integration Adapter
```

一つのprocessにあることから、それらを一つのsemantic concernへ統合しません。将来service分割してもcanonical meaningを変えない構造を維持します。

### 2.3 Storageは交換可能なRealizationとする

filesystem、RDB、object store、event store等はPersistence Realizationです。

Logical Reference、Semantic Lineage、Exact Binding、Provenance等の意味を、file path、row ID、object key、event sequenceへ依存させません。

```text
filesystem locator != Logical Reference
Storage migration != Semantic Revision
```

### 2.4 保存できたことと意味を理解できたことを分ける

未知versionや未知Contractを含むportable dataを保持できても、その意味を検証済みとは主張しません。

```text
bytes retained
  != semantics understood
  != validation succeeded
```

### 2.5 artifact identityとsemantic identityを分ける

配布archiveにはbuild version、source commit、target等のidentityを持たせられますが、それらはArtifactの追跡情報です。

```text
artifact identity
  != semantic identity
  != Semantic Contract version
```

archive名やbinary versionをLogical Reference、Decision identity、Semantic Contract identityへ流用しません。

## 3. 最初のPackaging Profile

最初に成立させる最小profileを、**Local Single-Node Package**とします。

```text
┌─────────────────────────────────────┐
│ SEI local runtime                  │
│                                     │
│ Interaction / machine adapters      │
│ Canonical semantic runtime          │
│ Persistence boundary                │
│ Provider / Integration boundary     │
└─────────────────┬───────────────────┘
                  │
                  ▼
        local durable data root
                  │
          portable semantic data
```

first-party runtimeはADR-0027に従いGoを標準とします。最小profileでは、単一host・単一processで始められることを優先し、最初から複数daemon、service mesh、Kubernetes等を要求しません。

runtime外には明示的なdurable data rootを置きます。最初のfilesystem Realizationでは、portable semantic bundleを中心に保持します。必要なlocal payloadやruntime-local metadataを追加する場合も、それらがsemantic authorityかどうかを明示的に分けます。

## 4. portable semantic data

current baselineでは、新しいpackage専用Universal Contractを追加せず、`sei.semantic-interchange/v1alpha1`をportable semantic export / importの中心として再利用します。

```text
Persistence internal form
  -> portable Semantic Interchange
  -> another Persistence Realization
```

Persistence Provider内部のindex、transaction log、DB schema等をportable semantic formatへ漏らしません。

import / exportでunknown recordを保持する場合、runtimeが理解していないrecordを黙って再構成・正規化しません。Storage migrationだけを理由にSemantic Revisionも生成しません。

large binaryや外部Sourceをすべてinline化することは要求しません。payload locatorはPersistence / runtimeの実装詳細であり、Logical ReferenceやExact Bindingへfilesystem pathを埋め込むことも要求しません。

## 5. 保存と再開

Local Single-Node Packageは、少なくとも次を満たす必要があります。

1. portable semantic dataをdurable data rootへ保存できる。
2. processを終了した後、同じdata rootから別processで再読できる。
3. 再読後もlogical identity、Decision basis、Unknown / Conflict、Responsibility、Provenance等の意味差を保てる。
4. 保存途中の不完全な状態を正常に確定したpackageとして見せない。
5. supported Contract範囲ではruntime executableを交換してもsemantic dataを引き継げる方向を保つ。
6. Surface-local stateが失われてもcanonical semantic dataを失わない。

ISSUE-000054では、同一versionのbuild済みGo executableを実際に生成し、独立したsave processを終了した後に別processを起動して、durable dataだけからbundleを再構成できることを確認しました。

```text
same-version process restart: scoped Executable Evidence available
version-upgrade resume: not yet verified
```

process restartが成立したことを、executable version upgradeやRelease Evidenceへ広げません。

## 6. filesystem Persistence

最初のfilesystem Realizationでは、data root配下の`semantic.bundle.json`をcanonical bundle fileとして扱います。

reference probeでは、complete bytesをtemporary fileへ書き、file sync、closeの後にcanonical fileへrenameします。これはfirst filesystem Realizationのmechanicsであり、Universal Persistence要件ではありません。

この実装から、power loss時のcrash durability、directory fsyncを含む保証、Windows / macOS等を含む全platformでの同一挙動を推定しません。

## 7. backup / restore

最小profileでは、backupをrunning processのheap複製とは定義しません。別processで意味を再構成するために必要なdurable dataを対象とします。

reference probeではcanonical semantic bundle fileを別directoryへcopyし、そのrestore先から同じportable bytesを再読できることを確認しました。

これはcanonical bundle fileに限ったEvidenceです。将来追加されるexternal payload、credential、index等を含む完全なproduction backup、online backup、incremental backup、PITR等は未検証です。

## 8. Persistence交換とStorage migration

最小の交換境界は次です。

```text
Persistence A
  -> portable export
  -> Persistence B
  -> reload
  -> semantic comparison
```

reference probeではfilesystemからmemory Persistenceへoriginal Semantic Interchange bytesを移し、同じbundleを再読できることを確認しました。

これはPersistence Realization交換の補助的なExecutable Evidenceです。memory Persistenceは評価用であり、SCN-0008が想定するproduction RDB / object storeへのactual Storage migrationを証明するものではありません。

## 9. Local Reference Package

PMS-04の最小配布Evidenceを得るため、ISSUE-000055でLinux / amd64向けの**Local Reference Package**を実体化しました。

current reference profileは次です。

- version: `0.2.0-reference`
- target: `linux-amd64`
- archive: `soza-local-reference-linux-amd64.tar.gz`
- executable: `soza-local-reference`
- build metadata format: `soza.local-reference/v1`

Local Package Artifact workflowでは、同一inputからbinaryを2回buildし、byte-for-byte一致を確認します。さらにbuild identityを検査し、決定的なarchiveとSHA-256 checksumを作成します。

生成したarchiveは別directoryへ展開し、その中のbinary自身を独立したprocessとして使って、Semantic Interchangeのsave → process終了 → reloadを検査します。

Local Package Artifact Run `33509521544`はsuccessし、workflow artifact ID `9801021136`、workflow artifact digest `sha256:6282a2fe0b58dd023090d363e3323ce963a9f29c097f869ebab79b73aab2ba85`が記録されています。

```text
Local Reference Package PASS
  = PMS-04 Minimum scoped Executable Evidence
  != Product Release
  != formal platform support matrix
```

Linux / amd64、tar.gz、checksum、現在のlifecycle commandはreference distribution profileのRealizationです。Universal Product Requirementや恒久的Release formatではありません。

## 10. Product Interactionとの境界

PMS-04で扱うpackage lifecycle controlと、PMS-03で扱うProduct Interaction Surfaceを分けます。

```text
package lifecycle control
  != human / AI Product Interaction
```

`soza-local-reference`の`version` / `save` / `inspect`はPackaging acceptance用の管理操作です。Inquiry、Observation、Recommendation、Decision等を扱う正式なSEI CLIではありません。

正式なhuman-facing / AI-facing Surfaceは、引き続きPMS-03側のOpen Questionとして扱います。

## 11. Requirement / Acceptance監査

current Packaging境界とartifact実証は、主に既存のREQ-0001 / 0005 / 0009 / 0011 / 0018 / 0020 / 0021、SCN-0008 / 0010で表現できます。

literal process restartとreference distribution artifactまで実証した結果も、既存Requirementでは表現できない独立したfailureを示しませんでした。そのため、新しいstable Requirement / Scenarioは追加していません。

archive形式、target、checksum、build identity、package lifecycle commandはcurrent reference profileの実現方式であり、Universal Requirementではありません。

## 12. Current Evidence

```text
Packaging / Deployment Design: established
filesystem persistence: scoped Executable Evidence available
runtime-state-independent reconstruction: scoped Executable Evidence available
same-version literal process restart: scoped Executable Evidence available
canonical bundle copy / restore: scoped Executable Evidence available
filesystem -> memory Persistence exchange: scoped Executable Evidence available
Local Reference Package distribution artifact: scoped Executable Evidence available
Product Release: not yet verified
formal platform support matrix: not yet verified
version upgrade resume: not yet verified
actual production Storage migration: not yet verified
Release / Operational / Adoption: not yet verified
```

主なCIは次です。

- Semantic Runtime Conformance Run `33508376230` — literal process probe success
- Local Package Artifact Run `33509521544` — distribution artifact build / extract / save / reload / upload success
- Plan integrity Run `33509521580` — success
- Semantic Runtime Conformance Run `33509521596` — success

詳細は`../../runtime/PACKAGING_PROBE_EVIDENCE_2026-09-01.md`と`../../runtime/LOCAL_PACKAGE_ARTIFACT_EVIDENCE_2026-09-01.md`を参照します。

## 13. 次に固定しないこと

次はOpen Questionのまま残します。

- Product Releaseとして最初にsupportするOS / architecture
- production archive、installer、package manager、code signing、auto-update
- executable version upgrade後のresume
- productionで最初に採用するhuman-facing / AI-facing Product Interaction Surface
- RDBを最初のserver-side Storageとするか
- team / multi-user deployment topology
- online migration、HA / replication、production backup SLA
- container imageやcloud-managed deploymentを正式配布形態とするか
- background daemonを必須にするか

これらはLocal Reference PackageのPASSだけを理由にRequirementへ昇格させません。

## 14. 関連文書

- `../definition/SEI_PRODUCT_SHAPE.md`
- `../roadmap/SEI_PRODUCT_MILESTONES.md`
- `../interaction/SEI_PRODUCT_INTERACTION.md`
- `../../architecture/SEI_DEPLOYMENT_ARCHITECTURE.md`
- `../../requirements/PRODUCT_REQUIREMENTS.md`
- `../../requirements/ACCEPTANCE_SCENARIOS.md`
- `../../plan/adr/ADR-0007-canonical-persistence-boundary.md`
- `../../plan/adr/ADR-0027-go-as-standard-production-runtime-language.md`
- `../../plan/adr/ADR-0029-local-single-node-packaging-profile.md`
- `../../plan/issue/ISSUE-000046-define-v0-2-0-product-packaging-and-deployment-boundary.md`
- `../../plan/issue/ISSUE-000054-materialize-packaged-resume-and-storage-migration-probe.md`
- `../../plan/issue/ISSUE-000055-materialize-first-supported-local-package-artifact.md`
- `../../runtime/PACKAGING_PROBE_EVIDENCE_2026-09-01.md`
- `../../runtime/LOCAL_PACKAGE_ARTIFACT_EVIDENCE_2026-09-01.md`

## 15. Natural Japanese review

Product Value、Product Shape、PMS-04、Product Interaction、REQ-0001 / 0005 / 0009 / 0011 / 0018 / 0020 / 0021、SCN-0008 / 0010、ADR-0007 / 0027 / 0029、current Semantic Interchange runtime、Packaging probe、Local Reference Package、Local Package Artifact Run `33509521544`とartifact metadataを照合しました。Packagingをsemantic ontologyではなく、実行物・Persistence・durable data・portable semantic dataの組み合わせとして整理し、same-version process restartとversion upgrade、Persistence交換probeとactual production Storage migration、reference distribution artifactとProduct Release、package lifecycle controlと正式Product Interactionを分けています。そのうえで、意味、規範強度、未検証範囲、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。