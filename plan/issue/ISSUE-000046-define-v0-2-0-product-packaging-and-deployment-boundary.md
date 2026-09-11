# ISSUE-000046: v0.2.0 Product Packaging / Deployment boundaryを定義する

Status: **Resolved**  
Priority: **2**  
Related ADRs: **ADR-0007, ADR-0014, ADR-0021, ADR-0022, ADR-0029**  
Updated: 2026-09-01

## Goal

SOZAのsemantic boundaryを保ったまま実際に利用可能な製品へ近づけるため、**何を最初の配布・実行単位とし、耐久データ、Persistence、Interaction Surface、外部Providerをどの境界から接続するか**を定義する。

library、service、CLI、reference UI、embedded storage等を、現在の実装都合だけでProduct ontologyへ固定しない。

## Resolution

最初のPackaging / Deployment Profileを**Local Single-Node Package**とする。

正本は`product/packaging/SOZA_PRODUCT_PACKAGING.md`、Deployment Architectureは`architecture/SOZA_DEPLOYMENT_ARCHITECTURE.md`、技術判断はADR-0029とする。

```text
Go runtime executable
  + replaceable Persistence boundary
  + explicit durable data root
  + portable semantic data
```

Goの単一バイナリ化は配布上の利点として利用するが、実行物そのものをcanonical semantic dataにはしない。

```text
runtime executable != canonical semantic data
filesystem locator != Logical Reference
Storage migration != Semantic Revision
```

## 最初のPackaging構成

### runtime

ADR-0027に従い、first-party runtimeの標準実装言語はGoとする。最初は単一host・単一processで始められることを優先し、複数daemon、service mesh、Kubernetes等を前提にしない。

### durable data root

process外に明示的なdurable data rootを置く。最初のfilesystem Realizationではportable Semantic Interchangeをcanonical semantic bundleとして保持し、file pathやdirectory名をsemantic identityにはしない。

### Interaction Surface

Interaction Surfaceは同一processへ載せられるが、本IssueではWeb / desktop / CLI / HTTP API / MCPのproduction標準を決めない。PMS-03で定めたSurfaceとcanonical meaningの分離を維持する。

### Persistence

Persistenceは交換可能なRealizationとする。filesystemから将来RDB / object store等へ移行しても、portable semantic boundaryを介してlogical identity、historical meaning、unknown record等を保持できる構造を優先する。

## import / export / migration

package専用の新しいUniversal Contractは追加せず、current `sei.semantic-interchange/v1alpha1`をportable semantic export / importの中心として再利用する。

```text
Persistence A
  -> portable Semantic Interchange
  -> Persistence B
  -> reload / semantic verification
```

Storage内部のrow ID、file path、object key、event sequence等をportable semantic contractへ持ち込まない。

## 保存・再開

最小packageには、少なくとも次を求める。

1. portable semantic dataをdurable storageへ保存できる。
2. process終了後、別processから再読できる。
3. 保存・再読前後でsemantic identityと重要な意味差を失わない。
4. Surface-local stateをcanonical persistenceへ必須化しない。
5. 不完全なwriteを正常packageとして扱わない。
6. unknown Contract / versionを保持する場合、理解済み・validatedへ昇格させない。

ISSUE-000054では、build済みGo executableを独立したprocessとして起動し、save process終了後に別processがdurable dataだけから再読できることをactual testで確認した。

## Local Reference Package

ISSUE-000055では、PMS-04の配布に関するMinimum Executable Evidenceを得るため、Linux / amd64向けのLocal Reference Packageを実体化した。

Local Package Artifact Run `33509521544`では、次がすべてsuccessした。

- 同一inputからbinaryを2回buildし、byte-for-byte一致を検査する。
- artifact version、source commit、targetをbuild identityとして保持する。
- 決定的なtar.gzとSHA-256 checksumを生成する。
- archiveを別directoryへ展開する。
- 展開したartifactでsave → process終了 → reloadを実行する。
- 生成物をGitHub Actions artifactへ保存する。

保存されたworkflow artifactは、artifact ID `9801021136`、digest `sha256:6282a2fe0b58dd023090d363e3323ce963a9f29c097f869ebab79b73aab2ba85`である。

これはLocal Reference Packageのscoped Executable Evidenceであり、Product Releaseではない。

## backup / restore

最初のfilesystem profileでは、整合したcanonical bundleを別locationへ複製し、restore先から同じportable semantic dataを再読できることを最小条件とする。

ISSUE-000054ではcanonical bundle fileのcopy / restoreを確認した。online backup、incremental backup、PITR、HA / replication、external payloadを含むproduction backup全体は本Issueの成立条件には含めない。

