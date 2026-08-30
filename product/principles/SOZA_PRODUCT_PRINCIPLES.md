# SOZA Product Principles

更新日: 2026-08-31  
状態: **Product Principles Baseline**

## 1. この文書の役割

この文書は、`SOZA_PRODUCT_VALUE.md`と`SOZA_VALUE_MODEL.md`で定めた価値を、Requirements、ADR、Architecture、Implementationへ落とすときに繰り返し適用する設計原則をまとめます。

個別の型やAPIを直接決める文書ではありません。下位設計で迷ったときに、どちらの方向がSOZAのProduct Valueへ近いかを判断するために使います。

## 2. 意味を実装より先に置く

SOZAでは、現在のコード、データベース、Prompt、workflow、agent runtimeを製品の恒久的な中心とはみなしません。

まず守るべき意味の違いを定め、その後で実現手段を選びます。実装が便利だからという理由だけで意味構造を決めません。

## 3. 観測・解釈・提案・判断を混ぜない

SOZAでは、見えたもの、そこから読み取ったこと、採るべきだと考えた案、実際に採用したDecisionを必要な範囲で分けます。

```text
Observation
  != Interpretation / Hypothesis
  != Recommendation
  != Decision
```

すべてを常に別Artifactへ分割することを要求するものではありません。重要なのは、後から意味の違いを復元できることです。

## 4. 不確実性を正直に保持する

`Unknown`、`Conflict`、`Hypothesis`、Observation不足を、都合よく確定値へ変換しません。

判断が必要な場合は、不確実性を残したままでも判断でき、その時点で何が未解決だったかを後から辿れる構造を優先します。

`not observed`を`unavailable`や`false`へ暗黙変換しません。

## 5. Recommendation・Decision・Authority・Executionを分離する

```text
Recommendation != Decision != Authority != Action Intent != Execution
```

提案が優れていること、採用判断が行われたこと、権限があること、実行されたことは別の意味です。

AIの能力向上や自動化率の上昇を理由に、この境界を暗黙化しません。

## 6. ProvenanceとSemantic Lineageを失わない

どこから得た情報か、どの経路で発見したか、何をもとに派生したか、どの意味変更が何を置き換えたかを区別します。

storage revision、Git commit、DB version等を、そのままsemantic identityやsemantic revisionと同一視しません。

## 7. 過去を現在の知識で上書きしない

現在の理解が変わっても、過去のDecisionが当時どのEvidence、Observation、Unknown、Constraint等を参照していたかを再構成できるようにします。

最新状態だけを残して履歴を消す設計を避けます。

## 8. CapabilityとProviderを分ける

Capabilityは「何を可能にするか」、Providerは「誰／何がそのCapabilityを提供するか」です。

```text
Capability != Provider
```

人間、AI、SaaS、外部組織、TEI、custom code等を、その種類だけから信頼、優先度、Authorityへ結び付けません。

## 9. Providerを交換可能にする

SOZAの意味構造は、特定のAIモデル、SaaS、workflow engine、BPM、TEI、DB等を交換しても保てることを目指します。

Provider固有の情報が必要な場合は、Coreへ一般化する前にProvider / Profile側へ置けないかを検討します。

Providerの変更によってIntent、Decision、Responsibilityの意味まで変わる設計を避けます。

## 10. Coreは小さく保つが、必要な意味境界まで薄くしない

Coreを小さくすること自体を目的にはしません。

一方、現在の都合でUniversal型を増やしすぎることも避けます。Coreへ追加する概念は、現在の具体Scenarioで必要であり、技術が大幅に進歩しても区別する意味が残ることを確認します。

既存概念の組合せ、Reference、Extension、Profile、Capability Provider、domain-specific knowledgeで十分に表現できる場合は、Universal型を増やさないことを優先します。

## 11. 簡略表示とcanonicalな意味保持を分ける

利用者にすべての意味境界を常時見せる必要はありません。

UIや入力を簡略化しても、重要な意味を内部で黙って消さず、必要になったときにcanonicalな状態へ戻れる構造を優先します。

