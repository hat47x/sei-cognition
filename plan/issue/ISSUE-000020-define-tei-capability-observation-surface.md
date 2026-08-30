# ISSUE-000020: TEIのApplication / Database情報をSOZAから読む境界を定める

Status: **Open**  
Priority: **5**  
Related ADRs: **ADR-0012, ADR-0013, ADR-0014**  
Updated: 2026-08-31

## Goal

SOZAがCapability discovery / matching / choiceを行う際に、TEIのApplication、Database、Environment、Release、Observation等をどの粒度で参照すべきかを定める。

TEI固有SchemaをSOZA Coreへコピーせず、Capability判断に必要な情報だけをProvider-neutralに読める境界を設計する。

## Background

TEIでは、ApplicationとDatabaseを独立対象とし、一つのApplicationが複数Databaseを利用できる。

DatabaseにはDesired / Actual / Diff / Migration / Release / Contractがあり、DeploymentではcommandとObservation / Evidenceを分離する。

SOZA側では、Capability Definition、Capability Observation、Matching、Decisionを分ける。

SOZAがTEIをCapability Providerとして扱うためには、TEI内部の詳細をすべて知らなくても、たとえば次を判断できる必要がある。

- このCapabilityは何を提供できるか。
- 現在利用可能か。
- どのConstraintを満たすか。
- 未確認点は何か。
- どのEvidenceからそう判断できるか。
- 実行に進む前に追加Decision / Authorizationが必要か。

## Questions

1. TEIのCapability DefinitionをSOZAのCapability Definitionへどう対応付けるか。
2. Application / Database ContractをProvider-specific Observationとして読むべきか。
3. Environmentごとのavailabilityやprovider bindingをどの粒度で外在化するか。
4. Database migration未完了等の状態を、Capability unavailable、degraded、unknown等へ誰が解釈するか。
5. TEIのObserved StateとSOZA Capability Observationを同一Artifactにすべきか、adapterで変換すべきか。
6. TEI release versionやPlugin LockをSOZA Decisionのexact historical inputとして参照する必要があるか。
7. Capability choice時にTEI内部のApplication / Database topologyをどこまで見せるべきか。
8. SOZAがTEI固有lifecycleを理解せずに、必要なEvidenceだけを検証できるか。

## Constraints

- TEIのApplication / Database / Deployment schemaをSOZA Universal Coreへ複製しない。
- TEI internal stateからSOZA Decisionを自動生成しない。
- TEIが関連製品であることを理由にmatchingを優遇しない。
- Provider-specific unknownを`unavailable`へ潰さない。
- command acknowledgementをCapability availabilityの十分なEvidenceとしない。
- SOZAがTEIのruntime authorityを持つ前提にしない。

## Required scenarios

1. TEI Applicationが利用可能だが、依存Databaseの一つがread-onlyである。
2. Database migration proposalはあるが未採用である。
3. Application Releaseは存在するがEnvironmentへ未Bindingである。
4. TEI Pluginは解決済みだがObservation Providerが利用不能である。
5. same CapabilityをTEIとSaaSの両方が提供する。
6. TEIの一部構成がunknownで、SOZAが選択を保留する。
7. 過去Decision時に参照したTEI release / bindingを後から再構成する。
8. TEI内部topologyをSelective DisclosureしながらCapability evidenceだけ共有する。

## Deliverables

- TEI→SOZA Capability Observation adapter boundary
- 必要なminimum fields / references
- exact historical binding rule
- selective disclosure rule
- provider-neutral fixtures
- ADR候補

## Source

`plan/kj/2026-08-31_TEI設計系列_ラウンドKJ統合.md` のG06を起点とする。

## Natural Japanese review

Issue作成後に自然な日本語の全文ドラフト工程を実施済み。Decision確定時にも再監査する。
