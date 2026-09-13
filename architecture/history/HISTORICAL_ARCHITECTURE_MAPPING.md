# Historical Architecture Mapping

更新日: 2026-08-31  
状態: **Historical Design Provenance Mapping**

## 1. この文書の役割

この文書は、Phase 1 candidateで作成されたM48 / M49 / M50周辺のArchitecture文書を、current `SEI_REFERENCE_ARCHITECTURE.md`へどのように統合・分離・保留したかを記録します。

historical文書をcurrent正本へrenameしたものではありません。

current Architectureは、Product Value、REQ-0001〜REQ-0022、SCN-0001〜SCN-0017、ADR-0001〜ADR-0024から再構成しています。

## 2. 継承の原則

historical candidateから再利用するのは、主として次です。

- 意味境界
- 反例
- Coreへ入れない理由
- historical reconstruction上の注意点
- Profile / Provider / Projection等への配置理由
- Acceptance上の論点

次は自動継承しません。

- M48 / M49 / M50等のMilestone identity
- old field set / schema shape / enum
- Go package layout
- historical local PASS / planning PASS
- current actual repositoryに存在しないruntime evidence
- historical時点のJCS / SHA-256 / JSON等の実装選択そのもの

currentで同じ技術を採用している場合でも、historical choiceを自動継承したのではなく、current Product Value / Requirement / ADRへ戻って改めて採否を決めたものとして扱います。

## 3. 主要historical Architecture mapping

| Historical document | current disposition | 主なcurrent Architecture |
|---|---|---|
| `CORE_BOUNDARY_REVIEW_v1.md` | **Integrated** | Architecture原則、Durable Semantic Core、Profile / Policy、固定しないもの |
| `CLAIM_INTERPRETATION_BOUNDARY_v1.md` | **Integrated as semantic boundary** | Inquiry / Epistemics、Cognitive Method。Universal Claim型はcurrent Coreへ採用しない |
| `REVISION_SUPERSESSION_SEMANTICS_v1.md` | **Integrated** | Decision revision、Semantic Revision、Persistence |
| `SEMANTIC_PERSISTENCE_CONTRACT_v1.md` | **Split and rebaselined** | Architecture意味核はReference / Persistenceへ統合。portableな一部境界はcurrent Contract familyへ実体化 |
| `EXACT_BINDING_VERIFICATION_BOUNDARY_v1.md` | **Integrated** | Logical Reference / Exact Historical Binding。representationはcurrent Representation Profileへ分離 |
| `BINDING_VERIFICATION_OUTCOME_v1.md` | **Integrated** | `not_verified != failed`、Evidence boundary |
| `PROGRESSIVE_SEMANTIC_EXPLICITNESS_v1.md` | **Integrated** | Profile / Policy。固定explicitness level / universal risk scoreは採用しない |
| `BOUNDED_SUBJECT_RESPONSIBILITY_v1.md` | **Integrated** | Responsibility / Authority。Global Principal ontologyは採用しない |
| `BOUNDED_FEDERATION_PROFILE_v1.md` | **Integrated as optional Profile** | Federation / Selective Disclosure。transport / cryptoはProvider-owned |
| `M49_DECISION_MEMORY_BOUNDARY_v1.md` | **Integrated without milestone identity** | Decision Memory |
| `M49_DECISION_REFERENCE_ROLES_v1.md` | **Integrated as role separation** | Basis / Rationale、Reference。current portable subsetはDecision Memory Contractへ接続 |
| `M49_PROGRESSIVE_DECISION_EXPLICITNESS_v1.md` | **Integrated** | Decision Memory、Profile / Policy |
| `M49_HISTORICAL_DECISION_BOUNDARY_BRIDGE_v1.md` | **Historical bridge only + semantic kernel integrated** | legacy schemaは自動継承せず、Decision / Authority等の境界だけ反映 |
| `M50_CAPABILITY_CHOICE_BOUNDARY_v1.md` | **Integrated without milestone identity** | Capability Understanding / Choice |
| `M50_CAPABILITY_REALIZATION_OPTIONS_v1.md` | **Partially integrated** | Provider-specific realizationをUniversal型にしない判断をProvider / Adapterへ反映。具体shapeは非継承 |
| `M50_HISTORICAL_CAPABILITY_EVIDENCE_REVIEW_v1.md` | **Historical evidence review only** | old M45実装をcurrent Executable Evidenceへ継承しない根拠として保持 |

