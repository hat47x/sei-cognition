# ISSUE-000018: Authorization EvidenceとDecision Memoryの接続境界を定める

Status: **Open**  
Priority: **3**  
Related ADRs: **ADR-0004, ADR-0010, ADR-0011, ADR-0014**  
Updated: 2026-08-31

## Goal

TEIや他のCapability Providerが行う認証・認可評価を、SOZAのEvidence、Responsibility、Decision Memoryからどのように参照するかを定める。

SOZAがAuthorization engineそのものを所有せず、かつ「誰が何をどの権限で実行したのか」を後から検証できる境界を作る。

## Background

TEI設計系列では、認証と認可を固定のUser / Role tableへ押し込まず、標準Capability入口と差し替え可能Providerへ分離する方向が採用されている。

また認可は、少なくとも次の二段階へ分ける考えがある。

```text
External Entry Authorization
    !=
Resource / Subject Authorization
```

SOZA側では、Decision、Responsibility、Authority、Executionを分離している。

```text
Decision != Responsibility != Authorization != Execution
```

したがって、Provider側で認可が成功した事実をSOZA DecisionやResponsibilityへ直接埋め込むべきではない。

## Questions

1. Authorization evaluation結果はObservation、Evidence、Assuranceのどこから参照するのが適切か。
2. evaluation request / resultのexact historical inputをどの粒度で残すべきか。
3. Provider固有policyやRBAC schemaをSOZAへ漏らさず、後から判断を検証するには何が必要か。
4. Entry AuthorizationとResource Authorizationを別Evidenceとして残す必要があるか。
5. Authorizationが後日失効・撤回された場合、過去Executionの意味をどう保持するか。
6. 「当時は許可された」と「現在も許可される」をどう分離するか。
7. Providerから返る`allowed / denied / unknown / not_evaluated`等の状態をUniversal vocabularyへ固定する必要があるか。
8. 認証Providerのlegacy-specific情報をSelective Disclosureしながら、検証可能性をどう保つか。

## Constraints

- Authorization結果からDecisionを推定しない。
- ResponsibilityからAuthorizationを推定しない。
- actor / provider kindからAuthorityを推定しない。
- password hash、credential、secretをSOZA Artifactへ保存しない。
- TEI固有RBAC / Principal schemaをSOZA Coreへコピーしない。
- Providerの単なるsuccess acknowledgementを十分なEvidenceとみなさない。
- historical authorizationとcurrent authorizationをlatest-winsで上書きしない。

## Required scenarios

1. Decisionは存在するがAuthorizationが拒否される。
2. AuthorizationはあるがDecisionが存在しないため実行しない。
3. Entryは許可されるが対象Resourceでは拒否される。
4. 当時許可されたExecutionを後日監査する。
5. Authorization policy revision後も過去評価を再構成する。
6. external SaaSとTEIで異なる認可方式を同じSOZA Decisionから利用する。
7. legacy password providerで認証し、別ProviderでResource Authorizationする。
8. 認可評価が一時的に利用不能で、`unknown`を`denied`へ潰さない。

## Deliverables

- Authorization Evidence boundary
- SOZA Decision / Responsibilityとの参照関係
- historical reconstruction rule
- selective disclosure rule
- Provider-neutral acceptance fixtures
- ADR候補

## Source

`plan/kj/2026-08-31_TEI設計系列_ラウンドKJ統合.md` のG04を起点とする。

## Natural Japanese review

Issue作成後に自然な日本語の全文ドラフト工程を実施済み。Decision確定時にも再監査する。
