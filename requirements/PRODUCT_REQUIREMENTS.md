# SOZA Product Requirements

更新日: 2026-09-05
状態: **Current Product Requirements Baseline**

## 1. この文書の位置づけ

この文書は、現在のSOZA Product Valueを満たすために必要なProduct Requirementの正本入口です。

過去candidateの`SOZA-PR-*`や`SOZA-NFR-*`をそのまま復元したものではありません。旧文書の意味核を参照しつつ、`SOZA_VALUE_MODEL.md`のV1〜V8、現在のProduct Principles、Accepted ADRへ戻って再構成しています。

Requirementの意味上の採用状態とEvidenceの高さは分けます。

```text
Requirement Accepted
  != Design Evidence Satisfied
  != Executable Evidence Satisfied
  != Release Evidence Satisfied
  != Operational Evidence Satisfied
  != Adoption / Outcome Evidence Satisfied
```

actual repositoryには現在、Product / Plan / Requirementsだけでなく、Reference Architecture、5 Semantic Contract family、JSON Schema、31 fixture、Representation Profile、Go semantic runtime、Cognitive Method typed runtime、synthetic Provider Adapter、V6/V7 Projection evaluation、end-to-end Semantic Product Journey harness、各種checker / CIが実体化されています。

ただし、Executable EvidenceはRequirementごとに確認範囲が異なります。fixtureやruntime sliceで一部を直接検証できたRequirementだけを`Partially Satisfied`等として扱い、production Provider integration、Release、Operational、Adoption / Outcome Evidenceへは広げません。

## 2. Current Requirement一覧

| ID | 要求 | 主なValue Axis | Status | Design Acceptance |
|---|---|---|---|---|
| REQ-0001 | 耐久的な意味の連続性 | V1, V3, V4, V8 | Accepted | Satisfied |
| REQ-0002 | 不確実性と認識状態の保持 | V2, V5 | Accepted | Satisfied |
| REQ-0003 | 出所・発見経路・派生の分離 | V1, V2, V3 | Accepted | Satisfied |
| REQ-0004 | Cognitive Methodの独立性 | V3, V8 | Accepted | Satisfied |
| REQ-0005 | Decisionの歴史的再構成 | V1, V3, V5 | Accepted | Satisfied |
| REQ-0006 | 提案・判断・権限・実行の分離 | V2 | Accepted | Satisfied |
| REQ-0007 | Capability / Providerの中立性 | V4, V8 | Accepted | Satisfied |
| REQ-0008 | 判断経路とResponsibilityの来歴保持 | V1, V2, V3 | Accepted | Satisfied |
| REQ-0009 | Revision / Supersessionの完全性 | V1, V3 | Accepted | Satisfied |
| REQ-0010 | Progressive Semantic Explicitness | V6, V7 | Accepted | Satisfied |
| REQ-0011 | Projectionを意味上の正本にしない | V6, V8 | Accepted | Partially Satisfied |
| REQ-0012 | Bounded CollaborationとSelective Disclosure | V4, V5, V8 | Accepted | Satisfied |
| REQ-0013 | actor種別からAuthority等を推定しない | V2, V4 | Accepted | Satisfied |
| REQ-0014 | 未解決残差と再開条件の保持 | V1, V3, V5 | Accepted | Partially Satisfied |
| REQ-0015 | private chain-of-thoughtへ依存しない | V2, V6, V8 | Accepted | Satisfied |
| REQ-0016 | ObservationとInterpretationを区別可能にする | V2, V5 | Accepted | Satisfied |
| REQ-0017 | Responsibilityを文脈に結び付ける | V1, V2 | Accepted | Satisfied |
| REQ-0018 | Storage実装から意味を独立させる | V1, V3, V8 | Accepted | Satisfied |
| REQ-0019 | 人間とAIの双方が意味を読める | V6 | Accepted | Partially Satisfied |
| REQ-0020 | Evidenceを超える達成主張をしない | V1, V6 | Accepted | Satisfied |
| REQ-0021 | Realization / Executionを交換可能にする | V4, V8 | Accepted | Satisfied |
| REQ-0022 | Provider-neutralなCapability Observation | V1, V2, V4, V5, V8 | Accepted | Satisfied |

`Partially Satisfied`はRequirement自体が未確定という意味ではありません。意味境界は採用済みですが、Projectionの実利用、再開条件の具体化、人間向け可読性の実利用Evidence等、Design上まだ厚くできる部分が残っていることを示します。

---

## REQ-0001 — 耐久的な意味の連続性

**Status:** Accepted  
**Type:** Semantic / Interoperability  
**Value:** V1, V3, V4, V8  
**Related Scenarios:** SCN-0003, SCN-0005, SCN-0008, SCN-0014, SCN-0018  
**Related ADRs:** ADR-0003, ADR-0007, ADR-0008, ADR-0014

### Requirement

