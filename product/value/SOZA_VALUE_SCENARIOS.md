# SOZA Value Scenarios

更新日: 2026-08-31  
状態: **Product Value Scenario Baseline**

## 1. この文書の役割

この文書は、`SOZA_PRODUCT_VALUE.md`と`SOZA_VALUE_MODEL.md`で定めた価値を、具体的な判断場面へ戻して確認するための基準です。

Value Scenarioは、Product RequirementやAcceptance Scenarioそのものではありません。実装方式やUIを先に決めるのでもありません。

目的は、SOZAが守ると定めた価値が、現実の仕事でどのような意味差として現れるべきかを示し、Requirements・Issue・ADR・Architectureへ展開するときに重要な価値を取り落とさないことです。

各シナリオでは、少なくとも次を区別します。

- 何が起きているか。
- SOZAが守るべき意味は何か。
- 何を安易に同一視してはいけないか。
- 後から何を検証・再構成できるべきか。
- どのEvidence levelまで確認できれば、どの強さの主張ができるか。

## 2. Scenario 01 — AI提案を採用せず、別案をDecisionする

### 状況

AIが、複数のEvidenceと過去事例をもとに有力な対応案をRecommendationとして提示します。人間または組織は、その提案を理解したうえで、別のConstraintを重視して採用しません。

### 守る価値

- AIのRecommendationと最終Decisionを分ける。
- Recommendationを棄却したことも判断の来歴として残せる。
- DecisionのbasisとResponsibilityを後から確認できる。
- 「AIが提案した」という事実をAuthorityへ昇格させない。

### 壊してはいけない境界

```text
Recommendation != Decision != Authority
```

AIの提案精度が高くても、この境界は自動的には消えません。

### 後から確認できるべきこと

- AIは何を提案したか。
- 何を根拠としていたか。
- 誰または何がDecisionを担ったか。
- なぜ別案を選んだか。
- 後に結果が悪かった場合でも、当時のEvidenceとConstraintを現在の知識で書き換えていないか。

## 3. Scenario 02 — Unknownを残したまま期限内に判断する

### 状況

重要な情報の一部がまだ取得できません。しかし期限や外部条件のため、完全な情報を待たずに判断する必要があります。

### 守る価値

- UnknownをNoや既定値へ変換しない。
- 不確実性が残った状態でDecisionしたことを明示できる。
- 後にEvidenceが得られたとき、過去Decisionを消さずに再審査できる。

### 壊してはいけない境界

```text
Unknown != No
Missing observation != negative evidence
```

### 後から確認できるべきこと

- 何が分かっていたか。
- 何がUnknownだったか。
- Unknownを抱えたまま進む必要があった理由は何か。
- 後から入ったEvidenceが、どのDecisionまたは前提を変えたか。

## 4. Scenario 03 — 相反するEvidenceを残して判断する

### 状況

複数の資料やProviderから、互いに両立しない観察・主張が得られます。現時点では、どちらか一方が誤りだと確定できません。

### 守る価値

- Conflictを最新値や多数決で消さない。
- それぞれの出所とEvidenceUseを辿れる。
- Conflictが未解決であること自体を判断材料として扱える。

### 壊してはいけない境界

```text
Conflict != latest-wins
Source count != truth
```

### 後から確認できるべきこと

- 何と何がConflictしていたか。
- 各主張の出所と時点は何か。
- Conflictを解消しないまま、どのようなDecisionを行ったか。
- 後に追加Evidenceが得られたとき、どの関係が解消・維持・再分類されたか。

## 5. Scenario 04 — 一度答えた設計質問を、新しいEvidenceで問い直す

### 状況

以前、「変更履歴を保持するか」などの設計質問に回答し、Decisionが残っています。その後、新しい法的要件、運用実績、障害、顧客条件などが入り、以前の回答をそのまま再利用することが不適切になります。

### 守る価値

- Questionの意味上のidentityと表示文を分ける。
- 同じ前提なら過去Decisionを再利用できる。
- 前提が変われば、過去Decisionを上書きせず後継Decisionを作れる。
- なぜ再審査が起きたかを辿れる。

### 壊してはいけない境界

```text
Question wording != Question semantic identity
Previous decision reuse != permanent suppression of inquiry
```

### 後から確認できるべきこと

- 以前のQuestionとDecisionは何だったか。
- どのEvidenceまたはConstraintが変わったか。
- 同じQuestionの再審査なのか、意味上別のQuestionなのか。
- 新旧DecisionのSemantic Lineageを辿れるか。

## 6. Scenario 05 — Capability Providerを交換する

