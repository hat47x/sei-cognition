# ISSUE-000079: SEI Application PlaneのTEI-first Reference Adoptionを検証する

Status: **Open**  
Priority: **1**  
Related ADRs: **ADR-0014, ADR-0021, ADR-0028**  
Updated: 2026-09-18

## Goal

2026-09-18のProduct Shape更新で、SEIのWork / Interaction Surface、Projection / Review Surface、Evidence / Governance Surface等のApplication Planeは、個別frameworkで機能を増やす前にTEIを第一候補として検討する方針になった。

本Issueでは、この方針を「TEIを使うこと自体が正しい」という実装規則へ短絡せず、次をReference Adoptionとして検証する。

> **SEIのApplication PlaneをTEIで実装すると、SEIのsemantic authorityをTEIへ移さずに、Application開発・変更・保守の負荷を実際に下げられるか。**

特に、ISSUE-000073のresume-first Product Sliceを大きく作り込む前に、read-onlyなResume / Review ProjectionとEvidence / Governance Surfaceを小さいReference sliceとしてTEIへ当て、TEI-firstが実装上のleverageを持つかを確認する。

```text
SEI Product / Semantic authority
  != TEI implementation authority

SEI Application Plane
  -> TEI-first candidate

SEI Cognitive / Semantic Kernel
  -> native / Provider-specific allowed
```

このIssueの成功条件は「SEIをTEIへ多く移すこと」ではない。二重管理を増やさず、change amplificationを減らし、headlessなSEIの中心機能を失わずにApplication Planeを薄くできるかを判断できることである。

## Background

Product ShapeはTEI-firstと全面TEI-native化を区別している。SEI Universal Coreのsemantic meaning、Cognitive Method、local model / classifier / associative cognition、provider-specific low-level integration、performance / device constraintが強いkernel処理、headless / embedded pathはTEIへ無理に移さない。

したがってISSUE-000074の`teiprobe`も本Issueの移管対象ではない。`teiprobe`はprovider-specific low-level integration / Evidence採取であり、Application Planeではない。

TEI current mainにはCanonical Semantic Layer、Application Pattern、Validation、Capability Binding、Plugin / Bundle / Plugin Lock、process Plugin runtime、Target-neutral Presentation / Interaction設計、Source Index / Provenance等が存在する。一方、Gate BはNot Ready、Gate CはBlocked、first Web Targetは未実装 / Evidence未取得である。

SUI SensemakingについてはTEI側ISSUE-000052と`plan/SUI_REFERENCE_ADOPTION_DESIGN_2026-09.md`でReference Adoptionが始まっている。そこで採った次の原則をSEIでも再利用する。

```text
encapsulation before translation

Existing TEI
or reusable Plugin / Adapter / Capability
or Native application asset
or Core / Product Requirement candidate
```

SUIのEvidenceをSEIへ流用はしない。ただし、SUIで見えたReview / Diff Visualization等のPlugin候補を、SEIという第二ApplicationでもPressureする材料にはできる。

## Product上の不確実性

1. TEIのApplication / Projection / Target境界で、SEIのresume-first Surfaceをsemantic duplicationなしに表現できるか。
2. Decision当時のbasisとlater change、Unknown / Conflict、Recommendation / Decision等の意味差を、TEI Coreへ同化させずApplication data / Projectionとして扱えるか。
3. Resume / Review Projectionの変更で、native実装よりchange amplificationを減らせるか。
4. Evidence / Governance SurfaceをTEIへ寄せても、Evidenceの高さやauthorityをUI都合で平坦化しないか。
5. TEIを外してもCanonical Semantic Access、Cognitive Method integration、headless read / write pathを維持できるか。
6. 不足をExisting TEI / reusable extension / Native SEI / TEI Product gap candidateのどれかへ説明可能に分類できるか。
7. SUI側のReview / Diff Visualization候補が、SEIを第二Applicationとしても再利用価値を持つか。
8. TEI-firstによってadapter / projection / sourceの二重管理が増える失敗を検出できるか。

## TEI Gateとの関係

Stage 0ではmapping、read-only Reference projection、fixture / change challenge準備、source authority固定、gap分類、Plugin候補比較を先に行う。未成立のTarget / Acceptance機能をproduction-readyとして扱わない。

```text
TEI mapping / Reference probe
  != production SEI Application Plane
  != Gate C Evidence
  != human usability Evidence
```

## Authority strategy

### Stage 0 — SEI sourceを維持する

