# ADR-0015: Requirement Inquiryに既存Question / Decision Memoryを再利用する

Status: **Accepted**  
Related Issue: **ISSUE-000017**  
Updated: 2026-08-31

## Context

TEIの設計支援では、変更履歴、1:N関係、部分処理、承認、取消後履歴、時点依存等、意味に影響する曖昧性だけをAIが控えめに確認し、一度回答した質問を無条件に繰り返さないUXが求められている。

この履歴をEditorのchat sessionだけへ置くと耐久性がない。一方、質問ダイアログ、表示文、dismiss状態までSOZA Coreへ持ち込むと、現在のAuthoring UIが意味モデルへ固定される。

ラウンドKJで、Questionの意味、AIの回答候補、利用者・組織の判断、後日の再審査を分けて検討した。

## Decision

### 1. Universal `RequirementDecision`型を新設しない

Requirementに関する回答も、既存のQuestion、Recommendation、Decision、Responsibility、Semantic Lineageで扱う。

```text
Question
  → Recommendation?   # AI等が回答候補を提案した場合
  → Decision           # 採用・不採用・保留等の判断
```

Requirement固有の意味が必要な場合はProfile / Method側のrelationやartifact kindで補う。まず通常Decisionとの共通部分を再利用する。

### 2. Questionのsemantic identityと表示文を分ける

同じ意味の質問を自然な日本語へ言い換えたりUIごとに表示を変えたりしても、それだけで別Questionにしない。

```text
Question semantic identity != presentation wording != chat turn
```

問いの対象・前提・意味が変わった場合は、別logical identityまたは明示的なSemantic Lineageとして扱う。

### 3. AIが推定した回答はRecommendationとする

AIが「履歴管理が必要と思われる」等の候補を出しても、それを利用者・組織のDecisionとして保存しない。

```text
AI answer proposal != Requirement Decision
```

誰がDecisionを担ったかはResponsibilityStatementで表す。

### 4. 「一度した質問を聞き返さない」を永続的禁止にしない

同じ前提・同じQuestionについて有効なDecisionを再利用できる場合は、Authoring clientが再質問を抑止してよい。

ただし、新しいEvidence、Constraint、対象変更等により過去Decisionの前提が崩れた場合は、再審査可能でなければならない。

過去Decisionを削除・上書きせず、新しいDecisionを作りSemantic Lineageで結ぶ。

### 5. Universal `DecisionImpact`型も現時点では追加しない

「何が変わったため再審査が必要になったか」は、Question、Derivation、Decision basis / unresolved、Semantic Lineage等の組み合わせでまず表現する。

複数domainで独立したImpact artifactが必要になる反復Evidenceが得られた場合に再検討する。

### 6. Question catalog / trigger logicはMethod / Authoring側へ置く

典型業務でどの問いを候補提示するか、どの条件で確認モードへ入るか、どの日本語で表示するかは、Cognitive Method、TEI Design Knowledge、Authoring Profile等が所有できる。

SOZA Coreは質問catalogやUI session lifecycleを所有しない。

## Consequences

### Positive

- 「一度回答した質問を聞き返さない」UXを、chat履歴ではなくDecision Memoryへ接続できる。
- AI候補と人間・組織Decisionの責任線を保てる。
- 新Evidenceで過去回答を上書きせず再審査できる。
- TEI Editor以外のAuthoring clientからも同じQuestion / Decision履歴を利用できる。
- Question wordingやUIを改善してもsemantic identityを維持できる。

### Costs

- Authoring clientは現在のQuestionに対応する既存Decisionを解決する必要がある。
- Question semantic identityとpresentation templateを管理する境界が必要になる。
- 再審査を起動するtriggerはMethod / Profileごとに設計する必要がある。

## Revisit conditions

次が複数domainで反復した場合に専用型を再検討する。

- Requirement Decisionだけに存在する普遍的意味が通常Decisionでは表せない。
- 再審査理由をQuestion / basis / Derivation / Lineageで表すと意味が失われる。
- `DecisionImpact`自体へ独立identity、Responsibility、Assurance、revisionが必要になる。

## Evidence

- `plan/kj/2026-08-31_RequirementInquiry_AuthorizationEvidence_ラウンドKJ.md`
- ADR-0003 / ADR-0005 / ADR-0010 / ADR-0011
- TEI設計系列の「一度した質問は聞き返さない」「回答履歴を後から追跡・変更できる」という要件

## Natural Japanese review

KJ統合と既存Decision Memory境界を確定した後、意味を変えず自然な日本語となることを最優先に全文を再ドラフトし、最終意味監査を実施済み。
