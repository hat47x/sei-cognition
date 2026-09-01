# First Product Interaction Reference Probe Evidence

更新日: 2026-09-01  
状態: **Scoped Executable Evidence**

## 1. この文書の役割

この文書は、`product/interaction/SOZA_PRODUCT_INTERACTION.md`とADR-0028で定めたfirst usable Product Interaction boundaryについて、`runtime/go/interactionprobe`で確認できた範囲を記録します。

今回の対象は、**人間向けと機械向けの異なるSurfaceが、同じcanonical sourceへ接続し、既存の意味差を失わずに読み書きできるか**という限定されたreference probeです。

production UI、正式API、MCP、Storage、認証、team collaboration、実利用上の使いやすさを実証するものではありません。

```text
interaction probe PASS
  != production UX proven
  != supported protocol finalized
  != packaged product proven
  != Operational Evidence
  != Adoption / Outcome Evidence
```

## 2. 実装したprobe

`runtime/go/interactionprobe`に、単一Inquiryを対象とするevaluation-onlyのprobeを実装しました。

構成は次のとおりです。

```text
HumanSurface ───┐
                ├─ CanonicalStore ─ existing semanticruntime records
MachineSurface ─┘
```

`CanonicalStore`はproduction Storageではありません。新しいUniversal Contractも定義しません。

既存Contractで表現できるrecordは、`semanticruntime.LoadStandalone`を通してcurrent validatorで再検証してから保持します。今回利用している主なtyped recordは次です。

- Decision Memory — Recommendation / Decision
- Capability Observation
- Cognitive Method — Method Application

一方、current typed runtimeで独立ContractがまだないInquiry、Unknown、Conflictは、既存のSemantic Interchange方針と同様に、opaqueな`not_verified` recordとして保持します。probeの都合で意味を理解したことにはしません。

## 3. human-oriented Surface

人間向けprobeでは、semantic Contractのfield名を直接入力しなくても、次の操作を行える形にしました。

- 短い文章からInquiryを開始する。
- Unknown / Conflictを追加する。
- machine側が追加したObservation / Recommendationをlight viewで読む。
- DecisionをRecommendationと分けて記録する。
- audit viewからbasis、Responsibility、未解決事項等へ降りる。

このSurfaceはproduction CLIの仕様ではありません。text / CLI相当の操作境界をGo APIとして最小限に表したreference probeです。

## 4. machine-oriented Surface

機械向けprobeでは、構造化された操作として次を実装しました。

- Capability Observationを追加する。
- Cognitive Method Applicationを追加する。
- Recommendationを追加する。
- canonical recordをstructured viewとして読む。
- human側が記録したDecisionをDecisionとして再読する。
- RecommendationをRecommendationとして再読する。

AI modelやagent runtimeは接続していません。したがって、「AIが実際にこのSurfaceを使いやすい」ことまでは検証していません。

## 5. canonical authorityの扱い

HumanSurfaceとMachineSurfaceは同じ`CanonicalStore`へ接続します。

Surfaceが持つ選択状態、cursor、tab等に相当するlocal stateはcanonical sourceへ保存しません。local stateを破棄してもcanonical digestが変わらないことをtestで確認します。

また、light view / audit view / structured viewはcanonical recordから都度生成します。Projection生成前後でcanonical digestが変化しないことを検査しています。

ここで使うdigestはprobe内部の比較用SHA-256であり、SOZAのRepresentation ProfileやExact Bindingではありません。

## 6. 確認したExecutable Evidence

Semantic Runtime Conformance Run `33504002579`で、current Contract fixtureの再検査と`runtime/go`全体の`go test ./...`がsuccessしました。このRunには、Surface-local stateだけに存在するRecommendation / Decision相当の情報をcanonical recordとして扱わないnegative testも含まれます。

`interactionprobe`では、少なくとも次をactual testとして確認しています。

### 6.1 Human / Machine間の意味共有

- HumanSurfaceが最小入力からInquiryを開始できる。
- MachineSurfaceが追加したCapability ObservationをHumanSurfaceから再読できる。
- MachineSurfaceが追加したRecommendationをHumanSurfaceから再読できる。
- HumanSurfaceが記録したDecisionをMachineSurfaceがDecisionとして再読できる。

### 6.2 Progressiveな詳細化

Inquiryだけの最小状態ではRecommendationやDecisionを要求せず、後からUnknown / Conflict、Observation、Method Application、Recommendation、Decisionを追加できます。

この結果は、production UX上の入力負担が十分に小さいことを示すものではありません。あくまで最小状態から後付けできるruntime構造を確認したものです。

### 6.3 Unknown / Conflictの保持

UnknownとConflictを空欄、false、latest-winsへ変換せず、別のopaque `not_verified` recordとして保持し、HumanSurfaceから再読できることを確認しました。

これはUnknown / Conflictのcurrent Universal Contractが完成したことを意味しません。むしろ、未対応意味を理解済みと偽らず保持できることのEvidenceです。

### 6.4 RecommendationとDecisionの分離

- RecommendationとDecisionを別typed recordとして保持する。
- Recommendationと同じlogical identityをDecisionへ再利用しようとした場合、canonical storeがduplicate recordとして拒否する。
- MachineSurfaceがhuman DecisionをRecommendationへ読み替えない。

### 6.5 light / audit / structured ProjectionとSurface-local stateの非権威性

