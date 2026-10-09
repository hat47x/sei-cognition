# SEIの価値評価モデル

更新日: 2026-09-11  
状態: **製品価値の基準版。複数の評価軸にまたがる判断継続性を反映済み**

## 1. この文書の役割

この文書は、`SEI_PRODUCT_VALUE.md`で定めた価値を、設計判断へ落とせる粒度まで精緻化するための基準です。

個々の機能や実装方式を決める文書ではありません。要求、ADR、全体構成、契約、実装が製品価値に合っているかを判断するため、価値の優先関係、境界、成立条件、失敗条件を定めます。

V1〜V8をどの検証根拠（Evidence）で確かめるかは`SEI_VALUE_ACCEPTANCE.md`、現行の下位文書との対応関係は`SEI_VALUE_TRACEABILITY.md`で扱います。

また、V1〜V8が利用者の一つの判断仕事で同時に働いたときに現れる複数の評価軸にまたがる製品上の成果を`SEI_DECISION_CONTINUITY.md`で扱います。

## 2. SEIが守る価値の階層

SEIでは、価値を次の三層に分けます。

### 2.1 第一層: 失ってはならない意味

最優先で守るのは、次の意味です。

- 何が観察されたか。
- 何が不明だったか。
- 何が仮説・解釈・推奨だったか。
- 何を根拠として判断したか。
- 誰または何が、どの役割と権限のもとで判断・実行したか。
- その判断や実行が、どの時点の状態に基づいていたか。
- 後から何が変わり、何を改訂・撤回・置換したか。

この層は、実装の簡略化、性能、操作性、特定の提供元との連携のしやすさを理由に失わせません。

### 2.2 第二層: 選び直せること

第一層の意味を保持したうえで、SEIは次を可能にします。

- 根拠を読み直す。
- 過去の判断を当時の状態として復元する。
- 新しい検証根拠を加えて判断し直す。
- 能力の提供元（Capability Provider）を交換する。
- 提案（Recommendation）を採用するかどうか判断し、必要なら修正する。
- 実行結果を次の問いや判断へ戻す。

SEIにとって、履歴を残すことは保存そのものが目的ではありません。将来の主体が、過去を消さずに選び直せることに価値があります。

### 2.3 第三層: 利用し続けられること

意味が正しくても、利用が著しく難しければ実務上の価値は失われます。

そのためSEIは、次も重要な製品価値として扱います。

- 人間が読んで意味を追えること。
- AIが構造として利用できること。
- 必要な意味だけを段階的に明示できること。
- 小さな利用から始め、必要に応じて厳密化できること。
- 外部システムと接続しても、SEI側が保持する意味の区別が失われないこと。
- 中断や環境変化の後でも、実務上許容できる負担で判断の続きを取り戻せること。

ただし、使いやすさのために第一層の意味を黙って捨てることは認めません。意味の省略が必要な場合は、簡略化した表示と、正本となる意味の保持を分けます。

また、「利用し続けられること」は単にサービスが稼働し続けることではありません。実際の利用者や組織が必要な場面で意味を読み直し、選び直し、再開するために使えることまで含みます。

## 3. 価値が衝突したときの優先規則

設計上の価値が衝突した場合は、原則として次の順に判断します。

1. **意味保存と責任線を守る。**
2. **再構成可能性と選び直せる余地を守る。**
3. **提供元や実行方式からの独立性を守る。**
4. **人間とAIの双方が扱える理解可能性を守る。**
5. **利用継続性と再開負担を改善する。**
6. **操作性、性能、自動化率、実装容易性を最適化する。**

これは、下位の価値を軽視するという意味ではありません。上位価値を破壊しない範囲で、下位価値を最大化します。

「再開しやすい」ことも、当時の判断根拠の誤表示や未確定事項の削除と引き換えにはしません。速さよりも意味の正確さを優先します。

重大な性能・運用上の制約によって上位価値を完全には満たせない場合は、暗黙に省略せず、制約、失われる意味、代替策、再検討条件をADRに残します。

また、一つの価値軸で高い成果が得られても、別の重大な価値欠損を相殺したことにはしません。製品価値の受け入れ判断では、V1〜V8を必要な範囲で個別に確認します。

## 4. SEIへ含めるための価値境界

ある概念・機能・データをSEIの中核へ含めるかは、次の問いで判断します。

