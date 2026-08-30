# ISSUE-000030: current SOZA Contract baselineをactual repositoryへ実体化する

Status: **Open**  
Priority: **2**  
Related ADRs: **ADR-0008, ADR-0009, ADR-0019, ADR-0021**  
Updated: 2026-08-31

## Goal

ADR-0021に従い、current Architectureで相互運用・historical reconstruction・verificationのために必要と判断された境界を、human-readable Contract Definitionと必要なmachine-readable schema / Representation Profileへ落とす。

historical Contract候補を一括復元せず、current REQ / ADR / Architectureで必要なContractだけを実体化する。

## Initial candidate contract families

Architecture baseline完成後、少なくとも次を再評価する。

1. Semantic Interchange
2. Logical Reference / Exact Artifact Binding
3. Revision / Semantic Lineage
4. Decision Memory interchange
5. Capability Observation interchange
6. Selective Disclosure / Federation exchange
7. Representation Profile

この一覧は採用済みContract一覧ではない。current Architectureから必要性を再確認する。

## Historical inputs

- `contracts/INQUIRY_EPISTEMIC_ARTIFACTS_v1.md`
- `contracts/M47_M48_COMPATIBILITY_PORT_v1.md`
- `contracts/SEMANTIC_PORTABLE_BUNDLE_v1.md`
- `contracts/PORTABLE_EXACT_BINDING_REPRESENTATION_v1alpha1.md`
- `contracts/JCS_SHA256_REPRESENTATION_PROFILE_candidate.md`
- `contracts/RAW_BYTES_SHA256_REPRESENTATION_PROFILE_candidate.md`
- historical semantic interchange schema candidate

## Constraints

- ContractをArchitecture説明の置き換えにしない。
- schemaにしか存在しないsemantic requirementを作らない。
- JSON / JCS / SHA-256等をsemantic Coreへ自動昇格させない。
- historical field名、enum、package、schema versionを無検査で継承しない。
- Contract fileが存在するだけでimplementation conformanceを主張しない。
- breaking semantic changeとrepresentation-only changeを分ける。
- Contract Definition確定後、自然な日本語全文再ドラフトと最終意味監査を行う。

## Acceptance

### Semantic / Design Acceptance

- [ ] current Contractの必要性がREQ / ADR / Architectureから説明できる。
- [ ] contract_id / versionが明示されている。
- [ ] semantic ContractとRepresentation Profileを分けている。
- [ ] Markdown Contract Definitionとschemaの権威関係がADR-0021と一致する。
- [ ] historical Contractとの対応を追跡できる。
- [ ] Design / Executable Evidenceを混同していない。
- [ ] 自然な日本語全文再ドラフトと最終意味監査が完了している。

### Executable Acceptance

- [ ] machine-readable schema / validatorが必要なContractについてactual conformance checkを実行できる。
- [ ] positive / negative fixtureが存在する。
- [ ] current Contractに対するactual PASS / expected FAILを再現できる。

DesignとExecutableは別sliceへ分けてもよい。

## Dependencies

- ADR-0021
- ISSUE-000029
- ISSUE-000009
- ISSUE-000024

## Natural Japanese review

Contract候補をまだ確定事項として扱わないよう留保を残し、semantic ContractとRepresentation Profileの責務を分離した後、自然な日本語となることを最重要視して全文を再ドラフトした。実体化時に最終意味監査を再実施する。
