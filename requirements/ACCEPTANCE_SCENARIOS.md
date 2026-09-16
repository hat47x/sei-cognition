# SEI Acceptance Scenarios

更新日: 2026-09-16  
状態: **Current Acceptance Scenario Baseline**

## 1. この文書の役割

この文書は、SEIが守る意味差を具体的な利用状況から検証するためのAcceptance Scenarioの正本入口です。

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
| SCN-0018 | Inquiryから実行後の再検討までを一続きに扱う | V1, V2, V3, V4, V5, V8 | REQ-0001, REQ-0002, REQ-0004, REQ-0005, REQ-0007, REQ-0014, REQ-0017, REQ-0021, REQ-0022 |
| SCN-0019 | 途中失敗・stale draftを含むcanonical commit | V1, V3, V8 | REQ-0009, REQ-0018, REQ-0020, REQ-0023 |

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
- SEI関連技術であることだけを理由にTEIを優先しない。
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
- Executable: **Partially Satisfied** — V6/V7 evaluation harnessで、low-impactの最小Decisionをlight Projectionで扱い、basis / Responsibility等の最大詳細を一律必須にしないことを確認した。high-impactのrich Decisionではaudit Projectionを要求し、lightだけで完了扱いにするnegative caseを拒否できる。productionでのimpact判定Policy / Profile runtimeや実運用は未検証。
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
- Executable: **Partially Satisfied** — `sei.cognitive-method/v1alpha1`のC1〜C8、negative / unknown-version fixture、standalone / Semantic Interchange双方のtyped runtimeで、Method Definition / Realization / Applicationを分離し、input / output / residual、Exact-bound Method / Realization Reference、Realization省略を意味を変えずに保持できることを確認した。Contract Conformance Run `33467838961`とSemantic Runtime Conformance Run `33467838941`はsuccess。異なるMethodやRealizationをproductionで実際に差し替えて運用する経路は未検証。
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

- Design: **Satisfied** — Projection非権威のArchitecture boundaryに加え、同一canonical sourceからlight / auditを派生させる評価protocolとsemantic question setを実体化した。
- Executable: **Partially Satisfied** — rich canonical sourceからlight / audit Projectionを決定的に再生成でき、Projectionを再構築してもcanonical sourceのstructural digestが変わらないことをharnessで確認した。lightから未解決事項と詳細の存在へ辿れる一方、Web / CLI / desktop等のproduction Projection交換は未検証。
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

- Provider内部SchemaをSEI Universal Coreへコピーせず、必要なObservation / Evidenceだけを共有できる。
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

- Design: **Satisfied** — light / audit Projectionの役割、同一canonical source、semantic question set、Progressive Explicitness policyを評価protocolとして定義済み。
- Executable: **Partially Satisfied** — lightはDecision、未解決事項、Authorization Evidence stateを前景化し、basis / Responsibility / Provenanceの件数とaudit導線を保持する。auditは6 semantic questionsについてmachine-readable sourceと一致し、low-impactでは不要な最大詳細を強制しないことをRun `33456710459`で確認した。production UIと実利用者の可読性は未検証。
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
- SEIが特定Providerのruntime lifecycleをUniversal Coreとして所有しない。

### 失敗例

- Camunda process instance IDがSEI Decisionのcanonical IDになる。
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
- domain-specific PatternをSEI Universal Coreへ取り込まない。

### 失敗例

- Reference Modelに一致しただけでRequirement充足や設計採用を確定する。

### Current Evidence

- Design: **Satisfied** — ADR-0017 / ADR-0025でPatternとCognitive Methodを別の意味境界として扱う。
- Executable: **Partially Satisfied** — Cognitive Method C5でdomain-specific Pattern相当の外部ArtifactをApplication input Referenceとして保持し、Pattern固有Universal fieldをMethod recordへ混入させるnegative fixtureを拒否する。typed runtimeはPattern inputをReferenceのまま保持し、Method ApplicationをRecommendation / Decision / Assuranceへ昇格させない。Contract Conformance Run `33467838961`とSemantic Runtime Conformance Run `33467838941`はsuccess。実際のTEI Pattern Card catalog、Pattern matching、別設計を選ぶproduction Decision workflowは未検証。
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
- Executable: **Partially Satisfied** — Decision with unresolved fixtureとruntimeに加え、end-to-end Product Journey harnessで、Decisionの`unresolved_refs`とexecution後の新しいObservationを後続のreopen Method Applicationへ入力として引き渡すsynthetic pathをRun `33478127484`で確認した。実業務上のInquiry lifecycle、reopen policy、D1→D2の運用は未検証。
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
- Executable: **Partially Satisfied** — current checker / fixture / runtime CIに加え、V6/V7 Projection evaluationもsummaryで`release=false / operational=false / adoption_outcome=false`を明示し、Product Value TraceabilityではRun `33456710459`をevaluation-harness scoped Executable Evidenceとしてのみ記録している。Evidence claim専用の汎用linterは未実装。
- Release: **Not Yet Verified**
- Operational: **Not Yet Verified**
- Adoption / Outcome: **Not Yet Verified**

