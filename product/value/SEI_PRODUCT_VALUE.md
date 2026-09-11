# SEI Product Value

更新日: 2026-09-01  
状態: **Product Value Baseline**

## 1. SEIが存在する理由

井（SEI）は、人間・AI・組織・プロジェクトなどの主体が、**何を観察し、何をまだ分かっていないと認め、何を問い、何を根拠として、どのように判断したか**を失わずに扱うための認知・意思決定基盤です。

SEIの価値は、処理を大量に自動化すること自体にはありません。AIや実行基盤が高度化し、現在のワークフローやエージェント実装が置き換わっても残る、判断の意味・根拠・不確実性・責任・来歴を保つことにあります。

この文書は「SEIがなぜ存在するか」と「何を価値として守るか」を定めます。価値同士が衝突したときの優先関係、Universal Coreへ含める基準、Product Valueを満たしたと判断するための検証観点は`SEI_VALUE_MODEL.md`で、実際にどのEvidenceをもって満たしたと判断するかは`SEI_VALUE_ACCEPTANCE.md`で具体化します。

## 2. 解こうとする問題

高度なAIや多数の外部システムを利用すると、処理は速くなっても、次のものが失われやすくなります。

- 何が事実として観察され、何が推測だったのか。
- 何が分からないまま残っていたのか。
- 相反する情報がどこに存在したのか。
- 提案と最終判断を誰がどのように区別したのか。
- どのCapabilityを、どの条件と根拠で選んだのか。
- 判断時点では何を知っており、その後何が変わったのか。
- 実行結果が、判断や前提をどのように更新したのか。

SEIは、これらを実行ランタイムの内部状態や一時的なプロンプトへ閉じ込めず、後から人間とAIの双方が読み直せる形で保持します。

## 3. 提供する中核価値

### 3.1 不確実性を消さずに前へ進める

SEIは、`Unknown`をNoへ、`Conflict`を最新値へ、`Hypothesis`を事実へ自動的に潰しません。

分からないことや対立した証拠を残したままでも、必要な判断を行い、その判断がどの不確実性を抱えていたかを後から再構成できることを価値とします。

### 3.2 提案・判断・権限・実行を分ける

SEIでは、少なくとも次を同一視しません。

```text
Recommendation != Decision != Authority != Action Intent != Execution
```

AIが強い提案を出せることと、それを採用する判断、実行権限、実際の実行は別です。この分離により、自動化を進めても責任線と統制可能性を失いにくくします。

### 3.3 判断の記憶を残す

SEIは、最終結果だけでなく、**その時点で何を根拠に判断したか**を残します。

後から前提・観察・Capability・制約が変わっても、過去の判断を書き換えて現在の知識へ合わせるのではなく、当時の判断を当時の状態として復元できることを重視します。

### 3.4 CapabilityとProviderを分け、手段を交換可能にする

SEIは「何を可能にするか」と「誰／何がそれを実現するか」を分けます。

人間、AI、SaaS、外部組織、TEI、custom codeなどを、必要に応じて異質なCapability Providerとして扱います。SEI自身と関係の深い技術であることだけを理由に、特定Providerを優遇しません。

これにより、利用技術が置き換わっても、Intent・Constraint・Decision・Provenance等の意味を保ちやすくします。

### 3.5 実行基盤より上位の意味を保持する

workflow、BPM、agent runtime、queue、retry、worker scheduling等は重要ですが、それらをSEIの恒久的な中心にはしません。

SEIは、外部の実行基盤をCapability Providerとして利用できる一方、それらが置き換わっても残る認知・判断の意味構造を所有します。

### 3.6 人間とAIが同じ判断面を読めるようにする

SEIの記録は、機械処理可能であるだけでなく、人間が意味を追える必要があります。

過剰な内部推論やprivate chain-of-thoughtの保存ではなく、観察、問い、根拠、未解決点、判断理由、責任、来歴など、外在化して共有すべき情報を扱います。

## 4. Product Valueと下位設計の境界

Product Valueは、現在の実装で何が作れるかを列挙する文書ではありません。また、Product Valueの文言から個別のRequirementやUniversal型を機械的に生成しません。

SEIでは、価値を実際の製品へ落とすときに、次の高さを分けます。

```text
Product Value
  → Product Milestone
  → Open Question / Product Hypothesis
  → Discussion / Research / Experiment
  → Candidate Requirement
  → Stable Requirement / Acceptance Scenario
  → Architecture / Contract / Implementation
```

