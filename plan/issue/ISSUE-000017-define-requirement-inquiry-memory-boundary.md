# ISSUE-000017: Requirement Inquiryと判断履歴の所有境界を定める

Status: **Resolved**  
Priority: **2**  
Related ADRs: **ADR-0005, ADR-0010, ADR-0011, ADR-0014, ADR-0015**  
Updated: 2026-08-31

## Goal

AIが設計時に行う確認質問について、Stable Question ID、回答候補、利用者・組織の判断、後続Evidenceによる再審査を、SOZA Core、Cognitive Method、TEI Authoringのどこで扱うかを定める。

## Investigation

TEI設計系列の「一度した質問は聞き返さない」「回答履歴は後から追跡・変更できる」という要件を、SOZAのQuestion / Recommendation / Decision / Semantic Lineageへ戻してラウンドKJ法で検討した。

その結果、専用`RequirementDecision`型を追加しなくても、次の意味を既存境界で保持できると判断した。

- Questionのlogical identityと表示文を分離する。
- AIの回答候補はRecommendationとする。
- 利用者・組織の回答はDecisionとする。
- 同じ前提では既存Decisionを再利用する。
- 新Evidenceでは過去Decisionを上書きせず後継Decisionを作る。
- 質問catalogやtrigger logicはCognitive Method / TEI Design Knowledge / Authoring Profileへ置く。

## Resolution

ADR-0015をAcceptedとし、本IssueをResolvedとする。

Universal `DecisionImpact`型も現時点では追加せず、Question、basis、Derivation、Semantic Lineageで再審査理由を表す。独立Impact identityが複数domainで必要になった場合に再検討する。

## Natural Japanese review

KJ統合とADR-0015へ戻して内容を照合した後、自然な日本語となることを最重要視して全文を再ドラフトし、意味監査を実施済み。
