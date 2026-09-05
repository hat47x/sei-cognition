# SOZA 上流プロダクト開発計画

更新日: 2026-09-05  
状態: **Current Upstream Planning Baseline — v0.2.0 Release Evidence / E3b fixed-artifact Evidence / historical reconstruction / fixed-scope Ollama runtime exchange / method-quality evaluation boundary / PMS-06 current state reflected**

## 1. この文書の役割

この文書は、SOZAのProduct Value、Milestone、Open Question、Requirement、ADR、Architecture、Implementation、Evidenceを、どの順序で具体化するかを定めます。

目的は、未定の領域を実装都合で早く固定することではありません。上位価値へ戻りながら、議論、調査、実証、人間レビューを通して必要な意味差を見つけ、必要性を確認できたものだけをRequirementやContractへ正本化します。

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
Discussion / Research / Experiment / Human Review
  ↓
Evidence
  ↓
Candidate Requirement
  ↓
Requirement audit
  ↓
Stable Requirement / existing Requirement integration / No Change
  ↓
ADR / Architecture / Contract
  ↓
Implementation / Fixture / Test / Tool
  ↓
必要なら上位へ戻って再基線化
```

コードやcurrent schemaを上位概念の根拠として逆輸入しません。一方、実装や実験から得た反証Evidenceは、Product仮説やRequirementを見直す正当な入力とします。

## 3. 現在の優先順位

### Priority A — Product ValueとMilestoneの正本維持

最優先で、次の文書間に矛盾がない状態を保ちます。

- `product/value/SOZA_PRODUCT_VALUE.md`
- `product/value/SOZA_VALUE_PROPOSITION.md`
- `product/value/SOZA_VALUE_MODEL.md`
- `product/value/SOZA_VALUE_ACCEPTANCE.md`
- `product/value/SOZA_VALUE_TRACEABILITY.md`
- `product/definition/SOZA_PRODUCT_SHAPE.md`
- `product/definition/SOZA_REALIZATION_PROVIDER_EXCHANGE.md`
- `product/vision/SOZA_PRODUCT_VISION.md`
- `product/principles/SOZA_PRODUCT_PRINCIPLES.md`
- `product/roadmap/SOZA_PRODUCT_MILESTONES.md`
- `product/roadmap/PMS06_CURRENT_STATE_2026-09-05.md`

下位作業がこの層と矛盾した場合、実装を先に温存しません。Product Value側の誤りを示すEvidenceがあるなら上位を再基線化し、そうでなければ下位設計を修正します。

### Priority B — 未定領域の探索

Product Interaction、Local Single-Node Packaging、Product Access責務分離は、Design baselineと限定されたExecutable Evidenceまで進んでいます。v0.2.0 Local Reference Product Baselineについてはactual Release Evidenceも成立しています。

Real Method / Provider Portabilityでは、E2、E3a、E3b-P1、E3b-P2 revision A fixed-artifact、E3b-M1a、E3b-M1b、historical reconstruction H1 / H2、actual model artifact交換、fixed-model Ollama runtime version交換まで段階的に実証しました。

ISSUE-000067では、実現機構が異なるM1a / M1bを別のlogical Method Realizationとして保持し、同一Realization内のhistorical revisionを固定する必要がある場合はExact Bindingを利用できることを確認しました。

ISSUE-000068では、KJ Atlas source、Method surface、入力、Ollama `0.32.14`を固定したまま、`qwen2.5:0.5b`と`qwen2.5:1.5b`のactual model artifactを交換しました。両方でactual inferenceを確認し、後続Application追加後も先行ApplicationのRealization、Provenance、outputが変わらないことを実証しています。

一方、生成内容と言語は同一ではありませんでした。構造上受理できるresponseでも、label / rationaleの言語や意味上の品質が変わり得ます。このため、execution成立と成果品質を同じEvidenceへまとめないことが重要になりました。

ISSUE-000071では、この問題に対する評価境界を確立しました。structure checker、review bundle manifest、non-golden case catalog、historical actual sample、structured human review templateを整備し、成功済みactual M1b履歴からreview-ready bundleを再構成できることまで確認しています。

ただし、ISSUE-000071のResolvedは「KJ法として成果品質がよい」と判定したことを意味しません。actual human review、複数caseでの比較、実利用時の価値評価は後続Evidenceです。

ISSUE-000069では、GitHub-hosted runnerの割当問題とrepository内の実証責務を分けました。その後PR #70でGitHub Actions workflow群をcurrent baselineから外したため、現在はActionsの成否をProduct / Plan / Evidenceの意味上の成立条件にしていません。

PMS-06ではversion exchangeを二つの独立した軸として扱いますが、現在のEvidence状態は同じではありません。

- **Ollama runtime version交換 — ISSUE-000070**: KJ Atlas source、Method input、model artifact、promptを固定し、Ollama `0.32.13` / `0.32.14`だけをactualに交換しました。execution `local-20260904T193531Z-7855` でA/B actual bytes / binary version、fixed model identity、same prompt、actual inference、same logical / different Exact Binding、historical Application不変性、portable reconstructionを確認し、canonical Evidence + Provenance verificationは`ready-to-review` / `107 ok / 0 blocked`です。current Requirement / Contractも再照合し、**Resolved**としました。
- **TEI executable version交換 — ISSUE-000072**: historical revision Aを保持したまま、exact revision B executable source + exact revision A fixed reference inputで`deployment-provider-plan`とcurrent SOZA Adapter compatibilityを検証します。source / fixed-input identity verifier、E2 / E3 runner、E2 / E3別Go toolchain、canonical combined runner、stage-aware failure Evidence、actual前Requirement / Scenario pre-auditまで整っていますが、revision B actualは**Not Yet Verified**です。

この二つは交換軸が異なります。ISSUE-000070のPASSをISSUE-000072のEvidenceへ流用しません。

```text
ISSUE-000070 Resolved
  = fixed-scope runtime-version-exchange Scoped Executable Evidence available
  != arbitrary runtime version portability
  != outcome quality satisfied
  != E4 Operational portability

