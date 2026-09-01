# ISSUE-000046: v0.2.0 Product Packaging / Deployment boundaryを定義する

Status: **Open**  
Priority: **2**  
Related ADRs: **ADR-0007, ADR-0014, ADR-0021, ADR-0022**  
Updated: 2026-09-01

## Goal

SOZAのsemantic boundaryを保ったまま、v0.2.0以降で実際に利用可能な製品へ近づけるため、**何を配布単位・実行単位として提供し、Storageや外部Providerをどこから接続するか**を定義する。

library、service、CLI、reference UI、embedded storage等を、現在の実装都合だけで製品ontologyへ固定しない。

## 背景

current repositoryにはGo runtime、Contract / Profile、fixture、Provider Adapter等があるが、これらは主にscoped Executable Evidenceであり、一つのdeployable productとしてのPackagingはまだ定義していない。

Product Shapeでは、Work / Interaction、Canonical Semantic Access、Integration、Projection / Review等の論理Surfaceを定めた。次は、それらをどのdeployment unitへ配置するかを、semantic boundaryと分けて決める必要がある。

## 検討対象

### Packaging

候補例:

- reusable Go library
- long-running service
- CLI
- reference UI
- local / embedded single-user package
- team / server package

一つに限定する前提ではない。ただし、最初のsupported combinationを明示する必要がある。

### Storage boundary

- canonical persistenceをどこが担うか。
- embedded / filesystem / relational DB / object storage等をどの順序でsupportするか。
- semantic referenceとphysical locatorを混同しないこと。
- backup / restore / migrationに必要な最低条件は何か。

### Deployment boundary

- 一つのprocessで始めても、論理Surfaceの意味境界を失わないこと。
- 将来分割してもcanonical semanticsが変わらないこと。
- workflow / agent runtimeを内蔵必須にしないこと。

### Portability

- export / importまたは等価な移行境界をどこまでv0.2.0で扱うか。
- ProviderやStorageを交換したときのExact Binding / payload availabilityの扱い。

## Non-goals

- production cloud architectureの全面確定
- Kubernetes等の特定基盤への固定
- workflow engineの内製
- general-purpose object storageの内製
- enterprise IAMの本Issue内での確定

## 完了条件

- [ ] v0.2.0でsupportする最小Packaging構成を定める。
- [ ] semantic boundaryとdeployable unitの対応をArchitectureへ反映する。
- [ ] Storageの最小support範囲と非対象を明示する。
- [ ] import / export / migrationの必要Acceptanceを整理する。
- [ ] 必要なREQ / SCNを既存項目との重複監査後に追加・更新する。
- [ ] 技術選択を伴う場合はADRを作成する。
- [ ] prototype / conformanceのExecutable Evidence条件を定義する。
- [ ] 自然な日本語全文再ドラフトと最終意味監査を行う。
- [ ] 対象CIをsuccessさせる。

## Evidence state

- Design Evidence: **Not Yet Verified for Packaging / Deployment**
- Executable Evidence: **Not Yet Verified as a packaged product**
- Release Evidence: **Not Yet Verified**
- Operational Evidence: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

## Natural Japanese review

Product Shape、REQ-0001 / 0018 / 0021、ADR-0007 / 0014 / 0021 / 0022、current Go runtimeとpayload acquisition境界へ戻り、semantic portabilityとdeployment方式を混同しないPackaging課題として整理した。特定cloudやruntimeへ早期固定せず、最初のsupported combinationを定めるための論点に限定して、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。