```text
Simple View != Lossy Canonical Model
```

読みやすさや操作性のために意味を省略する場合は、表示上の省略と意味上の削除を区別します。

## 12. Progressive Semantic Explicitnessを認める

すべての作業へ同じ重い記録手続きを要求しません。

低影響で可逆な作業と、高影響・不可逆・高不確実・外部性の大きい作業では、必要な意味境界の厚さが異なって構いません。

ただし、AI自身のconfidenceだけを理由に重要な境界を省略しません。必要な明示性はProfile / Policy等として外在化します。

## 13. 評価時点から10〜50倍程度先を見る

将来耐性は、固定された「100倍未来」の想定ではなく、評価時点の現実からおおむね10〜50倍程度先を見渡す移動基準として扱います。

この倍率はbenchmarkではありません。現在の制約への過適合を見つけるための思考上の距離です。

主要なArchitecture Rebaselineや技術環境の変化に応じて、新しい現在地から設計候補を再評価します。

## 14. 実装順序と世界の意味構造を混同しない

M48、M49等のMilestoneは開発上の順序です。

実装の順番を、そのまま利用者世界の必須workflowやontologyへ変換しません。

## 15. code shedding / prompt sheddingを前提とする

より優れたAIや標準技術が現れ、SOZA内部のコードやPromptが不要になった場合は、無理に維持しません。

削れる実装は削り、意味契約と検証可能な境界を残します。

## 16. human-readableを設計品質として扱う

SOZAの重要な文書・Artifactは、機械が処理できるだけでなく、人間が読んで意味を確認できることを重視します。

開発文書については、内容と構造を作成した後に、意味や仕様を変えず、**自然な日本語となることを最重要視して全文をドラフトし直す工程**を必ず設けます。

新規文書だけでなく、既存のactiveな開発文書もすべてこの工程を通します。historical evidence等、原文保存が必要な資料は本文を改変せず、除外理由と日本語の案内を別途残します。

## 17. Evidenceを超える主張をしない

local fixture、synthetic test、design review、production operationを区別します。

設計が整ったことを実装済みと呼ばず、ローカル試験のPASSを運用実績と呼ばず、実際に確認できたEvidenceを超えてcoverageやrelease状態を引き上げません。

```text
Execution Success != Decision Validity
Method Application != Assurance
```

実行に成功したことやMethodを適用したことだけから、判断や結論が正しかったと主張しません。

## 18. Product Valueを単一スコアへ潰さない

SOZAの価値は、単一の総合点やUniversal Scoreへ還元しません。

`SOZA_VALUE_MODEL.md`のV1〜V8をはじめとする複数の観点から、何を満たし、どこにtrade-offや未充足が残るかを個別に確認します。

一つの評価軸で優れていることを理由に、別の重大な価値欠損を相殺したことにはしません。

## 19. 関連製品を特権化しない

TEIを含む関連製品・技術を、SOZAとの関係が近いという理由で自動的に優先しません。

同じIntent、Constraint、Evidence、Decision境界のもとで、他のCapability Providerと比較可能であることを原則とします。

## 20. Product Valueの変更は明示的に再基線化する

下位実装の都合だけでProduct ValueやValue Modelを書き換えません。

上位価値を変更する必要が生じた場合は、反証Evidence、影響範囲、互換性、Revisit条件を明示し、通常の実装変更とは分けて再基線化します。

Product Valueの変更後は、影響するRequirements、ADR、Architecture、Implementationを上位から再監査します。

## 21. 関連文書

- `product/value/SOZA_PRODUCT_VALUE.md`
- `product/value/SOZA_VALUE_MODEL.md`
- `product/vision/SOZA_PRODUCT_VISION.md`
- `plan/adr/ADR-0018-product-value-authority-and-evaluation-boundary.md`

## 22. 自然な日本語ドラフト

Value ModelとProduct Visionへ戻って意味整合を確認し、重複する原則を整理した後、意味、仕様、強度、留保を変えず、自然な日本語となることを最重要視して全文を再ドラフトしました。その後、最終意味監査を実施しています。