ISSUE-000072 repository-side ready
  != revision B actual TEI / Adapter compatibility PASS
```

現在の主要な未定領域は次です。

- **TEI executable version交換**: ISSUE-000072。exact revision B executable + exact revision A fixed inputでactual Provider Planを得て、current SOZA AdapterのProvider-neutral Observation境界へ戻せるか。
- **actual human review**: ISSUE-000071で確立した評価基盤を使い、actual outputを人間がどのように評価するか。
- **broader portability**: ISSUE-000070で成立した固定scope、二つのQwen artifact、固定TEI revisionを越え、別model family、別Provider、別Realization、arbitrary runtime / Provider versionでも同じ意味境界を保てるか。
- **private artifact acquisition / credential lifecycle**: version compatibilityとは分け、artifact取得・配布・更新をどのdeployment / acquisition policyへ閉じ込めるか。
- **failure behavior**: network degradation、rate limit、credential失効、model acquisition failure、artifact acquisition failure等をどのEvidence段階で扱うか。
- **formal integration protocol**: 標準化する必要が本当にあるか。必要ならどこまでをUniversal semanticsへ含めるか。
- **E4 Operational portability**: 実環境でRealization / Provider / model / runtime交換後も判断記憶を継続利用できるか。
- **Adoption / Outcome**: 実際の利用者や組織にとって、SOZAがどの価値を届けたかをどう測るか。

actual v0.2.0 Releaseそのものは未定領域ではありません。既に成立したRelease Evidenceを維持し、post-releaseのExecutable Evidenceを公開済みv0.2.0のsupported scopeへ遡及的に追加しません。

### Priority C — RequirementとAcceptanceの精緻化

議論・実証から必要性が確認できたものだけをRequirementへ反映します。

既存REQ / SCNで表現できる場合は新しいIDを増やさず、横断AcceptanceやEvidenceの不足として扱います。

ISSUE-000067 / 000068 / 000070 / 000071では、current RequirementとContract境界で必要な意味を表現できたため、新しいStable RequirementやUniversal Contract fieldを追加していません。

ISSUE-000070ではactual runtime交換後にREQ-0001 / 0004 / 0021、SCN-0005 / 0015、Cognitive Method / Semantic Reference / Semantic Interchangeへ再照合し、既存境界で十分と判断しました。将来、arbitrary runtime versionや別runtime implementationへ一般化した際に独立したProduct failureが確認された場合は、そのEvidenceからCandidate Requirementとして上流へ戻します。

ISSUE-000072についても、actual revision Bの結果を見る前に`runtime/TEI_VERSION_EXCHANGE_REQUIREMENT_PREAUDIT_2026-09-05.md`でREQ-0001 / 0007 / 0021、SCN-0014 / 0018の判定基準を固定しました。Provider-neutral Capability Observationの隣接境界としてREQ-0022も監査対象候補です。

現時点ではexisting Requirement coverageで意味境界を表せると見ています。actual BがNot Yet Verifiedであるため、新しいStable RequirementやUniversal Contract fieldを追加する根拠にはしません。

```text
pre-audit completed
  != independent Product failure observed
  != new Stable Requirement required
