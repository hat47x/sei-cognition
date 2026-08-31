# ISSUE-000035: Provider AdapterからCapability Observationへの境界を定義する

Status: **Resolved**  
Priority: **1**  
Related ADRs: **ADR-0014, ADR-0019, ADR-0021, ADR-0022, ADR-0024**  
Updated: 2026-08-31

## Goal

first semantic runtime sliceの次段として、Provider固有stateをcurrent Capability Observationへ変換するProvider Adapter / Mapping境界を定める。

TEI固有Schemaや一つのSaaS API形状を先に採用せず、Provider Independence、historical reconstruction、Unknown preservationを満たす最小vertical sliceを設計する。

## Questions

1. Provider Adapterは何を所有し、何を所有しないか。
2. Provider-specific inputをUniversal schemaへ正規化すべきか。
3. Adapter outputはどのContractで検証するか。
4. field mapping、unit conversion、status interpretation等のprovenanceをどう残すか。
5. mapping version変更後に過去Decision basisをどう再構成するか。
6. Provider stateが欠落・取得不能・非開示のとき、negative factへの誤変換をどう防ぐか。
7. common comparison facetとProvider-specific informationをどう分けるか。
8. AdapterがMatching / Decision / Authority / Executionへ越境することをどう防ぐか。
9. 最初のExecutable fixtureに実TEIを使うべきか、synthetic Providerで境界を先に検証すべきか。
10. Adapter implementationとsemantic authorityをどう分けるか。

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

本IssueのclosureはDesign Evidenceである。

```text
ADR Accepted
  != Provider Adapter Executable Evidence
  != TEI integration
  != Provider production interoperability
```

Executable EvidenceはISSUE-000036でactual runtime / fixture / CIから取得する。

## Natural Japanese review

current Capability Observation、runtime、Provider Independenceの境界を照合して設計論点を確定した後、実装を先取りせず、意味、規範強度、Evidence境界を変えない範囲で自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
