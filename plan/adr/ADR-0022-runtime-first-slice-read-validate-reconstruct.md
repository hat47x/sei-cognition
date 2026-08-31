# ADR-0022: 最初のruntime sliceをread / validate / reconstructへ限定する

Status: **Accepted**  
Related Issue: **ISSUE-000032**  
Updated: 2026-08-31

## Context

SOZAのcurrent repositoryでは、Product Value、REQ / SCN、ADR、Reference Architecture、Contract Definition、Schema / Fixtureまでがactual treeに実体化され、Requirements RegistryとContract Conformanceについてfixture-scoped Executable Evidenceを得た。

次はcurrent `runtime/`を実体化する段階だが、historical candidateにはM48〜M50のGo package、runtime helper、Provider bridge等が存在した。これらを一括コピーすると、当時のMilestone順やpackage layoutをcurrent Architectureへ逆流させる危険がある。

また、ISSUE-000009ではstable Representation Profileとhistorical M47 digest mappingが未解決である。現時点でJCS / SHA-256等をruntime defaultへ固定すると、Semantic ContractとRepresentation Profileを分離したADR-0021と矛盾する。

そこで、current Contractから最初のruntime vertical sliceを再導出する。

## Decision

### 1. 最初のruntime sliceはread / validate / reconstructを所有する

最初のruntime sliceは、外部Actionの実行ではなく、current semantic recordsを読み、意味境界を検証し、historical contextを再構成することへ限定する。

```text
read
  → validate
  → reconstruct

!= authorize
!= execute
```

初期sliceは少なくとも次を扱えるようにする。

1. `soza.semantic-interchange/v1alpha1`を読み込む。
2. nested recordのContract identity / versionを識別する。
3. Logical ReferenceとExact Binding metadataを保持する。
4. Decision Memoryをbasis / unresolved / Recommendation relationとともに読み込む。
5. Capability ObservationをProvider-neutralな意味として読み込む。
6. bundle内exact recordとDecision basisの整合を検証する。
7. unknown Contract / verifier等を`not_verified`として保持できる。
8. historical reconstruction用のread modelを組み立てる。
9. semantic recordを意味を変えず再exportできる。

### 2. Executionはfirst sliceへ含めない

次は初期runtime scope外とする。

- Action Intent dispatch
- Authorization enforcement
- workflow engine
- queue / retry
- agent-turn routing
- Provider execution session
- deployment lifecycle
- automatic best-candidate selection

これらは重要でないから外すのではなく、SOZAが最初に所有すべき意味が「実行制御」ではなく「意味と判断の再構成」であるため、順序を分ける。

Executionを将来追加する場合も、DecisionやAuthorityと別境界として行う。

### 3. Runtime implementationはsemantic authorityにならない

runtime struct、package layout、interface名は、current Contractを実装する手段である。

```text
Runtime type != Contract semantic authority
```

semantic conflictが起きた場合、実装の都合を根拠にContract Definitionを書き換えない。Product Value、REQ、ADR、Contractへ戻って判断する。

### 4. Goをcurrent implementation laneとするがUniversal requirementにはしない

current runtime implementationはGoを基本とする。

理由:

- current開発環境でcompile / testしやすい。
- small portable runtime / adapter実装に適する。
- historical candidateにもGo資産があり、意味を再評価したうえで部分再利用できる可能性がある。

ただし、

```text
Go implementation != SOZA semantic identity
```

とする。

別言語実装が同じContract / conformanceを満たすことを妨げない。

### 5. Package境界はArchitecture concernと一対一に固定しない

`Decision Memory`、`Capability`、`Persistence`等のArchitecture concernを、そのまま必ず一つずつGo package / serviceへ対応させない。

初期実装では保守可能な小さなpackageへ分けられるが、package構成自体をADRの恒久的意味にはしない。

packageを再編してもContract conformanceが保たれることを優先する。

### 6. Provider adapterはProvider固有stateとCapability Observationの間に置く

Provider adapterの役割は、Provider内部SchemaをSOZA Coreへコピーすることではない。

```text
Provider state
  → Adapter / Mapping
  → Capability Observation
  → Matching / Decision may consume
```