```

### Priority D — Architecture / Contract / Implementation

上位RequirementとAcceptanceが十分に定まった範囲から、Architecture、Contract、runtime、Provider Adapter、fixture、test、toolへ降ろします。

実装可能であることと、Requirementとして必要であることを混同しません。

## 4. 未定領域を要件化するまでの標準フロー

### Step 1 — Open Questionを明文化する

最初に「何を決めるか」ではなく、何がまだ分かっていないかを明確にします。

例:

- external Cognitive Methodをactual modelで動かした後、実行成立と生成品質をどの評価境界で分けるか。
- fixed-scope runtime version交換で成立したhistorical reconstructionを、別runtime version / implementationへ一般化するには何を追加で観測する必要があるか。
- TEI revision B executableをrevision A fixed inputで動かしたとき、failureが起きた場合に不足しているのはDurable Semantic Coreの意味か、Provider / Adapter-local compatibilityか、execution environmentか。
- external executableを取得するためのcredential方式を、SOZAのsemantic identityからどこまで分離できるか。

この段階では選択肢をRequirementへ固定しません。

### Step 2 — 議論・資料調査を行う

設計上の論点、利用場面、失敗例、既存技術、代替案を広く検討します。

チャットは探索と統合の作業空間として利用できますが、チャット上の結論そのものをcurrent正本にはしません。必要な内容はIssue、Product文書、Requirement、ADR等へ戻します。

外部Projectを候補にする場合は、名称や想像上のAPIだけで判断せず、実際のrepository、CLI、artifact、service surface、versioning、credential条件まで確認します。

### Step 3 — 実証実験を設計する

議論だけで判断しにくい場合は、小さなprototype、fixture、comparison harness、human review、provider接続試験等を作ります。

実験では、実装候補を完成させることより、次の問いに答えることを優先します。

- 意味境界が本当に必要か。
- 既存Requirementで十分か。
- ProviderやRealizationを交換しても意味が残るか。
- Method outputとRecommendation / Decisionを分離できるか。
- 失敗時に何が失われるか。
- artifact取得、credential、process invocation、semantic mappingを分けられるか。
- live processが動いたことと、modelやMethodの品質を分けて評価できるか。
- model / runtimeを交換したとき、過去Applicationを再構成するためのProvenanceが不足しないか。
- version交換の比較では、build / executable sourceとfixed reference inputを別々に固定・追跡できるか。
- execution toolchain要件をactual process開始前に観測できるか。
- machine-readable stageがない内部原因をstderrや自然言語logから推定してEvidenceを過大化していないか。

### Step 4 — Evidenceの高さを記録する

少なくとも次を区別します。

```text
Design Evidence
  != Executable Evidence
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

