# SOZA Acceptance Scenarios

更新日: 2026-08-31  
状態: **Current Acceptance Scenario Baseline**

## 1. この文書の役割

この文書は、SOZAが守る意味差を具体的な利用状況から検証するためのAcceptance Scenarioの正本入口です。

ScenarioはRequirementそのものでも、実装済みTest Caseでもありません。

```text
Requirement != Acceptance Scenario != Test Case
```

- Requirementは「何が必要か」を定めます。
- Scenarioは「どのような状況で、その意味差が必要になるか」を示します。
- Test Case / Fixtureは、actual implementationでScenarioをどう再現・検査するかを定めます。

current repositoryにはscoped Executable Evidenceがありますが、Scenarioごとに確認範囲は異なります。fixtureやruntimeがScenarioの一部だけを検証している場合は`Partially Satisfied`とし、確認していない部分まで引き上げません。

Evidenceは次の5段階で読みます。

```text
Design
  != Executable
  != Release
  != Operational
  != Adoption / Outcome
```

## 2. Scenario一覧

| ID | Scenario | 主なValue Axis | 主なRequirement |
|---|---|---|---|
| SCN-0001 | 根拠が割れている判断 | V1, V2, V5 | REQ-0002, REQ-0003, REQ-0014, REQ-0016 |
| SCN-0002 | 同じIntent、異なるCapability Provider | V2, V4, V8 | REQ-0006, REQ-0007, REQ-0022 |
| SCN-0003 | 新しいEvidenceでDecisionを見直す | V1, V3, V5 | REQ-0001, REQ-0005, REQ-0008, REQ-0009, REQ-0014 |
| SCN-0004 | 軽量案件と高影響案件 | V2, V6, V7 | REQ-0006, REQ-0010, REQ-0013 |
| SCN-0005 | Cognitive MethodとRealizationを交換する | V1, V3, V8 | REQ-0001, REQ-0004, REQ-0015, REQ-0021 |
| SCN-0006 | Projectionを作り直す | V6, V8 | REQ-0011, REQ-0019 |
| SCN-0007 | Bounded Principal間で協働する | V4, V5, V8 | REQ-0012 |
| SCN-0008 | Storageを交換する | V1, V3, V8 | REQ-0001, REQ-0018, REQ-0021 |
| SCN-0009 | RecommendationからExecutionまでの責任線 | V1, V2 | REQ-0005, REQ-0006, REQ-0008, REQ-0013, REQ-0017 |
| SCN-0010 | 可変Artifact更新後に過去Decisionを再構成する | V1, V3, V4 | REQ-0005, REQ-0009, REQ-0018, REQ-0020, REQ-0022 |
| SCN-0011 | Providerが部分的にdegraded / 未観測である | V2, V4, V5 | REQ-0002, REQ-0006, REQ-0007, REQ-0016, REQ-0022 |
| SCN-0012 | Provider内部をSelective Disclosureする | V4, V5, V8 | REQ-0012, REQ-0022 |
| SCN-0013 | 簡略UIとcanonical meaningを両立する | V6, V7 | REQ-0010, REQ-0011, REQ-0019 |
| SCN-0014 | Execution Providerを交換する | V1, V4, V8 | REQ-0001, REQ-0007, REQ-0021 |
| SCN-0015 | PatternとCognitive Methodを分離する | V2, V3, V8 | REQ-0004, REQ-0015, REQ-0016 |
| SCN-0016 | Decision後も残差を次のInquiryへ渡す | V1, V3, V5 | REQ-0002, REQ-0003, REQ-0005, REQ-0014 |
| SCN-0017 | Evidenceが低い段階で達成主張を監査する | V1, V6 | REQ-0020 |

---

## SCN-0001 — 根拠が割れている判断

### 状況

同じ論点について複数のSourceが一致していない。あるSourceは事実Aを支持し、別のSourceはAと両立しにくいObservation Bを報告している。Decisionを完全な情報が揃うまで延期できるとは限らない。

### 期待