AIモデル、Prompt、Skill、実装言語、UI、Storage、Capability Provider、Execution Providerが変わっても、SOZAが耐久的意味として保持するIntent、Observation、Decision、Responsibility、Provenance等を、別の意味へ黙って読み替えることなく引き継げなければならない。

### Rationale

SOZAの価値は現在の実装方式ではなく、技術が入れ替わっても判断の意味と来歴を読み直せることにあるため。

### Scope / Non-goals

すべての内部表現やwire formatを永久互換にすることは要求しない。必要なのはsemantic continuityであり、representation migration自体は許容する。

### Current Evidence

- Design: **Satisfied**
- Executable: **Partially Satisfied** — Semantic Interchange、Logical Reference / Exact Binding metadata、Decision / Capability / Cognitive Methodのcurrent fixtureとruntimeで、意味を分けたまま読み込む境界を確認した。SCN-0018 harnessではInterchange loaderを通るProduct Journeyとhistorical Decision basis非改変も確認した。さらに固定model artifact下でOllama `0.32.13` / `0.32.14`をactualに交換し、revisionごとのExact Binding、先行Application非改変、portable reconstructionを確認した。Storage migration、production Provider交換、任意runtime互換性は未検証。
- Release: **Not Yet Verified**
- Operational: **Not Yet Verified**
- Adoption / Outcome: **Not Yet Verified**

## REQ-0002 — 不確実性と認識状態の保持

**Status:** Accepted  
**Type:** Semantic  
**Value:** V2, V5  
**Related Scenarios:** SCN-0001, SCN-0003, SCN-0011, SCN-0016, SCN-0018  
**Related ADRs:** ADR-0002, ADR-0010, ADR-0019

### Requirement

Observation、Unknown、Conflict、Hypothesis、Evidence Use、Assurance等の異なる認識状態を、単一のtrue / false、最新値、confidence score、availability flag等へ黙って平坦化してはならない。

`not observed`、`unknown`、`conflicting`、必要な場合の`withheld`を、意味上区別して扱える余地を維持しなければならない。

### Rationale

不確実性を消すと、Decision時点で何が分かっていなかったかを後から再構成できなくなるため。

### Current Evidence

- Design: **Satisfied**
- Executable: **Partially Satisfied** — F4 / F7、partial-knowledge interchange、Decision unresolved fixtureで`unknown`、`withheld`、未解決参照を保持できる。SCN-0018 harnessでは未解決参照をDecision後も保持し、後続reviewへ入力できるsynthetic pathを確認した。Inquiry全体のproduction lifecycleは未検証。
- Release: **Not Yet Verified**
- Operational: **Not Yet Verified**
- Adoption / Outcome: **Not Yet Verified**

## REQ-0003 — 出所・発見経路・派生の分離

**Status:** Accepted  
**Type:** Semantic  
**Value:** V1, V2, V3  
**Related Scenarios:** SCN-0001, SCN-0005, SCN-0016  
**Related ADRs:** ADR-0007, ADR-0011, ADR-0017

### Requirement

原資料やObservationの出所、資料を発見した経路、その資料に対するInterpretation、そこから派生したArtifact、Cognitive Method Application等を、必要な場面で区別して追跡できなければならない。

### Rationale

「どこから来た情報か」と「どのように見つけ、どう解釈・加工したか」は異なる来歴であり、一つに潰すとEvidenceの意味を誤読しやすいため。

### Current Evidence

- Design: **Satisfied**
- Executable: **Partially Satisfied** — Capability Observationでprovenance / mapping provenanceを読み込め、Cognitive Method Applicationのinput / output / residual Referenceもtyped runtimeで保持できる。Discovery routeや一般的Derivationを含むproduction経路は未検証。
- Release: **Not Yet Verified**
- Operational: **Not Yet Verified**
- Adoption / Outcome: **Not Yet Verified**

## REQ-0004 — Cognitive Methodの独立性

**Status:** Accepted  
**Type:** Semantic / Interoperability  
**Value:** V3, V8  
**Related Scenarios:** SCN-0005, SCN-0015, SCN-0018  
**Related ADRs:** ADR-0017, ADR-0025

### Requirement

Cognitive Methodは、現在のPrompt、Skill、model program、code-assisted tool、人間手順等の一つのRealizationと同一視せず、手続き上の意味を独立して保持できなければならない。

Method Applicationの意味は、後からRealizationが変更されても当時の適用記録として再構成できなければならない。

### Rationale

SOZAが保持すべきなのは特定のPromptや実装ではなく、どの方法で資料を探索・比較・統合・検査したかという意味だからである。

### Current Evidence

