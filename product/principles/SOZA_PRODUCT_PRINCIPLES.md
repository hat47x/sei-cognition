# SOZA Product Principles

更新日: 2026-08-31  
状態: **Product Principles Baseline**

## 1. この文書の役割

この文書は、SOZAのProduct ValueとVisionを、Requirements・ADR・Architecture・Implementationで繰り返し使える判断原則へ落としたものです。

個別の設計判断を先取りする文書ではありません。具体的な選択肢が衝突したときに、何を守るべきかを思い出すための反復可能な基準です。

原則の適用だけで結論の正しさが保証されるわけではありません。個別判断はEvidenceとScenarioへ戻して確認します。

## 2. 意味を実装より先に置く

SOZAでは、現在のコード、データベース、Prompt、workflow、agent runtimeを製品の恒久的な中心とはみなしません。

まず守るべき意味の違いを定め、その後で実現手段を選びます。実装が便利だからという理由だけで意味構造を決めません。

## 3. 不確実性を正直に保持する

`Unknown`、`Conflict`、`Hypothesis`、Observation不足を、都合よく確定値へ変換しません。

判断が必要な場合は、不確実性を残したままでも判断でき、その時点で何が未解決だったかを後から辿れる構造を優先します。

`not observed`を`No`へ、`not evaluated`を`denied`へ、Conflictを最新値へ機械的に変換しません。

## 4. Recommendation・Decision・Responsibility・Authority・Executionを分離する

```text
Recommendation != Decision != Responsibility != Authority != Action Intent != Execution
```

提案が優れていること、採用判断が行われたこと、誰がその判断を担ったか、実行権限が成立したこと、実際に実行されたことは別の意味です。

AIの能力向上や自動化率の上昇を理由に、この境界を暗黙化しません。

## 5. ProvenanceとSemantic Lineageを失わない

どこから得た情報か、どの経路で発見したか、何をもとに派生したか、どの意味変更が何を置き換えたかを区別します。

storage revision、Git commit、DB version等を、そのままsemantic identityやsemantic revisionと同一視しません。

重要な判断で特定版のArtifactやProvider状態がbasisになった場合は、必要な粒度で当時の内容へ戻れるようにします。

## 6. 過去を現在の知識で上書きしない

現在の理解が変わっても、過去のDecisionが当時どのEvidence、Observation、Unknown、Constraint等を参照していたかを再構成できるようにします。

最新状態だけを残して履歴を消す設計を避けます。

後から誤りが分かった場合も、過去を改変して最初から正しかったように見せるのではなく、訂正・撤回・Supersessionの来歴を残します。

## 7. 問いを使い捨てにしない

重要なQuestionを、chat turn、ダイアログ文、session状態だけとして扱いません。

質問文の改善とQuestionの意味変更を分け、同じ前提では過去Decisionを再利用し、新しいEvidenceやConstraintが現れたときには再び問い直せる構造を優先します。

```text
Question wording != Question semantic identity
Previous decision reuse != permanent suppression of inquiry
```

## 8. CapabilityとProviderを分ける

Capabilityは「何を可能にするか」、Providerは「誰／何がそのCapabilityを提供するか」です。

```text
Capability != Provider
```

人間、AI、SaaS、外部組織、TEI、custom code等を、その種類だけから信頼・優先度・Authorityへ結び付けません。

## 9. Providerを交換可能にする

SOZAの意味構造は、特定のAIモデル、SaaS、workflow engine、BPM、TEI、DB等を交換しても保てることを目指します。

Provider固有の情報が必要な場合は、Coreへ一般化する前にProvider adapter、Profile、Policy、Extension等へ置けないかを検討します。

Provider内部の一つのstatusを、SOZA側のUniversalなavailabilityやtruthへ自動変換しません。

## 10. Coreは小さく保つが、必要な意味境界まで薄くしない

Coreを小さくすること自体を目的にはしません。

一方、現在の都合でUniversal型を増やしすぎることも避けます。Coreへ追加する概念は、現在の具体Scenarioで必要であり、複数domain・複数Providerでも同じ意味境界が成立し、Core外の表現では不足することを確認します。

特定製品との関係が近いこと、現在の実装で便利であること、AIが扱いやすいことだけではCoreへの昇格理由としません。

## 11. 評価時点から10〜50倍程度先を見る

将来耐性は、固定された「100倍未来」の想定ではなく、評価時点の現実からおおむね10〜50倍程度先を見渡す移動基準として扱います。

この倍率はbenchmarkではありません。現在のAIや実装制約へ過適合していないかを見つけるための思考上の距離です。

主要なArchitecture Rebaselineや技術環境の変化に応じて、新しい現在地から設計候補を再評価します。