最初のReferenceでは、SEIのcurrent canonical semantic stateと既存Product / Evaluation fixtureをsource ownerとして維持する。

```text
SEI canonical state / existing fixture
  = authoritative source

TEI Reference mapping / Projection
  = derived / read-only
```

TEI側に第二のauthoritative sourceを作らない。「TEIで表示できる」ことと「TEIが正本になった」ことを同一視しない。

### Stage 1 — authority migration候補

Referenceで十分なleverageが確認された場合だけ、対象surfaceごとにauthority migrationを検討する。その場合もsource owner before / after、migration transform、roundtrip / equivalence Evidence、rollback、headless fallbackを明示する。

## 初期マッピング

| SEI concern | TEI初期分類 | 境界 |
|---|---|---|
| Resume / Orientation Projection | Existing TEI候補 | read-only ProjectionとしてPressureする |
| Decision basis / later change | Existing TEI + SEI domain data | 意味はSEIが所有する |
| Unknown / Conflict | Existing TEI + SEI domain data | TEI Core kindへ昇格させない |
| Recommendation / Decision差分 | Existing TEI / Review extension候補 | semantic authorityはSEIに残す |
| Evidence / Governance review | Existing TEI / reusable extension候補 | Evidence高さを保持する |
| semantic change preview | TEI Acceptance候補 / Deferred | Gate readiness前にmutation authorityを移さない |
| canonical commit / stale-write guard | Native SEI | REQ-0023 / SCN-0019をUIへ委譲しない |
| AI / Cognitive Method execution | Native / Capability Binding | TEIはMethod authorityではない |
| `teiprobe` / Provider integration | Native SEI | low-level integrationでありApplication Plane外 |
| headless canonical access | Native SEI | TEI Applicationなしでも維持する |
| settings / policy editor | Existing TEI候補 | structured authoringをPressureする |
| Review / Diff Visualization | reusable extension候補 | SUIに続く第二Applicationで再利用性を検証する |

## 最初のReference slice

### Challenge A — Resume / Review Projection

current canonical fixtureから、current concern / question、Decision、Recommendation、historical basis、unresolved、changes since decision、audit detailへの入口をread-onlyでProjectionする。

確認すること:

- 同じ意味をTEI側で再定義せずProjectionできるか。
- Projection変更でSEI canonical schemaを書き換えずに済むか。
- later informationをhistorical basisへ混ぜない停止線を維持できるか。
- Light / Auditの段階的詳細化をApplication Pattern / Projectionとして扱えるか。
- current native projectionと比較して、変更箇所・同期箇所が減るか。

### Challenge B — Evidence / Governance Surface

ISSUE-000073 / 000078のhuman-review Evidence bundle、ISSUE-000074のderived TEI Evidence report等を、意味を変えずにreviewするread-only SurfaceをPressureする。

- Design / Executable / Release / Operational / Adoption・Outcomeの高さを一種類へ潰さない。
- human observationとsemantic auditを別layerとして表示する。
- source / digest / provenanceを見せつつ、secretやprovider-specific raw diagnosticを通常Evidenceへ混ぜない。
- SUI側Review / Diff Visualization候補と共通責務を抽出できるかを見る。

### Challenge C — semantic change preview / commit

Stage 0の必須実装にはしない。TEIのAcceptance / Target / Application execution境界が十分なEvidenceを持った後にPressureする。TEI UIが成立しても、canonical mutation authority、stale-write guard、atomic commit integrityはSEI側の意味境界として維持する。

## change amplificationの比較

TEI採用率や生成コード量を成功指標にしない。同じ意味変更についてnative SEI projectionとTEI Referenceで、hand-written code / config / schema、file / layer / source owner数、重複意味、manual synchronization、派生可能性、regression fixture、Target固有code、Adapter負担、authority ambiguity、rollback、headless fallbackへの影響を比較する。

中心指標はSUIと同じく**change amplification**とする。

```text
one semantic change
  -> how many owners / layers / files / tests must move together?
```

TEI記述が増えても第二の正本やmanual synchronizationが増えるなら成功とはしない。

## Plugin / extension discovery

不足は、Existing TEI → reusable Plugin / Adapter / Capability → Native SEI → TEI Core / Product Requirement candidateの順で扱う。Core candidateへ進む前に、1〜3で解けない理由とSEI以外でも意味差が再現するEvidenceを要求する。