- Design: **Satisfied**
- Executable: **Partially Satisfied** — `soza.cognitive-method/v1alpha1`、C1〜C8 fixture、negative / unknown-version boundary、Go typed runtimeによりMethod Definition / Realization / Applicationを分離してread / validate / reconstructできる。SCN-0018 harnessでもMethod ApplicationをRecommendation / Decisionとは別recordとして接続する。固定KJ Atlas / Ollamaではactual model artifact交換とruntime revision交換を行い、後続Application追加後も先行Applicationを保持した。別Method、人間手順、production Realizationへの交換は未検証。
- Release: **Not Yet Verified**
- Operational: **Not Yet Verified**
- Adoption / Outcome: **Not Yet Verified**

## REQ-0005 — Decisionの歴史的再構成

**Status:** Accepted  
**Type:** Semantic  
**Value:** V1, V3, V5  
**Related Scenarios:** SCN-0003, SCN-0009, SCN-0010, SCN-0016, SCN-0018  
**Related ADRs:** ADR-0008, ADR-0010, ADR-0011

### Requirement

Decisionについて、少なくともその時点のIntent / Goal文脈、明示的に利用したbasis、Recommendation、Rationale、Constraint、残っていたUnknown / Conflict、必要なAuthority / Responsibility、重要な可変参照Artifactを後から再構成できなければならない。

後から新しいEvidenceが追加されても、過去Decisionを現在版へ黙って書き換えてはならない。

### Rationale

最終Outcomeだけでは、なぜそのDecisionが行われたのか、どの不確実性を受け入れたのかを検証できないため。

### Current Evidence

- Design: **Satisfied**
- Executable: **Partially Satisfied** — Decision basis / recommendation / unresolved / rationale / lineageをruntimeへ読み込み、F6で当時のCapability Observationへのexact basisを保持できる。SCN-0018 harnessではexecution後Observationをhistorical basisへ混入させず、execution success後もDecision statement / basisを非改変のまま保持することを確認した。Authority Providerや実組織Decisionのproduction再構成は未検証。
- Release: **Not Yet Verified**
- Operational: **Not Yet Verified**
- Adoption / Outcome: **Not Yet Verified**

## REQ-0006 — 提案・判断・権限・実行の分離

**Status:** Accepted  
**Type:** Semantic / Constraint  
**Value:** V2  
**Related Scenarios:** SCN-0002, SCN-0004, SCN-0009, SCN-0011, SCN-0018  
**Related ADRs:** ADR-0010, ADR-0014, ADR-0016

### Requirement

Recommendation、Decision、Authority / Authorization、Action Intent、Provider Execution、Execution Receipt、Business Outcomeを、必要な場面で別の意味として扱えなければならない。

```text
Recommendation != Decision != Authority != Action Intent != Execution
```

一つの段階が存在することから、後続段階が成立したと自動推定してはならない。

### Rationale

AIの提案能力や自動化率が高まっても、責任線と統制可能性を失わないため。

### Current Evidence

- Design: **Satisfied**
- Executable: **Partially Satisfied** — Recommendation without Decisionを正常に読み込み、Decision recordへの`authority`埋め込みをSchema / runtime双方で拒否できる。SCN-0018 harnessではRecommendation identityをDecisionとして流用するcaseを拒否し、execution successがhistorical Decision自体を書き換えないことも検査した。実Authorization / Action executionはscope外。
- Release: **Not Yet Verified**
- Operational: **Not Yet Verified**
- Adoption / Outcome: **Not Yet Verified**

## REQ-0007 — Capability / Providerの中立性

**Status:** Accepted  
**Type:** Semantic / Interoperability  
**Value:** V4, V8  
**Related Scenarios:** SCN-0002, SCN-0011, SCN-0014, SCN-0018  
**Related ADRs:** ADR-0012, ADR-0013, ADR-0014, ADR-0019, ADR-0024

### Requirement

Capabilityと、そのCapabilityを提供するProviderを区別し、人間、AI、SaaS、外部組織、TEI、custom code等を同じIntentに対する異質な候補として扱えなければならない。

SOZAとの関係が近いこと、Provider kind、実装上の接続容易性だけを理由に、優先度、信頼、Authorityを自動付与してはならない。

### Rationale

特定Providerへ意味が固定されると、Provider交換時にIntentやDecisionまで壊れ、SOZAの長期価値を失うため。

### Current Evidence

- Design: **Satisfied**
- Executable: **Partially Satisfied** — F5とsynthetic Provider A / Bで異なるProvider-specific inputを同一CapabilityのObservationへ収束させ、Provider identityを分離して保持できる。SCN-0018 harnessでは交換前後Observationが同じCapabilityを参照しつつProviderだけが異なることを検査する。production Provider adapter / interoperabilityは未検証。
- Release: **Not Yet Verified**
- Operational: **Not Yet Verified**
- Adoption / Outcome: **Not Yet Verified**

## REQ-0008 — 判断経路とResponsibilityの来歴保持

**Status:** Accepted  
**Type:** Semantic  
**Value:** V1, V2, V3  
**Related Scenarios:** SCN-0002, SCN-0003, SCN-0009, SCN-0018  
**Related ADRs:** ADR-0004, ADR-0010, ADR-0011

