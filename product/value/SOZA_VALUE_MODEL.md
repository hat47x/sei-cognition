# SOZA Value Model

更新日: 2026-08-31  
状態: **Product Value Baseline**

## 1. この文書の役割

この文書は、`SOZA_PRODUCT_VALUE.md`で定めた価値を、Requirements・ADR・Architecture・Implementationの判断へ使える粒度まで具体化するための基準です。

個々の機能や実装方式を決める文書ではありません。SOZAが何を優先して守るのか、どのような状態を価値上の失敗とみなすのか、下位設計がProduct Valueと整合しているかをどの観点で確認するのかを定めます。

Product Valueを明文化したこと自体は、SOZAがその価値を実運用で実現できた証拠にはなりません。この文書が定めるのは**価値の基準**であり、実装・運用・利用者価値の実証は別のEvidenceとして積み上げます。

## 2. SOZAが守る価値の階層

SOZAでは、価値を次の三層に分けます。

### 2.1 第一層: 失ってはならない意味

最優先で守るのは、次の意味です。

- 何が観察されたか。
- 何が不明だったか。
- 何が仮説・解釈・推奨だったか。
- 何を根拠として判断したか。
- 誰または何が、どの責任と権限のもとで判断・実行したか。
- その判断や実行が、どの時点の状態に基づいていたか。
- 後から何が変わり、何を改訂・撤回・置換したか。

この層は、実装の簡略化、性能、操作性、特定Providerとの統合容易性を理由に黙って失わせません。

### 2.2 第二層: 選び直せること

第一層の意味を保持したうえで、SOZAは次を可能にします。

- 根拠を読み直す。
- 過去の判断を当時の状態として復元する。
- 新しいEvidenceを加えて再判断する。
- Capability Providerを交換する。
- Recommendationを採用・不採用・修正する。
- 実行結果を次の問いや判断へ戻す。

SOZAにとって、履歴を残すことは保存そのものが目的ではありません。将来の主体が、過去を消さずに判断を検証し、必要なら選び直せることに価値があります。

### 2.3 第三層: 利用し続けられること

意味が正しくても、利用が著しく難しければ実務上の価値は失われます。

そのためSOZAは、次も重要な製品価値として扱います。

- 人間が読んで意味を追えること。
- AIが構造として利用できること。
- 必要な意味だけを段階的に明示できること。
- 小さな利用から始め、必要に応じて厳密化できること。
- 外部システムと接続しても、SOZA側の意味境界が崩れないこと。

ただし、使いやすさのために第一層の意味を黙って捨てることは認めません。表示や入力を簡略化する場合も、必要なcanonicalな意味を失わない方法を優先します。

## 3. 価値が衝突したときの優先規則

設計上の価値が衝突した場合は、原則として次の順に判断します。

1. **判断の意味、不確実性、責任線、来歴を守る。**
2. **過去を再構成し、選び直せる余地を守る。**
3. **Providerや実行方式から意味を独立させる。**
4. **人間とAIの双方が理解・利用できる状態を守る。**
5. **操作性、性能、自動化率、実装容易性を最適化する。**

これは、下位の価値を軽視するという意味ではありません。上位価値を破壊しない範囲で、下位価値を最大化します。

重大な性能・運用上の制約によって上位価値を完全には満たせない場合は、暗黙に省略せず、失われる意味、制約、代替策、影響範囲、再検討条件をADRへ残します。

## 4. SOZAへ含めるための価値境界

ある概念・機能・データをSOZAのUniversal Coreへ含めるかは、次の問いで判断します。

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
- AIのprivate chain-of-thoughtや内部推論過程そのものを保存しなければ成立しない。
- 現在の実装で便利という理由だけでUniversalな意味へ昇格させようとしている。
- 特定製品とSOZAの関係が近いという理由だけで、共通概念として扱おうとしている。

### 4.3 Core以外に置けるなら、まずそちらを検討する

Universal Coreへ新しい概念を増やす前に、少なくとも次で表現できないかを確認します。

