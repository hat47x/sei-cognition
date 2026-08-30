# ISSUE-000019: Reference ModelとCognitive Methodの境界を整理する

Status: **Open**  
Priority: **4**  
Related ADRs: **ADR-0014**  
Updated: 2026-08-31

## Goal

渡辺幸三系のReference Model、Pattern Card、典型業務知識を、TEIのDesign Knowledge、SOZAのCognitive Method、単なるhistorical referenceのどこへ位置付けるかを整理する。

## Background

初期X-TEAではReference Modelが設計の出発点として強い役割を持っていた。

後発議論では、Reference Modelを正解テンプレートとして適用するのではなく、既存Patternや候補を探索する知識として使い、Analyzer / Simulator / AIによって対象へ適合するかを確認する方向へ修正された。

一方、SOZAはCognitive Method Definition / Realization / Applicationの意味境界を耐久的な中心候補として持つ。

このため、Reference Modelの一部が「設計対象について何を問い、どう検査するか」というMethodとしてSOZA側に現れる可能性がある。ただし、具体的な業務Schemaや画面TemplateまでSOZAへ移すべきではない。

## Questions

1. Reference Modelのうち、業務domain固有のPatternはTEI Design Knowledgeに留めるべきか。
2. 「どの順で何を確認するか」という探索・検証手続きはSOZA Cognitive Methodとして表せるか。
3. Pattern CardとMethod Definitionをどう区別するか。
4. Reference Modelを使った事実と、Reference Modelに適合したという判断をどう記録するか。
5. AIがReference Modelを候補探索に使った場合、その利用をMethod Applicationとして残す必要があるか。
6. Reference Modelを更新しても、過去設計Decisionを当時の版で再構成できるか。
7. X-TEA historical assetをTEI現行Productの正本と誤解させないため、provenanceをどう表すか。
8. cultural-substrate-weavingやKJ法と同様に、Reference Modelを「対象へ押し付けない認知場」として扱える部分と、domain constraintとして扱う部分をどう分けるか。

## Constraints

- Reference Modelを正解テンプレートとして自動適用しない。
- domain固有SchemaをSOZA Universal Coreへ移さない。
- Patternとの一致をRequirementやDecisionの根拠へ自動昇格させない。
- historical X-TEA artifactを現行TEI canonical definitionと同一視しない。
- Method利用とMethodが正しかったことを同一視しない。

## Required scenarios

1. Reference Modelから履歴管理Patternを候補提示する。
2. Patternを採用せず、別設計をDecisionする。
3. Patternの一部だけを利用する。
4. 後にReference Modelが改訂されても過去Decisionを再構成する。
5. TEI Editor以外のclientが同じCognitive Methodを利用する。
6. AIがPattern候補を提示し、人間が別案を採る。
7. historical X-TEA artifactをprovenance付きで参照する。
8. Pattern CardとCognitive Methodを別Artifactとして扱う。

## Deliverables

- Reference Model / Pattern / Methodの比較表
- ownership boundary
- historical provenance rule
- acceptance fixtures
- ADR候補または「現時点では分離維持」の結論

## Source

`plan/kj/2026-08-31_TEI設計系列_ラウンドKJ統合.md` のG05を起点とする。

## Natural Japanese review

Issue作成後に自然な日本語の全文ドラフト工程を実施済み。Decision確定時にも再監査する。
