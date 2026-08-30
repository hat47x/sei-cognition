# Historical Architecture Mapping

更新日: 2026-08-31  
状態: **Historical Design Provenance Mapping**

## 1. この文書の役割

この文書は、Phase 1 candidateで作成されたM48 / M49 / M50周辺のArchitecture文書を、current `SOZA_REFERENCE_ARCHITECTURE.md`へどのように統合・分離・保留したかを記録します。

historical文書をcurrent正本へrenameしたものではありません。

current Architectureは、Product Value、REQ-0001〜REQ-0022、SCN-0001〜SCN-0017、ADR-0001〜ADR-0021から再構成しています。

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
- JCS / SHA-256 / JSON等のRepresentation選択
- local PASS / planning PASS
- current actual repositoryに存在しないruntime evidence

## 3. 主要historical Architecture mapping

| Historical document | current disposition | 主なcurrent Architecture |
|---|---|---|
| `CORE_BOUNDARY_REVIEW_v1.md` | **Integrated** | §2 Architecture原則、§4 Durable Semantic Core、§11 Profile / Policy、§19固定しないもの |
| `CLAIM_INTERPRETATION_BOUNDARY_v1.md` | **Integrated as semantic boundary** | §5 Inquiry / Epistemics、§6 Cognitive Method。Universal Claim型はcurrent Coreへ採用しない |
| `REVISION_SUPERSESSION_SEMANTICS_v1.md` | **Integrated** | §7 Decision revision、§10 Semantic Revision、§15 Persistence |
| `SEMANTIC_PERSISTENCE_CONTRACT_v1.md` | **Split** | Architecture意味核は§10 / §15へ統合。portable contract部分はISSUE-000030で再評価 |
| `EXACT_BINDING_VERIFICATION_BOUNDARY_v1.md` | **Integrated** | §10 Logical Reference / Exact Historical Binding。Representation詳細はContractへDeferred |
| `BINDING_VERIFICATION_OUTCOME_v1.md` | **Integrated** | §10の`not_verified != failed`、§16 Evidence boundary |
| `PROGRESSIVE_SEMANTIC_EXPLICITNESS_v1.md` | **Integrated** | §11 Profile / Policy。固定explicitness level / universal risk scoreは採用しない |
| `BOUNDED_SUBJECT_RESPONSIBILITY_v1.md` | **Integrated** | §9 Responsibility / Authority。Global Principal ontologyは採用しない |
| `BOUNDED_FEDERATION_PROFILE_v1.md` | **Integrated as optional Profile** | §12 Federation / Selective Disclosure。transport / cryptoはProvider-owned |
| `M49_DECISION_MEMORY_BOUNDARY_v1.md` | **Integrated without milestone identity** | §7 Decision Memory |
| `M49_DECISION_REFERENCE_ROLES_v1.md` | **Integrated as role separation** | §7 Basis / Rationale、§10 Reference。wire shapeは未固定 |
| `M49_PROGRESSIVE_DECISION_EXPLICITNESS_v1.md` | **Integrated** | §7 Decision Memory、§11 Profile / Policy |
| `M49_HISTORICAL_DECISION_BOUNDARY_BRIDGE_v1.md` | **Historical bridge only + semantic kernel integrated** | legacy schemaは自動継承せず、Decision / Authority等の境界だけ§7 / §9へ反映 |
| `M50_CAPABILITY_CHOICE_BOUNDARY_v1.md` | **Integrated without milestone identity** | §8 Capability Understanding / Choice |
| `M50_CAPABILITY_REALIZATION_OPTIONS_v1.md` | **Partially integrated** | Provider-specific realizationをUniversal型にしない判断を§8 / §13へ反映。具体shapeは非継承 |
| `M50_HISTORICAL_CAPABILITY_EVIDENCE_REVIEW_v1.md` | **Historical evidence review only** | old M45実装をcurrent executable evidenceへ継承しない根拠として保持 |

## 4. 実装・Representation寄りhistorical review