Release Candidateの検査記録は、5段階Evidenceへ別の普遍段階を増やすものではありません。特定candidateについて必要なExecutable Evidenceをまとめて確認するgateとして扱います。

synthetic fixture、helper process、deterministic model stub、actual inference、actual model artifact交換、fixed-scope runtime version交換、version-exchange execution path、構造検査のPASSを、それぞれが確認していないarbitrary version互換性、生成品質、実運用品質、利用者価値へ自動昇格させません。

### Step 5 — Candidate Requirementを作る

実証結果から「製品として必ず守る必要がある意味差」が見えた場合だけCandidate Requirementを作ります。

この時点ではStable REQ IDを付けなくても構いません。

### Step 6 — Requirement化の監査を行う

Stable Requirementへ昇格する前に、少なくとも次を確認します。

1. Product Valueのどの価値を守るために必要か。
2. 具体的な利用Scenarioまたは失敗例で必要性を説明できるか。
3. 既存REQ / SCNの組み合わせで既に表現できないか。
4. 現在のUI、AI、DB、workflow、Provider revision、toolchain等の弱点を補うだけの一時的要求ではないか。
5. Provider / Profile / Projection / Adapter / deployment policyへ置く方が自然ではないか。
6. 評価時点から10〜50倍程度先を見ても意味上の必要性が残るか。
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

たとえばPMS-06でactual TEIやactual model-backed Methodとの接続を観測しても、GitHub token、private clone、CLI配布方式、Go version、Ollama、特定model tag、HTTP / gRPC / MCP等を直ちにStable Requirementへしません。

```text
Milestone outcome
  != implementation choice
  != acquisition mechanism
  != execution toolchain
  != Universal Requirement field list
```

## 6. 現在の主要探索系列

### 6.1 Product Interaction

ISSUE-000045 / 000053で、human-oriented Surfaceとmachine-oriented Surfaceが同じcanonical sourceへ戻る境界について、Design baselineと限定されたExecutable Evidenceがあります。

productionで最初にsupportするWeb / desktop / CLI / API / MCP等は引き続きOpen Questionですが、現時点の主探索系列ではありません。実利用やPackaging要件から必要性が現れた時点で再開します。

### 6.2 Packaging / Deployment

ISSUE-000046 / 000054 / 000055では、Local Single-Node Package、durable data root、save / reload、deterministic reference artifactについて限定されたExecutable Evidenceを得ました。

v0.2.0 Local Reference Product Baselineはactual release済みです。release後の実証を理由に、既存releaseのsupported scopeを遡及的に広げません。

### 6.3 Product Access / Collaboration

ISSUE-000047 / 000056では、login identity、Product access permission、semantic Responsibility / Authorityを分離したProduct baselineとreference probeがあります。

identity providerやpermission vocabularyをUniversal semanticsへ固定しません。

### 6.4 Real Method / Provider Portability

#### 6.4.1 Provider / TEI execution

E3a / E3b-P1では、synthetic・version固定artifact・public live serviceを段階的に接続しました。

E3b-P2ではTEI revision A `48a7ca1fe8a9538e9e9be3e1ee08ef14804c8f67`からactual `cmd/tei`をbuild・実行し、そのartifactをSOZA Adapterから別processとして呼び出し、Capability Observationへ戻す範囲までScoped Executable Evidenceがあります。

最初のcredential-aware probeでprivate TEI取得がskipされた事実は、そのまま履歴として保持しています。その後、別経路でrevision Aのactual executable実行を確認したからといって、credential運用自体が解決したとは扱いません。

ISSUE-000072では、TEI executable version交換の一変数比較を成立させるため、build / executable sourceをexact revision B、fixed reference inputをexact revision Aへ分離しました。

- revision A: `48a7ca1fe8a9538e9e9be3e1ee08ef14804c8f67`
- revision B: `1a7028d444fcae60a1c4f2f2d247456f4c7c35be`
- B build source: exact revision B
- fixed input: exact revision A