### Requirement

最終状態が同じであっても、利用したCognitive Method、Recommendation、Decision経路、Responsibility、Capability、Provider等が異なる場合、その差を後から確認できなければならない。

### Rationale

Outcomeだけを保存すると、同じ結果へ至った異なる責任線・判断線を区別できず、再評価や監査に必要な意味を失うため。

### Current Evidence

- Design: **Satisfied**
- Executable: **Partially Satisfied** — Decision / Recommendation / Capability / Provider / Cognitive Methodを別構造として保持できる。SCN-0018 collaborative pathではMethod Application側とDecision側のResponsibility Referenceを分離して一続きに検査している。実主体・Authority Providerを含むproduction経路は未検証。
- Release: **Not Yet Verified**
- Operational: **Not Yet Verified**
- Adoption / Outcome: **Not Yet Verified**

## REQ-0009 — Revision / Supersessionの完全性

**Status:** Accepted  
**Type:** Semantic  
**Value:** V1, V3  
**Related Scenarios:** SCN-0003, SCN-0010  
**Related ADRs:** ADR-0003, ADR-0008, ADR-0009

### Requirement

ArtifactやDecisionをlatest-winsだけで更新せず、どの意味が何を根拠として修正、置換、失効、明確化されたかを追跡できなければならない。

storage revision、representation change、content digest changeを、それだけでsemantic revisionと同一視してはならない。

### Rationale

現在の状態だけでは、過去の判断を当時の意味へ戻して再構成できないため。

### Current Evidence

- Design: **Satisfied**
- Executable: **Partially Satisfied** — `revises / supersedes / withdraws`のlineage境界と、same-logical-id lineageにexact endpointが必要であることをvalidator / runtimeで確認した。Storage revisionとのproduction統合は未検証。
- Release: **Not Yet Verified**
- Operational: **Not Yet Verified**
- Adoption / Outcome: **Not Yet Verified**

## REQ-0010 — Progressive Semantic Explicitness

**Status:** Accepted  
**Type:** Non-functional / Constraint  
**Value:** V6, V7  
**Related Scenarios:** SCN-0004, SCN-0013  
**Related ADRs:** ADR-0005

### Requirement

すべての案件へ最大の意味モデルや同一の重い入力手続きを強制してはならない。

影響、不確実性、不可逆性、外部性、法的・組織的責任等に応じて、必要なEvidence、Decision、Authority、binding等の明示性を段階的に厚くできなければならない。

簡略化したUIや入力を利用しても、canonicalな意味を黙って失ってはならない。

### Rationale

意味の厳密さと実務上の使いやすさを両立するため。

### Current Evidence

- Design: **Satisfied**
- Executable: **Partially Satisfied** — V6/V7 Projection evaluationで、low-impactのminimal Decisionにはlight Projectionを許容し、high-impactのrich Decisionではaudit detailを要求するsynthetic policy boundaryを検査した。productionのimpact判定Policy / Profile runtimeや実利用上の入力負担は未検証。
- Release: **Not Yet Verified**
- Operational: **Not Yet Verified**
- Adoption / Outcome: **Not Yet Verified**

## REQ-0011 — Projectionを意味上の正本にしない

**Status:** Accepted  
**Type:** Constraint  
**Value:** V6, V8  
**Related Scenarios:** SCN-0006, SCN-0013, SCN-0018  
**Related ADRs:** ADR-0007

### Requirement

Workspace、canvas、chat sequence、dashboard、matrix、worklist、特定UI layout等のProjectionを、SOZAのCanonical Semantic Authorityとしてはならない。

一つのProjectionを変更・削除しても、耐久的な意味資産を失わない構造を維持しなければならない。

### Rationale

UIや可視化方式は技術進歩や利用目的によって大きく変わるため、それを正本にするとExecution / UI Independenceを失うため。

### Current Evidence

- Design: **Partially Satisfied** — Reference ArchitectureでProjectionをDurable Semantic Coreから分離し、SCN-0006 / 0013 / 0018で意味境界を具体化している。production Projection lifecycleの設計はまだ限定的。
- Executable: **Partially Satisfied** — V6/V7 evaluationで同じcanonical sourceからlight / audit Projectionを再生成してもsource digestを変えないことを確認した。SCN-0018 harnessではProjectionがcanonical recordsと併存してもauthorityにならず、canonical Decisionを除去してProjectionだけを残すcaseをDecision欠落として拒否する。production UI交換は未検証。
- Release: **Not Yet Verified**
- Operational: **Not Yet Verified**
- Adoption / Outcome: **Not Yet Verified**

## REQ-0012 — Bounded CollaborationとSelective Disclosure

**Status:** Accepted  
**Type:** Interoperability / Constraint  
**Value:** V4, V5, V8  
**Related Scenarios:** SCN-0007, SCN-0012  
**Related ADRs:** ADR-0006, ADR-0019

