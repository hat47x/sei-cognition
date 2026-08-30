# SOZA Reference Architecture

更新日: 2026-08-31  
状態: **Current Reference Architecture Baseline**

## 1. 目的

この文書は、SOZAがProduct Valueを満たすために、どの意味を自ら保持し、どの境界をProfile、Provider、Adapter、Projection、Persistence等へ委ねるかを、current RequirementsとAccepted ADRから整理したReference Architectureです。

これはdeployment topology、microservice構成、Go package構成、database schema、固定workflowを定義する文書ではありません。

SOZAのArchitectureを、**認知・判断・責任・来歴を失わないための意味境界の網**として記述します。

## 2. Architectureを支配する原則

### 2.1 耐久的な意味を実現方式より先に置く

現在のAI、Prompt、workflow、DB、UI、Providerの都合を、SOZAの恒久的な意味構造へ直接持ち込みません。

Coreへ置く候補は、少なくとも次を満たす必要があります。

1. 現在の具体Scenarioで区別する必要がある。
2. 技術が大幅に進歩しても意味差が残る。
3. その区別を失うと、認識、判断、責任、来歴のいずれかが損なわれる。
4. Profile、Provider、Adapter、Projection、domain-specific knowledge等へ置く方が自然ではない。
5. Acceptance Scenarioから必要性を説明できる。

### 2.2 Coreは「重要なものを全部入れる場所」ではない

Coreを小さくすること自体を目的にはしませんが、現在便利という理由だけでUniversal概念を増やしません。

現在のbaselineでは、次を便宜だけでCoreへ追加しません。

- Universal Claim / Interpretation ontology
- Global Principal / Identity graph
- universal risk / confidence / suitability score
- workflow status machine
- approval / voting protocol
- queue / retry / agent turn
- provider-specific realization lifecycle
- DB / Git / event sourcing mechanics
- TEI固有Application / Database / Release / Deployment schema
- domain-specific Reference Model / Pattern

### 2.3 Architecture concernとruntime componentを分ける

この文書でいうDecision Memory、Capability、Persistence等はarchitecture concernです。

```text
Architecture concern != service != package != database
```

一つのruntime componentが複数concernを実装しても、一つのconcernが複数componentへ分散しても構いません。

## 3. 全体像

概念的には、SOZAを次の関係として読みます。

```text
External Sources / Humans / AI / Organizations / Systems
                 │
                 │ Observation / Request / Result / Evidence
                 ▼
        Provider / Adapter Boundary
                 │
                 ▼
┌──────────────────────────────────────────────────────┐
│              Durable Semantic Concerns               │
│                                                      │
│ Inquiry / Epistemics ↔ Cognitive Method              │
│          ↕                    ↕                      │
│     Decision Memory ↔ Capability Understanding       │
│          ↕                    ↕                      │
│ Responsibility / Authority Boundary                  │
│          ↕                                           │
│ Reference / Provenance / Revision / Exact Binding    │
└──────────────────────────────────────────────────────┘
        ▲                    ▲                    ▲
        │                    │                    │
 Profile / Policy      Federation Profile     Projection
        │                                         │
        └────────────── Persistence ───────────────┘
```

この図は処理順序を示しません。各concernが互いのArtifactやReferenceを利用し得ることを示します。

## 4. Durable Semantic Core concern

SOZA自身が長期に守る中心は、特定の型名よりも**意味上の区別**です。

current Requirementsから、少なくとも次を失わない必要があります。

- Goal / Intent / Constraintの文脈
- Questionと未解決状態
- ObservationとInterpretation / Hypothesisの差
- Unknownとnegative factの差
- Conflictとlatest-winsの差
- Evidenceの存在とEvidenceUse / Assuranceの差
- RecommendationとDecisionの差
- DecisionとAuthority / Action Intent / Executionの差
- CapabilityとProviderの差
- logical identityとexact historical content bindingの差
- storage revisionとsemantic revisionの差
- source origin、discovery route、Derivation等の来歴差
- contextual Responsibility

exact production field setはArchitectureだけで固定しません。portable contractが必要になった境界を`contracts/`へ落とします。

## 5. Inquiry / Epistemic State

### 5.1 役割

Inquiry / Epistemic concernは、「何を問い、何を観測し、何がまだ分からず、どの情報が競合しているか」を保持します。

重要なのは、情報を一つの確定状態へ急いで畳み込まないことです。

