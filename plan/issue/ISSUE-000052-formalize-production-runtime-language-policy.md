# ISSUE-000052: production runtimeの実装言語方針を正式化する

Status: **Resolved**  
Priority: **1**  
Related ADRs: **ADR-0014, ADR-0021, ADR-0022, ADR-0025, ADR-0027**  
Updated: 2026-09-01

## Goal

SOZAで暗黙に混在していたGoとPythonの役割を整理し、SOZA自身が所有するproduction runtimeの標準実装言語と、Cognitive Method・Provider・評価・研究で許容する言語境界を正式化する。

関連製品TEIのactual implementationがGoであることも比較材料とするが、SOZA / TEI Product Boundaryを弱めず、単なる組織内統一を理由に言語を固定しない。

## 背景

current SOZAでは、`runtime/go/`配下にsemanticruntime、provideradapter、journeyharnessがあり、Goがすでに主要runtime realizationとして利用されている。一方、evaluationや開発補助ではPythonが残っている。

この状態を「PythonからGoへ全面移行する」と捉えると、AI / ML・Cognitive Method prototype・分析等でPythonが持つ強みまで失う。一方、production runtime言語を未定義のままにすると、Packaging / Deployment検討で言語・依存・配布方式が無秩序に増える可能性がある。

## Resolution

ADR-0027をAcceptedとし、次をcurrent方針とした。

1. SOZA自身のproduction runtimeとfirst-party reference implementationの標準言語はGoとする。
2. Semantic Contractはlanguage-neutralを維持する。
3. Cognitive Method / Capability Providerの実装言語は本方針で固定しない。
4. PythonはAI / ML研究、Cognitive Method prototype、evaluation、fixture生成、one-shot tooling等で正式に利用可能とする。
5. Python実装をproduction利用する場合、SOZA Coreへ直接同化する前にProvider / process / API等の境界で分離できるかを検討する。
6. TEIとのGo共通化は利点の一つだが、SOZAとTEIを同一runtimeや同一deployment unitへ結合する根拠にはしない。

## Requirement判断

新しいProduct Requirementは追加しない。

実装言語はcurrent Product Valueを実現するArchitecture / Realization上の選択であり、利用者世界の独立したsemantic obligationではない。GoでなければSOZAの意味が成立しないわけではなく、Contractのportable semanticsもGoへ依存させない。

したがって、今回の判断はADR / Architecture / Development Workflowへ反映し、Requirement体系へ言語名を持ち込まない。

## 反映対象

- ADR-0027 — Go production runtime language policy
- `architecture/IMPLEMENTATION_LANGUAGE_POLICY.md`
- `architecture/README.md`
- `plan/DEVELOPMENT_WORKFLOW.md`
- `plan/registry.yaml`
- `plan/document_review_registry.yaml`

Product Value、Value Model、Semantic Contract schemaは変更しない。

## Evidence state

- Design Evidence: **Satisfied** — current Product / Architecture / actual code配置とTEI actual repositoryを比較し、言語境界をADR-0027へ正本化した。
- Executable Evidence: **Partially Satisfied** — current Go runtime / journey harness等にはfixture-scoped Evidenceがある。ただし言語選定そのものの優越性をproduction比較実験で証明したものではない。
- Release Evidence: **Not Yet Verified by this Issue**
- Operational Evidence: **Not Yet Verified**
- Adoption / Outcome Evidence: **Not Yet Verified**

## 完了条件

- [x] current SOZAにおけるGo / Python利用実態を確認する。
- [x] TEI actual repositoryがGo moduleを持つことを比較材料として確認する。
- [x] Go標準化の対象範囲とPython許容範囲を分ける。
- [x] Product Requirementへ言語選択を持ち込まないことを確認する。
- [x] ADR-0027をAcceptedとして作成する。
- [x] Architecture / Development Workflowへ反映する。
- [x] registry / document review registryを同期する。
- [x] 自然な日本語全文再ドラフトと最終意味監査を行う。
- [x] 対象CIをsuccessさせる。

Plan integrity Run `33501380243`で、ADR / Issue / registry integrity、Document Review Registry coverageを含む対象検査が**success**した。

## Reopen条件

- production runtimeでPython固有ecosystemが不可欠となり、Provider / process境界では実用要件を満たせない。
- Go標準化がPackaging / Deployment / Operational Evidenceで継続的な不利益を生む。
- SOZAのProduct Shapeが大きく変わり、runtime自体の役割が現在の前提と異なる。
- 別言語がSOZA単独でも明確に優位であるEvidenceが蓄積する。

## Natural Japanese review

current runtime実体、Product Principles、SOZA / TEI境界、Cognitive MethodのRealization分離、Packaging / Deployment未決領域、Plan integrity Run `33501380243`を照合し、「全面Go化」ではなくproduction runtimeの標準化として問題を切り分けた。Pythonを研究・評価・外部Realizationから排除せず、Requirement体系へ実装言語を昇格させない境界を保ったまま、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。