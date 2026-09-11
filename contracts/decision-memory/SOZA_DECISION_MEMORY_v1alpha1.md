# SOZA Decision Memory Contract v1alpha1

contract_id: `sei.decision-memory`  
version: `v1alpha1`  
状態: **Current pre-stable Design Baseline / Scoped Executable Evidence**  
更新日: 2026-08-31

## 1. 目的

このContractは、Decisionについて「何を決めたか」だけでなく、**その時点で何を根拠にし、何が未解決で、誰または何がどの責任を担い、後から何が変わったか**を再構成するための意味契約を定めます。

主な対象はREQ-0005、REQ-0006、REQ-0008、REQ-0014、REQ-0015、REQ-0017です。

## 2. 基本境界

次を同一視してはなりません。

```text
Recommendation
  != Decision
  != Authority / Authorization
  != Action Intent
  != Provider Execution
  != Execution Receipt
  != Business Outcome
```

Decisionが存在することから、後続段階の成立を自動推定してはなりません。

## 3. Decisionの最小意味

Decisionは、少なくとも次を後から識別できる必要があります。

- Decision自体のlogical identity
- 何を判断したか
- 判断時点のIntent / Goal / Constraint等の文脈
- 明示的に利用したbasis
- 必要に応じたRationale
- 判断時点で残っていたUnknown / Conflict / Question等
- contextual ResponsibilityへのReference
- 後続DecisionとのSemantic Lineage

すべての低影響Decisionに最大のfield setを強制しません。どこまで明示するかはProfile / Policyで決められます。

## 4. Basis

Basisは、Decision時に明示的に考慮されたArtifactまたは外部Referenceを指します。

候補には次が含まれ得ます。

- Observation
- Hypothesis / Interpretation
- Constraint
- Recommendation
- EvidenceUse
- Assurance
- Cognitive Method Application
- Capability Observation / Matching result
- external rule / contract reference

可変Artifactを重要なbasisとして利用する場合、historical reconstructionに必要な範囲でExact Artifact Bindingを利用できなければなりません。

Basisを後から現在版へ黙って差し替えてはなりません。

## 5. Rationale

Rationaleは、人間やAIが後からDecisionを読み直すために外在化された説明です。

```text
Rationale != private chain-of-thought
```

Rationaleだけを唯一のbasis rootにしません。重要な可変事実・資料・Recommendation等は、可能な範囲で明示Referenceとして保持します。

private chain-of-thoughtの保存・復元をContract適合条件にしてはなりません。

## 6. Unresolved state

Decisionは認識上の完成宣言ではありません。

```text
Decision creation != uncertainty resolution
```

Decision時点でUnknown、Conflict、Question、missing evidence等が残っている場合、それらをDecision作成に伴って自動的にresolvedへ変更してはなりません。

必要に応じて、reopen condition、review trigger、追加調査条件等を明示ArtifactまたはReferenceとして残せます。

## 7. Recommendationとの関係

RecommendationはDecisionの候補・提案です。

- RecommendationなしでDecisionしてもよい。
- RecommendationがあってもDecisionしなくてよい。
- 複数Recommendationを検討してもよい。
- AIがRecommendationを生成したことからDecision authorityを推定してはならない。

Recommendationを採用・不採用した経路を重要とする場合、その関係を後から追跡可能にします。

## 8. Responsibility / Authority

Decision maker responsibilityはcontextual Responsibilityとして表します。

```text
Responsibility != Authorization
```

actor kind、role名、Responsibilityの存在だけからAuthorityを推定してはなりません。

Authorityを確認する必要がある場合は、外部Authority ProviderやAuthority evidenceへのReferenceを別境界として扱います。

## 9. Revision / Supersession

後のObservationや条件変更によりD1からD2へ判断が変わった場合、D1を削除せず、D1のbasisを後知恵で書き換えてはなりません。

Semantic Lineageを利用し、少なくとも次を辿れる必要があります。

- D1が何をbasisにしていたか
- 新しいObservation等がいつ得られたか
- D2が何をbasisにしたか
- D2がD1を`revises` / `supersedes`等した関係

Decision固有のUniversal workflow status machineを要求しません。

## 10. Progressive Explicitness

Profile / Policyは、案件条件に応じて次を要求できます。

- explicit Decision artifact
- exact-bound basis
- unresolved refs
- Rationale
- Responsibility
- Authority evidence reference
- review / reopen condition

これらを単一risk scoreや固定levelへ圧縮しません。

## 11. 不変条件

実装は少なくとも次を破ってはなりません。

1. RecommendationをDecisionへ自動昇格しない。
2. DecisionをAuthorization / Executionへ自動昇格しない。
3. Decision作成時にUnknown / Conflictを自動解消しない。
4. 過去Decisionのbasisを現在版へ黙って差し替えない。
5. Rationaleにprivate chain-of-thoughtを要求しない。
6. ResponsibilityからAuthorityを推定しない。
7. 後続Decisionで過去Decisionを削除しない。

## 12. interoperability minimum

異なる実装間でDecision Memoryを交換する場合、受信側は少なくとも次を復元できなければなりません。

- Decision identity
- decision content / subject
- context refs
- basis refs
- unresolved refsが存在する場合の識別
- Responsibility refsが存在する場合の識別
- semantic lineage
- 使用Contract version

optional情報が欠けていることを否定事実へ変換してはなりません。

## 13. Evidence境界

本Contract DefinitionはDesign Evidenceです。

current repositoryでは、machine-readable schema、Recommendation without Decision、Decision with unresolved state、Decision recordへのAuthority埋め込み拒否、exact-bound basis整合、およびfirst semantic runtimeによるread / validate / reconstructについて、対象を限定したExecutable Evidenceがあります。

一方、次は未検証です。

- production組織での実Decision lifecycle
- Authority Provider / Authorizationとのend-to-end連携
- Decision→Action Intent→Execution→Outcomeの運用責任線
- 長期間のDecision revision / reopen運用
- Release Evidence
- Operational Evidence
- Adoption / Outcome Evidence

```text
Decision fixture PASS
  != decision valid
  != authorization granted
  != production governance verified
```

## 14. 関連

- REQ-0005, REQ-0006, REQ-0008, REQ-0014, REQ-0015, REQ-0017
- ADR-0010, ADR-0011, ADR-0015, ADR-0016, ADR-0021, ADR-0022
- `contracts/semantic-reference/SOZA_SEMANTIC_REFERENCE_v1alpha1.md`

## 15. Natural Japanese review

Decision、basis、Rationale、未解決状態、Responsibility、Authority、revisionの規範境界を維持したまま、current schema / fixtureとfirst semantic runtimeへEvidence節を再照合しました。その後、意味、留保、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
