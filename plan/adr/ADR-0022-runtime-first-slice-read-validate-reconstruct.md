# ADR-0022: 最初のruntime sliceをread / validate / reconstructへ限定する

Status: **Accepted**  
Related Issues: **ISSUE-000032, ISSUE-000033, ISSUE-000036**  
Updated: 2026-08-31

## Context

SOZAでは、Product Value、REQ / SCN、Reference Architecture、Contract Definition、Schema / Fixtureまでを上位の意味基線として持ち、その下にruntime実装を置く。

historical candidateには複数のGo packageやProvider bridge等が存在したが、それらを一括コピーすると、当時のMilestone順やpackage layoutがcurrent Architectureへ逆流する危険がある。

また、current Representation Profile基線はADR-0023で定まっているが、Profileのalgorithmや特定libraryをRuntime semantic authorityへ昇格させてはならない。

そこで、current Contractから最初のruntime vertical sliceを再導出し、その責務を意味の読込み・検査・再構成へ限定する。

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

少なくとも次を扱えるようにする。

1. `sei.semantic-interchange/v1alpha1`を読み込む。
2. nested recordのContract identity / versionを識別する。
3. Logical ReferenceとExact Binding metadataを保持する。
4. Decision Memoryをbasis / unresolved / Recommendation relationとともに読み込む。
5. Capability ObservationをProvider-neutralな意味として読み込む。
6. bundle内exact recordとDecision basisの整合を検証する。
7. unknown Contract / Profile / verifier等を、既知として扱わず`not_verified`相当で保持できる。
8. historical reconstruction用のread modelを組み立てる。
9. semantic recordを意味を変えず再exportできる。

### 2. Executionはfirst sliceへ含めない

次はfirst sliceのscope外とする。

- Action Intent dispatch
- Authorization enforcement
- workflow engine
- queue / retry
- agent-turn routing
- Provider execution session
- deployment lifecycle
- automatic best-candidate selection

これらは重要でないから外すのではない。SOZAが最初にExecutable Evidence化すべき中心が「実行制御」ではなく「意味と判断の再構成」であるため、実装順を分ける。

Executionを将来追加する場合も、DecisionやAuthorityと別境界として行う。

### 3. Runtime implementationはsemantic authorityにならない

runtime struct、package layout、interface名は、current Contractを実装する手段である。

```text
Runtime type != Contract semantic authority
```

semantic conflictが起きた場合、実装の都合を根拠にContract Definitionを書き換えない。Product Value、REQ、ADR、Contractへ戻って判断する。

### 4. Goをcurrent implementation laneとするがUniversal requirementにはしない

current runtime implementationはGoを基本とする。

ただし、

```text
Go implementation != SOZA semantic identity
```

である。

別言語実装が同じContract / conformanceを満たすことを妨げない。

### 5. Package境界はArchitecture concernと一対一に固定しない

Decision Memory、Capability、Persistence等のArchitecture concernを、そのまま一対一のGo package / serviceへ対応させることは要求しない。

packageを再編してもContract conformanceが保たれることを優先する。

### 6. Provider AdapterはProvider固有stateとCapability Observationの間に置く

Provider Adapterの役割は、Provider内部SchemaをSOZA Coreへコピーすることではない。

```text
Provider state
  → Adapter / Mapping
  → Capability Observation
  → Matching / Decision may consume
```

field mapping、unit換算、status解釈、aggregation等を行う場合は、そのmapping provenanceを後から追える設計とする。

production TEI adapterをfirst sliceの成立条件にはしない。Provider-neutralな境界を先に検証する。

### 7. Exact Bindingはmetadata / equality boundaryをfirst sliceで扱う

current runtimeはExact Bindingの少なくとも次を保持できるようにする。

- logical reference
- content digest
- Representation Profile identity / version

また、bundle内exact recordとDecision basisが同じbindingを指すかを比較できる必要がある。

