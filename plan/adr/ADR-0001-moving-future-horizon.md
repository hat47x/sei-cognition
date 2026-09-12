# ADR-0001: 評価時点から動く将来基準でCore候補を見直す

Status: **Accepted**  
Related Issue: **ISSUE-000001**  
Updated: 2026-08-31

## Context

SEIでは、現在のAIや実装技術の弱点を補うためだけの仕組みを、恒久的なCoreへ固定しないことが重要である。一方で、遠い未来を想像するあまり、現在の実務で必要な意味まで削ってしまえば、Productとしての実用性を失う。

そこで将来耐性の確認を、一度きりの未来予測ではなく、**評価時点の現実を起点として繰り返し見直す設計規律**として定める。

## Decision

Core候補を評価するときは、その時点の技術と実務を確認したうえで、能力や自動化が現在より**おおむね10〜50倍程度進んだ状態**を、思考上の距離として想定する。

10や50という数値は、性能benchmarkでも採点尺度でもない。現在の技術的制約へ過度に適合した設計になっていないかを考えるための目安であり、技術や実務が進歩すれば、評価の基準点そのものも動かす。

```text
その時点の現実
  ↓
現在の技術・実務を確認する
  ↓
10〜50倍程度先まで展望する
  ↓
それでも失ってはいけない意味差を確認する
  ↓
Core / Profile / Provider / Realizationへ配置する
  ↓
技術進歩後、新しい現在地から再評価する
```

Coreへ残す候補は、少なくとも次の条件を満たす必要がある。

1. 現在の実務でも区別する意味がある。
2. 技術が大幅に進歩しても、その意味差が残る可能性が高い。
3. 現在のAIの弱点だけを補う仕組みではない。
4. Provider、Method、Profile、Projectionへ置く方が自然ではない。
5. その区別を失うと、認識・判断・責任・来歴のいずれかが損なわれる。
6. 具体的なScenarioによって必要性を示せる。

「将来も残りそうだ」という予想だけでは、Coreへ採用する十分な根拠とはしない。

## Consequences

- workflow orchestrationやprompt固有の技法をCoreへ固定しにくくなる。
- 将来予測だけを理由に、現在必要なProduct Valueを削ることも抑えられる。
- 主要なArchitectureの見直しや技術環境の変化に合わせて、Core候補を改めて評価する必要がある。
- 10〜50という目安を、数値scoreや機械的な合否基準へ変換しない運用規律が必要になる。

## Revisit conditions

この評価方法が形骸化した場合、または新しい技術環境において「10〜50倍」という距離が思考補助として機能しなくなった場合に再検討する。

## Evidence

- ISSUE-000001で、Architecture reviewへ組み込む運用方法を整理済みである。
- `SEI_PRODUCT_VALUE.md`、Product Vision、Product Principlesでも、固定された未来予測ではなく、現在地とともに動く将来基準を採用している。
- current Architectureでは、実装技術より長く残る意味と、Provider / Profile / Realization等へ移譲できる仕組みを分離している。

## Natural Japanese review

current Product Value、Product Principles、Architectureへ戻って判断内容を照合した。その後、Decision、数値の位置づけ、Core昇格条件を変えない範囲で、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。
