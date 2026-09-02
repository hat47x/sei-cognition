# SOZA 上流プロダクト開発計画

更新日: 2026-09-02  
状態: **Current Upstream Planning Baseline — v0.2.0 Release Evidence / E3b-M1a reflected**

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

下位作業がこの層と矛盾した場合は、実装を先に温存しません。Product Value側の見直しが必要ならEvidenceを明示して再基線化し、そうでなければ下位設計を修正します。

### Priority B — 未定領域の探索

Product Interaction、Local Single-Node Packaging、Product Access責務分離、v0.2.0 Local Reference Product Baselineのreleaseについては、それぞれDesign / Executable / Release Evidenceが現在の範囲で成立しています。

Real Method / Provider Portabilityでは、E2、E3a、E3b-P1、E3b-M1aまで限定されたExecutable Evidenceが得られました。現在の主要な未定領域は次です。

- E3b-P2: actual TEI process / serviceをどの実行面から接続するか
- TEI executableの取得・private credentialとSOZA semantic integrationをどう分離するか
- E3b-M1b: 実外部modelを用いたKJ Atlas executionでもM1aの意味境界が保てるか
- Provider / Realization version交換時に必要なProvenance / Exact Bindingの水準
- formal integration protocolを本当に標準化する必要があるか
- E4 Operational portabilityを何で評価するか
- v0.2.0以後のreleaseでsupported scopeをどこまで広げるか
- Operational / Adoption / Outcome Evidenceをどの利用場面で収集するか

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
- external Cognitive Methodをlive実行するとき、Method Definitionとrunner固有protocolをどこまで分離できるか。
- M1aで使ったmodel stubを実外部modelへ交換したとき、どの意味差が新たに必要になるか。

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
- ProviderやMethodを交換してもhistorical meaningが残るか。
- failure時にcanonical stateを壊さないか。
- artifact取得、credential、process invocation、semantic mappingを分けられるか。
- 外部system固有schemaをUniversal Contractへ持ち込まずに済むか。

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

synthetic fixture、helper process、version固定artifact、public live service、KJ Atlas + model stubのPASSを、それぞれが確認していないactual Provider、実外部model、実運用のEvidenceへ自動昇格させません。

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

たとえばPMS-06でactual TEIやexternal Cognitive Methodを接続することを求めても、GitHub token、private clone、HTTP、FastAPI、SQLite、CLI配布方式等をStable Requirementにする必要はありません。

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

v0.2.0ではLocal Reference Product Baselineをactual Releaseとして固定し、Release Evidenceまで成立しました。ただしproduction installer、formal platform support matrix、server topology等は未検証です。

### 6.3 Identity / Authorization / Collaboration

ISSUE-000047 / 000056で、authentication identity、Bounded Subject、Product access permission、semantic Responsibility / Authorityを分離するDesign baselineと限定されたExecutable Evidenceがあります。

production IdP / IAM、formal RBAC / ABAC、team membership lifecycle等は未検証ですが、PMS-06の実Provider / Method交換を進めるために先に固定する必要はありません。

### 6.4 Real Method / Provider Portability

現在の主探索系列です。

```text
E1 Contract / in-process synthetic
  → E2 out-of-process reference exchange
  → E3a version-pinned external artifact integration
  → E3b live external process / service integration
  → E4 operational portability
```

E3bは次へ分けます。

```text
E3b-P1 public live Provider service
E3b-P2 actual TEI process / service
E3b-M1a live KJ Atlas process + deterministic model stub
E3b-M1b live external model-backed KJ execution
```

E2、E3a、E3b-P1、E3b-M1aには、それぞれ対象を限定したScoped Executable Evidenceがあります。これらを一括して「E3b完了」とは扱いません。

#### 6.4.1 E3b-P2 — actual TEI

TEIには`cmd/tei`が存在し、`deployment-provider-plan`等のJSON出力面があります。このため、SOZA向けの新しいwire protocolをTEIへ追加するより、既存TEI CLIをProvider固有の外部processとして扱う方針を優先します。

一方、TEI repositoryはprivateです。SOZA CIの標準`GITHUB_TOKEN`が別private repositoryを読めるとは仮定しません。

ISSUE-000061では次を明示的に分けています。

```text
TEI source / binary acquisition
  != credential resolution
  != external process invocation
  != Provider-specific JSON decoding
  != SOZA Capability Observation mapping
```

外部から与えられたexecutableを呼べるAdapter境界にはhelper processによるScoped Executable Evidenceがありますが、actual TEI executionではありません。

次のP2実証では、TEI executable / service自体を実際に呼べる環境と、そのsource identityをどのように確認するかを先に決めます。

#### 6.4.2 E3b-M1a — KJ Atlas live execution

ISSUE-000064では、`hat47x/kj-atlas`の固定commitを取得し、KJ Atlas FastAPI backendとrepository同梱のdeterministic model stubをSOZAとは別processとして起動します。

