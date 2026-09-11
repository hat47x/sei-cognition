# SOZA Capability Observation Contract v1alpha1

contract_id: `sei.capability-observation`  
version: `v1alpha1`  
状態: **Current pre-stable Design Baseline / Scoped Executable Evidence**  
更新日: 2026-08-31

## 1. 目的

このContractは、Capabilityやその実現候補について現在観測されている情報を、特定Providerの内部Schemaへ依存せず、DecisionやMatchingから独立して交換するための意味契約を定めます。

主な対象はREQ-0002、REQ-0007、REQ-0013、REQ-0016、REQ-0021、REQ-0022です。

## 2. 基本境界

次を同一視してはなりません。

```text
Capability Definition
  != Capability Observation
  != Matching
  != Choice Decision
  != Provider Selection
  != Authority
  != Execution
```

Capability Observationが存在することから、候補採用や実行可能性を自動確定してはなりません。

## 3. Observationの対象

Capability Observationは、少なくとも何を観測した情報かを識別できなければなりません。

対象は、文脈に応じて次のいずれかになり得ます。

- Capability Definition
- Providerが提示する実現候補
- Provider上のspecific offering / endpoint / application等
- 上記の組合せ

本Contractは、すべてを一つのUniversal `CapabilityRealization`型へ正規化することを要求しません。

Provider-specific targetを参照する場合は、Provider内部の完全SchemaをSOZAへ複製するのではなく、必要なReferenceと解釈可能なcontextを保持します。

## 4. Observationの最小意味

Observationは、必要に応じて次を保持できます。

- observation identity
- target Capability reference
- Provider reference
- Provider-specific target reference
- observed time / validity context
- observed condition
- source / evidence / provenance
- Unknown / Conflict / Withheld context
- mapping / adapter provenance

すべてのfieldを常時必須にはしません。Profile / Policyが案件文脈に応じて必要性を決められます。

## 5. observed condition

observed conditionには、たとえば次の情報が含まれ得ます。

- availability
- observed cost
- observed latency
- current contractual condition
- operational constraint
- audit characteristic
- reversibility characteristic
- capacity / limit

この一覧をUniversal closed taxonomyにはしません。

domain-specific propertyはextensionまたはProfileで表現できます。

## 6. Unknown / Conflict / Withheld

観測値がない場合を`false`や`unavailable`へ変換してはなりません。

```text
not observed != unavailable
Unknown != incompatible
Conflict != latest-wins
Withheld != false
```

複数Sourceが異なる状態を報告する場合、必要に応じてConflictを保持し、最新値だけで自動上書きしません。

情報の存在は分かるが開示されない場合、UnknownとWithheld Contextを区別できる余地を維持します。

## 7. Provider-neutrality

Provider kindやSOZAとの関係の近さから、Observationの信頼度、優先順位、Authority、採用可否を推定してはなりません。

human、AI service、SaaS、外部組織、TEI、custom codeは、異質なProvider候補になり得ます。

TEIのApplication / Database / Release / Deployment等の内部概念を、そのままSOZA Universal Coreのfieldへ昇格させません。

## 8. Adapter / Mapping provenance

Provider internal stateからCapability Observationへの変換は、単なるformat変換とは限りません。

```text
Provider state != Capability interpretation != Decision
```

mappingが次を含む場合、その解釈境界を後から追跡できるようにします。

- field mapping
- unit conversion
- category normalization
- status interpretation
- aggregation
- derived condition

重要なDecision basisとして利用されたObservationについては、必要な範囲で当時のmapping / adapter versionまたはexact referenceを特定できることを推奨します。

Provider-specific input schemaはAdapter側に留め、本ContractのUniversal field setへ無条件にコピーしません。

## 9. Matchingとの境界

Capability Observationは、候補を比較・推薦するMatchingそのものではありません。

Matchingは複数ObservationやConstraint等を利用し、supporting basis、conflicting basis、missing information、explanation等を示せます。

本ContractはUniversal suitability score、ranking algorithm、自動best-candidate selectionを要求しません。

## 10. Decisionとの境界

Capabilityを採用することはDecision Memoryの境界です。

Observationに`available=true`等が存在しても、採用DecisionやAuthorityを意味しません。

Choice DecisionがObservationをbasisとして利用する場合、historical reconstructionに必要なReferenceを保持します。

## 11. 不変条件

実装は少なくとも次を破ってはなりません。

1. Provider internal stateをCapability Definitionそのものとして扱わない。
2. Observation不足をnegative factへ変換しない。
3. Provider kindから優先・信頼・Authorityを推定しない。
4. ObservationをMatching / Decisionへ自動昇格しない。
5. TEI等のProvider固有SchemaをUniversal field setへ無条件にコピーしない。
6. 重要なmapping provenanceを失ったまま、解釈済みObservationをraw factとして扱わない。

## 12. interoperability minimum

異なる実装間でCapability Observationを交換する場合、受信側は少なくとも次を復元できなければなりません。

- Observation identity
- 観測対象
- 観測内容
- 観測時点または時間文脈
- provenanceが存在する場合のReference
- Unknown / Conflict / Withheld等が存在する場合の意味
- mapping provenanceが存在する場合のReference
- 使用Contract version

unknown extensionを理解できない場合、それを無視した結果、既知fieldだけで意味が確定したかのように扱ってはなりません。

## 13. Evidence境界

本Contract DefinitionはDesign Evidenceです。

current repositoryでは、JSON Schema、Capability Observation F1〜F7、first semantic runtime、および異なるinput shapeを持つsynthetic Provider A / B Adapterについて、対象を限定したExecutable Evidenceがあります。

synthetic Adapterでは、少なくとも次を確認しています。

- status interpretation / unit conversion
- missing readiness / latencyを`false`や`0`へ捏造しない
- mapping provenance / source state referenceの保持
- Provider-specific target referenceの保持
- Provider固有fieldをCapability Observation schemaへ漏らさない
- Adapter outputからRecommendation / Decision / Authority / Executionを生成しない

一方、次は未検証です。

- production TEI / SaaS / human Provider adapter
- Provider廃止・交換を伴う長期運用
- actual external interoperability
- Release Evidence
- Operational Evidence
- Adoption / Outcome Evidence

```text
synthetic Adapter PASS
  != production Provider interoperability
  != Capability Choice decided
```

ISSUE-000024とISSUE-000036はcurrent fixture / synthetic Adapter sliceの設計・実体化を完了しており、production Provider integrationを意味しません。

## 14. 関連

- REQ-0002, REQ-0007, REQ-0013, REQ-0016, REQ-0021, REQ-0022
- ADR-0012, ADR-0013, ADR-0014, ADR-0019, ADR-0021, ADR-0024
- `contracts/decision-memory/SOZA_DECISION_MEMORY_v1alpha1.md`
- `contracts/semantic-reference/SOZA_SEMANTIC_REFERENCE_v1alpha1.md`

## 15. Natural Japanese review

Capability、Provider、Observation、Matching、Decision、mapping provenanceの規範境界を維持したまま、F1〜F7、first semantic runtime、ADR-0024 / synthetic Provider AdapterへEvidence節を再照合しました。その後、意味、規範強度、留保、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
