# ADR-0028: Product Interactionをcanonical meaning上の操作境界として定義する

Status: **Accepted**  
Related Issue: **ISSUE-000045**  
Updated: 2026-09-01

## Context

SEIはProduct ShapeとしてWork / Interaction Surfaceを持ち、人間とAIが同じcanonical meaningへ触れられることを目指しています。一方、具体的なWeb UI、desktop UI、CLI、HTTP API、MCP等はまだ確定していません。

この段階で画面、会話、workspace、session等を先に正本化すると、現在のUIやAI integrationの都合がSEIの耐久的意味へ入り込みます。逆に、Interactionを「Semantic Contractを直接編集するだけ」と捉えると、利用者が型名やfield setを理解しなければ使えない製品になり、V6 Human / AI ReadabilityとV7 Progressive Explicitnessを損ないます。

必要なのは、UIやprotocolを交換しても残るProduct Interaction上の仕事を定義し、それらを既存のcanonical artifactへ接続する境界です。

current Requirementsでは、REQ-0010が最大詳細の一律強制を避け、REQ-0011がProjectionの非権威性を求め、REQ-0019が人間とAIの双方から意味を読めることを求めています。REQ-0001 / 0005 / 0006 / 0014 / 0015も、Interactionで失ってはならない意味差を既に定めています。

## Decision

first usable Product Interactionを、**既存のcanonical meaningへ対する利用者向けの論理操作境界**として定義します。

```text
Product Interaction
  = usable operations over canonical meaning
  != UI state
  != chat transcript
  != workflow state machine
```

人間向けSurfaceとAI向けSurfaceは異なるProjection / Adapterを持てますが、耐久的意味は同じcanonical artifactへ戻せなければなりません。

### 1. UI / conversationをcanonical authorityにしない

Web画面、desktop UI、CLI出力、AI conversation、prompt context、canvas、worklist等はInteractionのRealizationまたはProjectionとして扱います。

それらを削除・再生成しても、Decision、Unknown / Conflict、basis、Provenance、Responsibility、Lineage等の耐久的意味を失わない設計を標準とします。

### 2. 新しいUniversalなCase / Session / Workspace型を追加しない

first Interactionをまとめるためだけに、`Case`、`Session`、`Workspace`、`Thread`等をUniversal Coreへ追加しません。

UI上の作業単位はworking setやProjection-local stateとして持てます。複数domainで独立したsemantic necessityが実証された場合だけ、Requirement / ADRを通して再検討します。

### 3. 利用者の仕事をSurfaceへ露出する

Surfaceは、少なくとも次の仕事を自然に扱えることを目指します。

- 始める・開く。
- Observation / Evidenceを加える。
- Unknown / Conflictを残す。
- Cognitive Method Applicationを記録する。
- Recommendationを記録する。
- Decisionを記録する。
- 実行後のObservationを戻す。
- 過去を読み直し、再開する。

これらは固定workflowではありません。利用者が必要な順序・組み合わせで使えるProduct Interaction上の操作分類です。

### 4. Human / AI parityを「同じ意味へ戻れること」と定義する

人間とAIへ同一UIを要求しません。

Human / AI parityは、両者が異なる入口からでも同じcanonical artifactを参照でき、一方が残した耐久的意味を他方が読み直せることを意味します。

```text
same UI
  is not required

same canonical meaning
  is required
```

AI向けSurfaceはprivate chain-of-thoughtを要求せず、actor kindからAuthority / Responsibilityを自動推定しません。

### 5. light / auditを同じcanonical sourceから派生させる

低影響な日常利用ではlight Projectionを許容し、必要な場合だけaudit detailへ降ります。

light Projectionの簡略化をcanonical storageの欠落として実装せず、audit viewを別の正本にも置きません。

### 6. protocolはまだ固定しない

Web / desktop / CLI、HTTP API / MCP / SDK等の具体選択は本ADRで固定しません。

後続のreference probeでは、human-orientedな簡素な入口とmachine-orientedな構造化入口を意図的に分け、同じinteraction coreへ接続できることを検査します。このprobeのSurfaceをproduction標準とみなしません。

## Alternatives considered

### Chat-firstでconversationを作業の正本とする