### 4.1 中核へ置く可能性が高いもの

- Providerが変わっても意味が残る。
- 実行ランタイムが変わっても必要である。
- 判断、責任、不確実性、来歴の再構成に必要である。
- 複数domainで同じ意味境界を持つ。
- 失うと過去の判断を誤って読み替える危険が高い。

### 4.2 中核へ置かない可能性が高いもの

- 特定Providerの内部都合に強く依存する。
- 特定分野のパターンやスキーマである。
- 業務の流れを実行する仕組み、待ち行列、再試行、処理の配置など、外部の能力提供元へ委ねられる実行上の詳細である。
- AIの内部推論過程そのものを保存しなければ成立しない。
- 現在の実装に便利だという理由だけで、汎用的な意味として扱おうとしている。
- 再開時の要約、作業中の情報の集合、最近使った項目の一覧、状態を識別するトークンなど、利用者とのやり取りを便利にするための表示や実行環境内の概念である。

## 5. 製品価値を満たしたと判断するための検証観点

機能やArchitectureは、少なくとも次の観点で検証します。

### V1. 過去の判断根拠の復元

過去の判断（Decision）について、その時点の根拠、未確定事項、制約、権限、参照した成果物を復元できるか。

### V2. 意味の区別

観察、解釈、提案、判断、権限、実行の意図、実行を必要な範囲で区別できるか。

### V3. 改訂履歴の整合性

新しい知識によって過去の状態を上書きせず、SupersessionやRevisionとして来歴を辿れるか。

### V4. 提供元からの独立性

提供元を交換しても、能力、意図、判断、責任などの意味を保てるか。

### V5. 不確実性の保持

未確定事項、対立、仮説を、便宜上の確定値へ知らないうちに変換していないか。

### V6. 人間とAIの双方が理解できること

人間が判断理由を追え、AIも構造として利用できるか。どちらか一方だけに最適化していないか。

### V7. 段階的に意味を明確化できること

小さな利用では簡潔に扱いながら、必要になったときに厳密な意味へ降りられるか。

### V8. 実行環境からの独立性

外部の業務手順、AIエージェントの実行環境、TEIなどが置き換わっても、SEIが保持する判断の記録と意味の構造は残るか。

これらの軸に対するEvidenceは、少なくとも次の高さを分離して扱います。

```text
Design
  != Executable
  != Release
  != Operational
  != Adoption / Outcome
```

具体的な受入れ条件は`SEI_VALUE_ACCEPTANCE.md`を正とします。

## 6. 複数の評価軸にまたがる成果としての判断継続性

判断継続性（Decision Continuity）は、V1〜V8に追加する第9の評価軸ではありません。

一人の利用者が実際の判断作業を中断し、後から再開する際には、複数の価値の評価軸が同時に必要です。

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

したがって、判断継続性は**複数の評価軸にまたがって利用者の成果を検証する利用場面**として扱い、V1〜V8の独立監査を維持します。

### 6.2 判断継続性が成立しない例

- canonical dataは正しいが、chat historyがないと利用者がどこから再開すべきか分からない。
- Resume summaryは読みやすいが、Decision後に得た情報をhistorical basisへ混ぜている。
- AIが要点を出せるが、誤ったRecommendationを利用者が訂正・却下できない。
- Provider交換後にpast Decisionは読めるが、current unresolvedやreopen conditionへ戻れない。
- 詳細を残せるが、入力負担が大きすぎて継続利用されない。

## 7. 価値上の失敗パターン

次の状態は、機能が動いていても製品価値の実現には失敗したとみなします。

- AIの提案を、採用済みの判断として保存する。
- 現在のArtifactを参照して、過去のDecision basisを再構成したことにする。
- 未確定事項を未入力の値とみなして削除する。
- 対立を最新の値で上書きする。
- Provider固有IDだけをcanonical identityにする。
- 実行成功を、そのDecisionが妥当だった証明として扱う。
- Cognitive Methodを適用した事実を、結論の正しさの保証として扱う。
- 画面を簡略化するために正本となる意味を失う。
- 特定製品との密接な関係だけを理由に、その製品をSEIの一部として特別扱いする。
- Design Evidenceしかない状態を、actual repositoryやproductionで実証済みと表現する。
- fixtureがPASSしたことを、SEI全体のExecutable Acceptanceとして扱う。
- productionで正常稼働したことを、利用者や組織への価値が実現した証明として扱う。
- canonical dataは保持しているが、利用者が再開するにはraw historyを長時間読み直すしかない。
- time-to-resumeだけを短縮し、historical誤帰属やRecommendation / Decision混同を増やす。
- 監査可能性を理由に入力負担を増やし、capture overheadが実利用価値を上回る。

