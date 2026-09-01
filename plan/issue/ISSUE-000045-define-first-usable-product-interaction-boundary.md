# ISSUE-000045: first usable Product Interaction boundaryを定義する

Status: **Resolved**  
Priority: **1**  
Related ADRs: **ADR-0005, ADR-0018, ADR-0020, ADR-0021, ADR-0028**  
Updated: 2026-09-01

## Goal

`SOZA_PRODUCT_SHAPE.md`で定めたWork / Interaction Surfaceについて、最初に利用可能な製品として**人間とAIがどの入口から同じcanonical meaningへ触れ、どの仕事を一続きに行える必要があるか**を定義する。

UI frameworkやprotocolを先に選ぶのではなく、Product Value、Requirement、Acceptance ScenarioからInteraction boundaryを定める。

## Resolution

first usable Product Interactionを、**既存のcanonical meaningへ対する利用者向けの論理操作境界**として定義した。

正本は`product/interaction/SOZA_PRODUCT_INTERACTION.md`とADR-0028である。

```text
Product Interaction
  = usable operations over canonical meaning
  != UI state
  != chat transcript
  != workflow state machine
```

人間向けSurfaceとAI向けSurfaceは異なるProjection / Adapterを持てる。一方、耐久的意味は同じcanonical artifactへ戻せなければならない。

## 利用者の仕事として定義した最小操作

first usable interactionでは、少なくとも次を自然につなげられることを求める。

1. 問い・目的・短い文脈から始める、または過去の判断を開き直す。
2. Observation / Evidenceを加える。
3. Unknown / Conflictを未解決のまま残す。
4. 必要な場合、Cognitive Method Applicationを記録する。
5. Recommendationを記録する。
6. DecisionをRecommendationと区別して記録する。
7. 外部実行後の結果を新しいObservationとして戻す。
8. light viewからaudit detailへ降り、過去を読み直して再開する。

これは固定workflowではなく、Product Interaction上の操作分類である。

## Human / AI / Projection / canonical authorityの境界

Human / AI parityを「同じUIを使うこと」とは定義しない。

```text
same UI
  is not required

same canonical meaning
  is required
```

人間向け画面、AI conversation、prompt context、CLI出力、worklist、canvas等はProjectionまたはInteraction Realizationとして扱う。それらの状態だけをDecision、Unknown / Conflict、basis、Responsibility、Provenance等の唯一の保持場所にはしない。

AI向けSurfaceはprivate chain-of-thoughtを要求せず、AIであることだけを理由にAuthority / Responsibilityを推定しない。

## 新しいUniversal概念を追加しない

first Interactionをまとめる都合だけで、`Case`、`Session`、`Workspace`、`Thread`等をUniversal Coreへ追加しない。

UI上の作業単位はworking setやProjection-local stateとして扱える。複数domainで独立したsemantic necessityが実証された場合だけ、Requirement / ADRへ戻って再検討する。

## Requirement / Acceptance監査

新しいProduct Requirementは追加しない。

Interaction boundaryに必要な主な意味は、既存の次のRequirementで表現できる。

- REQ-0001 — 技術やUIが変わっても意味を引き継ぐ。
- REQ-0005 — Decisionを後から再構成する。
- REQ-0006 — Recommendation / Decision / Authority / Executionを分ける。
- REQ-0010 — 低影響案件へ最大詳細を強制しない。
- REQ-0011 — Projectionを意味上の正本にしない。
- REQ-0014 — 残差と再開条件を保持する。
- REQ-0015 — private chain-of-thoughtへ依存しない。
- REQ-0019 — 人間とAIの双方が意味を読める。

Acceptanceについても、SCN-0013「簡略UIとcanonical meaningを両立する」とSCN-0018「Inquiryから実行後の再検討までを一続きに扱う」の組み合わせでDesign上の必要性を表現できる。

そのため、新しいREQ / SCN IDをこのIssueだけを理由に追加しない。後続probeで既存Scenarioでは表現できない失敗が確認された場合だけ再検討する。

