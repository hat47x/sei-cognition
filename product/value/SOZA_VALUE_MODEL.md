# SOZA Value Model

更新日: 2026-09-11  
状態: **Product Value Baseline — Decision Continuity cross-axis outcome reflected**

## 1. この文書の役割

この文書は、`SOZA_PRODUCT_VALUE.md`で定めた価値を、設計判断へ落とせる粒度まで精緻化するための基準です。

個々の機能や実装方式を決める文書ではありません。Requirements、ADR、Architecture、Contract、ImplementationがProduct Valueと整合しているかを判断するために、価値の優先関係、境界、成立条件、失敗条件を定めます。

V1〜V8を具体的にどのEvidenceで確認するかは`SOZA_VALUE_ACCEPTANCE.md`、current下位文書への追跡は`SOZA_VALUE_TRACEABILITY.md`で扱います。

また、V1〜V8が利用者の一つの判断仕事で同時に働いたときに現れる横断的なProduct Outcomeを`SOZA_DECISION_CONTINUITY.md`で扱います。

## 2. SOZAが守る価値の階層

SOZAでは、価値を次の三層に分けます。

### 2.1 第一層: 失ってはならない意味

最優先で守るのは、次の意味です。

- 何が観察されたか。
- 何が不明だったか。
- 何が仮説・解釈・推奨だったか。
- 何を根拠として判断したか。
- 誰または何が、どの役割と権限のもとで判断・実行したか。
- その判断や実行が、どの時点の状態に基づいていたか。
- 後から何が変わり、何を改訂・撤回・置換したか。

この層は、実装の簡略化、性能、操作性、特定Providerとの統合容易性を理由に失わせません。

### 2.2 第二層: 選び直せること

第一層の意味を保持したうえで、SOZAは次を可能にします。

- 根拠を読み直す。
- 過去の判断を当時の状態として復元する。
- 新しいEvidenceを加えて再判断する。
- Capability Providerを交換する。
- Recommendationを採用・不採用・修正する。
- 実行結果を次の問いや判断へ戻す。

SOZAにとって、履歴を残すことは保存そのものが目的ではありません。将来の主体が、過去を消さずに選び直せることに価値があります。

### 2.3 第三層: 利用し続けられること

意味が正しくても、利用が著しく難しければ実務上の価値は失われます。

そのためSOZAは、次も重要な製品価値として扱います。

- 人間が読んで意味を追えること。
- AIが構造として利用できること。
- 必要な意味だけを段階的に明示できること。
- 小さな利用から始め、必要に応じて厳密化できること。
- 外部システムと接続しても、SOZA側の意味境界が崩れないこと。
- 中断や環境変化の後でも、実務上許容できる負担で判断の続きを取り戻せること。

ただし、使いやすさのために第一層の意味を黙って捨てることは認めません。意味の省略が必要な場合は、簡略表示とcanonicalな意味保持を分けます。

また、「利用し続けられること」は単にserviceが稼働し続けることではありません。実際の利用者や組織が必要な場面で意味を読み直し、選び直し、再開するために使えることまで含みます。

## 3. 価値が衝突したときの優先規則

設計上の価値が衝突した場合は、原則として次の順に判断します。

1. **意味保存と責任線を守る。**
2. **再構成可能性と選び直せる余地を守る。**
3. **Providerや実行方式からの独立性を守る。**
4. **人間とAIの双方が扱える理解可能性を守る。**
5. **利用継続性と再開負担を改善する。**
6. **操作性、性能、自動化率、実装容易性を最適化する。**

これは、下位の価値を軽視するという意味ではありません。上位価値を破壊しない範囲で、下位価値を最大化します。

「再開しやすい」ことも、historical basisの誤表示やUnknown消去と引き換えにはしません。速さよりsemantic correctnessを優先します。

重大な性能・運用上の制約によって上位価値を完全には満たせない場合は、暗黙に省略せず、制約、失われる意味、代替策、再検討条件をADRに残します。

また、一つの価値軸で高い成果が得られても、別の重大な価値欠損を相殺したことにはしません。Product Valueの受入れは、V1〜V8を必要な範囲で個別に確認します。

## 4. SOZAへ含めるための価値境界

ある概念・機能・データをSOZAの中核へ含めるかは、次の問いで判断します。

### 4.1 Coreへ置く可能性が高いもの

- Providerが変わっても意味が残る。
- 実行ランタイムが変わっても必要である。
- 判断、責任、不確実性、来歴の再構成に必要である。
- 複数domainで同じ意味境界を持つ。
- 失うと過去の判断を誤って読み替える危険が高い。