## 8. 実装規模と価値の関係

中核となる型やコードを増やすだけで、SEIの価値が高まるわけではありません。

新しい概念をCoreへ追加する場合は、既存概念の組合せ、Reference、Extension、Capability Provider、domain-specific knowledgeで表現できないかを先に確認します。

少ないUniversal Coreで意味を保てるなら、その方が将来の技術変化に耐えやすいと考えます。

同様に、製品価値を機能数だけで測ることはしません。Resume Brief、AI assistant、timeline等のSurface featureが増えても、Decision Continuityの失敗が減らないなら価値向上とは扱いません。

## 9. 将来耐性

将来耐性は、特定の未来技術を予測することではありません。

評価時点の現実からおおむね10〜50倍程度先を見たときにも、現在の実装方式を前提にしすぎていないかを点検する移動基準として扱います。

将来、現在のAI agent、workflow、orchestrator、UI、storage方式が大きく変わっても、この文書の第一層と第二層が依然として意味を持つことを目標とします。

Decision Continuityも、現在のchat UIやLLM context windowに依存する概念ではありません。将来AIがより自律化しても、過去に何が認識され、何が判断され、どこまで委任され、何が未解決だったかを別の主体が再開できる価値は残ると考えます。

この距離は性能の評価点ではありません。現在の制約や流行へ過適合していないかを問うための思考上の距離です。

## 10. 下位文書との関係

この文書の価値境界は、次の順に具体化します。

```text
SEI Product Value
  → SEI Value Model
  → SEI Value Acceptance
  → Product Vision / Principles
  → Requirements / Acceptance Scenarios
  → Issue / ADR
  → Architecture
  → Contract
  → Implementation / Test / Evidence
```

Vision / Principlesは価値の方向と反復原則を示し、Value Acceptanceは価値を満たしたと主張するためのEvidence境界を示します。これらは上下関係というより、Value Modelを異なる方向から具体化する補完文書です。

Decision Continuityはこの流れへ別の階層を追加しません。Value Modelを利用者成果へ横断して読むためのsynthesisです。

current下位文書との対応は`SEI_VALUE_TRACEABILITY.md`で索引化します。

下位の都合からこの価値境界を変更する必要が生じた場合は、実装を正当化するために直接書き換えず、Product Value変更として明示的に再審査します。

## 11. 関連文書

- `product/README.md`
- `product/value/SEI_PRODUCT_VALUE.md`
- `product/value/SEI_VALUE_PROPOSITION.md`
- `product/value/SEI_VALUE_ACCEPTANCE.md`
- `product/value/SEI_VALUE_TRACEABILITY.md`
- `product/value/SEI_DECISION_CONTINUITY.md`
- `product/interaction/SEI_FIRST_USABLE_PRODUCT_SLICE.md`
- `product/vision/SEI_PRODUCT_VISION.md`
- `product/principles/SEI_PRODUCT_PRINCIPLES.md`
- `requirements/PRODUCT_REQUIREMENTS.md`
- `requirements/ACCEPTANCE_SCENARIOS.md`
- `plan/adr/ADR-0018-product-value-authority-and-evaluation-boundary.md`

## 12. 自然な日本語ドラフト

Product Value、Value Acceptance、Decision Continuity synthesis、resume-first Product Slice、current Requirements / Architecture / Contractの状態を再確認した。

V1〜V8の独立性を保ったまま、実利用では複数軸が同時に成立して初めて「判断の続きを始められる」という成果になることをDecision Continuityとして整理した。これをV9にせず、既存軸の重大な欠損をcross-axis scoreで相殺しない境界を明示している。

また、第三層の「利用し続けられること」を、単なるUI usabilityから中断・Surface loss・AI変更後の再開可能性へ深めた。意味、規範強度、Evidence階層を固定したうえで自然な日本語として全文を再ドラフトし、最終意味監査を実施している。