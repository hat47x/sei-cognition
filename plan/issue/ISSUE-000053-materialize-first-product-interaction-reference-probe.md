# ISSUE-000053: first Product Interaction reference probeを実体化する

Status: **Open**  
Priority: **1**  
Related ADRs: **ADR-0005, ADR-0018, ADR-0020, ADR-0021, ADR-0028**  
Updated: 2026-09-01

## Goal

`product/interaction/SOZA_PRODUCT_INTERACTION.md`とADR-0028で定めたfirst usable Product Interaction boundaryについて、human-oriented入口とmachine-oriented入口が**同じcanonical meaningを失わずに扱えること**をreference probeで検証する。

このprobeはproduction UIやsupported protocolを決定するものではない。PMS-03をDesign EvidenceからExecutable Evidenceへ進めるための限定実験として扱う。

## 背景

current SOZAには、Semantic Contract、Go semantic runtime、V6 / V7 Projection evaluation、end-to-end Semantic Product Journey harnessがある。しかし、人間とAIが異なる入口から同じ判断文脈を読み書きするProduct Interaction自体はまだ実証していない。

Product Interaction baselineでは、UI、chat、session、workspaceをcanonical authorityにせず、既存のInquiry、Observation、Unknown / Conflict、Cognitive Method Application、Recommendation、Decision等へ戻る操作境界を採用した。

次に必要なのは、具体的なUIを作り込むことではなく、この境界が実装可能であり、異なるSurface間でも意味が保たれることを小さく確認することである。

## Probe方針

最初のprobeでは、少なくとも二つの入口を分ける。

### human-oriented probe

人間が型名やJSON fieldを直接編集しなくても、次を行える簡素なtext / CLI相当の入口を用意する。

- 最小入力から開始する。
- 現在の主要点をlight viewで読む。
- Observation / Unknown / Conflict等を加える。
- Recommendation / Decisionを区別して扱う。
- 必要なときだけaudit detailへ降りる。
- 過去を読み直し、再開する。

### machine-oriented probe

AIやtoolが構造化された操作を行えるJSON / process相当の入口を用意する。

- canonical referenceを含むcontextを取得する。
- 追加する意味種別を明示する。
- Observation / Method Application / Recommendation等を追加する。
- DecisionをRecommendationへ読み替えずに取得する。
- private chain-of-thoughtを送信しなくても操作できる。

いずれも同じinteraction core / canonical sourceへ接続する。

```text
human-oriented probe ─┐
                      ├─ interaction core ─ canonical meaning
machine-oriented probe┘
```

## 実装方針

current production runtime language policyに従い、SOZA自身が所有するreference probe coreはGoを基本とする。

ただし、probeの目的はGoの優位性を示すことではない。Surfaceとcanonical meaningの分離を検証することが目的である。

既存`runtime/go/semanticruntime`、`journeyharness`、Projection evaluationを再利用できる範囲を先に確認し、同じ意味を別実装で重複して持たない。

## 必須検査

少なくとも次をExecutable Evidenceとして検査する。

1. 二つの入口が同じcanonical sourceを利用する。
2. 人間側が最小入力から作業を開始し、後から詳細化できる。
3. machine側が追加したObservation / Recommendationをhuman側が再読できる。
4. human側が記録したDecisionをmachine側がDecisionとして取得できる。
5. RecommendationとDecisionを同じrecordへ平坦化しない。
6. Unknown / Conflictを未入力、false、latest-winsへ平坦化しない。
7. light Projectionを再生成してもcanonical sourceが変化しない。
8. audit Projectionからbasis / provenance / responsibility等へ降りられる。
9. private chain-of-thoughtを保存しなくても操作が成立する。
10. 実行後Observationを追加してもhistorical Decision basisを改変しない。
11. actor kindからAuthority / Responsibilityを自動推定しない。
12. human / machine Surface固有stateを削除してもcanonical artifactを失わない。

## Negative cases

少なくとも次を失敗として検出する。

- chat transcriptだけにRecommendationを保持し、canonical sourceへ戻さない。
- human UIの表示状態だけにDecisionを保持する。
- machine側がDecisionをRecommendationとして書き戻す。
- light viewに表示されないUnknownをcanonical sourceからも削除する。
- AI actorであることを理由にAuthorityを自動付与する。
- 実行後Observationを過去Decisionのbasisへ遡及追加する。

## Requirement / Scenario判断

probe開始時点では新しいProduct RequirementやAcceptance Scenarioを追加しない。

REQ-0001 / 0005 / 0006 / 0010 / 0011 / 0014 / 0015 / 0019と、SCN-0013 / SCN-0018を検査軸として利用する。

probeで、既存REQ / SCNでは表現できない独立した失敗・必要性が確認された場合に限り、Candidate Requirement / Scenarioとして上流監査へ戻す。

## Non-goals

- production Web UIの完成
- desktop framework選定
- HTTP API / MCPの正式標準化
- login / tenant / workspace設計
- production Storage選定
- agent orchestration
- workflow engine
- UXのOperational / Adoption Outcome証明

## 完了条件

- [ ] human-oriented probeを実体化する。
- [ ] machine-oriented probeを実体化する。
- [ ] 両Surfaceを同じinteraction core / canonical sourceへ接続する。
- [ ] 必須検査とnegative caseをactual testへ落とす。
- [ ] current semantic runtime / journey harness / Projection evaluationとの重複を監査する。
- [ ] CIで再現可能なExecutable Evidenceを得る。
- [ ] Product Interaction / PMS-03 / Evidence文書へ結果を同期する。
- [ ] Requirement / SCN追加の要否をprobe結果から再監査する。
- [ ] 自然な日本語全文再ドラフトと最終意味監査を行う。
- [ ] 対象CIをsuccessさせる。

## Evidence state

- Design Evidence: **Satisfied for probe plan**
- Executable Evidence: **Not Yet Verified**
- Release Evidence: **Not Yet Verified**
- Operational Evidence: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

## Reopen / escalation条件

本Issue実行中に次が確認された場合は、単なるprobe実装で押し切らず上流へ戻す。

- Case / Session等の新しい耐久的semantic entityがないと意味を保持できない。
- human / machine共通の操作境界では重要な意味差を表現できない。
- existing Semantic Contractに不足があり、Interactionだけでは解決できない。
- Packaging / DeploymentまたはIdentity / Authorizationの未決事項がprobe成立を阻害する。

## Natural Japanese review

Product Interaction baseline、ADR-0028、PMS-03、current Go runtime、V6 / V7 Projection evaluation、SCN-0018 Product Journeyを照合し、production UI選定ではなくSurface交換可能性とcanonical meaning保持を検証するreference probeとして作業を切り出しました。既存Requirement / Scenarioを先に再利用し、probeの都合だけで新しいUniversal概念やstable Requirementを追加しない境界を保っています。そのうえで、目的、検査条件、非対象、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。