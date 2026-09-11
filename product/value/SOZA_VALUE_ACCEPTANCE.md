# SOZA Value Acceptance

更新日: 2026-09-11  
状態: **Product Value Acceptance Baseline — Decision Continuity cross-axis acceptance reflected**

## 1. この文書の役割

この文書は、`SOZA_VALUE_MODEL.md`で定義したV1〜V8を、Requirements、ADR、Architecture、Contract、Implementation、Test、Evidenceへ落とすときの受入れ境界を定めます。

Product Valueを単一の点数へ変換する文書ではありません。また、個別機能のtest caseをすべて列挙する文書でもありません。

目的は、**「この設計・実装・運用はSOZAの価値を満たしている」と主張するとき、何を確認し、どの高さのEvidenceまで得られている必要があるか**を共通化することです。

Decision ContinuityはV1〜V8とは別のValue Axisではありません。本書では、複数Value Axisが一つの利用者仕事で同時に成立したかを確認するcross-axis Product Outcomeとして受け入れます。

## 2. Acceptanceの基本原則

### 2.1 各価値軸は原則として独立に確認する

V1〜V8の一つで高い評価を得ても、別の重大な欠損を相殺したことにはしません。

たとえば、非常に高速で使いやすい実装であっても、過去Decisionのbasisを再構成できなければV1を満たしません。

```text
high V6 / V7 != compensation for failed V1 / V2 / V3
```

Value coverageを集計する場合も、総合点によって重大な欠損を隠しません。

### 2.2 未検証をPASSとして扱わない

Evidenceがない状態はFAILと同じではありませんが、PASSでもありません。

最低限、次を区別します。

- `Satisfied` — 要求したEvidenceで確認済み
- `Partially Satisfied` — 一部Scenarioまたは一部条件のみ確認済み
- `Not Satisfied` — 反例または欠損を確認
- `Not Yet Verified` — 必要なEvidenceをまだ得ていない
- `Not Applicable` — 理由を明示して適用対象外

この状態語彙はProduct Value監査用です。Universal Coreのdomain ontologyへ自動的に持ち込みません。

### 2.3 Evidenceの高さを混同しない

Product Valueに関する主張では、少なくとも次のEvidence階層を分けます。

1. **Design Evidence**  
   文書、ADR、model、Contract Definition、schema等で意味境界や受入れ条件が定義されている。
2. **Executable Evidence**  
   actual repositoryでfixture、test、validator、tool等により、対象範囲を再現可能に確認できる。
3. **Release Evidence**  
   実際に配布・releaseされたArtifactについて、必要な性質を確認できる。
4. **Operational Evidence**  
   実運用環境で、期待した意味境界・相互運用・統制等が成立していることを観測できる。
5. **Adoption / Outcome Evidence**  
   実際の利用によって、人間・AI・組織の判断、再検討、説明可能性、Provider選択、業務上の成果等が意図した方向へ改善したことを確認できる。

```text
Design Evidence
  != Executable Evidence
  != Release Evidence
  != Operational Evidence
  != Adoption / Outcome Evidence
```

上位Evidenceが必要な主張を、下位Evidenceだけで満たしたことにはしません。

### 2.4 運用成功と利用者価値を分ける

SOZAが本番環境で安定して動作し、Contractに沿って記録を保存できたとしても、それだけでProduct Valueが利用者に届いたとは判断しません。

たとえば、次は別の問いです。

- 過去Decisionを技術的に再構成できるか。
- 利用者が必要な場面で実際に再構成し、判断を見直せたか。
- Unknownを保存できるか。
- Unknownを保存することで、過度な確定や説明責任上の誤りを減らせたか。
- Providerを交換できるか。
- Providerを交換できることが、実際に選択肢・交渉力・継続性の改善へつながったか。

したがって、Operational EvidenceとAdoption / Outcome Evidenceは分けて記録します。

```text
Operational success != user-value realization
```

Outcomeは単一のKPIへ固定しません。対象Scenarioに応じて、質的Evidence、具体事例、再判断結果、利用継続上の改善、障害・誤判断の回避等を組み合わせて評価できます。

### 2.5 Cross-axis Outcomeを新しい総合scoreにしない