### 4.2 Coreへ置かない可能性が高いもの

- 特定Providerの内部都合に強く依存する。
- 特定domainのPatternやSchemaである。
- workflow engine、queue、retry、worker schedulingなど、外部Capability Providerへ委譲できる実行詳細である。
- AIの内部推論過程そのものを保存しなければ成立しない。
- 現在の実装上便利という理由だけでUniversalな意味へ昇格させようとしている。
- Resume Brief、working set、recent list、snapshot token等、Product Interaction上の便利さだけで成立するProjection / runtime-local概念である。

## 5. Product Valueを満たしたとみなすための検証観点

機能やArchitectureは、少なくとも次の観点で検証します。

### V1. Historical Reconstruction

過去のDecisionについて、その時点のEvidence、Unknown、Constraint、Authority、参照Artifactを再構成できるか。

### V2. Semantic Separation

Observation、Interpretation、Recommendation、Decision、Authority、Action Intent、Executionを必要な範囲で区別できるか。

### V3. Revision Integrity

新しい知識によって過去の状態を上書きせず、SupersessionやRevisionとして来歴を辿れるか。

### V4. Provider Independence

Providerを交換しても、Capability、Intent、Decision、Responsibility等の意味が壊れないか。

### V5. Uncertainty Preservation

Unknown、Conflict、Hypothesisを、便宜上の確定値へ黙って変換していないか。

### V6. Human / AI Readability

人間が判断理由を追え、AIも構造として利用できるか。どちらか一方だけに最適化していないか。

### V7. Progressive Explicitness

小さな利用では簡潔に扱いながら、必要になったときに厳密な意味へ降りられるか。

### V8. Execution Independence

外部のworkflow、agent runtime、TEI等が置き換わっても、SOZAの判断記憶と意味構造が存続するか。

これらの軸に対するEvidenceは、少なくとも次の高さを分離して扱います。

```text
Design
  != Executable
  != Release
  != Operational
  != Adoption / Outcome
```

具体的な受入れ条件は`SOZA_VALUE_ACCEPTANCE.md`を正とします。

## 6. Cross-axis Product Outcome — Decision Continuity

Decision ContinuityはV1〜V8に追加する第9軸ではありません。

一人の利用者が実際の判断仕事を中断し、後から戻るときには複数のValue Axisが同時に必要になります。

```text
V1  当時のbasisへ戻る
V2  RecommendationとDecision等を取り違えない
V3  後から得た情報で過去を書き換えない
V5  unresolvedを未来へ持ち越す
V6  人間とAIが意味を読める
V7  再開・記録の負担を過大にしない

supported by:
V4  Providerが変わっても続ける
V8  実行基盤が変わっても続ける
```

この組み合わせが実務上成立した結果をDecision Continuityと呼びます。

### 6.1 なぜ独立軸にしないか

Decision ContinuityをV9にすると、V1 / V3 / V6等の成果を別名で二重評価しやすくなります。また、総合的に「continuityが高い」ことを理由に、一つの重大なsemantic failureを相殺する危険があります。

したがって、Decision Continuityは**利用者成果を検証するcross-axis Scenario / Product Outcome**として扱い、V1〜V8の独立監査を維持します。

### 6.2 Decision Continuityが成立しない例

- canonical dataは正しいが、chat historyがないと利用者がどこから再開すべきか分からない。
- Resume summaryは読みやすいが、Decision後に得た情報をhistorical basisへ混ぜている。
- AIが要点を出せるが、誤ったRecommendationを利用者が訂正・却下できない。
- Provider交換後にpast Decisionは読めるが、current unresolvedやreopen conditionへ戻れない。
- 詳細を残せるが、入力負担が大きすぎて継続利用されない。

## 7. 価値上の失敗パターン

次の状態は、機能が動作していてもProduct Value上の失敗とみなします。

