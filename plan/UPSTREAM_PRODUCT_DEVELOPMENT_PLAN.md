# SOZA 上流プロダクト開発計画

更新日: 2026-09-02  
状態: **Current Upstream Planning Baseline — v0.2.0 Release Evidence / E3b-P2 fixed-artifact / E3b-M1b / historical reconstruction H1-H2 reflected**

## 1. この文書の役割

この文書は、SOZAのProduct Value、Milestone、Requirement、ADR、Architecture、Implementationを、どの順序で具体化するかを定めます。

目的は、未定領域を実装都合で早期に固定せず、**上位価値へ戻りながら、議論と実証を通して必要な要求だけを正本化すること**です。

期限やcalendar scheduleは扱いません。優先順位は、Product Valueへの影響、未確定部分が下位設計を拘束する度合い、次の実証を可能にする依存関係によって決めます。

## 2. 上位から下位への基本順序

原則として、次の順序で進めます。

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

コードやexisting schemaを上位概念の根拠として逆輸入しません。一方、実装や実験から得た反証Evidenceは、上位仮説を見直す正当な入力とします。

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

下位作業がこの層と矛盾した場合、実装を先に温存しません。矛盾がProduct Value側の誤りを示すならEvidenceを明示して再基線化し、そうでなければ下位設計を修正します。

### Priority B — 未定領域の探索

Product Interaction、Local Single-Node Packaging、Product Access責務分離は、Design baselineと限定されたExecutable Evidenceまで進みました。v0.2.0 Local Reference Product Baselineについてはactual Release Evidenceも成立しています。

Real Method / Provider Portabilityでは、E2、E3a、E3b-P1、E3b-M1aに加え、E3b-P2でも固定revisionのactual TEI CLIをbuild・実行し、current SOZA Adapterへ戻す範囲までScoped Executable Evidenceが得られました。E3b-M1bでは、M1aと同じKJ Atlas Method surfaceを実際に推論するmodel artifactへ接続し、actual inferenceからcurrent Cognitive Method Applicationへのmappingまでを確認しました。

さらにISSUE-000067のH1 / H2では、Method Realization交換後のhistorical reconstructionを検査しました。実現機構が異なるM1a / M1bを別Realizationとして保持し、model / runtime等の具体条件をopaque Provenanceへ残せることをactual workflowで確認しています。同一Realization内のhistorical revisionについても、必要な場合はExact Bindingで当時のrevisionへ固定できることを確認しました。

現在の主要な未定領域は次です。

- E3b-P2: SOZA Actionsからprivate TEIを継続取得するrepository-scoped credentialを、どの運用境界で供給するか
- E3b-P2: fixed revision以外のTEI versionへ交換してもcurrent Adapter境界とhistorical reconstructionを保てるか
- E3b-M1b後続: model出力品質とKJ法としての成果品質を、semantic execution Evidenceと分離してどのように評価するか
- H1 / H2で確認した境界を越えて、任意のProvider / Realization / model / runtime versionへ交換してもhistorical reconstructionを保てるか
- network degradation、rate limit、credential失効、model acquisition failure等をどのEvidence段階で扱うか
- formal integration protocolを本当に標準化する必要があるか
- E4 Operational portabilityを何で観測するか
- release後のOperational / Adoption / Outcomeを、Product Valueと対応させてどう評価するか

actual v0.2.0 Releaseそのものは未定領域ではありません。既に成立したRelease Evidenceを維持しつつ、post-releaseのE3b Evidenceをv0.2.0 supported scopeへ遡及的に追加しません。

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

- actual TEI CLIを呼ぶために、SOZAがrepository取得方式まで知る必要は本当にあるか。
- external Cognitive Methodを実外部modelで動かした後、実行成立と生成品質をどの評価境界で分けるか。
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
- ProviderやRealizationを交換しても意味が残るか。
- Method outputとRecommendation / Decisionを分離できるか。
- 失敗時に何が失われるか。
- artifact取得、credential、process invocation、semantic mappingを分けられるか。
- live processが動いたことと、modelやMethodの品質を分けて評価できるか。
- model / runtimeを交換したとき、過去Applicationを再構成するためのProvenanceが不足しないか。

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

