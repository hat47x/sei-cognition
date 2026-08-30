# ISSUE-000019: Reference ModelとCognitive Methodの境界を整理する

Status: **Resolved**  
Priority: **4**  
Related ADRs: **ADR-0014, ADR-0017**  
Updated: 2026-08-31

## Goal

渡辺幸三系のReference Model、Pattern Card、典型業務知識を、TEIのDesign Knowledge、SOZAのCognitive Method、historical referenceのどこへ位置付けるかを整理する。

## Background

初期X-TEAではReference Modelが設計の出発点として強い役割を持っていた。

後発議論では、Reference Modelを正解テンプレートとして適用するのではなく、既存Patternや候補を探索する知識として使い、Analyzer / Simulator / AIによって対象へ適合するかを確認する方向へ修正された。

一方、SOZAはCognitive Method Definition / Realization / Applicationの意味境界を耐久的な中心候補として持つ。

このため、Reference Modelの一部に含まれていた「設計対象について何を問い、どう検査するか」という手続きと、業務domain固有のPatternそのものを分ける必要があった。

## Questions reviewed

1. Reference Modelのうち、業務domain固有のPatternはTEI Design Knowledgeに留めるべきか。
2. 「どの順で何を確認するか」という探索・検証手続きはSOZA Cognitive Methodとして表せるか。
3. Pattern CardとMethod Definitionをどう区別するか。
4. Reference Modelを使った事実と、Reference Modelに適合したという判断をどう記録するか。
5. AIがReference Modelを候補探索に使った場合、その利用をどう来歴化するか。
6. Reference Modelを更新しても、過去設計Decisionを当時の版で再構成できるか。
7. X-TEA historical assetをTEI現行Productの正本と誤解させないため、provenanceをどう表すか。
8. Reference Modelを対象へ押し付けない探索資産として使う部分と、domain constraintとして扱う部分をどう分けるか。

## Resolution

ADR-0017で次をAccepted Decisionとして確定した。

### 1. Reference Model / Patternはdomain-specific Design Knowledgeへ置く

業務domain固有のReference Model、Pattern Card、典型Data / Workflow / Authorization構造等は、原則としてTEI Design Knowledgeまたはdomain-specific knowledge assetとして扱う。

それらをSOZA Universal Coreの型体系へ移さない。

### 2. Cognitive Methodは探索・比較・統合・検査の手続きを表す

SOZA側のCognitive Methodは、どの資料やPattern候補を探索し、何を比較し、どの反例・境界・残差を確認し、どのように統合・検証するかという手続きを表し得る。

```text
Reference Model / Pattern != Cognitive Method
```

### 3. Pattern matchとMethod ApplicationをDecision / Assuranceへ自動昇格させない

```text
Pattern match != Recommendation != Decision
Method Application != conclusion truth != Assurance
```

AIやMethodがPatternを候補として提示したことと、対象へ採用するDecisionは別に扱う。

### 4. historical Reference / Patternは必要に応じてexact-bindする

重要なDecisionで特定版のReference ModelやPatternがbasisになった場合、後から現在版へ差し替えず、当時参照した内容を特定できるようにする。

X-TEA由来のReference Modelは、設計系譜のprovenanceを保持するが、現行TEI Productの絶対的正本とはみなさない。

## Required scenarios disposition

1. Reference Modelから履歴管理Patternを候補提示する。→ Pattern候補として扱い、Decisionとは分離する。
2. Patternを採用せず、別設計をDecisionする。→ ADR-0017で許容・想定する。
3. Patternの一部だけを利用する。→ Patternの全面適用を要求しない。
4. 後にReference Modelが改訂されても過去Decisionを再構成する。→ exact historical referenceで扱う。
5. TEI Editor以外のclientが同じCognitive Methodを利用する。→ MethodをTEI UIへ固定しない。
6. AIがPattern候補を提示し、人間が別案を採る。→ Recommendation / Decisionを分離する。
7. historical X-TEA artifactをprovenance付きで参照する。→ historical provenanceとして保持する。
8. Pattern CardとCognitive Methodを別Artifactとして扱う。→ 所有境界を分離する。

## Deliverables

- [x] Reference Model / Pattern / Methodの意味境界
- [x] ownership boundary
- [x] historical provenance rule
- [x] Pattern match / Method Applicationの非自動昇格規則
- [x] ADR-0017 Accepted

具体的なTEI Design Knowledgeのcatalog schemaやUI、Pattern fixtureはTEI側または将来のdomain-specific設計課題として扱う。このIssueではSOZAの境界判断を完了条件とする。

## Reopen conditions

次の場合にのみ再開する。

- 複数domainでPatternそのものにSOZA共通のstable identity / revision / responsibilityが必要となり、domain-specific knowledge assetでは意味を保てないことが実証される。
- Cognitive MethodとPatternを分離したことで、重要な実案件の来歴を再構成できないことが繰り返し確認される。

## Source

- `plan/kj/2026-08-31_TEI設計系列_ラウンドKJ統合.md`
- `plan/kj/2026-08-31_ReferenceModel_CapabilityObservation_ラウンドKJ.md`
- ADR-0017

## Natural Japanese review

ADR-0017のDecisionとRequired scenariosへ戻してResolutionを確定した後、意味、強度、留保を変えず、自然な日本語となることを最重要視して全文を再ドラフトした。その後、最終意味監査を実施済み。
