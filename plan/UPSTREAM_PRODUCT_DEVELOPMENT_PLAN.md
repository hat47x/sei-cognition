# SOZA 上流プロダクト開発計画

更新日: 2026-09-01  
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
- `product/vision/SOZA_PRODUCT_VISION.md`
- `product/principles/SOZA_PRODUCT_PRINCIPLES.md`
- `product/roadmap/SOZA_PRODUCT_MILESTONES.md`

下位作業がこの層と矛盾した場合は、実装を先に温存しません。矛盾がProduct Value側の誤りを示すならEvidenceを明示して再基線化し、そうでなければ下位設計を修正します。

### Priority B — 未定領域の探索

現時点でRequirementとして十分に定まっていない領域は、まずOpen Questionとして扱います。

現在の代表例は次です。

- first usable Product Interaction
- Packaging / Deployment
- Product Identity / Authorization / Collaboration
- 実Cognitive Method Realizationの交換
- 実Provider / TEI / SaaS等をまたぐproduct-level portability
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

- 人間が最初に触るsurfaceは、本当にWeb UIである必要があるか。
- single-user packageでcanonical stateを保持する最小Storage要件は何か。
- product login identityとhistorical actor referenceは同じidentityを要求するか。

この段階では選択肢をRequirementへ固定しません。

### Step 2 — チャット上の議論・資料調査を行う

設計上の論点、利用場面、失敗例、既存技術、代替案を広く検討します。

チャットは探索と統合の作業空間として利用できますが、**チャット上の結論そのものをcurrent正本にはしません**。後続作業でIssue、Product文書、Requirement、ADR等へ必要な内容を移します。

### Step 3 — 実証実験を設計する

議論だけで判断しにくい場合は、小さなprototype、fixture、comparison harness、human review、provider接続試験等を作ります。

実験は、実装候補を完成させることより、次のような問いに答えることを優先します。

- 意味境界が本当に必要か。
- 既存Requirementで十分か。
- どの選択肢が利用負担を減らすか。
- ProviderやUIを交換しても意味が残るか。
- 失敗時に何が失われるか。

### Step 4 — Evidenceの高さを記録する

実験結果は、少なくとも次を区別します。

```text
Design Evidence
  != Executable Evidence
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

synthetic fixtureのPASSを実利用Requirementの実証へ自動昇格させません。

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

たとえばPMS-03で「人間とAIがusable interactionから同じcanonical meaningへ触れられる」ことを求めても、Web UI、MCP、CLI等の具体方式はOpen Questionのままにできます。

```text
Milestone outcome
  != implementation choice
  != Universal Requirement field list
```

## 6. 現在の主要探索系列

### 6.1 Product Interaction

入口: ISSUE-000045。

まず、human / AI parity、light / audit Projection、canonical authority、最小操作を整理します。protocol / UI technologyは、その後に比較します。

### 6.2 Packaging / Deployment

入口: ISSUE-000046。

最小supported package、Storage、import / export、migrationを整理します。deployable unitをsemantic ontologyへしません。

### 6.3 Identity / Authorization / Collaboration

入口: ISSUE-000047。

semantic Responsibility / Authorityとproduct access permissionを分離したまま、single-userからteam利用へ進める条件を調べます。

### 6.4 Real Method / Provider Portability

current Cognitive Method Contract、Provider Adapter、Product Journey harnessを基礎に、実Realization / Providerを交換したときの意味保存を検証します。

新しいUniversal型を追加する前に、既存Contract / Reference / opaque extensionで十分かを確認します。

### 6.5 Operational / Adoption Outcome

Release後に初めて測れる価値については、現段階で数値KPIを固定しすぎません。

Product Valueが実際に届いたかを検証するため、過去Decisionの再構成負担、Provider交換後の意味継続、Unknown / Conflict保持の有用性、入力負担等を候補として扱い、実利用から測定方法を精緻化します。

## 7. 作業の停止線

次の場合は、実装へ急いで進まず上流へ戻ります。

- 何を価値として守るか説明できない。
- RequirementがProduct Valueとつながらない。
- 同じRequirementを既存REQが既に包含している可能性が高い。
- UIやprovider都合をUniversal Coreへ持ち込もうとしている。
- fixture PASSだけを理由にproduct-level達成を主張しようとしている。
- 未定事項を「実装しやすいから」という理由で確定しようとしている。

## 8. 計画文書の更新単位

上流作業では、必要に応じて次を同じ変更単位で更新します。

- Product文書
- Product Milestone
- Issue / ADR
- Requirement / Acceptance Scenario
- `plan/registry.yaml`
- `plan/document_review_registry.yaml`

文書追加・更新後は、自然な日本語となることを最重要視して全文を再ドラフトし、意味・規範強度・Evidence強度が変わっていないか最終監査します。

## 9. Natural Japanese review

current Product Value、Product Shape、Product Journey、ISSUE-000045〜000050、5段階Evidence、Moving Future Horizonへ戻り、未定領域を早期にRequirementへ固定しない上流開発手順として再構成した。チャット上の議論と実証実験を探索入力として認めつつ、current正本はrepository文書へ戻す境界を明示し、意味と規範強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。