### 状況

あるCapabilityを、当初はTEIが提供していました。後にSaaS、人間作業、別のAI、別実装へ切り替えます。

### 守る価値

- CapabilityとProviderを分ける。
- Providerを替えても、Intent、Constraint、Decision、Responsibilityの意味を維持する。
- Provider内部の固有状態をSOZAのUniversalな意味へ直接持ち込まない。

### 壊してはいけない境界

```text
Capability != Provider
Provider-specific state != universal capability semantics
```

### 後から確認できるべきこと

- 何のCapabilityが必要だったか。
- どのProvider候補があり、何を根拠に選んだか。
- Provider交換時に、意味上何が維持され、何が変わったか。
- 過去Decision時に利用したProvider-specific Evidenceへ必要に応じて戻れるか。

## 7. Scenario 06 — Provider内部状態が不完全でもCapability Choiceを検討する

### 状況

TEIや他Providerについて、一部の状態は確認できますが、依存関係や認可、Environment bindingなどが未確認です。

### 守る価値

- Provider内部の一つの状態からCapability availabilityを自動推定しない。
- `unknown`と`unavailable`を分ける。
- SOZAはProvider固有Schemaを複製せず、判断に必要なObservationとEvidenceを受ける。
- 必要に応じてProvider-specificなexact snapshotへ降りられる。

### 壊してはいけない境界

```text
Provider status != Capability Decision
Not observed != unavailable
```

### 後から確認できるべきこと

- 何が観察済みで、何が未確認だったか。
- どのProvider adapterやEvidenceを参照したか。
- Capability Choiceを進めた、保留した、または別Providerへ切り替えた理由は何か。

## 8. Scenario 07 — Decisionはあるが、実行Authorityが成立しない

### 状況

SOZA上では実行するDecisionが成立しています。しかし、実行先Providerでは必要なAuthorizationが未評価、失効、拒否、または一時的に確認不能です。

### 守る価値

- Decision、Responsibility、Authorization、Executionを分ける。
- Authorizationの未評価をDecision不在やdeniedへ変換しない。
- Providerごとの認可方式をSOZA Coreへ統一しない。

### 壊してはいけない境界

```text
Decision != Authorization != Execution
Not evaluated != denied
```

### 後から確認できるべきこと

- Decisionは誰が、どのbasisで行ったか。
- Provider側では、どの対象・scope・時点について何を評価したか。
- 実行しなかった理由がDecisionの撤回なのか、Authority不足なのか、技術障害なのか。

## 9. Scenario 08 — 実行は成功したが、判断の妥当性は別に評価する

### 状況

選択したProviderによる処理は技術的に成功しました。しかし、後から見るとDecision basisが不十分だった、重要なConflictを見落としていた、別案の方が目的に適していた、といった可能性があります。

### 守る価値

- Execution SuccessをDecision Validityへ昇格させない。
- 実行結果をObservationとして次の評価へ戻す。
- 成功した実装を理由に過去のDecision basisを書き換えない。

### 壊してはいけない境界

```text
Execution Success != Decision Validity != Product Value Realization
```

### 後から確認できるべきこと

- 技術的には何が成功したか。
- Decision時には何を知っていたか。
- 結果から新しく何を観察したか。
- Decisionを維持・修正・撤回する必要があるか。

## 10. Scenario 09 — Cognitive MethodやReference Modelを使うが、答えとして扱わない

### 状況

KJ法、cultural-substrate-weaving、Reference Model、Pattern Cardなどを用いて候補や問いを増やします。しかし、MethodやPatternそのものを対象の真実として扱いません。

### 守る価値

- Cognitive MethodとPatternを分ける。
- Method ApplicationとAssuranceを分ける。
- Pattern matchとDecisionを分ける。
- 重要なPatternを根拠として使った場合は、その版や内容へ戻れる。

### 壊してはいけない境界

```text
Reference Model != Cognitive Method != Decision
Method Application != Assurance
Pattern match != Pattern adoption
```

### 後から確認できるべきこと

- 何のMethodやPatternを使ったか。
- そこから何のQuestionやRecommendationが生じたか。
- 何を採用せず、なぜ棄却したか。
- 最終Decisionが対象側のEvidenceへ戻れるか。

## 11. Scenario 10 — Selective Disclosureを保ちながら組織をまたいで判断する

### 状況

複数組織・Providerが一つのDecisionに関与しますが、内部topology、契約、顧客情報、詳細Policyなどを全て相互公開できません。

### 守る価値