adapterが変換、unit換算、status解釈、aggregation等を行う場合、そのmapping provenanceを後から追える設計を優先する。

first sliceではproduction TEI adapterを必須にしない。synthetic Provider inputからCapability Observationを生成するtest adapterでruntime境界を先に検証できる。

### 7. Exact Bindingはmetadata / equality boundaryを実装し、stable verifierを先取りしない

current runtimeはExact Bindingを、少なくとも次の意味として保持できる必要がある。

- logical reference
- content digest
- Representation Profile identity / version

また、bundle内exact recordとDecision basisが同じbindingを指すかを比較できる必要がある。

一方、stable verifierの実装はISSUE-000009を尊重する。

runtimeへは交換可能なverifier boundaryを置けるが、JCS / SHA-256等をUniversal defaultとしてhard-codeしない。

verifier不在や未知Profileは`not_verified`、実際に検証して不一致なら`failed`と区別する。

### 8. historical Go candidateは差分材料として再利用する

historical candidateのGo codeは、次の順序で再評価する。

1. current Contractで必要な責務か確認する。
2. current Schema / Fixtureの意味と一致するか確認する。
3. Milestone名、old field、old package identityを意味として継承しない。
4. 必要部分だけcurrent runtimeへ移植または再実装する。
5. current CIでEvidenceを取り直す。

```text
historical code exists != current runtime adopted
```

### 9. runtime AcceptanceはContract fixtureとのend-to-end接続で行う

runtimeの最初のExecutable Acceptanceは、単なる`go test`成功だけにしない。

少なくとも、current `fixtures/contracts/v1alpha1/`の意味をruntimeへ読み込み、次を確認する。

- F1〜F7のCapability Observation意味を保持できる。
- Recommendation without Decisionを扱える。
- Decision with unresolved stateを扱える。
- same-logical-id lineage violationを拒否できる。
- mismatched exact bindingを拒否できる。
- unknown Contractを完全理解済みとして扱わない。
- partial knowledgeを正常に読み込める。

runtime独自fixtureを増やす場合も、可能な限りContract Scenarioへ戻して意味を確認する。

## Consequences

### Positive

- SOZAの中心をExecution engineではなく意味再構成へ保てる。
- current Contractからruntimeへ一方向に設計を降ろせる。
- historical Go codeの有用部分を再利用しつつ、旧Milestone構造を継承せずに済む。
- stable Representation Profile未確定状態を破らずruntime実装を開始できる。
- Provider固有SchemaがUniversal Coreへ漏れにくい。
- runtime package再編とsemantic compatibilityを分離できる。

### Costs

- 初期runtimeは外部Actionを実行しないため、見た目上の自動化機能は限定される。
- historical codeを一件ずつcurrent Contractへ照合する必要がある。
- Contract JSON SchemaとGo型の同期監査が必要になる。
- unknown Contract / Profileを明示的に扱うため、単純なunmarshal-only実装より境界処理が増える。

## Revisit conditions

次の場合に再検討する。

- read / validate / reconstructだけではProduct Valueの重要Scenarioを検証できないことが示された。
- Provider executionとの境界を置かないことでhistorical reconstructionが損なわれる具体例が反復する。
- Go implementationがcross-language interoperabilityを実質的に妨げる。
- Contract / runtime二層管理より安全で可読なauthority modelがactual Evidenceで示される。

## Evidence / Follow-up

- `architecture/SOZA_REFERENCE_ARCHITECTURE.md`
- `contracts/CONTRACT_CATALOG.md`
- `contracts/CONFORMANCE_EVIDENCE_2026-08-31.md`
- ISSUE-000032
- ISSUE-000009
- ISSUE-000022

runtime実装とend-to-end conformanceは後続Issueで追跡する。

## Natural Japanese review

current Contract、17 fixture、actual CI Evidence、runtime未実体化状態、ISSUE-000009のBlockerへ戻ってDecisionを確定した。その後、runtime実装の都合をsemantic authorityへ逆流させず、意味、制約、未解決範囲を変えないことを確認しながら、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。