Decision Continuityのような横断Outcomeは、V1〜V8を利用者の仕事へ接続するために使います。

ただし、一つのcontinuity scoreで軸ごとのFAILを平均化しません。

```text
Decision Continuity observed
  requires relevant V-axis failures to remain visible
```

resumeが速くてもhistorical basisを誤っていればV1 / V3の失敗です。入力が少なくてもUnknownを消していればV5の失敗です。

## 3. V1 Historical Reconstruction

### 価値

過去のDecisionについて、その時点のEvidence、Unknown、Constraint、Authority、参照Artifact等を再構成できること。

### Design Acceptance

- Decisionとそのbasisを表現する境界がある。
- 可変Artifactを現在版へ黙って追随させない設計がある。
- exact historical bindingが必要な場合の意味契約がある。
- Decision revisionとstorage revisionを区別できる。

### Executable Acceptance

少なくとも次をfixtureまたは同等の再現可能な検査で確認できる。

1. Decisionを作成する。
2. 参照ArtifactやObservationを後から更新する。
3. 過去Decisionを読み直す。
4. 現在版ではなく、当時参照したbasisを特定できる。
5. 検証不能な要素があれば、その検証不能性を明示できる。

### Operational / Outcomeで確認したいこと

- 実運用のDecision historyを、必要な時点で破綻なく再構成できる。
- 再構成した情報が、監査、説明、再判断、引継ぎ等で実際に役立つ。
- 中断後の利用者が、現在知っている情報を過去Decisionのbasisへ誤帰属しない。

### Failure examples

- logical referenceだけが残り、常に最新版を読む。
- Git commitやDB versionだけからsemantic revisionを推定する。
- 過去Decisionを書き換えて最新知識へ合わせる。

## 4. V2 Semantic Separation

### 価値

Observation、Interpretation / Hypothesis、Recommendation、Decision、Authority、Action Intent、Execution等を、必要な場面で区別できること。

### Design Acceptance

- 重要な意味差をschema、reference、role、provenance等から復元できる。
- 一つのArtifactへまとめる場合でも、意味上の役割が失われない。
- RecommendationからDecision、DecisionからAuthorization等への自動昇格を前提にしない。

### Executable Acceptance

negative fixtureを含め、少なくとも次を確認する。

- Recommendationだけが存在する状態をDecision済みと読まない。
- DecisionがあってもAuthorityがない状態を表現できる。
- Execution成功だけからDecisionの妥当性を確定しない。

### Operational / Outcomeで確認したいこと

- 実運用で提案、判断、権限、実行の責任線を必要な場面で追える。
- 意味差を残したことで、誤承認、誤帰属、説明上の混同を減らせる。
- AI suggestionを利用者自身のDecisionとして誤想起・誤表示しない。

### Failure examples

- AI出力をそのままDecision recordとして保存する。
- command acceptedをactual execution successと同一視する。
- Pattern matchやMethod ApplicationをAssuranceへ昇格させる。

## 5. V3 Revision Integrity

### 価値

新しい知識によって過去を上書きせず、何が何をSupersede / Reviseしたかを辿れること。

### Design Acceptance

- semantic revisionとstorage revisionが分離されている。
- supersession / lineageを表現できる。
- current stateとhistorical stateを区別できる。

### Executable Acceptance

- 同一logical Artifactの複数revisionを保持できる。
- 旧revisionをbasisにしたDecisionを、新revision作成後も再構成できる。
- representationだけの変更をsemantic changeへ自動昇格させない。

### Operational / Outcomeで確認したいこと

- 長期間の更新を経ても、過去の意味と現在の意味を取り違えない。
- 「なぜ判断が変わったか」を実際の再検討や説明に利用できる。
- resume時に「Decision当時」と「その後の変化」を短い距離で区別できる。

### Failure examples

- update操作が常に旧意味を破壊する。
- 最新revisionしか参照できない。
- digest差をsemantic changeと決めつける。

## 6. V4 Provider Independence

### 価値

Providerを交換しても、Capability、Intent、Decision、Responsibility等の意味が壊れないこと。

### Design Acceptance

- CapabilityとProviderが分離されている。
- Provider-specific schemaをUniversal Coreへ無条件に複製しない。
- Provider kindから信頼、優先度、Authorityを推定しない。

