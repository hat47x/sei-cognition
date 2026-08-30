# ISSUE-000017: Requirement Inquiryと判断履歴の所有境界を定める

Status: **Open**  
Priority: **2**  
Related ADRs: **ADR-0005, ADR-0010, ADR-0011, ADR-0014**  
Updated: 2026-08-31

## Goal

設計時にAIが行う確認質問について、Stable Question ID、回答履歴、Requirement Decision、後続EvidenceによるDecision Impactを、SOZA Core、Cognitive Method、TEI Authoring Profileのどこで扱うべきかを定める。

## Background

「渡辺幸三の業務システム設計」系列では、AIが典型的な業務要件を控えめに確認し、一度回答された質問を無条件に繰り返さないUXが重要とされた。

想定された問いには、たとえば次がある。

- 変更履歴を残すか。
- 1:N関係で本当に十分か。
- 部分処理を許すか。
- 誰が承認するか。
- 取消後の履歴をどう扱うか。
- 時点によって有効な値が変わるか。

この設計は、単なるEditor UXではなく、Question、Decision、Revision、Evidenceと関係する。

一方、すべての確認質問をSOZA Universal Coreへ入れると、特定Editorの対話状態や質問テンプレートをCore化する危険がある。

## Questions

1. Stable Question IDはUniversal `Question`のlogical identityで足りるか。
2. 「この設計問いには既に回答した」という状態はDecision Memoryか、Authoring Profileのsession memoryか。
3. Requirement Decisionを通常のDecision Artifactとして扱えるか。
4. 設計者の回答と、AIが推定した回答候補をどう分けるか。
5. 新Evidenceと旧回答が衝突したとき、再質問ではなくDecision Impactをどう表現するか。
6. 一度回答した質問を聞き返さない原則と、前提変更時に再確認する必要をどう両立するか。
7. 質問catalogや典型業務パターンはSOZA Cognitive Method、TEI Design Knowledge、Reference Modelのどこに置くか。
8. UI session、chat turn、model-specific promptをdurable identityへ混ぜないために何を分離するか。

## Constraints

- AIの会話履歴そのものをSemantic Coreへ保存しない。
- private chain-of-thoughtを要求しない。
- 質問に答えたことをAuthorityとみなさない。
- AIが推定した回答を利用者のDecisionとして保存しない。
- 「一度聞いたら永久に聞かない」と固定しない。前提変更時の再審査経路を持つ。
- Question templateの文言変更をsemantic identity変更と自動的に同一視しない。
- TEI Editor固有UXをSOZA Coreへ持ち込まない。

## Required scenarios

最低でも次を比較する。

1. 初回設計で履歴要否を質問し、回答する。
2. 同じ前提のまま再編集し、同じ質問を抑止する。
3. 新しい法令・業務条件により過去回答が疑わしくなる。
4. 同じQuestionに対しDecisionをrevisionする。
5. AIが回答候補を提案するが、人間が異なるDecisionを行う。
6. TEI以外のAuthoring clientから同じRequirement Decisionを参照する。
7. Question wordingを改善しても、意味上は同じ問いとして扱う。
8. 意味上異なる問いへ分岐した場合は新しいlogical identityを持つ。

## Deliverables

- Requirement Inquiry semantic boundary
- Stable Question IDの扱い
- Requirement Decisionと通常Decisionの関係
- Decision Impact / reopen semantics
- TEI Authoring Profileとの境界
- acceptance fixtures
- ADR候補

## Source

`plan/kj/2026-08-31_TEI設計系列_ラウンドKJ統合.md` のG01を起点とする。

## Natural Japanese review

Issue作成後に自然な日本語の全文ドラフト工程を実施済み。今後、Decisionが確定した際にも再度実施する。