- Source provenanceとdiscovery routeを必要に応じて区別できる。
- ObservationとInterpretation / Hypothesisを区別できる。
- Conflictを残したままRecommendationやDecisionを作れる。
- Decision後も、当時残っていたUnknown / Conflictを確認できる。
- EvidenceUseが何をbasisとして用いたかを示し、Artifact自体を普遍的Truthへ昇格させない。
- 後日追加Evidenceが得られたとき、残差からInquiryを再開できる。

### 失敗例

- 最新Sourceだけを残して過去のConflictを消す。
- confidence scoreが最も高いSourceをTruthとして自動採用する。
- Decisionが作成された時点でUnknownを自動的にresolvedへ変える。

### Current Evidence

- Design: **Satisfied**
- Executable: **Partially Satisfied** — Decision with unresolved、partial knowledge、Unknown / Withheldのfixtureとruntimeで、不確実性を残したDecisionの一部境界を確認済み。Source discovery、一般的Observation / Hypothesis、Inquiry再開を横断するruntimeは未検証。
- Release: **Not Yet Verified**
- Operational: **Not Yet Verified**
- Adoption / Outcome: **Not Yet Verified**

## SCN-0002 — 同じIntent、異なるCapability Provider

### 状況

一つのIntentに対して、人間による手作業、外部SaaS/API、TEI、別のAIサービスが候補になる。

### 期待

- Capability DefinitionとProviderを分けて扱える。
- availability、condition、cost、latency、auditability等を必要な範囲で比較できる。
- SOZA関連技術であることだけを理由にTEIを優先しない。
- Matchingは候補説明であり、Recommendation、Decision、Authorization、Executionへ自動昇格しない。
- Providerを未確定のままCapabilityを選ぶ、複数Capabilityを組み合わせる、Choiceを保留する状態を扱える。
- 最終Outcomeが同じでも、どのCapability / Provider経路を通ったか確認できる。

### 失敗例

- Provider kindごとに固定優先順位を持つ。
- Matching score最大のProviderを自動実行する。
- TEI固有IDをCapabilityのcanonical identityにする。

### Current Evidence

- Design: **Satisfied**
- Executable: **Partially Satisfied** — F5とsynthetic Provider A / B Adapterで、同じCapabilityに対する異質なProvider ObservationとProvider固有Schemaの分離を確認済み。Matching / Choice Decision / Executionは未実装。
- Release: **Not Yet Verified**
- Operational: **Not Yet Verified**
- Adoption / Outcome: **Not Yet Verified**

## SCN-0003 — 新しいEvidenceでDecisionを見直す

### 状況

Decision D1の後、新しいObservation O2が得られ、D1のbasisだったHypothesis H1が弱くなる。新しいDecision D2が必要になる。

### 期待

- D1を当時のEvidence、Unknown、Constraint、Rationaleとともに再構成できる。
- O2が後から得られたことを識別できる。
- H1、Recommendation、D1、D2のrevision / supersession関係を辿れる。
- D1を削除してD2へ置換するのではなく、両Decisionと変更理由を保持できる。
- 「現在はD2が妥当」という事実から、「D1作成時にもO2を知っていた」ことにしない。

### 失敗例

- latest Decisionだけを残す。
- 現在のArtifact revisionでD1のbasisを読み替える。
- Git commit差だけからsemantic revisionを推定する。

### Current Evidence

- Design: **Satisfied**
- Executable: **Partially Satisfied** — Semantic Lineage、Exact Binding、Decision basis / unresolvedをContract checkerとfirst runtimeで検査済み。D1→D2のproduction lifecycleと一般Hypothesis更新は未検証。
- Release: **Not Yet Verified**
- Operational: **Not Yet Verified**
- Adoption / Outcome: **Not Yet Verified**

## SCN-0004 — 軽量案件と高影響案件

### 状況

Aは可逆で低影響な内部作業、Bは不可逆性が高く外部影響や責任も大きい判断である。

### 期待

- Aに最大のDecision / Authority / Assurance記録を強制しない。
- Bでは必要なRecommendation、Decision、Authority、Evidence、historical binding等を省略しない。
- actorが人間かAIかだけで必要な明示性を決めない。
- AとBで要求される明示性が異なる理由をPolicy / Profile等から説明できる。
- simple UIを使ってもBのcanonical meaningを削らない。

### 失敗例

