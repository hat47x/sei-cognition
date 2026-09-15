# SEI Product Value

更新日: 2026-09-14  
状態: **Product Value Baseline — Decision Continuity / Brand-world discovery synthesis reflected**

## 1. SEIが存在する理由

井（SEI）は、人間・AI・組織・プロジェクトなどの主体が、**何を観察し、何をまだ分かっていないと認め、何を問い、何を根拠として、どのように判断したか**を失わずに扱うための認知・意思決定基盤です。

SEIの価値は、処理を大量に自動化すること自体にはありません。AIや実行基盤が高度化し、現在のワークフローやエージェント実装が置き換わっても残る、判断の意味・根拠・不確実性・責任・来歴を保つことにあります。

さらに、それらを保存するだけでなく、**時間が空き、SurfaceやAIが変わり、情報が増えた後でも、過去を捏造せず判断仕事の続きを始められる状態にすること**を、利用者へ届くProduct Valueとして重視します。本書ではこの横断的な成果をDecision Continuity（判断継続性）と呼びます。Decision Continuityは新しいValue AxisやUniversal型ではなく、V1〜V8が利用者の実際の仕事で同時に成立した結果です。

SEIは、すでに形になったKnowledgeやDecisionだけを保管する基盤でもありません。まだ十分に言葉になっていないObservation、違和感、問い、Hypothesis候補、相反する見方のような**未確定な認知材料を、早まってTruthへ昇格させず、後から問い直せる形へ外在化できること**も重視します。ここで重要なのは曖昧さを神秘化することではなく、何が確定しておらず、どの段階の認識なのかを失わないことです。

また、その認知成果を一人のworking memory、一つのAI session、一つのProviderへ閉じ込めないことを目指します。ただし共有可能性は無制限公開を意味しません。Product Access、Selective Disclosure、Responsibility、Authority等の境界を保ったまま、許された主体が必要な認知状態へ戻れることを価値とします。

この文書は「SEIがなぜ存在するか」と「何を価値として守るか」を定めます。価値同士が衝突したときの優先関係、Universal Coreへ含める基準、Product Valueを満たしたと判断するための検証観点は`SEI_VALUE_MODEL.md`で、実際にどのEvidenceをもって満たしたと判断するかは`SEI_VALUE_ACCEPTANCE.md`で具体化します。Decision Continuityの横断的な価値仮説と反証条件は`SEI_DECISION_CONTINUITY.md`で扱います。ブランド世界から得た洞察のsourceと採否判断は`../vision/SEI_BRAND_WORLD_SOURCE.md`と`SEI_BRAND_WORLD_VALUE_DISCOVERY_REVIEW.md`に分離して記録します。

## 2. 解こうとする問題

高度なAIや多数の外部システムを利用すると、処理は速くなっても、次のものが失われやすくなります。

- 何が事実として観察され、何が推測だったのか。
- 何が分からないまま残っていたのか。
- 相反する情報がどこに存在したのか。
- 提案と最終判断を誰がどのように区別したのか。
- どのCapabilityを、どの条件と根拠で選んだのか。
- 判断時点では何を知っており、その後何が変わったのか。
- 実行結果が、判断や前提をどのように更新したのか。
- 中断後に、利用者がどこまで進んでいたかを再構成する負担。
- chat、prompt、UI state、Provider固有履歴を失ったときに、判断の続きを始められなくなること。
- まだ説明しきれない違和感や弱いsignalが、構造化できないという理由だけで消えること。
- AIや組織が流暢な一つの説明へ早く収束し、alternate interpretationや未解決点を失うこと。
- 認知成果が特定の人・AI・Providerの私有状態に留まり、別の主体が適切な境界のもとで再利用できないこと。
- AI suggestion、通知、詳細入力が増えすぎ、支援基盤そのものが利用者の認知帯域を奪うこと。

SEIは、これらを実行ランタイムの内部状態や一時的なプロンプトへ閉じ込めず、後から人間とAIの双方が読み直せる形で保持します。

重要なのは、外部記憶を増やすこと自体ではありません。**壊れやすい一時状態へ判断文脈を預けず、canonical meaningから再構成できる外部認知基盤として保つこと**です。

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