まだ何を要求すべきか十分に分かっていない領域では、未定であることをそのまま認めます。チャット上の議論、資料調査、prototype、fixture、human review、provider接続試験等を通して必要性を確かめ、**独立した規範上の必要性が確認できたものだけをRequirementへ昇格**させます。

実験の結果、既存Requirementで十分だった、新しいUniversal概念は不要だった、という結論もProduct Valueに沿った正当な成果です。

この境界により、Product Valueを守りながら、現在のUI、AI、Storage、Provider等の制約を恒久的な製品要件へ焼き付けることを避けます。

## 5. 価値を測るときの考え方

SEIの価値を、単純な自動化率や実行件数だけで評価しません。

重要なのは、たとえば次の問いに答えられることです。

1. 判断時点の根拠と未解決点を後から再構成できるか。
2. AIの提案と、人間・組織のDecisionを区別できるか。
3. Providerを交換しても、IntentやDecisionの意味が壊れないか。
4. 相反するEvidenceやUnknownを保持したまま扱えるか。
5. 過去のDecisionを現在の知識で上書きせず、変更の来歴を辿れるか。
6. 実行ランタイムが変わっても、SEIの中核価値が残るか。
7. 人間とAIが、同じcanonical meaningへ必要な粒度で戻れるか。
8. 利用者が過剰な入力負担なしに、必要な場面だけ詳細化できるか。

これらを実際の設計評価へ使うときは、`SEI_VALUE_MODEL.md`のV1〜V8へ展開します。単一の総合点へ還元せず、どの価値を満たし、どこに未充足やtrade-offが残るかを個別に確認します。

さらに、「満たしている」という主張の高さを正確にするため、`SEI_VALUE_ACCEPTANCE.md`ではDesign、Executable、Release、Operational、Adoption / Outcome Evidenceを分けます。設計文書が整っているだけでactual repositoryやproductionで実証済みとは扱いません。

## 6. SEIが価値としないもの

SEIは、次をそれ自体の目的とはしません。

- ワークフロー実行量の最大化
- agent turn数や自律実行率の最大化
- 特定AIモデルへの最適化
- 特定Providerへの囲い込み
- Universalな単一スコアによる判断の自動化
- すべての仕事をSEI内部で実行すること
- 実装量やコード量を製品価値とみなすこと
- 未定領域を早くRequirement化した件数を進捗とみなすこと

## 7. 長期的に守る中心

技術が進歩するほど、現在の実装・プロンプト・オーケストレーションの一部は不要になります。

SEIが守るべき中心は、それらの仕組みではなく、**認識、問い、不確実性、根拠、判断、責任、Capability、来歴を、人間とAIが後から読み直し、選び直せる状態に保つこと**です。

期限を持たないProduct Milestoneは、この中心価値が製品としてどこまで成立したかを確認するために使います。Milestone自体をProduct Valueより上位に置きません。

## 8. 関連文書

- `product/value/SEI_VALUE_MODEL.md` — 価値の優先関係、Core境界、V1〜V8、失敗条件
- `product/value/SEI_VALUE_ACCEPTANCE.md` — V1〜V8を満たしたと判断するためのEvidence境界
- `product/value/SEI_VALUE_PROPOSITION.md` — 利用者から見た価値提案
- `product/definition/SEI_PRODUCT_SHAPE.md` — 製品としての外形
- `product/vision/SEI_PRODUCT_VISION.md` — 長期的に目指す利用状態
- `product/principles/SEI_PRODUCT_PRINCIPLES.md` — 下位設計で反復して適用する原則
- `product/roadmap/SEI_PRODUCT_MILESTONES.md` — 期限を持たない製品成立Milestone
- `plan/UPSTREAM_PRODUCT_DEVELOPMENT_PLAN.md` — 未定領域を議論・実証からRequirementへ進める手順
- `plan/adr/ADR-0018-product-value-authority-and-evaluation-boundary.md` — Product Valueの権威関係と変更・評価境界

## 9. 自然な日本語ドラフト

Value Model、Value Acceptance、Value Proposition、Product Shape、Product Milestoneと上流開発計画の役割分担を確認した。Product ValueからRequirementを直接生成せず、未定領域は議論・実証を経て必要なものだけ要件化する境界を追加したうえで、既存の中核価値、強度、留保を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施済みである。