```text
Observation != EvidenceUse != Assurance != Truth
Unknown != No
Conflict != latest-wins
Hypothesis != Decision
not observed != unavailable
```

### 5.2 Decisionとの関係

Decisionが作成されてもUnknown / Conflict / Questionは残り得ます。

```text
Decision creation != uncertainty resolution
```

Decision後の未解決残差は、後続InquiryやDecision reviewを再開する入口として保持できます。

### 5.3 Sourceと解釈

外部資料に「X」と書かれていることはObservationとして表現でき、その意味づけはHypothesis、Interpretation相当の派生、Method固有Artifact等として分けられます。

Universal Claim型を必須にはしません。REQ-0016が要求するのは、ObservationとInterpretationを必要な場面で再構成可能にすることです。

## 6. Cognitive Method

### 6.1 Methodの意味境界

Cognitive Methodは、探索、比較、統合、検査等をどのように行うかという手続き上の意味です。

```text
Method Definition
  != Realization
  != Method Application
  != Recommendation
  != Decision
  != Assurance
```

同じMethodをPrompt、人間手順、model program、code-assisted tool等で実現できます。

### 6.2 Reference Model / Patternとの分離

PatternやReference Modelはdomain-specificなDesign Knowledgeです。

```text
Pattern != Cognitive Method
Pattern match != Recommendation != Decision
```

MethodはPatternを探索対象として利用できますが、Pattern一致を採用Decisionへ自動昇格させません。

### 6.3 private chain-of-thought非依存

Method Applicationの再構成に、AIの非公開private chain-of-thoughtを必要としません。

外在化すべきなのは、利用したMethod、主要input / output、Evidence、Recommendation、Residual等です。

## 7. Decision Memory

### 7.1 中心目的

Decision Memoryの中心はDecision workflowではなく、**判断時点の意味を後から再構成できること**です。

概念的には次のような関係を持ち得ます。

```text
Intent / Goal / Constraint
          │
Observation / Hypothesis / Unknown / Conflict
          │ considered material
Recommendation? ───────────────┐
                               ▼
                            Decision
                               │
                  contextual Responsibility
                               │
                    later Observation
                               │
                    Semantic Lineage
                               ▼
                            Decision D2
```

矢印は固定workflowではありません。RecommendationなしのDecisionも、RecommendationだけでDecisionなしも許容します。

### 7.2 Decisionが意味しないもの

Decisionだけでは次を意味しません。

- Authorization
- Action Intent
- Provider Execution
- Execution Success
- Business Outcome
- uncertainty resolved

### 7.3 BasisとRationale

Decision時に明示的に利用したObservation、Hypothesis、Constraint、Recommendation、Assurance等をbasisとして辿れることを優先します。

Rationaleは監査・再読のための外在化された説明ですが、private chain-of-thoughtではありません。

```text
rationale != private chain-of-thought
```

Rationale文章だけを唯一のbasis rootにせず、重要な可変ArtifactはReference / Exact Bindingから辿れるようにします。

### 7.4 Revision

D1の後に新しいObservation O2が得られてD2へ判断が変わった場合、D1を削除せず、D1のbasisを後知恵で更新しません。

Semantic Lineageを利用し、O2がD2のbasisになったことを残します。

## 8. Capability Understanding / Choice

### 8.1 Definition、Observation、Matching、Decisionを分ける

```text
Capability Definition
  != current Capability Observation
  != Matching
  != Choice Decision
  != Provider selection
  != Authority
  != Execution
```

Capability Definitionは「何ができるか」の耐久的意味であり、Provider runtimeの一時状態とは分けます。

### 8.2 Provider-neutral Observation

Capability Observationは、Providerや実現候補について観測した現在情報を表します。

必要に応じて、次を扱えます。

- target Capability
- Provider reference
- provider-specific contextへのReference
- observation time
- observed condition
- Evidence / Provenance
- Unknown / Conflict / Withheld context
- mapping / adapter provenance

TEI ApplicationやDatabase等の内部SchemaをSOZA Coreへコピーしません。

### 8.3 Adapterは解釈境界でもある

Provider internal stateからSOZA Capability Observationへのmappingは、単純なformat変換とは限りません。

```text
Provider state != Capability interpretation != Decision
```

mappingが重要なDecision basisになった場合、当時利用したmapping versionを特定できるようにします。

### 8.4 Matching

MatchingはIntent / Constraint / contextとCapability候補の関係を説明します。

