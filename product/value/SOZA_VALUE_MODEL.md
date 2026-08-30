# SOZA Value Model

更新日: 2026-08-31  
状態: **Product Value Baseline**

## 1. この文書の役割

この文書は、`SOZA_PRODUCT_VALUE.md`で定めた価値を、設計判断へ落とせる粒度まで精緻化するための基準です。

個々の機能や実装方式を決める文書ではありません。Requirements、ADR、Architecture、ImplementationがProduct Valueと整合しているかを判断するために、価値の優先関係、境界、成立条件、失敗条件を定めます。

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

ただし、使いやすさのために第一層の意味を黙って捨てることは認めません。意味の省略が必要な場合は、簡略表示とcanonicalな意味保持を分けます。

## 3. 価値が衝突したときの優先規則

設計上の価値が衝突した場合は、原則として次の順に判断します。

1. **意味保存と責任線を守る。**
2. **再構成可能性と選び直せる余地を守る。**
3. **Providerや実行方式からの独立性を守る。**
4. **人間とAIの双方が扱える理解可能性を守る。**
5. **操作性、性能、自動化率、実装容易性を最適化する。**

これは、下位の価値を軽視するという意味ではありません。上位価値を破壊しない範囲で、下位価値を最大化します。

重大な性能・運用上の制約によって上位価値を完全には満たせない場合は、暗黙に省略せず、制約・失われる意味・代替策・再検討条件をADRに残します。

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

## 7. 実装規模と価値の関係

SOZAの価値は、Coreの型やコードが増えるほど高まるわけではありません。

新しい概念をCoreへ追加する場合は、既存概念の組合せ、Reference、Extension、Capability Provider、domain-specific knowledgeで表現できないかを先に確認します。

少ないUniversal Coreで意味を保てるなら、その方が将来の技術変化に耐えやすいと考えます。

## 8. 将来耐性

将来耐性は、特定の未来技術を予測することではありません。

評価時点の現実からおおむね10〜50倍程度先を見たときにも、現在の実装方式を前提にしすぎていないかを点検する移動基準として扱います。

将来、現在のAI agent、workflow、orchestrator、UI、storage方式が大きく変わっても、この文書の第一層と第二層が依然として意味を持つことを目標とします。

## 9. 下位文書との関係

この文書の価値境界は、次の順に具体化します。

```text
SOZA Product Value
  → SOZA Value Model
  → Product Vision / Principles
  → Requirements
  → Issue
  → ADR
  → Architecture
  → Implementation / Test / Evidence
```

下位の都合からこの価値境界を変更する必要が生じた場合は、実装を正当化するために直接書き換えず、Product Value変更として明示的に再審査します。

## 10. 自然な日本語ドラフト

内容と構造を確定した後、意味、強度、留保、技術的境界を変えず、自然な日本語となることを最優先に全文を再ドラフトしました。その後、最終意味監査を実施しています。
