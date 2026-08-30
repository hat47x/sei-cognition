# ISSUE-000016: SOZAとTEIのProduct Boundaryを正式化する

Status: **Resolved**  
Priority: **1**  
Related ADRs: **ADR-0014**  
Updated: 2026-08-31

## Goal

SOZAとTEIの役割分担を、関連製品同士の慣習的な説明ではなく、Product ValueとArchitectureへ影響する正式な境界として定義する。

## Background

過去の「渡辺幸三の業務システム設計」系列では、TEIが次第に、画面生成中心のローコード基盤から、業務上の意味を実装技術から分離し、Application / Database / Provider / Deploymentへ追跡可能に落とす基盤として再定義された。

一方SOZA側では、workflowやagent runtimeを恒久的中心とせず、Inquiry、Epistemics、Cognitive Method、Recommendation、Decision、Responsibility、Capability等の認知・意思決定意味を中心に置く再基線化が進んだ。

両者は強く関連するが、境界を曖昧にすると次の問題が起きる。

- SOZAがTEI固有のApplication / Database / Deployment lifecycleをCoreへ吸収する。
- TEIがSOZAのDecisionやAuthorityを暗黙に代行する。
- TEIが関連製品であるという理由だけでCapability選択時に優遇される。
- repository、release、evidenceの状態が相互に混同される。
- SOZAの実装不足をTEI実装の存在で補完したことにしてしまう。

## Investigation

指定された7チャット、SOZA既存基線、現行`hat47x/tei-platform`をラウンドKJ法で統合した。

最終的に、次の境界が独立資料から反復して支持された。

```text
SOZA
  Inquiry / Epistemics / Cognitive Method
  Recommendation / Decision / Responsibility
  Capability discovery / choice memory

          explicit provider boundary
                    ↓

TEI
  business semantic authoring / canonicalization
  realization / binding
  Application / Database / Query
  deployment / execution / observation
```

ただし、実際の利用ではTEIからObservation / EvidenceをSOZAへ戻し、次のInquiry / Decision revisionを起動できる。

## Resolution

ADR-0014でSOZAとTEIの正式なProduct BoundaryをAcceptedとする。

## Acceptance criteria

- SOZA Product文書でTEIをCapability Providerの一つとして説明できる。
- TEIのApplication / Database / Runtime概念をSOZA Universal Coreへコピーしない。
- TEIがSOZA Decision / Authorityを暗黙に持たない。
- SOZAはTEI以外のProviderを同じCapability判断面で扱える。
- TEIはSOZAなしでもTEI自身のProduct Boundary内で動作可能である。
- SOZAもTEIなしで他Providerを選べる。
- Observation / Evidenceの戻り経路は認めるが、execution stateをTruthへ自動昇格させない。
- release / verification / operational evidenceはrepositoryごとに分離する。

## Result

ADR-0014へ判断を移し、本IssueをResolvedとする。

## Natural Japanese review

論点と判断を固定した後、意味を変えず自然な日本語となることを最優先に全文を再ドラフトし、最終意味監査を実施済み。