synthetic fixture、helper process、version固定artifact、public live service、deterministic model stub、actual model inferenceのPASSを、それぞれが確認していない実運用品質や生成品質のEvidenceへ自動昇格させません。credential-aware workflow全体がsuccessでも、actual external process stepがskipされた場合は、そのprocessのExecutable Evidenceとして数えません。

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

たとえばPMS-06でactual TEIやactual model-backed Methodを接続することを求めても、GitHub token、private clone、CLI配布方式、Ollama、特定model tag、HTTP / gRPC / MCP等の具体方式をStable Requirementにする必要はありません。

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

v0.2.0ではLocal Reference Product Baselineをactual releaseし、Release Evidenceまで成立しました。production installer、formal platform support matrix、server topology等は引き続き先取りしません。

### 6.3 Identity / Authorization / Collaboration

ISSUE-000047 / 000056で、authentication identity、Bounded Subject、Product access permission、semantic Responsibility / Authorityを分離するDesign baselineと限定されたExecutable Evidenceがあります。

production IdP / IAM、formal RBAC / ABAC、team membership lifecycle等は未検証ですが、PMS-06の実Provider / Realization交換を進めるために先に固定する必要はありません。

### 6.4 Real Method / Provider Portability

現在の主探索系列です。

Evidenceの現在地は次です。

```text
E1 Contract / in-process synthetic
  → E2 out-of-process reference exchange                  [Scoped Evidence]
  → E3a version-pinned external artifact integration     [Scoped Evidence]
  → E3b
       ├─ P1 public live Provider service                 [Scoped Evidence]
       ├─ P2 actual TEI process / service
       │    ├─ external executable injection boundary     [Scoped Evidence]
       │    ├─ fixed-artifact actual TEI CLI execution    [Scoped Evidence]
       │    └─ credential operation / arbitrary version   [Not Yet Verified]
       └─ M1 live external Cognitive Method
            ├─ M1a KJ Atlas + deterministic model stub   [Scoped Evidence]
            ├─ M1b external model-backed execution       [Scoped Evidence]
            └─ H1/H2 historical reconstruction boundary  [Scoped Evidence]
  → E4 operational portability                           [Not Yet Verified]
```

E2、E3a、E3b-P1、E3b-P2 fixed-artifact、E3b-M1a、E3b-M1b、H1 / H2には、それぞれ対象を限定したExecutable Evidenceがあります。これらを一括して「E3b全体完了」や「Operational portability成立」とは扱いません。

#### 6.4.1 E3b-P2の後続探索

TEIには`cmd/tei`が存在し、`deployment-provider-plan`、`deployment-reconcile`、`deployment-simulate`等のJSON出力面を既に持っています。このため、SOZA向けの新しいwire protocolをTEIへ追加するより、**既存TEI CLIをProvider固有の外部processとして扱う**方が現在の境界に適合します。

一方、TEI repositoryはprivateです。SOZA CIの標準`GITHUB_TOKEN`が別private repositoryを読めるとは仮定しません。

ISSUE-000061では次を分離し、外部から明示的に与えたexecutableを呼ぶ境界まではExecutable Evidence化しました。

```text
TEI source / binary acquisition
  != credential resolution
  != external process invocation
  != Provider-specific JSON decoding
  != SOZA Capability Observation mapping
```

ISSUE-000065では、TEI commit `48a7ca1fe8a9538e9e9be3e1ee08ef14804c8f67`を固定しました。最初のcredential-aware Run `33589190828`では`TEI_REPOSITORY_TOKEN`が利用できずactual TEI stepがskipされましたが、後続のTEI側Run `33589084290`でactual `cmd/tei`をbuildし、`deployment-provider-plan`をskipなしで実行しました。

生成したactual artifactをcurrent SOZA Adapterから別processとして起動し、strict decode、Capability Observation mapping / validation、Provider固有情報の非漏出まで確認しています。actual Provider Plan bytesはdigest付きfixtureとして通常CIで継続検査します。したがって、E3b-P2はfixed-artifact範囲で**Scoped Executable Evidence available**です。

