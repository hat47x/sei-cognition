# SEI Product Journey Requirement Composition

更新日: 2026-09-01  
状態: **Current Product Integration Requirement Analysis**

## 1. この文書の役割

この文書は、`product/definition/SEI_PRODUCT_SHAPE.md`で定めたMinimum Usable Product Shapeを、current REQ-0001〜REQ-0022とSCN-0001〜SCN-0017へ照合し、**新しいRequirementが本当に必要か、それとも既存Requirementを横断するAcceptanceが不足しているのか**を整理するための分析文書です。

新しいRequirementやAcceptance Scenarioの意味上の正本を、この文書だけで追加しません。

```text
Product Shape
  → existing REQ / SCN composition analysis
  → ISSUE-000048
  → necessary stable REQ / SCN only
```

## 2. 結論

現時点では、Minimum Usable Product Shapeの主要な意味要求は、既存REQ-0001〜REQ-0022で概ね表現できます。

したがって、**製品外形を明確にするためだけに新しいREQを追加する必要はない**と判断します。

一方、既存SCNは個別の意味境界をよく検査していますが、次を一続きに横断するAcceptanceが不足しています。

```text
Inquiry
  → Observation / Evidence / Unknown / Conflict
  → Cognitive Method Application
  → Recommendation
  → Decision / Responsibility
  → external Capability / Execution
  → resulting Observation
  → historical review / reopen
```

不足しているのは新しいUniversal ontologyではなく、**既存Requirementが一つのProduct Journeyで同時に成立することを確認するend-to-end Acceptance Scenario**です。

この不足はISSUE-000048でstable Scenarioへ落とします。

## 3. Product Journeyと既存Requirementの対応

### 3.1 Inquiryを始め、後から再開する

主に次で表現できます。

- REQ-0001 — 技術や実装が変わっても耐久的な意味を保つ。
- REQ-0005 — Decisionをhistorical contextとともに再構成する。
- REQ-0014 — unresolved residualとreopen informationを保持する。

主な既存Scenario:

- SCN-0001 — 根拠が割れている判断
- SCN-0003 — 新しいEvidenceでDecisionを見直す
- SCN-0016 — Decision後も残差を次のInquiryへ渡す

ここでは新しいRequirementを追加しません。

### 3.2 Observation / Evidence / Unknown / Conflictを保持する

主に次で表現できます。

- REQ-0002 — Unknown / Conflict等を都合よく平坦化しない。
- REQ-0003 — Observation / Interpretation / Method等の意味差を保つ。
- REQ-0016 — Evidence / provenance / interpretationの境界を保つ。

主な既存Scenario:

- SCN-0001
- SCN-0011
- SCN-0012

ここでも新しいRequirementは不要です。

### 3.3 Cognitive Methodを適用する

主に次で表現できます。

- REQ-0004 — Cognitive MethodをRealizationと同一視しない。
- REQ-0015 — private chain-of-thoughtへ依存しない。
- REQ-0021 — Realization / Executionを交換可能にする。

主な既存Scenario:

- SCN-0005
- SCN-0015

current `sei.cognitive-method/v1alpha1`は、この意味境界をContractへ実体化し始めています。

### 3.4 Recommendation / Decision / Responsibilityを分ける

主に次で表現できます。

- REQ-0005 — Decision historyを再構成できる。
- REQ-0006 — semantic roleを黙って昇格させない。
- REQ-0008 — Recommendation / Decision等のrevisionを扱う。
- REQ-0013 — actor種別だけから必要な明示性やAuthorityを推定しない。
- REQ-0017 — Responsibilityを文脈へ結び付ける。

主な既存Scenario:

- SCN-0009 — RecommendationからExecutionまでの責任線

Product Journey用に新しいDecision概念は不要です。

### 3.5 Capability / Providerを選び、外部実行へ渡す

主に次で表現できます。

- REQ-0007 — CapabilityとProviderを分離する。
- REQ-0021 — Execution Realizationを交換可能にする。
- REQ-0022 — Provider-neutralなCapability Observationを扱う。

主な既存Scenario:

- SCN-0002
- SCN-0011
- SCN-0014

SEI自身がworkflow / agent runtimeを所有しないことと両立します。

### 3.6 実行結果を次の認知・判断へ戻す

ここは既存Requirementで必要な意味部品を表現できます。

- Execution successをDecision correctnessやBusiness Outcomeと同一視しない。
- Provider ObservationをProvider固有schemaから分離する。
- 新しいObservationを過去Decision作成時から存在したことにしない。
- residualからInquiryを再開できる。

これらはREQ-0001、REQ-0002、REQ-0005、REQ-0014、REQ-0022等へ追跡できます。

ただし、**外部実行後のObservationが次のInquiry / Decision reviewへ戻る循環全体**を一つのScenarioとして明示したcurrent SCNはありません。

ここが今回確認できた主要なAcceptance gapです。

### 3.7 人間とAIが同じcanonical meaningへ戻る

主に次で表現できます。

- REQ-0010 — Progressive Semantic Explicitness
- REQ-0011 — Projectionをcanonical authorityにしない。
- REQ-0019 — 人間とAIの双方が意味を読める。

主な既存Scenario:

- SCN-0006
- SCN-0013

この意味差も新しいREQは不要です。

### 3.8 時間経過後にhistorical basisを読み直す

主に次で表現できます。

- REQ-0001
- REQ-0005
- REQ-0009 — exact historical binding / revision integrity
- REQ-0018 — Storage implementationから意味を分離する。
- REQ-0020 — Evidenceを超える達成主張をしない。

主な既存Scenario:

- SCN-0003
- SCN-0008
- SCN-0010

## 4. 新しいRequirementを追加しない理由

Product Journeyは重要ですが、「一続きに使えること」を理由に、Inquiry、Execution Result、Workspace、Session等の新しいUniversal conceptを追加すると、製品UXや実装構造をsemantic Coreへ持ち込む危険があります。

current Requirementsは、各段階で失ってはならない意味をすでに定めています。

今回必要なのは次です。

```text
new semantic obligation
  → current evidenceでは未確認

existing semantic obligations composed end-to-end
  → current acceptance gap
```

現時点の不足は後者です。

したがって、Requirement追加ではなくAcceptance ScenarioとExecutable harnessで検証する方が適切です。

新しいRequirementが必要になるのは、end-to-end検討の中で、既存REQでは表現できない**独立した規範上の必要性**が見つかった場合だけです。

## 5. end-to-end Scenario候補

ISSUE-000048でstable IDを与える候補として、次のScenarioを提案します。

### 状況

利用者が一つのInquiryを開始する。Evidenceは一部がConflictし、不明点も残っている。

AIまたは人間がCognitive Methodを適用してRecommendationを作り、明示されたResponsibility / Authority境界のもとでDecisionを行う。

必要なCapabilityは外部Providerへ委ねる。実行結果から新しいObservationが得られる。

時間経過後、利用者または別のAIが当時のDecision basis、残っていたUnknown / Conflict、使用したMethod / Provider、実行後に得られたObservationを読み直し、必要ならInquiryを再開する。

### 期待

- Inquiry開始時に最大詳細を強制しない。
- Observation、Interpretation、Unknown、ConflictをDecisionへ黙って畳み込まない。
- Method Definition / Realization / Applicationを必要な範囲で読み分けられる。
- RecommendationをDecisionへ自動昇格させない。
- DecisionとResponsibility / Authorityを必要な粒度で追える。
- Provider run IDをDecision identityにしない。
- Execution successをDecision correctnessへ昇格させない。
- 実行後に得たObservationを、過去Decision作成時のEvidenceとして扱わない。
- residual / reopen informationを保持し、後からInquiryへ戻れる。
- ProjectionやProviderを交換してもcanonical meaningを再読できる。

### 失敗例

- AI RecommendationをそのままDecisionとして保存する。
- Decision作成時にUnknown / Conflictをresolvedへ変える。
- Provider runが成功しただけでDecisionを`verified`とする。
- 後から得たObservationで過去Decisionのbasisを上書きする。
- current ProviderやUIがなくなると過去Decisionを読めない。

## 6. 必須variant

一つのhappy pathだけではProduct Shapeを十分に検査できません。少なくとも次を同じScenario familyで扱います。

### normal path

Evidenceが十分に集まり、Decision後に外部実行まで進む。

### uncertain path

Unknown / Conflictを残したまま期限等の理由でDecisionし、後日追加Evidenceから再開する。

### collaborative path

AIがMethod Application / Recommendationを担い、人間または明示的に委任された主体がDecisionする。actor種別だけからAuthorityを推定しない。

### provider replacement path

後続実行でProviderを交換しても、以前のDecision identityとbasisを読み直せる。

### no-execution path

Decisionまでで完結し外部実行を行わない。SEIの価値がExecutionの存在に依存しないことを確認する。

## 7. semantic end-to-end harnessの最小仕様

ISSUE-000048の後続Executable Evidenceでは、最初からproduction UIを要求しません。

最小harnessは、canonical record / Contractを入力として次を検査できればよいとします。

1. journey内の各Artifact / recordをstable Referenceで辿れる。
2. Decisionからbasis、Method Application、Responsibility、residualへ戻れる。
3. external execution resultを新しいObservationとして接続できる。
4. 実行後Observationが過去Decision basisへ時間逆行して混入しない。
5. Provider交換後もhistorical Decisionを再構成できる。
6. no-execution variantでもDecision recordが成立する。
7. unknown / unsupported record versionをopaque + `not_verified`として保持できる。
8. Projectionだけからcanonical meaningを推測復元しない。

harnessの具体的な実装方式は別Issueで決めます。

## 8. Evidence境界

この文書で得られるのはDesign上のcomposition analysisです。

```text
Requirement composition defined
  != end-to-end Executable Evidence
  != human interaction validated
  != packaged product
  != release ready
  != operationally reliable
  != user outcome proven
```

- Design Evidence: **Satisfied for requirement-composition analysis**
- Executable Evidence: **Not Yet Verified for the end-to-end Product Journey**
- Release Evidence: **Not Yet Verified**
- Operational Evidence: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

## 9. Follow-up

- ISSUE-000048 — stable Acceptance Scenario化とRequirement / Scenario正本への反映
- ISSUE-000043 — Cognitive Method Contract / runtimeのExecutable slice
- ISSUE-000045 — human / AI Product Interaction boundary
- ISSUE-000046 — Packaging / Deployment boundary
- ISSUE-000047 — Identity / Authorization / Collaboration boundary

end-to-end harnessの実体化は、ISSUE-000048でScenarioを確定した後に独立Issueへ分離する。

## 10. Natural Japanese review

Product Shape、REQ-0001〜0022、SCN-0001〜0017、Cognitive Method Contract、Decision / Provider / Projectionのcurrent境界へ戻り、各journey段階がどの既存Requirementへ追跡できるかを一件ずつ照合した。その結果、新しいUniversal Requirementを増やすより、既存Requirementを一つのjourneyで同時に検査するAcceptanceが不足していると整理した。意味上の追加を最小限に保ち、Evidence強度を上げず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。
