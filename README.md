# SOZA Phase 1 — M48 Product Rebaseline Integration Candidate v6

更新日: 2026-08-31  
状態: **initial repository baseline candidate / release not claimed**

このbundleは、Phase 0で確定したProduct Value、Product Requirements、Acceptance Scenarios、ADRを、M47のCognitive Method境界を壊さない形でM48の実装候補へ降ろしたものです。

このtreeは`hat47x/soza`を新規repositoryとして開始するための初期基線です。**M48 release、旧M47実装との回帰互換、Product Vision coverage上昇、operational evidenceを主張するものではありません。**

## 1. 現在地

- ADR-0001〜ADR-0012: Accepted
- ISSUE-000001〜ISSUE-000008: Resolved
- ISSUE-000009: Blocked — Representation Contractのlocal stabilization完了、historical M47 digest mapping / stable JCS verifier待ち
- ISSUE-000010: Resolved — M49 Decision Memory core acceptance boundary
- ISSUE-000011: Resolved — M49 Decision reference role semantics
- ISSUE-000012: Resolved — M49 progressive decision explicitness planning
- ISSUE-000013: Resolved — M50 Capability Choice acceptance boundary
- ISSUE-000014: Open — Capability Realization / Offering boundary investigation
- M47: verified historical/reference baselineとして尊重
- M48: repository initial baseline candidateとしてGo実装・contract・conformanceを用意

`hat47x/soza`は新規・空repositoryとして利用可能になったため、このtreeを初期基線とします。`tei-platform`への代替統合は行いません。

## 2. 最初に読む順序

1. `product/value/SOZA_PRODUCT_VALUE.md`
2. `product/vision/SOZA_PRODUCT_VISION.md`
3. `product/principles/SOZA_PRODUCT_PRINCIPLES.md`
4. `requirements/PRODUCT_REQUIREMENTS_v1.md`
5. `requirements/ACCEPTANCE_SCENARIOS_v1.md`
6. `architecture/CORE_BOUNDARY_REVIEW_v1.md`
7. `architecture/M47_M48_PRESSURE_TEST_v2.md`
8. `architecture/M48_FEASIBILITY_TO_REBASELINE_DELTA_v1.md`
9. `contracts/INQUIRY_EPISTEMIC_ARTIFACTS_v1.md`
10. `contracts/M47_M48_COMPATIBILITY_PORT_v1.md`
11. `contracts/schemas/v1alpha1/SOZA_SEMANTIC_INTERCHANGE_v1alpha1.json`
12. `plan/rebaseline/PHASE1_IMPLEMENTATION_CANDIDATE_REPORT.md`
13. `architecture/BINDING_VERIFICATION_OUTCOME_v1.md`
14. `contracts/JCS_SHA256_REPRESENTATION_PROFILE_candidate.md`
15. `contracts/RAW_BYTES_SHA256_REPRESENTATION_PROFILE_candidate.md`
16. `plan/rebaseline/PHASE1_REPRESENTATION_CONTRACT_STABILIZATION_REPORT.md`
17. `requirements/M49_DECISION_MEMORY_ACCEPTANCE_v1.md`
18. `architecture/M49_DECISION_MEMORY_BOUNDARY_v1.md`
19. `architecture/M49_DECISION_REFERENCE_ROLES_v1.md`
20. `architecture/M49_PROGRESSIVE_DECISION_EXPLICITNESS_v1.md`
21. `plan/rebaseline/M49_ACCEPTANCE_PLANNING_CLOSURE_REPORT.md`
22. `plan/rebaseline/M49_NEXT_SLICE_ACCEPTANCE_REPORT.md`
23. `requirements/M50_CAPABILITY_CHOICE_ACCEPTANCE_v1.md`
24. `architecture/M50_CAPABILITY_CHOICE_BOUNDARY_v1.md`
25. `architecture/M50_HISTORICAL_CAPABILITY_EVIDENCE_REVIEW_v1.md`
26. `architecture/M50_CAPABILITY_REALIZATION_OPTIONS_v1.md`
27. `plan/rebaseline/M50_CAPABILITY_CHOICE_PLANNING_CLOSURE_REPORT.md`
28. `plan/registry.yaml`

## 3. Phase 1で実装候補へ降ろした境界

### Artifact reference

```text
LogicalArtifactRef
        +
必要な境界だけ ExactArtifactBinding
        +
SemanticLineageRecord
```

logical identity、exact content binding、semantic lineage、storage revisionを一つの`version`へ押し込みません。

### Epistemics

- Question
- Observation
- Hypothesis
- Unknown
- Conflict
- EvidenceUse
- AssuranceRecord
- EpistemicSeam
- Derivation
- Provenance