## protocol / UI判断

Web UI、desktop UI、CLI、HTTP API、MCP等はproduction標準としてまだ固定しない。

後続のreference probeでは、human-orientedな簡素なtext / CLI相当の入口と、machine-orientedなJSON / process相当の入口を意図的に分け、同じinteraction core / canonical sourceへ接続できることを検査する。

このprobeはproduction UIやsupported protocolの選定ではない。

```text
reference probe surface
  != supported production surface decision
```

## Executable Evidence条件

PMS-03をExecutable Evidenceへ進めるため、後続probeでは少なくとも次を検査する。

1. human-oriented入口とmachine-oriented入口が同じcanonical sourceを利用する。
2. 最小入力から開始し、後から詳細化できる。
3. AI側が加えたObservation / Recommendationを、人間側が別Projectionから再読できる。
4. 人間側が記録したDecisionを、AI側がRecommendationへ読み替えない。
5. Unknown / Conflictを未入力、false、latest-winsへ平坦化しない。
6. light Projectionを削除・再生成してもcanonical sourceを変えない。
7. audit Projectionからbasis / provenance / responsibility等へ降りられる。
8. hidden reasoning transcriptなしで一連の操作を成立させる。
9. 実行後Observationを追加してもhistorical Decision basisを改変しない。
10. actor kindからAuthority / Responsibilityを推定しない。

実体化はISSUE-000053へ切り出す。

## Non-goals

- UIデザイン完成
- frontend framework選定
- production protocol確定
- 認証方式確定
- production Storage確定
- production SLA確定
- workflow engine実装
- AI agent orchestration engine実装

## 完了条件

- [x] Product Interactionの必須操作を利用者の仕事単位で定義する。
- [x] human / AI / projection / canonical authorityの境界を定義する。
- [x] 既存REQ / SCNとの重複監査を行う。
- [x] 必要なREQ / SCNだけを追加・更新する。監査結果として今回は追加しない。
- [x] Architecture DecisionをADR-0028として正本化する。
- [x] 最小interaction conformance / reference probeのExecutable Evidence条件を定義する。
- [x] probe実体化をISSUE-000053へ切り出す。
- [x] 自然な日本語全文再ドラフトと最終意味監査を行う。
- [ ] 対象CIをsuccessさせる。

CI success確認後、最後の項目をEvidenceとして同期する。

## Evidence state

- Design Evidence: **Satisfied** — Product Interaction baselineとADR-0028でboundaryを正本化した。
- Executable Evidence: **Not Yet Verified for first usable interaction** — ISSUE-000053で実証する。
- Release Evidence: **Not Yet Verified**
- Operational Evidence: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

current V6 / V7 Projection evaluationやSCN-0018 harnessに関連Executable Evidenceはあるが、first usable interactionへ自動昇格させない。

## Reopen条件

- reference probeで、Case / Session等の新しい耐久的semantic entityが不可欠と確認された。
- human / machine共通の操作境界では重要な意味差を保持できない。
- existing Requirement / Scenarioでは表現できない独立した失敗が確認された。
- Packaging / DeploymentまたはIdentity / Collaborationの設計から、現在のInteraction boundaryと両立しない必須条件が確認された。

## Natural Japanese review

Product Value、Product Shape、PMS-03、REQ-0001 / 0005 / 0006 / 0010 / 0011 / 0014 / 0015 / 0019、SCN-0013 / 0018、V6 / V7 Projection evaluation、end-to-end Semantic Product Journeyを照合し、UI技術ではなく利用者の仕事からInteraction boundaryを再構成した。画面、chat、session等を意味上の正本へ昇格させず、人間とAIが異なる入口から同じcanonical meaningへ戻れることを中心に据えた。そのうえで、新しいRequirementやUniversal概念を不要に追加せず、意味、規範強度、未決事項、Evidenceの高さを保ったまま、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。