- すべての案件へ最大詳細を必須化する。
- AI confidenceが高いことだけを理由にBのAuthority記録を省略する。

### Current Evidence

- Design: **Satisfied**
- Executable: **Not Yet Verified** — Profile / Policyによる明示量の切替runtimeは未実装。
- Release: **Not Yet Verified**
- Operational: **Not Yet Verified**
- Adoption / Outcome: **Not Yet Verified**

## SCN-0005 — Cognitive MethodとRealizationを交換する

### 状況

同じInquiryへ、ある時点ではKJ法を使い、後の時点では別のCognitive Methodを使う。さらに同じMethodのRealizationがPromptからmodel programや人間手順へ変わる。

### 期待

- Method DefinitionとRealizationを区別できる。
- Method Applicationが重要なinput / output / residualを参照できる。
- Realization変更によって過去のMethod Applicationの意味を現在版へ書き換えない。
- private chain-of-thoughtの保存を必要としない。
- Method Applicationの存在だけをAssuranceとしない。

### 失敗例

- Prompt文字列をMethod identityとする。
- Methodを適用したことだけで結論を正しいと判定する。

### Current Evidence

- Design: **Satisfied**
- Executable: **Not Yet Verified** — first runtime sliceはCognitive Method Applicationを直接対象としていない。
- Release: **Not Yet Verified**
- Operational: **Not Yet Verified**
- Adoption / Outcome: **Not Yet Verified**

## SCN-0006 — Projectionを作り直す

### 状況

同じ案件をWeb workspace、kj-atlas、CLI、dashboard、将来の別UIで表示する。あるProjectionを廃止する。

### 期待

- UI layout、tab、chat順序を変えてもcanonical meaningが変化しない。
- 一つのProjectionを削除しても案件の耐久的Artifactを失わない。
- Projection固有の便利な状態とcanonical semantic stateを区別できる。
- 人間向けProjectionから、判断理由・未解決点・責任線を追える。

### 失敗例

- UI component stateが唯一のDecision recordになる。
- Projection削除とともにprovenanceが失われる。

### Current Evidence

- Design: **Partially Satisfied** — Projection非権威の原則とArchitecture boundaryはあるが、具体Projectionの設計は限定的。
- Executable: **Not Yet Verified**
- Release: **Not Yet Verified**
- Operational: **Not Yet Verified**
- Adoption / Outcome: **Not Yet Verified**

## SCN-0007 — Bounded Principal間で協働する

### 状況

組織Aと外部組織Bが協働する。双方には相手へ共有できない内部資料、判断手続、credentialがある。

### 期待

- 全内部Artifact共有を要求せず、Request、Offer、Commitment、Evidence、Result等の必要な情報だけを交換できる。
- 相手が開示しないcontextの存在を、必要に応じてWithheldとして外在化できる。
- Bの内部Decision processをAのcanonical world modelへ取り込むことを必須としない。
- Request、Commitment、Authority Grant、Executionを同一視しない。

### 失敗例

- federation参加の条件として全内部model統合を求める。
- 情報非開示をCapability不存在や不正の証拠として自動解釈する。

### Current Evidence

- Design: **Satisfied**
- Executable: **Partially Satisfied** — F7とpartial-knowledge fixtureでWithheld / Unknownを分離可能。FederationのRequest / Offer / Commitment transportは未検証。
- Release: **Not Yet Verified**
- Operational: **Not Yet Verified**
- Adoption / Outcome: **Not Yet Verified**

## SCN-0008 — Storageを交換する

### 状況

prototypeではGit / filesystemを使い、後にDB / object store等へ移行する。

### 期待

- logical identity、semantic revision、provenance、reference integrityを保ったままStorage implementationを交換できる。
- exact bindingが必要な過去Decisionについて、移行後も当時の内容を特定できる。
- Core Contractが特定DBのtransaction modelやevent sourcingを必須としない。

### 失敗例

- DB primary keyをsemantic identityと同一視する。
- Storage移行時に過去revisionを最新状態へ畳み込む。

### Current Evidence

- Design: **Satisfied**
- Executable: **Not Yet Verified** — runtimeはStorage固有IDをsemantic identityとして要求しないが、actual Storage migrationは未実施。
- Release: **Not Yet Verified**
- Operational: **Not Yet Verified**
- Adoption / Outcome: **Not Yet Verified**

