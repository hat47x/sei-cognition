# ISSUE-000046: v0.2.0 Product Packaging / Deployment boundaryを定義する

Status: **Resolved**  
Priority: **2**  
Related ADRs: **ADR-0007, ADR-0014, ADR-0021, ADR-0022, ADR-0027, ADR-0029**  
Updated: 2026-09-01

## Goal

SOZAのsemantic boundaryを保ったまま、実際に利用可能な製品へ近づけるため、**何を最初の配布・実行単位として提供し、耐久データ、Storage、Interaction Surface、外部Providerをどの境界から接続するか**を定義する。

library、service、CLI、reference UI、embedded storage等を、現在の実装都合だけでProduct ontologyへ固定しない。

## Resolution

最初に成立させるPackaging / Deployment Profileを、**Local Single-Node Package**として定義した。

正本は`product/packaging/SOZA_PRODUCT_PACKAGING.md`、Deployment Architectureは`architecture/SOZA_DEPLOYMENT_ARCHITECTURE.md`、技術判断はADR-0029とする。

```text
Go runtime executable
  + replaceable Persistence boundary
  + explicit durable data root
  + portable semantic data
```

Goの単一バイナリ化は配布上の利点として利用するが、実行物そのものをcanonical semantic dataにはしない。

```text
runtime executable
  != canonical semantic data

filesystem locator
  != Logical Reference

Storage migration
  != Semantic Revision
```

## 最初のPackaging構成

### runtime

ADR-0027に従いfirst-party runtimeはGoを標準とする。

最小profileでは単一host・単一processで開始できることを優先し、最初から複数daemon、service mesh、Kubernetes等を要求しない。

### durable data root

process外に明示的なdurable data rootを置く。

最初のfilesystem Realizationでは、portable Semantic Interchangeをcanonical semantic bundleとして保持する。file pathやdirectory名はphysical locatorであり、semantic identityにはしない。

### Interaction Surface

Interaction Surfaceは同一processへ載せられるが、本IssueではWeb / desktop / CLI / HTTP API / MCPのproduction標準を決定しない。

PMS-03で定めたSurfaceとcanonical meaningの分離を維持する。

### Persistence

Storageは交換可能なRealizationとする。

最初のfilesystem Realizationの後にRDB / object store等へ移行しても、portable Semantic Interchangeを介してlogical identity、historical meaning、unknown record等を保持できる構造を優先する。

## import / export / migration

新しいpackage専用Universal Contractは追加せず、current `soza.semantic-interchange/v1alpha1`をportable semantic export / importの中心として再利用する。

```text
Persistence A
  -> portable Semantic Interchange
  -> Persistence B
  -> reload / semantic verification
```

Storage内部のrow ID、file path、object key、event sequence等をportable semantic contractへ持ち込まない。

## 保存・再開

最小packageは、少なくとも次を満たす必要がある。

1. portable semantic dataをdurable storageへ保存できる。
2. process終了後、別runtime instanceで再読できる。
3. 保存・再読前後でsemantic identityと重要な意味差を失わない。
4. Surface-local stateをcanonical persistenceへ必須化しない。
5. 不完全なwriteを正常packageとして扱わない。
6. unknown Contract / versionを保持する場合、理解済み・validatedへ昇格させない。

## backup / restore

最初のfilesystem profileでは、整合したdurable data rootを別locationへ複製し、restore先から同じportable semantic dataを再読できることを最小条件とする。

online backup、incremental backup、PITR、HA / replicationは本Issueでは要求しない。

## Requirement / Acceptance監査

新しいstable Product Requirementは追加しない。

Packaging境界に必要な意味は、主に既存の次で表現できる。

- REQ-0001 — 耐久的な意味の連続性
- REQ-0005 — Decisionの歴史的再構成
- REQ-0009 — Revision / Supersessionの完全性
- REQ-0011 — Projectionを意味上の正本にしない
- REQ-0018 — Storage実装から意味を独立させる
- REQ-0020 — Evidenceを超える達成主張をしない
- REQ-0021 — Realization / Executionを交換可能にする

AcceptanceではSCN-0008「Storageを交換する」、SCN-0010「可変Artifact更新後に過去Decisionを再構成する」を中心に再利用する。

process restart後のresumeが既存Scenarioでは表現できない独立したProduct failureかどうかは、ISSUE-000054のprobe結果から再監査する。

## Open questions

次は本Issueで固定しない。

- productionで最初にsupportedとするhuman-facing UI
- productionで最初にsupportedとするAI-facing protocol
- server-side StorageとしてRDBをいつ採用するか
- team / multi-user topology
- online migration
- HA / replication
- cloud-managed deployment
- container imageを正式配布物とするか
- production backup SLA

## Non-goals

- production cloud architectureの全面確定
- Kubernetes等への固定
- workflow engineの内製
- general-purpose object storageの内製
- enterprise IAMの確定
- production UIの確定
- Release packageの完成

## 完了条件

- [x] v0.2.0以降で成立させる最小Packaging構成を定める。
- [x] semantic boundaryとdeployable unitの対応をDeployment Architectureへ反映する。
- [x] Storageの最小support範囲と非対象を明示する。
- [x] import / export / migrationの必要Acceptanceを整理する。
- [x] Requirement / SCNを既存項目と重複監査する。今回は追加しない。
- [x] 技術選択をADR-0029として正本化する。
- [x] prototype / conformanceのExecutable Evidence条件を定義する。
- [x] 実証作業をISSUE-000054へ切り出す。
- [x] 自然な日本語全文再ドラフトと最終意味監査を行う。
- [ ] 対象CIをsuccessさせる。

CIは本branchの最終headで確認し、成功後に本項目を同期する。

## Evidence state

- Design Evidence: **Satisfied for Packaging / Deployment boundary**
- Executable Evidence: **Not Yet Verified as a packaged resume / Storage migration** — ISSUE-000054で検証する。
- Release Evidence: **Not Yet Verified**
- Operational Evidence: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

## Reopen条件

- Local Single-Node Profileでは最小利用形態自体が成立しないEvidenceが得られた。
- portable Semantic Interchangeを介したStorage交換では必要な意味を保持できない独立した失敗が確認された。
- PackagingとIdentity / Authorizationの境界に重大な矛盾が確認された。
- actual production usabilityから、現在のdeployment boundaryそのものがProduct Shapeと合わないことが確認された。

## Natural Japanese review

Product Shape、Product Interaction、PMS-04、REQ-0001 / 0005 / 0009 / 0011 / 0018 / 0020 / 0021、SCN-0008 / 0010、ADR-0007 / 0014 / 0021 / 0022 / 0027 / 0029、current Semantic Interchange runtimeとPayload Source境界へ戻り、Packagingを実行物、Persistence、durable data、portable semantic dataの関係として整理しました。Go単一バイナリとfilesystemは最初のRealizationとして利用しつつ、意味上の正本や唯一のdeployment topologyへ昇格させていません。未決事項とExecutable Evidence未成立範囲を残したまま、意味、規範強度、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。