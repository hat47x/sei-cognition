# ADR-0015: Requirement Inquiryに既存Question / Decision Memoryを再利用する

Status: **Accepted**  
Related Issue: **ISSUE-000017**  
Updated: 2026-08-31

## Context

業務システムの設計支援では、変更履歴、1:N関係、部分処理、承認、取消後履歴、時点依存等、意味に影響する曖昧性についてだけ控えめに確認し、一度回答した質問を同じ前提のまま無条件に繰り返さないUXが求められる。

この履歴をAuthoring clientのchat sessionだけへ置くと、sessionやUIが変わった時点で判断の来歴を失いやすい。一方で、質問dialog、表示文、dismiss状態までSOZA Coreへ持ち込むと、現在のUI実装が意味モデルへ固定されてしまう。

そこで、Questionの意味、AI等による回答候補、利用者・組織等のDecision、後日の再審査を分けて扱う。

## Decision

### 1. Universal `RequirementDecision`型を新設しない

Requirementに関する回答も、既存のQuestion、Recommendation、Decision、Responsibility、Semantic Lineageで扱う。

```text
Question
  → Recommendation?   # AI等が回答候補を提案した場合
  → Decision           # 採用・不採用・保留等の判断
```

Requirement固有の意味が必要な場合は、Profile / Method側のrelationやArtifact kindで補う。まず通常のDecisionと共通する意味を再利用する。

### 2. Questionのsemantic identityと表示文を分ける

同じ意味の質問を自然な日本語へ言い換えたり、UIごとに表示を変えたりしても、それだけで別Questionにはしない。

```text
Question semantic identity != presentation wording != chat turn
```

問いの対象、前提、意味が変わった場合は、別のlogical identityまたは明示的なSemantic Lineageとして扱う。

### 3. AI等が推定した回答はRecommendationとする

AIが「履歴管理が必要と思われる」等の回答候補を提示しても、それを利用者や組織のDecisionとして保存しない。

```text
AI answer proposal != Requirement Decision
```

誰または何がDecisionを担ったかは、Responsibilityの境界から表す。

### 4. 「一度した質問を聞き返さない」を永続的な禁止規則にしない

同じ前提・同じQuestionについて有効なDecisionを再利用できる場合は、Authoring clientが再質問を抑止してよい。

ただし、新しいEvidence、Constraint、対象変更等によって過去Decisionの前提が崩れた場合は、再審査できなければならない。

過去Decisionを削除・上書きせず、新しいDecisionを作りSemantic Lineageで結ぶ。

### 5. Universal `DecisionImpact`型も現時点では追加しない

「何が変わったため再審査が必要になったか」は、Question、Derivation、Decision basis / unresolved、Semantic Lineage等の組み合わせによって、まず表現する。

複数domainで独立したImpact Artifactが必要になるEvidenceが繰り返し得られた場合に再検討する。

### 6. Question catalog / trigger logicはMethod / Authoring側へ置く

典型業務でどの問いを候補提示するか、どの条件で確認modeへ入るか、どの日本語で表示するかは、Cognitive Method、domain-specific Design Knowledge、Authoring Profile等が所有できる。

SOZA Coreは、質問catalogやUI session lifecycleを所有しない。

## Current realization

current Decision Memory Contractとfirst semantic runtimeでは、RecommendationとDecision、basisとunresolved、Semantic Lineage等の基礎境界が実体化している。

一方、Question catalog、Authoring clientによる再質問抑止、Requirement Inquiry専用Profileまでをcurrent runtimeで完成したとは主張しない。本ADRは、それらを実装する際にDecision Memoryを再利用する意味上の方針を定める。

## Consequences

### Positive

- 「一度回答した質問を聞き返さない」というUXを、chat履歴だけではなくDecision Memoryへ接続できる。
- AI等の回答候補と、人間・組織その他の主体によるDecisionの責任線を保てる。
- 新しいEvidenceが得られたとき、過去回答を上書きせずに再審査できる。
- 特定のEditorに限定せず、複数のAuthoring clientから同じQuestion / Decision履歴を利用できる。
- Questionの表示文やUIを改善してもsemantic identityを維持しやすい。

### Costs

- Authoring clientは、現在のQuestionに対応する既存Decisionを解決する必要がある。
- Question semantic identityとpresentation templateを管理する境界が必要になる。
- 再審査を起動するtriggerはMethod / Profileごとに設計する必要がある。

## Revisit conditions

次のような不足が複数domainで繰り返し現れた場合に、専用型を再検討する。

- Requirementに関するDecisionだけに存在する普遍的意味が、通常Decisionでは表せない。
- 再審査理由をQuestion / basis / Derivation / Lineageで表すと意味が失われる。
- `DecisionImpact`自体に独立identity、Responsibility、Assurance、revisionが必要になる。

## Natural Japanese review

current Decision Memory、Question / Recommendation / Responsibility / Semantic Lineage境界へ戻ってDecisionを照合した。その後、検討手法や特定Editorの実装を正本にせず、Requirement Inquiryで長期に必要な意味とAuthoring側へ残すUXを分離した。意味を変えない範囲で自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。