## SCN-0009 — RecommendationからExecutionまでの責任線

### 状況

AIがRecommendation Rを作り、組織の担当者がDecision Dを行う。実行には別のAuthorityが必要で、外部ProviderがActionを実行する。

### 期待

- R、D、Authority、Action Intent、Provider Executionを区別できる。
- Rを作成した主体、Dを担った主体、Authorizationを付与した主体、実行ProviderのResponsibilityを文脈ごとに参照できる。
- Dが存在してもAuthorizationがなければ実行可能と推定しない。
- Executionが成功しても、Dが妥当だったことの十分な証明とはしない。

### 失敗例

- AI RecommendationをDecisionとして保存する。
- Decision記録へ`approved=true`があるだけで外部Providerを実行する。

### Current Evidence

- Design: **Satisfied**
- Executable: **Partially Satisfied** — Recommendation-onlyを正常に扱い、Decision recordへのAuthority埋め込みを拒否するfixture / runtimeを確認済み。Authorization / Action executionはscope外。
- Release: **Not Yet Verified**
- Operational: **Not Yet Verified**
- Adoption / Outcome: **Not Yet Verified**

## SCN-0010 — 可変Artifact更新後に過去Decisionを再構成する

### 状況

Decision Dは、Provider Observation O、Reference Artifact A、mapping Mをbasisとして作られた。その後O、A、Mはいずれも更新される。

### 期待

- D作成時に使ったO / A / Mの版を、必要なexact historical bindingから特定できる。
- 現在版を参照してDのbasisを再構成したことにしない。
- Representation Profileやverifierが利用不能なら、`not_verified`と`failed`を区別できる。
- Evidenceが低い段階ではhistorical reconstructionを実証済みと主張しない。

### 失敗例

- logical refを辿って常に最新版を読む。
- verifier不在をdigest mismatchと記録する。

### Current Evidence

- Design: **Satisfied**
- Executable: **Partially Satisfied** — F6、Exact Binding mismatch、Verification Outcome、first runtimeでhistorical basisの一部を再構成可能。長期のproduction更新とhistorical M47 digest mappingは未検証。
- Release: **Not Yet Verified**
- Operational: **Not Yet Verified**
- Adoption / Outcome: **Not Yet Verified**

## SCN-0011 — Providerが部分的にdegraded / 未観測である

### 状況

TEI Applicationは存在するが依存Databaseの一つがread-onlyである。別のケースではPluginは解決済みだがObservation Providerが利用不能である。

### 期待

- Provider内部状態を一律な`available / unavailable`へ平坦化しない。
- 対象operationやconditionに応じたCapability Observationを作れる。
- `not observed`を`unavailable`へ変換しない。
- Provider stateからCapability interpretationへのadapter / mappingをObservationそのものやDecisionと同一視しない。
- mappingがDecision basisとして重要なら、後から当時版を特定できる。

### 失敗例

- Database一つがread-onlyならApplication全Capabilityをunavailableにする。
- Observation gapをnegative observationとして保存する。

### Current Evidence

- Design: **Satisfied**
- Executable: **Partially Satisfied** — F1 / F4、F1〜F7 runtime、synthetic Adapterのmissing→unknownをactual CIで確認。current fixture / synthetic Adapterの範囲では主要境界を検証済みだが、TEI production adapterは未検証。
- Release: **Not Yet Verified**
- Operational: **Not Yet Verified**
- Adoption / Outcome: **Not Yet Verified**

## SCN-0012 — Provider内部をSelective Disclosureする

### 状況

Providerは、内部topologyや契約情報を全量開示できないが、Capability Choiceに必要なEvidenceの一部は共有できる。

### 期待

- Provider内部SchemaをSOZA Universal Coreへコピーせず、必要なObservation / Evidenceだけを共有できる。
- Withheld contextとUnknownを必要に応じて区別できる。
- 非開示を理由にCapability不存在・incompatible・低信頼を自動推定しない。
- raw internal topologyを持たなくても、共有されたEvidenceのprovenanceを保持できる。

### 失敗例

- 比較のためにProvider内部DB構造の全量開示を必須にする。

