# SOZA Value Acceptance

更新日: 2026-08-31  
状態: **Product Value Acceptance Baseline**

## 1. この文書の役割

この文書は、`SOZA_VALUE_MODEL.md`で定義したV1〜V8を、Requirements、ADR、Architecture、Test、Evidenceへ落とすときの受入れ境界を定めます。

Product Valueを単一の点数へ変換する文書ではありません。また、個別機能のtest caseをすべて列挙する文書でもありません。

目的は、**「この設計や実装はSOZAの価値を満たしている」と主張するために、何を確認し、どのEvidenceまで得ている必要があるか**を共通化することです。

## 2. Acceptanceの基本原則

### 2.1 各価値軸は原則として独立に確認する

V1〜V8の一つで高い評価を得ても、別の重大な欠損を相殺したことにはしません。

たとえば、非常に高速で使いやすい実装であっても、過去Decisionのbasisを再構成できない場合はV1を満たしません。

```text
high V6 / V7 != compensation for failed V1 / V2 / V3
```

### 2.2 未検証をPASSとして扱わない

Evidenceがない状態はFAILと同じではありませんが、PASSでもありません。

最低限、次を区別します。

- `Satisfied` — 要求したEvidenceで確認済み
- `Partially Satisfied` — 一部Scenarioのみ確認済み
- `Not Satisfied` — 反例または欠損を確認
- `Not Yet Verified` — まだ必要なEvidenceがない
- `Not Applicable` — 理由を明示して適用対象外

この状態語彙はProduct Value監査用です。Universal Coreのdomain ontologyへ自動的に持ち込みません。

### 2.3 Evidenceの高さを混同しない

Product Valueの主張では、少なくとも次のEvidence階層を分けます。

1. **Design Evidence**  
   文書、ADR、schema、model、review等で意味境界が定義されている。
2. **Executable Evidence**  
   actual repositoryでfixture、test、tool等により再現可能に確認できる。
3. **Release Evidence**  
   配布・releaseされたArtifactについて同じ性質を確認できる。
4. **Operational Evidence**  
   実運用環境で期待した性質が成立していることを観測できる。

上位Evidenceが必要な主張を、下位Evidenceだけで満たしたことにはしません。

```text
Design Evidence != Executable Evidence != Release Evidence != Operational Evidence
```

## 3. V1 Historical Reconstruction

### 価値

過去のDecisionについて、その時点のEvidence、Unknown、Constraint、Authority、参照Artifact等を再構成できること。

### Design Acceptance

- Decisionとそのbasisを表現する境界がある。
- 可変Artifactを現在版へ黙って追随させない設計がある。
- exact historical bindingが必要な場合の意味契約がある。
- Decision revisionとstorage revisionを区別できる。

### Executable Acceptance

少なくとも次のfixtureを再現できる。

1. Decisionを作成する。
2. 参照ArtifactやObservationを後から更新する。
3. 過去Decisionを読み直す。
4. 現在版ではなく、当時参照したbasisを特定できる。
5. どの要素が検証不能なら、その検証不能性を明示できる。

### Failure examples

- logical referenceだけが残り、常に最新版を読む。
- Git commitやDB versionだけからsemantic revisionを推定する。
- 過去Decisionを書き換えて最新知識へ合わせる。

## 4. V2 Semantic Separation

### 価値

Observation、Interpretation / Hypothesis、Recommendation、Decision、Authority、Action Intent、Execution等を、必要な場面で区別できること。

### Design Acceptance

- 重要な意味差が少なくともschema、reference、role、provenance等から復元できる。
- 一つのArtifactへまとめる場合でも、意味上の役割が失われない。
- RecommendationからDecision、DecisionからAuthorization等への自動昇格を前提にしない。

### Executable Acceptance

negative fixtureを含める。

- Recommendationだけが存在する状態をDecision済みと読まない。
- DecisionがあってもAuthorityがなければExecution可能としない。
- Execution成功だけからDecisionの妥当性を確定しない。

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
- 旧revisionをbasisにしたDecisionが新revision作成後も再構成できる。
- representationだけの変更をsemantic changeへ自動昇格させない。

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
- Provider固有情報をadapter / profile / reference境界へ残せる。

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
- Unknownを抱えたままDecisionを行い、そのUnknownをbasisとして後から読める。

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

### Failure examples