### Requirement

複数主体・複数組織の協働に、各主体の内部world model、credential、判断手続、Provider内部topology等の全量共有を要求してはならない。

必要な情報だけを交換でき、非開示情報が存在する場合は、必要に応じて単純なUnknownと区別して扱える余地を維持しなければならない。

### Rationale

協働のために全内部情報の統合を要求すると、不要な結合、情報漏えい、global ontology化を招くため。

### Current Evidence

- Design: **Satisfied**
- Executable: **Partially Satisfied** — F7とpartial-knowledge fixtureで`withheld`と`unknown`を分離して保持できる。actual federation transport / cross-organization operationは未検証。
- Release: **Not Yet Verified**
- Operational: **Not Yet Verified**
- Adoption / Outcome: **Not Yet Verified**

## REQ-0013 — actor種別からAuthority等を推定しない

**Status:** Accepted  
**Type:** Constraint  
**Value:** V2, V4  
**Related Scenarios:** SCN-0004, SCN-0009, SCN-0018  
**Related ADRs:** ADR-0004, ADR-0012, ADR-0016

### Requirement

人間、AI、service、job、organization、TEI等のactor / provider kindから、信頼、責任、Decision権、Authorization、Assuranceを自動的に推定してはならない。

必要なAuthorityやResponsibilityは、明示的な文脈・Policy・Evidence・参照先によって扱わなければならない。

### Rationale

主体の種類と権限・責任は同じ意味ではなく、kindベースの推定は責任線を歪めるため。

### Current Evidence

- Design: **Satisfied**
- Executable: **Partially Satisfied** — Decision schema / runtimeへAuthority fieldを混入させない境界に加え、SCN-0018 collaborative pathでMethod側とDecision側のResponsibilityを別Referenceとして要求する。actor kindからAuthorityは生成しない。Authorization Providerとの実接続は未検証。
- Release: **Not Yet Verified**
- Operational: **Not Yet Verified**
- Adoption / Outcome: **Not Yet Verified**

## REQ-0014 — 未解決残差と再開条件の保持

**Status:** Accepted  
**Type:** Semantic  
**Value:** V1, V3, V5  
**Related Scenarios:** SCN-0001, SCN-0003, SCN-0016, SCN-0018  
**Related ADRs:** ADR-0010

### Requirement

未解決Question、Unknown、Conflict、反例、保留理由、reopen condition等を、Decisionや処理の完了と同時に失敗情報として捨ててはならない。

後続のInquiry、Decision review、revisionへ戻せる形で外在化できなければならない。

### Rationale

Decisionが行われたことは、すべての不確実性が解消したことを意味しないため。

### Current Evidence

- Design: **Partially Satisfied** — Decision MemoryとReference Architectureで未解決参照の保持は定義済みだが、reopen condition自体のcurrent Universal Contractは固定していない。
- Executable: **Partially Satisfied** — Decision with unresolved fixtureとruntimeで未解決参照を保持できる。SCN-0018 harnessではDecisionの`unresolved_refs`とexecution後の新しいObservationを後続reopen Method Applicationのinputとして引き渡すsynthetic pathを確認した。実業務上のInquiry lifecycle / reopen policyは未検証。
- Release: **Not Yet Verified**
- Operational: **Not Yet Verified**
- Adoption / Outcome: **Not Yet Verified**

## REQ-0015 — private chain-of-thoughtへ依存しない

**Status:** Accepted  
**Type:** Constraint  
**Value:** V2, V6, V8  
**Related Scenarios:** SCN-0005, SCN-0015, SCN-0018  
**Related ADRs:** ADR-0017, ADR-0025

### Requirement

SOZAの耐久的意味、Decisionの再構成、Cognitive Method Applicationの検証を、AIモデルの非公開private chain-of-thoughtの保存・復元へ依存させてはならない。

共有すべきなのは、Observation、Question、Evidence、Recommendation、Rationale、Decision、Method Application等として外在化できる情報でなければならない。

### Rationale

private chain-of-thoughtは共有可能な長期契約ではなく、モデルやProvider交換に耐えないため。

### Current Evidence

- Design: **Satisfied**
- Executable: **Partially Satisfied** — semantic runtimeとCognitive Method Contractは外在化されたDefinition / Realization / Application、input / output / residual Referenceだけから再構成し、private chain-of-thoughtを入力契約として要求しない。SCN-0018 harnessも外在化recordだけを接続する。Method実行品質やproduction AI Providerは未検証。
- Release: **Not Yet Verified**
- Operational: **Not Yet Verified**
- Adoption / Outcome: **Not Yet Verified**

## REQ-0016 — ObservationとInterpretationを区別可能にする

**Status:** Accepted  
**Type:** Semantic  
**Value:** V2, V5  
**Related Scenarios:** SCN-0001, SCN-0011, SCN-0015  
**Related ADRs:** ADR-0002, ADR-0017, ADR-0019, ADR-0024