`Unknown != No`、`Conflict != latest-wins`、`Observation != EvidenceUse != Assurance != Truth`を維持します。

### Subject / Responsibility

Global Principal ontologyを作らず、`BoundedSubjectRef { scope_ref, subject_id }`を基本参照とします。さらに`ResponsibilityStatement`で「その主体が何を担ったか」を任意Artifact文脈へ結びます。ResponsibilityからAuthorization / Credential / Trust / actor hierarchyを推定しません。

### Progressive Semantic Explicitness

Universal risk scoreや固定LevelをCoreへ追加しません。どの意味境界を必須にするかはProfile / Policy側で扱います。

### Federation / Persistence

Federationはoptional Profile、Persistenceはstorage-neutral contractとし、workflow engineやDB方式をSOZA Coreへ固定しません。

## 4. M47との接続

M47のMethod Definition / Realization / Method Application RecordをM48側で再定義しません。

M48 Derivationは、必要な場合にM47 Method Applicationを`ExactArtifactBinding`で参照します。さらに`runtime/go/integration/m47bridge`にCompatibility Portを置き、actual M47のGo structを推測して複製しません。今後、検証済みの歴史的M47実装sourceが回収できた場合は、既存M47型を包む薄いadapterで接続し、M47境界を再定義しないことを基本とします。

## 5. 旧138 Requirement

旧Requirement Registryの138件は履歴証拠として保持します。

- `requirements/PRODUCT_REQUIREMENT_EVIDENCE_BRIDGE_v1.md`
- `requirements/LEGACY_MIXED_EXTRACT_KERNELS_v1.md`

旧VERIFIED状態を新Product Requirementへ自動継承しません。

## 6. ローカル検査

全検査は次の一入口で再実行できます。

```bash
python3 tools/run_phase1_local_gate.py
```

内訳:

```bash
python3 plan/scripts/check_plan_ids.py
go test ./...
python3 tools/run_semantic_schema_conformance.py
python3 tools/run_exact_binding_conformance.py
node tools/run_jcs_profile_probe.mjs
python3 tools/run_representation_contract_conformance.py
python3 tools/test_preflight_actual_repo.py
python3 tools/check_product_candidate_evidence.py
python3 tools/check_m49_acceptance_design.py
python3 tools/check_m50_capability_choice_planning.py
python3 tools/run_m48_rebaseline_conformance.py
python3 tools/check_phase1_candidate.py
```

これらのPASSは、このrepository baseline内部の実装候補と構造が整合していることだけを示します。SOZA release evidenceではありません。

## 7. Repository bootstrap後の扱い

`hat47x/soza`は新規repositoryとしてこの基線から開始します。旧Semantic Platform時代のM47実装sourceはこのrepositoryにpre-existing codeとして存在しないため、**存在しない回帰試験をPASS扱いしません**。

今後の統合作業では次を区別します。

1. このrepository内で再現できるM48 local conformance
2. Library等に残るM47 historical contract / report
3. 将来回収できた場合のM47 actual source compatibility
4. release / governance / Self Build evidence
5. operational evidence

`ISSUE-000009`はrepository不在ではなく、historical M47 digest mappingとstable JCS Go verifier選定・実証が未完了であるためBlockedを維持します。

M49 Decision MemoryとM50 Capability ChoiceはAcceptance Planningまで完了していますが、production実装は別Issueで明示的に開始します。

## 8. Representation Contract hardening

ADR-0008 / ADR-0009により、Exact Bindingとその検証手段・検証結果を分離しています。

```text
ExactArtifactBinding
  != Representation Contract implementation
  != Verification Outcome
```

通常JSONのstable候補はRFC 8785 JCS + SHA-256、non-JSON / large binaryの候補はraw bytes + SHA-256です。custom canonical JSON v1alpha1はcross-language実験証拠としてのみ保持します。

`verified / failed / not_verified`を区別し、Verifier不在やpayload不在をdigest mismatchと同一視しません。

## 9. Product Requirement evidence closure

M48 local candidateのevidence所在は次で固定します。

```text
Product Requirements 18
  direct       8
  partial      8
  design-only  2

NFR 10
  direct       3
  partial      5
  design-only  2

operational evidence claims: 0
```

この分類は完成率ではありません。

## 10. 次段planning

- M49 Decision Memory: Acceptance Planning 12 fixture / production implementation未開始
- M50 Capability Choice: Acceptance Planning 12 fixture / production implementation未開始
- ISSUE-000014: Capability Realization / OfferingをUniversal Coreへ追加せずOpenで調査継続

実装順序をProduct ontologyにはしません。
