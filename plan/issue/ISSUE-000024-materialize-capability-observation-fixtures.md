# ISSUE-000024: Capability Observation境界をschemaとfixtureで実体化する

Status: **Open**  
Priority: **2**  
Related ADRs: **ADR-0012, ADR-0013, ADR-0014, ADR-0019**  
Updated: 2026-08-31

## Goal

ADR-0019で確定したProvider-neutralなCapability Observation境界を、actual repositoryで検証できるschema、fixture、adapter contractへ落とす。

意味境界を先に固定した状態を保ち、TEI固有Schemaや一時的な実装都合からUniversal Coreを逆算しない。

## Required work

1. Capability Observationのportable最小schema候補を作る。
2. Provider referenceとProvider-specific context referenceを分離する。
3. observed condition、Unknown、Conflict、Withheldを表現できることを確認する。
4. Evidence / provenanceへの参照を持たせる。
5. 必要に応じてadapter / mapping definitionのlogical referenceとexact bindingを持てるようにする。
6. normalized comparison facetとraw source Observationを分離する。
7. TEI固有情報はopaque / typed referenceまたはProvider profile側へ残し、SOZA Core schemaへ展開しない。
8. Decision basisとして使った場合のhistorical reconstruction fixtureを作る。
9. Selective Disclosure fixtureを作る。
10. TEIとSaaS等、異なるProvider種別を同じCapability候補として比較するfixtureを作る。

## Required scenarios

### F1. TEI partial degradation

Applicationは利用可能だが、依存Databaseの一つがread-onlyである。

期待:

- Capability全体を機械的に`unavailable`へしない。
- 対象operationに応じたconstraintを保持する。
- 元のTEI Observationへ戻れる。

### F2. Proposed state != actual state

Database migration proposalが存在するが未採用である。

期待:

- proposalをactual stateとして扱わない。
- Decision前提へ利用した場合、どちらの状態を参照したか判別できる。

### F3. Release without environment binding

Application Releaseは存在するがEnvironmentへ未Bindingである。

期待:

- Releaseの存在だけでavailabilityを確定しない。
- Environment contextをProvider-specific referenceとして保持できる。

### F4. Observation gap

Plugin解決は成功しているがObservation Providerが利用不能である。

期待:

- `not observed`を`unavailable`へ変換しない。
- observation gap自体を後から確認できる。

### F5. Cross-provider comparison

同じCapabilityをTEIとSaaSが提供する。

期待:

- 共通facetで比較できる。
- Provider固有情報を同一schemaへ無理に平坦化しない。
- Universal scoreを必須にしない。

### F6. Historical reconstruction

後日TEI release、binding、adapter mappingが更新された後に、過去Decision時のObservationを再構成する。

期待:

- 現在版へ黙って差し替えない。
- Decision basisとして重要な可変入力をexact bindingから再確認できる。

### F7. Selective disclosure

Provider内部topologyの一部を開示せず、Capability Evidenceだけを共有する。

期待:

- WithheldとUnknownを区別できる。
- 非開示だけを理由にincompatibleと判定しない。

## Acceptance criteria

- [ ] ADR-0019の意味境界をschemaで表現できる。
- [ ] TEI固有型がSOZA Universal Coreへ漏れていない。
- [ ] F1〜F7のfixtureが存在する。
- [ ] fixtureごとにV1〜V8のどの価値を検証するか明示する。
- [ ] normalized facetからraw provenanceへ戻れる。
- [ ] historical reconstructionが現在版への追随ではなく当時版の復元になっている。
- [ ] actual repository上で再現可能なtest evidenceを得る。
- [ ] 文書・fixture説明を自然な日本語で再ドラフトし、最終意味監査を行う。

## Dependencies

- ADR-0006
- ADR-0008
- ADR-0012
- ADR-0013
- ADR-0014
- ADR-0019
- ISSUE-000009
- ISSUE-000022

`ISSUE-000022`でactual repository baselineが整うまでは、schema / fixtureの設計は進めても、actual-repository PASSを主張しない。

## Natural Japanese review

Issueの意味とAcceptance境界を確定した後、条件や技術的強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトした。最終意味監査も実施済み。