### Requirement

資料やProviderから観測された内容と、そこから導かれたInterpretation、Hypothesis、Pattern match、Capability interpretation等を、重要な場面で区別できなければならない。

一つのUniversal `Claim`型を必須とすることは要求しない。必要なのは意味差の再構成可能性である。

### Rationale

観測と解釈を混ぜると、推測やadapter mappingが事実として固定され、後続Decisionのbasisを誤読するため。

### Current Evidence

- Design: **Satisfied**
- Executable: **Partially Satisfied** — Capability Observationとmapping provenanceを別要素として保持し、Provider stateをDecisionへ直接昇格させないfixtureを検証した。synthetic Provider A / Bでもstatus interpretationやunit conversionをmappingとして明示し、source state / mapping provenanceを保持したままObservationへ変換できる。一般的なObservation / Hypothesis runtimeは未実装。
- Release: **Not Yet Verified**
- Operational: **Not Yet Verified**
- Adoption / Outcome: **Not Yet Verified**

## REQ-0017 — Responsibilityを文脈に結び付ける

**Status:** Accepted  
**Type:** Semantic / Constraint  
**Value:** V1, V2  
**Related Scenarios:** SCN-0003, SCN-0009, SCN-0018  
**Related ADRs:** ADR-0004, ADR-0010, ADR-0016

### Requirement

ResponsibilityをGlobal Identity ontologyへ統合せず、Decision、Requirement、Capability、Action、Review等の具体文脈で、誰または何が何を担ったかを参照できなければならない。

Responsibilityの記録からAuthorization、Credential、Trust、actor hierarchyを自動推定してはならない。

### Rationale

「誰であるか」と「この文脈で何を担うか」は異なる意味であり、global identityへ統合すると過剰な結合を生むため。

### Current Evidence

- Design: **Satisfied**
- Executable: **Partially Satisfied** — Decision / Recommendation / Cognitive Method Applicationはcontextual responsibility refsを保持できる。SCN-0018 collaborative pathではMethod Application側とDecision側のResponsibilityが別であることを検査する。実Subject / Authority Provider統合は未検証。
- Release: **Not Yet Verified**
- Operational: **Not Yet Verified**
- Adoption / Outcome: **Not Yet Verified**

## REQ-0018 — Storage実装から意味を独立させる

**Status:** Accepted  
**Type:** Interoperability / Non-functional  
**Value:** V1, V3, V8  
**Related Scenarios:** SCN-0008, SCN-0010  
**Related ADRs:** ADR-0007, ADR-0008, ADR-0009

### Requirement

SOZAの意味契約は、特定DB、event sourcing、Git、object store、filesystem等のStorage実装を存在条件としてはならない。

一方で、Storageを交換してもlogical identity、semantic revision、provenance、必要なexact binding、reference integrityを失わない契約を定義できなければならない。

### Rationale

Storage技術の寿命より、SOZAが保持すべき判断・来歴の寿命を長くするため。

### Current Evidence

- Design: **Satisfied**
- Executable: **Partially Satisfied** — runtime read modelはStorage row ID等をsemantic identityとして要求せず、Logical Reference / Exact Bindingを独立して扱う。actual storage migrationは未検証。
- Release: **Not Yet Verified**
- Operational: **Not Yet Verified**
- Adoption / Outcome: **Not Yet Verified**

## REQ-0019 — 人間とAIの双方が意味を読める

**Status:** Accepted  
**Type:** Non-functional  
**Value:** V6  
**Related Scenarios:** SCN-0006, SCN-0013  
**Related ADRs:** ADR-0018, ADR-0020

### Requirement

SOZAの重要なArtifact、Requirement、Decision、Evidence関係は、AIが構造として処理できるだけでなく、人間が意味、理由、未解決点、責任線を確認できなければならない。

人間向けProjectionとmachine-readable representationが異なる場合でも、両者が同じcanonical meaningへ戻れるようにしなければならない。

### Rationale

人間に読めない正本も、AIが再利用できない散文だけの正本も、長期的な共同判断基盤として不十分だからである。

### Current Evidence

- Design: **Partially Satisfied** — human-readable Contract Definitionとmachine-readable Schemaを分け、Contract Definitionをsemantic normative sourceとしている。実利用での人間向けProjection usabilityは未検証。
- Executable: **Partially Satisfied** — Schema / validator / Go runtimeが同じContract fixtureを扱える。V6/V7 evaluationではlight / audit Projectionがmachine-readable canonical sourceとsemantic questions上で一致することを確認した。実利用者による可読性・理解度は未検証。
- Release: **Not Yet Verified**
- Operational: **Not Yet Verified**
- Adoption / Outcome: **Not Yet Verified**

## REQ-0020 — Evidenceを超える達成主張をしない

