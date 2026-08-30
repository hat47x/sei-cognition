# ADR-0020: Requirementsの追跡・状態・Evidence境界を定める

Status: **Accepted**  
Related Issue: **ISSUE-000025**  
Updated: 2026-08-31

## Context

SOZAのactual repositoryでは、Product Value / Value Model / Value Acceptance / Vision / PrinciplesとPlan文書は実体化されている一方、`requirements/`はまだ存在しない。

過去candidate bundleにはProduct RequirementsやAcceptance Scenariosが存在したが、現在のProduct Valueへ再照合する前に正本へ戻すと、古いMilestone構造、旧Product Boundary、旧Evidence状態を無意識に継承する危険がある。

また、RequirementそのものがAcceptedであることと、そのRequirementがactual repositoryやproductionで実証済みであることは別である。

このため、Requirementsを実体化する前に、stable identity、Product Value追跡、ADRとの責務分離、Evidenceの高さを固定する。

## Decision

### 1. Requirement IDはstableな単一namespaceとする

Product Requirementの恒久IDは、4桁固定の`REQ-0001`形式とする。

```text
REQ-0001
REQ-0002
...
REQ-9999
```

IDには次を埋め込まない。

- V1〜V8等のValue Axis
- M48 / M49 / M50等のMilestone
- Functional / NFR等のtype
- Core / Profile / Provider等の配置
- Proposed / Accepted等のstatus

これらは将来変わり得るため、metadataとして保持する。

### 2. Acceptance Scenarioは独立IDで管理する

Acceptance ScenarioはRequirementそのものとは分け、4桁固定の`SCN-0001`形式とする。

```text
SCN-0001
SCN-0002
...
SCN-9999
```

一つのScenarioが複数Requirementや複数Value Axisを同時に検証してよい。一つのRequirementに複数Scenarioが対応してもよい。

```text
Requirement != Acceptance Scenario != Test Case
```

Scenarioは意味上の利用・検証状況を表し、具体的なtest implementationは下位Evidenceとする。

### 3. Requirement typeはmetadataとし、namespaceを分割しない

少なくとも次のtypeを利用できる。

- `Semantic`
- `Functional`
- `Non-functional`
- `Constraint`
- `Interoperability`

必要に応じて追加できるが、typeごとに別ID空間を作らない。

同一Requirementが複数の性質を持つ場合は、primary typeと補助tagで扱える。

### 4. Requirementは「何が必要か」を定め、ADRは「どの設計判断を採るか」を定める

Requirement本文へ、特定の実装方法や現在の候補設計を不用意に固定しない。

```text
Product Value
  → Requirement: what / why / constraint
  → ADR: architectural decision
  → Architecture: concrete structure
  → Implementation
```

ただし、Product Valueを守るために方式自体が要求となる場合は例外とする。その場合も、なぜ方式が価値上不可欠なのかを明示する。

### 5. Product Value V1〜V8との追跡を持つ

Accepted Requirementは、原則として少なくとも一つのProduct Value Axisまたは明示的なProduct Principleへ追跡できなければならない。

主なValue Axisは次のとおり。

- V1 Historical Reconstruction
- V2 Semantic Separation
- V3 Revision Integrity
- V4 Provider Independence
- V5 Uncertainty Preservation
- V6 Human / AI Readability
- V7 Progressive Explicitness
- V8 Execution Independence

すべてのRequirementへ8軸を形式的に付けることはしない。関係する軸だけを付与する。

Value Axisが付かないRequirementを禁止はしないが、その場合はProduct Principle、legal / interoperability constraint等の別根拠を明示する。

### 6. Requirement statusとEvidence statusを分離する

Requirementの意味上の状態は、次を基本とする。

- `Proposed`
- `Accepted`
- `Rejected`
- `Superseded`
- `Deprecated`

これとは別に、Value Acceptanceに従ってEvidenceの高さを管理する。

各RequirementまたはScenarioについて、必要に応じて次を独立に記録する。

- Design Acceptance
- Executable Acceptance
- Release Acceptance
- Operational Acceptance

各層の状態は、原則として次を使う。

- `Satisfied`
- `Partially Satisfied`
- `Not Satisfied`
- `Not Yet Verified`
- `Not Applicable`

```text
Requirement Accepted != Executable Evidence Satisfied
```

Requirementを採用しただけで実装済みとはしない。

### 7. canonical Requirements文書とScenario文書を分ける

初期baselineでは、次をcanonical entry pointとする。

