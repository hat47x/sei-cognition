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

TEI-side Reference tool source
  = Not Yet Implemented

Reference Executable Evidence
  = Not Yet Verified

native vs TEI change-amplification comparison
  = Not Yet Observed
```
## Initial next step

最初の実装はWeb UI完成ではなく、**Challenge Aのread-only Resume / Review Reference**とする。

入力は既存SEI canonical / evaluation fixtureからのdeterministic handoff projectionを優先し、TEI移管専用の第三schemaを先に発明しない。

最初に確認するのは「同じ画面を作れたか」ではなく、**一つの意味変更が、SEI native実装より少ないowner / layer / manual synchronizationでApplication Surfaceへ反映できるか**である。

## Natural Japanese review

Product ShapeのTEI-first方針を「TEIを使わなければならない」という規範へ変換していない。SUI Reference Adoptionの設計知見を再利用しつつ、SUIのEvidenceをSEIへ流用せず、SEI自身のresume-first InteractionとEvidence / Governance SurfaceでTEIの適性を反証可能にした。

SEI semantic authority、TEI implementation authority、Cognitive Method / Provider、headless accessを分離し、TEIを外したときにSEIの中心意味まで失う構造を避ける。TEIで不足が見つかった場合も、SEI一件だけを理由にCoreを拡張せず、Existing → reusable extension → Native → cross-application Evidenceを伴うCore candidateの順で扱う。

本IssueはISSUE-000073のhuman value検証を置き換えず、広いApplication実装へ進む前のimplementation strategy validationとして並行する。