- 必要なObservation・Evidence・Assuranceだけを共有できる。
- 全内部状態の開示をSOZA参加条件にしない。
- 開示されていない部分を既知として扱わない。
- 必要な責任線とDecision basisを共有可能な範囲で維持する。

### 壊してはいけない境界

```text
Selective Disclosure != fabricated completeness
Hidden detail != negative evidence
```

### 後から確認できるべきこと

- 誰が何を開示したか。
- 何が非開示・未確認だったか。
- どのEvidenceだけでDecisionしたか。
- 後の監査で追加開示が許可された場合、当時の判断へ接続できるか。

## 12. Scenario 11 — 軽量利用から必要な箇所だけ厳密化する

### 状況

日常的な低影響作業では、全ての意味要素を明示するコストが高すぎます。一方、高影響・不可逆・高不確実な場面では、責任・Evidence・Authority・Exact Binding等をより厳密に残す必要があります。

### 守る価値

- Progressive Semantic Explicitnessを許す。
- UIや入力を軽くしても、必要なcanonical意味へ降りられる。
- AIのconfidenceだけで記録の厚さを自動決定しない。

### 壊してはいけない境界

```text
Simple presentation != semantic deletion
Low friction != low accountability
```

### 後から確認できるべきこと

- どのProfile / Policyによって明示性が選ばれたか。
- 省略されたのは表示か、canonical意味そのものか。
- 重大性が変わったとき、必要な意味を追加できるか。

## 13. Scenario 12 — 技術が大きく変わっても判断記憶を持ち運ぶ

### 状況

現在利用しているAI、workflow engine、agent runtime、UI、storage、TEI等が、将来別の技術へ置き換わります。

### 守る価値

- SOZAのCoreを現在の実装技術へ過適合させない。
- Goal、Intent、Question、Evidence、Decision、Responsibility、Capability、Semantic Lineage等の意味を持ち運べる。
- 不要になったcode / prompt / orchestrationは手放せる。

### 壊してはいけない境界

```text
Current implementation != enduring product meaning
```

### 後から確認できるべきこと

- 技術交換で失われた意味がないか。
- Provider固有情報とUniversalな意味が分離されていたか。
- 過去Decisionを新しい実行基盤からも再構成できるか。

## 14. Scenario 13 — 設計やテストの成功を利用者価値の実証と混同しない

### 状況

Product Value、ADR、Architecture、fixture、local conformanceが整い、テストも成功しています。しかし、productionで長期利用されたEvidenceや、利用者の意思決定が実際に改善したEvidenceはまだありません。

### 守る価値

- Evidence levelを正直に保つ。
- 設計整合をproduction readinessへ、local PASSをoperational evidenceへ、operational successを利用者価値へ自動昇格させない。
- 未検証であること自体を正規の状態として扱う。

### 壊してはいけない境界

```text
Value Definition
  != Design Coverage
  != Executable Conformance
  != Operational Evidence
  != Adoption / Outcome Evidence
```

### 後から確認できるべきこと

- 現時点でどこまでのEvidenceがあるか。
- どの主張はまだできないか。
- 次のEvidenceを得るために、何を実案件で観察・検証する必要があるか。

## 15. Requirements・ADRへの展開規則

Value Scenarioは、そのまま全てをRequirementへ複製しません。

下位文書へ展開するときは、少なくとも次を確認します。

1. 複数Scenarioに共通する耐久的な意味境界は何か。
2. Product Requirementとして必須にすべきことは何か。
3. Profile / Policy / Provider adapter / domain knowledgeへ置くべきことは何か。
4. Architecture Decisionが必要な選択は何か。
5. Acceptance Scenarioとして観察可能な結果へ落とせるか。
6. 実装がなくてもDecisionできる論点と、実装Evidenceが必要な論点を分けられるか。

Value Scenarioの数をRequirementの数へ一対一対応させる必要はありません。

## 16. この文書で主張しないこと

この文書は、次を証明しません。

- SOZAの実装が各Scenarioをすでに満たしていること。
- productionで価値が実証されていること。
- ここに挙げたScenarioが全利用領域を網羅していること。
- すべてのScenarioに同じ重さの記録が必要であること。

新しい実案件から重要な価値境界が見つかった場合は、Product Valueを変えずにScenarioを追加できる場合があります。一方、Scenario追加によってProduct Value自体の意味を変える必要がある場合は、ADR-0018の再基線化手続きを通します。

## 17. 自然な日本語ドラフト

内容と構造を確定した後、意味、強度、留保、技術的境界を変えず、自然な日本語となることを最重要視して全文を再ドラフトしました。その後、最終意味監査を実施しています。
