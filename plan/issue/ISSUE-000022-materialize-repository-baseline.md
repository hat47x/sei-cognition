# ISSUE-000022: SOZA repositoryのcurrent baselineを実体化し、Evidence claimを再整合する

Status: **Resolved**  
Priority: **2**  
Related ADRs: **ADR-0007, ADR-0008, ADR-0009, ADR-0014, ADR-0018, ADR-0020, ADR-0021**  
Updated: 2026-08-31

## Goal

GitHub上の`hat47x/soza`へ、Product Valueから追跡可能なRequirements、Architecture、Contracts、Fixtures、Runtime、Toolsをcurrent Product Boundaryに沿って実体化する。

同時に、historical candidate / Library資産と、actual repositoryで再現したcurrent Evidenceを分け、README、Requirements、Plan上の達成主張をactual treeへ一致させる。

## Closure summary

2026-08-31時点で、`develop/v0.1.0`にはcurrent baselineとして次が実体化された。

```text
.github/
product/
requirements/
architecture/
contracts/
fixtures/
plan/
runtime/
tools/
```

このIssueで求めていた「current repository baselineの実体化」は、Designだけでなく、対象を限定したExecutable Evidenceまでactual branchで再現できる状態へ到達したため、本IssueをResolvedとする。

release / operational completenessを意味するclosureではない。

## 1. Product / Value baseline

current正本として次を整備した。

- Product Value
- Value Model
- Value Acceptance
- Product Vision
- Product Principles

Product Valueから下位文書への権威関係と、V1〜V8の評価軸を明示した。

## 2. Requirements baseline

current正本:

- REQ-0001〜REQ-0022
- SCN-0001〜SCN-0017
- historical requirement mapping

Requirements Registry checkerとGitHub Actionsをactual repositoryへ実体化した。

直近の`requirements/PRODUCT_REQUIREMENTS.md`では、Architecture / Contract / Runtimeが未実体化だった時期のEvidence記述を削除し、現在のfixture / runtime EvidenceへRequirementごとに保守的に再基線化した。

GitHub Actions `Requirements Registry Conformance`:

- Run ID `33349256675`
- conclusion: **success**

このPASSはRequirementの全実装完了ではなく、registry構造と相互参照のExecutable Evidenceである。

## 3. Architecture baseline

actual repositoryへ次を実体化した。

```text
architecture/
  README.md
  SOZA_REFERENCE_ARCHITECTURE.md
  TRACEABILITY.md
  history/
    HISTORICAL_ARCHITECTURE_MAPPING.md
```

M48 / M49 / M50等のMilestone順をcurrent ontologyへ持ち込まず、Inquiry、Decision Memory、Capability、Responsibility / Authority、Semantic Reference、Provider / Adapter、Persistence等のarchitecture concernへ再構成した。

REQ-0001〜REQ-0022をArchitecture concernへ追跡できる。

## 4. Contract / Fixture baseline

current Contract family:

- `soza.semantic-reference/v1alpha1`
- `soza.decision-memory/v1alpha1`
- `soza.capability-observation/v1alpha1`
- `soza.semantic-interchange/v1alpha1`

加えて、次をactual treeへ実体化した。

- Contract Catalog / Traceability
- historical contract mapping
- JSON Schema v1alpha1
- Capability Observation F1〜F7
- boundary / negative fixture
- semantic conformance checker
- GitHub Actions `Contract Conformance`

Contract Definitionをsemantic authorityとし、Schema / validatorをその実装・検証representationとして分離している。

## 5. Representation Profile baseline

ADR-0023で、current/future Exact Binding向けに次をAcceptedした。

```text
soza.jcs+sha256/v1alpha1
soza.raw-bytes+sha256/v1alpha1
```

RFC 8785 JCS、raw bytes、high-precision boundary、Unicode non-normalization、`verified / failed / not_verified`等をfixtureとGo probeで検証した。

ISSUE-000009はcurrent/future Profile stabilizationとしてResolvedした。

historical M47 digestの生成規則は一次source未回収のため、ISSUE-000034へ独立して分離した。

```text
current Profile accepted
  != historical M47 Profile known
```

ADR-0023に従い、historical mappingの未回収をcurrent repository baselineのblocking conditionとはしない。確認不能なhistorical bindingをJCSへ推測で遡及変換しない。

## 6. First semantic runtime baseline

ADR-0022に従い、Goでread / validate / reconstructのfirst runtime sliceを実体化した。

主な範囲:

- Contract identity / version
- Logical Reference
- Exact Binding metadata
- Verification Outcome vocabulary
- Semantic Lineage
- Decision / Recommendation
- Capability Observation
- Semantic Interchange
- unknown nested Contract handling
- partial knowledge preservation
- historical exact basis consistency
- original interchange bytesのlossless re-export

