# SOZA 上流プロダクト開発計画

更新日: 2026-09-02  
状態: **Current Upstream Planning Baseline**

## 1. この文書の役割

この文書は、SOZAのProduct Value、Milestone、Requirement、ADR、Architecture、Implementationをどの順序で具体化するかを定めます。

目的は、未定の領域を実装都合で早期に固定せず、**上位価値へ戻りながら、議論と実証を通して必要な要求だけを正本化すること**です。

期限やcalendar scheduleは扱いません。優先順位は、Product Valueへの影響、未確定部分が下位設計を拘束する度合い、次の実証を可能にする依存関係によって決めます。

## 2. 上位から下位への基本順序

原則として次の順序で進めます。

```text
Product Value / Value Proposition
  ↓
Product Vision / Principles / Product Shape
  ↓
Deadline-free Product Milestones
  ↓
Open Question / Product Hypothesis
  ↓
Discussion / Research / Experiment
  ↓
Candidate Requirement
  ↓
Requirement / Acceptance Scenario
  ↓
Issue / ADR
  ↓
Architecture / Contract
  ↓
Implementation / Fixture / Test
  ↓
Evidence
  ↓
必要なら上位へ戻って再基線化
```

コードやexisting schemaを上位概念の根拠にしません。一方、実装・実験から得た反証Evidenceは、上位仮説を見直す正当な入力とします。

## 3. 現在の優先順位

### Priority A — Product ValueとMilestoneの正本維持

最優先で、次の文書間に矛盾がない状態を保ちます。

- `product/value/SOZA_PRODUCT_VALUE.md`
- `product/value/SOZA_VALUE_PROPOSITION.md`
- `product/value/SOZA_VALUE_MODEL.md`
- `product/value/SOZA_VALUE_ACCEPTANCE.md`
- `product/definition/SOZA_PRODUCT_SHAPE.md`
- `product/definition/SOZA_REALIZATION_PROVIDER_EXCHANGE.md`
- `product/vision/SOZA_PRODUCT_VISION.md`
- `product/principles/SOZA_PRODUCT_PRINCIPLES.md`
- `product/roadmap/SOZA_PRODUCT_MILESTONES.md`

下位作業がこの層と矛盾した場合は、実装を先に温存しません。矛盾がProduct Value側の誤りを示すならEvidenceを明示して再基線化し、そうでなければ下位設計を修正します。

### Priority B — 未定領域の探索

現時点でRequirementとして十分に定まっていない領域は、まずOpen Questionとして扱います。

Product Interaction、Local Single-Node Packaging、Product Access責務分離については、Design baselineと限定されたExecutable Evidenceまで進みました。現在の主要な未定領域は次です。

- E3b-P2: 実TEI process / serviceをどの実行面から接続するか
- E3b-P2で、TEI executableの取得・private credentialとSOZA semantic integrationをどう分離するか
- E3b-M1: 実Cognitive Methodをlive実行するrunnerを何とするか
- Provider / Realization version交換時に必要なProvenance / Exact Bindingの水準
- formal integration protocolを本当に標準化する必要があるか
- actual Product Releaseへ進む時点とRelease Evidenceの成立条件
- release後のOperational / Adoption / Outcome評価方法

既存Issueがある領域は、そのIssueを探索入口として使います。新しいRequirementを追加すること自体を成果にしません。

### Priority C — RequirementとAcceptanceの精緻化

議論・実証から必要性が確認できたものだけをRequirementへ反映します。

既存REQ / SCNで表現できる場合は新しいIDを増やさず、横断AcceptanceやEvidenceの不足として扱います。

### Priority D — Architecture / Contract / Implementation

上位RequirementとAcceptanceが十分に定まった範囲から、Architecture、Contract、runtime、Provider Adapter、fixture、testへ降ろします。

実装可能であることと、Requirementとして必要であることを混同しません。

## 4. 未定領域を要件化するまでの標準フロー

### Step 1 — Open Questionを明文化する

最初に「何を決めるか」ではなく、**何がまだ分かっていないか**を明確にします。

例:

- 実TEI CLIを呼ぶために、SOZAがrepository取得方式まで知る必要は本当にあるか。
- external Cognitive Methodをlive実行するとき、Method Definitionとrunner固有protocolをどこまで分離できるか。
- product login identityとhistorical actor referenceは同じidentityを要求するか。

この段階では選択肢をRequirementへ固定しません。

### Step 2 — チャット上の議論・資料調査を行う

設計上の論点、利用場面、失敗例、既存技術、代替案を広く検討します。

チャットは探索と統合の作業空間として利用できますが、**チャット上の結論そのものをcurrent正本にはしません**。後続作業でIssue、Product文書、Requirement、ADR等へ必要な内容を移します。