- light viewを生成してもcanonical digestが変わらない。
- audit viewを生成してもcanonical digestが変わらない。
- Surface-local stateを設定・破棄してもcanonical digestが変わらない。
- audit viewからDecision basis、Responsibility、unresolved refsへ降りられる。
- chat履歴を模したlocal stateにRecommendation相当の文字列を置いても、canonical RecommendationとしてProjectionへ現れない。
- UI状態を模したlocal stateにDecision相当の文字列を置いても、canonical DecisionとしてProjectionへ現れない。

### 6.6 private reasoningへ依存しない

MachineSurfaceのRecommendation入力にはprivate chain-of-thoughtやreasoning transcriptを要求しません。

このprobeでは、Recommendation statement、必要なbasis、任意のrationale等だけでrecordを成立させています。

### 6.7 actor kindからResponsibilityを推定しない

MachineSurfaceからRecommendationを作成しても、Responsibilityを自動付与しません。Responsibilityは明示的に渡された場合だけcanonical recordへ入ります。

したがって、`machine surface == AI actor == responsibility holder`という推定をprobe runtimeは行いません。

### 6.8 実行後Observationによる過去Decision非改変

Decision作成後に新しいCapability Observationを追加しても、既存Decisionの`basis_refs`が変化しないことを確認しました。

SCN-0018 journey harnessで既に確認しているtemporal integrityを、Interaction Surface経由の追加操作でも壊さないことを限定的に再確認した形です。

### 6.9 opaque recordのEvidence強度

typed semantic documentを持たないopaque recordを`validated`として追加しようとすると拒否します。

```text
opaque retained
  != semantics understood
  != validated
```

未対応意味を保持することと、その意味を検証済みと主張することを分けています。

## 7. 既存runtimeとの重複監査

reference probeは、既存runtimeを置き換える第二のsemantic runtimeとして実装していません。

- typed validation — `semanticruntime.LoadStandalone`を再利用
- semantic record型 — `semanticruntime`の既存型を再利用
- end-to-end temporal integrityの考え方 — `journeyharness`の既存Evidenceと整合
- Projection非権威性 — V6 / V7 evaluationの既存方針と整合

`interactionprobe`が新たに担うのは、これら既存部品の上に**human-oriented / machine-oriented Surfaceを二つ載せ、同じcanonical sourceを操作する最小Product Interaction**を実証する範囲です。

## 8. 今回確認していないこと

次は未検証です。

- 実際のWeb / desktop / CLI UI
- 実AI modelからの呼び出し
- HTTP API / MCP / SDKのproduction protocol
- 複数Inquiryをまたぐworkspace管理
- production persistence
- process restart後のresume
- concurrent write / transaction
- login / authorization / tenant / collaboration
- production security
- human usability test
- latency / throughput / resource usage
- actual Provider / TEI integration
- Operational / Adoption / Outcome Evidence

特に、probeは単一Inquiry用のin-memory evaluation storeです。この制約をproduction productの仕様として一般化しません。

## 9. Requirement / Acceptance再監査

probe結果から、現時点で新しいstable Product RequirementやAcceptance Scenarioを追加する必要性は確認されませんでした。

今回の検査対象は、引き続き既存の次のRequirement / Scenarioで表現できます。

- REQ-0001 — 耐久的な意味の連続性
- REQ-0005 — Decisionの歴史的再構成
- REQ-0006 — 提案・判断・権限・実行の分離
- REQ-0010 — Progressive Semantic Explicitness
- REQ-0011 — Projectionを意味上の正本にしない
- REQ-0014 — 未解決残差と再開条件の保持
- REQ-0015 — private chain-of-thoughtへ依存しない
- REQ-0019 — 人間とAIの双方が意味を読める
- SCN-0013 — 簡略UIとcanonical meaningを両立する
- SCN-0018 — Inquiryから実行後の再検討までを一続きに扱う

したがって、Interaction probeの実装都合だけでREQ / SCNを追加しません。

## 10. PMS-03への反映

PMS-03について、Design Evidenceに加えて**scoped Executable Evidence available**と判断できます。

ただし、MilestoneのOutcomeに含まれる「最初のusable interaction」を実利用上十分なUXとして証明したわけではありません。今回確認したのは、二つの異なるSurfaceが同じcanonical sourceへ接続できるruntime境界です。

そのため、PMS-03は次のように読みます。

```text
Interaction boundary Design: established
reference probe Executable Evidence: available
production supported Surface: not decided
production usability: not verified
Operational / Adoption Evidence: not verified
```

## 11. CI Evidence

- Workflow: `Semantic Runtime Conformance`
- Run: `33504002579`
- Result: **success**
- Scope:
  - current Contract fixture再検査
  - `runtime/go`で`go test ./...`
  - Surface-local state negative caseを含む`interactionprobe`のcurrent Go runtime test

同じheadではPlan integrity Run `33504002562`も**success**し、ISSUE / ADR / registry integrityとDocument Review Registry coverageを確認しています。

CIのsuccessは、上記scopeに限ったEvidenceとして扱います。

## 12. Natural Japanese review

Product Interaction baseline、ADR-0028、ISSUE-000053、REQ-0001 / 0005 / 0006 / 0010 / 0011 / 0014 / 0015 / 0019、SCN-0013 / 0018、existing semanticruntime / journeyharness / V6-V7 Projection evaluation、Semantic Runtime Conformance Run `33504002579`、Plan integrity Run `33504002562`を照合しました。実装で確認したことと、production UI、Packaging、Operational / Adoptionとしてまだ確認していないことを分けています。また、probe固有のin-memory storeやSurface DTOをUniversal semantic modelへ昇格させていません。そのうえで、意味、Evidence強度、未検証範囲を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。