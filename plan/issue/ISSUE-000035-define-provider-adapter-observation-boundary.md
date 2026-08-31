# ISSUE-000035: Provider AdapterからCapability Observationへの境界を定義する

Status: **Resolved**  
Priority: **1**  
Related ADRs: **ADR-0014, ADR-0019, ADR-0021, ADR-0022, ADR-0024**  
Updated: 2026-08-31

## Goal

first semantic runtime sliceの次段として、Provider固有stateをcurrent Capability Observationへ変換するProvider Adapter / Mapping境界を定める。

TEI固有Schemaや一つのSaaS API形状を先に採用せず、Provider Independence、historical reconstruction、Unknown preservationを満たす最小vertical sliceを設計する。

## Resolution

ADR-0024で次をAcceptedした。

- Provider AdapterはProvider-owned stateからCapability Observationへの一方向の観測解釈境界とする。
- Provider-specific inputのUniversal `ProviderState` schemaを作らない。
- Adapter outputはcurrent Capability Observation Contractで検証する。
- 解釈を伴うmappingにはmapping provenanceを残す。
- Decision basisとして重要なmappingはProfile / Policyによりexact historical bindingを要求できる。
- source state全量をCoreへ複製せず、source state reference / provenance / exact binding等から必要な戻り道を残す。
- missing / not observed / withheldをnegative factへ変換しない。
- common facetをUniversal closed taxonomyへしない。
- AdapterはMatching / Recommendation / Decision / Authority / Executionを所有しない。
- Go interface等の実装構造をsemantic authorityにしない。
- 最初のExecutable sliceは異なるinput schemaを持つsynthetic Providerで検証する。

## Acceptance

- [x] Provider Adapterの意味責務を定義した。
- [x] Provider-specific inputとUniversal semanticsの境界を定義した。
- [x] mapping provenanceの扱いを定義した。
- [x] historical reconstructionに必要なmapping version境界を定義した。
- [x] Unknown / missing / withheldの誤変換防止を定義した。
- [x] Matching / Decision / Authority / Executionとの境界を定義した。
- [x] synthetic Providerを先行させる理由を定義した。
- [x] 実装責務をISSUE-000036へ分離した。
- [x] 自然な日本語全文再ドラフトと最終意味監査を実施した。

## Evidence boundary

本Issue自身のclosureはDesign Evidenceである。

```text
ADR Accepted
  != Provider Adapter Executable Evidence
```

その後、ISSUE-000036でsynthetic Provider A / Bを実装し、mapping provenance、source state reference、Unknown preservation、Provider固有field leakage防止、Capability Observation runtime validationをactual CIで確認した。

したがってcurrent repositoryにはProvider Adapterのscoped Executable Evidenceも存在するが、それはISSUE-000036のEvidenceであり、本IssueのDesign closureを遡ってImplementation Issueへ変えるものではない。

```text
synthetic Adapter PASS
  != TEI production integration
  != production Provider interoperability
```

## Follow-up

- ISSUE-000036 — synthetic Provider Adapter（Resolved）
- production Provider adapterは対象Provider / Acceptanceが具体化した時点で独立Issueとして扱う。

## Natural Japanese review

current Capability Observation、ADR-0024、runtime、ISSUE-000036のsynthetic Adapter Evidenceへ戻って設計境界を照合した。その後、本Issue自身のDesign Evidenceと後続Executable Evidenceを区別し、意味、規範強度、Evidence境界を変えない範囲で自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。