## Requirement / Acceptance監査

新しいstable Product RequirementやAcceptance Scenarioは追加しない。

Packaging境界と今回の実証は、主に既存の次で表現できる。

- REQ-0001 — 耐久的な意味の連続性
- REQ-0005 — Decisionの歴史的再構成
- REQ-0009 — Revision / Supersessionの完全性
- REQ-0011 — Projectionを意味上の正本にしない
- REQ-0018 — Storage実装から意味を独立させる
- REQ-0020 — Evidenceを超える達成主張をしない
- REQ-0021 — Realization / Executionを交換可能にする

AcceptanceではSCN-0008「Storageを交換する」、SCN-0010「可変Artifact更新後に過去Decisionを再構成する」を中心に再利用する。

literal process restartやreference artifact化の過程でも、既存Requirement / Scenarioでは表現できない独立したsemantic failureは確認されなかった。

なお、filesystem / memory間のPersistence交換probeをSCN-0008が想定するproduction Storage migrationへ昇格させない。SCN-0008のactual RDB / object-store migration Evidenceは引き続き未検証である。

## Open questions

次は本Issueで固定しない。

- Product Releaseとして最初にsupportするOS / architecture
- productionのhuman-facing / AI-facing Surface
- executable version upgrade後のresume
- production installer / package manager / signing / auto-update
- server-side StorageとしてRDB / object storeをいつ採用するか
- team / multi-user topology
- online migration
- HA / replication
- cloud-managed deployment
- production backup SLA

## Non-goals

- production cloud architectureの全面確定
- Kubernetes等への固定
- workflow engineの内製
- general-purpose object storageの内製
- enterprise IAMの確定
- production UIの確定
- Product Releaseの成立

## 完了条件

- [x] 最小Packaging構成を定める。
- [x] semantic boundaryとdeployable unitの対応をDeployment Architectureへ反映する。
- [x] Persistenceの最小support範囲と非対象を明示する。
- [x] import / export / migrationのAcceptanceを整理する。
- [x] Requirement / SCNを既存項目と重複監査する。今回は追加しない。
- [x] 技術選択をADR-0029として正本化する。
- [x] literal process restartをISSUE-000054で実証する。
- [x] Local Reference PackageをISSUE-000055で実証する。
- [x] PMS-04へMinimum scoped Executable Evidenceを同期する。
- [x] 自然な日本語全文再ドラフトと最終意味監査を行う。
- [x] 対象CIをsuccessさせる。

## CI Evidence

主要なEvidenceは次のとおり。

- Semantic Runtime Conformance Run `33508376230` — literal process restart probe: **success**
- Local Package Artifact Run `33509521544` — reference distribution artifact: **success**
- Plan integrity Run `33509521580` — **success**
- Semantic Runtime Conformance Run `33509521596` — **success**

最終branch headについてはmerge前にPlan integrityを再確認する。

## Evidence state

- Design Evidence: **Satisfied for Packaging / Deployment boundary**
- Executable Evidence: **Minimum scoped Evidence available** — Local Reference Packageの範囲で配布・保存・再開を確認済み。
- Release Evidence: **Not Yet Verified**
- Operational Evidence: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

```text
PMS-04 Minimum scoped Evidence available
  != Product Release
  != formal platform support matrix
  != version upgrade compatibility proven
  != crash durability proven
  != actual production Storage migration proven
```

## Reopen条件

- Local Single-Node Profileでは最小利用形態自体が成立しないEvidenceが得られた。
- supported Release artifactへ進む際、現在のPackaging boundaryではsemantic continuityを保てない。
- executable version upgradeでsupported semantic dataを再読できない。
- production Storageへの移行でportable Semantic Interchangeでは意味を保持できない独立した失敗が確認された。
- PackagingとIdentity / Authorizationの境界に重大な矛盾が確認された。

## Natural Japanese review

Product Shape、Product Interaction、PMS-04、REQ-0001 / 0005 / 0009 / 0011 / 0018 / 0020 / 0021、SCN-0008 / 0010、ADR-0007 / 0014 / 0021 / 0022 / 0029、current Semantic Interchange runtime、ISSUE-000054のliteral process restart、ISSUE-000055のLocal Reference Package、Local Package Artifact Run `33509521544`を照合しました。Packagingを実行物、Persistence、durable data、portable semantic dataの関係として整理し、reference distribution artifactとProduct Release、package lifecycle controlとProduct Interaction、Persistence交換probeとactual production Storage migrationを分けています。Go単一バイナリ、filesystem、Linux / amd64等のRealizationを意味上の正本や唯一のdeployment topologyへ昇格させず、未検証事項も残したまま、意味、規範強度、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。