repository側ではrevision A historical Evidence再検証、revision B source identity、revision A fixed-input identity、E2 / E3 runner、E2 / E3別Go toolchain、canonical combined runner、stage-aware failure Evidenceまで整っています。

current SOZA E3 live testでは`runtime/go/go.mod`のGo directiveとactual E3 `go version`をlive test開始前に比較し、要件未満のtoolchainを`soza_go_toolchain` stageとして停止できるようにしています。このprecheckのPASSもAdapter compatibility PASSではありません。

```text
E3 Go requirement precheck PASS
  != current SOZA Adapter live compatibility PASS
```

revision B actual CLI / `deployment-provider-plan` / current SOZA Adapter compatibilityは**Not Yet Verified**です。

#### 6.4.2 actual model-backed Method

ISSUE-000064では、固定KJ Atlas revisionとdeterministic model stubを別processとして実行し、actual Method surfaceをSOZA Cognitive Method Applicationへ戻しました。

ISSUE-000066では同じMethod surfaceのmodel processをOllama `0.32.14`上の`qwen2.5:0.5b`へ交換し、actual inferenceを確認しました。

ISSUE-000068では`qwen2.5:1.5b`を加え、同じKJ Atlas source / Method input / runtimeの下でmodel artifactだけを交換しました。後続Application追加後も先行Applicationの履歴を保持できています。

```text
actual inference succeeded
  + response shape accepted
  + historical Application preserved
  != model output quality satisfied
  != language suitability satisfied
  != KJ-method outcome quality satisfied
```

#### 6.4.3 成果品質の評価境界

ISSUE-000071はResolvedです。

ここで確立したのは成果品質そのものではなく、成果品質を評価するための境界です。

```text
execution conformance
  != structural safety
  != human outcome review
  != Product Value / Adoption outcome
```

structure checkerはcard identity、held / excluded、重複、digest等だけを確認し、意味的品質を採点しません。non-golden case catalogは期待groupや期待表札を持たず、historical actual sampleにもwinnerやpreferred outputを付けません。

PR #72ではRun `33596839607` / Job `100141890796`のactual履歴からreview-ready bundleを再構成しました。元workflow artifactは存在しなかったため、再構成物であることをProvenanceへ明示しています。

PR #73では2つのactual resultの差をAI補助観測として保存しましたが、`humanReviewCompleted = false`、`qualityJudgement = not_evaluated`を維持しています。

次の段階は、Human Review Templateを使ったactual human reviewと、より難しいcaseでの比較です。

#### 6.4.4 Ollama runtime version交換とhistorical reconstruction

ISSUE-000070は**Resolved**です。

固定条件は、KJ Atlas source、Method input、`qwen2.5:0.5b`のactual model artifact、promptです。交換したのはOllama runtime versionだけです。

- revision A: `0.32.13`
- revision B: `0.32.14`

execution `local-20260904T193531Z-7855`では、固定runtime archive actual bytes / SHA-256、actual binary version、A/B `/api/tags`のfixed model full digest、同一prompt digest、A/B actual inferenceを確認しました。

さらに、same logical Realization / different Exact Binding、Application AのExact Reference / Provenance / output不変性、portable reconstruction、unknown revision negative controlを確認しています。canonical Evidence + Provenance verificationは`ready-to-review`、`107 ok / 0 blocked`です。

actual run時とcurrent developについて、ISSUE-000070 Resolution Criteria、core / Provenance verifier、fixed artifact manifest、Product Requirements、Acceptance Scenarios、relevant Contract baselineが同一Git objectであることも再監査しました。REQ-0001 / 0004 / 0021、SCN-0005 / 0015へ戻っても既存Requirement / Contractで表現できるため、新しいStable Requirement / Universal Contract fieldは追加していません。

```text
ISSUE-000070 Resolved
  = fixed-scope Ollama runtime version exchangeのScoped Executable Evidence available
  != arbitrary runtime version compatibility
  != other runtime implementation portability
  != model output quality satisfied
  != KJ-method outcome quality satisfied
  != E4 Operational portability
```

