# ISSUE-000054: packaged resume / Storage migration reference probeを実体化する

Status: **Open**  
Priority: **1**  
Related ADRs: **ADR-0007, ADR-0021, ADR-0022, ADR-0027, ADR-0029**  
Updated: 2026-09-01

## Goal

PMS-04と`product/packaging/SOZA_PRODUCT_PACKAGING.md`で定めたLocal Single-Node Packageについて、**portable semantic dataを保存し、process相当のin-memory stateを破棄した後に別runtime instanceで再開できること**をreference probeで検証する。

あわせて、filesystem persistenceと別Persistence Realization相当のmemory storeの間でportable Semantic Interchangeを移し、Storage implementationがsemantic identityになっていないことを限定的に確認する。

## Probe方針

first probeではproduction databaseや正式CLIを作らない。

```text
runtime instance A
  -> filesystem persistence
  -> process state discarded
  -> runtime instance B
  -> reload

filesystem persistence
  -> portable export
  -> memory persistence
  -> reload
```

同じSemantic Interchange bytesをPersistence境界の中心に置き、新しいpackage専用Universal Contractは追加しない。

## 実装方針

SOZA first-party runtime policyに従いGoで実装する。

既存`semanticruntime.LoadInterchange` / `Bundle.ExportOriginal`を再利用し、Semantic Interchangeのparse / validationを別実装しない。

最小Persistence interfaceはprobe-local / runtime-level interfaceとし、Universal Contractにはしない。

候補操作は次とする。

- `Save`
- `Load`
- `Export`
- `Import`

filesystem Realizationではtemporary fileへ完全書き込み後にrenameする方式を利用し、不完全なtemporary fileを通常のpackageとして読み込まない。

memory RealizationはStorage交換probe用の第二Realizationとして用いる。production in-memory StorageをsupportするDecisionではない。

## 必須検査

1. valid Semantic Interchange bytesをfilesystemへ保存できる。
2. 保存後にruntime / Bundle objectを破棄し、新しいinstanceから再読できる。
3. reload後もoriginal Semantic Interchange bytesを必要な範囲で保持する。
4. logical identityとtyped recordの意味が保存前後で一致する。
5. unknown Contract recordをopaque `not_verified`のまま保持する。
6. filesystem pathをLogical Referenceへ混入させない。
7. Surface-local stateを保存しなくてもcanonical bundleを再読できる。
8. data rootを別directoryへcopyしたrestoreで同じbundleを再読できる。
9. incomplete / invalid canonical fileを正常packageとして受理しない。
10. filesystemからexportしたportable bytesをmemory Persistenceへimportし、再読できる。
11. Persistence交換前後でsemantic bundleのidentity / referencesが保持される。
12. Storage migrationをSemantic Revisionとして自動生成しない。

## Negative cases

- invalid JSONを正常packageとして受理する。
- unknown Contract payloadをvalidatedへ昇格させる。
- restore先directoryのpathをsemantic identityとして扱う。
- temporary fileだけが存在する状態を正常save済みと扱う。
- Storage交換時にlogical refを新しいphysical IDへ書き換える。
- import時にoriginal Semantic Interchange bytesを不要に正規化し、opaque payloadを変える。

## Requirement / Scenario判断

主な検査軸は既存の次とする。

- REQ-0001
- REQ-0005
- REQ-0009
- REQ-0011
- REQ-0018
- REQ-0020
- REQ-0021
- SCN-0008
- SCN-0010

process restart後のresumeが、これらでは表現できない独立したProduct failureであることがprobeから確認された場合だけ、Candidate Scenarioとして追加を検討する。

## Non-goals

- production database選定
- database schema設計
- concurrent writer対応
- transaction isolation設計
- online migration
- distributed Storage
- cloud backup
- HA / replication
- production CLI / Web UI
- production security
- release package作成

## 完了条件

- [ ] filesystem Persistence probeを実体化する。
- [ ] memory Persistence probeを実体化する。
- [ ] save → state破棄 → reloadをactual testへ落とす。
- [ ] backup / restore相当のdirectory copy testを行う。
- [ ] filesystem → portable export → memory importをtestする。
- [ ] incomplete / invalid stateのnegative testを行う。
- [ ] existing semanticruntimeとの重複監査を行う。
- [ ] CIで再現可能なExecutable Evidenceを得る。
- [ ] PMS-04 / Product Packaging / Evidence文書へ結果を同期する。
- [ ] Requirement / SCN追加の要否を再監査する。
- [ ] 自然な日本語全文再ドラフトと最終意味監査を行う。
- [ ] 対象CIをsuccessさせる。

## Evidence state

- Design Evidence: **Satisfied for probe plan**
- Executable Evidence: **Not Yet Verified**
- Release Evidence: **Not Yet Verified**
- Operational Evidence: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

## Natural Japanese review

PMS-04、Product Packaging baseline、ADR-0029、REQ-0018 / 0021、SCN-0008 / 0010、current Semantic Interchange runtimeを照合し、production Storage選定ではなくsave / restart / restore / Storage交換の意味保持を確認するreference probeとして整理しました。probe-local Persistence interfaceをUniversal Contractへ昇格させず、既存runtimeを再利用する方針と未検証範囲を明確にしたうえで、意味、検査強度、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。