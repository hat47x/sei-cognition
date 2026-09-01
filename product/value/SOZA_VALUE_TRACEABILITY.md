# SOZA Value Traceability

更新日: 2026-09-01  
状態: **Current Product Value Traceability Baseline**

## 1. この文書の役割

この文書は、SOZAのProduct Valueを、current Requirements、Acceptance Scenarios、ADR、Reference Architecture、Semantic Contract、Representation Profile、runtime、Provider Adapter、Payload Source、Projection Evaluation、release candidate readiness、現在のEvidence状態まで上位から追跡するための索引です。

新しい意味上の正本は作りません。詳細は次を正とします。

- Product Value / V1〜V8: `SOZA_PRODUCT_VALUE.md`, `SOZA_VALUE_MODEL.md`
- Evidence受入れ境界: `SOZA_VALUE_ACCEPTANCE.md`
- Requirement: `../../requirements/PRODUCT_REQUIREMENTS.md`
- Acceptance Scenario: `../../requirements/ACCEPTANCE_SCENARIOS.md`
- Architecture: `../../architecture/SOZA_REFERENCE_ARCHITECTURE.md`, `../../architecture/TRACEABILITY.md`
- Contract: `../../contracts/TRACEABILITY.md`
- Representation Profile: `../../contracts/profiles/`
- runtime: `../../runtime/go/`
- V6 / V7 evaluation: `../../evaluation/v6-v7/`
- release candidate readiness: `../../plan/release/V0_1_0_RELEASE_READINESS.md`
- ADR / Issue: `../../plan/`

この追跡表が埋まっていること自体をProduct Valueの達成とはみなしません。

## 2. 追跡の基本形

```text
Product Value
  → V1〜V8
  → REQ-*
  → SCN-*
  → ADR
  → Architecture concern
  → Semantic Contract / Representation Profile
  → Runtime / Provider Adapter / Payload Source / Projection Evaluation
  → Fixture / Test / CI
  → Release Candidate Readiness
  → Evidence state
```

関係は多対多です。リンク数やcoverage率をProduct ValueのKPIにはしません。

## 3. V1〜V8のcurrent trace

| Value Axis | 主なREQ | 主なSCN | 主なADR | current executable material |
|---|---|---|---|---|
| **V1 Historical Reconstruction** | REQ-0001, 0003, 0005, 0008, 0009, 0014, 0017, 0018, 0020, 0022 | SCN-0001, 0003, 0005, 0008, 0009, 0010, 0014, 0016 | ADR-0003, 0007, 0008, 0009, 0010, 0011, 0019, 0021, 0022, 0023, 0024 | Semantic Reference / Decision Memory / Interchange fixture、F6 historical reconstruction、Go runtime、Verifier Registry、synthetic Payload Source、Adapter mapping provenance |
| **V2 Semantic Separation** | REQ-0002, 0003, 0006, 0008, 0013, 0015, 0016, 0017, 0022 | SCN-0001, 0002, 0004, 0009, 0011, 0015, 0016 | ADR-0002, 0004, 0010, 0011, 0012, 0016, 0017, 0019, 0022, 0024 | Recommendation-only、Decision with unresolved、Authority field rejection、Adapter outputのsemantic escalation非生成 |
| **V3 Revision Integrity** | REQ-0001, 0003, 0004, 0005, 0008, 0009, 0014, 0018 | SCN-0003, 0005, 0008, 0010, 0015, 0016 | ADR-0003, 0007, 0008, 0009, 0010, 0011, 0017, 0021, 0023, 0024 | lineage / exact binding invariant、Profile fixture、runtime verification、取得不能≠digest mismatch、mapping provenance |
| **V4 Provider Independence** | REQ-0001, 0007, 0012, 0013, 0021, 0022 | SCN-0002, 0007, 0010, 0011, 0012, 0014 | ADR-0006, 0012, 0013, 0014, 0019, 0021, 0022, 0024 | Capability Observation F1〜F7、cross-provider fixture、synthetic Provider A/B Adapter |
| **V5 Uncertainty Preservation** | REQ-0002, 0005, 0012, 0014, 0016, 0022 | SCN-0001, 0003, 0007, 0011, 0012, 0016 | ADR-0002, 0005, 0006, 0010, 0011, 0019, 0022, 0024 | Unknown / Conflict / Withheld / partial knowledge、Adapter missing→unknown |
| **V6 Human / AI Readability** | REQ-0010, 0011, 0019, 0020 | SCN-0004, 0006, 0013, 0017 | ADR-0005, 0017, 0018, 0020, 0021 | human-readable Contract / machine-readable schema、light/audit Projection、6 semantic questions、7 negative cases |
| **V7 Progressive Explicitness** | REQ-0010 | SCN-0004, 0013 | ADR-0005, 0019 | low-impact minimal Decisionとhigh-impact rich Decisionを同一harnessで評価 |
| **V8 Execution Independence** | REQ-0001, 0004, 0007, 0011, 0012, 0015, 0018, 0021, 0022 | SCN-0002, 0005, 0006, 0007, 0008, 0012, 0014, 0015 | ADR-0006, 0007, 0012, 0013, 0014, 0017, 0019, 0022, 0024 | Provider-neutral Contract、execution非依存runtime、Adapter-local provider schema、Storage-neutral Payload Source |