SUI側のReview / Diff Visualizationは有力候補だが、SUIとSEIの双方で役立つだけで直ちにTEI Coreへ入れない。Core meaningを増やさずextensionで表現できるならextensionに留める。

## ISSUE-000073との関係

```text
ISSUE-000073
  = Product Interaction / human value

ISSUE-000079
  = Application implementation strategy

073 human outcome
  != 079 TEI adoption result
```

本Issueは073のH1 / H2 human reviewをブロックしない。headless / native prototypeでProduct Value実証を続けつつ、広いUI実装へ進む前にTEI Referenceで実装戦略をPressureする。

## ISSUE-000072 / 000074との関係

ISSUE-000072 / 000074はTEIを外部Capability Providerとして扱う実行・Evidence境界である。本IssueはTEIをSEI Application Planeのimplementation layer候補として扱う。

```text
TEI Provider compatibility
  != TEI Application Plane suitability

actual TEI binary Evidence
  != SEI UI / Projection leverage
```

相互のPASSを流用しない。

## Non-goals

- SEI Universal CoreをTEI Coreへ移すこと。
- SEI domain vocabularyをTEI Canonical kindへそのまま追加すること。
- SEIを一括rewriteすること。
- TEIへの移管率100%を目標にすること。
- headless SEIを廃止すること。
- Cognitive Method / classifier / local model / associative cognitionをTEI-nativeへ再実装すること。
- provider-specific low-level integrationをTEI Applicationへ押し込むこと。
- TEI GateをSEI都合で飛び越えること。
- 一つのReference成功だけでTEIを全OSSの必須implementation layerとすること。
- TEI-first方針だけを根拠にStable Requirement / Universal Contract fieldを増やすこと。

## Evidence ladder

```text
Product Shape policy
  → mapping / Reference Design
  → read-only Reference slice
  → change-amplification comparison
  → extension / native / gap classification
  → migration decision
  → 必要ならauthority migration
```

```text
mapping complete
  != TEI implementation proven

Reference projection works
  != development burden reduced

development burden reduced
  != human usability improved

TEI migration selected
  != SEI semantic authority moved
```

## Resolution conditions

1. Application Plane concernのmappingがcurrent Product Shape / ISSUE-000073と整合している。
2. source authorityをSEI側に保持したread-only Resume / Review Reference sliceがある。
3. Evidence / Governance Surfaceについて少なくともmappingまたはReference sliceがある。
4. 同一change challengeについてnative / TEI Referenceのchange amplificationを比較できる。
5. 二重管理、manual synchronization、authority driftが増えていないことを確認できる。
6. gapをExisting / reusable extension / Native SEI / TEI Core candidateへ分類できる。
7. reusable extensionを主張する場合、SEI以外のApplicationでも再利用性をPressureしたEvidenceがある。なければcandidateに留める。
8. TEIを外してもheadless canonical accessとCognitive Method / Provider integrationを維持できる。
9. Product Value / Requirementを再監査し、新Stable Requirement、既存Requirement統合、No Change / Deferredのいずれかを明示する。
10. SEI Application Planeをbroad / incremental / limited / deferredのどれでTEIへ寄せるかを明示する。

## 2026-09-18 Stage 0 design baseline

`plan/SEI_TEI_REFERENCE_ADOPTION_DESIGN_2026-09.md`を追加し、最初のread-only Referenceのsource / oracle / temporal stoplineを固定した。

重要な判断は、既存fixtureの`conditions.C_sei_resume.surface_text`をTEI Referenceへの入力にはせず、`scenario`側を入力、`C_sei_resume.surface_text`を期待Projectionのoracle、`reference_state`をsemantic audit oracleとして分けることである。

これにより、SEI側で生成済みのResume ProjectionをTEIで再表示するだけの自己循環を避け、Recommendation / Decision、historical basis、unresolved、post-decision changeをTEI Application / Projection境界でどこまで重複なく導出できるかをPressureできる。

TEI current Application Pattern v1の`record` / `browse`へResumeを無理に押し込まず、新しい`resume` / `review` Pattern Kindも先取りしない。Stage 0はReference-local adapter / Projectionから開始し、複数Applicationで同じ不足が再現した場合だけreusable extensionやTEI Product gapを検討する。

current state:

```text
Stage 0 mapping / source authority / oracle design
  = available

Stage 0 source-freeze manifest / validator source
  = available

Stage 0 source-freeze current-content validation
  = PASS（evaluation-only）

TEI-side Reference tool source
  = available（TEI ISSUE-000054 / PR #686）

Reference Executable Evidence
  = Scoped Evidence available
  = Go 1.23.2 targeted go test / go vet PASS

TEI Application Pattern / Target adoption
  = Not Yet Verified

native vs TEI change-amplification comparison
  = Change 1 observed
  = semantic compatibility observed / TEI reduction not observed
  = Stage 0 snapshot sync overhead remains
```
## 2026-09-18 source-freeze execution boundary

Stage 0のReference入力を第三schemaへ変換せず固定するため、次を追加した。

- `evaluation/tei-reference-adoption/stage0_resume_review_source_freeze_v1.json`
- `evaluation/tei-reference-adoption/validate_stage0_resume_reference.py`
- `evaluation/tei-reference-adoption/test_validate_stage0_resume_reference.py`
- `evaluation/tei-reference-adoption/stage0_resume_review_source_freeze_validation_20260918.json`

manifestは既存fixtureのinput / oracle JSON pointerとsource identityだけを保持する。Decision Continuityのdataを複製したhandoff payloadではない。current fixture blob `6354fce0...`、bytes SHA-256 `43ce2ead...`を固定し、Recommendation / Decision、basis / unresolved、post-decision idsの参照整合とinput / oracle非混入を検査する。

GitHub connectorから取得したcurrent manifest / fixtureを同一規則で評価した結果はPASSで、validation errorsは0件だった。ただしPython self-test actual executionとTEI-side Reference tool executionはこのreceiptでは未検証である。

```text
source freeze PASS
  != TEI Reference tool PASS
  != change amplification reduction
  != Product Value
```

## 2026-09-18 TEI Stage 0 executable result

TEI側では、`research/sei-reference-adoption`の一つのworkstream branchでStage 0を実装し、PR #686として`main`へ統合した。

- TEI Issue: `plan/issue/000054-sei-reference-adoption-resume-review.md`
- TEI Design: `plan/design/SEI_REFERENCE_ADOPTION_STAGE0_DESIGN.md`
- frozen Reference snapshot: `reference/sei-adoption/decision-continuity-counterfactual-001.json`
- checker: `tools/sei-resume-reference`
- PR: #686
- merged TEI commit: `0d1c068d6fc9e9faf444c1a47eaa071eee61b272`

Go 1.23.2でtargetedに、

```text
gofmt -d
  -> 0 bytes

go test ./tools/sei-resume-reference
  -> PASS

go vet ./tools/sei-resume-reference
  -> PASS
```

を確認した。

checkerは`scenario`からRecommendation / Decision、historical basis、unresolved、post-decision changeを導出し、`C_sei_resume`と`reference_state`をoracleとして意味境界を監査する。historical basisはObservation roleへ限定し、Recommendation / Unknown等へのrole confusionもfail closedにした。

```text
source-freeze validation PASS
  + TEI Reference checker targeted PASS
  != TEI Application Pattern adoption
  != Target / Gate C Evidence
  != change amplification reduction
  != SEI Product Value / human usability
```

PR merge後、TEIの継続branch `research/sei-reference-adoption`はcurrent `main`へ戻し、同一workstreamの派生branchを増やしていない。

## 2026-09-18 Change 1 exact-blob Evidence

TEI側のChange 1結果は、`hat47x/tei-platform` mainへ統合済みである。

- TEI main merge: `981c93bc5f3455476885f1c34ec0f9af8b2667c3`
- TEI Evidence: `reference/sei-adoption/change1-execution-20260918.json`
- Evidence blob: `1b68634a7d21f2a9e912ba3899847c9ba6985d84`
- Reference implementation blob: `a62c0a10ac32d3c84156b74cec57b83f12866dfb`
- test blob: `7e06b9e289fa00bb19345240146844abad8a5989`
- frozen fixture blob: `6354fce0a01093cb5545ed6bb9730aceb3b20023`

exact blobをGo 1.23.2隔離環境へ再構成し、`gofmt` 0差分、9/9 test PASS、`go vet` PASS、tool実行時semantic audit全項目trueを確認した。Change 1ではproduction mapping code変更は0、新semantic kind / Application Pattern kind追加も0だった。

一方、native SEIの`ChangeReviewProjection`も同型changeを既存設計で扱えるため、TEIによるchange-amplification reductionは観測されていない。またStage 0 frozen snapshotのcross-repo同期は追加負担として残る。

```text
semantic compatibility
  = observed

TEI leverage over native SEI
  = not observed

TEI Core / new Pattern need
  = not observed
```