## 12. Progressive Semantic Explicitnessを認める

すべての作業へ同じ重い記録手続きを要求しません。

低影響で可逆な作業と、高影響・不可逆・高不確実・外部性の大きい作業では、必要な意味境界の厚さが異なって構いません。

ただし、簡潔なUIとsemantic deletionを同一視しません。AI自身のconfidenceだけを理由に重要な境界を省略せず、必要な明示性はProfile / Policy等として外在化します。

## 13. Selective DisclosureとUnknownを両立させる

複数組織やProviderをまたぐとき、内部情報を全て共有できるとは限りません。

必要なObservation・Evidence・Assuranceだけを共有できる設計を認めます。一方、非開示部分を既知として補ったり、開示されていないことを否定Evidenceとして扱ったりしません。

```text
Selective Disclosure != fabricated completeness
```

## 14. 実装順序と世界の意味構造を混同しない

M48、M49等のMilestoneは開発上の順序です。

実装の順番を、そのまま利用者世界の必須workflowやontologyへ変換しません。

同様に、現在のrepository treeやcandidate bundleの構造を、Product Valueが要求する唯一の構造とはみなしません。

## 15. code shedding / prompt sheddingを前提とする

より優れたAIや標準技術が現れ、SOZA内部のコードやPromptが不要になった場合は、無理に維持しません。

削れる実装は削り、意味契約と検証可能な境界を残します。

実装量をProduct Valueの代理指標にしません。

## 16. human-readableを設計品質として扱う

SOZAの重要な文書・Artifactは、機械が処理できるだけでなく、人間が読んで意味を確認できることを重視します。

開発文書については、内容と構造を作成した後に、意味や仕様を変えず、**自然な日本語となることを最重要視して全文をドラフトし直す工程**を必ず設けます。

新規文書だけでなく、既存のactiveな開発文書もすべてこの工程を通します。historical evidence等、原文保存が必要な資料は本文を改変せず、除外理由と日本語の案内を別途残します。

## 17. Evidenceを超える主張をしない

少なくとも次を区別します。

```text
Value Definition
  != Design / Requirement Coverage
  != Executable Conformance
  != Operational Evidence
  != Adoption / Outcome Evidence
```

local fixture、synthetic test、actual repositoryのtest、production operation、利用者による価値実証も、それぞれ別のEvidenceです。

設計が整ったことを実装済みと呼ばず、local試験のPASSを運用実績と呼ばず、productionで動いたことだけを利用者価値の証明と呼びません。

確認できたEvidenceを超えてcoverageやrelease状態、Product Valueの実証度を引き上げません。

## 18. 実行成功と判断妥当性を分ける

実行が成功したことは重要なObservationですが、そのDecisionが妥当だったことやProduct Valueが実現したことを自動的には証明しません。

```text
Execution Success != Decision Validity != Product Value Realization
```

実行結果は次のQuestion・Observation・Decisionへ戻し、必要なら過去判断を再審査します。

## 19. Cognitive MethodとDesign Knowledgeを答えとして特権化しない

KJ法、cultural-substrate-weaving、Reference Model、Pattern Card等は、問い・候補・比較・検査を豊かにできます。

しかし、Methodを適用した事実やPatternが似ていることだけで、結論の正しさや採用Decisionを確定しません。

```text
Method Application != Assurance
Pattern match != Decision
```

## 20. 関連製品を特権化しない

TEIを含む関連製品・技術を、SOZAとの関係が近いという理由で自動的に優先しません。

同じIntent、Constraint、Evidence、Decision境界のもとで、他のCapability Providerと比較可能であることを原則とします。

## 21. 原則を具体Scenarioへ戻す

抽象原則だけで設計を正当化しません。

重要なCore境界や高影響な判断では、`SOZA_VALUE_SCENARIOS.md`の代表場面、または同等の具体Scenarioへ戻し、原則が現実の意味差として必要かを確認します。

Scenarioが不足している場合は、新しいScenarioを追加するか、Product Value自体の見直しが必要かを分けて判断します。

## 22. 関連文書

- `product/value/SOZA_PRODUCT_VALUE.md`
- `product/value/SOZA_VALUE_MODEL.md`
- `product/value/SOZA_VALUE_SCENARIOS.md`
- `product/vision/SOZA_PRODUCT_VISION.md`
- `plan/adr/ADR-0018-product-value-authority-and-evaluation-boundary.md`

## 23. 自然な日本語ドラフト

Value Model、Vision、Value Scenarioとの整合を確認した後、意味、技術的境界、強度、留保を変えず、自然な日本語となることを最重要視して全文を再ドラフトしました。その後、最終意味監査を実施しています。