KJ Atlas自身の`POST /ai/suggest-card-groups`をactual HTTPで呼び、responseをopaqueな`not_verified` Method outputとして既存Cognitive Method Applicationへ結び付けます。

この実証では次の意味境界を固定しません。

- KJ Atlas response schemaをUniversal Contractへしない。
- grouping候補をRecommendation / Decisionへ自動昇格しない。
- repository / commit / HTTP endpointをMethod Definition identityへしない。
- model stubの出力品質をCognitive Method品質へ読み替えない。

再基線化前のPR #41ではactual KJ Atlas processまで成功しており、最新developへ再基線化した最終branchでも回帰CIを再確認します。

#### 6.4.3 次に進めるE3b-M1b

M1aはKJ Atlas本体の実処理経路を通しますが、modelは決定的stubです。

次のM1bでは実外部modelを利用し、次を確認します。

- modelを交換してもMethod Application / Provenanceの意味境界が保てるか。
- non-deterministic outputをRecommendation / Decisionへ自動昇格しないか。
- external model failureをSOZAのUnknown / Conflictへどこまで結び付けるべきか。
- model provider固有情報をUniversal Contractへ持ち込まずに済むか。

ここで新しい恒久的意味差が見つからなければ、新Requirementは追加しません。

### 6.5 Release / Operational / Adoption Outcome

v0.2.0 Local Reference Product Baselineはactual releaseされ、`release/v0.2.0/RELEASE_EVIDENCE.md`によってRelease EvidenceがSatisfiedとなっています。

ただし、supported Realization / Provider exchange scopeはE3aまでです。release後に成立したE3b-P1やE3b-M1aをv0.2.0へ遡及的に含めません。

```text
Release Evidence Satisfied
  != Operational Evidence
  != Adoption / Outcome Evidence
```

今後は、次releaseのscope拡張とOperational / Adoption評価を別々に設計します。

## 7. 並行作業とIssue番号の扱い

複数branchが同時に進む場合、Issue番号は先に`develop`へ統合された正本を優先します。

今回の系列では、release作業が先に統合されたため次を正本とします。

```text
ISSUE-000061 = external TEI executable injection boundary
ISSUE-000062 = v0.2.0 release publication workflow
ISSUE-000063 = v0.2.0 actual Release Evidence
ISSUE-000064 = E3b-M1a live KJ Atlas Cognitive Method execution
```

古いbranchの番号を維持するためにcurrent Planを巻き戻しません。意味上の成果を最新番号へ移し、古いPRはHistorical Evidenceとして扱います。

## 8. CI failureの扱い

CI failureは、その場で原因を切り分けます。

- 実装不備なら実装を修正する。
- registry / document coverage不備なら計画文書を同期する。
- 外部repositoryのcurrent contract差なら、固定revisionとactual contractを照合する。
- flaky network等なら、Evidence強度を落とさず再現性のある検査とlive pathを分ける。

失敗したrunを隠して成功runだけを残すのではなく、必要な場合はEvidence文書に「何が失敗し、何を補正したか」を残します。

## 9. 自然な日本語の最終工程

開発文書は、内容・構造・Evidence境界を固めた後に、必ず全文を自然な日本語として読み直します。

この工程では、意味や規範強度を変えず、次を確認します。

- 英語設計語の直訳を並べただけの文になっていないか。
- 主語と述語の関係が自然か。
- Evidenceの成立範囲と非主張範囲が一読して分かるか。
- 同じ意味を複数の用語で揺らしていないか。
- 技術的な固有名がProduct-level概念へ紛れ込んでいないか。

自然な日本語化は装飾ではなく、設計上の曖昧さを見つける最終監査として扱います。

## 10. Current next focus

現時点では、次の順で探索を継続します。

1. **E3b-P2 actual TEI execution** — source / binary acquisitionとcredentialをsemantic mappingから分離したまま、actual TEIを実行できる環境を特定する。
2. **E3b-M1b external model-backed Method execution** — M1aの意味境界を保ったまま実外部modelへ進める。
3. **E4 Operational portability** — 実運用でMethod / Providerを交換したときの継続利用を評価する。
4. **次releaseのscope判断** — E3b等をsupported scopeへ含めるに足るEvidenceがあるかを別途評価する。
5. **Operational / Adoption / Outcome Evidence** — releaseの成立とは分離して、利用時の価値と負担を観測する。

この順序は期限ではありません。新しいEvidenceによって前提が崩れた場合は、上位文書へ戻って再基線化します。

## 11. 自然な日本語レビュー

最新`develop/v0.2.0`のProduct Value / Milestones、Realization / Provider Exchange、ISSUE-000045〜000064、v0.2.0 Release Evidence、current runtime Evidenceを照合しました。

release系列を巻き戻さず、M1aだけをcurrent正本へ追加し、次の探索対象をactual TEI、実外部model、Operational portabilityへ分けています。実装上のGitHub、HTTP、FastAPI、SQLite、CLI等をStable Requirementへ昇格させず、Evidenceの高さと非主張範囲が自然に読めるよう全文を再構成しました。

意味、規範強度、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施しました。