- machine-readableだが、人間が意味を確認するには実装コードを読むしかない。
- human summaryがcanonical dataと異なる結論を表示する。
- AI向けPromptにしか重要な判断理由が残らない。

## 9. V7 Progressive Explicitness

### 価値

小さな利用では簡潔に始め、必要になったときに厳密な意味へ降りられること。

### Design Acceptance

- 低影響Scenarioへ過剰な必須入力を課さない。
- 高影響Scenarioでは必要なEvidence、Authority、binding等を追加できる。
- 簡略表示とcanonicalな意味保持を分ける。

### Executable Acceptance

- lightweight scenarioとhigh-impact scenarioの両方を同じ意味基盤で扱える。
- 後から記録を厚くした場合でも、既存Artifactの意味を破壊しない。

### Failure examples

- 全Scenarioで最大詳細を必須化する。
- simple UIのためにcanonical meaning自体を削除する。
- AI confidenceだけで必要記録を減らす。

## 10. V8 Execution Independence

### 価値

workflow、agent runtime、TEI等の実行基盤が置き換わっても、SOZAの判断記憶と意味構造が存続すること。

### Design Acceptance

- execution lifecycleをSOZAのUniversal ontologyへ過剰に固定しない。
- Execution ProviderとDecision Memoryの正本を分ける。
- provider-specific runtime detailはReference / Profile / Adapter等へ隔離できる。

### Executable Acceptance

- 異なるExecution Providerを用いたScenarioで、同じIntent / Decision semanticsを維持できる。
- Provider実装を削除・交換してもhistorical Decisionを読める。

### Failure examples

- workflow engineのrun IDがDecision identityの唯一の根拠になる。
- TEI deployment schemaがSOZAを利用するための必須Universal schemaになる。
- Provider廃止によりDecision historyが読めなくなる。

## 11. Cross-value acceptance

V1〜V8は独立に監査するが、実際のScenarioでは複数軸を同時に検証する。

特に重要な組合せは次のとおり。

- **V1 + V3** — 過去を当時の状態で再構成できるか。
- **V2 + V5** — 不確実なObservationやRecommendationをDecisionへ誤昇格させないか。
- **V4 + V8** — Providerや実行基盤を交換しても意味が残るか。
- **V6 + V7** — 簡単に使えてもcanonical meaningへ戻れるか。
- **V1 + V4 + V5** — Provider Observationが後から変わっても、当時のUnknownを含むChoice basisを再現できるか。

## 12. ADR / Issueへの適用

重要なADRとIssueでは、関係するV1〜V8を必要な範囲で明示する。

すべての文書へ機械的に8軸を記載する必要はない。ただし、Product Valueを理由に設計境界を決める場合は、どの価値を守っているかを後から追えるようにする。

IssueのAcceptance criteriaでは、可能な場合に次を分ける。

- semantic / design acceptance
- executable acceptance
- release acceptance
- operational acceptance

実装がまだ存在しない段階で、後三者を完了扱いにしない。

## 13. Requirementsへの導出規則

Requirementsを作るときは、Product Valueの文章をそのまま機能要件へコピーしない。

各Requirementについて、少なくとも次を確認する。

1. どのV軸を守るためのRequirementか。
2. どのScenarioで必要になるか。
3. 何を満たせばDesign Acceptanceと言えるか。
4. actual repositoryで何を確認すればExecutable Acceptanceと言えるか。
5. Provider / Profile固有の要求をUniversal Requirementへ誤昇格させていないか。
6. 未実装・未検証の場合、そのEvidence状態を正直に記録しているか。

## 14. 関連文書

- `product/value/SOZA_PRODUCT_VALUE.md`
- `product/value/SOZA_VALUE_MODEL.md`
- `product/vision/SOZA_PRODUCT_VISION.md`
- `product/principles/SOZA_PRODUCT_PRINCIPLES.md`
- `plan/adr/ADR-0018-product-value-authority-and-evaluation-boundary.md`
- `plan/adr/ADR-0019-provider-neutral-capability-observation-boundary.md`

## 15. 自然な日本語ドラフト

V1〜V8の意味をValue Modelへ戻って照合し、Evidenceの高さと受入れ状態を混同しないよう構造を整理した後、技術的意味、条件、留保を変えず、自然な日本語となることを最重要視して全文を再ドラフトしました。その後、最終意味監査を実施しています。
