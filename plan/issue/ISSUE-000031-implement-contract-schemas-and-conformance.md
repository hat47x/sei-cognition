# ISSUE-000031: current Contractのschema・fixture・conformanceを実装する

Status: **Resolved**  
Priority: **1**  
Related ADRs: **ADR-0008, ADR-0009, ADR-0019, ADR-0020, ADR-0021**  
Updated: 2026-08-31

## Goal

current Contract Design baselineをmachine-readable schema、positive / negative / boundary fixture、semantic validatorへ落とし、actual repository上でfixture-scoped Executable Evidenceを再現できる状態にする。

Contract Definitionの意味をschema都合で変更せず、schemaにしか存在しないsemantic requirementを作らない。

## Resolution

### 1. 4 ContractのJSON Schemaを実体化した

actual repositoryへ次を追加した。

```text
contracts/schemas/v1alpha1/
  semantic-reference.schema.json
  decision-memory.schema.json
  capability-observation.schema.json
  semantic-interchange.schema.json
```

JSON Schemaはcurrent v1alpha1のportable representation候補であり、JSONをUniversal semantic representationへ昇格させていない。

### 2. Schemaとsemantic validatorの責務を分けた

Schemaで自然に検査できるものと、意味上の関係を見なければ判断できないものを分離した。

Schemaで検査する例:

- contract id / version representation
- 必須field
- observed time
- Decision recordへの未定義`authority`埋め込み
- Recommendation / Decision recordの排他
- Capability condition state

semantic validatorで検査する例:

- 同一logical identity内のSemantic Lineageには両端のexact endpointが必要
- interchange recordのlogical refとexact bindingのlogical ref整合
- bundle内にexact recordが存在するとき、Decision / Recommendation basisのexact bindingが同じdigest / Profileを指すこと
- unknown nested Contractをknownとして扱わず`not_verified`とすること

```text
Schema valid != Semantic conformance complete
```

を実行系でも維持した。

### 3. Decision MemoryをRecommendation / Decisionの別recordとして表現した

`decision-memory.schema.json`では、

- `record_type: recommendation`
- `record_type: decision`

を別recordとして表現し、双方を相互排他にした。

これにより、Recommendationだけが存在してDecisionがない状態を正常に表現できる。

Decisionは`unresolved_refs`を保持でき、Decision作成がUnknown / Conflictの解消を意味しない。

### 4. Capability Observation F1〜F7を検証可能にした

ISSUE-000024のF1〜F7をcurrent schemaへ落とし、TEI partial degradation、proposed / actual、Environment binding、observation gap、cross-provider comparison、historical reconstruction、selective disclosureをactual fixtureとして検査した。

ISSUE-000024は本Issueとは別にResolvedしている。

### 5. negative / boundary fixtureを追加した

current checkerでは17 fixtureを扱う。

主な境界:

- DecisionへAuthorityを直接埋め込む → expected Schema FAIL
- Capability Observationの`observed_at`欠落 → expected Schema FAIL
- same-logical-id lineage without exact endpoints → expected Semantic FAIL
- bundle exact recordとDecision basisのdigest不一致 → expected Semantic FAIL
- unknown nested Contract version → expected `not_verified`
- `verification-not-verified` / `verification-failed` → 別状態としてvalid
- Recommendation without Decision → valid
- Decision with unresolved Unknown / Conflict → valid
- partial-knowledge interchange → valid

### 6. actual conformance runnerを実装した

- `tools/check_contract_conformance.py`
- `tools/contract-check-requirements.txt`
- `.github/workflows/contract-conformance.yml`

checkerはJSON Schema、semantic invariant、unknown-version boundaryを分離して分類する。

外部Schema参照はdeprecated `RefResolver`ではなく`referencing.Registry`を利用するよう修正した。

### 7. GitHub Actionsでcurrent Executable Evidenceを取得した

GitHub Actions `Contract Conformance`:

- Run ID: `33346472419`
- Head SHA: `9921c66f0803ddfe7810ea46c86b995f52895472`
- Conclusion: **success**
- Fixture count: **17**
- `passed`: **true**

F1〜F7、Recommendation-only、unresolved Decision、partial knowledgeはexpected PASSとなった。

Schema違反2件とsemantic違反2件はexpected FAILとして正しく検出され、unknown Contract versionはexpected `not_verified`となった。

Evidenceの詳細は`contracts/CONFORMANCE_EVIDENCE_2026-08-31.md`へ記録した。

## Acceptance

### Executable Acceptance

- [x] current Contractごとに必要なschemaがactual treeに存在する。
- [x] positive / negative fixtureが存在する。
- [x] unknown-version / partial-knowledge fixtureが存在する。
- [x] cross-contract / cross-record exact referenceの整合を検査できる。
- [x] Decision / Authority / Executionの非同一性をfixtureで確認できる。
- [x] Capability ObservationのProvider-neutralityをfixtureで確認できる。
- [x] `not_verified`と`failed`を区別できる。
- [x] actual conformance runnerの結果をGitHub Actionsで再現できる。
- [x] schema / validator / fixtureを文書へ戻して意味監査した。

### Release / Operational Acceptance

本Issueでは要求しない。

## Evidence state at closure

- Contract Design Baseline: **Satisfied**
- Contract v1alpha1 Fixture-scoped Executable Conformance: **Satisfied**
- Stable Representation Profile: **Not Yet Verified** — ISSUE-000009
- Historical M47 digest mapping: **Not Yet Verified** — ISSUE-000009
- Release Evidence: **Not Yet Verified**
- Operational Evidence: **Not Yet Verified**

`fixture.raw-json/v0`はfixture内部でexact reference整合を試すためのopaque Profile identityであり、stable Representation Profileではない。

本IssueのResolvedを、Exact Binding verification全体の安定化やSOZA release readinessへ拡張して解釈しない。

## Follow-up

- ISSUE-000009 — stable Representation Profile / historical M47 digest mapping
- ISSUE-000027 — Requirements registry checker
- ISSUE-000022 — repository baseline全体

## Natural Japanese review

4 Schema、17 fixture、semantic checker、GitHub Actionsの実行結果をContract Definitionへ戻して照合し、fixture-scoped Executable Evidenceと未検証のRepresentation / Release / Operational領域を分離した。その後、意味、条件、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