次の探索点は、SOZA Actionsからprivate TEIを継続取得するcredential運用、TEI executableの配布・更新、fixed revision以外のversion交換、E4 Operational portabilityです。credentialを利用する場合も、GitHub PATや特定Secret製品をUniversal semanticsへ持ち込まず、acquisition / deployment policy側の問題として扱います。

#### 6.4.2 E3b-M1b成立後の探索

ISSUE-000064では、`hat47x/kj-atlas`の固定commitを取得し、KJ Atlas FastAPI backendと同repositoryのdeterministic model stubをSOZAとは別processとして実際に起動しました。actual `POST /ai/suggest-card-groups`を通してKJ Atlasの処理経路を実行し、結果をopaqueな`not_verified` Method outputとしてcurrent Cognitive Method Applicationへ戻せることを確認しています。

ISSUE-000066では、同じKJ Atlas revisionとMethod surfaceを保ったまま、model processだけをOllama `0.32.14`上の`qwen2.5:0.5b`へ置き換えました。actual inferenceではprompt評価とtoken生成を伴う推論を観測し、KJ Atlasがmodel outputを受理した後、既存SOZA Method mapping boundaryを通してCognitive Method Applicationへ戻せています。

この結果、M1bの「actual modelを含む実行経路が成立するか」という問いにはScoped Executable Evidenceが得られました。さらにISSUE-000067のH2では、M1aとM1bを別RealizationとしてApplicationへ残し、model / runtime等の具体条件をopaque Provenanceとして保持したままactual mappingできることを確認しました。

次に残るのは、主として次の問いです。

```text
actual model-backed execution PASS
  + H1/H2 historical reconstruction boundary PASS
  != model output quality satisfied
  != KJ-method outcome quality satisfied
  != arbitrary model/runtime portability
  != Operational portability
```

model出力品質やKJ法としての成果品質を評価する場合は、semantic execution conformanceとは別の評価系として設計します。また、H1 / H2で確認した範囲を越える任意version交換でhistorical reconstructionが不足する場合にだけ、Durable ProvenanceやRequirementの追加を再検討します。

#### 6.4.3 version交換とhistorical reconstruction

ISSUE-000067では、M1a / M1bを入力としてhistorical reconstructionの最小境界をH1 / H2で検査しました。

H1では、同じMethod Realizationの中でhistorical revisionを区別する必要がある場合、current `MethodRealization.implementation_refs`と`MethodApplication.realization_ref`にExact Bindingを利用することで、後続revisionの存在によって過去Applicationのbindingを書き換えずに保持できることを確認しました。logical-only referenceでは複数revisionから過去revisionを一意に選べないこともnegative controlとして確認しています。

H2では、deterministic model stubを使うM1aとOllama上のactual modelを使うM1bは、単なる同一Realizationのrevisionではなく実現機構が異なるため、同じMethod Definitionを実現する別のlogical Realizationとして保持しました。model名、runtime名、version、model ID等はUniversal Cognitive Method fieldへ追加せず、probe-localなopaque Provenanceへ残しています。M1a / M1bのactual workflowの双方で、この情報を保持したままSOZA Method Applicationへ戻せることを確認しました。

したがって、current boundaryは次のように整理します。

```text
実現機構が異なる
  → logical Realizationを分ける

同じRealizationのhistorical revisionを固定する必要がある
  → Exact Bindingを使う

model / runtime等の具体的な実行条件
  → 必要な範囲でProvenanceへ残す
```

この実証では、model / runtime固有fieldをUniversal Contractへ追加する必要は確認されませんでした。新しいStable Requirement / Scenarioも追加せず、REQ-0001、REQ-0004、REQ-0021、SCN-0005、SCN-0015の既存境界で扱います。

一方、H1 / H2は任意のProvider / Realization / model / runtime version交換を実証したものではありません。今後は、異なるversionや別Realizationへ交換した実環境でも同じ境界で判断記憶を継続利用できるかをE4側で観測します。

