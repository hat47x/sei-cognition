# ISSUE-000025: Provider-neutral Capability Observationのcontractとfixtureを実体化する

Status: **Blocked**  
Priority: **2**  
Related ADRs: **ADR-0012, ADR-0013, ADR-0014, ADR-0019**  
Updated: 2026-08-31

## Goal

ADR-0019で確定したProvider-neutralなCapability Observation境界を、actual repository上で検査可能なcontract、schema、fixture、adapter conformanceへ落とす。

このIssueでは新しい意味境界を発明するのではなく、Accepted ADRを実装・検査可能な形へ具体化する。

## Background

ADR-0019では、Provider内部状態とSOZA Capability Observationを分離し、Provider adapterを介してObservation、Unknown、Conflict、Evidence、Provenance、Assurance等を扱う方針を確定した。

しかしactual GitHub repositoryには、現時点で`contracts/`、`fixtures/`、runtime等の基線がまだ実体化していない。historical / local candidateに類似資産が存在しても、それをactual repositoryの実装Evidenceとして扱うことはできない。

そのため、`ISSUE-000022`でrepository baselineが実体化されるまで、actual contract / fixtureの配置とconformance実行はBlockedとする。

## Questions

1. ADR-0019の意味を保つ最小contractは何か。
2. Capability、Provider、context / environment、observed facts、Unknown、Conflict、Evidence reference、Provenance、Assurance、exact provider referenceをどのように表すか。
3. Provider-specific extensionをCore contractへ漏らさずに保持する方法は何か。
4. adapterによるderived Observationで、source referenceとmapping / adapter revisionをどう追跡するか。
5. Selective Disclosure下で、非開示とUnknownをどう区別するか。
6. Provider statusからCapability Decisionを自動生成していないことを、fixtureでどう検査するか。
7. TEI以外のProviderでも同じcontractが成立することをどう確認するか。

## Constraints

- TEIのApplication / Database / Environment schemaをSOZA Coreへコピーしない。
- `available / unavailable`だけのUniversal enumへ縮退させない。
- `not observed`、Unknown、Conflictを否定値へ変換しない。
- Provider ObservationをCapability Choice Decisionへ自動昇格させない。
- adapterの変換結果だけを残し、materialなsource provenanceを失わない。
- Selective Disclosureされた情報を完全情報として扱わない。
- historical / local candidateのPASSをactual repositoryのPASSへ継承しない。

## Required fixtures

少なくとも次を含む。

1. TEI Applicationはreadyだが依存Databaseがread-only。
2. Migration Proposalは存在するが未採用。
3. Releaseは存在するがEnvironmentへ未Binding。
4. Observation取得自体ができず、状態がUnknown。
5. 複数ObservationがConflictする。
6. 同じCapabilityをTEIとSaaSが提供する。
7. Selective DisclosureによりProvider内部detailの一部だけが共有される。
8. 過去Decision時のprovider snapshot / adapter revisionをexact referenceで辿る。
9. Provider statusは良好だが、DecisionまたはAuthorizationが存在しない。
10. adapter更新後も過去Observationを当時のbasisで再構成する。

## Deliverables

- Provider-neutral Capability Observation contract
- schemaまたは同等の機械可読境界
- Provider adapter interface / mapping rule
- positive / negative fixtures
- historical reconstruction fixture
- selective disclosure fixture
- TEI以外を含むprovider-neutral conformance
- Evidence claimをactual repositoryの結果へ限定する検査

## Blocked by

**ISSUE-000022** — actual repository baseline materialization。

`contracts/`、fixture、test tool等の配置先とactual gateが成立するまでは、historical candidateをコピーして完了扱いしない。

## Completion criteria

- ADR-0019の主要な非同一性がfixtureで検査できる。
- TEI固有schemaなしでRequired fixturesを表現できる。
- Unknown / Conflict / Selective Disclosureを保持できる。
- Provider ObservationからDecisionを自動生成しないことを検査できる。
- provider-specific exact evidenceへ必要時に戻れる。
- TEI以外の少なくとも一つのProvider例で同じcontractを検証できる。
- actual repository上で再実行可能なEvidenceだけをPASSとして記録する。
- 成果文書は自然な日本語を最優先に全文を再ドラフトし、意味監査を行う。

## Reopen conditions

Resolved後、複数Providerでcontractが意味差を失う、adapterがProvider lifecycleを再実装する、historical reconstructionが成立しない等の問題が再現した場合は、ADR-0019の再検討を提案する。

## Natural Japanese review

ADR-0019とISSUE-000022のEvidence境界へ戻して内容を確定した後、意味、強度、留保、Blocked条件を変えず、自然な日本語となることを最重要視して全文を再ドラフトした。その後、最終意味監査を実施済み。