GitHub Actionsをcurrent baselineへ戻すことやHAT47Xで同じrunを再実行することをResolution条件にはしません。独立reproductionは再現性や一般化の追加Evidenceとして扱います。

#### 6.4.5 TEI executable version交換とRequirement再照合

ISSUE-000072はOpenです。

この探索ではTEI revision BそのものをCapability identityへ昇格させず、revision A historical Evidenceを保持したままProvider implementation revisionを交換できるかを見ます。

```text
build / executable source = exact revision B
fixed reference input     = exact revision A
```

actual E2 / E3を実行するcanonical entrypointは`runtime/integration/run_tei_version_exchange_evidence.py`です。E2 historical TEI build用GoとE3 current SOZA live-test用Goを別executableとして明示し、current `go.mod`の要件もactual E3 process前に確認します。

失敗時はrepository-local machine-readable stageまでをEvidenceとし、TEI内部のworkspace load / validation / durable run / plugin lockや、SOZA内部のstrict decode / mapping / validatorをstderr等の自然言語から推定しません。

actual結果を見る前にRequirement / Scenario pre-auditを固定しています。一次再照合対象はREQ-0001 / 0007 / 0021、SCN-0014 / 0018で、Provider-neutral Observationの隣接境界としてREQ-0022も確認対象候補です。

```text
exact-B + exact-A fixed-input path ready
  != revision B build PASS
  != Provider Plan execution PASS
  != current Adapter compatibility PASS
  != SCN-0014 Satisfied
  != new Stable Requirement required
```

actual Bで独立したProduct failureが確認されるまでは、build failure、toolchain failure、Provider Plan process failure、Adapter-local DTO incompatibilityだけを理由にStable RequirementやUniversal Contractを増やしません。

### 6.5 Release / Operational / Adoption Outcome

v0.2.0 Local Reference Product Baselineはactual release済みで、Release Evidenceが成立しています。

```text
v0.2.0 Release Evidence Satisfied
  != Operational Evidence
  != Adoption / Outcome Evidence
```

post-releaseのE3b-P1、E3b-P2 revision A fixed-artifact、E3b-M1a、E3b-M1b、H1 / H2、actual二モデル交換、fixed-scope Ollama runtime version交換、成果品質評価基盤、ISSUE-000072 version-exchange repository-side readinessは、新しいDesign / Executable materialとして扱います。これらを公開済みv0.2.0のsupported scopeへ遡及的に含めません。

今後はE4として、実環境でRealization / Provider / model / runtime等を交換した後も判断記憶を継続利用できるかを観測します。同時に、利用者にとっての価値をOperational / Adoption / Outcome Evidenceとして別に測ります。

## 7. 検証手段の扱い

current `develop/v0.2.0`では、PR #70によりGitHub Actions workflow群を常設していません。

これは検証を不要とする方針ではありません。

```text
what must be verified
  != where it is executed
```

repository同梱test、checker、fixture、保存Evidence、手動実行、外部runner、将来のCI等から、その検証に適した手段を使います。

GitHub Actions等を再導入する場合はISSUE-000069のReopen条件へ戻り、scenario-local責務、共有依存、runner availability、push / merge / release / Evidence gateを再監査します。

検証手段が利用不能な場合も、未実行をPASSへ読み替えません。一方、外部基盤の利用不能をrepository testのFAILやProduct Evidence failureとしても扱いません。

## 8. 作業の停止線

次の場合は、実装へ急いで進まず上流へ戻ります。

