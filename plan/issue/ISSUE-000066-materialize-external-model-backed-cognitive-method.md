# ISSUE-000066: external model-backed Cognitive Method executionを実証する

- Status: Open
- Priority: 1
- Related ADRs: ADR-0017, ADR-0021, ADR-0025
- Product Milestone: PMS-06

## 背景

ISSUE-000064では、固定revisionのKJ AtlasをSOZAとは別processとして起動し、`POST /ai/suggest-card-groups`を実行した結果を、SOZAのCognitive Method Applicationと`not_verified`なMethod outputへ写像するE3b-M1aを実証しました。

ただしM1aでKJ Atlasが接続したmodel endpointはdeterministic model stubです。したがって、外部Cognitive Methodのprocess境界は実在化できていますが、実際の生成modelを介したMethod実行まではEvidence化していません。

本IssueではM1aの境界を保ったままmodel transportだけを実modelへ交換し、E3b-M1bとして次の経路を最小範囲で実証します。

```text
SOZAのsynthetic input
  → 固定revisionのKJ Atlas process
  → KJ AtlasのLLM provider boundary
  → actual model inference
  → KJ AtlasのMethod output
  → SOZA Cognitive Method Application
  → opaque / not_verified Method output
```

## 目的

固定revisionのKJ Atlasがactual model inferenceを伴って実行され、その結果を既存のSOZA Method境界を壊さずに取り込めることをScoped Executable Evidenceとして残します。

ここで確認したいのは「実modelを含む外部Method executionの接続性」です。model出力の品質、KJ法としての妥当性、RecommendationやDecisionの正しさは評価対象にしません。

## 固定する外部source

- Repository: `hat47x/kj-atlas`
- Commit: `4f28c13abe4176503c6fed863383a2d1db2299e9`
- Method entry point: `POST /ai/suggest-card-groups`

M1aと同じsource revisionを使います。M1bのためにKJ Atlas source自体を書き換えません。

## 実証方法

GitHub Actionsの短命`GITHUB_TOKEN`へ`models: read`だけを付与し、GitHub Modelsの推論APIをactual model endpointとして使います。

固定revisionのKJ Atlasが持つDeepSeek transportはOpenAI互換requestを`/v1/chat/completions`へ送る一方、GitHub Modelsは`/inference/chat/completions`を公開しています。このURL差だけを、SOZA repository内のEvidence専用loopback protocol shimで変換します。

protocol shimはmodel outputを生成、補正、固定化しません。JSON requestとBearer credentialをGitHub Modelsへ転送し、上流responseをKJ Atlasへ返すだけです。このshimはproduction ProviderでもUniversal Contractでもありません。

## Evidenceとして確認すること

- [ ] 固定revisionのKJ Atlasが別processとして起動する。
- [ ] KJ Atlasの`providerKind`が外部model transportを示す設定で起動する。
- [ ] actual Method request前のprovider call countが0である。
- [ ] `POST /ai/suggest-card-groups`がactual model inferenceを経て成功する。
- [ ] request後のprovider call countが増加する。
- [ ] held cardがKJ AtlasのMethod outputで`excludedCardIds`へ保持される。
- [ ] actual Method outputを既存のSOZA `livemethodintegration`境界へ入力できる。
- [ ] SOZA側では結果をopaque / `not_verified` outputとして保持し、Recommendation / Decisionへ自動昇格させない。
- [ ] source repository / commit / entry point / result digestのProvenance境界を維持する。
- [ ] 対象CIがsuccessする。

## 明示的な停止線

```text
external Method process execution
  != external model invocation
  != model output quality
  != Recommendation
  != Decision
```

M1bでexternal model invocationが成立しても、次は主張しません。

- modelの回答内容が高品質であること
- KJ法として適切な島形成ができたこと
- 人間の探索や判断に実用上寄与したこと
- Method outputがRecommendationであること
- RecommendationやDecisionが正しいこと
- production向けmodel credential運用が成立したこと
- GitHub ModelsがSOZAまたはKJ Atlasの標準Providerであること
- v0.2.0のsupported scopeがE3b-M1bまで拡張されたこと
- Release / Operational / Adoption / Outcome Evidence

## Requirement / Scenarioの扱い

本Issueでは新しいStable Requirement / Scenarioを追加しません。

REQ-0001、REQ-0004、REQ-0005、REQ-0021、およびSCN-0005、SCN-0014、SCN-0018が保持している既存境界の上で、M1aより一段だけ実在性の高いEvidenceを追加します。実model接続のための特定provider、model ID、protocol shimをSOZA Universal Coreの要件へ昇格させません。

## 完了条件

固定revisionのKJ Atlasからactual model inferenceを一度以上実行し、そのactual Method outputを既存SOZA Method mappingへ通したことをCI Evidenceで確認できた時点でResolvedとします。

actual model endpointへ到達できない場合は、credential-aware pathやCI wiringが正しくてもResolvedにはしません。その場合はNot Yet Verifiedの事実をそのまま残します。