### Executable Acceptance

- 同じCapabilityについて異なるProvider種別のfixtureを扱える。
- Providerを交換しても、DecisionやIntentのlogical meaningが維持される。
- Provider固有情報をAdapter / Profile / Reference境界へ残せる。

### Operational / Outcomeで確認したいこと

- Provider変更や廃止が起きても、意味資産とDecision historyを維持できる。
- Provider中立性が、実際の選択肢、継続性、再交渉、移行可能性等に寄与する。
- Provider交換後も、利用者が同じ判断仕事の続きを実務上再開できる。

### Failure examples

- TEI専用fieldがCapability Universal identityの必須要素になる。
- AI Providerのmodel IDがCapabilityそのもののidentityになる。
- 関連製品であることを理由にTEIを自動優先する。

## 7. V5 Uncertainty Preservation

### 価値

Unknown、Conflict、Hypothesis、observation gap等を、便宜上の確定値へ黙って変換しないこと。

### Design Acceptance

- Unknownとnegative factを区別できる。
- Conflictを複数Observationとして保持できる。
- Withheld contextが必要なProfileでは単純Unknownと分けられる。

### Executable Acceptance

- `not observed`を`false`や`unavailable`へ変換しないfixtureがある。
- conflicting Evidenceを最新値だけで上書きしない。
- Unknownを抱えたままDecisionを行い、そのUnknownを後から確認できる。

### Operational / Outcomeで確認したいこと

- 実運用でも未確認事項を無理に埋めず、必要な不確実性を保持できる。
- 不確実性を保持したことが、誤った断定、不要な自動化、後日の説明困難を減らすことにつながる。
- 中断後の利用者が、何がまだ未解決かを再発見するためにraw履歴全体を読み直さなくてよい。

### Failure examples

- null / missingをNoと読む。
- conflict resolution前に古いObservationを削除する。
- confidence値だけでUnknownを確定値へ昇格させる。

## 8. V6 Human / AI Readability

### 価値

人間が意味を追え、AIも構造として利用できること。

### Design Acceptance

- canonical Artifactに、人間が判断理由を追うための情報がある。
- 機械可読性のためだけにopaque ID列へ意味を押し込めない。
- 人間向け説明と機械向け構造が互いに矛盾しない。

### Executable Acceptance

- representative Artifactを人間向けProjectionとmachine-readable representationの双方で確認する。
- 同一Decisionについて、両表示からbasis、未解決点、responsibilityを辿れる。
- transient chat / UI stateを削除しても、canonical stateから必要なProjectionを再生成できる。

### Operational / Outcomeで確認したいこと

- 人間が実務上必要な時間・負担で意味を読める。
- AIが構造を利用しても、人間向け説明との意味差が蓄積しない。
- 可読性がレビュー、引継ぎ、再判断、task resumptionの実効性につながる。

### Failure examples

- machine-readableだが、人間が意味を確認するには実装コードを読むしかない。
- human summaryがcanonical dataと異なる結論を表示する。
- AI向けPromptにしか重要な判断理由が残らない。
- canonical dataは正しいが、再開には長大なraw historyを読み直す必要がある。

## 9. V7 Progressive Explicitness

### 価値

小さな利用では簡潔に始め、必要になったときに厳密な意味へ降りられること。

### Design Acceptance

- 低影響Scenarioへ過剰な必須入力を課さない。
- 高影響Scenarioでは必要なEvidence、Authority、binding等を追加できる。
- 簡略表示とcanonicalな意味保持を分ける。

### Executable Acceptance

- lightweight scenarioとhigh-impact scenarioの両方を同じ意味基盤で扱える。
- 後から記録を厚くしても、既存Artifactの意味を破壊しない。

### Operational / Outcomeで確認したいこと

- 軽量利用では過剰な記録負担を生まず、高影響利用では必要な意味を取り戻せる。
- 明示量の調整が、利用放棄や形骸化を防ぎつつ、重要場面の説明可能性を維持する。
- SOZAのcapture / review overheadが、再開・再判断で得られる価値を継続的に上回らない。

### Failure examples