## 4. 実装・Representation寄りhistorical review

| Historical document | current disposition | currentでの扱い |
|---|---|---|
| `CANONICALIZATION_STANDARD_REVIEW_v1.md` | **Historical input; current Profile exists** | historical案をそのまま採用せず、ADR-0023でJCS+SHA-256 / raw-bytes+SHA-256をcurrent Representation ProfileとしてAccepted |
| `JCS_GO_IMPLEMENTATION_REVIEW_v1.md` | **Historical implementation review** | historical Go / JCS選択は非継承。current Go verifier probeはcurrent Profileに対する独立Executable Evidence |
| `M48_REFERENCE_CONTRACT_DRAFT_v1.md` | **Superseded as current authority** | current Contract権威はADR-0021とcurrent Contract Definition。historical draftはprovenanceとしてのみ参照 |
| `M47_M48_PRESSURE_TEST_v2.md` | **Historical pressure-test evidence** | current Architectureの正本ではないが、Core肥大化や境界崩壊の反例資料として利用可能 |
| `M48_FEASIBILITY_TO_REBASELINE_DELTA_v1.md` | **Historical rebaseline evidence** | current Design baselineはProduct Value / REQ / ADRから再構成済み |

## 5. historical Core候補の扱い

`CORE_BOUNDARY_REVIEW_v1.md`には、当時の型候補として次が列挙されていました。

- LogicalArtifactRef
- ExactArtifactBinding
- SemanticLineageRecord
- BoundedSubjectRef
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

current Architectureは、この**型名一覧そのもの**をproduction schemaとして採用していません。

再利用したのは、次の意味差です。

```text
logical identity != exact binding != semantic revision != storage revision
Observation != EvidenceUse != Assurance
Unknown != No
Conflict != latest-wins
source origin != discovery route
```

current v1alpha1 Contractは、この意味差のうち相互運用・検証上必要になったsubsetを実体化したものです。historical候補型の全量復活ではありません。

## 6. historical Decision Memoryの扱い

M49系列から、次をcurrent Decision Memoryへ統合しました。

- Recommendation != Decision
- Decision != Authority / Action Intent / Execution / Outcome
- Decision basisを後から辿れること
- rationale != private chain-of-thought
- Decision後もUnknown / Conflictが残り得ること
- D1を後知恵で書き換えずD2とのlineageを残すこと
- Progressive ExplicitnessをProfile / Policyへ置くこと

currentでは、これらの一部を`sei.decision-memory/v1alpha1`、Semantic Reference / Interchange、fixture、first semantic runtimeで限定的に検証しています。

一方、M49専用workflow、status machine、schema version lifecycleはcurrent Architectureへ導入していません。

## 7. historical Capability系列の扱い

M50系列から、次をcurrent Capability concernへ統合しました。

```text
Capability Definition
  != Capability Observation
  != Matching
  != Choice Decision
  != Provider selection
  != Authority
  != Execution
```

さらにADR-0019 / ADR-0024を反映し、Provider internal state→Adapter / Mapping→Capability Observationという境界をcurrent Architectureへ追加しています。

currentでは`sei.capability-observation/v1alpha1`、F1〜F7 fixture、Go first runtime、synthetic Provider A / B Adapterにより、この境界の一部をExecutable Evidenceとして確認しています。

旧M50で未決だった次は、current Architectureでも無理に固定していません。

- Capability Definitionのproduction field set
- Observation property vocabularyの永久固定
- Matchingの最終Artifact shape
- chosen Capability relationのwire表現
- provider realization / offerのUniversal semantic type
- composition表現
- universal cost / risk model