### 6.5 Release / Operational / Adoption Outcome

v0.2.0 Local Reference Product Baselineはactual release済みで、ISSUE-000063によりRelease Evidenceも成立しています。

```text
v0.2.0 Release Evidence Satisfied
  != Operational Evidence
  != Adoption / Outcome Evidence
```

post-releaseのE3b-P1、TEI executable注入境界、E3b-P2 fixed-artifact actual TEI CLI execution、E3b-M1a、E3b-M1b、H1 / H2 historical reconstructionは新しいScoped Executable Evidenceです。これらを既に公開済みのv0.2.0 supported scopeやRelease Evidenceへ遡及的に含めません。

今後の焦点は、E4として実環境でRealization / Provider / model等を交換しても判断記憶を継続利用できるかを観測することと、利用者にとっての実際の価値をOperational / Adoption / Outcome Evidenceとして分離して測ることです。

現段階で数値KPIを固定しすぎず、過去Decisionの再構成負担、Provider交換後の意味継続、Unknown / Conflict保持の有用性、入力負担等を候補として扱い、実利用から測定方法を精緻化します。

## 7. 作業の停止線

次の場合は、実装へ急いで進まず上流へ戻ります。

- 何を価値として守るか説明できない。
- RequirementがProduct Valueとつながらない。
- 同じRequirementを既存REQが既に包含している可能性が高い。
- UIやProvider / Method固有schemaをUniversal Coreへ持ち込もうとしている。
- repository取得方式やcredential方式をsemantic identityへ混ぜようとしている。
- model名、runtime名、repository名等の実装固有情報を、H1 / H2で必要性が確認されていないUniversal fieldへ昇格させようとしている。
- fixture / helper process / deterministic model stub / actual inferenceのPASSだけを理由に、それぞれが確認していない実運用品質や生成品質のproduct-level達成を主張しようとしている。
- H1 / H2のPASSだけを理由に、任意version交換やOperational portabilityまで成立したと扱おうとしている。
- credential-aware workflowのsuccessだけを理由に、skipされたactual Provider / Method executionを成功扱いしようとしている。
- post-releaseのExecutable Evidenceを既存releaseのsupported scopeへ遡及的に追加しようとしている。
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

current Product Value、Product Shape、Product Milestone、v0.2.0 Release Evidence、ISSUE-000045〜000067、E2 / E3a / E3b-P1 / E3b-P2 fixed-artifact / E3b-M1a / E3b-M1b / H1 / H2のactual Evidence、`hat47x/tei-platform`の固定CLI artifactとprivate repository条件、KJ Atlasの固定commit、actual model-backed executionへ戻り、現在の上流探索順序を再監査しました。

Product Interaction、Packaging、Product Accessの既存scoped Evidenceを「未着手」のまま残さず、Real Method / Provider Portabilityを主探索系列として維持しています。E3b-P2では最初のcredential-aware probeのskipを成功扱いせず、その後に固定revisionのactual `cmd/tei` build / executionとSOZA Adapter mappingを別経路で実証しました。E3b-M1bではactual inferenceとSOZA Method Applicationへのmappingまで成立しています。

その後のH1 / H2では、historical reconstructionに必要な意味差をさらに分けました。実現機構が異なるM1a / M1bは別Realizationとして保持し、同一Realization内のhistorical revisionは必要に応じてExact Bindingで固定できることを確認しています。model / runtime等の具体条件はopaque Provenanceへ残し、Universal Cognitive Method fieldへ持ち込んでいません。既存REQ / SCNで必要な意味を表現できたため、新しいStable Requirementも追加していません。

これにより、次の作業点を「historical reconstructionの最小境界を決めること」から、任意version交換、品質評価、E4 Operational portabilityへ移しました。v0.2.0 actual Release Evidenceは成立済みとして維持し、post-releaseのE3b / H1 / H2 Evidenceによってsupported scopeを遡及的に広げていません。

意味、規範強度、未決事項、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施しました。