- 何を価値として守るか説明できない。
- RequirementがProduct Valueとつながらない。
- 既存REQが同じ意味を既に包含している可能性が高い。
- UIやProvider / Method固有schemaをUniversal Coreへ持ち込もうとしている。
- repository取得方式やcredential方式をsemantic identityへ混ぜようとしている。
- model名、runtime名、repository名、model digest、prompt digest、TEI revision、Go toolchain等の実装・実験固有情報を、必要性が確認されていないUniversal fieldへ昇格させようとしている。
- actual inferenceのPASSだけでmodel品質やKJ法としての成果品質を主張しようとしている。
- structure checkのPASSだけでhuman outcome qualityをSatisfiedとしようとしている。
- AI補助観測をhuman reviewとして扱おうとしている。
- 二モデル交換やISSUE-000070の固定scope PASSだけでarbitrary model / runtime portability、E4 Operational portabilityまで成立したと扱おうとしている。
- ISSUE-000070のPASSをISSUE-000072のProvider compatibility Evidenceとして流用しようとしている。
- repository-side version-exchange pathやtoolchain precheckのPASSだけでISSUE-000072 actual compatibilityを主張しようとしている。
- 自然言語logの語句だけからformal contractのない内部substageやroot causeをEvidenceとして断定しようとしている。
- ISSUE-000072の限定TEI executable version exchange PASSだけでSCN-0014のExecution Provider exchange全体をSatisfiedへ上げようとしている。
- build / toolchain / Adapter-local failureだけで新しいStable RequirementやUniversal fieldを追加しようとしている。
- 未実行の検証を、実行基盤がなくなったことを理由にPASSへ読み替えようとしている。
- post-releaseのExecutable Evidenceを既存releaseのsupported scopeへ遡及的に追加しようとしている。
- 未定事項を「実装しやすいから」という理由だけで確定しようとしている。

## 9. 計画文書の更新単位

上流作業では、必要に応じて次を同じ変更単位で更新します。

- Product文書
- Product Milestone
- Issue / ADR
- Requirement / Acceptance Scenario
- Evidence文書
- `plan/registry.yaml`
- `plan/document_review_registry.yaml`

文書追加・更新後は、自然な日本語となることを最重要視して全文を再ドラフトします。その後、意味、規範強度、留保、Evidence強度が変わっていないかを最終監査します。

## 10. Natural Japanese review

2026-09-05時点のProduct Value、Product Shape、Product Milestone、PMS-06 current snapshot、Realization / Provider Exchange、Value Traceability、v0.2.0 Release Evidence、E3b-P2 revision A fixed-artifact、E3b-M1a、E3b-M1b、historical reconstruction H1 / H2、actual二モデル交換、fixed-scope Ollama runtime version交換、ISSUE-000069〜000072へ戻り、上流探索の現在地を再構成しました。

以前の文書では、GitHub Actions上の実証と今後の探索が一部で強く結び付いていました。PR #70でActionsをcurrent baselineから外したため、検証内容と実行場所を分離しました。検証を弱めるのではなく、利用可能なtest、checker、保存Evidence、外部実行で実際に確認できた高さだけを記録する方針です。

ISSUE-000071については「品質評価が完了した」と誤読されないよう、評価境界の確立とactual human reviewを分けています。

ISSUE-000070については、historical actual A/B Evidenceの回収だけでなく、canonical Evidence + Provenance verification、historical Application不変性、portable reconstruction、actual run時とcurrent developのResolution Criteria / verifier / manifest / Requirement / Scenario / relevant Contractのobject equivalenceまで再監査しました。その固定scopeでResolvedとし、arbitrary runtime portability、成果品質、E4へは拡張していません。

ISSUE-000072については、revision A historical fixed-artifact Evidenceとrevision B actual compatibilityを分離しました。exact-B executable + exact-A fixed inputの比較軸、E2 / E3別toolchain、current Go directiveのprecheck、stage-aware failure Evidence、actual前Requirement / Scenario pre-auditまでを上流計画へ同期していますが、revision B actual CLI / Provider Plan / current SOZA Adapter compatibilityはNot Yet Verifiedです。

既存REQ / SCNで現在必要な意味を表現できているため、新しいStable RequirementやUniversal Contract fieldを追加していません。現在の主要Open version-exchange探索はISSUE-000072であり、ISSUE-000070は独立reproductionやbroader portabilityへ進む場合の既存Evidence基線として扱います。

意味、規範強度、未決事項、Evidence強度を混同せず、自然な日本語として一続きに読めることを最重要視して最終監査しました。
