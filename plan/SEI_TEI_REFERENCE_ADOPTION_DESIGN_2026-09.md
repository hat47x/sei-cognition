# SEI → TEI Reference Adoption 設計基線 — Resume / Review Stage 0

更新日: 2026-09-18  
状態: **Pre-design / Reference Adoption Baseline — 実装・Executable Evidence未取得**  
親Issue: **ISSUE-000079**

## 1. この文書の役割

この文書は、SEI Application PlaneをTEI-firstで実装する方針について、最初のReference Adoptionをどこから始めるかを固定します。

最初の対象は、ISSUE-000073で設計済みのResume / Review Projectionです。

ここで確認したいのは、TEIで「同じような画面」を作れるかではありません。

> **SEIが所有する意味をTEIへ移さず、同じ意味変更をApplication Surfaceへ反映するためのowner、layer、手作業同期を減らせるか。**

したがってStage 0では、SEI canonical / evaluation sourceをauthoritative sourceとして維持し、TEI側はread-onlyなReference mapping / Projectionだけを担います。

```text
SEI source meaning
  = authority

TEI Reference mapping / Projection
  = derived / read-only

TEI can render SEI meaning
  != TEI owns SEI meaning
```

この文書だけでTEI Application Plane suitability、Gate C、human usability、Product Valueは成立しません。

## 2. Stage 0で再利用する既存SEI source

最初の固定fixtureには、既存の次を使います。

```text
evaluation/personal-inquiry-decision/
  decision_continuity_counterfactual_001.json
```

fixture id:

```text
e73-decision-continuity-001-provider-pilot
```

このfixtureを選ぶ理由は、Resume / Reviewで失ってはいけない意味差が一つのcaseに揃っているためです。

- initial question
- Observation
- Recommendation
- Unknown
- Recommendationとは異なる人間のDecision
- Decisionが参照したhistorical basis
- Decision時点で残したunresolved
- Decision後に追加されたObservation
- Decision時点には存在しなかったlater information
- historical misattributionを禁止するtemporal stopline

Stage 0では新しいhandoff JSON schemaを作りません。

## 3. 入力とoracleを分ける

### 3.1 TEI Referenceの入力

TEI側へ渡す入力は、fixtureの`scenario`側を基本とします。

```text
scenario.initial_question
scenario.phase_1[]
scenario.interruption_point
scenario.post_decision_evidence[]
```

`phase_1`にはObservation、Recommendation、Unknown、Decisionが含まれ、Decisionは`basis_refs`、`recommendation_refs`、`unresolved_refs`を持っています。

この既存構造からResume Projectionを導くこと自体をPressureします。

### 3.2 期待Projectionのoracle

fixture内の次は入力にはしません。

```text
conditions.C_sei_resume.surface_text
```

これは既存SEI設計で期待しているResume Projectionの比較oracleとして使います。

Stage 0で`C_sei_resume.surface_text`をTEIへ入力すると、SEIが既に作ったProjectionをTEIが再表示するだけになり、Projection leverageや意味導出の重複を検証できません。

したがって、

```text
scenario
  = Reference input

C_sei_resume.surface_text
  = expected Projection oracle
```

と分けます。

### 3.3 reference_stateの役割

`reference_state`はhuman review / semantic audit用の正解境界です。

特に次を使います。

- Decision
- Recommendation
- historical basis ids
- unresolved ids
- post-decision ids
- temporal stopline

TEI Referenceが出したProjectionを評価するときの意味監査に使い、TEI Applicationの入力としては使いません。

## 4. Stage 0で導出するResume Projection

最初のReferenceでは、少なくとも次を導出します。

| Resume concern | SEI fixture source | 期待する意味 |
|---|---|---|
| current question | `scenario.initial_question` | 今回の判断対象 |
| recommendation | `phase_1[role=recommendation]` | AI / 他者提案。Decisionではない |
| decision | `phase_1[role=decision]` | 人間が実際に採った判断 |
| historical basis | Decisionの`basis_refs`を`phase_1`で解決 | Decision当時の根拠だけ |
| unresolved | Decisionの`unresolved_refs`を`phase_1`で解決 | Decision時点に残ったUnknown |
| changes since decision | `post_decision_evidence` | Decision後に増えた情報 |
| audit detail | source ids / role / references | Projectionからsourceへ降りる入口 |

重要なのは、表示文言そのものの一致ではなく、参照関係と時間境界が維持されることです。

## 5. Temporal integrityを最優先の停止線にする

fixture 001には、Decision後に次が追加されます。

- Provider Bの429観測
- Provider Aのmaintenance公表

