# ADR-0029: 最初のPackagingをLocal Single-Node Profileとする

Status: **Accepted**  
Related Issues: **ISSUE-000046, ISSUE-000054**  
Updated: 2026-09-01

## Context

SOZAにはGo runtime、Semantic Contract、Interaction reference probe、Provider Adapter等があるが、実行物を終了した後にcanonical dataを保存・再読する最小製品単位はまだ定義していない。

最初のPackagingを考える際には、次を同時に満たす必要がある。

- 配布・起動が簡単であること。
- runtime executableを意味上の正本にしないこと。
- Storage implementationをUniversal Coreへ固定しないこと。
- 将来service / server / team deploymentへ分割してもsemantic boundaryを変えないこと。
- portable Semantic InterchangeをStorage交換の境界として利用できること。

Goはfirst-party production runtimeの標準言語として採用済みであり、単一バイナリとして配布しやすい。一方、その利点だけを理由にfilesystemやsingle-process構成を恒久的なProduct ontologyへ固定してはならない。

## Decision

最初に成立させるPackaging / Deployment Profileを**Local Single-Node Package**とする。

```text
Go runtime executable
  + replaceable Persistence boundary
  + explicit durable data root
  + portable semantic data
```

最小profileでは、単一host・単一processで開始できることを優先する。

ただし、次を意味上は分離する。

```text
runtime executable
  != canonical semantic data

one process
  != one semantic concern

filesystem locator
  != Logical Reference

Storage migration
  != Semantic Revision
```

最初のPersistence Realizationにはfilesystemを用いてよい。portable semantic dataはcurrent Semantic Interchange Contractを再利用し、package専用Universal Contractを新設しない。

Interaction Surfaceは同じprocessへ同居できるが、本ADRではWeb / desktop / CLI / HTTP / MCPのproduction標準を固定しない。

## 保存・再開の境界

最初のprofileは、少なくとも次を満たす。

1. durable data rootへportable semantic dataを保存できる。
2. process終了後、新しいruntime instanceが同じdata rootから再読できる。
3. logical identity、Decision basis、Unknown / Conflict、Responsibility、Provenance等を保存前後で失わない。
4. Surface-local stateをcanonical persistenceへ必須化しない。
5. 保存途中の不完全な出力を、正常なpackageとして扱わない。
6. filesystem pathをsemantic identityへ昇格させない。

atomic saveの実装方法はPersistence Realizationの責務とする。最初のfilesystem probeではtemporary fileへ完全に書き込んだ後に置換する方式を利用できる。

## import / export / migration

Storage交換は、原則として次の境界で扱う。

```text
Persistence A
  -> portable Semantic Interchange
  -> Persistence B
  -> reload / semantic verification
```

内部DB schema、file layout、object key、event sequence等をportable semantic contractへ持ち込まない。

未知Contract / versionを保持できても、その意味をvalidatedとは主張しない。

## Consequences

- 最初の製品単位を小さく保ち、配布・保存・再開を早く実証できる。
- Goの単一バイナリという配布上の利点を活用できる。
- filesystemを初期Realizationとして使っても、Storage semanticsへ固定されない。
- 将来server / DB / object storeへ移行する際、portable Semantic Interchangeを共通移行境界として再利用できる。
- production UIやmulti-user topologyの決定をPMS-04へ過剰に持ち込まずに済む。

一方、最初のprofileだけでは次は成立しない。

- production DBの選定
- concurrent write / transaction
- online migration
- multi-user / tenant separation
- HA / replication
- production backup SLA
- human usability

## Revisit conditions

次の場合は本Decisionを再検討する。

- 単一processでは最小利用形態すら成立しないことが実証された。
- portable Semantic InterchangeではStorage交換時に必要な意味を保持できない独立した失敗が確認された。
- filesystemを最初のPersistence Realizationにすると、probeではなく製品意味そのものがfilesystem mechanicsへ依存することが確認された。
- production security / collaboration要件から、local single-node profileとの重大な非互換が生じた。

## Evidence

- Design Evidence: **Satisfied by this ADR and Product Packaging baseline**
- Executable Evidence: **Not Yet Verified for save / restart / restore / migration** — ISSUE-000054で検証する。
- Release Evidence: **Not Yet Verified**
- Operational Evidence: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

## Natural Japanese review

Product Packaging baseline、REQ-0018 / 0021、ADR-0007 / 0027、Semantic Interchange、Payload Source、PMS-04を照合し、Go単一バイナリの利点とsemantic persistenceの権威を分離してDecisionを構成しました。Local Single-Node Packageは最初の実現profileであり、Universal ontologyや唯一のdeployment topologyではありません。未決事項とExecutable Evidence未成立範囲を残したまま、意味、規範強度、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。