### 3.7 判断の継続性を外在化する

SEIは、利用者自身のworking memory、chat transcript、画面状態、特定AIのcontext windowを判断仕事の唯一の継続手段にしません。

中断後に必要なのは、履歴をすべて再読することではなく、canonical meaningから少なくとも次へ戻れることです。

- いま何を考えているか。
- 何を決めたか。
- なぜそう決めたか。
- 何が未解決か。
- Decision後に何が変わったか。
- 何を見直すべきか。

```text
stored correctly
  != resumable in practice
```

したがって、再構成可能性だけでなく、**人間が実務上許容できる負担で判断文脈を取り戻し、誤った記憶や最新情報による過去の読み替えを避けながら続きを始められること**までをProduct Valueへ接続します。

### 3.8 まだ形を得ていないものを、早まって確定せず扱えるようにする

認知や判断は、最初から明確なEvidenceやQuestionとして現れるとは限りません。弱いObservation、違和感、まだ言葉になっていない問い、複数の解釈候補として始まることがあります。

SEIは、こうしたものを「構造化できないから捨てる」か「AIが説明できたからTruthとする」かの二択にしないことを重視します。

必要に応じてObservation、Inquiry、Hypothesis、Unknown等の既存意味へ外在化し、後から新しいEvidenceと結び付けたり、不要だったと判断して捨てたりできる余地を保ちます。

```text
made inspectable
  != made true
```

これは「深層」に正解があるという主張ではなく、**未確定な認知材料を未確定なまま問い直せること**へのProduct Valueです。

### 3.9 認知成果をboundedに共有し、特定の主体やsessionへ閉じ込めない

SEIは、認知成果を一つのchat、一人の担当者、一つのAI modelやProviderの寿命に閉じ込めないことを目指します。

別の主体が後から利用する場合も、Provenance、Responsibility、historical context等を保ち、何をどこまで読めるかというAccess boundaryと同時に扱います。

```text
shared cognition
  != unrestricted disclosure
  != shared authority
```

共有できること自体からDecision Authorityを推定しません。逆に、privacyやAccess Controlが必要だからという理由で、認知成果を各sessionへ分断することも避けます。

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

Decision Continuityについても同じです。resume-first UIを実装したことだけで新しいRequirementやValue Axisを増やさず、実利用比較で独立した価値差やfailureが確認された場合だけ下位規範へ戻します。

ブランド世界から得たProduct discoveryについても、象徴からRequirementを導きません。`井`、水、深層、余白等は探索sourceであり、利用者benefit、failure、counterexample、既存coverageへ戻して独立必要性を確認します。

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
9. 中断やSurface lossの後でも、利用者が過去と現在を取り違えず判断の現在地へ戻れるか。
10. その再開・確認・訂正の負担が、raw chatやsimple note等の妥当な代替に対して実質的な価値差を生むか。
11. まだ確定していないObservationや問いを、Truthへ過剰昇格させず後から再検討できるか。
12. 認知成果を別の人間・AIへ引き継ぐとき、共有可能性とAccess / Responsibilityの境界を同時に保てるか。
13. AIや通知による支援が、本来の判断仕事より大きなattention burdenになっていないか。

これらを実際の設計評価へ使うときは、`SEI_VALUE_MODEL.md`のV1〜V8へ展開します。単一の総合点へ還元せず、どの価値を満たし、どこに未充足やtrade-offが残るかを個別に確認します。今回のブランド世界探索によって新しいV軸は追加しません。

さらに、「満たしている」という主張の高さを正確にするため、`SEI_VALUE_ACCEPTANCE.md`ではDesign、Executable、Release、Operational、Adoption / Outcome Evidenceを分けます。設計文書が整っているだけでactual repositoryやproductionで実証済みとは扱いません。

Decision Continuityの初期Outcome評価では、time-to-orientationだけでなく、historical basisへの誤帰属、AI suggestionの誤昇格、修正負担、first useful saveまでのcapture burden等も観測します。速く再開できても意味を取り違えるならProduct Value上の成功とは扱いません。