**Status:** Accepted  
**Type:** Constraint / Non-functional  
**Value:** V1, V6  
**Related Scenarios:** SCN-0010, SCN-0017, SCN-0018  
**Related ADRs:** ADR-0009, ADR-0018, ADR-0020

### Requirement

Design、Executable、Release、Operational、Adoption / Outcome Evidenceを区別し、確認できたEvidenceの高さを超えてRequirement、coverage、release、運用成立性、利用者価値を達成済みと主張してはならない。

未検証はFAILと同じではないが、PASSでもない状態として扱わなければならない。

### Rationale

SOZA自身がEvidenceと判断を扱う基盤である以上、自身の開発状態についてEvidenceを過大主張するとProduct Valueと矛盾するため。

### Current Evidence

- Design: **Satisfied**
- Executable: **Partially Satisfied** — Requirements Registry、Contract / Profile / Runtime Conformance、V6/V7 evaluation、SCN-0018 Journey harnessで対象範囲と非対象範囲を分けたEvidenceを運用している。SCN-0018もfixture-scoped PASSを`Partially Satisfied`に留め、production Product Acceptanceへ昇格していない。
- Release: **Not Yet Verified** — CI PASSをrelease成立へ昇格していない。
- Operational: **Not Yet Verified** — CI PASSやsynthetic testをproduction成立へ昇格していない。
- Adoption / Outcome: **Not Yet Verified** — 実利用による判断、再検討、説明可能性、Provider選択、業務成果への価値実現はまだ検証していない。

## REQ-0021 — Realization / Executionを交換可能にする

**Status:** Accepted  
**Type:** Interoperability / Non-functional  
**Value:** V4, V8  
**Related Scenarios:** SCN-0005, SCN-0008, SCN-0014, SCN-0018  
**Related ADRs:** ADR-0013, ADR-0014, ADR-0017, ADR-0024, ADR-0025

### Requirement

Cognitive Method Realization、Capability Provider、Execution Provider、Projection、Storage等の交換可能な実現層を変更・簡素化・削除しても、Durable Semantic Coreの意味を不必要に変更しない構造を維持しなければならない。

現在便利なRealizationをUniversal Coreへ昇格させる場合は、それが複数Scenarioで不可欠な意味差であることを別途示さなければならない。

### Rationale

将来、現在のPrompt、agent runtime、workflow、Provider実装が中抜きされてもSOZAが残るため。

### Current Evidence

- Design: **Satisfied**
- Executable: **Partially Satisfied** — Go runtimeをContract semantic authorityから分離し、Representation verifier implementationもProfile authorityから分けている。Cognitive MethodではDefinition / Realization / Applicationを分離し、synthetic Provider A / Bは異なるinput schemaをAdapter-localに保ったまま同じCapability Observationへ収束する。SCN-0018ではno-execution path、Provider replacement boundary、Projection非権威を検査している。固定artifactでactual TEI、model、Ollama runtime revisionを交換し、交換対象固有情報をUniversal Coreへ昇格させずhistorical Applicationを保持した。production Provider / Storage / Execution Providerと任意artifactへの交換は未検証。
- Release: **Not Yet Verified**
- Operational: **Not Yet Verified**
- Adoption / Outcome: **Not Yet Verified**

## REQ-0022 — Provider-neutralなCapability Observation

**Status:** Accepted  
**Type:** Semantic / Interoperability  
**Value:** V1, V2, V4, V5, V8  
**Related Scenarios:** SCN-0002, SCN-0010, SCN-0011, SCN-0012, SCN-0018  
**Related ADRs:** ADR-0006, ADR-0008, ADR-0012, ADR-0013, ADR-0014, ADR-0019, ADR-0024

### Requirement

SOZAは、TEI、SaaS、人間、AI、外部組織等のProvider内部SchemaをUniversal Coreへコピーせず、Capability判断に必要な観測結果をProvider-neutralな意味境界から読めなければならない。

少なくとも、対象Capability、Provider、必要なProvider-specific contextへの参照、観測時点、condition、Evidence / provenance、Unknown / Conflict / Withheld等を必要に応じて扱えなければならない。

Provider内部状態からCapability interpretationへのmappingはDecisionと同一視せず、重要なDecision basisとなった場合はmappingや可変入力をhistoricalに再構成できなければならない。

### Rationale

Provider Independenceを守りつつ、実際のCapability Choiceに必要な状態・Evidence・不確実性を失わないため。

### Current Evidence

- Design: **Satisfied** — ADR-0019、ADR-0024、Capability Observation Contract、Reference Architectureで境界をAccepted。
- Executable: **Partially Satisfied** — F1〜F7をContract checkerとGo runtimeで検証し、Provider-neutral observation、provider-specific reference、mapping provenance、Unknown / Withheld、historical exact basisを保持できる。synthetic Provider A / Bではinput shape、status interpretation、unit conversion、missing値の`unknown`保持、mapping provenance、source state reference、Provider-specific fieldの非漏洩、Decision / Authority / Executionへの非昇格を検査している。SCN-0018 harnessでも同一Capabilityに対する異Provider Observationとexecution後Observationのprovenanceを扱う。production Provider adapter / interoperabilityは未検証。
- Release: **Not Yet Verified**
- Operational: **Not Yet Verified**
- Adoption / Outcome: **Not Yet Verified**