## SCN-0018 — Inquiryから実行後の再検討までを一続きに扱う

### 状況

利用者が一つのInquiryを開始する。Evidenceの一部は相互にConflictしており、未回答のQuestionも残っている。

人間またはAIがCognitive Methodを適用してRecommendationを作り、必要なResponsibility / Authority境界のもとでDecisionを行う。Decisionに基づく処理は外部のCapability Providerへ委ねられ、実行後に新しいObservationが得られる。

時間が経過した後、利用者または別のAIが、当時のDecision basis、残っていたUnknown / Conflict、適用したMethod、利用したProvider、実行後に得られたObservationを読み直し、必要ならInquiryを再開する。

このScenarioは、すべてのSEI利用が同じ順序で進むことを要求するものではない。SCN-0001〜SCN-0016で個別に定めた意味境界が、一つの代表的なProduct Journeyの中でも同時に失われないことを検査する統合Scenarioである。

### 期待

- Inquiry開始時に最大詳細の入力を一律に強制しない。
- Observation、Interpretation、Unknown、ConflictをDecisionへ黙って畳み込まない。
- Method Definition、Realization、Applicationを必要な範囲で読み分けられる。
- RecommendationをDecisionへ自動昇格させない。
- DecisionとResponsibility / Authorityを必要な粒度で追跡できる。
- Provider固有run IDをDecisionのcanonical identityにしない。
- Execution successをDecision correctnessやBusiness Outcome successへ自動昇格させない。
- 実行後に得たObservationを、過去Decisionを作成した時点ですでに存在したEvidenceとして扱わない。
- Decision時に残したresidual / reopen informationを保持し、新しいObservationからInquiry / Decision reviewを再開できる。
- ProjectionやProviderを交換しても、canonical meaningとhistorical basisを再読できる。
- external executionを行わずDecisionまでで終了する場合でも、SEI上のDecision recordとhistorical valueが成立する。

### 必須variant

- **normal path** — 必要なEvidenceが集まり、Decision後に外部実行まで進む。
- **uncertain path** — Unknown / Conflictを残したままDecisionし、後日得たEvidenceから再開する。
- **collaborative path** — AIがMethod Application / Recommendationを担い、人間または明示的に委任された主体がDecisionする。actor種別だけからAuthorityを推定しない。
- **provider replacement path** — 後続実行でProviderを交換しても、以前のDecision identityとbasisを読み直せる。
- **no-execution path** — Decisionまでで完結し、外部実行がなくても記録価値が成立する。

### 失敗例

- AI RecommendationをそのままDecisionとして保存する。
- Decision作成時にUnknown / Conflictを自動的にresolvedへ変える。
- Provider runが成功しただけでDecisionを`verified`または「正しかった」と扱う。
- 実行後に得たObservationで、過去Decisionのbasisを黙って上書きする。
- current ProviderやProjectionが利用不能になると過去Decisionを読めない。
- external executionがないDecisionを不完全なrecordとして捨てる。

### Current Evidence