- AIのRecommendationをDecisionとして保存する。
- 現在のArtifactを参照して、過去のDecision basisを再構成したことにする。
- Unknownを未入力値として削除する。
- Conflictを最新値で上書きする。
- Provider固有IDだけをcanonical identityにする。
- 実行成功を、そのDecisionが妥当だった証明として扱う。
- Cognitive Methodを適用した事実を、結論の正しさの保証として扱う。
- UIの簡略化のためにcanonicalな意味を失う。
- 特定製品との密接な関係だけを理由に、その製品をSOZAの一部として特別扱いする。
- Design Evidenceしかない状態を、actual repositoryやproductionで実証済みと表現する。
- fixtureがPASSしたことを、SOZA全体のExecutable Acceptanceとして扱う。
- productionで正常稼働したことを、利用者や組織への価値が実現した証明として扱う。
- canonical dataは保持しているが、利用者が再開するにはraw historyを長時間読み直すしかない。
- time-to-resumeだけを短縮し、historical誤帰属やRecommendation / Decision混同を増やす。
- 監査可能性を理由に入力負担を増やし、capture overheadが実利用価値を上回る。

## 8. 実装規模と価値の関係

SOZAの価値は、Coreの型やコードが増えるほど高まるわけではありません。

新しい概念をCoreへ追加する場合は、既存概念の組合せ、Reference、Extension、Capability Provider、domain-specific knowledgeで表現できないかを先に確認します。

少ないUniversal Coreで意味を保てるなら、その方が将来の技術変化に耐えやすいと考えます。

同様に、Product Valueもfeature数では測りません。Resume Brief、AI assistant、timeline等のSurface featureが増えても、Decision Continuityの失敗が減らないなら価値向上とは扱いません。

## 9. 将来耐性

将来耐性は、特定の未来技術を予測することではありません。

評価時点の現実からおおむね10〜50倍程度先を見たときにも、現在の実装方式を前提にしすぎていないかを点検する移動基準として扱います。

将来、現在のAI agent、workflow、orchestrator、UI、storage方式が大きく変わっても、この文書の第一層と第二層が依然として意味を持つことを目標とします。

Decision Continuityも、現在のchat UIやLLM context windowに依存する概念ではありません。将来AIがより自律化しても、過去に何が認識され、何が判断され、どこまで委任され、何が未解決だったかを別の主体が再開できる価値は残ると考えます。

この距離はbenchmark scoreではありません。現在の制約や流行へ過適合していないかを問うための思考上の距離です。

## 10. 下位文書との関係

この文書の価値境界は、次の順に具体化します。

```text
SOZA Product Value
  → SOZA Value Model
  → SOZA Value Acceptance
  → Product Vision / Principles
  → Requirements / Acceptance Scenarios
  → Issue / ADR
  → Architecture
  → Contract
  → Implementation / Test / Evidence
```

Vision / Principlesは価値の方向と反復原則を示し、Value Acceptanceは価値を満たしたと主張するためのEvidence境界を示します。これらは上下関係というより、Value Modelを異なる方向から具体化する補完文書です。

Decision Continuityはこの流れへ別の階層を追加しません。Value Modelを利用者成果へ横断して読むためのsynthesisです。

current下位文書との対応は`SOZA_VALUE_TRACEABILITY.md`で索引化します。

下位の都合からこの価値境界を変更する必要が生じた場合は、実装を正当化するために直接書き換えず、Product Value変更として明示的に再審査します。

## 11. 関連文書

- `product/README.md`
- `product/value/SOZA_PRODUCT_VALUE.md`
- `product/value/SOZA_VALUE_PROPOSITION.md`
- `product/value/SOZA_VALUE_ACCEPTANCE.md`
- `product/value/SOZA_VALUE_TRACEABILITY.md`
- `product/value/SOZA_DECISION_CONTINUITY.md`
- `product/interaction/SOZA_FIRST_USABLE_PRODUCT_SLICE.md`
- `product/vision/SOZA_PRODUCT_VISION.md`
- `product/principles/SOZA_PRODUCT_PRINCIPLES.md`
- `requirements/PRODUCT_REQUIREMENTS.md`
- `requirements/ACCEPTANCE_SCENARIOS.md`
- `plan/adr/ADR-0018-product-value-authority-and-evaluation-boundary.md`

## 12. 自然な日本語ドラフト

Product Value、Value Acceptance、Decision Continuity synthesis、resume-first Product Slice、current Requirements / Architecture / Contractの状態を再確認した。

V1〜V8の独立性を保ったまま、実利用では複数軸が同時に成立して初めて「判断の続きを始められる」という成果になることをDecision Continuityとして整理した。これをV9にせず、既存軸の重大な欠損をcross-axis scoreで相殺しない境界を明示している。

また、第三層の「利用し続けられること」を、単なるUI usabilityから中断・Surface loss・AI変更後の再開可能性へ深めた。意味、規範強度、Evidence階層を固定したうえで自然な日本語として全文を再ドラフトし、最終意味監査を実施している。