Supporting basis、conflicting basis、missing information、explanation等を保持できることを優先し、Universal suitability scoreを必須にしません。

MatchingはDecisionではありません。

### 8.5 Choice

実際にCapabilityを採ることはDecision境界へ入ります。

Choice専用のUniversal lifecycleを作らず、既存Decision Memoryを再利用します。

## 9. Responsibility / Authority boundary

### 9.1 Responsibilityは文脈に結び付ける

SOZA全体でGlobal Identity ontologyを要求せず、Decision、Requirement、Capability、Action、Review等の具体文脈で、誰または何が何を担ったかを参照します。

### 9.2 actor kindからAuthorityを推定しない

```text
human != automatically authorized
AI != automatically unauthorized
Responsibility != Authorization
```

同じ主体がDecision makerとAuthorization holderを兼ねる場合でも、意味上の役割は分けます。

credential validation、revocation check、external authorization mechanism等はAuthority Provider側へ委ねられます。

## 10. Semantic Reference / Revision / Exact Binding

### 10.1 Logical Reference

Logical Referenceは「どの意味上のArtifactを指すか」を表します。

Storage row ID、file path、object key等をsemantic identityそのものにはしません。

### 10.2 Exact Historical Binding

重要なDecision basisやMethod Application input等について、後から内容が変わり得るlogical Artifactの**当時内容**を固定する必要がある場合、Exact Historical Bindingを使います。

```text
Logical Reference != Exact Historical Binding
```

Representation Profileやverifierが利用不能な場合の`not_verified`と、内容不一致を確認した`failed`を分けます。

### 10.3 Semantic Revision

Semantic revisionはGit commit、DB version、event sequence等から自動推定しません。

`revises`、`supersedes`、`withdraws`等のsemantic relationを明示的に扱います。

physical deleteとsemantic withdrawalも分けます。

## 11. Profile / Policy

Core vocabularyが存在することと、すべての案件で全Artifactを必須にすることは別です。

Profile / Policyは、案件の影響、不確実性、不可逆性、外部性、組織規則等に応じて、たとえば次を要求できます。

- explicit Decision required
- basis refs required
- unresolved refs required
- rationale required
- Responsibility required
- exact historical binding required
- additional Assurance required

これらをUniversal fixed levelや単一risk scoreへ圧縮しません。

```text
Core provides durable vocabulary
Profile / Policy chooses required explicitness
```

## 12. Federation / Selective Disclosure

FederationはUniversal Core ontologyではなく、bounded subject間で既存semanticsを交換するoptional Profileとして扱います。

### 12.1 全内部world modelを共有しない

協働のために、各組織の内部Artifact、credential、source locator、判断手続の全量共有を要求しません。

必要なRequest、Offer、Commitment、Result、Evidence、Reference等だけを交換できます。

### 12.2 意味境界

```text
Request != Authority Grant != Commitment != Execution
Offer != Capability proof != Decision
Result != Business Outcome != Assurance
```

相手が一部情報の存在だけを示し、内容を開示しない場合、必要に応じてUnknownとWithheld Contextを分けます。

### 12.3 Transport / Cryptography

TLS / mTLS、OAuth / OIDC、message signing、encryption、replay protection、broker等のmechanicsはProvider-ownedとします。

SOZAは必要に応じてverification / assurance / signature referenceを保持できます。

## 13. Provider / Adapter

Providerは、Capability、Persistence、Authority、Transport、AI inference、workflow等の実現を担い得ます。

SOZAはProviderを交換可能な境界として扱い、Provider-specific SDK stateやsession lifecycleをUniversal Coreへ持ち込みません。

Adapterは、次を担い得ます。

- representation conversion
- provider-specific reference resolution
- observation mapping
- contract mapping
- historical compatibility bridge

Adapterが行うInterpretationをObservationそのものとして隠しません。

## 14. Projection

Projectionは、人間やAIがSOZAの意味資産を目的に応じて読むための表示・作業面です。

例:

- Web workspace
- kj-atlas
- dashboard
- CLI
- report
- machine-readable query view

ProjectionはCanonical Semantic Authorityではありません。

```text
Projection != Canonical Semantic Authority
Simple View != Lossy Canonical Model
```

Projectionを削除・再構築しても、Decision、Provenance、Revision等の耐久的意味を失わないことを要求します。

## 15. Persistence