| Historical document | current disposition | 理由 |
|---|---|---|
| `CANONICALIZATION_STANDARD_REVIEW_v1.md` | **Contract / Representation candidate** | canonicalizationはsemantic CoreではなくRepresentation ProfileとしてISSUE-000030で再評価 |
| `JCS_GO_IMPLEMENTATION_REVIEW_v1.md` | **Historical implementation review** | Go / JCSの選択をcurrent Architectureへ固定しない |
| `M48_REFERENCE_CONTRACT_DRAFT_v1.md` | **Superseded as current authority** | current Contract規約はADR-0021。意味核は必要に応じISSUE-000030で再評価 |
| `M47_M48_PRESSURE_TEST_v2.md` | **Historical pressure-test evidence** | current Architectureの正本ではないが、Core肥大化の反例資料として利用可能 |
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

production field setやContract typeはISSUE-000030以降で必要性を再確認します。

## 6. historical Decision Memoryの扱い

M49系列から、次をcurrent §7へ統合しました。

- Recommendation != Decision
- Decision != Authority / Action Intent / Execution / Outcome
- Decision basisを後から辿れること
- rationale != private chain-of-thought
- Decision後もUnknown / Conflictが残り得ること
- D1を後知恵で書き換えずD2とのlineageを残すこと
- Progressive ExplicitnessをProfile / Policyへ置くこと

一方、M49専用workflow、status machine、schema version lifecycleはcurrent Architectureへ導入していません。

## 7. historical Capability系列の扱い

M50系列から、次をcurrent §8へ統合しました。

```text
Capability Definition
  != Capability Observation
  != Matching
  != Choice Decision
  != Provider selection
  != Authority
  != Execution
```

さらにADR-0019の後発設計を反映し、Provider internal state→Adapter / Mapping→Capability Observationという境界をcurrent Architectureへ追加しています。

旧M50で未決だった次は、current Architectureでも無理に固定していません。

- Capability Definitionのproduction field set
- Observation property vocabulary
- Matchingの最終Artifact shape
- chosen Capability relationのwire表現
- provider realization / offerのsemantic type
- composition表現
- universal cost / risk model

## 8. historical Persistence系列の扱い

`SEMANTIC_PERSISTENCE_CONTRACT_v1.md`から、Storage-neutralな次のobligationをcurrent §15へ統合しました。

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

`file/Git`、`DB/object store`等の具体Provider間で同じportable semantic exportを作れるかという旧Acceptanceは、current Contract / Executable phaseで再検証します。historical PASSは継承しません。

## 9. historical Federationの扱い

`BOUNDED_FEDERATION_PROFILE_v1.md`から、次をcurrent §12へ統合しました。

- Federationはoptional ProfileでありUniversal world model統合ではない。
- Request != Authority Grant != Commitment != Execution。
- Offer != Capability proof != Decision。
- Result != Business Outcome != Assurance。
- Withheld Contextと単純Unknownを必要に応じて分ける。
- credential / transport / crypto mechanicsはProvider-owned。

Request / Offer / Commitment / Result等をcurrent production Contractへ採用するかはISSUE-000030で再評価します。

## 10. Evidence classification

historical bundle manifestは、そのbundle自体を「local Phase 1 candidate + M49/M50 planning; actual repository releaseではない」と位置づけていました。

current ArchitectureでもこのEvidence境界を維持します。

- historical Design / local executable evidence: **参考・再検証候補**
- current actual Architecture: **Design Evidence**
- current executable conformance: **Not Yet Verified**
- current release: **Not Yet Verified**
- operational evidence: **Not Yet Verified**

## 11. current baselineで新しく強化された点

historical candidate以降、current baselineでは特に次が強化されています。

1. Product Value V1〜V8からArchitectureまでの明示的traceability。
2. SOZA / TEI Product Boundaryの固定。
3. Reference Model / PatternとCognitive Methodの分離。
4. Provider-neutral Capability Observationとadapter provenance。
5. Product Value / Requirement / Architecture / Contractの権威関係。
6. Design / Executable / Release / Operational Evidenceの分離。
7. 全開発文書における自然な日本語全文再ドラフト工程。

## 12. Natural Japanese review

historical Architecture候補をcurrent Reference Architectureへ一件ずつ照合し、統合・分離・保留・非継承の理由を整理した後、対応関係とEvidence状態を変えず、自然な日本語となることを最重要視して全文を再ドラフトしました。その後、最終意味監査を実施しています。