外部Projectを候補にする場合は、名称や想像上のAPIだけで判断せず、実際のrepository、CLI、artifact、service surface、versioning、credential条件まで確認します。

### Step 3 — 実証実験を設計する

議論だけで判断しにくい場合は、小さなprototype、fixture、comparison harness、human review、provider接続試験等を作ります。

実験は、実装候補を完成させることより、次のような問いに答えることを優先します。

- 意味境界が本当に必要か。
- 既存Requirementで十分か。
- どの選択肢が利用負担を減らすか。
- ProviderやUIを交換しても意味が残るか。
- 失敗時に何が失われるか。
- artifact取得、credential、process invocation、semantic mappingを分けられるか。

### Step 4 — Evidenceの高さを記録する

実験結果は、少なくとも次を区別します。

```text
Design Evidence
  != Executable Evidence
  != Release Candidate Evidence
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

Release Candidate Evidenceは5段階Evidenceへ新しい普遍段階を加えるものではありません。特定candidateについて必要なExecutable Evidenceをまとめて再検査した記録として扱います。

synthetic fixture、helper process、version固定artifact、public live serviceのPASSを、それぞれが確認していない実Providerや実運用のEvidenceへ自動昇格させません。

### Step 5 — Candidate Requirementを作る

実証結果から「製品として必ず守る必要がある意味差」が見えた場合だけCandidate Requirementを作ります。

この時点ではstable REQ IDを付けなくても構いません。

### Step 6 — Requirement化の監査を行う

stable Requirementへ昇格する前に、少なくとも次を確認します。

1. Product Valueのどの価値を守るために必要か。
2. 具体的な利用Scenarioまたは失敗例で必要性を説明できるか。
3. 既存REQ / SCNの組み合わせで既に表現できないか。
4. 現在のUI、AI、DB、workflow等の弱点を補うだけの一時的要求ではないか。
5. Provider / Profile / Projection / Adapter / deployment policyへ置く方が自然ではないか。
6. 評価時点から10〜50倍程度先を見ても、意味上の必要性が残るか。
7. Acceptanceを観測可能な形で定義できるか。

### Step 7 — 結果を三つに分ける

監査結果は次のいずれでも正当です。

- **Stable Requirementへ昇格する。**
- **既存Requirement / Scenarioへ統合する。**
- **Requirement化せずDeferredまたはNo Changeとする。**

「調べた結果、新しいRequirementは不要だった」ことを失敗とみなしません。

## 5. Product MilestoneとRequirementの関係

Milestoneは、製品として成立させたい状態を示します。

Requirementは、その状態を成立させるために必ず守るべき規範を示します。

したがって、Milestoneの箇条書きをそのままRequirementへ変換しません。

たとえばPMS-06で実TEIを接続することを求めても、GitHub token、private clone、CLI配布方式、HTTP / gRPC / MCP等の具体方式をStable Requirementにする必要はありません。

```text
Milestone outcome
  != implementation choice
  != acquisition mechanism
  != Universal Requirement field list
```

## 6. 現在の主要探索系列

### 6.1 Product Interaction

ISSUE-000045 / 000053で、human-oriented Surfaceとmachine-oriented Surfaceを同じcanonical sourceへ戻す境界について、Design baselineと限定されたExecutable Evidenceがあります。

productionで最初にsupportするWeb / desktop / CLI / API / MCP等は引き続きOpen Questionですが、現時点の主探索系列ではありません。将来の実利用やPackaging要件から必要性が現れた時点で再開します。

### 6.2 Packaging / Deployment

ISSUE-000046 / 000054 / 000055で、Local Single-Node Package、durable data root、save / reload、deterministic reference artifactについて限定されたExecutable Evidenceがあります。

v0.2.0ではLocal Reference Product Baselineまでをcandidate scopeとし、production installer、formal platform support matrix、server topology等は先取りしません。

### 6.3 Identity / Authorization / Collaboration

ISSUE-000047 / 000056で、authentication identity、Bounded Subject、Product access permission、semantic Responsibility / Authorityを分離するDesign baselineと限定されたExecutable Evidenceがあります。

production IdP / IAM、formal RBAC / ABAC、team membership lifecycle等は未検証ですが、PMS-06の実Provider交換を進めるために先に固定する必要はありません。

### 6.4 Real Method / Provider Portability

現在の主探索系列です。

Evidenceを次の段階に分けます。

```text
E1 Contract / in-process synthetic
  → E2 out-of-process reference exchange
  → E3a version-pinned external artifact integration
  → E3b-P1 public live Provider service
  → E3b-P2 actual TEI process / service
  → E3b-M1 external Cognitive Method live execution
  → E4 operational portability
