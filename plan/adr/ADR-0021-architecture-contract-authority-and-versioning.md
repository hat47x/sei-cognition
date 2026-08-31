# ADR-0021: Architecture / Contractの権威関係と版管理境界を定める

Status: **Accepted**  
Related Issues: **ISSUE-000028, ISSUE-000029, ISSUE-000030, ISSUE-000031**  
Updated: 2026-08-31

## Context

SOZAでは、Product Value、Requirements、ADR、Architecture、Contract、Implementation / Evidenceの間で、何がどの判断を所有するかを明確にする必要がある。

historical candidateでは、Architectureの説明、Contractの意味定義、machine-readable schema、実装review、Milestone planning等が近い階層へ混在していた。その意味核には再利用価値がある一方、当時のMilestone順、field候補、package構成、algorithm、Evidence状態をそのままcurrent正本へ戻すと、Product Valueから下位設計へ流れる権威関係を逆転させる危険がある。

そこで、Architecture、Contract、ADR、Implementationの責務と版管理境界を明示する。

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

ADRとArchitectureが矛盾する場合、Architectureの更新日時だけを理由に正しいものとして扱わない。まず設計不整合として確認し、必要ならADRのSupersessionを行う。

### 2. Architecture current viewへMilestone identityを埋め込まない

current canonical Architecture文書の名前や意味境界へ、historical Milestoneの実装順序を埋め込まない。

Decision Memory、Capability、Persistence等は、現在の意味上のarchitecture concernとして表現する。

historical Milestone文書は`architecture/history/`のProvenanceとして保持・対応付けできる。

### 3. Architecture文書自体には恒久的な数値IDを要求しない

RequirementやADRと異なり、Architecture文書はcurrent viewとして更新される。

current canonical entry pointは次とする。

```text
architecture/
  README.md
  SOZA_REFERENCE_ARCHITECTURE.md
  TRACEABILITY.md
  history/
    HISTORICAL_ARCHITECTURE_MAPPING.md
```

関心領域が大きくなった場合は個別Architecture文書へ分割できる。

重要なsemantic Decisionの恒久identityはADRが担うため、Architecture filenameへ別の連番体系を重ねない。

### 4. Architecture concernをruntime componentと同一視しない

current Reference Architectureでは、たとえば次の関心領域を区別する。

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

単にArchitectureを詳しく説明するためだけにContractを作らない。

### 6. Contractはlogical identityとexplicit versionを持つ

Contractにはfilenameとは別にlogical identityとversionを明示する。

例:

```text
contract_id: soza.semantic-interchange
version: v1alpha1
```

pre-stable Contractは`v1alpha1`、`v1alpha2`等として更新できる。

stable `v1`以降で意味上の後方互換性を壊す変更を行う場合は、新しいmajor versionへ進める。

pre-stable段階でも、過去DecisionやArtifactが特定versionをbasisとしている場合は、当時のversionをhistoricalに特定できるようにする。

Contract versionはGit commitやStorage revisionと同一ではない。

### 7. Semantic ContractとRepresentation Profileを分ける

「どのArtifactをどう参照し、どの意味を交換するか」というSemantic Contractと、「どのbytesをどうcanonicalizeし、どのdigest algorithmで検証するか」というRepresentation Profileを同一視しない。

```text
Semantic Contract != Representation Profile
```

JSON、CBOR、JCS、SHA-256等を採用しても、その実装方式をUniversal semantic meaningへ昇格させない。

### 8. human-readable Contract Definitionをsemantic normative sourceとする

Contractごとに、意味、invariant、field / relationの役割、Unknownやversioning等の規則を自然言語で説明するContract Definitionを置く。

machine-readable schemaは、そのSemantic Contractの**検証可能なrepresentation**として扱う。

```text
Contract Definition
  → machine-readable schema / profile
  → conformance test
```

schemaにしか存在しない新しいsemantic requirementを作らない。

Markdownとschemaが矛盾した場合、どちらかを黙って正しいものとして処理せず、Contract inconsistencyとして修正する。意味判断はProduct Value、Requirement、ADR、Contract Definitionへ戻る。

