# ISSUE-000020: TEIのApplication / Database情報をSOZAから読む境界を定める

Status: **Resolved**  
Priority: **5**  
Related ADRs: **ADR-0012, ADR-0013, ADR-0014, ADR-0019**  
Updated: 2026-08-31

## Goal

SOZAがCapability discovery / matching / choiceを行う際に、TEIのApplication、Database、Environment、Release、Observation等をどの粒度で参照すべきかを定める。

TEI固有SchemaをSOZA Coreへコピーせず、Capability判断に必要な情報だけをProvider-neutralに読める境界を設計する。

## Background

TEIでは、ApplicationとDatabaseを独立対象とし、一つのApplicationが複数Databaseを利用できる。

DatabaseにはDesired / Actual / Diff / Migration / Release / Contract等の状態があり、DeploymentではcommandとObservation / Evidenceを分離する。

SOZA側では、Capability Definition、Capability Observation、Recommendation、Decisionを分ける。

SOZAがTEIをCapability Providerとして扱うためには、TEI内部の詳細をすべて知らなくても、たとえば次を判断材料として扱える必要がある。

- このCapabilityは何を提供できるか。
- 現在、何が観察できているか。
- どのConstraintを満たす可能性があるか。
- 未確認点やConflictは何か。
- どのEvidenceからそう判断できるか。
- 実行に進む前に追加Decision / Authorizationが必要か。

## Questions reviewed

1. TEIのCapability DefinitionをSOZAのCapability Definitionへどう対応付けるか。
2. Application / Database ContractをProvider-specific Observationとして読むべきか。
3. Environmentごとのavailabilityやprovider bindingをどの粒度で外在化するか。
4. Database migration未完了等の状態を、Capability unavailable、degraded、unknown等へ誰が解釈するか。
5. TEIのObserved StateとSOZA Capability Observationを同一Artifactにすべきか、adapterで変換すべきか。
6. TEI release versionやPlugin LockをSOZA Decisionのhistorical inputとして参照する必要があるか。
7. Capability choice時にTEI内部のApplication / Database topologyをどこまで見せるべきか。
8. SOZAがTEI固有lifecycleを理解せずに、必要なEvidenceだけを検証できるか。

## Resolution

ADR-0019で、Provider-neutralなCapability Observation境界をAccepted Decisionとして確定した。

### 1. TEI内部状態をSOZA Coreへ複製しない

Application、Database、Environment、Release、Plugin等のTEI固有modelはProvider側に残す。

SOZAはProvider adapterを介して、Capability Choiceに必要なObservation、Unknown、Conflict、Evidence、Provenance、Assurance等を受け取る。

### 2. Capability DefinitionとObservationを分ける

Capability Definitionは「何を可能にするか」を表し、Capability Observationは「あるProviderが、ある時点・文脈でどのように観察されたか」を表す。

Providerの一時状態でCapability Definitionを書き換えない。

### 3. Provider statusからavailabilityやDecisionを自動確定しない

```text
Provider status != universal availability truth
Provider Observation != Capability Choice Decision
Not observed != unavailable
```

Applicationがreadyであること、Releaseが存在すること、Pluginが解決済みであること等を、単独でCapability利用可能性の十分条件としない。

### 4. 通常判断と詳細監査を分ける

通常のCapability Choiceでは、Provider-neutralなObservationとEvidence referenceを扱う。

重要Decisionの監査やhistorical reconstructionでは、権限がある範囲でTEI Release、Binding、Database Contract等のprovider-specific exact snapshotへ降りられることを認める。

### 5. Selective Disclosureを前提にする

TEI内部topologyを全量開示することを要求しない。

必要なObservation / Evidenceだけを共有し、非開示・未確認部分は既知として補完しない。

### 6. TEIを特権化しない

この境界はTEI連携から導いたが、SaaS、人間、AI、他の業務基盤にも適用できるProvider-neutralな設計とする。

## Required scenarios disposition

1. TEI Applicationが利用可能だが、依存Databaseの一つがread-onlyである。→ 複数ObservationとConstraintとして扱い、単一statusへ潰さない。
2. Database migration proposalはあるが未採用である。→ Proposal存在をActual stateやavailabilityへ昇格させない。
3. Application Releaseは存在するがEnvironmentへ未Bindingである。→ Release存在と利用可能性を分ける。
4. TEI Pluginは解決済みだがObservation Providerが利用不能である。→ `not observed` / Unknownを保持する。
5. same CapabilityをTEIとSaaSの両方が提供する。→ 同じProvider-neutralな判断面で比較する。
6. TEIの一部構成がunknownで、SOZAが選択を保留する。→ 正規のDecision outcomeとして許容する。
7. 過去Decision時に参照したTEI release / bindingを後から再構成する。→ exact provider referenceへ降りる。
8. TEI内部topologyをSelective DisclosureしながらCapability evidenceだけ共有する。→ 全量開示を要求しない。

## Deliverables

Decision boundaryとして次を完了した。

- [x] TEI→SOZA Capability Observation adapter boundary
- [x] Provider-neutral Observationに必要な意味項目
- [x] exact historical referenceの原則
- [x] selective disclosure rule
- [x] Provider status / availability / Decisionの非同一性
- [x] ADR-0019 Accepted

具体的なschema、adapter contract、fixtures、actual repositoryでのconformanceは未実装であり、このIssueのResolutionに含めない。後続の`ISSUE-000025`で扱う。

## Reopen conditions

ADR-0019の境界そのものは、次の場合に再検討する。

- 複数ProviderでProvider-neutral Observationでは重要な意味差を保てないことが繰り返し確認される。
- adapter layerがProvider lifecycleそのものをSOZA側へ再実装する状態になる。
- Selective Disclosure下でhistorical reconstructionが成立しないことが継続的に問題になる。

具体contract / fixtureの不足は、このIssueを再開せず`ISSUE-000025`で扱う。

## Source

- `plan/kj/2026-08-31_ReferenceModel_CapabilityObservation_ラウンドKJ.md`
- ADR-0012
- ADR-0013
- ADR-0014
- ADR-0019

## Natural Japanese review

ADR-0019とRequired scenariosを照合してResolutionを確定した後、意味、強度、留保、Provider-neutral性を変えず、自然な日本語となることを最重要視して全文を再ドラフトした。その後、最終意味監査を実施済み。
