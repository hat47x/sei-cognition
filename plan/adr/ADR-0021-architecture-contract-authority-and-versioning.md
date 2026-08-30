# ADR-0021: Architecture / Contractの権威関係と版管理境界を定める

Status: **Accepted**  
Related Issue: **ISSUE-000028**  
Updated: 2026-08-31

## Context

current SOZA repositoryでは、Product Value、Requirements、ADRまでのDesign baselineが実体化された。

次にArchitecture / Contractsをactual treeへ戻す必要があるが、historical candidateには、Architectureの説明文書、Contractの意味定義、machine-readable schema、実装review、Milestone planningが同じ階層へ混在していた。

たとえば旧candidateには、`CORE_BOUNDARY_REVIEW_v1.md`、`M49_DECISION_MEMORY_BOUNDARY_v1.md`、`M50_CAPABILITY_CHOICE_BOUNDARY_v1.md`、`SEMANTIC_PERSISTENCE_CONTRACT_v1.md`、`INQUIRY_EPISTEMIC_ARTIFACTS_v1.md`、JCS / SHA-256 representation profile等が存在する。

これらの意味核には再利用価値がある一方、M48 / M49 / M50という実装順序、当時のfield候補、Go / JSON / JCS等の実装選択をcurrent architectureへそのまま戻すと、ADR-0018のProduct Value authorityやADR-0020のRequirement境界を逆転させる危険がある。

そこで、Architecture、Contract、ADR、Implementationの責務と権威関係を明示する。

## Decision

### 1. Architectureはcurrentな構造説明であり、Decision logではない

Architecture文書は、Accepted RequirementとADRを、現在どのような構造・境界・関係として実現するかを説明する**current design view**とする。

```text
Product Value
  → Requirement
  → ADR
  → Architecture
  → Contract
  → Implementation / Test
```

Architecture内で新しい重要な設計判断が必要になった場合は、Architecture本文だけで確定せず、Issue / ADRへ戻す。

```text
Architecture description != Architecture Decision Record
```

ADRとArchitectureが矛盾する場合、単にArchitectureを最新だから正しいとはみなさない。まず矛盾を設計不整合として扱い、必要ならADRのSupersessionを行う。

### 2. Architecture current viewへMilestone identityを埋め込まない

current canonical Architecture文書の名前や意味境界へ、M48 / M49 / M50等の実装順序を埋め込まない。

Decision Memory、Capability Choice、Persistence等は、現在の意味上の関心領域として表現する。

historical Milestone文書は`architecture/history/`のprovenanceとして保持・対応付けできる。

### 3. Architecture文書自体には恒久的な数値IDを要求しない

RequirementやADRと異なり、Architecture文書はcurrent viewとして更新される。

初期current baselineでは、次をcanonical entry pointとする。

```text
architecture/
  README.md
  SOZA_REFERENCE_ARCHITECTURE.md
  TRACEABILITY.md
  history/
    HISTORICAL_ARCHITECTURE_MAPPING.md
```

設計関心領域が大きくなった場合は個別Architecture文書へ分割できる。

重要なsemantic Decisionの恒久identityはADRが担うため、Architecture filenameへ別の連番体系を重ねない。

### 4. Architectureの関心領域はruntime componentと同一視しない

current Reference Architectureでは、たとえば次の関心領域を区別できる。

- Durable Semantic Core
- Inquiry / Epistemic State
- Cognitive Method
- Decision Memory
- Capability Definition / Observation / Choice
- Responsibility / Authority boundary
- Semantic Reference / Revision / Exact Binding
- Profile / Policy
- Federation / Selective Disclosure
- Provider / Adapter
- Projection
- Persistence

これらは意味設計を読み解くためのarchitecture concernであり、そのまま一対一のGo package、service、database、processへ変換することを要求しない。

```text
Architecture concern != runtime component
```

### 5. Contractは相互運用・検証が必要な境界だけを規範化する

Contractは、複数component、Provider、Storage、version、implementation等をまたいで、同じ意味を交換・検証する必要がある場合に作る。

Contractを新設する理由の例:

- portable semantic interchange
- exact historical binding
- Decision Memory interchange
- Capability Observation interchange
- Profile / Federation exchange
- representation verification

単にArchitectureを詳しく説明するためだけにContractを作らない。

### 6. Contractはlogical identityとexplicit versionを持つ

Contractには、filenameとは別にlogical identityとversionを明示する。

例:

```text
contract_id: soza.semantic-interchange
version: v1alpha1
```

pre-stable Contractは`v1alpha1`、`v1alpha2`等として更新できる。

stable `v1`以降で意味上の後方互換性を壊す変更を行う場合は、新しいmajor versionへ進める。

pre-stable段階でも、過去DecisionやArtifactが特定versionをbasisとしている場合は、当時versionをhistoricalに特定できるようにする。

Contract versionはGit commitやStorage revisionと同一ではない。

### 7. semantic ContractとRepresentation Profileを分ける

たとえば「どのArtifactをどう参照し、どの意味を交換するか」というsemantic Contractと、「JSONをどうcanonicalizeし、どのdigest algorithmで検証するか」というRepresentation Profileを同一視しない。

```text
Semantic Contract != Representation Profile
```