どちらもDecision記録後の情報です。

したがって、

```text
post-decision evidence
  -> changes since decision

post-decision evidence
  != historical basis
```

を必ず守ります。

TEI Referenceがorientationを短くできても、later informationをhistorical basisへ混ぜた場合は失敗です。

```text
faster projection
  + temporal misattribution
  = failure
```

## 6. TEI current Application Patternとの対応

TEI current mainのApplication Pattern v1には、少なくとも次があります。

- `browse`
- `record`
- `reference`
- `command`
- `header-detail`

これらはTarget固有UIではなく、ApplicationがSemantic上の意味をどう利用するかを表す層です。

ただし、Stage 0のResume / Reviewを既存Patternへ無理に割り当てません。

### 6.1 `record`へ押し込まない

Resume Briefは「一つのData recordを表示する」だけではありません。

一つのProjection内で、

- current question
- Recommendation
- Decision
- historical basis
- unresolved
- later changes

を異なる意味役割として束ねます。

したがって、単に`record`へ写すだけでは、Resume Projectionの意味差を説明できません。

### 6.2 `browse`へ押し込まない

Resume Briefは時系列一覧や検索結果でもありません。

特にhistorical basisとpost-decision changeは、単純なchronological listより強い時間・参照境界を持ちます。

### 6.3 新しいPattern Kindを先取りしない

Stage 0で`resume`、`review`、`decision-memory`等の新Pattern Kindは追加しません。

まず次を比較します。

1. 既存Application / Projection機構の組合せで十分か。
2. Reference-local adapter / derived projectionで十分か。
3. SUIでも候補になっているReview / Diff Visualization等のreusable extensionが自然か。
4. 複数Applicationで同じ不足が再現した場合だけTEI Product gap候補にする。

```text
SEI needs Resume Projection
  != TEI needs Resume Pattern Kind
```

## 7. Stage 0の実装境界

最初の実装は、TEI Product Coreを変更しない隔離されたReference tool / testとします。

論理構成は次です。

```text
existing SEI fixture
  decision_continuity_counterfactual_001.json
        |
        | read-only
        v
SEI-source adapter for TEI Reference
        |
        | resolve roles / refs / temporal partition
        v
Reference Projection model
        |
        +--> TEI current Application / Projection boundaryへmapping
        |
        v
derived Resume / Review output
        |
        +--> compare with C_sei_resume.surface_text
        +--> audit with reference_state
```

ここでいう`Reference Projection model`は、恒久schemaを意味しません。Reference tool内部の一時的な型・構造として実装できます。

外部交換用の第三schemaを作らず、sourceは既存SEI fixture、意味監査は既存oracle / reference_stateを使います。

## 8. Source freeze

Reference比較では、入力fixtureが途中で変わるとchange amplificationや意味比較が不明確になります。

そのため実装runでは、少なくとも次を固定します。

- SEI repository revision
- fixture path
- fixture bytes SHA-256
- TEI repository revision
- Reference tool revision

実装revisionと意味source revisionを同一と仮定しません。

```text
SEI source revision
  != TEI Reference implementation revision
```

## 9. Challenge Aの最小受入れ条件

read-only Resume / Review Referenceは、少なくとも次を満たす必要があります。

1. current questionを復元できる。
2. RecommendationとDecisionを別にProjectionできる。
3. Decisionの`basis_refs`だけをhistorical basisへ解決できる。
4. Decisionの`unresolved_refs`を保持できる。
5. post-decision Evidenceをchanges since decisionへ分離できる。
6. post-decision Evidenceをhistorical basisへ遡及混入しない。
7. source idへ降りられる。
8. missing refやunknown roleを黙って捨てずdiagnostic / Unknownとして観測できる。
9. SEI source fixtureを変更しない。
10. TEI Core / new Pattern Kind / Universal Contract fieldを追加せず開始できる。

## 10. Negative cases

Reference implementationでは少なくとも次をPressureします。

### N1 — RecommendationをDecisionへ昇格しない

```text
rec-full-switch
  != dec-pilot
```

AIは全面切替を提案していますが、人間は10% pilotを選んでいます。

### N2 — unresolvedを消さない

次はDecision後も未解決として残ります。

- Provider B本番負荷時rate-limit
- rollback所要時間

Resumeを短くするために省略し、解決済みに見せないことを確認します。

### N3 — later informationをhistorical basisへ混ぜない

429観測とmaintenance公表はDecision後です。

### N4 — unknown role / missing referenceをfalseへしない

fixtureのroleやreference解決に失敗した場合、単に項目を落として完全なResumeに見せません。

## 11. change amplification比較

