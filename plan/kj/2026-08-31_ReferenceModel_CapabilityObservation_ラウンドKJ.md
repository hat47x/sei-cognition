# Reference ModelとCapability ObservationのラウンドKJ統合

更新日: 2026-08-31  
状態: **Decision-preparation KJ / ADR source**

## 0. 目的

TEI設計系列から残った次の二論点を、SEI / TEIのProduct Boundaryを壊さずに整理する。

- ISSUE-000019: Reference Model / Pattern Card / Cognitive Methodの所有境界
- ISSUE-000020: TEIのApplication / Database等をSEI Capability Observationから読む境界

---

# 第1ラウンド　生カード

### R001

X-TEA時代のReference Modelには、業務構造、設計上の典型、確認観点、実装例が混在していた。

### R002

後発議論では、Reference Modelを正解テンプレートとして対象へ押し付けず、Pattern Cardや候補探索の知識として扱う方向へ修正された。

### R003

Patternは「この状況ではこの構造が有力」という再利用可能な設計知であり、対象案件のDecisionそのものではない。

### R004

Cognitive Methodは、どの資料を見て、どの問いを立て、どのように比較・統合・検査するかという手続きの意味を持つ。

### R005

同じPatternを、異なるCognitive Methodから発見・比較・棄却できる。

### R006

Reference Modelの特定Table / Screen / Workflow構造をSEI Universal Coreへ移すと、domain-specific設計が認知基盤へ逆流する。

### R007

KJ法やcultural-substrate-weavingと同様、Methodを適用した事実と、そのMethodが導いた結論が正しいことは同じではない。

### R008

Reference Modelが後で改訂されても、過去Decisionでどの版・どのPatternを参照したかは再構成できる方がよい。

### O001

SEIから見たTEIはCapability Providerであり、TEI内部のApplication / Database lifecycleをSEI Coreへコピーする必要はない。

### O002

SEIのCapability Choiceには、Capability Definitionとcurrent Observationを分離する境界がある。

### O003

TEI内部ではApplication、Database、Environment、Release、Plugin、Observed State等が独立対象として存在する。

### O004

TEI内部の一つの状態だけから「Capabilityが利用可能」と自動推定すると、provider-specificな複雑性を一つのbooleanへ潰す可能性がある。

### O005

Applicationがreadyでも依存Databaseがread-only、migration未採用、Environment未Binding等の状態はあり得る。

### O006

SEIに必要なのはTEI内部topologyそのものではなく、Intent / Constraintとの比較に必要な状態、Unknown、Evidence、Assuranceである。

### O007

詳細監査や過去Decision再構成では、TEI release、binding、database contract等のprovider-specific snapshotをexact referenceで辿れる価値がある。

### O008

Selective Disclosure下では、TEI内部topologyを全て見せず、必要なCapability ObservationとEvidenceだけ共有する場合がある。

---

# 第2ラウンド　束ね

## B01 Reference ModelはPattern集合と探索手続きが混ざりやすい

- R001-R005

Patternそのものと、それをどう探索・検査するMethodを分ける。

## B02 Pattern採用とMethod利用をDecisionへ自動昇格させない

- R006-R008

domain固有PatternをSEI Coreへ入れず、利用履歴は必要に応じてexact referenceで残す。

## B03 TEI内部状態とSEI Capability Observationを分ける

- O001-O004

Provider内部modelをSEIへ複製せず、adapter境界でObservationへ変換する。

## B04 Capability判断に必要な状態と監査用snapshotを二層で扱う

- O005-O008

通常判断では必要最小限のObservation、詳細監査ではprovider-specific exact referenceへ降りられる。

---

# 第3ラウンド　核融合法

4束を二つの核へ融合した。

## N01　Reference Modelの再利用知と、Cognitive Methodの認知手続きを分離する

- Pattern / Reference Model: domain-specific reusable design knowledge
- Cognitive Method: exploration / comparison / synthesis / validation procedure
- Method Application: Methodをある対象へ適用した来歴
- Decision: Patternを採用・棄却・修正した判断

### 残差

Patternを正解テンプレートへしないこと、Reference Model改訂後も過去参照版へ戻れることを保持する。

## N02　SEIはProvider-neutralなCapability Observationを読み、必要なときだけTEI固有Evidenceへ降りる

- Capability DefinitionとObservationは分離
- TEI internal stateはprovider-specific source
- AdapterがSEI側のObservation / Unknown / Conflict / Assuranceへ接続
- historical / audit useではexact provider snapshotへ降りられる
- internal topologyの全開示を要求しない

### 残差