JSON、CBOR、JCS、SHA-256等を採用しても、その実装方式をUniversal semantic meaningへ昇格させない。

Representation Profileは交換可能であり、必要なContractがどのProfileを使用したかを参照できる形を優先する。

### 8. human-readable Contract Definitionをsemantic normative sourceとする

初期baselineでは、Contractごとに自然言語で意味、invariant、field / relationの役割、Unknownやversioningの規則を説明するMarkdown Contract Definitionを置く。

machine-readable schemaは、そのsemantic Contractの**検証可能なrepresentation**として扱う。

```text
Contract Definition
  → machine-readable schema / profile
  → conformance test
```

schemaにしか存在しない新しいsemantic requirementを作らない。

Markdownとschemaが矛盾した場合、どちらかを黙って正しいものとして処理せず、Contract inconsistencyとして修正する。意味判断はProduct Value、Requirement、ADR、Contract Definitionへ戻る。

schemaで表現できないinvariantがある場合は、自然言語だけに隠さず、可能な範囲で別のvalidator / fixtureへ落とす。

### 9. Contract fileの存在をExecutable Evidenceとしない

Contract DefinitionやJSON Schemaがactual treeに存在しても、それだけではimplementation conformanceを意味しない。

```text
Contract exists != Implementation conforms
Schema validates example != Operational interoperability
```

Value Acceptanceに従い、少なくともDesign / Executable / Release / Operational Evidenceを分離する。

### 10. historical candidateは意味核・反例・設計系譜として再評価する

historical Architecture / Contractをcurrent baselineへ利用するときは、次を行う。

1. current REQ / SCNへ対応付ける。
2. current ADRと矛盾しないか確認する。
3. 再利用する意味核を特定する。
4. Milestone、package、field、algorithm、evidence stateを自動継承しない。
5. current Architecture / Contractへ統合したか、historyへのみ残したかをmappingに記録する。

旧文書の数をcurrent文書数として保存することを目的にしない。

### 11. traceabilityをcurrent Architectureの必須品質とする

current Architecture / Contractは、重要な境界について次を遡れるようにする。

```text
Product Value V1〜V8
  → REQ
  → ADR
  → Architecture concern
  → Contract（必要な場合）
  → Fixture / Test / Evidence（将来）
```

すべてのparagraphへ機械的なtrace tagを付けることは求めない。

ただし、Universal Coreへ概念を置く、Provider境界を固定する、historical reconstructionに関わる等の重要箇所では追跡を省略しない。

### 12. 自然な日本語をArchitecture / Contract品質の一部とする

Architecture / Contract文書は、内容と構造を確定した後、意味、規範強度、例外、未決事項を変えず、自然な日本語となることを最重要視して全文を再ドラフトする。

その後、文章を滑らかにしたことでMUST / SHOULD相当の強度や、Core / Profile / Provider等の境界が変わっていないか最終意味監査を行う。

## Consequences

### Positive

- historical M48 / M49 / M50の意味核を再利用しつつ、実装順序をcurrent ontologyへ固定しないで済む。
- ADRとArchitectureの二重Decision log化を避けられる。
- ContractとArchitectureの責務が明確になる。
- human-readable semanticsとmachine-readable validationを両立しやすい。
- JCS / SHA-256 / JSON等を交換可能なRepresentation Profileとして扱える。
- Product ValueからExecutable Evidenceまでの追跡線を作りやすい。

### Costs

- historical candidateを一件ずつcurrent REQ / ADRへ再照合する必要がある。
- Markdown Contract Definitionとschemaの同期監査が必要になる。
- Contract versionとGit revisionを別に管理する必要がある。
- current Architectureを作る際、old milestone文書を単純コピーできない。

## Revisit conditions

次の場合に再検討する。

- Architecture current viewにstable document identityが必要な外部利用が反復する。
- Contract Definitionとmachine-readable schemaの二層管理が重大な同期不良を繰り返す。
- 自動生成によって別のauthority modelの方が意味保存性・可読性とも明確に優れることが実証される。
- federation等でContract versioningにより強い互換性規則が必要になる。

## Evidence

- `product/value/SOZA_VALUE_MODEL.md`
- `product/value/SOZA_VALUE_ACCEPTANCE.md`
- `requirements/PRODUCT_REQUIREMENTS.md`
- `requirements/ACCEPTANCE_SCENARIOS.md`
- ADR-0017〜ADR-0020
- historical `CORE_BOUNDARY_REVIEW_v1.md`
- historical `SEMANTIC_PERSISTENCE_CONTRACT_v1.md`
- historical `M49_DECISION_MEMORY_BOUNDARY_v1.md`
- historical `M50_CAPABILITY_CHOICE_BOUNDARY_v1.md`
- historical Contract / schema candidate群

## Follow-up

current Architecture baselineの実体化はISSUE-000029、current Contract baselineの実体化はISSUE-000030で追跡する。

## Natural Japanese review

historical candidateの意味核とcurrent Product / Requirement / ADRの権威関係を照合してDecisionを確定した後、条件、規範強度、例外、Evidence境界を変えず、自然な日本語となることを最重要視して全文を再ドラフトした。その後、最終意味監査を実施済み。