- Profile / Policy
- Extension
- Reference
- Capability Provider
- Provider adapter
- domain-specific Design Knowledge
- Cognitive Method

Coreを小さくすること自体が目的ではありませんが、現在の実装事情をUniversalな意味へ昇格させないため、この順序を重視します。

## 5. Product Valueを検証する観点

機能やArchitectureは、少なくとも次の観点で検証します。

### V1. Historical Reconstruction

過去のDecisionについて、その時点のEvidence、Unknown、Constraint、Authority、参照Artifactを再構成できるか。

### V2. Semantic Separation

Observation、Interpretation、Hypothesis、Recommendation、Decision、Authority、Action Intent、Executionを、必要な範囲で区別できるか。

### V3. Revision Integrity

新しい知識によって過去の状態を上書きせず、RevisionやSupersessionとして来歴を辿れるか。

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

### V9. Evidence Calibration

設計上の整合、local fixtureのPASS、actual repositoryでのconformance、production operation、利用者価値の実証を区別できるか。

一つのEvidence levelを、より強いEvidenceへ自動的に読み替えないことを確認します。

## 6. 価値上の失敗パターン

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
- Provider内部の状態を、一つのUniversalなavailabilityやtruthへ機械的に変換する。
- 設計文書が整ったことを、production利用価値が実証されたこととして扱う。

## 7. 価値定義と価値実証を分ける

SOZAでは、少なくとも次のEvidence levelを区別します。

```text
Normative Value Definition
  ↓
Design / Requirement Coverage
  ↓
Executable Conformance Evidence
  ↓
Operational Evidence
  ↓
Adoption / Outcome Evidence
```

この矢印は自動昇格を表しません。下位のEvidenceが得られたときに、より強い主張を検討できるという順序を示します。

たとえば、Product Valueと整合するArchitectureが完成しても、実装がその境界を守るとは限りません。local testがPASSしても、productionで判断を再構成できるとは限りません。productionで動作しても、利用者がSOZAによって実際により良く判断できるとは限りません。

各文書・報告では、確認できたEvidenceの範囲を超えて価値充足を主張しません。

## 8. 価値を具体的な状況へ戻す

Product Valueは抽象原則だけでは検証しにくいため、`SOZA_VALUE_SCENARIOS.md`で代表的な状況へ戻します。

Value ScenarioはRequirementsやAcceptance Scenarioそのものではありません。Product Valueが現実の判断場面でどのような意味差として現れるべきかを確認し、下位文書へ漏れなく展開するための橋渡しです。

## 9. 実装規模と価値の関係

SOZAの価値は、Coreの型やコードが増えるほど高まるわけではありません。

新しい概念をCoreへ追加する場合は、既存概念の組合せやCore外の表現で意味を保てないかを先に確認します。

少ないUniversal Coreで必要な意味を保てるなら、その方が技術変化に耐えやすく、Providerやdomainを越えて再利用しやすいと考えます。

## 10. 将来耐性

将来耐性は、特定の未来技術を予測することではありません。

評価時点の現実からおおむね10〜50倍程度先を見たときにも、現在の実装方式を前提にしすぎていないかを点検する移動基準として扱います。

将来、現在のAI agent、workflow、orchestrator、UI、storage方式が大きく変わっても、この文書の第一層と第二層が意味を持ち続けることを目標とします。

## 11. 下位文書との関係

この文書の価値境界は、次の順に具体化します。

```text
SOZA Product Value
  → SOZA Value Model
  → Product Vision / Principles
  → Value Scenarios
  → Requirements / Acceptance Scenarios
  → Issue
  → ADR
  → Architecture
  → Implementation / Test / Evidence
```

下位の都合からこの価値境界を変更する必要が生じた場合は、実装を正当化するために直接書き換えず、Product Value変更として明示的に再審査します。

## 12. 自然な日本語ドラフト

内容と構造を確定した後、意味、強度、留保、技術的境界を変えず、自然な日本語となることを最重要視して全文を再ドラフトしました。その後、最終意味監査を実施しています。