Stage 0では、同一意味変更をnative SEI projectionとTEI Referenceで比較できるようにします。

最初のrepresentative changeは次です。

### Change 1 — post-decision Observationを一件追加する

期待:

- changes since decisionだけに現れる。
- historical basisは変わらない。
- Decisionは変わらない。
- unresolvedは自動解決されない。

比較するもの:

- 更新するsource owner数
- hand-written mapping数
- Projection code / config変更数
- test変更数
- manual synchronization
- duplicate semantic expression
- derived artifactの再生成可能性

### Change 2 — Resume表示順を変える

たとえば`unresolved`をDecision直下へ移す。

これはProjection concernです。

期待:

- SEI canonical sourceを変えない。
- historical refsを変えない。
- TEI側Presentation / Projection変更だけで済む可能性をPressureする。

### Change 3 — audit detailを追加する

source id / provenanceへの降下を一段追加する。

期待:

- light viewへraw provenanceを常時露出しない。
- canonical meaningへ新fieldを増やさない。
- Progressive ExplicitnessをSurface concernとして保つ。

## 12. SUI Reference Adoptionとの比較

SUIではCanvas / hierarchy / merge review等を通じてTEIのApplication基盤をPressureしています。

SEI Stage 0は別の圧力を与えます。

```text
SUI
  spatial / graph interaction
  hierarchy
  proposal / merge review

SEI
  temporal integrity
  historical basis
  Recommendation / Decision separation
  unresolved preservation
  Evidence level / governance
```

特にReview / Diff Visualizationが両者で有用なら、第二Applicationでの再利用性Evidenceになります。

ただし、

```text
useful in SUI + useful in SEI
  != TEI Core concept
```

です。

Target component、Plugin、Adapter等で十分ならCoreへ上げません。

## 13. Evidence高さ

Stage 0のEvidenceは次を分けます。

```text
mapping document
  = Design Evidence

Reference tool source
  = Implementation source

Reference tool test PASS
  = Scoped Executable Evidence for Reference mapping

native vs TEI change comparison
  = implementation-strategy Evidence

human usability review
  = separate Product Outcome Evidence
```

Reference toolがPASSしてもISSUE-000073のDecision Continuity valueは証明しません。

またTEI Provider compatibility（ISSUE-000072 / 000074）とも別です。

## 14. 実装開始条件

Reference codeへ進む条件は次です。

- existing fixtureをread-only sourceとして使える。
- source authorityをSEIに置ける。
-新しいexchange schemaを作らず始められる。
- TEI Product Coreを変更せず隔離できる。
- Gate B / Cをproduction-readyとして先取りしない。
- native SEI projectionとの比較点を固定できる。
- Reference codeは判断後に削除可能な形で置ける。

この条件を満たすため、最初の実装はTEI repository側のReference tool / testとして置くのが自然です。ただし、TEI repositoryのbranch / Gate運用はTEI側の開発規則に従い、本SEI Issueから勝手にTEI mainへproduction contractを追加しません。

## 15. 次の具体作業

次の作業単位は次です。

1. TEI側で、既存SEI fixture 001をread-onlyに読むReference toolの置き場所を選ぶ。
2. fixture bytesとSEI source revisionを固定する。
3. `scenario`からResume concernを決定論的に導出する。
4. `C_sei_resume.surface_text`と`reference_state`をoracleとして意味差を検査する。
5. N1〜N4 negative casesをfixture-local testにする。
6. Change 1〜3のうち少なくとも一つをnative / TEI Referenceで比較する。
7. 結果をExisting / reusable extension / Native SEI / TEI Product gap candidateへ分類する。

## 16. Natural Japanese review

Stage 0では、SEIのResume BriefをTEIへ「移す」ことを先に成功条件にしていません。

既存SEI fixtureの`scenario`をsourceとし、既に用意されている`C_sei_resume.surface_text`をoracleへ退かせることで、SEI側で生成済みのProjectionをTEIへ再表示するだけの自己循環を避けています。

また、TEI current Application Pattern v1へResumeを無理に`record`や`browse`として押し込まず、新しい`resume` Pattern Kindも先取りしません。最初に既存境界とReference-local mappingでどこまで解けるかを確認し、SUIを含む複数Applicationで同じ不足が再現したときだけreusable extensionやProduct gapを検討します。

最も重要な停止線は、Resumeの短さや見栄えより、historical basis、Recommendation / Decision、unresolved、later changeの意味差を壊さないことです。TEI-firstはSEI semantic authorityをTEIへ移す方針ではなく、Application Planeの実装負荷を下げられるかを反証可能に試す実装戦略として扱います。