自然なInteractionを作りやすい利点がありますが、conversation順序、context window、model固有履歴がDecisionやEvidenceの唯一の保持場所になると、AIやUIを交換した後のhistorical reconstructionが難しくなります。

chatは有力なProjection / Interaction Realizationですが、canonical authorityにはしません。

### Workspace / Caseを新しいUniversal Core型として追加する

UI実装は整理しやすくなりますが、現時点ではそれらが判断意味としてProviderやdomainを越えて不可欠であるEvidenceがありません。Product convenienceからUniversal ontologyへ昇格させることを避けます。

### Semantic Contractを直接操作させる

実装は単純ですが、人間側に型・fieldの知識を要求し、Progressive Explicitnessを損ないやすくなります。AIについてもContract表現そのものと利用者の仕事を同一視する必要はありません。

### Web UIとHTTP APIを最初から標準化する

一般的な構成ですが、Packaging / Deployment、human usability、AI integrationの実証前にprotocolを固定する理由が不足しています。本ADRでは操作境界だけを先に固定します。

## Consequences

### Positive

- UI、AI model、protocolを交換してもInteractionの意味を保ちやすい。
- Product InteractionからUniversal Core概念を不用意に増やさずに済む。
- 人間向けには自然な仕事の言葉を使い、AI向けには構造化Surfaceを用意できる。
- REQ-0010 / 0011 / 0019を一つのProduct Surfaceで整合させやすい。
- light / audit Projectionを既存V6 / V7評価と接続しやすい。
- first interaction probeをproduction UI選定から切り離して実証できる。

### Costs / Risks

- Interaction operationとcanonical artifact mappingの設計が必要になる。
- UI固有の便利な状態とcanonical stateの境界を実装時に明示し続ける必要がある。
- 人間向けとAI向けのSurfaceが異なるため、両方が同じ意味を保つconformanceが必要になる。
- protocol決定を先送りするため、PMS-03のDesign Evidenceだけでは製品UIの使いやすさを主張できない。

## Revisit conditions

次のEvidenceが得られた場合、本Decisionを再検討します。

- Case / Workspace等に、Projection convenienceでは説明できない独立した耐久的semantic necessityが複数domainで確認された。
- UI / conversationをcanonical authorityにしない構成では、主要なProduct Valueを実用上満たせないことが実証された。
- human / AIで共通の操作境界を持つことが、実装・運用上かえって意味の誤読を増やすEvidenceが得られた。
- Packaging / DeploymentやIdentity / Collaborationの設計から、現在のInteraction boundaryと両立しない必須条件が確認された。

## Evidence

### Design Evidence

- SEI Product Value / Product Shape
- PMS-03 first usable Product Interaction
- REQ-0001 / 0005 / 0006 / 0010 / 0011 / 0014 / 0015 / 0019
- SCN-0013 / SCN-0018
- V6 / V7 Projection evaluation
- end-to-end Semantic Product Journey harness
- `product/interaction/SEI_PRODUCT_INTERACTION.md`

### Executable Evidence

current Projection evaluationとSemantic Product Journeyには関連するscoped Executable Evidenceがありますが、本ADRで定めたhuman-oriented / machine-oriented Interaction parity自体はまだ実証していません。

```text
current projection / journey PASS
  != first usable interaction proven
```

Release / Operational / Adoption・Outcome Evidenceは`Not Yet Verified`です。

## Follow-up

- ISSUE-000053でfirst Product Interaction reference probeを実体化する。
- probeではhuman-oriented入口とmachine-oriented入口を同じcanonical sourceへ接続する。
- probe結果から、既存REQ / SCNでは表現できない意味差が確認された場合だけRequirement / Acceptance Scenario追加を再検討する。
- productionのsupported surface選定はprobeとISSUE-000046 Packaging / Deploymentの結果を踏まえて判断する。

## Natural Japanese review

Product Value、Product Shape、PMS-03、REQ-0010 / 0011 / 0019、SCN-0013 / 0018、current Projection evaluationとProduct Journeyを照合し、UIやchatを先に固定せず、利用者の仕事からcanonical meaningへ戻る操作境界としてDecisionを組み立てました。Case / Session等を現在の都合だけでUniversal Coreへ追加せず、human / AI parityを同一UIではなく同一意味への到達可能性として定義しています。そのうえで、Decision、非同一性、未決事項、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みです。