### Current Evidence

- Design: **Satisfied**
- Executable: **Partially Satisfied** — F7でWithheldとProvider-specific contextを保持し、内部topology全量をUniversal fieldへ要求しないことを確認。current fixtureの範囲では主要境界を検証済みだが、production selective disclosure運用は未検証。
- Release: **Not Yet Verified**
- Operational: **Not Yet Verified**
- Adoption / Outcome: **Not Yet Verified**

## SCN-0013 — 簡略UIとcanonical meaningを両立する

### 状況

日常利用ではDecisionの短い要約と主要な未解決点だけを表示し、監査時にはbasis、provenance、Authority、revisionまで確認する必要がある。

### 期待

- simple viewを採用してもcanonical meaningを削除しない。
- 人間が簡略画面から必要に応じて詳細へ降りられる。
- AIは同じcanonical dataを構造として利用できる。
- human summaryとmachine-readable representationが矛盾しない。
- 低影響案件では不要な詳細入力を強制しない。

### 失敗例

- UIを簡単にするためUnknownやResponsibilityをcanonical recordから削除する。
- AI用Promptにしかbasisが残らない。

### Current Evidence

- Design: **Partially Satisfied**
- Executable: **Not Yet Verified** — human-readable Contract Definitionとmachine-readable Schemaはあるが、simple UI / Projectionの実装Evidenceはない。
- Release: **Not Yet Verified**
- Operational: **Not Yet Verified**
- Adoption / Outcome: **Not Yet Verified**

## SCN-0014 — Execution Providerを交換する

### 状況

同じIntent / Decisionに対する実行を、当初はworkflow engine A、後にはAI agent runtime B、別案件ではTEIへ委ねる。

### 期待

- Execution Providerを交換してもIntent / Decisionのlogical meaningを維持できる。
- Provider固有run IDをDecision identityの唯一の根拠にしない。
- Provider廃止後もhistorical Decisionを読める。
- SOZAが特定Providerのruntime lifecycleをUniversal Coreとして所有しない。

### 失敗例

- Camunda process instance IDがSOZA Decisionのcanonical IDになる。
- TEI deployment schemaなしでは過去Decisionを読めない。

### Current Evidence

- Design: **Satisfied**
- Executable: **Not Yet Verified** — synthetic Provider AdapterはObservation Provider境界のEvidenceであり、Execution Provider交換のEvidenceではない。
- Release: **Not Yet Verified**
- Operational: **Not Yet Verified**
- Adoption / Outcome: **Not Yet Verified**

## SCN-0015 — PatternとCognitive Methodを分離する

### 状況

TEI Design KnowledgeのPattern Cardを、AIがCognitive Methodの探索対象として利用する。Patternと対象が似ているが、人間は別設計をDecisionする。

### 期待

- Pattern CardとCognitive Method Definitionを別Artifact / roleとして扱える。
- Pattern matchをRecommendationやDecisionへ自動昇格させない。
- Method Applicationを結論の正しさやAssuranceへ自動昇格させない。
- historical Pattern版がDecision basisとして重要なら当時版を特定できる。
- domain-specific PatternをSOZA Universal Coreへ取り込まない。

### 失敗例

- Reference Modelに一致しただけでRequirement充足や設計採用を確定する。

### Current Evidence

- Design: **Satisfied** — ADR-0017。
- Executable: **Not Yet Verified** — Pattern / Cognitive Methodを横断するcurrent runtime sliceは未実装。
- Release: **Not Yet Verified**
- Operational: **Not Yet Verified**
- Adoption / Outcome: **Not Yet Verified**

## SCN-0016 — Decision後も残差を次のInquiryへ渡す

### 状況

期限のためDecision Dを行うが、Q1は未回答、Evidence E2 / E3はConflictしたまま、反例Cも残っている。後日、新しいEvidenceが得られる。

### 期待

- Dの作成によってQ1、Conflict、反例、reopen conditionを消さない。
- Dがどの残差を受け入れて行われたか確認できる。
- 後日、残差を起点としてInquiry / Decision reviewを再開できる。
- 新しいEvidenceをD作成時から存在したことにしない。

### 失敗例