## 8. historical Persistence / Representation系列の扱い

`SEMANTIC_PERSISTENCE_CONTRACT_v1.md`から、Storage-neutralな次のobligationをcurrent Persistenceへ統合しました。

- logical identity preservation
- exact binding integrity
- semantic lineage preservation
- provenance preservation
- reference integrity
- contract / representation identity
- portable export / import

次のmechanicsはcurrent ArchitectureでもProvider-ownedです。

- table / collection / object layout
- transaction implementation
- MVCC / lock
- event store
- replication / sharding
- backup / restore
- physical compaction
- encryption-at-rest implementation

currentではSemantic Reference / Interchange ContractとRepresentation Profileを実体化し、fixture / verifier / first runtimeで一部を検証しています。ただしactual Storage migration自体は未検証です。

historical M47 digest mappingもcurrent JCS / raw-bytes Profileから推定せず、ISSUE-000034で別問題として扱います。

## 9. historical Federationの扱い

`BOUNDED_FEDERATION_PROFILE_v1.md`から、次をcurrent Federation concernへ統合しました。

- Federationはoptional ProfileでありUniversal world model統合ではない。
- Request != Authority Grant != Commitment != Execution。
- Offer != Capability proof != Decision。
- Result != Business Outcome != Assurance。
- Withheld Contextと単純Unknownを必要に応じて分ける。
- credential / transport / crypto mechanicsはProvider-owned。

Request / Offer / Commitment / Result等は、current baselineで独立Universal Contractとしては固定していません。必要性が具体Scenarioで生じた場合に改めてIssue / ADRから判断します。

## 10. Evidence classification

historical bundle manifestは、そのbundle自体を「local Phase 1 candidate + M49/M50 planning; actual repository releaseではない」と位置づけていました。

current ArchitectureでもこのEvidence境界を維持します。

```text
historical Design / local executable evidence
  != current Design Evidence
  != current Executable Evidence
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

current 2026-08-31 baselineでは、少なくとも次を区別します。

- historical Design / local executable evidence: **参考・再検証候補**
- current actual Architecture / Contract / Profile: **Design Evidence**
- current Contract 17 fixture conformance: **scoped Executable Evidence**
- current Representation Profile fixture / Go probe: **scoped Executable Evidence**
- current first semantic runtime slice: **scoped Executable Evidence**
- current synthetic Provider Adapter slice: **scoped Executable Evidence**
- current Release Evidence: **Not Yet Verified**
- current Operational Evidence: **Not Yet Verified**
- current Adoption / Outcome Evidence: **Not Yet Verified**

Executable Evidenceが増えたことを、historical candidateの正当化やproduction成立へ遡及させません。

## 11. current baselineで新しく強化された点

historical candidate以降、current baselineでは特に次が強化されています。

1. Product Value V1〜V8からArchitectureまでの明示的traceability。
2. SEI / TEI Product Boundaryの固定。
3. Reference Model / PatternとCognitive Methodの分離。
4. Provider-neutral Capability ObservationとAdapter mapping provenance。
5. Product Value / Requirement / Architecture / Contract / Representation Profileの権威関係。
6. 4 Contract familyと2 Representation Profileのcurrent実体化。
7. first semantic runtime sliceとsynthetic Provider Adapterによる限定的Executable Evidence。
8. Design / Executable / Release / Operational / Adoption・Outcome Evidenceの分離。
9. 全開発文書における自然な日本語全文再ドラフト工程。

## 12. Natural Japanese review

historical Architecture候補をcurrent Product Value、REQ-0001〜0022、SCN-0001〜0017、ADR-0001〜0024、4 Contract family、2 Representation Profile、first semantic runtime、synthetic Provider Adapterへ一件ずつ照合しました。historical時点の未決候補と、currentで既にAccepted・実体化・限定検証された境界を分離し、historical PASSをcurrent Evidenceへ自動継承しない原則も維持しています。その後、対応関係、留保、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