- 全Scenarioで最大詳細を必須化する。
- simple UIのためにcanonical meaning自体を削除する。
- AI confidenceだけで必要記録を減らす。
- audit可能性を理由に入力負担を増やし、利用者がraw noteへ戻る。

## 10. V8 Execution Independence

### 価値

workflow、agent runtime、TEI等の実行基盤が置き換わっても、SOZAの判断記憶と意味構造が存続すること。

### Design Acceptance

- execution lifecycleをSOZAのUniversal ontologyへ過剰に固定しない。
- Execution ProviderとDecision Memoryの正本を分ける。
- provider-specific runtime detailをReference / Profile / Adapter等へ隔離できる。

### Executable Acceptance

- 異なるExecution Providerを用いたScenarioで、同じIntent / Decision semanticsを維持できる。
- Provider実装を削除・交換してもhistorical Decisionを読める。

### Operational / Outcomeで確認したいこと

- 実行基盤の更新・交換・廃止が、SOZAの意味資産を巻き込んで破壊しない。
- 実行基盤から独立していることが、長期保守、移行、再利用、ロックイン回避に実際に寄与する。
- AI / runtime変更後も利用者が同じ判断文脈を再開できる。

### Failure examples

- workflow engineのrun IDがDecision identityの唯一の根拠になる。
- TEI deployment schemaがSOZAを利用するための必須Universal schemaになる。
- Provider廃止によりDecision historyが読めなくなる。

## 11. Cross-value acceptance

V1〜V8は独立に監査しますが、実際のScenarioでは複数軸を同時に検証します。

特に重要な組合せは次のとおりです。

- **V1 + V3** — 過去を当時の状態で再構成できるか。
- **V2 + V5** — 不確実なObservationやRecommendationをDecisionへ誤昇格させないか。
- **V4 + V8** — Providerや実行基盤を交換しても意味が残るか。
- **V6 + V7** — 簡単に使えてもcanonical meaningへ戻れるか。
- **V1 + V4 + V5** — Provider Observationが後から変わっても、当時のUnknownを含むChoice basisを再現できるか。

Cross-value ScenarioのPASSも、V1〜V8を一つの総合点へまとめる根拠にはしません。

### 11.1 Decision Continuity acceptance

Decision Continuityは、主にV1 / V2 / V3 / V5 / V6 / V7を、V4 / V8の交換可能性と合わせて利用者仕事へ接続します。

#### Design Acceptance

- canonical stateとtransient Surface / chat / AI contextが分離されている。
- resume時にcurrent question、Decision、historical basis、unresolved、post-decision changeへ戻る設計がある。
- AI suggestionをprovisionalに扱い、訂正・却下できる境界がある。
- capture burdenを下げてもcanonical meaningを黙って削らない。

#### Executable Acceptance

少なくともfirst sliceでは次を再現可能に確認します。

1. transient UI state、chat history、Projection cacheを除去する。
2. canonical stateだけからresume Projectionを再構成する。
3. Decision当時basisとDecision後のObservationを区別する。
4. AI suggestionを修正・却下し、uncommitted suggestionをcanonical Decisionへ昇格させない。
5. AI unavailableでもmanualなread / add / Decision / review / reopenを継続する。
6. stale / partial semantic changeを正常成功として見せない。

これらはISSUE-000073のprototype Evidenceで検証します。

#### Adoption / Outcome Acceptance

Decision Continuityを利用者価値として主張するには、技術的resumeだけでは不十分です。

妥当な代替手段、たとえばraw chat / chronological note等と比べて、少なくとも次を観測します。

- current question / Decision / unresolvedを正しく再構成できるか。
- post-decision情報をhistorical basisへ誤帰属しないか。
- RecommendationとDecisionを誤認しないか。
- 再開までの時間・操作・mental effortがどう変わるか。
- AI correction / dismissalの負担がどう変わるか。
- first useful saveまでのcapture burdenがどう変わるか。
- 利用者が継続利用したいと判断するか。その理由は何か。

初期段階では一つの固定thresholdをStable Requirementへしません。

```text
faster resume
  + worse historical accuracy
  = not accepted as Decision Continuity improvement
```