- Design: **Satisfied** — `PRODUCT_JOURNEY_COMPOSITION.md`でProduct ShapeとREQ-0001〜REQ-0022、SCN-0001〜SCN-0017を横断し、新しいUniversal Requirementを追加せずに統合Scenarioとして成立することを確認した。
- Executable: **Partially Satisfied** — `runtime/go/journeyharness`でnormal / uncertain / collaborative / provider replacement / no-executionの主要variantを一つのsemantic Product Journeyとして検査するfixtureを実体化した。Run `33478127484`では、Semantic Interchange loaderを通るnormal path、RecommendationとDecisionの分離、Responsibility分離、execution後Observationの時間境界、historical Decision statement / basisの非改変、unresolvedからreopenへの引継ぎ、Provider / Capability分離、unsupported recordの`not_verified`保持、Projectionがcanonical Decisionを代替しないことを確認した。ただしproduction UI、production Provider / execution engine、実際のAuthorization、長期運用上のreopen、実利用者価値は未検証であり、本Scenario全体を`Satisfied`にはしない。
- Release: **Not Yet Verified**
- Operational: **Not Yet Verified**
- Adoption / Outcome: **Not Yet Verified**

## SCN-0019 — 途中失敗・stale draftを含むcanonical commit

### 状況

利用者またはmachine clientがcanonical state S0を読み、そのstateを前提として複数recordを含むsemantic change planを作る。

一つのvariantでは、commit途中にfailureが発生するか、先行changeをstagingした後のchangeがvalidationに失敗する。別のvariantでは、plan作成後に別操作がcanonical stateをS1へ変更し、その後S0由来の古いdraft / planをcommitしようとする。

このScenarioは、特定DB transactionやsnapshot token方式を要求するものではない。Product Interactionが「commit成功」として公開する意味がcanonical stateと矛盾しないことを検査する。

### 期待

- 正常完了として読めるcanonical stateは、操作前のvalid stateまたは全変更反映後のvalid stateのいずれかである。
- commit途中までstagingされた一部changeをsuccessful canonical stateとして露出しない。
- 後続validation failureが起きた場合、先行changeだけを正常完了として公開しない。
- S0由来のstale draft / planが、S1で追加・変更された意味を黙って無視または上書きしない。
- stale writeはreject、explicit conflict、明示的なre-plan / rebase等として観測できる。
- wording等のdraft編集だけでsnapshot preconditionを暗黙更新したことにしない。
- concurrency token、generation、digest、ETag等をSemantic Revision、Logical Reference、Decision revisionへ読み替えない。
- Persistence transaction、atomic replace、append protocol、compensation等の具体方式をUniversal Coreへ固定しない。
- commit failureやstale conflictを、案件上のnegative fact、Decision failure、`No`へ自動変換しない。

### 必須variant

- **multi-record success** — 複数changeがすべてvalidで、全体が一貫したafter-stateとして公開される。
- **mid-commit fault** — 一部changeをstagingした後にfailureを注入し、before-stateのcanonical meaningが維持される。
- **later validation failure** — 後続changeが拒否されても、先行changeだけがsuccessful stateとして残らない。
- **stale snapshot** — draft作成後のcanonical changeを検知し、古いdraftを黙ってcommitしない。必要ならfresh planを明示的に作り直す。

### 失敗例

- 2件のchangeのうち1件目だけ保存された状態を「保存しました」と表示する。
- validationに失敗した後続changeだけを捨て、先行changeを正常完了として残す。
- 古いAI draftが、draft作成後に追加されたUnknownやObservationを無視してlast-write-winsでcommitされる。
- storage generationが増えたことをSemantic Revisionが起きた証拠として保存する。
- stale conflictを案件上の`unavailable`やDecision rejectionへ変換する。

### Current Evidence

- Design: **Satisfied** — REQ-0023、`SEI_FIRST_USABLE_PRODUCT_SLICE.md`のmeaning-preserving commit / stale-write境界、`SEI_INTERACTION_WORKING_SET_ARCHITECTURE.md`のCommit Coordinator / snapshot precondition、ISSUE-000073 Candidate Requirement監査でScenario上の意味差を固定した。
- Executable: **Not Yet Verified** — `runtime/go/interactionprobe/commit.go` / `commit_test.go`にはmulti-record staging、fault injection、後続validation failureを扱うprobe sourceがあり、`provisional.go` / `provisional_test.go`にはstale snapshot拒否とfresh proposalを扱うprobe sourceがある。ただしSCN-0019採用時点では、このScenarioに対するactual test runをcurrent Evidenceとして確認していない。
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

SCN-0018のような統合Scenarioも、Journeyの途中に登場する概念を自動的にUniversal Coreへ昇格させる根拠にはしません。Product Interaction上のSession、Workspace、Step等が必要になっても、semantic Coreへ必要かは別途ScenarioとADRで判断します。