SEI側のcross-repository receiptは`evaluation/tei-reference-adoption/change1_tei_reference_evidence_20260918.json`へ固定する。

## 2026-09-18 Change 2 Gate boundary

Projection-onlyなChange 2についてTEI current Gateを再監査した結果、Product behaviorとしての実装はdeferする。

TEI current stateはGate B Not Ready、Gate C Blocked、First Web Target未実装で、complete Target-neutral Presentation IRも未成立である。この状態でSEI Reference専用のordering / Presentation helperを追加すると、既存TEI能力のleverageではなく、比較のために発明したsurrogate layerを測ることになる。

TEI側ではこの停止線を `reference/sei-adoption/change2-presentation-gate-boundary-20260918.json` としてmain `1683182b730a41120f56da00e396220c6d5f7a13`へ統合した。SEI側link receiptは `evaluation/tei-reference-adoption/change2_presentation_gate_boundary_20260918.json` に置く。

```text
Change 2 Product behavior
  = deferred by current Gate

TEI failure
  = not observed

TEI Presentation leverage
  = not observed

new Pattern / Core gap
  = not observed
```

再開条件は、Gate B Ready + Handover Baseline固定 + First Web Target着手、またはSEIと独立した根拠でtarget-neutral Presentation機構が成立することとする。

## 2026-09-18 Challenge B mapping result

Evidence / Governance SurfaceについてTarget behaviorを作らずmapping-only監査を行い、TEI側結果をmain `eb587a5aed06d24d6c813d2db4dd40d13286b5ca`へ統合した。

- TEI mapping: `reference/sei-adoption/challenge-b-evidence-governance-mapping-20260918.json`
- mapping blob: `5d52463c0fd6cf571c83d47a0013dcbdf1e4b097`
- SEI link receipt: `evaluation/tei-reference-adoption/challenge_b_evidence_governance_mapping_20260918.json`

再利用できるのは、non-Canonical Evidence artifact、subject / revision / build / context trace、fingerprint、source provenance、secret-safe collection、Evidence natureの非代替性といった**generic Evidence mechanics**である。

一方、

- human reviewer observation / semantic auditの意味分離
- review開始条件とreveal順序
- authorship / prior exposure declaration
- SEI固有のEvidence高さ
- Product Value / Stable Requirementへの昇格可否

はSEI Governanceとして残す。TEIが将来表示しても意味authorityは取得しない。

Review / Diff VisualizationはSUIとSEIで共通需要が見えるためreusable extension候補ではあるが、Target Evidenceがない現段階ではcandidateに留める。

### 現時点の採用姿勢

Stage 0全体から、現時点では**limited / Reference-local**とする。

```text
TEI-first
  = candidate policy remains

current actual adoption
  = limited to Reference-local validation / generic Evidence mechanics

broader SEI Application Plane migration
  = deferred until valid Target evidence
```

理由は、Change 1でsemantic compatibilityは確認できたもののnative SEI比の負荷低減は観測されず、frozen snapshot同期負担が残り、Change 2はcurrent Gateでは正当なPresentation比較を実行できないためである。

この判断から新Stable Requirement、Universal Contract field、Application Pattern kind、TEI Core gapは追加しない。

## Next step

Challenge Bのmapping-only監査まで完了した。次の高情報量Evidenceは、TEI Gate B / Handover / First Targetが実Application PlaneをPressureできる状態になった後のChange 2再開、またはSUI / SEI双方から独立に成立したReview / Diff実装の再利用性Pressureである。

それまではReference専用のUI / Presentation surrogateを増やさず、SEIのheadless / native Product Value検証を独立に継続する。

## Natural Japanese review

Product ShapeのTEI-first方針を「TEIを使わなければならない」という規範へ変換していない。SUI Reference Adoptionの設計知見を再利用しつつ、SUIのEvidenceをSEIへ流用せず、SEI自身のresume-first InteractionとEvidence / Governance SurfaceでTEIの適性を反証可能にした。

SEI semantic authority、TEI implementation authority、Cognitive Method / Provider、headless accessを分離し、TEIを外したときにSEIの中心意味まで失う構造を避ける。TEIで不足が見つかった場合も、SEI一件だけを理由にCoreを拡張せず、Existing → reusable extension → Native → cross-application Evidenceを伴うCore candidateの順で扱う。

本IssueはISSUE-000073のhuman value検証を置き換えず、広いApplication実装へ進む前のimplementation strategy validationとして並行する。