また、raw chat / simple noteで十分で追加構造に実質的な価値差がなければ、Product hypothesisの反証Evidenceとして扱います。

## 12. ADR / Issueへの適用

重要なADRとIssueでは、関係するV1〜V8を必要な範囲で明示します。

すべての文書へ機械的に8軸を記載する必要はありません。ただし、Product Valueを理由に設計境界を決める場合は、どの価値を守っているかを後から追えるようにします。

IssueのAcceptance criteriaでは、必要に応じて次を分けます。

- semantic / design acceptance
- executable acceptance
- release acceptance
- operational acceptance
- adoption / outcome acceptance

下位Evidenceしかない段階で、上位Acceptanceを完了扱いにしません。

## 13. Requirementsへの導出規則

Requirementsを作るときは、Product Valueの文章をそのまま機能要件へコピーしません。

各Requirementについて、少なくとも次を確認します。

1. どのV軸を守るためのRequirementか。
2. どのAcceptance Scenarioで必要になるか。
3. 何を満たせばDesign Acceptanceと言えるか。
4. actual repositoryで何を確認すればExecutable Acceptanceと言えるか。
5. Release / Operational / Outcomeまで必要な主張か。
6. Provider / Profile固有の要求をUniversal Requirementへ誤昇格させていないか。
7. 未実装・未検証の場合、そのEvidence状態を正直に記録しているか。
8. cross-axis Product Outcomeの都合だけで既存Value Axisを重複Requirement化していないか。

## 14. 現在のEvidence読み取り規則

current repositoryには、Product / Requirements / Architecture / ContractのDesign baselineがあります。また、Contract、semantic runtime、Product Interaction、Packaging、Product Access、Realization / Provider交換等には対象を限定したScoped Executable Evidenceがあります。

v0.2.0 Local Reference Product BaselineにはRelease Evidenceがありますが、release後のExecutable Evidenceを既存releaseのsupported scopeへ遡及的に追加しません。

Decision Continuityについては、Product Value synthesisとresume-first first sliceのDesign Evidenceがありますが、prototype Executable Evidence、human comparative Evidence、Operational / Adoption・Outcome Evidenceは`Not Yet Verified`です。

GitHub Actions等の特定実行基盤をEvidenceの意味上の成立条件にはしません。必要なtest、checker、probe、保存Evidence、human reviewを実際に実行できた範囲だけ記録します。

## 15. 関連文書

- `product/value/SOZA_PRODUCT_VALUE.md`
- `product/value/SOZA_VALUE_MODEL.md`
- `product/value/SOZA_VALUE_PROPOSITION.md`
- `product/value/SOZA_VALUE_TRACEABILITY.md`
- `product/value/SOZA_DECISION_CONTINUITY.md`
- `product/interaction/SOZA_FIRST_USABLE_PRODUCT_SLICE.md`
- `product/vision/SOZA_PRODUCT_VISION.md`
- `product/principles/SOZA_PRODUCT_PRINCIPLES.md`
- `requirements/PRODUCT_REQUIREMENTS.md`
- `requirements/ACCEPTANCE_SCENARIOS.md`
- `architecture/TRACEABILITY.md`
- `contracts/TRACEABILITY.md`
- `plan/issue/ISSUE-000073-define-first-usable-resume-first-product-slice.md`
- `plan/adr/ADR-0018-product-value-authority-and-evaluation-boundary.md`

## 16. 自然な日本語ドラフト

V1〜V8の意味をValue Modelへ戻って照合し、Design / Executable / Release / Operational / Adoption・Outcomeの各Evidenceを混同しないよう全体を再構成した。

今回、Decision Continuityをcross-axis Product Outcomeとして追加し、V1〜V8を別の総合scoreへ畳み込まずに利用者成果へ接続した。技術的にresumeできることと、実際に正しく・低負担で再開できることを分け、raw chat / simple note等の妥当な代替との比較までAdoption / Outcome Acceptanceへ置いた。

また、current Evidence記述を特定CI基盤から分離し、resume-first Product SliceのDesign Evidenceと未検証のprototype / human reviewを明確に分けた。技術的意味、条件、留保、Evidence強度を変えず、自然な日本語となることを最重要視して全文を再ドラフトし、最終意味監査を実施している。