SCN-0019も同様に、canonical commit integrityを要求することからUniversal Transaction、Snapshot、ETag、Generation等のsemantic entityを導かない。Scenarioが要求するのはsuccessful canonical stateの意味整合性であり、実現方式はProduct / Persistence Architectureへ委ねる。

## 4. Executable fixtureとの関係

current repositoryでは、一部Scenarioがfixture / runtime / evaluation harnessへ接続されています。

例:

```text
SCN-0004 / SCN-0006 / SCN-0013
  → V6 / V7 Projection evaluation harness
  → rich / low-impact canonical source
  → light / audit Projection
  → semantic question / negative case checker

SCN-0005 / SCN-0015
  → Cognitive Method C1〜C8 + negative / unknown-version fixture
  → standalone / Semantic Interchange typed runtime
  → Partially Satisfied (Contract Run 33467838961 / Runtime Run 33467838941)

SCN-0011
  → Capability Observation F1 / F4
  → synthetic Provider Adapter missing→unknown test

SCN-0012
  → Capability Observation F7

SCN-0018
  → end-to-end semantic Product Journey harness
  → Partially Satisfied (fixture-scoped; Run 33478127484)

SCN-0019
  → interactionprobe Commit Coordinator / provisional stale-draft source
  → Executable Not Yet Verified until an actual run is pinned to this Scenario
```

SCN IDはsemantic scenario identityとして保ち、fixture / test IDとは分けます。fixtureのPASS / FAILによってSCNそのものの意味を変更しません。

Scenarioの一部だけを検証した場合は`Partially Satisfied`とし、Scenario全体の実装完了へ読み替えません。

SCN-0005 / SCN-0015では、portable Cognitive Method Contractとtyped runtimeが成立していても、Method execution、production Realization交換、TEI Pattern catalog / Pattern matching、Method品質やAssuranceまで検証済みとは扱いません。

SCN-0018では、既存のcomponent-level PASSを合算してend-to-end PASSとみなしません。今回のEvidenceは、Cognitive Method、Recommendation、Decision、Provider / execution result、historical review / reopen、Projection非権威を一つの検査経路として接続したfixture-scoped Evidenceです。production Product Journeyや利用者成果への昇格は行いません。

SCN-0019では、probe sourceやtest sourceの存在をactual Executable Evidenceへ読み替えない。fault injectionとstale snapshot behaviorを実際に実行し、その結果をcurrent Evidenceとして固定した後にだけExecutable statusを更新する。

## 5. Historical Scenarioとの関係

2026-08-30 candidateの`SEI-AS-001`〜`SEI-AS-008`は、意味核をSCN-0001〜SCN-0008へ継承しました。

旧IDはhistorical provenanceとして`history/HISTORICAL_REQUIREMENT_MAPPING.md`に残し、current SCN identityには用いません。

SCN-0018は、historical Scenarioの単純な再採番ではなく、current Product ShapeとREQ-0001〜REQ-0022を横断して定義したcurrent統合Scenarioです。

SCN-0019もhistorical Scenarioの再採番ではない。ISSUE-000073のresume-first Product Sliceでpartial semantic commitとstale draftをfaultとして具体化した結果、successful canonical commitの整合性を独立して検査する必要が確認されたため追加したcurrent Scenarioです。

## 6. Natural Japanese review

SCN-0001〜0019をcurrent Product Value、Product Shape、`PRODUCT_JOURNEY_COMPOSITION.md`、5 Contract family、Representation Profile、semantic runtime、synthetic Provider Adapter、V6/V7 Projection evaluation、end-to-end Product Journey harness、ISSUE-000073 Candidate Requirement監査とinteraction probe sourceへ照合した。

SCN-0019はStorage transaction方式を固定するScenarioではなく、Product Interactionがsuccessful commitとして公開するcanonical meaningがpartial / stale stateにならないことだけを要求する。concurrency versionとSemantic Revisionの境界、commit failureとbusiness negative factの境界も維持した。probe / test sourceの存在はactual Executable PASSへ昇格させず、採用時点のExecutable Evidenceは`Not Yet Verified`に留めている。

既存Scenarioについてもcomponent-level / fixture-scoped Evidenceをproductionのend-to-end Product Acceptanceへ昇格させず、Release / Operational / Adoption / Outcomeを必要以上に引き上げていない。その後、Scenarioの意味、期待、失敗条件、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再監査した。