表中のmaterialが存在しても、そのValue Axis全体のExecutable AcceptanceがSatisfiedになったとは読みません。

## 4. Requirement / Scenario baseline

current Product Requirementsは`REQ-0001`〜`REQ-0022`、Acceptance Scenariosは`SCN-0001`〜`SCN-0017`です。

```text
Requirement != Acceptance Scenario != Test Case
```

Requirements Registryの代表runは`33349256675`で**success**しています。これはregistry構造とcheckerに対するExecutable Evidenceであり、Requirement内容のproduction実現を証明しません。

## 5. Architecture / Contract baseline

current Reference Architectureは実装package順ではなく、意味上のarchitecture concernで構成します。

current Semantic Contractは次の4 familyです。

- `soza.semantic-reference/v1alpha1`
- `soza.decision-memory/v1alpha1`
- `soza.capability-observation/v1alpha1`
- `soza.semantic-interchange/v1alpha1`

Contract baselineは17 fixtureでconformanceを確認しています。

## 6. Representation Profile baseline

current/future Exact Binding向けProfile:

- `soza.jcs+sha256/v1alpha1`
- `soza.raw-bytes+sha256/v1alpha1`

Profile Conformance:

- Run `33347989530`: **success**

Runtime Verifier Registry:

- Run `33452115728`: **success**

```text
Semantic Contract != Representation Profile != verifier implementation
```

### historical M47 digest

historical M47 digest mappingはcurrent Profileとは別問題としてISSUE-000034で回収しました。

GitHub reachable history、branch、Actions、Library semantic / exact-name search、個別Go / Python inventory、archive時系列まで確認しましたが、actual digest-producing source、actual M47 conformance tool、actual historical digest anchor、M47 source archiveは回収できませんでした。

そのためISSUE-000034は、**現在保持された直接Evidenceからdigest ruleを回収不能であることを確定し、historical bindingを`not_verified`として保持する**方針でResolvedとしました。

```text
ISSUE-000034 Resolved
  != historical M47 Profile verified

current Profile verified
  != historical digest identified
```

新たな一次資料が得られた場合は再開できます。

## 7. first semantic runtime / Verifier / Payload Source

first runtimeはread / validate / reconstructへ限定します。

- first semantic runtime: Run `33348972805` — **success**
- Verifier Registry: Run `33452115728` — **success**
- Payload acquisition boundary: Run `33457416359` — **success**

Payload SourceはStorage固有mechanicsをCoreへ持ち込まず、取得不能・source error・local size limitをdigest mismatchと区別します。

```text
payload unavailable / operational acquisition failure
  → not_verified

payload available + digest mismatch
  → failed
```

synthetic Payload SourceのPASSをproduction S3 / MinIO / filesystem / HTTP integrationへ拡張しません。

## 8. synthetic Provider Adapter

ADR-0024 / ISSUE-000036に基づき、異なるProvider-specific input shapeを各Adapterが解釈し、Capability Observationへ収束させます。

- first Adapter slice: Run `33349604842` — **success**
- Provider-specific field非漏洩hardening: Run `33349801993` — **success**

AdapterはRecommendation / Decision / Authority / Executionを生成しません。

## 9. V6 / V7 Projection evaluation

Run `33456710459`は**success**しています。

- canonical source: rich / low-impact 2件
- Projection: light / audit
- semantic question: 6件
- negative case: 7件

これはstatic / synthetic evaluation-harness scoped Executable Evidenceです。実利用者の理解可能性、入力負担、見落とし率、production UXのOperational / Adoption Evidenceではありません。

## 10. v0.1.0 Release Candidate Readiness

ISSUE-000041で、current checkerを同一commit上で一括再実行するRelease Readiness Gateを実体化しました。

negative self-testを含む確認Run:

- Workflow: `v0.1.0 Release Readiness`
- Run ID: `33462118480`
- candidate Head SHA: `d4539322bf5cd4eca55c339c57b98a61cfa72f69`
- conclusion: **success**

同一candidate commitで次がsuccessしています。

- Plan registry integrity
- document review checker negative self-tests
- document review registry integrity
- Requirements checker self-tests / registry
- Contract conformance
- Representation Profile fixtures
- commit-pinned RFC 8785 JCS probe
- Go semantic runtime / Provider Adapter / Verifier / Payload Source tests
- V6 / V7 Projection evaluation

closure commitでも同じGateを再実行し、Issue / registry / Traceability更新後の回帰がないことを確認しています。

これはrelease-candidate readiness scoped Executable Evidenceです。

```text
Release Readiness Gate PASS
  != Git tag created
  != GitHub Release published
  != distributed Artifact verified
  != Release Evidence
```

## 11. Evidenceの現在地