GitHub Actions `Semantic Runtime Conformance` run #3:

- Run ID `33348972805`
- conclusion: **success**

current Contract fixture checkerと`go test ./...`を同じfixture sourceへ接続した。

## 7. Provider Adapter baseline

ADR-0024に従い、Provider-owned stateをProvider-neutral Capability Observationへ変換する境界を実体化した。

異なるinput schemaを持つsynthetic Provider A / Bから、同じCapabilityに対するObservationを生成できる。

検証した主な境界:

- Provider-specific inputをUniversal `ProviderState`へ統合しない。
- status interpretation / unit conversionをmappingとして扱う。
- mapping provenanceを保持する。
- source state referenceを保持する。
- missing値をnegative/defaultへ変換しない。
- Provider-specific targetをopaque referenceとして保持する。
- AdapterからDecision / Authority / Executionを生成しない。
- outputをcurrent Capability Observation validationへ戻す。

GitHub Actions `Semantic Runtime Conformance` run #4:

- Run ID `33349604842`
- commit `4450ea1acf41615a3679a65e266c008a460c5c33`
- conclusion: **success**

これはsynthetic Provider AdapterのExecutable Evidenceであり、TEI / SaaS production interoperabilityではない。

## 8. Plan / CI baseline

current planはADR / Issue registryとintegrity checkerを持つ。

CI failureを検出した場合は、その時点で原因を解消し、successを確認してから次へ進む運用を適用している。

実際にfirst runtime sliceでは、

1. checker dependency導入漏れ
2. Semantic Interchange fixtureをstandalone recordとして読んだtest誤り

をCIから検出し、その都度修正してsuccessを確認した。

Provider Adapter設計のatomic commitについても、Plan integrity run `33349483470`でsuccessを確認した。

## 9. Historical candidateとの境界

旧runtime、旧M48〜M50 planning、generated summary、local PASS等はhistorical Evidence / 再利用候補として扱う。

```text
historical PASS != current PASS
```

current Product / Requirement / ADR / Contractへ再照合し、actual branchのcurrent CIを通すまでcurrent Executable Evidenceへ昇格しない。

## 10. Completion criteria

### Design baseline

- [x] Product ValueからRequirements / ADRまで追跡できる。
- [x] RequirementsからArchitectureへ追跡できる。
- [x] ArchitectureからContractへ追跡できる。
- [x] historical mappingをcurrent正本から分離した。
- [x] current文書へ自然な日本語再ドラフト工程を適用した。

### Executable baseline

- [x] Requirements registry checkerをactual treeで再現できる。
- [x] Contract conformanceをactual treeで再現できる。
- [x] Capability Observation F1〜F7をactual treeで検証できる。
- [x] expected negative / boundary caseを検査できる。
- [x] current `runtime/` baselineを実体化した。
- [x] runtimeとContract fixtureを横断するend-to-end conformanceを構築した。
- [x] current/future Representation Profileをactual fixture / probeで検証した。
- [x] Provider Adapter vertical sliceをcurrent Capability Observationへ接続した。
- [x] current actual Evidenceとhistorical candidateを分離した。

### Evidence closure

- [x] root READMEをcurrent Executable baselineへ同期した。
- [x] Requirement文書の古い「未実体化」記述をcurrent treeへ同期した。
- [x] Decision Memory / Capability Observationの最初のruntime実装範囲をcurrent Evidenceから確定した。
- [x] release / operational Evidenceを未確認のまま引き上げていない。

## 11. Closureで完了を主張しないもの

本IssueをResolvedとしても、次は未完了である。

- production TEI Adapter
- production SaaS Adapter
- Authority / Action Intent / Execution runtime
- production Storage migration
- Production-grade Provider interoperability
- historical M47 digest Profile recovery（ISSUE-000034）
- Release Evidence
- Operational Evidence
- repository全開発文書の自然な日本語監査完了（ISSUE-000015）

これらはcurrent repository baselineの存在条件とは分離して、必要なIssueで追跡する。

## Follow-up

- ISSUE-000015 — 全開発文書の自然な日本語監査
- ISSUE-000021 — design history provenance監査（Deferred）
- ISSUE-000034 — historical M47 digest Profile recovery（Blocked）
- production Provider integrationは、具体ProviderとAcceptanceが定まった時点で独立Issueを作成する。

## Natural Japanese review

actual root tree、Product / Requirements / Architecture / Contract、Representation Profile、runtime、Provider Adapter、各CI結果へ戻ってCompletion criteriaを一件ずつ再確認した。historical M47 mapping、production Provider、Release / Operational Evidenceをcurrent baseline closureへ混入させずに分離した後、意味、完了条件、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