---

## 3. Requirement間の重要な関係

### 歴史的再構成

```text
REQ-0003 Provenance
  + REQ-0005 Decision reconstruction
  + REQ-0009 Revision integrity
  + REQ-0014 residual / reopen
  + REQ-0018 Storage independence
```

### AI・自動化の責任境界

```text
REQ-0002 Uncertainty
  + REQ-0006 Semantic separation
  + REQ-0013 No kind-based authority inference
  + REQ-0017 Contextual responsibility
```

### Provider交換

```text
REQ-0007 Capability / Provider neutrality
  + REQ-0021 Replaceable realization
  + REQ-0022 Provider-neutral observation
```

### 使いやすさと意味保存

```text
REQ-0010 Progressive explicitness
  + REQ-0011 Projection non-authority
  + REQ-0019 Human / AI readability
```

### Product Journey統合

```text
SCN-0018
  = existing REQ composition
  != new workflow ontology
```

SCN-0018は、上記Requirement群を一つの代表的なJourneyで同時に検査するための統合Scenarioです。Product Journeyの順序やUI都合を、それだけで新しいUniversal Requirementへ昇格させません。

## 4. Current evidence baseline

current actual repositoryでは、次のEvidence層まで存在します。

### Design Evidence

```text
Product Value / Value Proposition / Product Shape
  → Requirement / Scenario
  → ADR
  → Reference Architecture
  → Contract Definition
```

### Executable Evidence

現在、少なくとも次をactual CIで再現しています。

- Requirements Registry Conformance
- current 31-fixture Contract Conformance
- Capability Observation F1〜F7
- Cognitive Method C1〜C8 / boundary / negative fixtures
- Representation Profile Conformance
- semantic runtime / Cognitive Method typed runtime
- synthetic Provider Adapter A / B mapping tests
- V6 / V7 Projection Evaluation
- end-to-end Semantic Product Journey harness

current SCN-0018正本Evidence更新後の代表Run:

- Requirements Registry Conformance Run `33478396211`: **success**
- Semantic Runtime Conformance Run `33478396131`: **success**
- V6 V7 Projection Evaluation Run `33478396138`: **success**
- Plan integrity Run `33478396165`: **success**

Journey harness自体ではRun `33478127484`でnormal / uncertain / collaborative / provider replacement / no-execution、temporal integrity、historical Decision非改変、unsupported record、Projection非権威をfixture-scopedに確認しています。

ただし、これらのExecutable Evidenceは各fixture / runtime / evaluation sliceの確認範囲に限定されます。

```text
fixture / runtime / journey CI PASS
  != whole Requirement satisfied
  != production Provider integration
  != production Product Journey validated
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

Requirementごとの`Current Evidence`は、この境界を前提として更新します。

### Release / Operational / Adoption・Outcome

2026-09-01時点では、Release、Operational、Adoption / Outcomeのいずれもcurrent Requirement全体についてSatisfiedとは主張しません。

```text
release artifact verified
  != production operation verified
  != user-value realization verified
```

将来これらのEvidenceを得た場合も、下位Evidenceから自動昇格させず、Requirementごとに確認します。

## 5. Historical candidateとの関係

旧`SOZA-PR-001`〜`SOZA-PR-018`と`SOZA-NFR-001`〜`010`の意味核は、必要なものをcurrent REQへ統合しています。

旧番号や旧Evidence状態はcurrent正本ではありません。詳細な対応は`history/HISTORICAL_REQUIREMENT_MAPPING.md`を参照します。

## 6. Natural Japanese review

Product Value、Value Proposition、Product Shape、Value Model、Value Acceptance、Accepted ADR、current Architecture、5 Semantic Contract family、31 fixture、Representation Profile、semantic runtime、Cognitive Method typed runtime、synthetic Provider Adapter、V6/V7 Projection evaluation、SCN-0018 end-to-end Product Journey harness、actual CI Evidence、fixed-scope actual model / runtime exchange、およびhistorical candidateの意味核を照合し、Requirement本文の意味や要求強度を変えずにEvidence欄をcurrent状態へ再基線化しました。とくにCognitive Method、historical Decision非改変、Projection非権威、残差からreopenへの引継ぎは、実際に検査できた範囲だけ`Partially Satisfied`へ反映しています。ISSUE-000070の結果は既存REQ-0001 / 0004 / 0021で表現できるため、新しいStable Requirementは追加していません。そのうえで、Design / Executable / Release / Operational / Adoption・Outcomeの区別、未検証事項、production境界を変えない範囲で、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