schemaだけでは表現しにくいinvariantがある場合も、自然言語だけへ隠さず、可能な範囲でvalidator / fixtureへ落とす。

### 9. Contract fileの存在をExecutable Evidenceとしない

Contract DefinitionやJSON Schemaがactual treeに存在することだけでは、implementation conformanceを意味しない。

```text
Contract exists != Implementation conforms
Schema validates example != Operational interoperability
```

Value Acceptanceに従い、Design / Executable / Release / Operational Evidenceを分離する。

### 10. historical candidateは意味核・反例・設計系譜として再評価する

historical Architecture / Contractをcurrent baselineへ利用するときは、次を行う。

1. current REQ / SCNへ対応付ける。
2. current ADRと矛盾しないか確認する。
3. 再利用する意味核を特定する。
4. Milestone、package、field、algorithm、Evidence stateを自動継承しない。
5. current Architecture / Contractへ統合したか、historyへのみ残したかをmappingに記録する。

旧文書の数をcurrent文書数として保存すること自体を目的にしない。

### 11. traceabilityをcurrent Architecture / Contractの必須品質とする

重要な境界について、次を遡れるようにする。

```text
Product Value V1〜V8
  → REQ
  → ADR
  → Architecture concern
  → Contract（必要な場合）
  → Fixture / Test / Evidence
```

すべてのparagraphへ機械的なtrace tagを付けることは求めない。

ただし、Universal Coreへの概念配置、Provider境界、historical reconstruction等の重要箇所では追跡を省略しない。

### 12. 自然な日本語をArchitecture / Contract品質の一部とする

Architecture / Contract文書は、内容と構造を確定した後、意味、規範強度、例外、未決事項を変えず、自然な日本語となることを最重要視して全文を再ドラフトする。

その後、文章を滑らかにしたことでMUST / SHOULD相当の強度やCore / Profile / Provider等の境界が変わっていないか最終意味監査を行う。

## Current realization

current repositoryでは、このADRに従って次がactual treeへ実体化されている。

- Reference Architecture / Architecture Traceability / historical mapping
- 4つのcurrent Contract family
- Contract Catalog / Traceability / historical mapping
- machine-readable schema
- 17件のContract fixture
- Contract conformance checker / GitHub Actions
- Representation Profile Definition / fixture / conformance
- first semantic runtime / Provider AdapterのExecutable Evidence

したがって、Architecture / Contractを「これから戻す」段階ではない。

一方、Contract fixture PASSやRuntime test PASSをRelease / Operational Evidenceへ昇格させないという本ADRのEvidence境界は、引き続き有効である。

## Consequences

### Positive

- historical candidateの意味核を再利用しつつ、実装順序をcurrent ontologyへ固定せずに済む。
- ADRとArchitectureの二重Decision log化を避けられる。
- ContractとArchitectureの責務が明確になる。
- human-readable semanticsとmachine-readable validationを両立しやすい。
- Representation ProfileをSemantic Contractから交換可能に保てる。
- Product ValueからExecutable Evidenceまでの追跡線を作りやすい。

### Costs

- historical candidateをcurrent REQ / ADRへ再照合する作業が必要になる。
- Contract Definitionとschemaの同期監査が必要になる。
- Contract versionとGit revisionを別に管理する必要がある。

## Revisit conditions

次の場合に再検討する。

- Architecture current viewにstable document identityが必要な外部利用が繰り返し現れる。
- Contract Definitionとmachine-readable schemaの二層管理が重大な同期不良を繰り返す。
- 別のauthority modelの方が意味保存性・可読性とも明確に優れることがactual Evidenceで示される。
- federation等でContract versioningにより強い互換性規則が必要になる。

## Natural Japanese review

current Architecture、Contract、Schema、fixture、Runtime Evidenceへ戻ってDecisionを照合した。その後、「次にArchitecture / Contractsを戻す」というDecision時点の未実体化状態をCurrent realizationへ更新し、ADR / Architecture / Contract / Implementationの権威関係とEvidence境界を変えず、自然な日本語となることを最重要視して全文を再ドラフトした。最後に規範強度を含めて意味監査を実施済みである。