```

E2、E3a、E3b-P1には、それぞれ対象を限定したExecutable Evidenceがあります。これらを一括して「E3b完了」とは扱いません。

#### 6.4.1 次に進めるE3b-P2

実体を調査した結果、TEIには`cmd/tei`が存在し、`deployment-provider-plan`、`deployment-reconcile`、`deployment-simulate`等のJSON出力面を既に持っています。このため、SOZA向けの新しいwire protocolをTEIへ追加するより、**既存TEI CLIをProvider固有の外部processとして扱う**方が現在の境界に適合します。

一方、TEI repositoryはprivateです。SOZA CIの標準`GITHUB_TOKEN`が別private repositoryを読めるとは仮定しません。

そのため、ISSUE-000061では次を明示的に分けます。

```text
TEI source / binary acquisition
  != credential resolution
  != external process invocation
  != Provider-specific JSON decoding
  != SOZA Capability Observation mapping
```

まず、外部から与えられたTEI executableを呼べるAdapter境界をExecutable Evidence化します。helper processによる境界testはactual TEI executionの代替にはせず、実TEI executableを実際に呼べる環境が得られた時点でE3b-P2 Evidenceを別に収集します。

credentialを利用する実証が必要になった場合も、GitHub PATや特定Secret製品をUniversal semanticsへ持ち込まず、acquisition / deployment policy側の問題として扱います。

#### 6.4.2 E3b-M1の扱い

`cultural-substrate-weaving`にはversion管理されたSkill、複数platform向けadapter、build / validation基盤がありますが、現時点のrepository調査では、Methodを独立processとして実行してRecommendationを返す標準runnerは確認できていません。

したがって、SOZA側が便宜的なrunnerを作って「実Cognitive Methodを実行した」とみなすことはしません。既存の実runnerまたは実際のhost integrationを特定できてからE3b-M1を設計します。

### 6.5 Release / Operational / Adoption Outcome

v0.2.0については、actual `develop/v0.2.0`上でRelease Candidate Gateを再現できるEvidenceがありますが、actual Product Release / Release Evidenceは別です。

release tag、release identity、配布Artifactとのexactな対応等を成立させる操作は、開発中のscoped Evidenceから自動実行しません。releaseを行う判断が明示された時点で、`release/v0.2.0/RELEASE_ACCEPTANCE.md`の条件へ戻ります。

Operational / Adoption / Outcomeは、実利用後に初めて測れる価値を含みます。現段階で数値KPIを固定しすぎず、過去Decisionの再構成負担、Provider交換後の意味継続、Unknown / Conflict保持の有用性、入力負担等を候補として扱い、実利用から測定方法を精緻化します。

## 7. 作業の停止線

次の場合は、実装へ急いで進まず上流へ戻ります。

- 何を価値として守るか説明できない。
- RequirementがProduct Valueとつながらない。
- 同じRequirementを既存REQが既に包含している可能性が高い。
- UIやProvider固有schemaをUniversal Coreへ持ち込もうとしている。
- repository取得方式やcredential方式をsemantic identityへ混ぜようとしている。
- fixture / helper process / artifact PASSだけを理由に実Providerのproduct-level達成を主張しようとしている。
- 未定事項を「実装しやすいから」という理由で確定しようとしている。

## 8. 計画文書の更新単位

上流作業では、必要に応じて次を同じ変更単位で更新します。

- Product文書
- Product Milestone
- Issue / ADR
- Requirement / Acceptance Scenario
- Evidence文書
- `plan/registry.yaml`
- `plan/document_review_registry.yaml`

文書追加・更新後は、自然な日本語となることを最重要視して全文を再ドラフトし、意味・規範強度・Evidence強度が変わっていないか最終監査します。

## 9. Natural Japanese review

current Product Value、Product Shape、Product Milestone、v0.2.0 Release Candidate boundary、ISSUE-000045〜000061、E2 / E3a / E3b-P1のactual Evidence、`hat47x/tei-platform`の実CLIとprivate repository条件、`cultural-substrate-weaving`のcurrent repository構成へ戻り、現在の上流探索順序を再監査した。Product Interaction、Packaging、Product Accessの既存scoped Evidenceを「未着手」のまま残さず、現在の主探索系列をReal Method / Provider Portabilityへ更新した。TEIについては既存CLIを利用できる実行可能性と、private source / binary acquisitionのcredential問題を分離し、helper process testをactual TEI executionへ昇格させない停止線を明示した。Cognitive Method側も、実runnerが確認できていない段階で便宜的な実装を正式Realizationとみなさない。意味、規範強度、未決事項、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施した。