Quiet Infrastructureやbounded sharingについても、文書へ書いたことをProduct Valueの実証とは扱いません。attention burden、missed material signal、共有後の誤読、Access boundaryとのtrade-off等をactual interactionで観測する必要があります。

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
- 保存量や履歴量そのものを判断継続性とみなすこと
- 利用者へ過剰な記録作業を課し、その負担を「監査可能性」の名で正当化すること
- AI suggestionやnotificationの量を支援品質とみなすこと
- 未整理な材料を大量に保存すること自体を「深い認知」とみなすこと
- 「共有」を理由にAccess / Responsibility境界を弱めること

## 7. 長期的に守る中心

技術が進歩するほど、現在の実装・プロンプト・オーケストレーションの一部は不要になります。

SEIが守るべき中心は、それらの仕組みではなく、**認識、問い、不確実性、根拠、判断、責任、Capability、来歴を、人間とAIが後から読み直し、選び直し、続きを始められる状態に保つこと**です。

その入口は、すでに明確なDecisionがある場面だけに限定しません。まだ答えになっていない問いや弱いObservationを、必要以上に確定させず外在化し、後から別の主体が適切な境界のもとで問い直せる状態も含みます。

この「続きを始められる」は、過去を最新知識で書き換えることでも、AIにすべて覚えさせることでもありません。耐久的な意味を外在化し、必要な時点で正しい文脈を再構成できることです。

期限を持たないProduct Milestoneは、この中心価値が製品としてどこまで成立したかを確認するために使います。Milestone自体をProduct Valueより上位に置きません。

## 8. 関連文書

- `product/value/SEI_VALUE_MODEL.md` — 価値の優先関係、Core境界、V1〜V8、失敗条件
- `product/value/SEI_VALUE_ACCEPTANCE.md` — V1〜V8を満たしたと判断するためのEvidence境界
- `product/value/SEI_VALUE_PROPOSITION.md` — 利用者から見た価値提案
- `product/value/SEI_DECISION_CONTINUITY.md` — V1〜V8を判断継続性というcross-axis Product Outcomeへ接続する価値仮説
- `product/vision/SEI_BRAND_WORLD_SOURCE.md` — 「井」のブランド世界をProduct探索へ利用する非規範source
- `product/value/SEI_BRAND_WORLD_VALUE_DISCOVERY_REVIEW.md` — ブランド世界から得たProduct hypothesisの採否・配置判断
- `product/definition/SEI_PRODUCT_SHAPE.md` — 製品としての外形
- `product/vision/SEI_PRODUCT_VISION.md` — 長期的に目指す利用状態
- `product/principles/SEI_PRODUCT_PRINCIPLES.md` — 下位設計で反復して適用する原則
- `product/roadmap/SEI_PRODUCT_MILESTONES.md` — 期限を持たない製品成立Milestone
- `plan/UPSTREAM_PRODUCT_DEVELOPMENT_PLAN.md` — 未定領域を議論・実証からRequirementへ進める手順
- `plan/adr/ADR-0018-product-value-authority-and-evaluation-boundary.md` — Product Valueの権威関係と変更・評価境界

## 9. 自然な日本語ドラフト

Value Model、Value Acceptance、Value Proposition、Decision Continuity、ブランド世界のdiscovery source / review、Product Vision、Product Principles、Product Shape、Product Milestoneと上流開発計画の役割分担を確認した。

従来のProduct Valueは「何を意味として失わないか」と「判断をどう継続するか」を強く定義していた。今回、そこへ「まだ形を得ていない認知材料を早まってTruthへ昇格させず扱えること」と「認知成果を一人・一AI・一Providerの一時状態へ閉じず、Access / Responsibilityを保って引き継げること」を統合した。

これらを新しいValue AxisやUniversal型として追加せず、current V1〜V8が利用世界でどのように現れるかを深める表現として扱う。また、Quiet InfrastructureはProduct Valueの実証済み特性ではなく、attention burdenとproactive valueをactualに比較すべきDesign hypothesisとして留保した。

意味、規範強度、Evidence階層を変えず、自然な日本語として全文を再監査した。