```text
requirements/
  README.md
  PRODUCT_REQUIREMENTS.md
  ACCEPTANCE_SCENARIOS.md
  history/
```

`PRODUCT_REQUIREMENTS.md`はREQ IDを持つcurrent requirement registryとして扱う。

`ACCEPTANCE_SCENARIOS.md`はSCN IDを持つcurrent scenario registryとして扱う。

将来、量が増えた場合は個別ファイルへ分割できるが、REQ / SCNのlogical identityは変えない。

`history/`にはhistorical candidateや旧Requirementとのmappingを置ける。historical文書をcurrent canonical requirementと混ぜない。

### 8. Requirementの最小記載項目を定める

AcceptedまたはProposed Requirementには、原則として次を持たせる。

- ID
- Title
- Status
- Type
- Requirement statement
- Rationale
- Related Product Value / Principle
- Scope / Non-goals
- Related Scenarios
- Related ADR / Issue
- Acceptance / Evidence state
- Revisit / Supersession information（必要な場合）

すべてを機械的な長文にする必要はない。意味を復元するために必要な情報を優先する。

### 9. historical candidateはprovenance付きで再評価する

過去candidate Requirementをcurrent baselineへ採用する場合、次を行う。

1. current Product Value / Value Model / Value Acceptanceへ照合する。
2. current Product Boundaryへ照合する。
3. historical requirement IDや文書名をprovenanceとして残す。
4. current REQ IDを新たに付与する。
5. historical `VERIFIED` / PASS等のEvidence状態を自動継承しない。
6. actual repositoryで再検証するまでExecutable Acceptance以上を引き上げない。

historical文書の文言をそのままコピーすることを目的にしない。

### 10. Product Value変更時はRequirementを上位から再監査する

Product Value / Value Model / Value Acceptanceが意味変更された場合は、影響するREQを特定して再監査する。

Requirementの意味が変わる場合は、単に本文を黙って書き換えず、必要に応じてSupersessionや変更履歴を残す。

Git commitだけをsemantic revisionの唯一の表現にはしない。

### 11. 自然な日本語をRequirement品質の一部とする

Requirement statementは、英語の断片や機械的な名詞列だけで意味を成立させない。

技術用語の識別に英語が必要な場合は保持するが、何が要求されているかを日本語本文から読めるようにする。

文書作成後は、意味、強度、例外、留保を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を行う。

## Requirement statementの強度

Requirement statementでは、必要に応じて次の強度をmetadataまたは本文で区別できる。

- `MUST` — Product Value / interoperability / safety等のため必須
- `SHOULD` — 原則として満たすが、明示的なtrade-offで例外を認め得る
- `MAY` — 許容される選択肢

日本語本文では、強度が読める自然な表現を併用する。

`MUST`を増やすこと自体を品質としない。Product Value上の必要性が説明できる場合に用いる。

## Consequences

### Positive

- Product ValueからRequirementへ追跡しやすくなる。
- Milestoneや実装方式がRequirement identityへ固定されにくい。
- Requirement採用と実装Evidenceを混同しにくい。
- historical candidateを価値ある資料として残しながら、current baselineへ無条件に継承しないで済む。
- Acceptance Scenarioを複数Requirement横断で再利用できる。
- 文書分割後もstable IDを維持できる。

### Costs

- historical candidateからcurrent REQへmappingする作業が必要になる。
- Evidence状態をRequirement statusとは別に管理する必要がある。
- actual repositoryのfixtureが揃うまでは、多くのExecutable Acceptanceが`Not Yet Verified`になる。

## Revisit conditions

次の場合に再検討する。

- REQ-0001形式では規模・federation・外部公開上のidentity管理が不足する。
- Requirementsを一つのregistry文書へまとめる方式が編集競合や可搬性を大きく損なう。
- actual operationで別namespaceが必要なRequirement種別が反復して現れる。
- RequirementとScenarioの分離がhistorical reconstructionを妨げる。

## Evidence

- `product/value/SOZA_PRODUCT_VALUE.md`
- `product/value/SOZA_VALUE_MODEL.md`
- `product/value/SOZA_VALUE_ACCEPTANCE.md`
- `plan/README.md`
- ISSUE-000022 actual tree audit
- ISSUE-000025

## Follow-up

actual `requirements/` baselineの作成とhistorical candidate mappingはISSUE-000026で実施する。

## Natural Japanese review

Requirementのidentity、Value追跡、Evidence、ADRとの責務境界を確定した後、技術的意味、強度、留保を変えず、自然な日本語となることを最重要視して全文を再ドラフトした。その後、最終意味監査を実施済み。