Application readyだけでavailabilityを確定しないこと、Provider固有状態を一つのUniversal enumへ押し込まないことを保持する。

## 戻し照合

16枚へ戻して照合した結果、R007「Method適用≠結論の正しさ」とO008「Selective Disclosure」が初回核で弱かった。

N01にAssurance非自動化、N02にSelective Disclosureを明記して補正した。

主要意味核欠落: **0件**

---

# 第4ラウンド　A型図解

```text
TEI Design Knowledge
  Reference Model / Pattern Cards
       │ candidate / comparison input
       ▼
SEI Cognitive Method
  exploration / comparison / synthesis / validation
       │ Method Application
       ▼
Recommendation / Decision
       │
       └─ exact reference to Pattern / historical version when material

TEI Provider internal state
  Application / Database / Environment / Release / Plugin / Observation
       │ provider adapter
       ▼
SEI Capability Observation
  observed properties
  Unknown / Conflict
  provenance / assurance / evidence refs
       │ when detailed audit is needed
       └──────────→ exact provider-specific snapshot/reference
```

### 重要な非同一性

```text
Reference Model != Cognitive Method != Decision
Pattern match != Pattern adoption
Method Application != conclusion truth
TEI internal state != SEI Capability Observation schema
Application ready != Capability universally available
provider snapshot != Capability Definition
```

---

# 第5ラウンド　B型文章化

Reference Modelは、初期X-TEAでは強い設計の出発点だったが、設計が進むにつれて、その扱いは変わった。重要なのは典型構造を捨てることではなく、対象へ正解として押し付けないことである。履歴管理、Subsystem、Data-first、組織・認可等のPatternは、候補探索を助ける設計知として価値がある。一方、どのPatternをどう探し、何と比較し、どの反例を確認するかという手続きはCognitive Methodの側に置ける。

この分離により、TEIはdomain-specificなPattern CardやReference Modelを豊かに持てる一方、SEIは特定業務SchemaをUniversal Coreへ取り込まずに済む。AIがPatternを提示したことはRecommendationになり得るが、Patternが対象へ適合することや採用が決まったことを意味しない。Methodを適用した事実も、結論が正しいというAssuranceにはならない。重要なDecisionでReference Modelの版やPatternが根拠になったなら、そのhistorical contentを後から辿れるようにする。

TEIのCapabilityをSEIから読む場合も、同じ分離が必要になる。TEI内部にはApplication、Database、Environment、Release、Plugin等の具体的な状態があるが、SEIがそれらのlifecycleをUniversal modelとして理解する必要はない。SEIが必要とするのは、IntentやConstraintとの比較に必要なObservation、Unknown、Conflict、Evidence、Assuranceである。

たとえばApplicationがreadyでも、依存Databaseがread-onlyかもしれない。Migration Proposalが存在しても未採用かもしれない。EnvironmentへまだBindingされていないかもしれない。したがって一つのinternal statusを`available=true`へ機械的に変換しない。Provider adapterは、何が観察でき、何が未確認で、どのEvidenceに基づくかをSEI側へ渡す。

通常のCapability ChoiceではTEI内部topologyをすべて開示する必要はない。一方、重要なDecisionを後から監査するときは、当時のTEI Release、Binding、Database Contract等へexact referenceで降りられる方がよい。この二層構造により、SEIはProvider-neutralでありながら、必要な場合には具体的な実装Evidenceまで追跡できる。

---

# 第6ラウンド　Decision preparation

## D1 Reference Model / Cognitive Method

ADR候補:

- Reference Model / Pattern Cardは原則としてTEI Design Knowledgeまたはdomain-specific knowledge assetへ置く。
- Cognitive Methodは探索・比較・統合・検査の手続きをSEI側で表し得る。
- PatternそのものをSEI Universal Coreへ移さない。
- Method ApplicationやPattern matchからDecision / Assuranceを自動推定しない。
- 重要なDecisionで利用したPattern / Reference versionは必要に応じてexact historical referenceへ結ぶ。

## D2 TEI Capability Observation surface

ADR候補:

- SEIはTEI内部schemaを複製せず、Provider adapterを介したCapability Observationを受ける。
- UniversalなTEI-specific status vocabularyを作らない。
- AdapterはObservation / Unknown / Conflict / provenance / assuranceを保持できる。
- Capability availabilityを単一internal statusから自動推定しない。
- 詳細監査・historical reconstructionではprovider-specific exact snapshotへ降りられる。
- Selective Disclosure下では内部topology全量共有を要求しない。

これらをADR-0017 / ADR-0018候補へ進める。