SOZAはGit、RDB、object store、document DB、event sourcing等の一つをCoreへ固定しません。

Persistence Providerが変わっても、少なくとも次のsemantic obligationsを守れることを求めます。

- logical identity preservation
- exact binding integrity
- semantic lineage preservation
- provenance preservation
- reference integrity
- contract / representation identity
- portable export / import

Storage migrationやschema migrationだけを理由にsemantic revisionを自動生成しません。

large binaryや外部Sourceをすべてinlineすることも要求しません。

## 16. Evidence / Assurance boundary

Evidenceが存在すること、Evidenceを特定Decisionのbasisとして用いたこと、Assuranceを付与したこと、世界のTruthであることを分けます。

同様に、SOZA自身の開発Evidenceについても次を分けます。

- Design Evidence
- Executable Evidence
- Release Evidence
- Operational Evidence

Architecture文書やContract schemaの存在をExecutable Evidenceへ昇格させません。

## 17. 主な横断フロー

### 17.1 InquiryからDecisionへ

```text
Question
  ↕
Observation / Hypothesis / Unknown / Conflict
  ↕
Cognitive Method Application
  ↓ may produce
Recommendation
  ↓ may inform
Decision
```

どの段階も必須固定順序ではありません。

### 17.2 Capability ChoiceからProvider crossingへ

```text
Intent / Constraint
      +
Capability Definition / Observation
      ↓
Matching? / Inquiry
      ↓ may inform
Decision
      ↓
Authority boundary
      ↓
Action Intent
      ↓
Provider Execution
      ↓
Result / Receipt
      ↓ imported as observation
SOZA Inquiry / Decision review
```

Execution ResultをBusiness Outcomeへ自動昇格させません。

### 17.3 Historical revision

```text
Decision D1 ── exact basis ── Artifact A@t1
     │
 later Observation O2
     │
Semantic Lineage
     ▼
Decision D2 ── new basis ── Artifact A@t2 / O2
```

D2の現在知識をD1の過去basisへ遡及挿入しません。

## 18. Contractへ落とす候補境界

current Architectureから、相互運用・検証のためにContract化を再評価すべき候補は次です。

| Concern | Contract候補 | 現在状態 |
|---|---|---|
| Semantic Reference / Interchange | portable semantic interchange | ISSUE-000030で評価 |
| Exact Historical Binding | logical / exact binding contract | ISSUE-000009 / 000030 |
| Decision Memory | Decision / basis / unresolved interchange | ISSUE-000030で評価 |
| Capability Observation | provider-neutral observation contract | ISSUE-000024 / 000030 |
| Federation | selective disclosure exchange profile | ISSUE-000030で評価 |
| Representation | canonicalization / digest profile | ISSUE-000009 / 000030 |

Architectureに候補として記載しただけではContract採用を意味しません。

## 19. 現時点でArchitectureが固定しないもの

次はcurrent Architectureだけでは固定しません。

- production field set
- JSON Schema shape
- package structure
- database schema
- API transport
- message broker
- queue / retry semantics
- ranking algorithm
- Capability composition algorithm
- universal cost model
- universal risk score
- approval workflow
- specific UI layout
- TEI preference
- JCS / SHA-256等のRepresentation Profile採用

必要なものはContract、Implementation Issue、Provider Profile等で別途扱います。

## 20. 将来耐性

Architecture reviewでは、評価時点の現実からおおむね10〜50倍程度先を見渡し、現在の技術制約へ過適合していないかを監査します。

この距離はbenchmarkではありません。

AIや実行基盤が大幅に高度化しても、提案したこと、判断したこと、権限があったこと、実行したこと、何を根拠にしたこと、何が未解決だったことは、引き続き異なる意味を持つと考えます。

## 21. 関連文書

- `product/value/SOZA_VALUE_MODEL.md`
- `product/value/SOZA_VALUE_ACCEPTANCE.md`
- `requirements/PRODUCT_REQUIREMENTS.md`
- `requirements/ACCEPTANCE_SCENARIOS.md`
- `architecture/TRACEABILITY.md`
- `plan/adr/ADR-0021-architecture-contract-authority-and-versioning.md`

## 22. Natural Japanese review

current Product Value、REQ-0001〜0022、ADR-0001〜0021とhistorical Architectureの意味核を照合し、Milestone / runtime component / contract候補を分離して構造を作成しました。その後、意味、規範強度、未決事項、Evidence境界を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施しています。