current Representation Profileを利用できる場合でも、それをUniversal Coreの唯一の方式としてhard-codeしない。

verifier不在や未知Profileは`not_verified`、実際に検証して不一致なら`failed`と区別する。

### 8. historical Go candidateは差分材料として再利用する

historical codeを利用する場合は、次の順に再評価する。

1. current Contractで必要な責務か確認する。
2. current Schema / Fixtureの意味と一致するか確認する。
3. Milestone名、old field、old package identityを意味として継承しない。
4. 必要部分だけcurrent runtimeへ移植または再実装する。
5. current CIでEvidenceを取り直す。

```text
historical code exists != current runtime adopted
```

### 9. runtime AcceptanceはContract fixtureとのend-to-end接続で行う

runtimeのExecutable Acceptanceは、単なる`go test`成功だけにしない。

current Contract fixtureを同じcheckoutで再検査し、その意味をruntimeへ読み込んだうえで、少なくとも次を確認する。

- F1〜F7のCapability Observation意味を保持できる。
- Recommendation without Decisionを扱える。
- Decision with unresolved stateを扱える。
- same-logical-id lineage violationを拒否できる。
- mismatched exact bindingを拒否できる。
- unknown Contractを完全理解済みとして扱わない。
- partial knowledgeを正常に読み込める。

## Current realization and Evidence

current repositoryでは、このfirst sliceがactual treeへ実体化されている。

```text
runtime/go/semanticruntime/
  model.go
  loader.go
  loader_test.go
```

さらに、ADR-0024に基づくsynthetic Provider Adapterも別packageとして追加されている。

```text
runtime/go/provideradapter/
```

`Semantic Runtime Conformance`では、同じcheckoutでcurrent Contract checkerを実行した後、`go test ./...`を実行する。

current Evidenceでは次がsuccessしている。

- Contract fixture 17件の期待結果一致
- `semanticruntime` tests
- `provideradapter` tests
- Provider固有field leakage hardening test

詳細は次を正本とする。

```text
runtime/CONFORMANCE_EVIDENCE_2026-08-31.md
```

ISSUE-000033とISSUE-000036はResolvedである。

ただし、これはAuthorization / Action execution、Production Provider integration、Release Evidence、Operational Evidenceの成立を意味しない。

## Consequences

### Positive

- SOZAの中心をExecution engineではなく意味再構成へ保てる。
- current Contractからruntimeへ一方向に設計を降ろせる。
- historical Go codeを参照しても、旧Milestone構造を継承せずに済む。
- Representation Profileを尊重しつつ、Profile実装をRuntime semantic authorityへ昇格させずに済む。
- Provider固有SchemaがUniversal Coreへ漏れにくい。
- runtime package再編とsemantic compatibilityを分離できる。

### Costs

- first runtime sliceだけでは外部Actionを実行しない。
- Contract SchemaとGo型の同期監査が必要になる。
- unknown Contract / Profileを明示的に扱うため、単純なunmarshal-only実装より境界処理が増える。
- Runtime test、Representation Profile conformance、Release / Operational Evidenceを別々に管理する必要がある。

## Revisit conditions

次の場合に再検討する。

- read / validate / reconstructだけではProduct Valueの重要Scenarioを検証できないことが示された。
- Provider executionとの境界を分けることでhistorical reconstructionが損なわれる具体例が繰り返し現れる。
- Go implementationがcross-language interoperabilityを実質的に妨げる。
- Contract / runtime二層管理より安全で可読なauthority modelがactual Evidenceで示される。

## Natural Japanese review

current Contract fixture、Representation Profile、Semantic Runtime、Provider Adapterのactual Evidenceへ戻ってDecisionを照合した。その後、runtime未実体化時点のContextとISSUE-000033 In Progressという古い状態をCurrent realizationへ更新した。read / validate / reconstructをfirst sliceとする判断、Execution / Authorityとの分離、Evidence境界を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。