- Decision statusが`done`になった時点で全Questionをresolvedへ変える。

### Current Evidence

- Design: **Partially Satisfied** — unresolved参照は定義済みだが、reopen conditionのcurrent Contractは限定的。
- Executable: **Partially Satisfied** — Decision with unresolved fixtureとruntimeで残差保持を確認。Inquiry再開のend-to-end runtimeは未検証。
- Release: **Not Yet Verified**
- Operational: **Not Yet Verified**
- Adoption / Outcome: **Not Yet Verified**

## SCN-0017 — Evidenceが低い段階で達成主張を監査する

### 状況

ある開発時点ではProduct Value、ADR、Requirement、Scenarioだけが整備され、Architecture / Contract / Runtimeのcurrent Executable Evidenceはまだない。一方、historical candidateにはlocal PASSが残っている。

その後current repositoryへExecutable Evidenceが増えても、対象範囲を超えるRelease / Operational / Adoption / Outcome主張へ自動昇格させてはならない。

### 期待

- current Evidenceとhistorical candidate evidenceを分ける。
- historical local PASSをcurrent repositoryのExecutable Evidenceへ自動継承しない。
- Evidenceがない高さは`Not Yet Verified`として扱う。
- READMEや報告書がactual treeに存在しないtest commandを「現在実行可能」と主張しない。
- actual fixtureがPASSしても、それだけでRelease / Operational / Adoption / Outcome Evidenceへ昇格させない。

### 失敗例

- 設計文書完成を「実装完了」と表現する。
- historical candidateのPASSをcurrent branchのPASSとして表示する。
- releaseされていない状態でrelease coverageを主張する。
- productionで動いたことだけから利用者価値を実証済みとする。

### Current Evidence

- Design: **Satisfied** — Value Acceptance / ADR-0018 / REQ-0020で5段階Evidenceを定義。
- Executable: **Partially Satisfied** — current checker / fixture / runtime CIのEvidence文書で対象範囲を限定し、historical PASSをcurrent PASSへ継承しない運用を実施。Evidence claim専用の自動linterは未実装。
- Release: **Not Yet Verified**
- Operational: **Not Yet Verified**
- Adoption / Outcome: **Not Yet Verified**

---

## 3. Core概念を追加するときのScenario規則

新しいUniversal Core概念は、少なくとも一つのAcceptance Scenarioで、**その概念を区別しなければ実際にどの意味が失われるか**を説明できることを採用条件の一つとします。

現在の実装で便利でも、Scenario上の意味差を示せない場合は、Coreへ追加する前に次を検討します。

- 既存概念の組合せ
- Reference
- Extension
- Profile
- Provider-specific knowledge
- Cognitive Method
- Projection
- Adapter / Mapping

Scenarioが存在することだけでCore化を決定するものではありません。Product Value、複数domainでの意味安定性、Provider Independence等を合わせてADRで判断します。

## 4. Executable fixtureとの関係

current repositoryでは、すでに一部Scenarioがfixture / runtimeへ接続されています。

例:

```text
SCN-0011
  → Capability Observation F1 / F4
  → synthetic Provider Adapter missing→unknown test

SCN-0012
  → Capability Observation F7
```

SCN IDはsemantic scenario identityとして保ち、fixture / test IDとは分けます。fixtureのPASS / FAILによってSCNそのものの意味を変更しません。

Scenarioの一部だけを検証した場合は`Partially Satisfied`とし、Scenario全体の実装完了へ読み替えません。

## 5. Historical Scenarioとの関係

2026-08-30 candidateの`SOZA-AS-001`〜`SOZA-AS-008`は、意味核をSCN-0001〜SCN-0008へ継承しました。

旧IDはhistorical provenanceとして`history/HISTORICAL_REQUIREMENT_MAPPING.md`に残し、current SCN identityには用いません。

## 6. Natural Japanese review

SCN-0001〜0017をcurrent Product Value traceability、Contract 17 fixture、Representation Profile、first runtime、synthetic Provider Adapterへ一件ずつ照合した。実際にExecutable EvidenceがあるScenarioだけを限定的に更新し、Release / Operational / Adoption / Outcomeへは引き上げていない。その後、Scenarioの意味、期待、失敗条件、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。