```text
Design Evidence
  != Executable Evidence
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

### Design Evidence

Product、Requirements、ADR-0001〜0024、Reference Architecture、4 Semantic Contract family、2 Representation Profile、runtime / Adapter / Payload Source boundary、V6/V7 evaluation protocol、release-readiness baselineがあります。

### Executable Evidence — scoped

- Plan registry integrity
- document review registry integrity + negative self-tests
- Requirements registry structural conformance
- Contract 17-fixture conformance
- Representation Profile fixture / probe
- first semantic runtime
- current 2 ProfileのVerifier Registry
- synthetic Payload Source
- synthetic Provider Adapter
- V6 / V7 Projection evaluation harness
- v0.1.0 Release Candidate Readiness Gate

### Release Evidence

**Not Yet Verified**

readiness gateのPASSを、実際に配布されたArtifactのRelease Evidenceへ昇格させません。

### Operational Evidence

**Not Yet Verified**

### Adoption / Outcome Evidence

**Not Yet Verified**

## 12. Value Axisごとの主要な未検証点

### V1 Historical Reconstruction

current Contract / Profile / runtime / Adapter / Payload Sourceの限定境界は検査済みです。historical M47 digest ruleは回収不能として`not_verified`を維持しています。production Storage、実Provider mapping変更をまたぐ長期historical reconstruction、再判断への寄与は未検証です。

### V2 Semantic Separation

Recommendation / Decision / Authority等の分離と、Adapterが後続意味へ自動昇格しないことを一部検査済みです。production責任線・権限線をまたぐOperational Evidenceはありません。

### V3 Revision Integrity

lineage / exact binding invariant、mapping provenance、取得不能をdigest mismatchへ変換しない境界は検査済みです。production Storage revisionや長期間のmapping changeをまたぐEvidenceはありません。

### V4 Provider Independence

cross-provider fixtureとsynthetic A/B Adapterは検査済みです。実Providerの交換・廃止・移行を伴うOperational / Outcome Evidenceはありません。

### V5 Uncertainty Preservation

Unknown / Conflict / Withheld / partial knowledge、Adapter missing→unknownを検査済みです。実際の誤判断回避へ寄与したOutcome Evidenceはありません。

### V6 Human / AI Readability

semantic question一致とlight/audit Projectionをstatic harnessで確認しました。実利用者・異なるAI実装によるOperational / Adoption Evidenceはありません。

### V7 Progressive Explicitness

low-impactでは軽量、high-impactではauditを要求するharnessを検査しました。実運用でのimpact判定、入力負担、見落とし率は未検証です。

### V8 Execution Independence

semantic runtime、Provider Adapter、Payload Sourceをexecution / provider / storage mechanicsから分離しています。異なるproduction Execution / Storage Provider間で意味を維持したEvidenceはありません。

## 13. current Planとの関係

current registryはADR-0001〜0024、ISSUE-000001〜000041を管理します。

- ISSUE-000001〜000020: Resolved
- ISSUE-000021: Deferred — design history provenance逐語監査
- ISSUE-000022〜000041: Resolved

ISSUE-000021はhistorical chat export等が利用できる場合の再監査留保であり、current Product / Runtimeのblockerではありません。

historical M47 closure後のPlan integrity:

- commit: `7aaa1280da01810c212b83de28b0741f5adccd2b`
- Run `33461793246`: **success**

v0.1.0 Release Readiness closureでは、ISSUE-000041とdocument review registryを含めたPlan integrityもsuccessしています。

## 14. CoverageをKPIにしない

次の読み方をしません。

- REQリンクが多いValue Axisほど重要である。
- Contractやfixtureが多いほどProduct Valueが高い。
- CIが多く通るほど利用者価値が高い。
- Executable Evidenceが増えればOperational / Outcomeも自動的に増える。
- IssueがResolvedなら、その対象がすべてVerifiedである。

追跡の目的は、**どこまで確認したかと、どこから先をまだ主張してはいけないかを見失わないこと**です。

## 15. 更新規則

Product Value、REQ、SCN、ADR、Architecture、Contract、Profile、runtime、Provider Adapter、Payload Source、Projection Evaluation、Release Readiness、Evidence stateのいずれかが変わった場合、この文書を必要に応じて更新します。

下位実装の都合に合わせてProduct Valueを後付けで変更しません。上位仮説を変える必要がある場合はADR-0018の再基線化規則に従います。

## 16. 自然な日本語ドラフト

V1〜V8、REQ-0001〜0022、SCN-0001〜0017、ADR-0001〜0024、current Architecture、4 Semantic Contract family、2 Representation Profile、first semantic runtime、Verifier Registry、synthetic Payload Source、synthetic Provider Adapter、V6/V7 Projection evaluation、ISSUE-000034 recovery closure、ISSUE-000041 Release Readiness closure、actual CIへ戻って追跡を再確認しました。その後、Issue closureとVerification、readiness-scoped Executable EvidenceとRelease Evidence、Design / Executable / Release / Operational / Adoption・OutcomeのEvidence強度を混同せず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
